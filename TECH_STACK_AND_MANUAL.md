# 기술 스택 문서

## 프론트엔드
- **프레임워크:** Streamlit (Python 기반 웹앱)
- **UI/UX:** Streamlit 기본 컴포넌트 + 커스텀 CSS
- **데이터 시각화:** Plotly, pandas
- **이미지 처리:** Pillow, OpenCV (cv2)
- **얼굴 인식:** mediapipe (Google 오픈소스)
- **자동 새로고침:** streamlit_autorefresh
- **HTTP 통신:** requests

## 백엔드(API 서버)
- **프레임워크:** FastAPI (Python)
- **DB:** SQLite (SQLAlchemy ORM)
- **API 통신:** RESTful (POST/GET)

## 기타
- **환경 변수 관리:** python-dotenv
- **버전 관리:** git, GitHub
- **배포 환경:** 로컬 PC(권장), AWS EC2 또는 Google Cloud VM(권장), Docker(자동화), Streamlit Cloud(일부 기능 제한)

---

# 시스템 아키텍처 문서

```
[사용자 브라우저]
        │
        ▼
[Streamlit 프론트엔드 (app.py)]
        │
        │  (HTTP 요청, REST API)
        ▼
[백엔드 API 서버 (FastAPI)]
        │
        └─ [SQLite DB]
```

- **Streamlit 프론트엔드**:  
  - 그룹 생성, 타이머, 인증 업로드, 실시간 피드, 통계, 지켜보기 모드(얼굴 인식)
  - 얼굴 인식(지켜보기 모드)은 opencv-python/mediapipe 설치 환경에서만 동작

- **백엔드 API 서버**:  
  - 그룹 관리, 타이머 기록, 이미지 업로드, 피드, 통계, 자리비움 상태 기록
  - SQLite DB에 모든 기록 저장

---

# 설치 및 실행 매뉴얼

## 1) Python 환경 준비
- Python 3.7 ~ 3.11 설치 (mediapipe 지원 버전)
- (권장) 가상환경(venv) 사용

## 2) 프로젝트 클론 및 진입
```bash
git clone <본인 깃허브 저장소 주소>
cd <프로젝트 폴더>
```

## 3) 가상환경 생성 및 활성화
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

## 4) 패키지 설치
```bash
pip install --upgrade pip
pip install -r frontend/requirements.txt
```

## 5) Streamlit 앱 실행
```bash
streamlit run frontend/app.py
```
- 브라우저에서 http://localhost:8501 접속

## 6) (선택) 백엔드 API 서버 실행
```bash
# 예시: FastAPI 서버
uvicorn backend.main:app --reload --host 0.0.0.0 --port 10000
```

## 7) (추천) AWS EC2 또는 Google Cloud VM 배포
- AWS EC2(무료 티어 또는 유료) 또는 Google Cloud VM에서 Ubuntu 인스턴스 생성
- SSH로 접속 후 Python 3.11, pip, venv 설치
- 프로젝트 코드 업로드 후 (예: git clone) opencv-python, mediapipe 등 모든 패키지 설치
- streamlit run으로 서비스 실행 (예: streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0)
- 보안그룹(또는 방화벽)에서 8501 포트 오픈
- (선택) 도메인 연결, HTTPS 적용

## 8) (선택) Docker로 완전 자동화
- Dockerfile 작성 (필요 패키지 모두 설치)
- DockerHub에 이미지 푸시
- AWS ECS, Google Cloud Run, Railway 등에서 배포

---

# 기타 참고

- **지켜보기 모드(얼굴 인식)**는 opencv-python/mediapipe가 설치된 환경에서만 동작합니다.
- 클라우드(AWS EC2, Google Cloud VM 등)에서는 보안그룹/방화벽에서 8501 포트 오픈 필요
- Streamlit Cloud에서는 얼굴 인식 기능 사용 불가(패키지 설치 제한) 