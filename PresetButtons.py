import streamlit as st

def main():
    st.set_page_config(page_title="Bearly AI-like Interface", layout="wide")

    # Sidebar
    with st.sidebar:
        st.title("Bearly AI")
        st.selectbox("Select Model", ["Claude Opus", "GPT-4", "Other Models"])
        st.checkbox("Enable streaming")
        st.button("Clear conversation")

    # Main content
    tab1, tab2, tab3 = st.tabs(["Chat", "Documents", "Settings"])

    with tab1:
        st.header("Chat Interface")
        
        # Chat history (you'd need to implement the logic to maintain chat history)
        for i in range(5):  # Example: displaying 5 mock messages
            st.text_area(f"Message {i+1}", value="Sample message", height=100, key=f"msg_{i}")

        # User input
        user_input = st.text_area("Enter your message", height=100)
        col1, col2 = st.columns([1, 5])
        with col1:
            st.button("Submit")
        with col2:
            st.button("Regenerate")

    with tab2:
        st.header("Document Management")
        st.file_uploader("Upload a document")
        st.text("Document list would appear here")

    with tab3:
        st.header("Settings")
        st.text("Various settings options would go here")

if __name__ == "__main__":
    main()
