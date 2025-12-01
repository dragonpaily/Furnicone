import streamlit as st
import utils
from PIL import Image
import time

st.set_page_config(page_title="Admin Bot", page_icon="🍌")

st.title("🍌 Nano Banana Chat")

# --- CHAT HISTORY & STATE ---
# We need to remember the chat history so it doesn't disappear on reload
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Hi! I'm Nano Banana. Upload a product image to start."}
    ]
if "current_image" not in st.session_state:
    st.session_state.current_image = None
if "bot_status" not in st.session_state:
    st.session_state.bot_status = "awaiting_upload" # Options: awaiting_upload, awaiting_dims, done

# --- RENDER CHAT HISTORY ---
# This loop draws the previous conversation every time the app updates
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        # If this message was an image upload, show the image again
        if msg.get("image_data"):
            st.image(msg["image_data"], width=250)

# --- LOGIC ENGINE ---

# 1. IMAGE UPLOADER (Only show if we are waiting for one)
if st.session_state.bot_status == "awaiting_upload":
    uploaded_file = st.file_uploader("Upload Image", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
    
    if uploaded_file:
        # A. Process Image
        image = Image.open(uploaded_file)
        st.session_state.current_image = image
        
        # B. Add User's "Upload" to chat history
        st.session_state.messages.append({
            "role": "user", 
            "content": "Here is the product image:",
            "image_data": image
        })
        
        # C. Add Bot's "Analysis" to chat history
        with st.chat_message("assistant"):
            with st.spinner("Analyzing pixels and texture..."):
                ai_data = utils.analyze_image_mock(image)
                st.session_state.draft_data = ai_results = ai_data
                st.session_state.draft_data["image_obj"] = image
            
            response_text = f"✅ I've analyzed the image.\n\n**Detected:** {ai_data['detected_type']}\n**Material:** {ai_data['primary_material']}\n\nI cannot see the size. Please enter dimensions below:"
            st.write(response_text)
            
            # Save Bot response to history
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
            # Update Status
            st.session_state.bot_status = "awaiting_dims"
            st.rerun()

# 2. DIMENSION INPUT (Only show if we have an image but no size)
if st.session_state.bot_status == "awaiting_dims":
    with st.chat_message("assistant"):
        st.write("📝 **Product Details Form**")
        
        # We use a form so the page doesn't reload on every keystroke
        with st.form("chat_form"):
            title = st.text_input("Title", value=f"AI {st.session_state.draft_data['detected_type']}")
            price = st.number_input("Price ($)", value=150.0)
            c1, c2, c3 = st.columns(3)
            h = c1.number_input("H (cm)", min_value=1)
            w = c2.number_input("W (cm)", min_value=1)
            d = c3.number_input("D (cm)", min_value=1)
            
            submitted = st.form_submit_button("Publish to Store 🚀")
            
            if submitted:
                # Add User's "Form Submit" to history
                st.session_state.messages.append({
                    "role": "user", 
                    "content": f"Dimensions are {h}x{w}x{d}. Title: {title}"
                })
                
                # Save Data
                st.session_state.draft_data["title"] = title
                st.session_state.draft_data["price"] = price
                st.session_state.draft_data["dimensions_str"] = f"{h}x{w}x{d} cm"
                utils.save_product_to_store(st.session_state.draft_data)
                
                # Bot Success Message
                success_msg = "🎉 Perfect. I have published this item to the Storefront."
                st.session_state.messages.append({"role": "assistant", "content": success_msg})
                
                # Reset for next item
                st.session_state.bot_status = "done"
                st.rerun()

# 3. RESET BUTTON (To start over)
if st.session_state.bot_status == "done":
    with st.chat_message("assistant"):
        st.write("🎉 Perfect. I have published this item to the Storefront.")
        if st.button("Process Another Item"):
            # Clear history and restart
            st.session_state.messages = [{"role": "assistant", "content": "👋 Ready for the next one. Upload image."}]
            st.session_state.bot_status = "awaiting_upload"
            st.session_state.current_image = None
            st.rerun()