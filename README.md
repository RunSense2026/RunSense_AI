# RunSense_AI
동양미래대 2026 졸업작품 런센스 AI

# RunSense AI Server - Minimal Starter

RunSense AI 서버의 최소 초기 세팅 버전입니다.

이 버전은 아래 3가지만 확인하는 목적입니다.

```text
FastAPI 서버 실행
Supabase PostgreSQL DB 연결
Gemini API 연동
```

## 스택

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- PostgreSQL / Supabase
- Gemini API
- Pydantic

## 폴더 구조

```text
runsense_ai_server_minimal/
├── main.py
├── db.py
├── llm_service.py
├── run_schema.py
├── requirements.txt
├── .env.example
└── .gitignore
```

## 시작하기

### 1. 가상환경 생성(필요하다면)

```powershell
python -m venv venv
```

### 2. 가상환경 실행(필요하다면)

```powershell
.\venv\Scripts\activate
```

### 3. 의존성 설치

```powershell
python -m pip install -r requirements.txt
```

### 4. 환경변수 설정

`.env.example` 파일을 복사해서 `.env` 파일을 만듭니다.

```env
디스코드 백스레드 참고
```

`.env` 파일은 GitHub에 올리면 안 됩니다.

## 서버 실행

```powershell
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Swagger API 문서

```text
http://localhost:8000/docs
```

## 테스트 API

### 서버 실행 확인

```text
GET /
```

### 서버 상태 확인

```text
GET /health
```

### DB 연결 확인

```text
GET /db-test
```

성공 응답:

```json
{
  "database": "connected"
}
```

### Gemini API 연결 확인

```text
POST /ai-test
```

요청 JSON:

```json
{
  "pace": 330,
  "heart_rate": 175,
  "cadence": 160
}
```

응답 JSON:

```json
{
  "message": "심박이 높습니다. 호흡을 안정시키며 페이스를 조금 낮춰보세요."
}
```

## 현재 버전에서 구현하지 않은 것

```text
러닝 분석 로직
CRUD 전체 구현
TTS 음성 생성
DB 테이블 모델
Spring Boot 연동
React Native 연동
```

## GitHub 업로드 주의

`.env`는 절대 업로드하지 않습니다.
