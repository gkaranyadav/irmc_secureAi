"""
Signup page for iRMC SecureAI
"""

import streamlit as st
from auth import register_user

def show():
    st.markdown("""
    <style>
    .signup-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.08);
        border-left: 4px solid #DC2626;
    }
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(135deg, #DC2626, #7F1D1D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 700;
        margin: 1.5rem 0;
    }
    .stButton > button {
        background: linear-gradient(135deg, #DC2626, #7F1D1D);
        color: white;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">iRMC SecureAI ®</h1>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="signup-container">', unsafe_allow_html=True)
        
        st.markdown("### 📝 Create New Account")
        
        with st.form("signup_form"):
            full_name = st.text_input("**Full Name**", placeholder="Enter your full name")
            username = st.text_input("**Username**", placeholder="Choose a username")
            email = st.text_input("**Email**", placeholder="Enter your email")
            password = st.text_input("**Password**", type="password", placeholder="Create a password (min 6 characters)")
            confirm_password = st.text_input("**Confirm Password**", type="password", placeholder="Confirm your password")
            
            col1, col2 = st.columns(2)
            with col1:
                role = st.selectbox("**Role**", ["analyst", "investigator", "viewer"])
            with col2:
                department = st.text_input("**Department**", placeholder="e.g., Fraud Investigation")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("**Register**", use_container_width=True)
            with col2:
                if st.form_submit_button("**Back to Login**", use_container_width=True):
                    st.session_state.page = "login"
                    st.rerun()
            
            if submitted:
                if not all([full_name, username, email, password, confirm_password]):
                    st.error("❌ Please fill in all required fields")
                elif password != confirm_password:
                    st.error("❌ Passwords do not match")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                else:
                    with st.spinner("Creating account..."):
                        result = register_user(username, email, password, full_name, role, department)
                        if result["success"]:
                            st.success("✅ Registration successful! Please login.")
                            st.session_state.page = "login"
                            st.rerun()
                        else:
                            st.error(f"❌ {result['message']}")
        
        st.markdown('</div>', unsafe_allow_html=True)
