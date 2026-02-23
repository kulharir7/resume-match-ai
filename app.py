"""ResumeMatch AI — 💬 Analyzer (Main Page)."""

import streamlit as st

st.set_page_config(page_title="ResumeMatch AI", page_icon="📄", layout="wide")

from src.ui import check_auth, inject_css, render_header, render_sidebar_footer, score_color, score_emoji

if not check_auth():
    st.stop()

inject_css()
render_header()

from src.parser import extract_resume_text, extract_sections
from src.analyzer import full_analysis

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 📄 Input")
    
    jd_text = st.text_area(
        "Paste Job Description",
        height=200,
        placeholder="Paste the full job description here...",
    )
    
    uploaded = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])
    
    analyze_btn = st.button("🔍 Analyze Match", type="primary", use_container_width=True,
                            disabled=not (jd_text and uploaded))
    
    st.divider()
    
    if not jd_text:
        st.info("👆 Paste a job description")
    if not uploaded:
        st.info("👆 Upload your resume (PDF/DOCX)")
    
    render_sidebar_footer()

# --- Main Content ---
if not st.session_state.get("analysis_result"):
    # Empty state
    st.markdown("""
    <div style="text-align:center; padding:60px 20px;">
        <div style="font-size:4em; margin-bottom:12px;">📄</div>
        <div style="color:#c9d1d9; font-size:1.3em; font-weight:600;">Optimize Your Resume for Any Job</div>
        <div style="color:#6e7681; font-size:0.95em; margin-top:6px;">
            Paste job description + Upload resume → Get match score & actionable suggestions
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("🎯 **Match Score**\n\nSee how well your resume matches")
    with c2:
        st.markdown("🔍 **Skills Gap**\n\nFind missing keywords")
    with c3:
        st.markdown("✍️ **AI Rewrite**\n\nGet optimized version")

# --- Run Analysis ---
if analyze_btn and jd_text and uploaded:
    resume_bytes = uploaded.read()
    
    with st.status("🔍 Analyzing your resume...", expanded=True) as status:
        st.write("📄 Parsing resume...")
        try:
            resume_text = extract_resume_text(resume_bytes, uploaded.name)
        except Exception as e:
            st.error(f"❌ Could not parse resume: {e}")
            st.stop()
        
        st.write(f"✅ Parsed — {len(resume_text.split())} words")
        st.write("🤖 Running AI analysis...")
        
        try:
            result = full_analysis(resume_text, jd_text, uploaded.name)
        except Exception as e:
            st.error(f"❌ Analysis failed: {e}")
            st.stop()
        
        result["resume_text"] = resume_text
        result["jd_text"] = jd_text
        result["filename"] = uploaded.name
        st.session_state.analysis_result = result
        
        status.update(label="✅ Analysis Complete!", state="complete")
    
    st.rerun()

# --- Display Results ---
if st.session_state.get("analysis_result"):
    r = st.session_state.analysis_result
    
    # Overall Score
    st.markdown("### 🎯 Overall Match Score")
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        color = score_color(r["overall_score"])
        st.markdown(f'<div class="score-card"><div class="score-value">{r["overall_score"]}%</div><div class="score-label">Overall Match</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="score-card"><div class="score-value">{r["hard_skills"]["score"]}%</div><div class="score-label">Hard Skills</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="score-card"><div class="score-value">{r["experience"]["score"]}%</div><div class="score-label">Experience</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="score-card"><div class="score-value">{r["education"]["score"]}%</div><div class="score-label">Education</div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="score-card"><div class="score-value">{r["ats"]["score"]}%</div><div class="score-label">ATS Format</div></div>', unsafe_allow_html=True)
    
    # Overall Fit
    if r.get("overall_fit"):
        st.info(f"💡 **AI Assessment:** {r['overall_fit']}")
    
    st.divider()
    
    # Skills Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Skills Found")
        if r["hard_skills"]["found"]:
            skills_html = " ".join([f'<span class="skill-found">{s}</span>' for s in r["hard_skills"]["found"]])
            st.markdown(skills_html, unsafe_allow_html=True)
        else:
            st.caption("No matching hard skills found")
        
        if r["soft_skills"]["found"]:
            soft_html = " ".join([f'<span class="skill-found">{s}</span>' for s in r["soft_skills"]["found"]])
            st.markdown(soft_html, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### ❌ Skills Missing")
        if r["hard_skills"]["missing"]:
            missing_html = " ".join([f'<span class="skill-missing">{s}</span>' for s in r["hard_skills"]["missing"]])
            st.markdown(missing_html, unsafe_allow_html=True)
        else:
            st.success("All required hard skills present!")
        
        if r["soft_skills"]["missing"]:
            soft_missing_html = " ".join([f'<span class="skill-missing">{s}</span>' for s in r["soft_skills"]["missing"]])
            st.markdown(soft_missing_html, unsafe_allow_html=True)
    
    st.divider()
    
    # Strengths & Weaknesses
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 💪 Strengths")
        for s in r.get("strengths", []):
            st.markdown(f"✅ {s}")
    
    with col2:
        st.markdown("### ⚠️ Weaknesses")
        for w in r.get("weaknesses", []):
            st.markdown(f"❌ {w}")
    
    st.divider()
    
    # Suggestions
    st.markdown("### 💡 Top Suggestions")
    for i, suggestion in enumerate(r.get("suggestions", []), 1):
        st.markdown(f'<div class="suggestion-card">**{i}.** {suggestion}</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # ATS Issues
    if r["ats"]["issues"]:
        st.markdown("### 📋 ATS Formatting Issues")
        for issue in r["ats"]["issues"]:
            st.warning(f"⚠️ {issue}")
    
    # Contact info
    with st.expander("📇 Parsed Contact Info"):
        contact = r.get("contact", {})
        st.markdown(f"**Name:** {contact.get('name', 'N/A')}")
        st.markdown(f"**Email:** {contact.get('email', 'N/A')}")
        st.markdown(f"**Phone:** {contact.get('phone', 'N/A')}")
    
    # New analysis button
    if st.button("🔄 New Analysis", use_container_width=True):
        st.session_state.analysis_result = None
        st.rerun()
