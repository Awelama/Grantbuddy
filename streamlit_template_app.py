import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from PIL import Image

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

# Initialize Gemini client
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Chat", "PDF Upload", "Settings"])

if page != st.session_state.current_page:
    st.session_state.current_page = page
    st.experimental_rerun()

# Home page
def home_page():
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

    if st.button("Get Started"):
        st.session_state.current_page = "Chat"
        st.experimental_rerun()

# Chat page
def chat_page():
    st.title("Chat with Grantbuddy")

    # Load system prompt
    system_prompt = "You are Grantbuddy, an AI assistant specializing in grant writing, budgeting, and impact storytelling."

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
                    {"role": "user", "parts": [f"System: {system_prompt}"]},
                    {"role": "model", "parts": ["Understood. I will follow these instructions."]},
                ]
                
                if st.session_state.pdf_content:
                    initial_messages.extend([
                        {"role": "user", "parts": [f"The following is the content of an uploaded PDF document. Please consider this information when responding to user queries:\n\n{st.session_state.pdf_content}"]},
                        {"role": "model", "parts": ["I have received and will consider the PDF content in our conversation."]}
                    ])
                
                st.session_state.chat_session = model.start_chat(history=initial_messages)

            # Generate response with error handling
            try:
                with st.spinner("Generating response..."):
                    response = st.session_state.chat_session.send_message(current_message["content"])

                full_response = response.text
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.error(f"An error occurred while generating the response: {e}")

        st.experimental_rerun()

# PDF Upload page
def pdf_upload_page():
    st.title("Upload PDF")

    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_pdf:
        try:
            with st.spinner("Processing PDF..."):
                pdf_reader = PdfReader(uploaded_pdf)
                pdf_text = ""
                for page in pdf_reader.pages:
                    pdf_text += page.extract_text() + "\n"
                st.session_state.pdf_content = pdf_text
                st.success(f"PDF processed successfully! {len(pdf_text)} characters extracted.")
            
            # Display a preview of the extracted text
            st.subheader("PDF Content Preview")
            st.text_area("Extracted Text", pdf_text[:500] + "...", height=200)
            
        except Exception as e:
            st.error(f"Error processing PDF: {e}. Please try again with a different file.")

# Settings page
def settings_page():
    st.title("Settings")

    st.caption("Note: Gemini-1.5-pro-002 can only handle 2 requests per minute, gemini-1.5-flash-002 can handle 15 per minute")

    model_option = st.selectbox(
        "Select Model:", ["gemini-1.5-flash-002", "gemini-1.5-pro-002"],
        index=0 if st.session_state.model_name == "gemini-1.5-flash-002" else 1
    )

    if model_option != st.session_state.model_name:
        st.session_state.model_name = model_option
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.success("Model updated. Chat history has been cleared.")

    temperature = st.slider("Temperature:", 0.0, 1.0, st.session_state.temperature, 0.1)
    if temperature != st.session_state.temperature:
        st.session_state.temperature = temperature
        st.success("Temperature updated.")

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.success("Chat history cleared.")

# Display the selected page
if st.session_state.current_page == "Home":
    home_page()
elif st.session_state.current_page == "Chat":
    chat_page()
elif st.session_state.current_page == "PDF Upload":
    pdf_upload_page()
elif st.session_state.current_page == "Settings":
    settings_page()
