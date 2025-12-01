import streamlit as st
import json
import time
from PIL import Image
from io import BytesIO

# --- CONFIGURATION ---
# SECURE METHOD: Read from .streamlit/secrets.toml
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except FileNotFoundError:
    st.error("Secrets file not found. Please create .streamlit/secrets.toml")
    st.stop()
except KeyError:
    st.error("GOOGLE_API_KEY not found in secrets.toml")
    st.stop()

# Import the new 2025 Google GenAI SDK
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
    st.error(f"Failed to initialize Google Client: {e}")
    client = None

# --- 1. GEMINI 2.5 FLASH (The Analyst) ---
def analyze_image_mock(image):
    """
    Uses Gemini 2.5 Flash to extract JSON metadata.
    """
    if not client: return {}

    try:
        # Convert PIL Image to Bytes for the API
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        image_bytes = img_byte_arr.getvalue()

        prompt = """
        Analyze this product image for an e-commerce database.
        Return ONLY a JSON object with these keys:
        - detected_type
        - primary_material
        - color
        - description (marketing copy, approx 30 words)
        - suggested_tags (list of 5 strings)
        """

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
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
        st.error(f"Gemini Analysis Failed: {e}")
        return {"detected_type": "Error", "description": str(e), "suggested_tags": []}

# --- 2. NANO BANANA (Gemini 2.5 Flash Image) ---
def generate_product_variations(original_image):
    """
    Uses Gemini 2.5 Flash Image (Nano Banana) to generate 3 angle variations.
    """
    generated_images = []
    
    if not client: return [original_image]

    try:
        # Convert PIL to Bytes
        img_byte_arr = BytesIO()
        original_image.save(img_byte_arr, format='PNG')
        image_bytes = img_byte_arr.getvalue()

        prompt = "Generate a professional product photo of this object from a slightly different side angle. Studio lighting, white background. High fidelity, photorealistic."

        response = client.models.generate_content(
            model='gemini-2.5-flash-image',
            contents=[
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                        types.Part.from_text(text=prompt)
                    ]
                )
            ],
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_generation_config=types.ImageGenerationConfig(
                    number_of_images=3, 
                    aspect_ratio="1:1"
                )
            )
        )

        if response.generated_images:
            for img_blob in response.generated_images:
                image_data = img_blob.image.image_bytes
                generated_images.append(Image.open(BytesIO(image_data)))
        
        return generated_images

    except Exception as e:
        # Fallback logic handles regions where 2.5 isn't live yet
        st.warning(f"Nano Banana Failed ({e}). Trying Imagen 3 fallback...")
        try:
            response = client.models.generate_images(
                model='imagen-3.0-generate-001',
                prompt=prompt,
                config=types.GenerateImagesConfig(number_of_images=3)
            )
            for img_blob in response.generated_images:
                image_data = img_blob.image.image_bytes
                generated_images.append(Image.open(BytesIO(image_data)))
            return generated_images
        except Exception as e2:
             st.error(f"All Generation Failed: {e2}")
             return [original_image]

# --- 3. DATABASE LOGIC ---
def init_db():
    if "db_products" not in st.session_state:
        st.session_state.db_products = []

def save_product_to_store(product_data):
    product_data["id"] = len(st.session_state.db_products) + 1
    st.session_state.db_products.append(product_data)

def get_all_products():
    return st.session_state.get("db_products", [])