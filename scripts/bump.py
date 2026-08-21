#!/usr/bin/env python3
"""Auto-bump Scoop manifests from live GitHub releases."""
import hashlib, json, os, urllib.request

REPO_SRC = "cybersec-tools"
OWNER = "BartoszOsiej"
TOOLS = ["netrecon", "hashsleuth"]
TARGET = "x86_64-pc-windows-msvc"
DESCS = {
    "netrecon": "Fast network reconnaissance - host discovery & port scanning (Rust)",
    "hashsleuth": "Multi-threaded hash identification & cracking toolkit (Rust)",
}

def api(url):
    req = urllib.request.Request(url, headers={"User-Agent": "bucket-bot"})
    return json.load(urllib.request.urlopen(req, timeout=30))

def sha256_url(url):
    req = urllib.request.Request(url, headers={"User-Agent": "bucket-bot"})
    h = hashlib.sha256()
    with urllib.request.urlopen(req, timeout=120) as r:
        for chunk in iter(lambda: r.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

rel = api(f"https://api.github.com/repos/{OWNER}/{REPO_SRC}/releases/latest")
tag = rel["tag_name"].lstrip("v")
assets = {a["name"]: a["browser_download_url"] for a in rel.get("assets", [])}

for tool in TOOLS:
    asset = f"{tool}-{TARGET}.exe"
    if asset not in assets:
        print(f"{tool}: brak {asset} - pomijam")
        continue
    url = assets[asset]
    manifest = {
        "version": tag,
        "description": DESCS[tool],
        "homepage": f"https://github.com/{OWNER}/{REPO_SRC}",
        "license": "MIT",
        "architecture": {
            "64bit": {"url": url, "hash": sha256_url(url)},
        },
        "bin": f"{tool}.exe",
        "checkver": "github",
        "autoupdate": {
            "architecture": {
                "64bit": {
                    "url": f"https://github.com/{OWNER}/{REPO_SRC}/releases/download/v{{version}}/{tool}-{TARGET}.exe",
                },
            },
        },
    }
    os.makedirs("bucket", exist_ok=True)
    path = f"bucket/{tool}.json"
    old = open(path).read() if os.path.exists(path) else ""
    new = json.dumps(manifest, indent=2)
    if old != new:
        open(path, "w").write(new)
        print(f"{path}: -> v{tag}")
    else:
        print(f"{path}: bez zmian")
