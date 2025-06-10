import streamlit as st
import requests
import os
from datetime import datetime, timedelta
import time
import pandas as pd
import plotly.express as px
from PIL import Image
import io

# API 엔드포인트 설정 (환경변수 우선)
API_URL = os.environ.get("API_URL", "http://localhost:10000")

# 페이지 설정
st.set_page_config(
    page_title="당근 스터디 모임",
    page_icon="🥕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'timer_running' not in st.session_state:
    st.session_state.timer_running = False
if 'timer_start' not in st.session_state:
    st.session_state.timer_start = None
if 'timer_duration' not in st.session_state:
    st.session_state.timer_duration = 50  # 기본 50분

# 유틸리티 함수들
def login_user(username, password):
    try:
        response = requests.post(f"{API_URL}/auth/login", json={"username": username, "password": password})
        if response.status_code == 200:
            st.session_state.user_id = response.json()["user_id"]
            return True
        return False
    except requests.exceptions.RequestException:
        st.error("서버 연결에 실패했습니다.")
        return False

def register_user(username, password, email):
    try:
        response = requests.post(f"{API_URL}/auth/register", 
                               json={"username": username, "password": password, "email": email})
        return response.status_code == 200
    except requests.exceptions.RequestException:
        st.error("서버 연결에 실패했습니다.")
        return False

def upload_study_proof(image, comment):
    if st.session_state.user_id is None:
        st.error("로그인이 필요합니다.")
        return False
    
    try:
        files = {"image": ("image.jpg", image, "image/jpeg")}
        data = {"user_id": st.session_state.user_id, "comment": comment}
        response = requests.post(f"{API_URL}/study/upload", files=files, data=data)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        st.error("서버 연결에 실패했습니다.")
        return False

def get_study_feed():
    try:
        response = requests.get(f"{API_URL}/study/feed")
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException:
        st.error("서버 연결에 실패했습니다.")
        return []

def get_user_stats():
    if st.session_state.user_id is None:
        return None
    
    try:
        response = requests.get(f"{API_URL}/stats/user/{st.session_state.user_id}")
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        st.error("서버 연결에 실패했습니다.")
        return None

def get_my_ip():
    try:
        return requests.get('https://api.ipify.org').text
    except:
        return "local"

# 사이드바 - 로그인/회원가입
with st.sidebar:
    st.title("🥕 당근 스터디")
    
    if st.session_state.user_id is None:
        tab1, tab2 = st.tabs(["로그인", "회원가입"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("아이디")
                password = st.text_input("비밀번호", type="password")
                submit = st.form_submit_button("로그인")
                
                if submit:
                    if login_user(username, password):
                        st.success("로그인 성공!")
                        st.rerun()
                    else:
                        st.error("로그인 실패. 아이디와 비밀번호를 확인해주세요.")
        
        with tab2:
            with st.form("register_form"):
                new_username = st.text_input("새 아이디")
                new_password = st.text_input("새 비밀번호", type="password")
                confirm_password = st.text_input("비밀번호 확인", type="password")
                email = st.text_input("이메일")
                submit = st.form_submit_button("회원가입")
                
                if submit:
                    if new_password != confirm_password:
                        st.error("비밀번호가 일치하지 않습니다.")
                    elif register_user(new_username, new_password, email):
                        st.success("회원가입 성공! 로그인해주세요.")
                    else:
                        st.error("회원가입 실패. 다시 시도해주세요.")
    else:
        st.success(f"환영합니다! (ID: {st.session_state.user_id})")
        if st.button("로그아웃"):
            st.session_state.user_id = None
            st.rerun()
    
    st.markdown("---")
    
    # 메인 메뉴
    menu = ["뽀모도로 타이머", "인증 업로드", "실시간 피드", "통계"]
    choice = st.selectbox("메뉴", menu)

# 메인 컨텐츠
if choice == "뽀모도로 타이머":
    st.header("⏰ 뽀모도로 타이머")
    st.write("공부 시간을 설정하고 타이머를 시작하세요. 타이머 기록은 하단에 저장됩니다.")
    
    # 타이머 설정 UI
    col1, col2, col3 = st.columns(3)
    with col1:
        hours = st.number_input("시간", min_value=0, max_value=23, value=0, step=1)
    with col2:
        minutes = st.number_input("분", min_value=0, max_value=59, value=25, step=1)
    with col3:
        seconds = st.number_input("초", min_value=0, max_value=59, value=0, step=1)
    set_seconds = int(hours * 3600 + minutes * 60 + seconds)
    
    if 'timer_running' not in st.session_state:
        st.session_state.timer_running = False
    if 'timer_start' not in st.session_state:
        st.session_state.timer_start = None
    if 'timer_left' not in st.session_state:
        st.session_state.timer_left = set_seconds
    
    def reset_timer():
        st.session_state.timer_running = False
        st.session_state.timer_start = None
        st.session_state.timer_left = set_seconds
    
    if st.button("START"):
        st.session_state.timer_running = True
        st.session_state.timer_start = datetime.now()
        st.session_state.timer_left = set_seconds
    if st.button("RESET"):
        reset_timer()
    
    # 타이머 동작
    if st.session_state.timer_running and st.session_state.timer_left > 0:
        elapsed = (datetime.now() - st.session_state.timer_start).total_seconds()
        left = max(0, st.session_state.timer_left - int(elapsed))
        m, s = divmod(left, 60)
        h, m = divmod(m, 60)
        st.markdown(f"## ⏳ 남은 시간: {int(h):02d}:{int(m):02d}:{int(s):02d}")
        if left == 0:
            st.session_state.timer_running = False
            st.success("타이머 종료! 기록이 저장됩니다.")
            # 기록 업로드
            try:
                requests.post(f"{API_URL}/timerlog/upload", data={
                    "set_seconds": set_seconds,
                    "start_time": st.session_state.timer_start.isoformat(),
                    "end_time": datetime.now().isoformat()
                })
            except Exception as e:
                st.error(f"기록 저장 실패: {e}")
    elif not st.session_state.timer_running:
        st.markdown(f"## ⏳ 남은 시간: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
    
    st.markdown("---")
    st.subheader("나의 타이머 기록")
    # 타이머 기록 불러오기
    try:
        logs = requests.get(f"{API_URL}/timerlog/feed").json()
        if logs:
            for log in logs:
                st.write(f"- {log['start_time']} ~ {log['end_time']} | 설정: {log['set_seconds']//60}분 {log['set_seconds']%60}초")
        else:
            st.info("타이머 기록이 없습니다.")
    except Exception as e:
        st.error(f"기록 불러오기 실패: {e}")

elif choice == "인증 업로드":
    st.header("📸 인증 업로드")
    st.write("공부 인증 이미지를 업로드하고 코멘트를 남겨보세요.")
    uploaded_file = st.file_uploader("이미지 업로드", type=["jpg", "jpeg", "png"])
    comment = st.text_area("코멘트 입력")
    if st.button("업로드") and uploaded_file:
        files = {"image": uploaded_file.getvalue()}
        data = {"comment": comment}
        try:
            response = requests.post(f"{API_URL}/upload", files={"image": (uploaded_file.name, uploaded_file, uploaded_file.type)}, data={"comment": comment})
            if response.status_code == 200:
                st.success("업로드 성공!")
            else:
                st.error("업로드 실패: " + response.text)
        except Exception as e:
            st.error(f"서버 연결 실패: {e}")

elif choice == "실시간 피드":
    st.header("📰 실시간 피드")
    try:
        feed = requests.get(f"{API_URL}/feed").json()
        for post in feed:
            st.image(post["image_url"], width=200)
            st.write(post["comment"])
            st.caption(f"IP: {post['user_id']} | {post['created_at']}")
            st.markdown("---")
    except Exception as e:
        st.error(f"피드 불러오기 실패: {e}")

elif choice == "통계":
    st.header("📊 나의 통계")
    try:
        stats = requests.get(f"{API_URL}/stats/{get_my_ip()}").json()
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