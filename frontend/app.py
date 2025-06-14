# =============================
# [배포 변경 전] - 현재 코드는 로컬/개인 환경에서 모든 기능(지켜보기 모드 포함) 정상 동작 기준입니다.
# 클라우드 배포(Oracle, GCP 등) 전 상태를 명확히 기록합니다.
# =============================
import streamlit as st
import requests
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
from PIL import Image, ImageOps
import io
from streamlit_autorefresh import st_autorefresh
import time

# 안전한 import (설치 안 된 환경 대응)
try:
    import cv2
    import mediapipe as mp
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# API 엔드포인트 설정 (환경변수 우선)
API_URL = os.environ.get("API_URL", "http://localhost:10000")

def get_my_ip():
    try:
        return requests.get('https://api.ipify.org').text
    except:
        return "local"

st.set_page_config(page_title="당근 스터디 모임", layout="wide")

st.markdown("""
    <style>
    /* 반응형 폰트/여백/버튼 */
    html, body, [data-testid="stAppViewContainer"] {
        font-size: 18px;
    }
    @media (max-width: 600px) {
        html, body, [data-testid="stAppViewContainer"] {
            font-size: 15px !important;
        }
        .mobile-hide { display: none !important; }
        .mobile-full { width: 100% !important; }
        .stButton>button, .stTextInput>div>input, .stTextArea>div>textarea {
            font-size: 1em !important;
            width: 100% !important;
        }
        .stFileUploader { width: 100% !important; }
    }
    @media (min-width: 601px) {
        .desktop-hide { display: none !important; }
    }
    /* 입력 박스 중앙 정렬 */
    div[data-testid="stTextInput"] {
        margin: 0 auto;
    }
    </style>
""", unsafe_allow_html=True)

# 최초 진입 시 그룹명 입력/입장 화면 강제
if "group_id" not in st.session_state or "group_name" not in st.session_state:
    st.markdown("<h1 style='text-align:center;'>🥕 당근 스터디 시작하기</h1>", unsafe_allow_html=True)
    st.write("<div style='text-align:center;'>스터디명(그룹명)을 입력하세요.</div>", unsafe_allow_html=True)
    # 입력 박스 중앙 정렬 및 placeholder 적용
    st.markdown("""
        <style>
        div[data-testid="stTextInput"] > div > input {
            text-align: left;
            font-size: 1.1em;
            color: #222;
        }
        div[data-testid="stTextInput"] > div > input::placeholder {
            color: #888;
            opacity: 0.5;
        }
        div[data-testid="stTextInput"] {
            width: 60vw;
            margin: 0 auto;
        }
        </style>
    """, unsafe_allow_html=True)
    group_name = st.text_input(
        label=" ",
        value="",
        key="group_name_input",
        placeholder="예시) 스타벅스 6월 9일 오후 1시 <4명>"
    )
    if st.button("START"):
        if group_name.strip():
            resp = requests.post(f"{API_URL}/group/create", params={"name": group_name.strip()})
            if resp.status_code == 200:
                group_id = resp.json()["group_id"]
                st.session_state["group_id"] = group_id
                st.session_state["group_name"] = group_name.strip()
                st.session_state["choice"] = "뽀모도로 타이머"
                st.rerun()
            else:
                st.error("그룹 생성/입장 실패: " + resp.text)
    st.stop()

# 그룹명 상단에 표시
st.markdown(f"<h2 style='text-align:center;'>🥕 {st.session_state.get('group_name', '')} 스터디</h2>", unsafe_allow_html=True)

# 세션에 choice가 없으면 기본값 지정
if "choice" not in st.session_state:
    st.session_state["choice"] = "뽀모도로 타이머"

# 사이드바 안내 메시지
with st.sidebar:
    st.markdown("### 🥕 당근 스터디")
    st.info("함께 하면 더 오래, 멀리 갈 수 있어요. just do it, together")
    menu = ["뽀모도로 타이머", "지켜보기 모드", "인증 업로드", "실시간 피드", "통계"]
    choice = st.radio("메뉴", menu, key="choice")

my_ip = get_my_ip()
group_id = st.session_state["group_id"]

hobang_url = "https://i.imgur.com/0XKzn8F.png"

st.markdown(f"""
    <style>
    [data-testid="collapsedControl"] {{
        background-image: url('{hobang_url}');
        background-size: cover;
        background-position: center;
        color: transparent !important;
        border-radius: 50%;
        width: 36px !important;
        height: 36px !important;
    }}
    [data-testid="collapsedControl"] svg {{
        display: none !important;
    }}
    </style>
""", unsafe_allow_html=True)

