# -*- coding: utf-8 -*-
import streamlit as st
from data.personnel_data import PERSONNEL_DATA, PERSONNEL_CATEGORIES, JOB_TYPES
from utils.styles import inject_base_css, badge, CATEGORY_BADGE_KIND
from utils.detail_panel import render_regulation_detail
from utils import db

db.init_db()
inject_base_css()

st.title("인력·자격 기준")
st.caption("의료인 및 직원의 배치 기준과 자격 요건을 확인할 수 있습니다.")

top_l, top_r = st.columns([5, 1.3])
with top_l:
    query = st.text_input("검색", placeholder="예) 간호사 배치기준, 의사 면허, 당직의료인 등",
                           label_visibility="collapsed", key="personnel_query")
with top_r:
    st.button("🔧 상세검색", use_container_width=True, key="personnel_adv")

cat_tab = st.radio("카테고리", ["전체"] + PERSONNEL_CATEGORIES, horizontal=True, label_visibility="collapsed")

fcol1, fcol2, fcol3, fcol4 = st.columns(4)
with fcol1:
    job_f = st.selectbox("직종", ["전체"] + JOB_TYPES, key="personnel_job")
with fcol2:
    inst_f = st.selectbox("의료기관 종류", ["전체", "의원", "병원", "종합병원", "요양병원"], key="personnel_inst")
with fcol3:
    work_f = st.selectbox("근무 형태", ["전체", "상근", "당직", "겸직"], key="personnel_work")
with fcol4:
    law_options = ["전체"] + sorted({d["related_law"] for d in PERSONNEL_DATA})
    law_f = st.selectbox("관련 법령", law_options, key="personnel_law")

reset_col = st.columns([6, 1])
with reset_col[1]:
    if st.button("🔄 초기화", use_container_width=True, key="personnel_reset"):
        for k in ["personnel_query", "personnel_job", "personnel_inst", "personnel_work", "personnel_law"]:
            st.session_state.pop(k, None)
        st.rerun()


def filter_data():
    rows = PERSONNEL_DATA
    if cat_tab != "전체":
        rows = [r for r in rows if r["category"] == cat_tab]
    if job_f != "전체":
        rows = [r for r in rows if r["job_type"] == job_f]
    if inst_f != "전체":
        rows = [r for r in rows if inst_f in r["institutions"] or "모든 의료기관" in r["institutions"]]
    if work_f != "전체":
        rows = [r for r in rows if r["work_type"] == work_f]
    if law_f != "전체":
        rows = [r for r in rows if r["related_law"] == law_f]
    if query.strip():
        q = query.strip().lower()
        rows = [r for r in rows if q in r["title"].lower() or q in " ".join(r.get("keywords", [])).lower()]
    return sorted(rows, key=lambda r: r["revision_date"], reverse=True)

filtered = filter_data()
st.markdown(f"**총 {len(filtered)}건**")

if "personnel_selected" not in st.session_state or st.session_state["personnel_selected"] not in [r["id"] for r in filtered]:
    st.session_state["personnel_selected"] = filtered[0]["id"] if filtered else None

list_col, detail_col = st.columns([1.6, 1.1])

with list_col:
    header = st.columns([0.6, 1.1, 2.4, 1.6, 1.1, 1])
    for h, lbl in zip(header, ["번호", "분류", "제목", "관련법령", "의료기관", "개정일"]):
        h.markdown(f"**{lbl}**")
    if not filtered:
        st.info("검색 결과가 없습니다.")
    for r in filtered:
        cols = st.columns([0.6, 1.1, 2.4, 1.6, 1.1, 1])
        cols[0].write(r["id"])
        cols[1].markdown(badge(r["category"], CATEGORY_BADGE_KIND.get(r["category"], "blue")), unsafe_allow_html=True)
        if cols[2].button(f"[{r['job_type']}] {r['title']}", key=f"sel_per_{r['id']}", use_container_width=True):
            st.session_state["personnel_selected"] = r["id"]
        cols[3].markdown(f":gray[{r['related_law']}]")
        cols[4].markdown(f":gray[{', '.join(r['institutions'])}]")
        cols[5].markdown(f":gray[{r['revision_date']}]")

with detail_col:
    sel = next((r for r in PERSONNEL_DATA if r["id"] == st.session_state.get("personnel_selected")), None)
    if sel:
        render_regulation_detail(sel, "personnel")
    else:
        st.info("좌측 목록에서 규정을 선택하면 상세정보가 표시됩니다.")

st.divider()
st.markdown("### 직종별 바로가기")
jc = st.columns(6)
job_icons = {"의사": "🧑‍⚕️", "간호사": "👩‍⚕️", "간호조무사": "🧑‍🔬", "약사": "💊", "의료기사": "🩻", "기타 인력": "👥"}
job_desc = {
    "의사": "배치기준·면허요건<br>당직기준·겸직기준", "간호사": "배치기준·면허요건<br>교육·보수교육",
    "간호조무사": "배치기준·자격요건<br>교육·보수교육", "약사": "자격요건·면허요건<br>배치기준",
    "의료기사": "자격요건·면허요건<br>배치기준", "기타 인력": "배치기준·자격요건<br>교육·보수교육",
}
for c, job in zip(jc, JOB_TYPES):
    with c:
        cnt = len([r for r in PERSONNEL_DATA if r["job_type"] == job])
        st.markdown(
            f'<div class="quick-nav-card"><div style="font-size:26px;">{job_icons[job]}</div>'
            f'<div style="font-weight:700;margin:6px 0;">{job}</div>'
            f'<div style="font-size:11px;color:#6B7280;">{job_desc[job]}</div>'
            f'<div style="font-size:11px;color:#2B5CE6;margin-top:4px;">{cnt}건</div></div>',
            unsafe_allow_html=True,
        )
