1. 프로젝트 파일
전체 프로젝트 ZIP 다운로드
핵심 코드 app.py
실행 설명서 README.md

압축파일에는 다음 파일이 들어 있습니다.

report_review_bot/
├── app.py              # Streamlit 챗봇 본체
├── requirements.txt    # 필요한 라이브러리 목록
├── .env.example        # API 키 입력 예시
├── .gitignore          # API 키의 Git 업로드 방지
└── README.md           # 설치 및 실행 방법

문법 검사도 통과시켰습니다.

2. 이번에 구현한 기능

단순히 기존 챗봇의 시스템 메시지만 바꾼 것이 아닙니다.

기능	                    동작
검토자 관점 선택	    대표, 고객, 투자자, 법무 담당자, 실무 책임자
검토 강도 선택	        균형 있게, 냉정하게, 레드팀
보고 목적 입력	        무엇을 결정받으려는 보고인지 입력
보고 내용 입력	        아이디어, 주장, 근거 등을 자유롭게 입력
구조화된 분석	        8개 항목으로 고정하여 검토
후속 대화	            앞선 분석을 기억하고 추가 질문에 답변
대화 초기화	            새로운 안건으로 다시 시작
토큰 누적 표시	        API 사용 토큰 확인
결과 저장	            전체 검토 결과를 Markdown 파일로 내려받기
예시 불러오기	        ERP 가격, AI 영어학습, 신규 사업 예시

구조화된 분석 항목은 다음과 같습니다.

1. 한 줄 판정
2. 핵심 주장
3. 설득력 있는 부분
4. 부족한 근거
5. 숨은 가정
6. 가장 강한 반론
7. 반드시 확인할 질문
8. 다음 행동

수업에서 배운 코드를 설명하기 쉽도록 client.chat.completions.create() 방식을 유지했습니다. OpenAI는 신규 프로젝트에 Responses API를 우선 권장하지만 Chat Completions도 계속 지원하고 있으며, 현재 사용한 gpt-5.4-nano도 공식 모델입니다. max_completion_tokens도 현재 Chat Completions에서 사용하는 올바른 파라미터입니다.

3. WSL·Ubuntu에서 실행하기

압축을 푼 뒤 VS Code 터미널에서 프로젝트 폴더로 이동합니다.

cd report_review_bot
가상환경 만들기

현재 수업용 가상환경이 이미 있다면 그 환경을 사용해도 됩니다. 새로 만든다면 다음 명령어를 실행합니다.

python3 -m venv .venv
source .venv/bin/activate

터미널 앞에 (.venv)가 표시되면 활성화된 것입니다.

(.venv) user@computer:~/report_review_bot$
라이브러리 설치
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

실제로는 다음 세 라이브러리가 설치됩니다.

streamlit
openai
python-dotenv
4. API 키 설정

예시 파일을 실제 .env 파일로 복사합니다.

cp .env.example .env

그다음 VS Code에서 .env 파일을 열고 다음처럼 입력합니다.

OPENAI_API_KEY=sk-실제_API_키
OPENAI_MODEL=gpt-5.4-nano

주의할 점은 다음과 같습니다.

OPENAI_API_KEY="sk-실제_API_키"

따옴표가 있어도 대체로 작동하지만, 처음에는 다음처럼 따옴표 없이 쓰는 편이 단순합니다.

OPENAI_API_KEY=sk-실제_API_키

.gitignore에는 이미 다음 내용이 들어 있습니다.

.env

따라서 실수로 API 키를 GitHub에 올리는 것을 방지합니다.

5. 실행
streamlit run app.py

정상 실행되면 터미널에 다음과 비슷하게 나옵니다.

You can now view your Streamlit app in your browser.


Local URL: http://localhost:8501
Network URL: http://172.xx.xx.xx:8501

브라우저가 자동으로 열리지 않으면 Local URL로 접속합니다.

http://localhost:8501

Streamlit의 st.chat_input()과 st.chat_message()는 채팅 입력창과 메시지 화면을 만들고, st.session_state는 앱이 재실행되어도 현재 세션의 대화 기록을 유지하는 데 사용됩니다.

6. 실제 사용 순서

처음 화면에서는 다음처럼 설정합니다.

검토자 관점: 냉정한 대표
검토 강도: 레드팀

보고 목적:

