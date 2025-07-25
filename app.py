"""
Investment Research Platform PRO
Built: 25-Jul-2025 20:50 IST
"""

import os, uuid, io
from datetime import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from openai import OpenAI
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# ---------- Config & Theme ----------
st.set_page_config(page_title="Investment Research PRO",
                   page_icon="📊", layout="wide",
                   initial_sidebar_state="expanded")

# Color palette
BG = "#121212"
PANEL = "#242424"
TEXT = "#D0D0D0"
NEON = "#9EFF9C"

# CSS Reset & Dark Theme
st.markdown(f"""
<style>
html, body, .stApp {{background:{BG}; color:{TEXT}; margin:0; padding:0;}}
.block-container {{padding-top:0;}}
section[data-testid="stSidebar"] > div:first-child {{background:{PANEL};}}
button[kind="primary"] {{background:{NEON}; color:{BG};}}
</style>
""", unsafe_allow_html=True)

# ---------- Perplexity Client ----------
@st.cache_resource(show_spinner=False)
def init_client():
    key = os.getenv("PPLX_API_KEY")
    return OpenAI(api_key=key, base_url="https://api.perplexity.ai") if key else None

client = init_client()
MODELS = ["sonar-pro","sonar","sonar-reasoning"]

@st.cache_data(ttl=3600, show_spinner=False)
def ask_ai(prompt: str) -> str:
    if client is None:
        return "⚠️ API key not configured."
    for m in MODELS:
        try:
            resp = client.chat.completions.create(
                model=m,
                messages=[
                    {"role":"system","content":
                     "You are an equity research analyst. Provide detailed data-driven analysis."},
                    {"role":"user","content":prompt}
                ],
                temperature=0.1, max_tokens=2000
            )
            return resp.choices[0].message.content
        except Exception as e:
            if "invalid_model" in str(e).lower():
                continue
            return f"❌ {e}"
    return "❌ All models failed."

# ---------- Sample Data & Charts ----------
def fake_data():
    np.random.seed(42)
    years = list(range(datetime.now().year-4, datetime.now().year+1))
    rev = [100 + i*12 + np.random.randint(-8,10) for i in range(5)]
    prof = [r*np.random.uniform(0.11,0.18) for r in rev]
    marg = [p/r*100 for p,r in zip(prof,rev)]
    return years, rev, prof, marg

def make_charts():
    yrs, rev, prof, marg = fake_data()
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=yrs,y=rev,mode="lines+markers",name="Revenue",line=dict(color=NEON)))
    fig1.add_trace(go.Scatter(x=yrs,y=prof,mode="lines+markers",name="Profit",line=dict(color="#4ADE80")))
    fig1.update_layout(template="plotly_dark",plot_bgcolor=BG,paper_bgcolor=PANEL,
                       font_color=TEXT,height=300,margin=dict(t=30,b=10,l=10,r=10))
    fig2 = go.Figure(go.Bar(x=yrs,y=marg,marker_color=NEON))
    fig2.update_layout(template="plotly_dark",plot_bgcolor=BG,paper_bgcolor=PANEL,
                       font_color=TEXT,height=300,margin=dict(t=30,b=10,l=10,r=10),
                       yaxis_title="Margin %")
    return fig1, fig2

# ---------- PDF Generation ----------
def create_pdf(ticker: str, summary: str, charts: list[go.Figure]) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    # Page 1: Dashboard snapshots
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, height-40, f"{ticker.upper()} Investment Research PRO")
    c.setFont("Helvetica", 10)
    c.drawString(40, height-60, f"Generated: {datetime.now().strftime('%d %b %Y %H:%M')}")
    y = height-100
    for fig in charts:
        img_buf = io.BytesIO()
        fig.write_image(img_buf, format="png", width=600, height=300)
        img_buf.seek(0)
        c.drawImage(ImageReader(img_buf), 40, y-310, width=520, height=260)
        y -= 320
        if y<100:
            c.showPage()
            y = height-100
    # Page 2: Summary & Deep Sections
    c.showPage()
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, height-40, "Executive Summary")
    text = c.beginText(40, height-60)
    text.setFont("Helvetica", 10)
    for line in summary.split("\n"):
        text.textLine(line)
        if text.getY() < 40:
            c.drawText(text)
            c.showPage()
            text = c.beginText(40, height-40)
            text.setFont("Helvetica", 10)
    c.drawText(text)
    c.showPage()
    c.save()
    return buf.getvalue()

