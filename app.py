import streamlit as st
import requests

'''
# Let's ride in NY City!
'''

pickup_datetime = st.datetime_input("When do you want to ride?")

'''### Pick-up location'''
pickup_longitude = st.number_input("Pick-up longitude")
pickup_latitude = st.number_input("Pick-up latitude")

'''### Arrival location'''
dropoff_longitude = st.number_input("Drop-off longitude")
dropoff_latitude = st.number_input("Drop-off latitude")


'''### Arrival location'''
passenger_count = st.number_input("How many passengers?")


# Once we have these, let's call our API in order to retrieve a prediction

#See ? No need to load a `model.joblib` file in this app, we do not even need to know anything about Data Science in order to retrieve a prediction...

# 🤔 How could we call our API ? Off course... The `requests` package 💡


url = 'https://taxifaire-900640444126.europe-west1.run.app/predict'

if url == 'https://taxifare.lewagon.ai/predict':

    st.markdown('Maybe you want to use your own API for the prediction, not the one provided by Le Wagon...')

# 2. Let's build a dictionary containing the parameters for our API...
params = {
    "pickup_datetime":pickup_datetime,
    "pickup_longitude":pickup_longitude,
    "pickup_latitude":pickup_latitude,
    "dropoff_longitude":dropoff_longitude,
    "dropoff_latitude":dropoff_latitude,
    "passenger_count":passenger_count}


#3. Let's call our API using the `requests` package...

if st.button("Get fare prediction for this ride:"):
    response = requests.get(url, params=params)

    #4. Let's retrieve the prediction from the **JSON** returned by the API...
    fare_prediction = response.json()['fare']

    ## Finally, we can display the prediction to the user
    st.write(f"Fare prediction ${fare_prediction:.2f}")
