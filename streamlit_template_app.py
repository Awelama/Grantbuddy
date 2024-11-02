import streamlit as st
from PIL import Image
import google.generativeai as genai
import json
from datetime import datetime

# Custom CSS for message styling
st.markdown("""
<style>
.user-message {
    padding: 10px;
    border-radius: 15px;
    background-color: #e6f3ff;
    margin: 5px 0;
}
.bot-message {
    padding: 10px;
    border-radius: 15px;
    background-color: #f0f0f0;
    margin: 5px 0;
}
</style>
""", unsafe_allow_html=True)

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
if "session_start_time" not in st.session_state:
    st.session_state.session_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Sidebar for customization and session info
with st.sidebar:
    st.subheader("Customization")
    temperature = st.slider("AI Creativity", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
    max_tokens = st.number_input("Max Response Length", min_value=50, max_value=500, value=200, step=50)
    
    st.subheader("Session Info")
    st.write(f"Messages in this session: {len(st.session_state.messages)}")
    st.write(f"Session started: {st.session_state.session_start_time}")

# Function to initialize chat sessions
def initialize_chat_session():
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-002",
            generation_config={"temperature": temperature, "max_output_tokens": max_tokens}
        )
        
        initial_messages = [
            {"role": "model", "parts": [{"text": "Let's start the session with basic information."}]},
            {"role": "model", "parts": [{"text": "Okay, I am ready to process your requests."}]}
        ]

        st.session_state.chat_session = model.start_chat(history=initial_messages)
        
    except Exception as e:
        st.error(f"Error during chat initialization: {e}")
        st.session_state.debug.append(f"Chat initialization error: {e}")

# Initialize the session if not already started
if st.session_state.chat_session is None:
    initialize_chat_session()

# Chat input area
user_input = st.chat_input("Type your message here:", key="user_input")

# Preserve context toggle
preserve_context = st.checkbox("Preserve conversation context", value=True)

if user_input:
    try:
        st.session_state.messages.append({"role": "user", "parts": [{"text": user_input}]})
        
        if st.session_state.chat_session:
            with st.spinner("Grantbuddy is thinking..."):
                if preserve_context:
                    history = st.session_state.messages
                else:
                    history = [st.session_state.messages[-1]]
                
                response = st.session_state.chat_session.send_message(
                    {"role": "user", "parts": [{"text": user_input}]}
                )
                
                grantbuddy_response = response.text
                
                st.session_state.messages.append({"role": "model", "parts": [{"text": grantbuddy_response}]})
        else:
            st.error("Chat session was not initialized correctly.")
    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please try again. If the problem persists, try clearing your chat history or reloading the page.")
        st.session_state.debug.append(f"Chat communication error: {e}")

# Display chat history
st.subheader("Chat History")
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-message">User: {msg["parts"][0]["text"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-message">Grantbuddy: {msg["parts"][0]["text"]}</div>', unsafe_allow_html=True)

# User feedback
if st.session_state.messages:
    with st.expander("Was this response helpful?"):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍 Yes"):
                st.success("Thank you for your feedback!")
        with col2:
            if st.button("👎 No"):
                feedback = st.text_area("How can we improve?")
                if st.button("Submit Feedback"):
                    st.success("Thank you for your feedback!")
                    # Here you could add logic to store or process the feedback

# Clear chat history button
if st.button("Clear Chat History"):
    st.session_state.messages = []
    st.experimental_rerun()

# Export chat history
if st.button("Export Chat History"):
    chat_history = json.dumps(st.session_state.messages, indent=2)
    st.download_button(
        label="Download Chat History",
        data=chat_history,
        file_name="chat_history.json",
        mime="application/json"
    )

# Optional debug info
if st.session_state.debug:
    st.sidebar.title("Debug Info")
    for debug_msg in st.session_state.debug:
        st.sidebar.write(debug_msg)
