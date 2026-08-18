# -*- coding: utf-8 -*-
"""규정/신고 상세정보 패널 렌더링 헬퍼."""
import streamlit as st
from utils.styles import badge, CATEGORY_BADGE_KIND
from utils import db
from utils.html_export import build_regulation_report_html, build_report_item_html


def _meta_row(k, v):
    st.markdown(f'<div class="meta-row"><div class="k">{k}</div><div class="v">{v}</div></div>',
                unsafe_allow_html=True)


def render_regulation_detail(item, section_key: str):
    """운영·시설 / 인력·자격 공용 상세 패널.
    item: facility_data.py / personnel_data.py 의 레코드 딕셔너리
    section_key: 'facility' 또는 'personnel' (즐겨찾기 구분용)
    """
    st.markdown('<div class="detail-panel">', unsafe_allow_html=True)

    cat_kind = CATEGORY_BADGE_KIND.get(item["category"], "blue")
    st.markdown(badge(item["category"], cat_kind), unsafe_allow_html=True)
    st.markdown(f'<div class="detail-title">{item["title"]}</div>', unsafe_allow_html=True)

    top_cols = st.columns([1, 1, 1])
    fav_key = f"fav_{section_key}_{item['id']}"
    with top_cols[0]:
        is_fav = db.is_favorite(section_key, item["id"])
        if st.button(("★ 즐겨찾기됨" if is_fav else "☆ 즐겨찾기"), key=fav_key, use_container_width=True):
            db.toggle_favorite(section_key, item["id"], item["title"])
            st.rerun()
    with top_cols[1]:
        st.link_button("🖨️ 인쇄용 보기", "javascript:window.print()", use_container_width=True, disabled=False) \
            if False else st.caption("🖨️ 인쇄: 브라우저 인쇄(Ctrl+P) 이용")
    with top_cols[2]:
        html_report = build_regulation_report_html(item)
        st.download_button("📄 HTML 리포트 저장", data=html_report,
                            file_name=f"{item['title']}_리포트.html", mime="text/html",
                            key=f"dl_{section_key}_{item['id']}", use_container_width=True)

    _meta_row("관련 법령", item["related_law"])
    _meta_row("적용 의료기관", ", ".join(item["institutions"]))
    _meta_row("최종 개정일", item["revision_date"])
    _meta_row("관련 부처", item["department"])
    _meta_row("키워드", " ".join([f"#{k}" for k in item.get("keywords", [])]))

    tabs = st.tabs(["핵심내용", "상세내용", "위반 시 조치", "관련서식", f"Q&A ({len(item.get('qna', []))})"])

    with tabs[0]:
        st.markdown("**핵심 체크 항목**")
        for c in item.get("core_checklist", []):
            st.markdown(f'<div class="check-item">{c}</div>', unsafe_allow_html=True)
        st.caption("※ 실제 적용 여부는 기관 상황에 따라 다를 수 있으므로 최신 법령 원문과 반드시 대조하시기 바랍니다.")

    with tabs[1]:
        st.write(item.get("detail_content", ""))

    with tabs[2]:
        v = item.get("violation", {})
        if v:
            labels = {
                "administrative_disposition": "행정처분",
                "fine": "과태료",
                "penalty": "벌칙(형사)",
                "corrective_order": "시정명령",
                "basis": "법적 근거",
            }
            for key, label in labels.items():
                if v.get(key):
                    st.markdown(f"**{label}**")
                    st.write(v[key])
        st.info("실제 적용은 위반 유형·기관 상황 등에 따라 달라질 수 있으므로, 법령 근거와 최신 기준 확인 경로를 함께 확인하세요.")

    with tabs[3]:
        forms = item.get("forms", [])
        if forms:
            for f in forms:
                st.markdown(f"- 📎 {f} (서식자료실 연결 예정)")
        else:
            st.caption("등록된 관련 서식이 없습니다.")

    with tabs[4]:
        qna = item.get("qna", [])
        if qna:
            for qa in qna:
                with st.expander(f"Q. {qa['q']}"):
                    st.write(qa["a"])
        else:
            st.caption("등록된 Q&A가 없습니다.")

    st.markdown("**관련 링크**")
    lcol = st.columns(3)
    with lcol[0]:
        st.button("📖 법령 원문 보기", key=f"law_{section_key}_{item['id']}", use_container_width=True)
    with lcol[1]:
        st.button("⚖️ 행정해석 사례", key=f"case_{section_key}_{item['id']}", use_container_width=True)
    with lcol[2]:
        st.button("📢 관련 고시·지침", key=f"notice_{section_key}_{item['id']}", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_report_detail(item):
    """신고·보고 관리 전용 상세 패널."""
    st.markdown('<div class="detail-panel">', unsafe_allow_html=True)

    cat_kind = CATEGORY_BADGE_KIND.get(item["category"], "blue")
    st.markdown(badge(item["category"], cat_kind), unsafe_allow_html=True)
    st.markdown(f'<div class="detail-title">{item["title"]}</div>', unsafe_allow_html=True)

    top_cols = st.columns([1, 1, 1])
    with top_cols[0]:
        is_fav = db.is_favorite("report", item["id"])
        if st.button(("★ 즐겨찾기됨" if is_fav else "☆ 즐겨찾기"), key=f"fav_report_{item['id']}", use_container_width=True):
            db.toggle_favorite("report", item["id"], item["title"])
            st.rerun()
    with top_cols[1]:
        st.caption("🖨️ 인쇄: 브라우저 인쇄(Ctrl+P) 이용")
    with top_cols[2]:
        html_report = build_report_item_html(item)
        st.download_button("📄 HTML 리포트 저장", data=html_report,
                            file_name=f"{item['title']}_리포트.html", mime="text/html",
                            key=f"dl_report_{item['id']}", use_container_width=True)

    _meta_row("신고 대상", item["target"])
    _meta_row("신고 기관", item["agency"])
    _meta_row("신고 기한", item["period"])
    _meta_row("관련 법령", item["related_law"])
    _meta_row("적용 의료기관", ", ".join(item["institutions"]))
    _meta_row("최종 개정일", item["revision_date"])

    tabs = st.tabs(["신고개요", "필요서류", "신고절차", "주의사항", f"Q&A ({len(item.get('qna', []))})"])

    with tabs[0]:
        st.write(item.get("overview", ""))
        st.markdown("**핵심 체크 항목**")
        for c in item.get("core_checklist", []):
            st.markdown(f'<div class="check-item">{c}</div>', unsafe_allow_html=True)

    with tabs[1]:
        docs = item.get("required_docs", [])
        if docs:
            doc_kind = {"필수": "red", "해당 시": "orange", "선택": "gray"}
            for d in docs:
                k = doc_kind.get(d["type"], "gray")
                st.markdown(f'{badge(d["type"], k)} {d["name"]}', unsafe_allow_html=True)
            st.caption("※ 서식자료실과 연결하여 바로 다운로드할 수 있도록 확장 예정입니다.")
        else:
            st.caption("등록된 필요서류가 없습니다.")

    with tabs[2]:
        for s in item.get("procedure_steps", []):
            st.markdown(
                f'<div class="step-card"><div class="step-label">{s["step"]}</div>'
                f'<div class="step-title">{s["title"]}</div>'
                f'<div class="step-desc">{s["desc"]}</div></div>',
                unsafe_allow_html=True,
            )

    with tabs[3]:
        for c in item.get("cautions", []):
            st.markdown(f'<div class="caution-item">⚠ {c}</div>', unsafe_allow_html=True)
        if item.get("penalty_basis"):
            st.markdown("**과태료·행정처분 근거**")
            st.write(item["penalty_basis"])

    with tabs[4]:
        qna = item.get("qna", [])
        if qna:
            for qa in qna:
                with st.expander(f"Q. {qa['q']}"):
                    st.write(qa["a"])
        else:
            st.caption("등록된 Q&A가 없습니다.")

    st.markdown("**관련 링크**")
    lcol = st.columns(4)
    with lcol[0]:
        st.button("📖 법령 원문 보기", key=f"law_report_{item['id']}", use_container_width=True)
    with lcol[1]:
        st.button("⚖️ 행정해석 사례", key=f"case_report_{item['id']}", use_container_width=True)
    with lcol[2]:
        st.button("📢 관련 고시·지침", key=f"notice_report_{item['id']}", use_container_width=True)
    with lcol[3]:
        st.button("⬇️ 신고서식 다운로드", key=f"form_report_{item['id']}", use_container_width=True)

    if item.get("schedule_link"):
        st.success("📅 이 업무는 신고기한을 가지고 있습니다. [규정 일정 관리]에서 관련 일정을 확인하세요.")

    st.markdown("</div>", unsafe_allow_html=True)
