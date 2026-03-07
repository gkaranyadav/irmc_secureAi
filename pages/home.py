"""
Home page - shown after successful login
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

def show():
    user = st.session_state.user
    
    # Header with user info
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        st.markdown(f"# 🏠 Welcome, {user['full_name']}!")
        st.markdown(f"**Role:** {user['role'].title()} • **Department:** {user['department'] or 'N/A'}")
    with col3:
        if st.button("**Logout**"):
            from auth import logout_user
            logout_user()
            st.rerun()
    
    st.markdown("---")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #DC2626, #7F1D1D); color: white; padding: 1.5rem; border-radius: 12px; text-align: center;">
            <h4 style="margin:0;">Today's Transactions</h4>
            <h2 style="margin:0.5rem 0;">1,24,891</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #2563EB, #1E3A8A); color: white; padding: 1.5rem; border-radius: 12px; text-align: center;">
            <h4 style="margin:0;">Fraud Alerts</h4>
            <h2 style="margin:0.5rem 0;">23</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #059669, #047857); color: white; padding: 1.5rem; border-radius: 12px; text-align: center;">
            <h4 style="margin:0;">Cases Assigned</h4>
            <h2 style="margin:0.5rem 0;">12</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #D97706, #B45309); color: white; padding: 1.5rem; border-radius: 12px; text-align: center;">
            <h4 style="margin:0;">Detection Rate</h4>
            <h2 style="margin:0.5rem 0;">94.2%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🚨 Recent Alerts", "👤 Profile"])
    
    with tab1:
        st.markdown("### Recent Fraud Activity")
        
        # Sample data (replace with real data from database)
        data = pd.DataFrame({
            'Date': pd.date_range(end=datetime.now(), periods=10, freq='D'),
            'Fraud Cases': [12, 15, 8, 21, 18, 24, 19, 22, 17, 14],
            'Amount Blocked (Lakhs)': [2.4, 3.1, 1.8, 4.2, 3.7, 5.1, 4.3, 4.8, 3.9, 3.2]
        })
        
        fig = px.line(data, x='Date', y=['Fraud Cases', 'Amount Blocked (Lakhs)'], 
                     title="Fraud Trends - Last 10 Days")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### Recent Fraud Alerts")
        
        alerts = [
            {"time": "2 min ago", "card": "****1234", "amount": "₹45,000", "risk": "96%", "status": "🚨 Critical"},
            {"time": "5 min ago", "card": "****5678", "amount": "₹12,500", "risk": "88%", "status": "⚠️ High"},
            {"time": "12 min ago", "card": "****9012", "amount": "₹2,34,000", "risk": "99%", "status": "🚨 Critical"},
            {"time": "18 min ago", "card": "****3456", "amount": "₹8,750", "risk": "72%", "status": "⚠️ Medium"},
        ]
        
        for alert in alerts:
            st.markdown(f"""
            <div style="background: #FEE2E2; border-left: 4px solid #DC2626; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
                <strong>{alert['time']}</strong> - Card: {alert['card']} | Amount: {alert['amount']} | Risk: {alert['risk']} | {alert['status']}
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### Your Profile")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Username:** {user['username']}")
            st.markdown(f"**Full Name:** {user['full_name']}")
            st.markdown(f"**Email:** {user['email']}")
        with col2:
            st.markdown(f"**Role:** {user['role'].title()}")
            st.markdown(f"**Department:** {user['department'] or 'Not set'}")
            st.markdown(f"**User ID:** {user['id']}")
        
        if st.button("🔄 Change Password"):
            st.info("Password change feature coming soon!")
