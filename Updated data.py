#!/usr/bin/env python
# coding: utf-8

# In[1]:


import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import geopandas as gp
import shapely
import fiona

shp_file_name = "NSW_LOCALITY_POLYGON_shp/NSW_LOCALITY_POLYGON_shp.shp"
zip_file_name = "nsw_locality_polygon_shp.zip"
web_file_path = ("https://data.gov.au/dataset/91e70237-d9d1-4719-a82f-e71b811154c6/resource/"
                 "5e295412-357c-49a2-98d5-6caf099c2339/download/nsw_locality_polygon_shp.zip")


# In[2]:


get_ipython().run_line_magic('matplotlib', 'inline')
plt.rcParams['figure.figsize'] = (20,10)


# In[3]:


import matplotlib.style as style
style.available
style.use('fivethirtyeight')


# # Setting up notebook
# > Importing plotting styles and maps data for plotting.
# 

# In[4]:


def unzip_zipfile(zipped_file_path, put_it_here="."):
    import zipfile
    zip_of_suburbs = zipfile.ZipFile(zipped_file_path, 'r')
    zip_of_suburbs.extractall(put_it_here)
    zip_of_suburbs.close()


# In[5]:


# unzipping the file
if os.path.isfile(shp_file_name):
    print("loading from file")
else:
    if os.path.isfile(zip_file_name):
        print("unzipping")
        unzip_zipfile(zip_file_name)
    else:
        import requests
        print("loading from the internet")
        page = requests.get(web_file_path)
        with open(zip_file_name, 'wb') as z:
            z.write(page.content)
        unzip_zipfile(zip_file_name)

print("done")


# In[38]:


burbs = gp.GeoDataFrame.from_file(shp_file_name)
burbs.columns
burbs.sample(3)


# In[6]:


saved_style_state = matplotlib.rcParams.copy()


# # Importing Airbnb Dataset
# > Imported Dataset of listings from 10 July, 2019.

# In[7]:


air_bnb = pd.read_csv("listings.csv")
# , dtype={'user_id': int}


# In[8]:


# how many rows and columns are in the airbnb dataset?
air_bnb.shape


# In[9]:


# all the names of the columns
air_bnb.columns


# In[10]:


# display all 106 columns 
pd.set_option('display.max_columns', 106)


# ### Tidying Up Dataset
# > Using user-defined functions to tidy up elements in columns. 

# In[11]:


def float_str_to_int(str1):
    try:
        a = str(str1)
        a = a.strip( '.00' )
        a = a.strip('$')
        a = ''.join(a.split(','))
        if str1 == "$0.00":
            return 0
    #     a = a.strip(' ')
        return int(a.strip(' '))
    except Exception as e:
        print(e)
        import pdb; pdb.set_trace()
        return str1
#     return int(float(a))


# In[12]:


def remove(str1):
    a = str(str1)
    a = a.strip( 'NSW' )
    a = a.strip('.0')
    a = a.split('\n')
    if a == "nan":
        return a 
    return a


# In[94]:


def convert_to_integer_for_price(row):
    x = row.price
    if type(x) is str:
        if type(x) is float:
            new_x = int(x)
            return new_x 
        return int(x)
    return int(x)

air_bnb["price"] = air_bnb.apply(convert_to_integer_for_price,axis=1)
air_bnb.sample(5)


# In[95]:


def clean_up_simple_postcode(row):
    k = row.simple_postcode
    if type(k) is str:
        if "\n2766" in k:
            return k[:4]
        else:
            return k
    else:
        return k

air_bnb["simple_postcode"] = air_bnb.apply(clean_up_simple_postcode,axis=1)
air_bnb.sample(5)


# In[13]:


def simplify_postcodes(row):
    z = row.zipcode
    if type(z) is str:
        if "NSW " in z:
            return z[4:]
        else:
            return z
    elif type(z) is float and not np.isnan(z):
        return str(int(z))
    else:
        return "0000"

air_bnb["simple_postcode"] = air_bnb.apply(simplify_postcodes,axis=1)
air_bnb.sample(5)


# In[14]:


def simplify_host_response(row):
    y = row.host_response_rate
    if type(y) is str:
        no_p = y.strip('%')
        return no_p
    elif type(y) is float and not np.isnan(y):
        no_p = y.strip('%')
        return str(int(no_p))
    else:
        return "0"

air_bnb["simple_host_response_rate"] = air_bnb.apply(simplify_host_response,axis=1)


