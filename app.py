import streamlit as st
import google.generativeai as genai
import os
from PIL import Image, ImageDraw, ImageFont

# 1. Secure API Loading
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("🚨 CONFIG ERROR: The 'GEMINI_API_KEY' variable is not set in Render Settings.")
    st.stop()

genai.configure(api_key=api_key)
# Using flash for faster multimodal processing
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Function to Get AI Captions
def get_ai_caption(image):
    prompt = "Create a short 2-line meme caption for this image. Line 1: Top, Line 2: Bottom. Uppercase only."
    try:
        response = model.generate_content([prompt, image])
        # Troubleshooting: Ensure response actually has text
        if not response.text:
            return "AI ERROR", "NO CAPTION GENERATED"
        lines = response.text.strip().split('\n')
        top = lines[0].replace('"', '')
        bottom = lines[1].replace('"', '') if len(lines) > 1 else ""
        return top, bottom
    except Exception as e:
        return "ERROR", str(e)

# 3. Meme Creation Logic
def make_meme(img, top_text, bottom_text):
    draw = ImageDraw.Draw(img)
    width, height = img.size
    font_size = int(height / 7) # Increased size for better readability
    
    try:
        font = ImageFont.truetype("Impact.ttf", font_size)
    except:
        # Fallback for Render's Linux environment
        font = ImageFont.load_default(size=font_size)

    def draw_text(text, y_pos):
        bbox = draw.textbbox((0, 0), text, font=font) # Modern Pillow text measurement
        x = (width - (bbox[2] - bbox[0])) / 2
        # Draw with black outline for visibility
        draw.text((x, y_pos), text, font=font, fill="white", stroke_width=3, stroke_fill="black")

    draw_text(top_text, 10)
    draw_text(bottom_text, height - font_size - 20)
    return img

# 4. Streamlit UI (2026 Updated Syntax)
st.title("🤖 AI Meme Generator")
uploaded_file = st.file_uploader("Upload Image", type=["jpg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    # Use width='stretch' to fix the Render log error
    st.image(image, caption="Uploaded", width='stretch')
    
    if st.button("Generate Meme"):
        with st.spinner("AI is working..."):
            top, bottom = get_ai_caption(image)
            if top == "ERROR":
                st.error(f"API Error: {bottom}")
            else:
                meme = make_meme(image.copy(), top, bottom)
                st.image(meme, caption="Final Meme", width='stretch')