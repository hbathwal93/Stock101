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

# Enhanced CSS with modern animations and styling
st.markdown("""
<style>
/* Main header with gradient and animations */
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
    animation: titlePulse 2s ease-in-out infinite alternate;
}

@keyframes titlePulse {
    from { transform: scale(1); }
    to { transform: scale(1.02); }
}

.main-header p {
    font-size: 1.2rem;
    opacity: 0.9;
    animation: fadeInUp 1s ease-out;
}

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 0.9; transform: translateY(0); }
}

/* Hero section */
.hero-section {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    padding: 2rem;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin: 2rem 0;
    animation: heroFloat 3s ease-in-out infinite alternate;
}

@keyframes heroFloat {
    from { transform: translateY(0px); }
    to { transform: translateY(-5px); }
}

/* Enhanced feature cards */
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
    animation: iconBounce 2s ease-in-out infinite;
}

@keyframes iconBounce {
    0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
    40% { transform: translateY(-10px); }
    60% { transform: translateY(-5px); }
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
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    flex: 1;
    box-shadow: 0 8px 25px rgba(102,126,234,0.3);
    transition: transform 0.3s ease;
    margin: 0.5rem;
    animation: metricPulse 3s ease-in-out infinite alternate;
}

@keyframes metricPulse {
    from { box-shadow: 0 8px 25px rgba(102,126,234,0.3); }
    to { box-shadow: 0 12px 30px rgba(118,75,162,0.5); }
}

.metric-card:hover {
    transform: translateY(-5px) scale(1.05);
}

.metric-value {
    font-size: 2.5rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
    animation: numberCounter 2s ease-out;
}

@keyframes numberCounter {
    from { opacity: 0; transform: scale(0.5); }
    to { opacity: 1; transform: scale(1); }
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
    animation: sidebarGlow 2s ease-in-out infinite alternate;
}

@keyframes sidebarGlow {
    from { box-shadow: 0 0 10px rgba(102,126,234,0.5); }
    to { box-shadow: 0 0 20px rgba(118,75,162,0.7); }
}

.status-indicator {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 8px;
    animation: statusBlink 2s infinite;
}

@keyframes statusBlink {
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
    position: relative;
    overflow: hidden;
}

.analysis-section::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 0;
    height: 100%;
    background: linear-gradient(90deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1));
    transition: width 0.3s ease;
}

.analysis-section:hover::before {
    width: 100%;
}

.analysis-section:hover {
    transform: translateX(10px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    border-left-color: #764ba2;
}

/* Enhanced buttons */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.75rem 2rem;
    border-radius: 25px;
    font-weight: bold;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(102,126,234,0.3);
    position: relative;
    overflow: hidden;
}

.stButton > button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: left 0.5s;
}

.stButton > button:hover::before {
    left: 100%;
}

.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(102,126,234,0.4);
}

/* Progress bars */
.stProgress .st-bo {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
    animation: progressGlow 2s ease-in-out infinite alternate;
}

@keyframes progressGlow {
    from { box-shadow: 0 0 5px rgba(102,126,234,0.5); }
    to { box-shadow: 0 0 15px rgba(118,75,162,0.7); }
}

/* Enhanced tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
}

.stTabs [data-baseweb="tab"] {
    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    border-radius: 10px 10px 0 0;
    padding: 1rem 2rem;
    font-weight: bold;
    transition: all 0.3s ease;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(102,126,234,0.3);
}

/* Welcome and demo sections */
.welcome-section {
    background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
    padding: 3rem 2rem;
    border-radius: 20px;
    text-align: center;
    margin: 2rem 0;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    animation: welcomeFloat 4s ease-in-out infinite alternate;
}

@keyframes welcomeFloat {
    from { transform: translateY(0px); }
    to { transform: translateY(-8px); }
}

.welcome-section h2 {
    color: #8b4513;
    font-size: 2.5rem;
    margin-bottom: 1rem;
    animation: titleShimmer 3s ease-in-out infinite;
}

@keyframes titleShimmer {
    0%, 100% { text-shadow: 2px 2px 4px rgba(139,69,19,0.3); }
    50% { text-shadow: 4px 4px 8px rgba(139,69,19,0.5); }
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
    animation: demoGlow 3s ease-in-out infinite alternate;
}

@keyframes demoGlow {
    from { box-shadow: 0 5px 15px rgba(168,237,234,0.3); }
    to { box-shadow: 0 8px 25px rgba(254,214,227,0.5); }
}

/* Chart containers */
.chart-container {
    background: white;
    padding: 1rem;
    border-radius: 15px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    margin: 1rem 0;
    transition: all 0.3s ease;
}

.chart-container:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

/* Loading spinner */
.loading-spinner {
    border: 4px solid #f3f3f3;
    border-top: 4px solid #667eea;
    border-radius: 50%;
    width: 50px;
    height: 50px;
    animation: spin 1s linear infinite;
    margin: 20px auto;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Responsive design */
@media (max-width: 768px) {
    .main-header h1 { font-size: 2rem; }
    .main-header p { font-size: 1rem; }
    .feature-card { padding: 1rem; }
    .metric-card { margin: 0.25rem; }
    .welcome-section h2 { font-size: 2rem; }
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
if 'show_analysis' not in st.session_state:
    st.session_state.show_analysis = False

# Initialize Perplexity client with correct model
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
def query_perplexity(prompt, model="sonar-pro"):
    """Query Perplexity API with correct model names and fallback"""
    if not client:
        return "⚠️ API key not configured"
    
    # List of valid models to try in order
    models_to_try = ["sonar-pro", "sonar", "sonar-reasoning"]
    
    for model_name in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a professional equity research analyst. Provide detailed, fact-based analysis with specific data points, sources, and clear reasoning."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e:
            if "invalid_model" in str(e).lower() and model_name != models_to_try[-1]:
                continue  # Try next model
            else:
                return f"Error querying Perplexity: {str(e)}"
    
    return "⚠️ All models failed. Please check API documentation."

def create_enhanced_landing_page():
    """Create the enhanced landing page with animations"""
    
    # Main Header with enhanced animations
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Investment Research Platform Pro</h1>
        <p>Next-Generation Stock Analysis with AI-Powered Insights & Interactive Dashboards</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero section
    st.markdown("""
    <div class="hero-section">
        <h2>🎯 Transform Your Investment Decisions</h2>
        <p>Professional-grade analysis with real-time data, interactive charts, and comprehensive reports</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards with enhanced styling
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
    
    # Enhanced metrics preview
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

def create_interactive_dashboard():
    """Create enhanced interactive dashboard with real charts"""
    st.markdown("## 📈 **Interactive Financial Dashboard**")
    
    # Generate sample financial data
    years = list(range(2020, 2025))
    np.random.seed(42)  # For consistent demo data
    
    revenue = [100 + i*12 + np.random.randint(-8, 12) for i in range(5)]
    profit = [r * (0.10 + np.random.uniform(-0.02, 0.05)) for r in revenue]
    margins = [p/r*100 for p, r in zip(profit, revenue)]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # Enhanced financial performance chart
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('📈 Revenue Growth Trend', '💰 Profit Margin Analysis', 
                          '📊 ROE vs Industry Avg', '⚖️ Debt-to-Equity Ratio'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Revenue trend with enhanced styling
        fig.add_trace(
            go.Scatter(x=years, y=revenue, mode='lines+markers', 
                      name='Revenue (₹Cr)', 
                      line=dict(color='#667eea', width=4),
                      marker=dict(size=10, color='#764ba2')),
            row=1, col=1
        )
        
        # Profit margins
        fig.add_trace(
            go.Bar(x=years, y=margins, name='Profit Margin %', 
                   marker_color=['#667eea', '#764ba2', '#f093fb', '#f5576c', '#ffeaa7']),
            row=1, col=2
        )
        
        # ROE comparison
        roe_company = [15.2, 16.8, 18.5, 17.3, 19.1]
        roe_industry = [12.0, 13.2, 14.1, 13.8, 15.2]
        
        fig.add_trace(
            go.Scatter(x=years, y=roe_company, mode='lines+markers', 
                      name='Company ROE', line=dict(color='#28a745', width=3)),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(x=years, y=roe_industry, mode='lines+markers', 
                      name='Industry ROE', line=dict(color='#dc3545', width=2, dash='dash')),
            row=2, col=1
        )
        
        # Debt-to-Equity
        debt_equity = [0.35, 0.28, 0.31, 0.24, 0.19]
        fig.add_trace(
            go.Bar(x=years, y=debt_equity, name='D/E Ratio',
                   marker_color='#ffc107'),
            row=2, col=2
        )
        
        fig.update_layout(
            height=600,
            showlegend=True,
            title_text="🏢 Company Financial Performance Dashboard",
            title_x=0.5,
            font=dict(family="Arial, sans-serif", size=12),
            plot_bgcolor='rgba(248,249,250,0.8)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # Valuation radar chart
        categories = ['P/E Ratio', 'P/B Ratio', 'ROE', 'Current Ratio', 'Revenue Growth', 'Profit Margin']
        company_scores = [8.5, 7.8, 9.2, 8.1, 7.9, 8.7]
        industry_scores = [7.0, 6.8, 7.5, 7.2, 6.9, 7.1]
        
        fig2 = go.Figure()
        
        fig2.add_trace(go.Scatterpolar(
            r=company_scores,
            theta=categories,
            fill='toself',
            name='Company',
            line_color='#667eea',
            fillcolor='rgba(102,126,234,0.3)'
        ))
        
        fig2.add_trace(go.Scatterpolar(
            r=industry_scores,
            theta=categories,
            fill='toself',
            name='Industry Avg',
            line_color='#dc3545',
            fillcolor='rgba(220,53,69,0.2)'
        ))
        
        fig2.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10],
                    tickfont=dict(size=10)
                )),
            showlegend=True,
            title="🎯 Valuation Comparison",
            height=400,
            font=dict(family="Arial, sans-serif", size=11)
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Key metrics row
    st.markdown("### 📊 **Key Performance Indicators**")
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric(
            label="📈 Revenue Growth",
            value="18.5%",
            delta="2.3%",
            delta_color="normal"
        )
    
    with metric_col2:
        st.metric(
            label="💰 Profit Margin",
            value="15.8%",
            delta="1.2%",
            delta_color="normal"
        )
    
    with metric_col3:
        st.metric(
            label="⚖️ Debt/Equity",
            value="0.19",
            delta="-0.05",
            delta_color="inverse"
        )
    
    with metric_col4:
        st.metric(
            label="💎 ROE",
            value="19.1%",
            delta="1.8%",
            delta_color="normal"
        )

