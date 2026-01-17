import streamlit as st
import google.generativeai as genai
import os
from PIL import Image, ImageDraw, ImageFont

# 1. Setup API Key Securely
# It looks for "GEMINI_API_KEY" in Render's Environment Variables
api_key = os.getenv("AIzaSyDZtii1NWe8dqlzMyKRi3a1x1YJQf2aqB4")

if not api_key:
    st.error("🚨 API Key not found! Go to Render Settings -> Environment and add GEMINI_API_KEY.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Function to Get AI Captions
def get_ai_caption(image):
    prompt = """
    Analyze this image and create a funny meme caption. 
    Return ONLY two lines of text:
    Line 1: Top caption
    Line 2: Bottom caption
    Keep it short and witty.
    """
    try:
        response = model.generate_content([prompt, image])
        lines = response.text.strip().split('\n')
        top = lines[0].replace('"', '').upper()
        bottom = lines[1].replace('"', '').upper() if len(lines) > 1 else ""
        return top, bottom
    except Exception as e:
        return "ERROR", str(e)

# 3. Function to Draw Meme Text
def make_meme(img, top_text, bottom_text):
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # Font Logic: Try Impact, fallback to default if missing on Linux/Render
    font_size = int(height / 10)
    try:
        font = ImageFont.truetype("Impact.ttf", font_size)
    except:
        font = ImageFont.load_default()

    def draw_text_with_outline(text, pos_y):
        # Center the text
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) / 2
        
        # Draw black outline (shadow)
        for adj in range(-3, 4):
            draw.text((x+adj, pos_y), text, font=font, fill="black")
            draw.text((x, pos_y+adj), text, font=font, fill="black")
        
        # Draw white text
        draw.text((x, pos_y), text, font=font, fill="white")

    draw_text_with_outline(top_text, 10)
    draw_text_with_outline(bottom_text, height - font_size - 20)
    
    return img

# 4. Streamlit UI
st.set_page_config(page_title="AI Meme Generator", page_icon="🤖")
st.title("🤖 AI Meme Generator")
st.write("Upload a photo and let Gemini write the joke!")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Original Image", use_container_width=True)
    
    if st.button("Generate Meme"):
        with st.spinner("Gemini is thinking..."):
            top, bottom = get_ai_caption(image)
            meme_img = make_meme(image.copy(), top, bottom)
            
            st.image(meme_img, caption="Your AI Meme", use_container_width=True)
            
            # Download Button
            meme_img.save("meme.png")
            with open("meme.png", "rb") as file:
                st.download_button("Download Meme", file, "my_ai_meme.png", "image/png")