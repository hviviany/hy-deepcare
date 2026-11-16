import streamlit as st
from google import genai
from google.genai import types
from datetime import datetime

# 1. 웹페이지 설정 (프리뷰 사이트의 차분한 톤앤매너 반영)
st.set_page_config(page_title="DeepCare - 피해자의 첫 대응을 돕는 AI 프로그램", page_icon="🛡️", layout="wide")

st.title("🛡️ DeepCare")
st.caption("한양대학교 미래지능연결 IC-PBL · 딥페이크 성범죄 피해자의 초기 대응을 돕는 맞춤형 지원 프로그램")
st.info("🔒 **안심 이용 안내**: 실제 피해 영상·사진, 실명, 연락처 등 민감한 개인정보는 입력하지 마세요. DeepCare는 수사·법률 판단을 대체하지 않으며 전문 기관 연결 전 초기 준비를 돕습니다.")

# 2. 시스템 프롬프트 (PPT 문제 정의 및 상담 원칙 완벽 반영)
SYSTEM_PROMPT = """
당신은 딥페이크 성범죄 피해자의 초기 대응을 돕는 맞춤형 지원 AI 'DeepCare'입니다.
당신의 역할은 경찰(112)이나 중앙디지털성범죄피해자지원센터(d4u.stop.or.kr) 같은 공식 기관을 대체하는 것이 아니라, 피해자가 공식 지원을 요청하기 전 심리적 안정을 찾고 필요한 증거와 절차를 준비하도록 돕는 '안전한 다리'입니다.

[핵심 상담 원칙]
1. 진위 입증 부담 덜어주기 & 비난 금지: 피해자에게 "가짜임을 증명하라"고 압박하거나 책임을 묻지 마세요. "당신의 잘못이 아닙니다. 조작된 영상으로 인한 고통은 명백한 피해입니다"라고 따뜻하게 수용하세요.
2. 단계별 호흡: 한 번에 너무 많은 법률 용어나 절차를 쏟아내지 말고, 3~4문장 내외로 핵심만 차분하게 안내한 뒤 다음 단계로 넘어갈지 물어보세요.
3. 2차 트라우마 방지: 증거를 모을 때 피해자가 직접 영상을 반복해서 보며 괴로워하지 않도록 주의시켜 주세요.

[상황별 대응 프로토콜]
- 초기 패닉/불안 호소 시: 절차 설명보다 먼저 심호흡(4초 들이마시고, 4초 멈추고, 6초 내쉬기)이나 그라운딩 기법(주변 사물 3가지 확인)으로 진정시키세요.
- 협박·금전 요구·신체 위험이 있는 경우: 무엇보다 안전이 최우선임을 알리고 즉시 112 경찰 신고 및 1366 여성긴급전화를 안내하세요.
- 증거 수집 질문 시: 4가지 핵심 증거(① 게시물 URL, ② 게시 시점, ③ 관련 계정/ID, ④ 협박·유포 관련 메시지)를 화면 전체 캡처로 남기도록 안내하세요.
- 기관 연계 안내 시:
  * 긴급 신고·수사: 경찰청 ☎ 112
  * 삭제 지원·유포 모니터링·법률·의료 연계(무료): 중앙디지털성범죄피해자지원센터(d4u.stop.or.kr / ☎ 02-735-8994)
  * 24시간 위기·심리 상담: 여성긴급전화 ☎ 1366 / 자살예방상담전화 ☎ 109
"""

# 3. 사이드바 설정 및 긴급 연락처
with st.sidebar:
    st.header("⚙️ DeepCare 설정")
    api_key = st.text_input("Gemini API Key 입력", type="password").strip()
    
    st.markdown("---")
    st.markdown("### 🚨 즉시 도움 받을 수 있는 곳")
    st.markdown("- **긴급 신고 / 수사**: `112` (경찰청)")
    st.markdown("- **삭제 지원 / 통합 연계**: `02-735-8994`\n  *(중앙디지털성범죄피해자지원센터)*")
    st.markdown("- **24시간 여성긴급전화**: `1366`")
    st.markdown("- **자살예방상담전화**: `109`")
    st.markdown("---")
    if st.button("🔄 전체 내용 초기화", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "ai_summary" not in st.session_state:
    st.session_state.ai_summary = ""

# 모델 호출 보조 함수 (503 혼잡 자동 우회)
def call_gemini_stream(api_key, contents):
    models_to_try = ["gemini-3.8-flash", "gemini-3.8-flash-lite", "gemini-2.5-flash-lite"]
    for model_name in models_to_try:
        try:
            with genai.Client(api_key=api_key) as client:
                stream = client.models.generate_content_stream(
                    model=model_name,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.5,
                    ),
                )
                for chunk in stream:
                    if chunk.text:
                        yield chunk.text
                return
        except Exception as e:
            last_err = e
            continue
    raise RuntimeError(f"서버 응답 지연: {last_err}")

