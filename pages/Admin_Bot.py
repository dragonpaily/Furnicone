import streamlit as st
import utils
from PIL import Image
import pandas as pd

st.set_page_config(page_title="Admin Bot", page_icon="🍌")
st.title("🍌 Furnicon Admin")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "👋 Upload a product."}]
if "bot_status" not in st.session_state:
    st.session_state.bot_status = "awaiting_upload" 
if "draft_data" not in st.session_state:
    st.session_state.draft_data = {}

# Chat Render
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if msg.get("image_data"): st.image(msg["image_data"], width=250)
        if msg.get("variations"):
            cols = st.columns(3)
            for i, var_img in enumerate(msg["variations"]):
                with cols[i]: st.image(var_img, use_container_width=True)

# 1. UPLOAD
if st.session_state.bot_status == "awaiting_upload":
    uploaded_file = st.file_uploader("Upload Product", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.session_state.messages.append({"role": "user", "content": "Product Image:", "image_data": image})
        
        with st.chat_message("assistant"):
            with st.spinner("Analyzing & Generating..."):
                # 1. Extract Specs
                ai_data = utils.analyze_image_mock(image)
                
                # 2. Generate Angles (FIXED: No longer needs description arg)
                variations = utils.generate_product_variations(image)
                
                st.session_state.draft_data = ai_data
                st.session_state.draft_data["image_obj"] = image
                st.session_state.draft_data["variations"] = variations
            
            st.write(f"✅ Identified Category: **{ai_data.get('category', 'Unknown')}**")
            st.write("**Generated Angles:**")
            cols = st.columns(3)
            for i, var_img in enumerate(variations):
                with cols[i]: st.image(var_img, use_container_width=True)
            
            st.session_state.messages.append({"role": "assistant", "content": "Draft Created. Verify specs below.", "variations": variations})
            st.session_state.bot_status = "awaiting_dims"
            st.rerun()

# 2. DYNAMIC SPEC FORM
if st.session_state.bot_status == "awaiting_dims":
    with st.chat_message("assistant"):
        st.write("📝 **Verify Specifications**")
        
        with st.form("dynamic_form"):
            # Fixed Core Fields
            title = st.text_input("Title", value=st.session_state.draft_data.get("title", ""))
            desc = st.text_area("Description", value=st.session_state.draft_data.get("description", ""))
            
            c1, c2 = st.columns(2)
            price = c1.number_input("Price ($)", value=float(st.session_state.draft_data.get("price_estimate", 199.99)))
            stock = c2.number_input("Stock", value=50)
            
            st.markdown("---")
            st.write("**Technical Specs (Editable)**")
            
            # Dynamic Table
            raw_specs = st.session_state.draft_data.get("technical_specifications", {})
            # Ensure raw_specs is a dictionary to prevent errors
            if not isinstance(raw_specs, dict): raw_specs = {"Error": "Could not parse specs"}
            
            df_specs = pd.DataFrame(
                {"Feature": list(raw_specs.keys()), "Details": list(raw_specs.values())}
            )
            
            edited_df = st.data_editor(df_specs, num_rows="dynamic", use_container_width=True)

            if st.form_submit_button("Publish 🚀"):
                # Convert back to dict
                final_specs = dict(zip(edited_df["Feature"], edited_df["Details"]))
                
                full_data = {
                    "id": 0,
                    "title": title, "description": desc, "price": price, "stock": stock,
                    "specs": final_specs,
                    "image_obj": st.session_state.draft_data["image_obj"],
                    "variations": st.session_state.draft_data["variations"]
                }
                
                utils.save_product_to_store(full_data)
                
                st.session_state.messages.append({"role": "assistant", "content": "🎉 Published!"})
                st.session_state.bot_status = "done"
                st.rerun()

# 3. RESET
if st.session_state.bot_status == "done":
    with st.chat_message("assistant"):
        if st.button("Add Next Product"):
            st.session_state.messages = [{"role": "assistant", "content": "👋 Ready."}]
            st.session_state.bot_status = "awaiting_upload"
            st.session_state.draft_data = {}
            st.rerun()