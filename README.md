# 🥕 당근 스터디 모임

## 서비스 개요
- 동네 기반 스터디 인증, 피드백, 통계, 게이미피케이션 제공

## 기술 스택
- 프론트엔드: Streamlit
- 백엔드: FastAPI
- 데이터베이스: SQLite + SQLAlchemy

## 폴더 구조
```
backend/   # FastAPI 서버 및 DB
frontend/  # Streamlit 대시보드
```

## 실행 방법

### 백엔드(FastAPI)
```
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 프론트엔드(Streamlit)
```
cd frontend
pip install -r requirements.txt
streamlit run app.py
``` 