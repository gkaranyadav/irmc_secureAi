"""
Main application router for iRMC SecureAI
"""

import streamlit as st
import sys
from pathlib import Path

# Add pages directory to path
sys.path.append(str(Path(__file__).parent))

# Page config
st.set_page_config(
    page_title="iRMC SecureAI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# Import pages
from pages import login, signup, home

# Router
def main():
    if not st.session_state.authenticated:
        if st.session_state.page == 'login':
            login.show()
        elif st.session_state.page == 'signup':
            signup.show()
        else:
            login.show()
    else:
        if st.session_state.page == 'home':
            home.show()
        else:
            home.show()

if __name__ == "__main__":
    main()
