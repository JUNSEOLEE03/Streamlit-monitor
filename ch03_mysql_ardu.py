import streamlit as st
import pandas as pd
import pymysql
import time

# MySQL 연결 설정
conn = pymysql.connect(
    host= "220.66.160.87",         # MySQL 서버 주소
    user="smart",                  # MySQL 사용자 이름
    password="smart",              # MySQL 비밀번호
    db="smartf_2025_01"            # 사용할 데이터베이스
)

# conn이라는 데이터베이스 핸들 역할
curs = conn.cursor() 

# 페이지 설정
st.set_page_config(
    page_title = "Streamlit을 이용한 실시간 스마트 팜 모니터링",
    page_icon = "📈📉",
    layout = "wide"
)

# 이미지 크기를 줄이기 위해 비율 설정
col1, col2 = st.columns([1, 4])

with col1:
    # 작은 크기로 표시
    st.image("23emblem-1.jpg", width = 300)
with col2:
    st.title("Streamlit을 이용한 실시간 생육 환경 모니터링 연구")

st.write("스마트 팜의 효율적인 환경 개선을 도와주고 / 온도, 습도, 조도, CO2 값을 보여줌.")

# 데이터 초기화
st.subheader("측정 값 시각화")

# ✅ 최신 측정 값 표시할 자리 (제목 아래로 이동)
measurement_placeholder = st.empty()

# ✅ 그래프를 고정할 자리 미리 확보
temp_chart_placeholder = st.empty()
humi_chart_placeholder = st.empty()
light_chart_placeholder = st.empty()
CO2_chart_placeholder = st.empty()

# 세션 상태에 데이터가 저장되지 않은 경우 초기화
if 'chart_data' not in st.session_state:
    st.session_state.chart_data = pd.DataFrame(columns=["Time", "Temperature", "Humidity", "Light", "CO2"])

 # ✅ 그래프를 처음 한 번만 표시
with temp_chart_placeholder.container():
    st.subheader("🌡 Temperature 변화")
    st.line_chart(st.session_state.chart_data.set_index('Time')[['Temperature']])

with humi_chart_placeholder.container():
    st.subheader("💦 Humidity 변화")
    st.line_chart(st.session_state.chart_data.set_index('Time')[['Humidity']])

with light_chart_placeholder.container():
    st.subheader("💡 Light 변화")
    st.line_chart(st.session_state.chart_data.set_index('Time')[['Light']])

with CO2_chart_placeholder.container():
    st.subheader("🌍 CO2 변화")
    st.line_chart(st.session_state.chart_data.set_index('Time')[['CO2']])

# 데이터 업데이트 루프
while True: 
    # 데이터 테이블 선택 후 출력
    sql = "select * from smart"
    curs.execute(sql)
    rows = curs.fetchall()

    # Pandas에서 데이터를 "표" 형식으로 변환 후 'result' 변수에 저장
    result = pd.DataFrame(rows)

    # Pandas의 DataFrame에서 마지막 개의 행을 선택하는 코드
    data = result.tail(1)

    # 시간 간결, 구체화(년-월-일 시:분:초)
    time1 = data[1].values 
    time_str = str(time1).split('.')[0]
    time_list = [time_str]
    cleaned_str = time_str.replace("['", "").replace("T", " ")

    # 온도, 습도, 조도 값
    temp = data[2].values
    humi = data[3].values
    light = data[4].values
    CO2 = data[5].values

    # 새 데이터를 기존 chart_data에 추가
    new_data = pd.DataFrame({
        'Time': [cleaned_str],
        'Temperature': [temp[0]],
        'Humidity': [humi[0]],
        'Light': [light[0]],
        'CO2' : [CO2[0]]
    })

    # ✅ 최신 200개 데이터만 유지 (오래된 데이터 삭제)
    st.session_state.chart_data = pd.concat(
        [st.session_state.chart_data, new_data], ignore_index=True
    ).tail(200)

    # ✅ "측정 값 시각화" 아래에 최신 데이터 표시
    with measurement_placeholder.container():
        st.subheader(f"📅 측정 시간: {cleaned_str}")
        cols = st.columns((1, 1, 1, 2))
        cols[0].metric("🌡 Temperature", float(temp[0]))
        cols[1].metric("💦 Humidity", float(humi[0]))
        cols[2].metric("💡 Light", float(light[0]))
        cols[3].metric("🌍 CO2", int(CO2[0]))

    # ✅ 개별 그래프 업데이트
    with temp_chart_placeholder.container():
        st.subheader("🌡 Temperature 변화")
        st.line_chart(st.session_state.chart_data.set_index('Time')[['Temperature']])

    with humi_chart_placeholder.container():
        st.subheader("💦 Humidity 변화")
        st.line_chart(st.session_state.chart_data.set_index('Time')[['Humidity']])

    with light_chart_placeholder.container():
        st.subheader("💡 Light 변화")
        st.line_chart(st.session_state.chart_data.set_index('Time')[['Light']])
    
    with CO2_chart_placeholder.container():
        st.subheader("🌍 CO2 변화")
        st.line_chart(st.session_state.chart_data.set_index('Time')[['CO2']])
    
    # 프로그램 2초 동안 멈춤
    time.sleep(2) 

    # streamlit 페이지 강제 새로고침
    st.rerun()