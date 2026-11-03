// What the unattended worker session may do: read, and write only under the inbox folder.
// Pure, so tests reach it without an engine. A best-effort fence, not a sandbox: anything it
// cannot read with confidence is refused, and nothing it allows runs a program the worker wrote.
//
// The worker reads Slack and Notion, so a message it reads can carry instructions. The fence
// therefore also refuses ways to send data out (WebFetch) or to act outside it (Agent).

// The first line of the worker's prompt; the session that sends it is fenced from then on.
export const WORKER_MARK = '[inbox-worker]'

// Sent with the worker's first prompt, so the worker can stop when no fence is in place.
export const GUARD_NOTE =
  'inbox 가드 켜짐: 이 세션은 inbox 폴더 밖에 쓰거나, 프로그램을 실행하거나, 외부로 보내는 도구 호출이 막힌다.'

const norm = (p: string) => p.replace(/\\/g, '/').replace(/\/+$/, '').toLowerCase()

export const isInside = (path: string, dir: string) => {
  const p = norm(path)
  const d = norm(dir)
  return (p === d || p.startsWith(`${d}/`)) && !p.split('/').includes('..')
}

// Agent is left out: a subagent's tool calls may not pass through this fence. WebFetch is left
// out: a URL can carry what the worker read to anyone. WebSearch stays for research.
const READ_TOOLS = new Set(['Read', 'Glob', 'Grep', 'WebSearch', 'ToolSearch', 'Skill', 'LSP'])
const WRITE_TOOLS = new Set(['Write', 'Edit', 'NotebookEdit'])
// An MCP tool is a read when its name says so and names no change.
const MCP_READ = /(search|fetch|read|get|list|query|view|download|status|whoami|self)/i
const MCP_WRITE = /(create|update|delete|remove|send|post|add|set|move|schedule|upload|cancel|complete|duplicate|restore|stop|spawn|resolve|react|publish|start|run|write|edit|archive|merge|push)/i

// Read commands, each with the options that would make it write a file or run a program.
const READ_COMMANDS: Record<string, RegExp | null> = {
  ls: null, cat: null, head: null, tail: null, grep: null, wc: null, pwd: null, echo: null,
  cut: null, jq: null, diff: null, file: null, stat: null, which: null, basename: null,
  dirname: null, realpath: null, cd: null, true: null, uniq: null,
  find: /^-(exec|execdir|ok|okdir|delete|fprint0?|fprintf|fls)$/,
  sort: /^(-[^-]*o|--output)/,
  tree: /^-o$/,
  rg: /^--pre(=|$)/,
  date: /^(-s|--set)/,
}
const GIT_READ = new Set(['log', 'show', 'diff', 'status', 'grep', 'blame', 'ls-files', 'ls-tree', 'rev-parse', 'shortlog', 'describe', 'cat-file', 'remote', 'branch', 'tag', 'config'])
// `-c` and `--config-env` can point a hook or pager at any program; `--output` writes a file.
const GIT_UNSAFE = /^(-c|--config-env|--exec-path|--output|--ext-diff|-O|--open-files-in-pager)(=|$)/
const GH_READ = /^gh\s+(pr|issue|run|repo|release)\s+(view|list|diff|checks)\b|^gh\s+search\b|^gh\s+auth\s+status\b/

// `>`, `>>`, `>|`, `2>`, `&>`, each with its target. `2>&1` style targets are descriptors.
const REDIRECT = /(?:\d*|&)>>?\|?\s*(&\d+|"[^"]*"|'[^']*'|[^\s;&|<>]+)/g
// A lone `&` sends the rest to the background as a separate command.
const BACKGROUND = /(^|[^&>])&(?![&>])/

function redirectProblem(command: string, inbox: string): string | null {
  for (const m of command.matchAll(REDIRECT)) {
    const target = m[1].replace(/^["']|["']$/g, '')
    if (/^&\d+$/.test(target) || target === '/dev/null' || isInside(target, inbox)) continue
    return `inbox 폴더 밖으로 리다이렉트: ${target}`
  }
  return null
}

function segmentProblem(seg: string): string | null {
  const words = seg.trim().replace(REDIRECT, ' ').trim().split(/\s+/)
  const [cmd] = words
  if (cmd === undefined || cmd === '') return null
  if (cmd in READ_COMMANDS) {
    const unsafe = READ_COMMANDS[cmd]
    const bad = unsafe === null ? undefined : words.slice(1).find(w => unsafe.test(w))
    if (bad !== undefined) return `${cmd} ${bad}는 쓰기나 실행이라 막힘`
    // `uniq IN OUT` writes OUT.
    if (cmd === 'uniq' && words.slice(1).filter(w => !w.startsWith('-')).length > 1) return 'uniq의 출력 파일 인자는 막힘'
    return null
  }
  if (cmd === 'git') {
    const bad = words.find(w => GIT_UNSAFE.test(w))
    if (bad !== undefined) return `git ${bad}는 막힘`
    const at = words.findIndex((w, i) => i > 0 && !w.startsWith('-') && words[i - 1] !== '-C')
    const verb = at < 0 ? undefined : words[at]
    if (verb === 'branch' || verb === 'tag' || verb === 'remote' || verb === 'config') {
      const rest = words.slice(at + 1)
      const isList = rest.every(w => w.startsWith('-') && !/^-(d|D|m|M|c|C|f|-delete|-move|-copy|-force|-set|-unset|-add|-replace)/.test(w)) || (verb === 'remote' && rest[0] === '-v') || (verb === 'config' && /^(--get|--list|-l)/.test(rest[0] ?? ''))
      return isList ? null : `git ${verb}의 변경 형태는 막힘`
    }
    return verb !== undefined && GIT_READ.has(verb) ? null : `git ${verb ?? ''}은(는) 읽기 명령이 아님`
  }
  if (cmd === 'gh') return GH_READ.test(seg.trim()) ? null : 'gh는 view/list/search만 허용'
  // Interpreters are refused even for scripts under the inbox folder: the worker can write
  // there, so running what it wrote would undo the whole fence.
  return `${cmd}는 허용 목록에 없음`
}

// Why the call is refused, or null when it may run. `inbox` is the inbox folder, absolute.
export function sideEffect(input: Readonly<Record<string, unknown>>, inbox: string): string | null {
  const tool = String(input.tool)
  if (READ_TOOLS.has(tool) || tool.startsWith('mcp__ccd_turn__')) return null
  if (WRITE_TOOLS.has(tool)) {
    const path = String(input.file_path ?? input.notebook_path ?? '')
    return isInside(path, inbox) ? null : `inbox 폴더 밖에 쓰기: ${path}`
  }
  if (tool === 'Bash') {
    const command = String(input.command ?? '')
    if (/\$\(|`|<\(|>\(/.test(command)) return '명령 치환은 막힘'
    if (BACKGROUND.test(command)) return '백그라운드 실행(&)은 막힘'
    const redirect = redirectProblem(command, inbox)
    if (redirect !== null) return redirect
    for (const seg of command.split(/&&|\|\||;|\||\n/)) {
      const problem = segmentProblem(seg)
      if (problem !== null) return problem
    }
    return null
  }
  if (tool.startsWith('mcp__')) {
    const name = tool.split('__').slice(2).join('__')
    return MCP_READ.test(name) && !MCP_WRITE.test(name) ? null : `읽기 전용이 아닌 MCP 도구: ${tool}`
  }
  // PowerShell is not parsed with the Bash rules above, so it is refused rather than misread.
  return `작업 세션에서 허용하지 않는 도구: ${tool}`
}
