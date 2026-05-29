# RunSense_AI

동양미래대 2026 졸업작품 런센스 AI

# RunSense AI Server

RunSense 프로젝트의 AI 코칭 서버입니다.

# 스택

* Python
* FastAPI
* Uvicorn
* SQLAlchemy
* PostgreSQL / Supabase
* Gemini API
* gTTS
* Pydantic


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
  "feedback_text": "숨을 깊게 쉬며 페이스를 조금 낮춰보세요.",
  "focus_point": "호흡 안정과 페이스 조절",
  "rec_exercise": "가벼운 조깅과 호흡 조절 훈련",
  "voice_file": "/audio/coach_xxxx.mp3"
}
```

---

## TTS 테스트

```text
POST /tts/test
```

응답 예시

```json
{
  "text": "호흡을 안정시켜보세요",
  "voice_file": "/audio/coach_xxxx.mp3"
}
```

---

## AI 코칭 저장

```text
POST /ai/coaching
```

AI 코칭 텍스트는 DB에 저장되며,

```text
feedback_text
focus_point
rec_exercise
```

음성 파일 경로는 응답에만 포함됩니다.

---

## AI 코칭 전체 조회

```text
GET /ai/coaching
```

특정 러닝 활동 조회

```text
GET /ai/coaching?activity_id=3
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


# Git 컨벤션

## 브랜치 규칙

```text
feat/기능명
fix/버그명
refactor/기능명
docs/readme
```

예시

```text
feat/ai-coaching
feat/tts
fix/gemini-error
```

---

## 커밋 규칙

| 타입       | 설명    |
| -------- | ----- |
| feat     | 기능 추가 |
| fix      | 버그 수정 |
| refactor | 리팩토링  |
| docs     | 문서 수정 |
| chore    | 기타 작업 |

예시

```text
feat: AI 코칭 API 구현
feat: Gemini API 연동
feat: TTS 테스트 API 구현
fix: Foreign Key 오류 수정
docs: README 업데이트
```

---

## PR 규칙

* develop 브랜치로 PR 생성
* 최소 1명 이상 리뷰
* Squash Merge 사용

---

# GitHub 업로드 주의

`.env`는 절대 업로드하지 않습니다.

`.gitignore`에 아래 항목이 포함되어 있어야 합니다.

```gitignore
.env
venv/
__pycache__/
*.pyc
audio/*.mp3
```
