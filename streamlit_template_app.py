import streamlit as st
import sqlite3
import google.generativeai as genai
from PIL import Image
import io
import pandas as pd
from fpdf import FPDF
import base64

# Database setup
conn = sqlite3.connect('grantbuddy.db', check_same_thread=False)
c = conn.cursor()

# Create tables if they don't exist
c.execute('''CREATE TABLE IF NOT EXISTS chat_history
             (id INTEGER PRIMARY KEY, user_id TEXT, message TEXT, role TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
c.execute('''CREATE TABLE IF NOT EXISTS user_files
             (id INTEGER PRIMARY KEY, user_id TEXT, filename TEXT, file_data BLOB, upload_date DATETIME DEFAULT CURRENT_TIMESTAMP)''')
conn.commit()

# Initialize GenerativeAI client
genai.configure(api_key=st.secrets.get("GOOGLE_API_KEY", ""))

# Function to initialize or get chat session
def get_chat_session():
    if "chat_session" not in st.session_state:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro-latest",
            generation_config={
                "temperature": 0.7,
                "max_output_tokens": 1024
            }
        )
        st.session_state.chat_session = model.start_chat(history=[])
    return st.session_state.chat_session

# Function to save message to database
def save_message(user_id, message, role):
    c.execute("INSERT INTO chat_history (user_id, message, role) VALUES (?, ?, ?)",
              (user_id, message, role))
    conn.commit()

# Function to get chat history from database
def get_chat_history(user_id):
    c.execute("SELECT message, role FROM chat_history WHERE user_id = ? ORDER BY timestamp", (user_id,))
    return c.fetchall()

# Function to save uploaded file
def save_file(user_id, file):
    file_data = file.read()
    c.execute("INSERT INTO user_files (user_id, filename, file_data) VALUES (?, ?, ?)",
              (user_id, file.name, file_data))
    conn.commit()

# Function to get user files
def get_user_files(user_id):
    c.execute("SELECT id, filename FROM user_files WHERE user_id = ?", (user_id,))
    return c.fetchall()

# Function to generate AI suggestions
def generate_suggestion(text):
    chat = get_chat_session()
    response = chat.send_message(f"Please provide a suggestion to improve this grant proposal section: {text}")
    return response.text

# Function to export chat history as PDF
def export_as_pdf(chat_history):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for message, role in chat_history:
        pdf.cell(200, 10, txt=f"{role}: {message}", ln=True)
    pdf_output = pdf.output(dest="S").encode("latin-1")
    return base64.b64encode(pdf_output).decode()

# Streamlit app
st.set_page_config(page_title="Grantbuddy", layout="wide")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Chat", "File Management", "Export"])

# Main content
if page == "Chat":
    st.title("Grantbuddy Chat")
    
    user_id = "test_user"  # In a real app, this would be the authenticated user's ID
    chat = get_chat_session()

    # Display chat history
    chat_history = get_chat_history(user_id)
    for message, role in chat_history:
        st.text(f"{role}: {message}")

    # Chat input
    user_input = st.text_area("Type your message here:", key="user_input")
    if st.button("Send", key="send_button"):
        if user_input:
            save_message(user_id, user_input, "User")
            st.text(f"User: {user_input}")
            
            response = chat.send_message(user_input)
            ai_response = response.text
            save_message(user_id, ai_response, "AI")
            st.text(f"AI: {ai_response}")

    # AI Suggestion feature
    st.subheader("Get AI Suggestion")
    section_text = st.text_area("Enter a section of your grant proposal for suggestions:")
    if st.button("Get Suggestion"):
        suggestion = generate_suggestion(section_text)
        st.write("AI Suggestion:", suggestion)

elif page == "File Management":
    st.title("File Management")
    
    user_id = "test_user"  # In a real app, this would be the authenticated user's ID

    uploaded_file = st.file_uploader("Upload a file", type=['txt', 'pdf', 'doc', 'docx'])
    if uploaded_file:
        save_file(user_id, uploaded_file)
        st.success("File uploaded successfully!")

    st.subheader("Your Files")
    files = get_user_files(user_id)
    for file_id, filename in files:
        st.write(filename)

elif page == "Export":
    st.title("Export Chat History")
    
    user_id = "test_user"  # In a real app, this would be the authenticated user's ID
    chat_history = get_chat_history(user_id)

    if st.button("Export as PDF"):
        pdf_b64 = export_as_pdf(chat_history)
        href = f'<a href="data:application/pdf;base64,{pdf_b64}" download="chat_history.pdf">Download PDF</a>'
        st.markdown(href, unsafe_allow_html=True)

# Accessibility improvements
st.markdown("""
<style>
    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
    }
    .stButton>button {
        font-size: 16px;
        padding: 10px 20px;
    }
    .stTextInput>div>div>input {
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# Run the app
if __name__ == "__main__":
    pass
