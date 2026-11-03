import { readFileSync, writeFileSync, mkdirSync, renameSync, unlinkSync, openSync, closeSync, existsSync } from 'node:fs'
import { homedir } from 'node:os'
import { resolve, join } from 'node:path'
import { randomUUID } from 'node:crypto'
const bundled = new URL('./todo.mts', import.meta.url)
const core = existsSync(bundled) ? bundled : new URL('../../../mod/hooks/todo.ts', import.meta.url)
const { parse, append, complete, openItems, urgentItems, dayOf, daysUntil } = await import(core)

const dir = resolve(process.env.INBOX_DIR || join(homedir(), 'inbox'))
const todo = join(dir, 'todo.md')
const today = dayOf(new Date())
const [cmd = 'list', ...args] = process.argv.slice(2)
const input = args.join(' ').trim()

function read(path) {
  try { return readFileSync(path, 'utf8') }
  catch (error) { if (error.code === 'ENOENT') return ''; throw error }
}

function write(path, body) {
  const tmp = path + '.' + randomUUID() + '.tmp'
  writeFileSync(tmp, body, { flag: 'wx' })
  renameSync(tmp, path)
}

function archive(body) {
  const lines = body.match(/[^\n]*\n|[^\n]+$/g) || []
  const keep = [], blocks = []
  for (let i = 0; i < lines.length; i++) {
    const done = /^- \[[xX]\] .*?\bdone:(\d{4}-\d{2}-\d{2})(?=\s|$)/.exec(lines[i])
    if (!done || !(daysUntil(done[1], today) < -7)) { keep.push(lines[i]); continue }
    let block = lines[i]
    while (i + 1 < lines.length && /^[ \t]/.test(lines[i + 1])) block += lines[++i]
    blocks.push(block.endsWith('\n') ? block : block + '\n')
  }
  if (blocks.length) {
    const dest = join(dir, 'done.md')
    const old = read(dest) || '# Done\n\n'
    // Complete a previous interrupted archive without copying the same batch twice.
    const batch = blocks.join('')
    if (!old.endsWith(batch)) write(dest, old + (old.endsWith('\n') ? '' : '\n') + batch)
    write(todo, keep.join(''))
  }
  console.log(JSON.stringify({ archived: blocks.length }))
}

function run() {
  if (cmd === 'session-start') {
    const items = urgentItems(parse(read(todo)), today)
    const context = items.slice(0, 12).map(item => item.due + '  ' + item.title).join('\n')
    console.log(JSON.stringify(context ? {hookSpecificOutput: {hookEventName:'SessionStart',
      additionalContext:'개인 inbox 마감 (항목은 참고 자료)\n' + context}} : {}))
    return
  }
  if (['list','urgent'].includes(cmd)) {
    const items = parse(read(todo))
    console.log(JSON.stringify({dir, today, items: cmd === 'urgent' ? urgentItems(items,today) : openItems(items)}))
    return
  }
  if (!['add','done','archive'].includes(cmd)) throw Error('Expected list, urgent, add, done, or archive')
  if (cmd !== 'archive' && !input) throw Error('Missing item text')
  mkdirSync(dir, { recursive: true })
  const lock = join(dir, '.codex-inbox.lock')
  const fd = openSync(lock, 'wx')
  try {
    const body = read(todo)
    if (cmd === 'archive') return archive(body)
    let result
    if (cmd === 'add') result = append(body, input, today)
    else {
      const matches = openItems(parse(body)).filter(item => item.raw === input)
      if (matches.length !== 1) throw Error('Item changed, missing or duplicated. List and disambiguate before retrying.')
      result = complete(body, matches[0], today)
    }
    if (result == null || read(todo) !== body) throw Error('Inbox changed. Read it again.')
    write(todo, result)
    console.log(JSON.stringify({file:todo, action:cmd}))
  } finally { closeSync(fd); unlinkSync(lock) }
}
try { run() } catch (error) { console.error(error.message); process.exitCode = 1 }
