import pandas as pd
import requests
import googlemaps
from datetime import datetime
import streamlit as st
import numpy as np
import polyline

GOOGLE_MAPS_API_KEY = st.secrets["google"]["map_api_key"]
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

def get_route(origin, destination):
    try:
        # Request directions
        directions_result = gmaps.directions(
            origin,
            destination,
            mode="driving",
            alternatives=True
        )
        return directions_result
    except Exception as e:
        st.error(f"Error getting route: {str(e)}")
        return None

def get_points_along_route(route, interval_km=50):
    # Get total distance in meters
    total_distance = route[0]['legs'][0]['distance']['value']
    
    # Calculate number of points based on distance
    num_intervals = max(2, int(total_distance / (interval_km * 1000)))
    
    route_coords = []
    for step in route[0]['legs'][0]['steps']:
        points = polyline.decode(step['polyline']['points'])
        route_coords.extend(points)
    
    route_coords = np.array(route_coords)
    
    # Always include start and end points
    points = [route_coords[0]]
    
    if num_intervals > 2:
        # Add intermediate points at specified intervals
        for i in range(1, num_intervals):
            idx = int((i * len(route_coords)) / num_intervals)
            points.append(route_coords[idx])
    
    # Add end point
    points.append(route_coords[-1])
    
    return [(point[0], point[1]) for point in points]


def get_petronas_stations_along_route(route, radius=5000):
    stations = {}
    route_points = get_points_along_route(route)
    st.write(f"Searching at {len(route_points)} points along the route...")
    
    for i, point in enumerate(route_points):
        progress_text = f"Searching near point {i+1}/{len(route_points)}"
        with st.spinner(progress_text):
            try:
                result = gmaps.places_nearby(
                    location={'lat': point[0], 'lng': point[1]},
                    keyword='Petronas station',
                    radius=radius
                )
                
                while True:
                    for place in result.get('results', []):
                        if place['place_id'] not in stations:
                            place_details = gmaps.place(
                                place['place_id'],
                                fields=['name', 'geometry', 'vicinity', 'rating', 'user_ratings_total', 'reviews']
                            )
                            details = place_details.get('result', {})
                            
                            # Calculate distance from route
                            station_location = (place['geometry']['location']['lat'], 
                                             place['geometry']['location']['lng'])
                            
                            stations[place['place_id']] = {
                                'Station Name': place['name'],
                                'Latitude': station_location[0],
                                'Longitude': station_location[1],
                                'Address': place.get('vicinity', 'Address not available'),
                                'Rating': place.get('rating', 'No rating'),
                                'Total Ratings': place.get('user_ratings_total', 0),
                                'Place ID': place['place_id'],
                                'Reviews': details.get('reviews', []),
                                'Search Point': f"Point {i+1}/{len(route_points)}"
                            }
                    
                    if 'next_page_token' not in result:
                        break
                        
                    time.sleep(2)
                    result = gmaps.places_nearby(
                        location={'lat': point[0], 'lng': point[1]},
                        keyword='Petronas station',
                        radius=radius,
                        page_token=result['next_page_token']
                    )
                    
            except Exception as e:
                st.error(f"Error fetching stations at point {i+1}: {str(e)}")
    
    return pd.DataFrame(list(stations.values()))

def get_station_reviews(place_id):
    try:
        # Get place details including reviews
        result = gmaps.place(place_id, fields=['reviews', 'rating'])
        reviews = result.get('result', {}).get('reviews', [])
        return reviews
    except Exception as e:
        st.error(f"Error fetching reviews: {str(e)}")
        return []

def get_petronas_stations():
    stations = []
    search_query = "Petronas station Malaysia"
    location = {'lat': 4.2105, 'lng': 101.9758}
    
    try:
        result = gmaps.places_nearby(
            location=location,
            keyword='Petronas station'
        )

        while True:
            for place in result.get('results', []):
                # Get detailed place information including reviews
                place_details = gmaps.place(place['place_id'], 
                    fields=['name', 'geometry', 'vicinity', 'rating', 
                           'user_ratings_total', 'reviews'])
                
                details = place_details.get('result', {})
                reviews = details.get('reviews', [])
                
                station_info = {
                    'Station Name': place['name'],
                    'Latitude': place['geometry']['location']['lat'],
                    'Longitude': place['geometry']['location']['lng'],
                    'Address': place.get('vicinity', 'Address not available'),
                    'Rating': place.get('rating', 'No rating'),
                    'Total Ratings': place.get('user_ratings_total', 0),
                    'Place ID': place['place_id'],
                    'Reviews': reviews
                }
                stations.append(station_info)

            if 'next_page_token' in result:
                time.sleep(2)
                result = gmaps.places_nearby(
                    location=location,
                    keyword='Petronas station',
                    page_token=result['next_page_token']
                )
            else:
                break

    except Exception as e:
        st.error(f"Error fetching station data: {str(e)}")
    
    return pd.DataFrame(stations)