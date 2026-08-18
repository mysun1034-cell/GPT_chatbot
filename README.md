# 수업 그래프 · 과목 퀴즈

수업 슬라이드를 마인드맵처럼 펼치고, 칸을 고르면 설명·예제 코드·객관식 퀴즈가 나오는 Streamlit 앱입니다.

오늘 작업:

- 수업 슬라이드 25개를 트리에 넣었다. 전체 **8과목 · 31수업 · 163항목**.
- 그래프는 클릭하면 그 층만 남는다. 노드는 제자리에 고정해서 화면 밖으로 안 나간다.
- 마우스가 잘 안 잡혀서 제목 아래 **큰 과목 단추**와 왼쪽 **큰 라디오**를 같이 두었다.
- 퀴즈는 `chat.completions.parse` + Pydantic `Quiz` 로 문항 모양을 고정한다. 보기는 4개, 정답은 1~4.
- 항목마다 줄마다 한글 주석이 달린 예제 코드가 붙는다.

## 과목

| 과목 | 수업 |
|---|---|
| Streamlit | 5/21 위젯·대시보드, 5/22 session_state·배포 |
| 머신러닝 | k-NN → 회귀·규제 → 분류 지표 → 트리·CV → K-Means·PCA |
| 딥러닝 | 퍼셉트론 → 역전파 → Dropout → CNN → 전이학습·탐지 |
| 미니프로젝트 | Git 협업, EDA·전처리, 충돌·리뷰 |
| Spring AI | ChatClient부터 스트리밍·통합까지 6일 |
| PyTorch NLP | 텐서·루프 → 텍스트를 숫자로 → RNN → LSTM·GRU |
| LLM 핵심기술 | 어텐션, 셀프 어텐션, BERT/GPT, 생성 디코딩 |
| LLM API | 무상태 대화, 구조화 출력, 도구 호출 |

## 실행

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item env.example .env
```

`.env`에 키를 넣는다.

```env
OPENAI_API_KEY=sk-실제_API_키
```

```powershell
streamlit run lecture_quiz_app.py
```

### Ubuntu / WSL

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp env.example .env
streamlit run lecture_quiz_app.py
```

브라우저가 안 열리면 터미널에 나온 주소로 들어간다. 제목 아래 과목 단추 8개가 보여야 한다. 안 보이면 **전체 맵으로**를 누르거나 새로고침한다.

## 쓰는 법

1. 위 단추나 청록 상자에서 과목을 고른다.
2. 그래프에서 수업을 누르면 항목이 펼쳐진다.
3. 항목을 누르면 설명과 예제 코드가 나온다.
4. **퀴즈 3문제 만들기** → 고르고 **채점**.

`전체 맵으로`는 과목 8개가 다시 둘러싼다. `한 단계 위`는 항목 → 수업 → 과목 → 전체 맵이다.

## 파일

| 파일 | 하는 일 |
|---|---|
| `lecture_quiz_app.py` | 그래프 + 단추 + 라디오 + 퀴즈 |
| `curriculum.py` | LLM 핵심기술 · LLM API |
| `curriculum_more.py` | Streamlit · ML · DL · 미니 · Spring AI · PyTorch NLP |
| `curriculum_code.py` / `curriculum_code_more.py` | 항목마다 줄 주석 예제 |
| `quiz.py` | 터미널 퀴즈 |
| `structured.ipynb` | `json_object` → `json_schema`+`strict` → Pydantic `parse` |
| `tools.ipynb` | 도구 호출 |
| `day02/tool_chat.py` | 날씨·계산 도구 챗 |
| `수업정리/` | 강사 코드와 슬라이드 쉽게 풀이 |
| `app.py` | 예전에 만든 의사결정 점검봇 |

퀴즈 핵심은 이 모양이다.

```python
class Question(BaseModel):
    question: str
    choices: List[str]
    answer: int
    explanation: str

class Quiz(BaseModel):
    questions: List[Question]

r = client.chat.completions.parse(..., response_format=Quiz)
```

모델은 확률만 만들고, 문항 칸은 클래스가 계약한다. 키가 흔들리지 않아서 채점이 된다.

## 주의

- API 키는 `.env` / `env`에만 둔다. git에 올리지 않는다.
- 그래프 라이브러리는 `streamlit-agraph` (vis.js)다.
