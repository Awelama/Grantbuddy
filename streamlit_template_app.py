import streamlit as st

def main():
    st.set_page_config(page_title="Grantbuddy AI Proposal Assistant", layout="wide")

    st.title("Welcome to Grantbuddy AI Proposal Assistant")
    st.write("I'm here to help you create compelling, comprehensive, and tailored fundraising proposals.")

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

    current_stage = stages[st.session_state.stage]
    current_stage()

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.session_state.stage > 0:
            if st.button("← Back"):
                st.session_state.stage -= 1
                st.experimental_rerun()
    with col3:
        if st.session_state.stage < len(stages) - 1:
            if st.button("Next →"):
                st.session_state.stage += 1
                st.experimental_rerun()

def introduction():
    st.header("Let's get started!")
    st.write("I'm excited to help you with your fundraising proposal. Before we begin, I'd like to know a bit about you.")

def assess_experience():
    st.header("Your Experience")
    experience = st.radio("What's your level of experience with proposal writing?", 
                          ["Beginner", "Intermediate", "Advanced"])
    st.session_state.user_info['experience'] = experience

def project_details():
    st.header("Project Information")
    st.session_state.user_info['organization'] = st.text_input("What's the name of your organization (if any)?")
    st.session_state.user_info['project'] = st.text_area("Briefly describe your project or idea:")
    st.session_state.user_info['funder'] = st.text_input("Do you have a specific funder in mind? If so, who?")
    
    project_status = st.radio("Where are you in your project development?", 
                              ["I have a developed project", "I just have an idea", "I need help brainstorming"])
    st.session_state.user_info['project_status'] = project_status

def proposal_development():
    st.header("Proposal Development")
    sections = ["Executive Summary", "Problem Statement", "Goals and Objectives", "Methods and Activities", 
                "Timeline", "Budget", "Evaluation Plan", "Sustainability"]
    
    selected_section = st.selectbox("Which section would you like to work on?", sections)
    
    st.write(f"Let's work on the {selected_section} section.")
    st.session_state.proposal[selected_section] = st.text_area(f"Enter your {selected_section} here:", 
                                                               height=300)
    
    if selected_section == "Budget":
        st.write("Here's a simple budget template (in US dollars):")
        budget_df = st.data_editor({
            "Item": ["Personnel", "Equipment", "Travel", "Supplies", "Other"],
            "Amount": [0, 0, 0, 0, 0]
        })
        st.session_state.proposal['Budget Table'] = budget_df
    
    if st.button("Save Section"):
        st.success(f"{selected_section} saved successfully!")

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
        st.success("Thank you for your feedback! I'll use this to improve the proposal.")

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
        st.success("Thank you for using Grantbuddy! Good luck with your proposal!")
        st.balloons()

if __name__ == "__main__":
    main()
