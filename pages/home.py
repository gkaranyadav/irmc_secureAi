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
        st.markdown(f"**Role:** {user['role'].title()} • **Department:** {user['department'] or 'Not specified'}")
    with col3:
        if st.button("**🚪 Logout**", use_container_width=True):
            from auth import logout_user
            logout_user()
            st.rerun()
    
    st.markdown("---")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #DC2626, #7F1D1D); color: white; padding: 1.5rem; border-radius: 12px; text-align: center;">
            <h4 style="margin:0; font-size:0.9rem;">TODAY'S TRANSACTIONS</h4>
            <h2 style="margin:0.5rem 0;">1,24,891</h2>
            <p style="margin:0; font-size:0.8rem;">+12% vs yesterday</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #2563EB, #1E3A8A); color: white; padding: 1.5rem; border-radius: 12px; text-align: center;">
            <h4 style="margin:0; font-size:0.9rem;">FRAUD ALERTS</h4>
            <h2 style="margin:0.5rem 0;">23</h2>
            <p style="margin:0; font-size:0.8rem;">8 critical</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #059669, #047857); color: white; padding: 1.5rem; border-radius: 12px; text-align: center;">
            <h4 style="margin:0; font-size:0.9rem;">CASES ASSIGNED</h4>
            <h2 style="margin:0.5rem 0;">12</h2>
            <p style="margin:0; font-size:0.8rem;">3 pending review</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #D97706, #B45309); color: white; padding: 1.5rem; border-radius: 12px; text-align: center;">
            <h4 style="margin:0; font-size:0.9rem;">DETECTION RATE</h4>
            <h2 style="margin:0.5rem 0;">94.2%</h2>
            <p style="margin:0; font-size:0.8rem;">↑ 2.3% this week</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🚨 Recent Alerts", "👤 Profile"])
    
    with tab1:
        st.markdown("### 📈 Fraud Trends - Last 7 Days")
        
        # Sample data
        data = pd.DataFrame({
            'Date': pd.date_range(end=datetime.now(), periods=7, freq='D'),
            'Fraud Cases': [12, 15, 8, 21, 18, 24, 19],
            'Amount Blocked (Lakhs)': [2.4, 3.1, 1.8, 4.2, 3.7, 5.1, 4.3]
        })
        
        fig = px.line(data, x='Date', y=['Fraud Cases', 'Amount Blocked (Lakhs)'], 
                     title="Fraud Detection Performance")
        st.plotly_chart(fig, use_container_width=True)
        
        # Recent transactions table
        st.markdown("### 📋 Recent Fraudulent Transactions")
        sample_transactions = pd.DataFrame({
            'Transaction ID': ['TXN1001', 'TXN1002', 'TXN1003', 'TXN1004'],
            'Amount': ['₹45,000', '₹12,500', '₹2,34,000', '₹8,750'],
            'Merchant': ['Amazon', 'Flipkart', 'Apple', 'Swiggy'],
            'Risk Score': ['96%', '88%', '99%', '72%'],
            'Status': ['Blocked', 'OTP Sent', 'Blocked', 'Flagged']
        })
        st.dataframe(sample_transactions, use_container_width=True, hide_index=True)
    
    with tab2:
        st.markdown("### 🚨 Live Fraud Alerts")
        
        alerts = [
            {"time": "2 min ago", "card": "****1234", "amount": "₹45,000", "location": "Mumbai", "risk": "96%", "status": "🔴 CRITICAL"},
            {"time": "5 min ago", "card": "****5678", "amount": "₹12,500", "location": "Delhi", "risk": "88%", "status": "🟠 HIGH"},
            {"time": "12 min ago", "card": "****9012", "amount": "₹2,34,000", "location": "Bangalore", "risk": "99%", "status": "🔴 CRITICAL"},
            {"time": "18 min ago", "card": "****3456", "amount": "₹8,750", "location": "Chennai", "risk": "72%", "status": "🟡 MEDIUM"},
            {"time": "25 min ago", "card": "****7890", "amount": "₹67,000", "location": "Pune", "risk": "91%", "status": "🔴 CRITICAL"},
        ]
        
        for alert in alerts:
            color = "#DC2626" if "CRITICAL" in alert['status'] else "#D97706" if "HIGH" in alert['status'] else "#2563EB"
            st.markdown(f"""
            <div style="background: #FEE2E2; border-left: 4px solid {color}; padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
                <strong>{alert['time']}</strong> - Card: {alert['card']} | Amount: {alert['amount']} | Location: {alert['location']}<br>
                Risk: {alert['risk']} | Status: {alert['status']}
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 👤 User Profile")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Username:** {user['username']}")
            st.markdown(f"**Full Name:** {user['full_name']}")
            st.markdown(f"**Email:** {user['email']}")
            st.markdown(f"**User ID:** {user['id']}")
        with col2:
            st.markdown(f"**Role:** {user['role'].title()}")
            st.markdown(f"**Department:** {user['department'] or 'Not set'}")
            st.markdown(f"**Admin Access:** {'Yes' if user['is_admin'] else 'No'}")
        
        st.markdown("---")
        if st.button("🔄 Change Password", use_container_width=False):
            st.info("Password change feature coming soon!")
