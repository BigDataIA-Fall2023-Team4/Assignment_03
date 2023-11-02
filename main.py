# # main.py
import streamlit as st
from UI.signup import show as show_signup
from UI.login import show as show_login
from UI.home import show as show_home
from UI.chatbot import show as show_chatbot


def main():
    # Initialize session state variables
    if "page" not in st.session_state:
        st.session_state["page"] = "Login"  # Set initial page to Login

    # Sidebar for navigation
    st.sidebar.title("Navigation")

    # Check if user is logged in
    if "token" in st.session_state:
        # User is logged in
        page_selection = st.sidebar.radio("Go to", ["Home", "Logout"])
    else:
        # User is not logged in
        page_selection = st.sidebar.radio("Go to", ["Login", "Signup"])

    # Update session state based on sidebar selection
    st.session_state["page"] = page_selection

    # Display pages based on session state
    if st.session_state["page"] == "Signup":
        show_signup()
    elif st.session_state["page"] == "Login":
        show_login()
    elif st.session_state["page"] == "Home":
        show_chatbot()
    elif st.session_state["page"] == "Logout":
        st.session_state.pop("token", None)  # Remove token from session state
        st.session_state["page"] = "Login"  # Set page to Login
        st.experimental_rerun()  # Rerun the script to update the UI


if __name__ == "__main__":
    main()