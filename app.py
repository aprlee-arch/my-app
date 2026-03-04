import streamlit as st
import requests
import random

# --- 1. 로그인 상태를 기억하는 '기억 상자' 만들기 ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- 2. 로그인 안 했을 때만 비밀번호 창 보여주기 ---
if not st.session_state.logged_in:
    password = st.text_input("펜타 점심시간 HHmm를 입력해주세요 (예 1130) 🔒", type="password")
    
    if password == "1130":  # 원하는 비밀번호 숫자로 변경하세요!
        st.session_state.logged_in = True
        st.rerun()  # 화면을 싹 새로고침해서 비밀번호 창을 날려버립니다!
    elif password != "":
        st.error("비밀번호가 틀렸습니다. 다시 입력해 주세요.")

# --- 3. 로그인 성공 시에만 나타나는 진짜 내 앱 화면 ---
if st.session_state.logged_in:
    st.title("🍔 우리 동네 점심 메뉴 뽑기 봇")
    st.write("버튼을 누르면 카카오 지도가 식당을 하나 골라줍니다!")

    # 내 출입증과 동네 설정
    api_key = "ab13d19ee1e9080db6e7c939474ebb5c"
    
    # 사용자가 직접 동네를 입력할 수 있는 창!
    location = st.text_input("🔍 어느 지역 맛집을 찾으시나요?", "여의도동") 
    st.write("예시: 광명역, 부천역, 여의도동 등 자유롭게 적어보세요!")

    # --- 마법의 클릭 버튼 만들기 ---
    if st.button("🎲 오늘 뭐 먹지? (클릭!)"):
        
        # 카카오 API 요청 코드
        query = f"{location} 맛집"
        url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={query}&category_group_code=FD6"
        headers = {"Authorization": f"KakaoAK {api_key}"}

        response = requests.get(url, headers=headers)
        result = response.json()

        restaurants = []
        for place in result.get('documents', []):
            restaurants.append(place['place_name'])

        # --- 결과 보여주기 ---
        if restaurants:
            st.write(f"📍 **{location}** 주변 식당 {len(restaurants)}개를 찾았어요!")
            st.write("🥁 두구두구두구... 오늘의 추천 점심 메뉴는?!")
            st.subheader(f"👉 [ {random.choice(restaurants)} ] 👈")
        else:
            st.error("앗, 식당을 찾지 못했어요. 동네 이름을 다시 확인해 보세요!")
