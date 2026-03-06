import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

# -----------------------------
# CONFIG
# -----------------------------

st.set_page_config(
    page_title="NYC Taxi Fare",
    page_icon="🚕",
    layout="wide"
)

API_URL = "https://taxifaire-900640444126.europe-west1.run.app/predict"

NYC_CENTER = [40.7128, -74.0060]

NYC_BOUNDS = {
    "min_lat": 40.49,
    "max_lat": 40.92,
    "min_lon": -74.27,
    "max_lon": -73.68
}

geolocator = Nominatim(user_agent="taxi-fare-app")

# -----------------------------
# STYLE
# -----------------------------

st.markdown("""
<style>

.main-title{
font-size:40px;
font-weight:700;
}

.stButton button{
background:black;
color:white;
border-radius:8px;
height:48px;
font-weight:600;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------
# HEADER
# -----------------------------

st.markdown('<div class="main-title">🚕 NYC Taxi Fare Estimator</div>', unsafe_allow_html=True)
st.write("Estimate the cost of a taxi ride in New York City.")

# -----------------------------
# FUNCTIONS
# -----------------------------

def geocode_address(address):

    try:
        locations = geolocator.geocode(
            address,
            exactly_one=False,
            limit=5,
            country_codes="us"
        )

        if not locations:
            return []

        results = []

        for loc in locations:

            lat = loc.latitude
            lon = loc.longitude

            if (
                NYC_BOUNDS["min_lat"] <= lat <= NYC_BOUNDS["max_lat"]
                and NYC_BOUNDS["min_lon"] <= lon <= NYC_BOUNDS["max_lon"]
            ):

                results.append({
                    "address": loc.address,
                    "lat": lat,
                    "lon": lon
                })

        return results

    except:
        return []

# -----------------------------
# LAYOUT
# -----------------------------

col1, col2 = st.columns([1,2])

# -----------------------------
# INPUT PANEL
# -----------------------------

with col1:

    st.subheader("Trip")

    pickup_datetime = st.datetime_input("Pickup time")

    passenger_count = st.slider(
        "Passengers",
        1,
        6,
        1
    )

    st.divider()

    # PICKUP

    pickup_query = st.text_input(
        "Pickup address",
        placeholder="Times Square"
    )

    pickup_coords = None

    if pickup_query:

        results = geocode_address(pickup_query)

        if results:

            options = [r["address"] for r in results]

            selected = st.selectbox(
                "Select pickup location",
                options
            )

            for r in results:
                if r["address"] == selected:
                    pickup_coords = (r["lat"], r["lon"])

    # DROPOFF

    drop_query = st.text_input(
        "Dropoff address",
        placeholder="JFK Airport"
    )

    drop_coords = None

    if drop_query:

        results = geocode_address(drop_query)

        if results:

            options = [r["address"] for r in results]

            selected = st.selectbox(
                "Select dropoff location",
                options
            )

            for r in results:
                if r["address"] == selected:
                    drop_coords = (r["lat"], r["lon"])

# -----------------------------
# MAP
# -----------------------------

with col2:

    m = folium.Map(
        location=NYC_CENTER,
        zoom_start=11
    )

    # NYC boundary

    folium.Rectangle(
        bounds=[
            [NYC_BOUNDS["min_lat"], NYC_BOUNDS["min_lon"]],
            [NYC_BOUNDS["max_lat"], NYC_BOUNDS["max_lon"]],
        ],
        color="blue",
        fill=False
    ).add_to(m)

    if pickup_coords:

        folium.Marker(
            pickup_coords,
            tooltip="Pickup",
            icon=folium.Icon(color="green")
        ).add_to(m)

    if drop_coords:

        folium.Marker(
            drop_coords,
            tooltip="Dropoff",
            icon=folium.Icon(color="red")
        ).add_to(m)

    if pickup_coords and drop_coords:

        folium.PolyLine(
            [pickup_coords, drop_coords],
            weight=4
        ).add_to(m)

    map_data = st_folium(
        m,
        height=500
    )

# -----------------------------
# CLICK MAP
# -----------------------------

if map_data and map_data["last_clicked"]:

    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]

    if (
        NYC_BOUNDS["min_lat"] <= lat <= NYC_BOUNDS["max_lat"]
        and NYC_BOUNDS["min_lon"] <= lon <= NYC_BOUNDS["max_lon"]
    ):

        if not pickup_coords:
            pickup_coords = (lat, lon)
            st.success("Pickup selected on map")

        elif not drop_coords:
            drop_coords = (lat, lon)
            st.success("Dropoff selected on map")

# -----------------------------
# PREDICTION
# -----------------------------

st.divider()

if st.button("Estimate Fare", use_container_width=True):

    if not pickup_coords or not drop_coords:
        st.error("Please select pickup and dropoff locations")
        st.stop()

    params = {
        "pickup_datetime": pickup_datetime,
        "pickup_longitude": pickup_coords[1],
        "pickup_latitude": pickup_coords[0],
        "dropoff_longitude": drop_coords[1],
        "dropoff_latitude": drop_coords[0],
        "passenger_count": passenger_count
    }

    with st.spinner("Calculating fare..."):

        response = requests.get(API_URL, params=params)

        prediction = response.json()["fare"]

    st.success(f"Estimated fare: **${prediction:.2f}**")
