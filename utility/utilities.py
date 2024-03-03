import os, re
from unidecode import unidecode
from geonamescache import GeonamesCache
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from cartopy.crs import PlateCarree
import math
from collections import Counter

#transforming each location in headlines case independent and accent independent
def name_to_regex(name):
    decoded_name = unidecode(name)
    if name != decoded_name:
        regex = fr'\b({name}|{decoded_name})\b'
    else:
        regex = fr'\b{name}\b'
    
    return re.compile(regex, flags=re.IGNORECASE)

#finding location in text data
def get_name_in_text(text, dictionary):
    for regex, name in sorted(dictionary.items(), key = lambda x: x[1]):
        if regex.search(text):
            return name
        
    return None

#fetching multiplcity headlines
def get_cities_in_headline(headline, city_to_name):
    cities_in_headline = set()
    for regex, name in city_to_name.items():
        match = regex.search(headline)
        if match:
            if headline[match.start()].isupper():
                cities_in_headline.add(name)
    
    return list(cities_in_headline)

def get_longest_city(cities):
    if cities:
        return max(cities, key=len)
    return None


#assiging geographic coordinates to cities
def get_lat_log(df: pd.DataFrame, geocache: GeonamesCache):
    latitudes, longitudes = [], []
    for city_name in df.City.values:
        city = max(geocache.get_cities_by_name(city_name), 
                   key = lambda x: list(x.values())[0]['population'])
        city = list(city.values())[0]
        latitudes.append(city['latitude'])
        longitudes.append(city['longitude'])
    
    return latitudes, longitudes

def give_elbow_curve(df: pd.DataFrame):
    
    coordinates = df[['Latitude', 'Longitude']]
    k_values = range(1, 10)
    inertia_values = []
    for k in k_values:
        inertia_values.append(KMeans(k).fit(coordinates).inertia_)
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output_img")
    plt.plot(range(1, 10), inertia_values)
    plt.xlabel('K')
    plt.ylabel('Inertia')
    plt.savefig(f"{path}/elbow.png")
    
def plot_clusters(clusters, longitudes, latitudes, name):
    plt.figure(figsize=(12, 10))
    ax = plt.axes(projection = PlateCarree())
    ax.coastlines()
    ax.scatter(longitudes, latitudes, c = clusters)
    ax.set_global()
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output_img")
    plt.savefig(f"{path}/clusters_{name}.png")
        
def great_circle_distance(coord1, coord2, radius = 3956):
    #3956 = radius of earth in miles
    if np.array_equal(coord1, coord2):
        return 0.0
    
    coord1, coord2 = np.radians(coord1), np.radians(coord2)
    delta_x, delta_y = coord2 - coord1
    haversin = math.sin(delta_x / 2) ** 2 + np.prod([math.cos(coord1[0]), math.cos(coord2[0]),
                                                     math.sin(delta_y / 2) ** 2])
    return 2 * radius * math.asin(haversin ** 0.5)

def assign_country_codes(df: pd.DataFrame, gc: GeonamesCache):
    
    def get_country_codes(city_name):
        city = max(gc.get_cities_by_name(city_name), key = lambda x: list(x.values())[0]['population'])
        return list(city.values())[0]['countrycode']
    
    df["Country_code"] = df.City.apply(get_country_codes)
    return df

def compute_centrality(group):
    group_coords = group[['Latitude', 'Longitude']].values
    center_coords = group_coords.mean(axis =0)
    distance_to_center = [great_circle_distance(center_coords, coord) for coord in group_coords]
    group['Distance_to_center'] = distance_to_center
    
def sort_by_centrality(group):
    compute_centrality(group)
    return group.sort_values(by = ['Distance_to_center'], ascending = True)

def countries_cluster(group: pd.DataFrame, gc: GeonamesCache):
    countries = [gc.get_countries()[country_code]['name'] for country_code in group['Country_code'].values]
    return dict(Counter(countries))