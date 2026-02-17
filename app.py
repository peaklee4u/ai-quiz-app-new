import streamlit as st
import quiz_generator as qg
import utils
import os

# 페이지 설정
st.set_page_config(
    page_title="AI 퀴즈 생성기",
    page_icon="🎓",
    layout="wide"
)

# 스타일링
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
    }
    .success-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #D4EDDA;
        color: #155724;
        margin-bottom: 1rem;
    }
    .error-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #F8D7DA;
        color: #721C24;
        margin-bottom: 1rem;
    }
    .question-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.title("🎓 AI 퀴즈 마스터")
    st.markdown("강의 자료를 업로드하면 AI가 핵심 문제를 만들어 드립니다!")

    # 사이드바 설정
    with st.sidebar:
        st.header("설정 및 업로드")
        
        # API 키 설정 (secrets에서 가져오기)
        try:
            if "GEMINI_API_KEY" in st.secrets:
                api_key = st.secrets["GEMINI_API_KEY"]
            else:
                st.error("secrets.toml에 GEMINI_API_KEY가 설정되지 않았습니다.")
                st.stop()
        except FileNotFoundError:
             st.error("secrets.toml 파일이 없습니다. .streamlit 폴더에 생성해주세요.")
             st.stop()
        except Exception as e:
            st.error(f"설정 로드 중 오류 발생: {e}")
            st.stop()
        
        # 파일 업로드
        uploaded_file = st.file_uploader("강의 자료 업로드 (PDF, PPTX, TXT)", type=['pdf', 'pptx', 'txt'])
        
        if st.button("퀴즈 생성하기") and uploaded_file:
            if api_key:
                qg.init_gemini(api_key)
                with st.spinner("파일 분석 및 퀴즈 생성 중... (잠시만 기다려주세요)"):
                    text_content = utils.extract_text(uploaded_file)
                    if len(text_content) < 50:
                        st.error("텍스트 추출 실패: 내용이 너무 적거나 읽을 수 없습니다.")
                    else:
                        quiz_data = qg.generate_quiz(text_content)
                        if quiz_data:
                            st.session_state['quiz_data'] = quiz_data
                            st.session_state['user_answers'] = [None] * len(quiz_data)
                            st.session_state['score'] = 0
                            st.rerun()

    # 퀴즈 세션 상태 확인
    if 'quiz_data' in st.session_state and st.session_state['quiz_data']:
        quiz_data = st.session_state['quiz_data']
        
        # 진행률 표시
        answered_count = len([x for x in st.session_state['user_answers'] if x is not None])
        progress = answered_count / len(quiz_data)
        st.progress(progress)
        
        st.markdown(f"### 총 {len(quiz_data)}문제 중 {answered_count}문제 완료")

        for idx, q in enumerate(quiz_data):
            with st.container():
                st.markdown(f"<div class='question-card'><h4>Q{idx+1}. {q['question']}</h4></div>", unsafe_allow_html=True)
                
                # 라디오 버튼 키를 유니크하게 설정
                user_choice = st.radio(
                    "정답을 선택하세요:",
                    q['options'],
                    key=f"q_{idx}",
                    index=None
                )
                
                if user_choice:
                    st.session_state['user_answers'][idx] = user_choice
                    
                    if user_choice == q['answer']:
                        st.markdown(f"<div class='success-box'>✅ 정답입니다! <br><b>해설:</b> {q['explanation']}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='error-box'>❌ 오답입니다. <br><b>정답:</b> {q['answer']} <br><b>해설:</b> {q['explanation']}</div>", unsafe_allow_html=True)
                
                st.divider()

        # 결과 확인 버튼
        if answered_count == len(quiz_data):
            if st.button("최종 결과 확인"):
                score = 0
                for i, ans in enumerate(st.session_state['user_answers']):
                    if ans == quiz_data[i]['answer']:
                        score += 1
                
                st.session_state['score'] = score
                st.balloons()
                
                st.markdown(f"""
                <div style='text-align: center; padding: 2rem; background-color: #e6f3ff; border-radius: 10px;'>
                    <h2>🏆 최종 점수: {score} / {len(quiz_data)}</h2>
                </div>
                """, unsafe_allow_html=True)

                if score < len(quiz_data):
                     st.warning("💡 부족한 부분을 다시 학습해보세요!")

                if st.button("다시 시작하기"):
                    # 상태 초기화
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()

    else:
        st.info("👈 왼쪽 사이드바에서 파일을 업로드하고 퀴즈를 생성하세요.")

if __name__ == "__main__":
    main()
