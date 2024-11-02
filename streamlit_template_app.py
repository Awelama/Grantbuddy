import streamlit as st
import google.generativeai as genai
from PIL import Image
import streamlit.components.v1 as components

# Streamlit configuration and custom CSS
st.set_page_config(page_title="Grantbuddy", layout="wide")
components.html("""
<style>
    .stButton > button {
        border-radius: 50px;
        background-color: #0073e6;
        color: white;
        font-size: 16px;
        padding: 10px 20px;
    }
    h1 {
        color: #F63366;
    }
    .sidebar .sidebar-content {
        background-color: #F0F2F6;
        color: #262730;
    }
</style>
""", height=0)

# Banner image
image_path = 'Grantbuddy.webp'
try:
    image = Image.open(image_path)
    st.image(image, caption='Your Partner in Fundraising Success', use_column_width=True)
except FileNotFoundError:
    st.error("Image file not found. Please check the file path.")
except Exception as e:
    st.error("An unexpected error occurred while loading the image.")

# Title and Description
st.title("Welcome to Grantbuddy!")
st.write("""
**Grantbuddy** is your advanced AI assistant specializing in proposal writing, budgeting, and impact storytelling 
for educators, NGO workers, and others in fundraising. Grantbuddy helps create compelling, comprehensive, and tailored proposals to meet your project needs.
""")
st.caption("AI is a support tool—remember to consult with experts for critical decisions.")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model_name" not in st.session_state:
    st.session_state.model_name = "gemini-1.5-flash-002"
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.5
if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = ""
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "debug" not in st.session_state:
    st.session_state.debug = []

# Placeholder for model initialization
def initialize_chat_session():
    try:
        model = genai.GenerativeModel(
            model_name=st.session_state.model_name,
            generation_config={
                "temperature": st.session_state.temperature,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
        
        # Verify the structure of initial_messages
        initial_messages = [
            {"role": "user", "content": "Let's start the session with basic information."},
            {"role": "model", "content": "Okay, I am ready to process your requests."}
        ]

        if st.session_state.pdf_content:
            initial_messages.append(
                {"role": "user", "content": f"Here is the PDF content:\n\n{st.session_state.pdf_content}"}
            )
            initial_messages.append(
                {"role": "model", "content": "PDF content received and noted."}
            )

        st.session_state.chat_session = model.start_chat(history=initial_messages)

    except KeyError as e:
        st.error(f"A KeyError occurred: {e}")
        st.session_state.debug.append(f"KeyError during chat session initialization: {e}")

initialize_chat_session()

# Debug information
st.sidebar.title("Debug Info")
for debug_msg in st.session_state.debug:
    st.sidebar.text(debug_msg)
