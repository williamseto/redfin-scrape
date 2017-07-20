
import pandas as pd
from utils import *
import time

def get_tax(TRA, tax_df):

    tax = "NA"
    try:
        # col 1 is TRA
        tra_cats = tax_df.loc[tax_df[1] == TRA]
        tax = tra_cats[3].sum()

    except:
        pass

    return tax

property_csv = 'multifamily.csv'
property_df = pd.read_csv(property_csv)

# read tax rate csv
tax_csv = 'TRA-2016-2017.csv'
tax_df = pd.read_csv(tax_csv, header=None)

# add some more columns
new_cols = ['parcel',
            'tax_rate',
            '#units'
            'price_estimate',
            'rent_estimate']

for col in new_cols:
    property_df[col] = property_df.index


# create new df with filtered results
new_df = pd.DataFrame(columns = property_df.columns.values)


start_time = time.time()
for n in range(len(property_df)):

    url = property_df.loc[n]['URL']
    url = 'http://www.redfin.com/CA/Lynwood/3310-Burton-Ave-90262/unit-A/home/7356569'

    listing_id = get_listing_id(url)
    property_id = url.split("/")[-1]

    property_dict = get_property_details(property_id, listing_id)

    extra_data = []

    parcel_num = property_dict[u'publicRecordsInfo'][u'basicInfo'][u'apn']
    extra_data.append(parcel_num)

    TRA = get_TRA(parcel_num)
    # now lookup full tax rate using TRA code
    tax_rate = get_tax(TRA, tax_df)
    extra_data.append(tax_rate)
    
    num_units = get_num_units(property_dict, property_id)
    extra_data.append(num_units)

    price_estimate = get_price_estimate(property_id, listing_id)
    extra_data.append(price_estimate)

    
    get_rent_estimate(property_dict)
    exit()
    

