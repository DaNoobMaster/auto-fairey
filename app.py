from datetime import datetime

import streamlit as st

import main as main_app

st.set_page_config(page_title="Auto Fare Calculator", page_icon="🚖", layout="centered")
st.title("Auto Fare Calculator")
st.write("Estimate taxi fare using your pickup, destination, baggage, and travel-time inputs.")

with st.form("fare_form"):
    start_location = st.text_input("Starting location", value="Bangalore")
    destination_location = st.text_input("Destination", value="Electronic City")
    travel_time_minutes = st.number_input("Travel time (minutes)", min_value=0, value=0, step=1)
    baggage_weight_kg = st.number_input("Baggage weight (kg)", min_value=0, value=0, step=1)

    use_custom_fare = st.checkbox("Use custom fare pricing")
    base_fare_value = st.number_input(
        "Base fare",
        min_value=0,
        value=36,
        step=1,
        disabled=not use_custom_fare,
    )
    rate_value = st.number_input(
        "Rate per km",
        min_value=0,
        value=18,
        step=1,
        disabled=not use_custom_fare,
    )

    submitted = st.form_submit_button("Calculate Fare")

if submitted:
    try:
        origin = main_app.location(start_location)
        destination = main_app.location(destination_location)
        distance_meters, duration_minutes = main_app.maps(origin, destination)
        zone = main_app.find_region(origin[0], origin[1]) or "unknown"

        if use_custom_fare:
            main_app.base_fare = int(base_fare_value)
            main_app.rate = int(rate_value)
        else:
            main_app.base_fare = 36
            main_app.rate = 18

        wait_time = max(travel_time_minutes - duration_minutes, 0)
        fare_text = main_app.fare(distance_meters / 1000, datetime.now().hour, wait_time, baggage_weight_kg)

        st.success(f"Estimated fare: {fare_text}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Distance", f"{distance_meters / 1000:.2f} km")
        col2.metric("Estimated duration", f"{duration_minutes:.1f} min")
        col3.metric("Region", zone.replace("-", " ").title() if zone else "Unknown")
        st.caption(f"Calculated wait time: {wait_time:.1f} minutes")
    except Exception as exc:
        st.error(str(exc))
