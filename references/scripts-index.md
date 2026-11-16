# 脚本说明

本文件保存原先放在 README 里的脚本用法。完整目录见 `repository-map.md`。

47 个顶层脚本均为纯标准库实现并纳入 Python 3.8+ 语法检查；各 CLI 的退出码以其 `--help` 为准。
脚本通过文件名约定与 `追踪/门禁/gate_chN.json`、`追踪/entity_index.json` 等约定路径互相协作，
不依赖任何 agent，是质量底线。

R4 新增原稿保真与上下文复用核验：

```bash
python scripts/source_materialize.py "{原稿文件}" "{新目标文件}"
python scripts/source_materialize.py --text-json "{单JSON字符串文件}" "{新目标文件}"
python scripts/resume.py "{book}" --json
python scripts/context_manager.py select "{book}" --chapter {N} --json --output "{工程外上下文包.json}"
python scripts/context_manager.py verify "{book}" --context "{工程外上下文包.json}"
```

复制不改换行、BOM或末尾字符；不同目标内容拒绝覆盖，排他发布需要文件系统支持hard-link。
会话字符串物化仅证明其UTF-8表示，不声称知道上传前编码。恢复区分原生、外稿、空书、未知和
未完事务；来源变更需重建上下文，旧包无清单不假报fresh。相关人物后置约束保留为required，
预算不足停止；哈希不证明摘要或人物推断正确。完整边界见导入、任务路由及单章工作流。

R5 收敛事件名称契约：规范名与旧名均能预检、记录和校验；未知名明确报错，既有冷却不变。
旧工程缺人物卡且有明确本人状态时支持带来源说明的 `state_only`；空卡/不可读卡不回退，
补卡后旧上下文包过期。备份顺序须记录编辑前的目标状态，不能仅凭最终文件声称已证实。

### 1. check_text.py — 7 Gate 机械闸口

```bash
# 7 Gate 检测 + 字数 + 禁用词 + 毒句式 + 伏笔超期 + 量化打分 + 7类AI模式检测
python scripts/check_text.py "正文/第037章_标题.md" \
  --min-chars 2000 --max-chars 3500 \
  --ledger "追踪/伏笔台账.md" --current-chapter 37 --gate-report

# 去AI味量化分级（六级打分 → 轻/中/重建议）
python scripts/check_text.py "正文/第037章_标题.md" --deslop

# 白名单豁免词（设定/禁用词.txt 中 ! 前缀的词不检测）
python scripts/check_text.py "正文/第037章_标题.md" --whitelist "设定/禁用词.txt"
```

7 类段落级 AI 模式检测：微动作复读、抽象总结复读、套词密度、解释链密度、监控动作清单、引号强调滥用、工程词泄漏。

### 2. style_fingerprint.py — 文风指纹提取与漂移检测

```bash
# 从样章提取六维文风锚
python scripts/style_fingerprint.py extract "正文/第001章.md" "正文/第002章.md" \
  --output "设定/文风锚.md"

# 对比当前章节与文风锚
python scripts/style_fingerprint.py compare "正文/第037章.md" "设定/文风锚.md"
```

### 3. rhythm_guard.py — 节奏配额检查

```bash
# 检查本章是否越界（A/B/C 配额 + 5+1类事件矩阵 + 事件冷却 + 档位分布）
python scripts/rhythm_guard.py \
  --chapter-file "正文/第037章.md" --quota "追踪/节奏配额.md"

# 为下一章推荐事件类型
python scripts/rhythm_guard.py --quota "追踪/节奏配额.md" --recommend "快"

# 记录本章事件
python scripts/rhythm_guard.py --quota "追踪/节奏配额.md" --record "conflict"

# 写章前预检声明
python scripts/rhythm_guard.py --quota "追踪/节奏配额.md" --declare "A,conflict,快"
```

将事件类型从 A/B/C 三类扩展为 5+1 类：conflict(冲突爽点)/bond(人物羁绊)/faction(势力经营)/world(风土人情)/crisis(危机升级)/revelation(核心秘密)，每类有独立冷却章数和连续上限，新增 gentle_window（每5章至少1次bond或world）。A/B/C 配额向后兼容。

### 4. event_matrix.py — 事件矩阵调度器

```bash
# 为下一章推荐事件类型分配（按档位推荐）
python scripts/event_matrix.py recommend "{书名目录}" --gear 快

# 记录本章事件类型，更新冷却状态
python scripts/event_matrix.py record "{书名目录}" --chapter 37 --event conflict

# 查看当前冷却状态和 gentle_window 进度
python scripts/event_matrix.py status "{书名目录}"
```

