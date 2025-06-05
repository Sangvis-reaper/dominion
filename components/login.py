import streamlit as st

def login():
    st.markdown("<h2 style='text-align:center;'>🔐 Login to OSINT Tool Pro</h2>", unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            if username == "admin" and password == "password":  # Replace with real authentication logic
                st.session_state.authenticated = True
                st.success("Login successful! Redirecting to homepage...")
                st.rerun()  # 🔁 Trigger app rerun to load the homepage
            else:
                st.error("Invalid username or password")
