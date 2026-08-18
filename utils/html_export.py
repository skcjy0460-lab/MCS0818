# -*- coding: utf-8 -*-
"""자급식(self-contained) HTML 리포트 생성 유틸.
브라우저에서 열어 바로 확인/인쇄(PDF 저장: Ctrl+P → PDF로 저장)할 수 있도록 구성합니다.
"""
from datetime import datetime

REPORT_CSS = """
<style>
  * { box-sizing: border-box; }
  body { font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; background:#F5F7FB; margin:0; padding:32px; color:#111827; }
  .wrap { max-width: 860px; margin: 0 auto; background: white; border-radius: 14px; padding: 36px 40px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
  .brand { font-size: 13px; color:#2B5CE6; font-weight:800; letter-spacing:1px; }
  .gen-date { font-size: 11px; color:#9CA3AF; margin-bottom: 18px; }
  h1 { font-size: 22px; margin: 6px 0 18px 0; color:#111827; border-bottom: 3px solid #2B5CE6; padding-bottom: 12px;}
  h2 { font-size: 15px; margin-top: 26px; color:#1E3A8A; border-left: 4px solid #2B5CE6; padding-left: 10px; }
  .badge { display:inline-block; background:#E3EAFD; color:#1E3A8A; font-size:11px; font-weight:700; padding:2px 10px; border-radius:20px; margin-bottom:8px;}
  table.meta { width:100%; border-collapse: collapse; font-size: 13px; margin-bottom: 8px;}
  table.meta td { padding: 6px 4px; border-bottom: 1px dashed #EEF1F6; }
  table.meta td.k { width: 110px; color:#6B7280; }
  ul.check li { font-size: 13.5px; margin-bottom: 4px; }
  .box { background:#F8FAFF; border-radius:10px; padding: 12px 16px; font-size:13px; margin-bottom:8px;}
  .warn { background:#FFFBEB; border-left:3px solid #F59E0B; padding:8px 12px; font-size:13px; margin-bottom:6px; border-radius:4px;}
  .step { background:#F5F7FB; border-left:4px solid #2B5CE6; border-radius:8px; padding:10px 14px; margin-bottom:8px;}
  .step .label { font-size:11px; font-weight:800; color:#2B5CE6; }
  .step .title { font-size:14px; font-weight:700; margin: 2px 0 4px 0;}
  .doc-tag { display:inline-block; font-size:11px; font-weight:700; padding:2px 8px; border-radius: 12px; margin-right:6px;}
  .tag-req { background:#FDE8E8; color:#B91C1C; }
  .tag-opt { background:#FEF0DE; color:#B4600A; }
  .tag-sel { background:#EEF0F3; color:#4B5563; }
  .qna { margin-bottom: 10px; }
  .qna .q { font-weight:700; font-size:13.5px; }
  .qna .a { font-size:13px; color:#374151; margin-top:2px; }
  .footer { margin-top: 28px; font-size: 11px; color:#9CA3AF; text-align:center; }
  @media print { body { background:white; padding:0;} .wrap{ box-shadow:none; } }
</style>
"""


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def build_regulation_report_html(item: dict) -> str:
    checklist = "".join(f"<li>{c}</li>" for c in item.get("core_checklist", []))
    v = item.get("violation", {})
    labels = {"administrative_disposition": "행정처분", "fine": "과태료", "penalty": "벌칙(형사)",
              "corrective_order": "시정명령", "basis": "법적 근거"}
    violation_html = "".join(
        f'<div class="box"><b>{labels[k]}</b><br>{v[k]}</div>' for k in labels if v.get(k)
    )
    forms_html = "".join(f"<li>{f}</li>" for f in item.get("forms", [])) or "<li>등록된 서식 없음</li>"
    qna_html = "".join(
        f'<div class="qna"><div class="q">Q. {qa["q"]}</div><div class="a">A. {qa["a"]}</div></div>'
        for qa in item.get("qna", [])
    ) or "<div>등록된 Q&amp;A가 없습니다.</div>"

    return f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<title>{item['title']} - MEDIUM 규정 리포트</title>{REPORT_CSS}</head>
<body><div class="wrap">
  <div class="brand">MEDIUM · 의료기관 규정 관리 시스템</div>
  <div class="gen-date">생성일시: {_now()}</div>
  <span class="badge">{item['category']}</span>
  <h1>{item['title']}</h1>
  <table class="meta">
    <tr><td class="k">관련 법령</td><td>{item['related_law']}</td></tr>
    <tr><td class="k">적용 의료기관</td><td>{', '.join(item['institutions'])}</td></tr>
    <tr><td class="k">최종 개정일</td><td>{item['revision_date']}</td></tr>
    <tr><td class="k">관련 부처</td><td>{item.get('department','-')}</td></tr>
    <tr><td class="k">키워드</td><td>{' '.join('#'+k for k in item.get('keywords', []))}</td></tr>
  </table>

  <h2>핵심 체크 항목</h2>
  <ul class="check">{checklist}</ul>

  <h2>상세 내용</h2>
  <div class="box">{item.get('detail_content','')}</div>

  <h2>위반 시 조치</h2>
  {violation_html or '<div class="box">등록된 위반 조치 정보가 없습니다.</div>'}

  <h2>관련 서식</h2>
  <ul>{forms_html}</ul>

  <h2>Q&amp;A</h2>
  {qna_html}

  <div class="footer">본 리포트는 실무 참고용으로 제작되었으며, 법적 판단의 최종 근거는 반드시 관련 법령 원문 및 소관 부처 확인을 통해 검증하시기 바랍니다.<br>
  ⓒ MEDIUM Medical Premium Consulting</div>
