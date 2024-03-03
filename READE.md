Disease Outbreak App

Extract clusters of disease outbreak based on density from headlines data archived from various news portals.

Uses DBSCAN to form clusters where min_samples is minimum numbers of cities to have to consider one a cluster. Epsilon is distance in miles for circle around a city data point.

Uses geonamescache to get info about coordinates and city/country name.

data:
    headlines.txt - Data of headlines about various disease in different area across the globe

    data.csv - preprocessed and cleaned data for clustering

output_img:
    contains all the images saved from running KMeans algo for determining number of clusters. Used DBSCAN at last.

utility:
    contains all the functions required for preprocessing, ploting, distance metric, sorting, assigning country codes, elbow method etc.

website:
    home.py - base file for streamlit app
    pages:
        Get Custom Area.py - Give coordinates to get that area with scatter plot of disease news
        Get Headlines.py - Give coordinates to get coutries, top 5 headlines

preprocessing.py:
    all the preprocessing required to extract city, country and coordinates from data
    saved data in data.csv

main.py:
    proof of concept 




