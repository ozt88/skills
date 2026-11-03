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
const META = /(?:^|\s)(?:#[^\s#]+|(?:due|added|done):\d{4}-\d{2}-\d{2})(?=\s|$)/g

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

// Appends one open item at the end, creating the header for a new file.
export function append(body: string, text: string, today: string): string {
  const line = `- [ ] ${text.replace(/\s+/g, ' ').trim()} added:${today}`
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

export const nextPrompt = (dir: string): string =>
  `할 일 목록에서 지금 할 일 하나를 골라 줘.\n` +
  `- 읽을 파일: ${dir}/todo.md (할 일), ${dir}/projects.md (태그별 저장소 경로, 없으면 건너뜀)\n` +
  '- 기준 순서: 마감 지남 > 3일 안에 마감 > 진행 중인 checkpoint가 있는 항목 > 선행 단계가 끝난 항목 > 오래 묵은 항목\n' +
  '- 고른 항목, 고른 이유 한두 줄, 작업할 저장소를 말한다. 후보가 비슷하면 2순위도 한 줄로 덧붙인다.\n' +
  '- 저장소를 모르거나 #미정이면 어느 저장소에서 할지 묻고, 답을 받으면 projects.md에 태그와 경로를 적는다.\n' +
  '- 저장소가 정해지면 그 저장소에서 새 세션을 시작할지 묻는다.\n' +
  '- todo.md는 사용자가 요청할 때만 고친다.'
