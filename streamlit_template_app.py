import streamlit as st
import google.generativeai as genai
from PIL import Image
import streamlit.components.v1 as components

# Simplified CSS for styling
components.html("""
<style>
    .stButton > button {
        border-radius: 50px;
    }
    h1 {
        color: #F63366;
    }
</style>
""", height=0)

# Load banner image
image_path = 'Grantbuddy.webp'
try:
    image = Image.open(image_path)
    st.image(image, caption='Your Partner in Fundraising Success')
except Exception as e:
    st.error("Error loading image.")

# App Title and Description
st.title("Welcome to Grantbuddy!")
st.write("AI-driven assistant to aid you in proposal writing and fundraising efforts.")

# Initialize GenerativeAI client
genai.configure(api_key=st.secrets.get("GOOGLE_API_KEY", ""))

# Ensure proper initialization of session state variables
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = ""
if "debug" not in st.session_state:
    st.session_state.debug = []

# Function to initialize chat sessions
def initialize_chat_session():
    try:
        # Create generative model instance
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-002",
            generation_config={
                "temperature": 0.5
            }
        )
        
        # Define initial rich message structure
        initial_messages = [
            {"parts": [{"text": "Let's start the session with basic information."}]},
            {"parts": [{"text": "Okay, I am ready to process your requests."}]}
        ]

        if st.session_state.pdf_content:
            initial_messages.extend([
                {"parts": [{"text": f"Here is the PDF content:\n\n{st.session_state.pdf_content}"}]},
                {"parts": [{"text": "PDF content received and noted."}]}
            ])

        # Start a chat session with properly structured messages
        st.session_state.chat_session = model.start_chat(history=initial_messages)

    except Exception as e:
        st.error(f"Error during chat initialization: {e}")
        st.session_state.debug.append(f"Chat initialization error: {e}")

# Execute session initialization
initialize_chat_session()

# Debug information
st.sidebar.title("Debug Info")
for debug_msg in st.session_state.debug:
    st.sidebar.write(debug_msg)
