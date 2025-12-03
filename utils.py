import streamlit as st
import json
import time
from PIL import Image
from io import BytesIO

# --- CONFIGURATION ---
try:
    # Works for Tier 1 Keys
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

# --- 1. AMAZON ANALYST (Tier 1 Power) ---
def analyze_image_mock(image):
    if not client: return {}

    image_bytes = optimize_image(image)
    
    # Prompt for Dynamic Amazon Specs
    prompt = """
    You are an Amazon Catalog Specialist. Analyze this product image.
    1. Identify the Category (e.g. Chair, Lamp, Table).
    2. Extract the 8 most critical technical specifications for that category.
    
    Return a pure JSON object with this structure:
    {
        "title": "SEO Title (Brand + Spec + Type)",
        "description": "3-sentence technical description.",
        "category": "Detected Category",
        "price_estimate": 199.99,
        "technical_specifications": {
            "Material": "...",
            "Color": "...",
            "Dimensions": "...",
            "Assembly": "...",
            "Key Feature": "...",
            ... (Add category-specific fields)
        }
    }
    """

    try:
        # We use Gemini 2.0 Flash Exp because it is smarter at JSON than 1.5
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
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
        # Fallback to 1.5 Flash if 2.0 is busy (Tier 1 usually allows both)
        try:
            response = client.models.generate_content(
                model='gemini-1.5-flash',
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
        except:
            st.error(f"Analysis Error: {e}")
            return {}

# --- 2. IMAGE CONSISTENCY (Image-to-Image) ---
def generate_product_variations(original_image):
    """
    Uses Gemini 2.0 Flash (Multimodal) to rotate the object.
    Since you are Tier 1, we can send the image bytes directly.
    """
    if not client: return [original_image]

    image_bytes = optimize_image(original_image)
    generated_images = []
    
    # 3 Specific Views for E-commerce
    prompts = [
        "Generate a photorealistic image of THIS object viewed from the left side. White background.",
        "Generate a photorealistic image of THIS object viewed from the right side. White background.",
        "Generate a close-up detail shot of the material texture of THIS object."
    ]

    st.toast("🎨 Generating Consistent Angles (Tier 1 GPU)...")

    for p in prompts:
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash-exp', # The only model that does I2I well
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=p),
                            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg") # INPUT IMAGE
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_generation_config=types.ImageGenerationConfig(
                        number_of_images=1
                    )
                )
            )
            
            if response.generated_images:
                for img_blob in response.generated_images:
                    image_data = img_blob.image.image_bytes
                    generated_images.append(Image.open(BytesIO(image_data)))
            
            # Even on Tier 1, a tiny pause helps prevent "Burst" limits
            time.sleep(1)

        except Exception as e:
            print(f"Angle Gen Error: {e}")
            # If I2I fails, we silently skip that angle rather than crashing
            pass
    
    if not generated_images:
        st.warning("Could not generate variations. Returning original.")
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