import streamlit as st
from streamlit_folium import st_folium
import folium
from folium.plugins import MarkerCluster

import os
import requests
import polyline
import pandas as pd
import torch

from pages.utils.google_map_utils import get_route, get_petronas_stations_along_route
from pages.utils.custom_model_utils import preprocess_input, load_model


dirname = os.path.dirname(__file__)

def config():
    """Configure Streamlit page settings and custom CSS"""
    st.set_page_config(
        layout="wide",
        page_title="SETTLE | AI Routes",
        page_icon="🚗"
    )
    st.title("AI Routes 🚗")
    
    # Custom CSS
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
        .teal-card {
            background-color: #00c2af;
            color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)

def render_route_planner():
    """Render route planner with Google Maps integration"""
       # Route input
    col1, col2 = st.columns(2)
    with col1:
        origin = st.text_input("Starting Point", "Setel Venture, Bangsar South")
    with col2:
        destination = st.text_input("Destination", "Atas Tol Kuala Terengganu")
    
    # Search radius
    radius = st.slider("Search radius for stations (meters)", 500, 10000, 3000, 500)
    
    if st.button("Plan Route"):
        with st.spinner('Planning route and finding stations...'):
            # Get route
            route = get_route(origin, destination)
            
            if route:
                # Get stations along route
                df = get_petronas_stations_along_route(route, radius)
                
                # Create tabs
                tab1, tab2, tab3 = st.tabs(["Map View", "Station List", "Route Details"])
                
                with tab1:
                    create_route_map(df, route)
  
                
                with tab2:
                    st.subheader("Stations Along Route")
                    display_df = df.drop(columns=['Reviews', 'Place ID'])
                    st.dataframe(display_df, hide_index=True)
                
                with tab3:
                    st.subheader("Route Information")
                    route_info = route[0]['legs'][0]
                    st.write(f"Distance: {route_info['distance']['text']}")
                    st.write(f"Duration: {route_info['duration']['text']}")
                    st.write(f"Number of stations found: {len(df)}")
                    
                    with st.container(border=True):
                        predictor()


def create_route_map(df, route):
    # Create map centered on route start
    start_location = route[0]['legs'][0]['start_location']
    m = folium.Map(location=[start_location['lat'], start_location['lng']], zoom_start=10)
    
    # Draw the route
    route_coordinates = []
    for step in route[0]['legs'][0]['steps']:
        points = polyline.decode(step['polyline']['points'])
        route_coordinates.extend(points)
    
    folium.PolyLine(
        route_coordinates,
        weight=4,
        color='blue',
        opacity=0.8
    ).add_to(m)
    
    # Add markers for stations
    markercluster = MarkerCluster().add_to(m)
    
    # Add markers for start and end points
    folium.Marker(
        [start_location['lat'], start_location['lng']],
        popup='Start',
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(markercluster)
    
    end_location = route[0]['legs'][0]['end_location']
    folium.Marker(
        [end_location['lat'], end_location['lng']],
        popup='Destination',
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(markercluster)
    
    
    markercluster1 = MarkerCluster().add_to(m)
    for idx, row in df.iterrows():
        petronas_pin = folium.CustomIcon(icon_image= dirname + "/img/petronas.webp", icon_size=(50, 50))
        reviews_html = ""
        if len(row['Reviews']) > 0:
            reviews_html = "<br><br><b>Recent Reviews:</b><br>"
            for review in row['Reviews'][:3]:
                reviews_html += f"""
                    ⭐ {review.get('rating', 'N/A')}/5 - {review.get('relative_time_description', '')}<br>
                    "{review.get('text', 'No comment')}"<br><br>
                """

        popup_html = f"""
            <div style='width: 300px'>
                <h4>{row['Station Name']}</h4>
                <b>Address:</b> {row['Address']}<br>
                <b>Rating:</b> {'⭐' * int(row['Rating']) if isinstance(row['Rating'], (int, float)) else 'No rating'} 
                ({row['Rating']} from {row['Total Ratings']} reviews)
                {reviews_html}
            </div>
        """
        
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_html, max_width=350),
            icon=petronas_pin
        ).add_to(markercluster1)
        
    folium.plugins.Fullscreen(
        position="topright",
        title="Expand me",
        title_cancel="Exit me",
        force_separate_button=True,
    ).add_to(m)
    
    
    st_folium(m, width=1200, returned_objects=[])

# Streamlit app
def predictor():
    st.title('Vehicle Emission and Fuel Consumption Predictor')
    
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
    
    # Preprocess input
    input_data = preprocess_input(vehicle_class, engine_size, cylinders, transmission, fuel_type)
    
    # Make prediction
    model = load_model()
    with torch.no_grad():
        prediction = model(torch.FloatTensor(input_data))
    
    # Display results
    st.write('Predicted CO2 Emissions (g/km):', prediction[0][0].item())
    st.write('Predicted Fuel Consumption (L/100 km):', prediction[0][1].item())

def main():
    """Main function to render the Streamlit application"""
    config()
    render_route_planner()

if __name__ == "__main__":
    main()
