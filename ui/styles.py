import streamlit as st


def inject_custom_css() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #ffffff;
            color: #333333;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1350px;
        }
        .div-card {
            background-color: #f7f7f7;
            border: 1px solid #d9d9d9;
            border-radius: 10px;
            overflow: hidden;
            margin-bottom: 14px;
        }
        .div-card-header {
            background-color: #ececec;
            border-bottom: 1px solid #e0e0e0;
            text-align: center;
            padding: 8px 12px;
            font-size: 0.95rem;
            font-weight: 500;
            color: #444444;
            min-height: 36px;
        }
        .div-card-body {
            padding: 14px 16px;
        }
        .div-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
            font-size: 0.92rem;
            color: #333333;
        }
        .div-label {
            font-weight: 700;
        }
        .div-value {
            color: #444444;
        }
        .div-bar-track {
            width: 100%;
            height: 11px;
            background-color: #f0f0f0;
            border: 1px solid #d5d5d5;
            border-radius: 999px;
            overflow: hidden;
            margin-top: 2px;
            margin-bottom: 10px;
        }
        .div-bar-fill {
            height: 100%;
            border-radius: 999px;
            transition: width 0.3s ease;
        }
        .div-serif {
            font-family: Georgia, "Times New Roman", serif;
            text-align: center;
            font-size: 0.88rem;
            color: #333333;
            margin: 4px 0 8px 0;
        }
        .div-log-box {
            height: 280px;
            overflow-y: auto;
            padding: 14px 16px;
            background-color: #f7f7f7;
            font-size: 0.9rem;
            line-height: 1.45;
        }
        .div-log-entry {
            display: flex;
            gap: 14px;
            margin-bottom: 10px;
        }
        .div-log-time {
            color: #444444;
            min-width: 44px;
            font-variant-numeric: tabular-nums;
        }
        .div-log-msg {
            color: #333333;
        }
        .div-equip-slot {
            margin-bottom: 14px;
        }
        .div-equip-slot:last-child {
            margin-bottom: 0;
        }
        .div-equip-title {
            font-weight: 700;
            font-size: 0.9rem;
            color: #333333;
            margin-bottom: 2px;
        }
        div[data-testid="stTextArea"] textarea {
            background-color: #eeeeee !important;
            border: 1px solid #d5d5d5 !important;
            border-radius: 6px !important;
            color: #333333 !important;
            font-size: 0.9rem !important;
        }
        div[data-testid="stButton"] button {
            background-color: #eeeeee !important;
            color: #333333 !important;
            border: 1px solid #cccccc !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
        }
        div[data-testid="stButton"] button:hover {
            background-color: #e2e2e2 !important;
            border-color: #b5b5b5 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def progress_bar_html(percent: float, color: str) -> str:
    clamped = max(0.0, min(100.0, float(percent)))
    return (
        f'<div class="div-bar-track">'
        f'<div class="div-bar-fill" style="width:{clamped:.1f}%; background-color:{color};"></div>'
        f'</div>'
    )