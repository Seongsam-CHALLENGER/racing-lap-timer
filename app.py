import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import platform

st.set_page_config(page_title="레이싱 랩타임 분석 시스템", page_icon="🏎️", layout="centered")

if platform.system() == 'Windows':
    plt.rc('font', family='Malgun Gothic')
elif platform.system() == 'Darwin':
    plt.rc('font', family='AppleGothic')
plt.rcParams['axes.unicode_minus'] = False

# --- 간단한 비밀번호 인증 기능 ---
def check_password():
    """비밀번호를 입력받아 일치할 경우에만 True를 반환합니다."""
    def password_entered():
        if st.session_state["password"] == "2027":  # 원하는 비밀번호로 변경하세요
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # 비밀번호 세션 삭제
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # 최초 실행 시 비밀번호 입력창 표시
        st.text_input("🔒 시스템 접근 비밀번호를 입력하세요", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # 비밀번호가 틀렸을 때
        st.text_input("🔒 시스템 접근 비밀번호를 입력하세요", type="password", on_change=password_entered, key="password")
        st.error("😕 비밀번호가 틀렸습니다.")
        return False
    else:
        # 인증 성공
        return True

if not check_password():
    st.stop()  # 비밀번호가 틀리거나 입력되기 전에는 아래 코드를 실행하지 않고 멈춤


st.title("🏎️ 레이싱 랩타임 기록 및 분석 시스템")
st.write("팀원들과 실시간으로 랩타임 기록을 공유하고 분석하세요!")

if "lap_times" not in st.session_state:
    st.session_state.lap_times = []

st.sidebar.header("⚙️ 데이터 입력 설정")
event_name = st.sidebar.text_input("이벤트/세션 명", value="예선전_1차")

with st.sidebar.form(key="lap_form", clear_on_submit=True):
    st.write("**랩타임 입력 (예: 123 또는 45.67)**")
    lap_input_str = st.text_input("랩타임(초)", value="")
    submit_btn = st.form_submit_button("기록 추가하기 (Enter 가능)", type="primary")

if submit_btn:
    try:
        new_lap = float(lap_input_str.strip())
        if new_lap > 0:
            st.session_state.lap_times.append(new_lap)
            st.sidebar.success(f"{len(st.session_state.lap_times)}랩 기록 추가 완료: {new_lap:.2f}초")
        else:
            st.sidebar.warning("0보다 큰 숫자를 입력해주세요.")
    except ValueError:
        st.sidebar.error("올바른 숫자 형식으로 입력해주세요 (예: 123 또는 45.67)")

if st.sidebar.button("전체 기록 초기화", type="secondary"):
    st.session_state.lap_times = []
    st.rerun()

st.subheader(f"📌 현재 세션: [{event_name}]")

if st.session_state.lap_times:
    df = pd.DataFrame({
        "랩 번호": list(range(1, len(st.session_state.lap_times) + 1)),
        "랩타임(초)": st.session_state.lap_times
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**[상세 기록 리스트]**")
        st.dataframe(df, use_container_width=True)
        
    with col2:
        st.write("**[주행 요약 분석]**")
        fastest = min(st.session_state.lap_times)
        slowest = max(st.session_state.lap_times)
        avg = sum(st.session_state.lap_times) / len(st.session_state.lap_times)
        
        st.metric(label="총 주행 랩", value=f"{len(st.session_state.lap_times)} 랩")
        st.metric(label="최고 기록 (최단)", value=f"{fastest:.2f} 초", delta=f"-{(avg-fastest):.2f}s vs Avg")
        st.metric(label="최저 기록 (최장)", value=f"{slowest:.2f} 초")
        st.metric(label="평균 랩타임", value=f"{avg:.2f} 초")

    st.subheader("📊 랩타임 추이 그래프")
    fig, ax = plt.subplots(figsize=(8, 4))
    laps = list(range(1, len(st.session_state.lap_times) + 1))
    
    ax.plot(laps, st.session_state.lap_times, marker='o', color='blue', linestyle='-', linewidth=2)
    
    for x, y in zip(laps, st.session_state.lap_times):
        if y == fastest:
            color, weight = 'red', 'bold'
        elif y == slowest:
            color, weight = 'blue', 'bold'
        else:
            color, weight = 'black', 'normal'
        ax.text(x, y + (max(st.session_state.lap_times) * 0.03), f"{y:.1f}s", 
                fontsize=9, ha='center', va='bottom', fontweight=weight, color=color)

    ax.set_xticks(laps)
    ax.set_title(f"Lap Time Trend - {event_name}")
    ax.set_xlabel("Lap Number")
    ax.set_ylabel("Time (seconds)")
    ax.grid(True)
    
    st.pyplot(fig)

    csv_data = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 CSV 파일로 다운로드하기",
        data=csv_data,
        file_name=f"{event_name}_records.csv",
        mime="text/csv",
    )
else:
    st.info("👈 왼쪽 사이드바에서 원하는 랩타임 숫자를 직접 입력하고 엔터나 버튼을 눌러 연속으로 기록하세요!")
