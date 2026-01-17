import streamlit as st
import google.generativeai as genai
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

# 1. API Configuration
# On Vercel, ensure you added 'GEMINI_API_KEY' in Settings -> Environment Variables
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("🚨 GEMINI_API_KEY not found! Please add it to your Vercel Environment Variables.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. AI Caption Logic
def get_ai_caption(image):
    prompt = """
    Analyze this image and create a funny meme caption. 
    Return ONLY two lines of text:
    Line 1: Top caption
    Line 2: Bottom caption
    Keep it short, witty, and in UPPERCASE.
    """
    try:
        response = model.generate_content([prompt, image])
        lines = response.text.strip().split('\n')
        top = lines[0].replace('"', '').upper()
        bottom = lines[1].replace('"', '').upper() if len(lines) > 1 else ""
        return top, bottom
    except Exception as e:
        return "API ERROR", f"Details: {str(e)[:50]}"

# 3. Smart Meme Logic (Mobile-Ready)
def make_meme(img, top_text, bottom_text):
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # Adaptive Font Size (1/8th of image height)
    font_size = int(height / 8) 
    
    try:
        font = ImageFont.truetype("Impact.ttf", font_size)
    except:
        # Fallback for Vercel's Linux environment
        font = ImageFont.load_default(size=font_size)

    def draw_wrapped_text(text, position):
        # Prevent text overflow on mobile: wrap text based on width
        avg_char_width = font_size * 0.5
        chars_per_line = max(1, int(width / avg_char_width))
        
        wrapped_lines = textwrap.wrap(text, width=chars_per_line)
        line_height = font_size + 10
        
        if position == "top":
            current_y = 30
        else:
            current_y = height - (len(wrapped_lines) * line_height) - 50

        for line in wrapped_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_w = bbox[2] - bbox[0]
            x = (width - line_w) / 2
            
            # Thick black stroke for high contrast
            stroke = max(2, int(font_size / 10))
            draw.text((x, current_y), line, font=font, fill="white", 
                      stroke_width=stroke, stroke_fill="black")
            current_y += line_height

    draw_wrapped_text(top_text, "top")
    draw_wrapped_text(bottom_text, "bottom")
    return img

# 4. UI Layout
st.set_page_config(page_title="AI Meme Gen", page_icon="🤖")
st.title("🤖 AI Meme Generator")

uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    
    # OPTIMIZATION: Resize large phone photos for Vercel Serverless limits
    if image.width > 1500 or image.height > 1500:
        image.thumbnail((1200, 1200))
        
    st.image(image, caption="Uploaded Image", width="stretch")
    
    if st.button("Generate Meme"):
        with st.spinner("🤖 Thinking of a joke..."):
            top, bottom = get_ai_caption(image)
            
            # Create meme on a copy
            meme_result = make_meme(image.copy(), top, bottom)
            
            st.image(meme_result, caption="Your AI Meme", width="stretch")
            
            # Download Logic
            meme_result.save("final_meme.png")
            with open("final_meme.png", "rb") as f:
                st.download_button("📥 Download Meme", f, "meme.png", "image/png")