# -*- coding: utf-8 -*-
"""규정 일정 관리 - 컴플라이언스 캘린더 데이터
일정 유형: 신고 / 보고 / 교육 / 점검 / 기한 / 기타
법정 일정(legal=True) vs 병원 자체 일정(legal=False) 구분
"""
from datetime import date, timedelta

SCHEDULE_TYPES = ["신고", "보고", "교육", "점검", "기한", "기타"]

TYPE_ICON = {
    "신고": "🏢", "보고": "📑", "교육": "🎓", "점검": "⭐", "기한": "📌", "기타": "🔧",
}
TYPE_COLOR = {
    "신고": "#EF4444", "보고": "#3B82F6", "교육": "#10B981",
    "점검": "#F59E0B", "기한": "#8B5CF6", "기타": "#6B7280",
}


def _d(days_from_today: int) -> date:
    return date.today() + timedelta(days=days_from_today)


def build_schedule_events():
    """오늘 날짜 기준으로 상대적인 일정 데이터를 생성합니다 (데모용)."""
    events = [
        {
            "id": 1, "date": _d(2), "title": "의료기관 현황 보고", "type": "보고", "legal": True,
            "target": "의료기관 전체", "agency": "건강보험심사평가원", "related_law": "의료법 제43조",
            "preparation": "인력·시설·장비 현황표 최신화", "required_docs": ["의료기관 현황 신고서"],
            "institutions": ["모든 의료기관"], "completed": False,
        },
        {
            "id": 2, "date": _d(5), "title": "의료인 보수교육 이수 마감", "type": "교육", "legal": True,
            "target": "의사·간호사 등 의료인 전원", "agency": "관할 협회", "related_law": "의료법 제30조의2",
            "preparation": "미이수자 명단 확인 및 독려", "required_docs": ["보수교육 이수 확인서"],
            "institutions": ["모든 의료기관"], "completed": False,
        },
        {
            "id": 3, "date": _d(7), "title": "의료장비 정기점검", "type": "점검", "legal": False,
            "target": "전 의료장비", "agency": "원내 시설팀", "related_law": "의료기기법",
            "preparation": "장비별 점검 체크리스트 준비", "required_docs": ["의료장비 관리대장"],
            "institutions": ["병원", "종합병원"], "completed": False,
        },
        {
            "id": 4, "date": _d(11), "title": "정기보고 제출 마감", "type": "보고", "legal": True,
            "target": "의료기관 전체", "agency": "건강보험심사평가원", "related_law": "관련 고시",
            "preparation": "제출 서식 최종 검토", "required_docs": ["정기보고서"],
            "institutions": ["모든 의료기관"], "completed": False,
        },
        {
            "id": 5, "date": _d(13), "title": "간호사 면허신고 마감", "type": "기한", "legal": True,
            "target": "간호사", "agency": "간호협회", "related_law": "의료법 제25조",
            "preparation": "면허신고 대상자 확인", "required_docs": ["면허신고서"],
            "institutions": ["모든 의료기관"], "completed": False,
        },
        {
            "id": 6, "date": _d(16), "title": "CCTV 저장기간 점검", "type": "점검", "legal": False,
            "target": "CCTV 설치구역", "agency": "원내 시설팀", "related_law": "개인정보보호법",
            "preparation": "저장기간 및 접근기록 점검", "required_docs": ["CCTV 운영 관리대장"],
            "institutions": ["병원", "의원"], "completed": False,
        },
        {
            "id": 7, "date": _d(19), "title": "감염관리 자율점검", "type": "점검", "legal": False,
            "target": "감염관리실", "agency": "원내 감염관리위원회", "related_law": "감염병예방법",
            "preparation": "체크리스트 기반 자체점검 실시", "required_docs": ["자체점검 결과보고서"],
            "institutions": ["병원", "종합병원"], "completed": False,
        },
        {
            "id": 8, "date": _d(22), "title": "의료기관 변경 신고 마감", "type": "신고", "legal": True,
            "target": "변경사항 발생 의료기관", "agency": "시·군·구 보건소", "related_law": "의료법 제33조 제5항",
            "preparation": "변경 증빙서류 준비", "required_docs": ["의료기관 변경신고서"],
            "institutions": ["모든 의료기관"], "completed": False,
        },
        {
            "id": 9, "date": _d(27), "title": "의료기관 변경 신고 마감(2)", "type": "신고", "legal": True,
            "target": "변경사항 발생 의료기관", "agency": "시·군·구 보건소", "related_law": "의료법 제33조 제5항",
            "preparation": "변경 증빙서류 준비", "required_docs": ["의료기관 변경신고서"],
            "institutions": ["모든 의료기관"], "completed": False,
        },
        {
            "id": 10, "date": _d(28), "title": "마약류 관리 교육", "type": "교육", "legal": True,
            "target": "마약류 취급 의료인", "agency": "관할 지자체", "related_law": "마약류 관리에 관한 법률",
            "preparation": "대상자 명단 확인 및 교육 신청", "required_docs": ["교육 이수 확인서"],
            "institutions": ["병원", "종합병원"], "completed": False,
        },
        {
            "id": 11, "date": _d(30), "title": "당직의료인 기준 점검", "type": "점검", "legal": False,
            "target": "당직 운영 부서", "agency": "원내 간호부", "related_law": "의료법 시행규칙 제39조",
            "preparation": "당직표와 근태기록 대조", "required_docs": ["당직의료인 명단 및 배치표"],
            "institutions": ["병원", "종합병원"], "completed": False,
        },
        {
            "id": 12, "date": _d(34), "title": "소방시설 자체점검 결과 제출", "type": "보고", "legal": True,
            "target": "의료기관 전체", "agency": "관할 소방서", "related_law": "소방시설 설치 및 관리에 관한 법률",
            "preparation": "작동기능점검 결과 정리", "required_docs": ["소방시설 자체점검 결과보고서"],
            "institutions": ["모든 의료기관"], "completed": False,
        },
        {
            "id": 13, "date": _d(40), "title": "의료폐기물 위탁계약 갱신", "type": "기한", "legal": True,
            "target": "폐기물 배출기관", "agency": "위탁처리업체", "related_law": "폐기물관리법",
            "preparation": "계약서 갱신 및 인계서 점검", "required_docs": ["의료폐기물 위탁처리 계약서"],
            "institutions": ["모든 의료기관"], "completed": False,
        },
        {
            "id": 14, "date": _d(45), "title": "개인정보 내부관리계획 점검", "type": "기타", "legal": False,
            "target": "개인정보 취급부서", "agency": "원내 개인정보보호책임자", "related_law": "개인정보보호법",
            "preparation": "내부관리계획 갱신 여부 확인", "required_docs": [],
            "institutions": ["모든 의료기관"], "completed": False,
        },
        {
            "id": 15, "date": _d(52), "title": "직원 법정의무교육(성희롱예방 등)", "type": "교육", "legal": True,
            "target": "전 직원", "agency": "관할부처", "related_law": "관련 개별 법령",
            "preparation": "교육자료 준비 및 일정 공지", "required_docs": ["법정의무교육 이수 현황표"],
            "institutions": ["모든 의료기관"], "completed": False,
        },
        {
            "id": 16, "date": _d(-3), "title": "의료장비 품질관리검사(특수의료장비)", "type": "점검", "legal": True,
            "target": "특수의료장비 보유기관", "agency": "한국의료영상품질관리원", "related_law": "특수의료장비의 설치 및 운영에 관한 규칙",
            "preparation": "검사 신청 및 장비 점검", "required_docs": ["품질관리검사 신청서"],
            "institutions": ["병원", "종합병원"], "completed": True,
        },
        {
            "id": 17, "date": _d(-10), "title": "간호인력 현황 정기 점검", "type": "점검", "legal": False,
            "target": "간호부", "agency": "원내 인사팀", "related_law": "의료법 시행규칙 제37조",
            "preparation": "부서별 배치기준 대비 실인원 확인", "required_docs": [],
            "institutions": ["병원", "종합병원"], "completed": True,
        },
    ]
    return events


CATEGORY_INSTITUTIONS = ["전체", "의원", "병원", "종합병원", "요양병원"]
