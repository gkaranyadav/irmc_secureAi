# src/dashboard/app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.core.config import settings
from src.core.database import get_db
from src.agents.orchestrator import AgentOrchestrator

# Page config
st.set_page_config(
    page_title="iRMC SentinelAI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        font-weight: 700;
    }
    .agent-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        border-left: 5px solid #3B82F6;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .fraud-alert {
        background-color: #FEE2E2;
        border-left: 5px solid #EF4444;
        padding: 1rem;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = AgentOrchestrator()
if 'transactions' not in st.session_state:
    # Generate sample data for demo
    np.random.seed(42)
    n_transactions = 1000
    st.session_state.transactions = pd.DataFrame({
        'transaction_id': [f'TXN{i:08d}' for i in range(n_transactions)],
        'amount': np.random.exponential(100, n_transactions).round(2),
        'merchant': np.random.choice(['Amazon', 'Walmart', 'Target', 'Starbucks', 'Apple', 'Netflix'], n_transactions),
        'card_last4': np.random.choice(['1234', '5678', '9012', '3456', '7890'], n_transactions),
        'timestamp': pd.date_range(end=datetime.now(), periods=n_transactions, freq='5min'),
        'country': np.random.choice(['USA', 'UK', 'Canada', 'India', 'Germany'], n_transactions, p=[0.7, 0.1, 0.1, 0.05, 0.05]),
        'risk_score': np.random.randint(0, 100, n_transactions),
        'is_fraud': np.random.choice([0, 1], n_transactions, p=[0.97, 0.03])
    })

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150x50?text=iRMC+SentinelAI", use_column_width=True)
    st.markdown("---")
    
    st.markdown("### 🕵️ Agents Status")
    agents_status = {
        "Dark Web Monitor": "🟢 Active",
        "Behavioral Profiler": "🟢 Active",
        "Pattern Miner": "🟢 Active",
        "Network Analyzer": "🟢 Active",
        "Anomaly Detector": "🟢 Active",
        "Risk Aggregator": "🟢 Active",
        "Action Agent": "🟢 Active",
        "Feedback Agent": "🟢 Active"
    }
    
    for agent, status in agents_status.items():
        st.markdown(f"{agent}: {status}")
    
    st.markdown("---")
    
    st.markdown("### ⚙️ Controls")
    risk_threshold = st.slider("Risk Threshold", 0, 100, 70)
    auto_block = st.checkbox("Auto-block high risk", value=True)
    
    if st.button("🔄 Retrain Models"):
        st.info("Retraining triggered...")

# Main content
st.markdown('<h1 class="main-header">iRMC SentinelAI - Agentic Fraud Detection</h1>', unsafe_allow_html=True)
st.markdown("*Intelligent agents working together to prevent card fraud*")

# Top metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_today = len(st.session_state.transactions[
        st.session_state.transactions['timestamp'] > datetime.now() - timedelta(days=1)
    ])
    st.metric("Transactions Today", f"{total_today:,}", "+12%")

with col2:
    fraud_today = len(st.session_state.transactions[
        (st.session_state.transactions['timestamp'] > datetime.now() - timedelta(days=1)) &
        (st.session_state.transactions['is_fraud'] == 1)
    ])
    st.metric("Fraud Attempts", fraud_today, "-8%")

with col3:
    blocked = int(fraud_today * 0.85)  # 85% blocked
    st.metric("Blocked", blocked, "95% success")

with col4:
    avg_response = 47  # milliseconds
    st.metric("Avg Response", f"{avg_response}ms", "-12ms")

st.markdown("---")

# Real-time transaction monitor
st.markdown("### 📊 Real-Time Transaction Monitor")

# Filter by risk
risk_filter = st.selectbox("Filter by Risk", ["All", "Low (0-30)", "Medium (31-70)", "High (71-100)"])

df = st.session_state.transactions.copy()
if risk_filter == "Low (0-30)":
    df = df[df['risk_score'] <= 30]
elif risk_filter == "Medium (31-70)":
    df = df[(df['risk_score'] > 30) & (df['risk_score'] <= 70)]
elif risk_filter == "High (71-100)":
    df = df[df['risk_score'] > 70]

# Color coding for risk
def color_risk(val):
    if val > 70:
        return 'background-color: #FEE2E2'
    elif val > 30:
        return 'background-color: #FEF3C7'
    return ''

