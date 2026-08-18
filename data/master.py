# -*- coding: utf-8 -*-
"""규정 통합검색 페이지에서 사용하는 전체 데이터 집계 모듈.
5개 카테고리(운영·시설 / 인력·자격 / 신고·보고 / 규정일정)의 데이터를
하나의 통합 인덱스로 묶어 키워드 검색이 가능하도록 합니다.
"""
from data.facility_data import FACILITY_DATA
from data.personnel_data import PERSONNEL_DATA
from data.report_data import REPORT_DATA
from data.schedule_data import build_schedule_events

SECTION_META = {
    "facility": {
        "label": "운영·시설 기준", "icon": "🏢", "page": "views/facility.py",
        "desc": "의료기관 운영 및 시설·장비 관련 기준을 확인합니다.",
        "bullets": ["서류·기록 관리", "시설 기준", "장비·CCTV 기준", "감염관리·소독 기준"],
    },
    "personnel": {
        "label": "인력·자격 기준", "icon": "👥", "page": "views/personnel.py",
        "desc": "의료인 및 직원의 배치 기준과 자격 요건을 확인합니다.",
        "bullets": ["직종별 배치 기준", "자격·면허 기준", "당직·겸직 기준", "교육·보수교육 기준"],
    },
    "report": {
        "label": "신고·보고 관리", "icon": "📋", "page": "views/report.py",
        "desc": "개설·변경·폐업 및 각종 신고와 보고 일정을 관리합니다.",
        "bullets": ["개설·변경·폐업 신고", "인력·시설 신고", "정기 보고", "신고 서식 및 가이드"],
    },
    "schedule": {
        "label": "규정 일정 관리", "icon": "🗓️", "page": "views/schedule.py",
        "desc": "신고·보고·교육·점검 등 주요 일정을 한눈에 관리합니다.",
        "bullets": ["월별 주요 일정", "교육·보수교육 일정", "점검·평가 일정", "알림 설정"],
    },
}


def build_unified_index():
    """검색용 통합 인덱스: (섹션키, 원본레코드, 검색텍스트) 리스트."""
    index = []
    for item in FACILITY_DATA:
        text = " ".join([item["title"], item["category"], item["related_law"],
                          " ".join(item.get("keywords", []))])
        index.append({"section": "facility", "record": item, "text": text, "title": item["title"],
                       "category": item["category"], "related_law": item["related_law"],
                       "institutions": item["institutions"], "revision_date": item["revision_date"]})
    for item in PERSONNEL_DATA:
        text = " ".join([item["title"], item["category"], item["related_law"],
                          item.get("job_type", ""), " ".join(item.get("keywords", []))])
        index.append({"section": "personnel", "record": item, "text": text, "title": item["title"],
                       "category": item["category"], "related_law": item["related_law"],
                       "institutions": item["institutions"], "revision_date": item["revision_date"]})
    for item in REPORT_DATA:
        text = " ".join([item["title"], item["category"], item["related_law"], item["target"], item["agency"]])
        index.append({"section": "report", "record": item, "text": text, "title": item["title"],
                       "category": item["category"], "related_law": item["related_law"],
                       "institutions": item["institutions"], "revision_date": item["revision_date"]})
    return index


def counts_summary():
    facility_cat_counts = {}
    for item in FACILITY_DATA:
        facility_cat_counts[item["category"]] = facility_cat_counts.get(item["category"], 0) + 1
    personnel_cat_counts = {}
    for item in PERSONNEL_DATA:
        personnel_cat_counts[item["category"]] = personnel_cat_counts.get(item["category"], 0) + 1
    report_cat_counts = {}
    for item in REPORT_DATA:
        report_cat_counts[item["category"]] = report_cat_counts.get(item["category"], 0) + 1
    return {
        "total": len(FACILITY_DATA) + len(PERSONNEL_DATA) + len(REPORT_DATA),
        "facility": len(FACILITY_DATA), "personnel": len(PERSONNEL_DATA), "report": len(REPORT_DATA),
        "schedule": len(build_schedule_events()),
        "facility_cat": facility_cat_counts, "personnel_cat": personnel_cat_counts, "report_cat": report_cat_counts,
    }
