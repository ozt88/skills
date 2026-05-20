# 시각화 패턴 카탈로그

내용 유형별로 효과적인 HTML 표현 방식을 모은 참고 문서.
**강제 템플릿이 아니다.** 영감을 얻거나 처음 시작점이 필요할 때만 본다.

원본 영감: <https://thariqs.github.io/html-effectiveness/>
로컬 사본: `references/examples/*.html` (20개 예제 + `_index.html`).
**구체 구현이 궁금하면 실제 파일을 읽어라** — 설명보다 코드가 정확하다.

---

## 공통 설계 원칙

모든 효과적인 시각화에서 반복되는 5가지 패턴:

1. **계층적 정보 아키텍처**: 메타 → TL;DR → 본문 → 부록(액션/용어). 스캔 가능한 헤더 깊이.
2. **컬러 코딩된 의미 배지**: 상태를 작은 칩으로 압축 (Blocking/Nit/Safe, SEV-2, +/− 등).
3. **앵커 + 인라인 점프**: 목차·파일:행 참조로 긴 문서를 짧게 만든다.
4. **복사·내보내기 행동 유도**: "Copy markdown/diff/JSON/SVG" 버튼을 거의 모든 에디터에 둔다.
5. **CSS 변수 토큰 팔레트**: 5색 정도의 통일된 팔레트, 다크모드도 같은 변수로 전환.

---

## 카테고리별 패턴

### 탐색·계획 (PLAN.md, 설계 문서)

