// Pure helpers, kept apart from the hooks so tests reach them without an engine.

// Same cut as hooks/knowledge_index_hook.py: an oversized index never takes over the prompt.
export const MAX_CHARS = 16000

// `dir` and every folder above it, nearest first, ending at `/`.
export function parentsOf(dir: string): string[] {
  const out: string[] = []
  let d = dir.replace(/\/+$/, '') || '/'
  for (;;) {
    out.push(d)
    if (d === '/') return out
    const at = d.lastIndexOf('/')
    d = at <= 0 ? '/' : d.slice(0, at)
  }
}

// The file a Read under the knowledge folder opened, relative to it (`decisions.md`); null for
// anything else. index.md is already in the prompt, so reading it again is not a reference.
export function entryOf(path: string, kdir: string): string | null {
  if (!path.startsWith(`${kdir}/`) || !path.endsWith('.md')) return null
  const name = path.slice(kdir.length + 1)
  return name === 'index.md' ? null : name
}

// A dated raw log, the file the CLAUDE.md logging rule appends to.
export const isRawLog = (path: string): boolean =>
  /\/\.knowledge\/raw\/\d{4}-\d{2}-\d{2}\.md$/.test(path)

export function cut(body: string): string {
  return body.length > MAX_CHARS
    ? `${body.slice(0, MAX_CHARS)}\n\n(이하 생략. 전체는 파일을 직접 연다)`
    : body
}

// Same wording as the Python hook, so the model reads the index the same way under either.
export const indexSection = (dir: string, body: string): string =>
  `이 프로젝트에서 지난 작업으로 쌓은 지식의 인덱스다. 경로: ${dir}/\n` +
  '작업이 아래 주제나 키워드에 닿으면, 진행하기 전에 해당 파일을 Read로 열어 결정, 규칙, 함정을 확인한다.\n' +
  '참고한 항목과 지금 상황이 어긋나면 그대로 따르지 말고 사용자에게 알린다.\n\n' +
  body

// Leaves the judgement to the model: compile counts a `참조:` line as "applied", not "opened".
export const refReminder = (opened: readonly string[]): string =>
  `이번 세션에서 연 knowledge 파일: ${opened.join(', ')}\n` +
  '방금 남긴 raw 기록이 이 파일의 항목을 근거로 판단을 바꿨거나 실수를 피한 것이면, 그 기록에 ' +
  '`- 참조: <파일> › <항목 제목>` 줄을 항목마다 덧붙인다. 열어 보기만 한 항목은 적지 않는다.'
