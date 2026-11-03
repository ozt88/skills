import { expect, mock, test } from 'claude-code/testing'
import type { On } from 'claude-code'

import { append, complete, dayOf, dueLabel, extractDue, openItems, parse, urgentItems } from '../hooks/todo'

const DIR = 'C:/Users/me/inbox'
const FILE = `${DIR}/todo.md`

const PANE = {
  plugin: 'inbox',
  component: 'Pane',
  requestId: 'inbox',
  surface: 'desktop',
  props: {
    title: '할 일',
    isFocused: false,
    bodyColumns: 60,
    placement: 'dock',
    scroll: { offset: 0, bodyRows: 30 },
    view: {},
  },
} as const

// todo.md in memory, answering the plugin's $.fs calls; `files` shows what was written.
function fakeFs(on: On, initial: string) {
  const files: Record<string, string> = { [FILE]: initial }
  // The engine hands Windows paths over with backslashes.
  const key = (path: string) => path.replace(/\\/g, '/')
  on('fs.exists', (_, e) => ({ value: key(e.path) in files }))
  on('fs.read', (_, e) => ({ value: files[key(e.path)] }))
  on('fs.write', (_, e) => {
    files[key(e.path)] = e.text
    return { value: undefined }
  })
  return files
}

async function start($: Parameters<Parameters<typeof test>[1]>[0], on: On) {
  mock.env(on, { INBOX_DIR: DIR })
  mock.clock(on)
  on('command.register', (_, e) => ({ value: { command: e.name } }))
  on('ui.open', () => ({ value: { isPlaced: true } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })
}

const shift = (days: number) => dayOf(new Date(Date.now() + days * 86_400_000))

test('parse reads checkboxes, tags and due dates, and skips sub-steps', () => {
  const items = parse(
    '# Inbox\n\n- [ ] 보고서 작성 #업무 due:2026-11-14 added:2026-11-03\n  - [ ] 초안\n- [x] 릴리스 확인 #프로젝트A done:2026-11-03\n',
  )
  expect(items.length).toBe(2)
  expect(items[0]).toEqual({
    line: 2,
    raw: '보고서 작성 #업무 due:2026-11-14 added:2026-11-03',
    title: '보고서 작성',
    tags: ['업무'],
    due: '2026-11-14',
    isDone: false,
  })
  expect(items[1].isDone).toBe(true)
})

test('open items put dated ones first; urgent keeps the ones due soon', () => {
  const items = parse('- [ ] a\n- [ ] b due:2026-11-20\n- [ ] c due:2026-11-04\n- [x] d due:2026-11-01\n')
  expect(openItems(items).map(i => i.title)).toEqual(['c', 'b', 'a'])
  expect(urgentItems(items, '2026-11-03').map(i => i.title)).toEqual(['c'])
  expect(dueLabel('2026-11-01', '2026-11-03')).toBe('2일 지남')
  expect(dueLabel('2026-11-03', '2026-11-03')).toBe('오늘 마감')
})

test('append starts a new file with the header; complete finds a line that moved', () => {
  const body = append('', '보고서  작성', '2026-11-03')
  expect(body).toBe('# Inbox\n\n- [ ] 보고서 작성 added:2026-11-03\n')

  const [item] = parse(body)
  const moved = `- [ ] 새로 위에 끼운 항목\n${body}`
  expect(complete(moved, item, '2026-11-04')).toBe(
    '- [ ] 새로 위에 끼운 항목\n# Inbox\n\n- [x] 보고서 작성 added:2026-11-03 done:2026-11-04\n',
  )
  expect(complete('# Inbox\n', item, '2026-11-04')).toBe(null)
})

test('deadline words become due dates', () => {
  // 2026-11-03 is a Tuesday.
  const due = (text: string) => extractDue(text, '2026-11-03')
  expect(due('보고서 작성 #업무 11/13까지')).toEqual({ text: '보고서 작성 #업무', due: '2026-11-13' })
  expect(due('~1/5 연말정산')).toEqual({ text: '연말정산', due: '2027-01-05' })
  expect(due('리뷰 답변 내일')).toEqual({ text: '리뷰 답변', due: '2026-11-04' })
  expect(due('PR 정리 금요일까지').due).toBe('2026-11-06')
  expect(due('PR 정리 화요일').due).toBe('2026-11-03')
  expect(due('회고 다음주 월요일').due).toBe('2026-11-09')
  expect(due('회고 월까지').due).toBe('2026-11-09')
  expect(due('월간 리포트 작성')).toEqual({ text: '월간 리포트 작성', due: null })
  expect(due('배포 due:2026-12-01 11/13')).toEqual({ text: '배포 due:2026-12-01 11/13', due: '2026-12-01' })
  expect(append('', '회의록 #업무 11/13까지', '2026-11-03')).toBe(
    '# Inbox\n\n- [ ] 회의록 #업무 due:2026-11-13 added:2026-11-03\n',
  )
})

test('the pane adds an item from its field and checks one off', async ($, on) => {
  const files = fakeFs(on, `# Inbox\n\n- [ ] 보고서 작성 #업무 due:${shift(1)}\n`)
  await start($, on)

  const ui = await $.ui.mount(PANE)
  expect((await ui.find({ type: 'Text', text: /보고서/ }))?.text).toBe('보고서 작성')
  expect((await ui.find({ type: 'Text', text: /D-1/ }))?.text).toBe('D-1 #업무')

  await ui.input({ key: 'add', text: '회의록 작성 #업무', kind: 'submit' })
  expect(files[FILE]).toContain('- [ ] 회의록 작성 #업무 added:')
  expect((await ui.find({ type: 'Text', text: /회의록/ }))?.text).toBe('회의록 작성')

  await ui.press({ key: 'done-2' })
  expect(files[FILE]).toContain('- [x] 보고서 작성 #업무')
  expect(await ui.find({ type: 'Text', text: /보고서/ })).toBe(undefined)
  await ui.unmount()
})

test('the band shows an item due soon and stays quiet without one', async ($, on) => {
  fakeFs(on, `- [ ] 보고서 작성 due:${shift(-1)}\n- [ ] 나중 일 due:${shift(30)}\n`)
  // Stands for the engine's own band, drawn when the plugin passes.
  on('ui.render', ($, e) => {
    const { Text } = $.ui.resolve(e)
    return <Text>engine</Text>
  })
  await start($, on)

  const band = await $.ui.mount({ plugin: 'inbox', component: 'AbovePrompt', surface: 'desktop', props: { hasSurvey: false } })
  expect((await band.find({ type: 'Text', text: /마감 임박/ }))?.text).toBe('마감 임박: 보고서 작성 (1일 지남)')
  await band.press({ key: 'hide' })
  expect(await band.find({ type: 'Text', text: /마감 임박/ })).toBe(undefined)
  await band.unmount()
})

test('/todo with text adds it without opening the pane', async ($, on) => {
  const files = fakeFs(on, '')
  await start($, on)

  const ran = await $.command.run({ command: 'todo', args: '테스트 시나리오 재작성 #프로젝트A' })
  expect(ran.text).toBe('추가함: 테스트 시나리오 재작성 #프로젝트A')
  expect(files[FILE]).toContain('# Inbox\n\n- [ ] 테스트 시나리오 재작성 #프로젝트A added:')
})
