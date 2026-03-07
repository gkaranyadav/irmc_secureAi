"""
Authentication helper functions
"""

import streamlit as st
from database import db

def login_user(username, password):
    """Login user and set session state"""
    result = db.authenticate_user(username, password)
    
    if result["success"]:
        st.session_state.authenticated = True
        st.session_state.user = result["user"]
        st.session_state.is_admin = result["user"]["is_admin"]
        st.session_state.page = "home"
        return True, result["message"]
    else:
        return False, result["message"]

def register_user(username, email, password, full_name, role="analyst", department=None):
    """Register new user"""
    return db.register_user(username, email, password, full_name, role, department)

def logout_user():
    """Logout user and clear session"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.authenticated = False
    st.session_state.page = "login"
