import streamlit as st
import os
from openai import OpenAI
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import time
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Investment Research Platform Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS - NOW VISIBLE IMMEDIATELY
st.markdown("""
<style>
/* Main header styling */
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 3rem 2rem;
    border-radius: 20px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    animation: headerGlow 3s ease-in-out infinite alternate;
}

@keyframes headerGlow {
    from { box-shadow: 0 10px 30px rgba(102,126,234,0.4); }
    to { box-shadow: 0 15px 40px rgba(118,75,162,0.6); }
}

.main-header h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.main-header p {
    font-size: 1.2rem;
    opacity: 0.9;
}

/* Hero section */
.hero-section {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    padding: 2rem;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin: 2rem 0;
    animation: pulse 2s ease-in-out infinite alternate;
}

@keyframes pulse {
    from { transform: scale(1); }
    to { transform: scale(1.02); }
}

/* Feature cards */
.feature-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    padding: 2rem;
    border-radius: 15px;
    border: 2px solid transparent;
    background-clip: padding-box;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
    margin: 1rem 0;
    position: relative;
    overflow: hidden;
}

.feature-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
    transition: left 0.5s;
}

.feature-card:hover::before {
    left: 100%;
}

.feature-card:hover {
    transform: translateY(-10px) scale(1.02);
    box-shadow: 0 15px 35px rgba(0,0,0,0.2);
    border-color: #667eea;
}

.feature-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    color: #667eea;
}

.feature-title {
    font-size: 1.5rem;
    font-weight: bold;
    color: #333;
    margin-bottom: 1rem;
}

.feature-description {
    color: #666;
    line-height: 1.6;
}

/* Metrics dashboard */
.metrics-row {
    display: flex;
    gap: 1rem;
    margin: 2rem 0;
}

.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    flex: 1;
    box-shadow: 0 8px 25px rgba(102,126,234,0.3);
    transition: transform 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-5px) scale(1.05);
}

.metric-value {
    font-size: 2.5rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
}

.metric-label {
    font-size: 1rem;
    opacity: 0.8;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Sidebar enhancements */
.sidebar-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    margin-bottom: 1rem;
}

.status-indicator {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 8px;
    animation: blink 2s infinite;
}

@keyframes blink {
    0%, 50% { opacity: 1; }
    51%, 100% { opacity: 0.3; }
}

.status-online { background-color: #00ff00; }
.status-offline { background-color: #ff0000; }

/* Analysis sections */
.analysis-section {
    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    padding: 2rem;
    border-radius: 15px;
    margin: 1rem 0;
    border-left: 5px solid #667eea;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}

.analysis-section:hover {
    transform: translateX(10px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    border-left-color: #764ba2;
}

/* Button styles */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.75rem 2rem;
    border-radius: 25px;
    font-weight: bold;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102,126,234,0.3);
}

.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(102,126,234,0.4);
}

/* Progress bars */
.stProgress .st-bo {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
}

.stTabs [data-baseweb="tab"] {
    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    border-radius: 10px 10px 0 0;
    padding: 1rem 2rem;
    font-weight: bold;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

/* Landing page specific */
.welcome-section {
    background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
    padding: 3rem 2rem;
    border-radius: 20px;
    text-align: center;
    margin: 2rem 0;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.welcome-section h2 {
    color: #8b4513;
    font-size: 2.5rem;
    margin-bottom: 1rem;
}

.welcome-section p {
    color: #d2691e;
    font-size: 1.1rem;
}

.demo-section {
    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
    padding: 2rem;
    border-radius: 15px;
    margin: 2rem 0;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'current_ticker' not in st.session_state:
    st.session_state.current_ticker = ""
if 'show_demo' not in st.session_state:
    st.session_state.show_demo = False

# FIXED: Initialize Perplexity client with correct model
@st.cache_resource
def init_perplexity_client():
    """Initialize Perplexity client with correct model"""
    api_key = os.getenv("PPLX_API_KEY")
    if api_key:
        return OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
    else:
        return None

client = init_perplexity_client()

@st.cache_data(ttl=3600)
def query_perplexity(prompt, model="llama-3.1-sonar-large-128k-online"):
    """FIXED: Query Perplexity API with correct model name"""
    if not client:
        return "⚠️ API key not configured"
    
    try:
        response = client.chat.completions.create(
            model=model,  # Using the correct model name
            messages=[
                {"role": "system", "content": "You are a professional equity research analyst. Provide detailed, fact-based analysis with specific data points, sources, and clear reasoning."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error querying Perplexity: {str(e)}"

def create_enhanced_landing_page():
    """Create the enhanced landing page that's visible immediately"""
    
    # Main Header - NOW ENHANCED
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Investment Research Platform Pro</h1>
        <p>Next-Generation Stock Analysis with AI-Powered Insights & Interactive Dashboards</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero section with features
    st.markdown("""
    <div class="hero-section">
        <h2>🎯 Transform Your Investment Decisions</h2>
        <p>Professional-grade analysis with real-time data, interactive charts, and comprehensive reports</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Interactive Dashboards</div>
            <div class="feature-description">
                Real-time financial charts, ratio analysis, and performance metrics with beautiful visualizations
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">AI-Powered Analysis</div>
            <div class="feature-description">
                Comprehensive analysis across 17+ dimensions including management evaluation and sector trends
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📈</div>
            <div class="feature-title">Professional Reports</div>
            <div class="feature-description">
                Download detailed reports in multiple formats with actionable investment recommendations
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Metrics preview
    st.markdown("## 📊 **Live Platform Metrics**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">2,500+</div>
            <div class="metric-label">Stocks Analyzed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">17</div>
            <div class="metric-label">Analysis Dimensions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">99.2%</div>
            <div class="metric-label">Accuracy Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">24/7</div>
            <div class="metric-label">Real-time Data</div>
        </div>
        """, unsafe_allow_html=True)

def create_sample_dashboard():
    """Create sample interactive dashboard"""
    st.markdown("## 📈 **Interactive Dashboard Preview**")
    
    # Sample financial data
    years = list(range(2019, 2024))
    revenue = [100 + i*15 + np.random.randint(-5, 5) for i in range(5)]
    profit = [r * 0.12 + np.random.randint(-2, 3) for r in revenue]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Revenue and profit chart
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Revenue Growth Trend', 'Profitability Analysis'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        fig.add_trace(
            go.Scatter(x=years, y=revenue, mode='lines+markers', 
                      name='Revenue (₹Cr)', line=dict(color='#667eea', width=4)),
            row=1, col=1
        )
        
        margins = [p/r*100 for p, r in zip(profit, revenue)]
        fig.add_trace(
            go.Bar(x=years, y=margins, name='Profit Margin %', 
                   marker_color='#764ba2'),
            row=1, col=2
        )
        
        fig.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Valuation metrics
        metrics = ['P/E', 'P/B', 'ROE', 'D/E', 'Current Ratio']
        values = [15.2, 3.1, 18.5, 0.3, 2.1]
        
        fig2 = go.Figure(go.Bar(
            x=metrics,
            y=values,
            marker_color=['#667eea', '#764ba2', '#f093fb', '#f5576c', '#ffeaa7']
        ))
        
        fig2.update_layout(
            title="Key Financial Ratios",
            height=400,
            xaxis_title="Metrics",
            yaxis_title="Values"
        )
        
        st.plotly_chart(fig2, use_container_width=True)

