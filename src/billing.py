"""Billing & Usage — Freemium gating with Razorpay integration."""

import os
import json
import time
import hashlib
import streamlit as st
from pathlib import Path

# --- Constants ---
FREE_ANALYSES = 2
DATA_DIR = Path("data/users")

# --- Razorpay Config ---
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_DEMO1234567890")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
RAZORPAY_PLAN_AMOUNT = int(os.getenv("RAZORPAY_PLAN_AMOUNT", "9900"))  # paise (9900 = ₹99)
RAZORPAY_CURRENCY = "INR"


def _user_file(username: str) -> Path:
    """Get user data file path."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    safe = hashlib.md5(username.encode()).hexdigest()
    return DATA_DIR / f"{safe}.json"


def _load_user(username: str) -> dict:
    """Load user data from disk."""
    fp = _user_file(username)
    if fp.exists():
        return json.loads(fp.read_text())
    return {
        "username": username,
        "plan": "free",
        "analyses_used": 0,
        "created_at": time.time(),
        "payment_id": None,
    }


def _save_user(username: str, data: dict):
    """Save user data to disk."""
    fp = _user_file(username)
    fp.write_text(json.dumps(data, indent=2))


def get_usage(username: str) -> dict:
    """Get current usage stats."""
    data = _load_user(username)
    return {
        "plan": data["plan"],
        "used": data["analyses_used"],
        "limit": FREE_ANALYSES if data["plan"] == "free" else 999999,
        "remaining": max(0, FREE_ANALYSES - data["analyses_used"]) if data["plan"] == "free" else 999999,
        "is_pro": data["plan"] == "pro",
    }


def increment_usage(username: str):
    """Count +1 analysis."""
    data = _load_user(username)
    data["analyses_used"] = data.get("analyses_used", 0) + 1
    _save_user(username, data)


def can_analyze(username: str) -> bool:
    """Check if user can run another analysis."""
    usage = get_usage(username)
    return usage["is_pro"] or usage["remaining"] > 0


def activate_pro(username: str, payment_id: str = "demo"):
    """Activate pro plan."""
    data = _load_user(username)
    data["plan"] = "pro"
    data["payment_id"] = payment_id
    data["upgraded_at"] = time.time()
    _save_user(username, data)


def render_usage_badge():
    """Show usage badge in sidebar."""
    username = st.session_state.get("username", "guest")
    usage = get_usage(username)

    if usage["is_pro"]:
        st.markdown("""
        <div style="background:linear-gradient(135deg,#667eea,#764ba2);
            border-radius:10px; padding:10px 14px; margin:8px 0; text-align:center;">
            <div style="color:white; font-weight:700; font-size:0.95em;">⭐ PRO Plan</div>
            <div style="color:rgba(255,255,255,0.7); font-size:0.75em;">Unlimited analyses</div>
        </div>""", unsafe_allow_html=True)
    else:
        remaining = usage["remaining"]
        color = "#3fb950" if remaining > 0 else "#f85149"
        st.markdown(f"""
        <div style="background:rgba(22,27,34,0.8); border:1px solid rgba(48,54,61,0.5);
            border-radius:10px; padding:10px 14px; margin:8px 0; text-align:center;">
            <div style="color:{color}; font-weight:700; font-size:0.95em;">
                {remaining}/{FREE_ANALYSES} Free Analyses Left
            </div>
            <div style="color:#6e7681; font-size:0.75em;">Upgrade for unlimited</div>
        </div>""", unsafe_allow_html=True)


def render_paywall():
    """Show paywall when free tier exhausted."""
    st.markdown("""
    <div style="text-align:center; padding:40px 20px;">
        <div style="font-size:3em; margin-bottom:12px;">🔒</div>
        <div style="background:linear-gradient(135deg,#667eea,#764ba2,#f093fb);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
            font-size:1.8em; font-weight:800;">Free Limit Reached</div>
        <div style="color:#6e7681; font-size:1em; margin:12px 0 24px 0;">
            You've used your 2 free analyses. Upgrade to Pro for unlimited access.
        </div>
    </div>""", unsafe_allow_html=True)

    render_pricing_card()


def render_pricing_card():
    """Show pricing + Razorpay button."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background:linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.08));
            border:2px solid rgba(102,126,234,0.3); border-radius:16px; padding:30px; text-align:center;">
            <div style="color:#667eea; font-weight:700; font-size:0.85em; letter-spacing:2px;">PRO PLAN</div>
            <div style="margin:12px 0;">
                <span style="color:white; font-size:2.5em; font-weight:800;">₹99</span>
                <span style="color:#6e7681; font-size:0.9em;">/month</span>
            </div>
            <div style="color:#b1bac4; font-size:0.9em; text-align:left; padding:0 20px;">
                ✅ Unlimited resume analyses<br>
                ✅ AI Resume Rewriter<br>
                ✅ ATS Simulator (detailed)<br>
                ✅ PDF download of optimized resume<br>
                ✅ Priority support<br>
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Razorpay checkout button
        razorpay_html = f"""
        <div style="text-align:center;">
            <form>
                <script src="https://checkout.razorpay.com/v1/payment-button.js"
                    data-payment_button_id="DEMO_BUTTON"
                    data-key="{RAZORPAY_KEY_ID}"
                    data-amount="{RAZORPAY_PLAN_AMOUNT}"
                    data-currency="{RAZORPAY_CURRENCY}"
                    data-name="ResumeMatch AI"
                    data-description="Pro Plan — Monthly"
                    data-prefill.name=""
                    data-prefill.email=""
                    data-theme.color="#667eea">
                </script>
            </form>
        </div>
        """

        # For demo: use a Streamlit button instead of real Razorpay
        if st.button("💳 Upgrade to Pro — ₹99/month", type="primary", use_container_width=True):
            _show_razorpay_checkout()


def _show_razorpay_checkout():
    """Show Razorpay checkout (demo mode)."""
    username = st.session_state.get("username", "guest")

    st.markdown("---")
    st.markdown("### 💳 Payment (Demo Mode)")
    st.info("🧪 **Demo Mode** — No real payment. Click 'Complete Payment' to simulate.")

    with st.form("payment_form"):
        st.text_input("Name", value=username, disabled=True)
        email = st.text_input("Email", placeholder="your@email.com")
        st.markdown(f"""
        <div style="background:rgba(102,126,234,0.1); border:1px solid rgba(102,126,234,0.2);
            border-radius:8px; padding:12px; margin:8px 0;">
            <div style="color:white; font-weight:600;">Order Summary</div>
            <div style="color:#b1bac4; font-size:0.9em; margin-top:4px;">
                ResumeMatch AI Pro — ₹99/month
            </div>
        </div>""", unsafe_allow_html=True)

        if st.form_submit_button("✅ Complete Payment (Demo)", use_container_width=True, type="primary"):
            # Demo: activate immediately
            demo_payment_id = f"pay_demo_{int(time.time())}"
            activate_pro(username, demo_payment_id)
            st.session_state.is_pro = True
            st.success(f"🎉 Payment successful! Payment ID: {demo_payment_id}")
            st.balloons()
            time.sleep(1)
            st.rerun()