# In[15]:


air_bnb.head()


# ## Which suburb has the worst response rate?
# >Which suburb in NSW has 0% response rate?

# In[133]:


air_bnb.simple_host_response_rate.value_counts().plot()
plt.title('Host response rate')
plt.ylabel('Number of responses')
plt.xlabel('Percentage %')


# In[17]:


# which suburb is the worst at responding?
air_bnb.simple_host_response_rate.value_counts()[0]


# In[18]:


# which suburb is the worst at responding?
def zero_response_rate(column):
    for x in column:
        if x =="0":
            return True
    return False

zero_response_rate(air_bnb.simple_host_response_rate)


# In[19]:


# made a new column 
air_bnb["zero_response_rate"] = air_bnb.apply(zero_response_rate,axis=1)
air_bnb.sample(2)


# In[20]:


# only used the true values from the new column
zeroresponse = air_bnb[air_bnb["zero_response_rate"]]


# In[134]:


which_suburb_zero_responses = zeroresponse.groupby("simple_postcode").sum().host_listings_count.plot(kind="bar")
plt.title('Surburbs and the number of 0% responses')
plt.ylabel('Number of responses')
plt.xlabel('Postcodes')
plt.rcParams['figure.figsize'] = (20.0, 10.0)


# In[22]:


zero_response_sum = zeroresponse.groupby("simple_postcode").sum()


# In[23]:


# which suburb has the worst response rate?
hl = zero_response_sum["host_total_listings_count"].value_counts()
zero_response_sum["host_total_listings_count"][zero_response_sum["host_total_listings_count"]>1000].plot(kind="bar")
plt.title("Which suburb has the worst response rate?")
plt.ylabel('Number of responses')
plt.xlabel('Postcode')


# ## Number of Airbnbs in each city
# > Bondi Beach seems to have the highest number of airbnbs at first analysis. 

# In[24]:


# how many cities are there?
air_bnb["city"].value_counts()


# In[135]:


# How many airbnbs in each city?
air_bnb["city"].value_counts().plot(kind="bar");
plt.title("Airbnbs in each city")
plt.ylabel('Number of airbnbs')
plt.xlabel('City name')


# In[26]:


# what type of cancellation policies were there?
air_bnb["cancellation_policy"].value_counts()


# ## What are the cancellation policies?

# In[136]:


air_bnb["cancellation_policy"].value_counts().plot(kind="bar")
plt.title('Cancellation Policy')
plt.ylabel('Number of airbnbs under category')
plt.xlabel('Catergoies of Cancellation Policy')


# ## Do any of the Airbnbs offer experiences?
# > Seems like no airbnbs offer any experiences. 

# In[28]:


air_bnb["experiences_offered"].value_counts()


# In[137]:


# did any airbnbs offer experiences?
air_bnb["experiences_offered"].value_counts().plot(kind="area");
plt.title('Experiences Offered')
plt.ylabel('Amount of certain experiences')
plt.xlabel('Experiences')


# ## What beds do hosts usually provide?
# > What kinds of beds are there? 

# In[138]:


# different bed types offered by airbnb hosts 
air_bnb["bed_type"].value_counts().plot(kind="bar")
plt.title('Different types of beds offered by airbnb hosts')
plt.ylabel('Number of each type of beds')
plt.xlabel('Types of Bed')


# In[31]:


# how many futon beds are there?
def find_futon_number(column):
    count = 0
    for x in column:
        if x =="Futon":
            count+=1
#             print(count)
    return count
            
find_futon_number(air_bnb.bed_type)
# air_bnb["bed_type"== Futon].value_counts().plot(kind="bar")


# In[32]:


# What suburb are they in?
def futon_suburb(column):
    for x in column:
        if x =="Futon":
            return True
    return False

futon_suburb(air_bnb.bed_type)


# In[33]:


air_bnb["Futon"] = air_bnb.apply(futon_suburb,axis=1)
air_bnb.sample(10)


# In[34]:


# finding out which suburb the futons are located in
# a file of all the airbnbs with futons
futonBNB = air_bnb[air_bnb["Futon"]]


# In[35]:


futonBNB


# In[139]:


sum_of_futon_in_suburb = futonBNB.groupby("simple_postcode").sum().host_listings_count.plot(kind="bar")
plt.title('Total Number of Futons in a Suburb')
plt.ylabel('Number of Futons')
plt.xlabel('Postcode')


