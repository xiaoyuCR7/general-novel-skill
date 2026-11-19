# general-novel-skill

写长篇网文与短篇小说的 agent skill（**v8.2.0**）：长篇正文和设定一起提交，追踪表里的每条事实都查得到正文出处；
短篇走五段式、以情绪和反转收尾。去 AI 味不把好句子改坏。适用于 Claude Code、Codex、Cursor、OpenCode 等支持 skill 的客户端。

English version: [README_EN.md](README_EN.md)（英文简介；skill 本体、参考文档与示例作品均为中文）

## 五分钟上手

还没安装？直接跳到文末「安装」一节，一条命令即可装好。装好后回来，直接说人话，不必记命令。

1. **先看手感（没有工程）**  
   「先写一章看看：都市异能，外卖骑手能看见别人头顶的寿命倒计时。」  
   按 [`references/workflow/quick-start.md`](references/workflow/quick-start.md)：五个问题 → 迷你章纲 → 草稿，做一次机器自检。第 1–3 章同时用 [`references/craft/opening.md`](references/craft/opening.md) 的开篇硬目标（约 300 字进入压力、约 1000 字出现异常、三章内至少一次当面冲突）。交付标「草稿，未入事务」。
2. **正式开书**  
   「开书：男频玄幻，发番茄。」  
   走 [`references/workflow/book-init.md`](references/workflow/book-init.md)。平台章长和开篇偏好见 [`references/platforms/platform-guide.md`](references/platforms/platform-guide.md)。
3. **已有书，写下一章**  
   「写第 N 章。」  
   先 `python scripts/resume.py "{书名目录}"`，再走 [`references/workflow/chapter-loop.md`](references/workflow/chapter-loop.md)。连载章尾按 [`references/craft/scene-rendering.md`](references/craft/scene-rendering.md) 停在能引出问题的威胁、抉择或物证，招式在 [`references/craft/hooks.md`](references/craft/hooks.md)。

决定试写要连载时再说「开书」。共同不变量（事务、停止点、失败码）在 [`references/workflow/session-invariants.md`](references/workflow/session-invariants.md)，入口路由在 [`SKILL.md`](SKILL.md)。

## 它解决什么

- **写着写着吃书**：每章是一次事务，正文与章节摘要、角色状态、伏笔台账、时间线、节奏配额一起提交，
  失败自动回滚；追踪表的每条变更都要附一段能在正文里逐字找到的原文。
- **一股 AI 味，越改越干**：7 道闸口定位套路句式，按“这句有没有用”判断改不改；
  同时防住改过头的另一种腔调（碎句、一行一段、成片的身体反应套词、叙述者替读者总结）。
- **断更之后接不上**：一条命令说清写到第几章、欠什么账、下一章章纲在不在。
- **大纲被悄悄改写**：章纲不锁定进不了写作流程；锁定后只增不改。

## 看效果

示例书 [`demo/看见倒计时的骑手/`](demo/README.md) 是用完整流程写出来的五章连载，
正文、章纲、设定和五张追踪表都在里面。第 1 章里的一段：

> “阿姨，把链子摘了，我背您下去。”
>
> “我不去。你们这号人社区讲过，先说人有病，再往外头领。”她攥着衣裳的手没松，“救护车拉一趟多少钱你知道吗？”
>
> “不知道。反正比火化便宜。”

去 AI 味的前后对照（同一场戏，blocking 9 → 0，附逐处修改理由和复现命令）见
[`demo/deslop-before-after/`](demo/deslop-before-after/README.md)。

## 短篇创作

除长篇连载外，skill 也写**完整短篇**（4000–30000 字），面向知乎盐言、番茄短篇、七猫短篇等平台。
短篇不是长篇的缩水版，是另一种叙事形态：核心是「一个情绪、一个反转、一次结算」，
走 [`workflow/short-story-loop.md`](references/workflow/short-story-loop.md) 的**五段式**
（开头钩子 → 铺垫升级 → 矛盾爆发 → 反转 → 结算收尾），按目标字数分配每段预算。

