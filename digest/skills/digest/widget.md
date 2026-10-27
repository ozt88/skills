# digest 위젯

digest를 채팅 옆 인라인 위젯(`show_widget`)으로 그리는 기준이다. 처음 그릴 때는 `read_me`를 `interactive`, `data_viz` 모듈로 먼저 부른다.
위젯에 담은 내용은 채팅 본문에 다시 쓰지 않는다. 채팅에는 두세 줄 안내만 남긴다.

## 1. 구성

위에서 아래로 이 순서로 둔다. 원문에 해당 내용이 없는 블록은 뺀다.

| 블록 | 처음 상태 | 내용 |
|---|---|---|
| 메타 줄 | 항상 보임 | 원문 링크, 분량과 읽는 시간, 상태 배지(`차트 N개 반영`, `본문과 차트 불일치 N건`, `N개 못 읽음`) |
| 한 줄 | 항상 보임 | 19px, 굵게(500), 산세리프 |
| 주요 수치 | 항상 보임 | 수치 카드 2~4개. 라벨, 값, 비교 기준 한 줄 |
| TL;DR | 펼침 | 3줄 이내. "근거 보기 ↗" 버튼 |
| 데이터 블록 | 접힘 | 원문의 표나 차트에서 비교할 수치가 있을 때만. 2절 참고 |
| 핵심 내용 | 접힘 | 번호 목록. 차트에서 읽은 수치가 있는 항목에 `차트` 배지 |
| 확인할 것 | 접힘 | 본문과 차트의 불일치를 카드 두 장으로 나란히. 원인을 따지는 버튼 |
| 구조 지도 | 접힘 | 섹션 제목, 설명, 원문으로 읽을 섹션에 `원문 확인` 배지 |
| 남은 질문과 더 볼 거리 | 접힘 | 열린 질문, 문서가 설명하지 않은 것, 링크 |

- 블록은 `<details class="dg-sec">`로 만든다. 렌더링 중에 숨긴 내용은 그려지지 않으므로 모두 `open`으로 내보내고,
  맨 끝 스크립트에서 TL;DR(`data-keep`)을 뺀 나머지를 닫는다.
- 버튼은 `sendPrompt`로 질문을 보낸다. 라벨 끝에 `↗`를 붙인다. 블록마다 하나까지만 둔다.

## 2. 데이터 블록

원문에 있는 수치만 그린다. 차트 이미지에서 읽은 값으로 원문 차트를 통째로 다시 그리지 않고, 비교에 필요한 값만 골라 그린다.

| 보여 줄 것 | 형태 |
|---|---|
| 항목별 비율 | 가로 막대 한 줄, 값 텍스트를 옆에 |
| 같은 항목의 전후 변화 | 덤벨(회색 점 = 이전, 파란 점 = 이후)과 `이전 → 이후` 텍스트 |
| 여럿 중 하나가 반대로 움직임 | 그 행만 `--bg-success`나 `--bg-warning` 배경으로 강조 |

- 행은 비교 기준이 되는 값 순으로 정렬한다(예: PvE로 옮긴 비율 순).
- 좋아진 값은 `--text-success`, 나빠진 값은 `--text-danger`로 쓴다. 색만으로 구분하지 않고 화살표와 숫자를 함께 둔다.
- 차트 색은 Chart.js나 HTML에서 쓸 수 있게 고정 hex를 쓴다. 순서는 파랑 `#2a78d6`, 주황 `#eb6834`, 청록 `#1baf7a`, 빨강 `#e34948`, 회색 `#898781`.
- 데이터가 없는 항목은 지우지 않고 `차트에 없음`으로 둔다.

## 3. 글꼴과 크기

한글이 기본 글꼴의 대체 글꼴로 그려지면 획이 고르지 않다. Pretendard를 불러와 위젯 전체에 쓴다.

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<style>
.dg{font-family:"Pretendard Variable",Pretendard,var(--font-sans);color:var(--text-primary);word-break:keep-all;letter-spacing:-0.01em}
.dg-sec{border-top:0.5px solid var(--border);padding:16px 0}
.dg-sec>summary{cursor:pointer;list-style:none;display:flex;align-items:center;gap:8px;font-size:17px;font-weight:500}
.dg-sec>summary::-webkit-details-marker{display:none}
.dg-sec>summary .ti-chevron-down{transition:transform .15s;color:var(--text-secondary)}
.dg-sec:not([open])>summary .ti-chevron-down{transform:rotate(-90deg)}
.dg-badge{font-size:12px;padding:3px 8px;border-radius:var(--radius);white-space:nowrap;font-weight:500}
.dg-more{font-size:13px;padding:4px 12px;margin-left:auto}
.dg-li{margin:0 0 12px;font-size:16px;line-height:1.75}
</style>
<div class="dg"> ... </div>
```

| 요소 | 크기 | 색 |
|---|---|---|
| 본문 문장, 목록 | 16px, 행간 1.75 | `--text-primary` |
| 블록 제목 | 17px, 500 | `--text-primary` |
| 한 줄 | 19px, 500 | `--text-primary` |
| 수치 카드 값 | 22~24px, 500 | `--text-primary` |
| 라벨, 보조 설명 | 13~15px | `--text-secondary` |
| 배지 | 12px, 500 | 같은 계열의 `--bg-*`와 `--text-*` |

- 13px보다 작은 글자를 쓰지 않는다.
- 문장에는 `--text-muted`를 쓰지 않는다. 흐려서 읽히지 않는다.
- 세리프(`--font-voice`)를 쓰지 않는다. 한글은 세리프에서 대체 글꼴로 그려진다.
- 굵기는 400과 500만 쓴다.

## 4. 문체

위젯 문장도 SKILL.md 4절의 문체 기준을 그대로 따른다. 위젯에서 특히 자주 틀리는 것은 다음과 같다.

- 카드 라벨과 구조 지도 설명처럼 칸 안에 들어가는 짧은 글만 명사구로 끝낸다. 나머지 문장은 합니다체로 쓴다.
- 수치 카드에는 무엇의 수치인지 라벨을 달고, 값에는 단위를 붙인다(`13.5초 → 17.2초`, `9.8% → 11.5%`).
- 불일치 카드의 라벨은 출처를 앞에 쓴다(`본문: 천 판당 티밍`, `차트: 주간 티밍 라운드(천 판당)`).

## 5. 확인

- 숫자를 다 넣은 뒤 원문의 숫자와 한 번 더 대조한다. 옮겨 적다 틀린 값이 차트로 그려지면 그럴듯해 보여서 찾기 어렵다.
- 다크 모드와 좁은 폭에서 어떻게 보이는지는 그려 본 뒤에도 확인하지 못한다. 확인하지 못했다고 채팅에 적는다.
