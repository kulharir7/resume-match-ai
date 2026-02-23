"""Shared UI — auth, CSS, header, components."""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def check_auth():
    """Login gate. Returns True if authenticated."""
    if st.session_state.get("authenticated"):
        return True

    st.markdown("""<style>.stApp{background:#0a0a1a}#MainMenu,footer{visibility:hidden}</style>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; padding-top:60px;">
            <div style="font-size:4em; margin-bottom:8px;">📄</div>
            <div style="background:linear-gradient(135deg,#667eea,#764ba2,#f093fb);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                font-size:2.2em;font-weight:800;">ResumeMatch AI</div>
            <div style="color:#6e7681;font-size:0.9em;margin-bottom:30px;">ATS Resume Optimizer</div>
        </div>""", unsafe_allow_html=True)

        with st.form("login_form"):
            user = st.text_input("Username", placeholder="Enter username")
            pwd = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("🔓 Sign In", use_container_width=True, type="primary")
            if submitted:
                if user == os.getenv("APP_USER", "admin") and pwd == os.getenv("APP_PASS", "resume123"):
                    st.session_state.authenticated = True
                    st.session_state.username = user
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")

        st.markdown('<div style="text-align:center;color:#6e7681;font-size:0.8em;margin-top:16px;">Default: admin / resume123</div>', unsafe_allow_html=True)
    return False


def inject_css():
    """Premium dark theme."""
    st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    .stApp { background: #0a0a1a; font-family: 'Inter', sans-serif; }

    .hero-title {
        background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: 2em; font-weight: 800; display: inline;
    }
    .hero-badge {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white; font-size: 0.65em; padding: 2px 8px;
        border-radius: 20px; font-weight: 600; vertical-align: super;
    }

    .score-card {
        background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.06));
        border: 1px solid rgba(102,126,234,0.15); border-radius: 14px;
        padding: 20px; text-align: center;
    }
    .score-value {
        font-size: 2.5em; font-weight: 800;
        background: linear-gradient(135deg, #667eea, #764ba2);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .score-label { color: #6e7681; font-size: 0.85em; margin-top: 4px; }

    .match-good { color: #3fb950; }
    .match-warn { color: #d29922; }
    .match-bad { color: #f85149; }

    .skill-found {
        display: inline-block; background: rgba(35,134,54,0.15);
        border: 1px solid rgba(35,134,54,0.3); color: #3fb950;
        padding: 4px 12px; border-radius: 20px; font-size: 0.85em; margin: 3px;
    }
    .skill-missing {
        display: inline-block; background: rgba(248,81,73,0.12);
        border: 1px solid rgba(248,81,73,0.3); color: #f85149;
        padding: 4px 12px; border-radius: 20px; font-size: 0.85em; margin: 3px;
    }
    .skill-partial {
        display: inline-block; background: rgba(210,153,34,0.12);
        border: 1px solid rgba(210,153,34,0.3); color: #d29922;
        padding: 4px 12px; border-radius: 20px; font-size: 0.85em; margin: 3px;
    }

    .section-card {
        background: rgba(22,27,34,0.6); border: 1px solid rgba(48,54,61,0.5);
        border-radius: 12px; padding: 16px 20px; margin: 8px 0;
    }

    .suggestion-card {
        background: rgba(102,126,234,0.06); border: 1px solid rgba(102,126,234,0.15);
        border-radius: 10px; padding: 12px 16px; margin: 6px 0;
        color: #b1bac4; font-size: 0.9em;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117, #161b22);
        border-right: 1px solid rgba(48,54,61,0.4);
    }

    #MainMenu, footer { visibility: hidden; }
    header { visibility: visible !important; }
    [data-testid="stHeader"] { background: transparent !important; }
</style>""", unsafe_allow_html=True)


def render_header():
    st.markdown("""
    <div style="padding:8px 0 16px 0; border-bottom:1px solid rgba(102,126,234,0.15); margin-bottom:20px;">
        <span class="hero-title">📄 ResumeMatch AI</span>
        <span class="hero-badge">ATS OPTIMIZER</span>
        <div style="color:#6e7681; font-size:0.92em; margin-top:2px;">
            Paste job description → Upload resume → Get match score & AI-optimized resume
        </div>
    </div>""", unsafe_allow_html=True)


def render_sidebar_footer():
    st.divider()
    st.caption(f"👤 **{st.session_state.get('username', 'admin')}**")
    if st.button("🚪 Logout", use_container_width=True, key="logout_global"):
        st.session_state.authenticated = False
        st.rerun()


def score_color(score: int) -> str:
    """Return CSS class for score coloring."""
    if score >= 75:
        return "match-good"
    elif score >= 50:
        return "match-warn"
    return "match-bad"


def score_emoji(score: int) -> str:
    if score >= 75:
        return "✅"
    elif score >= 50:
        return "⚠️"
    return "❌"