- **先定情绪再动笔**：意难平 / 甜 / 虐 / 爽 / 恐，情绪与目标平台要匹配（如「虐」配番茄短篇会投错胎）。
- **人物求立不求全**：每人三个标签（核心欲望 + 阻力 + 反差），不做长篇式完整小传。
- **结尾句默认交付**：正文写完必点睛，按 [`craft/short-story-ending.md`](references/craft/short-story-ending.md) 写
  点睛句（正文内，≤1 句）/ 彩蛋句 / 碎碎念；铁律是「用动作收尾，不升华」，写总结等于毁掉整篇。
- **平台适配**：字数区间与爽度基调按平台加载（盐言 / 番茄短篇 / 七猫短篇），不污染长篇主链。

对话里说「写一篇番茄短篇」「写个盐言故事」即可触发。

## 支持范围

核心只装通用写作工艺（工作流 + 模板 + 禁区清单），题材规则（34 题材 + 九件事正文层规范）与平台规则
（长篇番茄/起点/晋江/飞卢 + 短篇知乎盐言/番茄短篇/七猫短篇）做成可插拔的参考文件，按需加载。

玄幻、修仙、武道、系统等题材按作品内设定创作与审核，允许复生、瞬移、无代价奖励等超现实机制；
不把现实法律或科学作为剧情可行性的门槛。题材惯例服从作者路线，保留内部因果和能力条件的一致性。
具体见 [虚构世界创作规则](references/craft/fictional-world.md)，6个补充场景见 [评测集](evals/README.md)。

## 能力证据边界

### 已实现并自动验证

- 轻量意图路由、章意图契约、场景渲染、大纲不足时的 `outline_underfilled` 停止协议，以及正文与追踪的事务边界。
- 本地 Dashboard 的路径隔离、revision 冲突保护、原子保存、备份和可恢复删除。
- 47 个顶层 Python 脚本、121 份 reference（50 份 craft、31 份 workflow）、24 个 MCP tool；测试收集数由 `skill.json` 与发布契约核对。平台不支持的符号链接测试可能跳过，运行器分别报告通过、失败与跳过。
- skill 契约、公开版本一致性、工作流闭环和关键文件事务均有确定性校验。
- 限时场景的时间—行动闭环已验证：只使用合法时间来源，整体至少一项时间证据改变后续取舍、分工、顺序、风险判断或验收；主要耗时分支以授权动作中的过程进展、阻力变化或累计身体/环境反馈中的至少一项呈现窗口消耗。

### 有条件能力与降级

- 联网调研与动态平台规则依赖当次可用网络；不可用时必须标记未核验并采用本地资料回退。
- RAG、自定义 Agent 和 MCP 属于可选增强，缺失时保留本地章纲、追踪和机器门禁主链。
- 只有用户明确要求且图片工具可用时才实际生成封面；否则只交付结构化 prompt、尺寸与排版安全区，明确未生成图片。

### 建议性或人工判断

- 文学感染力、平台适配与最终封面文字仍需作者或编辑验收；脚本分数不替代审美与发布审核。
- 自动化校验只证明明确写入契约的行为，不替代真实创作样本的匿名评审与长期连载检验。

## 仓库地图

目录树和能力对照已移到 [`references/repository-map.md`](references/repository-map.md)。
脚本用法见 [`references/scripts-index.md`](references/scripts-index.md)。
入口路由见 [`SKILL.md`](SKILL.md)，共同不变量见 [`references/workflow/session-invariants.md`](references/workflow/session-invariants.md)。

## 用法速览

0. **试写**：「先写一章看看」→ 按 `workflow/quick-start.md` 走轻量模式：五个问题 → 迷你章纲 → 草稿，
   不建工程，交付标「草稿，未入事务」。第 1–3 章同时读 `craft/opening.md`。
