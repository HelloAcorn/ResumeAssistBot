import streamlit as st
from PyPDF2 import PdfReader
import requests
import json
import os

# 환경 변수에서 API 키를 가져옴
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def analyze_with_gemini_api(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [{"parts": [{"text": text}]}]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()

def query_gemini_with_context(context, question):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [{"parts": [{"text": f"{context}\n\nQuestion: {question}"}]}]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    result = response.json()
    return result['candidates'][0]['content']['parts'][0]['text']

def main():
    st.title("PDF 문서 분석 및 질문 응답 챗봇")
    st.write("PDF 파일을 드래그 앤 드롭하여 업로드하고, 질문을 통해 문서 내용을 확인하세요.")

    # st.session_state 초기화
    if 'pdf_text' not in st.session_state:
        st.session_state.pdf_text = ""
    if 'analysis_result' not in st.session_state:
        st.session_state.analysis_result = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'analysis_done' not in st.session_state:
        st.session_state.analysis_done = False

    if not st.session_state.analysis_done:
        uploaded_file = st.file_uploader("PDF 파일을 업로드하세요", type="pdf")
        if uploaded_file is not None:
            with st.spinner("파일을 분석 중입니다..."):
                pdf_text = extract_text_from_pdf(uploaded_file)
                st.session_state.pdf_text = pdf_text
                analysis_result = analyze_with_gemini_api(pdf_text)
                st.session_state.analysis_result = analysis_result
                st.session_state.analysis_done = True  # 분석 완료 플래그 설정
                st.success("분석이 완료되었습니다!")
                st.experimental_rerun()  # 분석이 완료되면 페이지를 리로드하여 채팅 인터페이스로 이동
    else:
        st.text_area("PDF 내용", st.session_state.pdf_text, height=300)
        user_question = st.text_input("질문을 입력하세요", key="user_question_input")

        if st.button("질문 전송"):
            if user_question:
                with st.spinner("Gemini와 대화 중입니다..."):
                    response = query_gemini_with_context(st.session_state.pdf_text, user_question)
                    st.session_state.chat_history.append({"question": user_question, "response": response})
                    st.success("응답을 받았습니다!")

        st.write("### 대화 기록")
        for chat in st.session_state.chat_history:
            st.markdown(f"<div style='text-align: left; background-color: #D1E7DD; padding: 10px; border-radius: 10px; margin-bottom: 5px;'><strong>질문:</strong> {chat['question']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div style='text-align: right; background-color: #F8D7DA; padding: 10px; border-radius: 10px; margin-bottom: 5px;'><strong>응답:</strong> {chat['response']}</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
