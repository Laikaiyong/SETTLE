import streamlit as st
from PIL import Image

import os
import requests
import polyline
import pandas as pd
import torch

from pages.utils.custom_model_utils import preprocess_input, load_model

dirname = os.path.dirname(__file__)

def config():
    st.set_page_config(
        layout="wide",
        page_title="SETTLE | Profile",
        page_icon="👤"
    )
    st.title("Profile 👤")
    st.markdown("""
        <style>
        .metric-card {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 10px 0;
        }
        .profile-section {
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

def render_view():
    st.markdown("<hr>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRoBdgrsKeeSfxKa6FD1xr9yeKABQNOHD2i2w&s", width=150)
    
    with col2:
        st.title("User Profile")
        st.write("Name: John Doe")
        st.write("Member ID: #12345")
        st.write("Account Status: Active ✅")
    
    st.markdown("<hr>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="metric-card">
                <h3>Wallet Balance</h3>
                <h2>RM 250.00</h2>
                <p>Last updated: Today</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class="metric-card">
                <h3>Points</h3>
                <h2>1,250</h2>
                <p>Expires in 30 days</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class="metric-card">
                <h3>Active Vouchers</h3>
                <h2>5</h2>
                <p>Click to view details</p>
            </div>
        """, unsafe_allow_html=True)
        
    car_brand = "Toyota"
    car_model = "Model X"
    with st.container(border=True):
        predictor(car_brand, car_model)
    
    

def predictor(car_brand, car_model):
    st.markdown(f"""
        <h3>Current Car</h3>
        <h2>{car_brand} {car_model}</h2>
        <p>Details provided by user</p>
    """, unsafe_allow_html=True)
    # Input fields
    vehicle_class = st.selectbox('Vehicle Class', [
        'COMPACT',
        'SUV - SMALL',
        'MID-SIZE',
        'TWO-SEATER',
        'MINICOMPACT',
        'SUBCOMPACT',
        'FULL-SIZE',
        'STATION WAGON - SMALL',
        'SUV - STANDARD',
        'VAN - CARGO',
        'VAN - PASSENGER',
        'PICKUP TRUCK - STANDARD',
        'MINIVAN',
        'SPECIAL PURPOSE VEHICLE',
        'STATION WAGON - MID-SIZE',
        'PICKUP TRUCK - SMALL'
    ])
    engine_size = st.number_input('Engine Size (L)', min_value=1.0, max_value=8.0, value=2.0)
    cylinders = st.number_input('Number of Cylinders', min_value=1, max_value=20, value=4)
    transmission = st.selectbox('Transmission', [
        'AS5',
        'M6',
        'AV7',
        'AS6',
        'AM6',
        'A6',
        'AM7',
        'AV8',
        'AS8',
        'A7',
        'A8',
        'M7',
        'A4',
        'M5',
        'AV',
        'A5',
        'AS7',
        'A9',
        'AS9',
        'AV6',
        'AS4',
        'AM5',
        'AM8',
        'AM9',
        'AS10',
        'A10',
        'AV10',
    ])
    fuel_type = st.selectbox('Fuel Type', [
        'Z',
        'D',
        'X',
        'E',
        'N',
    ])
        
        
    if st.button("Predict"):
        # Preprocess input
        input_data = preprocess_input(vehicle_class, engine_size, cylinders, transmission, fuel_type)
        
        # Make prediction
        model = load_model()
        with torch.no_grad():
            prediction = model(torch.FloatTensor(input_data))
        # Display results
        st.write('Predicted CO2 Emissions (g/km):', prediction[0][0].item())
        st.write('Predicted Fuel Consumption (L/100 km):', prediction[0][1].item())
        
        st.session_state["co2_emission"] = prediction[0][0].item()
        st.session_state["fuel_consumption"] = prediction[0][1].item()
    
    
    if 'co2_emission' in st.session_state and 'fuel_consumption' in st.session_state:
        # Predicted Mileage for Car X (Dynamic)
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("Dynamic Predictions")
        predicted_mileage = st.slider("Set Predicted Mileage for Car X (km)", 100, 1000, 500)
        st.markdown(f"""
            <div class="metric-card">
                <h3>Predicted Mileage for Car X</h3>
                <h2>{predicted_mileage} km</h2>
                <p>Adjusted based on your input</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Predicted Monthly Fuel Cost (Dynamic)
        predicted_fuel_cost = predicted_mileage * st.session_state["fuel_consumption"]  * 3.19 / 100

        
        # CO2 Emissions (Dynamic)
        col6, col7 = st.columns(2)
        co2_emissions = predicted_mileage * st.session_state["co2_emission"] / 1000
        with col6:
            st.markdown(f"""
                <div class="metric-card">
                    <h3>Predicted CO2 Emissions</h3>
                    <h2>{co2_emissions:.2f} kg</h2>
                    <p>Based on your predicted mileage</p>
                </div>
            """, unsafe_allow_html=True)
            
        with col7:
            st.markdown(f"""
                <div class="metric-card">
                    <h3>Predicted Fuel Cost (RON 97)</h3>
                    <h2>RM {predicted_fuel_cost:.2f}</h2>
                    <p>Estimated based on mileage</p>
                </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    config()
    render_view()
