
from bs4 import BeautifulSoup
import urllib
import requests
import json
import re

def get_amen_info_from_dict(property_dict, info_str):
    attr_info = None
    group_list = property_dict[u'amenitiesInfo'][u'superGroups']
    for group in group_list:
        for amenity_info in group[u'amenityGroups']:
            if amenity_info[u'groupTitle'] == info_str:
                attr_info = amenity_info[u'amenityEntries']
    return attr_info

def get_amen_val_from_info(attr_info, val_str):
    num_val = None
    for entry in attr_info:
        try:
            if entry[u'amenityName'] == val_str:
                # remove anything not number or decimal
                num_val = int(re.sub("[^\d\.]", "", entry[u'amenityValues'][0]))
        except:
            pass
    return num_val

def get_api_response(query):

    ua_headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    resp = requests.get(query, headers=ua_headers)
    resp_dict = json.loads(resp.text[4:])

    if resp_dict[u'errorMessage'] != u'Success':
        print resp_dict
        print "uh oh"
        exit()

    return resp_dict[u'payload']

# redfin has an internal(?) id that we can use to query more details
def get_listing_id(url):
    base_url = 'http://www.redfin.com/stingray/api/home/details/initialInfo?'
    
    property_url = url.split('http://www.redfin.com')[1]

    params = {'path' : property_url}
    query = base_url + urllib.urlencode(params)
    
    resp_dict = get_api_response(query)

    listing_id = resp_dict[u'listingId']
    
    return listing_id

# returns dictionary
def get_property_details(property_id, listing_id):
    base_url = 'http://www.redfin.com/stingray/api/home/details/belowTheFold?'

    params = {'propertyId' : property_id, 'listingId' : listing_id, 'accessLevel': 1}
    query = base_url + urllib.urlencode(params)
    
    resp_dict = get_api_response(query)

    return resp_dict

def get_price_estimate(property_id, listing_id):
    base_url = 'http://www.redfin.com/stingray/api/home/details/avm?'
    params = {'propertyId' : property_id, 'listingId' : listing_id, 'accessLevel': 1}
    query = base_url + urllib.urlencode(params)

    resp_dict = get_api_response(query)

    try:
        estimate = resp_dict[u'predictedValue']
    except:
        estimate = 'NA'
    return estimate

def get_rent_estimate(property_dict):

    # check if the multi unit info has rent info
    multi_unit_info = get_amen_info_from_dict(property_dict, u'Multi-Unit Information')
    gross_income = get_amen_val_from_info(multi_unit_info, u'Gross Income')

    print gross_income
    # else, query trulia for average rent in zip code
    if gross_income is None:
        pass

def get_num_units(property_dict, property_id):


    # first, check property info
    prop_info = get_amen_info_from_dict(property_dict, u'Property Information')
    num_units = get_amen_val_from_info(prop_info, u'Total # of Units')

    # try a different query
    if num_units is None:
        base_url = 'http://www.redfin.com/stingray/api/home/details/belowTheFold?'
        params = {'propertyId' : property_id, 'accessLevel': 1}
        query = base_url + urllib.urlencode(params)
    
        resp_dict = get_api_response(query)

        unit_info = get_amen_info_from_dict(resp_dict, u'Unit Information')
        num_units = get_amen_val_from_info(unit_info, u'# of Units')

    return num_units


# gets tax rate area code for computing property tax
# uses the parcel num and queries la-county
def get_TRA(parcel_num):

    # query LA county for TRA
    c_query = "http://maps.assessor.lacounty.gov/Geocortex/Essentials/REST/sites/PAIS/SQLAINSearch?f=json&AIN="
    c_query = c_query + parcel_num

    t = requests.get(c_query)

    try:
        parcel_data = json.loads(t.text)[u'results']
        tra = int(parcel_data[u'ParcelDetails'][u'TRA'])
    except:
        tra = "NA"
    #print tra
    return tra