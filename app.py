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
    st.title("선택의 요정 🧚")
    st.write("버튼을 누르면 카카오 지도가 식당을 하나 골라줍니다!")

    # 내 출입증과 동네 설정
    api_key = "ab13d19ee1e9080db6e7c939474ebb5c"
    
# 사용자가 직접 동네를 입력할 수 있는 창!
    location = st.text_input("🔍 어느 지역 맛집을 찾으시나요?", "광명") 
    st.write("예시: 광명역, 부천역, 여의도동 등 자유롭게 적어보세요!")

    # --- 🎁 새로운 맞춤형 기능: 체크박스 만들기 ---
    st.write("---") # 화면에 예쁜 가로줄을 하나 그어줍니다
    
    # 체크박스를 누르면 is_kids_friendly 가 True(참)가 됩니다
    is_kids_friendly = st.checkbox("👶 아이들과 맘 편히 갈 수 있는 식당만 찾기 (놀이방, 캠핑 감성 등)")
    
    # --- 마법의 클릭 버튼 만들기 ---
    if st.button("🎲 오늘 뭐 먹지? (클릭!)"):
        
        restaurants = []
        
        for page in range(1, 4): 
            # ✅ 체크박스가 눌렸는지 확인하고 검색어(query)를 똑똑하게 바꿉니다!
            if is_kids_friendly:
                # "광명 맛집" 대신 "광명 놀이방 식당" 또는 "광명 아기랑 식당"으로 검색!
                # 검색어를 리스트에서 랜덤으로 골라서 더 다양한 결과가 나오게 해봐요.
                kids_keywords = ["놀이방 식당", "아기랑 맛집", "예스키즈존", "캠핑 식당"]
                query = f"{location} {random.choice(kids_keywords)}"
            else:
                query = f"{location} 맛집"

            url = f"https://dapi.kakao.com/v2/local/search/keyword.json?query={query}&category_group_code=FD6&page={page}"
            headers = {"Authorization": f"KakaoAK {api_key}"}

            # ...(아래 데이터를 받아오는 requests.get 부분은 기존과 동일하게 둡니다)...
        
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
# --- 🛡️ 에러 방어막(try-except) 시작! ---
            try:
                image_search_url = "https://dapi.kakao.com/v2/search/image"
                params = {
                    "query": f"{location} {selected_restaurant}",
                    "size": 1
                }
                
                image_response = requests.get(image_search_url, headers=headers, params=params)
                image_result = image_response.json()
                
                # --- 🚨 여기서부터 바뀝니다! ---
                if image_result.get('documents'):
                    img_url = image_result['documents'][0]['image_url']
                    
                    # 주소만 띡 던져주지 않고, 파이썬(requests)이 직접 사진 데이터를 다운로드합니다!
                    img_data = requests.get(img_url).content
                    
                    # 다운받은 사진 데이터(img_data)를 화면에 띄웁니다
                    st.image(img_data, caption=f"📸 {selected_restaurant} 관련 사진", use_container_width=True)
                else:
                    st.info("앗, 이 식당은 인터넷에서 사진을 찾지 못했어요 😢")
                    
            except Exception as e:
                st.info("사진을 불러오지 못했어요. 식당 이름으로 만족해 주세요! 😅")
            # --- 🛡️ 에러 방어막 끝! ---
            
    
        else:
            st.error("앗, 식당을 찾지 못했어요. 동네 이름을 다시 확인해 보세요!")
