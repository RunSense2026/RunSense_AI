# RunSense_AI

동양미래대 2026 졸업작품 런센스 AI

# RunSense AI Server

RunSense 프로젝트의 AI 코칭 서버입니다.

현재 버전은 아래 기능들을 중심으로 구현되어 있습니다.

```text
러닝 히스토리 구조화
학습 기록 CRUD 개발 및 API 작성
프롬프트 설계 및 튜닝
Gemini LLM API 연동
오류 처리 및 예외 케이스 처리
```

---

# 현재 구현 범위

## 데이터

```text
AI 코칭 기록 저장
AI 코칭 기록 조회
AI 코칭 기록 수정
AI 코칭 기록 삭제
Supabase PostgreSQL 연동
기존 running_activity 테이블 연동
기존 ai_coaching 테이블 연동
```

---

## AI / LLM

```text
러닝 데이터 규칙 기반 분석
Gemini API 연동
AI 러닝 코칭 문장 생성
프롬프트 설계 및 튜닝
Fallback 메시지 처리
```

---

## 서버

```text
FastAPI 서버 구축
Swagger API 문서 자동 생성
Pydantic 기반 JSON 검증
예외 처리 및 오류 응답 처리
```

---

# 추후 구현 예정

```text
텍스트 -> 음성 변환 모듈 개발
음질, 발음, 속도 조정
백엔드 데이터 흐름 연결
앱 화면과 인터랙션 연결
Spring Boot 연동
React Native 연동
실시간 센서 데이터 처리
```

---

# 스택

* Python
* FastAPI
* Uvicorn
* SQLAlchemy
* PostgreSQL / Supabase
* Gemini API
* Pydantic

---

# 폴더 구조

```text
RunSense_AI/
├── main.py
├── db.py
├── run_model.py
├── run_schema.py
├── crud.py
├── analysis_service.py
├── prompt_service.py
├── llm_service.py
├── tts_service.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

# 파일 역할

| 파일                    | 역할                     |
| --------------------- | ---------------------- |
| `main.py`             | FastAPI API 관리         |
| `db.py`               | Supabase PostgreSQL 연결 |
| `run_model.py`        | ai_coaching 테이블 모델     |
| `run_schema.py`       | 요청/응답 JSON 구조          |
| `crud.py`             | AI 코칭 CRUD 처리          |
| `analysis_service.py` | 러닝 데이터 분석              |
| `prompt_service.py`   | Gemini 프롬프트 생성         |
| `llm_service.py`      | Gemini API 호출 및 오류 처리  |
| `tts_service.py`      | 추후 TTS 기능 확장용          |
| `requirements.txt`    | Python 라이브러리 목록        |
| `.env.example`        | 환경변수 예시                |
| `.gitignore`          | GitHub 업로드 제외 파일 설정    |

---

# 현재 DB 구조

## users

```text
사용자 계정 정보 저장
```

## running_activity

```text
러닝 활동 기록 저장
```

## foot_sensor_data

```text
족압 및 착지 데이터 저장
```

## ai_coaching

```text
AI 코칭 결과 저장
```

---

# 시작하기

## 1. 가상환경 생성(필요하다면)

```powershell
python -m venv venv
```

---

## 2. 가상환경 실행(필요하다면)

```powershell
.\venv\Scripts\activate
```

---

## 3. 의존성 설치

```powershell
python -m pip install -r requirements.txt
```

---

## 4. 환경변수 설정

`.env` 파일을 생성합니다.

```env
디스코드 백스레드 참고
```

`.env` 파일은 GitHub에 업로드하면 안 됩니다.

---

# 서버 실행

```powershell
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

# Swagger API 문서

```text
http://localhost:8000/docs
```

---

# API 목록

## 서버 실행 확인

```text
GET /
```

---

## 서버 상태 확인

```text
GET /health
```

---

## DB 연결 확인

```text
GET /db-test
```

성공 응답:

```json
{
  "database": "connected"
}
```

---

## AI 코칭 테스트

```text
POST /ai/test
```

요청 JSON:

```json
{
  "activity_id": 3,
  "user_id": 1,
  "pace": 330,
  "heart_rate": 178,
  "cadence": 155,
  "pronation_type": "overpronation",
  "heel_strike_rate": 82
}
```

응답 JSON:

```json
{
  "issues": [
    "심박수 높음",
    "과회내 경향",
    "뒤꿈치 착지 비율 높음"
  ],
  "feedback_test": "숨을 깊게 쉬며 페이스를 조금 낮춰보세요.",
  "focus_point": "호흡 안정과 페이스 조절",
  "rec_exercise": "가벼운 조깅과 호흡 조절 훈련"
}
```

---

## AI 코칭 저장

```text
POST /ai/coaching
```

---

## AI 코칭 전체 조회

```text
GET /ai/coaching
```

---

## AI 코칭 단건 조회

```text
GET /ai/coaching/{coaching_id}
```

---

## AI 코칭 수정

```text
PATCH /ai/coaching/{coaching_id}
```

---

## AI 코칭 삭제

```text
DELETE /ai/coaching/{coaching_id}
```

---

# 전체 흐름

```text
앱 / Spring Boot
↓
running_activity 생성
↓
foot_sensor_data 저장
↓
FastAPI(main.py)
↓
러닝 데이터 분석(analysis_service.py)
↓
프롬프트 생성(prompt_service.py)
↓
Gemini 호출(llm_service.py)
↓
ai_coaching 저장(crud.py)
↓
응답 반환
```

---

# GitHub 업로드 주의

`.env`는 절대 업로드하지 않습니다.

`.gitignore`에 아래 항목이 포함되어 있어야 합니다.

```gitignore
.env
venv/
__pycache__/
*.pyc
```
