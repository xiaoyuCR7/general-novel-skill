---
description: 写章：按章事务写下一章或指定章，正文与追踪一起提交
argument-hint: "[章号，留空为下一章]"
---

使用 general-novel-skill，先运行 `python scripts/resume.py "{book}"` 查欠账，再按
`references/workflow/chapter-loop.md` 与 `references/craft/scene-rendering.md` 写章。
章纲状态须为「已锁定」；blocking 清零、追踪变更核对过正文出处后才提交。
完成后简报实际产物、门禁状态、未决风险和下一个决策点。

要写的章节：$ARGUMENTS
