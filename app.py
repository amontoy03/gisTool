import streamlit as st  
import folium  
from folium.plugins import Draw 
from streamlit_folium import st_folium 
import geopandas as gpd    
from shapely.geometry import shape
import os
import glob


state_county_map = {
    "Colorado": ["Boulder", "Clear Creek", "Gilpin", "Grand", "Jefferson", "Larimer", "Weld"],
    "Florida": ["Bay", "Brevard", "Lake", "Lee", "Marion", "Orange", "Osceola", "Pinellas", "Prince George", "Seminole", "Volusia"],
    "Maryland": ["Anne Arundel", "Montgomery"],
    "North Carolina": ["Anson", "Cabarrus", "Catawba", "Cleveland", "Davidson", "Durham", "Forsyth", "Gaston", "Iredell", "Lincoln", "Mecklenburg", "Moore", "New Hanover", "Orange", "Rowan", "Stanley", "Union", "Wake", "Watauga"],
    "South Carolina": ["Greenville", "Horry", "Lancaster", "York"],
    "Texas": ["Dallas", "Denton", "Johnson", "Tarrant"],
    "Virginia": ["Arlington", "Fairfax", "Loudoun", "Prince William"]
}

county_coords = {
    # North Carolina
    ("North Carolina", "Anson"): [34.985, -80.081],
    ("North Carolina", "Cabarrus"): [35.416, -80.579],
    ("North Carolina", "Catawba"): [35.662, -81.214],
    ("North Carolina", "Cleveland"): [35.339, -81.554],
    ("North Carolina", "Davidson"): [35.799, -80.242],
    ("North Carolina", "Durham"): [36.022, -78.903],
    ("North Carolina", "Forsyth"): [36.134, -80.254],
    ("North Carolina", "Gaston"): [35.260, -81.180],
    ("North Carolina", "Iredell"): [35.850, -80.872],
    ("North Carolina", "Lincoln"): [35.490, -81.234],
    ("North Carolina", "Mecklenburg"): [35.263, -80.837],
    ("North Carolina", "Moore"): [35.292, -79.465],
    ("North Carolina", "New Hanover"): [34.201, -77.886],
    ("North Carolina", "Orange"): [36.072, -79.125],
    ("North Carolina", "Rowan"): [35.641, -80.517],
    ("North Carolina", "Stanley"): [35.315, -80.254],
    ("North Carolina", "Union"): [34.991, -80.553],
    ("North Carolina", "Wake"): [35.800, -78.639],
    ("North Carolina", "Watauga"): [36.220, -81.678],

    # South Carolina
    ("South Carolina", "Greenville"): [34.852, -82.394],
    ("South Carolina", "Horry"): [33.777, -78.926],
    ("South Carolina", "Lancaster"): [34.722, -80.775],
    ("South Carolina", "York"): [34.994, -81.239],

    # Maryland
    ("Maryland", "Anne Arundel"): [38.953, -76.547],
    ("Maryland", "Montgomery"): [39.154, -77.240],

    # Virginia
    ("Virginia", "Arlington"): [38.879, -77.106],
    ("Virginia", "Fairfax"): [38.856, -77.365],
    ("Virginia", "Loudoun"): [39.086, -77.653],
    ("Virginia", "Prince William"): [38.701, -77.476],

    # Florida
    ("Florida", "Bay"): [30.180, -85.684],
    ("Florida", "Brevard"): [28.263, -80.721],
    ("Florida", "Lake"): [28.764, -81.713],
    ("Florida", "Lee"): [26.624, -81.939],
    ("Florida", "Marion"): [29.193, -82.137],
    ("Florida", "Orange"): [28.484, -81.251],
    ("Florida", "Osceola"): [28.063, -81.075],
    ("Florida", "Pinellas"): [27.876, -82.752],
    ("Florida", "Prince George"): [37.229, -77.287],  
    ("Florida", "Seminole"): [28.713, -81.207],
    ("Florida", "Volusia"): [29.027, -81.075],

    # Colorado
    ("Colorado", "Boulder"): [40.020, -105.271],
    ("Colorado", "Clear Creek"): [39.690, -105.641],
    ("Colorado", "Gilpin"): [39.844, -105.521],
    ("Colorado", "Grand"): [40.102, -106.125],
    ("Colorado", "Jefferson"): [39.578, -105.214],
    ("Colorado", "Larimer"): [40.661, -105.461],
    ("Colorado", "Weld"): [40.554, -104.392],

    # Texas
    ("Texas", "Dallas"): [32.776, -96.797],
    ("Texas", "Denton"): [33.215, -97.133],
    ("Texas", "Johnson"): [32.409, -97.386],
    ("Texas", "Tarrant"): [32.769, -97.309],
}

