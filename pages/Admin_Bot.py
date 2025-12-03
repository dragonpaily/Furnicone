import streamlit as st
import utils
from PIL import Image
import time

# --- PAGE CONFIG ---
st.set_page_config(page_title="Admin Console", layout="wide")

# --- CUSTOM CSS FOR "WORLD CLASS" LOOK ---
st.markdown("""
    <style>
        div.stButton > button {
            width: 100%;
            border-radius: 8px;
            font-weight: 600;
        }
        div[data-testid="stFileUploader"] {
            border: 2px dashed #ddd;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        h3 { font-weight: 700 !important; font-size: 1.4rem !important; }
        .sub-header { color: #666; font-size: 0.9rem; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- STATE MANAGEMENT ---
if "bot_status" not in st.session_state:
    st.session_state.bot_status = "idle" # idle, processing, review, done
if "draft_data" not in st.session_state:
    st.session_state.draft_data = {}

# --- HEADER SECTION ---
col_h1, col_h2 = st.columns([0.8, 0.2])
with col_h1:
    st.title("Furnicon Ingestion")
    st.caption("AI-Powered Cataloging Workflow")
with col_h2:
    if st.button("New Upload", type="secondary"):
        st.session_state.bot_status = "idle"
        st.session_state.draft_data = {}
        st.rerun()

st.markdown("---")

# =========================================================
# 1. UPLOAD VIEW (Clean & Centered)
# =========================================================
if st.session_state.bot_status == "idle":
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        with st.container(border=True):
            st.markdown("### 📤 Source Asset")
            st.write("Upload a product image to begin the automated pipeline.")
            
            uploaded_file = st.file_uploader("Drag and drop image here", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
            
            if uploaded_file:
                # Initialize Pipeline
                image = Image.open(uploaded_file)
                st.session_state.draft_data["image_obj"] = image
                st.session_state.bot_status = "processing"
                st.rerun()

# =========================================================
# 2. PROCESSING VIEW (System Log)
# =========================================================
elif st.session_state.bot_status == "processing":
    
    col_img, col_log = st.columns([0.3, 0.7])
    
    with col_img:
        st.image(st.session_state.draft_data["image_obj"], caption="Processing...", use_container_width=True)
    
    with col_log:
        st.subheader("⚙️ System Pipeline")
        
        # Professional Step-by-Step Log
        with st.status("Executing Neural Tasks...", expanded=True) as status:
            
            st.write("🔹 Connection established to Gemini 2.5 Flash...")
            # CALL BACKEND: TEXT ANALYSIS
            image = st.session_state.draft_data["image_obj"]
            ai_data = utils.analyze_image_mock(image)
            st.session_state.draft_data.update(ai_data)
            st.write(f"✅ Extracted Metadata: {ai_data.get('title', 'Unknown Product')}")
            
            st.write("🔹 Initializing Image Generation Engine...")
            # Prepare Visual Description for Consistency
            vis_desc = f"{ai_data.get('colour', '')} {ai_data.get('style', '')} {ai_data.get('category', 'item')}"
            
            # CALL BACKEND: IMAGE GENERATION
            variations = utils.generate_product_variations(image, description=vis_desc)
            st.session_state.draft_data["variations"] = variations
            st.write(f"✅ Generated {len(variations)} High-Fidelity Angles.")
            
            status.update(label="Pipeline Complete", state="complete", expanded=False)
        
        time.sleep(1) # UX Pause
        st.session_state.bot_status = "review"
        st.rerun()

# =========================================================
# 3. REVIEW WORKSTATION (The "Amazon" Editor)
# =========================================================
elif st.session_state.bot_status == "review":
    
    # Split Layout: Visuals (Left) vs Data (Right)
    col_visuals, col_form = st.columns([0.4, 0.6], gap="medium")
    
    # --- LEFT PANEL: VISUAL ASSETS ---
    with col_visuals:
        st.subheader("🖼️ Visual Assets")
        
        # Main Asset Card
        with st.container(border=True):
            st.image(st.session_state.draft_data["image_obj"], use_container_width=True, caption="Master Asset")
        
        # Variations Gallery
        st.markdown("**Generated Angles**")
        vars = st.session_state.draft_data.get("variations", [])
        if vars:
            # Grid Layout for thumbnails
            c1, c2, c3 = st.columns(3)
            for idx, img in enumerate(vars):
                with [c1, c2, c3][idx % 3]:
                    st.image(img, use_container_width=True)
        else:
            st.warning("Generation skipped (using fallback).")

    # --- RIGHT PANEL: DATA EDITOR ---
    with col_form:
        st.subheader("📝 Catalog Metadata")
        
        # We use a single form for atomic submission
        with st.form("catalog_form"):
            
            # SECTION 1: CORE INFO
            with st.container(border=True):
                st.markdown("**General Information**")
                title = st.text_input("SEO Title", value=st.session_state.draft_data.get("title", ""))
                desc = st.text_area("Product Description", value=st.session_state.draft_data.get("description", ""), height=100)
                
                c_cat, c_brand = st.columns(2)
                category = c_cat.text_input("Category", value=st.session_state.draft_data.get("category", "Furniture"))
                brand = c_brand.text_input("Brand", value=st.session_state.draft_data.get("brand_generic", "Generic"))

            # SECTION 2: COMMERCIAL
            with st.container(border=True):
                st.markdown("**Pricing & Inventory**")
                c_price, c_stock = st.columns(2)
                
                # Handle price safely
                p_val = st.session_state.draft_data.get("price_estimate", 299.99)
                if isinstance(p_val, str): p_val = 299.99
                
                price = c_price.number_input("Price ($)", value=float(p_val))
                stock = c_stock.number_input("Stock Qty", value=50)

            # SECTION 3: AMAZON TECHNICAL SPECS
            with st.container(border=True):
                st.markdown("**Technical Specifications**")
                
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
                dims_input = c8.text_input("Dimensions (LxWxH)", value=st.session_state.draft_data.get("dimensions_str", ""))

            st.markdown(" ")
            
            # SUBMIT ACTION
            if st.form_submit_button("🚀 Publish to Storefront", type="primary", use_container_width=True):
                
                # Consolidate Data Package
                full_payload = {
                    "id": 0, # Auto-assigned by DB
                    "title": title, "description": desc, "category": category, "brand": brand,
                    "price": price, "stock": stock,
                    # Specs for the Table View
                    "colour": colour, "frame_material": frame, "style": style, 
                    "furniture_finish": finish, "seat_height": seat_h, "seat_width": seat_w,
                    "leg_style": legs, "dimensions_str": dims_input,
                    # Assets
                    "image_obj": st.session_state.draft_data["image_obj"],
                    "variations": st.session_state.draft_data["variations"]
                }
                
                # Send to Backend
                utils.save_product_to_store(full_payload)
                st.session_state.bot_status = "done"
                st.rerun()

# =========================================================
# 4. SUCCESS STATE
# =========================================================
elif st.session_state.bot_status == "done":
    
    st.balloons()
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        with st.container(border=True):
            st.markdown("""
                <div style="text-align: center; padding: 20px;">
                    <h2 style="color: #28a745; margin:0;">✅ Published</h2>
                    <p style="color: #666;">Product is live on the Storefront.</p>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("View Live Listing", use_container_width=True):
                st.switch_page("pages/Storefront.py")
                
            if st.button("Add Another Product", type="secondary", use_container_width=True):
                st.session_state.bot_status = "idle"
                st.session_state.draft_data = {}
                st.rerun()