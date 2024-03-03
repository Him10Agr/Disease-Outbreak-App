import streamlit as st
import os, sys
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(
    page_title='Disease Outbreak App'
)

st.title('Disease Outbreak App')
st.header('''Know What's Going Around You''')

file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/data.csv')
df = pd.read_csv(file_path)

fig = px.scatter_geo(df, lat='Latitude', lon='Longitude')

st.plotly_chart(fig, use_container_width=True)