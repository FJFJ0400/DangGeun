# 🥕 당근 스터디 모임

## 서비스 개요
- 동네 기반 스터디 인증, 피드백, 통계, 게이미피케이션 제공
- 사용자들이 스터디 목표를 설정하고 달성하는 과정을 관리하고 공유할 수 있는 플랫폼
- 지역 기반으로 비슷한 목표를 가진 스터디원들을 매칭

## 주요 기능
- 스터디 그룹 생성 및 관리
- 스터디 인증 및 피드백
- 스터디 통계 및 분석
- 게이미피케이션 요소 (뱃지, 포인트, 레벨 등)
- 지역 기반 스터디원 매칭

## 기술 스택
- 프론트엔드: Streamlit
  - 대시보드 및 데이터 시각화
  - 사용자 인터페이스
- 백엔드: FastAPI
  - RESTful API 서버
  - 비즈니스 로직 처리
- 데이터베이스: SQLite + SQLAlchemy
  - 데이터 영속성
  - ORM을 통한 데이터 관리

## 폴더 구조
```
backend/   # FastAPI 서버 및 DB
  ├── main.py          # FastAPI 애플리케이션 진입점
  ├── models.py        # 데이터베이스 모델
  ├── schemas.py       # Pydantic 스키마
  ├── database.py      # 데이터베이스 설정
  └── requirements.txt # 백엔드 의존성

frontend/  # Streamlit 대시보드
  ├── app.py           # Streamlit 애플리케이션
  ├── pages/           # 추가 페이지들
  ├── components/      # 재사용 가능한 컴포넌트
  └── requirements.txt # 프론트엔드 의존성
```

## 실행 방법

### 백엔드(FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
- 서버는 기본적으로 http://localhost:8000 에서 실행됩니다
- API 문서는 http://localhost:8000/docs 에서 확인할 수 있습니다

### 프론트엔드(Streamlit)
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```
- 대시보드는 기본적으로 http://localhost:8501 에서 실행됩니다

## 개발 환경 설정
1. Python 3.8 이상 설치
2. 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
3. 필요한 패키지 설치
```bash
# 백엔드
cd backend
pip install -r requirements.txt

# 프론트엔드
cd frontend
pip install -r requirements.txt
```

## 기여 방법
1. 이슈 생성 또는 기존 이슈 확인
2. 새로운 브랜치 생성
3. 변경사항 커밋
4. Pull Request 생성

## 라이선스
MIT License 