# > The Futons are spread evenly across NSW.

# In[140]:


# Where the futons are
futonBNB.plot(kind="scatter", x="longitude", y="latitude", alpha=0.4)
plt.title('Are these futons clustered?')
plt.show()


# In[39]:


# Suburbs with the highest amount of Futons
burbs = gp.GeoDataFrame.from_file(shp_file_name)
burbs.drop(["NSW_LOCA_1", "NSW_LOCA_3", "NSW_LOCA_4", "DT_RETIRE"], axis=1, inplace=True)
air_bnb_burbs = (burbs[burbs.NSW_LOCA_2 == "NORTH BONDI"])
air_bnb_burbs.head()
air_bnb_burbs.plot()
plt.title("NORTH BONDI")


# In[40]:


# which suburb has the most futons
burbs = gp.GeoDataFrame.from_file(shp_file_name)
air_bnb_burbs = burbs[burbs.NSW_LOCA_2 == "MARRICKVILLE"]
air_bnb_burbs.head()
air_bnb_burbs.plot()
plt.title("MARRICKVILLE")


# ### Where do those hosts live?
# > With the exception of some not providing their location, most hosts live in Sydney City. 

# In[158]:


futonBNB["host_location"].value_counts().plot(kind="bar");
plt.title("Where the hosts that offer Futons as beds live")
plt.ylabel('Number of Hosts')
plt.xlabel('Suburb')


# ## What types of accommodation is offered?

# In[161]:


# different types of accomodation offered 
air_bnb["room_type"].value_counts().plot(kind="bar")
plt.title("Types of airbnbs offered in each suburb")
plt.ylabel('Amount of type')
plt.xlabel('Types of airbnbs')


# In[45]:


# is it an entire home, private room or shared room?
def entirehome(column):
    for x in column:
        if x =="Entire home/apt":
            return True
    return False
    
entirehome(air_bnb.room_type)


# In[159]:


air_bnb["Entire_home"] = air_bnb.apply(entirehome,axis=1)
air_bnb.sample(5)


# In[47]:


entirehomeBNB = air_bnb[air_bnb["Entire_home"]]


# In[162]:


mean_of_entirehomes_in_suburb = entirehomeBNB.groupby("simple_postcode").mean().host_listings_count.plot(kind="bar")
plt.title("Average of entire homes offered in a suburb")
plt.ylabel('Number of entired homes')
plt.xlabel('Suburb')


# In[50]:


# is it an entire home or shared room?
def sharedhome(column):
    for x in column:
        if x =="Private room" or x =="Shared room":
            return True
    return False

sharedhome(air_bnb.room_type)


# In[51]:


air_bnb["Shared"] = air_bnb.apply(sharedhome,axis=1)
air_bnb.sample(10)


# In[52]:


sharedhomeBNB = air_bnb[air_bnb["Shared"]]


# In[163]:


sharedhomeBNB.sample(5)


# In[164]:


mean_of_sharedhomes_in_suburb = sharedhomeBNB.groupby("simple_postcode").mean().host_listings_count.plot(kind="bar")
plt.title("Average of shared homes/rooms in a Suburb")
plt.ylabel('Number of shared homes/rooms')
plt.xlabel('Suburb')


# In[165]:


# ratio of entire homes to shared homes in different suburbs
mean_of_entirehomes_in_suburb = entirehomeBNB.groupby("simple_postcode").mean().host_listings_count.plot(kind="bar",facecolor='pink')
mean_of_sharedhomes_in_suburb = sharedhomeBNB.groupby("simple_postcode").mean().host_listings_count.plot(kind="line")
plt.title('Different bed types offered by airbnb hosts (Pink=Entire Homes Blue=Shared Homes)')
plt.ylabel('Number of beds types')
plt.xlabel('Bed types')


# In[57]:


air_bnb.price = air_bnb.price.apply(float_str_to_int)


# In[62]:


type(air_bnb.price.iloc[0])


# In[63]:


some_numbers = pd.Series(range(100))
some_numbers.head()


# In[64]:


some_numbers[some_numbers < 8]


# In[65]:


some_numbers[(some_numbers < 4) | (some_numbers > 97)]


# ## Which suburbs have the least amount of Airbnbs?

# In[66]:


air_bnb["zipcode"].value_counts()


# In[67]:


air_bnb["zipcode"].value_counts().plot(kind="bar")


# In[68]:


