"""
Login page for iRMC SecureAI
"""

import streamlit as st
from auth import login_user

def show():
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
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
    .stButton > button:hover {
        background: linear-gradient(135deg, #B91C1C, #5F0F0F);
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">iRMC SecureAI ®</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; margin-bottom: 2rem;">Agentic AI for Financial Fraud Detection</p>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        st.markdown("### 🔐 Login to Your Account")
        
        with st.form("login_form"):
            username = st.text_input("**Username or Email**", placeholder="Enter your username or email")
            password = st.text_input("**Password**", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("**Login**", use_container_width=True)
            with col2:
                if st.form_submit_button("**Create Account**", use_container_width=True):
                    st.session_state.page = "signup"
                    st.rerun()
            
            if submitted:
                if not username or not password:
                    st.error("❌ Please enter both username and password")
                else:
                    with st.spinner("Authenticating..."):
                        success, message = login_user(username, password)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
        
        # Demo credentials hint
        st.markdown("---")
        st.markdown("""
        **Demo Credentials:**
        - Admin: `admin` / `Admin@123`
        - Analyst: `analyst` / `demo123`
        """)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown('<p style="text-align: center; color: #666;">© 2026 iRMC SecureAI - Enterprise Fraud Detection Platform</p>', unsafe_allow_html=True)
