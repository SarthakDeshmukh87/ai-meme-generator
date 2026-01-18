import streamlit as st
import google.generativeai as genai
import os
import textwrap
import time
from PIL import Image, ImageDraw, ImageFont

# 1. API Configuration
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("🚨 GEMINI_API_KEY missing! Add it to your Environment Variables.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. Advanced AI Caption Logic with Styles
def get_ai_caption(image, style_choice):
    # Style prompts to fix "lame" jokes
    style_prompts = {
        "Sarcastic": "Be extremely sarcastic and cynical. Use dark situational irony.",
        "Existential": "Focus on existential dread, modern struggle, and the absurdity of life.",
        "Classic": "Standard witty internet humor. Observational and relatable."
    }
    
    selected_style = style_prompts.get(style_choice, style_prompts["Sarcastic"])
    
    prompt = f"""
    Analyze this image. {selected_style}
    Create a viral meme caption. 
    Return ONLY two lines:
    Line 1: Top caption
    Line 2: Bottom caption
    Keep it witty and uppercase.
    """
    
    try:
        # Temperature 0.9 makes it more creative/unpredictable
        response = model.generate_content(
            [prompt, image],
            generation_config={"temperature": 0.9}
        )
        lines = response.text.strip().split('\n')
        top = lines[0].replace('"', '').upper()
        bottom = lines[1].replace('"', '').upper() if len(lines) > 1 else ""
        return top, bottom
    except Exception as e:
        if "429" in str(e):
            return "LIMIT REACHED", "TRY AGAIN IN 1 MINUTE"
        return "AI ERROR", "COULD NOT GENERATE"

# 3. Dynamic Scaling Meme Logic (Mobile-Fit)
def make_meme(img, top_text, bottom_text):
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # Text must fit within 90% width and 25% height
    max_w, max_h = width * 0.9, height * 0.25

    def get_scaling_font(text):
        size = int(height / 8) # Starting size
        while size > 15:
            try:
                font = ImageFont.truetype("Impact.ttf", size)
            except:
                font = ImageFont.load_default(size=size)
            
            # Wrap text based on current font size
            avg_char = size * 0.55
            chars = max(1, int(max_w / avg_char))
            wrapped = textwrap.wrap(text, width=chars)
            
            # Calculate pixel height of wrapped block
            total_h = len(wrapped) * (size + 5)
            
            if total_h <= max_h:
                # Final check on pixel width
                longest = max(wrapped, key=len)
                bbox = draw.textbbox((0, 0), longest, font=font)
                if (bbox[2] - bbox[0]) <= max_w:
                    return font, wrapped, size
            size -= 3
        return font, wrapped, size

    def draw_text_block(text, pos):
        font, wrapped, size = get_scaling_font(text)
        line_h = size + 5
        y = 20 if pos == "top" else height - (len(wrapped) * line_h) - 40
        
        for line in wrapped:
            bbox = draw.textbbox((0, 0), line, font=font)
            x = (width - (bbox[2] - bbox[0])) / 2
            stroke = max(2, size // 15)
            draw.text((x, y), line, font=font, fill="white", 
                      stroke_width=stroke, stroke_fill="black")
            y += line_h

    draw_text_block(top_text, "top")
    draw_text_block(bottom_text, "bottom")
    return img

# 4. Streamlit App Layout
st.set_page_config(page_title="AI Meme Engine", layout="centered")
st.title("🖼️ AI Meme Engine")

# Sidebar for style selection
style = st.sidebar.selectbox("Choose Humor Style", ["Sarcastic", "Existential", "Classic"])
st.sidebar.info("Sarcastic/Existential modes provide 'edgier' humor.")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    # Optimized for Vercel/Render memory limits
    if image.width > 1200:
        image.thumbnail((1200, 1200))
        
    st.image(image, caption="Your Image", width="stretch")
    
    if st.button("Generate AI Meme"):
        with st.spinner("🤖 Cooking up some irony..."):
            top, bottom = get_ai_caption(image, style)
            meme_img = make_meme(image.copy(), top, bottom)
            
            st.image(meme_img, caption="Final Result", width="stretch")
            
            # Download button
            meme_img.save("meme.png")
            with open("meme.png", "rb") as f:
                st.download_button("📥 Download Meme", f, "meme_result.png")