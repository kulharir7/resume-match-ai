"""ResumeMatch AI — 📊 ATS Simulator."""

import streamlit as st

st.set_page_config(page_title="ResumeMatch AI — ATS Simulator", page_icon="📄", layout="wide")

from src.ui import check_auth, inject_css, render_header, render_sidebar_footer, score_color, score_emoji
from src.billing import get_usage, render_paywall, render_usage_badge

if not check_auth():
    st.stop()

inject_css()
render_header()

# --- Pro-only gate ---
username = st.session_state.get("username", "guest")
usage = get_usage(username)
if not usage["is_pro"]:
    st.markdown("""
    <div style="text-align:center; padding:60px 20px;">
        <div style="font-size:3em; margin-bottom:12px;">📊</div>
        <div style="color:white; font-size:1.5em; font-weight:700;">ATS Simulator</div>
        <div style="color:#6e7681; margin:8px 0 20px 0;">This is a Pro feature. Upgrade to see detailed ATS analysis.</div>
    </div>""", unsafe_allow_html=True)
    render_paywall()
    st.stop()

# --- Check analysis ---
if not st.session_state.get("analysis_result"):
    st.warning("⚠️ Run an analysis first on the main page.")
    st.stop()

r = st.session_state.analysis_result
ats = r.get("ats", {})
contact = r.get("contact", {})

# --- Header ---
st.markdown("### 📊 ATS Simulator")
st.caption("See how Applicant Tracking Systems read your resume")

# --- ATS Score ---
score = ats.get("score", 0)
emoji = score_emoji(score)

st.markdown(f'<div class="score-card"><div class="score-value">{emoji} {score}%</div><div class="score-label">ATS Compatibility Score</div></div>', unsafe_allow_html=True)

st.divider()

# --- Parsing Results ---
st.markdown("### 🔍 What ATS Sees")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**📇 Contact Information**")
    
    name = contact.get("name", "N/A")
    email = contact.get("email")
    phone = contact.get("phone")
    
    st.markdown(f"{'✅' if name != 'Unknown' else '❌'} **Name:** {name}")
    st.markdown(f"{'✅' if email else '❌'} **Email:** {email or 'NOT FOUND'}")
    st.markdown(f"{'✅' if phone else '❌'} **Phone:** {phone or 'NOT FOUND'}")

with col2:
    st.markdown("**📑 Sections Detected**")
    
    expected_sections = ["experience", "education", "skills", "summary", "projects"]
    found_sections = ats.get("sections_found", [])
    
    for sec in expected_sections:
        if sec in found_sections:
            st.markdown(f"✅ **{sec.title()}** — Found")
        else:
            st.markdown(f"❌ **{sec.title()}** — Not found")

st.divider()

# --- Formatting Checks ---
st.markdown("### 📐 Formatting Analysis")

c1, c2, c3 = st.columns(3)

with c1:
    wc = ats.get("word_count", 0)
    if 300 <= wc <= 800:
        st.success(f"📝 Word Count: **{wc}** ✅")
    elif wc < 300:
        st.warning(f"📝 Word Count: **{wc}** — Too short")
    else:
        st.warning(f"📝 Word Count: **{wc}** — Consider trimming")

with c2:
    if ats.get("file_type_ok"):
        st.success(f"📎 File Type: **{r.get('filename', 'PDF')}** ✅")
    else:
        st.error("📎 File Type: Not ATS-friendly")

with c3:
    if ats.get("has_metrics"):
        st.success("📊 Quantified Results: **Found** ✅")
    else:
        st.warning("📊 Quantified Results: **Missing** — Add numbers!")

st.divider()

# --- Action Verbs ---
st.markdown("### 💪 Action Verbs")
found_verbs = ats.get("action_verbs_found", [])
if found_verbs:
    verbs_html = " ".join([f'<span class="skill-found">{v}</span>' for v in found_verbs])
    st.markdown(verbs_html, unsafe_allow_html=True)
    if len(found_verbs) >= 5:
        st.success(f"Great! {len(found_verbs)} action verbs found")
    else:
        st.info(f"Found {len(found_verbs)} — try adding more: Managed, Led, Designed, Improved, Delivered")
else:
    st.warning("No strong action verbs detected. Add: Managed, Developed, Led, Implemented...")

st.divider()

# --- Keywords Found ---
st.markdown("### 🔑 Keywords Analysis")

jd_keywords = r.get("jd_keywords", {})
hard_found = r.get("hard_skills", {}).get("found", [])
hard_missing = r.get("hard_skills", {}).get("missing", [])

total_keywords = len(hard_found) + len(hard_missing)
if total_keywords > 0:
    st.progress(len(hard_found) / total_keywords)
    st.caption(f"**{len(hard_found)}/{total_keywords}** keywords from job description found in resume")

col1, col2 = st.columns(2)
with col1:
    if hard_found:
        st.markdown("**✅ Found in resume:**")
        found_html = " ".join([f'<span class="skill-found">{s}</span>' for s in hard_found])
        st.markdown(found_html, unsafe_allow_html=True)
with col2:
    if hard_missing:
        st.markdown("**❌ Missing from resume:**")
        missing_html = " ".join([f'<span class="skill-missing">{s}</span>' for s in hard_missing])
        st.markdown(missing_html, unsafe_allow_html=True)

st.divider()

# --- Issues ---
if ats.get("issues"):
    st.markdown("### ⚠️ Issues to Fix")
    for issue in ats["issues"]:
        st.warning(f"⚠️ {issue}")

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 📊 ATS Score")
    st.markdown(f'<div class="score-card"><div class="score-value">{score}%</div></div>', unsafe_allow_html=True)
    render_sidebar_footer()