selected_state = st.selectbox("Select State", list(state_county_map.keys()))
selected_county = st.selectbox("Select County", state_county_map[selected_state])
st.markdown(f"### Selected Location: {selected_county} County, {selected_state}")


def get_available_layers(state, county):
    base_path = os.path.join("data", state, county)
    if not os.path.isdir(base_path):
        return []

    layer_names = []
    for folder in glob.glob(os.path.join(base_path, "*")):
        if os.path.isdir(folder):
            shp_files = glob.glob(os.path.join(folder, "*.shp"))
            for shp_file in shp_files:
                name = os.path.splitext(os.path.basename(shp_file))[0].replace("_", " ")
                layer_names.append(name)
    return sorted(list(set(layer_names)))

available_layers = get_available_layers(selected_state, selected_county)
selected_layers = st.multiselect("Select Available Data", available_layers)


location = county_coords.get((selected_state, selected_county), [35.2271, -80.8431])
m = folium.Map(location=location, zoom_start=11)

Draw(
    export=False,
    position="topleft",
    draw_options={
        "polyline": False,
        "circle": False,
        "marker": False,
        "circlemarker": False,
        "rectangle": True,
        "polygon": False,
    },
    edit_options={"edit": True},
).add_to(m)



def find_shapefile(base_dir, file_key):
    folder_glob = os.path.join(base_dir, "*")
    for folder in glob.glob(folder_glob):
        if os.path.isdir(folder) and os.path.basename(folder).lower() == file_key.lower():
            shp_glob = os.path.join(folder, "*.shp")
            for shp_file in glob.glob(shp_glob):
                if os.path.splitext(os.path.basename(shp_file))[0].lower() == file_key.lower():
                    return shp_file
    return None


for layer in selected_layers:
    file_key = layer.replace(" ", "_")
    base_dir = os.path.join("data", selected_state, selected_county)
    file_path = find_shapefile(base_dir, file_key)

    if file_path and os.path.exists(file_path):
        try:
            gdf = gpd.read_file(file_path).to_crs("EPSG:4326")

            gdf = gdf[gdf.geometry.notnull()]
            gdf = gdf[gdf.geometry.is_valid]

            if not gdf.empty:
                for col in gdf.columns:
                    if col != "geometry":
                        try:
                            gdf[col] = gdf[col].astype(str)
                        except Exception:
                            gdf[col] = gdf[col].apply(lambda x: str(x))

                popup_fields = [col for col in gdf.columns if col != "geometry"]
                folium.GeoJson(
                    gdf,
                    name=layer,
                    popup=folium.GeoJsonPopup(fields=popup_fields, aliases=popup_fields, max_width=400)
                ).add_to(m)
            else:
                st.warning(f"{layer} shapefile has no valid geometry.")
        except Exception as e:
            st.error(f"Error loading {layer}: {e}")
    else:
        st.warning(f"Missing: {file_key} in {selected_county}, {selected_state}")



st_data = st_folium(m, width=1000, height=600)

@st.cache_data
def load_layer(filepath):
    return gpd.read_file(filepath).to_crs("EPSG:4326")

if st_data and st_data.get("all_drawings"):
    drawing = st_data["all_drawings"][-1]
    if drawing and "geometry" in drawing:
        geom = shape(drawing["geometry"])
        st.success("Area selected, displaying data inside:")
        for layer in selected_layers:
            file_key = layer.replace(" ", "_")
            base_dir = os.path.join("data", selected_state, selected_county)
            file_path = find_shapefile(base_dir, file_key)

            if file_path and os.path.exists(file_path):
                gdf = load_layer(file_path)
                filtered = gdf[gdf.intersects(geom)]
                st.subheader(f"{layer} Features")
                if not filtered.empty:
                    st.dataframe(filtered.drop(columns="geometry").head(20))
                    st.info(f"{len(filtered)} feature(s) found.")
                else:
                    st.warning("No features found in this area.")
            else:
                st.warning(f"Missing: {file_key} layer.")
else:
    st.info("Draw a shape on the map to show features.")