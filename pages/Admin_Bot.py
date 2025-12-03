import streamlit as st
import utils
from PIL import Image

st.set_page_config(page_title="Admin Bot", page_icon="🍌")
st.title("🍌 Furnicon Admin")

# --- ERROR DASHBOARD ---
if "global_error" in st.session_state:
    st.error("🚨 SYSTEM CRASHED (See below)")
    st.code(st.session_state["global_error"], language="python")
    if st.button("Clear Error Log"):
        del st.session_state["global_error"]
        st.rerun()

# --- CHAT STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "👋 Upload a product."}]
if "bot_status" not in st.session_state:
    st.session_state.bot_status = "awaiting_upload" 
if "draft_data" not in st.session_state:
    st.session_state.draft_data = {}

# Render Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("image_data"): st.image(msg["image_data"], width=250)
        if msg.get("variations"):
            cols = st.columns(3)
            for i, var_img in enumerate(msg["variations"]):
                with cols[i]: st.image(var_img, use_container_width=True)

# 1. UPLOAD LOGIC
if st.session_state.bot_status == "awaiting_upload":
    uploaded_file = st.file_uploader("Upload Product", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.session_state.messages.append({"role": "user", "content": "Product Image:", "image_data": image})
        
        with st.chat_message("assistant"):
            # 1. Extract Specs
            with st.spinner("Extracting Specs (Gemini 2.5)..."):
                ai_data = utils.analyze_image_mock(image)
                st.session_state.draft_data = ai_data
                st.session_state.draft_data["image_obj"] = image
            
            # 2. Generate Angles
            vis_desc = f"{ai_data.get('colour', '')} {ai_data.get('style', '')} {ai_data.get('category', 'item')}"
            
            with st.spinner("Generating Angles (Gemini 2.5 Image)..."):
                variations = utils.generate_product_variations(image, description=vis_desc)
                st.session_state.draft_data["variations"] = variations
            
            st.write(f"✅ Extracted Specs for **{ai_data.get('title', 'Product')}**")
            st.write("**Generated Angles:**")
            cols = st.columns(3)
            for i, var_img in enumerate(variations):
                with cols[i]: st.image(var_img, use_container_width=True)
            
            st.session_state.messages.append({"role": "assistant", "content": "Draft Created. Verify specs below.", "variations": variations})
            st.session_state.bot_status = "awaiting_dims"
            st.rerun()

# 2. DATA VERIFICATION FORM
if st.session_state.bot_status == "awaiting_dims":
    with st.chat_message("assistant"):
        st.write("📝 **Verify Amazon Specifications**")
        
        with st.form("amazon_form"):
            # We use .get() to prevent crashes if a key is missing
            title = st.text_input("Title", value=st.session_state.draft_data.get("title", ""))
            desc = st.text_area("Description", value=st.session_state.draft_data.get("description", ""))
            
            c1, c2 = st.columns(2)
            price = c1.number_input("Price ($)", value=299.99)
            stock = c2.number_input("Stock", value=50)
            
            st.markdown("---")
            st.markdown("**Technical Specs**")
            
            c1, c2 = st.columns(2)
            colour = c1.text_input("Colour", value=st.session_state.draft_data.get("colour", ""))
            frame = c2.text_input("Frame Material", value=st.session_state.draft_data.get("frame_material", ""))
            
            c3, c4 = st.columns(2)
            style = c3.text_input("Style", value=st.session_state.draft_data.get("style", ""))
            finish = c4.text_input("Finish", value=st.session_state.draft_data.get("furniture_finish", ""))
            
            c5, c6 = st.columns(2)
            seat_h = c5.text_input("Seat Height", value=st.session_state.draft_data.get("seat_height", ""))
            seat_w = c6.text_input("Seat Width", value=st.session_state.draft_data.get("seat_width", ""))
            
            c7, c8 = st.columns(2)
            legs = c7.text_input("Leg Style", value=st.session_state.draft_data.get("leg_style", ""))
            brand = c8.text_input("Brand", value=st.session_state.draft_data.get("brand_generic", ""))

            dims_input = st.text_input("Dimensions (LxWxH)", value=st.session_state.draft_data.get("dimensions_str", ""))

            if st.form_submit_button("Publish to Storefront 🚀"):
                # Save Data
                full_data = st.session_state.draft_data
                full_data.update({
                    "title": title, "price": price, "description": desc, "stock": stock,
                    "colour": colour, "frame_material": frame, "style": style, 
                    "furniture_finish": finish, "seat_height": seat_h, "seat_width": seat_w,
                    "leg_style": legs, "brand": brand, "dimensions_str": dims_input
                })
                
                utils.save_product_to_store(full_data)
                
                st.session_state.messages.append({"role": "assistant", "content": "🎉 Published! Check the Storefront page."})
                st.session_state.bot_status = "done"
                st.rerun()

# 3. RESET
if st.session_state.bot_status == "done":
    with st.chat_message("assistant"):
        st.write("🎉 Product is LIVE.")
        if st.button("Add Next Product"):
            st.session_state.messages = [{"role": "assistant", "content": "👋 Ready."}]
            st.session_state.bot_status = "awaiting_upload"
            st.session_state.draft_data = {}
            st.rerun()