abz = air_bnb["zipcode"].value_counts()
abz[abz < 2000].plot(kind="bar")


# In[69]:


abz = air_bnb["zipcode"].value_counts()
abz[abz < 200].plot(kind="bar")


# In[70]:


abz = air_bnb["zipcode"].value_counts()
abz[abz < 100].plot(kind="bar")


# In[71]:


abz = air_bnb["zipcode"].value_counts()
abz[abz < 50].plot(kind="bar")


# In[72]:


abz = air_bnb["zipcode"].value_counts()
abz[abz < 20].plot(kind="bar")


# In[73]:


abz = air_bnb["zipcode"].value_counts()
abz[abz < 10].plot(kind="bar")


# In[74]:


air_bnb.zipcode = air_bnb.zipcode.apply(remove)


# In[75]:


abz = air_bnb["zipcode"].value_counts()
abz[abz < 10].plot(kind="bar")


# In[76]:


# # suburbs with least amount of airbnbs
# abz = air_bnb["zipcode"].value_counts()
# abz[abz > 10].plot(kind="bar")


# In[77]:


air_bnb[air_bnb['zipcode']==1]['price'] 


# In[78]:


mu, sigma = 100, 15
x = mu + sigma*np.random.randn(10000)


# In[80]:


# the histogram of the data
plt.hist(x, 50, density=True, facecolor='pink', alpha=0.75)
plt.xlabel('Postcode')
plt.ylabel('Frequency')
plt.title(r'$\mathrm{Histogram\ of\ Postcodes:}\ \mu=100,\ \sigma=15$') # allows for latex formatting
# plt.axis([40, 160, 0, 0.03])
plt.grid(True)
plt.show()


# ## The amount of Airbnbs in NSW costing less than $200

# In[81]:


# amount of airbnbs with prices lower than $200
capped_price_data = air_bnb["price"][air_bnb["price"] < 200]

plt.hist(capped_price_data)
plt.show()


# In[82]:


capped_price_data =air_bnb["price"][air_bnb["price"] < 200]

plt.hist(capped_price_data, bins=10, facecolor='pink', alpha=0.2) #<-old one
plt.hist(capped_price_data, bins=50, facecolor='orange', alpha=1)  #<-new one
plt.show()


# ## What's the average price of airbnbs in a suburb?

# In[179]:


# the average price of airbnbs in suburb
average_price = air_bnb.groupby("simple_postcode").mean().price.plot(kind="bar")
# average price of suburbs
average_price.plot()
plt.title('Average Price of Airbnbs in a Suburb')
plt.ylabel('Price $')
plt.xlabel('Suburbs')
plt.rcParams['figure.figsize'] = (20.0, 10.0)


# In[87]:


# most expensive airbnb is in 2756
average_price.sort_values(ascending = False)


# ## Average number of people a house accomodates

# In[89]:


# how many people a house accommodates
air_bnb.accommodates.plot()
plt.title('Amount of people each airbnb accommodates')
plt.ylabel('Amount of people')
plt.xlabel('ID')


# In[93]:


ac = air_bnb.accommodates.value_counts()
print(ac)


# In[182]:


average_accomodates = air_bnb.groupby("simple_postcode").mean().accommodates.plot(kind="bar")
plt.title('Average amount of guests a house can accomodate in a suburb')
plt.ylabel('Number of guests')
plt.xlabel('Postcode')


# ### Grouping by postcodes

# In[96]:


# groupby and aggregate 
# max or mean 
air_bnb_post = air_bnb.groupby(["simple_postcode"]).mean()


# In[97]:


air_bnb_sum = air_bnb.groupby(["simple_postcode"]).sum()


# In[191]:


air_bnb_sum.sample(5)


# ## Comparison of top 3 suburbs with most airbnbs and top 3 suburbs with highest income

# In[99]:


number_of_homes = air_bnb_sum["host_listings_count"]
# plt.xkcd()
plt.plot(number_of_homes, "x-")
plt.title("Number of houses in a suburb", fontsize=18)
plt.xlabel('Postcode', fontsize=26)
plt.ylabel('Number of houses', fontsize=26)
plt.grid(True)
plt.show()


# In[100]:


# shows the top 3 suburbs containing the most airbnbs
number_of_homes = air_bnb_sum.host_listings_count[air_bnb_sum.host_listings_count>int(20000)]
# plt.xkcd()
plt.plot(number_of_homes, "x-")
plt.title("Number of houses in a suburb", fontsize=18)
plt.xlabel('Postcode', fontsize=26)
plt.ylabel('Number of houses', fontsize=26)
plt.grid(True)
plt.show()


