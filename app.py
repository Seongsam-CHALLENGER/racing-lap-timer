import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# 페이지 설정
st.set_page_config(
    page_title="레이싱 랩타임 기록 및 분석 시스템",
    page_icon="🏎️",
    layout="wide"
)

# 세션 상태 초기화 (데이터 및 로그인 상태 유지)
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "lap_data" not in st.session_state:
    st.session_state["lap_data"] = pd.DataFrame(columns=["세션명", "랩 번호", "랩타임(초)"])

# 비밀번호 인증 화면 (st.secrets 사용)
def check_password():
    def password_entered():
        # st.secrets에 설정된 비밀번호와 비교
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["logged_in"] = True
            del st.session_state["password"]  # 비밀번호 상태 제거
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

# 인증 통과 시에만 앱 실행
if check_password():
    st.title("🏎️ 레이싱 랩타임 기록 및 분석 시스템")
    st.markdown("팀원들과 실시간으로 랩타임 기록을 공유하고 분석하세요!")

    # 사이드바 - 데이터 입력 설정
    st.sidebar.header("⚙️ 데이터 입력 설정")
    session_name = st.sidebar.text_input("이벤트/세션 명", value="예선전_1차")

    st.sidebar.markdown("---")
    st.sidebar.subheader("랩타임 입력 (예: 123 또는 45.67)")

    # 엔터키 입력 지원을 위한 form 활용
    with st.sidebar.form(key="lap_form", clear_on_submit=True):
        lap_input = st.text_input("랩타임(초)")
        submit_button = st.form_submit_button(label="기록 추가하기 (Enter 가능)")

        if submit_button and lap_input:
            try:
                lap_time_val = float(lap_input)
                
                # 현재 세션의 기존 랩 개수 확인하여 다음 랩 번호 부여
                current_session_df = st.session_state["lap_data"][
                    st.session_state["lap_data"]["세션명"] == session_name
                ]
                next_lap_no = len(current_session_df) + 1

                # 새로운 데이터 추가
                new_row = pd.DataFrame({
                    "세션명": [session_name],
                    "랩 번호": [next_lap_no],
                    "랩타임(초)": [lap_time_val]
                })
                
                st.session_state["lap_data"] = pd.concat(
                    [st.session_state["lap_data"], new_row], 
                    ignore_index=True
                )
                st.sidebar.success(f"{next_lap_no}랩 기록 ({lap_time_val}초) 추가 완료!")
            except ValueError:
                st.sidebar.error("⚠️ 올바른 숫자를 입력해주세요 (예: 78.5)")

    # 전체 초기화 버튼
    if st.sidebar.button("전체 기록 초기화"):
        st.session_state["lap_data"] = pd.DataFrame(columns=["세션명", "랩 번호", "랩타임(초)"])
        st.rerun()

    # 메인 화면 구성
    st.markdown(f"### 📌 현재 세션: [{session_name}]")

    # 현재 세션 데이터 필터링
    df = st.session_state["lap_data"]
    session_df = df[df["세션명"] == session_name]

    if not session_df.empty:
        # 주요 지표 표시
        best_lap = session_df["랩타임(초)"].min()
        avg_lap = session_df["랩타임(초)"].mean()
        total_laps = len(session_df)

        col1, col2, col3 = st.columns(3)
        col1.metric("🏆 베스트 랩타임", f"{best_lap:.2f} 초")
        col2.metric("📊 평균 랩타임", f"{avg_lap:.2f} 초")
        col3.metric("🔄 총 주행 랩 수", f"{total_laps} 랩")

        st.markdown("---")

        # 시각화 및 데이터 테이블 레이아웃 분할
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
            st.subheader("📋 기록 데이터")
            st.dataframe(session_df[["랩 번호", "랩타임(초)"]], hide_index=True, use_container_width=True)

            # CSV 다운로드 버튼
            csv_data = session_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 CSV로 내보내기",
                data=csv_data,
                file_name=f"lap_times_{session_name}.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.info("👈 왼쪽 사이드바에서 랩타임 숫자를 직접 입력하고 엔터나 버튼을 눌러 연속으로 기록하세요!")
