# Digest

Digest turns a long document you are reading into something you can absorb in a few minutes. Give it a Notion page, a web article, a PDF, or pasted text, and it returns a layered Korean digest you can stop reading at any level.

Supported runtime: **Claude Code**.

## Output

1. **One line**: what the document is ultimately saying
2. **TL;DR**: three lines at most
3. **Key points**: 3 to 7 claims, each with its supporting reason
4. **Section map**: one or two lines per section of the original, with ⭐ on the parts worth reading in full
5. **Terms**: only the ones you are unlikely to know
6. **What is left for you**: decisions, action items, open questions, and what the document does not cover
7. **Further reading**: subpages and important links

Short documents get only the first three. Long documents are split by heading and digested in parallel by subagents, then merged.

Chart images in a Notion page are downloaded and read too, since analysis documents often keep their numbers only in charts. Numbers taken from a chart are marked `(차트)`, and a mismatch between the text and a chart is shown rather than resolved.

The digest never invents content that is not in the source; any interpretation is marked `(해석)`. The source page or file is read-only.

## Usage

```
/digest https://www.notion.so/...
/digest https://example.com/long-article 우리 팀에 적용할 부분만
```

Or just paste a link and say "이거 소화하기 좋게 정리해줘". If you state why you are reading, the digest puts the matching parts first.

The digest is shown in chat. Ask to visualize it ("시각화해줘", "위젯으로") and it is drawn as an inline widget next to the chat: the one line, key numbers, and TL;DR stay open, the other sections fold, and before/after numbers become bars and dumbbells. The widget uses the Pretendard font for Korean and follows [widget.md](./skills/digest/widget.md). Inline widgets need the Claude desktop app.

Ask to save it and it goes to a new Notion page (you choose where) or to `digests/<slug>.md`.

## Requirements

- Notion pages: the `notion-blocks` skill or the Notion MCP connector. Chart images need the Notion MCP connector, because `notion-blocks` drops the URLs of uploaded images
- Web pages: WebFetch, or a browser tool such as Claude in Chrome for pages behind a login

## Install

```bash
bash scripts/install-claude.sh
```

This copies `skills/digest` to `~/.claude/skills/digest`.