# 4. PPT 8장 구조를 반영한 3개 핵심 탭 구성
tab1, tab2, tab3 = st.tabs([
    "💬 1. AI 초기 대응 상담",
    "📋 2. 증거 정리 & 초기 대응 요약서",
    "🧭 3. 기관 연결 및 대응 가이드"
])

# ==========================================
# TAB 1: AI 초기 대응 상담
# ==========================================
with tab1:
    st.subheader("지금의 마음과 상황을 편하게 들려주세요")
    
    # 고정 첫 인사말
    with st.chat_message("assistant"):
        st.markdown(
            "안녕하세요, **DeepCare**입니다. 갑작스러운 일로 많이 놀라고 막막하셨을 텐데, "
            "이곳은 당신을 의심하거나 탓하지 않는 안전한 공간입니다. "
            "지금 가장 불안한 점이나 겪고 계신 상황을 편하신 만큼만 말씀해 주세요."
        )

    # 이전 대화 출력
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 채팅 입력 처리
    if prompt := st.chat_input("현재 상황이나 고민을 입력해 주세요 (예: 단톡방에 제 합성 영상이 돌고 있대요...)"):
        if not api_key:
            st.warning("👈 왼쪽 사이드바에 Gemini API Key를 먼저 입력해 주세요.")
            st.stop()

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        history = [
            types.Content(
                role="user" if m["role"] == "user" else "model",
                parts=[types.Part.from_text(text=m["content"])],
            )
            for m in st.session_state.messages
        ]

        with st.chat_message("assistant"):
            try:
                full_text = st.write_stream(call_gemini_stream(api_key, history))
                st.session_state.messages.append({"role": "assistant", "content": full_text})
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")

