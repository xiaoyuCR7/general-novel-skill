# 全自动写书调度（auto-write）

托管模式：把「写 N 章」整件事交给调度器，自动完成从会话恢复到进度报告的全流程。
单章逻辑完全不变（仍走 `chapter-loop.md` 的 Step 0–8），本文件只管「多章自动调度的
状态机、断点续写、幂等缓存、停止条件、进度报告」。

托管只省掉「逐章向作者报告并等待确认」，不放宽任何一条核心契约：

- 每一章都是一次完整的章事务（prepare → stage 写作 → 门禁/审核 → validate → commit）。
  正文和追踪五表只通过 commit 一起入库，调度器不直接写 `正文/` 或 `追踪/` 下的正式文件。
- 一章是否写完，以 `resume.py` 报告的事务与门禁状态为准，不以调度器自己的缓存为准。
- 任何一章出现 `gate_blocked`、`transaction_incomplete`、`state_conflict`、`outline_missing`
  或 `outline_underfilled`，托管立即停止并报告，不跳过这一章去写下一章。
- 托管不替作者做决定：不锁纲、不补主线、不改设定、不处理超期伏笔的去留。

## 目录

- 何时用这个
- 与 daily-batch.md 的关系
- 三阶段调度
- 状态机
- 状态持久化
- 执行锁
- 断点续写
- 每章流程
- 进度报告
- 终止条件
- 停止后的恢复
- 幂等性保障
- 退化防护（托管特有）
- 托管纪律
- 实现方式
- 与其他工作流的关系

## 何时用这个

- 用户说「托管写完」「自动日更」「帮我连续写 N 章」「睡一觉起来写 10 章」
- 适用前提：书籍工程已开书（`book-init.md` 走完）；目标范围内每一章的章纲都已就位并且
  「已锁定」，或者作者在启动托管时明确说了按未锁定的提案直接写（记录原话，见
  `chapter-loop.md` Step 3B）。
- 托管范围只到最后一章满足上述条件的章纲为止。作者要求的章数超出这个范围时，先说明
  实际能写到第几章、还缺哪些章纲，由作者决定先补纲还是缩短范围。
- 不适用：开书首章、卷末大高潮、关键转折章——这些质量优先于数量，走单章
  `chapter-loop.md` 或 `beat-pipeline.md`，不进托管。

## 与 daily-batch.md 的关系

| 关注点 | daily-batch.md | auto-write.md |
|---|---|---|
| 触发方式 | 人工触发，每轮 2–3 章 | 托管触发，连续写 N 章 |
| 会话边界 | 单会话内完成 | 跨会话（断点续写） |
| 状态持久化 | 无（会话内串行） | 有（plan / state / cache 三个文件） |
| 进度报告 | 批末一次 | 每 5 章一次 + 终止报告 |
| 停止机制 | 人工判断 | 任一章被阻断即自动停止并报告 |
| 人工介入 | 每章都向作者报告 | 仅停止/终止时通知 |

简单说：`daily-batch` 是「人在边上盯着的批量」，`auto-write` 是「人去睡觉的托管」。
托管期间调度器代替人做「这一章提交了，要不要接着写下一章」的决策，不代替人做
「这一章没过怎么办」「改主线/改设定」的决策——遇到这些一律停下来等人工。

## 三阶段调度

托管模式分 plan / run / report 三个阶段。状态机的 PLANNING 态对应 plan 阶段，
WRITING、GATE、COMMIT 态对应 run 阶段，REPORTING 态对应 report 阶段。

### plan 阶段（计划）

**输入**：简介/总纲（`大纲/总纲.md`）+ 当前进度（`resume.py` 输出）+ 目标章数。
**动作**：
1. 跑 `resume.py`。有未完成的事务先按报告里的命令 recover；有其他欠账按「每章流程」
   Step 0 的规则处理，处理不了就停。
2. 解析总纲的分卷规划表，计算卷章结构（每卷章数、总字数预算）。
3. 逐章确认目标范围内的章纲是否就位、是否已锁定，据此确定实际托管范围。
4. 输出计划文件 `{book}/.auto-write/plan.json`。

**plan.json 结构**：

```json
{
  "book_dir": "D:/存放/小说/我的书",
  "plan_at": "2026-07-28T10:00:00",
  "target_chapters": 10,
  "start_chapter": 25,
  "end_chapter": 29,
  "volume_structure": [
    { "volume": 2, "chapters": "20-35", "title": "龙城风云", "total_words": 48000 }
  ],
  "chapters_missing_outline": [30, 32],
  "chapters_unlocked_outline": [31],
  "unlocked_outline_authorization": null,
  "debt_check": { "passed": true, "issues": [] },
  "estimated_words": 15000
}
```