独立的事件矩阵调度器，数据持久化到 `追踪/event_matrix.json`。与 rhythm_guard.py 双向兼容。

### 5. entity_index.py — BM25 两级语义检索

```bash
# 每章更新摘要后重建索引（或批量补建）
python scripts/entity_index.py build "{书名目录}"

# 写前检索某个实体出现在哪几章
python scripts/entity_index.py query "{书名目录}" 林雷 盘龙戒指

# BM25 两级语义检索（粗筛BM25取top-8 + 精排TF-IDF取top-4 + 缓存 + 命中可解释）
python scripts/entity_index.py semantic "{书名目录}" "林雷的战斗场景" "魔法试炼"
python scripts/entity_index.py semantic "{书名目录}" "与盘龙戒指有关的秘密" --top 5

# 顺带在正文里抓原文行
python scripts/entity_index.py query "{书名目录}" 林雷 --grep
```

升级为 BM25 两级检索：粗筛用 BM25 评分（k1=1.5, b=0.75）取 top-8 candidate，精排用片段级 TF-IDF 取 top-4。新增查询缓存（`追踪/query_cache.json`）、轻场景触发判定（过场/赶路自动跳过全量检索）、命中原因可解释（输出匹配关键词和得分）、章节元数据读取（`追踪/chapter_meta/第XXX章.meta.json`）。

### 6. deconstruct.py — 拆文辅助

```bash
# 量化统计
python scripts/deconstruct.py stats "对标书/第1章.md" ... --output "对标/量化统计.md"

# 结构分析（钩子/对话/段落）
python scripts/deconstruct.py structure "对标书/第1章.md" ... --output "对标/结构分析.md"

# 节奏分析（快中慢档位 + 爽点位置）
python scripts/deconstruct.py rhythm "对标书/第1章.md" ... --output "对标/节奏分析.md"

# 文风指纹
python scripts/deconstruct.py fingerprint "对标书/第1章.md" ... --output "对标/文风指纹.md"
```

### 7. normalize_punct.py — 标点归一化

```bash
# 先 --check 看一眼，确认后去掉 --check 就地改写（写前自动留一份 .bak）
python scripts/normalize_punct.py "正文/第037章_标题.md" --check
python scripts/normalize_punct.py "正文/第037章_标题.md"

# 多文件批量预览
python scripts/normalize_punct.py a.md b.md --check
```

清理省略号 `……/…/。。。`、破折号 `——/—/--`、感叹/疑问堆叠 `!!!/???`、独立分隔线、
全角空格与行尾空白；引号字符本身不动（`「」`/`""` 原样保留）。让停顿用动作/短句/换行表达。

### 8. init_book.py — 一键初始化书籍工程

```bash
# 在当前目录下创建 {书名}/ 书籍工程骨架
python scripts/init_book.py "我的小说" --genre 玄幻 --platform 番茄

# 指定父目录；--force 重建缺失模板（不动 正文/ 与 大纲/）
python scripts/init_book.py "我的小说" --dir "D:/存放/小说" --force
```

按 `assets/templates/book-structure.md` 的布局创建 `大纲/ 正文/ 对标/ 参考资料/`、
`设定/`（含 `角色/`）、`追踪/`（含 `门禁/`），从 `assets/templates/` 拷贝五个追踪文件 +
三个设定文件模板，并轻量预填 `设定/题材定位.md`（书名/主题材/平台）。已有目录且非空时默认拒绝覆盖。

### 9. resume.py — 会话恢复 / 欠账门

```bash
# 每次开工先跑一次
python scripts/resume.py "{书名目录}"

# 机器可读（供编排工具消费）
python scripts/resume.py . --json
```

一次说清四件事：① 最新一章是第几章；② 该章门禁（`追踪/门禁/gate_chN.json`）是否通过、
正文过闸后是否被改动；③ 追踪文件是否同步（章节摘要/节奏配额有无该章条目、伏笔台账有无 🔴 超期）；
④ 下一章章纲是否就位。有欠账时退出码 1，报告里列出补账步骤。

### 10. validate_tracking.py — 追踪文件格式校验

```bash
# 校验整本书的五个追踪文件
python scripts/validate_tracking.py "{书名目录}"

# 只校验单个文件
python scripts/validate_tracking.py . --file "追踪/伏笔台账.md"
```

把五个追踪文件的约定格式变成可校验的 schema：伏笔台账四节齐备（🔴🟡🟢✅）+ ID 形如 `F1-03`；
节奏配额三节齐备（A/B/C 配额 / 事件冷却 / 档位）；章节摘要每个 `### 第N章` 含七个必填字段；
角色状态每个 `## 角色` 含四个必填字段；时间线表格列数 ≥4。每 10 章或新会话首次校验一次，
防止模型把格式写歪导致下游脚本静默漏检。