# ==========================================
# TAB 2: 증거 정리 체크리스트 & 초기 대응 요약서 (PPT 8장 구현)
# ==========================================
with tab2:
    st.subheader("공식 상담·신고 전 [초기 대응 요약서] 만들기")
    st.caption("혼란스러운 상황에서 빠뜨리기 쉬운 증거를 점검하고, 112 및 디성센터 제출용 요약서를 정리합니다.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 1 / 3 · 현재 상황 확인")
        q_uploaded = st.radio(
            "내 영상(이미지)이 온라인에 올라와 있나요?",
            ["네, 확인했어요", "아니요 (유포 협박만 받음)", "잘 모르겠어요"],
            index=0
        )
        q_threat = st.radio(
            "협박, 금전 요구, 또는 긴급한 신체적 위험이 있나요?",
            ["아니요", "네, 협박이나 긴급 위험이 있어요"],
            index=0
        )
        q_platform = st.text_input("발견된 플랫폼 / 경로 (예: 텔레그램, 인스타그램, 오픈채팅 등)", placeholder="예: 인스타그램 릴스 및 DM")

    with col2:
        st.markdown("#### 2 / 3 · 증거 정리 체크리스트")
        st.caption("2차 피해를 막기 위해 영상을 직접 반복 시청하지 마시고, 화면 캡처 위주로 확인해 주세요.")
        c_url = st.checkbox("게시물 URL (링크 주소) 확보", value=True)
        c_time = st.checkbox("게시 시점 (날짜·시간이 보이게 전체 화면 캡처)", value=True)
        c_account = st.checkbox("관련 계정 (작성자·유포자 ID, 프로필 링크)")
        c_msg = st.checkbox("관련 메시지 (협박 내용, 제보받은 대화 내역)")

        checked_count = sum([c_url, c_time, c_account, c_msg])
        st.progress(checked_count / 4)
        st.write(f"**확인됨 {checked_count}개** · **미확인 {4 - checked_count}개**")

    st.markdown("---")
    st.markdown("#### 3 / 3 · 초기 대응 요약서 생성")

    # 준비된 항목 / 미확인 항목 정리
    items_map = {
        "게시물 URL": c_url,
        "게시 시점": c_time,
        "관련 계정": c_account,
        "관련 메시지": c_msg,
    }
    confirmed_list = [k for k, v in items_map.items() if v]
    missing_list = [k for k, v in items_map.items() if not v]

    urgent_action = "🚨 **[최우선] 협박/긴급 위험이 있으므로 즉시 112 경찰 신고 및 1366 상담 연결**" if "네" in q_threat else "1️⃣ **중앙디지털성범죄피해자지원센터(02-735-8994 / d4u.stop.or.kr) 삭제 및 상담 신청**"
    second_action = f"2️⃣ **미확인 증거 보완하기**: {', '.join(missing_list)}" if missing_list else "2️⃣ **모든 기본 증거 확보 완료 — 즉시 경찰서(112) 및 디성센터 제출 가능**"

    summary_text = f"""[DeepCare 초기 대응 요약서]
작성 일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}
--------------------------------------------------
1. 피해 상황 요약
- 온라인 유포 여부: {q_uploaded}
- 협박/긴급 위험 여부: {q_threat}
- 발견 경로(플랫폼): {q_platform if q_platform else '미입력'}

2. 필요한 다음 행동
- {urgent_action.replace('**', '')}
- {second_action.replace('**', '')}

3. 공식 상담·신고 준비자료 현황 ({checked_count}/4 완료)
- 확보 완료: {', '.join(confirmed_list) if confirmed_list else '없음'}
- 추가 보완 필요: {', '.join(missing_list) if missing_list else '없음'}
--------------------------------------------------
※ 본 요약서는 피해자의 초기 대응 준비를 돕기 위해 작성되었으며, 실제 피해 원본 파일은 포함하지 않습니다.
"""

    st.text_area("생성된 초기 대응 요약서 미리보기", value=summary_text, height=270)

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.download_button(
            label="📥 초기 대응 요약서 저장 (.txt)",
            data=summary_text,
            file_name=f"DeepCare_초기대응요약서_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    with btn_col2:
        if st.button("✨ AI 맞춤 대응 조언 추가 생성", use_container_width=True):
            if not api_key:
                st.warning("👈 왼쪽 사이드바에 Gemini API Key를 먼저 입력해 주세요.")
            else:
                with st.spinner("현재 체크리스트 상태를 바탕으로 맞춤 조언을 생성 중입니다..."):
                    prompt_for_summary = f"아래 피해자의 현재 초기 대응 요약서를 보고, 지금 당장 가장 안전하게 실행할 행동 2가지만 따뜻하고 명확하게 조언해 주세요.\n\n{summary_text}"
                    try:
                        with genai.Client(api_key=api_key) as client:
                            res = client.models.generate_content(
                                model="gemini-3.8-flash",
                                contents=prompt_for_summary,
                                config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, temperature=0.4),
                            )
                        st.session_state.ai_summary = res.text
                    except Exception as e:
                        st.error(f"생성 오류: {e}")

    if st.session_state.ai_summary:
        st.success("**🤖 DeepCare AI 맞춤 가이드**")
        st.markdown(st.session_state.ai_summary)

# ==========================================
# TAB 3: 기관 연결 및 대응 가이드
# ==========================================
with tab3:
    st.subheader("작은 단계부터, 전문 기관과 함께")
    st.markdown("""
    * **1단계 · 혼자 감당하지 않기**: 영상 삭제만으로 재유포 불안이 끝나지 않을 수 있습니다. 국가 전문 기관의 무료 지원을 꼭 받으세요.
    * **2단계 · 증거 보전 원칙**: 원본 영상을 다운로드해 소장하기보다, **유포 사이트 주소(URL)와 날짜·작성자 ID가 나온 전체 화면 캡처**를 남기는 것이 안전합니다.
    * **3단계 · 공식 지원 기관 연결**:
      * **중앙디지털성범죄피해자지원센터 (`d4u.stop.or.kr` / ☎ 02-735-8994)**: 불법 영상물 삭제 지원, 유포 모니터링, 수사·법률·의료 지원 연계 (전액 무료)
      * **경찰청 사이버범죄 신고 (`112` / `ecrm.police.go.kr`)**: 가해자 추적 및 수사 의뢰
      * **여성긴급전화 (`1366`)**: 24시간 초기 심리 상담 및 긴급 보호 연계
    """)