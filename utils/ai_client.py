# -*- coding: utf-8 -*-
"""Gemini API 클라이언트.
모델 우선순위: gemini-3.6-flash → gemini-3.5-flash-lite → gemini-2.5-flash → gemini-2.0-flash
API 키가 없거나 모든 모델 호출이 실패하면 rule-based 폴백 진단으로 대체합니다.
"""
import json
import requests
import streamlit as st

MODEL_FALLBACK_CHAIN = [
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
]

API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

DIAGNOSIS_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "overall_risk": {"type": "STRING", "enum": ["낮음", "보통", "높음", "매우 높음"]},
        "summary": {"type": "STRING"},
        "checklist_results": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "area": {"type": "STRING"},
                    "status": {"type": "STRING", "enum": ["적정", "미흡", "확인 필요"]},
                    "comment": {"type": "STRING"},
                },
                "required": ["area", "status", "comment"],
            },
        },
        "recommended_actions": {"type": "ARRAY", "items": {"type": "STRING"}},
        "related_keywords": {"type": "ARRAY", "items": {"type": "STRING"}},
    },
    "required": ["overall_risk", "summary", "checklist_results", "recommended_actions", "related_keywords"],
}


def _get_api_key():
    try:
        return st.secrets.get("GEMINI_API_KEY", None)
    except Exception:
        return None


def _call_model(model: str, prompt: str, api_key: str, json_mode: bool = True, schema: dict = None):
    url = f"{API_BASE}/{model}:generateContent?key={api_key}"
    gen_config = {"temperature": 0.3}
    if json_mode:
        gen_config["responseMimeType"] = "application/json"
        if schema:
            gen_config["responseSchema"] = schema
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": gen_config,
    }
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    return text


def generate_with_fallback(prompt: str, json_mode: bool = True, schema: dict = None):
    """모델 체인을 순서대로 시도. 모두 실패하면 (None, error_message) 반환."""
    api_key = _get_api_key()
    if not api_key:
        return None, "GEMINI_API_KEY가 설정되어 있지 않습니다."

    last_error = None
    for model in MODEL_FALLBACK_CHAIN:
        try:
            text = _call_model(model, prompt, api_key, json_mode=json_mode, schema=schema)
            return text, None
        except Exception as e:
            last_error = f"{model} 호출 실패: {e}"
            continue
    return None, last_error


def _rule_based_diagnosis(institution_type, bed_count, concerns):
    """API 미설정/실패 시 사용하는 규칙 기반 폴백 진단 (데모/오프라인 대비)."""
    risk = "보통"
    results = []
    actions = []
    if institution_type in ["병원", "종합병원"] and bed_count and bed_count >= 200:
        results.append({"area": "간호인력 배치", "status": "확인 필요",
                         "comment": "병상 규모가 커질수록 간호인력 배치기준 위반 리스크가 높아집니다. 최신 배치기준 대비 실인원을 다시 확인하세요."})
        actions.append("간호인력 배치기준 재점검 및 예비인력 확보 계획 수립")
    if "당직" in concerns or "야간" in concerns:
        results.append({"area": "당직의료인 운영", "status": "미흡",
                         "comment": "당직표와 실제 근무기록(출입기록 등)을 상호 대조하는 절차가 필요합니다."})
        actions.append("당직표-근태기록 정기 대조 절차 마련")
        risk = "높음"
    if "cctv" in concerns.lower() or "개인정보" in concerns:
        results.append({"area": "CCTV/개인정보", "status": "확인 필요",
                         "comment": "저장기간 준수 및 안내표지 부착 여부를 점검하세요."})
        actions.append("CCTV 저장기간·안내표지 자체점검 실시")
    if not results:
        results.append({"area": "종합", "status": "적정",
                         "comment": "입력하신 정보 기준으로 별도 고위험 요소는 확인되지 않았습니다. 정기점검을 지속하세요."})
        actions.append("정기 자체점검 체계 유지")

    return {
        "overall_risk": risk,
        "summary": f"{institution_type} 기준 자가진단 결과입니다. (AI 연결 없이 규칙 기반으로 산출된 참고용 결과입니다.)",
        "checklist_results": results,
        "recommended_actions": actions,
        "related_keywords": [institution_type, "정기점검", "자가진단"],
    }


def run_compliance_diagnosis(institution_type, bed_count, concerns_text):
    """AI 컴플라이언스 자가진단 실행. (institution_type, bed_count, 우려사항 자유서술)"""
    prompt = f"""당신은 대한민국 의료기관 규정·컴플라이언스 전문 컨설턴트입니다.
아래 병원 정보를 바탕으로 규정 준수 리스크를 진단해 주세요.

- 의료기관 종별: {institution_type}
- 병상 수: {bed_count if bed_count else '미입력'}
- 실무자가 우려하는 사항: {concerns_text if concerns_text else '없음'}

의료법 시행규칙상 시설기준, 인력배치기준, 신고·보고 의무, 감염관리기준 등을 종합적으로 고려하여
점검이 필요한 영역과 실무 조치사항을 제시해 주세요. 반드시 실제 법령 조문 번호를 단정적으로 창작하지 말고
일반적인 실무 체크포인트 중심으로 답변하세요. 지정된 JSON 스키마 형식으로만 응답하세요."""

    text, error = generate_with_fallback(prompt, json_mode=True, schema=DIAGNOSIS_SCHEMA)
    if text:
        try:
            parsed = json.loads(text)
            return parsed, None
        except Exception:
            pass
    # 폴백
    fallback = _rule_based_diagnosis(institution_type, bed_count, concerns_text or "")
    note = error or "AI 응답을 해석할 수 없어 기본 진단으로 대체되었습니다."
    return fallback, note
