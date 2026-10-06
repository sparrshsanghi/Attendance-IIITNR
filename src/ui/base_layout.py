import streamlit as st

def style_background_home():
    st.markdown("""
    <style>
        .stApp {
            background:
                radial-gradient(1200px 600px at 10% -10%, #c7f0ff 0%, transparent 60%),
                radial-gradient(1000px 500px at 100% 0%, #ffe9cc 0%, transparent 55%),
                linear-gradient(145deg, #f4fbff 0%, #eef6fb 55%, #e8f2f7 100%) !important;
        }
        .stApp div[data-testid="stColumn"] {
            background: rgba(255, 255, 255, 0.82) !important;
            border: 1px solid rgba(26, 55, 77, 0.08) !important;
            box-shadow: 0 12px 40px rgba(12, 42, 62, 0.08) !important;
            padding: 2.2rem !important;
            border-radius: 1.4rem !important;
            backdrop-filter: blur(3px);
            animation: riseIn 0.7s ease-out both;
        }

        .stApp div[data-testid="stColumn"]:hover {
            transform: translateY(-2px);
            transition: transform 0.22s ease;
        }
    </style>
    """, unsafe_allow_html=True)

def style_background_dashboard():
    st.markdown("""
    <style>
        .stApp {
            background:
                radial-gradient(900px 500px at 0% 0%, #dff6ff 0%, transparent 52%),
                radial-gradient(800px 450px at 100% 10%, #ffeed9 0%, transparent 50%),
                linear-gradient(180deg, #f6fbff 0%, #edf5fa 100%) !important;
        }
    </style>
    """, unsafe_allow_html=True)

def style_base_layout():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

        :root {
            --brand-700: #145a75;
            --brand-600: #1f6f8b;
            --brand-500: #2f88a7;
            --brand-100: #e5f5fb;
            --ink-900: #123047;
            --ink-700: #2c4b61;
            --ink-500: #5f7383;
            --surface-0: #ffffff;
            --surface-1: #f8fcff;
            --warn-500: #e07a2b;
            --ok-500: #2f8f5b;
            --danger-500: #c23f3f;
        }

        .block-container {
            padding-top: 1.2rem !important;
            padding-bottom: 1.5rem !important;
            max-width: 1140px !important;
        }

        html, body, [class*="css"], h1, h2, h3, h4, h5, h6, p, div, span, label, button, input {
            font-family: 'Outfit', sans-serif !important;
            color: var(--ink-900);
        }

        h1 {
            font-weight: 800 !important;
            font-size: 2.35rem !important;
            line-height: 1.2 !important;
            margin-bottom: 0.5rem !important;
            letter-spacing: -0.03em;
        }

        h2 {
            font-weight: 750 !important;
            font-size: 1.85rem !important;
            line-height: 1.2 !important;
            margin-bottom: 0.5rem !important;
            letter-spacing: -0.02em;
        }

        h3, h4 {
            font-weight: 650 !important;
            color: var(--ink-900) !important;
        }

        p, label, small {
            font-weight: 500 !important;
            color: var(--ink-700) !important;
        }

        .stButton > button {
            border-radius: 0.9rem !important;
            background: linear-gradient(135deg, var(--brand-600) 0%, var(--brand-500) 100%) !important;
            color: white !important;
            padding: 10px 18px !important;
            border: 1px solid rgba(16, 71, 95, 0.25) !important;
            box-shadow: 0 8px 18px rgba(31, 111, 139, 0.22) !important;
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out, filter 0.2s ease-in-out !important;
            font-weight: 650 !important;
        }

        .stButton > button[kind="secondary"] {
            background: #ffffff !important;
            color: var(--brand-700) !important;
            border: 1px solid rgba(20, 90, 117, 0.25) !important;
            box-shadow: 0 3px 12px rgba(18, 48, 71, 0.06) !important;
        }

        .stButton > button[kind="tertiary"] {
            background: #edf7fc !important;
            color: var(--ink-900) !important;
            border: 1px solid rgba(24, 76, 102, 0.15) !important;
            box-shadow: none !important;
        }

        .stButton > button:hover {
            transform: translateY(-1px) scale(1.01) !important;
            box-shadow: 0 10px 20px rgba(18, 88, 115, 0.25) !important;
            filter: saturate(1.05);
        }

        .stButton > button:focus {
            outline: 2px solid rgba(47, 136, 167, 0.35) !important;
            outline-offset: 2px !important;
        }

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stSelectbox"] > div,
        div[data-testid="stMultiSelect"] > div {
            border-radius: 0.8rem !important;
            border: 1px solid rgba(22, 79, 104, 0.2) !important;
            background: rgba(255, 255, 255, 0.9) !important;
        }

        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stTextArea"] textarea:focus,
        div[data-testid="stNumberInput"] input:focus {
            border-color: rgba(31, 111, 139, 0.65) !important;
            box-shadow: 0 0 0 3px rgba(47, 136, 167, 0.2) !important;
        }

        div[data-testid="stForm"],
        div[data-testid="stExpander"],
        div[data-testid="stDataFrame"] {
            border-radius: 1rem !important;
            overflow: hidden;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(20, 90, 117, 0.13) !important;
        }

        hr {
            border: none !important;
            height: 1px !important;
            background: linear-gradient(90deg, transparent, rgba(20, 90, 117, 0.35), transparent) !important;
        }

        .portal-note {
            color: var(--ink-700);
            font-size: 0.96rem;
            margin-top: -0.25rem;
            margin-bottom: 0.7rem;
        }

        .portal-card {
            background: linear-gradient(175deg, rgba(255, 255, 255, 0.95) 0%, rgba(236, 247, 253, 0.9) 100%);
            border: 1px solid rgba(31, 111, 139, 0.16);
            border-radius: 1rem;
            padding: 0.85rem 1rem;
            margin-bottom: 0.8rem;
            box-shadow: 0 10px 26px rgba(18, 55, 84, 0.08);
        }

        .brand-home-wrap {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin: 1.4rem 0 1.8rem;
            animation: riseIn 0.75s ease-out both;
        }

        .brand-home-logo {
            height: 102px;
            filter: drop-shadow(0 8px 18px rgba(15, 68, 88, 0.2));
        }

        .brand-home-title {
            text-align: center;
            color: #0e4964 !important;
            margin-top: 0.25rem;
            margin-bottom: 0.2rem !important;
        }

        .brand-home-subtitle {
            color: var(--ink-700) !important;
            font-weight: 500;
            text-align: center;
            margin-bottom: 0;
        }

        .brand-dash-wrap {
            display: flex;
            align-items: center;
            justify-content: flex-start;
            gap: 0.65rem;
        }

        .brand-dash-logo {
            height: 82px;
        }

        .brand-dash-title {
            margin: 0 !important;
            color: #145a75 !important;
            line-height: 1.03 !important;
        }

        .brand-dash-subtitle {
            margin-top: 0.2rem;
            margin-bottom: 0;
            color: var(--ink-500) !important;
            font-size: 0.88rem;
        }

        .app-footer {
            margin-top: 2rem;
            display: flex;
            gap: 0.45rem;
            justify-content: center;
            align-items: center;
            padding-top: 0.5rem;
        }

        .app-footer p {
            margin: 0;
            font-weight: 700 !important;
            font-size: 0.92rem;
            letter-spacing: 0.01em;
        }

        .home-footer p,
        .dash-footer p {
            color: var(--ink-700) !important;
        }

        @keyframes riseIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    </style>
    """, unsafe_allow_html=True)