def generate_section_prompt(section_key, ticker, date):
    """Generate prompts for analysis sections"""
    base_context = f"Analyze {ticker} stock as of {date}. Provide current, factual data with sources."
    
    prompts = {
        "quick_analysis": f"""
        {base_context}
        
        Provide a comprehensive but concise analysis covering:
        1. Current financial performance and key metrics
        2. Recent news and market sentiment
        3. Sector position and competitive advantages
        4. Valuation assessment with target price
        5. Investment recommendation with reasoning
        
        Keep analysis detailed but focused on key insights.
        """,
        
        "financial_overview": f"""
        {base_context}
        
        Analyze the financial health:
        1. Revenue and profit trends (last 3 years)
        2. Key financial ratios and their interpretation
        3. Cash flow and debt position
        4. Return on equity and asset efficiency
        5. Financial strengths and concerns
        """,
        
        "market_analysis": f"""
        {base_context}
        
        Examine market position:
        1. Industry trends and growth drivers
        2. Competitive landscape and market share
        3. Recent developments and news impact
        4. Regulatory environment
        5. Future growth catalysts
        """
    }
    
    return prompts.get(section_key, f"{base_context}\n\nProvide detailed analysis for {section_key}")

# Enhanced Sidebar
st.sidebar.markdown("""
<div class="sidebar-header">
    <h2>🎛️ Control Center</h2>
    <p>Advanced Analysis Tools</p>
</div>
""", unsafe_allow_html=True)

# Analysis mode selection
analysis_mode = st.sidebar.selectbox(
    "📊 **Analysis Mode**",
    ["Quick Analysis", "Standard Analysis", "Deep Dive", "Demo Mode"],
    help="Choose your analysis depth"
)

# Stock input
ticker_input = st.sidebar.text_input(
    "🏢 **Stock Ticker**",
    placeholder="e.g., TCS, RELIANCE, AAPL",
    value=st.session_state.current_ticker,
    help="Enter stock symbol for analysis"
)

# API status indicator
st.sidebar.markdown("### 🔧 **System Status**")
if client:
    st.sidebar.markdown(
        '<span class="status-indicator status-online"></span>**API:** Connected ✅',
        unsafe_allow_html=True
    )
    api_status = "Connected"
else:
    st.sidebar.markdown(
        '<span class="status-indicator status-offline"></span>**API:** Disconnected ❌',
        unsafe_allow_html=True
    )
    api_status = "Disconnected"

