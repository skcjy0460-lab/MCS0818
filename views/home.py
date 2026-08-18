# -*- coding: utf-8 -*-
import streamlit as st
from datetime import date
from data.master import build_unified_index, counts_summary, SECTION_META
from data.schedule_data import build_schedule_events, TYPE_ICON
from utils.styles import inject_base_css, badge, CATEGORY_BADGE_KIND
from utils.html_export import build_search_summary_html
from utils.ai_client import run_compliance_diagnosis
from utils import db

db.init_db()
inject_base_css()

st.markdown(
    """
    <div class="medium-hero">
        <div class="eyebrow">MEDICAL COMPLIANCE SEARCH</div>
        <h1>의료기관 규정 통합 검색 시스템</h1>
        <p>의료기관 원무·청구심사 업무의 법적 기준을 한눈에 검색·확인하세요.<br>
        근거: 의료법·국민건강보험법·개인정보보호법 등 최신 법령 기준 (참고용 데이터셋)</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------- 상단 통합검색 ----------------
index = build_unified_index()
counts = counts_summary()

col_search, col_btn = st.columns([5, 1])
with col_search:
    query = st.text_input(
        "통합검색", placeholder="예) 처방전 보관기간, 간호사 배치기준, CCTV 설치 기준, 마약류 관리, 개설신고",
        label_visibility="collapsed",
    )
with col_btn:
    search_clicked = st.button("🔍 검색", use_container_width=True, type="primary")

with st.expander("🔧 상세검색 필터", expanded=False):
    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        section_filter = st.multiselect(
            "검색 범위", options=list(SECTION_META.keys()),
            format_func=lambda k: SECTION_META[k]["label"], default=[],
        )
    with fcol2:
        inst_filter = st.selectbox("의료기관 종류", ["전체", "의원", "병원", "종합병원", "요양병원"])
    with fcol3:
        sort_opt = st.selectbox("정렬", ["최신순", "제목순"])

# 카테고리 요약 배지
badge_cols = st.columns(5)
badge_defs = [
    ("서류·보관", counts["facility_cat"].get("시설 기준", 0), "blue"),
    ("시설·장비", counts["facility"], "green"),
    ("인력·자격", counts["personnel"], "purple"),
    ("신고·보고", counts["report"], "orange"),
    ("업무 캘린더", counts["schedule"], "gray"),
]
for c, (label, cnt, kind) in zip(badge_cols, badge_defs):
    with c:
        st.markdown(f'{badge(f"{label} {cnt}", kind)}', unsafe_allow_html=True)

st.markdown("### 한눈에 보는 규정 현황")
scols = st.columns(5)
stat_defs = [
    ("전체 규정", f"{counts['total']}건"),
    ("운영·시설 기준", f"{counts['facility']}건"),
    ("인력·자격 기준", f"{counts['personnel']}건"),
    ("신고·보고 항목", f"{counts['report']}건"),
    ("이번 달 일정", f"{counts['schedule']}건"),
]
for c, (lbl, num) in zip(scols, stat_defs):
    with c:
        st.markdown(f'<div class="stat-card"><div class="num">{num}</div><div class="lbl">{lbl}</div></div>',
                    unsafe_allow_html=True)

st.divider()

# ---------------- 검색 결과 ----------------
def run_search(q, sections, inst, sort_opt):
    q_lower = q.strip().lower()
    results = []
    for entry in index:
        if sections and entry["section"] not in sections:
            continue
        if inst != "전체" and "모든 의료기관" not in entry["institutions"] and inst not in entry["institutions"]:
            continue
        if q_lower and q_lower not in entry["text"].lower():
            continue
        results.append(entry)
    if sort_opt == "제목순":
        results.sort(key=lambda x: x["title"])
    else:
        results.sort(key=lambda x: x["revision_date"], reverse=True)
    return results


if search_clicked or query:
    results = run_search(query, section_filter, inst_filter, sort_opt)
    st.markdown(f"#### 검색 결과 · 총 {len(results)}건")
    if results:
        html_report = build_search_summary_html(query or "(전체)", results)
        st.download_button("📄 검색결과 HTML 리포트 저장", data=html_report,
                            file_name=f"규정검색결과_{query or '전체'}.html", mime="text/html")
        for r in results[:40]:
            kind = CATEGORY_BADGE_KIND.get(r["category"], "blue")
            with st.container():
                cols = st.columns([1.4, 4, 2, 1.3])
                with cols[0]:
                    st.markdown(badge(SECTION_META[r["section"]]["label"], kind), unsafe_allow_html=True)
                with cols[1]:
                    st.markdown(f"**{r['title']}**  \n:gray[{r['related_law']}]")
                with cols[2]:
                    st.markdown(f":gray[{', '.join(r['institutions'])}]")
                with cols[3]:
                    st.markdown(f":gray[{r['revision_date']}]")
                st.caption(f"자세히 보려면 좌측 메뉴의 **{SECTION_META[r['section']]['label']}** 페이지에서 '{r['title']}'을(를) 검색하세요.")
                st.markdown("---")
        if len(results) > 40:
            st.caption(f"...외 {len(results) - 40}건 더 있습니다. 검색어를 구체화해 보세요.")
    else:
        st.info("검색 결과가 없습니다. 다른 키워드로 시도해 보세요.")
    st.divider()

# ---------------- 카테고리별 규정 관리 허브 ----------------
st.markdown("### 카테고리별 규정 관리")
cat_cols = st.columns(4)
for c, key in zip(cat_cols, ["facility", "personnel", "report", "schedule"]):
    meta = SECTION_META[key]
    with c:
        bullets_html = "".join(f"<li>{b}</li>" for b in meta["bullets"])
        st.markdown(
            f'<div class="cat-card"><h4>{meta["icon"]} {meta["label"]}</h4>'
            f'<p>{meta["desc"]}</p><ul style="font-size:12px;color:#4B5563;padding-left:16px;">{bullets_html}</ul></div>',
            unsafe_allow_html=True,
        )
        st.page_link(meta["page"], label="바로가기 →", use_container_width=True)

st.divider()

# ---------------- 이번 달 주요 일정 미리보기 ----------------
left, right = st.columns([1.3, 1])
with left:
    st.markdown("### 🗓️ 이번 달 주요 일정")
    events = sorted(build_schedule_events(), key=lambda e: e["date"])
    upcoming = [e for e in events if e["date"] >= date.today()][:5]
    if upcoming:
        for e in upcoming:
            dday = (e["date"] - date.today()).days
            dday_str = "D-DAY" if dday == 0 else f"D-{dday}"
            st.markdown(
                f'{TYPE_ICON.get(e["type"],"🔧")} **{e["title"]}** — '
                f'{badge(dday_str, "red" if dday <= 3 else "orange")} '
                f':gray[{e["date"].strftime("%Y.%m.%d")} · {e["agency"]}]',
                unsafe_allow_html=True,
            )
    else:
        st.caption("예정된 일정이 없습니다.")
    st.page_link("views/schedule.py", label="규정 일정 관리 전체보기 →")

with right:
    st.markdown("### ⭐ 맞춤 추천")
    favs = db.list_favorites()
    if favs:
        st.caption("즐겨찾기한 규정")
        for f in favs[:5]:
            st.markdown(f"- {f['title']}")
    else:
        st.caption("자주 찾는 키워드 기반 추천 규정입니다.")
        for kw in ["CCTV 설치 기준", "처방전 보관기간", "간호사 배치기준", "마약류 관리", "당직의료인 기준"]:
            st.markdown(f"- {kw}")

st.divider()

# ---------------- AI 컴플라이언스 자가진단 ----------------
st.markdown("### 🤖 AI 컴플라이언스 자가진단")
st.caption("병원 기본 정보를 입력하면 AI가 규정 준수 리스크 영역과 우선 점검 항목을 진단해 드립니다. "
           "⚠ 진단 결과는 실무 참고용이며, 최종 판단은 반드시 법령 원문 및 전문가 확인을 거쳐야 합니다.")

with st.form("ai_diagnosis_form"):
    d1, d2 = st.columns(2)
    with d1:
        institution_type = st.selectbox("의료기관 종별", ["의원", "병원", "종합병원", "요양병원"])
    with d2:
        bed_count = st.number_input("병상 수 (해당 시)", min_value=0, max_value=3000, value=0, step=10)
    concerns_text = st.text_area(
        "현재 우려되는 사항 또는 최근 이슈를 입력하세요",
        placeholder="예) 야간 당직 인력이 부족한 것 같고, CCTV 저장기간 관리가 안 되고 있습니다.",
        height=90,
    )
    diagnose_clicked = st.form_submit_button("🔎 AI 진단 실행", type="primary", use_container_width=True)

if diagnose_clicked:
    with st.spinner("AI가 규정 준수 현황을 분석하고 있습니다..."):
        result, note = run_compliance_diagnosis(institution_type, bed_count, concerns_text)

    risk_kind = {"낮음": "green", "보통": "orange", "높음": "red", "매우 높음": "red"}.get(result["overall_risk"], "gray")
    st.markdown(f'#### 진단 결과 {badge(result["overall_risk"], risk_kind)}', unsafe_allow_html=True)
    st.write(result["summary"])
    if note:
        st.caption(f"ℹ️ {note}")

    st.markdown("**영역별 점검 결과**")
    for item in result["checklist_results"]:
        status_kind = {"적정": "green", "미흡": "red", "확인 필요": "orange"}.get(item["status"], "gray")
        st.markdown(f'{badge(item["status"], status_kind)} **{item["area"]}** — {item["comment"]}',
                    unsafe_allow_html=True)

    st.markdown("**권장 조치사항**")
    for a in result["recommended_actions"]:
        st.markdown(f"- ✅ {a}")

    if result.get("related_keywords"):
        st.caption("관련 키워드: " + ", ".join(result["related_keywords"]))

st.markdown('<div class="footer-note">본 시스템은 병원명·직원 명단·병원 내부정보를 저장하지 않습니다. '
            '모든 콘텐츠는 실무 참고용이며 법적 효력이 있는 유권해석이 아닙니다.</div>', unsafe_allow_html=True)