上例中作者要 10 章，但第 30 章缺纲，所以 `end_chapter` 停在 29，并在启动时告诉作者。
`unlocked_outline_authorization` 只在作者明确授权按提案写时填入授权原话，否则为 null，
未锁定的章不进入范围。plan.json 是一次性的计划快照，run 阶段不修改它。

### run 阶段（执行）

**输入**：plan.json + state.json（断点续写时）。
**动作**：对范围内的每一章执行一次完整的单章循环（见「每章流程」），commit 成功后
更新 state.json 和 cache.json，再进入下一章。
**自动停止**：遇到终止条件（见「终止条件」）即停止 run 循环，进入 report 阶段。

每章不可跳过的安全约束，全部由 `chapter-loop.md` 定义，托管不另立一套：

- prepare 之前的节奏预检（`rhythm_guard.py` 只读预检）。
- stage 上的 `check_text.py` 与 `rhythm_guard.py` 机器门禁。
- `chapter_transaction.py validate`（追踪格式、正文与节奏门禁、实体索引、文件哈希）。
- 主 Agent 的语义自查与交付前场景审计；通过后才运行带 `--self-review-confirmed` 的 commit。

### report 阶段（报告）

**输入**：state.json + cache.json + 最新的 `resume.py` 输出。
**动作**：生成进度报告（每 5 章一次 + 终止时终局报告）。
**输出**：报告文本（输出到对话，并把 `last_report_chapter` 写入 state.json）。

plan 是一次性的，run 是循环的，report 是周期性的。断点续写时 plan.json 已存在，
但仍要重新跑 `resume.py` 核对进度，再进入 run。

## 状态机

```
        ┌──────────┐
        │   IDLE   │ ← 初始/终止态
        └────┬─────┘
             │ 启动指令（目标章数 N）
             ▼
        ┌──────────┐
        │ PLANNING │ resume.py 无欠账、章纲就位且已锁定
        └────┬─────┘
             │ 前提就绪
             ▼
        ┌──────────┐
        │ WRITING  │ 预检 → prepare → 在 stage 写正文与追踪五表
        └────┬─────┘
             ▼
        ┌──────────┐  有 blocking/P0（两轮额度内）
        │   GATE   │ ───────────────────────────► 定向修复后重验
        └────┬─────┘
             │ blockers 为零           两轮用尽仍有 blocking/P0
             ▼                         ────────────► STOPPED（gate_blocked）
        ┌──────────┐
        │  COMMIT  │ validate → 语义自查 → commit
        └────┬─────┘
             │ 成功                    失败/冲突
             ▼                         ────────────► STOPPED（按错误码）
        ┌──────────┐
        │REPORTING │ 更新 state/cache；到周期则输出进度报告
        └────┬─────┘
             │ 未达终止条件 → 回 WRITING 写下一章
             │ 达终止条件
             ▼
        ┌──────────┐
        │   IDLE   │ 写终局报告，释放锁
        └──────────┘
```

### 各状态职责

- **IDLE**：无任务。检测到 state.json 存在且状态非 IDLE → 进入断点续写（见下节）。
- **PLANNING**：执行 plan 阶段。前提不满足就不进入 WRITING。
- **WRITING**：走 `chapter-loop.md` Step 0–4。正文和追踪变更只写在事务的 stage 里，
  此时正式工程没有任何变化。
- **GATE**：`chapter-loop.md` Step 5–6 与交付前场景审计。blocking/P0 在两轮共享额度内
  定向修复；额度用尽仍未清零 → 报 `gate_blocked`，保留 checkpoint 与 pending draft，
  进入 STOPPED。P1/P2 与 advisory 不阻断，按 `chapter-loop.md` 的规则集中处理一次并写进报告。
- **COMMIT**：`chapter-loop.md` Step 7。validate 通过且语义自查真实完成后 commit。
  validate 或 commit 报错时不重试绕过，按错误码进入 STOPPED。
- **REPORTING**：commit 成功之后才更新 state.json 与 cache.json。每写完 5 章输出一次
  进度报告；终止条件满足时输出终局报告。
- **STOPPED**：state.json 记录 `stop_reason` 与 `blocked_chapter`，释放执行锁，等待人工。
- **IDLE（终止）**：终局报告输出后，state.json 标记 IDLE，释放执行锁。

## 状态持久化

