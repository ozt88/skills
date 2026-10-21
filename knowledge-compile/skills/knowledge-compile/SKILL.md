---
name: knowledge-compile
description: Compile a project's accumulated .knowledge/raw/ logs into curated .knowledge/knowledge/ files (decisions, guardrails, anti-patterns, troubleshooting, index). Use when the user asks to compile knowledge, says raw logs are piling up, or when the nightly runner invokes it headlessly. Works in any project, GSD or not.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Bash(python3 ~/.claude/skills/knowledge-compile/scripts/manifest.py *)
---

# knowledge-compile

현재 작업 디렉터리의 `.knowledge/raw/`에 쌓인 기록을 `.knowledge/knowledge/`로 합친다.
raw는 읽기 전용이다. 이 작업 자체는 raw에 기록하지 않는다(CLAUDE.md의 raw 기록 지시가 다루는 작업이 아니다).

장부 명령은 아래에 적힌 그대로, 다른 명령과 `;`, `&&`로 잇지 말고 한 번에 하나씩 실행한다.
야간 실행은 이 명령만 셸로 허용한다. 디렉터리 확인은 Glob을 쓴다.

## 1. 대상 파일 고르기

`python3 ~/.claude/skills/knowledge-compile/scripts/manifest.py pending .`를 실행한다.
- 출력이 비면 "새 기록 없음"을 알리고 끝낸다.
- 출력된 파일만 Read로 읽는다. 처음 컴파일하는 프로젝트라 파일이 많으면 오래된 날짜부터 읽는다.

## 2. 기존 knowledge 읽기

`.knowledge/knowledge/`가 있으면 `index.md`를 먼저 읽고, 병합할 대상 파일만 연다.
없으면 디렉터리를 만들고 아래 다섯 파일을 새로 만든다.

## 3. 추려서 병합하기

다음 세션의 실수를 막는 내용만 남긴다.
- 담는 것: 설계 결정과 그 이유, 시스템 동작 구조, 되풀이된 오류와 해법, 맥락에 따라 판단이 갈리는 주의점
- 버리는 것: 일회성 확인, 결과 없는 탐색, 이미 있는 항목과 같은 내용, 진행 상황 보고

파일별 형식은 다음과 같다. 모든 항목은 `## 제목` 다음 줄에 `[context: 태그]`를 단다.
태그는 항목이 적용되는 모듈이나 영역 이름을 쓰고, 항목당 3개까지 붙인다.

- `decisions.md`: 설계 결정
  ```
  ## 제목
  [active] [context: tag1, tag2]

  **시도:** ...
  **결과:** ...
  **결정:** ...
  **Observed:** 1 times (YYYY-MM-DD)
  ```
  상태값은 `[active]`, `[uncertain]`, `[superseded]`, `[rejected]` 넷이다.
- `guardrails.md`: 대안이 하나로 정해진 규칙. "~를 쓴다", "~를 거친다"처럼 해야 할 행동으로 쓴다.
- `anti-patterns.md`: 맥락에 따라 답이 달라지는 함정. **관찰:** / **이유:** / **대신:** 구조와 **Observed:** 줄을 쓴다.
- `troubleshooting.md`: 오류와 해법. **에러:** / **원인:** / **해법:** 구조와 **Observed:** 줄을 쓴다.
- `index.md`: 맨 위에 `**Last compiled:** YYYY-MM-DD`, `**Total entries:** N`을 두고,
  주제 | 파일 | 핵심 항목 표와 파일별 한 줄 요약을 둔다. index.md만 읽어도 어느 파일을 열지 정할 수 있게 쓴다.

위 형식은 새로 만드는 파일에만 쓴다. 이미 있는 파일에 덧붙일 때는 그 파일이 쓰는 필드 이름, 제목 수준, 구분선을 그대로 따른다.
예를 들어 기존 항목이 `**Attempt:** / **Result:** / **Decision:**`이면 새 항목도 같은 이름을 쓴다. 한 파일 안에 두 형식이 섞이지 않게 한다.
`**Observed:**` 줄과 `[context: ...]` 태그는 기존 파일에 없더라도 새 항목에 붙인다.

같은 내용이 다시 나왔을 때의 처리:
- 같은 결론이 다시 확인되면 `**Observed:**` 횟수를 1 올리고 날짜를 덧붙인다. `**Observed:** 3 times (2026-04-16, 2026-05-07, 2026-10-21)`
- 기존 결정과 정면으로 어긋나는 결론이 나오면 제목 줄 아래에 `[conflict: YYYY-MM-DD]`를 달고,
  `> **New (YYYY-MM-DD):** ...` 인용으로 새 내용을 남긴 뒤 상태를 `[uncertain]`으로 바꾼다.
- 이미 `[uncertain]`인 항목은 이번 raw에서 증거를 찾는다. 같은 방향이면 `[active]`, 반대로 확정되면 `[superseded]` 또는 `[rejected]`, 증거가 없으면 그대로 둔다.
- decisions 항목의 제목을 바꾸면 index.md도 같이 고친다.

## 4. 장부 갱신

병합을 마친 뒤 1단계에서 읽은 파일 이름을 넘겨 `python3 ~/.claude/skills/knowledge-compile/scripts/manifest.py mark . <파일...>`을 실행한다.
병합하다 중단했으면 장부는 건드리지 않는다. 다음 실행에서 같은 파일을 다시 본다.

## 5. 결과 보고

다음 세 가지를 짧게 출력한다.
- 처리한 raw 파일 수
- 추가하거나 갱신한 항목 수
- 바뀐 knowledge 파일 목록
