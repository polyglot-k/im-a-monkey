# 기여하기

안티패턴은 `catalog/antipatterns.md`에 ID를 붙여 적어요. ID는 분류 글자와 두 자리 숫자(`S01`, `A12`)로 정하고 한 번 쓴 ID는 다른 항목에 다시 쓰지 않으며 목차에도 함께 올려요.

예문은 다른 글에서 가져오지 않고 직접 새로 써요. 나쁜 예를 일부러 보여 줘야 하는 곳은 `<!-- monkey-lint: off -->`와 `<!-- monkey-lint: on -->` 사이에 넣어 두면 린트가 건너뛰어요.

고친 뒤에는 저장소 루트에서 테스트를 돌리고 문서를 바꿨다면 자체 점검도 함께 돌려 주세요.

```
python3 -m unittest discover -s tests -v
python3 scripts/lint.py skills persona catalog examples README.md docs
```

라이선스는 MIT이고 전문은 [LICENSE](LICENSE)에 있어요.
