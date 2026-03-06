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
    
# --- 🎁 마법의 사이드바 (왼쪽 메뉴) 만들기 ---
    with st.sidebar:
        st.header("🔎 맛집 검색 설정")
        
        # 1. 지역 및 음식 종류
        location = st.text_input("🔍 어느 지역 맛집을 찾으시나요?", "광명") 
        cuisine = st.selectbox("🍜 어떤 음식이 땡기시나요?", ["아무거나", "한식", "중식", "일식", "양식", "분식"])
        
        st.write("---") 
        
        # ⭐️ 2. 방문 목적 선택창 (새로 추가!)
        purpose = st.selectbox("🎯 방문 목적이 무엇인가요?", ["상관없음", "데이트/분위기", "가족 모임", "가성비/혼밥", "회식/술자리"])
        
        # 3. 아이 동반 체크박스
        is_kids_friendly = st.checkbox("👶 아이들과 맘 편히 갈 수 있는 식당")
        
        st.write("---")
        search_clicked = st.button("🎲 오늘 뭐 먹지? (클릭!)")

    # --- 메인 화면 (오른쪽 결과창) ---
    if search_clicked:
        restaurants = []
        for page in range(1, 4): 
            # ✅ 검색어 조립의 마법!
            base_keyword = "맛집" if cuisine == "아무거나" else cuisine
            
            # 방문 목적에 따라 검색어에 살 붙이기
            purpose_keyword = ""
            if purpose == "점심식사": purpose_keyword = "점심" # '점심 맛집'이나 '점심'으로 적으셔도 좋아요!
            elif purpose == "데이트/분위기": purpose_keyword = "분위기 좋은"
            elif purpose == "가족 모임": purpose_keyword = "룸식당 가족모임"
            elif purpose == "가성비/혼밥": purpose_keyword = "가성비 혼밥"
            elif purpose == "회식/술자리": purpose_keyword = "회식 술집"

            # 최종 검색어 완성! (예: "광명 한식 분위기 좋은 놀이방 식당")
            query_parts = [location, base_keyword, purpose_keyword]
            if is_kids_friendly:
                query_parts.append(random.choice(["놀이방 식당", "아기랑", "예스키즈존", "캠핑 식당"]))
            
            # 빈칸을 기준으로 단어들을 예쁘게 이어 붙여줍니다
            query = " ".join([word for word in query_parts if word])

            url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={query}&category_group_code=FD6&page={page}"
            # ...(이 아래 API 요청 코드는 그대로 유지합니다!)...

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

# --- 🗺️ [오른쪽 칸] 지도 띄우기 (Outdoors 테마!) ---
            with col2:
                map_data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
                
                # 1. 지도의 중심점과 확대 정도(zoom) 설정
                view_state = pdk.ViewState(latitude=lat, longitude=lon, zoom=15)
                
                # 🚨 에러 원인 해결: 색상과 위치에서 문제의 '따옴표'를 제거했습니다!
                layer = pdk.Layer(
                    'ScatterplotLayer',
                    data=map_data,
                    get_position=['lon', 'lat'],    # 👈 따옴표 제거!
                    get_radius=20,                  # 점의 크기
                    get_fill_color=[255, 50, 50],   # 👈 따옴표 완전 제거! (숫자 리스트로 변경)
                    pickable=True
                )
                
                # 3. Outdoors 테마로 멋진 지도 그리기!
                st.pydeck_chart(pdk.Deck(
                    map_style='road', 
                    initial_view_state=view_state,
                    layers=[layer]
                ))
        else:
            st.error("앗, 식당을 찾지 못했어요. 동네 이름을 다시 확인해 보세요!")