### tracking_delta.py — 写后事实增量的证据核对

```bash
python scripts/tracking_delta.py check "{工程外增量.json}" --chapter-file "{stage}/正文/{chapter_file}" --ledger "{stage}/追踪/伏笔台账.md"
python scripts/tracking_delta.py apply-summary "{工程外增量.json}" --summary-file "{stage}/追踪/章节摘要.md"
```

事务保证正文与五表一起落盘，不保证表里的事实正文里真的发生过。增量文件按
`assets/templates/tracking-delta.json` 填写，每条追踪变更附一段正文原文摘录；`check` 核对摘录逐字存在、
关键实体在正文出现、伏笔 ID 已登记，`apply-summary` 用同一份增量生成或替换本章摘要条目。
它只证明“有出处”，不替代语义自查。

### 11. entity_index.py — BM25 两级语义检索 + 实体索引

（已在上文第 5 节详述）

### 12. outline_anchor.py — 大纲锚点动态约束注入

```bash
python scripts/outline_anchor.py inject "{书名目录}" --chapter 37
python scripts/outline_anchor.py check "{书名目录}" --chapter 37 --quota A
```

从章纲提取「禁止揭露/必须达成/阶段定位」三条约束，生成自然语言注入写前上下文；同时检查配额兼容性（本章声明的配额与近3章记录是否冲突）。

### 13. story_graph.py — 知识图谱

```bash
python scripts/story_graph.py build "{书名目录}"
python scripts/story_graph.py query "{书名目录}" "主角" --depth 2
python scripts/story_graph.py cascade "{书名目录}" --from-chapter 50 --desc "改纲：加入新反派"
python scripts/story_graph.py update "{书名目录}" --chapter 37
```

从 `追踪/entity_index.json` + 章节摘要构建节点（角色/事件/地点/物品/势力），提取关系边，支持级联标记（改纲后标记受影响节点）。`update` 子命令：每章写完后增量更新（只从本章摘要提取新实体和关系追加到图谱），避免全量 rebuild 的代价。

### 14. research_agent.py — 联网调研

```bash
python scripts/research_agent.py keywords --genre 历史 --topic "中世纪盔甲"
python scripts/research_agent.py gaps "{书名目录}" --json
# 使用可用联网工具取得资料后，存储真实调研文本及来源
python scripts/research_agent.py store "{书名目录}" --dimension "战争装备" --source-file "参考资料/盔甲调研.md" --url "{来源链接}"
```

脚本提供关键词生成、知识库缺口检测与结构化存储；实际搜索由当次可用联网工具完成。没有搜索结果时不得声称已联网调研。

### 15. style_library.py — 风格库跨书复用

```bash
python scripts/style_library.py import "{旧书目录}" --name "旧书A风格"
python scripts/style_library.py search --keyword "旧书A风格" --format json
# 从搜索结果取得真实 style_id 后应用或删除；脚本不支持按对话比例/句长过滤
python scripts/style_library.py apply "{style_id}" --target "{新书目录}"
python scripts/style_library.py delete "{style_id}"
```

跨项目导入/搜索/应用/删除文风指纹，多书写作时迁移风格基线。

### 16. content_expander.py — 智能内容扩充引擎

```bash
# 分析扩充潜力
python scripts/content_expander.py analyze "正文/第037章.md" --target 3500

# 生成扩充建议报告
python scripts/content_expander.py analyze "正文/第037章.md" --target 3500 --output "追踪/扩充建议_ch37.json"
```

五维扩充策略（场景扩充/对话丰富化/心理深化/动作细节/过渡平滑），智能分析文本各维度的扩充潜力，按优先级排序并估算可扩充字数。解决「章节过短」的量化扩充问题。

### 17. context_manager.py — 长篇上下文管理器

```bash
# 选取目标章节的最小必读上下文
python scripts/context_manager.py select "{书名目录}" --chapter 37 --max-chars 4000

# 压缩多章摘要
python scripts/context_manager.py compress "{书名目录}" --from 30 --to 36 --output "追踪/压缩摘要_30-36.md"
```

组件化上下文选取（章纲/人物卡/近章摘要/伏笔台账/设定摘要），按预算比例分配各组件字数，解决百万字长篇的上下文爆炸问题。

### 18. novel_flow.py — 统一流程执行器

