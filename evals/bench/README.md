# 한국어 글쓰기 플러그인 벤치마크

같은 요청을 다섯 갈래(팔)로 돌려서 결과를 비교하는 도구예요. 팔은 플러그인 없음(baseline), im-not-ai(humanize-korean), im-not-strange-ai, patina, im-a-monkey 다섯 개예요.

## 준비

외부 플러그인 두 개는 git에서 무시하는 폴더에 받아 둬요.

```
mkdir -p .superpowers/bench/src
git clone --depth 1 https://github.com/itssosunny/im-not-strange-ai .superpowers/bench/src/im-not-strange-ai
git clone --depth 1 https://github.com/devswha/patina .superpowers/bench/src/patina
```

im-not-ai는 로컬 플러그인 캐시 경로를 써요. 다른 경로에 있으면 `evals/bench.py`의 `ARMS`를 고쳐요.

돌리기 전에 각 플러그인의 `.claude-plugin/plugin.json`, `hooks/hooks.json`, `SKILL.md`, 에이전트 파일을 읽어 봐요. 코드를 실행하는 Claude Code 훅이 있으면 훅을 뺀 사본을 만들어서 그 경로를 `ARMS`에 넣어요.

## 실행

```
python3 evals/bench.py
python3 evals/bench.py --out .superpowers/bench/runs/<이름> --jobs 6
```

같은 `--out`을 다시 주면 이미 끝난 칸은 건너뛰고 빠진 칸만 돌려요. 결과는 `<out>/<사례>/`에 팔별 `<팔>.md`(답), `<팔>.json`(쓴 도구·걸린 시간·오류), `judge-0.json`·`judge-1.json`(순위 판정)으로 남고, 전체 요약은 `<out>/summary.json`에 모여요.

## 격리

모든 호출은 빈 임시 폴더에서 `claude -p --setting-sources project --strict-mcp-config`로 돌려요. 도구는 모든 팔에 `Read,Write,Edit,Bash(python3:*)`만 허용해요. 프롬프트는 stdin으로 넘겨요. `--allowedTools`가 뒤따르는 인자를 삼키기 때문이에요. 플러그인 팔에만 `--plugin-dir`와 `--add-dir`를 붙여요. 호출 하나는 600초에서 끊고, 실패한 칸은 ERROR로 남긴 채 다음 칸으로 넘어가요.

## 사례

`cases/<id>.md`는 머리말(`track`, `intent`)과 입력으로 되어 있어요. A 트랙은 입력 앞에 "이 글을 사람이 쓴 것처럼 자연스럽게 다듬어 주세요. 다듬은 글만 주세요:"를 붙이고, B 트랙은 입력을 그대로 요청으로 보내요.

## 지표

- **humanize-scan 6신호**: im-not-ai의 humanize-scan 스킬이 고른 C-8, E-1, C-11, I-4, E-2, F-5를 정규식으로 옮겨 세요. 이 지표는 im-not-ai의 도구에서 왔으니 그 팔에 유리할 수 있어요.
- **의미 보존**(A 트랙): `scripts/preserve.py`로 빠진 숫자·토큰·링크, 부정 표현 개수 차이, 편집률을 봐요.
- **길이 비율**: 답 글자 수를 입력 글자 수로 나눠요.
- **블라인드 순위**: 다섯 답을 섞어 후보 A~E로 만들고, 플러그인 없는 판정자가 의미 보존, 사람다운 한국어, 읽기 쉬움, 불필요한 변경 없음 순으로 1~5위를 매겨요. 섞는 순서를 바꿔 두 번 판정하고 평균을 내요. 순위를 못 읽으면 한 번 다시 물어요.
- **스킬 발동**: 각 `<팔>.json`의 `tools`에 Skill·Agent 호출이 남아 있으면 발동한 거예요.

이 저장소의 린트(`scripts/lint.py`)는 im-a-monkey 규칙이라 채점에 쓰지 않아요.
