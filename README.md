# 보고 전 5분 — AI 의사결정 점검봇

사업 아이디어나 보고안을 입력하면 선택한 의사결정자의 관점에서 다음을 점검하는 Streamlit 챗봇입니다.

- 한 줄 판정
- 핵심 주장
- 설득력 있는 부분
- 부족한 근거
- 숨은 가정
- 가장 강한 반론
- 반드시 확인할 질문
- 다음 행동

## 1. 가상환경 만들기

### Ubuntu / WSL

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 2. 패키지 설치

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 3. API 키 설정

`env.example`을 `.env`로 복사합니다.

### Ubuntu / WSL

```bash
cp env.example .env
```

### Windows PowerShell

```powershell
Copy-Item env.example .env
```

그다음 `.env`를 열어 실제 API 키를 입력합니다.

```env
OPENAI_API_KEY=sk-실제_API_키
OPENAI_MODEL=gpt-5.4-nano
```

## 4. 실행

점검봇:

```bash
streamlit run app.py
```

수업 그래프 · 과목 퀴즈 (오늘 작업, `parse` + Pydantic):

```bash
streamlit run lecture_quiz_app.py
```

브라우저가 자동으로 열리지 않으면 터미널에 표시된 로컬 주소로 접속합니다.

제목 아래 과목 단추 8개(Streamlit · 머신러닝 · 딥러닝 · 미니프로젝트 · Spring AI · PyTorch NLP · LLM 핵심기술 · LLM API)가 보여야 합니다. 안 보이면 **전체 맵으로**를 누르거나 페이지를 새로고침합니다.

| 파일 | 내용 |
|---|---|
| `lecture_quiz_app.py` | vis.js 그래프 + 큰 칸 + 퀴즈 3문제 (`chat.completions.parse`) |
| `curriculum.py` / `curriculum_more.py` | 수업 31개, 항목 163개 |
| `curriculum_code.py` / `curriculum_code_more.py` | 항목마다 줄 주석 예제 코드 |
| `quiz.py` | 터미널 퀴즈 |
| `structured.ipynb` · `tools.ipynb` | Day 2 구조화 출력 · 도구 호출 |
| `day02/tool_chat.py` | 날씨·계산 도구 챗 |
| `수업정리/` | 강사 코드 정리와 슬라이드 풀이 |

## 핵심 학습 포인트

1. `st.session_state.messages`가 사용자와 AI의 대화를 기억합니다.
2. `build_system_prompt()`가 검토자 관점과 강도에 따라 AI 역할을 만듭니다.
3. `request_review()`가 시스템 메시지와 누적 대화를 OpenAI에 전달합니다.
4. 최초에는 입력 폼을 보여 주고, 분석 후에는 `st.chat_input()`으로 후속 대화를 받습니다.
5. `.env`에 API 키를 보관하고 `.gitignore`로 Git 업로드를 막습니다.
