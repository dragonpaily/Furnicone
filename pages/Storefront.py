import streamlit as st
import utils

st.set_page_config(page_title="Live Store", page_icon="🛍️", layout="wide")

st.title("🛍️ Modern Furniture Store")
st.caption("Live view of the 'db_products' database")

products = utils.get_all_products()

if not products:
    st.container(border=True).info("🏪 Store empty. Use Admin Bot to add items.")
else:
    cols = st.columns(3)
    
    for index, item in enumerate(products):
        with cols[index % 3]:
            with st.container(border=True):
                # --- GALLERY LOGIC ---
                variations = item.get("variations", [])
                
                if variations:
                    # Tabs for Main + Variations
                    tabs = st.tabs(["Main"] + [f"View {i+1}" for i in range(len(variations))])
                    
                    with tabs[0]:
                        if "image_obj" in item:
                            st.image(item["image_obj"], use_container_width=True)
                    
                    for i, var_img in enumerate(variations):
                        with tabs[i+1]:
                            st.image(var_img, use_container_width=True)
                else:
                    # Fallback (Single Image)
                    if "image_obj" in item:
                        st.image(item["image_obj"], use_container_width=True)
                
                # Details
                title = item.get("title", "Untitled")
                price = item.get("price", 0.00)
                
                st.subheader(title)
                st.markdown(f"### ${price}")
                
                dims = item.get("dimensions_str", "N/A")
                mat = item.get("primary_material", "N/A")
                
                st.text(f"Dim: {dims}")
                st.text(f"Mat: {mat}")
                
                tags = item.get("suggested_tags", [])
                if tags:
                    st.caption(", ".join(tags))
                
                st.button("Add to Cart 🛒", key=f"cart_{index}", type="primary", use_container_width=True)