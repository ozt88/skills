// Pure helpers over todo.md, kept apart from the hooks so tests reach them without an engine.
//
// One item per top-level checkbox line; indented lines under it (sub-steps, notes) are left alone.
//   - [ ] 주간 보고서 작성 #업무 due:2026-11-14 added:2026-11-03
//   - [x] 릴리스 절차 확인 #프로젝트A added:2026-11-01 done:2026-11-03

import type { Item } from '../types'

// Items due within this many days show in the band above the prompt.
export const SOON_DAYS = 3

export const HEADER = '# Inbox\n\n'

const ITEM = /^- \[([ xX])\] (.*)$/
// A lookahead, not `\b`: `\b` sees no boundary after a Korean tag like `#업무`.
const DUE = /(?:^|\s)due:(\d{4}-\d{2}-\d{2})(?=\s|$)/
const TAG = /(?:^|\s)#([^\s#]+)/g
// `work:<name>`: the worker's note for the item, `work/<name>.md` under the inbox folder.
const WORK = /(?:^|\s)work:([\w.-]+)(?=\s|$)/
const META = /(?:^|\s)(?:#[^\s#]+|(?:due|added|done):\d{4}-\d{2}-\d{2}|work:[\w.-]+)(?=\s|$)/g

export function parse(body: string): Item[] {
  const out: Item[] = []
  body.split(/\r?\n/).forEach((raw, line) => {
    const m = ITEM.exec(raw)
    if (m === null) return
    const rest = m[2]
    out.push({
      line,
      raw: rest,
      title: rest.replace(META, '').trim() || rest.trim(),
      tags: [...rest.matchAll(TAG)].map(t => t[1]),
      due: DUE.exec(rest)?.[1] ?? null,
      work: WORK.exec(rest)?.[1] ?? null,
      isDone: m[1] !== ' ',
    })
  })
  return out
}

// `YYYY-MM-DD` in local time.
export function dayOf(d: Date): string {
  const p = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`
}

export function daysUntil(due: string, today: string): number {
  const at = (s: string) => Date.UTC(+s.slice(0, 4), +s.slice(5, 7) - 1, +s.slice(8, 10))
  return Math.round((at(due) - at(today)) / 86_400_000)
}

export function dueLabel(due: string, today: string): string {
  const n = daysUntil(due, today)
  return n < 0 ? `${-n}일 지남` : n === 0 ? '오늘 마감' : `D-${n}`
}

// Open items, dated ones first by due date, then the rest in file order.
export function openItems(items: readonly Item[]): Item[] {
  return items
    .filter(i => !i.isDone)
    .sort((a, b) =>
      a.due !== null && b.due !== null ? a.due.localeCompare(b.due) || a.line - b.line
        : a.due !== null ? -1 : b.due !== null ? 1 : a.line - b.line)
}

export const urgentItems = (items: readonly Item[], today: string): Item[] =>
  openItems(items).filter(i => i.due !== null && daysUntil(i.due, today) <= SOON_DAYS)

export function addDays(day: string, n: number): string {
  const d = new Date(Date.UTC(+day.slice(0, 4), +day.slice(5, 7) - 1, +day.slice(8, 10) + n))
  return d.toISOString().slice(0, 10)
}

const WEEKDAYS = '월화수목금토일'
// Tokens a person types for a deadline, each a whole word: `11/13`, `~11/13`, `11/13까지`,
// `오늘`, `내일`, `모레`, `금요일`, `금까지`, `다음주 월요일`.
const MONTH_DAY = /(?:^|\s)~?(\d{1,2})\/(\d{1,2})(?:까지)?(?=\s|$)/
const RELATIVE = /(?:^|\s)(오늘|내일|모레)(?:까지)?(?=\s|$)/
const WEEKDAY = /(?:^|\s)(다음\s?주\s?)?([월화수목금토일])(?:요일까지|요일|까지)(?=\s|$)/

// Turns the first deadline word in `text` into a date and removes it. Text that already has
// `due:` is left as is. A month/day already past means next year; a bare weekday means the next
// one from today, today included; `다음주` means that day of the following Monday-to-Sunday week.
export function extractDue(text: string, today: string): { text: string; due: string | null } {
  const has = DUE.exec(text)
  if (has !== null) return { text, due: has[1] }
  const cut = (m: RegExpExecArray) => `${text.slice(0, m.index)} ${text.slice(m.index + m[0].length)}`.replace(/\s+/g, ' ').trim()

  const md = MONTH_DAY.exec(text)
  if (md !== null && +md[1] >= 1 && +md[1] <= 12 && +md[2] >= 1 && +md[2] <= 31) {
    const p = (n: string) => n.padStart(2, '0')
    const year = +today.slice(0, 4)
    const due = `${year}-${p(md[1])}-${p(md[2])}`
    return { text: cut(md), due: due < today ? `${year + 1}${due.slice(4)}` : due }
  }
  const rel = RELATIVE.exec(text)
  if (rel !== null) return { text: cut(rel), due: addDays(today, ['오늘', '내일', '모레'].indexOf(rel[1])) }
  const wd = WEEKDAY.exec(text)
  if (wd !== null) {
    const now = (new Date(`${today}T00:00:00Z`).getUTCDay() + 6) % 7
    const want = WEEKDAYS.indexOf(wd[2])
    const n = wd[1] ? want - now + 7 : (want - now + 7) % 7
    return { text: cut(wd), due: addDays(today, n) }
  }
  return { text, due: null }
}

// Appends one open item at the end, creating the header for a new file. A deadline word in the
// text becomes `due:`, so nobody has to type the date format.
export function append(body: string, raw: string, today: string): string {
  const { text, due } = extractDue(raw.replace(/\s+/g, ' ').trim(), today)
  const tail = due !== null && !DUE.test(text) ? ` due:${due}` : ''
  const line = `- [ ] ${text}${tail} added:${today}`
  const base = body.trim() === '' ? HEADER : body.endsWith('\n') ? body : `${body}\n`
  return `${base}${line}\n`
}

// Checks off the item at `item.line`. The file may have changed since it was parsed, so a line
// that no longer holds the same text is looked up by text instead; null when it is gone.
export function complete(body: string, item: Item, today: string): string | null {
  const lines = body.split('\n')
  const holds = (i: number) => ITEM.exec(lines[i]?.replace(/\r$/, '') ?? '')?.[2] === item.raw
  const at = holds(item.line) ? item.line : lines.findIndex((_, i) => holds(i))
  if (at < 0) return null
  const cr = lines[at].endsWith('\r') ? '\r' : ''
  lines[at] = `- [x] ${item.raw} done:${today}${cr}`
  return lines.join('\n')
}

export const workPrompt = (dir: string, item: Item): string =>
  `${dir}/work/${item.work}.md 를 읽고, "${item.title}" 항목에 Claude가 미리 해 둔 것을 정리해 줘.\n` +
  '- 알아낸 것과 만든 것(프로토타입 위치 포함)을 짧게, 내가 답하거나 정해야 할 것을 먼저 보여 준다.\n' +
  '- 이어서 할 일을 제안하고, 저장소 작업이 필요하면 projects.md에서 저장소를 찾아 새 세션을 시작할지 묻는다.'

export const nextPrompt = (dir: string): string =>
  `할 일 목록에서 지금 할 일 하나를 골라 줘.\n` +
  `- 읽을 파일: ${dir}/todo.md (할 일), ${dir}/projects.md (태그별 저장소 경로, 없으면 건너뜀), ` +
  `항목에 work:<이름>이 있으면 ${dir}/work/<이름>.md (Claude가 미리 해 둔 조사와 프로토타입)\n` +
  '- 미리 해 둔 것이 있는 항목은 바로 이어서 할 수 있으니 같은 조건이면 먼저 고른다.\n' +
  '- 기준 순서: 마감 지남 > 3일 안에 마감 > 진행 중인 checkpoint가 있는 항목 > 선행 단계가 끝난 항목 > 오래 묵은 항목\n' +
  '- 고른 항목, 고른 이유 한두 줄, 작업할 저장소를 말한다. 후보가 비슷하면 2순위도 한 줄로 덧붙인다.\n' +
  '- 저장소를 모르거나 #미정이면 어느 저장소에서 할지 묻고, 답을 받으면 projects.md에 태그와 경로를 적는다.\n' +
  '- 저장소가 정해지면 그 저장소에서 새 세션을 시작할지 묻는다.\n' +
  '- todo.md는 사용자가 요청할 때만 고친다.'
