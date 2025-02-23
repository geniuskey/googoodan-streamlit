import streamlit as st
import time
import pandas as pd
from db_manager import init_db, insert_ranking, get_top_rankings
from game_logic import generate_questions, check_answer

def show_top_rankings(latest_rankings):
    """
    latest_rankings: [(name, score, play_time, correct_count), ...] 형태
    """
    if not latest_rankings:
        st.info("랭킹 데이터가 없습니다.")
        return

    # 표시용 딕셔너리 리스트 생성
    ranking_data = []
    for idx, row in enumerate(latest_rankings):
        r_name, r_score, r_time, r_correct = row
        ranking_data.append({
            "순위": idx + 1,
            "이름": r_name,
            "점수": f"{r_score:.2f}",
            "시간(초)": f"{r_time:.2f}",
            "맞힌 문제": r_correct
        })

    # pandas DataFrame으로 변환
    df = pd.DataFrame(ranking_data)

    # 인터랙티브 테이블(정렬/스크롤 등 가능): st.dataframe()
    st.dataframe(df, hide_index=True, use_container_width=True)

def main():
    st.title("구구단 게임")

    # DB 초기화
    init_db()

    # 세션 초기화
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0
    if "correct_count" not in st.session_state:
        st.session_state.correct_count = 0
    if "start_time" not in st.session_state:
        st.session_state.start_time = 0.0
    if "end_time" not in st.session_state:
        st.session_state.end_time = 0.0
    if "game_over" not in st.session_state:
        st.session_state.game_over = False
    if "incorrect_problems" not in st.session_state:
        st.session_state.incorrect_problems = []
    # 랭킹 등록 여부 플래그
    if "registered" not in st.session_state:
        st.session_state.registered = False

    # -----------------------
    # 1. 게임 시작(문제 생성) 처리
    # -----------------------
    if not st.session_state.questions and not st.session_state.game_over:
        if st.button("게임 시작", use_container_width=True):
            st.session_state.questions = generate_questions(num_questions=10)
            st.session_state.current_index = 0
            st.session_state.correct_count = 0
            st.session_state.incorrect_problems = []
            st.session_state.start_time = time.time()
            st.session_state.game_over = False
            st.session_state.registered = False  # 시작 시마다 초기화

    # -----------------------------
    # 2. 게임 진행
    # -----------------------------
    if st.session_state.questions and not st.session_state.game_over:
        q_str, q_answer, q_choices = st.session_state.questions[st.session_state.current_index]
        
        st.subheader(f"문제 {st.session_state.current_index+1} / {len(st.session_state.questions)}")
        st.markdown(
            f"<h1 style='text-align:center; font-size:48px;'>{q_str}</h1>",
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        for i, choice in enumerate(q_choices):
            button_label = f"{i+1}. {choice}"
            if i < 2:
                if col1.button(button_label, key=f"btn_{st.session_state.current_index}_{i}",
                               use_container_width=True):
                    if check_answer(choice, q_answer):
                        st.session_state.correct_count += 1
                    else:
                        # 틀린 문제 기록
                        st.session_state.incorrect_problems.append({
                            "question": q_str,
                            "user_answer": choice,
                            "correct_answer": q_answer
                        })

                    st.session_state.current_index += 1
                    if st.session_state.current_index >= len(st.session_state.questions):
                        st.session_state.end_time = time.time()
                        st.session_state.game_over = True
                    st.rerun()

            else:
                if col2.button(button_label, key=f"btn_{st.session_state.current_index}_{i}",
                               use_container_width=True):
                    if check_answer(choice, q_answer):
                        st.session_state.correct_count += 1
                    else:
                        st.session_state.incorrect_problems.append({
                            "question": q_str,
                            "user_answer": choice,
                            "correct_answer": q_answer
                        })

                    st.session_state.current_index += 1
                    if st.session_state.current_index >= len(st.session_state.questions):
                        st.session_state.end_time = time.time()
                        st.session_state.game_over = True
                    st.rerun()

    # -----------------------------
    # 3. 게임 종료 후 결과 표시
    # -----------------------------
    if st.session_state.game_over:
        total_time = st.session_state.end_time - st.session_state.start_time
        correct_count = st.session_state.correct_count
        score = max((correct_count * 10) - total_time, 0)

        st.subheader("게임 결과")
        st.write(f"- 맞힌 문제 수: **{correct_count} / {len(st.session_state.questions)}**")
        st.write(f"- 소요 시간: **{total_time:.2f}초**")
        st.write(f"- 최종 점수: **{score:.2f}**")

        # 틀린 문제 요약
        if st.session_state.incorrect_problems:
            with st.expander("틀린 문제 확인하기"):
                for idx, wrong_info in enumerate(st.session_state.incorrect_problems, start=1):
                    st.write(f"**{idx}. {wrong_info['question']}**")
                    st.write(f"- 내 답: {wrong_info['user_answer']}, 정답: {wrong_info['correct_answer']}")

        # -- 3-1) Top 100 진입 여부 판단 --
        rankings = get_top_rankings(100)
        if len(rankings) < 100:
            in_top_100 = True
        else:
            last_score = rankings[-1][1]  # (name, score, play_time, correct_count)에서 score
            in_top_100 = score > last_score

        # -- 3-2) 랭킹 등록 UI (이미 등록하지 않았다면 표시) --
        if in_top_100 and not st.session_state.registered:
            st.success("축하합니다! 현재 점수로 Top 100에 들었습니다!")
            user_name = st.text_input("이름을 입력해주세요.")
            if st.button("랭킹 등록", use_container_width=True):
                insert_ranking(user_name, float(f"{score:.2f}"), float(f"{total_time:.2f}"), correct_count)
                st.session_state.registered = True  # 등록 플래그 설정
                st.rerun()

        # -- 3-3) 랭킹 등록이 끝났으면 안내 문구만 표시 --
        if in_top_100 and st.session_state.registered:
            st.info("랭킹 등록이 완료되었습니다.")

        if not in_top_100:
            st.info("아쉽지만 Top 100에는 들지 못했습니다.")

        # 최신 TOP 100 랭킹 표시
        st.subheader("TOP 100 랭킹")
        latest_rankings = get_top_rankings(100)
        show_top_rankings(latest_rankings)

        # 게임 다시 시작
        if st.button("게임 다시 시작", use_container_width=True):
            st.session_state.questions = []
            st.session_state.current_index = 0
            st.session_state.correct_count = 0
            st.session_state.start_time = 0.0
            st.session_state.end_time = 0.0
            st.session_state.game_over = False
            st.session_state.incorrect_problems = []
            st.session_state.registered = False
            st.rerun()

if __name__ == "__main__":
    main()
