
# pretty much ripped from google map JS and trulia JS

import numpy as np
import requests
import json
from bs4 import BeautifulSoup
import gc

# the idea is that we're extremely zoomed in on our target location
# and trulia api should ideally just return 1 result
map_zoom = 19

def normalize_coord(val):
    i = np.sqrt(4**map_zoom)

    if map_zoom > 0:
        while val > i or val < 0:
            if val > i:
                val = val - i
            elif val < 0:
                val = val + i

    return val

def from_latlng_to_pt(loc):
    def bound(a, b, c):
        new_val = max(a, b)
        new_val = min(new_val, c)
        return new_val

    # ???
    j = 256. / 360
    l = 256. / (2*np.pi)
    c = [128, 128]

    b = [0, 0]
    b[0] = c[0] + loc[1] * j

    a = bound(np.sin(loc[0]*np.pi/180), -(1-1e-15), 1-1e-15)

    b[1] = c[1] + 0.5*np.log( (1+a)/(1-a) ) * -l

    return b

def get_pix_coords(loc):
    n = 2**map_zoom

    r = from_latlng_to_pt(loc)

    coord = [r[0]*n, r[1]*n]
    return coord

def get_tile_coords(loc):
    n = get_pix_coords(loc)

    tile_size = 256
    coord = [int(np.floor(n[0]/tile_size)), int(np.floor(n[1]/tile_size))]
    return coord

def get_data_url(tile_coord):
    base_url = 'https://tiles.trulia.com/'
    #map_type_str = 'tiles/home_prices_listings_data'
    map_type_str = 'tiles/rental_prices_data'

    # check this manually
    version = '20170307'

    final_url = base_url + map_type_str + '/{}/{}/{}.json?v={}'.format(map_zoom, \
                                        normalize_coord(tile_coord[0]), \
                                        normalize_coord(tile_coord[1]), version)

    return final_url

# returns rent per bedroom
def get_rent_for_location(loc):

    tile_coord = get_tile_coords(loc)

    query_url = get_data_url(tile_coord)

    resp = requests.get(query_url)
    resp_dict = json.loads(resp.text)
    
    rent_val = resp_dict[u'data'][u'1'][u'pc_median_price_per_bed']
    return rent_val

def get_rent_for_zip(zip_code):
    base_url = 'https://www.trulia.com/real_estate/'
    full_url = base_url + str(int(zip_code)) + '-a'

    resp = requests.get(full_url)
    soup_obj = BeautifulSoup(resp.text, 'lxml')

    rent_txt = str(soup_obj.find('p', text='Median Rent Per Month')\
                .previous_sibling.previous_sibling.contents[0])

    rent_txt = rent_txt.strip()
    rent_txt = rent_txt.replace('$', '').replace(',', '')

    # beautifulsoup memory leak?
    gc.collect()

    return rent_txt
# example usage

# # lat, lon
# loc = [34.066473, -118.138482]

# print get_rent_for_location(loc)
