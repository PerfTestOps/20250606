import streamlit as st
from Login_Form import check_user, create_user
from Transaction_Analyzer import transaction_analysis_page

st.set_page_config(page_title="Login App", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

if st.session_state.logged_in:
    st.sidebar.success(f"Welcome, {st.session_state.username}!")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
else:
    tab = st.sidebar.radio("Select an option", ("Login", "SignUp"))

    if tab == "Login":
        st.subheader("Login Here")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if check_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login Successful")
                st.rerun()
            else:
                st.error("Invalid username or password")

    elif tab == "SignUp":
        st.subheader("Create Account")
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("SignUp"):
            if not (name and email and new_username and new_password and confirm_password):
                st.error("Please fill in all fields.")
            elif new_password != confirm_password:
                st.error("Passwords do not match!")
            else:
                result = create_user(name, email, new_username, new_password)
                if result == "success":
                    st.success("Signup successful. Please log in.")
                elif result == "username_exists":
                    st.error("Username already exists.")
                elif result == "email_exists":
                    st.error("Email already registered.")

# Main Func.
if st.session_state.logged_in:
    transaction_analysis_page()
else:
    st.write("")