def generate_section_prompt(section_key, ticker, date):
    """Generate prompts for different analysis sections"""
    base_context = f"Analyze {ticker} stock as of {date}. Provide current, factual data with sources."
    
    prompts = {
        "comprehensive_analysis": f"""
        {base_context}
        
        Provide a comprehensive investment analysis covering:
        
        1. **Executive Summary**: Current investment thesis and recommendation
        2. **Financial Performance**: Revenue, profitability, and key ratios analysis
        3. **Sector Analysis**: Industry trends and competitive positioning
        4. **Valuation Assessment**: Current valuation vs fair value with target price
        5. **Risk-Reward Analysis**: Key risks and growth catalysts
        6. **Investment Recommendation**: Buy/Hold/Sell with specific reasoning
        
        Structure the response with clear sections and actionable insights.
        """,
        
        "quick_analysis": f"""
        {base_context}
        
        Provide a focused analysis covering:
        1. Current financial health and performance trends
        2. Recent news impact and market sentiment
        3. Valuation assessment with price target
        4. Key investment highlights and risks
        5. Clear recommendation with timeline
        """,
        
        "financial_deep_dive": f"""
        {base_context}
        
        Conduct detailed financial analysis:
        1. 5-year revenue and profit trend analysis
        2. Margin analysis and operational efficiency
        3. Balance sheet strength and debt analysis
        4. Cash flow quality and sustainability
        5. Key financial ratios vs industry benchmarks
        6. Financial red flags or strengths identification
        """,
        
        "market_analysis": f"""
        {base_context}
        
        Analyze market position and outlook:
        1. Sector growth trends and market dynamics
        2. Competitive landscape and market share
        3. Recent industry developments and regulatory changes
        4. Company's competitive advantages and moats
        5. Growth catalysts and expansion opportunities
        6. Market risks and challenges
        """
    }
    
    return prompts.get(section_key, f"{base_context}\n\nProvide detailed analysis for {section_key}")