三个调度文件和执行锁都放在书籍目录下以点开头的隐藏目录 `{book}/.auto-write/` 里。
章事务在 commit 时会比对整本书所有非隐藏文件的哈希，prepare 之后往 `追踪/` 等目录
新增或改动任何文件都会被判为 `state_conflict`；隐藏目录不计入这个快照，所以调度状态
只能写在这里，不能写进 `追踪/`。

### plan.json

plan 阶段输出的一次性计划快照，路径 `{book}/.auto-write/plan.json`，结构见上文。

### state.json

路径 `{book}/.auto-write/state.json`。调度器在 REPORTING 与 STOPPED 时写入：

```json
{
  "status": "WRITING",
  "book_dir": "D:/存放/小说/我的书",
  "target_chapters": 10,
  "start_chapter": 25,
  "end_chapter": 29,
  "last_committed_chapter": 27,
  "written_count": 3,
  "first_pass_rate": 0.67,
  "repair_rounds": { "26": 1, "28": 0 },
  "stop_reason": null,
  "blocked_chapter": null,
  "start_time": "2026-07-27T10:00:00",
  "last_checkpoint_time": "2026-07-27T11:30:00",
  "last_report_chapter": 25
}
```

字段说明：
- `status`：IDLE / PLANNING / WRITING / GATE / COMMIT / REPORTING / STOPPED
- `target_chapters`：作者要求的章数；`end_chapter` 是 plan 确定的实际范围终点
- `last_committed_chapter`：最后一个 commit 成功的章号；`written_count` 是本轮已提交章数
- `first_pass_rate`：本轮未动用修复额度就通过的章数 / 已提交章数
- `repair_rounds`：每章已用的 blocking/P0 修复轮次（键=章号），单章上限 2。这是
  `chapter-loop.md` 规定的同章同任务共享额度，断点续写、换会话都不清零
- `stop_reason`：停止时的错误码或原因（如 `gate_blocked`、`outline_missing`、`user_stop`）
- `blocked_chapter`：停在哪一章
- `last_report_chapter`：上次进度报告对应的章号

### cache.json

路径 `{book}/.auto-write/cache.json`。只记录已经 commit 成功的章，供进度报告汇总用：

```json
{
  "chapters": {
    "25": {
      "title": "第025章_龙城惊变",
      "word_count": 3120,
      "repair_rounds": 0,
      "committed_at": "2026-07-27T10:25:00",
      "summary": "主角识破陷阱，与反派正面交锋，埋下神秘符文伏笔。"
    },
    "26": {
      "title": "第026章_暗流涌动",
      "word_count": 2980,
      "repair_rounds": 1,
      "committed_at": "2026-07-27T10:55:00",
      "summary": "配角线推进，揭示反派背景，为下一章高潮铺垫。"
    }
  }
}
```

cache 是报告用的摘要，不是进度的权威来源。它与 `resume.py` 的结果不一致时以
`resume.py` 为准，并在报告里指出不一致。

## 执行锁

`{book}/.auto-write/lock` 防止两个托管实例同时调度同一本书。启动时写入：

```
session: {本次会话标识}
started: 2026-07-27T10:00:00
```

- 启动 PLANNING 前检查锁文件是否存在。存在 → 询问用户「另一实例可能正在运行，强制接管还是退出？」
- 用户选「强制接管」→ 覆盖锁文件，继续。选「退出」→ 停止。
- 终局报告输出后或进入 STOPPED 后，删除锁文件。
- 这把锁只管调度器之间互斥。章事务自己的锁与 journal 由 `chapter_transaction.py` 管理，
  两者互不替代。

## 断点续写

会话中断后重新进入时，先跑 `resume.py`，再看 state.json：

1. **`resume.py` 报告有未完成的事务**：不管 state.json 写的是什么，先按报告里的命令
   recover。recover 会放弃那一章未提交的 stage，正式工程回到上一章提交后的状态。
2. **state.json 不存在**：全新任务，正常启动。
3. **state.json 存在且 `status == IDLE`**：上一轮已正常结束，清理后启动新任务。
4. **state.json 存在且 `status == STOPPED`**：走「停止后的恢复」。
5. **其余非 IDLE 状态**：上一轮被中断。向用户报告并让其选择：

   ```
   检测到未完成的托管任务：
   - 目标：从第 25 章起写到第 29 章
   - 进度：已提交 3 章（第 25–27 章），第 28 章写作中断、未提交（已 recover）
   - 第 28 章已用修复轮次：0 / 2
   - 上次断点：2026-07-27 11:30

   选择：
   [1] 从第 28 章继续托管
   [2] 重新规划范围后再托管
   [3] 放弃托管，手动接手
   ```

