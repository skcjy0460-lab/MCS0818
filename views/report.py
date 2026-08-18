# -*- coding: utf-8 -*-
import streamlit as st
from data.report_data import REPORT_DATA, REPORT_CATEGORIES
from utils.styles import inject_base_css, badge, CATEGORY_BADGE_KIND
from utils.detail_panel import render_report_detail
from utils import db

db.init_db()
inject_base_css()

st.title("신고·보고 관리")
st.caption("개설·변경·폐업 및 각종 신고와 보고 일정을 관리하고 필요한 서식을 확인할 수 있습니다.")

top_l, top_r = st.columns([5, 1.3])
with top_l:
    query = st.text_input("검색", placeholder="예) 개설신고, 변경신고, 진료과목 변경, 인력 변경",
                           label_visibility="collapsed", key="report_query")
with top_r:
    st.button("🔧 상세검색", use_container_width=True, key="report_adv")

cat_tab = st.radio("카테고리", ["전체"] + REPORT_CATEGORIES, horizontal=True, label_visibility="collapsed")

fcol1, fcol2, fcol3, fcol4 = st.columns(4)
with fcol1:
    st.selectbox("신고 유형", ["전체"], key="report_type_dummy")
with fcol2:
    inst_f = st.selectbox("의료기관 종류", ["전체", "의원", "병원", "종합병원", "요양병원"], key="report_inst")
with fcol3:
    period_options = ["전체"] + sorted({d["period"] for d in REPORT_DATA})
    period_f = st.selectbox("신고 주기", period_options, key="report_period")
with fcol4:
    agency_options = ["전체"] + sorted({d["agency"] for d in REPORT_DATA})
    agency_f = st.selectbox("신고 기관", agency_options, key="report_agency")


def filter_data():
    rows = REPORT_DATA
    if cat_tab != "전체":
        rows = [r for r in rows if r["category"] == cat_tab]
    if inst_f != "전체":
        rows = [r for r in rows if inst_f in r["institutions"] or "모든 의료기관" in r["institutions"]]
    if period_f != "전체":
        rows = [r for r in rows if r["period"] == period_f]
    if agency_f != "전체":
        rows = [r for r in rows if r["agency"] == agency_f]
    if query.strip():
        q = query.strip().lower()
        rows = [r for r in rows if q in r["title"].lower() or q in r["target"].lower() or q in r["overview"].lower()]
    return sorted(rows, key=lambda r: r["revision_date"], reverse=True)

filtered = filter_data()
st.markdown(f"**총 {len(filtered)}건**")

if "report_selected" not in st.session_state or st.session_state["report_selected"] not in [r["id"] for r in filtered]:
    st.session_state["report_selected"] = filtered[0]["id"] if filtered else None

list_col, detail_col = st.columns([1.7, 1.1])

with list_col:
    header = st.columns([1.1, 2, 1.3, 1.3, 1.3, 1])
    for h, lbl in zip(header, ["신고유형", "신고명", "신고대상", "신고기관", "신고주기/기한", "개정일"]):
        h.markdown(f"**{lbl}**")
    if not filtered:
        st.info("검색 결과가 없습니다.")
    for r in filtered:
        cols = st.columns([1.1, 2, 1.3, 1.3, 1.3, 1])
        cols[0].markdown(badge(r["category"], CATEGORY_BADGE_KIND.get(r["category"], "blue")), unsafe_allow_html=True)
        if cols[1].button(r["title"], key=f"sel_rep_{r['id']}", use_container_width=True):
            st.session_state["report_selected"] = r["id"]
        cols[2].markdown(f":gray[{r['target']}]")
        cols[3].markdown(f":gray[{r['agency']}]")
        cols[4].markdown(f":red[{r['period']}]")
        cols[5].markdown(f":gray[{r['revision_date']}]")

with detail_col:
    sel = next((r for r in REPORT_DATA if r["id"] == st.session_state.get("report_selected")), None)
    if sel:
        render_report_detail(sel)
    else:
        st.info("좌측 목록에서 신고·보고 항목을 선택하면 상세정보가 표시됩니다.")

st.caption("※ 신고 기한을 놓치면 과태료, 과징금 또는 행정처분 대상이 될 수 있습니다. 반드시 기한 내 신고하시기 바랍니다.")

st.divider()
st.markdown("### 자주 찾는 신고 바로가기")
quick = [
    ("🏢 개설·변경·폐업 신고", "개설·변경·폐업 신고"), ("👥 인력·시설 신고", "인력·시설 신고"),
    ("📑 정기 보고", "정기 보고"), ("📣 수시 보고", "수시 보고"),
    ("🎓 교육·점검 관련", "교육·점검 관련"), ("📄 기타 신고", "기타 신고"),
]
qc = st.columns(6)
for c, (label, cat) in zip(qc, quick):
    with c:
        cnt = len([r for r in REPORT_DATA if r["category"] == cat])
        st.markdown(f'<div class="quick-nav-card"><div style="font-size:22px;">{label.split()[0]}</div>'
                     f'<div style="font-weight:700;font-size:12.5px;margin-top:4px;">{" ".join(label.split()[1:])}</div>'
                     f'<div style="font-size:11px;color:#2B5CE6;margin-top:4px;">{cnt}건</div></div>',
                     unsafe_allow_html=True)
