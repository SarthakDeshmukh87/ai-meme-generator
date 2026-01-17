import streamlit as st
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import textwrap
import io
import os
import os
import google.generativeai as genai

# This looks for the key in Render's environment variables
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
# --- CONFIGURATION ---
# Replace with your actual API Key or set as an environment variable
genai.configure(api_key="AIzaSyDIUEQhbsjKj9el4EGUD5TcTKCRWxkXb5M")
model = genai.GenerativeModel('gemini-2.5-flash')

def get_ai_caption(image):
    """Uses AI to analyze the image and return a funny meme caption."""
    prompt = """
    Analyze this image and create a funny meme caption. 
    Return the result in exactly this format:
    TOP: [Top text]
    BOTTOM: [Bottom text]
    Keep it short, witty, and relevant to the objects or expressions in the image.
    """
    response = model.generate_content([prompt, image])
    text = response.text
    
    # Simple parsing logic
    try:
        top = text.split("TOP:")[1].split("BOTTOM:")[0].strip()
        bottom = text.split("BOTTOM:")[1].strip()
        return top, bottom
    except:
        return "WHEN THE AI WORKS", "BUT THE PARSING FAILS"

def make_meme(img, top_text, bottom_text):
    img = img.convert("RGB")
    draw = ImageDraw.Draw(img)
    w, h = img.size
    font_size = int(h * 0.08)
    
    # Try to find Impact font, else default
    try:
        font = ImageFont.truetype("Impact.ttf", font_size)
    except:
        font = ImageFont.load_default()

    def draw_text(text, y_pos):
        lines = textwrap.wrap(text.upper(), width=w//(font_size//2))
        for line in lines:
            line_w = draw.textlength(line, font=font)
            x = (w - line_w) / 2
            # Outline for readability
            for adj in range(-2, 3):
                draw.text((x+adj, y_pos), line, font=font, fill="black")
                draw.text((x, y_pos+adj), line, font=font, fill="black")
            draw.text((x, y_pos), line, font=font, fill="white")
            y_pos += font_size

    draw_text(top_text, 20)
    draw_text(bottom_text, h - (font_size * 2) - 20)
    return img

# --- STREAMLIT UI ---
st.set_page_config(page_title="AI Meme Genius")
st.title("🤖 AI Meme Generator")

uploaded_file = st.file_uploader("Upload an image...", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)
    
    if st.button("✨ Generate AI Caption"):
        with st.spinner("AI is thinking of a joke..."):
            top, bottom = get_ai_caption(image)
            
            # Create the meme
            result_img = make_meme(image, top, bottom)
            
            st.subheader("Resulting Meme:")
            st.image(result_img, use_container_width=True)
            
            # Download Button
            buf = io.BytesIO()
            result_img.save(buf, format="PNG")
            st.download_button("Download Meme", buf.getvalue(), "ai_meme.png")

            st.write(f"**AI suggested:** {top} | {bottom}")