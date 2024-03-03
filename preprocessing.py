import os, re
from unidecode import unidecode
from geonamescache import GeonamesCache
import pandas as pd
import utility.utilities
from sklearn.cluster import KMeans, DBSCAN
import matplotlib.pyplot as plt
import cartopy
from cartopy.crs import PlateCarree

data_file = os.path.join(os.path.dirname(__file__), "data/headlines.txt")

with open(data_file, "r") as file:
    headlines = [line.strip() for line in file.readlines()]
    
gc = GeonamesCache()

countries = [country['name'] for country in gc.get_countries().values()]
country_to_name = {utility.utilities.name_to_regex(name): name for name in countries}
cities = [city['name'] for city in gc.get_cities().values()]
city_to_name = {utility.utilities.name_to_regex(name): name for name in cities}

matched_countries = [utility.utilities.get_name_in_text(headline, country_to_name) for headline in headlines]
matched_cities = [utility.utilities.get_name_in_text(headline, city_to_name) for headline in headlines]


data = {'Headline': headlines, 'City': matched_cities, 'Country': matched_countries}
df = pd.DataFrame(data)
df['Cities'] = df['Headline'].apply(lambda x: utility.utilities.get_cities_in_headline(x, city_to_name))
df['Num_Cities'] = df['Cities'].apply(len)
df_multiple_cities = df[df.Num_Cities > 1]
df['City'] = df['Cities'].apply(utility.utilities.get_longest_city)
short_cities = df[df.City.str.len() <= 4][['City', 'Headline']]

"""
Since all headlines with country name also have city name we can assign a latitude
and logitude without relying on country central coordinates
df[df.Country.notnull()]['City','Country','Headline'] 
Total = 15
"""
df.drop('Country', axis = 1, inplace = True)

"""
39 healdines (6%) of data where city was not identified by GeonamesCache.Since 
missing data is small we can drop off these healines
df[df.City.isnull()]
"""
df = df[~df.City.isnull()][['City', 'Headline']]

latitudes, longitudes = utility.utilities.get_lat_log(df = df, geocache= gc)
df = df.assign(Latitude = latitudes, Longitude= longitudes)

"""
utility.utilities.give_elbow_curve(df= df)
With K = 3 we were getting wrong clusters even though elbow method gave 3. 

df['Cluster'] = KMeans(3).fit_predict(df[['Latitude', 'Longitude']])
utility.utilities.plot_clusters(clusters= df['Cluster'], 
                                longitudes= df['Longitude'],
                                latitudes= df['Latitude'])

Saved img as clusters_k3.png
"""

"""
With K = 6 we were getting wrong clusters IN AFRICA got two clusters within itself
Because of reliance on euclidean distance clustering algo not able to capture 
relation between point on curved surface of out planet

df['Cluster'] = KMeans(6).fit_predict(df[['Latitude', 'Longitude']])
utility.utilities.plot_clusters(clusters= df['Cluster'], 
                                longitudes= df['Longitude'],
                                latitudes= df['Latitude'])
Saved img as clusters_K6.png
""" 

"""
We will be using DBSCAN becuz it gives us option to decide distance function
Assuming in global setting a cluster contains minimum 3 cities and minimum 250 miles 
apart


metric = utility.utilities.great_circle_distance
dbscan = DBSCAN(eps = 250, min_samples=3, metric=metric)
df['Cluster'] = dbscan.fit_predict(df[['Latitude', 'Longitude']])
utility.utilities.plot_clusters(clusters= df['Cluster'], 
                                longitudes= df['Longitude'],
                                latitudes= df['Latitude'])

Since news headlines are biased towards US we have got dense cluster in US.
We have to maintain Seperate Clusters for each country. Here we are targeting particularly
US hence we will go for two df one for US and other for non US

Saved img as clusters_K6.png
"""
"""
df = utility.utilities.assign_country_codes(df = df, gc = gc)
df_us = df[df['Country_code'] == 'US']
df_not_us = df[df['Country_code'] != 'US']

metric = utility.utilities.great_circle_distance
dbscan = DBSCAN(eps = 125, min_samples=3, metric=metric)
df_us['Cluster'] = dbscan.fit_predict(df_us[['Latitude', 'Longitude']])
df_us = df_us[df_us['Cluster'] > -1]

metric = utility.utilities.great_circle_distance
dbscan = DBSCAN(eps = 250, min_samples=3, metric=metric)
df_not_us['Cluster'] = dbscan.fit_predict(df_not_us[['Latitude', 'Longitude']])
df_not_us = df_not_us[df_not_us['Cluster'] > -1]

#Largest Cluster
groups = df_not_us.groupby('Cluster')
print(f"{len(groups)} Non US clusters have been detected")
sorted_groups = sorted(groups, key = lambda x: len(x[1]), reverse= True)
group_id, largest_group = sorted_groups[0]
print(f"Largest cluster contains {len(largest_group)} headlines")
largest_group = utility.utilities.sort_by_centrality(largest_group)
print("Countries mentioned in largest cluster :")
for k, v in utility.utilities.countries_cluster(largest_group):
    print(f"{k} : {v}")
print("Headlines in largest cluster :")
for headline in largest_group['Headline'].values[:5]:
    print(5)

"""

df = utility.utilities.assign_country_codes(df = df, gc = gc)
path = os.path.join(os.path.dirname(__file__), "data")
df.to_csv(f"{path}/data.csv", index = False)
