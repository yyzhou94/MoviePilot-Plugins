import os, base64, json, urllib.request, urllib.error

TOKEN = os.environ.get("GHTOKEN")
OWNER = "yyzhou94"
REPO = "MoviePilot-Plugins"
API = "https://api.github.com"
BRANCH = "main"
ROOT = r"C:/Users/yyzhou/WorkBuddy/2026-10-12-10-37-31/groupchatzone-plugin"

# 收集除 .git / __pycache__ 外的所有文件
files = []
for dp, dn, fn in os.walk(ROOT):
    if ".git" in dp or "__pycache__" in dp:
        continue
    for f in fn:
        full = os.path.join(dp, f)
        rel = os.path.relpath(full, ROOT).replace("\\", "/")
        files.append(rel)
files.sort()

proxy = urllib.request.ProxyHandler({"https": "http://127.0.0.1:49433"})
opener = urllib.request.build_opener(proxy)

ok = 0
for rel in files:
    full = os.path.join(ROOT, rel)
    with open(full, "rb") as fh:
        data = fh.read()
    b64 = base64.b64encode(data).decode("ascii")
    body = json.dumps({"message": f"add {rel}", "content": b64, "branch": BRANCH}).encode("utf-8")
    url = f"{API}/repos/{OWNER}/{REPO}/contents/{rel}"
    req = urllib.request.Request(url, data=body, method="PUT", headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.github+json",
        "User-Agent": "push-script",
    })
    try:
        resp = opener.open(req, timeout=30)
        print(f"OK   {rel}  ({resp.status})")
        ok += 1
    except urllib.error.HTTPError as e:
        print(f"ERR  {rel}  {e.code}  {e.read().decode('utf-8','replace')[:240]}")
    except Exception as e:
        print(f"EXC  {rel}  {e}")

print(f"--- done: {ok}/{len(files)} files uploaded ---")
