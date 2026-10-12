# general-novel-skill

An agent skill for writing long-form Chinese web fiction. Prose and story state are committed together,
every tracked fact must cite the chapter text it came from, and the de-slop pass is built to leave good
sentences alone. Works with Claude Code, Codex, Cursor, OpenCode and other clients that load skills.

The skill itself, its reference files and its sample book are written in Chinese. 中文说明见 [README.md](README.md)。

![Local dashboard: chapters, word counts, gates and foreshadowing](assets/screenshots/dashboard.png)

## What it is for

- **Continuity over hundreds of chapters.** Each chapter is a transaction: the prose and five tracking
  tables (chapter summaries, character state, foreshadowing ledger, timeline, pacing quota) are staged,
  validated and committed together, with rollback on failure. Each tracking change carries a verbatim
  excerpt that a script checks against the chapter.
- **Prose that does not read as machine-written.** Seven gates locate stock phrasing; edits are decided by
  what a sentence does, not by word frequency. The checker also flags the usual over-corrections:
  staccato fragments, one-line paragraphs, clusters of stock body reactions, and a narrator who explains
  the scene after it has played.
- **Picking a serial back up.** One command reports the last committed chapter, what is owed, and whether
  the next outline exists.
- **Outlines that stay put.** A chapter cannot enter the writing flow until its outline is locked.

## Quick start

```bash
npx skills add xiaoyuCR7/general-novel-skill
```

Then ask, in Chinese, for a trial chapter. The skill asks for whatever is missing, proposes a short
outline, and writes a draft with one mechanical self-check. Say 「开书」 when you want the full,
transactional workflow.

In Claude Code you can install it as a plugin and get slash commands:

```text
/plugin marketplace add xiaoyuCR7/general-novel-skill
/plugin install general-novel-skill@general-novel-skill
```

| Command | Purpose |
|---|---|
| `/general-novel-skill:try` | Draft one chapter without creating a project |
| `/general-novel-skill:init` | Start a book: positioning, setting, outlines |
| `/general-novel-skill:write` | Write the next chapter and commit prose with tracking |
| `/general-novel-skill:deslop` | Minimal revision of stock phrasing |
| `/general-novel-skill:review` | Diagnose a chapter without editing it |
| `/general-novel-skill:resume` | Recover after an interruption |

## See it

- [`demo/看见倒计时的骑手/`](demo/看见倒计时的骑手/README.md): a two-chapter sample serial written through
  the full workflow, with outlines, setting files and tracking tables.
- [`demo/deslop-before-after/`](demo/deslop-before-after/README.md): one scene before and after revision,
  with the checker output and a reason for every change.

## Scope and limits

- 34 genre cards and platform notes for the major Chinese fiction platforms, loaded on demand.
- The scripts use only the Python standard library (3.8+). They verify mechanical contracts; they do not
  judge literary quality, and a passing gate is not a claim that a chapter is good.
- The sample book is two chapters long and was drafted and checked by a single agent. It shows the
  workflow, not long-run consistency.

License: MIT.
