import streamlit as st
import google.generativeai as genai
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

# --- 1. SETUP THE AI ---
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-3.0-flash')

# --- 2. GET THE JOKE FROM AI ---
def get_joke(image):
    # We tell the AI to be funny and sarcastic here
    prompt = "Look at this image and write a sarcastic 2-line meme caption. Line 1 is top, Line 2 is bottom. Uppercase only."
    try:
        response = model.generate_content([prompt, image])
        lines = response.text.strip().split('\n')
        top = lines[0].upper()
        bottom = lines[1].upper() if len(lines) > 1 else ""
        return top, bottom
    except:
        return "AI IS THINKING", "PLEASE TRY AGAIN"

# --- 3. DRAW TEXT ON THE IMAGE ---
def draw_meme(img, top_text, bottom_text):
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # We start with a big font size
    font_size = int(height / 10)
    try:
        font = ImageFont.truetype("Impact.ttf", font_size)
    except:
        font = ImageFont.load_default(size=font_size)

    # This part centers the text and adds a black outline
    def put_text(text, y_pos):
        # Wrap text so it doesn't go off the screen
        wrapped_lines = textwrap.wrap(text, width=20) 
        current_y = y_pos
        for line in wrapped_lines:
            # Math to find the middle of the image
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) / 2
            # Draw white text with a black border
            draw.text((x, current_y), line, font=font, fill="white", stroke_width=2, stroke_fill="black")
            current_y += font_size

    # Put top text at the top (20px down) and bottom text at the bottom
    put_text(top_text, 20)
    put_text(bottom_text, height - (font_size * 2) - 40)
    return img

# --- 4. THE WEBSITE INTERFACE ---
st.title("🖼️ Easy AI Meme Maker")

upload = st.file_uploader("Upload a photo", type=["jpg", "png"])

if upload:
    user_img = Image.open(upload)
    st.image(user_img, width="stretch") # Shows your photo
    
    if st.button("Make Meme"):
        top, bottom = get_joke(user_img) # Ask AI for joke
        final_meme = draw_meme(user_img.copy(), top, bottom) # Draw it
        st.image(final_meme, width="stretch") # Show final meme