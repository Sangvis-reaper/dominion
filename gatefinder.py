import streamlit as st
from components.login import login  # Import login normally

# Set the page title
st.set_page_config(page_title="OSINT Web Application", layout="wide")

# Lazy import function to avoid circular dependencies
def load_homepage():
    from components.homepage import homepage  # Import only when needed
    return homepage

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Redirect to the homepage or login screen
if st.session_state.authenticated:
    homepage = load_homepage()
    homepage()
else:
    login()