1. **开书**：「开书：男频玄幻，发番茄」→
   先 `python scripts/init_book.py "{书名}" --genre 玄幻 --platform 番茄` 建骨架，
   再按 `workflow/book-init.md` 走完定位/契约/人物/**敏感词替换表（与世界观同步建，真实地名/机构/人物 → 全书代称）**/总纲/卷纲/章纲，
   落定读者契约与文风锚。
2. **写章**：「写第 37 章」→ 按 `workflow/chapter-loop.md` 走（第 1–3 章加 `craft/opening.md`；连载章尾用 `craft/hooks.md`）：
   先跑 `resume.py` 查欠账 → 读章纲（状态须为「已锁定」，否则 `prepare` 以 `outline_unlocked` 拒绝） → 节奏预检 → 检索上下文（必要时 `entity_index.py query` / `context_manager.py select`） → 写正文 →
   内容扩充（必要时 `content_expander.py analyze`） → 标点归一化 → 三条机器闸口 → 质量评分（`quality_score.py score`） →
   自查清单 → 更新追踪五文件 → `tracking_delta.py check` 核对每条变更的正文出处 → 跑 `validate_tracking.py` 复核 → 重建实体索引。
3. **写短篇**：「写一篇番茄短篇」→ 按 `workflow/short-story-loop.md` 走短篇五段式，
   定稿后**默认加结尾句**（简短，一句顶满），按 `craft/short-story-ending.md` 写点睛句/彩蛋句/碎碎念。
4. **拆文**：「拆解这本对标书」→ 按 `workflow/deconstruct.md` 走，产出存入 `对标/{书名}/`。
5. **扫榜**：「帮我扫榜看趋势」→ 按 `workflow/market-scan.md` 走，产出存入 `参考资料/扫榜报告.md`。
6. **带旧稿接手**：「我有几十章旧稿」→ `workflow/import-book.md`。
7. **查平台规则**：题材卡「平台适配要点」节 + `platforms/platform-guide.md`。

> Windows 提示：若系统里 `python3` 指向微软商店占位 stub（运行无输出），改用 `python` 调用脚本。

## 本地可编辑 Dashboard

```bash
python scripts/dashboard.py "书籍工程目录"
# 或：python novel-cli.py dashboard "书籍工程目录"
```

Dashboard 默认仅绑定 `127.0.0.1`，可查看状态、章节、质量趋势、伏笔台账，并编辑
`.md/.txt/.json/.yaml/.yml/.toml/.ini` 文本文件。浏览器每次打开文件都会取得 SHA-256
revision；保存或删除必须提交同一 revision。若文件已被终端、同步软件或另一页面修改，API 返回
`409 Conflict`，不会覆盖磁盘内容，也不会清空浏览器里的未保存缓冲区。
异步加载期间继续输入会取消切换；旧文件的保存/删除响应不会改变新打开的文件。写请求串行执行，
保存期间新输入仍保留为未保存修改；删除期间的新输入保留在编辑器，可保存重建文件。

成功保存前，旧文件会备份到同目录的 `.文件名.dashboard-backup`；新内容先写入同目录临时文件，
执行 `flush` + `fsync` 后再由 `os.replace` 原子替换。删除不会永久擦除文件，而是移动到书籍工程的
`追踪/.dashboard-trash/`，可手动检查并恢复。

可用 `--host` 显式改为非回环地址，但这会把编辑服务暴露到网络。Dashboard 没有身份认证或 TLS；
改动监听地址后不能视为网络安全服务，只应在可信隔离网络中临时使用。请求体上限为 2 MiB，
路径穿越、越界符号链接和非白名单扩展会被拒绝。

