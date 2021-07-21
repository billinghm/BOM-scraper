import requests
import json

bom_url = "http://www.bom.gov.au/fwo/IDQ60901/IDQ60901.94576.json"
headers = {'User-Agent': 'Mozilla/5.0'}

data = requests.get(bom_url, headers=headers)


with open('bne.json', 'w') as outfile:
    json.dump(data.json(), outfile)

resp = data.json()

print(resp)