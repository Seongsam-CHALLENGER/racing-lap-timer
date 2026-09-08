import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time

# 페이지 설정
st.set_page_config(
    page_title="레이싱 랩타임 기록 및 분석 시스템",
    page_icon="🏎️",
    layout="wide"
)

# 세션 상태 초기화
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "lap_data" not in st.session_state:
    st.session_state["lap_data"] = pd.DataFrame(columns=["세션명", "랩 번호", "랩타임(초)"])

# 스탑워치용 세션 상태 초기화
if "is_running" not in st.session_state:
    st.session_state["is_running"] = False
if "start_time" not in st.session_state:
    st.session_state["start_time"] = 0.0
if "elapsed_time" not in st.session_state:
    st.session_state["elapsed_time"] = 0.0
if "last_lap_time" not in st.session_state:
    st.session_state["last_lap_time"] = 0.0

# 비밀번호 인증 함수
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["logged_in"] = True
            del st.session_state["password"]
        else:
            st.session_state["logged_in"] = False

    if not st.session_state["logged_in"]:
        st.markdown("## 🔐 시스템 접근 권한 확인")
        st.text_input(
            "비밀번호를 입력하세요", 
            type="password", 
            key="password", 
            on_change=password_entered
        )
        return False
    return True

if check_password():
    st.title("🏎️ 레이싱 랩타임 스탑워치 시스템")
    st.markdown("스탑워치 버튼을 활용해 실시간으로 랩타임을 측정하세요!")

    # 사이드바 - 세션 설정 및 컨트롤
    st.sidebar.header("⚙️ 측정 제어판")
    session_name = st.sidebar.text_input("이벤트/세션 명", value="결승전_1차")

    st.sidebar.markdown("---")

    # 스탑워치 로직 계산
    current_time = time.time()
    if st.session_state["is_running"]:
        total_elapsed = st.session_state["elapsed_time"] + (current_time - st.session_state["start_time"])
        current_lap_elapsed = total_elapsed - st.session_state["last_lap_time"]
    else:
        total_elapsed = st.session_state["elapsed_time"]
        if st.session_state["start_time"] == 0:
            current_lap_elapsed = 0.0
        else:
            current_lap_elapsed = total_elapsed - st.session_state["last_lap_time"]

    # 화면에 타이머 실시간 표시용 박스
    st.sidebar.subheader("⏱️ 실시간 타이머")
    st.sidebar.metric("총 경과 시간", f"{total_elapsed:.2f} 초")
    st.sidebar.metric("현재 랩 진행 시간", f"{current_lap_elapsed:.2f} 초", delta_color="off")

    st.sidebar.markdown("---")

    # 스탑워치 시작 / 정지 버튼
    col_s1, col_s2 = st.sidebar.columns(2)
    with col_s1:
        if not st.session_state["is_running"]:
            if st.button("▶️ 측정 시작", use_container_width=True):
                st.session_state["is_running"] = True
                st.session_state["start_time"] = time.time()
                st.rerun()
        else:
            if st.button("⏸️ 일시정지", use_container_width=True):
                st.session_state["elapsed_time"] += time.time() - st.session_state["start_time"]
                st.session_state["is_running"] = False
                st.rerun()

    with col_s2:
        if st.button("⏹️ 초기화", use_container_width=True):
            st.session_state["is_running"] = False
            st.session_state["start_time"] = 0.0
            st.session_state["elapsed_time"] = 0.0
            st.session_state["last_lap_time"] = 0.0
            st.rerun()

    # 랩 기록 버튼 (달리는 중에만 활성화 혹은 누를 때마다 현재 랩타임 저장)
    if st.button("🏁 랩(Lap) 기록하기", use_container_width=True, type="primary"):
        if st.session_state["is_running"] or total_elapsed > 0:
            # 이번 랩에 소요된 시간 계산
            lap_duration = current_lap_elapsed
            
            if lap_duration > 0.5: # 너무 짧은 오작동 클릭 방지
                current_session_df = st.session_state["lap_data"][
                    st.session_state["lap_data"]["세션명"] == session_name
                ]
                next_lap_no = len(current_session_df) + 1

                new_row = pd.DataFrame({
                    "세션명": [session_name],
                    "랩 번호": [next_lap_no],
                    "랩타임(초)": [round(lap_duration, 2)]
                })
                
                st.session_state["lap_data"] = pd.concat(
                    [st.session_state["lap_data"], new_row], 
                    ignore_index=True
                )
                
                # 마지막 랩 기준점 갱신 (다음 랩은 0초부터 다시 측정)
                st.session_state["last_lap_time"] = total_elapsed
                st.success(f"{next_lap_no}랩 기록 ({lap_duration:.2f}초) 저장 완료!")
                st.rerun()

    # 전체 데이터 초기화
    if st.sidebar.button("전체 랩 기록 리셋"):
        st.session_state["lap_data"] = pd.DataFrame(columns=["세션명", "랩 번호", "랩타임(초)"])
        st.rerun()

    # 메인 화면 분석 시각화
    st.markdown(f"### 📌 현재 세션: [{session_name}]")

    df = st.session_state["lap_data"]
    session_df = df[df["세션명"] == session_name]

    if not session_df.empty:
        best_lap = session_df["랩타임(초)"].min()
        avg_lap = session_df["랩타임(초)"].mean()
        total_laps = len(session_df)

        col1, col2, col3 = st.columns(3)
        col1.metric("🏆 베스트 랩타임", f"{best_lap:.2f} 초")
        col2.metric("📊 평균 랩타임", f"{avg_lap:.2f} 초")
        col3.metric("🔄 총 주행 랩 수", f"{total_laps} 랩")

        st.markdown("---")

        chart_col, table_col = st.columns([2, 1])

        with chart_col:
            st.subheader("📈 랩타임 트렌드 그래프")
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(
                session_df["랩 번호"], 
                session_df["랩타임(초)"], 
                marker="o", 
                linestyle="-", 
                color="crimson", 
                linewidth=2
            )
            ax.set_title(f"[{session_name}] Lap Times Trend")
            ax.set_xlabel("Lap Number")
            ax.set_ylabel("Time (seconds)")
            ax.grid(True, linestyle="--", alpha=0.6)
            st.pyplot(fig)

        with table_col:
            st.subheader("📋 랩 기록 데이터")
            st.dataframe(session_df[["랩 번호", "랩타임(초)"]], hide_index=True, use_container_width=True)

            csv_data = session_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 CSV로 내보내기",
                data=csv_data,
                file_name=f"lap_times_{session_name}.csv",
                mime="text/css",
                use_container_width=True
            )
    else:
        st.info("👈 사이드바에서 [측정 시작]을 누른 뒤, 차량이 들어올 때마다 [랩 기록하기] 버튼을 누르세요!")

    # 실시간 타이머가 구동 중일 때 화면 자동 새로고침 (초 단위 갱신용)
    if st.session_state["is_running"]:
        time.sleep(0.1)
        st.rerun()
