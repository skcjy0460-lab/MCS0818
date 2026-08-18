# -*- coding: utf-8 -*-
import calendar
from datetime import date, timedelta
import streamlit as st
from data.schedule_data import build_schedule_events, SCHEDULE_TYPES, TYPE_ICON, TYPE_COLOR, CATEGORY_INSTITUTIONS
from utils.styles import inject_base_css, badge
from utils.html_export import build_calendar_month_html
from utils import db

db.init_db()
inject_base_css()

WEEKDAY_KR = ["월", "화", "수", "목", "금", "토", "일"]


def event_key(e):
    return f"legal_{e['id']}"


def dday_label(d: date):
    diff = (d - date.today()).days
    if diff == 0:
        return "D-DAY"
    elif diff > 0:
        return f"D-{diff}"
    else:
        return f"기한경과 {abs(diff)}일"


def dday_kind(d: date):
    diff = (d - date.today()).days
    if diff < 0:
        return "gray"
    if diff <= 3:
        return "red"
    if diff <= 7:
        return "orange"
    return "blue"


st.title("규정 일정 관리 (업무 캘린더)")
st.caption("신고·보고·교육·점검 등 주요 일정을 한눈에 확인하고 관리할 수 있습니다.")

# ---------------- 상태 초기화 ----------------
today = date.today()
if "cal_year" not in st.session_state:
    st.session_state["cal_year"] = today.year
if "cal_month" not in st.session_state:
    st.session_state["cal_month"] = today.month
if "cal_selected_event" not in st.session_state:
    st.session_state["cal_selected_event"] = None

all_legal_events = build_schedule_events()
for e in all_legal_events:
    e["completed"] = db.get_completion(event_key(e)) or e.get("completed", False)

custom_events_raw = db.list_custom_events()

# ---------------- 상단 컨트롤 ----------------
nav_l, nav_title, nav_r, nav_view, nav_add = st.columns([0.6, 2, 0.6, 1.4, 1.4])
with nav_l:
    if st.button("◀", use_container_width=True):
        m, y = st.session_state["cal_month"] - 1, st.session_state["cal_year"]
        if m == 0:
            m, y = 12, y - 1
        st.session_state["cal_month"], st.session_state["cal_year"] = m, y
with nav_title:
    st.markdown(f"<h3 style='text-align:center;'>{st.session_state['cal_year']}년 {st.session_state['cal_month']}월</h3>",
                unsafe_allow_html=True)
with nav_r:
    if st.button("▶", use_container_width=True):
        m, y = st.session_state["cal_month"] + 1, st.session_state["cal_year"]
        if m == 13:
            m, y = 1, y + 1
        st.session_state["cal_month"], st.session_state["cal_year"] = m, y
with nav_view:
    view_mode = st.radio("보기", ["월간", "목록"], horizontal=True, label_visibility="collapsed")
with nav_add:
    if st.button("오늘로 이동", use_container_width=True):
        st.session_state["cal_year"], st.session_state["cal_month"] = today.year, today.month

col_main, col_side = st.columns([2.1, 1])

with col_side:
    st.markdown("#### 📌 이번 달 주요 일정")
    y, m = st.session_state["cal_year"], st.session_state["cal_month"]
    month_events = [e for e in all_legal_events if e["date"].year == y and e["date"].month == m]
    month_events_upcoming = sorted([e for e in month_events], key=lambda e: e["date"])
    if month_events_upcoming:
        for e in month_events_upcoming[:6]:
            if st.button(
                f'{TYPE_ICON.get(e["type"],"🔧")} {e["title"]}  ·  {dday_label(e["date"])}',
                key=f"side_ev_{e['id']}", use_container_width=True,
            ):
                st.session_state["cal_selected_event"] = ("legal", e["id"])
    else:
        st.caption("이번 달 등록된 일정이 없습니다.")

    st.markdown("#### 🔍 일정 필터")
    type_filter = st.multiselect("일정 유형", SCHEDULE_TYPES, default=[], key="sched_type_filter")
    inst_filter = st.selectbox("의료기관 종류", CATEGORY_INSTITUTIONS, key="sched_inst_filter")
    legal_filter = st.selectbox("구분", ["전체", "법정 일정", "자체 일정"], key="sched_legal_filter")

    st.markdown("#### 📥 리포트")
    month_html = build_calendar_month_html(y, m, month_events)
    st.download_button("이번 달 캘린더 HTML 리포트", data=month_html,
                        file_name=f"{y}년_{m}월_규정일정리포트.html", mime="text/html", use_container_width=True)

    with st.expander("➕ 일정 등록 (병원 자체 일정)"):
        with st.form("add_event_form", clear_on_submit=True):
            new_title = st.text_input("업무명")
            new_date = st.date_input("날짜", value=today)
            new_type = st.selectbox("유형", SCHEDULE_TYPES)
            new_memo = st.text_area("메모(준비사항 등)", height=70)
            add_submit = st.form_submit_button("등록", use_container_width=True)
        if add_submit:
            if new_title.strip():
                db.add_custom_event(new_date, new_title.strip(), new_type, new_memo, legal=False)
                st.success("일정이 등록되었습니다.")
                st.rerun()
            else:
                st.warning("업무명을 입력해 주세요.")

    with st.expander("🔁 반복 일정 설정 안내"):
        st.caption("매월·분기·반기·매년 반복되는 점검·보고 업무는 위 [일정 등록]에서 먼저 1건을 등록한 뒤, "
                    "다음 회차부터 동일한 방식으로 추가하시면 됩니다. (자동 반복 생성 기능은 추후 업데이트 예정)")

    with st.expander("🔔 알림 설정 안내"):
        st.caption("규정 일정 상세정보에서 항목별로 30일 전 / 14일 전 / 7일 전 / 3일 전 / 당일 알림을 설정할 수 있습니다.")

