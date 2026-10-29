# 스킬 행동 평가

스킬이 정말 기준선보다 나은지 확인하는 도구예요. 같은 요청을 플러그인 없이, 그리고 플러그인을 켜고 각각 돌린 뒤 Claude가 두 답을 비교해요. 판정은 순서를 바꿔 두 번 해서 위치 편향을 지워요.

## 사례 만들기

`evals/behavior/<스킬>/<사례>/` 아래에 두 파일을 둬요.

- `prompt.md`: 사용자가 보낼 요청
- `rubric.md`: 판정 기준 3~6줄. "길수록 좋다" 같은 기준은 쓰지 않아요.

## 실행

```
python3 evals/judge.py <스킬>
python3 evals/judge.py <스킬> --case <사례>
python3 evals/judge.py <스킬> --repeat 3
```

`--repeat N`(기본 1)은 사례마다 기준선·스킬 답을 한 번만 만들고, 순서를 바꾼 판정만 N번 돌려요. 사례 결과는 N번의 최종 판정 중 다수결이고, 동률이면 `tie`예요. 판정 한 번은 결과가 자주 뒤집혀요. 결과를 믿기 전에 `--repeat 3`으로 돌리는 걸 권해요. 답 생성 자체의 흔들림은 이 옵션으로 줄지 않아요.

결과는 `evals/runs/<날짜-시각>/<스킬>/<사례>/`에 `baseline.md`, `skill.md`, `verdict.json`으로 남고(`verdict.json`에는 회차별 `rounds`와 `final`이 들어 있어요), 마지막에 `skill W / baseline L / tie T / error E`를 출력해요. 사례 하나가 실패하거나 시간 초과여도 `ERROR <사례>: <이유>`만 찍고 다음 사례로 넘어가요. `evals/runs/`는 git에서 무시해요.

두 판정이 엇갈리면 무승부로 세요. 한쪽 순서만 이긴 건 위치 편향일 수 있어서예요.

## 격리

두 쪽은 플러그인만 다르게 돌려요. 매번 빈 임시 폴더에서 실행해서 프로젝트의 CLAUDE.md나 저장소 맥락이 섞이지 않고, `--setting-sources project --strict-mcp-config`로 다른 플러그인·사용자 설정·MCP 서버를 건너뛰어요. 스킬 쪽에만 `--plugin-dir <저장소 경로>`를 붙여요. 판정자는 플러그인 없이 돌아요. 두 쪽 모두 `--allowedTools`로 `Read`, `Write`, `Edit`, `Bash(python3:*)`를 허용하고, 스킬 쪽에는 `--add-dir`로 플러그인 폴더도 열어서 스킬이 스크립트와 참조 파일을 실제로 쓸 수 있어요.

사용자 수준 CLAUDE.md 같은 메모리는 두 쪽에 똑같이 로드될 수 있어요. 차이를 만들지는 않지만 답변 문체에는 영향을 줄 수 있어요.

기준선을 깨끗하게 얻으려면 이 플러그인을 전역 설치하지 않은 상태에서 돌려요.

## 사람 교정

판정자도 틀릴 수 있어요. 처음 20건은 사람이 두 답과 verdict를 직접 읽고, 판정에 동의하는지를 `calibration.md`에 적어요. 일치율이 낮으면 rubric을 먼저 고쳐요.

## 설치 검증

깨끗한 임시 `XDG_CONFIG_HOME`에서 `claude -p --plugin-dir <저장소>`로 문구마다 한 번씩 돌렸어요. 각 요청 뒤에 "실제 작업은 하지 말고 스킬만 정해서 호출하고, 마지막 줄에 사용한 스킬 이름만 적어 줘"를 붙였어요. 요청 하나에 표본은 한 번이라 우연히 맞았을 수도 있어요.

| 요청 | 기대 | 실제 | 일치 |
|---|---|---|---|
| 이 내용 문서로 써줘: (짧은 내용) | monkey-doc | monkey-doc | 예 |
| 이 글 AI 티 없애줘: (짧은 글) | monkey-human | monkey-human | 예 |
| 이 흐름 그림으로 그려줘: (짧은 흐름) | monkey-visual | monkey-visual | 예 |
| 캐시 무효화 쉽게 설명해줘 | monkey-clear | monkey-clear | 예 |
| 반말로 해줘 | monkey-voice | monkey-voice | 예 |
| 다음엔 이러지 마, 규칙으로 남겨 | monkey-learn | monkey-learn | 예 |
| monkey 스킬 뭐 써야 해? | monkey | monkey | 예 |

7개 중 7개가 일치했어요.