```bash
# 诊断书籍工程状态
python scripts/novel_flow.py status "{书名目录}"

# 日更批量模式（串行执行 N 章）
python scripts/novel_flow.py daily "{书名目录}" --chapters 3

# 进度报告
python scripts/novel_flow.py report "{书名目录}"

# 改纲级联
python scripts/novel_flow.py revise "{书名目录}" --from-chapter 50 --description "加入新反派"
```

编排分散工作流：status（诊断）→ prepare（写前准备）→ write（单章写作）→ daily（日更批量）→ revise（改纲级联）→ report（进度报告）。fail-fast 机制：检查不过不继续下一章。

### 19. quality_score.py — 质量评分系统

```bash
# 评分单章（Markdown 报告）
python scripts/quality_score.py score "正文/第037章.md" --chapter 37 --book-dir "." --markdown

# 多章趋势分析
python scripts/quality_score.py trend --book-dir "." --from 30 --to 40 --markdown
```

七维加权评分（AI腔控制 20% / 节奏控制 15% / 文风一致性 15% / 情感冲击力 15% / 结构完整性 15% / 对话质量 10% / 可读性 10%），总分 0-100 分，A/B/C/D/F 五级。评分结果落盘 `追踪/质量评分/quality_ch{N}.json`，支持趋势分析。

### 20. beat_sheet_generator.py — Beat Sheet 分镜表生成器

```bash
# 从章纲生成 Beat Sheet（按场景/情绪转折拆分为 3-7 个 Beat）
python scripts/beat_sheet_generator.py generate "{书名目录}" --chapter 37

# 为指定 Beat 生成五维扩写提示（角色/场景/情绪/动作/对话）
python scripts/beat_sheet_generator.py expand "{书名目录}" --chapter 37 --beat 2

# 校验合成稿（Beat 覆盖度/字数分布/情绪曲线连贯性）
python scripts/beat_sheet_generator.py validate "{书名目录}" --chapter 37 --manuscript "正文/第037章_标题.md"
```

将复杂章节拆解为多个 Beat（节拍），每个 Beat 是独立叙事单元。配合 `workflow/beat-pipeline.md` 工作流，解决 AI 单次生成长章节时压缩剧情、跳过细节的问题。Beat Sheet 产出存入 `追踪/beat_sheets/beat_ch{N}.json`；expand 产出五维扩写提示直接输出到终端；validate 产出校验报告并更新 Beat Sheet 的 validation 字段。

### 21. chapter_synthesizer.py — 章节合成器

```bash
# 拼接 Beat 片段为完整章节，检测衔接
python scripts/chapter_synthesizer.py synthesize "{书名目录}" --chapter 37

# 合成稿五维校验（字数/覆盖度/衔接/钩子/格式）
python scripts/chapter_synthesizer.py check "{书名目录}" --chapter 37 --manuscript "正文/第037章_标题.md"

# 生成 Beat 边界过渡润色提示
python scripts/chapter_synthesizer.py polish "{书名目录}" --chapter 37
```

将 Beat Sheet 流水线产出的多个 Beat 片段合成为完整章节，对应 `workflow/beat-pipeline.md` 的 Step 4。synthesize 按序拼接并检测 Beat 间衔接；check 做字数/覆盖度/衔接/钩子/格式五维校验输出报告 JSON；polish 识别 Beat 边界生成过渡润色提示（Markdown）。

### 22. gate_repair.py — 门禁修复计划生成器

```bash
# 读取门禁报告生成最短修复路径
python scripts/gate_repair.py "{书名目录}" --chapter 37

# 指定门禁报告路径
python scripts/gate_repair.py "{书名目录}" --chapter 37 --gate-report "追踪/门禁/gate_ch37.json"

# 输出 Markdown 修复计划
python scripts/gate_repair.py "{书名目录}" --chapter 37 --markdown
```

当章节门禁检查失败时，自动分析失败原因并生成最短修复路径：读取门禁报告 → 按严重度分类（blocking/advisory）→ 为每个 blocking 问题生成修复建议（内置禁用词替换表 + 毒句式改写方向）→ 生成最短修复路径（优先修复高影响问题，合并相关问题）→ 输出 `追踪/门禁/repair_plan_ch{N}.md`。

### 23. editorial_manager.py — 编辑团队状态管理器

```bash
# 生成上下文快照 JSON（供编辑团队启动）
python scripts/editorial_manager.py snapshot "{书名目录}" --chapter 37

# 记录单次审核结果
python scripts/editorial_manager.py record-review "{书名目录}" --chapter 37 --stage final --agent consistency-reviewer --verdict pass --p0 0 --p1 2 --p2 1

# 查看最近 N 章审核历史（表格格式）
python scripts/editorial_manager.py status "{书名目录}" --last 10

# 检测是否需要人工介入（防死循环）
python scripts/editorial_manager.py need-human "{书名目录}"
```

