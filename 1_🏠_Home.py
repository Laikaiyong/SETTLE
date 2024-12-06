import streamlit as st
import pymongo
import certifi
import random

from pages.utils.search_button_utils import get_embedding, vector_search
from functools import partial

# MongoDB connection setup
ca = certifi.where()
MONGO_URI = st.secrets["mongo"]["host"]

@st.cache_resource
def init_connection():
    return pymongo.MongoClient(MONGO_URI, tlsCAFile=ca)

def config():
    """Configure Streamlit page settings and custom CSS."""
    st.set_page_config(
        page_title="SETTLE Home",
        page_icon="🚗",
        layout="wide"
    )
    st.markdown("""
        <style>
        * { box-sizing: border-box; }
        body { font-family: Arial, sans-serif; }
        .container { padding: 20px; }
        .section-title { text-align: center; font-size: 2em; margin-bottom: 20px; }
        .card { 
            border: 1px solid #ddd; 
            border-radius: 8px; 
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); 
            padding: 10px; 
            text-align: center; 
            margin: 10px; 
            background-color: #fff; 
            height: 250px; 
            display: flex; 
            flex-direction: column; 
            justify-content: space-between; 
        }
        .card img { 
            max-width: 100%; 
            max-height: 150px; 
            object-fit: cover; 
            border-radius: 5px; 
            margin-bottom: 10px; 
        }
        .card-name { 
            font-size: 1.2em; 
            font-weight: bold; 
            color: #333; 
            cursor: pointer; 
        }
        .card-clicks {
            font-size: 1em; 
            color: #666;
        }
        .highlighted { 
            background-color: #fffae6; 
            border: 2px solid #ffd700; 
        }
        .search-container {
            margin-bottom: 20px;
            text-align: center;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px; /* Space between the input and button */
        }

        .search-container input {
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            width: 50%; /* Adjust width as per your layout */
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .search-container input:focus {
            border-color: #ffa500;
            outline: none;
            box-shadow: 0 2px 8px rgba(255, 165, 0, 0.5);
        }

        .search-container button {
            padding: 10px 20px;
            background-color: #ffa500;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(255, 165, 0, 0.5);
        }

        .search-container button:hover {
            background-color: #ff8c00;
        }
        </style>
    """, unsafe_allow_html=True)

def render_section(title, items, highlight=False):
    """
    Render a section with a title and grid of styled cards.
    Args:
        title (str): Section title
        items (list): List of dictionaries with card details
        highlight (bool): Whether to apply a highlight style to the cards
    """
    st.markdown(f'<h2 class="section-title">{title}</h2>', unsafe_allow_html=True)
    st.markdown('<div class="container">', unsafe_allow_html=True)
    
    cols = st.columns(4)  # Four columns for grid layout
    for idx, item in enumerate(items):
        with cols[idx % 4]:  # Cycle through columns
            card_class = "card highlighted" if highlight else "card"
            st.markdown(f"""
                <div class="{card_class}">
                    <img src="{item['picture_url']}" alt="{item['name']}">
                    <div class="card-name">{item['name']}</div>
                    <div class="card-clicks">Clicks: {item['clicks']}</div>
                </div>
            """, unsafe_allow_html=True)

            # Bind a unique function for each button using partial
            if st.button("Select", key=f"click_{item['name']} + {str(random.random())}", on_click=partial(increment_clicks, item["name"])):
                st.success(f"Clicked on {item['name']}!")
                
def click_incrementing(item_name):
    st.session_state["item_name"] = item_name
    increment_clicks(st.session_state["item_name"])


def increment_clicks(item_name):
    """
    Increment clicks for a specific item.
    Args:
        collection_name (str): Name of the collection
        item_name (str): Name of the item to increment clicks for
    """
    try:
        client = init_connection()
        if not client:
            return
        
        db = client["Home"]
        collection = db["Home Icons"]
        
        collection.update_one(
            {"name": item_name},
            {"$inc": {"clicks": 1}}
        )
    except Exception as e:
        st.error(f"Error incrementing clicks for {item_name}: {e}")


def main():
    """Main function to render the Streamlit application."""
    config()
    
    # Styled Search Box with Button
    col_1, col_2 = st.columns(2)
    
    with col_1:
        search_word = st.text_input("Search")
    
    with col_2:
        searchClicked = st.button("🔎")

    if searchClicked:
        if search_word == None or search_word == "":
            st.warning("Keyword / Question is not typed")
        else:
            search_results = vector_search(search_word)
            render_section("Search Result", search_results)
            

    try:
        client = init_connection()
        db = client["Home"]
        collection = db["Home Icons"]
        items = list(collection.find({}, {
            "_id": 0,
            "name": 1,
            "picture_url": 1,
            "clicks": 1
        }))
        
        # Fetch top 4 items with the highest clicks
        highlighted_items = sorted(items, key=lambda x: x['clicks'], reverse=True)[:4]
        
        # Render highlighted section
        render_section("Most Popular", highlighted_items, highlight=True)
        
        # Render all items section
        render_section("All Items", items)
    except Exception as e:
        st.error(f"Error fetching data: {e}")

if __name__ == "__main__":
    main()
