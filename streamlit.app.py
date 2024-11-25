import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests

# Streamlit configuration
st.set_page_config(page_title="Welcome to Grantbuddy!", layout="wide")

# Add this code between st.set_page_config(page_title="Streamlit Chatbot", layout="wide") and Display image code block
if "form_submitted" not in st.session_state:
    st.session_state.form_submitted = False
if "form_responses" not in st.session_state:
    st.session_state.form_responses = {}
if "should_generate_response" not in st.session_state:
    st.session_state.should_generate_response = False
    
# Display image
# This code attempts to open and display an image file named 'Build2.png'.
# If successful, it shows the image with a caption. If there's an error, it displays an error message instead.
# You can customize this by changing the image file name and path. Supported image types include .png, .jpg, .jpeg, and .gif.
# To use a different image, replace 'Build2.png' with your desired image file name (e.g., 'my_custom_image.jpg').
image_path = 'Grantbuddy.webp'
try:
    image = Image.open(image_path)
    st.image(image, caption='Created by Awelama Kwarase (2024)', use_column_width=True)
except Exception as e:
    st.error(f"Error loading image: {e}")

# Title and BotDescription 
# You can customize the title, description, and caption by modifying the text within the quotes.
st.title("Welcome to Grantbuddy!")
st.write("I'm Grantbuddy, an advanced AI assistant specializing in proposal writing, budgeting, and impact storytelling to help you.")
st.write("If you want to search the web while using me, type lookup, followed by your query.")
st.caption("Grantbuddy can make mistakes. Please double-check all responses.")


# Initialize Gemini client
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

PERPLEXITY_API_KEY = st.secrets["P_API_KEY"]

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "model_name" not in st.session_state:
    st.session_state.model_name = "gemini-1.5-pro-002"
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.5
if "debug" not in st.session_state:
    st.session_state.debug = []
if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = ""
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None

# Sidebar for model and temperature selection
with st.sidebar:
    st.title("Settings")
    st.caption("Note: Gemini-1.5-pro-002 can only handle 2 requests per minute, gemini-1.5-flash-002 can handle 15 per minute")
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
        # Upload file using File API with mime_type specified
        uploaded_file = genai.upload_file(uploaded_pdf, mime_type="application/pdf")
        st.session_state.uploaded_file = uploaded_file
        st.success("File uploaded successfully!")
                  
    except Exception as e:
        st.error(f"Error uploading file: {e}")
        st.session_state.debug.append(f"File upload error: {e}")

# Clear chat function
if clear_button:
    st.session_state.messages = []
    st.session_state.debug = []
    st.session_state.pdf_content = ""
    st.session_state.chat_session = None
    st.rerun()

# Load system prompt
def load_text_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        st.error(f"Error loading text file: {e}")
        return ""

system_prompt = load_text_file('instructions.txt')

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
def search_perplexity(query):
    """Execute a search query using Perplexity API"""
    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "accept": "application/json",
                "content-type": "application/json",
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}"
            },
            json={
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [{"role": "user", "content": f"Search the web for: {query}"}]
            }
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"Perplexity API Error: {e}")
        return None

# User input
# The placeholder text "Your message:" can be customized to any desired prompt, e.g., "Message Creative Assistant...".
user_input = st.chat_input("Describe what you want Grantbuddy to do and provide the necessary background information. An example is: I am from a small NGO in Kenya focused on girls' education. We need help creating a proposal for a $50,000 grant to expand our after-school tutoring program. Can you guide me through the process?")

if user_input:
    current_message = {"role": "user", "content": user_input}
    st.session_state.messages.append(current_message)

    with st.chat_message("user"):
        st.markdown(current_message["content"])

    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        # Initialize chat session if needed
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
            
            initial_messages = [
                {"role": "user", "parts": [f"System: {system_prompt}"]},
                {"role": "model", "parts": ["Understood. I will follow these instructions."]},
            ]
            
            if st.session_state.pdf_content:
                initial_messages.extend([
                    {"role": "user", "parts": [f"PDF content for reference:\n\n{st.session_state.pdf_content}"]},
                    {"role": "model", "parts": ["Acknowledged PDF content."]}
                ])
            
            st.session_state.chat_session = model.start_chat(history=initial_messages)

        try:
            is_search = user_input.lower().startswith(("lookup"))
            
            if is_search:
                # Extract search query
                search_query = ' '.join(user_input.split()[2:] if user_input.lower().startswith("search the web") else user_input.split()[1:])
                
                if not search_query:
                    message_placeholder.warning("Please provide a search query.")
                    st.session_state.messages.pop()  # Remove the empty query from history
                    st.rerun()
                
                # Execute search
                message_placeholder.info("🔍 Searching the web...")
                search_results = search_perplexity(search_query)
                
                if search_results:
                    # Process results with Gemini
                    prompt = (
                        f"Here are web search results for: '{search_query}'\n\n"
                        f"{search_results}\n\n"
                        "Please provide a clear, accurate summary of these results in a well-formatted response. "
                        "Include relevant links when available. Verify accuracy before responding."
                    )
                    
                    response = st.session_state.chat_session.send_message(prompt)
                    message_placeholder.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    st.session_state.debug.append("Search results processed successfully")
            else:
                # Handle regular chat
                response = st.session_state.chat_session.send_message(user_input)
                message_placeholder.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                st.session_state.debug.append("Regular chat response generated")
                
        except Exception as e:
            st.error(f"Error generating response: {e}")
            st.session_state.debug.append(f"Error: {e}")
            st.session_state.messages.pop()  # Remove failed message from history
    
    st.rerun()

# Debug information
# You can remove this by adding # in front of each line

st.sidebar.title("Debug Info")
for debug_msg in st.session_state.debug:
    st.sidebar.text(debug_msg)
