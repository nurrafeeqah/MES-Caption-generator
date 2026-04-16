import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# 1. Setup Gemini using Streamlit's Secret System
if "GEMINI_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_KEY"])
else:
    st.error("Missing API Key! Add GEMINI_KEY to your Streamlit Cloud Secrets.")

model = genai.GenerativeModel('gemini-3-flash-preview')

# 2. Helper Functions
def fetch_blog_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('h1').text if soup.find('h1') else "Blog Post"
        paragraphs = soup.find_all('p')
        text = " ".join([p.text for p in paragraphs[:15]])
        return title, text
    except Exception as e:
        return None, str(e)

def generate_caption(title, content, platform):
    prompts = {
        "LinkedIn": f"Write a professional LinkedIn post for: {title}. Context: {content}. Structure: Hook, Value points, and CTA.",
        "Instagram": f"Write an engaging Instagram caption for: {title}. Context: {content}. Use emojis and 3 hashtags.",
        "YouTube": f"Write a YouTube description and 3 click-worthy titles for: {title}. Context: {content}."
    }
    instruction = "You are a viral social media manager. Make the reader want to click the link."
    response = model.generate_content(f"{instruction} {prompts[platform]}")
    return response.text

# 3. Streamlit UI
st.set_page_config(page_title="Viral Caption Architect", page_icon="✍️")
st.title("✍️ Viral Caption Architect")
st.markdown("Transform blog URLs into high-converting social media posts.")

blog_url = st.text_input("Paste Blog URL here:")
platform = st.selectbox("Select Platform", ["LinkedIn", "Instagram", "YouTube"])

if st.button("Generate Content"):
    if blog_url:
        with st.spinner('Gemini 3 is crafting your post...'):
            title, content = fetch_blog_content(blog_url)
            if title:
                caption = generate_caption(title, content, platform)
                st.subheader(f"🚀 Your {platform} Post")
                st.write(caption)
                st.divider()
                st.info(f"**Source Link:** {blog_url}")
            else:
                st.error("Scrape failed. Check the URL.")
    else:
        st.warning("Please enter a URL.")
