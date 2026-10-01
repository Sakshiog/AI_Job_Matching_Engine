import hashlib
import hmac
import html
import json
import re
from pathlib import Path

import pandas as pd
import streamlit as st
# --- HTML cards ko code block banne se rokta hai ---
_orig_markdown = st.markdown

def _clean_markdown(body, *args, **kwargs):
    if kwargs.get("unsafe_allow_html") and isinstance(body, str):
        body = "\n".join(line.strip() for line in body.splitlines() if line.strip())
    return _orig_markdown(body, *args, **kwargs)

st.markdown = _clean_markdown

from matching_engine import JobMatchingEngine
from resume_parser import extract_resume_text
from skill_extractor import extract_skills

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="AI Job Matching Engine",
    page_icon="🤖",
    layout="wide"
)


# =========================================================
# GLOBAL CSS
# =========================================================

st.markdown(
    """
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@600;700&family=Poppins:wght@400;500;600;700&display=swap');

    /* =====================================================
       GENERAL
       ===================================================== */

    :root, .stApp {
        color-scheme: light !important;
    }

    .stApp {
        background: #ffffff;
        font-family: 'Poppins', sans-serif;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    h1, h2, h3 {
        color: #111827 !important;
    }

    p, label, span {
        font-family: 'Poppins', sans-serif;
    }


    /* =====================================================
       HERO / HOME
       ===================================================== */

    .hero-title {
        text-align: center;
        font-size: 52px;
        font-weight: 700;
        color: #111827;
        margin-top: 10px;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        text-align: center;
        font-size: 22px;
        font-weight: 500;
        color: #2563eb;
        margin-bottom: 8px;
    }

    .home-title {
        text-align: center;
        font-size: 60px;
        font-weight: 700;
        color: #111827;
        margin-top: 40px;
        margin-bottom: 10px;
    }

    .home-subtitle {
        text-align: center;
        font-size: 23px;
        font-weight: 500;
        color: #2563eb;
        margin-bottom: 8px;
    }

    .home-tagline {
        text-align: center;
        font-family: 'Caveat', cursive;
        font-size: 28px;
        color: #64748b;
        margin-bottom: 35px;
    }


    /* =====================================================
       SECTION HEADINGS
       ===================================================== */

    .section-title {
        font-size: 26px;
        font-weight: 700;
        color: #111827;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    .section-subtitle {
        font-size: 14px;
        color: #64748b;
        margin-bottom: 20px;
    }

    /* Centered heading (Create Candidate Profile) */
    .center-title {
        text-align: center;
        font-size: 55px;
        font-weight: 700;
        color: #111827;
        margin-top: 15px;
        margin-bottom: 8px;
    }

    .center-subtitle {
        text-align: center;
        font-size: 35px;
        color: #64748b;
        margin-bottom: 25px;
    }


    /* =====================================================
       FEATURE CARDS
       ===================================================== */

    .feature-card {
        background: #eff6ff;
        border: 1px solid #dbeafe;
        border-radius: 14px;
        padding: 22px;
        min-height: 150px;
        margin-bottom: 15px;
    }

    .feature-icon {
        font-size: 30px;
        margin-bottom: 8px;
    }

    .feature-title {
        font-size: 17px;
        font-weight: 600;
        color: #111827;
        margin-bottom: 5px;
    }

    .feature-text {
        font-size: 13px;
        color: #64748b;
        line-height: 1.5;
    }


    /* =====================================================
       FORM LABELS
       ===================================================== */

    .stTextInput label,
    .stNumberInput label,
    .stSelectbox label,
    .stTextArea label,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] label,
    [data-testid="stWidgetLabel"] span {
        color: #111827 !important;
        font-weight: 700 !important;
        font-size: 16px !important;
    }


    /* =====================================================
       ALL INPUTS = LIGHT BLUE (text, number, password, select)
       ===================================================== */

    div[data-baseweb="input"],
    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"],
    div[data-baseweb="input"] input,
    div[data-baseweb="input"] input[type="number"],
    div[data-testid="stTextInputRootElement"],
    div[data-testid="stTextInputRootElement"] > div,
    div[data-testid="stNumberInputContainer"],
    div[data-testid="stNumberInputContainer"] > div,
    div[data-testid="stNumberInputContainer"] input,
    input[type="password"],
    div[data-baseweb="input"]:has(input[type="password"]),
    div[data-baseweb="input"]:has(input[type="password"]) > div,
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] > div > div,
    div[data-testid="stNumberInput"] button,
    div[data-baseweb="input"] button {
        background: #E0F2FE !important;
        background-color: #E0F2FE !important;
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        box-shadow: none !important;
    }

    div[data-baseweb="input"],
    div[data-baseweb="select"] > div {
        border: 1px solid #BAE6FD !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    /* Focus = thoda gehra light blue */
    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="input"]:focus-within > div,
    div[data-baseweb="input"]:focus-within div[data-baseweb="base-input"],
    div[data-baseweb="input"]:focus-within input,
    div[data-testid="stTextInputRootElement"]:focus-within,
    div[data-testid="stTextInputRootElement"]:focus-within > div,
    div[data-testid="stNumberInputContainer"]:focus-within,
    div[data-testid="stNumberInputContainer"]:focus-within > div,
    div[data-testid="stNumberInputContainer"]:focus-within input,
    div[data-baseweb="input"]:has(input[type="password"]):focus-within,
    div[data-baseweb="input"]:has(input[type="password"]):focus-within > div,
    div[data-baseweb="input"]:has(input[type="password"]):focus-within input,
    div[data-baseweb="select"]:focus-within,
    div[data-baseweb="select"]:focus-within > div,
    div[data-baseweb="select"]:focus-within > div > div {
        background: #BAE6FD !important;
        background-color: #BAE6FD !important;
    }

    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="select"]:focus-within > div {
        border: 2px solid #38BDF8 !important;
        box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.15) !important;
    }

    div[data-baseweb="input"] input::placeholder {
        color: #64748b !important;
        -webkit-text-fill-color: #64748b !important;
        opacity: 1 !important;
    }

    div[data-baseweb="select"] span {
        background: transparent !important;
        color: #111827 !important;
        font-size: 14px !important;
    }

    div[data-baseweb="select"] svg,
    div[data-baseweb="input"] button svg {
        fill: #374151 !important;
        color: #374151 !important;
    }

    /* Work Mode selectbox = light blue
       Paints everything inside the widget EXCEPT the label and the
       wrapper layers that contain the label (so the label area stays white). */
    .st-key-reg_work_mode *:not(:has(label)):not(label):not(label *):not(svg):not(path),
    [data-baseweb="select"],
    [data-baseweb="select"] *:not(svg):not(path) {
        background: #E0F2FE !important;
        background-color: #E0F2FE !important;
        background-image: none !important;
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        border-color: #1E293B !important;
        border-radius: 10px !important;
        box-shadow: none !important;
    }

    /* label + wrappers around the label stay clean/transparent */
    .st-key-reg_work_mode,
    .st-key-reg_work_mode *:has(label),
    .st-key-reg_work_mode label,
    .st-key-reg_work_mode label * {
        background: transparent !important;
        background-color: transparent !important;
        border-radius: 0 !important;
    }

    .st-key-reg_work_mode *:not(:has(label)):focus-within,
    [data-baseweb="select"]:focus-within,
    [data-baseweb="select"]:focus-within *:not(svg):not(path) {
        background: #BAE6FD !important;
        background-color: #BAE6FD !important;
    }

    .st-key-reg_work_mode svg,
    [data-baseweb="select"] svg {
        fill: #374151 !important;
        color: #374151 !important;
        background: transparent !important;
    }

    .st-key-reg_work_mode svg path[fill="none"],
    [data-baseweb="select"] svg path[fill="none"],
    .st-key-reg_work_mode svg rect,
    [data-baseweb="select"] svg rect {
        fill: none !important;
    }

    /* Dropdown list (Work Mode) */
    div[role="listbox"],
    div[role="option"] {
        background: #E0F2FE !important;
        background-color: #E0F2FE !important;
        color: #111827 !important;
        font-size: 14px !important;
    }

    div[role="listbox"] {
        border: 1px solid #BAE6FD !important;
    }

    div[role="option"]:hover {
        background: #BAE6FD !important;
        background-color: #BAE6FD !important;
    }


    /* =====================================================
       BUTTONS
       ===================================================== */

    .stButton > button {
        background: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #d1d5db !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        box-shadow: none !important;
    }

    .stButton > button:hover {
        background: #f8fafc !important;
        color: #111827 !important;
        border-color: #94a3b8 !important;
    }

    .stButton > button:focus,
    .stButton > button:active {
        background: #eff6ff !important;
        color: #111827 !important;
        border-color: #60a5fa !important;
        box-shadow: none !important;
    }


    /* =====================================================
       INDIGO BUTTONS (Create Profile + Back on register page)
       ===================================================== */

    .st-key-btn_create_profile .stButton > button,
    .st-key-btn_register_back .stButton > button {
        background: #4338CA !important;
        background-color: #4338CA !important;
        color: #ffffff !important;
        border: 1px solid #312E81 !important;
    }

    .st-key-btn_create_profile .stButton > button *,
    .st-key-btn_register_back .stButton > button * {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    .st-key-btn_create_profile .stButton > button:hover,
    .st-key-btn_register_back .stButton > button:hover,
    .st-key-btn_create_profile .stButton > button:focus,
    .st-key-btn_register_back .stButton > button:focus,
    .st-key-btn_create_profile .stButton > button:active,
    .st-key-btn_register_back .stButton > button:active {
        background: #3730A3 !important;
        background-color: #3730A3 !important;
        color: #ffffff !important;
        border-color: #312E81 !important;
    }


    /* =====================================================
       PROFILE / DASHBOARD CARDS
       ===================================================== */

    .profile-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 20px;
    }

    .profile-label {
        font-size: 12px;
        color: #64748b;
        margin-bottom: 3px;
    }

  .profile-value {
    font-size: 20px !important;
    color: #111827 !important;
    font-weight: 700 !important;
    margin-bottom: 12px !important;
}

/* Create Candidate Profile - Input Text */
.stTextInput input,
.stNumberInput input,
.stTextArea textarea {
    font-size: 18px !important;
    font-weight: 600 !important;
}

/* Create Candidate Profile - Dropdown Text */
.stSelectbox div[data-baseweb="select"] {
    font-size: 18px !important;
}

.stSelectbox div[data-baseweb="select"] > div {
    font-size: 18px !important;
    font-weight: 600 !important;
}

    .recommendation-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 15px;
    }

    .recommendation-title {
        font-size: 18px;
        font-weight: 600;
        color: #111827;
    }

    .recommendation-company {
        font-size: 14px;
        color: #2563eb;
        margin-top: 3px;
    }

    .recommendation-info {
        font-size: 13px;
        color: #64748b;
        margin-top: 8px;
    }

    .skill-gap-card {
        background: #eff6ff;
        border: 1px solid #dbeafe;
        border-radius: 12px;
        padding: 18px;
        margin-top: 12px;
    }


    /* =====================================================
       MOBILE
       ===================================================== */

    @media (max-width: 768px) {
        .hero-title,
        .home-title {
            font-size: 38px;
        }

        .hero-subtitle,
        .home-subtitle {
            font-size: 18px;
        }

        .home-tagline {
            font-size: 23px;
        }
    }


    /* =====================================================
       REGISTER PAGE - fit in ONE screen (no scrolling)
       Applies only when the register form is on screen.
       ===================================================== */

    .stApp:has(.st-key-reg_full_name) header[data-testid="stHeader"] {
        display: none !important;
    }

        /* whole register form inside ONE card/box (same as Sign In) */
    .stApp:has(.st-key-reg_full_name) .block-container {
        max-width: 1400px !important;
        width: 97% !important;
        height: fit-content !important;
        margin: 1.5vh auto 1vh auto !important;
        padding: clamp(12px, 2vh, 24px) clamp(20px, 3vw, 40px) clamp(14px, 2.2vh, 26px) !important;
        background: #F8FAFF !important;
        border: 2px solid #C7D2FE !important;
        border-radius: 22px !important;
        box-shadow: 0 12px 36px rgba(67, 56, 202, 0.14) !important;
    }

    .stApp:has(.st-key-reg_full_name) [data-testid="stVerticalBlock"] {
        gap: clamp(0.2rem, 2.4vh, 1.4rem) !important;
    }

    .stApp:has(.st-key-reg_full_name) .center-title {
        margin-top: 0 !important;
        margin-bottom: 4px !important;
    }

    .stApp:has(.st-key-reg_full_name) .center-subtitle {
        margin-bottom: clamp(6px, 1.5vh, 16px) !important;
    }

    .stApp:has(.st-key-reg_full_name) [data-testid="stWidgetLabel"] {
        margin-bottom: 2px !important;
        min-height: 0 !important;
    }

    .stApp:has(.st-key-reg_full_name) [data-testid="stWidgetLabel"] p,
    .stApp:has(.st-key-reg_full_name) [data-testid="stWidgetLabel"] label {
        font-size: clamp(14px, 2.1vh, 18px) !important;
    }

    .stApp:has(.st-key-reg_full_name) div[data-baseweb="input"] input {
        height: clamp(34px, 5.8vh, 52px) !important;
        min-height: clamp(34px, 5.8vh, 52px) !important;
        font-size: clamp(13px, 1.9vh, 16px) !important;
    }

    .stApp:has(.st-key-reg_full_name) div[data-baseweb="select"] > div {
        min-height: clamp(36px, 5.8vh, 52px) !important;
        font-size: clamp(13px, 1.9vh, 16px) !important;
    }

    .stApp:has(.st-key-reg_full_name) .stButton > button {
        min-height: clamp(38px, 5.8vh, 52px) !important;
        font-size: clamp(14px, 2vh, 17px) !important;
    }

    /* short screens (laptops): tighten a little more */
    @media (max-height: 780px) {
        .stApp:has(.st-key-reg_full_name) [data-testid="stVerticalBlock"] {
            gap: 0.2rem !important;
        }
        .stApp:has(.st-key-reg_full_name) [data-testid="stWidgetLabel"] p,
        .stApp:has(.st-key-reg_full_name) [data-testid="stWidgetLabel"] label {
            font-size: 14px !important;
        }
        .stApp:has(.st-key-reg_full_name) div[data-baseweb="input"] input {
            height: 32px !important;
            min-height: 32px !important;
        }
        .stApp:has(.st-key-reg_full_name) div[data-baseweb="select"] > div {
            min-height: 34px !important;
        }
    }


    /* =====================================================
       HOME PAGE - fill the screen, indigo buttons
       Applies only when the home page is on screen.
       ===================================================== */

    .stApp:has(.home-title) header[data-testid="stHeader"] {
        display: none !important;
    }

    .stApp:has(.home-title) .block-container {
        padding-top: 4vh !important;
        padding-bottom: 2vh !important;
    }

    .stApp:has(.home-title) .home-title {
        font-size: clamp(38px, 8.5vh, 72px) !important;
        margin-top: 2vh !important;
        margin-bottom: 1.5vh !important;
    }

    .stApp:has(.home-title) .home-subtitle {
        font-size: clamp(18px, 3vh, 28px) !important;
        margin-bottom: 1.5vh !important;
    }

    .stApp:has(.home-title) .home-tagline {
        font-size: clamp(22px, 3.8vh, 36px) !important;
        margin-bottom: 4vh !important;
    }

    .stApp:has(.home-title) [data-testid="stVerticalBlock"] {
        gap: clamp(0.5rem, 2.5vh, 1.6rem) !important;
    }

    /* Indigo main buttons */
    .st-key-btn_home_create .stButton > button,
    .st-key-btn_home_signin .stButton > button {
        background: #4338CA !important;
        background-color: #4338CA !important;
        color: #ffffff !important;
        border: 1px solid #312E81 !important;
        min-height: clamp(48px, 7vh, 66px) !important;
        font-size: clamp(16px, 2.4vh, 21px) !important;
        font-weight: 600 !important;
    }

    .st-key-btn_home_create .stButton > button *,
    .st-key-btn_home_signin .stButton > button * {
        color: #ffffff !important;
        font-size: clamp(16px, 2.4vh, 21px) !important;
    }

    .st-key-btn_home_create .stButton > button:hover,
    .st-key-btn_home_signin .stButton > button:hover,
    .st-key-btn_home_create .stButton > button:focus,
    .st-key-btn_home_signin .stButton > button:focus,
    .st-key-btn_home_create .stButton > button:active,
    .st-key-btn_home_signin .stButton > button:active {
        background: #3730A3 !important;
        background-color: #3730A3 !important;
        color: #ffffff !important;
        border-color: #312E81 !important;
    }

    /* Home buttons - indigo + BOLD text (robust selectors) */
    .st-key-btn_home_create button,
    .st-key-btn_home_signin button,
    .st-key-btn_home_create [data-testid="stBaseButton-secondary"],
    .st-key-btn_home_signin [data-testid="stBaseButton-secondary"] {
        background: #4338CA !important;
        background-color: #4338CA !important;
        color: #ffffff !important;
        border: 1px solid #312E81 !important;
        font-weight: 700 !important;
    }

    .st-key-btn_home_create button *,
    .st-key-btn_home_signin button *,
    .st-key-btn_home_create button p,
    .st-key-btn_home_signin button p {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    .st-key-btn_home_create button:hover,
    .st-key-btn_home_signin button:hover,
    .st-key-btn_home_create button:focus,
    .st-key-btn_home_signin button:focus,
    .st-key-btn_home_create button:active,
    .st-key-btn_home_signin button:active {
        background: #3730A3 !important;
        background-color: #3730A3 !important;
        color: #ffffff !important;
        border-color: #312E81 !important;
    }

    /* Feature cards - bigger */
    .stApp:has(.home-title) .feature-card {
        min-height: clamp(170px, 30vh, 320px) !important;
        padding: clamp(20px, 3.5vh, 36px) !important;
        border-radius: 18px !important;
        margin-top: 2vh;
    }

    .stApp:has(.home-title) .feature-icon {
        font-size: clamp(34px, 6vh, 56px) !important;
        margin-bottom: 1.5vh !important;
    }

    .stApp:has(.home-title) .feature-title {
        font-size: clamp(18px, 3vh, 26px) !important;
        margin-bottom: 1vh !important;
    }

    .stApp:has(.home-title) .feature-text {
        font-size: clamp(14px, 2.1vh, 18px) !important;
    }


    /* =====================================================
       SIGN IN PAGE - centered card, bigger, indigo buttons
       ===================================================== */

    .stApp:has(.login-title) header[data-testid="stHeader"] {
        display: none !important;
    }

    /* whole sign-in form inside ONE card/box */
    .stApp:has(.login-title) .block-container {
        max-width: 680px !important;
        width: 92% !important;
        height: fit-content !important;
        margin: 9vh auto 0 auto !important;
        padding: clamp(24px, 4vh, 44px) clamp(24px, 4vw, 48px) clamp(26px, 4.5vh, 48px) !important;
        background: #F8FAFF !important;
        border: 2px solid #C7D2FE !important;
        border-radius: 22px !important;
        box-shadow: 0 12px 36px rgba(67, 56, 202, 0.14) !important;
    }

    .stApp:has(.login-title) [data-testid="stVerticalBlock"] {
        gap: clamp(0.5rem, 2.6vh, 1.6rem) !important;
    }

    .stApp:has(.login-title) .center-title {
        margin-bottom: 4px !important;
    }

    .stApp:has(.login-title) .center-subtitle {
        margin-bottom: 3vh !important;
    }

    .stApp:has(.login-title) [data-testid="stWidgetLabel"] p,
    .stApp:has(.login-title) [data-testid="stWidgetLabel"] label {
        font-size: clamp(15px, 2.2vh, 19px) !important;
    }

    .stApp:has(.login-title) div[data-baseweb="input"] input {
        height: clamp(42px, 6.5vh, 58px) !important;
        min-height: clamp(42px, 6.5vh, 58px) !important;
        font-size: clamp(14px, 2vh, 17px) !important;
    }

    .st-key-btn_login_signin button,
    .st-key-btn_login_back button,
    .st-key-btn_login_save button {
        background: #4338CA !important;
        background-color: #4338CA !important;
        color: #ffffff !important;
        border: 1px solid #312E81 !important;
        font-weight: 700 !important;
        min-height: clamp(44px, 6.5vh, 58px) !important;
        font-size: clamp(15px, 2.2vh, 19px) !important;
    }

    .st-key-btn_login_signin button *,
    .st-key-btn_login_back button *,
    .st-key-btn_login_save button * {
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    .st-key-btn_login_signin button:hover,
    .st-key-btn_login_back button:hover,
    .st-key-btn_login_save button:hover,
    .st-key-btn_login_signin button:focus,
    .st-key-btn_login_back button:focus,
    .st-key-btn_login_save button:focus,
    .st-key-btn_login_signin button:active,
    .st-key-btn_login_back button:active,
    .st-key-btn_login_save button:active {
        background: #3730A3 !important;
        background-color: #3730A3 !important;
        color: #ffffff !important;
        border-color: #312E81 !important;
    }


    /* =====================================================
       RESUME UPLOADER - light blue dropzone, indigo browse button
       ===================================================== */

    [data-testid="stFileUploaderDropzone"] {
        background: #E5E7EB !important;
        background-color: #E5E7EB !important;
        border: 1px dashed #9CA3AF !important;
        border-radius: 10px !important;
    }

    [data-testid="stFileUploaderDropzone"] *:not(button):not(button *):not(svg):not(path) {
        background: transparent !important;
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
    }

    [data-testid="stFileUploaderDropzone"] button {
        background: #4338CA !important;
        background-color: #4338CA !important;
        color: #ffffff !important;
        border: 1px solid #312E81 !important;
        font-weight: 700 !important;
    }

    [data-testid="stFileUploaderDropzone"] button * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        background: transparent !important;
    }

    [data-testid="stFileUploaderDropzone"] button:hover {
        background: #3730A3 !important;
        background-color: #3730A3 !important;
    }

    /* uploaded file chip */
    [data-testid="stFileUploaderFile"] *:not(button):not(svg):not(path) {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
    }

    /* keep the register page on one screen: compact dropzone */
    .stApp:has(.st-key-reg_full_name) [data-testid="stFileUploaderDropzone"] {
        padding: 0.25rem 0.7rem !important;
        min-height: clamp(36px, 5.8vh, 52px) !important;
    }

    .stApp:has(.st-key-reg_full_name) [data-testid="stFileUploaderDropzone"] small,
    .stApp:has(.st-key-reg_full_name) [data-testid="stFileUploaderDropzoneInstructions"] small {
        display: none !important;
    }

    .stApp:has(.st-key-reg_full_name) [data-testid="stFileUploaderDropzone"] button {
        padding: 0.2rem 0.8rem !important;
        min-height: 0 !important;
    }

    /* download button on dashboard */
    .st-key-btn_resume_download button,
    .st-key-btn_resume_save button {
        background: #4338CA !important;
        color: #ffffff !important;
        border: 1px solid #312E81 !important;
        font-weight: 700 !important;
    }

    .st-key-btn_resume_download button *,
    .st-key-btn_resume_save button * {
        color: #ffffff !important;
        font-weight: 700 !important;
    }


    /* =====================================================
       RESUME UPLOADER - LIGHT GREY (key + testid + section based)
       Paints everything inside the uploader light grey except the label
       and the Browse/Upload button (indigo).
       ===================================================== */

    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploader"] section *:not(button):not(button *):not(svg):not(path),
    [class*="resume_upload"] section,
    [class*="resume_upload"] section *:not(button):not(button *):not(svg):not(path),
    [class*="resume_upload"] *:not(:has(label)):not(label):not(label *):not(button):not(button *):not(svg):not(path) {
        background: #E5E7EB !important;
        background-color: #E5E7EB !important;
        background-image: none !important;
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        border-color: #9CA3AF !important;
        border-radius: 10px !important;
        box-shadow: none !important;
    }

    [class*="resume_upload"],
    [class*="resume_upload"] *:has(label),
    [class*="resume_upload"] label,
    [class*="resume_upload"] label * {
        background: transparent !important;
        background-color: transparent !important;
        border-radius: 0 !important;
    }

    [class*="resume_upload"] button {
        background: #4338CA !important;
        background-color: #4338CA !important;
        color: #ffffff !important;
        border: 1px solid #312E81 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }

    [class*="resume_upload"] button *,
    [class*="resume_upload"] button svg,
    [class*="resume_upload"] button svg path {
        background: transparent !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        fill: #ffffff !important;
    }

    [class*="resume_upload"] button:hover {
        background: #3730A3 !important;
        background-color: #3730A3 !important;
    }

    /* limit text says 200MB (Streamlit default) - hide it, label shows our real limit */
    [data-testid="stFileUploaderDropzoneInstructions"] {
        display: none !important;
    }

        /* register page: title / subtitle / form ke beech ka gap kam */
    .stApp:has(.st-key-reg_full_name) .center-title {
        margin: 0 !important;
        line-height: 1.15 !important;
    }

    .stApp:has(.st-key-reg_full_name) .center-subtitle {
        margin: 0 !important;
        line-height: 1.2 !important;
    }

    .stApp:has(.st-key-reg_full_name) [data-testid="stElementContainer"]:has(.create-profile-box) {
        display: none !important;
    }

    .stApp:has(.st-key-reg_full_name) [data-testid="stElementContainer"]:has(.center-title) {
        margin-bottom: -0.6rem !important;
    }

    .stApp:has(.st-key-reg_full_name) [data-testid="stElementContainer"]:has(.center-subtitle) {
        margin-bottom: -0.8rem !important;
    }

        /* alert boxes ka text dark */
    [data-testid="stAlert"] *,
    [data-testid="stAlertContainer"] * {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
    }

    /* View Extracted Resume Text */
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary * {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        font-weight: 600 !important;
    }

    [data-testid="stExpander"] textarea {
        background: #F3F4F6 !important;
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
    }

    /* =====================================================
       DASHBOARD PROFILE CARDS - better look
       ===================================================== */

    .profile-card {
        background: linear-gradient(180deg, #F8FAFF 0%, #EEF2FF 100%) !important;
        border: 1.5px solid #C7D2FE !important;
        border-radius: 18px !important;
        padding: 22px 24px !important;
        height: 100% !important;
        box-shadow: 0 6px 18px rgba(67, 56, 202, 0.08) !important;
    }

    .profile-label {
        font-size: 12px !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        color: #6366F1 !important;
        font-weight: 600 !important;
        margin-bottom: 2px !important;
    }

    .profile-value {
        font-size: 17px !important;
        font-weight: 600 !important;
        color: #111827 !important;
        margin-bottom: 16px !important;
        word-break: break-word !important;
        line-height: 1.4 !important;
    }

    .profile-value:last-child {
        margin-bottom: 0 !important;
    }

    .skill-chip {
        display: inline-block;
        background: #E0E7FF;
        color: #3730A3;
        border: 1px solid #C7D2FE;
        border-radius: 999px;
        padding: 3px 12px;
        font-size: 13px;
        font-weight: 600;
        margin: 0 6px 6px 0;
    }

    /* teeno cards ki height barabar */
    .stApp:has(.profile-card) [data-testid="stColumn"],
    .stApp:has(.profile-card) [data-testid="stColumn"] > [data-testid="stVerticalBlock"],
    .stApp:has(.profile-card) [data-testid="stColumn"] [data-testid="stElementContainer"],
    .stApp:has(.profile-card) [data-testid="stColumn"] [data-testid="stMarkdownContainer"] {
        height: 100% !important;
    }

        /* =====================================================
       RECOMMENDED JOBS - better cards
       ===================================================== */

    .job-card {
        display: flex;
        align-items: center;
        gap: 18px;
        background: linear-gradient(180deg, #F8FAFF 0%, #EEF2FF 100%);
        border: 1.5px solid #C7D2FE;
        border-radius: 18px;
        padding: 18px 22px;
        margin-bottom: 14px;
        box-shadow: 0 6px 18px rgba(67, 56, 202, 0.08);
    }

    .job-rank {
        flex: 0 0 40px;
        height: 40px;
        border-radius: 50%;
        background: #4338CA;
        color: #ffffff;
        font-weight: 700;
        font-size: 17px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .job-main { flex: 1; min-width: 0; }

    .job-title {
        font-size: 19px;
        font-weight: 700;
        color: #111827;
    }

    .job-company {
        font-size: 15px;
        font-weight: 600;
        color: #4338CA;
        margin-top: 2px;
    }

    .job-meta {
        font-size: 13px;
        color: #64748b;
        margin-top: 4px;
    }

    .job-bar {
        height: 7px;
        background: #E0E7FF;
        border-radius: 999px;
        margin-top: 10px;
        overflow: hidden;
    }

    .job-bar-fill {
        height: 100%;
        background: #4338CA;
        border-radius: 999px;
    }

    .job-score { text-align: center; flex: 0 0 auto; }

    .job-score-num {
        font-size: 24px;
        font-weight: 700;
        color: #4338CA;
        line-height: 1.1;
    }

    .job-score-label {
        font-size: 12px;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# LOAD ENGINE
# =========================================================

@st.cache_resource
def load_engine():
    return JobMatchingEngine()


engine = load_engine()


# =========================================================
# AUTH FILE
# =========================================================

AUTH_FILE = Path(__file__).with_name("auth_store.json")


def _load_auth():
    if not AUTH_FILE.exists():
        return {}

    try:
        with open(AUTH_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_auth(data):
    with open(AUTH_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def _hash(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def set_password(candidate_id, password):
    data = _load_auth()
    data[candidate_id] = {"password_hash": _hash(password)}
    _save_auth(data)


def check_password(candidate_id, password):
    data = _load_auth()

    if candidate_id not in data:
        return False

    stored_hash = data[candidate_id].get("password_hash", "")
    return hmac.compare_digest(stored_hash, _hash(password))


# =========================================================
# RESUME STORAGE
# =========================================================

RESUME_DIR = Path(__file__).with_name("resumes")
ALLOWED_RESUME_TYPES = ["pdf", "docx", "doc"]
MAX_RESUME_MB = 5


def _safe_id(candidate_id):
    return re.sub(r"[^A-Za-z0-9_-]", "_", str(candidate_id).strip())


def get_resume_path(candidate_id):
    if not RESUME_DIR.exists():
        return None

    matches = sorted(RESUME_DIR.glob(f"{_safe_id(candidate_id)}.*"))
    return matches[0] if matches else None


def save_resume(candidate_id, uploaded_file):
    RESUME_DIR.mkdir(exist_ok=True)

    # remove any older resume of this candidate (could have a different extension)
    for old in RESUME_DIR.glob(f"{_safe_id(candidate_id)}.*"):
        old.unlink()

    ext = Path(uploaded_file.name).suffix.lower()
    target = RESUME_DIR / f"{_safe_id(candidate_id)}{ext}"

    with open(target, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return target


def resume_too_large(uploaded_file):
    return uploaded_file.size > MAX_RESUME_MB * 1024 * 1024


# =========================================================
# SESSION STATE
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "candidate_id" not in st.session_state:
    st.session_state.candidate_id = None

if "setup_password_for" not in st.session_state:
    st.session_state.setup_password_for = None


def go(page):
    st.session_state.page = page
    st.rerun()


# =========================================================
# HOME PAGE
# =========================================================

def home_page():

    st.markdown(
        """
        <div class="home-title">AI Job Matching Engine</div>
        <div class="home-subtitle">AI-Powered Job Recommendations for Your Career</div>
        <div class="home-tagline">Your Skills + Experience + Preferences = Better Opportunities</div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("➕ Create Candidate Profile", key="btn_home_create", use_container_width=True):
            go("register")

    with col2:
        if st.button("🔐 Sign In", key="btn_home_signin", use_container_width=True):
            go("login")

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🎯</div>
                <div class="feature-title">Smart Matching</div>
                <div class="feature-text">
                    Matches your skills and preferences with suitable jobs.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🧠</div>
                <div class="feature-title">AI Recommendations</div>
                <div class="feature-text">
                    Uses machine learning techniques to generate recommendations.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Skill Insights</div>
                <div class="feature-text">
                    Understand your skill gaps and improve your job profile.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# REGISTER PAGE
# =========================================================

def register_page():

    st.markdown(
        '<div class="center-title">Create Candidate Profile</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="center-subtitle">Enter your details to get personalized job recommendations.</div>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # CREATE PROFILE BOX
    st.markdown('<div class="create-profile-box">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:

        full_name = st.text_input(
            "Full Name",
            key="reg_full_name",
            placeholder="Enter your full name"
        )

        candidate_id = st.text_input(
            "Candidate ID",
            key="reg_candidate_id",
            placeholder="Enter candidate ID"
        )

        education = st.text_input(
            "Education",
            key="reg_education",
            placeholder="e.g. B.Tech CSE"
        )

        experience = st.number_input(
            "Experience (Years)",
            key="reg_experience",
            min_value=0.0,
            max_value=50.0,
            value=0.0,
            step=0.1
        )

        preferred_role = st.text_input(
            "Preferred Role",
            key="reg_role",
            placeholder="e.g. AI Developer"
        )

        resume_file = st.file_uploader(
            "Upload Resume (PDF/DOCX, max 5 MB)",
            type=ALLOWED_RESUME_TYPES,
            key="resume_upload",
            help=f"PDF or Word file, up to {MAX_RESUME_MB} MB"
        )

    with col2:

        preferred_location = st.text_input(
            "Preferred Location",
            key="reg_location",
            placeholder="e.g. Jaipur"
        )

        work_mode = st.selectbox(
            "Work Mode",
            ["Remote", "Hybrid", "On-site"],
            key="reg_work_mode"
        )

        expected_salary = st.number_input(
            "Expected Salary (₹)",
            key="reg_salary",
            min_value=0,
            value=0,
            step=10000
        )

        skills = st.text_input(
            "Skills",
            key="reg_skills",
            placeholder="e.g. Python, SQL, Machine Learning"
        )

        password = st.text_input(
            "Create Password",
            type="password",
            key="reg_password",
            placeholder="Create your password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="reg_confirm_password",
            placeholder="Re-enter your password"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "Create Profile",
            key="btn_create_profile",
            use_container_width=True
        ):

            if not full_name.strip():
                st.error("Please enter your full name.")

            elif not candidate_id.strip():
                st.error("Please enter Candidate ID.")

            elif not education.strip():
                st.error("Please enter your education.")

            elif not preferred_role.strip():
                st.error("Please enter your preferred role.")

            elif not preferred_location.strip():
                st.error("Please enter your preferred location.")

            elif not skills.strip():
                st.error("Please enter your skills.")

            elif not password:
                st.error("Please create a password.")

            elif password != confirm_password:
                st.error("Passwords do not match.")

            elif resume_file is not None and resume_too_large(resume_file):
                st.error(
                    f"Resume must be smaller than {MAX_RESUME_MB} MB."
                )

            else:

                try:

                    existing = engine.candidate_exists(
                        candidate_id.strip()
                    )

                    if existing:

                        st.error("Candidate ID already exists.")

                    else:

                        engine.save_candidate(
                            candidate_id=candidate_id.strip(),
                            name=full_name.strip(),
                            education=education.strip(),
                            experience=experience,
                            preferred_role=preferred_role.strip(),
                            location=preferred_location.strip(),
                            work_mode=work_mode,
                            expected_salary=expected_salary,
                            skills=skills.strip()
                        )

                        set_password(
                            candidate_id.strip(),
                            password
                        )

                        if resume_file is not None:
                            save_resume(
                                candidate_id.strip(),
                                resume_file
                            )

                        st.session_state.candidate_id = (
                            candidate_id.strip()
                        )

                        st.success(
                            "Profile created successfully!"
                        )

                        go("dashboard")

                except Exception as e:

                    st.error(
                        f"Unable to create profile: {e}"
                    )

    with c2:

        if st.button(
            "← Back",
            key="btn_register_back",
            use_container_width=True
        ):
            go("home")

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )


# =========================================================
# LOGIN PAGE
# =========================================================

def login_page():

    st.markdown(
        '<div class="center-title login-title">Sign In</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="center-subtitle">Sign in to view your personalized job recommendations.</div>',
        unsafe_allow_html=True
    )

    candidate_id = st.text_input(
        "Candidate ID",
        placeholder="Enter your candidate ID"
    )

    password = st.text_input(
        "Password",
        type="password",
        placeholder="Enter your password"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:

        if st.button("Sign In", key="btn_login_signin", use_container_width=True):

            candidate_id = candidate_id.strip()

            if not candidate_id:
                st.error("Please enter Candidate ID.")

            elif not password:
                st.error("Please enter password.")

            else:

                try:

                    candidate = engine.get_candidate(candidate_id)

                    if candidate is None:
                        st.error("Candidate ID not found.")

                    else:

                        auth_data = _load_auth()

                        if candidate_id not in auth_data:

                            st.session_state.setup_password_for = candidate_id
                            st.rerun()

                        elif check_password(candidate_id, password):

                            st.session_state.candidate_id = candidate_id

                            go("dashboard")

                        else:

                            st.error("Incorrect password.")

                except Exception as e:
                    st.error(f"Unable to sign in: {e}")

    with c2:

        if st.button("← Back", key="btn_login_back", use_container_width=True):
            st.session_state.setup_password_for = None
            go("home")

    # ----- Password setup (for candidates without a password) -----

    setup_id = st.session_state.get("setup_password_for")

    if setup_id:

        st.markdown("<br>", unsafe_allow_html=True)

        st.warning(
            f"No password is set for '{setup_id}'. "
            "Please create a password below."
        )

        new_password = st.text_input(
            "Create Password",
            type="password",
            key="login_create_password",
            placeholder="Create password"
        )

        confirm_new_password = st.text_input(
            "Confirm Password",
            type="password",
            key="login_confirm_password",
            placeholder="Confirm password"
        )

        if st.button("Save Password", key="btn_login_save", use_container_width=True):

            if not new_password:
                st.error("Please create a password.")

            elif new_password != confirm_new_password:
                st.error("Passwords do not match.")

            else:

                set_password(setup_id, new_password)
                st.session_state.setup_password_for = None

                st.success(
                    "Password created successfully. "
                    "Please sign in again."
                )


# =========================================================
# FIND METHOD
# =========================================================

def find_method(obj, names):

    for name in names:

        if hasattr(obj, name):
            method = getattr(obj, name)

            if callable(method):
                return method

    return None


# =========================================================
# RECOMMENDATIONS
# =========================================================

def _score_percent(row):
    preferred = ["match_score", "score", "similarity", "match", "final_score"]
    keys = [k for k in preferred if k in row.index]
    keys += [
        k for k in row.index
        if k not in keys and any(w in str(k).lower() for w in ("score", "match", "similar"))
    ]

    for k in keys:
        try:
            v = float(row[k])
        except (TypeError, ValueError):
            continue

        if pd.isna(v):
            continue

        if v <= 1:
            v *= 100

        return max(0, min(100, round(v)))

    return None


def show_recommendations(candidate_id):

    method = find_method(
        engine,
        [
            "recommend_jobs",
            "get_recommendations",
            "recommend",
            "match_jobs",
            "get_job_recommendations"
        ]
    )

    if method is None:
        st.info("Recommendation method is not available.")
        return

    try:

        recommendations = method(candidate_id)

        if recommendations is None:
            st.info("No recommendations found.")
            return

        if not isinstance(recommendations, pd.DataFrame):
            st.write(recommendations)
            return

        if recommendations.empty:
            st.info("No recommendations found.")
            return

        st.markdown(
            '<div class="section-title">Recommended Jobs</div>',
            unsafe_allow_html=True
        )

        for rank, (_, row) in enumerate(recommendations.head(10).iterrows(), start=1):

            title = row.get("job_title", row.get("title", "Job Opportunity"))
            company = row.get("company", "")
            pct = _score_percent(row)

            meta = []
            for key in ("location", "work_mode", "job_type"):
                val = row.get(key, "")
                if val is not None and str(val).strip() and str(val) != "nan":
                    meta.append(html.escape(str(val)))

            meta_html = (
                '<div class="job-meta">' + " &bull; ".join(meta) + "</div>"
                if meta else ""
            )

            score_html = (
                f'<div class="job-score"><div class="job-score-num">{pct}%</div>'
                f'<div class="job-score-label">Match</div></div>'
                if pct is not None else ""
            )

            bar_html = (
                f'<div class="job-bar"><div class="job-bar-fill" style="width:{pct}%"></div></div>'
                if pct is not None else ""
            )

            st.markdown(
                f'<div class="job-card">'
                f'<div class="job-rank">{rank}</div>'
                f'<div class="job-main">'
                f'<div class="job-title">{html.escape(str(title))}</div>'
                f'<div class="job-company">{html.escape(str(company))}</div>'
                f'{meta_html}{bar_html}'
                f'</div>'
                f'{score_html}'
                f'</div>',
                unsafe_allow_html=True
            )

    except Exception as e:

        st.warning(f"Could not load recommendations: {e}")

# =========================================================
# SKILL GAP
# =========================================================

def skill_gap_section(candidate_id):

    method = find_method(
        engine,
        [
            "skill_gap_analysis",
            "get_skill_gaps",
            "skill_gap"
        ]
    )

    if method is None:
        return

    try:

        result = method(candidate_id)

        if result is None:
            return

        st.markdown(
            '<div class="section-title">Skill Gap Insights</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="skill-gap-card">
                {html.escape(str(result))}
            </div>
            """,
            unsafe_allow_html=True
        )

    except Exception:
        pass


# =========================================================
# CANDIDATE RANKING
# =========================================================

def candidate_ranking_section():

    candidate_id = st.session_state.get("candidate_id")

    if not candidate_id:
        return

    method = find_method(
        engine,
        [
            "rank_candidate",
            "get_candidate_ranking",
            "get_candidate_rankings",
            "candidate_ranking",
            "get_ranking",
            "rank_candidates"
        ]
    )

    if method is None:
        return

    try:

        result = method(candidate_id)

        if result is None:
            return

        st.markdown(
            '<div class="section-title">Candidate Ranking</div>',
            unsafe_allow_html=True
        )

        if isinstance(result, pd.DataFrame):

            if result.empty:
                return

            st.dataframe(result.head(10), use_container_width=True)

        else:
            st.markdown(
                f"""
                <div class="skill-gap-card">
                    {html.escape(str(result))}
                </div>
                """,
                unsafe_allow_html=True
            )

    except Exception:
        pass



# =========================================================
# MATCHING VISUALIZATION
# =========================================================

def matching_visualization_section(candidate_id):

    st.markdown(
        '<div class="section-title">Matching Insights</div>',
        unsafe_allow_html=True
    )

    try:

        recommendations = engine.get_recommendations(
            candidate_id,
            top_n=10
        )

        if recommendations is None:
            st.info("No matching data available.")
            return

        if not isinstance(recommendations, pd.DataFrame):
            st.info("No matching data available.")
            return

        if recommendations.empty:
            st.info("No matching data available.")
            return

        score_column = None

        for column in [
            "realtime_score",
            "match_score",
            "score"
        ]:
            if column in recommendations.columns:
                score_column = column
                break

        if score_column is None:
            st.info("Match score data is not available.")
            return

        chart_data = recommendations[
            ["job_title", score_column]
        ].copy()

        chart_data[score_column] = pd.to_numeric(
            chart_data[score_column],
            errors="coerce"
        )

        chart_data = chart_data.dropna()

        if chart_data.empty:
            st.info("No valid match scores available.")
            return

        chart_data = chart_data.set_index(
            "job_title"
        )

        st.bar_chart(
            chart_data[score_column]
        )

    except Exception as e:

        st.warning(
            f"Could not load matching visualization: {e}"
        )

# =========================================================
# RESUME SECTION (dashboard)
# =========================================================

def resume_section(candidate_id):

    st.markdown(
        '<div class="section-title">Resume</div>',
        unsafe_allow_html=True
    )

    current = get_resume_path(candidate_id)

    if current is not None:

        c1, c2 = st.columns([3, 1])

        with c1:
            st.markdown(
                f'''
                <div class="profile-card">
                    <div class="profile-label">Uploaded resume</div>
                    <div class="profile-value">{html.escape(current.name)}</div>
                </div>
                ''',
                unsafe_allow_html=True
            )

        with c2:
            with open(current, "rb") as f:
                st.download_button(
                    "⬇ Download",
                    data=f.read(),
                    file_name=current.name,
                    key="btn_resume_download",
                    use_container_width=True
                )



        # =====================================================
        # RESUME PARSING + AUTOMATIC SKILL EXTRACTION
        # =====================================================

        try:

            resume_text = extract_resume_text(current)

            if resume_text:

                extracted_skills = extract_skills(resume_text)

                st.markdown(
                    '<div class="section-title">Resume Analysis</div>',
                    unsafe_allow_html=True
                )

                if extracted_skills:

                    skills_display = ", ".join(
                        skill.title()
                        for skill in extracted_skills
                    )

                    st.success(
                        f"Automatically Detected Skills: {skills_display}"
                    )

                else:

                    st.info(
                        "No matching skills were detected from the resume."
                    )

                with st.expander("View Extracted Resume Text"):

                    st.text_area(
                        "Resume Content",
                        resume_text,
                        height=300,
                        label_visibility="collapsed"
                    )

            else:

                st.warning(
                    "Resume was uploaded, but no readable text was found."
                )

        except Exception as e:

            st.error(
                f"Resume parsing failed: {e}"
            )

    else:

        st.info("No resume uploaded yet.")

    # =====================================================
    # UPLOAD / REPLACE RESUME
    # =====================================================

    new_resume = st.file_uploader(
        "Upload / Replace Resume (PDF/DOCX, max 5 MB)",
        type=ALLOWED_RESUME_TYPES,
        key="dashboard_resume_upload",
        help=f"PDF or Word file, up to {MAX_RESUME_MB} MB"
    )

    if new_resume is not None:

        if st.button("Save Resume", key="btn_resume_save"):

            if resume_too_large(new_resume):

                st.error(
                    f"Resume must be smaller than {MAX_RESUME_MB} MB."
                )

            else:

                save_resume(candidate_id, new_resume)

                st.success(
                    "Resume saved successfully."
                )

                st.rerun()

def profile_card(items):
    rows = ""

    for label, value in items:
        if label == "Skills":
            chips = "".join(
                f'<span class="skill-chip">{html.escape(s.strip())}</span>'
                for s in str(value).split(",") if s.strip()
            )
            value_html = f'<div class="profile-value">{chips or "-"}</div>'
        else:
            text = html.escape(str(value)) if str(value).strip() else "-"
            value_html = f'<div class="profile-value">{text}</div>'

        rows += f'<div class="profile-label">{html.escape(label)}</div>{value_html}'

    st.markdown(
        f'<div class="profile-card">{rows}</div>',
        unsafe_allow_html=True
    )


# =========================================================
# DASHBOARD PAGE
# =========================================================

def dashboard_page():

    candidate_id = st.session_state.get("candidate_id")

    if not candidate_id:
        go("login")
        return

    # ---------------------------------------------------------
    # LOAD CANDIDATE
    # ---------------------------------------------------------

    try:
        candidate = engine.get_candidate_profile(candidate_id)
    except Exception as e:
        st.error(f"Unable to load candidate profile: {e}")
        return

    if candidate is None:
        st.error("Candidate profile not found.")

        if st.button("Back to Home"):
            go("home")

        return

    # ---------------------------------------------------------
    # HERO
    # ---------------------------------------------------------

    st.markdown(
        '<div class="hero-title">AI Job Matching Engine</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="hero-subtitle">Your Personalized Career Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # CANDIDATE PROFILE
    # ---------------------------------------------------------

    st.markdown(
        '<div class="section-title">Candidate Profile</div>',
        unsafe_allow_html=True
    )

    # Convert candidate to dictionary

    if isinstance(candidate, dict):
        profile_data = candidate

    elif hasattr(candidate, "to_dict"):
        profile_data = candidate.to_dict()

    else:
        try:
            profile_data = dict(candidate)
        except Exception:
            profile_data = {}

    # ---------------------------------------------------------
    # GET PROFILE VALUE
    # ---------------------------------------------------------

    def get_value(*keys, default=""):

        for key in keys:

            if key in profile_data:

                value = profile_data[key]

                if pd.isna(value):
                    return default

                return value

        return default

    # ---------------------------------------------------------
    # PROFILE CARDS
    # ---------------------------------------------------------

    p1, p2, p3 = st.columns(3)

    # ---------------------------------------------------------
    # CARD 1
    # ---------------------------------------------------------

    with p1:

        st.markdown(
            f"""
            <div class="profile-card">

                <div class="profile-label">
                    Candidate ID
                </div>

                <div class="profile-value">
                    {html.escape(str(
                        get_value(
                            "candidate_id",
                            default=candidate_id
                        )
                    ))}
                </div>

                <div class="profile-label">
                    Name
                </div>

                <div class="profile-value">
                    {html.escape(str(
                        get_value(
                            "name",
                            "full_name"
                        )
                    ))}
                </div>

                <div class="profile-label">
                    Education
                </div>

                <div class="profile-value">
                    {html.escape(str(
                        get_value(
                            "education"
                        )
                    ))}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # ---------------------------------------------------------
    # CARD 2
    # ---------------------------------------------------------

    with p2:

        st.markdown(
            f"""
            <div class="profile-card">

                <div class="profile-label">
                    Experience
                </div>

                <div class="profile-value">
                    {html.escape(str(
                        get_value(
                            "experience",
                            default="0"
                        )
                    ))} years
                </div>

                <div class="profile-label">
                    Preferred Role
                </div>

                <div class="profile-value">
                    {html.escape(str(
                        get_value(
                            "preferred_role",
                            "role"
                        )
                    ))}
                </div>

                <div class="profile-label">
                    Location
                </div>

                <div class="profile-value">
                    {html.escape(str(
                        get_value(
                            "location",
                            "preferred_location"
                        )
                    ))}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # ---------------------------------------------------------
    # CARD 3
    # ---------------------------------------------------------

    with p3:

        st.markdown(
            f"""
            <div class="profile-card">

                <div class="profile-label">
                    Work Mode
                </div>

                <div class="profile-value">
                    {html.escape(str(
                        get_value(
                            "work_mode"
                        )
                    ))}
                </div>

                <div class="profile-label">
                    Expected Salary
                </div>

                <div class="profile-value">
                    ₹ {html.escape(str(
                        get_value(
                            "expected_salary",
                            default="0"
                        )
                    ))}
                </div>

                <div class="profile-label">
                    Skills
                </div>

                <div class="profile-value">
                    {html.escape(str(
                        get_value(
                            "skills"
                        )
                    ))}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # =========================================================
    # RESUME
    # =========================================================

    resume_section(candidate_id)

    # =========================================================
    # UPDATE SKILLS FROM RESUME
    # =========================================================

    current_resume = get_resume_path(candidate_id)

    if current_resume is not None:

        try:
            engine.update_skills_from_resume(
                candidate_id,
                current_resume
            )
        except Exception:
            pass

    # =========================================================
    # RECOMMENDED JOBS
    # =========================================================

    show_recommendations(candidate_id)

    # =========================================================
    # SKILL GAP
    # =========================================================

    skill_gap_section(candidate_id)

    # =========================================================
    # CANDIDATE RANKING
    # =========================================================

    candidate_ranking_section()

    # =========================================================
    # MATCHING VISUALIZATION
    # =========================================================

    matching_visualization_section(candidate_id)

    # =========================================================
    # LOGOUT
    # =========================================================

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button(
        "Logout",
        use_container_width=True
    ):
        st.session_state.candidate_id = None
        go("home")


# =========================================================
# PAGE ROUTER
# =========================================================

if st.session_state.page == "home":
    home_page()

elif st.session_state.page == "register":
    register_page()

elif st.session_state.page == "login":
    login_page()

elif st.session_state.page == "dashboard":
    dashboard_page()

else:
    go("home")