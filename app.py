import streamlit as st
import google.generativeai as genai
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

# Secure API setup
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("API Key missing! Add GEMINI_API_KEY to Vercel Environment Variables.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

def get_ai_caption(image):
    prompt = "Create a funny 2-line meme caption. Line 1: Top, Line 2: Bottom. Short and uppercase."
    try:
        response = model.generate_content([prompt, image])
        lines = response.text.strip().split('\n')
        top = lines[0].replace('"', '').upper()
        bottom = lines[1].replace('"', '').upper() if len(lines) > 1 else ""
        return top, bottom
    except:
        return "AI ERROR", "TRY AGAIN"

def make_meme(img, top_text, bottom_text):
    draw = ImageDraw.Draw(img)
    w, h = img.size
    f_size = int(h / 12) # Adjusted for mobile balance
    
    try:
        font = ImageFont.truetype("Impact.ttf", f_size)
    except:
        font = ImageFont.load_default(size=f_size)

    def draw_wrap(text, pos):
        # Calculate wrapping for mobile screens
        chars = max(1, int(w / (f_size * 0.5)))
        lines = textwrap.wrap(text, width=chars)
        y = 20 if pos == "top" else h - (len(lines) * (f_size + 10)) - 40
        
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            x = (w - (bbox[2] - bbox[0])) / 2
            # High-visibility stroke
            draw.text((x, y), line, font=font, fill="white", 
                      stroke_width=max(2, f_size//15), stroke_fill="black")
            y += f_size + 10

    draw_wrap(top_text, "top")
    draw_wrap(bottom_text, "bottom")
    return img

# UI
st.title("🤖 AI Meme Generator")
file = st.file_uploader("Upload Image", type=["jpg", "png"])

if file:
    img = Image.open(file)
    st.image(img, width="stretch")
    if st.button("Generate"):
        with st.spinner("🤖 Thinking..."):
            t, b = get_ai_caption(img)
            meme = make_meme(img.copy(), t, b)
            st.image(meme, width="stretch")