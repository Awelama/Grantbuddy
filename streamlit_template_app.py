import streamlit as st
from PIL import Image
import google.generativeai as genai
import json
from datetime import datetime
import pandas as pd
from io import BytesIO
import time

# Page configuration
st.set_page_config(page_title="Grantbuddy", page_icon="📝", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
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
        text-align: right;
    }
    .bot-bubble {
        background-color: #f0f0f0;
        margin-right: auto;
    }
    .chat-container {
        display: flex;
        flex-direction: column;
    }
    .big-font {
        font-size: 30px !important;
        font-weight: bold;
        text-align: center;
        color: #4CAF50;
    }
    .stButton>button {
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

# Main layout
st.markdown('<h1 class="big-font">Welcome to Grantbuddy!</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("Navigation")
    page = st.radio("Go to", ["Home & Chat", "Progress & Export"])
    st.write(f"Session started: {st.session_state.session_start_time}")

# Main content area
if page == "Home & Chat":
    st.write("AI-driven assistant to aid you in proposal writing and fundraising efforts.")
    
    # Initialize the session if not already started
    if st.session_state.chat_session is None:
        initialize_chat_session()

    # Display chat history
    for msg in st.session_state.messages:
        display_chat_message(msg["role"], msg["parts"][0]["text"])

    # Chat input area
    user_input = st.text_input("Type your message here:", key="user_input")
    send_button = st.button("Send")

    if send_button and user_input:
        try:
            st.session_state.messages.append({"role": "user", "parts": [{"text": user_input}]})
            display_chat_message("user", user_input)
            
            if st.session_state.chat_session:
                with st.spinner("Grantbuddy is thinking..."):
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

    # Clear chat history button
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.experimental_rerun()

elif page == "Progress & Export":
    st.title("Grant Writing Progress & Export")

    # Progress Tracking
    st.subheader("Progress Tracking")
    
    # Display and update progress
    for step, completed in st.session_state.progress.items():
        st.session_state.progress[step] = st.checkbox(step, value=completed)

    # Calculate overall progress
    progress_percentage = sum(st.session_state.progress.values()) / len(st.session_state.progress) * 100

    # Display progress bar
    st.progress(progress_percentage / 100)
    st.write(f"Overall Progress: {progress_percentage:.0f}%")

    # Save progress button
    if st.button("Save Progress"):
        st.success("Progress saved successfully!")

    # Export Functionality
    st.subheader("Export Chat History")

    if st.session_state.messages:
        # Export as JSON
        if st.button("Export as JSON"):
            chat_history = json.dumps(st.session_state.messages, indent=2)
            st.download_button(
                label="Download Chat History (JSON)",
                data=chat_history,
                file_name="chat_history.json",
                mime="application/json"
            )
        
        # Export as Excel
        if st.button("Export as Excel"):
            df = pd.DataFrame([(msg["role"], msg["parts"][0]["text"]) for msg in st.session_state.messages], 
                              columns=["Role", "Message"])
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Chat History', index=False)
            st.download_button(
                label="Download Chat History (Excel)",
                data=buffer,
                file_name="chat_history.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.write("No chat history available to export.")

# Run the app
if __name__ == "__main__":
    pass
