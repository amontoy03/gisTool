import streamlit as st
import folium
from streamlit_folium import st_folium
import geopandas as gpd
import os


layers = st.multiselect("Select Available Data", ["Parcels", "Zoning", "Flood Plains", "Streets"])

m = folium.Map(location=[35.2271, -80.8431], zoom_start=13)
m.add_child(folium.LatLngPopup())

for layer in layers:
    file_key = layer.lower().replace(" ", "_")
    filepath = os.path.join("data", f"{file_key}.shp")
    if os.path.exists(filepath):
        try:
            gdf = gpd.read_file(filepath)
            folium.GeoJson(gdf, name=layer).add_to(m)
        except Exception as e:
            st.error(f"Error reading {filepath}: {e}")
    else:
        st.warning(f"Missing file: {filepath}")

st_folium(m, width=1000, height=600)