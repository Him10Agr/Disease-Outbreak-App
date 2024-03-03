import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import os, sys
from geonamescache import GeonamesCache

gc = GeonamesCache()

path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if path in sys.path:
    pass
else:
    sys.path.append(path)

import utility.utilities
from sklearn.cluster import KMeans, DBSCAN
import matplotlib.pyplot as plt
import cartopy
from cartopy.crs import PlateCarree

st.set_page_config(
    page_title='Specific Area'
)

st.title('Give Co-Ordinates')

if 'store' not in st.session_state:
    st.session_state.store = False

with st.form(key='columns_in_form'):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        min_lat = st.number_input("Min Latitude")
    with c2:
        max_lat = st.number_input("Max Latitude")
    with c3:
        min_lon = st.number_input("Min Longitude")
    with c4:
        max_lon = st.number_input("Max Longitude")

    submitButton_coord = st.form_submit_button(label = 'Proceed')
    
file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data/data.csv')
df = pd.read_csv(file_path)
    
if submitButton_coord or st.session_state.store:
    
    st.session_state.store = True
    df = df[(df['Longitude'] >= min_lon) & (df['Longitude'] <= max_lon) & (df['Latitude'] >= min_lat) & (df['Latitude'] <= max_lat)]
    metric = utility.utilities.great_circle_distance
    coord = [min_lon, max_lon, min_lat, max_lat]
    
    n = st.number_input('Give minimum number of cities to form a cluster', min_value=2)
    epsilon = st.slider('Radius of cluster in miles', min_value=2, max_value=3635)
        
    try:
        if st.button('Show'):
            dbscan = DBSCAN(eps=epsilon, min_samples=n, metric = metric, n_jobs=-1)
            df['Cluster'] = dbscan.fit_predict(df[['Latitude', 'Longitude']])
            df = df[df['Cluster'] > -1]
            
            groups = df.groupby('Cluster')
            #sorted_groups = sorted(groups, key = lambda x: len(x[1]), reverse= True)
            for group_id, largest_group in groups:
                st.write()
                st.header(f"Cluster {group_id + 1} contains {len(largest_group)} headlines")
                largest_group = utility.utilities.sort_by_centrality(largest_group)
                st.subheader('Countries mentioned in the cluster :')
                for k, v in utility.utilities.countries_cluster(largest_group, gc).items():
                    st.caption(f"{k} : {v}")
                st.subheader("Top 5 Headlines in the cluster :")
                for headline in largest_group['Headline'].values[:5]:
                    st.caption(headline)
                fig = px.scatter_mapbox(df[df['Cluster'] == group_id], lat = 'Latitude', lon = 'Longitude',
                        color_discrete_sequence=px.colors.qualitative.Prism_r,
                        zoom = 7, mapbox_style='open-street-map',width=1200, height=700).update_traces(marker = {'size': 10})
                st.plotly_chart(fig, use_container_width=True)
                st.divider()
    except Exception as e:
        pass
    

    