# ---------- Layout & Interaction ----------
# Header
st.markdown(f"""
<div style='background:{PANEL};padding:1.5rem;border-radius:8px;margin-bottom:1rem;'>
  <h1 style='color:{NEON};margin:0;'>Investment Research PRO</h1>
  <p style='margin:0;color:{TEXT};opacity:.8;'>AI‐Driven Equity Research • Dark Mode • PDF Reports</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
ticker = st.sidebar.text_input("Ticker / Symbol", placeholder="e.g., AAPL / TCS")
run = st.sidebar.button("🚀 Run Full Analysis", type="primary", use_container_width=True)
st.sidebar.markdown("---")
st.sidebar.write("**On‐Demand Deep Dive** will appear below after analysis.")

if run:
    dt = datetime.now().strftime("%d %b %Y")
    # 17-section prompts
    sections = {
      "Sector Trends & Triggers":
        f"Analyze sector trends for {ticker} as of {dt}. Provide drivers, risks, examples.",
      "News & Competition":
        f"Summarize last 30-day news for {ticker}, classify as positive/neutral/negative.",
      "P&L Analysis":
        f"5-year P&L deep dive for {ticker}. Detail revenue, margins, seasonality.",
      "Balance Sheet":
        f"5-year balance sheet analysis for {ticker}. Detail assets, debt ratios.",
      "Cash Flow":
        f"5-year cash flow analysis for {ticker}. Detail operating/FCF trends.",
      "Ratio Analysis":
        f"Provide ROE, ROA, margins, liquidity, leverage, valuation ratios with industry avg.",
      "Management Eval":
        f"Evaluate management quality: background, track record, governance.",
      "Guidance Delivery":
        f"Assess management guidance vs actual over past 3 years for {ticker}.",
      "Presentations":
        f"Summarize key themes from last 12 investor presentations for {ticker}.",
      "Conference Calls":
        f"Summarize last 12 quarters earnings calls tone and key updates.",
      "Community Sentiment":
        f"Analyze retail forum sentiment for {ticker} over last 90 days.",
      "Annual Report":
        f"Forensic analysis of latest annual report for {ticker}. Red flags.",
      "Integrity Matrix":
        f"Score management integrity on guidance accuracy, transparency, governance.",
      "Growth Triggers":
        f"Identify key growth catalysts for {ticker} with timelines and impact.",
      "Valuation":
        f"Valuation: P/E, EV/EBITDA, DCF, peer comparison for {ticker}.",
      "Scenario Analysis":
        f"Bull, Base, Bear cases for {ticker} with targets and probabilities.",
      "Final Recommendation":
        f"Executive recommendation for {ticker}. Buy/Hold/Sell, target price."
    }
    # Run AI for each
    results = {}
    with st.spinner("Generating analysis..."):
        for title, prompt in sections.items():
            results[title] = ask_ai(prompt)
    st.success("Analysis complete — explore below.")

    # Summary Dashboard
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Rating", results["Final Recommendation"].split()[-1])
    kpi2.metric("Generated", datetime.now().strftime("%d %b %Y %H:%M"))
    kpi3.metric("Model", MODELS[0])
    kpi4.metric("Sections", len(sections))

    fig1, fig2 = make_charts()
    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)

    # PDF Download
    pdf_bytes = create_pdf(ticker.upper(), results["Final Recommendation"], [fig1, fig2])
    st.download_button("⬇️ Download Full PDF Report",
                       data=pdf_bytes,
                       file_name=f"{ticker.upper()}_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                       mime="application/pdf",
                       key=str(uuid.uuid4()))

    # Deep Dive Expanders
    for title, content in results.items():
        with st.expander(title, expanded=False):
            st.markdown(content)

else:
    st.info("Enter a ticker at left and click **Run Full Analysis** to begin.")
