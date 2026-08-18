# -*- coding: utf-8 -*-
import streamlit as st
from data.facility_data import FACILITY_DATA, FACILITY_CATEGORIES
from utils.styles import inject_base_css, badge, CATEGORY_BADGE_KIND
from utils.detail_panel import render_regulation_detail
from utils import db

db.init_db()
inject_base_css()

st.title("운영·시설 기준")
st.caption("의료기관 운영 및 시설·장비 관련 기준을 확인할 수 있습니다.")

# ---------------- 검색/필터 ----------------
top_l, top_r = st.columns([5, 1.3])
with top_l:
    query = st.text_input("검색", placeholder="예) 입원실 기준, CCTV 설치 기준, 소독 시설, 응급장비 등",
                           label_visibility="collapsed", key="facility_query")
with top_r:
    st.button("🔧 상세검색", use_container_width=True, key="facility_adv")

cat_tab = st.radio("카테고리", ["전체"] + FACILITY_CATEGORIES, horizontal=True, label_visibility="collapsed")

fcol1, fcol2, fcol3, fcol4 = st.columns(4)
with fcol1:
    inst_f = st.selectbox("의료기관 종류", ["전체", "의원", "병원", "종합병원", "요양병원"], key="facility_inst")
with fcol2:
    st.selectbox("적용 기준", ["전체"], key="facility_apply")
with fcol3:
    law_options = ["전체"] + sorted({d["related_law"] for d in FACILITY_DATA})
    law_f = st.selectbox("관련 법령", law_options, key="facility_law")
with fcol4:
    sort_f = st.selectbox("정렬", ["최신순", "제목순", "조회수순"], key="facility_sort")

# ---------------- 필터링 ----------------
def filter_data():
    rows = FACILITY_DATA
    if cat_tab != "전체":
        rows = [r for r in rows if r["category"] == cat_tab]
    if inst_f != "전체":
        rows = [r for r in rows if inst_f in r["institutions"] or "모든 의료기관" in r["institutions"]]
    if law_f != "전체":
        rows = [r for r in rows if r["related_law"] == law_f]
    if query.strip():
        q = query.strip().lower()
        rows = [r for r in rows if q in r["title"].lower() or q in " ".join(r.get("keywords", [])).lower()
                or q in r["related_law"].lower()]
    if sort_f == "제목순":
        rows = sorted(rows, key=lambda r: r["title"])
    elif sort_f == "조회수순":
        rows = sorted(rows, key=lambda r: r["views"], reverse=True)
    else:
        rows = sorted(rows, key=lambda r: r["revision_date"], reverse=True)
    return rows

filtered = filter_data()
st.markdown(f"**총 {len(filtered)}건**")

if "facility_selected" not in st.session_state:
    st.session_state["facility_selected"] = filtered[0]["id"] if filtered else None

list_col, detail_col = st.columns([1.6, 1.1])

with list_col:
    header = st.columns([0.6, 1, 2.6, 1.6, 1.1, 1])
    labels = ["번호", "분류", "제목", "관련법령", "의료기관", "개정일"]
    for h, lbl in zip(header, labels):
        h.markdown(f"**{lbl}**")

    if not filtered:
        st.info("검색 결과가 없습니다.")
    for r in filtered:
        cols = st.columns([0.6, 1, 2.6, 1.6, 1.1, 1])
        cols[0].write(r["id"])
        cols[1].markdown(badge(r["category"], CATEGORY_BADGE_KIND.get(r["category"], "blue")), unsafe_allow_html=True)
        if cols[2].button(r["title"], key=f"sel_fac_{r['id']}", use_container_width=True):
            st.session_state["facility_selected"] = r["id"]
        cols[3].markdown(f":gray[{r['related_law']}]")
        cols[4].markdown(f":gray[{', '.join(r['institutions'])}]")
        cols[5].markdown(f":gray[{r['revision_date']}]")

with detail_col:
    sel = next((r for r in FACILITY_DATA if r["id"] == st.session_state.get("facility_selected")), None)
    if sel:
        render_regulation_detail(sel, "facility")
    else:
        st.info("좌측 목록에서 규정을 선택하면 상세정보가 표시됩니다.")

st.divider()
st.markdown("### 운영·시설 기준 분류 안내")
guide = [
    ("🏢 시설 기준", "입원실, 수술실, 중환자실, 격리실, 대기실 등 의료기관 시설의 구조·면적·설비 기준", "면적, 구조, 설비, 환자안전, 편의시설"),
    ("🩺 장비 기준", "응급장비, 진단장비, 치료장비, CCTV 등 의료장비의 구비·성능·운영 기준", "구비기준, 성능, 유지관리, 점검, 교체주기"),
    ("🛡️ 감염관리 기준", "소독, 멸균, 세척, 폐기물 처리 등 감염 예방을 위한 시설·관리 기준", "감염예방, 소독, 멸균, 폐기물, 격리"),
    ("🌿 환경·안전 기준", "소방, 전기, 가스, 환기, 소음 등 안전하고 쾌적한 환경 유지 기준", "소방, 전기, 가스, 안전, 환경관리"),
    ("📄 기타 기준", "주차장, 안내표지, 편의시설 등 기타 운영 관련 시설 기준", "주차장, 안내, 편의시설, 표지, 기타"),
]
gc = st.columns(5)
for c, (title, desc, kw) in zip(gc, guide):
    with c:
        st.markdown(f'<div class="cat-card"><h4>{title}</h4><p>{desc}</p>'
                     f'<p style="font-size:11px;color:#9CA3AF;">주요 키워드<br>{kw}</p></div>',
                     unsafe_allow_html=True)
