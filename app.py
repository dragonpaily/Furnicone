import streamlit as st
import utils
import time
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Furnicon Dashboard",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INITIALIZE BACKEND ---
utils.init_db()
products = utils.get_all_products()

# --- ENTERPRISE CSS STYLING ---
st.markdown("""
    <style>
        /* Global Font & Background */
        .stApp {
            background-color: #f8f9fa;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }
        
        /* Hero Section */
        .hero-container {
            background: linear-gradient(135deg, #2c3e50 0%, #4ca1af 100%);
            padding: 3rem;
            border-radius: 12px;
            color: white;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .hero-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .hero-subtitle {
            font-size: 1.1rem;
            opacity: 0.9;
            font-weight: 300;
        }

        /* Metric Cards */
        div[data-testid="stMetric"] {
            background-color: white;
            border: 1px solid #e9ecef;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.9rem;
            color: #6c757d;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem;
            color: #212529;
            font-weight: 600;
        }

        /* Action Containers */
        .action-header {
            font-size: 1.2rem;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }
        
        /* Table Styling */
        div[data-testid="stDataFrame"] {
            background-color: white;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #e9ecef;
        }
    </style>
""", unsafe_allow_html=True)

# --- HERO HEADER ---
st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Furnicon Operations</div>
        <div class="hero-subtitle">AI-Powered Product Catalog & Digital Asset Management</div>
    </div>
""", unsafe_allow_html=True)

# --- KPI METRICS ---
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total SKUs", value=len(products))

with col2:
    # Determine Status based on client init
    status = "Active" if utils.client else "Disconnected"
    st.metric(label="Gemini Engine", value=status)

with col3:
    st.metric(label="Asset Library", value=f"{len(products) * 4} Images")

with col4:
    st.metric(label="System Version", value="v2.1 (Tier 1)")

st.markdown("---")

# --- MAIN NAVIGATION ---
st.markdown("### Workflow Modules")

col_left, col_right = st.columns(2, gap="medium")

with col_left:
    with st.container(border=True):
        st.markdown('<div class="action-header">Admin Console</div>', unsafe_allow_html=True)
        st.write("Ingest raw product images, extract technical specifications via Vision AI, and generate consistent multi-angle assets.")
        
        st.markdown(" ") # Spacer
        if st.button("Launch Admin Bot", type="primary", use_container_width=True):
            st.switch_page("pages/Admin_Bot.py")

with col_right:
    with st.container(border=True):
        st.markdown('<div class="action-header">Live Storefront</div>', unsafe_allow_html=True)
        st.write("Preview the customer-facing e-commerce experience with interactive 3D-consistent galleries and specification tables.")
        
        st.markdown(" ") # Spacer
        if st.button("View Storefront", use_container_width=True):
            st.switch_page("pages/Storefront.py")

# --- RECENT DATA TABLE ---
st.markdown("### Recent Inventory")

if products:
    # Transform data for a cleaner table view
    recent_items = products[-5:] # Last 5 items
    
    clean_data = []
    for p in recent_items:
        clean_data.append({
            "Product Name": p.get("title", "Untitled"),
            "Category": p.get("category", "Furniture"),
            "Price": f"${p.get('price', 0)}",
            "Variations": len(p.get("variations", [])),
            "ID": p.get("id")
        })
    
    # Display interactive dataframe
    df = pd.DataFrame(clean_data)
    st.dataframe(
        df, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Product Name": st.column_config.TextColumn(width="large"),
            "Price": st.column_config.TextColumn(width="small"),
        }
    )

else:
    st.info("No inventory found. Initialize the database by adding products in the Admin Console.")