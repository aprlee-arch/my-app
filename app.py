import streamlit as st
import requests
import random
import pandas as pd
import pydeck as pdk

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
    st.title("선택의 요정 🧚")
    st.write("버튼을 누르면 카카오 지도가 식당을 하나 골라줍니다!")

    # 내 출입증과 동네 설정
    api_key = "ab13d19ee1e9080db6e7c939474ebb5c"
    
# 사용자가 직접 동네를 입력할 수 있는 창!
    location = st.text_input("🔍 어느 지역 맛집을 찾으시나요?", "광명사거리역") 
    st.write("예시: 광명역, 부천역, 여의도동, 은행로 54 등 자유롭게 적어보세요!")

    # --- 🎁 새로운 맞춤형 기능: 음식 종류 & 체크박스 ---
    st.write("---") 
    
    # 1. 음식 종류를 선택하는 깔끔한 메뉴 창 만들기
    cuisine = st.selectbox("🍜 어떤 종류의 음식이 땡기시나요?", ["아무거나", "한식", "중식", "일식", "양식", "분식"])

    # 2. 아이 동반 체크박스
    is_kids_friendly = st.checkbox("👶 아이들과 맘 편히 갈 수 있는 식당만 찾기 (놀이방, 캠핑 감성 등)")

    st.write("---") 

    
# --- 마법의 클릭 버튼 만들기 ---
    if st.button("🎲 오늘 뭐 먹지? (클릭!)"):
        
        restaurants = []
        
        for page in range(1, 4): 
            base_keyword = "맛집" if cuisine == "아무거나" else cuisine
            if is_kids_friendly:
                kids_keywords = ["놀이방 식당", "아기랑", "예스키즈존", "캠핑 식당"]
                query = f"{location} {base_keyword} {random.choice(kids_keywords)}"
            else:
                query = f"{location} {base_keyword}"

            url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={query}&category_group_code=FD6&page={page}"
            headers = {"Authorization": f"KakaoAK {api_key}"}

            response = requests.get(url, headers=headers)
            result = response.json()

            # ✅ 이름, 링크와 함께 '지도 좌표(x, y)'도 바구니에 같이 담습니다!
            for place in result.get('documents', []):
                restaurants.append({
                    "name": place['place_name'],
                    "link": place['place_url'],
                    "lat": float(place['y']), # 위도
                    "lon": float(place['x'])  # 경도
                })
                
            if result.get('meta', {}).get('is_end'):
                break

        # --- 결과 보여주기 ---
        if restaurants:
            st.write(f"📍 **{location}** 주변 식당 {len(restaurants)}개를 싹싹 긁어왔어요!")
            st.write("🥁 두구두구두구... 오늘의 추천 점심 메뉴는?!")
            
            selected_data = random.choice(restaurants)
            selected_restaurant = selected_data["name"]
            restaurant_link = selected_data["link"]
            lat = selected_data["lat"]
            lon = selected_data["lon"]
            
            st.subheader(f"👉 [ {selected_restaurant} ] 👈")
            st.link_button("🗺️ 카카오맵에서 방문자 리뷰 & 메뉴판 확인하기", restaurant_link)
            
            # ⭐️ 화면을 두 칸으로 나누기! (왼쪽: 사진, 오른쪽: 지도)
            col1, col2 = st.columns(2) 
            
            # --- 🛡️ [왼쪽 칸] 사진 띄우기 ---
            with col1:
                try:
                    image_search_url = "https://dapi.kakao.com/v2/search/image"
                    params = {"query": f"{location} {selected_restaurant}", "size": 1}
                    image_response = requests.get(image_search_url, headers=headers, params=params)
                    image_result = image_response.json()
                    
                    if image_result.get('documents'):
                        img_url = image_result['documents'][0]['image_url']
                        img_data = requests.get(img_url).content
                        # 사진이 col1(절반 크기)에 쏙 맞게 들어갑니다
                        st.image(img_data, caption=f"📸 {selected_restaurant} 관련 사진", use_container_width=True)
                    else:
                        st.info("앗, 인터넷에서 사진을 찾지 못했어요 😢")
                        
                except Exception as e:
                    st.info("사진을 불러오지 못했어요. 😅")

            # --- 🗺️ [오른쪽 칸] 지도 띄우기 --- #

            with col2:
                map_data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
                
                # 1. 지도의 중심점과 확대 정도(zoom) 설정
                view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=15)
                
                # 🚨 에러 원인 해결: 색상과 위치에서 문제의 '따옴표'를 제거했습니다!
                layer = pdk.Layer(
                    'ScatterplotLayer',
                    data=map_data,
                    get_position=['lon', 'lat'],    # 👈 따옴표 제거!
                    get_radius=50,                  # 점의 크기
                    get_fill_color=[255, 50, 50],   # 👈 따옴표 완전 제거! (숫자 리스트로 변경)
                    pickable=True
                )
                
                # 3. Outdoors 테마로 멋진 지도 그리기!
                st.pydeck_chart(pdk.Deck(
                    map_style='mapbox://styles/mapbox/outdoors-v11', 
                    initial_view_state=view_state,
                    layers=[layer]
                ))
        else:
            st.error("앗, 식당을 찾지 못했어요. 동네 이름을 다시 확인해 보세요!")
