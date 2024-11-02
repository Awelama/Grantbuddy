import streamlit as st
from PIL import Image
import google.generativeai as genai

# Load a welcome image
image_path = 'Grantbuddy.webp'
try:
    image = Image.open(image_path)
    st.image(image, caption='Your Partner in Fundraising Success')
except Exception as e:
    st.error("Error loading image.")

# Page Title
st.title("Welcome to Grantbuddy!")
st.write("AI-driven assistant to aid you in proposal writing and fundraising efforts.")

# Initialize GenerativeAI client
genai.configure(api_key=st.secrets.get("GOOGLE_API_KEY", ""))

# Initialize session state variables
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "debug" not in st.session_state:
    st.session_state.debug = []

# Function to initialize chat sessions
def initialize_chat_session():
    try:
        # Initiate the generative model
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-002",
            generation_config={"temperature": 0.5}
        )
        
        # Define initial messages with correct parts structure and roles
        initial_messages = [
            {"role": "model", "parts": [{"text": "Let's start the session with basic information."}]},
            {"role": "model", "parts": [{"text": "Okay, I am ready to process your requests."}]}
        ]

        # Start the chat session with initial messages
        st.session_state.chat_session = model.start_chat(history=initial_messages)
        
    except Exception as e:
        st.error(f"Error during chat initialization: {e}")
        st.session_state.debug.append(f"Chat initialization error: {e}")

# Initialize the session if not already started
if st.session_state.chat_session is None:
    initialize_chat_session()

# Chat input and display area
user_input = st.text_input("Type your message here:")

if st.button("Send"):
    if user_input:
        try:
            # Ensure the message being sent conforms to expected structure and role
            st.session_state.messages.append({"role": "user", "parts": [{"text": user_input}]})
            
            if st.session_state.chat_session:
                # Send the message to the model
                response = st.session_state.chat_session.send_message(
                    {"role": "user", "parts": [{"text": user_input}]}
                )
                
                # Assuming the text response is accessed directly, adjust accordingly
                grantbuddy_response = response.text  # or another available attribute, e.g., response.content if applicable
                
                st.session_state.messages.append({"role": "model", "parts": [{"text": grantbuddy_response}]})
            else:
                st.error("Chat session was not initialized correctly.")
        
        except Exception as e:
            st.error(f"Communication error with Grantbuddy: {e}")
            st.session_state.debug.append(f"Chat communication error: {e}")

# Display chat history
st.subheader("Chat History")
for msg in st.session_state.messages:
    role = "User" if msg["role"] == "user" else "Grantbuddy"
    for part in msg["parts"]:
        st.write(f"{role}: {part['text']}")

# Optional debug info
if st.session_state.debug:
    st.sidebar.title("Debug Info")
    for debug_msg in st.session_state.debug:
        st.sidebar.write(debug_msg)