st.dataframe(
    df[['timestamp', 'transaction_id', 'amount', 'merchant', 'country', 'risk_score', 'is_fraud']].head(20),
    column_config={
        "timestamp": "Time",
        "transaction_id": "Transaction ID",
        "amount": st.column_config.NumberColumn("Amount", format="$%.2f"),
        "risk_score": st.column_config.NumberColumn("Risk Score", format="%d"),
        "is_fraud": st.column_config.CheckboxColumn("Fraud")
    },
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# Agent Activity Dashboard
st.markdown("### 🤖 Agent Activity")

tab1, tab2, tab3, tab4 = st.tabs(["Detection Agents", "Analysis Agents", "Action Agents", "Performance"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="agent-card">', unsafe_allow_html=True)
        st.markdown("#### 🕵️ Dark Web Monitor")
        st.markdown("**Status:** Scanning 150+ dark web sources")
        st.markdown("**Last Find:** 2 hours ago - 3 cards compromised")
        st.markdown("**Cards Flagged Today:** 47")
        st.progress(0.65, text="Coverage: 65% of known sources")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="agent-card">', unsafe_allow_html=True)
        st.markdown("#### 👤 Behavioral Profiler")
        st.markdown("**Status:** Active - 10,234 profiles loaded")
        st.markdown("**Profiles Updated Today:** 1,234")
        st.markdown("**Anomaly Detection Rate:** 94%")
        st.progress(0.94, text="Accuracy")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="agent-card">', unsafe_allow_html=True)
        st.markdown("#### 🔍 Pattern Miner")
        st.markdown("**Status:** Analyzing transaction streams")
        st.markdown("**Patterns Detected Today:** 23")
        st.markdown("**Top Pattern:** Card testing (12 cases)")
        st.progress(0.78, text="Pattern coverage")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="agent-card">', unsafe_allow_html=True)
        st.markdown("#### 🌐 Network Analyzer")
        st.markdown("**Status:** Graph analysis running")
        st.markdown("**Nodes in Graph:** 45,678")
        st.markdown("**Edges:** 234,567")
        st.markdown("**Fraud Rings Detected:** 3")
        st.progress(0.82, text="Graph coverage")
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="agent-card">', unsafe_allow_html=True)
        st.markdown("#### 📊 Anomaly Detector")
        st.markdown("**Status:** Real-time scoring")
        st.markdown("**Anomalies Found Today:** 156")
        st.markdown("**False Positive Rate:** 3.2%")
        st.progress(0.968, text="Precision")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="agent-card">', unsafe_allow_html=True)
        st.markdown("#### 🧮 Risk Aggregator")
        st.markdown("**Status:** Ensemble scoring active")
        st.markdown("**Transactions Scored:** 234,567")
        st.markdown("**Average Score:** 23.4")
        
        # Sample risk distribution
        risk_dist = pd.DataFrame({
            'Risk Level': ['Low', 'Medium', 'High'],
            'Count': [7890, 1234, 156]
        })
        fig = px.pie(risk_dist, values='Count', names='Risk Level', 
                     color_discrete_map={'Low':'#10B981', 'Medium':'#F59E0B', 'High':'#EF4444'})
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="agent-card">', unsafe_allow_html=True)
        st.markdown("#### ⚡ Action Agent")
        st.markdown("**Status:** Taking actions")
        st.markdown("**Blocks Today:** 134")
        st.markdown("**Alerts Sent:** 567")
        st.markdown("**Avg Response Time:** 47ms")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="agent-card">', unsafe_allow_html=True)
        st.markdown("#### 📝 Feedback Agent")
        st.markdown("**Status:** Learning from outcomes")
        st.markdown("**Feedback Processed Today:** 234")
        st.markdown("**Model Updates:** 3 pending")
        st.markdown("**Accuracy Improvement:** +2.3% this week")
        st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    # Performance charts
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pd.date_range(end=datetime.now(), periods=24, freq='1H'),
        y=np.random.normal(95, 2, 24).cummax(),
        mode='lines+markers',
        name='Detection Rate'
    ))
    fig.add_trace(go.Scatter(
        x=pd.date_range(end=datetime.now(), periods=24, freq='1H'),
        y=np.random.normal(3, 1, 24).cummin(),
        mode='lines+markers',
        name='False Positive Rate'
    ))
    fig.update_layout(
        title="Agent Performance (Last 24 Hours)",
        xaxis_title="Time",
        yaxis_title="Percentage",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Recent alerts
st.markdown("### 🚨 Recent Alerts")

alerts = [
    {"time": "2 min ago", "type": "High Risk Transaction", "card": "****1234", "amount": "$5,234", "action": "Blocked"},
    {"time": "5 min ago", "type": "Dark Web Match", "card": "****5678", "amount": "-", "action": "Card Blocked"},
    {"time": "12 min ago", "type": "Unusual Location", "card": "****9012", "amount": "$234", "action": "Challenge Sent"},
    {"time": "18 min ago", "type": "Pattern Detected", "card": "****3456", "amount": "$56, "$78", "$45", "action": "Monitoring"},
]

for alert in alerts:
    st.markdown(f"""
    <div class="fraud-alert">
        <strong>{alert['time']}</strong> - {alert['type']} | Card: {alert['card']} | Amount: {alert['amount']} | Action: {alert['action']}
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("© 2026 iRMC SentinelAI - Open Source Agentic Fraud Detection")
