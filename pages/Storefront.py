import streamlit as st
import utils
import pandas as pd

st.set_page_config(page_title="Furnicon Store", page_icon="🛍️", layout="wide")

st.title("🛍️ Furnicon")
st.markdown("---")

products = utils.get_all_products()

if not products:
    st.info("Inventory Empty.")
else:
    for item in products:
        col_img, col_info = st.columns([0.4, 0.6])
        
        with col_img:
            variations = item.get("variations", [])
            tab_labels = ["Front"] + [f"View {i+1}" for i in range(len(variations))]
            tabs = st.tabs(tab_labels)
            
            with tabs[0]:
                if "image_obj" in item: st.image(item["image_obj"], use_container_width=True)
            
            for i, var_img in enumerate(variations):
                with tabs[i+1]: st.image(var_img, use_container_width=True)

        with col_info:
            st.subheader(item.get("title", "Product"))
            st.caption(f"Brand: {item.get('brand', 'Generic')}")
            
            c1, c2 = st.columns([0.3, 0.7])
            c1.markdown(f"## ${item.get('price', 0)}")
            c2.button("Add to Cart", key=f"btn_{item['id']}")
            
            st.write(item.get("description", ""))
            
            st.markdown("### Technical Details")
            
            # The Amazon Table
            spec_data = {
                "Colour": item.get("colour"),
                "Frame Material": item.get("frame_material"),
                "Style": item.get("style"),
                "Finish": item.get("furniture_finish"),
                "Seat Height": item.get("seat_height"),
                "Seat Width": item.get("seat_width"),
                "Leg Style": item.get("leg_style"),
                "Dimensions": item.get("dimensions_str")
            }
            # Filter empty
            clean_specs = {k: v for k, v in spec_data.items() if v}
            
            st.table(pd.DataFrame(list(clean_specs.items()), columns=["Feature", "Details"]))
            
        st.markdown("---")