「从哪一章继续」始终取 `resume.py` 报告的下一章，不允许凭缓存跳过一个没有提交的章。
中断章已经用掉的修复轮次沿用 state.json 的记录。

## 每章流程

托管模式下每章完整走 `chapter-loop.md` 的 Step 0–8，不做任何跳步。差异只在「谁来确认」：

1. **Step 0 欠账门**：跑 `resume.py`。托管只自动处理不需要作者做决定的欠账——recover
   未完成的事务、把已提交章漏记的追踪条目按 `revision.md` 的五表规则通过章事务补上。
   上一章门禁未通过、🔴 超期伏笔、来源冲突这类需要取舍的欠账，停止并报告。
2. **Step 1 读章纲**：章纲缺失 → `outline_missing`，停止。章纲未锁定且没有作者的启动授权
   → 停止。托管不自行补纲、不自行改「状态」行。
3. **Step 2–3 上下文与章意图**：required 缺失或超预算、beat 预算不足
   （`outline_underfilled`）、节奏预检 FAIL，都在 prepare 之前停止并报告。
4. **Step 3B–4 事务与写作**：prepare 后只在 stage 里写正文和追踪五表。调度文件写在
   `{book}/.auto-write/`，章意图与审查报告写在工程外工作目录。
5. **Step 5–6 门禁与自查**：blocking/P0 最多修两轮，计入 `repair_rounds`。两轮后仍有
   blocking/P0 → `gate_blocked`，停止，不提交、不写下一章、不改标成「有条件通过」。
   P1/P2 不阻断：能并入当轮就并入，否则写进本章报告留给作者。
6. **Step 7 提交**：validate → 语义自查与场景审计 → commit。任何一步报错即停止。
7. **Step 8 报告**：不逐章向用户报告，把本章摘要写入 cache.json；每 5 章输出一次进度报告。
   本章的假设、冲突裁决、未处理的 P1/P2 仍要写进工程外的本章报告，供作者事后复核。

## 进度报告

### 每 5 章报告模板

```
========== 托管进度报告（第 {start}–{current} 章）==========
【卷】第 X 卷 {卷名}
【当前章】第 {current} 章 {标题}
【已提交】{written_count} / {范围内章数} 章（作者要求 {target_chapters} 章）
【字数】本轮累计 {total_words} 字，平均 {avg_words} 字/章
【门禁】一次通过率 {first_pass_rate}%，动用修复额度 {repaired} 章
【未处理的 P1/P2】{count} 条（见各章报告）
【伏笔】活跃 {active} 条，超期 {overdue} 条
【状态】{status}
下次报告：第 {current + 5} 章后
======================================================
```

### 终局报告模板

```
############## 托管结束 ##############
【目标】从第 {start} 章起写 {target} 章，实际范围到第 {end} 章
【结果】{written_count} 章已提交（第 {start}–{last_committed} 章）
【终止原因】{正常完成 / 用户手动停止 / gate_blocked / 章纲缺失或未锁定 / 其他错误码}
【停在】第 {blocked_chapter} 章：{具体命中项与两轮修复结果；正常完成则写「无」}
【总字数】{total_words} 字
【门禁】一次通过率 {first_pass_rate}%，共 {total_repairs} 轮修复，涉及 {repaired} 章
【伏笔台账】新埋 {planted} 条，回收 {resolved} 条，超期 {overdue} 条
【待作者决定】
  - {问题1}
  - {问题2}
【建议】{下一步操作建议}
######################################
```

报告只写实际发生的事：没有提交的章不计入「已提交」，没有跑的检查不写成通过。

## 终止条件

满足以下任一条件，调度器停止并输出终局报告：

1. **正常完成**：范围内的章全部 commit 成功。
2. **用户手动停止**：用户说「停」「停止托管」「暂停」。当前章已经 prepare 的，要么走完
   到 commit，要么 recover 放弃，不留下未完成的事务；向用户说明选了哪一种。
3. **门禁阻断**：某一章两轮修复后仍有 blocking/P0（`gate_blocked`）。
4. **事务异常**：`transaction_incomplete`、`state_conflict`、validate 或 commit 报错。
5. **章纲问题**：`outline_missing`、章纲未锁定且无授权、`outline_underfilled`，或者继续写
   需要改主线、改设定。
6. **伏笔超期**：`resume.py` 报告伏笔台账出现 🔴 超期项。回收、延期还是废弃由作者决定。
7. **节奏预检 FAIL**：A/B/C 配额越界、事件冷却违规或连续快档超限。调整章纲的节奏声明
   需要作者授权。
8. **必需上下文问题**：`required_context_missing` 或 `required_context_over_budget`。
9. **文风退化**：见「退化防护」。