# In[101]:


income = air_bnb_sum["price"]
# plt.xkcd()
plt.plot(income, "x-")
plt.title("Income of each suburb", fontsize=18)
plt.xlabel('Postcode', fontsize=26)
plt.ylabel('Income', fontsize=26)
plt.grid(True)
plt.show()


# In[102]:


number_of_homes = air_bnb_sum.price[air_bnb_sum.price>int(200000)]
# plt.xkcd()
plt.plot(number_of_homes, "x-")
plt.title("Income of each suburb", fontsize=18)
plt.xlabel('Postcode', fontsize=26)
plt.ylabel('Income', fontsize=26)
plt.grid(True)
plt.show()


# Postcode | Number of Houses in each suburb | Income
#      --- | :---:                            | ---
# 2010     | 21000                           | $210000
# 2026     | 26000                           | $490000

# ## Are Airbnbs with Chinese characters in their description cheaper or more expensive?
# > u'[\u4e00-\u9fff] searches for chinese and japanese characters in a string.

# In[104]:


# Air_bnb's with chinese characters in their description 
import re
def find_chinese(row):
    for x in (row):
        if re.search(u'[\u4e00-\u9fff]', str(x)):
            print ('found chinese character in ' + str(x))
    return str(x)

find_chinese(air_bnb.description)


# In[105]:


def find_chinese(row):
    for x in (row):
        if re.search(u'[\u4e00-\u9fff]', str(x)):
            print ('found chinese character in ' + str(x))
            return True
    return False


# In[106]:


air_bnb["Chinese_char_in_row"] = air_bnb.apply(find_chinese,axis=1)
air_bnb.sample(10)


# In[107]:


# summing up the prices for airbnbs with chinese description
# a file of all the airbnbs with chinese characters 
chairBNB = air_bnb[air_bnb["Chinese_char_in_row"]]
# plotting the price and ID of Air-bnbs
chairBNB.price.plot()
plt.title("Prices of Airbnbs with Chinese characters in their description", fontsize=18)
plt.xlabel('ID', fontsize=26)
plt.ylabel('Price', fontsize=26)
plt.grid(True)
plt.show()


# In[108]:


# Which suburb has the most houses with chinese descriptions?
chairBNBpost = chairBNB.groupby("simple_postcode")
cbs = chairBNBpost.host_listings_count.sum()
cbs[cbs>2000].plot(kind="bar")


# In[109]:


# average price for airbnb with chinese characters in description 
chairBNB.price.mean()


# In[110]:


# no chinese characters in description
def find_english(row):
    for x in (row):
        if re.search(u'[\u4e00-\u9fff]', str(x)):
#             print ('found chinese character in ' + str(x))
            return False
    return True


# In[111]:


air_bnb["No_chinese_char_in_row"] = air_bnb.apply(find_english,axis=1)
air_bnb.sample(5)


# In[112]:


nochairBNB = air_bnb[air_bnb["No_chinese_char_in_row"]]
# plotting the price and ID of Air-bnbs
nochairBNB.price.plot()
plt.title("Prices of Airbnbs with No Chinese characters in their description", fontsize=18)
plt.xlabel('ID', fontsize=26)
plt.ylabel('Price', fontsize=26)
plt.grid(True)
plt.show()


# In[113]:


# Which suburb has the most houses with english descriptions?
nochairBNBpost = nochairBNB.groupby("simple_postcode")
ncbs = nochairBNBpost.host_listings_count.sum()
ncbs[ncbs>2000].plot(kind="bar")


# cbp = chairBNBpost.sum().host_listings_count>.plot(kind="bar")


# In[114]:


nochairBNB.price.mean()


# ## Maping time

# In[91]:


burbs = gp.GeoDataFrame.from_file(shp_file_name)
burbs.drop(["NSW_LOCA_1", "NSW_LOCA_3", "NSW_LOCA_4", "DT_RETIRE"], axis=1, inplace=True)
air_bnb_burbs = burbs[burbs.NSW_LOCA_2 == ""]
air_bnb_burbs.head()
# air_bnb_burbs.plot()


# In[183]:


burbs = gp.GeoDataFrame.from_file(shp_file_name)
burbs.columns
burbs.sample(5)


# In[116]:


