import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from PIL import Image

# Streamlit configuration
st.set_page_config(page_title="Grantbuddy", layout="wide")

# Display image
image_path = 'Grantbuddy.webp'
try:
    image = Image.open(image_path)
    st.image(image, caption='Prince (2024)', use_column_width=True)
except FileNotFoundError:
    st.error("Image file not found. Please check the file path.")
except Exception as e:
    st.error("An unexpected error occurred while loading the image.")

# Title and Description
st.title("Welcome to Grantbuddy!")
st.write("""
Grantbuddy is an advanced AI assistant specializing in proposal writing, budgeting, and impact storytelling 
for educators, NGO workers, and others involved in fundraising. Grantbuddy helps create compelling, comprehensive, 
and tailored proposals to meet your project needs.
""")
st.caption("Hello! I'm an AI here to help, but I might occasionally err. If that happens, a little grace and a virtual coffee would be lovely. Please verify important info as we continue!")

# Initialize the Generative AI client
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model" not in st.session_state:
    st.session_state.model_name = "gemini-1.5-flash-002"
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.5
if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = ""
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

# Sidebar for settings
with st.sidebar:
    st.title("Settings")
    st.caption(
        "Note: Gemini-1.5-pro-002 handles 2 requests/min, gemini-1.5-flash-002 handles 15 requests/min"
    )
    model_option = st.selectbox(
        "Select Model:", ["gemini-1.5-flash-002", "gemini-1.5-pro-002"]
    )
    if model_option != st.session_state.model_name:
        st.session_state.model_name = model_option
        st.session_state.messages = []
        st.session_state.chat_session = None
    temperature = st.slider("Temperature:", 0.0, 1.0, st.session_state.temperature, 0.1)
    st.session_state.temperature = temperature
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    clear_button = st.button("Clear Chat")

# Process uploaded PDF
if uploaded_pdf:
    try:
        pdf_reader = PdfReader(uploaded_pdf)
        pdf_text = ""
        for page in pdf_reader.pages:
            pdf_text += page.extract_text() + "\n"
        st.session_state.pdf_content = pdf_text
        # Reset chat session when new PDF is uploaded
        st.session_state.chat_session = None
    except Exception as e:
        st.error(f"Error processing PDF: {e}")

# Clear chat function
if clear_button:
    st.session_state.messages = []
    st.session_state.pdf_content = ""
    st.session_state.chat_session = None
    st.experimental_rerun()

# Load system prompt
def load_text_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        st.error("Instructions file not found.")
        return ""
    except Exception as e:
        st.error(f"Error loading text file: {e}")
        return ""

system_prompt = load_text_file('instructions.txt')

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
user_input = st.chat_input("Your message:")

if user_input:
    # Add user message to chat history
    current_message = {"role": "user", "content": user_input}
    st.session_state.messages.append(current_message)

    with st.chat_message("user"):
        st.markdown(current_message["content"])

    # Generate and display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        # Prepare messages for Gemini API
        if st.session_state.chat_session is None:
            generation_config = {
                "temperature": st.session_state.temperature,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
            model = genai.GenerativeModel(
                model_name=st.session_state.model_name,
                generation_config=generation_config,
            )
            
            # Initialize chat with system prompt and PDF content
            initial_messages = [
                {"role": "user", "content": f"System: {system_prompt}"},
                {"role": "model", "content": "Understood. I will follow these instructions."},
            ]
            
            if st.session_state.pdf_content:
                initial_messages.extend([
                    {"role": "user", "content": f"The following is the content of an uploaded PDF document. Please consider this information when responding to user queries:\n\n{st.session_state.pdf_content}"},
                    {"role": "model", "content": "I have received and will consider the PDF content in our conversation."}
                ])
            
            st.session_state.chat_session = model.start_chat(history=initial_messages)

        # Generate response with error handling
        try:
            response = st.session_state.chat_session.send_message(current_message["content"])

            full_response = response.text
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"An error occurred while generating the response: {e}")

    st.experimental_rerun()

# Debug information
st.sidebar.title("Debug Info")
for debug_msg in st.session_state.debug if "debug" in st.session_state else []:
    st.sidebar.text(debug_msg)
