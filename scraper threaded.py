import threading
import time
import concurrent.futures
import requests
import urllib
from bs4 import BeautifulSoup
import ssl
import json
import dbcon

ssl.CERT_REQUIRED = 0

threading = threading.local()

headers = {'User-Agent': 'Mozilla/5.0'}
det_list = []
up_list = []
glob_list_name = []
field_list = ['wmo', 'local_date_time', 'air_temp', 'wind_spd_kmh', 'wind_dir', 'rel_hum', 'rain_trace', 'cloud',
              'lat', 'lon']


def check_locations():
    con = dbcon.connect()
    c = con.cursor()
    c.execute("""SELECT name FROM locations""")
    names = c.fetchall()
    return names


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


field_list = ['wmo', 'local_date_time', 'air_temp', 'wind_spd_kmh', 'wind_dir', 'rel_hum', 'rain_trace', 'cloud',
              'lat', 'lon']

def retrieve_names(url):
    data = requests.get(url, headers=headers)
    resp = data.json()
    resp = resp['observations']['data'][0]
    name = resp['name']
    if name not in glob_list_name and (name not in det_list or name not in up_list):
        for value in field_list:
            det_list.append(resp[value])
        det_list.append(name)
    else:
        for item in field_list:
            up_list.append(resp[item])
        up_list.append(name)


if __name__ == "__main__":
    # check for all existing locations
    glob_loc_names = check_locations()

    # iterate through and remove puncuation
    for x in range(len(glob_loc_names)):
        name = glob_loc_names[x][0]
        glob_list_name.append(name)
    # scrape all the BOM urls
    url_list = scrape_urls()
    # using threading, execute the function and then print the total time
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(retrieve_names, url_list)
    # open a db connection
    con = dbcon.connect()
    c = con.cursor()
    # for every item in the list of names and id's, if the number is even (names),
    # insert it and the item next to it into the database
    for x in range(len(det_list)):
        if x % 11 == 0:
            data = tuple(det_list[x + l] for l in range(0, 11))
            print(data)
            c.execute(
                """INSERT INTO locations (id, date, temp, wind_speed, wind_dir, 
                humidity, rain, cloud, lat, long, name) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                data)
            con.commit()
        else:
            pass
    for p in range(len(up_list)):
        if p % 11 == 0:
            data = tuple(up_list[p + l] for l in range(0, 11))
            name = up_list[p]
            c.execute("""UPDATE locations 
            SET id = ?, date =?, temp=?, wind_speed=?, wind_dir=?, humidity=?,
             rain=?, cloud=?, lat = ?, long = ? WHERE name = ?""",
                      data)
            con.commit()
        else:
            pass