</div></body></html>"""


def build_report_item_html(item: dict) -> str:
    checklist = "".join(f"<li>{c}</li>" for c in item.get("core_checklist", []))
    doc_tag_cls = {"필수": "tag-req", "해당 시": "tag-opt", "선택": "tag-sel"}
    docs_html = "".join(
        f'<div><span class="doc-tag {doc_tag_cls.get(d["type"],"tag-sel")}">{d["type"]}</span> {d["name"]}</div>'
        for d in item.get("required_docs", [])
    ) or "<div>등록된 필요서류가 없습니다.</div>"
    steps_html = "".join(
        f'<div class="step"><div class="label">{s["step"]}</div><div class="title">{s["title"]}</div>{s["desc"]}</div>'
        for s in item.get("procedure_steps", [])
    )
    cautions_html = "".join(f'<div class="warn">⚠ {c}</div>' for c in item.get("cautions", []))
    qna_html = "".join(
        f'<div class="qna"><div class="q">Q. {qa["q"]}</div><div class="a">A. {qa["a"]}</div></div>'
        for qa in item.get("qna", [])
    ) or "<div>등록된 Q&amp;A가 없습니다.</div>"

    return f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<title>{item['title']} - MEDIUM 신고·보고 리포트</title>{REPORT_CSS}</head>
<body><div class="wrap">
  <div class="brand">MEDIUM · 의료기관 규정 관리 시스템</div>
  <div class="gen-date">생성일시: {_now()}</div>
  <span class="badge">{item['category']}</span>
  <h1>{item['title']}</h1>
  <table class="meta">
    <tr><td class="k">신고 대상</td><td>{item['target']}</td></tr>
    <tr><td class="k">신고 기관</td><td>{item['agency']}</td></tr>
    <tr><td class="k">신고 기한</td><td>{item['period']}</td></tr>
    <tr><td class="k">관련 법령</td><td>{item['related_law']}</td></tr>
    <tr><td class="k">적용 의료기관</td><td>{', '.join(item['institutions'])}</td></tr>
  </table>

  <h2>신고 개요</h2>
  <div class="box">{item.get('overview','')}</div>
  <ul class="check">{checklist}</ul>

  <h2>필요 서류</h2>
  {docs_html}

  <h2>신고 절차</h2>
  {steps_html}

  <h2>주의사항</h2>
  {cautions_html or '<div class="box">등록된 주의사항이 없습니다.</div>'}
  <div class="box"><b>과태료·행정처분 근거</b><br>{item.get('penalty_basis','-')}</div>

  <h2>Q&amp;A</h2>
  {qna_html}

  <div class="footer">본 리포트는 실무 참고용으로 제작되었으며, 신고기한·필요서류 등은 관할 기관 최신 공지를 반드시 확인하시기 바랍니다.<br>
  ⓒ MEDIUM Medical Premium Consulting</div>
</div></body></html>"""


def build_search_summary_html(query: str, results: list) -> str:
    rows = "".join(
        f"<tr><td>{r['category']}</td><td>{r['title']}</td><td>{r['related_law']}</td>"
        f"<td>{', '.join(r['institutions'])}</td><td>{r['revision_date']}</td></tr>"
        for r in results
    )
    return f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<title>규정 통합검색 결과 - {query}</title>{REPORT_CSS}
<style>table.res {{ width:100%; border-collapse: collapse; font-size:13px; margin-top:10px;}}
table.res th {{ background:#F5F7FB; text-align:left; padding:8px; border-bottom:2px solid #E5E9F2;}}
table.res td {{ padding:8px; border-bottom:1px solid #EEF1F6;}}</style></head>
<body><div class="wrap">
  <div class="brand">MEDIUM · 의료기관 규정 관리 시스템</div>
  <div class="gen-date">생성일시: {_now()}</div>
  <h1>규정 통합검색 결과: "{query}"</h1>
  <p style="font-size:13px;color:#4B5563;">총 {len(results)}건이 검색되었습니다.</p>
  <table class="res">
    <tr><th>구분</th><th>제목</th><th>관련 법령</th><th>적용 의료기관</th><th>최종 개정</th></tr>
    {rows}
  </table>
  <div class="footer">ⓒ MEDIUM Medical Premium Consulting</div>
</div></body></html>"""


def build_calendar_month_html(year: int, month: int, events: list) -> str:
    rows = "".join(
        f"<tr><td>{e['date'].strftime('%m.%d')} ({['월','화','수','목','금','토','일'][e['date'].weekday()]})</td>"
        f"<td>{e['type']}</td><td>{'법정' if e['legal'] else '자체'}</td><td>{e['title']}</td>"
        f"<td>{e['agency']}</td><td>{'완료' if e.get('completed') else '진행중'}</td></tr>"
        for e in sorted(events, key=lambda x: x['date'])
    )
    return f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<title>{year}년 {month}월 규정 일정 리포트</title>{REPORT_CSS}
<style>table.res {{ width:100%; border-collapse: collapse; font-size:13px; margin-top:10px;}}
table.res th {{ background:#F5F7FB; text-align:left; padding:8px; border-bottom:2px solid #E5E9F2;}}
table.res td {{ padding:8px; border-bottom:1px solid #EEF1F6;}}</style></head>
<body><div class="wrap">
  <div class="brand">MEDIUM · 의료기관 규정 관리 시스템</div>
  <div class="gen-date">생성일시: {_now()}</div>
  <h1>{year}년 {month}월 규정 업무 캘린더 리포트</h1>
  <table class="res">
    <tr><th>날짜</th><th>유형</th><th>구분</th><th>업무명</th><th>담당/신고기관</th><th>상태</th></tr>
    {rows}
  </table>
  <div class="footer">ⓒ MEDIUM Medical Premium Consulting</div>
</div></body></html>"""
