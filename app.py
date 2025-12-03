import streamlit as st
import utils

# Initialize Database
utils.init_db()

st.set_page_config(page_title="Furnicon Hub", page_icon="🛋️", layout="wide")

st.title("🛋️ Furnicon System")
st.subheader("Internal Prototype: Phase 1")

st.markdown("""
### Instructions:
1. Go to **Admin Bot** (Sidebar) to upload and process images.
2. Go to **Storefront** (Sidebar) to view the published website.
""")

st.success("System Online.")