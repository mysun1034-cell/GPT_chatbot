"""보고 전 5분: AI 의사결정 점검봇.

Streamlit과 OpenAI Chat Completions API를 이용해
사업 아이디어와 보고 내용을 여러 관점에서 검토한다.
"""

import os
from pathlib import Path
from typing import Final

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI


# -----------------------------------------------------------------------------
# 1. 기본 설정
# -----------------------------------------------------------------------------
load_dotenv(Path(__file__).resolve().parent / ".env")

st.set_page_config(
    page_title="보고 전 5분",
    page_icon="🔎",
    layout="centered",
)

API_MODEL: Final[str] = os.getenv("OPENAI_MODEL", "gpt-5.4-nano")
MAX_COMPLETION_TOKENS: Final[int] = 1_500

REVIEWERS: Final[dict[str, str]] = {
    "냉정한 대표": "사업성, 비용, 일정, 책임자, 숫자, 실행 가능성",
    "고객": "고객 문제, 실제 효용, 사용 불편, 신뢰, 가격 대비 가치",
    "투자자": "시장성, 경쟁 우위, 수익 구조, 확장성, 핵심 위험",
    "법무 담당자": "법적 근거, 사실과 가정의 구분, 책임, 동의, 계약, 증빙",
    "실무 책임자": "절차, 담당자, 일정, 자원, 선행 조건, 운영 실패 가능성",
}

INTENSITIES: Final[dict[str, str]] = {
    "균형 있게": "장점과 약점을 균형 있게 평가한다.",
    "냉정하게": "칭찬보다 약점, 누락, 실행 위험을 우선적으로 지적한다.",
    "레드팀": "반대편 입장에서 이 안건이 실패하거나 거절될 가장 강한 이유를 찾는다.",
}

EXAMPLES: Final[dict[str, tuple[str, str]]] = {
    "ERP 가격 전략": (
        "대표에게 ERP 가격 전략 보고",
        "우리 ERP는 회계와 AI 자동 검산 기능을 함께 제공하므로 "
        "경쟁사보다 높은 가격을 받을 수 있다고 생각합니다. "
        "기본 구독료는 월 11만 원 이상으로 책정하는 것이 적절합니다.",
    ),
    "AI 영어학습 경쟁력": (
        "AI 영어학습 서비스의 경쟁력 설명",
        "우리 영어학습 서비스는 AI를 활용하기 때문에 기존 영어교육 서비스보다 "
        "경쟁력이 있습니다. 학생마다 맞춤형 피드백을 줄 수 있다는 점을 강조하려고 합니다.",
    ),
    "신규 사업 제안": (
        "신규 사업 추진 여부 결정",
        "부산 지역 공공기관을 대상으로 시니어용 디지털 체험 장비를 판매하려고 합니다. "
        "고령화로 수요가 늘 것이므로 올해 안에 영업 인력을 먼저 채용해야 합니다.",
    ),
}


