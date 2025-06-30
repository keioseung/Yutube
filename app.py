import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re
import anthropic

# Claude API 키 설정 (본인 키로 교체하세요)
# https://console.anthropic.com 에서 API 키를 발급받으세요
client = anthropic.Anthropic(
    api_key="your-claude-api-key-here"  # 여기에 실제 Claude API 키를 입력하세요
)

# 페이지 설정
st.set_page_config(
    page_title="YouTube 스크립트 추출기",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 커스텀 CSS - 삼성 스타일 프리미엄 디자인
st.markdown("""
<style>
    /* 전체 페이지 스타일 */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 메인 컨테이너 */
    .main-container {
        max-width: 1000px;
        margin: 0 auto;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin-top: 2rem;
        margin-bottom: 2rem;
    }
    
    /* 헤더 스타일 */
    .header-container {
        text-align: center;
        margin-bottom: 3rem;
        animation: fadeInDown 1s ease-out;
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        text-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        font-size: 1.3rem;
        color: #6b7280;
        font-weight: 400;
        margin-bottom: 0;
    }
    
    /* 입력 필드 스타일 */
    .stTextInput > div > div > input {
        background: #ffffff;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        transform: translateY(-2px);
    }
    
    /* 텍스트 영역 스타일 */
    .stTextArea > div > div > textarea {
        background: #f8fafc;
        border: 2px solid #e5e7eb;
        border-radius: 16px;
        padding: 1.5rem;
        font-family: 'Monaco', 'Menlo', monospace;
        line-height: 1.6;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        background: #ffffff;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* 정보/에러 메시지 스타일 */
    .stInfo {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
        border-radius: 12px;
        border-left: 4px solid #1e40af;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        animation: slideIn 0.5s ease-out;
    }
    
    .stError {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        border-radius: 12px;
        border-left: 4px solid #b91c1c;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        animation: slideIn 0.5s ease-out;
    }
    
    /* 스피너 스타일 */
    .stSpinner {
        background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    /* 라벨 스타일 */
    .stTextInput > label,
    .stTextArea > label {
        font-size: 1.1rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 0.5rem;
    }
    
    /* 애니메이션 */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* 모바일 반응형 */
    @media (max-width: 768px) {
        .main-container {
            margin: 1rem;
            padding: 1.5rem;
            border-radius: 16px;
        }
        
        .main-title {
            font-size: 2.5rem;
        }
        
        .subtitle {
            font-size: 1.1rem;
        }
    }
    
    /* 숨기기 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 컨테이너 여백 */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['en', 'ko', 'ja', 'zh'])
        lines = transcript.fetch()
        text = " ".join([line.text for line in lines])
        text = re.sub(r'\n+', '\n', text)
        return text
    except TranscriptsDisabled:
        return "자막이 비활성화된 영상입니다."
    except NoTranscriptFound:
        return "해당 영상에 자막이 없습니다."
    except Exception as e:
        return f"자막을 불러오는 중 오류가 발생했습니다: {str(e)}"

def split_text_by_length(text, max_chars):
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        if end < len(text):
            # 가능한 문장 끝 기준으로 자르기 (마침표, 줄바꿈 등)
            possible_cut = max(text.rfind('.', start, end),
                               text.rfind('\n', start, end),
                               text.rfind(' ', start, end))
            if possible_cut != -1 and possible_cut > start:
                end = possible_cut + 1
        chunks.append(text[start:end].strip())
        start = end
    return chunks

def summarize_text(text):
    """Claude AI를 사용하여 텍스트를 요약하는 함수"""
    try:
        prompt = f"""다음 YouTube 동영상의 스크립트를 한국어로 간결하고 핵심적으로 요약해주세요. 
        
주요 포인트:
1. 핵심 내용을 3-5개 불릿포인트로 정리
2. 중요한 키워드나 개념 강조
3. 전체적인 결론이나 메시지 포함

스크립트:
{text}

요약:"""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            temperature=0.3,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        summary = message.content[0].text.strip()
        return summary
        
    except Exception as e:
        return f"요약 중 오류가 발생했습니다: {str(e)}"

# 메인 콘텐츠 영역
with st.container():
    st.markdown("""
    <div class="main-container">
        <div class="header-container">
            <h1 class="main-title">🎬 YouTube 스크립트 추출기</h1>
            <p class="subtitle">Claude AI 기반 자동 요약 기능으로 더 스마트하게</p>
        </div>
    """, unsafe_allow_html=True)

    video_url_input = st.text_input(
        "🔗 YouTube 영상 URL을 입력하세요",
        placeholder="https://www.youtube.com/watch?v=...",
        help="YouTube 동영상의 전체 URL을 입력해주세요"
    )
    
    lang = st.selectbox(
        "🎯 스크립트 언어를 선택하세요",
        options=["한국어", "영어", "일본어", "중국어"],
        index=0,
        help="선택한 언어 기준으로 스크립트를 분할합니다"
    )
    
    if video_url_input:
        video_id_match = re.search(r"v=([\w-]+)", video_url_input)
        
        if video_id_match:
            video_id = video_id_match.group(1)
            with st.spinner("🔍 영상 자막을 불러오는 중입니다..."):
                script = get_transcript(video_id)
            
            if script.startswith("자막이") or script.startswith("해당") or "오류가 발생했습니다" in script:
                st.error(f"❌ {script}")
            else:
                st.success("✅ 스크립트를 성공적으로 불러왔습니다!")

                # 최대 글자 수 설정
                max_chars = 30000 if lang == "영어" else 10000
                
                chunks = split_text_by_length(script, max_chars)
                
                st.markdown(f"▶ 총 스크립트 길이: {len(script)}자, {len(chunks)}개 분할")
                
                for i, chunk in enumerate(chunks, 1):
                    st.text_area(f"📄 스크립트 분할본 {i}", value=chunk, height=250)
                    # Streamlit 1.21 이상부터 clipboard 지원 가능
                    if st.button(f"복사하기 - 분할본 {i}", key=f"copy_btn_{i}"):
                        st.experimental_set_query_params()  # 강제로 UI 새로고침용 (임시방편)
                        # 복사는 직접 영역에서 Ctrl+C 권장
                        st.info("텍스트 영역을 선택 후 Ctrl+C로 복사하세요.")
                
                # 요약 버튼 (기존 유지)
                if st.button("🧠 Claude AI로 스크립트 요약하기", help="Claude AI가 스크립트를 분석하여 핵심 내용을 요약합니다"):
                    with st.spinner("🤖 Claude AI가 스크립트를 분석하고 요약하는 중..."):
                        summary = summarize_text(script)
                    if summary.startswith("요약 중 오류가"):
                        st.error(f"❌ {summary}")
                    else:
                        st.success("✅ Claude AI 요약이 완료되었습니다!")
                        st.text_area(
                            "🧠 Claude AI 요약 결과",
                            value=summary,
                            height=200,
                            help="Claude AI가 생성한 스크립트 요약입니다"
                        )
        else:
            st.error("⚠️ 유효한 YouTube URL이 아닙니다. 올바른 형식으로 입력해주세요.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
# 푸터
st.markdown("""
<div style="text-align: center; margin-top: 3rem; color: rgba(255,255,255,0.7);">
    <p>💡 <strong>Tip:</strong> 더 정확한 요약을 위해 명확한 발음의 영상을 선택해주세요</p>
</div>
""", unsafe_allow_html=True)