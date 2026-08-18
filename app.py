# -*- coding: utf-8 -*-
import streamlit as st
from utils.license_gate import require_license
from utils.styles import inject_base_css

st.set_page_config(
    page_title="MEDIUM | 의료기관 규정 관리",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_base_css()

st.markdown(
    """
    <div style="display:flex;justify-content:space-between;align-items:center;padding:4px 0 12px 0;">
        <div style="font-weight:900;font-size:20px;color:#1E3A8A;">
            MEDIUM <span style="font-weight:500;font-size:11px;color:#6B7280;">Medical Premium Consulting</span>
        </div>
        <div style="font-size:12px;color:#6B7280;">의료기관 규정 관리 · 유료 서비스</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not require_license():
    st.stop()

with st.sidebar:
    st.markdown("### 🏥 의료기관 규정 관리")
    st.caption("이용문의  평일 09:00~18:00  \n070-0000-0000")
    st.divider()
    if st.button("🔓 로그아웃(라이선스 초기화)", use_container_width=True):
        st.session_state["license_ok"] = False
        st.rerun()

pages = [
    st.Page("views/home.py", title="규정 통합검색", icon="🔍", default=True),
    st.Page("views/facility.py", title="운영·시설 기준", icon="🏢"),
    st.Page("views/personnel.py", title="인력·자격 기준", icon="👥"),
    st.Page("views/report.py", title="신고·보고 관리", icon="📋"),
    st.Page("views/schedule.py", title="규정 일정 관리", icon="🗓️"),
]

pg = st.navigation(pages)
pg.run()

st.markdown(
    '<div class="footer-note">ⓒ MEDIUM Medical Premium Consulting · '
    '본 시스템은 병원명·직원 명단·병원 내부정보를 저장하지 않으며, 실무 참고용 정보를 제공합니다.</div>',
    unsafe_allow_html=True,
)
