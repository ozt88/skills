// One top-level checkbox line of todo.md.
export type Item = {
  // 0-based line number in the file as last read.
  line: number
  // The line after `- [ ] `, as written; how a later write finds the line again.
  raw: string
  // `raw` without its #tags and `due:`/`added:`/`done:` fields.
  title: string
  // Tags without `#`, e.g. `프로젝트A`.
  tags: string[]
  // `YYYY-MM-DD`, or null when the item has no `due:`.
  due: string | null
  isDone: boolean
}

declare module 'claude-code' {
  interface PluginState {
    inbox: {
      // todo.md as last read; empty when the file is missing.
      items: Item[]
      // Why the last read or write failed; null after a good one.
      error: string | null
      // Today's date as of the last read, `YYYY-MM-DD`.
      today: string
      // The band was dismissed for this session.
      isBandHidden: boolean
    }
  }
}
