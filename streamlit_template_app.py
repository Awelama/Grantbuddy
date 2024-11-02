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

# Initialize session state variables
for state_var in ["chat_session", "messages", "pdf_content", "debug"]:
    if state_var not in st.session_state:
        st.session_state[state_var] = [] if state_var in ["messages", "debug"] else None

# Initialization function
def initialize_chat_session():
    try:
        # Create generative model instance
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-002",
            generation_config={"temperature": 0.5}
        )

        # Correct structure with 'parts'
        initial_messages = [
            {"parts": [{"text": "Let's start the session with basic information."}]},
            {"parts": [{"text": "Okay, I am ready to process your requests."}]}
        ]

        if st.session_state.pdf_content:
            initial_messages.extend([
                {"parts": [{"text": f"Here is the PDF content:\n\n{st.session_state.pdf_content}"}]},
                {"parts": [{"text": "PDF content received and noted."}]}
            ])

        # Consider using model correctly, ensure all methods required are called correctly
        st.session_state.chat_session = model.start_chat(history=initial_messages)

    except Exception as e:
        st.error(f"Error during chat initialization: {e}")
        st.session_state.debug.append(f"Chat initialization error: {e}")

# Start session if not already started
if st.session_state.chat_session is None:
    initialize_chat_session()

# Chat input and display area
user_input = st.text_input("Type your message here:", key="user_input")

if st.button("Send"):
    if user_input:
        # Ensure the correct format for messages with correct structure
        st.session_state.messages.append({"role": "user", "parts": [{"text": user_input}]})
        try:
            if st.session_state.chat_session:
                response = st.session_state.chat_session.send_message({"role": "user", "parts": [{"text": user_input}]})
                grantbuddy_response = response.text
                st.session_state.messages.append({"role": "model", "parts": [{"text": grantbuddy_response}]})
            else:
                st.error("Chat session is not initialized correctly. Please restart the session.")
        except Exception as e:
            st.error(f"Communication error with Grantbuddy: {e}")
            st.session_state.debug.append(f"Chat communication error: {e}")

st.subheader("Chat History")
for msg in st.session_state.messages:
    role = "User" if msg["role"] == "user" else "Grantbuddy"
    for part in msg["parts"]:
        st.write(f"{role}: {part['text']}")

# Optional: Debugging info
if st.session_state.debug:
    st.sidebar.title("Debug Info")
    for debug_msg in st.session_state.debug:
        st.sidebar.write(debug_msg)
