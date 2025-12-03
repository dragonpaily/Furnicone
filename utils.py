import streamlit as st
import json
import time
import traceback
import base64
from PIL import Image
from io import BytesIO

# --- CONFIGURATION ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except (FileNotFoundError, KeyError):
    st.error("Missing .streamlit/secrets.toml")
    st.stop()

try:
    from google import genai
    from google.genai import types
except ImportError:
    st.error("Library missing. Please run: pip install -r requirements.txt")
    st.stop()

# Initialize Client
try:
    client = genai.Client(api_key=GOOGLE_API_KEY)
except Exception as e:
    st.error(f"Client Error: {e}")
    client = None

# --- HELPER ---
def optimize_image(image):
    img_copy = image.copy()
    img_copy.thumbnail((1024, 1024))
    if img_copy.mode in ("RGBA", "P"):
        img_copy = img_copy.convert("RGB")
    img_byte_arr = BytesIO()
    img_copy.save(img_byte_arr, format='JPEG', quality=85)
    return img_byte_arr.getvalue()

# --- ERROR LOGGER ---
def log_error(context, error):
    error_msg = f"❌ **Error in {context}:**\n\n{str(error)}"
    st.session_state["global_error"] = error_msg
    print(f"[{context}] {error}")

# --- 1. AMAZON ANALYST (Reliable Flat JSON) ---
def analyze_image_mock(image):
    if not client: return {}

    try:
        image_bytes = optimize_image(image)
        
        # RESTORED: The specific, flat prompt that worked
        prompt = """
        Analyze this product image for an Amazon listing.
        Return a pure JSON object with these EXACT keys:
        {
            "title": "SEO Product Title",
            "description": "3-sentence technical description",
            "brand_generic": "Suggested Brand Name",
            "category": "General Category (e.g. Chair)",
            "colour": "Main Color",
            "frame_material": "Material",
            "style": "Style",
            "furniture_finish": "Finish",
            "seat_height": "Height",
            "seat_width": "Width",
            "leg_style": "Leg Type",
            "dimensions_str": "LxWxH cm"
        }
        """

        response = client.models.generate_content(
            model='gemini-2.5-flash', # Robust Text Model
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                        types.Part.from_text(text=prompt)
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)

    except Exception as e:
        log_error("Text Analysis", e)
        return {}

# --- 2. IMAGE GENERATION (Gemini 2.5 Flash Image) ---
def generate_product_variations(original_image, description=""):
    """
    Uses gemini-2.5-flash-image with the Dictionary Config Fix to prevent crashes.
    """
    if not client: return [original_image]

    image_bytes = optimize_image(original_image)
    generated_images = []
    
    # 3 Angles
    prompts = [
        "Generate a photorealistic product image of this object viewed from the left side. White background.",
        "Generate a photorealistic product image of this object viewed from the right side. White background.",
        "Generate a close-up detail shot of the material texture."
    ]

    st.toast("🎨 Generating Angles (Gemini 2.5)...")
    target_model = 'gemini-2.5-flash-image'

    for i, p in enumerate(prompts):
        success = False
        
        # --- ATTEMPT 1: Image-to-Image ---
        try:
            # Using Pure Dict config to bypass SDK type errors
            response = client.models.generate_content(
                model=target_model,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=p),
                            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
                        ]
                    )
                ],
                config={ "response_modalities": ["IMAGE"] }
            )
            
            if hasattr(response, 'parts'):
                for part in response.parts:
                    if part.inline_data:
                        img_bytes = part.inline_data.data
                        if isinstance(img_bytes, str):
                            img_bytes = base64.b64decode(img_bytes)
                        
                        img = Image.open(BytesIO(img_bytes))
                        generated_images.append(img)
                        success = True

        except Exception as e:
            # Silent fail for I2I, allow fallback
            pass

        # --- ATTEMPT 2: Text-to-Image Fallback ---
        if not success:
            try:
                # Add description to prompt for context
                text_prompt = f"{p} Object details: {description}. High fidelity, 4k."
                
                response = client.models.generate_content(
                    model=target_model,
                    contents=[
                        types.Content(
                            role="user",
                            parts=[
                                types.Part.from_text(text=text_prompt)
                            ]
                        )
                    ],
                    config={ "response_modalities": ["IMAGE"] }
                )
                
                if hasattr(response, 'parts'):
                    for part in response.parts:
                        if part.inline_data:
                            img_bytes = part.inline_data.data
                            if isinstance(img_bytes, str):
                                img_bytes = base64.b64decode(img_bytes)
                            
                            img = Image.open(BytesIO(img_bytes))
                            generated_images.append(img)
                            success = True
            
            except Exception as e:
                log_error(f"Strategy B (T2I) Angle {i+1}", e)

        time.sleep(1)

    if not generated_images:
        st.warning("⚠️ Generation Failed. Returning original.")
        return [original_image]
        
    return generated_images

# --- 3. DATABASE ---
def init_db():
    if "db_products" not in st.session_state:
        st.session_state.db_products = []

def save_product_to_store(product_data):
    product_data["id"] = len(st.session_state.db_products) + 1
    st.session_state.db_products.append(product_data)

def get_all_products():
    return st.session_state.get("db_products", [])