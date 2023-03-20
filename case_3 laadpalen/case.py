import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st
import folium
from streamlit_folium import st_folium
import branca.colormap as cm

# rdw dataset
r = requests.get("https://opendata.rdw.nl/resource/8jni-y848.json")
rdw = pd.json_normalize(r.json())

# laadpaaldata
lpd = pd.read_csv("laadpaaldata.csv")

# opencharge dataset
response = requests.get(
    "https://api.openchargemap.io/v3/poi/?output=json&countrycode=NL&maxresults=1000&compact=true&verbose=false&key=772ba88b-50db-49f1-b9f1-933c6053edd3"
)

json_lp = response.json()

opencharge = pd.json_normalize(json_lp)

df4 = pd.json_normalize(opencharge.Connections)
df5 = pd.json_normalize(df4[0])

ocm = pd.concat([opencharge, df5], axis=1)

ocm.columns = ocm.columns.str.replace(".", "_")
ocm.columns = ocm.columns.str.replace(" ", "_")

ocm = ocm.loc[:, ~ocm.columns.duplicated()].copy()
ocm = ocm[ocm["Quantity"].notna()]
ocm = ocm[ocm["PowerKW"].notna()]


# Folium map
def colorpicker(value):
    if value >= 300:
        return "darkred"
    elif value >= 250:
        return "red"
    elif value >= 200:
        return "lightred"
    elif value >= 150:
        return "lightgreen"
    elif value >= 100:
        return "green"
    elif value >= 50:
        return "lightblue"
    elif value >= 25:
        return "blue"
    elif value >= 10:
        return "darkblue"
    elif value >= 5:
        return "purple"
    else:
        return "orange"


m = folium.Map(location=[52.091684, 5.114055], zoom_start=8)

for i, row in ocm.iterrows():
    folium.Circle(
        location=[row["AddressInfo_Latitude"], row["AddressInfo_Longitude"]],
        fill=True,
        radius=300,
        popup=row["AddressInfo_Title"],
        color=colorpicker(row["PowerKW"]),
    ).add_to(m)

# Streamlit initialisation
st.title("Laadpalen case")
st.dataframe(rdw)
st.dataframe(lpd)
st.dataframe(ocm)
st_data = st_folium(m, width=725)