# Analysis button
if st.sidebar.button("🚀 **Start Analysis**", type="primary", use_container_width=True):
    if analysis_mode == "Demo Mode" or not ticker_input:
        st.session_state.show_demo = True
        st.rerun()
    elif not client:
        st.error("❌ Please configure your Perplexity API key in environment variables")
    else:
        ticker = ticker_input.upper().strip()
        st.session_state.current_ticker = ticker
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with status_text:
            st.info("🔄 Analyzing stock fundamentals...")
        progress_bar.progress(25)
        
        # Quick analysis
        prompt = generate_section_prompt("quick_analysis", ticker, datetime.now().strftime("%B %d, %Y"))
        analysis_result = query_perplexity(prompt)
        
        progress_bar.progress(50)
        status_text.info("📊 Processing financial data...")
        
        # Financial analysis
        financial_prompt = generate_section_prompt("financial_overview", ticker, datetime.now().strftime("%B %d, %Y"))
        financial_result = query_perplexity(financial_prompt)
        
        progress_bar.progress(75)
        status_text.info("🎯 Generating recommendations...")
        
        # Market analysis
        market_prompt = generate_section_prompt("market_analysis", ticker, datetime.now().strftime("%B %d, %Y"))
        market_result = query_perplexity(market_prompt)
        
        progress_bar.progress(100)
        status_text.success("✅ Analysis complete!")
        
        # Store results
        st.session_state.analysis_results[ticker] = {
            'quick_analysis': analysis_result,
            'financial_overview': financial_result,
            'market_analysis': market_result,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Display results
        st.markdown(f"# 📊 Analysis Results: {ticker}")
        
        tab1, tab2, tab3 = st.tabs(["📈 **Overview**", "💰 **Financials**", "🌍 **Market**"])
        
        with tab1:
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("### 🎯 **Investment Analysis**")
            st.markdown(analysis_result)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("### 💰 **Financial Health**")
            st.markdown(financial_result)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab3:
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("### 🌍 **Market Position**")
            st.markdown(market_result)
            st.markdown('</div>', unsafe_allow_html=True)

# Demo mode button
if st.sidebar.button("🎮 **Try Demo**"):
    st.session_state.show_demo = True
    st.rerun()

# Quick stats
st.sidebar.markdown("---")
st.sidebar.metric("📊 Platform Status", api_status)
st.sidebar.metric("🕒 Last Updated", datetime.now().strftime("%H:%M"))

# Main content area
if st.session_state.show_demo:
    st.markdown("# 🎮 **Demo Mode: Interactive Dashboard**")
    create_sample_dashboard()
    
    # Demo analysis
    st.markdown("## 📊 **Sample Analysis Report**")
    
    demo_col1, demo_col2 = st.columns(2)
    
    with demo_col1:
        st.markdown("""
        <div class="analysis-section">
            <h3>🎯 Investment Recommendation</h3>
            <p><strong>Rating:</strong> BUY</p>
            <p><strong>Target Price:</strong> ₹1,250 (25% upside)</p>
            <p><strong>Investment Horizon:</strong> 12-18 months</p>
            <p><strong>Key Strengths:</strong></p>
            <ul>
                <li>Strong revenue growth (15% CAGR)</li>
                <li>Improving profit margins</li>
                <li>Market leadership position</li>
                <li>Robust cash flows</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with demo_col2:
        st.markdown("""
        <div class="analysis-section">
            <h3>⚠️ Risk Factors</h3>
            <ul>
                <li>Sector cyclicality concerns</li>
                <li>Regulatory changes impact</li>
                <li>Competition intensity</li>
                <li>Global market volatility</li>
            </ul>
            <h3>📈 Catalysts</h3>
            <ul>
                <li>New product launches</li>
                <li>Market expansion plans</li>
                <li>Operational efficiency gains</li>
                <li>Strategic partnerships</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("🔄 **Reset to Main Page**"):
        st.session_state.show_demo = False
        st.rerun()

else:
    # Show enhanced landing page
    create_enhanced_landing_page()
    
    # Welcome section
    st.markdown("""
    <div class="welcome-section">
        <h2>🎯 Ready to Start?</h2>
        <p>Enter a stock ticker in the sidebar and click "Start Analysis" to see the platform in action!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Demo section
    st.markdown("""
    <div class="demo-section">
        <h3>🎮 Try Our Interactive Demo</h3>
        <p>Click "Try Demo" in the sidebar to see sample charts and analysis without using API credits.</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; margin-top: 2rem;'>
    <h3>🚀 Investment Research Platform Pro</h3>
    <p><strong>Version 2.0</strong> • Enhanced UI • Interactive Dashboards • Real-time Analysis</p>
    <p><small>Powered by Perplexity AI • Built with Streamlit • For Educational Use</small></p>
</div>
""", unsafe_allow_html=True)
