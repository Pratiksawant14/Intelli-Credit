import urllib.request as r
import json

req = r.Request('http://localhost:8000/api/v1/score/', data=b'{"raw_text":"test", "document_data":{}}', headers={'Content-Type':'application/json'})
res = json.loads(r.urlopen(req).read().decode())
print(json.dumps(res, indent=2))
