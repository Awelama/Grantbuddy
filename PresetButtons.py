import streamlit as st

def main():
    st.set_page_config(page_title="Bearly AI-like Interface", layout="wide")

    # Sidebar
    with st.sidebar:
        st.title("Bearly AI")
        st.selectbox("Select Model", ["Claude Opus", "GPT-4", "Other Models"])
        st.checkbox("Enable streaming")
        if st.button("Clear conversation"):
            st.session_state.messages = []

    # Main content
    tab1, tab2, tab3 = st.tabs(["Chat", "Documents", "Settings"])

    with tab1:
        st.header("Chat Interface")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat history
        for message in st.session_state.messages:
            st.text_area("", value=message, height=100, disabled=True)

        # User input
        user_input = st.text_area("Enter your message", height=100)
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.button("Submit"):
                if user_input:
                    st.session_state.messages.append(f"User: {user_input}")
                    st.session_state.messages.append(f"AI: This is a mock response to '{user_input}'")
                    st.experimental_rerun()
        with col2:
            if st.button("Regenerate"):
                if st.session_state.messages:
                    st.session_state.messages.append("AI: This is a regenerated response.")
                    st.experimental_rerun()

    with tab2:
        st.header("Document Management")
        uploaded_file = st.file_uploader("Upload a document")
        if uploaded_file is not None:
            st.write("File uploaded:", uploaded_file.name)
        st.text("Document list would appear here")

    with tab3:
        st.header("Settings")
        st.text("Various settings options would go here")
        if st.button("Save Settings"):
            st.write("Settings saved!")

if __name__ == "__main__":
    main()
