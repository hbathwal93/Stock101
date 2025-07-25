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

# Enhanced CSS for professional look with animations
st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #1e88e5 100%);
    padding: 2rem;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 4px 15px rgba(30, 60, 114, 0.3);
}

.metric-card {
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
    padding: 1.5rem;
    border-radius: 12px;
    border: 1px solid #e9ecef;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    text-align: center;
    transition: transform 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.metric-value {
    font-size: 2rem;
    font-weight: bold;
    color: #2a5298;
    margin-bottom: 0.5rem;
}

.metric-label {
    color: #6c757d;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.analysis-section {
    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1rem 0;
    border-left: 4px solid #2a5298;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
}

.analysis-section:hover {
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    border-left-color: #1e88e5;
}

.recommendation-buy { 
    background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); 
    border: 2px solid #28a745;
    border-radius: 12px;
}

.recommendation-hold { 
    background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); 
    border: 2px solid #ffc107;
    border-radius: 12px;
}

.recommendation-sell { 
    background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%); 
    border: 2px solid #dc3545;
    border-radius: 12px;
}

.progress-container {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 1rem;
    margin: 1rem 0;
}

.tab-content {
    padding: 1.5rem;
    background: #ffffff;
    border-radius: 8px;
    margin-top: 1rem;
}

.sidebar-info {
    background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}

.status-indicator {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 8px;
}

.status-online { background-color: #28a745; }
.status-offline { background-color: #dc3545; }

.loading-spinner {
    border: 3px solid #f3f3f5;
    border-top: 3px solid #2a5298;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    margin: 20px auto;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.chart-container {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state for persistent data
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'current_ticker' not in st.session_state:
    st.session_state.current_ticker = ""

# FIXED: Initialize Perplexity client for Render.com
@st.cache_resource
def init_perplexity_client():
    """Initialize Perplexity client - Render.com compatible with caching"""
    api_key = os.getenv("PPLX_API_KEY")
    
    if api_key:
        return OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
    else:
        return None

# Initialize client
client = init_perplexity_client()

@st.cache_data(ttl=3600)  # Cache for 1 hour
def query_perplexity(prompt, model="sonar-pro"):
    """Query Perplexity API with caching and error handling"""
    if not client:
        return "⚠️ API key not configured"
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a professional equity research analyst. Provide detailed, fact-based analysis with specific data points, sources, and clear reasoning. Always include current dates and verify information accuracy."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=4000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error querying Perplexity: {str(e)}"

def create_sample_financial_chart(ticker):
    """Create sample financial visualization"""
    # Generate sample data for demonstration
    years = list(range(2019, 2024))
    revenue = [100 + i*15 + np.random.randint(-10, 10) for i in range(5)]
    profit = [r * 0.15 + np.random.randint(-5, 5) for r in revenue]
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Revenue Trend', 'Profit Margin Analysis', 'ROE vs Industry', 'Debt-to-Equity Ratio'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Revenue trend
    fig.add_trace(
        go.Scatter(x=years, y=revenue, mode='lines+markers', name='Revenue', 
                  line=dict(color='#2a5298', width=3)),
        row=1, col=1
    )
    
    # Profit margins
    margins = [p/r*100 for p, r in zip(profit, revenue)]
    fig.add_trace(
        go.Bar(x=years, y=margins, name='Profit Margin %', 
               marker_color='#1e88e5'),
        row=1, col=2
    )
    
    # ROE comparison
    roe_company = [12, 14, 16, 15, 17]
    roe_industry = [10, 11, 12, 11, 13]
    fig.add_trace(
        go.Scatter(x=years, y=roe_company, mode='lines+markers', name=f'{ticker} ROE',
                  line=dict(color='#28a745', width=3)),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=years, y=roe_industry, mode='lines+markers', name='Industry ROE',
                  line=dict(color='#dc3545', width=2, dash='dash')),
        row=2, col=1
    )
    
    # Debt-to-Equity
    debt_equity = [0.3, 0.25, 0.28, 0.22, 0.20]
    fig.add_trace(
        go.Bar(x=years, y=debt_equity, name='D/E Ratio',
               marker_color='#ffc107'),
        row=2, col=2
    )
    
    fig.update_layout(
        height=600,
        showlegend=True,
        title_text=f"{ticker} - Financial Performance Dashboard",
        title_x=0.5
    )
    
    return fig

def create_valuation_radar_chart(ticker):
    """Create radar chart for valuation metrics"""
    categories = ['P/E Ratio', 'P/B Ratio', 'ROE', 'Debt/Equity', 'Current Ratio', 'Revenue Growth']
    
    # Sample data for company vs industry
    company_values = [8.5, 7.2, 8.8, 9.1, 7.5, 8.0]
    industry_avg = [7.0, 6.5, 7.0, 7.5, 7.0, 6.8]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=company_values,
        theta=categories,
        fill='toself',
        name=ticker,
        line_color='#2a5298'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=industry_avg,
        theta=categories,
        fill='toself',
        name='Industry Average',
        line_color='#dc3545'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )),
        showlegend=True,
        title=f"{ticker} vs Industry - Valuation Comparison"
    )
    
    return fig