# -----------------------------------------------------------------------------
# 2. 함수: 프로그램이 반복해서 사용하는 작업
# -----------------------------------------------------------------------------
def initialize_state() -> None:
    """Streamlit 재실행 사이에 유지할 값을 최초 한 번만 만든다."""
    defaults = {
        "messages": [],
        "review_started": False,
        "total_tokens": 0,
        "report_purpose": "",
        "report_text": "",
        "reviewer": "냉정한 대표",
        "intensity": "냉정하게",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_review(clear_inputs: bool = False) -> None:
    """현재 분석 대화를 초기화한다."""
    st.session_state.messages = []
    st.session_state.review_started = False
    st.session_state.total_tokens = 0

    if clear_inputs:
        st.session_state.report_purpose = ""
        st.session_state.report_text = ""


def load_example(example_name: str) -> None:
    """선택한 예시를 입력창에 채운다."""
    purpose, report_text = EXAMPLES[example_name]
    reset_review(clear_inputs=False)
    st.session_state.report_purpose = purpose
    st.session_state.report_text = report_text


def build_system_prompt(reviewer: str, intensity: str) -> str:
    """사이드바 설정에 맞춰 AI의 역할과 출력 규칙을 만든다."""
    focus = REVIEWERS[reviewer]
    intensity_rule = INTENSITIES[intensity]

    return f"""
너는 기업의 사업 아이디어와 보고안을 검토하는 {reviewer}다.
가장 중요하게 볼 기준은 다음과 같다: {focus}.
검토 강도는 다음 원칙을 따른다: {intensity_rule}

사용자가 최초 검토를 요청하면 반드시 아래 8개 항목을 같은 순서로 작성하라.

## 1. 한 줄 판정
- 현재 상태를 '보고 가능', '보완 후 보고', '재검토 필요' 중 하나로 판정하고 한 문장으로 이유를 쓴다.

## 2. 핵심 주장
- 사용자가 실제로 주장하는 내용을 1~3개로 분리한다.

## 3. 설득력 있는 부분
- 근거가 있거나 방향이 타당한 부분만 구체적으로 적는다.

## 4. 부족한 근거
- 결론을 뒷받침하기 위해 필요한 수치, 비교자료, 사실 확인 사항을 적는다.

## 5. 숨은 가정
- 사용자가 사실처럼 전제했지만 아직 입증하지 않은 가정을 찾는다.

## 6. 가장 강한 반론
- {reviewer}가 실제 회의에서 제기할 법한 가장 어려운 반론을 작성한다.

## 7. 반드시 확인할 질문
- 의사결정 전에 답해야 할 질문을 중요도 순으로 최대 5개 제시한다.

## 8. 다음 행동
- 담당자가 바로 실행할 수 있도록 우선순위가 있는 행동을 최대 5개 제시한다.

공통 원칙:
- 사용자의 주장에 자동으로 동의하지 않는다.
- 사실, 추정, 의견을 구분한다.
- 제공되지 않은 숫자나 외부 사실을 만들어내지 않는다.
- 최신 자료나 외부 검증이 필요하면 '확인 필요'라고 명시한다.
- 추상적인 조언 대신 무엇을 조사하고, 비교하고, 결정해야 하는지 쓴다.
- 한국어로 명확하게 답한다.
- 최초 분석 이후의 후속 질문에는 앞선 대화를 기억하여 답한다.
- 사용자가 보고문, 발표문, 질문 목록 등으로 바꾸라고 하면 바로 사용할 수 있는 완성본을 준다.
""".strip()


def get_client() -> OpenAI:
    """환경변수의 API 키로 OpenAI 클라이언트를 만든다."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY가 없습니다. 프로젝트의 .env 파일에 API 키를 입력하세요."
        )
    return OpenAI(api_key=api_key)


def request_review() -> tuple[str, int]:
    """현재 대화 전체를 OpenAI에 보내고 답변과 토큰 수를 반환한다."""
    client = get_client()
    system_prompt = build_system_prompt(
        reviewer=st.session_state.reviewer,
        intensity=st.session_state.intensity,
    )

    api_messages = [
        {"role": "system", "content": system_prompt},
        *st.session_state.messages,
    ]

    response = client.chat.completions.create(
        model=API_MODEL,
        messages=api_messages,
        max_completion_tokens=MAX_COMPLETION_TOKENS,
    )

    answer = response.choices[0].message.content
    if not answer:
        raise RuntimeError("모델이 빈 답변을 반환했습니다. 다시 시도하세요.")

    used_tokens = 0
    if response.usage is not None:
        used_tokens = response.usage.total_tokens

    return answer, used_tokens


def make_initial_message(purpose: str, report_text: str) -> str:
    """최초 입력값을 AI가 분명하게 읽을 수 있는 메시지로 조립한다."""
    return f"""
다음 안건을 최초 검토해 주세요.

### 보고·의사결정 목적
{purpose}

### 검토할 내용
{report_text}
""".strip()


def export_markdown() -> str:
    """현재 대화를 마크다운 문서 형태로 변환한다."""
    lines = [
        "# 보고 전 5분 — AI 의사결정 검토 결과",
        "",
        f"- 검토 관점: {st.session_state.reviewer}",
        f"- 검토 강도: {st.session_state.intensity}",
        f"- 사용 모델: {API_MODEL}",
        "",
    ]

    for message in st.session_state.messages:
        speaker = "사용자" if message["role"] == "user" else "AI 검토자"
        lines.extend([f"## {speaker}", "", message["content"], ""])

    return "\n".join(lines)


# -----------------------------------------------------------------------------
# 3. 화면 구성
# -----------------------------------------------------------------------------
initialize_state()

st.title("🔎 보고 전 5분")
st.subheader("AI 의사결정 점검봇")
st.caption(
    "아이디어나 보고안을 입력하면 논리적 허점, 부족한 근거, 예상 반론과 다음 행동을 점검합니다."
)

with st.sidebar:
    st.header("검토 설정")

    st.selectbox(
        "검토자 관점",
        options=list(REVIEWERS.keys()),
        key="reviewer",
        on_change=reset_review,
    )

    st.selectbox(
        "검토 강도",
        options=list(INTENSITIES.keys()),
        key="intensity",
        on_change=reset_review,
    )

    st.divider()
    st.write(f"**모델:** `{API_MODEL}`")
    st.metric("누적 토큰", f"{st.session_state.total_tokens:,}")

    st.button(
        "새 검토 시작",
        on_click=reset_review,
        kwargs={"clear_inputs": True},
        use_container_width=True,
    )

    if st.session_state.review_started:
        st.download_button(
            "검토 결과 내려받기",
            data=export_markdown(),
            file_name="decision_review.md",
            mime="text/markdown",
            use_container_width=True,
        )


# 최초 분석 전: 보고 목적과 내용을 받는다.
if not st.session_state.review_started:
    st.info(
        "먼저 검토 관점을 고른 뒤, 보고 목적과 검토할 내용을 입력하세요. "
        "첫 분석이 끝나면 아래 채팅창에서 계속 질문할 수 있습니다."
    )

    st.write("#### 예시 불러오기")
    example_columns = st.columns(3)
    for column, example_name in zip(example_columns, EXAMPLES, strict=True):
        with column:
            st.button(
                example_name,
                on_click=load_example,
                args=(example_name,),
                use_container_width=True,
            )

    with st.form("initial_review_form"):
        purpose = st.text_input(
            "보고·의사결정 목적",
            placeholder="예: 대표에게 신규 ERP 가격 전략을 보고하고 승인을 받기",
            key="report_purpose",
        )

        report_text = st.text_area(
            "검토할 아이디어 또는 보고 내용",
            placeholder=(
                "주장, 예상 효과, 근거, 일정, 비용 등을 아는 범위에서 입력하세요. "
                "완성된 문서가 아니어도 됩니다."
            ),
            height=260,
            key="report_text",
        )

        submitted = st.form_submit_button(
            "검토 시작",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        clean_purpose = purpose.strip()
        clean_report_text = report_text.strip()

        if not clean_purpose or not clean_report_text:
            st.warning("보고 목적과 검토할 내용을 모두 입력하세요.")
        else:
            initial_message = make_initial_message(clean_purpose, clean_report_text)
            st.session_state.messages.append(
                {"role": "user", "content": initial_message}
            )

            try:
                with st.spinner("의사결정 관점에서 검토하고 있습니다..."):
                    answer, used_tokens = request_review()
            except Exception as error:  # 수업용 앱에서는 오류를 사용자에게 보여 준다.
                st.session_state.messages.pop()
                st.error(f"API 요청에 실패했습니다: {error}")
            else:
                st.session_state.messages.append(
                    {"role": "assistant", "content": answer}
                )
                st.session_state.total_tokens += used_tokens
                st.session_state.review_started = True
                st.rerun()


# 최초 분석 후: 저장된 대화를 그리고 후속 질문을 받는다.
else:
    st.success(
        f"현재 **{st.session_state.reviewer}** 관점에서 "
        f"**{st.session_state.intensity}** 검토 중입니다."
    )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    follow_up = st.chat_input(
        "예: 대표에게 보고할 30초 문장으로 바꿔줘"
    )

    if follow_up:
        st.session_state.messages.append(
            {"role": "user", "content": follow_up}
        )

        try:
            with st.spinner("후속 요청을 반영하고 있습니다..."):
                answer, used_tokens = request_review()
        except Exception as error:
            st.session_state.messages.pop()
            st.error(f"API 요청에 실패했습니다: {error}")
        else:
            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )
            st.session_state.total_tokens += used_tokens
            st.rerun()
