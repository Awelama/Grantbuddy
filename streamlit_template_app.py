import streamlit as st
import time
import plotly.graph_objects as go

# Custom CSS
st.markdown("""
<style>
    .main { background-color: #f5f5f5; }
    .stButton>button { background-color: #4CAF50; color: white; }
    .stProgress > div > div > div > div { background-color: #4CAF50; }
</style>
""", unsafe_allow_html=True)

def show_thinking_animation(message="Grantbuddy is thinking..."):
    with st.spinner(message):
        time.sleep(2)

def add_backward_button():
    if st.button("← Go Back"):
        st.session_state.stage -= 1
        st.experimental_rerun()

def generate_suggestions(user_input, section):
    return f"Here are some suggestions for your {section}:\n1. Consider adding more detail about...\n2. You might want to elaborate on...\n3. Don't forget to mention..."

def introduction():
    st.header("Let's get started!")
    st.write("I'm excited to help you with your fundraising efforts. Before we begin, I'd like to know a bit about you.")
    
    name = st.text_input("What's your name?", key="name_input")
    
    if st.button("Continue", key="intro_continue"):
        if name:
            st.session_state.user_info['name'] = name
            show_thinking_animation("Processing your information...")
            st.session_state.stage += 1
            st.experimental_rerun()
        else:
            st.error("Please enter your name before continuing.")

def assess_experience():
    st.header("Your Experience")
    experience = st.radio("What's your level of experience with proposal writing?", 
                          ["Beginner", "Intermediate", "Advanced"])
    
    if st.button("Continue"):
        if experience:
            st.session_state.user_info['experience'] = experience
            show_thinking_animation("Analyzing your experience level...")
            st.session_state.stage += 1
            st.experimental_rerun()
        else:
            st.error("Please select your experience level before continuing.")
    add_backward_button()

def project_details():
    st.header("Project Information")
    organization = st.text_input("What's the name of your organization (if any)?")
    project = st.text_area("Briefly describe your project or idea:")
    funder = st.text_input("Do you have a specific funder in mind? If so, who?")
    project_status = st.radio("Where are you in your project development?", 
                              ["I have a developed project idea", "I just have an idea", "I need to brainstorm"])
    
    if st.button("Continue"):
        if project and project_status:
            st.session_state.user_info.update({
                'organization': organization,
                'project': project,
                'funder': funder,
                'project_status': project_status
            })
            show_thinking_animation("Processing your project details...")
            st.session_state.stage += 1
            st.experimental_rerun()
        else:
            st.error("Please provide a project description and select your project status before continuing.")
    add_backward_button()

def proposal_development():
    st.header("Proposal Development")
    sections = ["Proposal Development", "Budget for Proposal", "Impact Storytelling"]
    
    selected_section = st.selectbox("Which section would you like to work on?", sections)
    
    st.write(f"Let's work on the {selected_section} section.")
    user_input = st.text_area(f"Enter your {selected_section} here:", height=300)
    
    if st.button("Generate Suggestions"):
        if user_input:
            show_thinking_animation()
            suggestions = generate_suggestions(user_input, selected_section)
            st.write("Here are some suggestions for improvement:")
            st.write(suggestions)
        else:
            st.error("Please enter some content before generating suggestions.")
    
    if selected_section == "Budget for Proposal":
        st.write("Here's a simple budget template (in US dollars):")
        budget_df = st.data_editor({
            "Item": ["Personnel", "Equipment", "Travel", "Supplies", "Other"],
            "Amount": [0, 0, 0, 0, 0]
        })
        st.session_state.proposal['Budget Table'] = budget_df
        
        # Visualize budget
        fig = go.Figure(data=[go.Pie(labels=budget_df['Item'], values=budget_df['Amount'])])
        st.plotly_chart(fig)
    
    if st.button("Save Section"):
        if user_input or (selected_section == "Budget for Proposal" and 'Budget Table' in st.session_state.proposal):
            show_thinking_animation("Saving your progress...")
            st.session_state.proposal[selected_section] = user_input
            st.success(f"{selected_section} saved successfully!")
        else:
            st.error("Please enter some content before saving.")
    
    if st.button("Continue to Review"):
        if st.session_state.proposal:
            st.session_state.stage += 1
            st.experimental_rerun()
        else:
            st.error("Please save at least one section before continuing to review.")
    add_backward_button()

def review_and_feedback():
    st.header("Review and Feedback")
    st.write("Great job on your proposal! Here's a summary of what you've created:")
    
    for section, content in st.session_state.proposal.items():
        st.subheader(section)
        if section == "Budget Table":
            st.table(content)
        else:
            st.write(content)
    
    feedback = st.text_area("Do you have any questions or areas you'd like to improve?")
    if st.button("Submit Feedback"):
        if feedback:
            show_thinking_animation("Processing your feedback...")
            st.success("Thank you for your feedback! I'll use this to improve the proposal.")
            st.session_state.stage += 1
            st.experimental_rerun()
        else:
            st.error("Please provide some feedback before submitting.")
    add_backward_button()

def conclusion():
    st.header("Conclusion")
    st.write("Congratulations on completing your proposal draft!")
    st.write("Here's a summary of key points and actions for further development:")
    
    summary = {
        "Section": list(st.session_state.proposal.keys()),
        "Status": ["Completed" for _ in st.session_state.proposal],
        "Next Steps": ["Review and refine" for _ in st.session_state.proposal]
    }
    st.table(summary)
    
    satisfaction = st.radio("Did you find the proposal writing process with Grantbuddy helpful?", 
                            ["Yes, very helpful", "Somewhat helpful", "Not very helpful"])
    future_use = st.radio("Do you plan to use Grantbuddy in the future?", 
                          ["Definitely", "Maybe", "Probably not"])
    
    if st.button("Finish"):
        if satisfaction and future_use:
            show_thinking_animation("Finalizing your proposal...")
            st.success("Thank you for using Grantbuddy! Good luck with your proposal!")
            st.balloons()
        else:
            st.error("Please answer both questions before finishing.")
    add_backward_button()

def main():
    st.set_page_config(page_title="Grantbuddy", layout="wide")

    st.title("Welcome to Grantbuddy")
    st.write("Your AI-powered proposal writing assistant")

    if 'stage' not in st.session_state:
        st.session_state.stage = 0
        st.session_state.user_info = {}
        st.session_state.proposal = {}

    stages = [
        introduction,
        assess_experience,
        project_details,
        proposal_development,
        review_and_feedback,
        conclusion
    ]

    # Progress bar
    st.progress((st.session_state.stage + 1) / len(stages))

    current_stage = stages[st.session_state.stage]
    current_stage()

if __name__ == "__main__":
    main()