所有页面/API 都检查 Host（主机名与实际端口）；默认仅接受 loopback 主机名。显式非回环
`--host` 只接受配置的主机名或接收连接的本机接口地址，不能借任意 DNS 名访问。
POST/DELETE 还要求严格同源 Origin 和每次服务启动独立的 `X-Dashboard-Token`。
浏览器自动完成握手；脚本客户端须先用合法 Host 请求 `GET /api/session` 取得 `token`，
再在写请求中同时发送 `Origin: http://合法主机:端口`、`X-Dashboard-Token: token` 和 JSON 请求体。
跨源或非法 Host 不能取得令牌，缺少/错误凭据返回结构化 `403`；这防护来源伪造，**不是用户身份认证**。
非法 UTF-8 内容（包括 JSON 孤立代理字符）或非法编码路径返回 `400`，不会创建备份或改动文件。

前端行为测试直接执行发布的 HTML 内联脚本，可用 `node scripts/tests/dashboard_frontend.test.js`
单独运行；`test_dashboard` 也会自动调用（无 Node 时明确跳过）。使用 Node 18+ 的本机或 CI 可运行，
不需 npm 安装依赖。

## 测试套件（scripts/tests/）

`scripts/tests/` 是核心脚本与发布契约的测试套件，纯标准库（unittest）。默认 runner 全量运行；收集数由 `skill.json` 与发布契约自动核对，跨平台流水线另做多版本冒烟验证。下列为代表性模块：

- `test_common.py`（36）— common.py 共享工具函数
- `test_config.py`（14）— config.py 配置常量
- `test_check_text.py`（23）— check_text.py 7 Gate 闸口
- `test_novel_flow.py`（16）— novel_flow.py 写作流程编排
- `test_context_manager.py` — 上下文预算、关键段落召回及来源核验
- `test_source_materialize.py` — 原稿字节与会话字符串保真、拒绝覆盖
- `test_resume.py` — 原生/外稿/空/未知/未完事务的只读分流
- `test_run_tests.py` — 测试结果的通过、失败与跳过分类
- `test_static_check.py`（19）— static_check.py 静态代码质量
- `test_benchmark.py`（16）— benchmark.py 性能基准
- `test_rhythm_guard.py`（18）— rhythm_guard.py 节奏配额
- `test_entity_index.py`（16）— entity_index.py 实体索引
- `test_outline_anchor.py`（16）— outline_anchor.py 大纲锚点

```bash
# 运行全部测试
python scripts/tests/run_tests.py

# 运行指定模块
python scripts/tests/run_tests.py test_common test_check_text
```

`run_tests.py` 是测试运行器，逐模块及末尾分别汇总通过、跳过和失败；skip不计入实际执行通过，
也不会单独令整套测试失败。退出码 0 无失败 / 1 有失败 / 2 参数错误。详细原因查看pytest或unittest报告。

## 编辑团队（assets/agents/）

`references/craft/editorial-team.md` 是方法论，`assets/agents/` 是让它真正跑起来的四个
agent 定义文件 + 部署/降级/防死循环协议。

- `planning-editor.md`：策划主编，读章纲/人物卡/追踪文件，产出 Chapter Brief。
- `novelist.md`：写作特工，只接收 Brief，只输出 `NOVEL_TEXT_START...NOVEL_TEXT_END` 之间的纯正文。
- `anti-ai-editor.md`：反AI编辑，对正文执行 7 Gate 检测 + 两遍式润色，输出报告 + 净化后正文。
- `consistency-reviewer.md`：连载核实官，核查事实冲突/伏笔断线/角色属性一致性，输出 S1–S4 报告。

部署方式、模型分级建议、Fallback 链（缺 agent → 主会话内联扮演 → 单 Agent 循环，机器闸口永远可用）、
防死循环协议（单章返工上限 2 次、连续 3 章有条件通过强制人工介入）见 `assets/agents/README.md`。
日常日更走单 Agent 循环，关键章（卷末高潮/大反转/上架前）才启用团队。

## 扩展新题材

复制 `references/genres/` 下任一题材卡的栏目骨架（12 个固定栏目 + 九件事正文层规范），
撰写新卡，把别名登记进 `references/genres/INDEX.md` 即可，核心 skill 不用动。
九件事规范详见 `references/genres/GENRE-PROSE-SPEC.md`。