# ---------------- 필터 적용 ----------------
def event_passes_filter(e, legal):
    if type_filter and e["type"] not in type_filter:
        return False
    if inst_filter != "전체" and inst_filter not in e.get("institutions", ["전체"]) and "모든 의료기관" not in e.get("institutions", []):
        return False
    if legal_filter == "법정 일정" and not legal:
        return False
    if legal_filter == "자체 일정" and legal:
        return False
    return True


display_legal = [e for e in all_legal_events if event_passes_filter(e, True)]
display_custom = []
for ce in custom_events_raw:
    ce2 = dict(ce)
    ce2["date"] = date.fromisoformat(ce["event_date"])
    ce2["type"] = ce["event_type"]
    ce2["title"] = ce["title"]
    ce2["agency"] = "병원 자체 관리"
    ce2["legal"] = False
    ce2["completed"] = bool(ce["completed"])
    ce2["institutions"] = ["전체"]
    if event_passes_filter(ce2, False):
        display_custom.append(ce2)

with col_main:
    if view_mode == "월간":
        cal = calendar.Calendar(firstweekday=0)  # 월요일 시작
        month_days = cal.monthdatescalendar(y, m)

        hcols = st.columns(7)
        for hc, wd in zip(hcols, WEEKDAY_KR):
            hc.markdown(f"<div style='text-align:center;font-weight:700;color:#6B7280;'>{wd}</div>",
                        unsafe_allow_html=True)

        for week in month_days:
            wcols = st.columns(7)
            for wc, d in zip(wcols, week):
                in_month = d.month == m
                is_today = d == today
                day_events = [e for e in display_legal if e["date"] == d] + [e for e in display_custom if e["date"] == d]
                with wc:
                    day_style = "color:#111827;" if in_month else "color:#D1D5DB;"
                    if is_today:
                        day_style += "background:#2B5CE6;color:white;border-radius:6px;padding:1px 6px;display:inline-block;"
                    st.markdown(f"<div style='font-size:12.5px;{day_style}'>{d.day}</div>", unsafe_allow_html=True)
                    for e in day_events[:3]:
                        etype_key = "legal" if e in display_legal else "custom"
                        chip_color = TYPE_COLOR.get(e["type"], "#6B7280")
                        done_style = "text-decoration:line-through;opacity:0.5;" if e.get("completed") else ""
                        chip_label = e["title"][:8] + ("…" if len(e["title"]) > 8 else "")
                        if st.button(f"{TYPE_ICON.get(e['type'],'🔧')} {chip_label}", key=f"chip_{etype_key}_{e['id']}_{d.isoformat()}",
                                     help=f"{e['title']} ({dday_label(e['date'])})"):
                            st.session_state["cal_selected_event"] = (etype_key, e["id"])
                    if len(day_events) > 3:
                        st.caption(f"+{len(day_events)-3}건")
    else:
        st.markdown("#### 목록 보기")
        merged = sorted(display_legal + display_custom, key=lambda e: e["date"])
        if not merged:
            st.info("조건에 맞는 일정이 없습니다.")
        for e in merged:
            etype_key = "legal" if e in display_legal else "custom"
            with st.container():
                c1, c2, c3, c4 = st.columns([1.2, 2.6, 1.4, 1.2])
                c1.markdown(f"{TYPE_ICON.get(e['type'],'🔧')} {e['date'].strftime('%Y.%m.%d')} ({WEEKDAY_KR[e['date'].weekday()]})")
                title_disp = e["title"] + (" ✅" if e.get("completed") else "")
                if c2.button(title_disp, key=f"list_ev_{etype_key}_{e['id']}", use_container_width=True):
                    st.session_state["cal_selected_event"] = (etype_key, e["id"])
                c3.markdown(badge("법정" if e.get("legal", etype_key == "legal") else "자체", "blue" if etype_key == "legal" else "gray"),
                            unsafe_allow_html=True)
                c4.markdown(badge(dday_label(e["date"]), dday_kind(e["date"])), unsafe_allow_html=True)
            st.markdown("---")