- **나란히 비교** ([code-approaches](https://thariqs.github.io/html-effectiveness/01-exploration-code-approaches.html)): 접근법 2~3개 수직 비교 + Pro/Con 표 + 인라인 메트릭 배지(`Bundle impact`)
- **라이트·다크 토글 디자인 컴파** ([visual-designs](https://thariqs.github.io/html-effectiveness/02-exploration-visual-designs.html)): 4방향 × Light/Dark, 미세 애니메이션
- **마일스톤→흐름→목업→코드 종단 흐름** ([implementation-plan](https://thariqs.github.io/html-effectiveness/16-implementation-plan.html)): 진행도 배지, 위험/완화 2열 표, 댓글 + 회신

### 코드 리뷰 (REVIEW.md, PR 노트)

- **주석 달린 PR** ([annotated-pr](https://thariqs.github.io/html-effectiveness/03-code-review-pr.html)): 개요 → 위험도 맵 → 파일 목록. 인라인 라인 주석 + Blocking/Nit/Safe 배지
- **PR 서술문** ([pr-writeup](https://thariqs.github.io/html-effectiveness/17-pr-writeup.html)): TL;DR → Why → File-by-file → Test plan → Rollout. 파일:행 참조, ±라인 수 배지, Before/After 표
- **모듈 맵** ([module-map](https://thariqs.github.io/html-effectiveness/04-code-understanding.html)): 다이어그램 → 5단계 콜스택 워크스루. `<details>` 로 접힌 소스 펼침

### 디자인 시스템

- **리빙 디자인 시스템** ([design-system](https://thariqs.github.io/html-effectiveness/05-design-system.html)): 색·타이포·간격·그림자·컴포넌트 계층 + 라이브 버튼/입력/배지
- **컴포넌트 변형 시트** ([component-variants](https://thariqs.github.io/html-effectiveness/06-component-variants.html)): 6변형 그리드 + padding/border/shadow 슬라이더 라이브 조정 + 호버 시 Props 코드 표시

### 프로토타이핑

- **마이크로 인터랙션 샌드박스** ([animation](https://thariqs.github.io/html-effectiveness/07-prototype-animation.html)): 체크박스 클릭 → 채움→체크 그리기→취소선→축소. 스프링 이징
- **드래그앤드롭 플로우** ([interaction](https://thariqs.github.io/html-effectiveness/08-prototype-interaction.html)): 사이드바 리스트 재정렬, 중앙선 통과 시 스냅. ~40줄 vanilla JS

### 다이어그램

- **SVG 시트** ([svg-illustrations](https://thariqs.github.io/html-effectiveness/10-svg-illustrations.html)): 3개 720×320 SVG + 개별 Download 버튼. 5색 팔레트, 일관 corner radius
- **클릭 가능한 플로우차트** ([flowchart](https://thariqs.github.io/html-effectiveness/13-flowchart-diagram.html)): 단계 클릭 → 실행/소요시간/장애지점 패널. 직사각=프로세스, 다이아=결정

### 덱·리서치·리포트

- **화살표 키 슬라이드 덱** ([deck](https://thariqs.github.io/html-effectiveness/09-slide-deck.html)): 좌우 화살표 네비, 1/6 카운터, 메트릭 큰 숫자
- **기능 학습 자료** ([feature-explainer](https://thariqs.github.io/html-effectiveness/14-research-feature-explainer.html)): 목차 + 4단계 확장 + 3열 코드 비교 + FAQ
- **개념 시뮬레이터** ([concept-explainer](https://thariqs.github.io/html-effectiveness/15-research-concept-explainer.html)): 선형 학습 흐름 + 인터랙티브 시뮬레이터 (해시 링 add/remove/reset) + 비교표 + 용어사전
- **주간 상태 리포트** ([status](https://thariqs.github.io/html-effectiveness/11-status-report.html)): KPI 큰 숫자 헤더 + Shipped 표 + 일별 히트맵
- **장애 회고** ([incident](https://thariqs.github.io/html-effectiveness/12-incident-report.html)): 메타 칩 행(SEV-2/상태/owner) → TL;DR → 타임라인 → 근본원인 → 영향 → 액션

### 커스텀 에디터

- **트리아지 보드** ([triage-board](https://thariqs.github.io/html-effectiveness/18-editor-triage-board.html)): Now/Next/Later/Cut 칸반 + DnD + 태그 필터 + "Copy as markdown" 내보내기
- **피처 플래그 에디터** ([feature-flags](https://thariqs.github.io/html-effectiveness/19-editor-feature-flags.html)): 토글 + 의존성 경고 자동 갱신 + Copy diff/Copy full JSON + "Pending changes (n)" 카운터
- **프롬프트 튜너** ([prompt-tuner](https://thariqs.github.io/html-effectiveness/20-editor-prompt-tuner.html)): 좌 편집 / 우 라이브 프리뷰 + `{{slot}}` 슬롯 문법 + 토큰 카운트 + Copy prompt

---

## 재사용 스니펫

### 색·타이포 토큰 (다크모드 대응)

```css
:root {
  --bg: #ffffff; --fg: #1a1a1a; --muted: #6b7280;
  --line: #e5e7eb; --card: #f9fafb; --code: #f3f4f6;
  --accent: #2563eb; --done: #16a34a;
  --warn: #f59e0b; --danger: #dc2626;
  --radius: 8px;
  --shadow: 0 1px 2px rgba(0,0,0,.04), 0 1px 3px rgba(0,0,0,.06);
  --ease-spring: cubic-bezier(.34, 1.56, .64, 1);
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0f172a; --fg: #e5e7eb; --muted: #94a3b8;
    --line: #1e293b; --card: #1e293b; --code: #0b1220;
    --accent: #60a5fa; --done: #4ade80;
    --warn: #fbbf24; --danger: #f87171;
  }
}
body {
  font-family: -apple-system, "Segoe UI", "Pretendard", "Apple SD Gothic Neo", sans-serif;
  background: var(--bg); color: var(--fg);
  line-height: 1.55;
}
```

### 의미 배지 시스템

```html
<span class="badge badge--blocking">차단</span>
<span class="badge badge--nit">사소</span>
<span class="badge badge--safe">안전</span>
<style>
.badge { font: 600 11px/1 ui-monospace, monospace; padding: 3px 7px;
         border-radius: 4px; letter-spacing: .02em; }
.badge--blocking { background: #fde2e2; color: #a01b1b; }
.badge--nit      { background: #fff1c2; color: #7a5a00; }
.badge--safe     { background: #dff3df; color: #1f6b2a; }
@media (prefers-color-scheme: dark) {
  .badge--blocking { background: #4a1717; color: #fda4a4; }
  .badge--nit      { background: #463a0e; color: #fde68a; }
  .badge--safe     { background: #14361b; color: #86efac; }
}
</style>
```

### KPI 헤더 (상태 리포트·회고 공용)

```html
<header class="kpi-row">
  <div><b>14</b><span>PR 머지됨</span></div>
  <div><b>3</b><span>장애</span></div>
  <div><b>92%</b><span>그린 빌드</span></div>
</header>
<style>
.kpi-row { display: flex; gap: 32px; border-bottom: 1px solid var(--line); padding: 16px 0; flex-wrap: wrap; }
.kpi-row b { font: 600 32px/1 system-ui; display: block; }
.kpi-row span { font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: .05em; }
</style>
```

### "소스 보기" 토글 (`<details>` 활용)

```html
<details class="source">
  <summary>소스 보기 · auth/session.ts</summary>
  <pre><code>export function createSession(...) { ... }</code></pre>
</details>
<style>
.source { background: var(--card); border-radius: var(--radius); margin: 8px 0; }
.source summary { cursor: pointer; font: 500 12px ui-monospace, monospace;
                  color: var(--muted); padding: 8px 12px; }
.source pre { margin: 0; padding: 0 12px 12px; }
</style>
```

### 화살표 키 슬라이드 덱

```html
<div id="deck">
  <section>슬라이드 1</section>
  <section hidden>슬라이드 2</section>
  <section hidden>슬라이드 3</section>
</div>
<aside id="counter">1 / 3</aside>
<script>
const s = [...document.querySelectorAll('#deck section')]; let i = 0;
const show = n => {
  s.forEach((e, k) => e.hidden = k !== n);
  counter.textContent = `${n+1} / ${s.length}`;
};
addEventListener('keydown', e => {
  if (e.key === 'ArrowRight') show(i = Math.min(i+1, s.length-1));
  if (e.key === 'ArrowLeft')  show(i = Math.max(i-1, 0));
});
</script>
<style>
#deck section { padding: 40px; min-height: 60vh; }
#counter { position: fixed; top: 16px; right: 20px; color: var(--muted); font: 500 12px ui-monospace; }
</style>
```

### 사이드바 + 본문 레이아웃 (검색 가능)

```html
<div class="layout">
  <aside class="sidebar">
    <input type="search" placeholder="검색..." oninput="filter(this.value)">
    <nav id="toc"><!-- 목차 --></nav>
  </aside>
  <main><!-- 본문 --></main>
</div>
<style>
.layout { display: grid; grid-template-columns: 240px 1fr; gap: 32px; }
.sidebar { position: sticky; top: 16px; align-self: start; }
@media (max-width: 800px) { .layout { grid-template-columns: 1fr; } }
</style>
```

### 카드 그리드 (상태별 색)

```html
<div class="grid">
  <article class="card done">
    <header><h3>제목</h3><span class="badge done">완료</span></header>
    <p>본문</p>
  </article>
</div>
<style>
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; }
.card { background: var(--card); padding: 14px; border-radius: var(--radius);
        border-left: 3px solid var(--muted); }
.card.done   { border-left-color: var(--done); }
.card.warn   { border-left-color: var(--warn); }
.card.danger { border-left-color: var(--danger); }
</style>
```

### 정렬 가능한 표

```html
<table id="t">
  <thead><tr><th onclick="sort(0)">이름</th><th onclick="sort(1)">상태</th></tr></thead>
  <tbody><!-- ... --></tbody>
</table>
<script>
function sort(col) {
  const tb = document.querySelector('#t tbody');
  const rows = [...tb.rows];
  const asc = tb.dataset.col === String(col) && tb.dataset.dir !== 'asc';
  rows.sort((a, b) => a.cells[col].textContent.localeCompare(b.cells[col].textContent) * (asc ? 1 : -1));
  tb.dataset.col = col; tb.dataset.dir = asc ? 'asc' : 'desc';
  rows.forEach(r => tb.appendChild(r));
}
</script>
```

### 복사 버튼

```html
<pre><code>코드 내용</code></pre>
<button onclick="navigator.clipboard.writeText(this.previousElementSibling.textContent).then(()=>{this.textContent='복사됨';setTimeout(()=>this.textContent='복사',1500)})">복사</button>
```

### 접기/펴기 (네이티브)

```html
<details open>
  <summary>섹션 제목</summary>
  <div>내용</div>
</details>
<style>
details { background: var(--card); border-radius: var(--radius); padding: 8px 14px; margin-bottom: 8px; }
summary { cursor: pointer; font-weight: 600; }
</style>
```

### 타임라인 (수직)

```html
<div class="timeline">
  <div class="stop done"><div class="dot"></div><div class="content"><h4>1단계</h4></div></div>
  <div class="stop active"><div class="dot"></div><div class="content"><h4>2단계</h4></div></div>
</div>
<style>
.timeline { position: relative; padding-left: 24px; }
.timeline::before { content: ""; position: absolute; left: 7px; top: 0; bottom: 0;
                    width: 2px; background: var(--line); }
.stop { position: relative; margin-bottom: 16px; }
.stop .dot { position: absolute; left: -22px; top: 6px; width: 14px; height: 14px;
             border-radius: 50%; background: var(--bg); border: 3px solid var(--muted); }
.stop.done   .dot { background: var(--done); border-color: var(--done); }
.stop.active .dot { border-color: var(--warn); }
</style>
```

### 탭

```html
<div class="tabs">
  <button class="tab active" onclick="showTab(this,0)">개요</button>
  <button class="tab" onclick="showTab(this,1)">상세</button>
</div>
<div class="panel active">개요 내용</div>
<div class="panel">상세 내용</div>
<script>
function showTab(btn, i) {
  document.querySelectorAll('.tab').forEach((t, idx) => t.classList.toggle('active', idx === i));
  document.querySelectorAll('.panel').forEach((p, idx) => p.classList.toggle('active', idx === i));
}
</script>
<style>
.tabs { display: flex; gap: 4px; border-bottom: 1px solid var(--line); }
.tab { background: none; border: none; padding: 8px 16px; cursor: pointer; color: var(--muted); }
.tab.active { color: var(--fg); border-bottom: 2px solid var(--accent); }
.panel { display: none; padding: 16px 0; }
.panel.active { display: block; }
</style>
```

### 스프링 이징 체크 애니메이션

```html
<label class="check" data-done="false" onclick="this.dataset.done = this.dataset.done==='true' ? 'false' : 'true'">
  <svg viewBox="0 0 24 24" width="20" height="20">
    <path d="M5 12l5 5L20 7" fill="none" stroke="currentColor" stroke-width="2.5"
          stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
  <span>할 일 항목</span>
</label>
<style>
.check { display: inline-flex; align-items: center; gap: 8px; cursor: pointer;
         padding: 6px 12px; border-radius: var(--radius);
         transition: background .25s var(--ease-spring), color .25s var(--ease-spring); }
.check svg path { stroke-dasharray: 24; stroke-dashoffset: 24;
                  transition: stroke-dashoffset .35s var(--ease-spring) .1s; }
.check[data-done="true"] { background: var(--done); color: white; }
.check[data-done="true"] svg path { stroke-dashoffset: 0; }
.check[data-done="true"] span { text-decoration: line-through; opacity: .7; }
</style>
```

### Mermaid 다이어그램 (CDN, 필요 시만)

```html
<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
<div class="mermaid">
flowchart LR
  A[시작] --> B{판단}
  B -->|예| C[실행]
  B -->|아니오| D[중단]
</div>
<script>mermaid.initialize({ startOnLoad: true, theme: 'default' });</script>
```