대표에게 AI 영어학습 서비스의 경쟁력을 설명하고 개발 방향을 승인받기

검토할 내용:

우리 영어학습 서비스는 AI를 활용하기 때문에 기존 영어교육 서비스보다
경쟁력이 있습니다. 학생마다 맞춤형 피드백을 줄 수 있다는 점을 강조하려고 합니다.

검토 시작을 누르면 AI는 대략 다음 문제를 지적하게 됩니다.

AI를 사용한다는 사실만으로 경쟁력이 입증되는 것은 아니다.


확인할 사항:
- 경쟁 서비스도 AI를 사용하고 있지 않은가?
- 맞춤형 피드백이 실제로 어떤 학습 문제를 해결하는가?
- 학습 효과나 지속률을 보여 주는 수치가 있는가?
- 교사 또는 보호자의 업무가 얼마나 줄어드는가?

분석이 끝나면 아래 채팅창에서 다음처럼 계속 요청합니다.

이 분석을 바탕으로 대표에게 보고할 30초 문장으로 바꿔줘.

그다음:

대표가 제기할 질문 5개와 답변을 만들어줘.

그다음:

근거가 확인된 내용과 아직 가정인 내용을 표로 구분해줘.

이렇게 하면 단순히 한 번 답하는 챗봇이 아니라 의사결정안을 반복적으로 개선하는 멀티턴 도구가 됩니다.

7. 핵심 코드 구조
① 상태 초기화
def initialize_state() -> None:
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

이 함수는 챗봇이 기억해야 할 값을 최초 한 번만 만듭니다.

messages
→ 사용자와 AI의 대화 기록


review_started
→ 최초 분석이 시작됐는지 여부


total_tokens
→ 누적 토큰 수


report_purpose
→ 보고 목적


report_text
→ 검토할 내용


reviewer
→ 선택한 검토자


intensity
→ 선택한 검토 강도
② 선택값에 따라 시스템 프롬프트 생성
def build_system_prompt(reviewer: str, intensity: str) -> str:

기존 코드에는 시스템 메시지가 고정되어 있었습니다.

{
    "role": "system",
    "content": "너는 친절한 대화 봇이야."
}

이번 코드에서는 사용자가 선택한 설정에 따라 시스템 메시지가 달라집니다.

system_prompt = build_system_prompt(
    reviewer=st.session_state.reviewer,
    intensity=st.session_state.intensity,
)

예를 들어:

검토자: 냉정한 대표
강도: 레드팀

을 선택하면 AI는 다음과 같은 역할을 받습니다.

너는 기업의 사업 아이디어와 보고안을 검토하는 냉정한 대표다.
비용, 일정, 책임자, 숫자, 실행 가능성을 중요하게 보라.
반대편 입장에서 이 안건이 실패하거나 거절될 가장 강한 이유를 찾아라.

따라서 같은 보고 내용도 관점에 따라 다른 결과가 나옵니다.

③ OpenAI API 호출

핵심은 여전히 수업 코드와 같습니다.

response = client.chat.completions.create(
    model=API_MODEL,
    messages=api_messages,
    max_completion_tokens=MAX_COMPLETION_TOKENS,
)

다만 api_messages 앞에 방금 만든 시스템 프롬프트를 붙였습니다.

api_messages = [
    {"role": "system", "content": system_prompt},
    *st.session_state.messages,
]

별표 *는 리스트의 내용을 펼치는 문법입니다.

예를 들어:

messages = [
    {"role": "user", "content": "내 보고서를 검토해줘"}
]

라면 다음과 같이 합쳐집니다.

api_messages = [
    {"role": "system", "content": "너는 냉정한 대표다."},
    {"role": "user", "content": "내 보고서를 검토해줘"},
]
④ 최초 분석과 후속 대화를 구분
if not st.session_state.review_started:

아직 분석을 시작하지 않았다면:

보고 목적 입력
검토 내용 입력
검토 시작 버튼

을 보여 줍니다.

분석을 시작한 뒤에는:

else:

다음 화면으로 바뀝니다.

기존 대화 출력
후속 질문 입력창

그래서 하나의 앱이 두 가지 화면 상태를 갖습니다.

상태 1: 최초 검토 입력 화면
상태 2: 후속 대화 화면

이 부분이 기존 기본 챗봇보다 한 단계 발전한 핵심입니다.