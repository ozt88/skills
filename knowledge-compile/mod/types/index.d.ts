// The compiled index this session reads: `<project>/.knowledge/knowledge/index.md`.
export type KnowledgeIndex = {
  // The knowledge folder, absolute, without a trailing slash.
  dir: string
  // index.md as read, cut to MAX_CHARS.
  body: string
}

declare module 'claude-code' {
  interface PluginState {
    knowledge: {
      // Read at session start and after each compaction, sent with the next prompt; null when the project has none.
      index: KnowledgeIndex | null
      // True from each read of the index until the next prompt carries it.
      isIndexPending: boolean
      // Files under the knowledge folder the model read since the last raw log reminder, e.g. `decisions.md`.
      opened: string[]
    }
  }
}
