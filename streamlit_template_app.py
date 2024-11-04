import streamlit as st
from PIL import Image
import google.generativeai as genai
import json
from datetime import datetime
import pandas as pd
from io import BytesIO
from streamlit_icons import icon
import time

# Page configuration
st.set_page_config(page_title="Grantbuddy", page_icon="📝", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
    /* ... (previous CSS) ... */

    /* Chat bubble styling */
    .chat-bubble {
        padding: 10px 15px;
        border-radius: 20px;
        margin: 5px 0;
        max-width: 75%;
        word-wrap: break-word;
    }
    .user-bubble {
        background-color: #e6f3ff;
        margin-left: auto;
    }
    .bot-bubble {
        background-color: #f0f0f0;
        margin-right: auto;
    }
    .chat-container {
        display: flex;
        flex-direction: column;
    }

    /* Typing indicator */
    .typing-indicator {
        display: flex;
        justify-content: flex-start;
        align-items: center;
        padding: 10px;
    }
    .typing-indicator span {
        height: 10px;
        width: 10px;
        background-color: #9E9E9E;
        border-radius: 50%;
        display: inline-block;
        margin: 0 2px;
        animation: typing 1s infinite;
    }
    .typing-indicator span:nth-child(2) {
        animation-delay: 0.2s;
    }
    .typing-indicator span:nth-child(3) {
        animation-delay: 0.4s;
    }
    @keyframes typing {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-5px); }
        100% { transform: translateY(0px); }
    }

    /* Dark mode toggle */
    .dark-mode {
        background-color: #1E1E1E;
        color: #FFFFFF;
    }
    .dark-mode .stTextInput>div>div>input {
        background-color: #2D2D2D;
        color: #FFFFFF;
    }
    .dark-mode .stButton>button {
        background-color: #4CAF50;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_start_time" not in st.session_state:
    st.session_state.session_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
if "progress" not in st.session_state:
    st.session_state.progress = {"Project Description": False, "Budget Planning": False, "Impact Assessment": False}
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# Initialize GenerativeAI client
genai.configure(api_key=st.secrets.get("GOOGLE_API_KEY", ""))

# Function to initialize chat sessions
def initialize_chat_session():
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-002",
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 250
            }
        )
        
        initial_messages = [
            {"role": "model", "parts": [{"text": "Let's start the session with basic information."}]},
            {"role": "model", "parts": [{"text": "Okay, I am ready to process your requests."}]}
        ]

        st.session_state.chat_session = model.start_chat(history=initial_messages)
        
    except Exception as e:
        st.error(f"Error during chat initialization: {e}")

# Function to display centered image
def display_centered_image(image_path, caption):
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        try:
            image = Image.open(image_path)
            st.image(image, caption=caption, use_column_width=True)
        except Exception as e:
            st.error(f"Error loading image: {e}")

# Function to display chat messages
def display_chat_message(role, content):
    bubble_class = "user-bubble" if role == "user" else "bot-bubble"
    st.markdown(f"""
    <div class="chat-container">
        <div class="chat-bubble {bubble_class}">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)

# Function to show typing indicator
def show_typing_indicator():
    st.markdown("""
    <div class="typing-indicator">
        <span></span>
        <span></span>
        <span></span>
    </div>
    """, unsafe_allow_html=True)

# Main layout
col1, col2 = st.columns([3, 1])

with col2:
    # Sidebar content (moved to the right column)
    st.markdown('<h2>Navigation</h2>', unsafe_allow_html=True)
    page = st.radio("Go to", [
        icon("house") + " Home & Chat",
        icon("graph-up-arrow") + " Progress & Export"
    ])
    
    # Dark mode toggle
    st.session_state.dark_mode = st.toggle("Dark Mode", st.session_state.dark_mode)
    if st.session_state.dark_mode:
        st.markdown('<style>body {background-color: #1E1E1E; color: #FFFFFF;}</style>', unsafe_allow_html=True)

with col1:
    # Main content area
    if "Home & Chat" in page:
        st.markdown('<h1 class="big-font">Welcome to Grantbuddy!</h1>', unsafe_allow_html=True)
        
        # Display centered image
        display_centered_image('Grantbuddy.webp', 'Your Partner in Fundraising Success')
        
        st.write("AI-driven assistant to aid you in proposal writing and fundraising efforts.")
        
        # Initialize the session if not already started
        if st.session_state.chat_session is None:
            initialize_chat_session()

        # Display chat history
        for msg in st.session_state.messages:
            display_chat_message(msg["role"], msg["parts"][0]["text"])

        # Spacer for fixed input
        st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)

        # Chat input area (fixed at bottom)
        user_input = st.text_input("Type your message here:", key="user_input")
        send_button = st.button("Send")

        if send_button and user_input:
            try:
                st.session_state.messages.append({"role": "user", "parts": [{"text": user_input}]})
                display_chat_message("user", user_input)
                
                if st.session_state.chat_session:
                    show_typing_indicator()
                    with st.spinner(""):
                        response = st.session_state.chat_session.send_message(
                            {"role": "user", "parts": [{"text": user_input}]}
                        )
                        
                        grantbuddy_response = response.text
                        
                        # Simulate streaming effect
                        placeholder = st.empty()
                        for i in range(len(grantbuddy_response)):
                            placeholder.markdown(f"""
                            <div class="chat-container">
                                <div class="chat-bubble bot-bubble">
                                    {grantbuddy_response[:i+1]}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            time.sleep(0.01)
                        
                        st.session_state.messages.append({"role": "model", "parts": [{"text": grantbuddy_response}]})
                else:
                    st.error("Chat session was not initialized correctly.")
            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.info("Please try again. If the problem persists, try clearing your chat history or reloading the page.")
                if st.button("Retry"):
                    st.experimental_rerun()

        # Clear chat history button
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.experimental_rerun()

    elif "Progress & Export" in page:
        # ... (Progress & Export code remains the same) ...

# Display session start time
st.sidebar.write(f"Session started: {st.session_state.session_start_time}")

# Run the app
if __name__ == "__main__":
    pass
