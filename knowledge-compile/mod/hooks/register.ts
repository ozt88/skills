import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { KnowledgeIndex } from '../types'
import { cut, entryOf, indexSection, isRawLog, parentsOf, refReminder } from './paths'

const index = atom({ plugin: 'knowledge', key: 'index' } as const, null)
const isIndexPending = atom({ plugin: 'knowledge', key: 'isIndexPending' } as const, false)
const opened = atom({ plugin: 'knowledge', key: 'opened' } as const, [])

// Stops at the project root (the first folder with .git or .knowledge) or at home: going further
// would mix the home folder's .knowledge into every project under it.
async function findIndex($: EngineInterface, cwd: string): Promise<KnowledgeIndex | null> {
  const home = await $.env.get('HOME')
  for (const d of parentsOf(cwd)) {
    const base = d === '/' ? '' : d
    const dir = `${base}/.knowledge/knowledge`
    if (await $.fs.exists(`${dir}/index.md`)) {
      const body = await $.fs.read(`${dir}/index.md`).catch(() => null)
      return typeof body === 'string' ? { dir, body: cut(body) } : null
    }
    if (d === home || await $.fs.exists(`${base}/.git`) || await $.fs.exists(`${base}/.knowledge`)) return null
  }
  return null
}

// Read at session start and after a compaction, the points where the conversation loses what the
// last prompt carried; a nightly compile reaches a running session at its next compaction.
async function loadIndex($: EngineInterface, cwd: string) {
  const found = await findIndex($, cwd).catch(() => null)
  await update($, index, () => found)
  await update($, isIndexPending, () => found !== null)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    const result = await next(e)
    await loadIndex($, result.cwd)
    return result
  })

  on('session.compact', async ($, e, next) => {
    const result = await next(e)
    if (e.agentId === undefined && !('skip' in result && result.skip)) await loadIndex($, await $.session.cwd())
    return result
  }).catch(($, e, next) => next(e))

  // Rides the next prompt as context, not a prompt.compose section: on a machine with managed
  // settings the built-in security plugin runs past a user mod's prompt.compose hook.
  on('prompt.submit', async ($, e, next) => {
    const idx = await read($, index)
    if (idx === null || !(await read($, isIndexPending))) return next(e)
    await update($, isIndexPending, () => false)
    return next({ ...e, context: [...(e.context ?? []), indexSection(idx.dir, idx.body)] })
  }).catch(($, e, next) => next(e))

  // Only watches the path; a failure here never holds up the tool call.
  on('tool.call', { tool: 'Read' }, async ($, e, next) => {
    const idx = await read($, index)
    const name = idx === null ? null : entryOf(e.file_path, idx.dir)
    if (name !== null) await update($, opened, xs => (xs.includes(name) ? xs : [...xs, name]))
    return next(e)
  }).catch(($, e, next) => next(e))

  // A raw log written after reading knowledge files gets one reminder naming them, then the list starts over.
  on('tool.call', { tool: 'Write' }, async ($, e, next) => {
    const result = await next(e)
    return isRawLog(e.file_path) ? remind($, result) : result
  }).catch(($, e, next) => next(e))
  on('tool.call', { tool: 'Edit' }, async ($, e, next) => {
    const result = await next(e)
    return isRawLog(e.file_path) ? remind($, result) : result
  }).catch(($, e, next) => next(e))
}

async function remind<R extends { result?: unknown; isError?: true; context?: readonly string[] }>($: EngineInterface, result: R): Promise<R> {
  if (result.result === undefined || result.isError) return result
  const names = await read($, opened)
  if (names.length === 0) return result
  await update($, opened, () => [])
  return { ...result, context: [...(result.context ?? []), refReminder(names)] }
}
