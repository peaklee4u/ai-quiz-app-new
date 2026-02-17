import google.generativeai as genai
import json
import streamlit as st

def init_gemini(api_key):
    """Gemini API를 초기화합니다."""
    genai.configure(api_key=api_key)

def generate_quiz(text_content, num_questions=5):
    """
    텍스트 내용을 바탕으로 퀴즈를 생성합니다.
    """
    # 사용 가능한 모델 찾기
    model_name = 'gemini-1.5-flash' # 기본값
    try:
        logging_models = []
        for m in genai.list_models():
            logging_models.append(m.name)
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini' in m.name:
                    model_name = m.name
                    break # 첫 번째 발견된 Gemini 모델 사용
        # st.toast(f"사용 모델: {model_name}") # 디버깅용 (필요시 주석 해제)
    except Exception as e:
        st.warning(f"모델 목록 조회 실패, 기본값({model_name})을 사용합니다. 에러: {e}")

    try:
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        당신은 교육 전문가입니다. 아래 제공된 텍스트 내용을 바탕으로 학습자의 이해도를 평가할 수 있는 객관식 퀴즈 {num_questions}개를 만들어주세요.
        
        [텍스트 내용]
        {text_content[:10000]}  # 텍스트가 너무 길 경우 앞부분만 사용 (토큰 제한 고려)
        
        [요구사항]
        1. 문제는 핵심 개념을 묻는 것이어야 합니다.
        2. 각 문제는 4개의 보기를 가져야 합니다.
        3. 정답과 오답에 대한 명확하고 상세한 해설을 포함하세요.
        4. 반드시 아래 JSON 형식으로만 출력하세요. 마크다운이나 다른 텍스트는 포함하지 마세요.

        [출력 형식]
        [
            {{
                "question": "문제 내용",
                "options": ["보기1", "보기2", "보기3", "보기4"],
                "answer": "정답 보기 (예: 보기1)",
                "explanation": "해설 내용"
            }},
            ...
        ]
        """

        response = model.generate_content(prompt)
        response_text = response.text
        
        # JSON 포맷팅 보정 (혹시 모를 마크다운 제거)
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "")
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "")
        
        quiz_data = json.loads(response_text)
        return quiz_data

    except Exception as e:
        st.error(f"퀴즈 생성 중 오류 발생: {e}")
        st.error(f"사용 시도한 모델: {model_name}")
        return []