停止时的报告要写清：停在哪一章、命中了什么、两轮修复各改了什么、判断是「写作层问题」
（改正文可解）还是「结构层问题」（需改纲或改设定），以及建议的处理方向。

## 停止后的恢复

停止后 state.json 的 `status` 为 `STOPPED`，等待人工处理：

1. 作者排查原因并处理：补纲或锁纲、调整节奏声明、处理超期伏笔、修正设定或禁用词表，
   或者亲自决定被阻断那一章怎么改。
2. 重新启动托管时，先跑 `resume.py`，再向作者确认：

   ```
   上次托管停在第 {X} 章，原因：{stop_reason}
   {上次报告的命中项}

   是否已处理？[1] 已处理，从第 {X} 章继续 [2] 手动接手
   ```

3. 用户确认「已处理」→ 从 `resume.py` 报告的下一章继续。

被 `gate_blocked` 的章，两轮自动修复额度已经用完，重新启动托管不会让它清零。只有作者
明确给出新的修改指示（等于一次新的修订任务）时，才按 `revision.md` 重新开事务处理这一章。

## 幂等性保障

断点续写或重试时，哪些章已完成由 `resume.py` 判定：

- 已提交且门禁记录与正文哈希一致的章 → 跳过。
- 正文在过闸后被改动过的章 → 属于欠账，按 Step 0 停止并报告，不由托管决定重写还是保留。
- 没有提交的章 → 正常写；之前中断留下的 stage 已在 recover 时放弃，不从半成品续写。

cache.json 只用来补全报告里的标题、字数与摘要。幂等检查在 PLANNING 阶段执行。

## 退化防护（托管特有）

托管连写时间最长、章数最多，文风退化风险最高。在 `daily-batch.md` 的退化防护基础上加强：

1. **每 5 章跑一次文风指纹对比**（`style_fingerprint.py compare`），与文风锚对比。
   漂移 > 15% → 在进度报告中标记警告，不立即停（可能是某一章的个别漂移）。指纹是观察
   信号，按 `chapter-loop.md` 的规则对照作者认可样段判断，不强行回调。
2. **连续 2 份报告（10 章）漂移都 > 15%** → 停止，报告文风退化趋势。
3. **每 10 章做一次跨 Agent 审核**（见 `cross-review.md`），托管模式下自动触发。
   审核发现已提交章的 P0 → 停止并报告；已提交章的修改走 `revision.md`，由作者授权。

退化防护的基线：开书前 10 章的 AI 味分数均值 + 文风六维指纹，存在 `设定/文风锚.md`
的量化基线部分。

## 托管纪律

- **不越权决策**：托管只做「这一章提交了，接着写下一章还是到此为止」「报告还是继续」。
  不做「改主线」「改设定」「弃伏笔」「换题材」「锁纲」「带着没过的门禁往下写」。
- **不跳步**：每章完整走 Step 0–8 和章事务。
- **不并发**：同一本书同一时间只允许一个托管实例（执行锁保障）。
- **不留半成品**：中断的章 recover 后重写，不从未提交的 stage 续写。
- **不虚报**：没有提交的章不算完成；机器门禁通过不等于语义审查通过，两者分别如实报告。

## 实现方式

本文档是协议规范，不是外部调度脚本。模型按本协议操作，通过读写 `{book}/.auto-write/`
下的 plan.json、state.json、cache.json 三个文件实现状态管理和断点续写。

- **plan/run/report 三阶段**由模型按本协议的步骤执行，不依赖外部编排引擎。
- **断点续写**以 `resume.py` 为进度依据，state.json 提供调度上下文。
- **自动停止**靠模型在每章每一步检查终止条件，不依赖外部监控进程。

每次状态转换都要更新 state.json，确保会话中断后能恢复调度上下文。

## 与其他工作流的关系

| 场景 | 用哪个 |
|---|---|
| 人工日更 2–3 章 | `daily-batch.md` |
| 托管连写 N 章 | `auto-write.md`（本文件） |
| 单章精写 | `chapter-loop.md` |
| 复杂章拆 Beat | `beat-pipeline.md` |
| 关键章团队写 | `editorial-team.md` + `assets/agents/` |
| 卷级评审 | `review-rubric.md` |
| 每 10 章跨 Agent 审核 | `cross-review.md`（托管模式自动触发） |
| 大修 | `revision.md` |

托管模式是「调度器」角色：它调用 `chapter-loop.md`（单章逻辑与章事务）和 `resume.py`
（进度与欠账检查），自身只管状态机和「继续还是停」。