## 安装

general-novel-skill 支持多个 AI 客户端：Claude Code、TRAE、Cursor、OpenCode、Codex、Gemini CLI、Antigravity，以及任何支持 MCP 协议的客户端。装好后回到「五分钟上手」，在对话里直接说「开书」「写第 X 章」「写一篇番茄短篇」等即可触发（skill 描述里带触发关键词）。

### 方式一：npx 一键安装（推荐）

需要 Node.js 22.20+ 且能访问 GitHub。这条命令会自动检测你已安装的 AI 客户端，并把 skill 装到对应目录：

```bash
npx skills add xiaoyuCR7/general-novel-skill
```

常用参数：

| 参数 | 作用 |
|------|------|
| `-g, --global` | 装到用户目录（所有项目可用），默认装到当前项目 |
| `-a, --agent <名>` | 只装到指定客户端，如 `claude-code`、`cursor`、`codex` |
| `-y, --yes` | 跳过交互确认 |
| `--list` | 先看看仓库里有哪些 skill，不安装 |

例如全局装到 Claude Code、无需交互：

```bash
npx skills add xiaoyuCR7/general-novel-skill -g -a claude-code -y
```

说明：`npx skills` 会把仓库整个目录装进客户端（含 demo/docs 等非运行文件），功能完整但略显臃肿；介意体积或需要离线安装可用下面的脚本。

### 方式二：安装脚本（离线 / 精简 / TRAE 等客户端）

适用于**无网络**、想要**精简安装**（脚本只复制运行必需的 9 项，剔除 demo/docs/缓存），或使用 **TRAE、Antigravity** 等 npx skills 未明确支持的客户端。脚本会自动检测已安装的 AI 客户端并复制 skill；支持 `--tool` 指定单个平台，或 `--tool all` 安装到所有检测到的平台。

**Linux/macOS (Bash):**
```bash
bash install.sh --tool all
```

**Windows (PowerShell):**
```powershell
.\install.ps1 -Tool all
```

> 前提：已先把仓库下载/克隆到本地，在仓库目录内执行脚本。

### 方式三：手动安装

| 平台 | 安装路径 | 命令 |
|------|---------|------|
| Claude Code | `~/.claude/skills/` | `cp -R general-novel-skill ~/.claude/skills/` |
| TRAE | `~/.trae/skills/` 或项目级 `.trae/skills/` | `cp -R general-novel-skill ~/.trae/skills/` |
| Cursor | `~/.cursor/skills/` | `cp -R general-novel-skill ~/.cursor/skills/` |
| OpenCode | `~/.opencode/skills/` | `cp -R general-novel-skill ~/.opencode/skills/` |
| Codex | `~/.codex/skills/` | `cp -R general-novel-skill ~/.codex/skills/` |

### MCP Server 模式（可选增强）

任何支持 MCP 的客户端都可以通过 MCP Server 调用全部 24 个工具：

```bash
cd mcp_server
pip install mcp
python server.py
```

配置示例（Claude Desktop）:
```json
{
  "mcpServers": {
    "general_novel_skill": {
      "command": "python",
      "args": ["/path/to/general-novel-skill/mcp_server/server.py"]
    }
  }
}
```

详见 `mcp_server/README.md`。

### Agent 部署（可选增强）

编辑团队（策划主编/写作特工/反AI编辑/连载核实官）的 Agent 定义文件在 `assets/agents/`：

```bash
# Claude Code / OpenCode
cp assets/agents/*.md {书籍工程根}/.claude/agents/

# TRAE
cp assets/agents/*.md {书籍工程根}/.trae/agents/

# Codex（需转成 .toml 或内联扮演）
```

## provenance

- maintainer: 熊小雨
- version: 8.2.0
- created: 2026-07-26
- last_reviewed: 2026-10-12
- review_interval_days: 90
