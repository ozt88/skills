import type { On } from 'claude-code'
import { describe, expect, test } from 'claude-code/testing'

import { entryOf, isRawLog, MAX_CHARS, parentsOf } from '../hooks/paths'

const INDEX = '# Knowledge Index\n\n| 주제 | 파일 |\n|---|---|\n| 배포 | decisions.md |\n'

// The engine beneath the plugin: a file system of `files` and `dirs`, HOME=/home/u.
// Returns the context each submitted prompt reached the engine with.
const engine = (on: On, files: Record<string, string>, dirs: string[] = []) => {
  const exists = (p: string) => p in files || dirs.includes(p)
  const contexts: (readonly string[])[] = []
  on('env.get', () => ({ value: '/home/u' }))
  on('session.cwd', () => ({ value: '/home/u/proj/sub' }))
  on('fs.exists', (_$, e) => ({ value: exists(e.path) }))
  on('fs.read', (_$, e) => (e.path in files ? { value: files[e.path] ?? '' } : { deny: 'ENOENT' }))
  on('session.start', (_$, e) => ({ cwd: e.cwd }))
  on('session.compact', () => ({ messages: SUMMARY }))
  on('prompt.submit', (_$, e) => {
    contexts.push(e.context ?? [])
    return { text: e.text }
  })
  on('tool.call', () => ({ result: {} }))
  return contexts
}

const START = { cwd: '/home/u/proj/sub', surface: 'terminal', isInteractive: true } as const
const PROMPT = { wait: false, origin: { kind: 'composer' } } as const
const SUMMARY = [{ role: 'user' as const, text: 'summary', toolUses: [] }]
const KDIR = '/home/u/proj/.knowledge/knowledge'

describe('paths', () => {
  test('walks up to the root', async () => {
    expect(parentsOf('/a/b')).toEqual(['/a/b', '/a', '/'])
    expect(parentsOf('/')).toEqual(['/'])
  })

  test('names a knowledge file but not the index', async () => {
    expect(entryOf(`${KDIR}/decisions.md`, KDIR)).toBe('decisions.md')
    expect(entryOf(`${KDIR}/index.md`, KDIR)).toBeNull()
    expect(entryOf('/home/u/proj/README.md', KDIR)).toBeNull()
  })

  test('knows a dated raw log', async () => {
    expect(isRawLog('/p/.knowledge/raw/2026-10-27.md')).toBe(true)
    expect(isRawLog('/p/.knowledge/raw/notes.md')).toBe(false)
  })
})

describe('index', () => {
  test('rides the first prompt only', async ($, on) => {
    const contexts = engine(on, { [`${KDIR}/index.md`]: INDEX }, ['/home/u/proj/.git', '/home/u/proj/.knowledge'])
    await $.session.start(START)
    await $.prompt.submit({ text: 'first', ...PROMPT })
    await $.prompt.submit({ text: 'second', ...PROMPT })

    expect(contexts[0]).toHaveLength(1)
    expect(contexts[0]?.[0]).toContain(`경로: ${KDIR}/`)
    expect(contexts[0]?.[0]).toContain('| 배포 | decisions.md |')
    expect(contexts[1]).toHaveLength(0)
  })

  test('stops at the project root and never reaches home', async ($, on) => {
    const contexts = engine(on, { '/home/u/.knowledge/knowledge/index.md': INDEX }, ['/home/u/proj/.git'])
    await $.session.start(START)
    await $.prompt.submit({ text: 'first', ...PROMPT })
    expect(contexts[0]).toHaveLength(0)
  })

  test('cuts an oversized index', async ($, on) => {
    const contexts = engine(on, { [`${KDIR}/index.md`]: 'x'.repeat(MAX_CHARS + 10) })
    await $.session.start(START)
    await $.prompt.submit({ text: 'first', ...PROMPT })
    expect(contexts[0]?.[0]).toContain('(이하 생략')
  })

  test('re-reads the index after a compaction and sends it again', async ($, on) => {
    const files: Record<string, string> = { [`${KDIR}/index.md`]: INDEX }
    const contexts = engine(on, files)
    await $.session.start(START)
    await $.prompt.submit({ text: 'first', ...PROMPT })
    files[`${KDIR}/index.md`] = '# compiled tonight'

    await $.session.compact({ trigger: 'manual', messages: SUMMARY })
    await $.prompt.submit({ text: 'after', ...PROMPT })
    expect(contexts[1]?.[0]).toContain('compiled tonight')
  })
})

describe('reference reminder', () => {
  test('names the files read once, on the next raw log write', async ($, on) => {
    engine(on, { [`${KDIR}/index.md`]: INDEX })
    await $.session.start(START)

    await $.tool.call({ tool: 'Read', file_path: `${KDIR}/index.md` })
    await $.tool.call({ tool: 'Read', file_path: `${KDIR}/decisions.md` })
    await $.tool.call({ tool: 'Read', file_path: `${KDIR}/decisions.md` })

    const other = await $.tool.call({ tool: 'Write', file_path: '/home/u/proj/a.md', content: 'x' })
    expect('context' in other ? other.context : undefined).toBeUndefined()

    const raw = await $.tool.call({ tool: 'Edit', file_path: '/home/u/proj/.knowledge/raw/2026-10-27.md', old_string: 'a', new_string: 'b' })
    const context = 'context' in raw ? raw.context ?? [] : []
    expect(context).toHaveLength(1)
    expect(context[0]).toContain('이번 세션에서 연 knowledge 파일: decisions.md\n')

    const again = await $.tool.call({ tool: 'Write', file_path: '/home/u/proj/.knowledge/raw/2026-10-27.md', content: 'x' })
    expect('context' in again ? again.context : undefined).toBeUndefined()
  })
})