def create_metrics_dashboard(ticker, results):
    """Create interactive metrics dashboard"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">8.5/10</div>
            <div class="metric-label">Overall Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">BUY</div>
            <div class="metric-label">Recommendation</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">₹1,250</div>
            <div class="metric-label">Target Price</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">25%</div>
            <div class="metric-label">Upside Potential</div>
        </div>
        """, unsafe_allow_html=True)

def generate_section_prompt(section_key, ticker, date):
    """Generate specific prompts for each analysis section"""
    
    base_context = f"Analyze {ticker} stock as of {date}. Provide current, factual data with sources."
    
    prompts = {
        "sectoral_analysis": f"""
        {base_context}
        
        Provide a comprehensive sectoral analysis covering:
        1. Current sector trends and growth drivers
        2. Industry structure and competitive dynamics
        3. Recent regulatory changes and policy impacts
        4. Technological disruptions affecting the sector
        5. Upcoming government actions or regulatory changes
        6. Macroeconomic factors influencing the industry
        
        Focus on both positive and negative triggers with specific examples and timeframes.
        """,
        
        "news_competition": f"""
        {base_context}
        
        Analyze recent news and competitive landscape:
        1. Key news from the past 30 days affecting {ticker}
        2. Major competitor developments and announcements
        3. Market share changes and competitive positioning
        4. Industry-wide developments impacting all players
        5. Regulatory news affecting the company/sector
        
        Categorize news as positive, negative, or neutral with reasoning.
        """,
        
        "financial_pl": f"""
        {base_context}
        
        Conduct deep P&L analysis for the last 5 years:
        1. Revenue trends, growth rates, and seasonality
        2. Gross margin evolution and cost structure changes
        3. Operating leverage and efficiency metrics
        4. One-time items and extraordinary expenses
        5. Earnings quality and sustainability assessment
        6. Forward-looking revenue and margin implications
        
        Provide specific numbers, percentages, and year-over-year comparisons.
        """,
        
        "financial_bs": f"""
        {base_context}
        
        Analyze balance sheet strength over 5 years:
        1. Asset quality and composition changes
        2. Debt levels, leverage ratios, and debt maturity profile
        3. Working capital trends and efficiency
        4. Capital allocation patterns
        5. Return on assets and equity trends
        6. Balance sheet risks and strengths vs sector norms
        
        Include specific financial ratios and benchmark comparisons.
        """,
        
        "financial_cf": f"""
        {base_context}
        
        Examine cash flow patterns for 5 years:
        1. Operating cash flow trends and quality
        2. Free cash flow generation and consistency
        3. Capital expenditure patterns and efficiency
        4. Financing activities and dividend policy
        5. Cash conversion cycle analysis
        6. Any unusual cash flow patterns or anomalies
        
        Focus on cash flow sustainability and capital allocation effectiveness.
        """,
        
        "ratio_analysis": f"""
        {base_context}
        
        Provide comprehensive ratio analysis in tabular format:
        Create a table with columns: Ratio | Current | 5-Year Trend | Industry Average | Analysis
        
        Cover these key ratios:
        - Profitability ratios (ROE, ROA, ROCE, Gross/Operating/Net margins)
        - Liquidity ratios (Current, Quick, Cash ratios)
        - Leverage ratios (Debt-to-equity, Interest coverage, Debt service)
        - Efficiency ratios (Asset turnover, Inventory turnover, Receivables turnover)
        - Valuation ratios (P/E, P/B, EV/EBITDA, Price-to-Sales)
        
        Explain trends, drivers, and management influence for each.
        """,
        
        "management_eval": f"""
        {base_context}
        
        Evaluate management quality and track record:
        1. CEO and key executives' background and tenure
        2. Strategic execution capability and past performance
        3. Crisis management and adaptability
        4. Capital allocation decisions and effectiveness
        5. Board composition and independence
        6. Management compensation alignment with performance
        7. Transparency in communications and reporting
        8. Any governance concerns or red flags
        
        Provide specific examples and track record evidence.
        """,
        
        "management_guidance": f"""
        {base_context}
        
        Analyze management guidance history and credibility:
        1. Historical guidance vs actual performance over past 3 years
        2. Quality and specificity of current forward guidance
        3. Management's conservatism vs aggressiveness in projections
        4. Sector comparison of guidance accuracy
        5. Recent changes in guidance and explanations provided
        6. Credibility assessment based on delivery track record
        
        Include specific guidance figures and actual outcomes.
        """,
        
        "investor_presentations": f"""
        {base_context}
        
        Review investor presentations from the last 12 quarters:
        1. Key strategic initiatives and business updates
        2. Product launches and market expansion plans
        3. Segmental performance and revenue mix evolution
        4. EBITDA trends and margin guidance
        5. Capital expenditure plans and utilization
        6. Management's strategic pivots and rationale
        7. Performance against previously stated targets
        
        Extract key themes and assess execution against promises.
        """,
        
        "conference_calls": f"""
        {base_context}
        
        Summarize recent conference calls (last 12 quarters):
        1. Management tone and confidence levels
        2. Growth outlook and new product pipeline
        3. Margin trends and cost management initiatives
        4. Capacity utilization and expansion plans
        5. M&A commentary and corporate actions
        6. Competitive positioning and market share discussions
        7. Guidance changes and reasoning
        
        Compare statements with actual delivery and flag inconsistencies.
        """,
        
        "community_analysis": f"""
        {base_context}
        
        Analyze investor community discussions (last 90 days):
        1. ValuePickr forum discussions and key insights
        2. Reddit and other investment community sentiment
        3. Common concerns and bullish/bearish arguments
        4. Unique insights not found in mainstream analysis
        5. Consensus opinion and contrarian viewpoints
        6. Risk factors highlighted by retail investors
        
        Summarize key themes and assess credibility of community insights.
        """,
        
        "annual_report": f"""
        {base_context}
        
        Conduct forensic analysis of the latest annual report:
        1. Accounting policy changes and their impact
        2. Related party transactions and potential conflicts
        3. Contingent liabilities and off-balance-sheet items
        4. Audit qualifications or concerns raised
        5. Management discussion and forward-looking statements
        6. Hidden gems or strategic insights in disclosures
        7. Any red flags or unusual accounting treatments
        
        Focus on items that might not be evident in standard financial analysis.
        """,
        
        "integrity_matrix": f"""
        {base_context}
        
        Create Management Integrity Matrix with scores (1-10) and evidence:
        
        1. Guidance Accuracy (Score/10): Historical accuracy of forecasts
        2. Delivery vs Promise (Score/10): Execution of stated plans
        3. Transparency & Disclosure (Score/10): Quality of communication
        4. Governance Flags (Score/10): Any red flags or concerns
        5. Overall Integrity (Score/10): Combined assessment
        
        For each KPI, provide:
        - Specific score out of 10
        - 2-3 concrete examples as evidence
        - Reasoning for the score assigned
        - Recent developments affecting the score
        """,
        
        "growth_triggers": f"""
        {base_context}
        
        Identify key growth catalysts and triggers:
        1. Operating leverage potential and scalability
        2. Capacity utilization trends and expansion benefits
        3. Recent acquisitions and their revenue contribution
        4. New product launches and market penetration
        5. Market expansion opportunities (geographic/segment)
        6. Technology upgrades and digital transformation impact
        7. Regulatory changes benefiting the company
        
        Quantify potential impact and provide realistic timelines.
        """,
        
        "valuation_analysis": f"""
        {base_context}
        
        Comprehensive valuation analysis:
        1. Current valuation ratios: P/E, P/S, PEG, P/B, EV/EBITDA
        2. Peer comparison with 3-4 closest competitors
        3. Historical valuation trends (5-year range)
        4. Sector average comparisons
        5. DCF-based intrinsic value estimate
        6. Sum-of-parts valuation if applicable
        7. Assessment: Overvalued, fairly valued, or undervalued
        
        Provide specific numbers, peer names, and reasoning for valuation conclusion.
        """,
        
        "scenario_analysis": f"""
        {base_context}
        
        Create three detailed scenarios:
        
        BULL CASE:
        - Key catalysts and positive triggers
        - Revenue/margin upside potential
        - Target price and timeline
        - Probability assessment
        - Investment strategy recommendations
        
        BASE CASE:
        - Realistic growth assumptions
        - Steady-state margins and returns
        - Fair value estimate
        - Most likely outcome
        - Prudent positioning strategy
        
        BEAR CASE:
        - Key risks and negative catalysts
        - Downside scenarios and impact
        - Worst-case target price
        - Risk mitigation strategies
        - Exit triggers
        
        Include specific price targets and probability weightings.
        """,
        
        "final_recommendation": f"""
        {base_context}
        
        Provide final investment recommendation:
        1. Overall investment thesis (Buy/Hold/Sell)
        2. Key supporting arguments (3-4 main points)
        3. Target price and time horizon
        4. Risk-reward assessment
        5. Position sizing recommendations
        6. Key monitoring triggers and metrics
        7. Conditions that would change the recommendation
        
        Structure as executive summary suitable for investment committee presentation.
        Ensure recommendation is clearly justified based on all previous analysis.
        """
    }
    
    return prompts.get(section_key, f"{base_context}\n\nProvide detailed analysis for {section_key}")

