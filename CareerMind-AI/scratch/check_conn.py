import urllib.request
try:
    resp = urllib.request.urlopen("http://localhost:5173/")
    print("STATUS:", resp.getcode())
except Exception as e:
    print("ERROR:", e)

