import streamlit as st
from PIL import Image
import google.generativeai as genai
import datetime
import json
import pandas as pd
from io import BytesIO

# Page configuration
st.set_page_config(page_title="Grantbuddy", layout="wide")

# CSS styling
st.markdown("""
<style>
.big-font {
    font-size: 30px !important;
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
    st.session_state.session_start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
if "progress" not in st.session_state:
    st.session_state.progress = {"Project Description": False, "Budget": False, "Impact Assessment": False}
if "user_level" not in st.session_state:
    st.session_state.user_level = 1
if "user_points" not in st.session_state:
    st.session_state.user_points = 0
if "achievements" not in st.session_state:
    st.session_state.achievements = []
if "brainstorm_ideas" not in st.session_state:
    st.session_state.brainstorm_ideas = []

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home & Chat", "Progress & Export", "Brainstorm"])

# Initialize Google AI client
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Function to initialize chat session
def initialize_chat_session():
    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat(history=[])
    st.session_state.chat_session = chat
    st.session_state.messages = []

# Function to display centered image
def display_centered_image(image_path, caption):
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        try:
            image = Image.open(image_path)
            st.image(image, use_column_width=True, caption=caption)
        except Exception as e:
            st.error(f"Error loading image: {e}")

# Gamification functions
def update_points(progress):
    points = sum(progress.values()) * 100
    level = points // 300 + 1
    st.session_state.user_points = points
    st.session_state.user_level = level
    return level, points

def get_achievements(points):
    achievements = []
    if points >= 100:
        achievements.append("Novice Grant Writer")
    if points >= 300:
        achievements.append("Intermediate Grant Writer")
    if points >= 600:
        achievements.append("Expert Grant Writer")
    st.session_state.achievements = achievements
    return achievements

# Storytelling functions
def get_story_suggestions(text):
    # Placeholder for AI-generated storytelling suggestions
    return "Consider adding a personal anecdote to make your proposal more engaging."

def calculate_story_strength(text):
    # Placeholder for story strength calculation
    return len(text.split()) / 10  # Simple metric based on word count

# Style adaptation functions
def adapt_style(text, org):
    # Placeholder for style adaptation
    return f"Adapted for {org}: " + text

def check_style_consistency(text):
    # Placeholder for style consistency check
    return 85  # Returning a dummy percentage

# Emotional intelligence functions
def analyze_emotion(text):
    # Placeholder for emotion analysis
    return "The tone is primarily informative with a hint of enthusiasm."

def visualize_emotional_journey(text):
    # Placeholder for emotional journey visualization
    # In a real implementation, you'd return a Plotly figure here
    return "Emotional Journey Visualization (placeholder)"

# Brainstorming functions
def create_brainstorm_board():
    ideas = st.text_area("Enter your ideas (one per line):")
    if ideas:
        st.session_state.brainstorm_ideas = ideas.split('\n')
    return st.session_state.brainstorm_ideas

def generate_ai_suggestions(ideas):
    # Placeholder for AI-generated suggestions
    return ["Consider the long-term impact", "Explore partnerships", "Highlight innovation"]

# Main application logic
if page == "Home & Chat":
    st.markdown('<p class="big-font">Welcome to Grantbuddy!</p>', unsafe_allow_html=True)
    
    display_centered_image('Grantbuddy.webp', 'Your AI Partner in Fundraising Success')
    
    st.write("AI-driven assistance to help you craft winning proposals and streamline your fundraising efforts.")
    
    if st.session_state.chat_session is None:
        initialize_chat_session()

    user_input = st.chat_input("Type your message here:", key="user_input")
    
    if user_input:
        try:
            st.session_state.messages.append({"role": "user", "parts": [user_input]})
            
            with st.spinner("Grantbuddy is thinking..."):
                response = st.session_state.chat_session.send_message(user_input)
                grantbuddy_response = response.text
                
                st.session_state.messages.append({"role": "model", "parts": [grantbuddy_response]})

            # Storytelling Assistant
            story_suggestions = get_story_suggestions(user_input)
            st.info("Storytelling Tip: " + story_suggestions)
            
            story_strength = calculate_story_strength(user_input)
            st.progress(story_strength)
            st.write(f"Story Strength: {story_strength:.0f}%")

            # Style Adaptation
            funding_org = st.text_input("Enter funding organization (optional):")
            if funding_org:
                adapted_text = adapt_style(user_input, funding_org)
                col1, col2 = st.columns(2)
                with col1:
                    st.write("Original Text:")
                    st.write(user_input)
                with col2:
                    st.write("Adapted Style Suggestion:")
                    st.write(adapted_text)
                
                style_consistency = check_style_consistency(adapted_text)
                st.write(f"Style Consistency: {style_consistency}%")

            # Emotional Intelligence Feedback
            emotion_feedback = analyze_emotion(user_input)
            st.write("Emotional Impact:", emotion_feedback)
            
            emotional_journey = visualize_emotional_journey(user_input)
            st.write(emotional_journey)  # In a real implementation, use st.plotly_chart()

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.info("Please try again. If the problem persists, try clearing your chat history or reloading the page.")

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["parts"][0])
        else:
            st.chat_message("assistant").write(msg["parts"][0])

    if st.button("Clear History"):
        st.session_state.messages = []
        st.experimental_rerun()

elif page == "Progress & Export":
    st.markdown('<p class="big-font">Grant Progress & Export</p>', unsafe_allow_html=True)
    
    display_centered_image('Grantbuddy.webp', 'Your AI Partner in Fundraising Success')
    
    st.subheader("Progress Tracking")
    
    for step, completed in st.session_state.progress.items():
        st.session_state.progress[step] = st.checkbox(step, value=completed)
    
    progress_percentage = sum(st.session_state.progress.values()) / len(st.session_state.progress) * 100
    st.progress(progress_percentage / 100)
    st.write(f"Overall Progress: {progress_percentage:.0f}%")
    
    if st.button("Save Progress"):
        st.success("Progress saved successfully!")

    st.subheader("Export History")

    if st.session_state.messages:
        if st.button("Export as JSON"):
            json_str = json.dumps(st.session_state.messages, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name="chat_history.json",
                mime="application/json"
            )

        if st.button("Export as Excel"):
            df = pd.DataFrame([(msg["role"], msg["parts"][0]["text"]) for msg in st.session_state.messages],
                              columns=["Role", "Message"])
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Chat History', index=False)
            st.download_button(
                label="Download Excel",
                data=buffer,
                file_name="chat_history.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.write("No chat history to export.")

elif page == "Brainstorm":
    st.title("AI-Assisted Brainstorming Board")
    ideas = create_brainstorm_board()
    
    if ideas:
        st.write("Your Ideas:")
        for idea in ideas:
            st.write(f"- {idea}")
    
    if st.button("Generate AI Suggestions"):
        ai_suggestions = generate_ai_suggestions(ideas)
        st.write("AI Suggestions:")
        for suggestion in ai_suggestions:
            st.write(f"- {suggestion}")

# Gamification display in sidebar
user_level, user_points = update_points(st.session_state.progress)
st.sidebar.subheader("Your Progress")
st.sidebar.write(f"Level: {user_level}")
st.sidebar.write(f"Points: {user_points}")
achievements = get_achievements(user_points)
if achievements:
    st.sidebar.write("Achievements:", ", ".join(achievements))

# Run the app
if __name__ == "__main__":
    st.sidebar.write("Session started at:", st.session_state.session_start_time)
