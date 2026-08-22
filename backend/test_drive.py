import urllib.request, json

req = urllib.request.Request(
    'http://127.0.0.1:5000/api/mock-drive/start',
    data=json.dumps({'company_name': 'TCS'}).encode(),
    headers={'Content-Type': 'application/json'}
)
res = urllib.request.urlopen(req)
data = json.loads(res.read())
print(f"Total rounds: {data['total_rounds']}")
for i, r in enumerate(data['rounds']):
    rn = r.get('round_name', f'Round {i+1}')
    diff = r.get('difficulty', '?')
    q = r.get('question', '')[:100]
    print(f"  {rn} [{diff}]: {q}")
