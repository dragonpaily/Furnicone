import streamlit as st
import time

# --- 1. MOCK AI VISION ---
def analyze_image_mock(image):
    """
    Simulates looking at a photo and extracting e-commerce tags.
    """
    time.sleep(1.0) # Simulate processing
    return {
        "category": "Furniture",
        "detected_type": "Accent Chair",
        "primary_material": "Velvet",
        "secondary_material": "Oak Wood",
        "suggested_tags": ["Modern", "Mid-Century", "Living Room"],
        "ai_confidence": 0.92
    }

# --- 2. DATABASE LOGIC ---
def init_db():
    if "db_products" not in st.session_state:
        st.session_state.db_products = []

def save_product_to_store(product_data):
    # Assign a simple ID
    product_data["id"] = len(st.session_state.db_products) + 1
    st.session_state.db_products.append(product_data)

def get_all_products():
    return st.session_state.get("db_products", [])