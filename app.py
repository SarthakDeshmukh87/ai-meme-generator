import streamlit as st
import google.generativeai as genai
import os
from PIL import Image, ImageDraw, ImageFont

# 1. API Configuration
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("🚨 GEMINI_API_KEY not found! Set it in Render's Environment Variables.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. AI Caption Logic
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
        # Clean text and convert to uppercase for classic meme look
        top = lines[0].replace('"', '').upper()
        bottom = lines[1].replace('"', '').upper() if len(lines) > 1 else ""
        return top, bottom
    except Exception as e:
        return "AI ERROR", "COULD NOT GENERATE CAPTION"

# 3. Enhanced Image Processing (Bigger Text + Outline)
def make_meme(img, top_text, bottom_text):
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # FONT SIZE INCREASED: Now 1/7th of image height (was 1/10th)
    # This makes the captions much more prominent.
    font_size = int(height / 7) 
    
    try:
        # If you have Impact.ttf in your repo, it uses that
        font = ImageFont.truetype("Impact.ttf", font_size)
    except:
        # Fallback for Render/Linux server environments
        font = ImageFont.load_default(size=font_size)

    def draw_text_with_outline(text, pos_y):
        # Calculate centering
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) / 2
        
        # Stroke width scales with font size for better readability
        thickness = max(2, int(font_size / 15))
        
        # Draw text with built-in stroke (Pillow 10.0+ feature)
        draw.text((x, pos_y), text, font=font, fill="white", 
                  stroke_width=thickness, stroke_fill="black")

    # Draw Top and Bottom Captions
    draw_text_with_outline(top_text, 20)
    draw_text_with_outline(bottom_text, height - font_size - 40)
    
    return img

# 4. Streamlit UI (2026 Standards)
st.set_page_config(page_title="AI Meme Generator", page_icon="🖼️")
st.title("🖼️ AI Meme Generator")

uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    # Using width="stretch" to replace the deprecated use_container_width
    st.image(image, caption="Original Image", width="stretch")
    
    if st.button("Generate Meme"):
        with st.spinner("🤖  Thinking of a joke..."):
            top, bottom = get_ai_caption(image)
            
            # Create the meme using a copy of the image
            meme_result = make_meme(image.copy(), top, bottom)
            
            st.image(meme_result, caption="Generated Meme", width="stretch")
            
            # Save and Download
            meme_result.save("meme.png")
            with open("meme.png", "rb") as file:
                st.download_button("📥 Download Meme", file, "my_meme.png", "image/png")