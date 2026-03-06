# src/dashboard/app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import random

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent))

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
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 2rem;
    }
    .agent-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        border-left: 5px solid #3B82F6;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        border-bottom: 3px solid #3B82F6;
    }
    .fraud-alert {
        background-color: #FEE2E2;
        border-left: 5px solid #EF4444;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-active {
        background-color: #D1FAE5;
        color: #065F46;
    }
    .status-warning {
        background-color: #FEF3C7;
        color: #92400E;
    }
    .status-critical {
        background-color: #FEE2E2;
        color: #991B1B;
    }
    .footer {
        text-align: center;
        color: #6B7280;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #E5E7EB;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'transactions' not in st.session_state:
    # Generate sample data for demo
    np.random.seed(42)
    random.seed(42)
    
    n_transactions = 5000
    merchants = ['Amazon', 'Walmart', 'Target', 'Starbucks', 'Apple', 'Netflix', 
                 'Uber', 'DoorDash', 'CVS', 'Walgreens', 'Home Depot', 'Best Buy',
                 'Costco', 'Spotify', 'Shell', 'Marriott', 'Delta Airlines']
    
    countries = ['USA', 'UK', 'Canada', 'India', 'Germany', 'France', 'Australia']
    country_weights = [0.6, 0.12, 0.08, 0.06, 0.05, 0.05, 0.04]
    
    # Generate timestamps over last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    timestamps = [start_date + timedelta(
        days=random.randint(0, 7),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    ) for _ in range(n_transactions)]
    
    # Generate risk scores with some fraud cases
    risk_scores = []
    is_fraud = []
    for i in range(n_transactions):
        if random.random() < 0.03:  # 3% fraud rate
            risk_scores.append(random.randint(75, 100))
            is_fraud.append(1)
        else:
            risk_scores.append(random.randint(0, 40))
            is_fraud.append(0)
    
    st.session_state.transactions = pd.DataFrame({
        'transaction_id': [f'TXN{random.randint(10000000, 99999999)}' for _ in range(n_transactions)],
        'timestamp': timestamps,
        'amount': [round(random.uniform(5, 500), 2) for _ in range(n_transactions)],
        'merchant': [random.choice(merchants) for _ in range(n_transactions)],
        'card_last4': [f'{random.randint(1000, 9999)}' for _ in range(n_transactions)],
        'country': [random.choices(countries, weights=country_weights)[0] for _ in range(n_transactions)],
        'risk_score': risk_scores,
        'is_fraud': is_fraud
    })
    
    # Sort by timestamp
    st.session_state.transactions = st.session_state.transactions.sort_values('timestamp', ascending=False).reset_index(drop=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🛡️ iRMC SentinelAI")
    st.markdown("---")
    
    st.markdown("### 🤖 Agents Status")
    
    agents_status = [
        {"name": "Dark Web Monitor", "status": "active", "icon": "🕵️"},
        {"name": "Behavioral Profiler", "status": "active", "icon": "👤"},
        {"name": "Pattern Miner", "status": "active", "icon": "🔍"},
        {"name": "Network Analyzer", "status": "active", "icon": "🌐"},
        {"name": "Anomaly Detector", "status": "warning", "icon": "📊"},
        {"name": "Risk Aggregator", "status": "active", "icon": "🧮"},
        {"name": "Action Agent", "status": "active", "icon": "⚡"},
        {"name": "Feedback Agent", "status": "active", "icon": "📝"}
    ]
    
    for agent in agents_status:
        status_class = "status-active" if agent['status'] == "active" else "status-warning"
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-size: 1.2rem; margin-right: 0.5rem;">{agent['icon']}</span>
            <span style="flex-grow: 1;">{agent['name']}</span>
            <span class="status-badge {status_class}">{agent['status'].upper()}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### ⚙️ Controls")
    risk_threshold = st.slider("Risk Threshold", 0, 100, 70, 
                               help="Transactions above this risk score will be flagged")
    auto_block = st.checkbox("Auto-block high risk (>85)", value=True)
    show_fraud_only = st.checkbox("Show only fraud cases", value=False)
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()
    
    st.markdown("---")
    
    st.markdown("### 📊 System Health")
    st.markdown("🟢 **All systems operational**")
    st.markdown(f"⏱️ **Uptime:** 99.97%")
    st.markdown(f"📈 **Today's volume:** {len(st.session_state.transactions[st.session_state.transactions['timestamp'] > datetime.now() - timedelta(days=1)])} txns")
    
    st.markdown("---")
    st.markdown("© 2026 iRMC SentinelAI")
    st.markdown("*Open Source Agentic Fraud Detection*")

# Main content
st.markdown('<h1 class="main-header">iRMC SentinelAI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Intelligent agents working together to prevent card fraud in real-time</p>', unsafe_allow_html=True)

# Top metrics
col1, col2, col3, col4 = st.columns(4)

# Filter transactions for today
today = datetime.now().date()
today_transactions = st.session_state.transactions[
    pd.to_datetime(st.session_state.transactions['timestamp']).dt.date == today
]
today_fraud = today_transactions[today_transactions['is_fraud'] == 1]
blocked_rate = 85  # Simulated blocked rate

with col1:
    st.markdown("""
    <div class="metric-card">
        <h3 style="margin:0; color:#6B7280; font-size:0.9rem;">TODAY'S TRANSACTIONS</h3>
        <h2 style="margin:0.5rem 0; font-size:2rem;">{:,}</h2>
        <p style="margin:0; color:#10B981;">↑ 12% vs yesterday</p>
    </div>
    """.format(len(today_transactions)), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <h3 style="margin:0; color:#6B7280; font-size:0.9rem;">FRAUD ATTEMPTS</h3>
        <h2 style="margin:0.5rem 0; font-size:2rem;">{}</h2>
        <p style="margin:0; color:#EF4444;">↓ 8% vs yesterday</p>
    </div>
    """.format(len(today_fraud)), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <h3 style="margin:0; color:#6B7280; font-size:0.9rem;">BLOCKED</h3>
        <h2 style="margin:0.5rem 0; font-size:2rem;">{}</h2>
        <p style="margin:0; color="#10B981;">{}% success rate</p>
    </div>
    """.format(int(len(today_fraud) * blocked_rate / 100), blocked_rate), unsafe_allow_html=True)

with col4:
    avg_response = 47
    st.markdown("""
    <div class="metric-card">
        <h3 style="margin:0; color:#6B7280; font-size:0.9rem;">AVG RESPONSE</h3>
        <h2 style="margin:0.5rem 0; font-size:2rem;">{}ms</h2>
        <p style="margin:0; color="#10B981;">↓ 12ms vs yesterday</p>
    </div>
    """.format(avg_response), unsafe_allow_html=True)

st.markdown("---")

# Real-time transaction monitor
st.markdown("### 📊 Real-Time Transaction Monitor")

# Filter transactions based on user input
df_display = st.session_state.transactions.copy()
if show_fraud_only:
    df_display = df_display[df_display['is_fraud'] == 1]

# Add color coding for risk
def highlight_risk(row):
    if row['risk_score'] > 85:
        return ['background-color: #FEE2E2'] * len(row)
    elif row['risk_score'] > 70:
        return ['background-color: #FEF3C7'] * len(row)
    else:
        return [''] * len(row)

# Display transactions
st.dataframe(
    df_display[['timestamp', 'transaction_id', 'amount', 'merchant', 'country', 'risk_score', 'is_fraud']].head(20),
    column_config={
        "timestamp": "Time",
        "transaction_id": "Transaction ID",
        "amount": st.column_config.NumberColumn("Amount", format="$%.2f"),
        "merchant": "Merchant",
        "country": "Country",
        "risk_score": st.column_config.NumberColumn("Risk Score", format="%d ⚠️"),
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
        st.markdown("""
        <div class="agent-card">
            <h4>🕵️ Dark Web Monitor</h4>
            <p><strong>Status:</strong> <span class="status-badge status-active">ACTIVE</span></p>
            <p><strong>Sources scanned:</strong> 156 dark web forums</p>
            <p><strong>Last find:</strong> 2 hours ago - 3 cards compromised</p>
            <p><strong>Cards flagged today:</strong> 47</p>
            <progress value="65" max="100" style="width:100%; height:10px;"></progress>
            <p style="text-align:right; margin:0; font-size:0.8rem;">Coverage: 65%</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="agent-card">
            <h4>👤 Behavioral Profiler</h4>
            <p><strong>Status:</strong> <span class="status-badge status-active">ACTIVE</span></p>
            <p><strong>Profiles loaded:</strong> 10,234</p>
            <p><strong>Updated today:</strong> 1,234</p>
            <p><strong>Accuracy:</strong> 94%</p>
            <progress value="94" max="100" style="width:100%; height:10px;"></progress>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="agent-card">
            <h4>🔍 Pattern Miner</h4>
            <p><strong>Status:</strong> <span class="status-badge status-active">ACTIVE</span></p>
            <p><strong>Patterns detected today:</strong> 23</p>
            <p><strong>Top pattern:</strong> Card testing (12 cases)</p>
            <p><strong>Coverage:</strong> 78%</p>
            <progress value="78" max="100" style="width:100%; height:10px;"></progress>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="agent-card">
            <h4>🌐 Network Analyzer</h4>
            <p><strong>Status:</strong> <span class="status-badge status-active">ACTIVE</span></p>
            <p><strong>Graph nodes:</strong> 45,678</p>
            <p><strong>Edges:</strong> 234,567</p>
            <p><strong>Fraud rings detected:</strong> 3</p>
            <progress value="82" max="100" style="width:100%; height:10px;"></progress>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="agent-card">
            <h4>📊 Anomaly Detector</h4>
            <p><strong>Status:</strong> <span class="status-badge status-warning">DEGRADED</span></p>
            <p><strong>Anomalies found today:</strong> 156</p>
            <p><strong>False positive rate:</strong> 3.2%</p>
            <p><strong>Precision:</strong> 96.8%</p>
            <progress value="96.8" max="100" style="width:100%; height:10px;"></progress>
            <p style="color:#F59E0B; font-size:0.8rem;">⚠️ Running on backup model</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="agent-card">
            <h4>🧮 Risk Aggregator</h4>
            <p><strong>Status:</strong> <span class="status-badge status-active">ACTIVE</span></p>
            <p><strong>Transactions scored:</strong> 234,567</p>
            <p><strong>Average score:</strong> 23.4</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Risk distribution pie chart
        risk_dist = pd.DataFrame({
            'Risk Level': ['Low (0-30)', 'Medium (31-70)', 'High (71-100)'],
            'Count': [7890, 1234, 156]
        })
        fig = px.pie(risk_dist, values='Count', names='Risk Level', 
                     color_discrete_map={
                         'Low (0-30)': '#10B981',
                         'Medium (31-70)': '#F59E0B',
                         'High (71-100)': '#EF4444'
                     })
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="agent-card">
            <h4>⚡ Action Agent</h4>
            <p><strong>Status:</strong> <span class="status-badge status-active">ACTIVE</span></p>
            <p><strong>Blocks today:</strong> 134</p>
            <p><strong>Alerts sent:</strong> 567</p>
            <p><strong>Avg response time:</strong> 47ms</p>
            <progress value="99.9" max="100" style="width:100%; height:10px;"></progress>
            <p style="text-align:right;">Uptime: 99.9%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="agent-card">
            <h4>📝 Feedback Agent</h4>
            <p><strong>Status:</strong> <span class="status-badge status-active">ACTIVE</span></p>
            <p><strong>Feedback processed today:</strong> 234</p>
            <p><strong>Model updates pending:</strong> 3</p>
            <p><strong>Accuracy improvement:</strong> +2.3% this week</p>
            <progress value="2.3" max="10" style="width:100%; height:10px;"></progress>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    # Performance charts
    st.markdown("#### 📈 Agent Performance (Last 24 Hours)")
    
    # Create sample performance data
    hours = list(range(24))
    detection_rate = [95 + np.random.normal(0, 1) for _ in hours]
    false_positive = [3 + np.random.normal(0, 0.5) for _ in hours]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours,
        y=detection_rate,
        mode='lines+markers',
        name='Detection Rate (%)',
        line=dict(color='#10B981', width=3)
    ))
    fig.add_trace(go.Scatter(
        x=hours,
        y=false_positive,
        mode='lines+markers',
        name='False Positive Rate (%)',
        line=dict(color='#EF4444', width=3)
    ))
    fig.update_layout(
        xaxis_title="Hours Ago",
        yaxis_title="Percentage",
        height=400,
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Model performance table
    st.markdown("#### 🧠 Model Performance")
    
    models_df = pd.DataFrame({
        'Model': ['XGBoost', 'Isolation Forest', 'Neural Network', 'Ensemble'],
        'Accuracy': [96.2, 91.5, 94.8, 97.3],
        'Precision': [95.1, 89.2, 93.4, 96.8],
        'Recall': [94.3, 88.7, 92.9, 95.9],
        'F1 Score': [94.7, 88.9, 93.1, 96.3],
        'Last Trained': ['2026-03-05', '2026-03-04', '2026-03-03', '2026-03-05']
    })
    
    st.dataframe(models_df, use_container_width=True, hide_index=True)

st.markdown("---")

# Recent alerts
st.markdown("### 🚨 Recent Alerts")

# CORRECTED ALERTS SECTION - NO SYNTAX ERROR
alerts = [
    {"time": "2 min ago", "type": "High Risk Transaction", "card": "****1234", "amount": "$5,234", "action": "Blocked"},
    {"time": "5 min ago", "type": "Dark Web Match", "card": "****5678", "amount": "N/A", "action": "Card Blocked"},
    {"time": "12 min ago", "type": "Unusual Location", "card": "****9012", "amount": "$234", "action": "Challenge Sent"},
    {"time": "18 min ago", "type": "Pattern Detected", "card": "****3456", "amount": "$56, $78, $45", "action": "Monitoring"},
    {"time": "25 min ago", "type": "Velocity Check", "card": "****7890", "amount": "$1,234", "action": "Flagged"},
    {"time": "32 min ago", "type": "Card Testing", "card": "****2345", "amount": "$1, $5, $10", "action": "Blocked"},
    {"time": "41 min ago", "type": "Amount Anomaly", "card": "****6789", "amount": "$8,500", "action": "Review"},
    {"time": "55 min ago", "type": "New Device", "card": "****0123", "amount": "$320", "action": "Verified"}
]

for alert in alerts:
    # Determine color based on action
    if alert['action'] == "Blocked":
        color = "#EF4444"
    elif alert['action'] == "Challenge Sent":
        color = "#F59E0B"
    else:
        color = "#3B82F6"
    
    st.markdown(f"""
    <div style="background-color: #F9FAFB; border-left: 5px solid {color}; padding: 0.75rem 1rem; border-radius: 8px; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center;">
        <div>
            <strong>{alert['time']}</strong> - {alert['type']} | Card: {alert['card']} | Amount: {alert['amount']}
        </div>
        <div>
            <span style="background-color: {color}; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">
                {alert['action']}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Fraud patterns insights
st.markdown("---")
st.markdown("### 📊 Fraud Pattern Insights")

col1, col2 = st.columns(2)

with col1:
    # Top fraud types
    fraud_types = pd.DataFrame({
        'Fraud Type': ['Card Testing', 'Unusual Location', 'High Amount', 'Velocity Check', 'Dark Web Match'],
        'Count': [45, 32, 28, 21, 15]
    })
    
    fig = px.bar(fraud_types, x='Fraud Type', y='Count', color='Count',
                 color_continuous_scale=['#10B981', '#F59E0B', '#EF4444'])
    fig.update_layout(title="Top Fraud Types (Last 7 Days)", height=350)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Fraud by hour
    hours = list(range(24))
    fraud_by_hour = [random.randint(5, 30) for _ in hours]
    
    fig = px.line(x=hours, y=fraud_by_hour, markers=True)
    fig.update_layout(
        title="Fraud Attempts by Hour of Day",
        xaxis_title="Hour (24h)",
        yaxis_title="Number of Attempts",
        height=350
    )
    fig.update_traces(line_color='#EF4444', line_width=3)
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("""
<div class="footer">
    <p>iRMC SentinelAI v1.0.0 | Open Source Agentic Fraud Detection | © 2026</p>
    <p style="font-size:0.7rem;">Running on 100% free and open-source technology stack</p>
</div>
""", unsafe_allow_html=True)