def clean_up_postcode_for_maps(row):
    k = row.LOC_PID
    if type(k) is str:
        if "NSW" in k:
            return k.strip('NSW')
        else:
            return k
    else:
        return k

burbs["LOC_PID"] = burbs.apply(clean_up_postcode_for_maps,axis=1)
burbs.sample(5)


# In[117]:


# joining datasets together 
merged = burbs.set_index("LOC_PID").join(air_bnb_post)
merged.sample(6)


# ## Which suburb has the largest accomodation?

# In[118]:


variable = "guests_included"
vmin, vmax = 0, 20
fig, ax = plt.subplots(1, figsize=(10, 6))
merged.plot(column=variable, cmap="Blues", linewidth=0.8, ax=ax, edgecolor="0.8")


# In[119]:


variable = "guests_included"
vmin, vmax = 0, 50
fig, ax = plt.subplots(1, figsize=(10, 6))
merged.plot(column=variable, cmap="Blues", linewidth=0.8, ax=ax, edgecolor="0.8")
ax.axis("off")


# In[120]:


variable = "guests_included"
vmin, vmax = 120, 220
fig, ax = plt.subplots(1, figsize=(10, 6))
merged.plot(column=variable, cmap="Blues", linewidth=0.8, ax=ax, edgecolor="0.8")
ax.axis("off")
# add a title
ax.set_title("Number of guests included in Airbnbs", fontdict={"fontsize": "25", "fontweight" : "3"})
# create an annotation for the data source
ax.annotate("Map of NSW", xy=(0.1, .08), xycoords="figure fraction", ha="left", va="top", fontsize=12, color="#555555")


# In[121]:


variable = "guests_included"
vmin, vmax = 120, 220
fig, ax = plt.subplots(1, figsize=(10, 6))
merged.plot(column=variable, cmap="Blues", linewidth=0.8, ax=ax, edgecolor="0.8")
ax.axis("off")
# add a title
ax.set_title("Number of guests included in Airbnbs", fontdict={"fontsize": "25", "fontweight" : "3"})
# create an annotation for the data source
ax.annotate("Map of NSW", xy=(0.1, .08), xycoords="figure fraction", ha="left", va="top", fontsize=12, color="#555555")
# Create colorbar as a legend
sm = plt.cm.ScalarMappable(cmap="Blues", norm=plt.Normalize(vmin=vmin, vmax=vmax))
# empty array for the data range
sm._A = []
# add the colorbar to the figure
cbar = fig.colorbar(sm)


# In[122]:


def add_centroid(row):
    return row.geometry.centroid

burbs["centroid"] = burbs.apply(add_centroid, axis=1)


# In[123]:


a = burbs.iloc[0]
print(a.centroid)
a.centroid


# In[187]:


this_point = shapely.geometry.point.Point(144.3,-34.45)
burbs["distance_from_Maude"] = burbs.geometry.distance(this_point)


# In[189]:


burbs.distance_from_Maude.hist(bins=50);
plt.title("Distance from Maude", fontsize=18)
plt.xlabel('Lat Long', fontsize=26)
plt.grid(True)
plt.show()


# In[126]:


close_burbs = burbs[burbs.distance_from_Maude<1]
close_burbs.plot();


# In[127]:


close_burbs.geometry.convex_hull.plot();


# In[128]:


close_burbs.geometry.envelope.plot();


# In[129]:


really_close_burbs = burbs[burbs.distance_from_Maude<0.6]
really_close_burbs.plot()

for idx, row in really_close_burbs.iterrows():
    plt.annotate(row.NSW_LOCA_2, xy=tuple(row.centroid.coords)[0], ha='center')
plt.title('Suburbs near town with largest accomodation')


# In[130]:


print(this_point)
in_this_burb = None
for _, row in really_close_burbs.iterrows():
    if this_point.within(row.geometry):
        in_this_burb = row
        
in_this_burb


# In[131]:


in_this_burb = really_close_burbs[really_close_burbs.apply(lambda x: this_point.within(x.geometry) , axis=1)]
in_this_burb


# In[132]:


really_close_burbs.plot(column='distance_from_Maude', cmap='Pastel1');


# # END OF PRESENTATION
# > In conclusion, the Airbnb Dataset was an interesting dataset to analyse because of the diversity of information it provides. It informed me that it was cheaper to hire airbnbs with chinese characters in the description, go to Marrickville or Bondi for a Futon bed and much more. 
