import json

d = {}

with open('besh.json', 'r') as f:
    d = json.load(f)

lis = d['movies']
newlis = []

for i in lis:
    i['id'] = int(i['id'])
    newlis.append(i)

d['movies'] = newlis

# with open('besh.json', 'w') as f:
#     json.dump(
#         d, f
#     )