import os
import re
import sys
import requests

FILE_ID = "1OAEiMVp1WqmH9avVtuEB8_5F7qHj1vKD"
OUT = sys.argv[1] if len(sys.argv) > 1 else "TOPbase.h5"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")

s = requests.Session()
s.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})

url = "https://drive.google.com/uc"
params = {"export": "download", "id": FILE_ID}

print("[1] GET", url)
r = s.get(url, params=params, stream=True, allow_redirects=True, timeout=60)
print("    status", r.status_code)
print("    url", r.url[:200])
print("    ctype", r.headers.get("Content-Type"), "clen", r.headers.get("Content-Length"))

ctype = r.headers.get("Content-Type", "") or ""
if "text/html" in ctype:
    body = r.text
    open("first_response.html", "w", encoding="utf-8", errors="replace").write(body)
    print("    html bytes", len(body))
    m = re.search(r"confirm=([0-9A-Za-z_\-]+)", body)
    u = re.search(r'name="uuid" value="([^"]+)"', body)
    a = re.search(r'action="([^"]+)"', body)
    print("    confirm_token", m.group(1) if m else None)
    print("    uuid", u.group(1) if u else None)
    print("    form_action", a.group(1) if a else None)
    q = {"id": FILE_ID, "export": "download", "confirm": (m.group(1) if m else "t")}
    if u:
        q["uuid"] = u.group(1)
    r = s.get("https://drive.usercontent.google.com/download", params=q,
              stream=True, allow_redirects=True, timeout=60)
    print("[2] status", r.status_code, "ctype", r.headers.get("Content-Type"),
          "clen", r.headers.get("Content-Length"))
    if "text/html" in (r.headers.get("Content-Type") or ""):
        open("second_response.html", "w", encoding="utf-8", errors="replace").write(r.text)
        print("    second html bytes", len(r.text))
        print("    snippet:", r.text[:300].replace("\n", " "))
        sys.exit(4)

total = 0
with open(OUT, "wb") as f:
    for chunk in r.iter_content(chunk_size=1 << 20):
        if chunk:
            f.write(chunk)
            total += len(chunk)
            if total % (1 << 24) < (1 << 20):
                print("    wrote", total, flush=True)
print("DONE bytes=%d" % total)
print("size", os.path.getsize(OUT))
