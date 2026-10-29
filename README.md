# im-a-monkey

<p align="center"><img src="assets/logo.svg" alt="im-a-monkey 로고: 눈이 몰린 원숭이" width="160"></p>

한국어 글을 원숭이도 알아듣게, 그리고 AI가 아니라 영장류가 쓴 글처럼 쓰게 돕는 Claude Code 플러그인이에요. 짧게 쓰는 게 아니라 따라가기 쉽게 쓰는 게 목표예요.

## 예시

스킬마다 고치기 전과 후를 하나씩 보여 드려요.

**monkey-human**: 번역투와 AI 상투어를 걷어 내요. 뜻은 그대로 둬요.

<!-- monkey-lint: off -->
```text
전: 해당 기능은 사용자들에게 있어 매우 중요한 역할을 수행하고 있다고 할 수 있습니다.
```
<!-- monkey-lint: on -->

```text
후: 이 기능은 사용자에게 아주 중요해요.
```

**monkey-clear**: 식별자가 섞인 압축 설명을 결론부터, 한 문장에 한 사실씩 풀어요.

<!-- monkey-lint: off -->
```text
전: retry_max=0이라 sync_job 실패 시 재시도 X → 큐 적체, 아침 리포트 지연.
```
<!-- monkey-lint: on -->

```text
후: 아침 리포트가 늦어진 건 재시도가 꺼져 있어서예요.
    sync_job이 한 번 실패하면 다시 돌지 않아요(retry_max=0).
    그 사이 큐에 작업이 쌓여요.
```

**monkey-visual**: 그림 아래에 독자가 품을 질문을 캡션으로 달아요.

<!-- monkey-lint: off -->
전: 캡션이 없어서 무엇을 봐야 할지 몰라요.

```mermaid
flowchart LR
  주문 --> 결제 --> 배송
```
<!-- monkey-lint: on -->

후:

```mermaid
flowchart LR
  주문 --> 결제 --> 배송
```
그림 1. 결제가 실패하면 주문은 어디서 멈출까요?

**monkey-doc**: 요청을 보고 문서 유형과 블록 순서를 먼저 정해요.

```text
요청: 지난주 로그인 장애를 팀에 공유할 글을 써 줘.
후:  유형 report, 200~800 어절, 맨 위에 영향·원인·조치 세 줄 요약
     블록 순서: 결론 → 흐름 그림 → 예시 → 위험 → 요청 → 열린 질문
```

## 설치

```
/plugin marketplace add polyglot-k/im-a-monkey
/plugin install im-a-monkey@im-a-monkey
```

설치하면 세션을 시작할 때 말투 규칙이 자동으로 적용돼요.

## 스킬 지도

어느 스킬이 맞는지 모르겠으면 `monkey`에게 물어보세요.

| 하고 싶은 일 | 스킬 |
|---|---|
| 글에서 AI 티와 번역투를 찾고 고쳐요 | monkey-human |
| 개념이나 코드, 장애 원인을 쉽게 풀어요 | monkey-clear |
| 말투를 바꾸거나 페르소나를 꺼요 | monkey-voice |
| 흐름이나 구조를 그림과 표로 보여 줘요 | monkey-visual |
| 공유할 문서를 쓰거나 구조를 다시 잡아요 | monkey-doc |
| 받은 지적을 규칙으로 남겨요 | monkey-learn |
| 입구, 어떤 스킬을 쓸지 안내해요 | monkey |

## 말투 바꾸기와 끄기

기본 말투는 해요체예요. 대화 중에 "반말로 해"라고 말하면 monkey-voice가 설정을 바꿔요. 고를 수 있는 값은 `haeyo`, `banmal`, `hapnida`, `off`예요.

`off`로 바꾸면 페르소나가 꺼져요. 한 세션만 바꾸려면 환경 변수 `IM_A_MONKEY_VOICE`를 쓰세요. 이 값이 설정 파일보다 먼저 적용돼요.

```
IM_A_MONKEY_VOICE=banmal claude
```

## 내 규칙 두기

설정과 개인 규칙은 한 폴더에 모여요. 위치는 아래 명령으로 확인해요.

```
python3 hooks/config.py path
```

`$XDG_CONFIG_HOME/im-a-monkey/`가 있으면 그곳이고, 없으면 `~/.config/im-a-monkey/`예요. 안에는 `config.json`(말투), `overlay/antipatterns.md`(내가 추가한 안티패턴), `overlay/types/*.md`(내가 추가한 문서 유형)가 들어가요.

## 스크립트만 쓰기

스크립트는 Python 3.9 이상만 있으면 돌아가요. 외부 패키지는 필요 없어요.

| 스크립트 | 하는 일 | 예 |
|---|---|---|
| `lint.py` | 안티패턴을 찾아요 | `python3 scripts/lint.py doc.md --type report` |
| `rhythm.py` | 문장 길이의 단조로움을 재요 | `python3 scripts/rhythm.py doc.md` |
| `preserve.py` | 고치기 전후로 숫자, 코드, 링크가 그대로인지 봐요 | `python3 scripts/preserve.py old.md new.md` |
| `visual.py` | 그림과 표 쓰임을 점검해요 | `python3 scripts/visual.py doc.md` |
| `coderef.py` | 글에 적은 코드 경로가 저장소에 있는지 확인해요 | `python3 scripts/coderef.py doc.md --repo .` |

`--json`을 붙이면 결과를 JSON으로 받아요.

## 평가

스킬이 기준선보다 나은지는 `evals/judge.py`로 비교해요. 사례를 만들고 돌리는 방법은 [evals/README.md](evals/README.md)에 있어요.

## 기여

- 안티패턴은 `catalog/antipatterns.md`에 ID를 붙여 적어요. ID는 분류 글자와 두 자리 숫자예요(`S01`, `A12`). 한 번 쓴 ID는 다른 항목에 다시 쓰지 않고, 목차에도 함께 올려요.
- 예문은 직접 새로 써요. 다른 글에서 가져오지 않아요.
- 고친 뒤에는 저장소 루트에서 테스트를 돌려요.

```
python3 -m unittest discover -s tests -v
```

라이선스는 [LICENSE](LICENSE)를 보세요.