if choice == "뽀모도로 타이머":
    st.header("⏰ 뽀모도로 타이머")
    st.write("공부 시간을 설정하고 타이머를 시작하세요. 타이머 기록은 하단에 저장됩니다.")
    col1, col2, col3 = st.columns(3)
    with col1:
        hours = st.number_input("시간", min_value=0, max_value=23, value=0, step=1)
    with col2:
        minutes = st.number_input("분", min_value=0, max_value=59, value=50, step=1)  # 기본값 50분
    with col3:
        seconds = st.number_input("초", min_value=0, max_value=59, value=0, step=1)
    set_seconds = int(hours * 3600 + minutes * 60 + seconds)

    # 1초마다 새로고침
    st_autorefresh(interval=1000, key="timer_refresh")

    # 세션 상태 초기화
    if 'timer_running' not in st.session_state:
        st.session_state.timer_running = False
    if 'timer_end' not in st.session_state:
        st.session_state.timer_end = None
    if 'timer_set_seconds' not in st.session_state:
        st.session_state.timer_set_seconds = set_seconds
    if 'timer_paused' not in st.session_state:
        st.session_state.timer_paused = False
    if 'timer_pause_left' not in st.session_state:
        st.session_state.timer_pause_left = None
    if 'timer_force_zero' not in st.session_state:
        st.session_state.timer_force_zero = False

    # 버튼 UI
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns([1,1,1,1])
    with col_btn1:
        start_btn = st.button("시작")
    with col_btn2:
        reset_btn = st.button("재설정")
    with col_btn3:
        stop_btn = st.button("중간끝내기")
    with col_btn4:
        pause_btn = st.button("= 일시 정지" if not st.session_state.timer_paused else "▶ 재시작")

    # 버튼 동작
    if start_btn:
        st.session_state.timer_running = True
        st.session_state.timer_set_seconds = set_seconds
        st.session_state.timer_end = (datetime.now() + timedelta(seconds=set_seconds)).isoformat()
        st.session_state.timer_paused = False
        st.session_state.timer_pause_left = None
        st.session_state.timer_force_zero = False
    if reset_btn:
        st.session_state.timer_running = False
        st.session_state.timer_end = None
        st.session_state.timer_set_seconds = set_seconds
        st.session_state.timer_paused = False
        st.session_state.timer_pause_left = None
        st.session_state.timer_force_zero = False
    if stop_btn and (st.session_state.timer_running or st.session_state.timer_paused):
        # 중간끝내기: 즉시 기록 저장
        st.session_state.timer_running = False
        st.session_state.timer_paused = False
        now = datetime.now()
        end_time = now
        # 일시정지 상태라면 남은 시간에서 start_time 계산
        if st.session_state.timer_paused and st.session_state.timer_pause_left is not None:
            start_time = end_time - timedelta(seconds=st.session_state.timer_pause_left)
        elif st.session_state.timer_end:
            start_time = end_time - timedelta(seconds=st.session_state.timer_set_seconds)
        else:
            start_time = end_time
        st.success("타이머가 중간에 종료되었습니다. 기록이 저장됩니다.")
        try:
            resp = requests.post(f"{API_URL}/timerlog/upload", data={
                "group_id": group_id,
                "set_seconds": st.session_state.timer_set_seconds,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            })
            if resp.status_code == 200:
                st.success("타이머 기록이 저장되었습니다.")
            else:
                st.error(f"기록 저장 실패: {resp.text}")
        except Exception as e:
            st.error(f"기록 저장 실패: {e}")
        st.session_state.timer_end = None
        st.session_state.timer_pause_left = None
        st.session_state.timer_force_zero = True
    if pause_btn and (st.session_state.timer_running or st.session_state.timer_paused):
        if not st.session_state.timer_paused and st.session_state.timer_running:
            # 일시정지
            end_time = datetime.fromisoformat(st.session_state.timer_end)
            left = int((end_time - datetime.now()).total_seconds())
            st.session_state.timer_paused = True
            st.session_state.timer_pause_left = left
            st.session_state.timer_running = False
            st.session_state.timer_end = None
        elif st.session_state.timer_paused:
            # 재시작
            left = st.session_state.timer_pause_left
            st.session_state.timer_end = (datetime.now() + timedelta(seconds=left)).isoformat()
            st.session_state.timer_running = True
            st.session_state.timer_paused = False
            st.session_state.timer_pause_left = None
            st.session_state.timer_force_zero = False

    # 남은 시간 계산 및 표시
    if st.session_state.timer_force_zero:
        h, m, s = 0, 0, 0
        st.markdown(f"## ⏳ 남은 시간: {int(h):02d}:{int(m):02d}:{int(s):02d}")
    elif st.session_state.timer_running and st.session_state.timer_end:
        end_time = datetime.fromisoformat(st.session_state.timer_end)
        left = int((end_time - datetime.now()).total_seconds())
        if left <= 0:
            st.session_state.timer_running = False
            st.session_state.timer_end = None
            st.session_state.timer_paused = False
            st.session_state.timer_pause_left = None
            st.success("타이머 종료! 기록이 저장됩니다.")
            try:
                resp = requests.post(f"{API_URL}/timerlog/upload", data={
                    "group_id": group_id,
                    "set_seconds": st.session_state.timer_set_seconds,
                    "start_time": (end_time - timedelta(seconds=st.session_state.timer_set_seconds)).isoformat(),
                    "end_time": end_time.isoformat()
                })
                if resp.status_code == 200:
                    st.success("타이머 기록이 저장되었습니다.")
                else:
                    st.error(f"기록 저장 실패: {resp.text}")
            except Exception as e:
                st.error(f"기록 저장 실패: {e}")
            left = 0
        h, m = divmod(left, 3600)
        m, s = divmod(m, 60)
        st.markdown(f"## ⏳ 남은 시간: {int(h):02d}:{int(m):02d}:{int(s):02d}")
        st.session_state.timer_force_zero = False
    elif st.session_state.timer_paused and st.session_state.timer_pause_left is not None:
        left = st.session_state.timer_pause_left
        h, m = divmod(left, 3600)
        m, s = divmod(m, 60)
        st.markdown(f"## ⏳ 남은 시간: {int(h):02d}:{int(m):02d}:{int(s):02d} (일시정지)")
    else:
        h, m = divmod(set_seconds, 3600)
        m, s = divmod(m, 60)
        st.markdown(f"## ⏳ 남은 시간: {int(h):02d}:{int(m):02d}:{int(s):02d}")

    st.markdown("---")
    st.subheader("나의 타이머 기록")
    try:
        logs = requests.get(f"{API_URL}/timerlog/feed", params={"group_id": group_id}).json()
        if isinstance(logs, dict) and "detail" in logs:
            st.error(f"기록 불러오기 실패: {logs['detail']}")
        elif logs:
            for log in logs:
                st.write(f"- {log['start_time']} ~ {log['end_time']} | 설정: {log['set_seconds']//60}분 {log['set_seconds']%60}초")
        else:
            st.info("타이머 기록이 없습니다.")
    except Exception as e:
        st.error(f"기록 불러오기 실패: {e}")