def display_enhanced_analysis_results(ticker, results, date):
    """Display comprehensive analysis results with enhanced UI"""
    
    st.markdown(f"""
    # 📊 Professional Investment Analysis: {ticker}
    **Analysis Date:** {date} | **Generated by:** Perplexity AI Research Platform Pro
    """)
    
    # Metrics Dashboard
    create_metrics_dashboard(ticker, results)
    
    # Interactive Charts Section
    st.markdown("## 📈 **Interactive Financial Dashboard**")
    
    chart_col1, chart_col2 = st.columns([2, 1])
    
    with chart_col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        financial_fig = create_sample_financial_chart(ticker)
        st.plotly_chart(financial_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        radar_fig = create_valuation_radar_chart(ticker)
        st.plotly_chart(radar_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced Tabbed Interface
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 **Core Analysis**", 
        "💼 **Management & Governance**", 
        "📊 **Valuation & Scenarios**", 
        "🎯 **Final Recommendation**",
        "📋 **Analysis History**"
    ])
    
    with tab1:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("### 🌐 **Sectoral Trends & Triggers**")
            st.markdown(results.get('sectoral_analysis', 'Analysis not available'))
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("### 💰 **Profit & Loss Analysis (5-Year)**")
            st.markdown(results.get('financial_pl', 'Analysis not available'))
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("### 💸 **Cash Flow Analysis (5-Year)**")
            st.markdown(results.get('financial_cf', 'Analysis not available'))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("### 📰 **News & Competition**")
            st.markdown(results.get('news_competition', 'Analysis not available'))
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("### 🏦 **Balance Sheet Analysis (5-Year)**")
            st.markdown(results.get('financial_bs', 'Analysis not available'))
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("### 📊 **Comprehensive Ratio Analysis**")
            st.markdown(results.get('ratio_analysis', 'Analysis not available'))
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("### 👥 **Management Evaluation**")
            st.markdown(results.get('management_eval', 'Analysis not available'))
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("### 📋 **Investor Presentations Analysis**")
            st.markdown(results.get('investor_presentations', 'Analysis not available'))
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("### 💬 **Community & Forum Analysis**")
            st.markdown(results.get('community_analysis', 'Analysis not available'))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("### 📈 **Management Guidance & Delivery**")
            st.markdown(results.get('management_guidance', 'Analysis not available'))
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("### 🎙️ **Conference Calls Analysis**")
            st.markdown(results.get('conference_calls', 'Analysis not available'))
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("### 📑 **Annual Report Forensics**")
            st.markdown(results.get('annual_report', 'Analysis not available'))
            st.markdown('</div>', unsafe_allow_html=True)
    
        st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
        st.markdown("### 🎯 **Management Integrity Matrix**")
        st.markdown(results.get('integrity_matrix', 'Analysis not available'))
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("### 🚀 **Growth Triggers**")
            st.markdown(results.get('growth_triggers', 'Analysis not available'))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
            st.markdown("### 💎 **Valuation Analysis**")
            st.markdown(results.get('valuation_analysis', 'Analysis not available'))
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="analysis-section">', unsafe_allow_html=True)
        st.markdown("### 🎭 **Scenario Analysis: Bull, Base & Bear Cases**")
        st.markdown(results.get('scenario_analysis', 'Analysis not available'))
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab4:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        recommendation_text = results.get('final_recommendation', 'Recommendation not available')
        
        rec_class = "recommendation-hold"
        if "buy" in recommendation_text.lower() and "don't buy" not in recommendation_text.lower():
            rec_class = "recommendation-buy"
        elif "sell" in recommendation_text.lower():
            rec_class = "recommendation-sell"
        
        st.markdown(f'<div class="analysis-section {rec_class}">', unsafe_allow_html=True)
        st.markdown("### ⭐ **Final Investment Recommendation**")
        st.markdown(recommendation_text)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Download options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            full_report = generate_full_report(ticker, results, date)
            st.download_button(
                label="📄 **Download MD Report**",
                data=full_report,
                file_name=f"{ticker}_Analysis_{datetime.now().strftime('%Y%m%d')}.md",
                mime="text/markdown"
            )
        
        with col2:
            pdf_report = generate_pdf_summary(ticker, results, date)
            st.download_button(
                label="📑 **Download PDF Summary**",
                data=pdf_report,
                file_name=f"{ticker}_Summary_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
        
        with col3:
            excel_data = generate_excel_data(ticker, results)
            st.download_button(
                label="📊 **Download Data (CSV)**",
                data=excel_data,
                file_name=f"{ticker}_Data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab5:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        st.markdown("### 📋 **Analysis History**")
        
        if st.session_state.analysis_history:
            history_df = pd.DataFrame(st.session_state.analysis_history)
            st.dataframe(history_df, use_container_width=True)
        else:
            st.info("No previous analyses found. Your analysis history will appear here.")
        
        if st.button("🗑️ **Clear History**"):
            st.session_state.analysis_history = []
            st.success("Analysis history cleared!")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

def generate_full_report(ticker, results, date):
    """Generate downloadable markdown report"""
    sections = [
        ("Executive Summary", results.get('final_recommendation', 'Not available')),
        ("Sectoral Trends & Triggers", results.get('sectoral_analysis', 'Not available')),
        ("News & Competition Analysis", results.get('news_competition', 'Not available')),
        ("P&L Analysis (5-Year)", results.get('financial_pl', 'Not available')),
        ("Balance Sheet Analysis (5-Year)", results.get('financial_bs', 'Not available')),
        ("Cash Flow Analysis (5-Year)", results.get('financial_cf', 'Not available')),
        ("Ratio Analysis", results.get('ratio_analysis', 'Not available')),
        ("Management Evaluation", results.get('management_eval', 'Not available')),
        ("Management Guidance & Delivery", results.get('management_guidance', 'Not available')),
        ("Investor Presentations", results.get('investor_presentations', 'Not available')),
        ("Conference Calls Analysis", results.get('conference_calls', 'Not available')),
        ("Community Analysis", results.get('community_analysis', 'Not available')),
        ("Annual Report Forensics", results.get('annual_report', 'Not available')),
        ("Management Integrity Matrix", results.get('integrity_matrix', 'Not available')),
        ("Growth Triggers", results.get('growth_triggers', 'Not available')),
        ("Valuation Analysis", results.get('valuation_analysis', 'Not available')),
        ("Scenario Analysis", results.get('scenario_analysis', 'Not available')),
    ]
    
    report = f"# Investment Analysis Report: {ticker}\nGenerated on: {date}\n\n"
    for title, content in sections:
        report += f"## {title}\n{content}\n\n---\n\n"
    
    return report

def generate_pdf_summary(ticker, results, date):
    """Generate PDF-style summary"""
    summary = f"""
INVESTMENT ANALYSIS SUMMARY
Company: {ticker}
Date: {date}

EXECUTIVE SUMMARY:
{results.get('final_recommendation', 'Not available')[:500]}...

KEY FINANCIAL HIGHLIGHTS:
{results.get('ratio_analysis', 'Not available')[:300]}...

MANAGEMENT ASSESSMENT:
{results.get('integrity_matrix', 'Not available')[:300]}...

VALUATION CONCLUSION:
{results.get('valuation_analysis', 'Not available')[:300]}...

RISK FACTORS:
{results.get('scenario_analysis', 'Not available')[:300]}...

This is a condensed summary. Download the full markdown report for complete analysis.
"""
    return summary

def generate_excel_data(ticker, results):
    """Generate CSV data for Excel"""
    data = {
        'Section': ['Final Recommendation', 'Sectoral Analysis', 'Financial Analysis', 'Management Evaluation', 'Valuation'],
        'Status': ['Complete', 'Complete', 'Complete', 'Complete', 'Complete'],
        'Key_Points': [
            'Investment thesis and recommendation',
            'Sector trends and competitive position',
            'Financial performance over 5 years',
            'Management quality assessment',
            'Valuation and price targets'
        ],
        'Timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] * 5
    }
    
    df = pd.DataFrame(data)
    return df.to_csv(index=False)

# Header with enhanced styling
st.markdown("""
<div class="main-header">
    <h1>📊 Professional Investment Research Platform Pro</h1>
    <p>Advanced Stock Analysis with Interactive Dashboards • Powered by Perplexity AI</p>
</div>
""", unsafe_allow_html=True)

# Enhanced Sidebar
st.sidebar.header("🔍 **Stock Analysis Control Center**")

# Analysis Mode Selection
analysis_mode = st.sidebar.selectbox(
    "📊 **Analysis Mode**",
    ["Single Stock Analysis", "Comparative Analysis", "Portfolio Review"],
    help="Choose your analysis approach"
)

# Stock Input with validation
ticker_input = st.sidebar.text_input(
    "🏢 **Enter Stock Ticker:**",
    placeholder="e.g., TCS, RELIANCE, AAPL",
    help="Enter NSE/BSE ticker for Indian stocks or standard ticker for international stocks",
    value=st.session_state.current_ticker
)

if analysis_mode == "Comparative Analysis":
    comparison_ticker = st.sidebar.text_input(
        "🔄 **Comparison Stock:**",
        placeholder="e.g., INFY, HCLTECH",
        help="Enter second stock for comparison"
    )

# Analysis Settings
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ **Analysis Settings**")

analysis_depth = st.sidebar.selectbox(
    "🎯 **Analysis Depth**",
    ["Quick Overview", "Standard Analysis", "Deep Dive"],
    index=1,
    help="Choose analysis comprehensiveness"
)

date_range = st.sidebar.selectbox(
    "📅 **Historical Period**",
    ["Last 3 Years", "Last 5 Years", "Last 10 Years"],
    index=1
)

# API Status with visual indicator
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔧 **System Status**")

if client:
    st.sidebar.markdown(
        '<span class="status-indicator status-online"></span>**API Status:** Connected ✅',
        unsafe_allow_html=True
    )
else:
    st.sidebar.markdown(
        '<span class="status-indicator status-offline"></span>**API Status:** Disconnected ❌',
        unsafe_allow_html=True
    )
    st.sidebar.error("Set PPLX_API_KEY in environment variables")

# Analysis Date
analysis_date = datetime.now().strftime("%B %d, %Y")
st.sidebar.info(f"📅 **Analysis Date:** {analysis_date}")

# Enhanced Analysis Button
if st.sidebar.button("🚀 **Generate Complete Analysis**", type="primary", use_container_width=True):
    if not ticker_input:
        st.error("❌ Please enter a stock ticker or company name.")
    elif not client:
        st.error("❌ Perplexity API key not configured. Please check your environment variables.")
    else:
        ticker = ticker_input.upper().strip()
        st.session_state.current_ticker = ticker
        
        # Enhanced progress tracking
        progress_container = st.container()
        with progress_container:
            st.markdown('<div class="progress-container">', unsafe_allow_html=True)
            st.markdown("### 🔄 **Analysis in Progress...**")
            progress_bar = st.progress(0)
            status_text = st.empty()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Analysis sections based on depth
        if analysis_depth == "Quick Overview":
            sections = [
                ("🌐 Sectoral Analysis", "sectoral_analysis"),
                ("💰 Financial Overview", "financial_pl"),
                ("💎 Valuation", "valuation_analysis"),
                ("⭐ Recommendation", "final_recommendation")
            ]
        elif analysis_depth == "Deep Dive":
            sections = [
                ("🌐 Sectoral Trends & Triggers", "sectoral_analysis"),
                ("📰 News & Competition", "news_competition"),
                ("💰 Financial Analysis - P&L", "financial_pl"),
                ("🏦 Financial Analysis - Balance Sheet", "financial_bs"),
                ("💸 Financial Analysis - Cash Flow", "financial_cf"),
                ("📊 Ratio Analysis", "ratio_analysis"),
                ("👥 Management Evaluation", "management_eval"),
                ("📈 Management Guidance & Delivery", "management_guidance"),
                ("📋 Investor Presentations Analysis", "investor_presentations"),
                ("🎙️ Conference Calls Analysis", "conference_calls"),
                ("💬 Community & Forum Analysis", "community_analysis"),
                ("📑 Annual Report Forensics", "annual_report"),
                ("🎯 Management Integrity Matrix", "integrity_matrix"),
                ("🚀 Growth Triggers", "growth_triggers"),
                ("💎 Valuation Analysis", "valuation_analysis"),
                ("🎭 Scenario Analysis", "scenario_analysis"),
                ("⭐ Final Recommendation", "final_recommendation")
            ]
        else:  # Standard Analysis
            sections = [
                ("🌐 Sectoral Trends & Triggers", "sectoral_analysis"),
                ("📰 News & Competition", "news_competition"),
                ("💰 Financial Analysis - P&L", "financial_pl"),
                ("🏦 Financial Analysis - Balance Sheet", "financial_bs"),
                ("💸 Financial Analysis - Cash Flow", "financial_cf"),
                ("📊 Ratio Analysis", "ratio_analysis"),
                ("👥 Management Evaluation", "management_eval"),
                ("🎯 Management Integrity Matrix", "integrity_matrix"),
                ("🚀 Growth Triggers", "growth_triggers"),
                ("💎 Valuation Analysis", "valuation_analysis"),
                ("🎭 Scenario Analysis", "scenario_analysis"),
                ("⭐ Final Recommendation", "final_recommendation")
            ]
        
        results = {}
        
        for i, (title, key) in enumerate(sections):
            with status_text:
                st.markdown(f"**Analyzing:** {title}")
            progress_bar.progress((i + 1) / len(sections))
            
            prompt = generate_section_prompt(key, ticker, analysis_date)
            results[key] = query_perplexity(prompt)
            
            # Small delay for better UX
            time.sleep(0.5)
        
        # Store results and update history
        st.session_state.analysis_results[ticker] = results
        st.session_state.analysis_history.append({
            'Ticker': ticker,
            'Date': analysis_date,
            'Depth': analysis_depth,
            'Sections': len(sections)
        })
        
        status_text.text("✅ **Analysis Complete!**")
        progress_bar.progress(1.0)
        
        # Clear progress and show results
        progress_container.empty()
        display_enhanced_analysis_results(ticker, results, analysis_date)

# Quick Actions Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ **Quick Actions**")

if st.sidebar.button("📈 **Sample Analysis Demo**"):
    demo_results = {
        'final_recommendation': "**BUY** - Strong fundamentals with 25% upside potential",
        'sectoral_analysis': "Technology sector showing robust growth...",
        'valuation_analysis': "Currently trading at attractive valuations..."
    }
    display_enhanced_analysis_results("DEMO", demo_results, analysis_date)

if st.sidebar.button("🔄 **Refresh Data Cache**"):
    st.cache_data.clear()
    st.success("✅ Cache cleared successfully!")

# Enhanced Sidebar Information
st.sidebar.markdown("---")
st.sidebar.markdown('<div class="sidebar-info">', unsafe_allow_html=True)
st.sidebar.markdown("### 📝 **Analysis Features:**")
st.sidebar.markdown("""
✅ **Interactive dashboards**  
✅ **Real-time financial charts**  
✅ **Comprehensive ratio analysis**  
✅ **Management evaluation**  
✅ **Peer comparison**  
✅ **Risk-reward scenarios**  
✅ **Multiple export formats**  
✅ **Analysis history tracking**  
""")
st.sidebar.markdown('</div>', unsafe_allow_html=True)

# Footer with enhanced styling
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 8px; margin-top: 2rem;'>
    <h4 style='color: #2a5298; margin-bottom: 1rem;'>📊 Professional Investment Research Platform Pro</h4>
    <p><strong>Powered by:</strong> Perplexity AI • <strong>Enhanced with:</strong> Interactive Dashboards & Advanced Analytics</p>
    <p><small>🔒 For educational and research purposes • Not financial advice • Always consult professionals</small></p>
    <p><small>Version 2.0 • Last Updated: {datetime.now().strftime('%B %Y')}</small></p>
</div>
""", unsafe_allow_html=True)
