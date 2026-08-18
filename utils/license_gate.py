# -*- coding: utf-8 -*-
"""유료 서비스 라이선스 키 게이트.
st.secrets["VALID_LICENSE_KEYS"] (쉼표구분 문자열 또는 리스트)에 등록된 키만 통과합니다.
secrets 미설정 시 데모 키 'MEDIUM-DEMO-2026'로 체험할 수 있습니다.
"""
import streamlit as st


def _get_valid_keys():
    try:
        raw = st.secrets.get("VALID_LICENSE_KEYS", None)
    except Exception:
        raw = None
    if not raw:
        return {"MEDIUM-DEMO-2026"}
    if isinstance(raw, str):
        return {k.strip() for k in raw.split(",") if k.strip()}
    return set(raw)


def require_license():
    """세션에 라이선스가 인증되어 있지 않으면 입력 폼을 그리고 앱 실행을 막습니다."""
    if st.session_state.get("license_ok"):
        return True

    st.markdown(
        '<div class="license-gate">🔒 이 시스템은 유료 구독 서비스입니다. '
        '발급받은 라이선스 키를 입력하시면 전체 기능을 이용하실 수 있습니다.</div>',
        unsafe_allow_html=True,
    )
    with st.form("license_form", clear_on_submit=False):
        key_input = st.text_input("라이선스 키", placeholder="예: MEDIUM-XXXX-XXXX", type="password")
        submitted = st.form_submit_button("확인", use_container_width=True)
    if submitted:
        if key_input.strip() in _get_valid_keys():
            st.session_state["license_ok"] = True
            st.success("라이선스가 확인되었습니다. 잠시 후 화면이 전환됩니다.")
            st.rerun()
        else:
            st.error("유효하지 않은 라이선스 키입니다. 담당 컨설턴트 또는 고객센터(070-0000-0000)로 문의해 주세요.")
    st.caption("체험을 원하시면 데모 키 `MEDIUM-DEMO-2026`을 입력해 보세요.")
    return False
