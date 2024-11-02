import streamlit as st
from PIL import Image
import google.generativeai as genai
import json
from datetime import datetime
import pandas as pd
from io import BytesIO

# Page configuration
st.set_page_config(page_title="Grantbuddy", page_icon="📝", layout="wide")

# Custom CSS for styling
st.markdown("""
<style>
.big-font {
    font-size:30px !important;
    font-weight: bold;
    text-align: center;
}
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
.centered-image {
    display: flex;
    justify-content: center;
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

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home & Chat", "Progress & Export"])

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

# Home & Chat Page
if page == "Home & Chat":
    st.markdown('<p class="big-font">Welcome to Grantbuddy!</p>', unsafe_allow_html=True)
    
    # Display centered image
    display_centered_image('Grantbuddy.webp', 'Your Partner in Fundraising Success')
    
    st.write("AI-driven assistant to aid you in proposal writing and fundraising efforts.")
    
    # Initialize the session if not already started
    if st.session_state.chat_session is None:
        initialize_chat_session()

    # Chat input area
    user_input = st.chat_input("Type your message here:", key="user_input")

    if user_input:
        try:
            st.session_state.messages.append({"role": "user", "parts": [{"text": user_input}]})
            
            if st.session_state.chat_session:
                with st.spinner("Grantbuddy is thinking..."):
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

    # Display chat history
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["parts"][0]["text"])
        else:
            st.chat_message("assistant").write(msg["parts"][0]["text"])

    # Clear chat history button
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.experimental_rerun()

# Progress & Export Page
elif page == "Progress & Export":
    st.markdown('<p class="big-font">Grant Writing Progress & Export</p>', unsafe_allow_html=True)

    # Display centered image
    display_centered_image('Grantbuddy.webp', 'Your Partner in Fundraising Success')

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
    st.sidebar.write(f"Session started: {st.session_state.session_start_time}")
