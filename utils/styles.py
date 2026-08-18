# -*- coding: utf-8 -*-
"""MEDIUM 의료기관 규정 관리 - 공통 스타일시트"""
import streamlit as st

PRIMARY = "#2B5CE6"
PRIMARY_DARK = "#1E3A8A"
BG_SOFT = "#F5F7FB"

BASE_CSS = f"""
<style>
    .block-container {{ padding-top: 2rem; padding-bottom: 3rem; max-width: 1400px; }}

    .medium-hero {{
        background: linear-gradient(135deg, {PRIMARY} 0%, {PRIMARY_DARK} 100%);
        border-radius: 16px; padding: 28px 32px; color: white; margin-bottom: 20px;
    }}
    .medium-hero .eyebrow {{ font-size: 12px; letter-spacing: 2px; opacity: 0.85; font-weight: 600; }}
    .medium-hero h1 {{ font-size: 26px; margin: 6px 0 8px 0; font-weight: 800; }}
    .medium-hero p {{ font-size: 14px; opacity: 0.9; margin: 0; }}

    .stat-card {{
        background: white; border: 1px solid #E5E9F2; border-radius: 12px;
        padding: 14px 16px; text-align: left;
    }}
    .stat-card .num {{ font-size: 22px; font-weight: 800; color: {PRIMARY_DARK}; }}
    .stat-card .lbl {{ font-size: 12px; color: #6B7280; margin-top: 2px; }}

    .badge {{
        display: inline-block; padding: 2px 10px; border-radius: 20px;
        font-size: 11px; font-weight: 700; margin-right: 4px;
    }}
    .badge-blue {{ background: #E3EAFD; color: {PRIMARY_DARK}; }}
    .badge-green {{ background: #E1F6EC; color: #0F7B4E; }}
    .badge-orange {{ background: #FEF0DE; color: #B4600A; }}
    .badge-purple {{ background: #F0E7FD; color: #6D28D9; }}
    .badge-gray {{ background: #EEF0F3; color: #4B5563; }}
    .badge-red {{ background: #FDE8E8; color: #B91C1C; }}

    .reg-row {{
        border-bottom: 1px solid #EEF1F6; padding: 10px 4px; font-size: 13.5px;
    }}
    .reg-row:hover {{ background: #F8FAFF; }}

    .detail-panel {{
        background: white; border: 1px solid #E5E9F2; border-radius: 14px;
        padding: 20px 22px; position: sticky; top: 12px;
    }}
    .detail-title {{ font-size: 19px; font-weight: 800; color: #111827; margin: 4px 0 14px 0; }}
    .meta-row {{ display: flex; font-size: 13px; padding: 5px 0; border-bottom: 1px dashed #EEF1F6; }}
    .meta-row .k {{ width: 96px; color: #6B7280; flex-shrink: 0; }}
    .meta-row .v {{ color: #111827; font-weight: 500; }}

    .check-item {{ font-size: 13.5px; padding: 5px 0; color: #1F2937; }}
    .check-item::before {{ content: "✅ "; }}

    .caution-item {{ font-size: 13.5px; padding: 6px 0; color: #92400E; background: #FFFBEB;
        border-left: 3px solid #F59E0B; padding-left: 10px; margin-bottom: 6px; border-radius: 4px; }}

    .step-card {{
        background: {BG_SOFT}; border-radius: 10px; padding: 12px 14px; margin-bottom: 8px;
        border-left: 4px solid {PRIMARY};
    }}
    .step-label {{ font-size: 11px; font-weight: 800; color: {PRIMARY}; letter-spacing: 1px; }}
    .step-title {{ font-size: 14px; font-weight: 700; color: #111827; margin: 2px 0 4px 0; }}
    .step-desc {{ font-size: 12.5px; color: #4B5563; }}

    .cat-card {{
        background: white; border: 1px solid #E5E9F2; border-radius: 12px; padding: 16px;
        height: 100%;
    }}
    .cat-card h4 {{ margin: 6px 0 4px 0; font-size: 15px; }}
    .cat-card p {{ font-size: 12.5px; color: #6B7280; margin-bottom: 8px; }}

    .quick-nav-card {{
        background: white; border: 1px solid #E5E9F2; border-radius: 12px; padding: 18px;
        text-align: center; height: 100%;
    }}

    .footer-note {{ font-size: 11.5px; color: #9CA3AF; margin-top: 24px; text-align: center; }}

    .license-gate {{
        background: #FFF7ED; border: 1px solid #FED7AA; border-radius: 12px;
        padding: 16px 20px; margin-bottom: 16px; font-size: 13.5px; color: #9A3412;
    }}
</style>
"""


def inject_base_css():
    st.markdown(BASE_CSS, unsafe_allow_html=True)


def badge(text, kind="blue"):
    return f'<span class="badge badge-{kind}">{text}</span>'


CATEGORY_BADGE_KIND = {
    "시설 기준": "blue", "장비 기준": "green", "감염관리 기준": "purple",
    "환경·안전 기준": "orange", "기타 기준": "gray",
    "직종별 배치 기준": "blue", "자격·면허 기준": "green",
    "당직·겸직 기준": "orange", "교육·보수교육 기준": "purple",
    "개설·변경·폐업 신고": "blue", "인력·시설 신고": "green", "정기 보고": "purple",
    "수시 보고": "red", "교육·점검 관련": "orange", "기타 신고": "gray",
}
