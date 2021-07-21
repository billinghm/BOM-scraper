from bs4 import BeautifulSoup
import requests
import json

headers = {'User-Agent': 'Mozilla/5.0'}


def scrape_urls():
    target_url = "http://www.bom.gov.au/qld/observations/qldall.shtml"
    page = requests.get(target_url, headers=headers)
    page_data = BeautifulSoup(page.text, 'html.parser')
    a_tags = page_data.find_all('a', href=True)
    href_tags = [i['href'] for i in a_tags]
    location_url = []
    for data in href_tags:
        if data.find('/products') == 0:
            data = data.replace('/products', 'http://bom.gov.au/fwo').replace('shtml', 'json')
            location_url.append(data)
    return location_url


def scrape_names(urls):
    headers = {'User-Agent': 'Mozilla/5.0'}
    for url in urls:
        data = requests.get(url, headers=headers)
        with open('bne.json', 'w') as outfile:
            json.dump(data.json(), outfile)
        resp = data.json()
        air_temp = resp['observations']['data'][0]['air_temp']
        name = resp['observations']['data'][0]['name']
        print("The current temperature at ", name, "is", air_temp)

urls = scrape_urls()
scrape_names(urls)