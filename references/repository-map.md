# 仓库地图

本文件保存原先放在 README 里的目录树和能力对照，便于入口页保持简短。数字以仓库现状为准；发布契约由 `scripts/tests/test_release_contract.py` 按目录实数核对。

## 结构

```
general-novel-skill/
├── SKILL.md                  # 路由入口：按动作指向工作流；不变量在 session-invariants.md
├── references/
│   ├── repository-map.md         # 本文件：目录树与能力对照
│   ├── scripts-index.md          # 脚本用法（从 README 移出）
│   ├── workflow/             # 工作流（当前 31 个，含无工程试写的 quick-start.md）
│   │   ├── session-invariants.md # 权威顺序、章事务、失败码、停止点
│   │   ├── book-init.md          # 开书流程（长篇，对接 init_book.py）
│   │   ├── task-router.md        # 任务路由与上下文装配（多意图拆解、改纲协议、外稿恢复）
│   │   ├── quick-start.md        # 无工程试写（五个问题 → 迷你章纲 → 草稿）
│   │   ├── chapter-loop.md       # 单章写作循环
│   │   ├── outline-system.md     # 三级大纲 + 大纲锚点配额
│   │   ├── short-story-loop.md   # 短篇写作循环（五段式）
│   │   ├── beat-pipeline.md      # Beat Sheet 多步流水线
│   │   ├── deconstruct.md        # 拆文学习对标（轻量四维）
│   │   ├── deconstruct-pipeline.md  # 拆文七阶段工业管道
│   │   ├── deconstruct-output-spec.md  # 拆文产出结构化分目录规范
│   │   ├── market-scan.md        # 扫榜选题（方法论）
│   │   ├── market-scan-deep.md   # 扫榜深度选题（选题四步+读者画像+决策报告）
│   │   ├── import-book.md        # 导入旧稿接手（概述）
│   │   ├── import-deep.md        # 导入旧稿深度逆向工程（10步+角色状态反推）
│   │   ├── daily-batch.md        # 日更批量模式
│   │   ├── daily-failfast.md     # 日更 fail-fast 五类资料检查
│   │   ├── auto-write.md         # 全自动写书调度（plan/run/report+断点续写）
│   │   ├── ideation.md           # 交互式脑洞引导（5轮收敛+压力测试）
│   │   ├── editorial-spawn.md    # 编辑团队 8 步 spawn 协议
│   │   ├── cross-review.md       # 跨 Agent 审核协议（路由表+三维度报告+批处理）
│   │   ├── research.md           # 联网调研工作流
│   │   ├── imitation.md          # 仿写工作流（对标书→新书五步）
│   │   ├── style-library.md      # 风格库跨书复用
│   │   ├── commands.md           # 命令入口表（30个命令+新手/高级分层）
│   │   ├── revision.md           # 大修流程
│   │   ├── publishing-pack.md    # 简介、标签、封面等上架物料
│   │   ├── author-preferences.md # 作者偏好的记录、更正与遗忘
│   │   ├── evidence-review.md    # 统计分数、图谱证据与评测的判读
│   │   ├── dashboard-workbench.md  # Dashboard 工作台的浏览与编辑
│   │   └── book-scaling.md       # 百万字结构展开
│   ├── craft/                # 通用写作工艺（当前 50 个）
│   │   ├── iron-law.md           # 七条铁律
│   │   ├── anti-ai-style.md      # 7 Gate 去AI腔（判定标准）
│   │   ├── deslop-engineering.md  # 去AI味工程化（机器输出判读+删除优先+两遍式+删改上限+改过头信号）
│   │   ├── sensitive-word-replacement.md  # 敏感词替换（地名代称/别称置换/地名脱敏）
│   │   ├── opening.md            # 黄金三章 + 开篇硬目标（300 字压力 / 1000 字异象 / 三章对峙）
│   │   ├── hooks.md              # 章首 7 式、章尾 13 式
│   │   ├── pacing-and-hooks.md   # 节奏三档制 + A/B/C 配额
│   │   ├── pacing-review.md      # 语义级节奏审查（四维度）
│   │   ├── reverse-brake.md      # 反向刹车 + 事件冷却
│   │   ├── reader-contract.md    # 读者契约（执行模板）
│   │   ├── reader-contract-deep.md  # 读者契约深度理论（因果权+结算权+终局储备+透支两问）
│   │   ├── emotional-arc.md      # 情绪弧线操作手册（六种弧线+情绪引擎+情绪模块八大类+长篇情绪引擎）
│   │   ├── character-design.md   # 角色设计操作手册（三层标签反差+九维人设）
│   │   ├── commercial-core.md    # 商业创作核心方法（卖点论+金手指原理+留存四支柱）
│   │   ├── outline-safety.md     # 大纲安全七检 + 可证伪降级检查
│   │   ├── plot-budget.md        # 情节点预算制（密/疏+字数求和校验）
│   │   ├── outline-structure-theory.md  # 深度结构理论（三级结构+五幕因果链+对标节奏迁移）
│   │   ├── style-fingerprint.md  # 文风指纹六维量化
│   │   ├── style-profile.md      # 文风协议（整书级视图+锚点片段+分层模仿+confidence）
│   │   ├── editorial-team.md    # 编辑团队协作（对接 assets/agents/）
│   │   ├── review-rubric.md      # 多视角盲评
│   │   ├── gate-artifacts-spec.md  # 门禁产物规范（schema + 跨Agent消费接口）
│   │   ├── suspense-grading.md   # 悬念分级（5级体系+多线周期+期待接力）
│   │   ├── information-cluster.md  # 信息团概念（定义+递进+排版+三层信息差）
│   │   ├── corpus-baseline.md    # 爆款语料基准（句长/逗号比/对话占比/爽点密度）
│   │   ├── chapter-meta.md       # 章节元数据侧车（per-chapter meta.json schema）
│   │   ├── narrative-modules.md  # 叙事元素卡+结构技法卡+情绪模块公式
│   │   ├── wit-battle.md         # 智斗构型三步两线法
│   │   ├── adaptation-method.md  # 改编法+三重重复循环检测
│   │   ├── writing-craft-extras.md  # 身体细节替代情绪词+ recurring props + 三维场景 + 开篇密度
│   │   ├── plot-special-topics.md   # 特殊题材处理（时间跳越/多POV/群戏/闪回/蒙太奇）
│   │   ├── genre-formulas.md        # 题材写作公式（打脸/升级/拉情绪/悬疑揭秘/日常装逼）
│   │   └── quality-checklist.md     # 全流程质量检查清单（开书前/大纲/写前/写后/卷末/发布前）
│   ├── genres/               # 题材包（可插拔，34 题材 + 九件事正文层规范）
│   │   ├── INDEX.md               # 路由 + 别名表 + 九件事说明
│   │   ├── GENRE-PROSE-SPEC.md   # 题材卡九件事正文层规范
│   │   └── {题材}.md × 34          # 每题材一张卡（12栏目+九件事，逐步补齐）
│   └── platforms/            # 平台基线：长篇 + 短篇
├── assets/
│   ├── templates/            # 书籍工程模板（20 个）
│   ├── agents/               # 编辑团队可部署资产（4 个角色 + README）
│   └── style_library/        # 风格库（跨书复用；首次导入风格时才生成，仓库里没有）
└── scripts/                  # 机械闸口、量化与验证工具（纯标准库，共 47 个）
    ├── common.py                 # 共享工具函数（文件I/O+文本处理+章节解析）
    ├── config.py                 # 全局配置常量（目录结构+文件名+BM25参数）
    ├── check_text.py             # 7 Gate + 字数 + 禁用词 + 毒句式 + 伏笔超期 + 量化打分 + 7类AI模式检测 + --deslop分级 + --whitelist
    ├── style_fingerprint.py      # 文风指纹六维提取 + 漂移检测
    ├── rhythm_guard.py           # 节奏配额检查（A/B/C + 5+1类事件矩阵 + recommend/record）
    ├── event_matrix.py           # 事件矩阵调度器（5+1类+独立冷却+gentle_window）
    ├── entity_index.py           # BM25两级语义检索 + 实体索引 + 缓存 + 触发判定
    ├── deconstruct.py            # 拆文辅助（量化/结构/节奏/文风）
    ├── normalize_punct.py        # 标点归一化
    ├── init_book.py              # 一键初始化书籍工程骨架
    ├── resume.py                 # 会话恢复报告（欠账门机器查验）
    ├── chapter_transaction.py    # 章事务（prepare/validate/commit/recover，正文与追踪五表一起入库）
    ├── validate_tracking.py      # 追踪文件格式校验
    ├── tracking_delta.py         # 写后事实增量：追踪变更逐条核对正文出处 + 生成章节摘要条目
    ├── outline_anchor.py         # 大纲锚点动态约束注入 + 配额兼容检查
    ├── story_graph.py            # 知识图谱（节点+边+版本+级联标记+Mermaid导出）
    ├── research_agent.py         # 联网调研（缺口检测+关键词生成+结构化存储）
    ├── style_library.py          # 风格库管理（import/search/apply/delete）
    ├── content_expander.py       # 智能内容扩充引擎（场景/对话/心理/动作/过渡五维策略）
    ├── context_manager.py        # 长篇上下文管理器（最小上下文选取+预算分配+压缩）
    ├── novel_flow.py             # 统一流程执行器（status/prepare/write/daily/revise/report）
    ├── quality_score.py          # 质量评分系统（七维加权+趋势分析）
    ├── beat_sheet_generator.py   # Beat Sheet分镜表生成器（generate/expand/validate）
    ├── chapter_synthesizer.py    # 章节合成器（synthesize/check/polish）
    ├── gate_repair.py            # 门禁修复计划生成器（失败原因分析+最短修复路径）
    ├── editorial_manager.py      # 编辑团队状态管理器（snapshot/record-review/status/need-human）
    ├── hooks.py                  # 自动化Hook机制（5个Hook）
    ├── rag_retriever.py          # RAG检索增强（build/query/status）
    ├── author_preferences.py     # 作者偏好存取
    ├── entry_mode.py             # 章节入口模式推荐
    ├── anti_resolution_guard.py  # 速决倾向只读扫描（复核信号，不是门禁）
    ├── ranking_crawler.py        # 榜单采集（需联网）
    ├── skill_contract.py         # Skill 契约检查（引用可达、命令参数、入口约束）
    ├── skill_eval.py             # Skill 评测案例校验
    └── tests/                    # 默认全量测试套件（收集数见 skill.json）
        ├── run_tests.py              # 测试运行器
        ├── test_common.py            # common.py（36）
        ├── test_config.py            # config.py（14）
        ├── test_check_text.py        # check_text.py（23）
        ├── test_novel_flow.py        # novel_flow.py（16）
        ├── test_context_manager.py   # context_manager.py（15）
        ├── test_static_check.py      # static_check.py（19）
        ├── test_benchmark.py         # benchmark.py（16）
        ├── test_rhythm_guard.py      # rhythm_guard.py（18）
        ├── test_entity_index.py      # entity_index.py（16）
        └── test_outline_anchor.py    # outline_anchor.py（16）
```


