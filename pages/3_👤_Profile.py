import streamlit as st
from PIL import Image
import pandas as pd
import os

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

    # Predicted Mileage for Car X (Dynamic)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Dynamic Predictions")
    col4, col5 = st.columns(2)
    predicted_mileage = st.slider("Set Predicted Mileage for Car X (km)", 100, 1000, 500)
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <h3>Predicted Mileage for Car X</h3>
                <h2>{predicted_mileage} km</h2>
                <p>Adjusted based on your input</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Predicted Monthly Fuel Cost (Dynamic)
    fuel_cost_per_km = 0.4  # Example rate in RM/km
    predicted_fuel_cost = predicted_mileage * fuel_cost_per_km
    with col5:
        st.markdown(f"""
            <div class="metric-card">
                <h3>Predicted Monthly Fuel Cost</h3>
                <h2>RM {predicted_fuel_cost:.2f}</h2>
                <p>Estimated based on mileage</p>
            </div>
        """, unsafe_allow_html=True)
    
    # CO2 Emissions (Dynamic)
    col6, col7 = st.columns(2)
    emission_rate_per_km = 0.2  # Example rate in kg/km
    co2_emissions = predicted_mileage * emission_rate_per_km
    with col6:
        st.markdown(f"""
            <div class="metric-card">
                <h3>Predicted CO2 Emissions</h3>
                <h2>{co2_emissions:.2f} kg</h2>
                <p>Based on your predicted mileage</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Current Car Details (Dynamic)
    car_make = st.selectbox("Select Your Car Make", ["Toyota", "Honda", "Ford", "BMW", "Mercedes"])
    car_model = st.text_input("Enter Your Car Model", value="Model X")
    with col7:
        st.markdown(f"""
            <div class="metric-card">
                <h3>Current Car</h3>
                <h2>{car_make} {car_model}</h2>
                <p>Details provided by user</p>
            </div>
        """, unsafe_allow_html=True)

    st.subheader("Recent Activities")
    activities = pd.DataFrame({
        'Date': ['2024-12-05', '2024-12-04', '2024-12-03'],
        'Activity': ['Payment Made', 'Points Earned', 'Voucher Redeemed'],
        'Details': ['RM 50.00', '+100 points', 'Discount Voucher']
    })
    st.dataframe(activities, hide_index=True)

if __name__ == "__main__":
    config()
    render_view()
