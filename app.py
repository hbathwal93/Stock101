import os, time, uuid
from datetime import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from openai import OpenAI

# ----------  Page Config  ----------
st.set_page_config(
    page_title="Investment Research Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------  Dark Theme CSS  ----------
st.markdown(
    """
    <style>
    body, .stApp {background-color:#1c1c1e; color:#e0e0e0;}
    .block-container {padding-top:0rem;}
    /* header */
    .main-header{background:#2e2e30;border-radius:12px;padding:2rem 1rem;margin-bottom:1.5rem;}
    .main-header h1{color:#a9ff9d;margin:0;}
    /* cards */
    .kpi-card{background:#2e2e30;padding:1.2rem;border-radius:10px;text-align:center;}
    .metric-value{color:#a9ff9d;font-size:1.8rem;font-weight:bold;margin:0;}
    .metric-label{font-size:.8rem;color:#999;}
    /* sections */
    .analysis-box{background:#2e2e30;padding:1.5rem;border-left:4px solid #a9ff9d;border-radius:10px;margin-bottom:1rem;}
    /* buttons */
    button[kind="primary"]{background:#3c3c3e;color:#a9ff9d;border:none;}
    </style>
    """,
    unsafe_allow_html=True
)

# ----------  API Client  ----------
@st.cache_resource
def init_client() -> OpenAI | None:
    key = os.getenv("PPLX_API_KEY")
    return OpenAI(api_key=key, base_url="https://api.perplexity.ai") if key else None

client = init_client()

def ask_perplexity(prompt: str, model: str = "sonar-pro") -> str:
    """Call Perplexity with graceful fallback."""
    if not client:
        return "⚠️ API key not configured."
    for m in ["sonar-pro", "sonar", "sonar-reasoning"]:
        try:
            resp = client.chat.completions.create(
                model=m,
                messages=[
                    {"role": "system", "content":
                     "You are a professional equity research analyst. Respond with data-driven reasoning."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2500
            )
            return resp.choices[0].message.content
        except Exception as e:
            if "invalid_model" in str(e).lower():
                continue
            return f"❌ {e}"
    return "⚠️ No valid model available."

# ----------  Minimal Prompt  ----------
PROMPT_TMPL = (
    "Give a concise executive summary (≤150 words) of {ticker} as of {date} "
    "covering financial health, valuation, opportunities, and key risks. "
    "End with a one-word call (BUY/HOLD/SELL)."
)

# ----------  Dummy Financial Data for Charts ----------
def sample_financials():
    yrs = list(range(datetime.now().year - 4, datetime.now().year + 1))
    rev = [100 + i * 12 + np.random.randint(-8, 10) for i in range(5)]
    profit = [r * np.random.uniform(0.11, 0.18) for r in rev]
    margin = [p / r * 100 for p, r in zip(profit, rev)]
    return yrs, rev, profit, margin

def plot_dashboard():
    yrs, rev, profit, margin = sample_financials()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=yrs, y=rev, mode="lines+markers",
                             name="Revenue", line=dict(color="#a9ff9d")))
    fig.add_trace(go.Scatter(x=yrs, y=profit, mode="lines+markers",
                             name="Profit", line=dict(color="#4ade80")))
    fig.update_layout(
        template="plotly_dark",
        height=280,
        margin=dict(l=10, r=10, t=25, b=10),
        legend=dict(orientation="h", y=1.1)
    )

    bar = go.Figure(go.Bar(x=yrs, y=margin, marker_color="#a9ff9d"))
    bar.update_layout(
        template="plotly_dark",
        height=280,
        margin=dict(l=10, r=10, t=25, b=10),
        yaxis_title="Margin (%)"
    )
    return fig, bar

# ----------  Header  ----------
st.markdown(
    """
    <div class="main-header">
        <h1>Investment Research Pro</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# ----------  Sidebar Inputs  ----------
ticker = st.sidebar.text_input(
    "Ticker / Symbol",
    placeholder="e.g., AAPL / TCS",
)
analyse_btn = st.sidebar.button("Run Analysis", type="primary", use_container_width=True)

if analyse_btn and not ticker:
    st.sidebar.error("Enter a valid ticker first.")

# ----------  Run Analysis  ----------
if analyse_btn and ticker:
    st.session_state["summary"] = ask_perplexity(
        PROMPT_TMPL.format(ticker=ticker.upper(), date=datetime.now().strftime("%d %b %Y"))
    )
    st.session_state["time"] = datetime.now().strftime("%d %b %Y %H:%M")
    st.success("Analysis complete.")

# ----------  Summary Dashboard  ----------
if "summary" in st.session_state:
    col1, col2, col3, col4 = st.columns(4)
    for c, label, val in zip(
        [col1, col2, col3, col4],
        ["Rating", "Run-Time", "AI Model", "Generated"],
        [
            st.session_state["summary"].split()[-1],  # last word is call
            "≈30 sec",
            "sonar-pro",
            st.session_state["time"],
        ],
    ):
        with c:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <p class="metric-value">{val}</p>
                    <p class="metric-label">{label}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ----------  Interactive Charts  ----------
    rev_fig, mar_fig = plot_dashboard()
    st.plotly_chart(rev_fig, use_container_width=True)
    st.plotly_chart(mar_fig, use_container_width=True)

    # ----------  Executive Summary  ----------
    with st.expander("🔍 Executive Summary", expanded=False):
        st.markdown(st.session_state["summary"])

    # ----------  Downloads (Unique Keys) ----------
    md_report = f"# {ticker.upper()} Executive Summary\n\n" + st.session_state["summary"]
    csv_export = pd.DataFrame(
        {"Metric": ["Summary"], "Value": [st.session_state["summary"]]}
    ).to_csv(index=False)

    st.download_button(
        label="⬇️ Download Markdown",
        data=md_report,
        file_name=f"{ticker.upper()}_summary.md",
        mime="text/markdown",
        key=f"dl-md-{uuid.uuid4()}",
    )
    st.download_button(
        label="⬇️ Download CSV",
        data=csv_export,
        file_name=f"{ticker.upper()}_summary.csv",
        mime="text/csv",
        key=f"dl-csv-{uuid.uuid4()}",
    )
else:
    st.info("Enter a ticker on the left and click “Run Analysis”.")