elif choice == "지켜보기 모드":
    if not CV2_AVAILABLE:
        st.error("이 환경에서는 '지켜보기 모드'를 사용할 수 없습니다. (opencv-python/mediapipe 미설치)")
    else:
        st.header("🧑‍💻 자리 비움 감지 (얼굴 인식)")

        def init_away_state():
            if "away_status" not in st.session_state:
                st.session_state["away_status"] = "active"
            if "last_face_time" not in st.session_state:
                st.session_state["last_face_time"] = time.time()
            if "face_detected" not in st.session_state:
                st.session_state["face_detected"] = False
            if "watch_mode" not in st.session_state:
                st.session_state["watch_mode"] = False
            if "countdown" not in st.session_state:
                st.session_state["countdown"] = 0
        init_away_state()

        FRAME_WINDOW = st.image([])
        col1, col2 = st.columns([1,1])
        with col1:
            if not st.session_state["watch_mode"]:
                if st.button('지켜보기 모드 시작', key="start_watch"):
                    st.session_state["countdown"] = 3
                    st.session_state["watch_mode"] = True
            else:
                if st.button('정지하기', key="stop_watch"):
                    st.session_state["watch_mode"] = False
                    st.session_state["away_status"] = "active"
                    st.session_state["face_detected"] = False
                    st.session_state["countdown"] = 0
                    FRAME_WINDOW.empty()
        with col2:
            if st.session_state["watch_mode"]:
                if st.session_state["away_status"] == "active":
                    st.markdown('<span style="font-size:48px; color:green;">●</span> <span style="font-size:20px;">활동 중</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span style="font-size:48px; color:red;">●</span> <span style="font-size:20px;">자리 비움</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span style="font-size:20px; color:gray;">대기 중</span>', unsafe_allow_html=True)

        mp_face_detection = mp.solutions.face_detection
        mp_drawing = mp.solutions.drawing_utils

        if st.session_state["watch_mode"]:
            # 카운트다운
            if st.session_state["countdown"] > 0:
                for i in range(st.session_state["countdown"], 0, -1):
                    FRAME_WINDOW.empty()
                    FRAME_WINDOW.markdown(f'<h1 style="text-align:center; font-size:72px;">{i}</h1>', unsafe_allow_html=True)
                    time.sleep(1)
                st.session_state["countdown"] = 0
                FRAME_WINDOW.empty()
            # 감지 시작
            cap = cv2.VideoCapture(0)
            with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
                while st.session_state["watch_mode"] and cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        st.warning("웹캠을 찾을 수 없습니다.")
                        break
                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = face_detection.process(image)
                    face_found = results.detections is not None and len(results.detections) > 0
                    if face_found:
                        for detection in results.detections:
                            mp_drawing.draw_detection(image, detection)
                    FRAME_WINDOW.image(image, channels='RGB')
                    now = time.time()
                    if face_found:
                        st.session_state["last_face_time"] = now
                        st.session_state["face_detected"] = True
                        if st.session_state["away_status"] != "active":
                            st.session_state["away_status"] = "active"
                    else:
                        st.session_state["face_detected"] = False
                        if now - st.session_state["last_face_time"] > 10:
                            if st.session_state["away_status"] != "away":
                                st.session_state["away_status"] = "away"
                                try:
                                    requests.post(f"{API_URL}/status", data={"group_id": st.session_state.get("group_id", ""), "user_id": get_my_ip(), "status": "away"})
                                except Exception as e:
                                    st.warning(f"상태 전송 실패: {e}")
                    time.sleep(0.1)
                    if not st.session_state["watch_mode"]:
                        break
            cap.release()
            FRAME_WINDOW.empty()

