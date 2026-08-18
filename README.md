# MEDIUM 의료기관 규정 관리 시스템

병원 개원·경영 컨설팅 실무에 사용하는 **유료 Streamlit 웹앱**입니다.
규정 통합검색 / 운영·시설 기준 / 인력·자격 기준 / 신고·보고 관리 / 규정 일정 관리(컴플라이언스 캘린더)
5개 모듈로 구성되어 있으며, 병원명·직원 명단·병원 내부정보는 저장하지 않습니다.

## 폴더 구조

```
medium_compliance/
├── app.py                     # 진입점 (네비게이션 + 라이선스 게이트)
├── requirements.txt
├── data/
│   ├── facility_data.py       # 운영·시설 기준 샘플 데이터 (18건)
│   ├── personnel_data.py      # 인력·자격 기준 샘플 데이터 (14건)
│   ├── report_data.py         # 신고·보고 관리 샘플 데이터 (15건)
│   ├── schedule_data.py       # 규정 일정(캘린더) 샘플 데이터 (오늘 기준 동적 생성)
│   └── master.py              # 통합검색 인덱스 및 집계
├── utils/
│   ├── styles.py               # 공통 CSS
│   ├── db.py                   # SQLite (즐겨찾기·개인일정·완료체크·알림설정만 저장)
│   ├── detail_panel.py         # 상세정보 패널 (규정/신고 공용)
│   ├── html_export.py          # 자급식 HTML 리포트 생성(저장/인쇄용)
│   ├── ai_client.py            # Gemini API 클라이언트 (모델 자동 폴백 + 규칙기반 폴백)
│   └── license_gate.py         # 유료 라이선스 키 검증
└── views/
    ├── home.py         # 규정 통합검색 + AI 컴플라이언스 자가진단
    ├── facility.py      # 운영·시설 기준
    ├── personnel.py     # 인력·자격 기준
    ├── report.py        # 신고·보고 관리
    └── schedule.py       # 규정 일정 관리 (업무 캘린더)
```

## 로컬 실행

```bash
pip install -r requirements.txt
streamlit run app.py
```

최초 접속 시 라이선스 키 입력 화면이 표시됩니다. 데모 키: `MEDIUM-DEMO-2026`

## Streamlit Community Cloud 배포

1. GitHub 새 저장소 생성 후 이 폴더 전체를 업로드(웹 UI 드래그앤드롭 가능)
2. [share.streamlit.io](https://share.streamlit.io) 에서 새 앱 생성, Main file은 `app.py`로 지정
3. **App settings → Secrets**에 아래 값을 등록 (`.streamlit/secrets.toml.example` 참고)
   ```
   GEMINI_API_KEY = "실제_API_키"
   VALID_LICENSE_KEYS = "MEDIUM-0001-AAAA,MEDIUM-0002-BBBB"
   ```
4. 배포 후 발급한 라이선스 키를 구매 고객에게 안내

## AI 컴플라이언스 자가진단

- 모델 우선순위: `gemini-3.6-flash` → `gemini-3.5-flash-lite` → `gemini-2.5-flash` → `gemini-2.0-flash`
- 모든 모델 호출 실패 또는 API 키 미설정 시 규칙 기반 폴백 진단으로 자동 전환되어 서비스가 끊기지 않습니다.
- 응답은 JSON 스키마(`responseSchema`)로 강제하여 안정적으로 파싱합니다.

## 데이터에 대한 안내

- 현재 각 모듈의 규정·신고·일정 데이터는 실무 시연을 위한 **샘플(참고용) 데이터셋**입니다.
- 실서비스 전, 반드시 최신 법령 원문·고시·지침과 대조하여 데이터를 검증·보강하시기 바랍니다.
- 데이터 건수를 늘리려면 `data/*.py`의 리스트에 동일한 딕셔너리 구조로 항목을 추가하면 자동으로
  검색/필터/상세패널/HTML 리포트에 반영됩니다.

## 개인정보 및 저장 정책

이 시스템은 병원 이름, 직원 명단, 환자 정보 등 병원 내부정보를 저장하지 않습니다.
SQLite에는 사용자의 이용 편의를 위한 **즐겨찾기, 개인(자체) 일정 라벨, 완료 체크 상태, 알림 설정값**만 저장됩니다.