st.markdown("#### 일정 유형 안내")
lg = st.columns(6)
type_desc = {
    "신고": "개설·변경·폐업, 인력·시설 신고 등", "보고": "정기보고, 수시보고 등",
    "교육": "법정교육, 보수교육, 직무교육 등", "점검": "자체점검, 정기점검, 안전점검 등",
    "기한": "면허신고, 등록갱신, 각종 제출기한 등", "기타": "병원 자체적으로 관리할 업무",
}
for c, t in zip(lg, SCHEDULE_TYPES):
    with c:
        st.markdown(f"{TYPE_ICON[t]} **{t}**")
        st.caption(type_desc[t])

st.info("ℹ️ 개정은 법령/고시/지침 변경 시 업데이트되며, 실제 신고·보고 시 관할 기관의 최신 안내를 확인하시기 바랍니다. "
        "D-Day는 기준일(오늘)로부터 남은 일수를 의미합니다.")

# ---------------- 선택된 일정 상세 패널 ----------------
sel = st.session_state.get("cal_selected_event")
if sel:
    kind, eid = sel
    if kind == "legal":
        target = next((e for e in all_legal_events if e["id"] == eid), None)
    else:
        target = next((dict(ce, date=date.fromisoformat(ce["event_date"])) for ce in custom_events_raw if ce["id"] == eid), None)

    if target:
        st.divider()
        st.markdown("### 📋 일정 상세정보")
        with st.container():
            st.markdown(f'<div class="detail-panel">', unsafe_allow_html=True)
            st.markdown(f"**{TYPE_ICON.get(target.get('type', target.get('event_type','기타')), '🔧')} "
                        f"{target.get('title')}**")
            dcols = st.columns(2)
            with dcols[0]:
                st.markdown(f"- 날짜: {target['date'].strftime('%Y.%m.%d')} ({dday_label(target['date'])})")
                st.markdown(f"- 대상: {target.get('target', '-')}")
                st.markdown(f"- 담당/신고기관: {target.get('agency', '병원 자체 관리')}")
            with dcols[1]:
                st.markdown(f"- 관련 법령: {target.get('related_law', '-')}")
                st.markdown(f"- 준비사항: {target.get('preparation', target.get('memo','-')) or '-'}")
                docs = target.get("required_docs", [])
                if isinstance(docs, list) and docs:
                    st.markdown(f"- 필요서류: {', '.join(docs)}")

            bcols = st.columns(4)
            with bcols[0]:
                st.button("📖 관련 규정 확인", key=f"det_law_{kind}_{eid}", use_container_width=True)
            with bcols[1]:
                st.button("📎 필요서류 확인", key=f"det_doc_{kind}_{eid}", use_container_width=True)
            with bcols[2]:
                if kind == "legal":
                    ekey = f"legal_{eid}"
                    is_done = db.get_completion(ekey)
                    if st.button("✅ 완료 처리" if not is_done else "↩️ 완료 취소", key=f"det_done_{kind}_{eid}", use_container_width=True):
                        db.set_completion(ekey, not is_done)
                        st.rerun()
                else:
                    if st.button("✅ 완료 처리 / 취소", key=f"det_done_custom_{eid}", use_container_width=True):
                        db.toggle_custom_event_complete(eid)
                        st.rerun()
            with bcols[3]:
                if kind == "custom":
                    if st.button("🗑️ 일정 삭제", key=f"det_del_{eid}", use_container_width=True):
                        db.delete_custom_event(eid)
                        st.session_state["cal_selected_event"] = None
                        st.rerun()

            with st.expander("🔔 이 일정에 대한 알림 설정"):
                ekey = f"{kind}_{eid}"
                current = db.get_notification(ekey)
                chosen = st.multiselect("알림 시점", [30, 14, 7, 3, 0],
                                         default=current,
                                         format_func=lambda x: "당일" if x == 0 else f"{x}일 전",
                                         key=f"notif_{ekey}")
                if st.button("알림 저장", key=f"notif_save_{ekey}"):
                    db.set_notification(ekey, chosen)
                    st.success("알림이 저장되었습니다.")
            st.markdown("</div>", unsafe_allow_html=True)