elif choice == "인증 업로드":
    st.header("📸 공부 인증 업로드")
    st.write("공부한 내용을 간단히 남겨주세요.")
    uploaded_file = st.file_uploader("이미지 업로드", type=["jpg", "jpeg", "png", "gif", "bmp", "webp"])
    comment = st.text_area("공부 내용 입력")
    if st.button("업로드") and uploaded_file:
        try:
            response = requests.post(
                f"{API_URL}/upload",
                files={"image": (uploaded_file.name, uploaded_file, uploaded_file.type)},
                data={"comment": comment, "group_id": group_id}
            )
            if response.status_code == 200:
                st.success("업로드 성공!")
            else:
                st.error("업로드 실패: " + response.text)
        except Exception as e:
            st.error(f"서버 연결 실패: {e}")

elif choice == "실시간 피드":
    st.header("📰 실시간 피드")
    try:
        feed = requests.get(f"{API_URL}/feed", params={"group_id": group_id}).json()
        for post in feed:
            image_url = post["image_url"]
            if image_url.startswith("/"):
                image_url = API_URL + image_url
            # 이미지 원본을 직접 불러와서 4:3(400x300) 비율로 맞춤
            try:
                img_response = requests.get(image_url)
                img = Image.open(io.BytesIO(img_response.content)).convert("RGB")
                target_size = (400, 300)
                img = ImageOps.pad(img, target_size, color=(255,255,255), centering=(0.5,0.5))
                st.image(img, width=400)
            except Exception as e:
                st.warning("이미지 로드 실패")
            st.markdown(f"<div style='font-size:1.1em; margin-top:8px; margin-bottom:4px;'><b>{post['comment']}</b></div>", unsafe_allow_html=True)
            st.caption(f"IP: {post['user_id']} | {post['created_at']}")
            st.markdown("---")
    except Exception as e:
        st.error(f"피드 불러오기 실패: {e}")

elif choice == "통계":
    st.header("📊 나의 통계")
    st.info("통계는 이미지 인증 업로드(인증 업로드 메뉴)만 집계됩니다. 타이머 기록은 통계에 포함되지 않습니다.")
    try:
        stats = requests.get(f"{API_URL}/stats/{my_ip}", params={"group_id": group_id}).json()
        st.metric("총 인증 수", stats["total_logs"])
        st.metric("연속 인증 일수", stats["streak_days"])
        st.metric("오늘 인증 여부", "O" if stats["today_logged"] else "X")
    except Exception as e:
        st.error(f"통계 불러오기 실패: {e}")

elif choice == "게이미피케이션":
    st.header("🏆 게이미피케이션")
    
    if st.session_state.user_id is None:
        st.warning("로그인이 필요한 서비스입니다.")
    else:
        stats = get_user_stats()
        if stats and "gamification" in stats:
            # 레벨 및 포인트
            col1, col2 = st.columns(2)
            with col1:
                st.metric("현재 레벨", f"Lv.{stats['gamification']['level']}")
            with col2:
                st.metric("보유 포인트", f"{stats['gamification']['points']}P")
            
            # 뱃지
            st.subheader("획득한 뱃지")
            badges = stats["gamification"]["badges"]
            cols = st.columns(4)
            for i, badge in enumerate(badges):
                with cols[i % 4]:
                    st.image(badge["icon"], width=100)
                    st.write(badge["name"])
                    st.caption(badge["description"])
            
            # 도전과제
            st.subheader("도전과제")
            achievements = stats["gamification"]["achievements"]
            for achievement in achievements:
                progress = achievement["current"] / achievement["target"] * 100
                st.progress(progress / 100)
                st.write(f"{achievement['name']} ({achievement['current']}/{achievement['target']})")
                st.caption(achievement["description"]) 