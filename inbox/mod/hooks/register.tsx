import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import { GUARD_NOTE, sideEffect, WORKER_MARK } from './guard'
import { append, complete, dayOf, dueLabel, nextPrompt, openItems, parse, urgentItems, workPrompt } from './todo'

const PANE = 'inbox'
const REFRESH_MS = 60_000

const items = atom({ plugin: 'inbox', key: 'items' } as const, [])
const error = atom({ plugin: 'inbox', key: 'error' } as const, null)
const today = atom({ plugin: 'inbox', key: 'today' } as const, '')
const isBandHidden = atom({ plugin: 'inbox', key: 'isBandHidden' } as const, false)
const isWorker = atom({ plugin: 'inbox', key: 'isWorker' } as const, false)

// One folder for every session, whatever repository it runs in: `INBOX_DIR`, else `~/inbox`.
async function inboxDir($: EngineInterface): Promise<string> {
  const own = await $.env.get('INBOX_DIR')
  if (own) return own.replace(/[\\/]+$/, '')
  const home = (await $.env.get('USERPROFILE')) ?? (await $.env.get('HOME')) ?? '.'
  return `${home.replace(/[\\/]+$/, '')}/inbox`
}

async function readBody($: EngineInterface, file: string): Promise<string> {
  return (await $.fs.exists(file)) ? String(await $.fs.read(file)) : ''
}

async function refresh($: EngineInterface) {
  const file = `${await inboxDir($)}/todo.md`
  try {
    const body = await readBody($, file)
    await update($, items, () => parse(body))
    await update($, error, () => null)
  } catch (err) {
    await update($, error, () => `${file}을 읽지 못함: ${String(err)}`)
  }
  await update($, today, () => dayOf(new Date()))
}

// Read, change and write in one go, so an edit made in an editor since the last refresh is kept.
async function edit($: EngineInterface, change: (body: string, day: string) => string | null): Promise<boolean> {
  const file = `${await inboxDir($)}/todo.md`
  try {
    const next = change(await readBody($, file), dayOf(new Date()))
    if (next !== null) await $.fs.write(file, next)
    await refresh($)
    return next !== null
  } catch (err) {
    await update($, error, () => `${file}에 쓰지 못함: ${String(err)}`)
    return false
  }
}

const add = ($: EngineInterface, text: string) =>
  text.trim() === '' ? Promise.resolve(false) : edit($, (body, day) => append(body, text, day))

const askNext = async ($: EngineInterface) =>
  $.prompt.submit({ text: nextPrompt(await inboxDir($)) })

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const result = await next(e)
    await $.command.register({ name: 'todo', description: '할 일 패널을 열거나, 인자로 받은 할 일을 추가한다' })
    await $.command.register({ name: 'next', description: '할 일 목록에서 지금 할 일 하나를 추천받는다' })
    await refresh($)
    // Picks up edits from an editor, the morning task, or another session.
    $.clock.every(REFRESH_MS, () => refresh($))
    return result
  })

  // The scheduled worker opens its prompt with WORKER_MARK. From then on the session is fenced,
  // and the note tells the worker the fence is up; without it the worker stops on its own.
  on('prompt.submit', async ($, e, next) => {
    if (!e.text.trimStart().startsWith(WORKER_MARK)) return next(e)
    await update($, isWorker, () => true)
    return next({ ...e, context: [...(e.context ?? []), GUARD_NOTE] })
  })

  on('tool.call', async ($, e, next) => {
    if (!(await read($, isWorker))) return next(e)
    const why = sideEffect(e as unknown as Record<string, unknown>, await inboxDir($))
    return why === null ? next(e) : { deny: `inbox 작업 세션: ${why}` }
  })

  on('command.run', { command: 'todo' }, async ($, e) => {
    if (e.args.trim() !== '') {
      return { text: (await add($, e.args)) ? `추가함: ${e.args.trim()}` : (await read($, error)) ?? '추가하지 못함' }
    }
    await refresh($)
    await $.ui.open({ id: PANE, title: '할 일' })
    return { text: '할 일 패널을 열었습니다.' }
  })

  on('command.run', { command: 'next' }, async $ => {
    await askNext($)
    return { text: '다음 할 일을 고르는 중입니다.' }
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Button, Input, Text } = $.ui.resolve(e)
    const day = await read($, today)
    const open = openItems(await read($, items))
    const problem = await read($, error)

    return (
      <Box flexDirection="column" gap={1}>
        {Input !== undefined && (
          <Input
            key="add"
            placeholder="할 일 추가 (예: 보고서 작성 #업무 11/13까지)"
            submitLabel="추가"
            onSubmit={value => void add($, value)}
          />
        )}
        <Box gap={1}>
          <Button key="next" label="다음 할 일 추천" onPress={() => void askNext($)} />
          <Button key="refresh" label="새로고침" onPress={() => void refresh($)} />
        </Box>
        {problem !== null && <Text color="red">{problem}</Text>}
        {open.length === 0 && <Text dimColor>쌓인 할 일이 없습니다.</Text>}
        {open.map(item => (
          <Box key={`item-${item.line}`} gap={1}>
            <Button key={`done-${item.line}`} label="완료" onPress={() => void edit($, (body, d) => complete(body, item, d))} />
            <Box flexDirection="column" flexShrink={1}>
              <Text>{item.title}</Text>
              {(item.due !== null || item.tags.length > 0) && (
                <Text dimColor color={item.due !== null && dueLabel(item.due, day).includes('지남') ? 'red' : undefined}>
                  {[item.due !== null ? dueLabel(item.due, day) : '', ...item.tags.map(t => `#${t}`)].filter(Boolean).join(' ')}
                </Text>
              )}
              {item.work !== null && (
                <Button
                  key={`work-${item.line}`}
                  label="Claude가 미리 해 둔 것 보기"
                  onPress={async () => void $.prompt.submit({ text: workPrompt(await inboxDir($), item) })}
                />
              )}
            </Box>
          </Box>
        ))}
      </Box>
    )
  })

  // The reminder every session sees: items past due or due within SOON_DAYS.
  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const urgent = urgentItems(await read($, items), await read($, today))
    if (e.props.hasSurvey || urgent.length === 0 || (await read($, isBandHidden))) return next(e)

    const { Box, Button, Text } = $.ui.resolve(e)
    const day = await read($, today)
    const first = urgent[0]
    const more = urgent.length > 1 ? ` 외 ${urgent.length - 1}건` : ''

    return (
      <Box gap={1}>
        <Text>
          마감 임박: {first.title} ({first.due !== null ? dueLabel(first.due, day) : ''}){more}
        </Text>
        <Button key="open" label="목록" onPress={() => void $.ui.open({ id: PANE, title: '할 일' })} />
        <Button key="hide" label="숨기기" onPress={() => void update($, isBandHidden, () => true)} />
      </Box>
    )
  })
}
