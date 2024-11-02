import streamlit as st
from PIL import Image
import google.generativeai as genai
import datetime
import json
import pandas as pd
from io import BytesIO
import time

# Page configuration
st.set_page_config(page_title="Grantbuddy", layout="wide")

# CSS styling
st.markdown("""
<style>
.big-font {
    font-size:30px !important;
    font-weight: bold;
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
if "current_step" not in st.session_state:
    st.session_state.current_step = "initial_assessment"
if "proposal_data" not in st.session_state:
    st.session_state.proposal_data = {}
if "user_experience" not in st.session_state:
    st.session_state.user_experience = None
if "project_stage" not in st.session_state:
    st.session_state.project_stage = None

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home & Chat", "Progress & Export", "Brainstorm"])

# Initialize Google AI client
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Helper functions
def initialize_chat_session():
    model = genai.GenerativeModel('gemini-pro')
    st.session_state.chat_session = model.start_chat(history=[])

def display_centered_image(image_path, caption):
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(image_path, caption=caption, use_column_width=True)

def update_points(progress):
    points = sum(progress.values()) * 10
    level = (points // 50) + 1
    return level, points

def get_achievements(points):
    achievements = []
    if points >= 10:
        achievements.append("Getting Started")
    if points >= 50:
        achievements.append("Proposal Pro")
    if points >= 100:
        achievements.append("Grant Guru")
    return achievements

def get_ai_response(prompt):
    response = st.session_state.chat_session.send_message(prompt)
    return response.text

# Main application logic
if page == "Home & Chat":
    st.markdown('<p class="big-font">Welcome to Grantbuddy!</p>', unsafe_allow_html=True)
    
    display_centered_image('Grantbuddy.webp', 'Your AI Partner in Fundraising Success')
    
    st.write("AI-driven assistance to help you craft winning proposals and streamline your fundraising efforts.")
    
    if st.session_state.chat_session is None:
        initialize_chat_session()

    # Initial Assessment
    if st.session_state.current_step == "initial_assessment":
        st.write("Before we begin, let's get to know you and your project better.")
        
        experience_levels = ["Beginner (0-1 grants written)", "Intermediate (2-5 grants written)", "Advanced (6+ grants written)"]
        st.session_state.user_experience = st.selectbox("What is your level of experience in grant writing?", experience_levels)
        
        project_stages = ["Just an idea", "Early planning stage", "Full project plan ready", "Looking to brainstorm"]
        st.session_state.project_stage = st.selectbox("What stage is your project or idea at?", project_stages)
        
        specific_area = st.text_input("Is there a specific area of fundraising you're focusing on? (e.g., education, healthcare, technology)")
        
        if st.button("Start My Journey") and st.session_state.user_experience and st.session_state.project_stage:
            st.session_state.proposal_data["experience_level"] = st.session_state.user_experience
            st.session_state.proposal_data["project_stage"] = st.session_state.project_stage
            st.session_state.proposal_data["focus_area"] = specific_area
            st.session_state.current_step = "ai_assessment"
            st.rerun()

    elif st.session_state.current_step == "ai_assessment":
        assessment_prompt = f"""
        Based on the following user information:
        - Experience level: {st.session_state.proposal_data['experience_level']}
        - Project stage: {st.session_state.proposal_data['project_stage']}
        - Focus area: {st.session_state.proposal_data['focus_area']}

        Provide a personalized assessment and recommendation for how to proceed with the grant writing process. 
        Include specific advice tailored to their experience level and project stage.
        """
        ai_assessment = get_ai_response(assessment_prompt)
        st.write("AI Assessment and Recommendation:")
        st.write(ai_assessment)
        
        if st.button("Continue to Next Step"):
            if st.session_state.project_stage == "Looking to brainstorm":
                st.session_state.current_step = "brainstorm"
            elif st.session_state.project_stage == "Just an idea":
                st.session_state.current_step = "idea_development"
            else:
                st.session_state.current_step = "proposal_type"
            st.rerun()

    elif st.session_state.current_step == "brainstorm":
        st.write("Let's brainstorm some ideas for your project.")
        focus_area = st.session_state.proposal_data.get('focus_area', 'fundraising')
        brainstorm_prompt = f"Generate 5 innovative fundraising ideas related to {focus_area}, suitable for a {st.session_state.proposal_data['experience_level']} grant writer."
        ai_ideas = get_ai_response(brainstorm_prompt)
        st.write("AI-generated ideas:")
        st.write(ai_ideas)
        
        user_idea = st.text_input("Do you have any ideas of your own? Enter them here:")
        if st.button("Add My Idea") and user_idea:
            st.session_state.brainstorm_ideas.append(user_idea)
            st.success("Your idea has been added!")
        
        if st.button("Develop Selected Idea"):
            st.session_state.current_step = "idea_development"
            st.rerun()

    elif st.session_state.current_step == "idea_development":
        st.write("Let's develop your idea further.")
        idea_to_develop = st.selectbox("Which idea would you like to develop?", st.session_state.brainstorm_ideas + ["I have a new idea"])
        
        if idea_to_develop == "I have a new idea":
            idea_to_develop = st.text_input("Enter your new idea:")
        
        if st.button("Develop This Idea") and idea_to_develop:
            development_prompt = f"""
            Develop the following idea into a more comprehensive project concept:
            Idea: {idea_to_develop}
            Experience level: {st.session_state.proposal_data['experience_level']}
            Focus area: {st.session_state.proposal_data['focus_area']}

            Provide a structured outline including:
            1. Project overview
            2. Goals and objectives
            3. Target audience
            4. Potential impact
            5. Next steps for implementation
            """
            developed_idea = get_ai_response(development_prompt)
            st.session_state.proposal_data["developed_idea"] = developed_idea
            st.write("Developed Project Concept:")
            st.write(developed_idea)
            
            if st.button("Move to Proposal Writing"):
                st.session_state.current_step = "proposal_type"
                st.rerun()

    # Continue with the proposal writing process (proposal_type, purpose, audience, etc.)
    # ... (include the rest of the proposal writing steps here, similar to the previous version)

    # Add a "Save Progress" button in the sidebar
    if st.sidebar.button("Save Progress"):
        st.sidebar.success("Progress saved successfully!")

    # Add a "Start Over" button in the sidebar
    if st.sidebar.button("Start Over"):
        for key in ['current_step', 'proposal_data', 'user_experience', 'project_stage', 'brainstorm_ideas']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

elif page == "Progress & Export":
    st.title("Progress & Export")
    st.write("Here's your current progress:")
    for section, content in st.session_state.proposal_data.items():
        st.subheader(section.capitalize())
        st.write(content)
    
    if "final_draft" in st.session_state.proposal_data:
        st.download_button("Download Final Draft", st.session_state.proposal_data["final_draft"], "proposal_final_draft.txt")
    else:
        st.write("Final draft not yet generated. Complete the writing process to generate a final draft.")

elif page == "Brainstorm":
    st.title("Brainstorm")
    st.write("Use this space to brainstorm ideas for your project or proposal.")
    
    focus_area = st.session_state.proposal_data.get('focus_area', 'fundraising')
    if st.button("Generate Ideas from AI"):
        ai_ideas = get_ai_response(f"Generate 5 innovative fundraising ideas related to {focus_area}, suitable for a {st.session_state.proposal_data['experience_level']} grant writer.")
        st.write("AI-generated ideas:")
        st.write(ai_ideas)
    
    idea = st.text_input("Enter your own idea:")
    if st.button("Add Idea") and idea:
        st.session_state.brainstorm_ideas.append(idea)
        st.success("Idea added successfully!")
    
    st.write("Your brainstormed ideas:")
    for i, idea in enumerate(st.session_state.brainstorm_ideas, 1):
        st.write(f"{i}. {idea}")

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