管理多 Agent 协作写作流程的状态。snapshot 生成编辑团队启动上下文快照；record-review 追加审核结果到 `追踪/review_history.json`；status 输出表格格式状态报告；need-human 检测防死循环（单章返工上限 2 次、连续条件通过 3 章强制人工介入）。对应 `workflow/editorial-spawn.md` 的 Step 1 与 Step 7。

### 24. hooks.py — 自动化 Hook 机制

```bash
# 会话开始时显示进度快照
python scripts/hooks.py session-start "{书名目录}"

# 写正文前检查大纲是否存在
python scripts/hooks.py guard-outline "{书名目录}" --chapter 37

# 正文写入后轻量扫描（毒句式+元信息泄漏）
python scripts/hooks.py check-prose "正文/第037章_标题.md" --book-dir "{书名目录}"

# 检测设定缺口
python scripts/hooks.py detect-gaps "{书名目录}"

# 上下文压缩前保存进度快照
python scripts/hooks.py pre-compact "{书名目录}"
```

五个自动化 Hook，适配本 skill 四目录文件结构（正文/大纲/追踪/设定）：session-start（进度快照）、guard-outline（大纲存在性校验）、check-prose（正文轻量扫描，含毒句式 + 元信息泄漏）、detect-gaps（设定缺口检测）、pre-compact（压缩前快照）。

**机械部署（Claude Code）**：hooks.py 的上述子命令原靠模型自觉调用，起提供平台级机械强制——`hook_entry.py`（事件分发器）+ `deploy_hooks.py`（settings.json 注册器）：

```bash
# 在书籍工程目录内执行，把 4 类 hook 注册进 .claude/settings.json（幂等，自动备份）
python scripts/deploy_hooks.py "{书名目录}"

# 卸载
python scripts/deploy_hooks.py "{书名目录}" --uninstall
```

注册后，PreToolUse 在「无章纲写正文」时平台级阻断（exit 2），PostToolUse 在「毒句式欠账未清」时阻断，SessionStart/PreCompact 自动做进度/压缩前快照。全程 fail-open（Python/脚本缺失、无法定位书目录时静默放行），正文文件含 `<!-- lns:skip -->` 时跳过检查。多书切换可用 `LNS_BOOK_DIR` 环境变量或项目根 `.active-book` 指定活跃书。

### 25. rag_retriever.py — RAG 检索增强

```bash
# 构建章节级 RAG 索引（章节号/标题/摘要/实体/字数/情绪）
python scripts/rag_retriever.py build "{书名目录}"

# 两级 BM25+TF-IDF 检索 + 写前上下文建议
python scripts/rag_retriever.py query "{书名目录}" "林雷的战斗场景" --top 4

# 轻场景跳过全量检索（赶路/过场自动跳过）
python scripts/rag_retriever.py query "{书名目录}" "赶路过场" --light

# 索引状态（覆盖率/最后更新/缓存命中率）
python scripts/rag_retriever.py status "{书名目录}"
```

基于 `entity_index.py` 的 BM25 检索能力增强，侧重语义级相关章节检索。build 构建章节级 RAG 索引；query 两级 BM25+TF-IDF 检索输出可解释结果 + 写前上下文建议（`追踪/next_plot_context.md`），轻场景触发判定（赶路/过场自动跳过全量检索），查询缓存 + 命中可解释；status 输出索引覆盖率与缓存命中率。与 entity_index.py 互补使用。

### 26. common.py — 共享工具函数

```python
from common import read_text, write_text, count_chinese_chars, parse_chapter_number, find_book_dir
```

所有脚本共享的工具函数集合：文件 I/O（read_text/write_text/read_json/write_json）、文本处理（count_chinese_chars/split_paragraphs/normalize_whitespace/truncate_text）、章节解析（parse_chapter_number/find_book_dir）等。集中管理通用逻辑，减少重复代码，默认 utf-8-sig 编码兼容 BOM。

### 27. config.py — 全局配置常量

```python
from config import SKILL_VERSION, BOOK_DIRS, TRACKING_FILES, SETTING_FILES
```

全局配置常量集中管理：SKILL_VERSION/SKILL_NAME、书籍工程目录结构（BOOK_DIRS）、追踪/设定文件名（TRACKING_FILES/SETTING_FILES）、章节命名格式、BM25 参数等。修改一处即全局生效，避免散落在各脚本中的魔法数字。