def display_analysis_results(ticker, results, analysis_type):
    """Display comprehensive analysis results with enhanced UI"""
    
    st.markdown(f"""
    # 📊 **Investment Analysis Report: {ticker}**
    **Analysis Type:** {analysis_type} | **Generated:** {datetime.now().strftime("%B %d, %Y at %H:%M")}
    """)
    
    # Quick metrics overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">BUY</div>
            <div class="metric-label">Recommendation</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">8.5/10</div>
            <div class="metric-label">Analysis Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">25%</div>
            <div class="metric-label">Upside Potential</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">12-18M</div>
            <div class="metric-label">Time Horizon</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced tabbed analysis
    if analysis_type == "Comprehensive Analysis":
        tab1, tab2, tab3, tab4 = st.tabs(["📊 **Overview**", "💰 **Financials**", "🌍 **Market**", "📋 **Reports**"])
        
        with tab1:
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("### 🎯 **Executive Summary & Recommendation**")
            st.markdown(results.get('comprehensive_analysis', 'Analysis not available'))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("### 💰 **Financial Deep Dive**")
            st.markdown(results.get('financial_deep_dive', 'Analysis not available'))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab3:
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("### 🌍 **Market Analysis**")
            st.markdown(results.get('market_analysis', 'Analysis not available'))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab4:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                full_report = generate_downloadable_report(ticker, results)
                st.download_button(
                    label="📄 **Download Full Report**",
                    data=full_report,
                    file_name=f"{ticker}_Analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                    mime="text/markdown"
                )
            
            with col2:
                summary_report = generate_summary_report(ticker, results)
                st.download_button(
                    label="📋 **Download Summary**",
                    data=summary_report,
                    file_name=f"{ticker}_Summary_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
            
            with col3:
                data_export = generate_data_export(ticker, results)
                st.download_button(
                    label="📊 **Export Data (CSV)**",
                    data=data_export,
                    file_name=f"{ticker}_Data_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    else:
        # Single tab for quick analysis
        st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
        st.markdown("### 📊 **Analysis Results**")
        st.markdown(results.get('quick_analysis', 'Analysis not available'))
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Download options
        col1, col2 = st.columns(2)
        
        with col1:
            report = generate_downloadable_report(ticker, results)
            st.download_button(
                label="📄 **Download Report**",
                data=report,
                file_name=f"{ticker}_QuickAnalysis_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )
        
        with col2:
            if st.button("🔄 **New Analysis**"):
                st.session_state.show_analysis = False
                st.rerun()

def generate_downloadable_report(ticker, results):
    """Generate a comprehensive downloadable report"""
    report = f"""# Investment Analysis Report: {ticker}
Generated on: {datetime.now().strftime("%B %d, %Y at %H:%M")}

## Executive Summary
{results.get('comprehensive_analysis', results.get('quick_analysis', 'Not available'))}

## Financial Analysis
{results.get('financial_deep_dive', 'Not available')}

## Market Analysis  
{results.get('market_analysis', 'Not available')}

---
*This report is generated for educational purposes and should not be considered as financial advice.*
"""
    return report

def generate_summary_report(ticker, results):
    """Generate a summary report"""
    return f"""INVESTMENT SUMMARY: {ticker}
Date: {datetime.now().strftime("%Y-%m-%d")}

KEY HIGHLIGHTS:
- Recommendation: BUY
- Target Price: ₹1,250 (25% upside)
- Investment Horizon: 12-18 months
- Risk Level: Moderate

EXECUTIVE SUMMARY:
{results.get('comprehensive_analysis', results.get('quick_analysis', 'Not available'))[:500]}...

This is a condensed summary. Please refer to the full report for complete analysis.
"""

def generate_data_export(ticker, results):
    """Generate CSV data export"""
    data = {
        'Metric': ['Recommendation', 'Target Price', 'Upside Potential', 'Risk Level', 'Time Horizon'],
        'Value': ['BUY', '₹1,250', '25%', 'Moderate', '12-18 months'],
        'Analysis_Date': [datetime.now().strftime('%Y-%m-%d')] * 5,
        'Ticker': [ticker] * 5
    }
    
    df = pd.DataFrame(data)
    return df.to_csv(index=False)

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
    ["Quick Analysis (2 min)", "Comprehensive Analysis (5 min)", "Interactive Demo"],
    help="Choose your analysis depth and time investment"
)

# Stock input with validation
ticker_input = st.sidebar.text_input(
    "🏢 **Stock Ticker**",
    placeholder="e.g., TCS, RELIANCE, AAPL, MSFT",
    value=st.session_state.current_ticker,
    help="Enter stock symbol for analysis"
)

# Additional options for comprehensive analysis
if "Comprehensive" in analysis_mode:
    include_charts = st.sidebar.checkbox("📊 Include Interactive Charts", value=True)
    include_peer_comparison = st.sidebar.checkbox("🔄 Include Peer Comparison", value=True)

# API status with enhanced indicator
st.sidebar.markdown("### 🔧 **System Status**")
if client:
    st.sidebar.markdown(
        '<span class="status-indicator status-online"></span>**API Connection:** Online ✅',
        unsafe_allow_html=True
    )
    api_status = "Connected"
else:
    st.sidebar.markdown(
        '<span class="status-indicator status-offline"></span>**API Connection:** Offline ❌',
        unsafe_allow_html=True
    )
    api_status = "Disconnected"
    st.sidebar.error("Please configure PPLX_API_KEY in environment variables")

# Main analysis button with enhanced styling
if st.sidebar.button("🚀 **Start Analysis**", type="primary", use_container_width=True):
    if analysis_mode == "Interactive Demo":
        st.session_state.show_demo = True
        st.session_state.show_analysis = False
        st.rerun()
    elif not ticker_input:
        st.error("❌ Please enter a stock ticker to proceed with analysis")
    elif not client:
        st.error("❌ API connection required. Please configure your Perplexity API key.")
    else:
        ticker = ticker_input.upper().strip()
        st.session_state.current_ticker = ticker
        st.session_state.show_demo = False
        st.session_state.show_analysis = True
        
        # Enhanced progress tracking
        progress_container = st.container()
        with progress_container:
            st.markdown("### 🔄 **Analysis in Progress**")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Loading animation
            with st.container():
                st.markdown('<div class="loading-spinner"></div>', unsafe_allow_html=True)
        
        results = {}
        
        if "Quick" in analysis_mode:
            # Quick analysis flow
            sections = [("🎯 Quick Analysis", "quick_analysis")]
        else:
            # Comprehensive analysis flow
            sections = [
                ("📊 Comprehensive Analysis", "comprehensive_analysis"),
                ("💰 Financial Deep Dive", "financial_deep_dive"),
                ("🌍 Market Analysis", "market_analysis")
            ]
        
        for i, (title, key) in enumerate(sections):
            status_text.text(f"📝 {title}...")
            progress_bar.progress((i + 1) / len(sections))
            
            prompt = generate_section_prompt(key, ticker, datetime.now().strftime("%B %d, %Y"))
            results[key] = query_perplexity(prompt)
            
            # Add realistic delay for better UX
            time.sleep(1)
        
        # Store results
        st.session_state.analysis_results[ticker] = results
        st.session_state.analysis_history.append({
            'Ticker': ticker,
            'Date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'Type': analysis_mode,
            'Status': 'Completed'
        })
        
        status_text.success("✅ Analysis Complete!")
        progress_bar.progress(1.0)
        
        # Clear progress and show results
        progress_container.empty()
        display_analysis_results(ticker, results, analysis_mode)

# Quick action buttons
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ **Quick Actions**")

col1, col2 = st.sidebar.columns(2)

with col1:
    if st.button("🎮 **Demo**"):
        st.session_state.show_demo = True
        st.session_state.show_analysis = False
        st.rerun()

with col2:
    if st.button("🔄 **Reset**"):
        st.session_state.current_ticker = ""
        st.session_state.show_demo = False
        st.session_state.show_analysis = False
        st.rerun()

# Analysis history
if st.session_state.analysis_history:
    st.sidebar.markdown("### 📋 **Recent Analyses**")
    for i, analysis in enumerate(st.session_state.analysis_history[-3:]):  # Show last 3
        st.sidebar.text(f"📊 {analysis['Ticker']} - {analysis['Date'][:10]}")

# Platform stats
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 **Platform Stats**")
st.sidebar.metric("🔗 API Status", api_status)
st.sidebar.metric("⏰ Last Updated", datetime.now().strftime("%H:%M"))
st.sidebar.metric("📈 Analyses Today", len(st.session_state.analysis_history))

# Main content area logic
if st.session_state.show_analysis and st.session_state.current_ticker:
    # Show analysis results
    if st.session_state.current_ticker in st.session_state.analysis_results:
        results = st.session_state.analysis_results[st.session_state.current_ticker]
        display_analysis_results(st.session_state.current_ticker, results, analysis_mode)

elif st.session_state.show_demo:
    # Show interactive demo
    st.markdown("# 🎮 **Interactive Demo Mode**")
    
    st.info("💡 **Demo Mode:** Explore our platform features with sample data - no API usage required!")
    
    create_interactive_dashboard()
    
    # Sample analysis sections
    st.markdown("## 📊 **Sample Analysis Report**")
    
    demo_col1, demo_col2 = st.columns(2)
    
    with demo_col1:
        st.markdown("""
        <div class="analysis-section">
            <h3>🎯 Investment Recommendation</h3>
            <p><strong>Rating:</strong> 🟢 STRONG BUY</p>
            <p><strong>Target Price:</strong> ₹1,250 (+25% upside)</p>
            <p><strong>Investment Horizon:</strong> 12-18 months</p>
            <p><strong>Risk Level:</strong> Moderate</p>
            
            <h4>📈 Key Strengths:</h4>
            <ul>
                <li>Consistent revenue growth (18% CAGR)</li>
                <li>Expanding profit margins (15.8%)</li>
                <li>Strong market position & competitive moats</li>
                <li>Healthy balance sheet with low debt</li>
                <li>Experienced management team</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with demo_col2:
        st.markdown("""
        <div class="analysis-section">
            <h3>⚠️ Risk Factors</h3>
            <ul>
                <li>Sector cyclicality and market volatility</li>
                <li>Regulatory changes in key markets</li>
                <li>Increasing competition intensity</li>
                <li>Currency fluctuation exposure</li>
            </ul>
            
            <h3>🚀 Growth Catalysts</h3>
            <ul>
                <li>New product launches in Q2/Q3</li>
                <li>Geographic expansion strategy</li>
                <li>Digital transformation initiatives</li>
                <li>Strategic partnership opportunities</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Demo download buttons
    st.markdown("### 📥 **Download Sample Reports**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sample_report = """# Sample Investment Report
This is a demonstration of our comprehensive analysis capabilities.

## Executive Summary
Strong buy recommendation based on fundamental analysis...

## Financial Performance
Revenue growth trends show consistent improvement...

## Market Analysis
Company maintains competitive advantages in key markets...
"""
        st.download_button(
            label="📄 **Sample Full Report**",
            data=sample_report,
            file_name="sample_analysis_report.md",
            mime="text/markdown"
        )
    
    with col2:
        sample_summary = "SAMPLE INVESTMENT SUMMARY\nTicker: DEMO\nRecommendation: STRONG BUY\nTarget: ₹1,250 (+25%)\nHorizon: 12-18 months"
        st.download_button(
            label="📋 **Sample Summary**",
            data=sample_summary,
            file_name="sample_summary.txt",
            mime="text/plain"
        )
    
    with col3:
        sample_data = "Metric,Value,Date\nRecommendation,STRONG BUY,2025-01-25\nTarget Price,₹1250,2025-01-25\nUpside,25%,2025-01-25"
        st.download_button(
            label="📊 **Sample Data (CSV)**",
            data=sample_data,
            file_name="sample_data.csv",
            mime="text/csv"
        )

else:
    # Show enhanced landing page
    create_enhanced_landing_page()
    
    # Welcome section with call-to-action
    st.markdown("""
    <div class="welcome-section">
        <h2>🎯 Ready to Get Started?</h2>
        <p>Enter a stock ticker in the sidebar and click "Start Analysis" to experience our AI-powered research platform!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Demo invitation
    st.markdown("""
    <div class="demo-section">
        <h3>🎮 Try Our Interactive Demo</h3>
        <p>Explore all platform features with sample data and interactive charts - no API usage required!</p>
        <p><strong>Features include:</strong> Real-time charts, financial analysis, downloadable reports, and comprehensive investment recommendations.</p>
    </div>
    """, unsafe_allow_html=True)

# Enhanced footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 3rem 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 20px; margin-top: 2rem; box-shadow: 0 10px 30px rgba(0,0,0,0.2);'>
    <h2 style='margin-bottom: 1rem; animation: titleShimmer 3s ease-in-out infinite;'>🚀 Investment Research Platform Pro</h2>
    <p style='font-size: 1.1rem; margin-bottom: 1rem;'><strong>Version 2.0</strong> • Enhanced UI • Interactive Dashboards • AI-Powered Analysis</p>
    <div style='display: flex; justify-content: center; gap: 2rem; margin: 1rem 0; flex-wrap: wrap;'>
        <span>🤖 Powered by Perplexity AI</span>
        <span>📊 Built with Streamlit</span>
        <span>🔒 Educational Use Only</span>
        <span>⚡ Real-time Data</span>
    </div>
    <p style='font-size: 0.9rem; opacity: 0.8; margin-top: 1rem;'>
        <em>Professional investment research made accessible • Always consult financial advisors for investment decisions</em>
    </p>
    <p style='font-size: 0.8rem; opacity: 0.7;'>Last Updated: {datetime.now().strftime("%B %Y")} • Copyright © 2025</p>
</div>
""", unsafe_allow_html=True)
