"""ResumeMatch AI — ⚙️ Settings."""

import os
import streamlit as st

st.set_page_config(page_title="ResumeMatch AI — Settings", page_icon="📄", layout="wide")

from src.ui import check_auth, inject_css, render_header, render_sidebar_footer

if not check_auth():
    st.stop()

inject_css()
render_header()

st.markdown("### ⚙️ Settings")

provider = st.selectbox("Provider", ["Ollama Cloud", "OpenAI", "Anthropic", "Custom"], index=0)

defaults = {
    "Ollama Cloud": ("https://ollama.com/v1", ["mistral-large-3:675b", "deepseek-v3.1:671b", "qwen3-coder:480b", "gpt-oss:120b", "gpt-oss:20b"]),
    "OpenAI": ("https://api.openai.com/v1", ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"]),
    "Anthropic": ("https://api.anthropic.com/v1", ["claude-sonnet-4-20250514", "claude-3-5-haiku-20241022"]),
    "Custom": ("", []),
}

url, models = defaults[provider]

c1, c2 = st.columns(2)
with c1:
    base_url = st.text_input("Base URL", value=url) if provider == "Custom" else st.text_input("Base URL", value=url)
    model = st.text_input("Model", "") if provider == "Custom" else st.selectbox("Model", models)
with c2:
    api_key = st.text_input("API Key", type="password", value=os.getenv("LLM_API_KEY", ""))

if st.button("💾 Save", type="primary", use_container_width=True):
    if api_key: os.environ["LLM_API_KEY"] = api_key
    if base_url: os.environ["LLM_BASE_URL"] = base_url
    if model: os.environ["LLM_MODEL"] = model
    st.success("✅ Saved!")

st.divider()
st.markdown("### 📋 Current Config")
st.code(f"Provider: {provider}\nBase URL: {os.getenv('LLM_BASE_URL', url)}\nModel: {os.getenv('LLM_MODEL', 'mistral-large-3:675b')}\nAPI Key: {'●●●●' if os.getenv('LLM_API_KEY') else '⚠️ Not set'}")

with st.sidebar:
    render_sidebar_footer()
