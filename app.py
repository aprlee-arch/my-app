import streamlit as st
import requests
import random

# --- 1. 철통 보안! 비밀번호 설정 ---
# 사이트 접속 시 가장 먼저 보이는 화면입니다.
password = st.text_input("나만의 비밀번호를 입력하세요 🔒", type="password")

if password == "1130":  # 원하는 비밀번호 숫자로 변경하세요!
    st.success("로그인 성공! 환영합니다. 🎉")

    # --- 2. 웹사이트 메인 화면 꾸미기 ---
    st.title("🍔 우리 동네 점심 메뉴 뽑기 봇")
    st.write("버튼을 누르면 카카오 지도가 식당을 하나 골라줍니다!")

    # 내 출입증과 동네 설정
    api_key = "ab13d19ee1e9080db6e7c939474ebb5c" 
    location = "서울시 영등포구 여의도동"  # 자주 가시는 동네 이름으로 바꿔주세요!

    # --- 3. 마법의 클릭 버튼 만들기 ---
    if st.button("🎲 오늘 뭐 먹지? (클릭!)"):
        
        # 카카오 API 요청 코드 (이전과 똑같습니다)
        query = f"{location} 맛집"
        url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={query}&category_group_code=FD6"
        headers = {"Authorization": f"KakaoAK {api_key}"}

        response = requests.get(url, headers=headers)
        result = response.json()

        restaurants = []
        for place in result.get('documents', []):
            restaurants.append(place['place_name'])

        # --- 4. 결과 보여주기 ---
        if restaurants:
            st.write(f"📍 **{location}** 주변 식당 {len(restaurants)}개를 찾았어요!")
            st.write("🥁 두구두구두구... 오늘의 추천 점심 메뉴는?!")
            
            # 결과를 아주 크고 예쁘게 보여줍니다
            st.subheader(f"👉 [ {random.choice(restaurants)} ] 👈")
        else:
            st.error("앗, 식당을 찾지 못했어요. 동네 이름을 다시 확인해 보세요!")

elif password != "":
    st.error("비밀번호가 틀렸습니다. 다시 입력해 주세요.")
