# 学术论文 — 学术论文写作代理团队

一个通用的学术论文写作工具 — 12个代理的流程覆盖所有学科，高等教育领域作为默认参考。

**v2.5** 增加了两个写作质量功能：
- **风格校准**（输入步骤 10，可选） — 提供 3+ 过去的论文，流程学习您的写作声音（句子节奏，词汇偏好，引用整合风格）。在起草过程中作为软指导；学科惯例始终优先。参见 `shared/style_calibration_protocol.md`。
- **写作质量检查** (`references/writing_quality_check.md`) — 在草稿自我审查步骤中应用上下文敏感的写作诊断：模糊或过度使用的术语，打断论证的标点符号，清嗓子式的开头，损害清晰度的段落和句子形状。根据作者和场所的要求提出判断，而不是配额 (#825)。

> **路由学科 (v3.9.2):** see `.claude/CLAUDE.md` "Routing Discipline (v3.9.2)" + `shared/references/intent_clarification_protocol.md` for cross-skill routing rules. This skill assumes routing has already settled — ambiguous cross-phase materials should have been clarified upstream.

## 快速入门

**最小命令：**
```
Write a paper on the impact of AI on higher education quality assurance
```

```
Write a paper on the impact of declining birth rates on private university management strategies
```

**执行流程：**
1. 配置访谈 — 论文类型，学科，引用格式，输出格式
2. 文献搜索 — 系统搜索策略，来源筛选
3. 架构设计 — 论文结构，大纲，字数分配
4. 论证构建 — 论点证据链，逻辑流程
5. 全文起草 — 分节起草，语域调整
6. 引用合规 + 双语摘要（并行）
7. 同行评审 — 五视角分类评估，修改建议
8. 输出格式化 — LaTeX/DOCX (通过 Pandoc)/PDF/Markdown

---

## 触发条件

### 触发关键词

**English**: write paper, academic paper, paper outline, write abstract, revise paper, literature review paper, check citations, convert to LaTeX, convert format, format paper, conference paper, journal article, thesis chapter, research paper, guide my paper, help me plan my paper, step by step paper, draft manuscript, write methodology, write discussion, parse reviews, revision roadmap, help me with my revision, I got reviewer comments, should we push back, conference rebuttal, grant panel response, convert citations

**Español**: redactar artículo, trabajo académico, esquema de artículo, escribir resumen, enmendar mi artículo, artículo de revisión bibliográfica, verificar citas, convertir a LaTeX, convertir formato, artículo de conferencia, artículo de revista, capítulo de tesis, artículo de investigación, guía mi artículo, ayúdame a planificar mi artículo, escribir artículo paso a paso, redactar manuscrito, escribir metodología, escribir discusión, analizar opiniones de revisores, ruta de revisión, ayúdame con mi revisión, recibí comentarios de revisores, convertir formato de citas

**繁體中文**: 寫論文, 學術論文, 論文大綱, 寫摘要, 修改論文, 文獻回顧論文, 檢查引用, 轉 LaTeX, 轉換格式, 研討會論文, 期刊文章, 學位論文, 研究論文, 引導我寫論文, 幫我規劃論文, 逐步寫論文, 寫方法論, 寫討論, 審查意見, 修訂路線圖, 幫我修改, 我收到審查意見, 轉換引用格式

**한국어**: 논문 작성, 논문 초안, 논문 개요, 초록 작성, 논문 수정, 인용 확인, 인용 형식 검사, LaTeX 변환, 서식 변환, 학위논문 작성, 학술지 논문 작성, 학회 논문 작성, 논문 계획을 도와줘, 단계별로 논문 쓰기, 심사 의견을 받았어, 심사 의견 반영, 답변서 점검, AI 사용 고지

### 模式激活

当用户需要指导、逐步规划或对论文结构表示不确定时，激活 `plan` 模式。**默认规则**：在 `plan` 和 `full` 之间不确定时，优先选择 `plan`。

> 参见 `references/plan_mode_protocol.md` 完整的意图信号和激活规则。

### 不触发

| 场景 | 使用替代方案 |
|----------|-------------|
| 深入研究 / 事实核查（非论文写作） | `deep-research` |
| 审阅论文（结构化审阅） | `academic-paper-reviewer` |
| 全研究到论文的流程 | `academic-pipeline` |

### 与 `deep-research` 的区别

| 特性 | `academic-paper` | `deep-research` |
|---------|-------------------|-----------------|
| 主要输出 | 可发表的论文草稿 | 研究报告 |
| 结构 | 期刊格式（IMRaD 等） | APA 7.0 报告 |
| 引用 | 多格式（APA/Chicago/MLA/IEEE/Vancouver） | APA 7.0 仅限 |
| 摘要 | 依赖运行声明的 `output_language_pair` 的双语摘要（默认 zh-TW + EN） — 运行中声明的两个摘要语言遵循 `output_language_pair` | 单语言 |
| 同行评审 | 模拟 5 维度评审 | 编辑评审 |
| 输出格式 | LaTeX/DOCX (通过 Pandoc)/PDF/Markdown | Markdown 仅限 |
| 修订循环 | 最大 2 轮修订；未解决项目 -> "承认限制" | 同行评审 Critical 严重问题阻止进展到 Phase 7 |
| 用户可以跳过 Phase 1（文献）如果提供自己的来源 |

---

## 代理团队 (12 个代理)

| # | 代理 | 角色 | 阶段 |
|---|-------|------|-------|
| 1 | `intake_agent` | 配置访谈：论文类型，学科，期刊，引用格式，输出格式，语言，字数； 手势检测；计划模式简化访谈 | Phase 0 |
| 2 | `literature_strategist_agent` | 搜索策略设计，来源筛选，注释参考文献，文献矩阵 | Phase 1 |
| 3 | `structure_architect_agent` | 论文结构选择，详细大纲，字数分配，证据映射 | Phase 2 |
| 4 | `argument_builder_agent` | 论证构建，论点证据链，逻辑流程，反论证处理；计划模式论证压力测试 | Phase 3 / Plan Step 3 |
| 5 | `draft_writer_agent` | 分节全文起草，学科语域调整，字数跟踪 | Phase 4 |
| 6 | `citation_compliance_agent` | 引用格式验证，参考文献完整性，DOI 检查 | Phase 5a |
| 7 | `abstract_bilingual_agent` | 依赖运行声明的双语摘要（默认 zh-TW + EN），关键词计数来自 `references/abstract_writing_guide.md` 中的规则表 | Phase 5b |
| 8 | `peer_reviewer_agent` | 模拟双盲评审，五视角分类评估，修改建议（最大 2 轮修订） | Phase 6 |
| 9 | `formatter_agent` | 转换为 LaTeX/DOCX (通过 Pandoc)/PDF/Markdown, 期刊格式化, 封面信, 引用格式转换 (APA 7 / Chicago / MLA / IEEE / Vancouver) | Phase 7 |
| 10 | `socratic_mentor_agent` | 计划模式苏格拉底导师：章节指导，收敛标准（4 信号），问题分类（4 类），INSIGHT 提取 | Plan Step 0-3 |
| 11 | `visualization_agent` | 解析论文数据并生成出版质量的图表代码 (Python matplotlib / R ggplot2) 与 APA 7.0 格式化，色盲安全调色板和 LaTeX 集成 | Phase 4 / Phase 7 |
| 12 | `revision_coach_agent` | 解析非结构化审稿意见为修订路线图，或明确识别的真实委员会意见为单独的 #668 源会计关注跟踪器；独立工作 | Revision-Coach 模式 |

---

## 输出格式

### 文本格式
LaTeX (.tex + .bib), DOCX (通过 Pandoc), PDF (通过 LaTeX 或 Pandoc), Markdown.

### 图表
当论文包含定量结果时，`visualization_agent` 可以生成符合出版标准的图表，使用 Python (matplotlib/seaborn) 或 R (ggplot2) 与 APA 7.0 格式和色盲安全调色板。图表作为可运行的代码 + LaTeX `\includegraphics` 集成代码交付。参见 `references/statistical_visualization_standards.md` 图表类型决策树和代码模板。

### 引用格式
APA 7.0 (默认), Chicago (作者-日期或注释-参考文献), MLA 9, IEEE, Vancouver。`formatter_agent` 支持在后期将任何两个支持的格式转换为 "Convert citations to [format]"。

---

## 或chestration Workflow (8 阶段)

```
Phase 0: CONFIG        -> [intake_agent]              -> Paper Configuration Record
Phase 1: RESEARCH      -> [literature_strategist]      -> Search Strategy + Source Corpus
Phase 2: ARCHITECTURE  -> [structure_architect]        -> Paper Outline + Evidence Map
Phase 3: ARGUMENTATION -> [argument_builder]           -> Argument Blueprint
Phase 4: DRAFTING      -> [draft_writer]               -> Complete Draft
Phase 5a: CITATIONS    -> [citation_compliance] ──┐    -> Citation Audit Report
Phase 5b: ABSTRACT     -> [abstract_bilingual]   ─┘    -> Bilingual Abstract + Keywords  (并行)
Phase 6: PEER REVIEW   -> [peer_reviewer]              -> Review Report (max 2 revision loops)
Phase 7: FORMAT        -> [formatter]                  -> Final Output Package
```

> 参见 `references/workflow_phase_details.md` 完整的每个阶段的代理行为和输出描述。

### 审阅目标标准绑定 (#684)

当 Phase 0 生成作者确认的 `ReviewTargetContext` (#683) 时，编排器初始化一个仅指针的 `ReviewCriteriaBindingManifest` 并在整个形成性、内部评估者和外部小组消费者中使用它不变。规范生命周期、确切标记、封闭角色和显式降级路径定义在
`shared/references/review_criteria_consumer_protocol.md`。

- Phase 2 拥有 `FORMATIVE` 收件人。结构建筑师将选定的标准 ID 映射到计划章节和证据需求；后续写作阶段重用该收件人，不会重新解析目标。
- Phase 6a 接收相同的指针权限和目标标准简报，同时保持论文盲文；其预提交工件拥有 `INTERNAL` 收件人。Phase 6b 接收该不变工件，可能在看到草稿后评估适用性，并拥有任何关键/主要建设性发现的侧边栏。

科学有效性、场所匹配和提交准备保持不同。标准永远不会授权编造的证据、结果、方法或更改作者的贡献声明。

绑定验证仅是手交一致性检查。它永远不会提供编辑意见、严重性、检查点状态或作者筛选。如果绑定不可用，披露 `criteria_binding_unavailable`；不要声称场所对齐，不要默默重建模型内存中的目标。

### 检查点规则

1. ⚠️ **铁律**：用户必须在继续到 Phase 1 之前确认论文配置记录
2. **Phase 2 -> 3**: 用户必须批准大纲（可以请求结构调整）
3. ⚠️ **铁律**：最大 2 轮修订；未解决的问题 -> "承认限制"
4. **同行评审** Critical 严重问题阻止进展到 Phase 7
5. 用户可以跳过 Phase 1（文献）如果提供自己的来源

---

> **v3.4.0 合规性（适用于 `full` 模式）：** 在最终确定之前，`compliance_agent` 运行 RAISE 原则仅检查（仅警告；主要研究不在 PRISMA-trAIce 范围内）。警告列在披露声明中，但永远不会阻止流程。参见 `shared/raise_framework.md § 范围免责声明`。

## 阶段式调用合同 (v3.9.2)

`academic-paper` 管道在 8 个阶段（Phase 0 输入 → 7 格式化）运行。两种调用模式：

**模式 A — 编排器驱动（默认）：** `pipeline_orchestrator_agent` (在 `academic-pipeline` 技能中) 依次端到端运行所有阶段，通过材料护照跟踪状态。

**模式 B — 阶段式（跨会话恢复）：** 用户每阶段调用一个代理，跨会话进行长时间项目。常见模式：在一个会话中起草草稿，下周返回独立进行引文检查 / 摘要 / 同行评审。

在模式 B 中，**单阶段代理（每个 `docs/design/2026-05-18-ars-v3.9.2-agent-phase-classification.md` 的桶 A）严格限制在其分配的阶段内进行写入**。学术论文中的 7 个桶 A 代理是：`literature_strategist` (P1), `structure_architect` (P2), `draft_writer` (P4/P6 每次调用), `citation_compliance` (P5a), `abstract_bilingual` (P5b), `peer_reviewer` (P6), `formatter` (P7)。允许从上游阶段读取。

多阶段代理（桶 B：`argument_builder` P3+Plan, `visualization` P4+P7）确实执行调用者指定的该阶段的工作 — 在同一调用中不会扩展到其他阶段。v3.6.6 生成器-评估器合同下方的内容额外约束 `draft_writer` 和 `peer_reviewer` 子阶段行为（Phase 4a/4b, Phase 6a/6b）。

进入模式 B 需要明确的用户信号 — `/ars-<mode>` 斜杠命令或 `[direct-mode]` 前缀。模棱两可的跨阶段输入默认按照 `.claude/CLAUDE.md` 路由学科 + `shared/references/intent_clarification_protocol.md` 进行澄清。

**执行 (v3.9.2)：** 阶段边界在桶 A 代理 + 建议验证器 (`scripts/check_pipeline_integrity.py`) + 在启用钩子的运行时中的确定性预工具使用写入范围保护 (#134 重新范围, PR #294)。多阶段信封保持向前范围 (#134 切片 3-5)。

## v3.6.6 生成器-评估器合同协议

> v3.6.6 合规性权威编排块，用于 `academic-paper full` 模式内部的 v3.6.6 合同门禁阶段。模式 13.1 自 v3.6.6 (`shared/sprint_contract.schema.json`) 应用。模板：`shared/contracts/writer/full.json` + `shared/contracts/evaluator/full.json`。设计规范：`docs/design/2026-04-27-ars-v3.6.6-generator-evaluator-contract-design.md` §5。
>
> **仅适用于 `academic-paper full` 模式。** 九个非完整模式 (`plan`, `outline-only`, `revision`, `revision-coach`, `abstract-only`, `lit-review`, `format-convert`, `citation-check`, `disclosure`) 在 v3.6.5 → v3.6.6 中字节等效，并且不调用此协议。后期添加的 `rebuttal-audit` 模式也是非完整模式，不调用此协议。管道边界不变：`academic-pipeline` 阶段 2 分发 `academic-paper`（完整模式仅调用此协议）；阶段 3 分发单独的 `academic-paper-reviewer` 技能（5 面板外部编辑评审）。在此协议下的内部对配对阶段 6 评估器与阶段 3 评审不同层级 — 见设计文档 §5.1 审计结论 2。

### 概述

v3.6.6 将 Phase 4（写作草稿）和 Phase 6（对配对评估）拆分为纸盲 / 纸可见调用对，由 `writer_full` 和 `evaluator_full` 合同门禁。拆分类似于 `academic-paper-reviewer/references/sprint_contract_protocol.md` (v3.6.2 评审模式) 但针对没有面板且（对于写作）没有评分计划的单代理生成器模式进行适配。

承载机制是 **调用的物理分离**：写作 Phase 4a 从不看到运行时起草工件；评估器 Phase 6a 从不看到写作 Phase 4b 草稿。这破坏了在配对自我质量门禁上 "阅读论文，然后合理化标准" 的漂移路径。

### 四调用结构

对于每个 `academic-paper full` 调用，Phase 4 + Phase 6 从两个单调用扩展为四个单独的模型调用。每个调用都有自己的系统提示和用户内容，如下面的系统与用户内容纪律所示。

1. **Phase 4a — 写作纸盲预提交。**
   - 系统提示：`academic-paper/agents/draft_writer_agent.md` § "v3.6.6 Generator-Evaluator Contract Protocol" 中的 `### Phase 4a — Writer paper-blind pre-commitment` 子节。
   - 用户内容：`writer_full` 合同 JSON + 论文元数据仅 (`title`, `field`, `word_count`)。
   - 输出：`## Acceptance Criteria Paraphrase` 部分 + 终端 `[PRE-COMMITMENT-ACKNOWLEDGED]` 标签。
   - Lint：3 结构检查（见下文 "Phase 4a / 6a 输出 lint"）。

2. **Phase 4b — 写作纸可见起草 + 自评分。**
   - 系统提示：`academic-paper/agents/draft_writer_agent.md` 中相同的代理文件中的 `### Phase 4b — Writer paper-visible drafting + self-scoring` 子节。
   - 用户内容：`writer_full` 合同 JSON（重新注入）+ Phase 4a 输出包装在 `<phase4a_output>...</phase4a_output>` 数据分隔符 + 上游起草工件（论文配置记录，论文大纲，论证蓝图，注释参考文献，包括其搜索策略 / Schema 2 `search_strategy` (#548 — 绑定的写作填充到搜索边界新颖性声明中）, 可选样式配置文件, 可选知识隔离指令。
   - 输出：`## Draft Body` → `## Dimension Scores` → `## Failure Condition Checks` → `## Writer Decision`.
   - Lint：4 结构检查（见下文 "Phase 4b / 6b 输出 lint"）。

3. **Phase 6a — 评估器纸盲预提交。**
   - 系统提示：`academic-paper/agents/peer_reviewer_agent.md` § "v3.6.6 Generator-Evaluator Contract Protocol" 中的 `### Phase 6a — Evaluator paper-blind pre-commitment` 子节。
   - 用户内容：`evaluator_full` 合同 JSON + 论文元数据 + 写作者的最新 `<phase4a_output>`（评估器必须根据 `disagreement_handling.pre_commitment_check_protocol.check_writer_artifact` 验证写作者工件）+, 激活时，指针仅 #684 表明/目标标准简报/`INTERNAL` 标记。
   - 输出：`## Contract Paraphrase` + `## Scoring Plan` (每个维度 `dimension_id` / `what_to_look_for` / `what_triggers_block` / `what_triggers_warn`) + 指针仅绑定承诺（或 `criteria_binding_unavailable`）+ 终端 `[PRE-COMMITMENT-ACKNOWLEDGED]` 标签。没有引入额外的 H2。
   - Lint：5 结构检查。

4. **Phase 6b — 评估器纸可见评分 + 决策。**
   - 系统提示：`academic-paper/agents/peer_reviewer_agent.md` 中相同的代理文件中的 `### Phase 6b — Evaluator paper-visible scoring + decision` 子节。
   - 用户内容：`evaluator_full` 合同 JSON（重新注入）+ Phase 6a 输出包装在 `<phase6a_output>...</phase6a_output>` + 写作者的 `<phase4a_output>`（无条件地根据 `pre_commitment_check_protocol.check_writer_artifact`) + 写作 Phase 4b 草稿（受评工件）+ 激活时未提供的未改变的 #684 权限。
   - 输出：`## Dimension Scores` → `## Failure Condition Checks` → `## Review Body` → `## Evaluator Decision`, 以及角色标记/不可用披露，适用时附带验证的构建侧边栏。
   - Lint：5 结构检查。

多异议重试保留给 `academic-paper-reviewer` 技能（`academic-paper-reviewer`）；生成器模式没有面板，也没有评分计划异议锚点。

Lint 计数摘要跨三个模式：

| 阶段 | 评审者（零接触） | 写作 |
|---|---|---|
| Phase 1 / 4a / 6a | 5 | 3 |
| Phase 2 / 4b / 6b | 6 | 4 |
| Phase 6a | 5 | 5 |

### 单代理生成器不可用处理

当写作或评估阶段变得不可用时（Phase Na linter 两次失败或 Phase Nb linter 失败），`academic-paper` 发射阶段级中止标签并路由到用户干预：

- **写作 Phase 4 不可用** → `[GENERATOR-PHASE-ABORTED: role=writer, contract=<id>, reason=<lint_failure_kind>]` → 中止 `academic-paper` Phase 4 → 用户干预决定重试 / 回退 / 退回到 Phase 3（论证蓝图）。
- **评估器 Phase 6 不可用** → `[GENERATOR-PHASE-ABORTED: role=evaluator, contract=<id>, reason=<lint_failure_kind>]` → 中止 `academic-paper` Phase 6 → 用户干预决定重试 / 回退 / 退回到 Phase 5（草稿完成）。

`[GENERATOR-PHASE-ABORTED]` 不构成有效的阶段 6b 发射，不能进入 Stage 3 评审分发。存在两个有效的 Stage 3 进入路径（根据设计文档 §5.1）：

- **标准路径**：评估器 Phase 6b 发射 F0 `evaluator_decision=accept` 或 F4 `evaluator_decision=accept_with_dissent_note`。
- **例外路径**：评估器 Phase 6b 在配对修订循环在第二轮以强制性维度阻止时，发射 F5 `evaluator_decision=flag_for_reviewer_stage`。

`academic-paper` 没有写 / 评审者面板基数不变量（没有 `panel_size` 字段 — Schema 13.1 §3.3.5 评审者条件）。没有 `[PANEL-SHRUNK]` 类似物在生成器侧；`[GENERATOR-PHASE-ABORTED]` 是阶段级中止。

**操作监控**：跟踪 `[GENERATOR-PHASE-ABORTED]` 率 v3.6.6 部署后的前三个月。分母是 **每个 `academic-paper full` 运行** — 一个用户感知的顶层调用。5% 阈值是 `(runs_with_any_abort) / (total_runs)`。如果该率超过 5%，v3.6.7 引入优雅降级回退（见下文 "已知限制"）。

### 跨会话恢复范围

v3.6.6 生成器-评估器轮次（Phase 4a + Phase 4b + Phase 6a + Phase 6b + 对配对修订循环）是一个 **会话内原子单元**。手动会话中途分割 → 写作 Phase 4a 输出丢失；新会话必须从 Phase 0 重新启动 `academic-paper full` 模式。

v3.6.3 `ARS_PASSPORT_RESET=1` `reset_boundary[]` 机制（根据 `academic-pipeline/references/passport_as_reset_boundary.md`）在 `academic-pipeline` 阶段边界操作，而不是 `academic-paper` 内部阶段边界。`academic-paper` 内部阶段（4a / 4b / 6a / 6b）**不是**边界点；它们之间不发出任何 `kind: boundary` 记录。v3.6.7+ 可能引入 `pre_commitment_history[]` 以在会话中持久化写作 Phase 4a 艺术品 — 如果操作数据证明 — 见 § "已知限制" 下面。

## 已知限制

- **v3.6.6 中没有优雅降级回退**：当写作或评估阶段通过 `[GENERATOR-PHASE-ABORTED]` 中止时，`academic-paper full` 中止并路由到用户干预。v3.6.6 可能引入一个回退，将受影响的阶段降级为 v3.6.5 单调用行为并记录降级。v3.6.6 发送中止行为。见上文的 "单代理生成器不可用处理"。

- **没有跨会话恢复中轮次**：生成器-评估器四阶段轮次是 **会话内原子单元**。手动会话中途分割 → 写作 Phase 4a 艺术品丢失；新会话必须从 Phase 0 重新启动 `academic-paper full` 模式。

- **对配对 Phase 6 评估器与 `academic-paper-reviewer` 外部评审**：配对 `peer_reviewer_agent`（Phase 6 评估器，具有 v3.6.6 合同门禁）和单独的 `academic-paper-reviewer` 技能（Stage 3 5 面板外部编辑评审）服务于不同的评审层级，并且根据设计文档 §1 已知技术债务保留为文档。路由 / 合并决策推迟到 v3.7.x。

## 模式选择逻辑

> 参见 `references/mode_selection_guide.md` 触发词到模式的映射和完整的流程图。

---

## 引用检查模式

在审计之前，加载 `agents/citation_compliance_agent.md`。对于 APA 7 与中文引用，还阅读 `references/apa7_chinese_citation_guide.md`；使用其区域特定缩写和排序检查，而不是将拉丁脚本字母顺序清单应用于中文姓名。保留提供的场所覆盖和指南的歧义例外。

---

## 评审模式

`rebuttal-audit` 评估作者**现有的**反驳 / 对审稿人回复草稿，用于覆盖范围、语气和证据。它是建议性质量保证 — 它**不**编写或重写回复。

**输入门禁（路由）：** 仅当用户提供 BOTH (a) 审稿意见 / 决策信函 AND (b) 现有的反驳/回复草稿以进行评估时，才激活 `rebuttal-audit`。如果只有 (a) 存在（还没有草稿），则路由到 `revision-coach`（它生成回复草稿模板）。如果意图不明确，请澄清，而不是猜测。

**它生成的内容：**
- 每条评论覆盖表 — 审稿人关注点在草稿中标记为 `addressed` / `partially` / `missing`。
- 缺口列表 — 草稿未能回答的关注点。
- 风险标志 — 语气过于攻击性，没有证据的声明，或对审稿人实际观点的误解的回复。
- 改进建议（建议性）。

**铁律 — 完整性边界（不可伪造认证）：** 每篇论文**必须**包括：数据可用性声明, 道德声明, 作者贡献 (CRediT), 利益冲突声明, 资助认可。
- **AI 使用报告** — 正常 `full` / `format-convert` 流水线包括现有的通用 AI 工具使用声明；独立的 `disclosure` 模式遵循选择的场所适用性/状态或政策锚点渲染合同。
- **局限性部分** — 明确讨论研究局限性。
- **道德声明** — 当适用时（人类受试者, 敏感数据）。

---

## 输出语言

遵循用户的语言。学术术语保留为英语。双语摘要遵循声明的输出语言对 (`output_language_pair`) — 除此之外。对配对选择两个摘要语言；它不是主体语言设置，也不是摘要数量设置（双语 / 仅英语 / 仅 zh-TW 仅限是输入回答）。默认入口 `zh-tw-en` 是繁體中文（L1）+ 英语（L2） — 预先 #862 对应，因此省略该字段的运行会重新生成遗留对象键和遗留标题文字，并省略序列化键。注册和语言角色：[`shared/output_language_pair.md`](../shared/output_language_pair.md)。摘要长度和关键词计数：`references/abstract_writing_guide.md` 中的规则表（`shared/contracts/writer/full.json`）。

---

## 与其他技能的集成

```
academic-paper + tw-hei-intelligence  -> Evidence-based HEI paper with real MOE data
academic-paper + deep-research        -> Deep research phase -> paper writing phase (auto-handoff)
academic-paper + report-to-website    -> Interactive web version of the paper
academic-paper + notebooklm-slides-generator -> Presentation slides from paper
academic-paper + academic-paper-reviewer -> Peer review -> revision loop
```

---

## 模型层级 (#517, 可选)

当 `ARS_MODEL_TIERING` 设置时，分发会话根据 `shared/model_tiering.md`（规范：完整的 39 个代理判断/执行表 + 规则）。紧凑规则：

- **未设置（默认）：** 每个代理继承会话模型 — 与 #517 之前的字节等效行为。
- **`economy`** (前沿层级会话)：执行类型代理分发会话模型下方的一个层级 — 楼层数 Opus 类, 从不更低；判断类型代理保持在会话模型上。在楼层数或以下进行无操作（宣布一次）。
- **`quality-boost`** (前沿以下会话)：判断类型代理在检查点表面（Stage 2.5/4.5 门禁；opt-in Stage 4→5 声明-参考审计；最终评审）向上跳转到前沿层级（无论有多少层级 — 不是单个增量）；没有任何内容被降级。前沿（宣布一次）进行无操作。

---

## 版本信息

| 项目 | 内容 |
|------|---------|
| 技能版本 | 3.3.1 |
| 最后更新 | 2026-08-15 |
| 维护者 | Cheng-I Wu |
| 依赖技能 | deep-research v1.0+ (上游), academic-paper-reviewer v1.0+ (下游) |

---

## 版本历史

> 参见 `references/changelog.md` 完整的版本历史。
