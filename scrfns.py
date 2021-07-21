import dbcon

det_list = []
up_list = []
glob_list_name = []


def check_locations():
    con = dbcon.connect()
    c = con.cursor()
    c.execute("""SELECT name FROM locations""")
    names = c.fetchall()
    return names


def json_to_lst(resp):
    name = resp['observations']['data'][0]['name']
    id = resp['observations']['data'][0]['wmo']
    date = resp['observations']['data'][0]['local_date_time']
    temp = resp['observations']['data'][0]['air_temp']
    wind_speed = resp['observations']['data'][0]['wind_spd_kmh']
    wind_dir = resp['observations']['data'][0]['wind_dir']
    humidity = resp['observations']['data'][0]['rel_hum']
    if name not in glob_list_name and (name not in det_list or name not in up_list):
        det_list.append(name)
        det_list.append(id)
        det_list.append(date)
        det_list.append(temp)
        det_list.append(wind_speed)
        det_list.append(wind_dir)
        det_list.append(humidity)
        return det_list
    else:
        up_list.append(name)
        up_list.append(id)
        up_list.append(date)
        up_list.append(temp)
        up_list.append(wind_speed)
        up_list.append(wind_dir)
        up_list.append(humidity)
        return (up_list)


glob_loc_names = check_locations()
# iterate through and remove puncuation
for x in range(len(glob_loc_names)):
    name = glob_loc_names[x][0]
    glob_list_name.append(name)
