import streamlit as st
import requests
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
from PIL import Image
import io
from streamlit_autorefresh import st_autorefresh

# API 엔드포인트 설정 (환경변수 우선)
API_URL = os.environ.get("API_URL", "http://localhost:10000")

def get_my_ip():
    try:
        return requests.get('https://api.ipify.org').text
    except:
        return "local"

st.set_page_config(page_title="당근 스터디 모임", layout="wide")
st.title("🥕 당근 스터디 모임")

# 사이드바 안내 메시지
with st.sidebar:
    st.markdown("### 🥕 당근 스터디")
    st.info("회원가입/로그인 없이 IP 기반으로 기록이 저장됩니다.")
    menu = ["뽀모도로 타이머", "인증 업로드", "실시간 피드", "통계"]
    choice = st.selectbox("메뉴", menu)

my_ip = get_my_ip()

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

    if 'timer_running' not in st.session_state:
        st.session_state.timer_running = False
    if 'timer_end' not in st.session_state:
        st.session_state.timer_end = None
    if 'timer_set_seconds' not in st.session_state:
        st.session_state.timer_set_seconds = set_seconds

    start_btn = st.button("START")
    reset_btn = st.button("RESET")

    if start_btn:
        st.session_state.timer_running = True
        st.session_state.timer_set_seconds = set_seconds
        st.session_state.timer_end = (datetime.now() + timedelta(seconds=set_seconds)).isoformat()
    if reset_btn:
        st.session_state.timer_running = False
        st.session_state.timer_end = None
        st.session_state.timer_set_seconds = set_seconds

    # 남은 시간 계산 및 표시
    if st.session_state.timer_running and st.session_state.timer_end:
        end_time = datetime.fromisoformat(st.session_state.timer_end)
        left = int((end_time - datetime.now()).total_seconds())
        if left <= 0:
            st.session_state.timer_running = False
            st.session_state.timer_end = None
            st.success("타이머 종료! 기록이 저장됩니다.")
            try:
                requests.post(f"{API_URL}/timerlog/upload", data={
                    "set_seconds": st.session_state.timer_set_seconds,
                    "start_time": (end_time - timedelta(seconds=st.session_state.timer_set_seconds)).isoformat(),
                    "end_time": end_time.isoformat()
                })
            except Exception as e:
                st.error(f"기록 저장 실패: {e}")
            left = 0
        h, m = divmod(left, 3600)
        m, s = divmod(m, 60)
        st.markdown(f"## ⏳ 남은 시간: {int(h):02d}:{int(m):02d}:{int(s):02d}")
    else:
        h, m = divmod(set_seconds, 3600)
        m, s = divmod(m, 60)
        st.markdown(f"## ⏳ 남은 시간: {int(h):02d}:{int(m):02d}:{int(s):02d}")

    st.markdown("---")
    st.subheader("나의 타이머 기록")
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
            image_url = post["image_url"]
            if image_url.startswith("/"):
                image_url = API_URL + image_url
            st.image(image_url, width=200)
            st.write(post["comment"])
            st.caption(f"IP: {post['user_id']} | {post['created_at']}")
            st.markdown("---")
    except Exception as e:
        st.error(f"피드 불러오기 실패: {e}")

elif choice == "통계":
    st.header("📊 나의 통계")
    try:
        stats = requests.get(f"{API_URL}/stats/{my_ip}").json()
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