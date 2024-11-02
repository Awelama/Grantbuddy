import streamlit as st
import google.generativeai as genai
from PIL import Image

# Load banner image
image_path = 'Grantbuddy.webp'
try:
    image = Image.open(image_path)
    st.image(image, caption='Your Partner in Fundraising Success')
except Exception as e:
    st.error("Error loading image.")

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
        
        # Define initial message structure
        initial_messages = [
            {"role": "model", "content": {"text": "Let's start the session with basic information."}},
            {"role": "model", "content": {"text": "Okay, I am ready to process your requests."}}
        ]

        if st.session_state.pdf_content:
            initial_messages.extend([
                {"role": "model", "content": {"text": f"Here is the PDF content:\n\n{st.session_state.pdf_content}"}},
                {"role": "model", "content": {"text": "PDF content received and noted."}}
            ])

        # Start a chat session with properly structured messages
        st.session_state.chat_session = model.start_chat(history=initial_messages)

    except Exception as e:
        st.error(f"Error during chat initialization: {e}")
        st.session_state.debug.append(f"Chat initialization error: {e}")

# Execute session initialization
if st.session_state.chat_session is None:
    initialize_chat_session()

# Chat input and display area
user_input = st.text_input("Type your message here:", key="user_input")

if st.button("Send"):
    if user_input:
        st.session_state.messages.append({"role": "user", "content": {"text": user_input}})
        try:
            response = st.session_state.chat_session.send_message({"role": "user", "content": {"text": user_input}})
            grantbuddy_response = response.text
            st.session_state.messages.append({"role": "model", "content": {"text": grantbuddy_response}})
        except Exception as e:
            st.error(f"Communication error with Grantbuddy: {e}")
            st.session_state.debug.append(f"Chat communication error: {e}")
        finally:
            # Avoid infinite loop by checking and rerunning the specific segment
            st.experimental_rerun()

st.subheader("Chat History")
for msg in st.session_state.messages:
    role = "User" if msg["role"] == "user" else "Grantbuddy"
    st.write(f"{role}: {msg['content']['text']}")

# Optional: Debugging info
if st.session_state.debug:
    st.sidebar.title("Debug Info")
    for debug_msg in st.session_state.debug:
        st.sidebar.write(debug_msg)
