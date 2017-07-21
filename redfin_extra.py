
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
            '#units',
            'price_estimate',
            'rent_estimate']

for col in new_cols:
    property_df[col] = property_df.index


# create new df with filtered results
new_df = pd.DataFrame(columns = property_df.columns.values)


start_time = time.time()
for n in range(len(property_df)):

    url = property_df.loc[n]['URL']
    #url = 'http://www.redfin.com/CA/Los-Angeles/669-W-31st-St-90731/home/7696251'
    #url = 'http://www.redfin.com/CA/Upland/1150-E-Arrow-Hwy-91786/home/4008568'
    
    try:
        listing_id = get_listing_id(url)
    except:
        # not for sale anymore?
        property_df.loc[n, new_cols] = ['OM']*len(new_cols)
        continue

    property_id = url.split("/")[-1]

    property_dict = get_property_details(property_id, listing_id)

    parcel_num = get_parcel_num(property_dict)
    if parcel_num > 100000000000:
        # probably off market
        property_df.loc[n, new_cols] = ['OM']*len(new_cols)
        continue
    property_df.loc[n, 'parcel'] = parcel_num

    # now lookup full tax rate using TRA code
    TRA = get_TRA(parcel_num)
    tax_rate = get_tax(TRA, tax_df)

    if tax_rate == "NA":
        # not in LA county
        property_df.loc[n, 'tax_rate'] = 1.00

    property_df.loc[n, 'tax_rate'] = tax_rate
 
    property_df.loc[n, '#units'] = get_num_units(property_dict, property_id)

    avm_dict = get_avm_info(property_id, listing_id)

    property_df.loc[n, 'price_estimate'] = get_price_estimate(property_id, listing_id, avm_dict)
    
    property_df.loc[n, 'rent_estimate'] = get_rent_estimate(property_dict, property_df.loc[n]['ZIP'])

    #ToDo: clean up bed/sqft columns
    num_beds = get_num_beds(property_dict, avm_dict)
    if num_beds != "NA":
        property_df.loc[n, 'BEDS'] = num_beds

    sqft = get_sqft(property_dict, avm_dict)
    if sqft != "NA":
        property_df.loc[n, 'SQUARE FEET'] = sqft

    # Append valid obs to new df
    new_df.loc[len(new_df.index)] = property_df.loc[n]

    print n

end_time = time.time()
property_df.to_csv('extra.csv', index = False)
new_df.to_csv('filtered.csv', index = False)

print "total time", end_time - start_time
    

