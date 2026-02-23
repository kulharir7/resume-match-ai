"""ResumeMatch AI — ✍️ AI Resume Rewriter."""

import streamlit as st

st.set_page_config(page_title="ResumeMatch AI — Rewriter", page_icon="📄", layout="wide")

from src.ui import check_auth, inject_css, render_header, render_sidebar_footer
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
        <div style="font-size:3em; margin-bottom:12px;">✍️</div>
        <div style="color:white; font-size:1.5em; font-weight:700;">AI Resume Rewriter</div>
        <div style="color:#6e7681; margin:8px 0 20px 0;">This is a Pro feature. Upgrade to rewrite your resume with AI.</div>
    </div>""", unsafe_allow_html=True)
    render_paywall()
    st.stop()

from src.parser import extract_sections
from src.rewriter import rewrite_section, generate_summary

# --- Check if analysis exists ---
if not st.session_state.get("analysis_result"):
    st.warning("⚠️ Run an analysis first on the main page, then come here to rewrite.")
    st.stop()

r = st.session_state.analysis_result
resume_text = r.get("resume_text", "")
jd_text = r.get("jd_text", "")
missing_skills = r.get("hard_skills", {}).get("missing", [])

# --- Page Header ---
st.markdown("### ✍️ AI Resume Rewriter")
st.caption("Side-by-side comparison — original vs AI-optimized for this job")

# --- Get sections ---
sections = extract_sections(resume_text)

if not sections:
    st.error("Could not parse resume sections. Try a different resume format.")
    st.stop()

# --- Generate Summary if missing ---
if "summary" not in sections:
    if st.button("✨ Generate Professional Summary", type="primary"):
        with st.spinner("Generating summary..."):
            summary = generate_summary(resume_text, jd_text)
            sections["summary"] = ""
            if "rewritten_sections" not in st.session_state:
                st.session_state.rewritten_sections = {}
            st.session_state.rewritten_sections["summary"] = summary
            st.rerun()

# --- Initialize rewritten sections ---
if "rewritten_sections" not in st.session_state:
    st.session_state.rewritten_sections = {}

# --- Section by section rewrite ---
rewrite_order = ["summary", "experience", "skills", "projects", "education"]

for section_name in rewrite_order:
    if section_name not in sections and section_name not in st.session_state.rewritten_sections:
        continue
    
    original = sections.get(section_name, "")
    rewritten = st.session_state.rewritten_sections.get(section_name, "")
    
    st.markdown(f"---")
    st.markdown(f"### {section_name.title()}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📄 Original**")
        st.text_area(
            f"Original {section_name}",
            value=original,
            height=200,
            disabled=True,
            key=f"orig_{section_name}",
            label_visibility="collapsed",
        )
    
    with col2:
        st.markdown("**✨ AI Rewritten**")
        if rewritten:
            edited = st.text_area(
                f"Rewritten {section_name}",
                value=rewritten,
                height=200,
                key=f"rewrite_{section_name}",
                label_visibility="collapsed",
            )
            st.session_state.rewritten_sections[section_name] = edited
        else:
            st.text_area(
                f"Rewritten {section_name}",
                value="Click 'Rewrite' to generate →",
                height=200,
                disabled=True,
                key=f"rewrite_empty_{section_name}",
                label_visibility="collapsed",
            )
    
    if original and not rewritten:
        if st.button(f"✍️ Rewrite {section_name.title()}", key=f"btn_{section_name}", use_container_width=True):
            with st.spinner(f"Rewriting {section_name}..."):
                result = rewrite_section(section_name, original, jd_text, missing_skills)
                st.session_state.rewritten_sections[section_name] = result
                st.rerun()

st.divider()

# --- Rewrite All ---
unrewritten = [s for s in rewrite_order if s in sections and s not in st.session_state.rewritten_sections]
if unrewritten:
    if st.button("🚀 Rewrite All Sections", type="primary", use_container_width=True):
        for section_name in unrewritten:
            with st.spinner(f"Rewriting {section_name}..."):
                result = rewrite_section(section_name, sections[section_name], jd_text, missing_skills)
                st.session_state.rewritten_sections[section_name] = result
        st.rerun()

# --- Download ---
if st.session_state.rewritten_sections:
    st.divider()
    st.markdown("### 📥 Download Rewritten Resume")
    
    # Build markdown
    md = f"# {r.get('contact', {}).get('name', 'Resume')}\n\n"
    if r.get("contact", {}).get("email"):
        md += f"📧 {r['contact']['email']}"
    if r.get("contact", {}).get("phone"):
        md += f" | 📱 {r['contact']['phone']}"
    md += "\n\n---\n\n"
    
    for section_name in rewrite_order:
        text = st.session_state.rewritten_sections.get(section_name, sections.get(section_name, ""))
        if text:
            md += f"## {section_name.title()}\n\n{text}\n\n"
    
    st.download_button(
        "📥 Download as Markdown",
        data=md,
        file_name="resume_optimized.md",
        mime="text/markdown",
        use_container_width=True,
    )

# --- Sidebar ---
with st.sidebar:
    st.markdown("### ✍️ Rewriter")
    total = len([s for s in rewrite_order if s in sections])
    done = len(st.session_state.rewritten_sections)
    st.progress(done / max(total, 1))
    st.caption(f"{done}/{total} sections rewritten")
    
    if missing_skills:
        st.markdown("**Missing skills to add:**")
        for s in missing_skills[:10]:
            st.markdown(f"- 🔴 {s}")
    
    render_sidebar_footer()
