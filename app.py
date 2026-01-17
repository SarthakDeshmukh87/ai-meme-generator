import streamlit as st
import google.generativeai as genai
import os
import textwrap
from PIL import Image, ImageDraw, ImageFont

# 1. API Configuration
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("🚨 GEMINI_API_KEY not found! Please set it in Render Environment Variables.")
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
    Keep it short and witty.
    """
    try:
        response = model.generate_content([prompt, image])
        lines = response.text.strip().split('\n')
        top = lines[0].replace('"', '').upper()
        bottom = lines[1].replace('"', '').upper() if len(lines) > 1 else ""
        return top, bottom
    except Exception as e:
        return "AI ERROR", "COULD NOT GENERATE CAPTION"

# 3. Smart Meme Logic (Text Wrapping + Scaling)
def make_meme(img, top_text, bottom_text):
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # Font size scales with image height (10%)
    font_size = int(height / 10) 
    
    try:
        font = ImageFont.truetype("Impact.ttf", font_size)
    except:
        # Fallback for Linux/Render servers
        font = ImageFont.load_default(size=font_size)

    def draw_wrapped_text(text, position):
        # Calculate characters per line based on font size and image width
        # This prevents text from bleeding off edges on mobile
        avg_char_width = font_size * 0.55
        chars_per_line = max(1, int(width / avg_char_width))
        
        wrapped_lines = textwrap.wrap(text, width=chars_per_line)
        line_height = font_size + 10
        
        # Calculate starting Y position
        if position == "top":
            current_y = 20
        else:
            current_y = height - (len(wrapped_lines) * line_height) - 40

        for line in wrapped_lines:
            # Centering logic
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            x = (width - line_width) / 2
            
            # Thick black outline for readability
            stroke = max(2, int(font_size / 15))
            draw.text((x, current_y), line, font=font, fill="white", 
                      stroke_width=stroke, stroke_fill="black")
            current_y += line_height

    draw_wrapped_text(top_text, "top")
    draw_wrapped_text(bottom_text, "bottom")
    
    return img

# 4. Streamlit UI (2026 Updated Syntax)
st.set_page_config(page_title="AI Meme Generator", page_icon="🖼️")
st.title("🖼️ AI Meme Generator")

uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    # width="stretch" fixes the Render/Streamlit log warning
    st.image(image, caption="Original Photo", width="stretch")
    
    if st.button("Generate Meme"):
        with st.spinner("🤖 Gemini is thinking..."):
            top, bottom = get_ai_caption(image)
            # Use image.copy() to preserve the original for future attempts
            meme_img = make_meme(image.copy(), top, bottom)
            
            st.image(meme_img, caption="Generated Meme", width="stretch")
            
            # Save for download
            meme_img.save("result.png")
            with open("result.png", "rb") as f:
                st.download_button("📥 Download Meme", f, "my_meme.png", "image/png")