# Home.py (Main file)

import streamlit as st
from PIL import Image
import os

# Streamlit configuration
st.set_page_config(page_title="Welcome to Grantbuddy!", layout="wide")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model_name" not in st.session_state:
    st.session_state.model_name = "gemini-1.5-pro-002"
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.5
if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = ""
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# Display image
image_path = 'Grantbuddy.webp'
try:
    image = Image.open(image_path)
    st.image(image, caption='Created by Awelama (2024)', use_column_width=True)
except Exception as e:
    st.error(f"Error loading image: {e}")

st.title("Welcome to Grantbuddy!")
st.markdown("""
    ### Your AI Assistant for Grant Writing and Impact Storytelling

    Grantbuddy is an advanced AI assistant specializing in:
    - 📝 Proposal writing
    - 💰 Budgeting
    - 📊 Impact storytelling

    Use the sidebar to navigate through different features:
    - **Chat**: Interact with Grantbuddy for assistance
    - **PDF Upload**: Upload and process grant-related documents
    - **Settings**: Customize your Grantbuddy experience

    *Note: While Grantbuddy is designed to be helpful, always verify important information.*
""")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Chat", "PDF Upload", "Settings"])

if page != st.session_state.current_page:
    st.session_state.current_page = page
    st.experimental_rerun()

# Load and display the selected page
if st.session_state.current_page == "Chat":
    exec(open("pages/01_Chat.py").read())
elif st.session_state.current_page == "PDF Upload":
    exec(open("pages/02_PDF_Upload.py").read())
elif st.session_state.current_page == "Settings":
    exec(open("pages/03_Settings.py").read())

# You can keep the "Get Started" button if you want, but it will just set the page to "Chat"
if st.button("Get Started"):
    st.session_state.current_page = "Chat"
    st.experimental_rerun()
