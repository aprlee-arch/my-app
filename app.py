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
    st.title("정기흡수 메뉴 고르기 👈(ﾟヮﾟ👈)")
    st.write("버튼을 누르면 카카오 지도가 식당을 하나 골라줍니다!")

    # 내 출입증과 동네 설정
    api_key = "ab13d19ee1e9080db6e7c939474ebb5c"
    
    # 사용자가 직접 동네를 입력할 수 있는 창!
    location = st.text_input("🔍 어느 지역 맛집을 찾으시나요?", "여의도동") 
    st.write("예시: 광명역, 부천역, 여의도동 등 자유롭게 적어보세요!")

# --- 마법의 클릭 버튼 만들기 ---
    if st.button("🎲 오늘 뭐 먹지? (클릭!)"):
        
        restaurants = [] # 식당을 담을 빈 바구니 준비
        
        # 1페이지부터 3페이지까지 (최대 45개) 반복해서 카카오에게 달라고 조르기!
        for page in range(1, 4): 
            query = f"{location} 맛집"
            # 주소 맨 끝에 '&page={page}' 를 붙여서 몇 페이지인지 알려줍니다
            url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={query}&category_group_code=FD6&page={page}"
            headers = {"Authorization": f"KakaoAK {api_key}"}

            response = requests.get(url, headers=headers)
            result = response.json()

            # 바구니에 식당 이름 담기
            for place in result.get('documents', []):
                restaurants.append(place['place_name'])
            
            # 만약 동네가 작아서 식당이 다 떨어졌으면(마지막 페이지면) 그만 가져오기
            if result.get('meta', {}).get('is_end'):
                break

# --- 결과 보여주기 및 사진 띄우기! ---
        if restaurants:
            st.write(f"📍 **{location}** 주변 식당 {len(restaurants)}개를 싹싹 긁어왔어요!")
            st.write("🥁 두구두구두구... 오늘의 추천 점심 메뉴는?!")
            
            # 1. 룰렛 돌려서 식당 하나 뽑기
            selected_restaurant = random.choice(restaurants)
            
            # 뽑힌 식당 이름 크게 보여주기
            st.subheader(f"👉 [ {selected_restaurant} ] 👈")
            
            # 2. 카카오 이미지 검색 API로 방금 뽑힌 식당 사진 찾아오기!
            image_query = f"{location} {selected_restaurant}" # 예: "광명역 홍콩반점"
            image_search_url = f"https://dapi.kakao.com/v2/search/image?query={image_query}&size=1"
            
            # 출입증(headers)은 아까 지도 검색할 때 썼던 걸 그대로 씁니다
            image_response = requests.get(image_search_url, headers=headers)
            image_result = image_response.json()
            
            # 3. 사진이 성공적으로 찾아졌다면 화면에 예쁘게 띄우기
            if image_result.get('documents'):
                img_url = image_result['documents'][0]['image_url']
                # st.image()가 스트림릿에서 마법처럼 사진을 띄워주는 명령어입니다
                st.image(img_url, caption=f"📸 {selected_restaurant} 관련 사진", use_container_width=True)
            else:
                st.info("앗, 이 식당은 인터넷에서 사진을 찾지 못했어요 😢")
    
        else:
            st.error("앗, 식당을 찾지 못했어요. 동네 이름을 다시 확인해 보세요!")
