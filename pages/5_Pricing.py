"""ResumeMatch AI — 💎 Pricing."""

import streamlit as st

st.set_page_config(page_title="ResumeMatch AI — Pricing", page_icon="📄", layout="wide")

from src.ui import check_auth, inject_css, render_header, render_sidebar_footer
from src.billing import get_usage, render_usage_badge, render_pricing_card, _show_razorpay_checkout

if not check_auth():
    st.stop()

inject_css()
render_header()

username = st.session_state.get("username", "guest")
usage = get_usage(username)

if usage["is_pro"]:
    st.markdown("""
    <div style="text-align:center; padding:60px 20px;">
        <div style="font-size:4em; margin-bottom:12px;">⭐</div>
        <div style="background:linear-gradient(135deg,#667eea,#764ba2,#f093fb);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
            font-size:2em; font-weight:800;">You're on Pro!</div>
        <div style="color:#3fb950; font-size:1.1em; margin-top:8px;">
            Unlimited analyses • AI Rewriter • ATS Simulator
        </div>
    </div>""", unsafe_allow_html=True)
else:
    st.markdown("### 💎 Upgrade to Pro")
    st.markdown("")

    # Comparison table
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style="background:rgba(22,27,34,0.8); border:1px solid rgba(48,54,61,0.5);
            border-radius:16px; padding:30px; text-align:center; height:100%;">
            <div style="color:#6e7681; font-weight:700; font-size:0.85em; letter-spacing:2px;">FREE</div>
            <div style="margin:12px 0;">
                <span style="color:white; font-size:2.5em; font-weight:800;">₹0</span>
            </div>
            <div style="color:#b1bac4; font-size:0.9em; text-align:left; padding:0 10px;">
                ✅ 2 resume analyses<br>
                ✅ Match score<br>
                ✅ Skills found/missing<br>
                ❌ AI Resume Rewriter<br>
                ❌ ATS Simulator<br>
                ❌ PDF download<br>
            </div>
            <div style="margin-top:16px; color:#6e7681; font-size:0.85em;">Current plan</div>
        </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background:linear-gradient(135deg, rgba(102,126,234,0.15), rgba(118,75,162,0.1));
            border:2px solid rgba(102,126,234,0.4); border-radius:16px; padding:30px; text-align:center; height:100%;">
            <div style="color:#667eea; font-weight:700; font-size:0.85em; letter-spacing:2px;">⭐ PRO</div>
            <div style="margin:12px 0;">
                <span style="color:white; font-size:2.5em; font-weight:800;">₹99</span>
                <span style="color:#6e7681; font-size:0.9em;">/month</span>
            </div>
            <div style="color:#b1bac4; font-size:0.9em; text-align:left; padding:0 10px;">
                ✅ Unlimited analyses<br>
                ✅ Match score<br>
                ✅ Skills found/missing<br>
                ✅ AI Resume Rewriter<br>
                ✅ ATS Simulator<br>
                ✅ PDF download<br>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("💳 Upgrade to Pro — ₹99/month", type="primary", use_container_width=True):
        _show_razorpay_checkout()

with st.sidebar:
    render_usage_badge()
    render_sidebar_footer()
