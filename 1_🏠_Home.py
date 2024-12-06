import streamlit as st
from pymongo import MongoClient
import os



def config():
    """Configure Streamlit page settings and custom CSS"""
    st.set_page_config(
        page_title="SETTLE Home",
        page_icon="🚗",
        layout="wide"
    )
    
    # Custom CSS to mimic the HTML styling
    st.markdown("""
        <style>
        /* Reset and base styles */
        * {
            box-sizing: border-box;
        }
        
        /* Floating bar styles */
        .floating-bar {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background-color: #333;
            color: white;
            display: flex;
            justify-content: space-between;
            padding: 10px 20px;
            z-index: 1000;
        }
        
        .floating-bar-item {
            display: flex;
            align-items: center;
        }
        
        .floating-bar-item span {
            margin-left: 5px;
        }
        
        /* Container and section styles */
        .container {
            padding: 80px 20px 20px;
        }
        
        .section {
            margin-bottom: 40px;
        }
        
        .section-title {
            margin-bottom: 20px;
        }
        
        /* Button grid styles */
        .button-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            grid-gap: 20px;
        }
        
        .stButton > button {
            width: 100%;
            height: 100%;
            background-color: white !important;
            border: none !important;
            border-radius: 5px !important;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1) !important;
            transition: background-color 0.3s ease !important;
        }
        
        .stButton > button:hover {
            background-color: #f0f0f0 !important;
        }
        </style>
        """, unsafe_allow_html=True)

def render_floating_bar():
    """Render the top floating bar with user information"""
    st.markdown("""
        <style>
        .floating-bar {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            background-color: #333;
            color: white;
            display: flex;
            justify-content: space-around;
            align-items: center;
            padding: 10px 0;
            z-index: 1000;
            font-family: Arial, sans-serif;
        }
        .floating-bar-item {
            display: flex;
            align-items: center;
            color: white;
            font-size: 16px;
        }
        .floating-bar-item i {
            margin-right: 8px;
        }
        </style>
        <div class="floating-bar">
            <div class="floating-bar-item">
                <i class="fas fa-wallet"></i>
                <span>RM 250.00</span>
            </div>
            <div class="floating-bar-item">
                <i class="fas fa-trophy"></i>
                <span>2.0k pts</span>
            </div>
            <div class="floating-bar-item">
                <i class="fas fa-car"></i>
                <span>Toyota Vios</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

def fetch_data_from_mongo(collection_name):
    """
    Fetch data from a MongoDB collection
    
    Args:
        collection_name (str): Name of the MongoDB collection
    
    Returns:
        list: List of documents with name and picture URL
    """
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")  # Update with your MongoDB URL
    client = MongoClient(mongo_url)
    db = client["settle"]  # Replace with your database name
    collection = db[collection_name]
    return list(collection.find({}, {"_id": 0, "name": 1, "picture_url": 1}))

def render_section(title, buttons):
    """
    Render a section with a title and grid of buttons
    
    Args:
        title (str): Section title
        buttons (list): List of dictionaries with button name and picture URL
    """
    st.markdown(f'<h2 class="section-title">{title}</h2>', unsafe_allow_html=True)
    
    # Create button grid using Streamlit columns
    num_columns = 4
    rows = (len(buttons) + num_columns - 1) // num_columns
    
    for i in range(rows):
        cols = st.columns(num_columns)
        for j in range(num_columns):
            idx = i * num_columns + j
            if idx < len(buttons):
                button = buttons[idx]
                with cols[j]:
                    st.markdown(f"""
                        <div style="text-align: center;">
                            <img src="{button['picture_url']}" alt="{button['name']}" style="width: 100%; border-radius: 5px; margin-bottom: 10px;">
                            <button style="width: 100%; background-color: #fff; border: none; border-radius: 5px; box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);">
                                {button['name']}
                            </button>
                        </div>
                    """, unsafe_allow_html=True)

def main():
    """Main function to render the Streamlit application"""
    config()
    render_floating_bar()  # Render the floating bar first
    
    # Add space to ensure the rest of the content is not overlapped
    st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)

    # Container for sections
    st.markdown('<div class="container">', unsafe_allow_html=True)
    
    # Fetch and render sections
    highlights = fetch_data_from_mongo("highlights")
    recommended = fetch_data_from_mongo("recommended")
    all_items = fetch_data_from_mongo("all_items")
    
    render_section("Highlights", highlights)
    render_section("Recommended", recommended)
    render_section("All", all_items)
    
    st.markdown('</div>', unsafe_allow_html=True)