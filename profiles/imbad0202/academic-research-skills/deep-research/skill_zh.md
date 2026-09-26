# 深度研究 — 通用学术研究代理团队

通用深度研究工具 — 一个领域无关的13代理团队，用于对任何主题进行严谨的学术研究。

**v2.4** 为报告编译器添加了写作质量改进：
- **风格配置文件消耗**（可选）— 如果从学术论文摄入中可用风格配置文件，报告编译器将其作为执行摘要和综合部分的软指导。学科惯例和报告客观性优先。
- **写作质量检查** — 报告编译器在最终确定之前使用 `academic-paper/references/writing_quality_check.md` 作为诊断指南（提示判断服从作者和场地要求，而不是配额），并将引用来源不支持的主张标记为 `[MATERIAL GAP]` 而不是含糊其辞 (#825)。

> **路由学科 (v3.9.2):** 插件和技能复制安装不会加载此存储库的 `.claude/CLAUDE.md`，因此其路由核心在下面重复，与 `shared/references/routing_core.md` 相同 (#892)。如果路由在加载此技能时尚未确定，请在分派任何代理之前应用核心。

<!-- routing-core:begin -->
**步骤 0 — 逃生舱检查（在任何分类之前）:** 如果用户的第一条消息以 `[direct-mode]` 开头（不区分大小写的字节0标记，可以可选地由空白/换行符前面的内容在解析时去除），记录这一事实，去除消息的前缀和周围空白，并直接跳转到 **步骤 1 显式意图处理** 在去除的内容上。字面值 `[direct-mode]` 不会传递给分派的代理。如果去除的消息本身没有命名的技能，步骤 1 会落入步骤 3 澄清（逃生舱绕过跨阶段澄清（步骤 2），而不是所有路由）。当标记被尊重并且命名的代理或技能需要消息没有提供的输入时，读取该代理或技能的文件并要求它需要的东西，用它的术语。没有字节0标记，命名代理不是显式意图：此类消息像任何其他一样通过步骤 1-3，因此跨阶段材料仍然得到步骤 2 澄清。

否则，对用户输入进行分类：

1. **显式明确意图** — 用户通过 `/ars-*` 斜杠命令调用特定技能，或使用无歧义触发关键字映射到单个技能（例如，“lit-review this”，“review my paper”，“draft an abstract”）：
   → 直接路由；没有澄清，没有协调器绕行。
   → 当模式的通常输入不存在或其中包含有其他日常意义时，请求保持显式。没有评论的修订请求是修订模式的“感觉某些部分需要改进”的情况，“revisar artículo”是审稿人的触发器。路由到该模式并让该模式处理缺失的内容；不要重新打开工作流程的选择。

2. **跨阶段材料检测** — 用户在没有命名特定技能的情况下提供了跨越 ≥ 2 个管道阶段的材料（例如，预先撰写的摘要 + 预先收集的文献；完整草稿 + 审稿人评论 + 参考文献列表）：
   → **澄清**。不要自动路由到单阶段代理。在 markdown 正文中将候选工作流程作为 a-d 选项列出（不通过 AskUserQuestion 工具）。参见 `shared/references/intent_clarification_protocol.md` 以获取消息模板。
   → 理由：当材料不能明确地识别意图时，澄清是最安全的行动。（v3.10 活动指挥官 (#134) 将通过结构化摄入处理此问题；v3.9.2 询问。）

3. **模糊意图，无材料** — 用户未提供任何材料且没有明确的请求：
   → 根据 `shared/references/intent_clarification_protocol.md` 进行澄清。

**反模式（由 #133 造成）:** 接收模糊的跨阶段材料并基于材料“看起来最接近”的阶段自动路由到单阶段代理。这绕过了协调器级的协调，并让子代理继承全部歧义而没有独立的监督。

<!-- routing-core:end -->

## 快速入门

**最小命令:**
```
研究人工智能对高等教育质量保证的影响
```

**苏格拉底模式:**
```
引导我的研究：出生率下降对私立大学的影响
引導我的研究：少子化對私立大學的影響
幫我釐清我的研究方向，我對高教品保有興趣但還不太確定
```

**执行:**
1. 范围界定 — 研究问题 + 方法论蓝图
2. 调查 — 系统文献搜索 + 来源验证
3. 分析 — 跨来源综合 + 偏见检查
4. 撰写 — 完整 APA 7.0 报告
5. 审阅 — 编辑 + 伦理 + 漏洞扫描
6. 修订 — 最终润色报告

---

## 触发条件

### 触发关键字

**英语**: research, deep research, literature review, systematic review, meta-analysis, PRISMA, evidence synthesis, fact-check, methodology, APA report, academic analysis, policy analysis, WHY HOW WHAT papers, 3W literature scan, guide my research, help me think through, monitor this topic, set up alerts

**Español**: investigación profunda, revisión de literatura, revisión sistemática, metaanálisis, síntesis de evidencia, verificación de datos, informe APA, comparación de artículos WHY HOW WHAT, escaneo de tres vías, guía mi investigación, ayúdame a razonar, monitorear este tema, configurar alertas

**繁體中文**: 研究, 深度研究, 文獻回顧, 文獻探討, 系統性回顧, 後設分析, 證據綜整, 事實查核, 三段式文獻掃描, WHY HOW WHAT 論文比較, 研究方法, 學術分析, 政策分析, 引導我的研究, 幫我釐清, 監測這個主題, 設定追蹤

**한국어**: 심층 연구, 문헌 조사, 문헌 고찰, 체계적 문헌고찰, 메타분석, 근거 종합, 사실 확인, 팩트체크, 연구 방법 설계, 학술 분석, 연구 방향을 잡아줘, 연구 주제 정하는 것을 도와줘, 무엇을 연구할지 모르겠어, 이 주제 계속 모니터링해줘

### 苏格拉底模式激活

当用户的 **意图** 符合以下任何模式时，**无论语言如何**，都激活 `socratic` 模式。检测含义，而不是精确的关键字。

**意图信号**（任何一个是足够的）:
1. 用户没有明确的研究问题，并且想要引导思考
2. 用户要求“引导”、“指导”或“指导”通过研究
3. 用户对要研究什么或从哪里开始表示不确定
4. 用户想要头脑风暴、探索或澄清研究方向
5. 用户描述了一个模糊的兴趣，但没有具体的、可回答的问题

**默认规则**: 当意图在 `socratic` 和 `full` 之间模糊时，**优先选择 `socratic`** — 比产生不想要的报告先引导更安全。用户可以随时切换到 `full`。

**示例触发器**（说明性，非详尽）:
"guide my research", "help me think through", 「引導我的研究」「幫我釐清」, 或任何语言的等效项

### 不触发

| 场景 | 使用替代方案 |
|----------|-------------|
| 写论文（不是研究） | `academic-paper` |
| 审阅论文（结构化审阅） | `academic-paper-reviewer` |
| 完整研究到论文的管道 | `academic-pipeline` |

### 快速模式选择指南

| 您的情况 你的狀況 | 推荐模式 | 范围 |
|----------------|-----------------|----------|
| 模糊想法，需要引導 / 有模糊想法，需要引導 | `socratic` | originality |
| 明确 RQ，需要全面研究 / 有明確 RQ，需要完整研究 | `full` | balanced |
| 需要快速摘要（30 分钟） / 需要快速摘要 | `quick` | fidelity |
| 有论文需要评估，然后再引用 | `review` | balanced |
| 需要主题的文獻回顧 | `lit-review` | fidelity |
| 需要快速论文比較扫描 | `three-way-scan` | fidelity |
| 需要验证特定主张 / 需要查核特定事實 | `fact-check` | fidelity |
| 需要系統性回顧 / 后設分析 | `systematic-review` | fidelity |

**范围** (v3.2): *fidelity* = 模板密集，可预测的输出; *balanced* = 默认; *originality* = 探索性，模板轻。参见 `shared/mode_spectrum.md` 以获取完整的跨技能范围表。

不确定？先用 `socratic` 模式——它将帮助您确定您需要什么。

---

## 代理团队 (13 代理)

| # | 代理 | 角色 | 阶段 |
|---|-------|------|-------|
| 1 | `research_question_agent` | 将模糊主题转换为精确的、FINER评分的研究问题，并界定范围边界 | 阶段 1, 苏格拉底层 1 |
| 2 | `research_architect_agent` | 设计方法论蓝图：范式、方法、数据策略、分析框架、有效性标准 | 阶段 1 |
| 3 | `bibliography_agent` | 系统文献搜索、来源筛选、APA 7.0 标注参考文献 | 阶段 2 |
| 4 | `source_verification_agent` | 事实核查、来源评分（证据层次）、掠夺性期刊检测、利益冲突标记 | 阶段 2 |
| 5 | `synthesis_agent` | 跨来源整合、矛盾解决、主题综合、差距分析 | 阶段 3 |
| 6 | `report_compiler_agent` | 起草完整的 APA 7.0 报告（标题 -> 摘要 -> 引言 -> 方法 -> 结果 -> 讨论 -> 参考文献） | 阶段 4, 6 |
| 7 | `editor_in_chief_agent` | Q1 期刊编辑审阅：原创性、严谨性、证据充分性、裁决（接受/修改/拒绝） | 阶段 5 |
| 8 | `devils_advocate_agent` | 挑战假设、测试逻辑谬误、寻找替代解释、确认偏差检查 | 阶段 1, 3, 5, 苏格拉底层 2, 4 |
| 9 | `ethics_review_agent` | AI 辅助研究伦理、归属完整性、双用途筛查、公平代表性 | 阶段 5 |
| 10 | `socratic_mentor_agent` | Q1 期刊编辑角色；通过苏格拉底提问引导研究思考，跨越 5 层 | 苏格拉底模式 (层 1-5) |
| 11 | `risk_of_bias_agent` | 使用 RoB 2 (RCTs) 和 ROBINS-I 评估偏倚风险；交通灯可视化 | 系统性回顾 (阶段 2) |
| 12 | `meta_analysis_agent` | 设计和执行元分析或叙述综合；效应量、异质性、GRADE | 系统性回顾 (阶段 3) |
| 13 | `monitoring_agent` | 研究后文献监测：摘要、撤回警报、矛盾发现 | 可选 (管道后) |

---

## 模式选择指南

参见 `references/mode_selection_guide.md` 以获取详细指南。

```
用户输入
    |
    +-- 已经有一个明确的研究问题？
    |   +-- 是 --> 需要符合 PRISMA 的系统性回顾 / 元分析？
    |   |           +-- 是 --> systematic-review 模式
    |   |           +-- 否 --> 需要完整报告？
    |   |                      +-- 是 --> full 模式
    |   |                      +-- 否 --> 只需要文獻？
    |   |                                 +-- 是 --> Need rapid paper comparison?
    |   |                                            +-- Yes --> three-way-scan 模式
    |   |                                            +-- No --> lit-review 模式
    |   |                                 +-- No --> quick 模式
    |   +-- 否 --> 想要被引导思考？
    |              +-- Yes --> socratic 模式
    |              +-- No --> full 模式 (阶段 1 将是交互式)
    |
    +-- 已经有文本需要审阅？ --> review 模式
    +-- 只需要事实核查？ --> fact-check 模式
```

---

## 阶段式编排工作流 (6 阶段)

```
用户: "研究 [主题]"
     |
=== 阶段 1: 范围界定 (交互式) ===
     |
     |-> [research_question_agent] -> RQ 简要说明
     |   - FINER 标准评分（可行性、趣味性、新颖性、伦理性、相关性）
     |   - 范围边界（在范围内 / 超出范围）
     |   - 2-3 个子问题
     |
     |-> [research_architect_agent] -> 方法论蓝图
     |   - 研究范式（实证主义 / 解释主义 / 实用主义）
     |   - 方法选择（定性 / 定量 / 混合）
     |   - 数据策略（原始 / 次要 / 两者兼有）
     |   - 分析框架
     |   - 有效性与可靠性标准
     |
     +-> [devils_advocate_agent] -- 检查点 1
         - RQ 清晰性和可回答性？
         - 方法是否适合问题？
         - 范围是否过于广泛或过于狭窄？
         - 裁决：通过 / 修改（附带具体反馈）
     |
     ** 用户确认，然后进入阶段 2 **
     |
=== 阶段 2: 调查 ===
     |
     |-> [bibliography_agent] -> 来源语料库 + 标注参考文献
     |   - 系统搜索策略（数据库、关键词、布尔运算）
     |   - 包含/排除标准
     |   - PRISMA 风格流程（如适用）
     |   - APA 7.0 标注参考文献
     |
     +-> [source_verification_agent] -> 验证和评分的来源
         - 证据层次评分（级别 I-VII）
         - 掠夺性期刊筛查
         - 利益冲突标记
         - 评估日期相关性
         - 来源质量矩阵
     |
=== 阶段 1: 分析 ===
     |
     |-> [synthesis_agent] -> 综合叙述 + 差距分析
     |   - 跨来源主题综合
     |   - 矛盾识别与解决
     |   - 证据趋同/分歧映射
     |   - 知识差距分析
     |   - 理论框架整合
     |
     +-> [devils_advocate_agent] -- 检查点 2
         - 挑选证据检查
         - 确认偏差检测
         - 逻辑链验证
         - 探索替代解释？
         - 裁决：通过 / 修改
     |
=== 阶段 4: 撰写 ===
     |
     +-> [report_compiler_agent] -> 完整 APA 7.0 草稿
         - 标题页
         - 摘要（150-250 字）
         - 引言（背景、问题、目的、RQ）
         - 文献综述 / 理论框架
         - 方法论
         - 结果 / 发现
         - 讨论（解释、启示、局限性）
         - 结论与建议
         - 参考文献 (APA 7.0)
         - 附录（如适用）
     |
=== 阶段 5: 审阅 (并行) ===
     |
     |-> [editor_in_chief_agent] -> 编辑裁决 + 行文反馈
     |   - 原创性评估
     |   - 方法论严谨性
     |   - 证据充分性
     |   - 论证连贯性
     |   - 写作质量（清晰度、简洁性、流畅性）
     |   - 裁决：接受 / 轻微修改 / 重大修改 / 拒绝
     |
     |-> [ethics_review_agent] -> 研究诚信审阅 + 人类受试者行政状态
     |   - AI 披露合规性
     |   - 归属完整性
     |   - 双用途筛查
     |   - 公平代表性检查
     |   - 诚信裁决：清除 / 条件清除 / 阻止
     |   - 人类受试者：准备状态和授权报告分别报告；需要机构决定
     |   - 权威绑定规划：精确要求 ID + 行为/消费者范围仅在 #666 回放验证的解决上下文门之后才提供
     |   - 候选规则跟踪：显示只有回放验证和表面检查的 #669 资产；永远不会将其用作路径结果或工作流程输入
     |   - 数据包结构：仅消耗回放验证的 #667 清单；确定性状态永远不会成为授权或内容充分性
     |   - 内容覆盖：仅消耗回放验证的 #681 `LLM-ADVISORY`; 保留确定性状态并报告效率为 `UNMEASURED`
     |
     +-> [devils_advocate_agent] -- 检查点 3
         - 最终漏洞扫描
         - 最强反论测试
         - “那么呢？”意义检查
         - 裁决：通过 / 修改
     |
=== 阶段 6: 修订 ===
     |
     +-> [report_compiler_agent] -> 最终报告
         - 解决编辑反馈
         - 解决伦理条件
         - 纳入魔鬼代言人见解
         - 最大 2 次修订循环
         - 剩余问题 -> “承认局限性”部分
```

### 检查点规则

1. ⚠️ **铁律**: **魔鬼代言人** 有 3 个强制检查点；**严重性** 问题是会导致核心结论无效或构成学术不端的问题。需要立即解决。

2. 修订循环限制为 **2 次**；剩余问题成为 “承认局限性”

3. ⚠️ **铁律**: **伦理审查** 停止用户一次以确认严重的 **诚信** 问题（捏造 / 抄袭 / 缺少 AI 披露 / 来源捏造 / 具体危害实现细节）。可以用记录的推理覆盖。它确认，它不否决。

4. 用户确认在阶段 1 之后才能继续

---

## 阶段式调用契约 (v3.9.2)

ARS 管道在 6 个阶段运行。两种调用模式：

**模式 A — 协调器驱动 (默认):** `pipeline_orchestrator_agent`（在 `academic-pipeline` 技能中）运行所有阶段，通过材料护照跟踪状态。

**模式 B — 阶段式 (跨会话恢复):** 用户每阶段调用一个代理，跨会话进行长期项目。常见模式通过 `ARS_PASSPORT_RESET=1` + `resume_from_passport=<hash>`（参见 `academic-pipeline/references/passport_as_reset_boundary.md`）。

在模式 B 中，**单阶段代理（每个 `docs/design/2026-05-18-ars-v3.9.2-agent-phase-classification.md` 的桶 A）严格保持在分配的阶段内进行写入**。允许从上游阶段读取。多阶段代理（桶 B：`devils_advocate_agent`, `report_compiler_agent`) 按调用者的调用指定的工作量执行——同一调用中不会扩展到其他阶段。

路由到模式 B 需要明确的用户信号——`/ars-<mode>` 斜杠命令或 `[direct-mode]` 前缀。模糊的跨阶段输入默认根据文件顶部的路由核心（步骤 2）+ `shared/references/intent_clarification_protocol.md` 进行澄清。

**执行 (v3.9.2):** 检查点边界在桶 A 代理上 + 建议验证器 (`scripts/check_pipeline_integrity.py`) + 在启用钩子的运行时中的确定性预工具使用写入范围保护 (#134 重新范围，PR #294)。多阶段信封保持向前范围 (#134 切片 3-5)。

---

## 苏格拉底模式：引导研究对话

5 层对话引导用户从模糊想法到具体研究问题。非生成式苏格拉底模式活动时，核心原则：⚠️ **铁律**: **永不直接给出答案**。显式候选生成退出将退出该模式，在显示任何明确标记的 AI 生成的候选之前。

> 参见 `references/socratic_mode_protocol.md` 以获取完整的 5 层对话流程、管理规则和自动结束条件。

### 选择阅读探针 (v3.5.1)

设置 `ARS_SOCRATIC_READING_PROBE=1` 启用一次性诚实探针，在 **目标导向** 的苏格拉底会话期间。当用户引用了特定论文时，导师要求他们释义其中一个段落。拒绝将记录而无需惩罚。默认关闭。参见 `agents/socratic_mentor_agent.md` §"可选阅读探针层"。

---

## 系统性回顾模式

PRISMA 2020 合规的系统性回顾，可选元分析。遵循 5 阶段协议：协议注册 -> 系统性搜索 -> 筛选 & 选择 -> 来源提取 & RoB -> 综合 & 报告。

> **v3.4.0 合规性:** `systematic-review` 模式在阶段 2.5（方法项目）和阶段 4.5（剩余项目 + RAISE 8-角色矩阵）触发 `compliance_agent`。PRISMA-trAIce 强制失败会阻止管道。参见 `shared/compliance_checkpoint_protocol.md`。

> 参见 `references/systematic_review_protocol.md` 以获取完整的 PRISMA 管道、检查点规则和元分析程序。

---

## 操作模式

| 模式 | 激活的代理 | 输出 | 字数 |
|------|---------------|--------|------------|
| `full` (默认) | 所有 9 个核心（排除 socratic_mentor, RoB, meta-analysis） | 完整 APA 7.0 报告 | 3,000-8,000 |
| `quick` | RQ + Bibliography + Verification + Report | 研究摘要 | 500-1,500 |
| `review` | Editor + Devil's Advocate + Ethics | 提供文本的审阅报告 | N/A |
| `lit-review` | Bibliography + Verification + Synthesis | 标注参考文献 + 综合 | 1,500-4,000 |
| `three-way-scan` | Bibliography + Verification (检索 + WHY/HOW/WHAT 提取) | 比较多篇论文的 WHY/HOW/WHAT + 跨论文综合 | 800-2,000 |
| `fact-check` | Source Verification only | 验证报告 | 300-800 |
| `socratic` | Socratic Mentor + RQ + Devil's Advocate | 研究计划摘要 (INSIGHT 收集) | N/A (交互式) |
| `systematic-review` | RQ + Architect + Bibliography + Verification + RoB + Meta-Analysis + Synthesis + Report + Editor + Ethics + DA | 完整 PRISMA 2020 报告 + 森林图数据 + GRADE 表 | 5,000-15,000 |

---

## 三方扫描模式 (WHY / HOW / WHAT)

当用户需要受控的论文短列表，但**尚未**需要完整的文献回顾报告时，使用 `three-way-scan`。

- **WHY**: 论文解决什么问题或瓶颈，为什么它很重要
- **HOW**: 论文使用什么策略、方法或技术路线
- **WHAT**: 论文发现了什么，构建了什么，或仍然未解决的

此模式有意比 `lit-review` 轻量级。它优先考虑：

1. 候选检索
2. 去重
3. 紧凑的每篇论文提取
4. 跨论文 WHY、HOW、分歧和未解决差距的综合

建议的每篇论文输出：

```markdown
## <paper title>
来源: <provider> | 年份: <year> | 链接: <url>

- WHY: ...
- HOW: ...
- WHAT: ...
```

然后添加：

- 共同的 `WHY`
- 分歧的 `HOW`
- 最强的 `WHAT`
- 未解决的全球差距

如果用户后来想要更广泛的证据矩阵、主题综合或 PRISMA 样的覆盖范围，请从 `three-way-scan` 升级到 `lit-review` 或 `systematic-review`。

---

## 失败路径

参见 `references/failure_paths.md` 以获取所有失败场景、触发条件和恢复策略。

关键失败路径摘要：

| 失败场景 | 触发条件 | 恢复策略 |
|---------|---------|---------|
| RQ 无法收敛 | 阶段 1 / 层 1 超过多个回合而仍然模糊 | 完整模式可能会使用其候选工作流程；苏格拉底模式总结用户已表达的方向或建议 `lit-review`，除非用户明确退出非生成式苏格拉底模式 |
| 文献不足 | bibliography_agent 找到的来源 < 5 个 | 扩展搜索策略，替代关键词 |
| 方法论不匹配 | RQ 类型与方法能力不匹配 | 返回阶段 1，建议 3 种替代方法 |
| 魔鬼代言人 CRITICAL | 发现致命逻辑错误 | 停止，解释问题，要求纠正 |
| 伦理 BLOCKED | 严重的诚信问题（不是主题内容） | 停止用户一次以确认；列出问题 + 补救路径；可以用记录的推理覆盖 |
| 苏格拉底非收敛 | > 10 轮未收敛 | 建议切换到完整模式 |
| 用户中途放弃 | 明确表示不想继续 | 保存进度，提供重新进入路径 |
| 只有中文文献 | 英文搜索返回空 | 切换到中文学术数据库 |

---

## 文献监测 (可选，管道后)

可选的研究后监测，监测研究领域的最新出版物。

> 参见 `references/literature_monitoring_strategies.md` 以获取跨学术数据库的设置说明。

---

## 代理协议：deep-research → academic-paper

研究完成后，以下材料可以传递给 `academic-paper`：

1. **研究问题简要说明** (来自 research_question_agent)
2. **方法论蓝图** (来自 research_architect_agent)
3. **标注参考文献** (来自 bibliography_agent)
4. **综合报告** (来自 synthesis_agent)
5. **[如果苏格拉底模式] INSIGHT 收集和研究计划摘要**
6. **预注册手柄** — 恰好一个构建产生的 `preregistration-artifact/1.0` 侧车（包括一个不可用的收据）以及当 `status=provided` 时，其明确命名的伴随字节 |

**触发**: 用户说“现在帮助我写一篇论文”或“根据这个写一篇论文”

`academic-paper` 的 `intake_agent` 将自动检测可用材料并跳过冗余步骤：
- 有 RQ 简要说明 -> 跳过主题范围界定
- 有参考文献 -> 跳过文献搜索
- 有综合 -> 加速发现 / 讨论 / 撰写
- 有预注册手柄 -> 严格验证它及其命名伴随字节；然后以字节对应的方式传递两者；永远不会从散文或模板中重建它 |

非 Shell `research_architect_agent` 仅提供显式调用声明和伴随句柄。在传递之前，必须运行名为 `build-preregistration-artifact` 的确定性子命令，在 `scripts/build_cross_document_consistency_advisory.py` 中，使用调用者持有的 RFC3339 `declared_at`。只有该构建者才能创建或更新侧车。稍后用户明确提供将创建一个新的构建者产生的侧车；省略或静默替换无效。

参见 `examples/handoff_to_paper.md` 以获取详细的传递示例。

---

## 完整学术管道

参见 `academic-pipeline/SKILL.md` 以获取完整工作流。

---

## 代理文件参考

| 代理 | 定义文件 |
|-------|----------------|
| research_question_agent | `agents/research_question_agent.md` |
| research_architect_agent | `agents/research_architect_agent.md` |
| bibliography_agent | `agents/bibliography_agent.md` |
| source_verification_agent | `agents/source_verification_agent.md` |
| synthesis_agent | `agents/synthesis_agent.md` |
| report_compiler_agent | `agents/report_compiler_agent.md` |
| editor_in_chief_agent | `agents/editor_in_chief_agent.md` |
| devils_advocate_agent | `agents/devils_advocate_agent.md` |
| ethics_review_agent | `agents/ethics_review_agent.md` |
| socratic_mentor_agent | `agents/socratic_mentor_agent.md` |
| risk_of_bias_agent | `agents/risk_of_bias_agent.md` |
| meta_analysis_agent | `agents/meta_analysis_agent.md` |
| monitoring_agent | `agents/monitoring_agent.md` |

---

## 参考文件

| 参考 | 目的 | 使用者 |
|-----------|---------|---------|
| `references/apa7_style_guide.md` | APA 7 版本快速参考 | report_compiler, editor_in_chief |
| `references/source_quality_hierarchy.md` | 证据金字塔 + 评分标准 | source_verification, bibliography |
| `references/methodology_patterns.md` | 研究设计模板 | research_architect |
| `references/logical_fallacies.md` | 30+ 逻辑谬误目录 | devils_advocate |
| `references/ethics_checklist.md` | AI 披露、归属、双用途 | ethics_review |
| `references/interdisciplinary_bridges.md` | 跨学科连接模式 | synthesis, research_architect |
| `references/socratic_questioning_framework.md` | 6 种苏格拉底问题类型 + 30+ 提示模式 | socratic_mentor |
| `references/failure_paths.md` | 12 失败场景及其触发条件和恢复路径 | 所有代理 |
| `references/mode_selection_guide.md` | 模式选择流程图和比较表 | orchestrator |
| `references/irb_decision_tree.md` | 可移植人类受试者导航辅助；不是权威，通用分类法，或路径确定 | ethics_review, research_architect |
| `shared/references/human_subjects_authority_protocol.md` | 精确权威选择，回放验证，行为/消费者过滤，以及解决上下文门 (#666) | ethics_review, research_architect |
| `shared/human_subjects_authority_registry.json` | 有界司法管辖权配置文件，包括精确要求 ID、权威锚点、受义务行为者，和消费者范围 | ethics_review, research_architect |
| `shared/contracts/human_subjects/resolved_authority_context.schema.json` | 指针仅解析的解决上下文形状；消费者仍然需要确定性回放验证 | ethics_review, research_architect |
| `shared/references/review_pathway_rule_trace_protocol.md` | 候选名称所有权，精确选择的配置文件谓词分区，回放，渲染，表面检查，和非消费者边界 (#669) | ethics_review, research_architect |
| `shared/contracts/human_subjects/review_pathway_trace_request.schema.json` | 关闭调用者拥有的候选映射；每个选择的配置文件 `pathway_trace` 要求都精确地一次 | 分发层 |
| `shared/contracts/human_subjects/review_pathway_rule_trace.schema.json` | 关闭候选仅谓词跟踪；回放和表面检查仍然是强制性的 | ethics_review, research_architect |
| `shared/references/submission_packet_manifest_protocol.md` | 确定性数据包清单，权威回放，状态，和非授权边界 (#667) | ethics_review, research_architect |
| `shared/contracts/human_subjects/submission_packet_manifest.schema.json` | 指针仅解析的确定性数据包清单形状；消费者仍然需要精确回放验证 | ethics_review, research_architect |
| `shared/references/authority_content_coverage_advisory_protocol.md` | 回放绑定的权威配置文件内容观察，证据行/1.1 起源，和非干扰边界 (#681) | ethics_review, research_architect |
| `shared/contracts/evidence/evidence_row_v1_1.schema.json` | 要求/期望/资产绑定的有界摘录行，用于 #681 提示 | ethics_review |
| `references/equator_reporting_guidelines.md` | EQUATOR 报告指南映射 | research_architect, report_compiler |
| `references/preregistration_guide.md` | 预注册决策树 + 平台 + 检查表 | research_architect |
| `shared/references/cross_document_consistency_advisory_protocol.md` | 精确预注册侧车所有权/回放加上 #672 提示和 #660 共存边界 | research_architect, academic-paper intake, 管道协调器 |
| `shared/contracts/passport/preregistration_artifact.schema.json` | 关闭的持久预注册手柄收据；伴随字节保留单独命名 | 分发层, intake, 管道协调器 |
| `references/systematic_review_toolkit.md` | Cochrane v6.4, PRISMA 2020, RoB 2, ROBINS-I, I² 指南, GRADE, 协议注册 | risk_of_bias, meta_analysis, bibliography, report_compiler |
| `references/literature_monitoring_strategies.md` | Google Scholar 警报, PubMed 警报, RSS 提要, 撤回监视器, 引用跟踪, 监测频率 | monitoring_agent |
| `references/argumentation_reasoning_framework.md` | 评估论证强度的认知框架：Toulmin 模型, 因果推理 (Bradford Hill), 推理最佳解释, 认知状态分类 | synthesis, devils_advocate, source_verification, socratic_mentor, research_architect |
| `references/socratic_mode_protocol.md` | 完整 5 层苏格拉底对话流程, 管理规则, 自动结束条件 | socratic_mentor, research_question |
| `references/systematic_review_protocol.md` | 完整 PRISMA 管道, 检查点规则, 元分析程序 | risk_of_bias, meta_analysis, bibliography, report_compiler |
| `references/cross_agent_quality_definitions.md` | 同一代理的统一定义。⚠️ 铁律: **严重性** 等级 = 会导致核心结论无效或构成学术不端的问题。需要立即解决。

> 参见 `references/cross_agent_quality_definitions.md` 以获取完整的同行评审来源级别, 评估标准, 和严重性定义。

---

## 与其他技能的集成

此技能是领域无关的，但可以与特定领域的技能组合使用：

```
deep-research + tw-hei-intelligence     -> 基于证据的高等教育政策研究
deep-research + report-to-website       -> 交互式研究报告
deep-research + podcast-script-generator -> 研究播客
deep-research + academic-paper          -> 完整研究到出版物管道
deep-research (socratic) + academic-paper (plan) -> 引导研究 + 论文计划
deep-research (systematic-review) + academic-paper -> PRISMA 系统性回顾论文
```

---

## 模型层级 (#517, 可选)

当 `ARS_MODEL_TIERING` 设置为激活时，分发会话根据 `shared/model_tiering.md`（规范：完整的 39 代理判断/执行表 + 规则）路由此技能的代理。紧凑规则：

- **未设置 (默认):** 每个代理继承会话模型——字节等价于 #517 之前的行為。
- **`economy`** (前沿层级会话): 执行类型代理分派会话模型下方的一个层级——地板 Opus 级别，永不更低；升级不会低于地板（宣布一次）。
- **`quality-boost`** (前沿会话下方): 判断类型代理在检查点表面（阶段 2.5/4.5 门; opt-in 阶段 4→5 声明–引用审计; 最终审阅）跳转到前沿层级（无论有多少层级——不是单个增量）; 任何内容都不会降级。前沿（地板）处为无效（宣布一次）。
- 未知值 → 警告一次，行为与未设置相同。层级是相对位置，永远不会固定锚定的模型 ID。当方向激活时，路由重复的同一阶段调用到相同的工人，使其提示缓存累积；未设置意味着分发形状保持字节等价。

---

## 版本信息

| 项目 | 内容 |
|------|---------|
| 技能版本 | 2.12.1 |
| 最后更新 | 2026-08-15 |
| 维护者 | Cheng-I Wu |
| 依赖技能 | academic-paper v1.0+ (下游) |

---

## 版本历史

> 参见 `references/changelog.md` 以获取完整的版本历史。
