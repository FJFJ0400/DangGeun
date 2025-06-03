import streamlit as st

st.set_page_config(page_title="당근 스터디 모임", layout="wide")

st.title("🥕 당근 스터디 모임")

menu = ["뽀모도로 타이머", "인증 업로드", "실시간 피드", "통계", "게이미피케이션"]
choice = st.sidebar.selectbox("메뉴", menu)

if choice == "뽀모도로 타이머":
    st.header("⏰ 뽀모도로 타이머")
    st.write("50분 공부 + 10분 휴식 루틴을 제공합니다.")
    # TODO: 타이머 구현
elif choice == "인증 업로드":
    st.header("📸 인증 업로드")
    st.write("공부 인증 이미지를 업로드하고 코멘트를 남겨보세요.")
    # TODO: 업로드 폼 구현
elif choice == "실시간 피드":
    st.header("📰 실시간 피드")
    st.write("다른 사람들의 인증글을 실시간으로 확인하세요.")
    # TODO: 피드 리스트 구현
elif choice == "통계":
    st.header("📊 나의 통계")
    st.write("내 공부량, 인증횟수, 연속일수 등 다양한 통계를 확인하세요.")
    # TODO: 통계 UI 구현
elif choice == "게이미피케이션":
    st.header("🏆 게이미피케이션")
    st.write("인증왕, 연속일, 뱃지 등 다양한 동기부여 요소를 제공합니다.")
    # TODO: 랭킹, 뱃지 등 구현 