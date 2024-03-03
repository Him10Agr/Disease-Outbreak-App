import os, re
from unidecode import unidecode
from geonamescache import GeonamesCache
import pandas as pd
import utility.utilities
from sklearn.cluster import KMeans, DBSCAN
import matplotlib.pyplot as plt
import cartopy
from cartopy.crs import PlateCarree

gc = GeonamesCache()

path = os.path.join(os.path.dirname(__file__), "data/data.csv")
df = pd.read_csv(path, header= 'infer')
#print(df)
while True:

    quest = str(input("Give the coordinates extent to show disease spread headlines: "))
    coord = quest.split() #min_lon, max_lon, min_lat, max_lat
    coord = list(map(lambda x: eval(x), coord))
    df = df[(df['Longitude'] >= coord[0]) & (df['Longitude'] <= coord[1]) & (df['Latitude'] >= coord[2]) & (df['Latitude'] <= coord[3])]
    metric = utility.utilities.great_circle_distance
    while True:
        inp = float(input("Give epsilon value: "))
        dbscan = DBSCAN(eps=inp, min_samples=3, metric = metric, n_jobs=-1)
        df['Cluster'] = dbscan.fit_predict(df[['Latitude', 'Longitude']])
        df = df[df['Cluster'] > -1]
        plt.figure(figsize=(12, 10))
        ax = plt.axes(projection = PlateCarree())
        ax.coastlines()
        ax.scatter(df.Longitude, df.Latitude, c = df["Cluster"])
        ax.set_extent(coord, crs = PlateCarree())
        ax.add_feature(cartopy.feature.OCEAN)
        ax.add_feature(cartopy.feature.LAND)
        ax.add_feature(cartopy.feature.BORDERS)
        ax.stock_img()
        plt.show()
        inp = str(input("Want to run dbscan again (Yes/No): "))
        if inp.lower() == "yes":
            continue
        else:
            break
    inp = str(input("Want to give coordinates again (Yes/No): "))
    if inp.lower() == "yes":
        continue
    else:
        break   

groups = df.groupby('Cluster')
sorted_groups = sorted(groups, key = lambda x: len(x[1]), reverse= True)
for group_id, largest_group in sorted_groups:
    print()
    print(f"Cluster {group_id + 1} contains {len(largest_group)} headlines")
    largest_group = utility.utilities.sort_by_centrality(largest_group)
    print("Countries mentioned in the cluster :")
    for k, v in utility.utilities.countries_cluster(largest_group, gc).items():
        print(f"{k} : {v}")
    print("Top 5 Headlines in the cluster :")
    for headline in largest_group['Headline'].values[:5]:
        print(headline)