## 核心能力

| 能力 | 一句话 | 依据 |
|---|---|---|
| 三级大纲 + 大纲锚点配额 | 总纲/卷纲/章纲三级，锚点配额防注水 | `workflow/outline-system.md` |
| 大纲安全七检 + 可证伪降级检查 | 七项定性检查 + 两项可证伪检查，大纲写完必审 | `craft/outline-safety.md` |
| 深度结构理论 | 三级结构选择 + 五幕因果链 + 对标节奏迁移1/4·中点·3/4 | `craft/outline-structure-theory.md` |
| 情节点预算制 | 密/疏三级 + 字数预算求和校验，防注水防过场 | `craft/plot-budget.md` |
| 单章写作循环 + 7 Gate 去AI腔 | 读上下文→写→闸口→追踪，7 道闸口去 AI 腔 | `workflow/chapter-loop.md`、`craft/anti-ai-style.md` |
| 开篇硬目标 | 前三章：约 300 字进入压力、约 1000 字出现异常、至少一次当面冲突；平台只决定有多靠前 | `craft/opening.md`、`platforms/platform-guide.md` |
| 连载章尾 | serial 停在能引出问题的威胁、抉择或物证，招式用章尾 13 式；不写预告句 | `craft/scene-rendering.md`、`craft/hooks.md` |
| 去AI味工程化 | 机器输出判读 + 删除优先三关 + 两遍式 + 删改上限 + 改过头信号 + 共享两轮修复额度 | `craft/deslop-engineering.md` |
| **敏感词替换表** | 开书必建：真实地名/机构/人物 → 全书代称，地名代称系统 + 别称置换规则 + 地名脱敏处理；必禁专名并入禁用词.txt 机器拦截 | `craft/sensitive-word-replacement.md`、`templates/sensitive-word-replacement.md` |
| Beat Sheet 多步流水线 | 一章拆 4–8 个 Beat 分镜写，末尾节奏预检 | `workflow/beat-pipeline.md`、`templates/beat-sheet.md` |
| 短篇五段式 | 短篇单篇情绪闭环结构 | `workflow/short-story-loop.md` |
| **短篇结尾句工艺** | 短篇默认必加：点睛句（正文最后一行，一句话）/ 彩蛋句（一句隐藏信息）/ 碎碎念（默认一句），一律简短 | `craft/short-story-ending.md`、`workflow/short-story-loop.md` Step 7 |
| 节奏三档制 + A/B/C 配额 + 事件矩阵5+1类 | 慢/中/快三档，6类事件独立冷却+gentle_window+recommend/record | `craft/pacing-and-hooks.md`、`craft/reverse-brake.md`、`scripts/event_matrix.py` |
| **语义级节奏审查** | 四维度：档位判断+配额语义核查+悬念质量+隐性加速检测，脚本检测不到的由Claude兜底 | `craft/pacing-review.md` |
| 反向刹车 | 非终局章禁止解决主线核心矛盾 | `craft/reverse-brake.md` |
| 读者契约（执行模板 + 深度理论） | 因果权+结算权+终局储备+透支两问+风险三级 | `craft/reader-contract.md`、`craft/reader-contract-deep.md` |
| 情绪弧线操作手册 | 六种弧线 + 情绪引擎四冲程 + 情绪模块八大类 + 长篇情绪引擎因果链 | `craft/emotional-arc.md` |
| 角色设计操作手册 | 三层标签反差 + 九维人设 + 金手指绑架人设 | `craft/character-design.md` |
| 商业创作核心方法 | 卖点论 + 金手指原理 + 留存四支柱 + 崩盘预警 | `craft/commercial-core.md` |
| 文风指纹（六维量化）+ 文风协议（整书级视图） | 六维量化 + 锚点片段 + 分层模仿 + confidence | `craft/style-fingerprint.md`、`craft/style-profile.md` |
| **风格库跨书复用** | import/search/apply/delete，多书写作时跨项目迁移风格 | `workflow/style-library.md`、`scripts/style_library.py` |
| 编辑团队协作（8步spawn协议） | 策划主编/写作特工/反AI编辑/连载核实官 + 完整生命周期 | `craft/editorial-team.md`、`workflow/editorial-spawn.md` |
| 多视角盲评 + 跨Agent审核 | 四视角盲评 + 路由表 + 三维度报告 + P0/P1/P2 + 批处理 + 防死循环 | `craft/review-rubric.md`、`workflow/cross-review.md` |
| 拆文（轻量四维 + 七阶段工业管道） | 四维统计 + 情绪模块卡 + 节奏权威索引 + 质量阈值 + 恢复机制 | `workflow/deconstruct.md`、`workflow/deconstruct-pipeline.md` |
| **仿写工作流** | 对标书→拆文→提取→选风格→开书→魔改五步 | `workflow/imitation.md` |
| 扫榜选题（方法论 + 深度执行） | 选题四步 + 读者画像 + 选题决策报告 | `workflow/market-scan.md`、`workflow/market-scan-deep.md` |
| 导入旧稿（概述 + 深度10步） | 角色状态反推 + 增量导入 + 卷划分用户确认制 | `workflow/import-book.md`、`workflow/import-deep.md` |
| **联网调研** | 题材维度映射+缺口检测+关键词生成+结构化存储 | `workflow/research.md`、`scripts/research_agent.py` |
| 全自动写书调度 | plan/run/report + 断点续写 + 自动暂停 | `workflow/auto-write.md` |
| 交互式脑洞引导 | 5轮收敛 + 压力测试 | `workflow/ideation.md` |
| 日更 fail-fast 五类资料检查 | 缺失必读资料即停止，输出修复动作 | `workflow/daily-failfast.md` |
| BM25两级语义检索 | 粗筛BM25 + 精排TF-IDF + 缓存 + 触发判定 + 命中可解释 | `scripts/entity_index.py` |
| **知识图谱** | 节点+边+版本+级联标记+Mermaid导出+影响分析 | `scripts/story_graph.py` |
| **章节元数据侧车** | per-chapter meta.json，统一消费方接口 | `craft/chapter-meta.md` |
| **门禁产物规范** | gate_result.json schema + 跨Agent消费接口 | `craft/gate-artifacts-spec.md` |
| **对话精通** | 7种决策路由+冲突递进五级+节奏控制+微动作配合 | `craft/dialogue.md` |
| **悬念分级** | 5级体系+多线周期+期待接力+信息释放节奏 | `craft/suspense-grading.md` |
| **信息团概念** | 定义+递进+排版+三层信息差 | `craft/information-cluster.md` |
| **爆款语料基准** | 句长/逗号比/对话占比/爽点密度/情绪转换频率 | `craft/corpus-baseline.md` |
| **命令入口表** | 30个命令+新手/高级分层 | `workflow/commands.md` |
| **叙事元素卡+结构技法卡+情绪模块公式** | 10种叙事元素+9种结构技法+11个情绪公式 | `craft/narrative-modules.md` |
| **智斗构型三步两线法** | 4种构型+三步构建+两线并行 | `craft/wit-battle.md` |
| **升级循环与多角度强化** | 三级循环+五种强化角度+疲劳防护 | `workflow/book-scaling.md`（升级循环+多角度强章节） |
| **改编法+三重重复循环检测** | 四步改编+情节/对话/情绪三重检测 | `craft/adaptation-method.md` |
| **智能内容扩充引擎** | 场景/对话/心理/动作/过渡五维扩充策略+预算分配+压缩算法，解决章节过短问题 | `scripts/content_expander.py` |
| **长篇上下文管理器** | 最小上下文选取+预算分配+压缩+组件化，解决百万字上下文爆炸 | `scripts/context_manager.py` |
| **统一流程执行器** | status/prepare/write/daily/revise/report 六命令编排，串起分散工作流 | `scripts/novel_flow.py` |
| **质量评分系统** | 七维加权评分（AI腔/节奏/文风/情感/结构/对话/可读性）+趋势分析 | `scripts/quality_score.py` |
| **全流程质量检查清单** | 开书前/大纲/写前/写后/卷末/发布前六阶段检查清单 | `craft/quality-checklist.md` |
| **题材写作公式** | 打脸/升级/拉情绪/悬疑揭秘/日常装逼五大题材公式 | `craft/genre-formulas.md` |
| **特殊题材处理** | 时间跳越/多POV切换/群戏/闪回/蒙太奇五类特殊场景 | `craft/plot-special-topics.md` |
| **Beat Sheet 生成器** | 分镜表自动拆分（3-7 Beat）+五维扩写提示+合成稿校验 | `scripts/beat_sheet_generator.py` |
| **章节合成器** | Beat 拼接+过渡检测+字数/覆盖度/衔接/钩子/格式五维校验+润色提示 | `scripts/chapter_synthesizer.py` |
| **门禁修复计划** | 失败原因分析+修复策略映射（禁用词替换+毒句式改写）+最短修复路径 | `scripts/gate_repair.py` |
| **编辑团队状态管理** | 快照/审核记录/状态查询/人工介入检测（防死循环） | `scripts/editorial_manager.py` |
| **自动化 Hook 机制** | 5 个 Hook：session-start/guard-outline/check-prose/detect-gaps/pre-compact | `scripts/hooks.py` |
| **RAG 检索增强** | BM25 两级+增量索引+查询缓存+轻场景跳过+命中可解释+写前上下文建议 | `scripts/rag_retriever.py` |
| **共享模块** | common.py 工具函数（I/O+文本+章节）+config.py 配置常量（目录+文件名+参数） | `scripts/common.py`、`scripts/config.py` |
| **核心脚本测试套件** | 默认全量运行已登记模块；收集数由发布契约核验 | `scripts/tests/run_tests.py` |
| 题材包可插拔（34题材 + 九件事） | 12栏目设定层 + 九件事正文层 | `genres/INDEX.md`、`genres/GENRE-PROSE-SPEC.md` |
| 平台适配（长篇+短篇） | 长篇番茄/起点/晋江/飞卢 + 短篇知乎盐言/番茄短篇/七猫短篇 | `platforms/platform-guide.md` |
| 一键开书骨架 | 一条命令建书籍工程目录 + 拷贝模板 | `scripts/init_book.py` |
| 会话恢复 / 欠账门 | 开工先跑一次，把「写到哪/欠什么账/下一章是什么」说清 | `scripts/resume.py` |
| 追踪格式校验 | 五个追踪文件的格式 schema 校验 | `scripts/validate_tracking.py` |
| 时间线检查与归档 | 五类时间冲突检测；写章只加载锚点、近 10 章与未了结的约定，卷末生成归档候选 | `scripts/timeline_manager.py` |
| 标点归一化 | 清理省略号/破折号/感叹堆叠等非功能性标点 | `scripts/normalize_punct.py` |
| 大纲锚点约束注入 | 每章写前生成「禁止揭露/必须达成/阶段定位」约束 | `scripts/outline_anchor.py` |
| 百万字结构展开 | 从一句话脑洞到 200-500 万字的可执行结构 | `workflow/book-scaling.md` |
| 日更批量模式 | 每次会话串行写 2-3 章，含退化防护与中途快照 | `workflow/daily-batch.md` |
| 格式排版硬约束 | 8 条绝对禁止 + 语气标点谱系 + 对话格式 + 平台差异表 | `craft/format-and-structure.md` |
| 跨书召回防污染 | 主一辅多 + 三道防线 + 预算控制 | `craft/cross-book-recall.md` |
| 异源审核降级 | L1 多模型/L2 多会话/L3 同会话三级降级 + 防死循环 | `craft/review-rubric.md` |
| 正文隔离 P0 触发器 | 6 类机器检测标记自动判定正文隔离违规 | `craft/editorial-team.md` |

