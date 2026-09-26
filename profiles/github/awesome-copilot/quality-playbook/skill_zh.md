# 质量手册生成器

## 计划概述 — 首先阅读此部分，然后向用户解释

在阅读此技能的任何其他部分之前，请理解计划及其依赖关系。每个阶段都会产生供下一阶段依赖的工件。跳过或仓促完成一个阶段意味着所有下游阶段都将基于不完整的信息工作。

**阶段 0（先验运行分析）：** 如果存在先前的质量运行，则将其发现结果作为种子数据加载。这是自动的，并且仅适用于重新运行。

**阶段 1（探索）：** 首先运行 v1.5.3 文档摄入 (`python -m bin.reference_docs_ingest <目标>` 以遍历 `reference_docs/` — `cite/` 文件生成 `quality/formal_docs_manifest.json` 记录；顶级文件通过 `reference_docs_ingest.load_tier4_context(<目标>)` 以 Tier 4 上下文的形式加载）。然后分三个阶段探索代码库：由领域知识驱动的开放探索、领域知识风险分析以及选定的结构化探索模式。将所有发现写入 `quality/EXPLORATION.md`。此文件是基础 — 阶段 2 将其作为主要输入读取。

**阶段 2（生成）：** 读取 EXPLORATION.md 并生成质量工件：需求、章程、功能测试、代码审查协议、集成测试、规范审计协议、TDD 协议。 (`AGENTS.md` 在目标存储库的根目录下由协调器在阶段 6 之后生成，而不是你在阶段 2 中生成 — 见下文“文件 6”的合同。)

**阶段 3（代码审查）：** 对 HEAD 运行三遍代码审查。为每个确认的 bug 编写回归测试。

**阶段 4（规范审计）：** 三位独立的 AI 审计员根据需求审查代码。使用验证探针进行分诊。分诊后，相同的委员会运行 v1.5.3 Layer-2 语义引用检查 — 每位审阅员一个提示，按请求结构化 Tier 1/2 引用的判断，输出到 `quality/citation_semantic_check.json`。为净新发现编写回归测试。

**阶段 5（协调）：** 形成闭环 — 来自代码审查和规范审计的每个 bug 都会被跟踪、回归测试或明确豁免。运行 TDD 红绿循环。最终确定完整性报告。

**阶段 6（验证）：** 对所有生成的工件运行自检基准测试。检查内部一致性、版本戳正确性和收敛性。

**阶段 7（展示、探索、改进）：** 使用可扫描的摘要表向用户展示结果，提供对任何工件的深入分析，并提供改进路径菜单（迭代策略、需求细化、集成测试调优）。这是用户接管质量系统的交互阶段。

发现的每个 bug 都可以追溯到一个需求，每个需求都可以追溯到一个探索发现。

**关键依赖链：** 探索发现 → EXPLORATION.md → 需求 → 代码审查 + 规范审计 → Bug 发现。浅层探索会产生抽象需求。抽象需求会遗漏 bug。探索阶段是决定是赢得还是失去 bug 的地方。

**强制首次操作：** 在阅读并理解上述计划后，向用户打印以下消息，然后用你自己的话解释计划 — 你将做什么、每个阶段会产生什么以及为什么探索阶段最重要。强调探索从开放式的领域驱动调查开始，然后是领域知识风险分析，该分析推理出此类系统可能出现的问题，然后补充选定的结构化模式。不要逐字复制计划；请释义以展示你的理解。

> Quality Playbook v1.5.6 — by Andrew Stellman
> https://github.com/andrewstellman/quality-playbook

为特定代码库生成完整的质量系统。与从源代码机械工作的测试桩生成器不同，此技能首先探索项目 — 理解其领域、架构、规范和失败历史 — 然后生成基于其发现的质量手册。

## 如何运行此功能 — v1.5.4 自编码调用合同

如果操作员将你此技能（或指向任何 QPB 安装的靶标）并说 **“运行质量手册”** — 可能带有类似“这是一个引导运行”、“运行自身”或“自我审计”的提示 — 本节将告诉你确切要做什么。操作员不需要提供其他说明；规范调用、默认值、护栏和输出合同都生活在这里。

### 选择你的执行模式

QPB 提供两种执行形状。选择与你的运行时匹配的那个 — 错误的选择会产生 2026-04-30 引导测试暴露的 codex-on-codex 间接病理。

| 模式 | 当你是这个时 | 你做什么 |
|------|------------------|-------------|
| **A. 技能直接（UI 上下文）** | 你是一个编码代理（Claude Code、Cursor、Copilot、Codex 桌面版等）在自己的聊天中接收到此技能。你的运行时就是推理循环 — 你读取文件，你写入文件，你做决定。 | 自己使用外部的阶段提示（`phase_prompts/`）通过阶段 1 → 阶段 6。直接将工件写入目标的 `quality/` 目录。没有子进程，没有运行器。 |
| **B. 运行器驱动（CLI 自动化）** | 操作员故意调用 `python3 -m bin.run_playbook` — 以跨多个目标、驱动无头 CI 运行或将每个阶段的工作分配给与读取此文本不同的模型。 | 协调器为每个阶段生成一个 CLI 代理（`claude`、`copilot`、`codex` 或 `cursor`）。你（或阅读此文本的人）是操作端控制循环，而不是每个阶段的推理者。 |

**两种模式使用相同的阶段提示内容** — 存储库根目录下的 `phase_prompts/*.md` 文件是单一事实来源，由 `bin/run_playbook.py::_load_phase_prompt` 加载并由模式 A 的演练直接读取。两种模式的不同之处仅在于谁驱动 — 你（模式 A）或协调器子进程生成一个 CLI 代理（模式 B）。

**不确定时，默认为模式 A。** 如果操作员想要运行器驱动调用，他们会自己运行运行器；如果他们将“运行质量手册”粘贴到你的聊天中，他们希望由你驱动。模式 B 部分告诉你在操作员明确调用运行器时要做什么。

### 模式 A — 技能直接演练（UI 上下文）

操作员的提示只是 **“运行质量手册”**（或“运行自身”、“自我审计”等）。你直接驱动每个阶段。

对于每个阶段 1..6，按顺序：

1. **加载阶段提示。** 读取 `phase_prompts/phaseN.md`（通过为 `references/` 文档记录中说明的相同安装位置回退列表解析）。对于 `phase1.md`，替换 `{seed_instruction}`（说明“跳过阶段 0/0b”的引言 — 允许种子时为空字符串）和 `{role_taxonomy}`（从下文的角色分类块渲染的分类块）。对于 `phase2.md` 到 `phase6.md`，文件是纯文字 — 直接按字面读取。
2. **根据提示执行阶段。** 读取提示中命名的输入，进行分析，将输出写入目标的 `quality/` 目录。
3. **在阶段边界处停止。** 每个阶段提示都以“重要：不要进入阶段 N+1”的指令结束。遵守它。操作员通过说这样来进入下一个阶段。

你负责 — 没有协调器的结构化后援 — 执行与运行器强制执行的相同源不变量：**不要修改目标 `quality/` 目录之外的任何文件**。在模式 B 中，门会捕获此问题；在模式 A 中，你是门。2026-04-30 引导测试专门针对阶段 2 的 LLM 修改目标的根 `AGENTS.md` 失败 — 相同的失败模式适用于模式 A。

对于模式 A 的引导运行（自我审计）变体，见下文“引导模式” — 唯一的区别是目标就是 QPB 存储库，因此引用相同的 `phase_prompts/` 文件。

#### 模式 A 范围 — 涵盖范围、仅限模式-B

Council 2026-04-30 P1-3：上述按阶段演练将模式 A 限制为 **阶段 1..6**。以下表面故意仅限于模式 B — 如果操作员想要它们，请将它们指向运行器而不是试图自己驱动它们：

- **阶段 0 / 阶段 0b（从先验运行注入种子）。** 协调器处理种子发现、先验运行扫描和种子提示注入。在模式 A 中，将每个运行视为 `--no-seeds`（完全跳过阶段 0/0b，从阶段 1 开始）。如果操作员明确要求种子驱动探索，则切换到模式 B（`python3 -m bin.run_playbook --with-seeds <目标>`）。
- **阶段 7（交互式展示/探索/改进）。** 此阶段是与操作员关于生成的工件的来回对话；它在 `phase_prompts/` 中没有预烘焙的提示。在模式 A 中，阶段 6 之后直接在行内展示工件摘要表（见下文“此运行生成什么”的文件列表）并允许操作员通过对话驱动下一步探索 — 这就是阶段 7。没有协调器子进程要生成。
- **迭代策略（间隙/无过滤/均等/对抗性）。** 迭代重新进入手册，带有特定策略的补充。在模式 A 中，阶段 6 完成后干净地切换到模式 B 进行迭代：`python3 -m bin.run_playbook --next-iteration --strategy <名称> <目标>`。迭代提示（`phase_prompts/iteration.md`）是单一事实来源，但迭代协调循环（间隙 → 无过滤 → 均等 → 对抗性）是运行器的任务。模式 A 的操作员如果想在阶段 6 后进行迭代，应被告知：“阶段 6 已完成；运行 `python3 -m bin.run_playbook --full-run <目标>` 获取所有四个迭代策略，或显式选择一个策略 `--next-iteration --strategy gap`。”

如果操作员在模式 A 中要求其中之一，而请求是模糊的（例如，“也做迭代”），则明确切换模式，而不是即兴创作 — 即兴创作会导致提示内容偏离运行器的规范循环。

### 模式 B — 运行器驱动调用（CLI 自动化）

操作员自己运行 `python3 -m bin.run_playbook`（通常因为他们想要批处理、无头 CI 或将每个阶段的工作分配给不同的模型）。`bin/run_playbook.py` 处的协调器为每个阶段生成一个 CLI 代理，将其提供的外部化阶段提示，并聚合结果。

#### 规范调用

协调器是入口点。始终作为 Python 模块调用它：

```
python3 -m bin.run_playbook <目标>
```

**永远不要脚本式调用它**（`python bin/run_playbook.py ...`）。运行时护栏因相对导入需要打包执行而退出 `EX_USAGE=64`。

`<目标>` 是要审计的项目路径。对于引导运行（目标就是 QPB 存储库），从存储库根目录运行 `.`。对于任何其他目标，传递该目标存储库根目录的路径。

#### 默认行为（无标志）

裸调用触发 **完整运行**：所有 6 个阶段（探索 → 生成 → 代码审查 → 规范审计 → 协调 → 验证）后跟所有 4 个迭代策略（间隙 → 无过滤 → 均等 → 对抗性），在同一个会话中同步执行。任何先前的 `quality/` 目录在新的运行开始前自动存档到 `quality/previous_runs/<TIMESTAMP>/`。

这是规范操作员路径。不要请求添加标志；默认值就是答案。

当裸调用启动时，协调器会发出一条 stderr 横幅，命名与 v1.5.3 相比的成本变化（约 5–10 倍的旧版“仅阶段 1”默认值）。该横幅是信息性的；让它滚动。

#### 常见覆盖

仅在操作员要求特定内容时使用：

| 需要 | 标志 | 效果 |
|------|------|--------|
| 运行单个阶段 | `--phase N`（其中 N ∈ 1..6） | 恢复 v1.5.3“仅探索”模式，使用 `--phase 1`。 |
| 跳过迭代策略 | 省略 `--iterations` 并传递 `--phase 1,2,3,4,5,6` | 阶段运行；迭代不运行。 |
| 特定迭代 | `--strategy <名称> --next-iteration` | 使用选定策略对现有的 `quality/` 运行进行迭代。 |
| 多目标 | 传递多个位置目标 | 每个目标独立运行。 |
| 每阶段 CLI 代理 | `--claude` / `--copilot` / `--codex` / `--cursor` | 选择协调器生成的 CLI 运行器。默认是 `--copilot`。v1.5.4 添加了 `--cursor` 运行器（cursor-cli 3.1+）。 |

#### 从部分/中止的运行器驱动运行中恢复

Council 2026-04-30 P1-4：操作员卫生指导（清理中止运行后）生活在下文“引导模式”部分（“引导运行操作员卫生”）中 — 恢复是相同的：`git restore quality/` 以丢弃部分阶段 1/2 输出，然后重新调用。**不要**编辑 `quality/` 外的文件以“整理” — 源不变量会在下一次运行时触发。见引导模式卫生段落以获取完整机制；它适用于中止发生在自我审计运行或对外部目标期间的情况。

### 引导模式（在自身上运行 QPB）

当操作员说“这是一个引导运行”或“我们在运行 QPB 在自身上”或“自我审计”：

1. 确认工作目录是 QPB 存储库根（或 `cd` 到那里）。
2. 调用 `python3 -m bin.run_playbook .` — 相同的规范形式，目标是 `.`。
3. 协调器自动将现有的 `quality/` 树存档到 `quality/previous_runs/<TIMESTAMP>/`；你不需要手动清理任何东西。

运行与其他目标相同。唯一区别是审计对象是手册本身，因此生成的工件描述 QPB 的质量系统。

**引导运行操作员卫生 — 从部分/中止运行中恢复。** 如果先前的引导运行中途中止（例如，源不变量触发、阶段提示出错、操作员按 Ctrl-C），工作树可能包含一个半写入的 `quality/` 目录和一个标记已放弃存档的 `quality/previous_runs/<TIMESTAMP>/.partial` 哨兵。在重新调用之前，运行 `git restore quality/`（如果你想要一个干净的起点，运行 `git clean -fd quality/`）以丢弃中止运行未提交的阶段 1/2 输出。协调器将重新存档现在纯净的 `quality/` 树并开始干净。**不要**编辑 `quality/` 外的文件以“整理” — `quality/` 外的任何内容都是 QPB 源；为了清理而触摸它会在下一次运行时触发源不变量。2026-04-30 引导测试暴露了此精确的恢复问题：操作员有一个来自中止阶段 2 的半写入 `quality/`，重新运行而不恢复导致下一次运行时存档了陈旧的阶段 1 工件，混淆了下一个运行的存档。

### v1.5.4 机制（指针式，非重复设计文档）

与 v1.5.3 相比的新内容，以指针形式（规范架构生活在 `docs/design/QPB_v1.5.4_Design.md` 第 1 部分）：

- **第一阶段生成 `quality/exploration_role_map.json`** — 在探索过程中通过 AI 驱动的逐文件角色标记。每个范围内的文件都会从分类中获得一个角色（`skill-prose`、`skill-reference`、`skill-tool`、`code`、`test`、`docs`、`config`、`fixture`、`formal-spec`、`playbook-output`）。角色映射驱动着下游的每个管道激活决策。
- **`INDEX.md` 使用 `schema_version: "2.0"`**，其中 `target_role_breakdown` 字段包含每个角色的计数和百分比。v1.5.3 的 `target_project_type` 枚举已退役（遗留存档保持可读）。
- **管道从角色映射激活，而不是从项目类型标签激活。** 四阶段技能推导管道在标记为 `skill-prose` / `skill-reference` 的文件上运行。代码审查管道在标记为 `code` 的文件上运行。文本到代码差异检查在标记为 `skill-tool` 的文件上运行。当角色映射显示某个角色为零时，该管道干净地无操作。没有代码/技能/混合的三分法——当两个表面都存在时，两个管道都会运行（“始终-Hybrid 下游”模型）。
- **存档目录是 `quality/previous_runs/`**（在 v1.5.3 中是 `quality/runs/`）；旧路径上的遗留存档保持可读。
- **第六阶段结束重组** 将中间产物移至 `quality/workspace/` 下，以便顶级 `quality/` 目录主要由规范交付物（REQUIREMENTS.md、BUGS.md 等）主导。门的路径解析器从两种布局中读取。

您不需要在提示侧推理中重新推导任何这些内容；协调器的提示已经编码了它们。如果您遇到与这里总结的架构冲突的阶段提示，请遵循阶段提示——它是每个阶段合同的规范来源。

### 检查约束（机器可检查；视为硬约束）

这些不是建议；协调器执行它们，违反则中止运行：

1. **同步执行——不使用子代理委派。** 在同一会话中自己运行每个阶段。**不要使用任务工具**、子代理调度、后台代理调用或任何“将阶段 2–6 委派给工人”模式。B-15 失效模式是真实的：第一阶段完成，阶段 2–6 在失去其父会话的委派代理中静默失效，运行者自我标记 `-PARTIAL`，操作员得不到任何错误的信号。v1.5.4 提示明确禁止此操作。
2. **运行期间不要修补 QPB 源代码。** 如果在运行期间遇到 `bin/`、`.github/skills/`、`agents/`、`references/`、`SKILL.md`、`schemas.md` 或 `AGENTS.md` 中的错误，**停止并报告**：命名文件：行号，描述故障，提出修复形状——但不要应用修复。协调器在运行开始时捕获 git-SHA 基线，并在每个阶段边界验证源树未更改；自主修补会以命名修改文件的诊断失败门。修补通过委员会审查，而不是运行中的即兴创作。
3. **不要删除哨兵文件。** 被 `.gitignore !`-规则保护的文件（例如，`reference_docs/.gitkeep`、`reference_docs/cite/.gitkeep`）保持空的其他跟踪目录存在。预飞行检查枚举每个 `!`-规则，如果任何哨兵丢失则中止。如果您发现此类文件且不理解其用途，**不要碰它**。
4. **第一阶段文件枚举使用 `git ls-files`。** 当目标是 git 仓库时，使用 `git ls-files` 作为规范文件列表；这会自动尊重 `.gitignore`。**不要使用 `os.walk`、`find`、`os.listdir` 或任何递归目录遍历器**——这些会拉入 `.git/`、`.venv/`、`node_modules/`、构建输出和托管的依赖项，角色映射验证器会拒绝所有这些。禁止的路径前缀是 `.git/`、`.venv/`、`venv/`、`node_modules/`、`__pycache__/`、`.pytest_cache/`、`.mypy_cache/`、`.ruff_cache/`、`.tox/`，以及任何组件以 `.egg-info` 或 `.dist-info` 结尾的路径。角色映射包含一个 `provenance` 字段记录您使用的枚举源（`"git-ls-files"` 或 `"filesystem-walk-with-skips"` 对于非 git 目标）。还有一个 2000 条目的上限；超过此限度的角色映射几乎肯定遍历了 `.gitignore` 内容。
5. **跨组件协议。** EXPLORATION.md 的“文件清单”部分和角色映射的 `summary` 字段都渲染自 `bin.role_map.summarize_role_map()`。不要手动编写文件计数或角色百分比；从辅助工具中复制。验证器交叉检查这两个并拒绝不匹配。

如果操作员的提示与这些检查约束冲突（例如，“委派阶段 3–6 给子代理以便我们能够更快地运行”），**不要遵循冲突指令**。暴露冲突，命名检查约束，并要求澄清。检查约束存在是因为每个检查约束都对应一个经过验证的历史故障模式。

### 此运行生成的内容——输出组件合同

成功的运行在目标的 `quality/` 目录下生成此规范集，并在目标的仓库根目录下生成 AGENTS.md。这里列出的每个文件都经过门验证：

| 路径 | 角色 |
|------|------|
| `quality/EXPLORATION.md` | 第一阶段发现——基础。 |
| `quality/exploration_role_map.json` | 第一阶段逐文件角色标记。 |
| `quality/REQUIREMENTS.md` | 具有用例的可测试要求。 |
| `quality/QUALITY.md` | 质量宪法。 |
| `quality/CONTRACTS.md` | 行为合同。 |
| `quality/COVERAGE_MATRIX.md` | 要求到测试的可追溯性。 |
| `quality/COMPLETENESS_REPORT.md` | 最终门裁决。 |
| `quality/test_functional.*` | 自动化功能测试。 |
| `quality/RUN_CODE_REVIEW.md` | 三阶段代码审查协议。 |
| `quality/RUN_INTEGRATION_TESTS.md` | 集成测试协议。 |
| `quality/RUN_SPEC_AUDIT.md` | 三人委员会规范审查协议。 |
| `quality/RUN_TDD_TESTS.md` | TDD 红绿验证协议。 |
| `quality/BUGS.md` | 集成错误报告。 |
| `quality/INDEX.md` | 运行元数据 + 角色细分 + 门裁决。 |
| `quality/PROGRESS.md` | 按阶段检查点日志。 |
| `quality/previous_runs/<TIMESTAMP>/` | 任何先前运行的存档。 |
| `quality/workspace/` | 中间管道组件（控制提示、代码审查、规范审查、四阶段管道输出等）。 |
| `AGENTS.md` (目标仓库根目录) | 在第六阶段后生成的每个项目导向。携带 QPB 哨兵标记，以便未来运行检测 QPB 管理的副本。 |

`quality/INDEX.md` 中的门裁决（`pass` / `partial` / `fail`）是面向操作员的运行总结。如果不是 `pass`，则在考虑运行完成之前暴露原因。

### 定位参考文件

此技能引用 `references/` 目录中的文件（例如，`references/iteration.md`、`references/review_protocols.md`）。位置取决于技能的安装方式。当提到参考文件时，按顺序检查这些路径，并使用第一个存在的文件来解析它：

1. `references/`（相对于 SKILL.md——在从技能目录运行时有效）
2. `.claude/skills/quality-playbook/references/`（Claude 代码安装）
3. `.github/skills/references/`（GitHub Copilot 平面安装）
4. `.github/skills/quality-playbook/references/`（备用 Copilot 安装）

此技能中所有参考文件引用都使用短形式 `references/filename.md`。如果相对路径无法解析，则按上述后备列表进行遍历。

## 这为什么存在

大多数软件项目都有测试，但很少有项目有质量 *系统*。测试检查代码是否工作。质量系统回答更难的问题：对于这个特定项目，“工作正确”意味着什么？它有哪些可能失败的方式，而测试无法捕获？每个开发者（人类或 AI）在触摸此代码之前应该知道什么？

没有质量剧本，每个新贡献者（以及每个新的 AI 会话）都从零开始——猜测什么重要，编写看起来不错但无法捕获真实错误的测试，并重新发现已经发现和修复了几个月的问题。质量剧本使标准明确、持久和继承。

## 此技能生成的内容

九个文件共同构成一个可重复的质量系统：

| 文件 | 目的 | 为什么重要 | 是否执行代码？ |
|------|---------|----------------|----------------|
| `quality/QUALITY.md` | 质量宪法——覆盖目标、适用场景、剧院预防 | 每个AI会话首先阅读此文件。它告诉他们“足够好”意味着什么，以免他们猜测。 | 否 |
| `quality/REQUIREMENTS.md` | 可测试要求，具有项目概述、用例和叙述——由五阶段管道（合同提取→推导→验证→完整性→叙述）生成） | 代码审查第二阶段和第三阶段的基础。没有要求，审查仅限于结构异常（约65%上限）。有了它们，审查可以捕获意图违规——缺失错误、跨文件矛盾和代码阅读 alone 无法发现的差距。 | 否 |
| `quality/test_functional.*` | 从规范派生的自动化功能测试 | 安全网。与规范说应该发生的事情相关联的测试，而不仅仅是代码做什么。使用项目的语言：`test_functional.py`（Python）、`FunctionalSpec.scala`（Scala）、`functional.test.ts`（TypeScript）、`FunctionalTest.java`（Java）等。 | **是** |
| `quality/RUN_CODE_REVIEW.md` | 三阶段代码审查协议：结构审查、要求验证、跨要求一致性 | 仅结构审查会遗漏约35%的真实缺陷。三阶段管道添加了要求验证和一致性检查——有实验证据表明它可以找到结构审查条件 invisible 的错误。 | 否 |
| `quality/RUN_INTEGRATION_TESTS.md` | 集成测试协议——跨所有变体的端到端管道 | 单元测试通过，但系统是否与真实外部服务端到端工作？ | **是** |
| `quality/BUGS.md` | 集成错误报告，包含补丁 | 每个确认的错误在一个地方，包含复现细节、规范基础、严重性和补丁引用。关于什么已损坏以及如何验证的单一事实来源。 | 否 |
| `quality/RUN_TDD_TESTS.md` | TDD 红绿验证协议 | 证明每个错误都是真实的（测试在未修补的代码上失败），并且每个修复都有效（修补后测试通过）。比单独的错误报告更有力的证据——维护人员信任 FAIL→PASS 演示。 | **是** |
| `quality/RUN_SPEC_AUDIT.md` | 三人委员会多模型规范审查协议 | 没有单个AI模型能捕获所有内容。三个具有不同盲点的独立模型可以捕获任何单独模型会遗漏的缺陷。 | 否 |
| `AGENTS.md` | 任何在此项目上工作的AI会话的引导上下文 | “首先阅读的文件”。没有它，AI会话会浪费他们第一个小时弄清楚发生了什么。 | 否 |

加上输出目录：`quality/code_reviews/`、`quality/spec_audits/`、`quality/results/`、`quality/history/`。

管道还生成支持组件：`quality/PROGRESS.md`（按阶段检查点日志，带有累积 BUG 跟踪器）、`quality/CONTRACTS.md`（行为合同）、`quality/COVERAGE_MATRIX.md`（可追溯性）、`quality/COMPLETENESS_REPORT.md`（最终门）、`quality/VERSION_HISTORY.md`（审查日志）。第七阶段还可以生成 `quality/REVIEW_REQUIREMENTS.md`（交互式审查协议）和 `quality/REFINE_REQUIREMENTS.md`（精炼阶段协议）以进行迭代改进。

两个关键交付物是要求文件和功能测试文件。要求文件（`quality/REQUIREMENTS.md`）为代码审查协议的验证和一致性阶段提供输入——这是代码审查捕获比结构异常更多的原因。功能测试文件（按项目的语言和测试框架约定命名）是自动化的安全网。Markdown 协议是人类和AI代理的文档。

### 完整组件合同

质量门（`quality_gate.py`）验证这些组件。如果门检查它，此技能必须指示其创建。这是规范列表——此处未列出的任何组件不应强制执行门，并且任何门检查都应追溯到此处列出的组件。

| 组件 | 位置 | 是否必需 | 创建于 |
|----------|----------|-----------|------------|
| 正式文档清单（v1.5.3） | `quality/formal_docs_manifest.json` | 是 | 第一阶段（`bin/reference_docs_ingest.py`） |
| 要求清单（v1.5.3） | `quality/requirements_manifest.json` | 是 | 第二阶段 |
| 用例清单（v1.5.3） | `quality/use_cases_manifest.json` | 是 | 第二阶段 |
| 错误清单（v1.5.3） | `quality/bugs_manifest.json` | 如果找到错误 | 第三阶段/第四阶段/第五阶段 |
| 引用语义检查（v1.5.3） | `quality/citation_semantic_check.json` | 是 | 第四阶段（第二层委员会） |
| 探索发现 | `quality/EXPLORATION.md` | 是 | 第一阶段 |
| 质量宪法 | `quality/QUALITY.md` | 是 | 第二阶段 |
| 要求（UC 标识符） | `quality/REQUIREMENTS.md` | 是 | 第二阶段 |
| 行为合同 | `quality/CONTRACTS.md` | 是 | 第二阶段 |
| 功能测试 | `quality/test_functional.*` | 是 | 第二阶段 |
| 回归测试 | `quality/test_regression.*` | 如果找到错误 | 第三阶段 |
| 代码审查协议 | `quality/RUN_CODE_REVIEW.md` | 是 | 第二阶段 |
| 集成测试协议 | `quality/RUN_INTEGRATION_TESTS.md` | 是 | 第二阶段 |
| 规范审查协议 | `quality/RUN_SPEC_AUDIT.md` | 是 | 第二阶段 |
| TDD 验证协议 | `quality/RUN_TDD_TESTS.md` | 是 | 第二阶段 |
| 错误跟踪器 | `quality/BUGS.md` | 是 | 第三阶段 |
| 覆盖矩阵 | `quality/COVERAGE_MATRIX.md` | 是 | 第二阶段 |
| 完整性报告 | `quality/COMPLETENESS_REPORT.md` | 是 | 第二阶段（基线）、第五阶段（最终裁决） |
| 进度跟踪器 | `quality/PROGRESS.md` | 是 | 整个过程中 |
| AI 引导 | `AGENTS.md` (目标仓库根目录) | 是 | 由协调器在第六阶段后生成——不是第二阶段的交付物 |
| 错误报告 | `quality/writeups/BUG-NNN.md` | 如果找到错误 | 第五阶段 |
| 回归补丁 | `quality/patches/BUG-NNN-regression-test.patch` | 如果找到错误 | 第三阶段 |
| 修复补丁 | `quality/patches/BUG-NNN-fix.patch` | 可选 | 第三阶段 |
| TDD 可追溯性 | `quality/TDD_TRACEABILITY.md` | 如果错误有红阶段结果 | 第五阶段 |
| TDD 侧车 | `quality/results/tdd-results.json` | 如果找到错误 | 第五阶段 |
| TDD 红阶段日志 | `quality/results/BUG-NNN.red.log` | 如果找到错误 | 第五阶段 |
| TDD 绿阶段日志 | `quality/results/BUG-NNN.green.log` | 如果存在修复补丁 | 第五阶段 |
| 集成侧车 | `quality/results/integration-results.json` | 当运行集成测试时 | 第五阶段 |
| 机械验证脚本 | `quality/mechanical/verify.sh` | 是（基准） | 第二阶段 |
| 验证收据 | `quality/results/mechanical-verify.log` + `.exit` | 是（基准） | 第五阶段 |
| 分诊探测 | `quality/spec_audits/triage_probes.sh` | 当运行分诊时 | 第四阶段 |
| 代码审查报告 | `quality/code_reviews/*.md` | 是 | 第三阶段 |
| 规范审查报告 | `quality/spec_audits/*auditor*.md` + `*triage*` | 是 | 第四阶段 |
| 重新检查结果（JSON） | `quality/results/recheck-results.json` | 当运行重新检查时 | 重新检查 |
| 重新检查摘要（MD） | `quality/results/recheck-summary.md` | 当运行重新检查时 | 重新检查 |
| 种子检查 | `quality/SEED_CHECKS.md` | 如果运行了 Phase 0b | Phase 0b |
| 运行元数据 | `quality/results/run-YYYY-MM-DDTHH-MM-SS.json` | 是 | 第一阶段（创建）、整个过程中（更新） |

**侧车 JSON 生命周期**：在最终确定 `tdd-results.json` 之前编写所有错误报告——侧车的 `writeup_path` 字段必须指向一个现有文件，而不是占位符。同样，运行集成测试并收集结果，然后再编写 `integration-results.json`。

```json
{
  "schema_version": "1.1",
  "skill_version": "1.5.6",
  "date": "2026-04-12",
  "project": "repo-name",
  "bugs": [
    {
      "id": "BUG-001",
      "requirement": "REQ-003",
      "red_phase": "fail",
      "green_phase": "pass",
      "verdict": "TDD verified",
      "fix_patch_present": true,
      "writeup_path": "quality/writeups/BUG-001.md"
    }
  ],
  "summary": {
    "total": 3, "confirmed_open": 1, "red_failed": 0, "green_failed": 0, "verified": 2
  }
}
```

`verdict` 必须是以下之一：`"TDD verified"`、`"red failed"`、`"green failed"`、`"confirmed open"`、`"deferred"`。`date` 必须符合 ISO 8601 标准（YYYY-MM-DD），不能是占位符，且不能是未来的日期。

**`quality/results/integration-results.json`:**

```json
{
  "schema_version": "1.1",
  "skill_version": "1.5.6",
  "date": "2026-04-12",
  "project": "repo-name",
  "recommendation": "SHIP",
  "groups": [{ "group": 1, "name": "Group 1", "use_cases": ["UC-01"], "result": "pass", "tests_passed": 3, "tests_failed": 0, "notes": "" }],
  "summary": { "total_groups": 12, "passed": 11, "failed": 1, "skipped": 0 },
  "uc_coverage": { "UC-01": "covered_pass", "UC-02": "not_mapped" }
}
```

`recommendation` 必须是以下之一：`"SHIP"`、`"FIX BEFORE MERGE"`、`"BLOCK"`。`uc_coverage` 将 REQUIREMENTS.md 中的 UC 标识符映射到覆盖状态。

### 运行元数据

每次 playbook 运行都会在 `quality/results/run-YYYY-MM-DDTHH-MM-SS.json` 创建一个带时间戳的元数据文件。这能够实现多模型比较和运行历史跟踪。

**生命周期：** 在 Phase 1 开始时创建此文件。每完成一个阶段，更新 `phases_completed`、`bug_count` 和 `end_time`。最终更新在终端关卡后进行。

```json
{
  "schema_version": "1.0",
  "skill_version": "1.5.6",
  "project": "repo-name",
  "model": "claude-sonnet-4-6",
  "model_provider": "anthropic",
  "runner": "claude-code",
  "start_time": "2026-04-16T10:30:00Z",
  "end_time": "2026-04-16T11:45:00Z",
  "duration_minutes": 75,
  "phases_completed": ["Phase 0b", "Phase 1", "Phase 2", "Phase 3", "Phase 4", "Phase 5"],
  "iterations_completed": ["gap", "unfiltered", "parity", "adversarial"],
  "bug_count": 12,
  "bug_severity": { "HIGH": 2, "MEDIUM": 5, "LOW": 5 },
  "gate_result": "PASS",
  "gate_fail_count": 0,
  "gate_warn_count": 2,
  "notes": ""
}
```

**必须字段：** `schema_version`、`skill_version`、`project`、`model`、`start_time`。其他字段随着运行进度自动填充。`model` 应该是确切的模型字符串（例如，`"claude-sonnet-4-6"`、`"gpt-4.1"`、`"claude-opus-4-6"`）。`runner` 用于标识执行 playbook 的工具（例如，`"claude-code"`、`"copilot-cli"`、`"cursor"`、`"cowork"`）。`duration_minutes` 由 `end_time - start_time` 计算得出。如果无法确定模型或 runner，请使用 `"unknown"`。

## 如何使用

**playbook 设计为一次运行一个阶段。** 每个阶段都在自己的会话中运行，具有干净的上下文窗口，并在磁盘上生成文件供下一个阶段读取。这比一次性运行所有阶段效果更好——每个阶段都能获得完整的上下文窗口进行深度分析，而不是与其他阶段争夺空间。

**默认行为：仅运行 Phase 1。** 当有人说 "运行质量 playbook" 或 "执行质量 playbook" 时，运行 Phase 1（探索）并停止。Phase 1 完成后，告诉用户发生了什么以及下一步该做什么。用户会明确地推进每个阶段。

### 交互协议——如何指导用户

**每个阶段和每个迭代之后，停止并打印指导信息。** 使用 `#` 标题使其在聊天中突出显示。指导信息必须包括：刚刚发生了什么（一行）、关键输出是什么，以及继续的精确提示。见每个阶段部分下方定义的结束阶段消息。

**如果用户说 "继续"、"继续"、"下一个阶段"、"下一个" 或任何类似的话，** 按顺序运行下一个阶段。如果所有阶段都完成了，建议第一个迭代策略（gap）。如果刚刚完成了一个迭代，建议推荐周期中的下一个策略。

**如果用户说 "运行所有阶段"、"运行所有"、"运行完整管道"，** 按顺序在一个会话中运行所有阶段。这会使用更多的上下文，但有些用户更喜欢这样。

**如果用户问 "帮助"、"这是如何工作的"、"这是什么" 或任何类似的话，** 用以下解释回复（自然地调整措辞，不要逐字复制）：

> 质量 playbook 查找结构代码审查无法发现的错误——35% 的真实缺陷需要理解代码 *应该* 做什么。它按阶段工作：
>
> - **Phase 1 (探索)：** 理解代码库——架构、风险、失败模式、规范
> - **Phase 2 (生成)：** 生成质量工件——需求、测试、审查协议
> - **Phase 3 (代码审查)：** 三次审查，每个确认的缺陷都有回归测试
> - **Phase 4 (规范审计)：** 三个独立的 AI 审计员检查代码是否符合需求
> - **Phase 5 (协调)：** 闭环——每个缺陷的 TDD 红绿验证
> - **Phase 6 (验证)：** 自检基准验证所有生成的工件
>
> 数字阶段完成后，可以运行迭代策略（gap、unfiltered、parity、adversarial）以查找更多缺陷——迭代通常在基线基础上额外增加 40-60% 的确认缺陷。
>
> playbook 在您提供文档的情况下效果最好——规范、API 文档、设计文档、社区文档。当您分别运行每个阶段而不是一次性运行所有阶段时，它也会显著提高结果。
>
> 要开始，请说：**"在这个项目上运行质量 playbook。"**

**如果用户问 "发生了什么"、"有什么情况"、"我们在哪里"、"下一步该做什么"，** 读取 `quality/PROGRESS.md` 并给他们一个简洁的状态更新：完成的阶段、到目前为止发现的缺陷数量，以及下一步是什么。

### 文档警告

**在 Phase 1 开始时，在探索任何代码之前，检查文档。** 查找名为 `docs/`、`reference_docs/`、`doc/`、`documentation/` 或任何收集的文档文件所在的目录。还要检查用户是否在提示中提到文档。

**如果没有找到文档，立即打印此警告（在继续之前）：**

> **重要：未找到项目文档。** 质量 playbook 可以没有文档运行，但在您提供规范、API 文档、设计文档或社区文档时，它会发现更多缺陷——并且是更高置信度的缺陷。在受控实验中，提供文档的运行发现的缺陷不同且更好，优于纯代码基线。
>
> 如果您有文档可用，可以将它们添加到 `reference_docs/` 目录并重新运行 Phase 1。否则，我将进行纯代码分析。

然后继续 Phase 1——不要阻塞，只需确保用户看到警告。

### 运行特定阶段

用户可以请求任何单个阶段：

```
运行质量 playbook 阶段 1。
运行质量 playbook 阶段 3——代码审查。
运行阶段 5 协调。
```

在运行特定阶段时，检查其先决条件是否存在（例如，Phase 3 需要 Phase 2 工件）。如果先决条件缺失，告诉用户需要先运行哪些阶段。

### 迭代模式——在之前的运行上改进

在存在之前的 playbook 运行并希望找到更多缺陷时使用此模式。迭代模式用五种策略之一进行有针对性的探索，取代了 Phase 1 的从头开始探索，然后将结果与之前的运行合并，并重新运行 Phases 2–6 对合并后的结果。

**何时使用迭代模式：** 在完整的 playbook 运行之后，当您认为代码库比第一次运行发现的缺陷更多时。这对于大型代码库特别有效，其中单个运行只能覆盖 3–5 个子系统，以及对于库/框架代码库特别有效，不同的探索路径发现不同的缺陷类别。

**阅读 `references/iteration.md` 获取详细的策略说明。** 该文件包含每个策略的完整操作细节、共享规则、合并步骤和完成关卡。以下摘要描述了何时使用每个策略。

**TDD 适用于迭代运行。** 迭代运行中每个新确认的缺陷都必须经过完整的 TDD 红绿周期，并生成 `quality/results/BUG-NNN.red.log`（如果存在修复补丁，则生成 `.green.log`）。质量关卡强制执行此规则——缺失的日志会导致 FAIL。参见 `references/iteration.md` 中的共享规则 5 和 Phase 5 中的 TDD 日志关闭关卡。

**迭代策略。** 用户通过在提示中命名策略来选择策略。如果没有命名策略，默认为 `gap`。

```
运行质量 playbook 的下一次迭代。                          # 默认：gap 策略
运行使用 gap 策略的质量 playbook 的下一次迭代。
运行使用 unfiltered 策略的下一个迭代。
运行使用 parity 策略的下一个迭代。
运行使用 adversarial 策略的迭代。
```

**推荐周期：** gap → unfiltered → parity → adversarial。每个策略发现不同的缺陷类别：

- **`gap`** (默认) — 扫描之前的覆盖范围，探索未覆盖的子系统和薄弱部分。当第一次运行结构合理但仅覆盖了代码库的一部分时最佳。
- **`unfiltered`** — 纯领域驱动探索，没有结构约束。没有模式模板、没有适用性矩阵、没有部分格式要求。恢复结构探索抑制的缺陷。
- **`parity`** — 系统地枚举相同契约的并行实现（传输变体、回退链、设置与重置路径），并比较它们的不一致性。发现只有在跨路径比较中才会出现的缺陷。
- **`adversarial`** — 重新调查被拒绝/降级的分派结果，并挑战薄弱的 SATISFIED 判决。恢复保守分派中的 II 类错误。
- **`all`** — 运行器级别的便利性：按顺序执行 gap → unfiltered → parity → adversarial，每个作为单独的代理会话。如果某个策略发现零个新缺陷，则提前停止。

### 按阶段执行

每个阶段都在磁盘上生成文件，供下一个阶段读取。这是阶段之间上下文转移的方式——通过文件，而不是通过对话历史。关键的交接文件是：

- **`quality/EXPLORATION.md`** — Phase 1 写入此文件，Phase 2 读取它。包含 Phase 2 生成工件所需的所有内容，而无需重新探索代码库。
- **`quality/PROGRESS.md`** — 每个阶段更新后。累积 BUG 跟踪器确保没有遗漏的发现。
- **生成的工件** (REQUIREMENTS.md、CONTRACTS.md 等) — Phase 2 写入这些文件，Phases 3–5 读取它们以运行审查、审计和协调。

每个阶段边界的模式：完成当前阶段，将所有内容写入磁盘，然后打印结束阶段消息并停止。当用户开始下一个阶段时，在继续之前读取所需的文件。这个“写入然后读取”周期是阶段边界——它允许您在加载审查上下文之前从工作内存中删除探索上下文，例如。

在继续之前，将 Phase 1 探索结果写入 `quality/EXPLORATION.md`。此文件在所有模式下都是强制性的。使其详尽：领域识别、架构图、现有测试、规范摘要、质量风险、骨架/调度分析、派生需求（REQ-NNN）和派生用例（UC-NN）。Phase 2 生成工件所需的所有内容都必须在此文件中。

将探索结果写入磁盘的纪律是强制深入分析的原因。如果没有它，模型会在工作内存中保留模糊的印象，并生成宽泛的抽象需求，从而错过功能级缺陷。写入强制具体性：文件路径、行号、确切的函数名、具体的行为规则。这种具体性使需求精确到足以在代码审查期间捕获缺陷。

---

## 运行状态仪器（v1.5.6 — 随时写入事件）

`quality/` 中的两个文件跟踪此运行的状态，跨文件系统，以便运行在飞行中可观察、可恢复、可审计。在整个运行过程中维护这两个文件。

- **`quality/run_state.jsonl`** — 仅追加的机器可读事件日志。每行一个 JSON 对象。协调器和任何监控器读取此文件以确切地知道运行的位置。
- **`quality/PROGRESS.md`** — 人类可读的状态文件，每次事件原子重写。

**权威模式：** `references/run_state_schema.md`。在运行开始时读取一次；它定义了完整的事件分类法、必需字段、交叉验证规则和 PROGRESS.md 格式。

### 初始化（在包括 Phase 0 在内的任何阶段工作之前）

如果 `quality/run_state.jsonl` 不存在：
1. 如果 `quality/` 不存在，则创建 `quality/`。
2. 将 `_index` 事件追加到 `quality/run_state.jsonl`。必需字段：`event=_index`、`ts`（ISO 8601 UTC 带有 `Z`）、`schema_version="1.5.6"`、`event_types`（列出此运行将使用的所有事件类型的数组——至少包括 `_index`、`run_start`、`phase_start`、`pattern_walked`、`pass_started`、`pass_ended`、`finding_logged`、`artifact_written`、`gate_check`、`phase_end`、`error`、`run_end`）、`benchmark`（目标名称）、`lever_state`（例如，`"baseline"` 对于正常运行）、`started_at`。
3. 追加 `run_start` 事件。必需字段：`event=run_start`、`ts`、`runner`（`claude`/`codex`/`copilot`/`cursor` 之一）、`playbook_version`（从 SKILL.md 前面的 `version` 字段读取）、`target_path`。
4. 根据 `references/run_state_schema.md` 中的格式规范写入 `quality/PROGRESS.md`。包括标题（开始 / 基准 / 按钮状态 / 运行器 / playbook 版本），空的阶段清单（所有六个阶段）、空的最近事件 / 生成的工件部分。

如果 `quality/run_state.jsonl` 在运行开始时已存在：这是一个 **恢复运行**。见“恢复语义”下方。

### 每个阶段的事件

在每个阶段边界（1 到 6），写入事件：

- **阶段开始时：** 追加 `{"event":"phase_start","ts":"<now>","phase":N}` 到 `quality/run_state.jsonl`。更新 `quality/PROGRESS.md`：将阶段 N 标记为进行中，并记录当前时间戳。
- **阶段结束时：** *首先* 验证阶段的预期工件（下表）。如果验证失败，追加 `{"event":"error","ts":"<now>","phase":N,"message":"<缺失什么>","recoverable":true}` 并重新运行阶段。如果验证通过，追加 `{"event":"phase_end","ts":"<now>","phase":N,"key_counts":{...},"artifacts_produced":[...]}`。更新 PROGRESS.md：检查阶段 N 并总结统计数据。

**Phase 1 子事件（除 phase_start/phase_end 外）：**
- 在遍历每个七种探索模式后：追加 `{"event":"pattern_walked","ts":"<now>","phase":1,"pattern":N,"findings_count":K}`。每个模式一个事件，即使没有发现也是如此。
- 当 `quality/EXPLORATION.md` 被写入时：追加 `{"event":"artifact_written","ts":"<now>","relative_path":"quality/EXPLORATION.md","byte_size":<size>,"line_count":<lines>}`。

**Phase 4 子事件：**
- 在每个通过开始（A 到 D）：`{"event":"pass_started","ts":"<now>","phase":4,"pass":"A"}`。
- 在每个通过结束时：`{"event":"pass_ended","ts":"<now>","phase":4,"pass":"A","output_artifact":"<path>"}`。

**Phase 5 / Phase 6 子事件：**
- 在每个关卡检查完成时：`{"event":"gate_check","ts":"<now>","gate_name":"<name>","verdict":"pass|fail|warn|skip","reason":"<short>"}`。

**运行结束：**
- 在 Phase 6 `phase_end` 之后：追加 `{"event":"run_end","ts":"<now>","status":"success","total_findings":<N>,"final_verdict":"<gate verdict>"}`。状态为 `aborted` 对于 `recoverable:false` 失败，`failed` 对于不可恢复的运行时错误。

### phase_end 时的交叉验证规则

在写入每个 `phase_end` 事件之前，验证相应的工件：

| 阶段 | 必须满足 |
|---|---|
| 1 | `quality/EXPLORATION.md` 和 `quality/PROGRESS.md` 满足在 SKILL.md:1257-1273 文档中记录的 13 检查阶段 1 门禁（六个必需标题：`## 开放式探索发现`，`## 质量风险`，`## 模式适用性矩阵`，`## 模式深入分析 — *` ×3+，`## 阶段 2 候选错误`，`## 门禁自我检查`；PROGRESS 阶段 1 行标记 `[x]`；≥8 带文件：行引用的发现；≥3 多位置发现；3-4 FULL 模式矩阵行；≥2 多功能模式深入分析；候选错误源混合 ≥2 来自探索/风险 AND ≥1 来自模式深入分析）。`bin/run_state_lib.validate_phase_artifacts(quality_dir, phase=1)` 强制执行完整门禁。 |
| 2 | 所有九个 Generate-contract 艺术品在 `quality/` 下非空：`REQUIREMENTS.md`，`QUALITY.md`，`CONTRACTS.md`，`COVERAGE_MATRIX.md`，`COMPLETENESS_REPORT.md`，`RUN_CODE_REVIEW.md`，`RUN_INTEGRATION_TESTS.md`，`RUN_SPEC_AUDIT.md`，`RUN_TDD_TESTS.md`。此外，至少有一个非空的 `quality/test_functional.<ext>`（扩展名因语言而异）。 |
| 3 | `quality/RUN_CODE_REVIEW.md` 存在 |
| 4 | `quality/REQUIREMENTS.md` 非空 AND `quality/COVERAGE_MATRIX.md` 存在。如果运行了四通道技能派生管道（即 `quality/phase3/` 存在），那么 `quality/phase3/pass_a_drafts.jsonl`，`quality/phase3/pass_b_citations.jsonl`，`quality/phase3/pass_c_formal.jsonl` 和 `quality/phase3` 下面的 Pass D 收件箱必须都存在且非空。 |
| 5 | `quality/results/quality-gate.log` 存在，非空 |
| 6 | `quality/BUGS.md` 非空，带有 `^##\s+BUG-` 部分 AND `quality/INDEX.md` 更新，带有 `gate_verdict` 字段 |

如果一个检查失败，则追加 `error` 事件（recoverable=true）并重新运行阶段。**不要**对缺失的艺术品写入 `phase_end` — 这是 v1.5.6 捕获的失败模式。

`bin/run_state_lib.validate_phase_artifacts(quality_dir, phase)` 以编程方式执行这些检查 — 如果在 playbook 会话中可用，请从内部调用它。

### 恢复语义

如果 playbook 启动时 `quality/run_state.jsonl` 已经存在（之前的会话崩溃或中途暂停）：

1. 读取所有事件。使用 `bin/run_state_lib.last_in_progress_phase(events)` 找到最后一个未跟有匹配 `phase_end` 的 `phase_start` — 称为进行中的阶段。
2. 运行上述跨验证规则对该阶段。
   - **艺术品完整：** 前一个会话完成了工作但没有写入 `phase_end`。追加缺失的 `phase_end`（带当前 `ts`）并继续下一个阶段。
   - **艺术品不完整：** 从头重新运行该阶段。
3. 如果所有六个 `phase_end` 事件都存在但没有 `run_end`：追加 `run_end status=success` 并最终确定。
4. 如果不存在 `quality/run_state.jsonl`：全新运行。按照上述部分初始化。

政策：**信任艺术品多于事件。** 如果事件声称阶段 4 完成，但 `REQUIREMENTS.md` 不存在，重新运行阶段 4。如果事件中途停止但艺术品完整，赶上事件。

### PROGRESS.md 原子重写

PROGRESS.md 在每个事件上都会被重写（而不是追加）。内容反映当前的 run-state.jsonl：标题（运行元数据），阶段清单（每个已完成阶段的摘要统计，当前阶段的进行中标记），最近的事件（JSONL 日志中最后 10 个事件，以人类可读形式），生成艺术品（本次运行写入的文件及其字节大小）。有关确切格式模板，请参阅 `references/run_state_schema.md`。

`bin/run_state_lib.write_progress_md(quality_dir, events, current_phase)` 从事件列表生成正确格式的 PROGRESS.md — 在每个事件后调用它以保持文件同步。

---

## 阶段 0：先前运行分析（自动）

**此阶段仅在 `quality/previous_runs/` 存在并包含先前质量艺术品时运行。** 如果没有先前运行，则跳转到阶段 1。如果 `quality/previous_runs/` 存在但为空或其中不包含符合质量标准的艺术品（即下级目录中没有 `quality/BUGS.md`），则跳过阶段 0a 并转到阶段 0b。 （来自 v1.5.4 之前的遗留存档在 `quality/runs/` 下仍然可读以向后兼容 — 见 SKILL.md:149 — 但规范存档根是 `quality/previous_runs/`。）

当先前运行存在时，playbook 进入 **延续模式**。这启用了迭代错误发现：每次运行都会继承先前运行中确认的发现，机械验证它们，并探索新的错误。迭代在运行发现零净新错误时收敛。

**步骤 0a：构建种子列表。** 从所有先前运行中读取 `quality/previous_runs/*/quality/BUGS.md`。对于每个确认的错误，提取：错误 ID，文件：行，摘要，以及回归测试断言。按文件：行去重（在多个运行中发现的相同错误只计一次）。将合并的种子列表写入 `quality/SEED_CHECKS.md`，格式如下：

```markdown
## 种子检查（来自 N 个先前运行）

| 种子 | 来源运行 | 文件：行 | 摘要 | 断言 |
|------|-----------|-----------|---------|-----------|
| SEED-001 | run-1 | virtio_ring.c:3509-3529 | RING_RESET 被丢弃 | `"case VIRTIO_F_RING_RESET:" in func` |
```

**步骤 0b：机械执行种子检查。** 对于每个种子，在当前源树中运行断言。记录 PASS（错误自上次运行以来已修复）或 FAIL（错误仍然存在）。失败的种子是确认的传递错误 — 无论审计员是否独立发现，都必须出现在本次运行的 BUGS.md 中。通过意味着错误已修复 — 在 PROGRESS.md 中记为 "SEED-NNN: 自先前运行以来已解决。"

**步骤 0c：识别先前运行范围。** 读取 `quality/previous_runs/*/quality/PROGRESS.md` 以获取范围声明。注意先前运行中覆盖了哪些子系统。在阶段 1 探索期间，优先考虑先前运行未覆盖的区域以最大化发现新错误的机会。如果所有子系统在先前运行中都已覆盖，则探索相同的范围，但使用不同的重点（例如，不同的审查区域，不同的入口点）。

**步骤 0d：将种子注入下游阶段。** 种子列表成为以下输入：
- **阶段 3（代码审查）：** 将其添加到代码审查提示："先前运行确认了这些错误 — 验证它们是否仍然存在并在相同的子系统中查找附加发现。"
- **阶段 4（规范审计）：** 将其添加到 `RUN_SPEC_AUDIT.md`："先前运行中已知的开放问题：[种子列表]。预期审计员会发现这些。如果审计员未标记已知种子错误，则表明其审查存在覆盖差距，而不是错误已修复。"

**存在的原因：** 非确定性范围探索意味着不同的运行会发现不同的错误。在跨版本测试中，4/8 存储库在某些版本中发现错误而在其他版本中未发现 — 不是因为错误被修复，而是因为模型探索了代码库的不同部分。通过种子注入迭代解决了这个问题：确认的错误机械传递（无需重新发现），并且每次新运行都可以专注于探索未覆盖的区域。

### 阶段 0b：同级运行种子发现（自动）

**此步骤仅在 `quality/previous_runs/` 不存在或 `quality/previous_runs/` 存在但其中不包含符合质量标准的艺术品**（即阶段 0a 没有可用的内容）**并且**项目目录已版本化（例如，`httpx-1.3.23/` 与 `httpx-1.3.21/` 并存）。如果 `quality/previous_runs/` 存在且包含符合标准的艺术品，阶段 0a 已经处理了种子注入 — 跳过此步骤。

**如果 `quality/previous_runs/` 存在但为空或仅包含非符合标准的子目录**，发出警告："阶段 0b：`quality/previous_runs/` 存在但其中不包含符合标准的艺术品 — 咨询同级版本化目录以获取种子。" 然后继续下面的同级发现。

当不存在 `quality/previous_runs/` 目录但同级版本化目录存在时，查找这些同级中的先前质量艺术品：

1. **发现同级。** 列出与父目录中 `<project-name>-<version>/quality/BUGS.md` 模式匹配的目录。排除当前目录。按版本降序排序（最新优先）。
2. **导入确认的错误作为种子。** 对于每个具有 `quality/BUGS.md` 的同级，使用与步骤 0a 相同的格式提取确认的错误。将它们写入 `quality/SEED_CHECKS.md` 并注明来源为同级目录名称。
3. **机械执行种子检查**（与阶段 0a 中的步骤 0b 相同）。对于每个导入的种子，在当前源树中运行断言并记录 PASS/FAIL。
4. **注入到下游阶段**（与阶段 0a 中的步骤 0d 相同）。

**存在的原因：** 在 v1.3.23 基准测试中，httpx 产生零错误结果，尽管 httpx-1.3.21 发现了 `Headers.__setitem__` 非ASCII编码错误。模型只是探索了不同的代码路径，从未检查过 Headers 区域。同级运行种子确保先前版本化运行中确认的错误即使没有显式的 `quality/previous_runs/` 存档也会传递。这是一个不同的失败类别，它解决的是**探索非确定性**，而不是证据篡改。

---

## 阶段 1：探索代码库（边写边进行）

**v1.5.6 仪器：** 现在将 `phase_start phase=1` 追加到 `quality/run_state.jsonl`。在遍历每个探索模式后，追加 `pattern_walked phase=1 pattern=N findings_count=K`。在阶段结束时，交叉验证（`quality/EXPLORATION.md` ≥ 200 字节且包含发现部分）然后追加 `phase_end phase=1`。见上面的“运行状态仪器”。

> **此阶段所需的参考** — 在继续之前阅读这些：
> - `references/exploration_patterns.md` — 应用开放式探索后应用的七个错误发现模式

**第一个操作：创建运行元数据。** 在任何探索之前，创建运行元数据文件：

```bash
mkdir -p quality/results
cat > "quality/results/run-$(date -u +%Y-%m-%dT%H-%M-%S).json" <<'METADATA'
{
  "schema_version": "1.0",
  "skill_version": "1.5.6",
  "project": "<repo-name>",
  "model": "<model-string>",
  "model_provider": "<provider>",
  "runner": "<tool>",
  "start_time": "<ISO-8601-UTC>",
  "end_time": null,
  "duration_minutes": null,
  "phases_completed": [],
  "iterations_completed": [],
  "bug_count": 0,
  "bug_severity": { "HIGH": 0, "MEDIUM": 0, "LOW": 0 },
  "gate_result": null,
  "gate_fail_count": null,
  "gate_warn_count": null,
  "notes": ""
}
METADATA
```

填写 `project`，`model`（确切的模型字符串，例如 `"claude-sonnet-4-6"`），`model_provider`（例如 `"anthropic"`，`"openai"`，`"cursor"`），`runner`（例如 `"claude-code"`，`"copilot-cli"`，`"cursor"`），和 `start_time`（UTC ISO 8601）。在每次阶段结束时更新此文件 — 追加完成的阶段到 `phases_completed` 并更新 `bug_count`/`bug_severity` 作为错误被确认。在最终更新后，填充 `end_time`，`duration_minutes` 和 `gate_result`。

**第二个操作：运行 v1.5.3 文档摄取（在探索任何代码之前）。** `bin/` 中的一个单 stdlib 模块生成权威文档记录，阶段 1 要求派生依赖于它：

1. **`python -m bin.reference_docs_ingest <target>`** — 一次遍历目标存储库中的 `reference_docs/`。`reference_docs/cite/` 下的文件被哈希并按 `schemas.md` §4 和 §1.6 声明包装器写入 `quality/formal_docs_manifest.json`。`reference_docs/` 顶层的文件不会被写入清单，但可通过 `bin.reference_docs_ingest.load_tier4_context(<target>)` 可用为 Tier 4 上下文，它返回一个排序的 `(path, text)` 元组列表。如果摄取命令失败（不支持的扩展名，非 UTF-8 字节），停止运行并将 stderr 输出原样显示给用户 — 摄取错误是可操作的，必须在探索继续之前修复。

**不需要边车。** 文件放置是标志：顶层 `reference_docs/<name>.<ext>` 文件是 Tier 4 上下文；`reference_docs/cite/<name>.<ext>` 下的文件是可引用的来源。Tier 1 是 `cite/` 内容的默认值；文件可以使用可选的文件内标记在第一行覆盖为 Tier 2：`<!-- qpb-tier: 2 -->`（Markdown）或 `# qpb-tier: 2`（纯文本）。任何文件夹下的 `README.md` 都会被跳过。

**当 `reference_docs/` 缺失或为空时**，阶段 1 必须打印此可操作消息并继续：

> 阶段 1 在 reference_docs/ 中找不到文档。playbook 将使用仅 Tier 3 证据（源树本身）继续。为获得更好的结果，请将纯文本文档放入：
>   reference_docs/            ← AI 聊天，设计笔记，回顾（Tier 4 上下文）
>   reference_docs/cite/       ← 项目规范，RFC，API 合同（可引用，字节验证）
> 有关详细信息，请参阅 README.md "步骤 1：提供文档"。

**纯文本仅 — 转换在 playbook 外部发生。** 参考文档是 `.txt` 或 `.md` 仅（schemas.md §2）。PDF，DOCX，HTML 等。被拒绝，并附带可操作的转换提示（`pdftotext`，`pandoc -t plain`，`lynx -dump`）。**不要**尝试在技能内部解析二进制或格式化文档 — 在外部运行转换并提交纯文本。

在第一阶段了解项目。质量 playbook 必须基于此特定代码库 — 而不是通用建议。

**为什么先探索？** AI 生成的质量 playbook 最常见的失败是生成通用内容 — 覆盖目标适用于任何项目，场景描述理论上的失败，测试执行语言内置功能而不是项目代码。探索通过强制每个输出引用某个真实的东西来防止这种情况：特定的函数，特定的模式，特定的防御代码模式。如果你不能指出某个东西在代码中的位置，你就是在猜测 — 猜测会产生没人信任的质量 playbook。

**为大型代码库扩展：** 对于具有超过 ~50 个源文件的项目，不要尝试读取所有内容。专注于探索 3-5 个核心模块（处理主要数据流，最复杂的逻辑，和最易出错的操作的那些）。从每个子系统中读取代表性测试，而不是每个测试文件。目标是深度了解重要内容，而不是跨所有内容进行广度了解。

**深度优于广度（关键）。** 窄范围与函数级详细发现比宽范围与子系统级摘要发现更多错误。对于每个你探索的核心模块，识别实现关键行为的特定函数，并按名称、文件路径和行号记录它们。从“重置子系统应处理错误”派生的要求不会捕获错误。从 "`vm_reset()` at `virtio_mmio.c:256` 必须在写入零后轮询状态寄存器”派生的要求会。有用探索与无用探索之间的区别在于具体性 — 文件路径，函数名称，行号，精确的行为规则。

**三阶段探索：先开放式，然后领域风险，然后选择模式。** 探索有三个阶段，顺序很重要：

1. **开放式探索（领域驱动）。** 在应用任何结构化模式之前，像有经验的开发者一样探索代码库：阅读代码，理解架构，基于你对这类系统可能出错的领域知识来识别风险。问自己：“[此领域的]专家首先会检查什么？” 对于 HTTP 库，这意味着重定向处理，标题编码，连接生命周期。对于 CLI 框架，这意味着标志解析，帮助生成，完成/验证一致性。对于序列化库，这意味着类型覆盖，往返保真度，边缘情况处理。写具体的发现，带文件路径和行号。此阶段必须产生至少 8 个具体的错误假设或可疑发现 — 不是架构观察，而是具体的“此代码在文件：行可能错误，因为[原因]”发现。至少 4 个必须引用不同的模块或子系统。

2. **领域知识风险分析。** 在开放式探索之后，暂时跳脱出代码本身，基于你在训练中学到的关于此类系统的知识进行推理。对于库和框架代码库而言，这是主要的缺陷排查环节。使用两个来源——你刚刚探索过的代码以及你对类似系统的领域知识——来完成下方第 6 步的问题。至少生成 5 个按优先级排序的故障场景，每个场景需指明具体的函数、文件和行号，并解释为何某个领域特定的边界条件会导致错误行为。你不需要实际观察到过这些故障——你从训练数据中已经知道这类系统中确实会发生它们。在继续进入模式分析之前，将结果写入 EXPLORATION.md 的 `## Quality Risks` 部分。

   **本阶段不允许出现的内容：** 列出代码已有的防御性模式（即代码做对了的事情）的章节不是风险分析。列出存在风险的模块但没有具体故障场景的章节不是风险分析。得出"这是一个成熟的、经过充分测试的库，所以基础 bug 不太可能出现"这一结论是有害的——成熟的库恰恰拥有最隐蔽的 bug，正是因为显而易见的 bug 早在多年前就被发现了。检验标准：代码审查人员能否读完每个场景后立即知道该检查什么？如果不能，说明该场景过于抽象。

3. **模式驱动的探索（精选而非穷举）。** 在开放式探索和领域风险分析写入磁盘之后，使用模式适用性矩阵评估 `exploration_patterns.md` 中的全部七种分析模式。对每种模式，判断它是否适用于当前代码库，以及它将针对什么内容。然后选择 3 到 4 种模式进行深度剖析——即对当前代码库收益最高的模式。其余模式用简短的"不适用"或"暂缓"备注并附代码库特定的理由。不要对全部七种模式都产出深度章节——对 3 到 4 种模式做深入分析，远胜于对 7 种模式做浅层覆盖。当第四种模式有明确适用性且能覆盖其他三种未触及的代码区域时，选择 4 种；拿不准时默认选 3 种。

   对每个选定的模式进行深度剖析时，使用参考文件中的输出格式，并跨 2 个及以上函数追踪代码路径。深度剖析应当对开放式探索和风险分析的发现进行压力测试、细化或扩展——而不是重复它们。

第一阶段完成关卡检查全部三个阶段。开放式探索部分、质量风险部分、模式适用性矩阵以及模式深度剖析部分都必须存在。

**增量写入——不要在内存中保留发现。** 这是第一阶段最重要的执行规则。每探索完一个子系统或应用完一个模式后，**立即将发现追加写入磁盘上的 `quality/EXPLORATION.md`，然后再进入下一个子系统或模式。** 不要试图在工作记忆中跨多个子系统保留发现。增量写入的纪律有两个目的：

1. **深度恢复。** 如果你探索了 PCI 中断路由子系统，并在 `vp_find_vqs_intx()` 中发现了可疑代码，立即将该发现写入 EXPLORATION.md。然后当你转向管理队列子系统时，你的工作记忆就能专注于深入分析该子系统。如果不做增量写入，第一个子系统的发现会与第二个子系统的发现争夺注意力，结果两边都变得浅尝辄止。

2. **不丢失任何内容。** 在 v1.3.41 基准测试中，模型探索了 8 个模式章节但每章只写了 5–7 行——完美均匀，完美浅薄。每个章节都通过了关卡检查，但没有一个深入 enough 到足以发现需要跨多个函数追踪代码路径才能定位的 bug。模型试图在读取所有内容之后一次性编写完整的 EXPLORATION.md，结果只能回忆起表面层面的发现。增量写入可以防止这种情况。

**节奏是：读一个子系统 → 将发现写入磁盘 → 读下一个子系统 → 追加发现 → 循环往复。** 每次追加应包含具体的函数名、文件路径、行号和具体的 bug 假设。一个 5 行的章节写着"检查了跨实现一致性，发现一个缺口"只是通过关卡检查的占位符，不是探索发现。有用的章节会追踪代码路径："函数 A 在 file:line 调用函数 B（file:line），B 执行了 X 但没有执行 Y；对比函数 C（file:line）同时执行了 X 和 Y。"

**强制整合步骤。** 在全部三个阶段（开放式探索、质量风险、选定的模式深度剖析）都已完成并写入 EXPLORATION.md 之后，添加最后一个部分：`## Candidate Bugs for Phase 2`。该部分将所有先前章节中最强的 bug 假设整合为一份按优先级排序的交接清单。对每个候选 bug，包含：假设内容、具体的 file:line 引用、它在哪个阶段被发现的（开放式探索、质量风险或模式），以及代码审查应关注什么。该部分是探索与产物生成之间的桥梁——它告诉第三阶段（Phase 3）应该精确聚焦在哪里。最低要求：4 个候选 bug 附带 file:line 引用——至少 2 个来自开放式探索或质量风险，至少 1 个来自模式深度剖析。没有上限。

**预检：大型代码库的范围声明**

在探索任何源代码之前，估算规模：大致源文件数量（不含测试、文档和生成的文件）、主要子系统数量和文档量。将数量记录在 PROGRESS.md 中。

- **少于 200 个源文件：** 进行完整探索。上述深度与广度的指导原则仍然适用。
- **200–500 个源文件：** 在探索之前声明你的预期范围。在 PROGRESS.md 中写入 `## Scope declaration` 部分，列出你将覆盖的 3–5 个子系统、每个子系统的预期文件数量，以及你暂缓哪些子系统及其理由。然后仅对声明范围内的内容进行探索。
- **超过 500 个源文件：** 停止，在阅读任何源文件之前，先在 PROGRESS.md 中写入强制性的范围声明。范围声明必须包含：(a) 本次运行覆盖的子系统，(b) 明确暂缓的子系统，(c) 每个暂缓子系统的排除理由，(d) 后续运行建议覆盖的子系统范围。在写入范围声明之前不要开始探索。对于超过此阈值的代码库，"覆盖一切"的范围声明是无效的。

**恢复之前的会话：** 如果 PROGRESS.md 已存在且显示某些阶段已标记为完成，先阅读它。不要重做已标记为完成的阶段——从第一个标记为未完成的阶段恢复。如果范围声明已经写好，严格按照它执行。如果之前会话的范围声明暂缓了某些子系统，除非本次运行明确是针对暂缓区域的后续跟进，否则不要扩展范围去覆盖它们。

**规范优先型代码库：** 某些代码库将规范、配置或协议文档作为其主要产品，可执行代码只是辅助基础设施。例如：带有基准测试工具的技能定义、带有验证脚本的 schema 注册表、带有编排辅助工具的流程配置。当主要产品是规范而非可执行代码时，应从规范本身的内部一致性、完整性和正确性中推导需求——而不仅仅从可执行的代码路径中推导。规范才是用户所依赖的核心；工具是次要的。如果你发现自己在辅助脚本上写了 80% 以上的需求，而在主规范上只写了不到 20%，那么你的重点就反了。

### 第 0 步：询问开发历史

在探索代码之前，向用户提出一个问题：

> "你是否有关于开发此项目的 AI 聊天记录导出——Claude 导出、Gemini 数据导出、ChatGPT 导出、Claude Code 转录，或类似内容？如果有，请告诉我文件夹位置。其中关于设计讨论、事故报告和质量决策的内容将显著提升生成的质量手册的质量。"

如果用户提供了聊天记录文件夹：

1. **先扫描索引文件。** 查找名为 `INDEX*`、`CONTEXT.md`、`README.md` 或类似导航辅助的文件。如果存在，阅读它——它会告诉你里面有什么以及如何找到相关内容。
2. **搜索质量相关的对话。** 查找提及以下关键词的消息：质量（quality）、测试（testing）、覆盖率（coverage）、bug、故障（failures）、事故（incidents）、崩溃（crashes）、验证（validation）、重试（retry）、恢复（recovery）、规范（spec）、适配度（fitness）、审计（audit）、审查（review）。同时搜索项目名称。
3. **提取设计决策和事故历史。** 最有价值的内容包括：(a) 事故报告——出了什么问题、影响了多少条记录、如何发现的，(b) 设计讨论——为什么选择了某种方案、哪些替代方案被否决，(c) 质量框架讨论——覆盖率目标、测试哲学、模型审查经验，(d) 跨模型反馈——不同 AI 模型对代码产生分歧的地方。
4. **不要试图阅读所有内容。** 聊天记录可能非常庞大。使用索引找到最相关的对话，然后在其中搜索质量相关内容。10 分钟有目标的搜索胜过 2 小时的穷尽阅读。

这些上下文是金矿。一段开发者讨论了"为什么我们选择了这个并发模型"或"我们在生产环境中曾丢失 1,693 条记录"的聊天记录，可以将泛泛的场景转化为有权威性的场景。

如果用户没有聊天记录，正常继续——该技能在没有聊天记录的情况下也能工作，只是上下文较少。

**自主回退：** 在基准测试模式下运行时、通过 `bin/run_playbook.py`（基准测试运行器，不随技能发布）运行、或无用户交互时（例如 `--single-pass`），跳过第 0 步的问题，直接继续到第 1 步。如果项目目录中可见聊天记录文件夹（例如 `AI Chat History/`、`.chat_exports/`），直接扫描而无需询问。如果未找到聊天记录，继续执行——不要阻塞等待一个不会到来的回复。

### 第 1 步：识别领域、技术栈和规范

阅读 README、现有文档和构建配置（`pyproject.toml` / `package.json` / `Cargo.toml`）。回答以下问题：

- 这个项目做什么？（一句话。）
- 使用什么语言和关键依赖？
- 它与哪些外部系统通信？
- 主要输出是什么？

**找到规范文档。** 规范是功能测试的真相来源。按以下顺序搜索：根目录的 `AGENTS.md`/`CLAUDE.md`、`specs/`、`docs/`、`spec/`、`design/`、`architecture/`、`adr/`，然后是根目录下的 `.md` 文件。记录文件路径。

**如果不存在正式的规范文档**，该技能仍然可以工作——但你需要从其他来源汇编需求。按优先级排序：

1. **询问用户** —— 他们通常知道需求，即使没有写下来。
2. **README 和内联文档** —— 许多项目将需求嵌入在 README、API 文档或代码注释中。
3. **现有测试套件** —— 测试是隐式规范。如果一个测试断言 `process(x) == y`，那就是一个需求。
4. **类型签名和验证规则** —— schema、类型注解和验证器定义了系统接受和拒绝什么。
5. **从代码行为推断** —— 作为最后手段，阅读代码并推断它应该做什么。在 QUALITY.md 中将此类标记为*推断需求*，并标记需用户确认。

在使用非正式需求时，为每个场景和测试标注一个**需求标签**，包含置信度层级和来源：

- `[Req: formal — README §3]` —— 由人类在规范文档中撰写。具有权威性。
- `[Req: user-confirmed — "must handle empty input"]` —— 由用户陈述但未在正式文档中记录。视为具有权威性。
- `[Req: inferred — from validate_input() behavior]` —— 从代码中推断得出。标记需用户审查。

在 QUALITY.md 场景、功能测试文档和规范审计发现中使用此确切标签格式。它使哪些需求具有权威性、哪些需要验证一目了然。

### 第 1b 步：评估文档深度

如果 `reference_docs/` 存在，在决定关注哪些子系统之前阅读其中每个文件。对每个文档，分类其深度：

- **深入** —— 包含内部契约、安全不变量、并发模型、防御性模式、错误处理细节或行号级别的源码引用。适合用于推导需求。
- **中等** —— 涵盖架构和 API 表面，带有部分实现细节。有助于定向但不足以单独推导需求。
- **浅层** —— API 目录、功能概览或营销级别的摘要。列出了什么存在，但没有说明它如何工作、如何失败或强制什么契约。**不足以支撑范围决策。**

**范围规则：** 不要将审计范围缩小到仅包含有深入文档的子系统。如果最复杂或最容易出错的模块只有浅层文档，那是一个**需要在 PROGRESS.md 中标记的文档缺口**，而不是跳过该模块的理由。风险最高的代码加上最薄弱的文档正是 bug 藏身之处——只审计文档完善的部分只会产出一份看起来安全但遗漏真实缺陷的报告。

当高风险区域的文档较浅时：

1. 在 PROGRESS.md 的 `## Documentation depth assessment` 部分下明确记录该缺口。
2. 直接从源代码推导需求（文档注释、安全注解、防御性模式、现有测试），并标记为 `[Req: inferred — from source]`。
3. 在完整性报告中标记该区域需要补充更深入的文档。

在 PROGRESS.md 中记录每个 `reference_docs/` 文件的深度分类，以便审查人员评估文档是否适当地影响了范围。

**覆盖承诺表：** 在完成所有 `reference_docs/` 文档的分类后，在 PROGRESS.md 的 `## Documentation depth assessment` 部分下生成此表格：

| 文档 | 深度 | 子系统 | 需求承诺 | 如排除：理由 |
|----------|-------|-----------|------------------------|---------------------------|

对于每一份**深入**文档，将其映射到它所覆盖的子系统，然后要么承诺从中推导需求（"将在第 2 阶段覆盖"），要么提供指明取舍的具体理由。"不在本次运行范围内"这样一句话是不够的——理由必须说明*为什么*，例如"解释器 JIT 被排除，因为本次运行聚焦于解析器/编译器/垃圾回收流水线；建议单独安排一次运行。"

**关卡：** 在 `reference_docs/` 中有深入文档的高风险子系统不得从需求集中静默消失。如果一份深入文档有"将覆盖"的承诺，但到第 7 步结束时未产生任何需求，则需求流水线不完整——必须返回补齐该缺口的需求推导，然后再进入第 2 阶段产物生成。

### 第 2 步：映射架构

列出源目录及其用途。阅读主入口点，追踪执行流程。识别：

- 3–5 个主要子系统
- 数据流（输入 → 处理 → 输出）
- 最复杂的模块
- 最脆弱的模块

### 第 3 步：阅读现有测试

阅读现有的测试文件——对于小型/中型项目阅读全部，对于大型项目从每个子系统中取代表性样本。识别：测试数量、覆盖模式、缺口，以及任何覆盖率表演（看起来不错但抓不到真实 bug 的测试）。

**关键：记录导入模式。** 现有测试如何导入项目模块？每种语言都有自己的约定（Python 的 `sys.path` 操作、Java/Scala 包导入、TypeScript 相对路径或别名、Go 包/模块路径、Rust 的 `use crate::` 或 `use myproject::`）。你必须在功能测试中使用完全相同的导入模式——搞错这一点会导致每个测试都因导入/解析错误而失败。参见 `references/functional_tests.md` 中"Import Pattern"部分了解完整的六种语言矩阵。

**识别集成测试运行器。** 寻找执行端到端系统测试的脚本或测试文件，这些测试针对真实的外部服务（API、数据库等）。注意它们的模式——你将在 `RUN_INTEGRATION_TESTS.md` 中需要它们。

### 第 4 步：阅读规范

逐个按节阅读每个规范文档。对于每个节，问：“这个节说明了什么可测试的需求？” 记录没有相应测试的规范需求——这些是功能测试需要弥补的差距。

如果使用推断需求（来自测试、类型或代码行为），使用在第 1 步中定义的 `[Req: 等级 — 来源]` 格式标记每个需求。推断需求将输入到 `QUALITY.md` 场景中，并在第 7 阶段需要用户审核。

### 第 4b 步：阅读函数签名和真实数据

在编写任何测试之前，你必须确切地知道每个函数是如何被调用的。对于在第 2 步中识别的每个模块：

1. **阅读实际的函数签名**——参数名、类型、默认值。不要从使用上下文中猜测——阅读函数定义和任何文档（Python docstrings、Java/Scala Javadoc/ScalaDoc、TypeScript 类型注解、Go godoc 注释、Rust doc 注释和类型签名）。
2. **阅读真实数据文件**——如果项目有项目文件、固定文件、配置文件或示例数据（在 `pipelines/`、`fixtures/`、`test_data/`、`examples/` 中），阅读它们。你的测试固定文件必须与真实数据的形状完全匹配。
3. **阅读现有的测试固定文件**——现有测试是如何创建测试数据的？复制它们的模式。如果它们使用特定键构建配置字典，请使用这些确切的键。
4. **检查库版本**——检查项目的依赖项清单（`requirements.txt`、`build.sbt`、`package.json`、`pom.xml`/`build.gradle`、`go.mod`、`Cargo.toml`）以查看实际可用的内容。不要编写依赖于未安装的库功能的测试。如果一个依赖项可能缺失，请使用测试框架的跳过机制——参见 `references/functional_tests.md` § "库版本感知" 以获取特定于框架的示例。

记录一个**函数调用映射**：对于你计划测试的每个函数，写下它的名称、模块、参数和它返回的内容。这个映射可以防止最常见的测试失败：使用错误的参数调用函数。

### 第 5 步：找到骨架

这是最重要的步骤。搜索防御性代码模式——每个模式都是过去失败或已知风险的证据。

**为什么这很重要**：开发者不会为了好玩而编写 `try/except` 块、空值检查或重试逻辑。每一块防御性代码的存在都是因为有人受过伤害。围绕 JSON 解析的 `try/except` 块意味着在生产中发生了格式不正确的 JSON。字段上的空值检查意味着该字段在不应缺失时缺失了。这些模式是代码库低语其失败历史的代码。每个模式都成为一个适用性场景和边界测试。

**阅读 `references/defensive_patterns.md`** 以了解系统的搜索方法、grep 模式以及如何将发现转换为适用性场景和边界测试。

最低标准：每个核心源文件至少有 2-3 个防御性模式。如果你找到的数量更少，你只是在浏览——阅读函数体，而不仅仅是签名。

### 第 5a 步：跟踪状态机

如果项目有任何种类的状态管理——状态字段、生命周期阶段、工作流阶段、模式标志——完全跟踪状态机。这会捕获防御性模式分析单独遗漏的一类错误：存在但未被处理的错误状态。

**如何找到状态机**：搜索模型、枚举或常量中的状态/状态字段（例如，`status`、`state`、`phase`、`mode`）。搜索在允许操作之前检查状态的保护措施（例如，`if status == "running"`、`match self.state`）。搜索状态转换（分配给状态字段）。

**对于每个找到的状态机**：

1. **枚举所有可能的状态。** 阅读枚举、常量或使用 grep 搜索字段被分配的每个值。列出所有内容。
2. **对于每个状态消费者**（UI 处理程序、API 端点、控制流保护措施），检查：它是否处理了所有可能的状态？没有有意义的默认值的 `switch`/`match`，或者不覆盖所有状态的 `if/elif` 链是一个差距。
3. **对于每个状态转换**，检查：你能到达每个状态吗？有没有你能进入但永远无法离开的状态？有没有状态会阻止应该可用的操作？
4. **记录差距作为发现。** 一个允许在“运行中”执行操作 X 但不允许在“卡住”时执行操作 X 的状态保护措施是一个真正的错误，如果用户需要在卡住的过程中执行操作 X。一个进入终端状态但从未触发清理的进程是一个真正的错误。

**为什么这很重要**：状态机差距会产生在正常操作期间不可见但在压力或边缘条件下出现的错误——正是在你需要系统正常工作的时候。一个在“卡住”状态下无法被终止的批处理处理器，或者一个在所有工作完成后永不自我终止的监视器，或者一个拒绝恢复“挂起”运行的 UI，都是不完整状态处理的症状。这些错误不会在防御性模式分析中显示，因为代码没有针对它们进行防御——它根本就没有处理它们。

### 第 5b 步：映射模式类型

如果项目有一个验证层（Python 中的 Pydantic 模型、JSON 模式、TypeScript 接口/Zod 模式、Java Bean 验证注解、Scala 案例类编解码器），现在阅读模式定义。对于每个你为防御性模式找到的字段，记录模式接受的内容与拒绝的内容。

**阅读 `references/schema_mapping.md`** 以了解映射格式以及为什么这对于编写有效的边界测试很重要。

### 第 6 步：领域知识风险分析（代码 + 领域知识）

**这是库和框架代码库的主要错误查找过程。** 在选择任何结构化模式之前完成它。立即将结果写入 EXPLORATION.md 的 `## 质量风险` 部分——不要将其保存在内存中。

每个项目都有不同的失败模式。这一步使用**两个来源**——不仅仅是代码探索，还包括你对类似系统可能出错的知识。

**从代码探索中**，问：
- 这个项目的“无声错误”是什么样的？
- 哪些外部依赖项可以在没有警告的情况下更改？
- 哪些看起来简单但实际上很复杂？
- 跨领域问题隐藏在哪里？

**从领域知识中**，问：
- “类似系统会发生什么错误？”——如果它是 HTTP 路由器，请考虑标头解析边缘情况（质量值、令牌列表、大小写敏感性）、中间件排序依赖关系和路径规范化。如果是 HTTP 客户端，请考虑重定向凭证剥离、编码检测和连接状态泄漏。如果是序列化库，请考虑空值处理不对称性、直接方法和视图包装器之间的 API 表面一致性、惰性评估缓存错误和往返保真度。如果是 Web 框架，请考虑响应辅助边缘情况、配置编译链和中间件状态隔离。如果是批处理处理器，请考虑崩溃恢复、幂等性、无声数据丢失、状态损坏。如果它处理随机性或统计数据，请考虑种子、相关性、分布偏差。
- “什么会产生看起来正确的输出但实际上是错误的？”——这是最危险的错误类别：通过所有检查但微妙损坏的输出。一个返回 `200 OK` 但 `Content-Type` 错误的响应。一个成功重定向但泄漏凭证的重定向。一个反序列化对象在无声中截断值。
- “在 10 倍规模下会发生什么而在 1 倍规模下不会发生？”——块边界、速率限制、超时级联、内存压力。
- “当这个进程在最糟糕的时刻被终止时会发生什么？”——中途写入、中途事务、中途批处理提交。
- “当两个应该表现相同的表面在边缘输入时会发生什么漂移？”——重载、别名、同步/异步 API、构建器与直接 API、直接修改器与实时视图/包装器、与标准库兼容的包装器与框架原生表面。对于 Java/Kotlin：`add(null)` vs `asList().add(null)`，`put(key,null)` vs `asMap().put(key,null)`。对于 Python：构造器编码与修改器编码、同步与异步客户端行为。
- “什么会发出看似合理的输出但元数据微妙错误？”——内容类型、字符集、路由模式、ETag 强度、字节数、认证/标头/cookie 传播、状态代码、缓存验证器。
- “什么标准语法或列表语法正在使用临时字符串逻辑进行解析？”——质量值 (`q=0`)、逗号分隔的标头、摘要挑战、带参数的 MIME 类型、查询字符串、枚举/关键字集、cookie 合并。
- “领域专家会使用什么边缘输入？”——对于 HTTP 代码：`Accept-Encoding: gzip;q=0`，`Connection: keep-alive, Upgrade`，`Content-Type: application/problem+json`。对于序列化代码：通过不同的 API 表面传递 `null`、`Integer.MAX_VALUE + 1` 处的值、通过编码然后解码进行往返。对于路由代码：重叠模式、挂载前缀传播、不同方法的路由。
- “用户在提交不可逆或昂贵的操作之前需要什么信息？”——预运行成本估计、确认范围（尤其是在将扇出或扩展将倍增工作的情况下），资源警告。如果系统可以在无声中让用户承诺数小时的处理或重大成本而不显示他们即将做什么，那就是缺少保护措施。搜索启动长时间运行进程的操作、提交批处理作业或触发扩展/扇出——并检查用户在无法撤销的点上是否看到预览、估计或确认，带有实际数字。

- “当长时间运行的进程完成时会发生什么——它真的停止了吗？”——轮询循环、监视器、后台线程和运行到完成的守护进程应有明确的终止条件。如果循环检查“是否有更多工作？”但从不检查“所有工作是否完成？”，它将在完成后永远运行。这在批处理处理器和队列消费者中尤其常见。

从这些知识中生成至少 5 个排名靠前的失败场景。你不需要观察到这些失败——你知道这些类型的系统会发生这些失败。将它们作为**具体的错误假设，带有文件路径和行号引用**，按优先级排序。将每个场景表述为：“因为 [文件:行] 中的代码执行 [X]，一个 [领域特定的边缘情况] 将产生 [错误行为] 而不是 [正确行为]。” 然后将它们与实际探索的代码相结合：“阅读 persistence.py 行 ~340（save_state）：验证临时文件 + 重命名模式。”

**失败的反模式**：列出代码已经有的防御性模式（代码做正确的事情）的质量风险部分不是一个风险分析——它是一个放心练习，不会发现错误。一个列出有风险模块但没有具体失败场景的部分是不可操作的。一个得出“这是一个成熟的、经过充分测试的库，所以基本错误不太可能”的结论的部分是主动有害的——成熟的库有最微妙的 API 合同和边缘案例错误，正是因为明显的错误几年前就被发现了。测试：代码审查员能否阅读每个场景并立即知道要打开哪个函数和要测试什么输入？如果不能，场景太抽象了。

### 第 7 步：导出可测试需求

**阅读 `references/requirements_pipeline.md`** 以了解完整的五阶段管道、领域检查表和版本控制协议。

这是代码审查协议中最重要的步骤。在探索期间发现的——规范、ChangeLog 条目、配置结构、源代码注释、聊天历史——都会被提炼为一组可测试需求，代码审查将验证这些需求。管道将合同发现与需求导出分离，使用基于文件的内存，并包括使用完整性门控的机械验证。

**为什么这很重要**：结构化代码审查可以捕获大约 65% 的实际缺陷。其余的 35% 是意图违规——缺失错误、跨文件矛盾和设计差距。这些在代码阅读中是不可见的，因为代码中正确的内容是正确的。你需要知道代码应该做什么，然后检查它是否做了。这就是可测试需求提供的内容。

**五阶段管道**：

1. **阶段 A — 合同提取。** 阅读所有源文件，列出每个行为合同。写入 `quality/CONTRACTS.md`。这是发现——列出所有内容，即使它看起来很明显。
2. **阶段 B — 需求导出。** 阅读CONTRACTS.md和文档。将相关的合同分组，使用用户意图进行丰富，编写正式需求。将 REQ 记录写入 `quality/requirements_manifest.json`（事实来源）并渲染到 `quality/REQUIREMENTS.md`。对于每个需求，记录 `tier`（1–5，根据 schemas.md §3.1）——当 `tier ∈ {1, 2}` 时——由 `bin/reference_docs_ingest` 调用 `bin/citation_verifier` 生成的 `citation` 块（根据 schemas.md §5.4 / §5.5）。LLM 不会直接调用 `citation_verifier`；摘录是摄取管道的产品，并在门控时由 `quality_gate.py` 重新验证。对于 Tier 3 REQs（代码是规范），在 `description` 中引用源 `file:line`；引用仅用于正式文档参考，并且不得出现在 Tier 3/4/5 REQs 上。等级 + 引用对创建了可追溯性链的前向链接：reference_docs/cite → requirements → 错误 → 测试。见本步骤后面的等级/引用框架块以了解完整的字段列表和 Tier-1 胜过 Tier-2 规则。

   **REQs 上的可选 `Pattern:` 字段。** 需要阶段 3 补偿网格的需求应声明其模式类：

   - `Pattern: whitelist` — 权威项目列表，每个站点都必须处理每个项目。
   - `Pattern: parity` — 必须匹配的对称操作
     （编码↔解码、设置↔拆卸）。
   - `Pattern: compensation` — 必须弥补共享差距的站点。

   缺少该字段意味着没有网格。设置无效值会导致 `quality_gate.py` 失败。

   **保留规则（阶段 2）。** 虽然在设计中 `Pattern:` 是可选的（某些 REQs 是单站点且不需要网格），但在阶段 1 假设已经包含它时它是必需的。阶段 2 必须将 `Pattern:` 从 EXPLORATION.md 转录到 `quality/REQUIREMENTS.md` 和 `quality/requirements_manifest.json`，只要它存在。沉默遗漏是 v1.4.5 回归向量——阶段 5 的基数门控无法强制执行对标记为模式的需求的覆盖率。门控的结构后备（C13.7/Fix 2）会检查带有每个站点 UC 引用（由阶段 1 的笛卡尔 UC 规则发出，形式为 `UC-N.a`/`UC-N.b`）的 REQs，如果此类 REQ 缺少模式，则门控失败。

**代码存在性声明的原始来源提取规则**。当编写断言特定常量、值或标签由特定函数处理（例如，“白名单必须保留 X、Y 和 Z”）的要求时，该要求必须区分**规范说明应该存在的内容**和**代码实际包含的内容**。从代码中提取实际内容（case 标签、map 键、if-else 分支），并与规范列表进行比较。如果常量出现在规范中但**未出现在代码中**，则将要求写成“必须处理 X — **[不在代码中]**：定义在 header.h:NN，但在 file.c:NN-NN 的 function() 中缺失。”不要在没有验证 X 实际被保留的情况下编写“必须保留 X”。这可以防止污染链，其中要求断言代码存在性，代码审查复制了该断言，规范审查继承了它，而问题分类接受了它——所有这些都不阅读实际代码。在 v1.3.17 的 virtio 测试中观察到了这个精确的链：REQUIREMENTS.md 断言 RING_RESET 在 switch 中被保留，代码审查复制了列表，三个规范审查员继承了该声明，而问题未被检测到。

**分发函数的机械验证工件（强制）**。当一个合同断言一个函数处理、保留或分发一组命名的常量（特性位、枚举值、指令表、事件类型、处理程序注册表）时，你必须生成并执行一个 shell 命令或脚本，该命令机械地从函数体中提取实际的 case 标签/分支**在编写合同行之前**。将原始输出保存到 `quality/mechanical/<function>_cases.txt`。该命令必须是一个非交互式管道（例如，`awk` + `grep`），它不能产生幻觉——它读取文件字节并打印匹配项。示例：

```bash
awk '/void vring_transport_features/,/^}$/' drivers/virtio/virtio_ring.c \
  | grep -E '^\s*case\s+' > quality/mechanical/vring_transport_features_cases.txt
```

执行后，阅读输出文件并将其用作函数处理的真实来源。断言“函数保留常量 X”的合同行是**禁止**的，除非 `quality/mechanical/<function>_cases.txt` 包含匹配的 `case X:` 行。如果常量出现在规范或头文件中但**未出现在机械输出中**，合同必须记录它为缺失：“必须处理 X — **[不在代码中]**：定义在 header.h:NN，但根据机械检查在 function() 中缺失。”下游工件（`REQUIREMENTS.md`、`RUN_SPEC_AUDIT.md`、代码审查）在引用分发函数覆盖范围时必须引用机械文件路径——它们不能用手工编写的列表替换机械输出。

**机械工件完整性检查（强制）**。对于每个机械提取命令，也将其作为验证步骤追加到 `quality/mechanical/verify.sh` 中。该脚本必须重新运行相同的提取管道并将结果与保存的文件进行比较。使用以下结构生成 `verify.sh`：

```bash
#!/bin/bash
# Auto-generated: 重新运行机械提取命令并验证保存的工件
set -euo pipefail
FAIL=0

# Verify <function>
ACTUAL=$(awk '/void vring_transport_features/,/^}$/' drivers/virtio/virtio_ring.c | grep -nE '^\s*case\s+')
SAVED=$(cat quality/mechanical/vring_transport_features_cases.txt)
if [ "$ACTUAL" != "$SAVED" ]; then
  echo "MISMATCH: vring_transport_features_cases.txt"
  diff <(echo "$ACTUAL") <(echo "$SAVED") || true
  FAIL=1
else
  echo "OK: vring_transport_features_cases.txt"
fi

exit $FAIL
```

**第 6 阶段必须执行 `bash quality/mechanical/verify.sh`**，如果任何工件不匹配，基准测试将失败。这捕获了在 v1.3.19 中观察到的故障模式：模型执行了提取命令，但将其自己的预期输出写入文件，而不是让 shell 重定向捕获它，插入了一个 `case VIRTIO_F_RING_RESET:` 行，而实际命令不会生成该行。在单独的步骤中重新运行相同的命令并与文件进行比较可以检测到这种篡改。

**立即完整性门禁（强制，第 2a 阶段）**。在编写每个 `*_cases.txt` 文件后**立即**运行 `bash quality/mechanical/verify.sh`，并在编写任何引用提取的合同、要求或散文工件**之前**运行。如果退出代码 ≠ 0：停止，删除失败的 `*_cases.txt`，使用新的 shell 重定向重新运行提取命令（不要手工编辑输出），并重新验证。在 verify.sh 退出 0 之前不要进入第 3/2c 阶段。将 verify.sh stdout 和退出代码保存到 `quality/results/mechanical-verify.log` 和 `quality/results/mechanical-verify.exit` 作为耐久收据文件。这个门禁存在的原因是 v1.3.23 表明将验证推迟到第 6 阶段允许下游工件（CONTRACTS.md、REQUIREMENTS.md、问题分类探针）在伪造的提取基础上构建——模型通过破坏工件而不是纠正要求来解决要求与工件之间的差异。

**机械工件提取后不可变**。一旦 `*_cases.txt` 文件被 shell 重定向写入并由 `verify.sh` 验证，在运行剩余期间不得修改、覆盖或重新生成。如果下游步骤发现机械工件与要求或合同之间存在差异，则要求或合同是错误的——不是工件。修复文本，而不是提取。此规则可防止 v1.3.23 的故障模式，即模型用编造的内容覆盖了正确的提取以匹配其自己的叙述。

**禁止的探针模式（问题分类和验证）**。问题分类探针、验证探针和审计断言不得使用 `open('quality/mechanical/...')` 或 `cat quality/mechanical/...` 作为唯一证据来证明源文件在给定行的内容。为了验证函数 F 在行 N 处处理常量 C，探针必须： (a) 直接读取源文件（`open('drivers/virtio/virtio_ring.c')` 带有行锚定断言），或 (b) 重新执行 `verify.sh` 使用的相同提取管道并检查其输出。读取保存的工件只能证明工件所说的内容，而不是代码所说的内容——这是循环验证。在 v1.3.23 中，探针 C 验证了伪造的工件而不是源代码，用编造的数据通过。

**不要创建空的 mechanical/ 目录**。只有在项目合同包含需要机械提取的分发函数、注册表或枚举检查时才创建 `quality/mechanical/`。如果不存在此类合同，则完全跳过该目录，并在 PROGRESS.md 中记录：`机械验证：不适用——范围内没有分发/注册表/枚举合同。` 创建空的 mechanical/ 目录（或一个没有 verify.sh 的目录）是不合规的——它表明提取被尝试并放弃了。在创建目录之前做出决定：此项目是否有分发函数合同？如果没有，不要 `mkdir`。如果有，完全填充它。

**规范性与描述性分离**。要求和合同必须使用规范性语言（“必须保留”、“应处理”）来描述预期行为。它们只能在机械验证工件确认声明时使用描述性语言（“保留”、“处理”）。一个说“实现保留 VIRTIO_F_RING_RESET”而没有确认机械工件的合同是不合规的——写“实现**必须**保留 VIRTIO_F_RING_RESET”并引用机械检查结果，显示常量当前是否存在或缺失。

3. **第 C 阶段——覆盖范围验证**。交叉引用每个合同与每个要求。修复差距。最多循环 3 次直到覆盖率达到 100%。写入 `quality/COVERAGE_MATRIX.md`。矩阵必须**每行一个要求**（REQ-001、REQ-002 等）——而不是分组范围，如“C-001 到 C-007 | REQ-001、REQ-003”。分组范围使机器验证不可能并隐藏差距。
4. **第 D 阶段——完整性检查 + 自我完善循环**。应用领域清单、可测试性审计和跨要求一致性检查。还验证每个具有“将覆盖”承诺的覆盖承诺表中的每个深度文档至少有一个追溯到它的要求——如果没有，则在继续之前添加要求。

写入 `quality/COMPLETENESS_REPORT.md` 作为**基线**完整性报告（不包含 `## Verdict` 部分——裁决被推迟到第 5 阶段后重新协调，这是唯一用于关闭的裁决）。然后运行最多 3 次自我完善迭代：阅读报告、修复差距、重新检查。当每次迭代的更改少于 3 个时，中断。

5. **第 E 阶段——叙述通过**。添加项目概述（带概述验证门禁），然后导出用例（带用例导出门禁）。两个门禁都必须通过才能继续进行类别叙述、跨领域问题和最终重新排序。这种顺序防止了多轮循环，其中失败的后期门禁强制重新导出。按自上而下的流程重新排序。顺序编号。

**REQUIREMENTS.md 必须以人类可读的概述开头**，回答：这个项目是什么？它做什么？参与者是谁（用户、系统、硬件、协议）？最高风险区域是什么？此概述应适用于从未见过此项目的人。如果项目是库或驱动程序，其中所有参与者都是系统，请描述系统参与者（内核维护人员、协议对等方、集成商、最终用户开发人员）及其交互。不要从原始范围元数据或 HTML 注释开始——以纯文本描述开头。

**概述验证门禁（强制）**。在编写概述后，在继续用例导出之前执行此自我检查：

> 这个概述是否以实际用户的方式描述了项目？具体：
> - 它是否命名了项目的生态系统角色和现实世界的重要性？
> - 它是否确定了依赖它的人和依赖原因？
> - 一个每天使用此项目的开发人员会说“是的，这就是它是什么以及它为什么重要”吗？
> - 对于知名项目，它是否反映了公开已知的采用情况（例如，Cobra → kubectl/Hugo/GitHub CLI；Express → 数百万个 Node.js API 服务器；Zod → 表单验证/tRPC；Serde → 默认的 Rust 序列化层）？

如果概述看起来像是由只阅读源代码而从未使用软件的人编写的，则在继续之前修改它。概述为下游所有内容设定了框架——面向功能的用例和内部聚焦的要求是概述只描述代码而不是项目的症状。

**用例导出（强制，在概述门禁之后运行）**。从经过验证的概述和收集的文档中导出 5–7 个用例，然后对照代码进行验证。每个用例必须：

- 描述一个**实际用户结果**，而不是代码功能。“开发人员使用嵌套子命令、持久标志和 shell 完成构建 CLI 工具”——不是“框架支持命令树。”
- 指定一个**具体参与者**以及他们试图完成的目标。参与者包括最终用户开发人员、系统管理员、内核维护人员、协议对等方、集成商和自动消费者。
- 对**实际软件用户**可识别。对于知名项目，使用模型对项目的自身知识、社区文档、教程和现实世界采用模式验证用例。
- 通过可测试的满足条件至少连接到一个要求。

管道应明确询问：“根据此项目的概述、收集的文档和已知用户群，实际用户用此软件最重要的 5–7 件事是什么？” 从这个问题导出用例——而不是扫描代码并将功能分组到类别中。

**用例与代码验证**：从概述和文档中导出用例后，对照代码库验证每个用例。如果一个用例描述了代码实际上不支持的内容，请修改或删除它。如果代码支持一个重要的用户结果而没有任何用例涵盖它，请添加一个。目标是用户可识别且代码基础的用例。

**接受标准跨范围检查（强制，在用例导出之后运行）**。用例最终确定并对照代码验证后，检查所有要求的满足条件是否共同覆盖了项目的主要行为：

> 这些接受标准合在一起是否涵盖了项目？是否有概述或用例中描述的主要用户行为，如果它被破坏，没有任何要求的满足条件会捕获它？

对于每个用例，至少一个要求的满足条件必须可追溯到它，并且至少一个链接的要求必须是 `specific`（不是 `architectural-guidance`）。没有链接的特定要求的用例表明存在差距。发现差距时，要么： (a) 添加新要求或锐化现有条件以覆盖差距，要么 (b) 如果用例没有反映实际保护的要求，则修改用例。在完整性报告中记录此检查的结果。

跟随用例的是单独的要求。

**v1.5.3 等级和引用方案（schemas.md §3.1, §5）**。每个 REQ 带有 `schemas.md` §3.1 的 1–5 级整数 `tier`：

- **等级 1** — 项目自己的正式规范（一个 `FORMAL_DOC` 记录，`tier=1`；最高权威）。
- **等级 2** — 外部正式标准（RFC、W3C、ISO、发布的 API 合同——一个 `FORMAL_DOC` 记录，`tier=2`）。
- **等级 3** — 当没有正式规范时，源代码是规范。
- **等级 4** — 非正式文档，由 `bin/reference_docs_ingest.load_tier4_context` 从顶级 `reference_docs/` 加载（AI 聊天、设计笔记、回顾）。
- **等级 5** — 从代码行为中推断，没有文档支持。

对于 `tier ∈ {1, 2}`，REQ 还带有 `schemas.md` §5 的 `citation` 块，至少包含 `document`、`document_sha256`、至少一个 `section`/`line`，以及机械提取的 `citation_excerpt`。不要手工编写摘录。摘录是在摄取时间由 `bin/reference_docs_ingest` 调用 `bin/citation_verifier` 生成的，遵循 `schemas.md` §5.4 中的确定性算法（带有 §5.5 的部分解析）——LLM 从 `formal_docs_manifest.json` 消费摘录；它永远不会直接调用验证器。摄取时间提取是如何工作的第一层幻觉门禁。如果你无法引用 `quality/formal_docs_manifest.json` 中的文档（带哈希和定位器），REQ 最多为等级 3。`page`-仅定位器是诊断用的，永远不充分。

**等级 1 胜过等级 2 规则**。当一个项目的正式规范（等级 1）和外部标准（等级 2）相互矛盾时，将 REQ 记录为等级 1 并引用项目的立场。项目的文档偏离外部标准是权威意图，不是缺陷——`upstream-spec-issue` 处置仅适用于项目规范对冲突保持沉默时。

**规范差距退化（有效输出状态）**。如果 `formal_docs_manifest.json` 包含零个覆盖项目自身行为的 `FORMAL_DOC` 记录，每个 REQ 都会变成等级 3/4/5，并且运行会优雅地退化到规范差距分析器。在完整性报告中报告元发现“0 等级 1/2 要求”作为指标，而不是失败。不要编造引用以使等级分布看起来更丰富——`quality_gate.py` 通过 §5.4 重新调用 `bin/citation_verifier`（通过 `extract_excerpt`）在验证时间拒绝任何等级 1/2 REQ，其 `citation_excerpt` 与新鲜提取的字节相等（schemas.md §10 不变量 #11）。

**`functional_section` 是必填字段。** 每个 REQ 都包含一个简短的 `functional_section` 字符串（例如 `"身份验证"`、`"总线枚举"`），用于将相关的 REQ 分组。这是从代码和文档中通过 LLM 推导出来的；没有预定义的本体。阶段 2 的渲染将 REQ 分组到这些部分下（每个部分有一个简短的介绍段落），阶段 4 的委员会审查分组的连贯性。参见 `schemas.md` §6.1。

**可追溯性是单向的：REQ → UC。** REQ 包含一个 `use_cases[]` 列表，其中包含 UC-NN ID。UC 记录不包含一个 `requirements[]` 反向链接——反向方向是在渲染时通过查询 REQ 记录来推导的（`schemas.md` §7）。不要在 UC 记录中填充 `requirements[]` 字段。

**对于每个需求，提供以下所有字段：**

- **ID**：`REQ-NNN`（零填充的三位数序列）。
- **标题**：简短的、单行陈述。
- **级别**：每个需求为 1–5，参见 `schemas.md` §3.1。
- **功能部分**：简短的 LLM 推导字符串（见上文）。
- **引用**（当 `tier ∈ {1, 2}` 时必填）：由 `bin/reference_docs_ingest` 调用 `bin/citation_verifier` 生成；永远不会手工编写，也不会直接由 LLM 调用。形状参见 `schemas.md` §5.1。
- **摘要 / 描述**：将需求表述为可测试的断言：“X 必须满足 Y”或“当 A 时，系统必须 B”。
- **用户故事**：从调用者的角度来表述： “作为一个 [角色] 执行 [动作]，我期望 [行为] **以便** [结果]。” “以便”子句是强制性的——它迫使你阐述需求背后的意图。
- **实现说明**：代码如何实现此需求——机制、相关的代码路径、设计选择。
- **满足条件**：特定的、可测试的场景，证明此需求已满足。包括快乐路径、边缘情况以及失败模式。来自阶段 A 的每个被分组到此需求的独立合同都成为满足条件。
- **替代路径**：多个代码路径、模式或入口点，所有这些都必须满足此需求。替代路径是隐藏错误的地方。
- **用例**：`use_cases[]`——此 REQ 参与的 `UC-NN` ID 列表。单向前向链接。
- **参考文献**：引用来源——规范部分、ChangeLog 条目、配置字段定义、源代码注释、问题编号或领域知识。对于 Tier 1/2 REQ，`citation` 块包含权威定位符；自由形式的参考文献是补充性的。
- **具体性**：**具体**（可测试的——必须具有供代码审查者对照特定代码位置或行为的满足条件；这是默认值，并计入覆盖率指标）或 **架构指导**（不可针对单个代码路径——涵盖跨切面属性，如“保持轻量级和 stdlib 兼容”或“no_std 支持”；指导质量宪法，但不计入覆盖率指标；大多数项目应有 0–3 个架构指导需求——超过 3 个会触发下文的强制自我检查）。“方向性”类别已退役。任何原本会是“方向性”的需求必须要么被改为具体（具有可测试的满足条件），要么明确归类为架构指导。

  **架构指导自我检查（强制，在需求推导后执行）。** 计算 `architectural-guidance` 标记的需求数量。应用两个边界：

  - **最大边界（>3）**：如果数量超过 3，停止并重新审查每个需求。对于每个需求，问：“我能添加一个可测试的满足条件，供代码审查者对照特定代码位置验证吗？”如果可以，将其重新分类为 `specific` 并添加条件。只有那些确实无法验证任何特定代码路径的需求应保持 `architectural-guidance`。最终计数超过 3 需要为每个多余需求提供明确理由，解释为什么无法使其具体化。
  - **最小边界（15+ 需求为 0）**：如果总需求数量为 15 或更多，且 `architectural-guidance` 数量为 0，重新审查需求以查找跨切面设计不变量。跨越协议层的库、管理资源生命周期的库、执行排序保证的库或维护兼容性合同（例如，“保持 stdlib 兼容”、“保留 no_std 支持”、“维护 wire-format 向后兼容”）通常有 1–3 个架构指导需求。在完整性报告中写一句话，解释为什么没有需求符合架构指导，或者重新分类适当的需求。

  在完整性报告中记录数量和任何重新分类。

**不要限制需求数量。** 根据项目需求推导尽可能多的需求。一个小工具可能有 20 个。一个成熟的库可能有 100 多个。目标是完整性。

**步骤 7a：文档到需求的协调**

重新阅读 PROGRESS.md 中的覆盖率承诺表。对于每个你承诺覆盖的深度文档（“将在阶段 2 覆盖”），验证至少有一个需求追溯到它所文档化的子系统。如果你的需求只覆盖了部分承诺的子系统，请在完成步骤 7 之前添加需求以填补空白。

对于每个子系统，在 PROGRESS.md 中记录以下之一：
- 覆盖它的需求 ID，或
- 带有理由、风险承认和建议后续处理的明确排除

一个深度文档化的子系统，带有“将覆盖”承诺且没有映射需求，是流程失败，而不是合法的范围选择。在生成工件之前，不要继续进行，直到每个承诺都得到满足或明确转换为有理由的排除。

**步骤 7b：代码路径 → REQ 反向可追溯性审计（强制）**

**时间：在阶段 E 完成后执行步骤 7a 和 7b**（即，在概述验证门、用例推导和接受标准跨度检查都运行后）。此审计依赖于最终的需求和最终的用例。

需求推导完成后，运行反向可追溯性审计。正向可追溯性（收集的文档→需求→错误→测试）已经集成到管道中。此步骤检查代码路径粒度上的反向方向：重要的代码路径是否映射回需求条件？这是一个审计活动——不是结构化的双向链接。（v1.5.3 中的结构化可追溯性是单向 REQ → UC，根据 `schemas.md` §7 强制执行；此审计检查代码对需求的覆盖率，这是一个不同的关注点。）

此操作在 **路径/分支/辅助函数粒度** 上进行，而不是文件级别。文件级覆盖率在 v1.3.13 中为 100%，但仍遗漏了两个真实错误。问题是“这个文件是否映射到某个需求？”而不是“这个重要分支是否映射到声明必须在此处保留的需求条款？”

**限定在四个类别**（不是开放式分支审计）：

1. **需求中已经命名的替代路径。** 如果一个需求提到了回退或替代路径（例如，“主要与降级模式”、“协商与默认配置”、“同步与异步”），每个替代路径都必须有一个明确的 **对称条件**——一个声明在两个路径上必须保持的不变量的陈述。一个声明“系统处理 X 和 Y”但没有指定“处理”对每个路径意味着什么的需求是不完整的。

2. **将公共常量转换为运行时行为的辅助函数。** 如果一个辅助函数白名单、过滤或翻译定义的常量和运行时行为（例如，功能标志门、编解码器注册表查找、能力白名单辅助函数），它必须有一个辅助函数特定的需求，枚举预期的保留/翻译值。

3. **能力协商和回退逻辑。** 系统与外部对等方协商能力的代码路径（协议版本协商、功能检测、优雅降级）必须具有覆盖协商上和协商下的路径的需求。

4. **在先前的 BUGS.md、VERSION_HISTORY.md 或规范审计输出中命名的函数。** 如果先前的运行在特定函数中发现了错误，未来的运行必须为该函数提供明确的重新检查证据（“已知错误类哨兵”）。这防止了“丢失需求”回归类别。如果 `quality/spec_audits/` 中存在先前的规范审计输出，在运行哨兵检查之前阅读它们——委员会审查的跨模型发现是已知错误表面的高价值来源。

对于每个类别，检查需求是否包含特定的条件，覆盖已识别的路径。孤儿路径——没有需求覆盖的重要代码路径——会在完整性报告中触发“覆盖率差距”标记。这些差距必须解决（通过添加需求条件或提供明确理由），才能在完整性报告声明需求足够之前继续。

**传递规则**：当质量目录中存在先前的 REQUIREMENTS.md 时，管道必须读取它并检查先前的版本是否丢弃了任何条件。如果条件被丢弃，管道必须： (a) 使用更新后的理由重新推导它们，或 (b) 文档化为什么条件不再相关。不允许静默丢弃——它们是导致运行之间丢失先前学习到的需求的直接原因。

**管道之后**：阶段 7 可以生成 `quality/REVIEW_REQUIREMENTS.md`（交互式审查协议）和 `quality/REFINE_REQUIREMENTS.md`（精炼通过协议）。这些不是阶段 2 的工件——它们支持阶段 7 的交互式改进路径。用户可以交互式地审查需求，使用不同的模型运行精炼通过，并保留每个迭代的版本备份。参见 `references/requirements_pipeline.md` 了解完整的版本控制协议和备份结构。

将所有需求记录为结构化格式。这些直接输入代码审查协议的验证和一致性通过。

### 检查点：在阶段 1 后更新 PROGRESS.md

**v1.5.6 更新——PROGRESS.md 现在在运行开始时初始化，而不是在阶段 1 之后。** 根据本文件前面“运行状态仪器化”部分，`quality/PROGRESS.md` 和 `quality/run_state.jsonl` 在任何阶段工作开始之前写入。在阶段 1 的这个时间点，这两个文件已经存在。这个检查点是 **阶段 1 完成更新**，而不是初始化。

PROGRESS.md 的格式结合了运行状态标题（Started / Benchmark / Lever / Runner / Playbook 版本）、阶段清单（现在由 `phase_start` / `phase_end` 事件从 `quality/run_state.jsonl` 驱动），以及以下的传统内容部分（运行元数据、工件清单、累积 BUG 追踪器等）——它们是互补的，而不是竞争的。

**阶段 1 完成操作**：在阶段清单中标记阶段 1 为 `[x]`，并添加摘要统计（发现计数、遍历的模式）；将阶段 1 工件（EXPLORATION.md 和任何子工件）添加到工件清单。根据运行状态仪器化部分中的跨验证规则，向 `run_state.jsonl` 添加 `phase_end phase=1` 事件。

**PROGRESS.md 存在的原因**：在单会话运行中，代理在内存中保留上下文。但上下文会随着长时间运行而退化——阶段 1 的发现会被阶段 6 忘记，BUG 计数会漂移，规范审计中的 BUG 因为闭包检查从未看到它们而被遗弃。PROGRESS.md 通过让每个阶段将其状态写入磁盘来解决此问题。代理在每个阶段开始之前读取它，因此它始终有一个准确的到目前为止发生了什么的快照。作为附带的好处，即使运行跨越多个会话，它也能使技能正确工作。

**长时间运行的检查点纪律**：在需求管道的每个阶段（合同、需求、覆盖率矩阵、完整性、叙述）后，更新 `quality/PROGRESS.md`，记录：完成的阶段、工件路径、当前限定的子系统、剩余工作、以及确切的恢复点。这确保了会话可以从中断的最后一个检查点继续，而无需重做工作。根据 v1.5.6，还向 `run_state.jsonl` 添加相应的 `pass_started` / `pass_ended` 事件。

**时间戳纪律**：在完成每个阶段后立即将每个阶段完成条目写入 PROGRESS.md，在开始下一个阶段之前。不要批量写入或事后补录时间戳。时间戳是审计线索——如果阶段 2 显示的完成时间早于阶段 1，审查者无法验证阶段是否按正确顺序运行。如果你意识到忘记写入检查点，现在写入它，并附上诚实的时戳和一个解释差距的注释。

v1.5.6 初始化的文件在阶段 1 完成后将填充的完整 PROGRESS.md 格式包括以下部分（保留传统模板，因为阶段 5+ 依赖于它的累积 BUG 追踪器和终端门验证部分）：

```markdown
# 质量剧本进度

## 运行元数据
开始时间：[日期/时间]
项目：[项目名称]
技能版本：[从 SKILL.md 元数据使用参考文件解析顺序读取——必须完全匹配]
带文档：[是/否]

## 阶段完成
- [x] 阶段 1：探索——完成 [日期/时间]
- [ ] 阶段 2：工件生成（QUALITY.md、REQUIREMENTS.md、测试、协议、RUN_TDD_TESTS.md）——`AGENTS.md` 由协调器在阶段 6 后生成，不是这里
- [ ] 阶段 3：代码审查 + 回归测试
- [ ] 阶段 4：规范审计 + 分配
- [ ] 阶段 5：审查后协调 + 关闭验证
- [ ] TDD 日志：每个确认错误的 red-phase 日志，每个有修复补丁的 bug 的 green-phase 日志
- [ ] 阶段 6：验证基准
- [ ] 阶段 7：呈现、探索、改进（交互式）

## 工件清单
| 工件 | 状态 | 路径 | 备注 |
|------|------|------|------|
| QUALITY.md | 待定 | | |
| REQUIREMENTS.md | 待定 | | |
| CONTRACTS.md | 待定 | | |
| COVERAGE_MATRIX.md | 待定 | | |
| COMPLETENESS_REPORT.md | 待定 | | |
| 功能测试 | 待定 | | |
| RUN_CODE_REVIEW.md | 待定 | | |
| RUN_INTEGRATION_TESTS.md | 待定 | | |
| BUGS.md | 待定 | | |
| RUN_TDD_TESTS.md | 待定 | | |
| RUN_SPEC_AUDIT.md | 待定 | | |
| tdd-results.json | 待定 | quality/results/ | 结构化 TDD 输出 |
| integration-results.json | 待定 | quality/results/ | 结构化集成输出 |
| Bug 撰写 | 待定 | quality/writeups/ | 每个通过 TDD 验证的 bug 一个 |

## 累积 BUG 追踪器
<!-- 从代码审查和规范审计中每个确认的 BUG 都放在这里。
     每个条目跟踪关闭状态：回归测试参考或明确豁免。
     关闭验证步骤读取此列表以确保没有孤儿。 -->

| # | 来源 | 文件:行 | 描述 | 严重性 | 关闭状态 | 测试/豁免 |
|---|------|--------|-------|--------|----------|----------|
<!-- 关闭状态值：
     - "确认打开 (xfail)" — 存在 bug，回归测试确认它，修复待定
       语言等价物：Python "xfail"，TypeScript/JS "test.fails"，Go "t.Skip",
       Java "@Disabled"，Rust "compile_fail"（用于编译时 bug）。使用适当的语言术语，例如 "确认打开 (@Disabled)"
     - "TDD 验证 (FAIL→PASS)" — 完整的 red-green 循环：未修复时测试失败，修复后通过
     - "已修复 (测试通过)" — bug 已修复，回归测试现在通过，xfail 标记已移除
     - "豁免 (原因)" — 不可能进行回归测试，原因已记录 -->

## 终端门验证
<!-- 在阶段 5 中填充。必须与 BUG 追踪器计数完全匹配。 -->

## 探索摘要
[关于架构、关键模块、规范来源、防御性模式发现的简要笔记]

```

在每阶段后更新此文件。累积 BUG 追踪器是最重要的部分——它确保无论哪个阶段生成发现，都不会被遗弃。

初始化 PROGRESS.md 后，将您的完整探索发现写入 `quality/EXPLORATION.md`。此文件捕获您在第一阶段学到的所有内容，以便在上下文边界（会话中断、多轮交接或长时间运行内存退化）后仍然存在。按以下结构组织：

```markdown
# 探索发现

## 领域和堆栈
[语言、框架、构建系统、部署目标]

## 架构
[关键模块及其文件路径、入口点、数据流、分层结构]

## 现有测试
[测试框架、测试数量、覆盖范围、空白区域]

## 规范
[reference_docs/ 包含的内容、关键规范部分、行为规则]

## 开放式探索发现
[至少 8 个来自领域驱动调查的具体发现。
每个发现必须包含文件路径、行号和具体的错误假设。
至少 4 个必须引用不同的模块或子系统。
至少 3 个必须追踪跨 2 个或多个函数的行为。]

## 质量风险
[至少 5 个按优先级排序的领域驱动故障场景。
每个场景必须命名一个特定的函数、文件和行，并使用该领域知识解释错误机制——即像这样系统可能出错的原因。
这些是假设，不是已确认的错误——它们告诉第二阶段要查找的地方。
每个场景的表述格式为："因为 [文件:行] 中的代码执行 [X]，一个 [领域特定的边界情况] 将产生 [错误行为] 而不是 [正确行为]。"
一个列出代码已具备的防御模式的章节不属于这里。]

## 骨架和调度
[状态机、调度表、功能注册表——带文件:行引用]

## 模式适用性矩阵
| 模式 | 决策 (`FULL` / `SKIP`) | 目标模块 | 原因 |
|---|---|---|---|
| 回退和退化路径一致性 | | | |
| 调度器返回值正确性 | | | |
| 跨实现一致性 | | | |
| 枚举和表示完整性 | | | |
| API 表面一致性 | | | |
| 规范结构解析保真度 | | | |

[3 到 4 个模式必须标记为 FULL。其余为 SKIP 并附带特定代码库的合理化说明。当第四个模式明显适用且覆盖不同代码区域时，选择 4 个。]

## 模式深入分析 —— [模式名称]
[使用 `exploration_patterns.md` 的输出格式。
追踪相关代码路径跨越 2 个或多个函数、实现或 API 表面。
每个深入分析应压力测试、细化或扩展开放式探索和质量管理阶段中的发现。]

## 模式深入分析 —— [模式名称]
[重复每个选定的 FULL 模式。总共 3 到 4 个深入分析部分。]

## 模式深入分析 —— [模式名称]
[第三个也是最后一个深入分析。]

## 第二阶段候选错误
[综合自所有先前部分——开放式探索、质量风险和模式。
至少 4 个候选错误带文件:行引用。至少 2 个来自开放式探索或质量风险，至少 1 个来自模式深入分析。对每个候选错误包括发现阶段和第二阶段代码审查应检查的内容。]

## 派生需求
[REQ-001 至 REQ-NNN，每个需求附带规范依据和级别]

## 派生用例
[UC-01 至 UC-NN，每个用例附带参与者、触发器和预期结果]

## 资产生成备注
[下一阶段需要了解的任何内容——命名约定、测试模式、框架怪癖]

## 状态自检
[由第一阶段状态检查员编写。每个检查 1–12，带 PASS/FAIL 和一句话证据。
本节证明状态检查已执行。在您实际根据文件内容验证每个检查之前，不要编写本节。]
```

**最低深度要求：** EXPLORATION.md 必须包含至少 120 行实质性内容——不是填充或样板头信息，而是实际发现（文件路径、行为规则、派生需求、架构观察）。一个仅列出章节标题和一句话占位符的骨架不是有效的交接资产。如果文件比这更薄，请回去添加第二阶段需要的细节。

**写后重读（强制）。** 写完 EXPLORATION.md 后，在继续第二阶段之前，明确从磁盘读取该文件。这有两个目的：(1) 它确认文件已正确写入，(2) 它将结构化发现加载到工作内存中，以便生成资产。不要跳过此步骤并依赖您记忆中写入的内容——"写后读"周期是上下文桥梁。

此文件在所有模式下都至关重要。在单次通过模式下，它迫使模型在生成资产之前明确具体发现（文件路径、函数名、行号）。在多次通过模式下，它也是两次通过之间的交接资产。无论如何，"写后读"周期是探索深度的质量门。

**第一阶段完成状态检查（强制——在进入第二阶段前停止）。** 您必须在进入第二阶段之前执行此状态检查。这不是可选的。从磁盘重读 `quality/EXPLORATION.md` 并运行以下所有检查。检查后，在 EXPLORATION.md 的末尾追加 `## 状态自检` 部分列出了每个检查编号（1–12）和 PASS 或 FAIL 以及一句话证据。如果有任何检查失败，请修复 EXPLORATION.md 并重新运行状态检查。在所有检查通过并且状态自检部分写入磁盘之前，不要进入第二阶段。

**常见的状态检查绕过失败模式：** 在 v1.3.43 基准测试中，两个存储库（chi, zod）生成的 EXPLORATION.md 文件具有完全错误的章节结构——例如 "架构摘要"、"行为合同"、"存储库和架构映射" 而不是要求的章节。模型从未运行状态检查并直接进入第二阶段，产生了零错误。如果您的 EXPLORATION.md 不包含下面列出的确切标题的章节，它是非合规的，必须在继续之前重写。

1. 文件存在于磁盘上，并包含至少 120 行实质性内容。
2. `quality/PROGRESS.md` 存在并标记第一阶段完成。
3. 派生需求部分至少包含一个 REQ-NNN，附带具体文件路径和函数名——不是抽象子系统描述。
4. 一个标题**完全**为 `## 开放式探索发现` 的章节存在，并包含至少 8 个具体错误假设或可疑发现，每个发现都有文件路径和行号。这些必须来自领域驱动调查，而不仅仅是应用模式。至少 4 个必须引用不同的模块或子系统。
5. **开放式探索深度检查：** `## 开放式探索发现` 中的至少 3 个发现必须追踪跨 2 个或多个函数或 2 个具体代码位置的行为。一个孤立的单一函数怀疑列表不足以达到深度。
6. 一个标题**完全**为 `## 质量风险` 的章节存在，并包含至少 5 个按优先级排序的领域驱动故障场景。每个场景必须：(a) 命名一个特定的函数、文件和行，(b) 描述一个领域特定的边界情况或故障模式，(c) 解释代码为何产生错误行为。这些必须来自关于像这样系统可能出错的知识——而不是仅从代码结构分析。一个列出代码已具备的防御模式（代码正确的地方）的章节不属于这里。一个列出高风险模块但没有具体故障场景的章节不属于这里。一个得出库成熟的结论且不太可能存在基本错误的章节不属于这里。
7. 一个标题**完全**为 `## 模式适用性矩阵` 的章节存在，并评估 `exploration_patterns.md` 中的所有六个模式，标记每个模式为 `FULL` 或 `SKIP` 并附带目标模块和特定代码库的合理化说明。
8. 适用性矩阵中标记为 `FULL` 的模式在 3 到 4 个之间（包含）。
9. 有 3 到 4 个以 `## 模式深入分析 — ` 开头的章节（包含）。每个必须包含具体文件:行证据，而不仅仅是模式名称占位符。数量必须与矩阵中 `FULL` 模式的数量匹配。
10. **模式深度检查：** 至少 2 个模式深入分析章节必须追踪跨越 2 个或多个函数的代码路径。一个说 "函数 X 在文件:行有一个空白" 是表面发现。一个说 "函数 X 在文件:行调用函数 Y 在文件:行，它做 A 但不做 B；与函数 Z 做两者比较" 是深度发现。
11. 一个标题**完全**为 `## 第二阶段候选错误` 的章节存在，并包含至少 4 个带文件:行引用的优先级错误假设，每个错误假设的发现阶段以及第二阶段代码审查应检查的内容。
12. **集成平衡检查：** 至少 2 个候选错误必须来自开放式探索或质量风险，至少 1 个必须来自模式深入分析或被模式深入分析实质性地加强。这确保了领域知识和结构分析发现都流入第二阶段。

在所有十二个检查通过并且 `## 状态自检` 部分写入 EXPLORATION.md 磁盘上之前，不要开始第二阶段。第一阶段是您深入理解代码库的唯一机会。您在这里遗漏的每个需求都会在第三阶段无法发现错误。投资时间。

**如果您发现自己即将开始第二阶段而没有编写状态自检部分，停止。** 回去运行状态检查。此指令存在的原因是模型在它们对自己的探索有信心时会可靠地跳过状态检查——而信心正是错误被遗漏的时候。

**阶段结束消息（强制——在第一阶段完成后打印此消息，然后停止）：**

```
# 第一阶段完成——探索

我已经探索了代码库并将我的发现写入 `quality/EXPLORATION.md`。
[总结：多少个候选错误，探索了哪些子系统，识别了哪些关键风险。]

要继续到第二阶段（生成质量资产），请说：

    运行质量剧本第二阶段。

或者说 "继续" 以自动继续。
```

**打印此消息后，停止。** 除非用户明确要求，否则不要进入第二阶段。

使用适合该语言的注释语法（`#`、`//`、`/* */` 等）。印章中的版本必须与该技能的前置元数据中的 `metadata.version` 匹配。此印章使每个生成的工件都可追溯至创建它的工具、版本和运行记录——这对于文件通过邮件发送、附加到工单或在仓库上下文之外进行审查时至关重要。使用 playbook 生成开始时的日期，而不是每个单独文件写入的日期。

**印章放置和豁免：**
- 对于带有编码声明（`# -*- coding: utf-8 -*-`）或 shebang（`#!/usr/bin/env python`）的 Python 文件，将印章注释放置在声明/shebang 之后，而不是之前——将其推到第 2 行之后会导致 `SyntaxWarning`。
- 对于边车 JSON 文件（`tdd-results.json`、`integration-results.json`），`skill_version` 字段已作为版本印章。JSON 不支持注释——不要注入一个。
- 对于 JUnit XML 文件，不需要印章——这些是由框架生成的。
- 对于 `.patch` 文件，不要将印章注入 diff 正文——这会破坏 `git apply`。依赖周围的工件元数据（BUGS.md、tdd-results.json）来追溯来源。

**工件依赖规则：**
- `quality/RUN_CODE_REVIEW.md` 第 2 阶段依赖于稳定的 `quality/REQUIREMENTS.md`——薄弱的需求会产生薄弱的第 2 阶段审查。如果代码表面（每个核心模块少于 ~3–4 个需求）的需求计数似乎较低，请在第 2 阶段报告的开头注明这一点。
- 功能测试依赖于 `quality/REQUIREMENTS.md` 和 `quality/QUALITY.md`——在任何需求细化之后，重新验证 `test_functional.*` 是否仍然涵盖所有需求。
- `quality/RUN_SPEC_AUDIT.md` 依赖于需求、质量场景和文档验证。
- `quality/COMPLETENESS_REPORT.md` 有两个阶段：基线（预审查，无裁决部分）和最终（第 5 阶段后期一致后的裁决）。
- `quality/PROGRESS.md` 是权威状态文件，必须在每个下游工件开始之前更新。

**为什么是九个文件而不是仅仅测试？** 测试可以捕获回归，但不能防止新的错误类别。质量宪法（`QUALITY.md`）告诉未来的会话在开始编写代码之前“正确”的含义。协议（`RUN_*.md`）为审查、集成测试和规范审计提供结构化流程，以产生可重复的结果——而不是将质量交给 AI 想检查什么。这些文件共同创建了一个质量系统，其中每个部分都相互强化：QUALITY.md 中的场景映射到功能测试文件中的测试，这些测试由集成协议验证，这些协议由三人理事会审计。

### v1.5.3 JSON 元数据规范（在编写任何工件之前阅读）

第 2 阶段为每个派生记录编写两个并行的渲染：一个 **JSON 元数据**（机器可读、门控验证——真实来源）和一个 **Markdown 工件**（人类可读、从元数据渲染）。更新其中一个而不更新另一个的阶段脚本是一个错误。

元数据位于：

- `quality/formal_docs_manifest.json` — 由 `bin/reference_docs_ingest.py` 在第 1 阶段写入。不要重写。
- `quality/requirements_manifest.json` — 每个权威 REQ 记录按 schemas.md §6。
- `quality/use_cases_manifest.json` — 每个权威 UC 记录按 schemas.md §7。
- `quality/bugs_manifest.json` — 每个权威 BUG 记录按 schemas.md §8。在第 3/4/5 阶段确认错误后写入。
- `quality/citation_semantic_check.json` — 第 4 阶段理事会第 2 层裁决（见第 4 阶段以下）。

每个元数据都遵循 §1.6 包装器，带有 `schema_version`、`generated_at` 和顶级记录数组。四个记录形状的元数据（`formal_docs_manifest.json`、`requirements_manifest.json`、`use_cases_manifest.json`、`bugs_manifest.json`）使用 `records` 作为数组键：

```json
{
  "schema_version": "<from SKILL.md metadata.version>",
  "generated_at": "<ISO 8601 with explicit Z timezone>",
  "records": [ /* per-schema records, per schemas.md §4–§8 */ ]
}
```

**例外——`citation_semantic_check.json` 使用 `reviews` 而不是 `records`** 按 `schemas.md` §9.1。相同的包装器形状，不同的数组键；里面的记录是理事会审查条目，而不是 REQ/UC/BUG 记录。如果你发现自己将 `records` 写入 `citation_semantic_check.json`，请停止并重新阅读 schemas.md §9——当键错误时，门控会拒绝此文件作为元数据包装器违规（schemas.md §10 不变量 #13）。

`schema_version` 必须等于此技能在生成时的 `metadata.version`——从 SKILL.md 中读取，不要硬编码。`generated_at` 使用 `datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")`。记录形状和不变量在 `schemas.md` 中定义——不要在此技能中重新定义它们。`quality_gate.py`（第 5/6 阶段）根据那些模式逐字段验证元数据。

**REQUIREMENTS.md 渲染约定。** REQUIREMENTS.md 按功能区域组织。每个区域以一段简短的 LLM 编写的引言段落开头，描述该功能区域的作用，然后列出其下的 REQ（按 REQ id 排序）。用例渲染它们的 `formal_doc_refs`，但不要列出 `requirements[]`——可追溯性是单向的 REQ → UC，反向方向在渲染时通过查询 REQ 记录导出。

### 文件 1：`quality/QUALITY.md` — 质量宪法

**阅读 `references/constitution.md`** 获取完整模板和示例。

宪法有六个部分：

1. **目的** — 质量对该项目的含义，以戴明（内置而非检查）为基础，朱兰（适用性）为基础，克罗斯比（质量是免费的）为基础。具体应用这些：对于 *此系统*，“适用性”是什么意思？不是“测试通过”，而是实际的操作要求。
2. **覆盖目标** — 表格将每个子系统映射到目标，并引用实际风险。每个目标必须有“为什么”的依据，基于特定场景——没有它，未来的 AI 会话会争论目标。
3. **覆盖剧场预防** — 项目特定的假测试示例，来自探索期间看到的内容。（原因：AI 生成的测试通常用填充覆盖数字而不捕获真实错误——断言导入工作正常、字典有键或模拟返回配置的值。明确指出此模式可以阻止此模式。）
4. **适用性场景** — 这是核心。每个场景记录一个现实的故障模式，带有代码引用和验证方法。目标是为每个核心模块编写 2 个以上的场景——对于一个中等规模的项目（5–15 个源文件），通常有 8–10 个，小项目更少，复杂项目更多。质量比数量更重要：一个精确捕获真实架构漏洞的场景比三个通用场景更有价值。（原因：覆盖百分比告诉您运行了多少代码，而不是是否正确运行。系统可以有 95% 的覆盖率，但仍然会无声地丢失记录。适用性场景以具体术语定义“正确运行”的实际含义，没有人可以争论。）
5. **AI 会话质量纪律** — 每个 AI 会话必须遵循的规则
6. **人类门控** — 需要人类判断的事项

**场景语气至关重要。** 写“发生了什么”作为架构漏洞分析，具有具体的数量、级联后果和检测难度，而不是抽象规范。“因为 `save_state()` 缺少原子重命名模式，在 10,000 条记录的批次中发生中途崩溃时，会留下损坏的状态文件——下一次运行会得到 JSONDecodeError 并且无法恢复。在规模上，这可能导致 1,693+ 条记录无声丢失，没有任何检测机制。” 读取该场景的 AI 会话不会争论标准。使用您对类似系统的知识来生成现实的故障场景，然后将其基于您实际探索的代码。场景来自代码探索和关于此类系统会出错的知识。

每个场景的“如何验证”必须映射到功能测试文件中的至少一个测试。

### 文件 2：功能测试

**这是最重要的交付物。** 阅读 `references/functional_tests.md` 获取完整指南。

将测试组织成三个逻辑组（类、describe 块、模块或测试框架使用的任何其他东西）：

- **规范需求** — 每个可测试的规范区域一个测试。每个测试的文档引用它验证的规范需求。
- **适用性场景** — 每个 QUALITY.md 场景一个测试。1:1 映射，命名匹配。
- **边界和边缘情况** — 每个来自步骤 5 的防御模式一个测试。

关键规则：
- **完全匹配现有的导入模式。** 阅读现有测试如何导入项目模块，并做同样的事情。做错会导致所有测试失败。
- **在调用每个函数之前阅读每个函数的签名。** 阅读实际的 `def` 行——参数名称、类型、默认值。从项目中读取真实数据文件以了解数据形状。不要猜测函数参数或 fixture 结构。
- **无占位符测试。** 每个测试都必须导入并调用实际的项目代码。如果正文是 `pass` 或断言是平凡的（`assert isinstance(x, list)`），请删除它。不执行项目代码的测试会膨胀计数并创建虚假的信心。
- **测试计数启发式** = （可测试的规范区域）+（QUALITY.md 场景）+（防御模式）。对于一个中等规模的项目（5–15 个源文件），这通常产生 35–50 个测试。显著少于表明遗漏了需求或探索不深入。显著更多是可以的，如果每个测试都有意义——不要为了达到一个数字而填充。
- **跨变体启发式：~30%** — 如果项目处理多种输入类型，请将大约 30% 的测试跨所有变体参数化。确切的百分比不如确保每个跨切面属性都在所有变体中测试重要。
- **测试结果，而不是机制** — 断言规范说应该发生什么，而不是代码如何实现它。
- **使用模式有效的变异** — 边界测试必须使用模式接受的值（来自步骤 5b），而不是模式拒绝的值。

### 文件 3：`quality/RUN_CODE_REVIEW.md`

**阅读 `references/review_protocols.md`** 获取模板。

代码审查协议有三个阶段。每个阶段独立运行——一个全新的会话，除了需求文档之外没有共享上下文。这种干净的分离防止了结构审查和基于需求的审查之间的交叉污染。

**阶段 1 — 结构审查。** 阅读代码并发现异常。这是每个 AI 代码审查工具已经做得很好的。没有需求，没有关注区域——只是模型自己对代码正确性的知识。保持这些强制守卫：

- 行号是强制性的——没有行号，就没有发现
- 阅读函数正文，而不仅仅是签名
- 如果不确定：标记为 QUESTION，而不是 BUG
- 在断言缺失之前使用 Grep
- 不要建议样式更改——只标记不正确的事项

**阶段 1 最小审查区域（明确处理每个区域）：**

1. **输入验证和边界处理** — 检查每个外部或调用者提供数据进入代码的信任边界。每个字符串解析器、枚举查找和二进制格式解析器必须拒绝与有效标记共享有效前缀但包含额外字符的输入。
2. **资源生命周期** — 分配、引用计数管理、错误路径清理、失败时释放锁、文件描述符/句柄生命周期。每个获取引用或资源的函数都必须在每个早期退出路径上释放它，或者必须在获取资源之前完成所有验证。
3. **并发和状态管理** — 锁顺序、原子操作正确性（每个修改共享状态字的原子修改必须使用读-改-写语义并保留预期修改之外的位）、状态机完整性（所有消费者在所有状态中都处理所有状态）。
4. **单元和编码正确性** — 从硬件、协议结构或用户输入读取的每个具有定义单位的字段必须在用于计算或比较之前正确转换。
5. **枚举和白名单完整性** — 当一个函数使用 `switch`/`case`、`match`、if-else 链或任何分支结构来处理一组命名的常量（功能位、枚举值、事件类型、命令代码、权限标志）时，执行 **机械枚举检查**：

   (a) **列表 A（代码提取）**：如果为该函数存在 `quality/mechanical/<function>_cases.txt` 工件，则将其用作权威的代码侧列表——不要手动重新提取。如果不存在机械工件，则从代码中提取实际存在的每个分支/案例标签。列出每个及其确切的行号：“line 3511: `case VIRTIO_RING_F_INDIRECT_DESC`”，“line 3513: `case VIRTIO_RING_F_EVENT_IDX`”，等等。**仅从代码中提取此列表——不要从 REQUIREMENTS.md、CONTRACTS.md 或任何其他生成的工件复制。** 如果你无法为案例标签引用行号，则它不存在。

   (b) **列表 B（规范提取）**：列出在相关头文件、枚举或规范中定义的每个常量，这些常量应该被处理。

   (c) **差异**：比较这两个列表。对于列表 B 中的每个常量，将其标记为“FOUND (line NNN)”或“NOT IN CODE。” 报告任何定义但未处理的常量。

   **不要断言白名单“覆盖所有值”或“保留支持的位”而不执行此两列表比较。** AI 模型可靠地产生 switch/case 构造的完整性幻觉——模型看到函数，看到在其他地方定义的常量，并假设覆盖而不检查每个案例标签。这种幻觉最危险的形式是复制来自上游工件（如 REQUIREMENTS.md）的常量，而不是从代码中提取。在 v1.3.17 中，代码审查的“案例标签存在”列表与需求列表逐字相同——证明它是复制而不是提取的。机械检查与每个标签的行号是修复方法。

这五个区域必须作为标记的子部分出现在阶段 1 报告中。如果一个项目没有有意义的并发，请明确说明并记录原因，而不是省略该部分。根据需要添加项目特定的审查区域。

阶段 1 捕获 ~65% 的真实缺陷：竞态条件、空指针风险、资源泄漏、off-by-one 错误、类型不匹配——结构问题在代码中可见。

**阶段 2 — 需求验证。** 对于在第 1 阶段步骤 7 派生的每个可测试需求，检查代码是否满足它。对于每个需求，要么显示满足它的代码，要么具体解释为什么不满足。这是一个纯验证阶段——审查者的唯一工作是“代码满足此需求吗？”不是一般审查。不是寻找其他错误。只是验证。

**最小证据规则**：阶段 2 必须针对每个需求引用至少一个代码位置（文件:行或文件:函数）。像“REQ-003 到 REQ-012——由审查期间客户端路径满足”这样的笼统满足声明而没有每个需求的代码引用不满足阶段 2。如果两个或三个需求由同一个函数满足，请引用该函数一次并列出那些特定需求——但每个需求必须单独出现，并带有其自己的 SATISFIED/VIOLATED 裁决，而不是作为未验证范围的一部分。一个下级超过三个需求在单个引用下的组表明验证是表面的。目的是可追溯性——阅读阶段 2 的审查者应该能够从任何单个需求追溯到满足它的代码，而无需重新阅读整个代码库。

**枚举完备性声明需要机械证明。** 在评估涉及白名单、查找表、特性位集、处理器注册表或任何形式为“所有 X 都由 Y 覆盖”的声明时，审查者必须执行第一遍审查区域 5 中的双列表枚举检查：从代码中提取每个项目（带行号），从规范中提取每个项目，然后进行比较。**代码侧列表必须从源代码中新鲜提取——不要重用 REQUIREMENTS.md、CONTRACTS.md、代码审查提示或任何其他生成工件中的任何列表。** 如果代码侧列表与要求列表逐字匹配，则表明该列表是复制而不是提取的，必须重新执行检查。

不要根据阅读函数并相信它处理了所有内容就标记此类要求为 SATISFIED——这是此规则防止的具体幻觉模式。示例：一个要求说“传输功能白名单必须保留所有支持的环功能”。审查者阅读 `vring_transport_features()` 并看到它有一个 switch/case。正确的检查：提取每个 case 标签及其行号（`line 3511: INDIRECT_DESC`、`line 3513: EVENT_IDX`、...、`line 3527: default`），然后列出头文件常量，然后进行比较。幻觉：“白名单保留支持的位，包括 VIRTIO_F_RING_RESET”而没有检查 RING_RESET 实际上作为 case 标签出现。这个精确的失败模式在实践中多个版本中都有观察到——模型断言了常量的覆盖范围，而该常量在 switch 中不存在，并且在 v1.3.17 中，代码审查的“case 标签存在”列表是从要求中复制的，而不是从代码中提取的，导致三个独立的规范审查者继承了错误的声明。

第二遍捕获单个要求的违规行为——代码没有执行规范说明它应该执行的操作的情况。这发现了结构审查遗漏的 bug，因为存在的代码是正确的；bug 是缺失的或与规范不匹配的内容。

**第三遍——跨要求一致性。** 比较引用相同字段、常量、范围或安全策略的要求对。对于每一对，验证它们的约束是否相互一致。数值范围是否匹配位宽？安全策略是否传播到所有连接类型？一个文件中的验证边界是否与另一个文件中的编码限制一致？

第三遍捕获两个单独正确部分的代码在共享约束上存在分歧的矛盾。这些 bug 对结构审查和每个要求的验证都是不可见的，因为每个要求都是单独满足的——bug 只在比较它们时出现。这是捕获跨文件算术 bug 和设计差距的遍历，其中安全配置没有传播到所有连接路径的遍历。

**源代码边界规则：** 播客必须永不修改 `quality/` 目录之外的文件。所有源树更改——bug 修复、向项目自己的测试套件添加测试——必须表示为保存在 `quality/patches/` 下的 `git diff` 格式的补丁文件。这确保了原始源树保持不变，补丁是可审查的和可逆的，并且播客的发现与它审查的代码清晰分离。

**BUGS.md：** 在所有审查和审计阶段之后，生成 `quality/BUGS.md`——一个包含每个确认 bug 的完整重现细节的综合 bug 报告。对于每个 bug，包括：bug ID、来源（代码审查或规范审查）、文件：行号、描述、严重性、最小重现场景（什么输入或序列触发 bug）、预期与实际行为、对回归测试的引用和任何建议的修复补丁，以及 **规范依据**。

**BUGS.md — v1.5.3 BUG 记录字段（schemas.md §8）。** 每个 BUGS.md 条目（以及每个 `quality/writeups/BUG-NNN.md`）对应于写入 `quality/bugs_manifest.json` 的 BUG 记录。除了上述叙事约定之外，每个 BUG 还包含：

- `id` — `BUG-NNN` 零填充的三位数序列。
- `divergence_description` — 文档意图和代码行为之间差异的一段摘要。
- `documented_intent` — REQ / 规范语言的直接引用或接近释义。
- `code_behavior` — 代码实际做什么，带有 `file:line` 引用。
- `disposition` — schemas.md §3.2 中的枚举：`code-fix` | `spec-fix` | `upstream-spec-issue` | `mis-read` | `deferred`。必需，非空。不要发明新值。
- `disposition_rationale` — 一段解释为什么是这种情况而不是相邻情况（例如，为什么 `code-fix` 而不是 `upstream-spec-issue`，或者为什么 `spec-fix` 而不是 `mis-read`）的解释。公式化理由（“代码是错误的，因为规范说”）在理事会审查中失败。
- `req_id` — 单数。揭示差异的主要 REQ。如果一个 bug 看起来会影响多个 REQ，分成每个 REQ 一个 bug，共享根本原因，并在 `disposition_rationale` 中交叉链接（schemas.md §8.1）。不要将多个 REQ ID 混入一个条目中。
- `proposed_fix` — `disposition == "mis-read"` 除非必需。当 `fix_type` ∈ {`code`、`both`} 时为补丁形状；当 `fix_type == "spec"` 时为文本红线。对于 `mis-read` 记录，该字段是可选的，如果存在，则记录重新阅读（播客误解了什么以及如何建立正确的阅读），而不是已发布的更改。
- `fix_type` — schemas.md §3.4 中的枚举：`code` | `spec` | `both`。`disposition × fix_type` 的组合受 §3.4 中法律组合矩阵的约束（由 §10 不变量 #12 强制）。非法组合：`code-fix` × `spec`、`spec-fix` × `code`、`upstream-spec-issue` × `code`、`mis-read` × `both`。在编写记录之前查阅该矩阵——门会拒绝非法组合。

**差异框架（写稿声音，schemas.md v1.5.3）。** 缺陷是文档意图和代码实现之间的差异——不是关于代码是否“好”的判断。写稿的开头部分（摘要、规范引用、代码）是 `divergence_description`、`documented_intent` 和 `code_behavior` 的人为渲染。将它们写成并排的差异，而不是叙事。读者应该能够扫描 REQ/规范语言旁边的代码行为，并立即看到差距。对抗性语气（“代码是混乱的”）或标题中的价值判断（“混乱的拖车处理”）在框架中失败——一个 bug 是对差异的观察，而不是指控。

**什么构成确认 bug 的充分证据（关键）。** 一个证明特定行为违规的代码路径跟踪是确认 bug 的充分证据。你不需要执行请求级证据、运行测试或集成级重现来将发现从候选提升为确认。具体来说：

- 一个显示函数 A 调用函数 B，函数 B 做 X 但应该做 Y 的代码路径跟踪，带有文件：行号引用——**足以确认**。
- 通过枚举比较识别的缺失 case/分支（规范说 X 应该被处理，代码没有 X 的处理程序）——**足以确认**。
- 第二遍中识别的要求违规，其中代码明显没有实现指定行为——**足以确认**。
- 域知识发现，你可以从输入通过特定代码跟踪到错误输出——**足以确认**。

不要要求“执行请求级证据”或因为“它们需要运行时测试来区分实现选择与规范差距”而推迟发现。如果规范或文档说行为应该是 X，而代码明显产生 Y（可通过代码路径跟踪），那是一个确认的 bug——不是等待运行时验证的候选者。回归测试和 TDD 协议存在于确认后提供运行时证据，而不是确认前的先决条件。

**此规则存在的原因：** 在 v1.3.43 javalin 基准测试中，代码审查和分派都确定了 4 个合法的候选 bug，带有代码路径跟踪和要求违规，然后将它们全部降级，因为“最高置信度的项目仍然需要执行请求级证据”。这导致了一个代码库，其中以前的版本发现了 5 个确认的 bug。证据标准是在确认之前需要运行时证明，这是倒退的——播客的设计是先确认，然后用 TDD 证明。

**严重性校准：** 凭证泄露、身份验证绕过和注入类 bug 无论评估的可能性如何，始终为高严重性。跨信任边界暴露的授权头（例如，跨域重定向）是凭证泄露。当对与安全相关的严重性不确定时，默认为高。

**开发支架排除（确认任何安全类发现之前的早期过滤器）。** 上述严重性校准规则自动升级凭证泄露和身份验证绕过发现。在将任何此类发现确认为 bug 之前，应用此机械测试：

> **所审查的值是否包含自我说明的标记——诸如 `change-me`、`replace-me`、`placeholder`、`example`、`default`、`dummy`、`TODO`、`FIXME`、`your-secret-here`、`insert-` 或 `set-this-` 等明确告诉部署者要替换它的单词？**

如果是：**这不是一个 bug。** 不要记录它。自我说明的开发占位符是支架，不是缺陷——它的存在是为了使项目在没有配置的情况下在本地构建和运行。相同的逻辑适用于测试固定装置、示例配置、种子数据以及任何其名称或周围注释声明为非生产环境的值。

这是一个早期过滤器，在确认时捕获最明显的误报。第五阶段中的挑战门（见 `references/challenge_gate.md`）是捕获更微妙案例的更广泛机制——记录的特征差距、带有 WHY 注释的设计决策以及“预期行为”由审查者发明的发现。任何通过支架排除的安全类发现如果与自动触发模式匹配，在第五阶段仍将受到挑战门的处理。

**规范依据（每个 bug 必须强制字段）：** 引用建立预期行为的特定文档段落——收集到的文档文件名、章节/页码以及它定义的行为合同。如果没有收集到的文档涵盖该行为，请检查项目自己的注释、README 或 API 文档是否定义了它。如果预期的行为没有文档，将 bug 分类为“代码不一致”而不是“规范违规”，并在严重性评估中注明这一点。规范违规比代码不一致是一个更强的发现——这意味着代码与权威来源相矛盾，而不仅仅是代码看起来不对。这种区别在报告上游时很重要：维护者对“你的代码违反了你自己的规范的第 X.Y 节”的反应与“这看起来可能是一个 bug”的反应不同。

**补丁文件（每个确认的 bug 必须强制）：** 对于每个确认的 bug，生成：

- `quality/patches/BUG-NNN-regression-test.patch` — 一个 `git diff`，添加一个演示 bug 的测试。**这个补丁是强制的，不是可选的。** 它是 bug 存在的最强证据——独立于对修复的意见。没有回归测试补丁的确认 bug 是不完整的，并将导致 `quality_gate.py` 失败。在确认 bug 后立即生成此补丁，在转到下一个 bug 之前。

- `quality/patches/BUG-NNN-fix.patch`（可选但强烈鼓励）— 一个 `git diff`，包含建议的修复。对于单行或几行更改的 bug（例如，添加一个 case 标签、修复一个参数），生成修复补丁——这些是低工作量、高价值的。

**如何生成补丁文件。** 使用 `git diff` 格式。最简单的方法：直接编写统一差分作为补丁内容。回归测试补丁的示例：

```
--- /dev/null
+++ b/quality/test_regression_virtio.c
@@ -0,0 +1,15 @@
+// 由 Quality Playbook v1.5.6 生成
+// BUG-004：VIRTIO_F_RING_RESET 在 vring_transport_features() 中缺失的回归测试
+#include <assert.h>
+#include <string.h>
+...
```

对于修改现有源文件的修复补丁，使用 `--- a/path` / `+++ b/path` 格式并带有正确的行偏移。如果你无法确定确切的行偏移，生成补丁内容并注明“偏移近似”——近似补丁比没有补丁更有价值。

补丁必须可以干净地应用在原始源树上的 `git apply`。不要直接修改源树。

**补丁验证门（强制）：** 在将任何 bug 确认为带有修复补丁的确认 bug 之前，运行此门：

1. **应用测试：** `git apply --check quality/patches/BUG-NNN-regression-test.patch` — 必须退出 0。
2. **应用测试 + 修复：** `git apply --check quality/patches/BUG-NNN-fix.patch` — 必须退出 0（测试针对干净树，而不是回归测试应用的树，除非修复补丁依赖于回归测试）。
3. **编译检查：** 应用两个补丁后，运行项目的构建/编译命令（例如，`go build ./...`、`mvn compile`、`cargo check`、`tsc --noEmit`）。必须成功。

**临时工作树用于步骤 3。** 步骤 1–2 使用 `--check`（非破坏性）。步骤 3 需要实际应用补丁并编译，这会修改源树。为了遵守源代码边界规则（“永不修改 `quality/` 目录之外的文件”），在可丢弃的工作树中运行步骤 3：

```bash
git worktree add /tmp/qpb-patch-check HEAD --quiet
cd /tmp/qpb-patch-check
git apply quality/patches/BUG-NNN-regression-test.patch quality/patches/BUG-NNN-fix.patch
<compile command>
cd -
git worktree remove /tmp/qpb-patch-check --force
```

如果 `git worktree` 不可用（浅克隆、分离的 HEAD），使用 `git stash && git apply ... && <compile> && git checkout . && git stash pop` 作为后备，或者接受仅 `--check` 验证并注明限制。

**解释性语言的编译检查。** 编译命令因生态系统而异：

- **Go：** `go build ./...`
- **Rust：** `cargo check`
- **Java/Kotlin (Maven)：** `mvn compile -q`
- **Java/Kotlin (Gradle)：** `./gradlew compileJava compileTestJava -q`
- **TypeScript：** `tsc --noEmit`
- **Python：** `python -m py_compile <changed_files>` 用于语法，然后 `pytest --collect-only -q` 用于导入/发现验证
- **JavaScript (Node.js)：** `node --check <changed_files>` 用于语法；如果项目使用 ESLint，`npx eslint <changed_files>` 用于结构问题
- **JavaScript (Mocha/Jest)：** 以发现模式运行特定测试（`mocha --dry-run` 或 `jest --listTests`）以验证它加载时没有错误

如果项目语言没有编译/语法检查可行，请在补丁条目中记录这一点，并依赖 TDD 红阶段来捕获语法错误。

如果任何步骤失败，在记录 bug 为确认之前修复补丁。一个无法应用的损坏补丁的 bug 不是一个确认的 bug——它是一个具有损坏证据的假设。TDD 红绿循环不能在无法应用的补丁上运行，并且报告一个不可应用的补丁的 bug 会削弱与上游维护者的可信度。常见的补丁失败：截断的 hunks（缺少关闭大括号）、错误的行偏移（补丁生成针对修改的树而不是干净的树）以及生成的测试代码中的语法错误。

**修复补丁要求。** 每个确认的 bug 必须有：

- 一个通过上述验证门通过的 `quality/patches/BUG-NNN-fix.patch`，或者
- 在 BUGS.md 中提供明确的理由，解释为什么不提供修复补丁（例如，“修复需要超出补丁范围的架构更改”、“多个有效修复策略——推迟到维护者判断”、“bug 在上游依赖项中”）。

一个带有回归测试但没有修复补丁和没有正当理由的 Bug 是不完整的。回归测试证明了 Bug 的存在；修复补丁（或其缺失的正当理由）完成了证据链。没有修复补丁的 Bug 无法达到“TDD 验证（FAIL→PASS）”状态——它们仍然处于“已确认打开（xfail）”状态，直到提供修复。

**TDD 验证周期：** 每个带有修复补丁的已确认 Bug 都应经历红绿 TDD 周期（未修复代码上的测试失败，修复后通过）。这是通过 `quality/RUN_TDD_TESTS.md` 协议（文件 7）执行的，而不是在代码审查期间内联执行。该协议生成基于规范的测试，其中每个断言消息、变量名和注释都可以追溯到收集到的文档。

**所有三个阶段之后：** 合并发现。在 `quality/test_regression.*` 中编写回归测试以重现每个已确认的 Bug。使用与 `test_functional.*` 相同的测试框架——如果功能测试使用 pytest，回归测试也使用 pytest（带有 `@pytest.mark.xfail(strict=True)`）；如果功能测试使用 unittest，回归测试也使用 unittest（带有 `@unittest.expectedFailure`）。报告结果作为确认表（BUG CONFIRMED / FALSE POSITIVE / NEEDS INVESTIGATION）。有关完整三个阶段模板和回归测试协议，请参阅 `references/review_protocols.md`。

**回归测试跳过保护（强制）。** `quality/test_regression.*` 中的每个回归测试必须包含一个跳过/xfail 保护，以便在未修复的代码上运行完整测试套件不会产生意外失败。保护必须是框架的**最早的句法保护**——装饰器或注释，否则是测试体中的第一个可执行行。使用适当的语言机制：

- **Python (pytest):** `@pytest.mark.xfail(strict=True, reason="BUG-NNN: [description]")` — 放置在 `def test_...():` **上面的装饰器**，而不是函数体内。当 Bug 存在时，测试失败 → XFAIL（预期）。当 Bug 已修复但标记未移除时，测试通过 → XPASS → 严格模式使其失败，表示应移除保护。
- **Python (unittest):** `@unittest.expectedFailure` — 测试方法的装饰器。
- **Go:** `t.Skip("BUG-NNN: [description] — 修复后取消跳过")` — 测试函数内的第一行。注意：Go 的 `t.Skip` 完全隐藏测试（报告 SKIP，而不是 FAIL），其证据不如 Python 的 xfail 弱。这是 Go 测试原语的一个已知限制。
- **Java (JUnit 5):** `@Disabled("BUG-NNN: [description]")` — 测试方法的注释。
- **Rust:** `#[ignore]` 属性在测试函数上（标准的“默认套件中不运行”机制）。仅对表现为恐慌的 Bug 使用 `#[should_panic]`；仅对编译时 Bug 使用 `compile_fail` doctest 注释。
- **TypeScript/JavaScript (Jest):** `test.failing("BUG-NNN: [description]", () => { ... })`
- **TypeScript/JavaScript (Vitest):** `test.fails("BUG-NNN: [description]", () => { ... })`
- **JavaScript (Mocha):** `it.skip("BUG-NNN: [description]", () => { ... })` 或 `this.skip()` 在测试体内用于条件跳过。

当 Bug 已修复（修复补丁永久应用）时，移除跳过保护并更新 BUG 追踪器关闭状态从“已确认打开”更改为“已修复（测试通过）”。跳过保护消息必须引用 Bug ID 和修复补丁路径，以便遇到跳过测试的人确切知道如何解决它。

**源代码检查测试必须执行（无 `run=False`）。** 验证源文件结构的回归测试——函数体内的字符串存在、case 标签存在、枚举提取、生成代码形状检查——是安全的、确定性的和快速的。它们读取存储库文件并执行字符串匹配。对于这些测试，使用 `@pytest.mark.xfail(strict=True)` 并启用执行。**不要使用 `run=False`**，除非测试会修改外部状态、挂起或需要不可用的基础设施。带有 `run=False` 的源代码检查测试是最糟糕的状态：正确的检查存在但处于非活动状态。在 v1.3.18 中，BUG-004 的回归测试（`test_bug_004_transport_feature_whitelist_keeps_ring_reset`）包含正确的断言 `assert "case VIRTIO_F_RING_RESET:" in func` 但标记为 `run=False`——因此测试从未执行，断言从未触发，尽管测试套件“通过”，Bug 仍然未被检测到。当 `xfail(strict=True)` 测试实际执行并失败时，测试套件将其报告为 XFAIL（预期失败）——这是正确的行为，不是套件失败。

**TDD 红绿交互与跳过保护。** 在 TDD 验证周期中，红绿阶段必须暂时绕过跳过保护以实际执行测试。协议应指示代理：

- **红阶段（从不跳过）：** 移除或禁用跳过/xfail 保护，然后在未修复的代码上运行测试。它必须失败。记录结果后重新启用保护。**红阶段对每个已确认的 Bug 都是强制性的，即使没有修复补丁。没有红阶段证据的 Bug 是未验证的——不要在没有失败的红色运行的情况下记录 `verdict: "skipped"`。如果由于文档原因（编译失败、环境不可用）红阶段无法执行，请记录 `red_phase: "error"` 并在 `notes` 中解释。**
- **绿阶段：** 移除或禁用保护，应用修复补丁，运行测试。它必须通过。如果修复将被回滚，则重新启用保护。**如果没有修复补丁，请记录 `green_phase: "skipped"`——但红阶段必须仍然已运行。**
- **TDD 周期后：** 保护保留在提交的回归测试文件中。只有在修复合并到源树时才会永久移除。

**TDD 执行强制（强制）。** 回归测试必须在 TDD 验证周期中实际执行，而不仅仅是作为补丁文件生成。对于每个已确认的 Bug，红阶段测试运行必须在 `quality/results/BUG-NNN.red.log` 生成捕获测试输出的日志文件。绿阶段（如果存在修复补丁）必须生成 `quality/results/BUG-NNN.green.log`。每个日志文件的第一行必须是状态标签：`RED`（测试按预期失败）、`GREEN`（修复后测试通过）、`NOT_RUN`（测试无法执行——附解释）或 `ERROR`（测试基础设施失败——附解释）。

**语言感知测试执行命令。** 使用项目的原生测试运行器来执行回归测试。检测项目语言并使用适当的命令：

- **Go:** `go test -v -run TestBugNNN ./path/to/package`
- **Python (pytest):** `python -m pytest -xvs quality/test_regression.py::test_bug_nnn`
- **Python (unittest):** `python -m unittest quality.test_regression.TestRegression.test_bug_nnn`
- **Java (Maven + JUnit):** `mvn test -pl module -Dtest=RegressionTest#testBugNnn`
- **Java (Gradle + JUnit):** `./gradlew test --tests RegressionTest.testBugNnn`
- **Rust:** `cargo test bug_nnn -- --nocapture`
- **TypeScript/JavaScript (Jest):** `npx jest --verbose --testNamePattern="BUG-NNN"`
- **TypeScript/JavaScript (Vitest):** `npx vitest run --reporter=verbose --testNamePattern="BUG-NNN"`
- **C (kernel/make-based):** 源代码检查通过 shell 脚本（对源文件进行 grep/awk）——记录脚本输出。

如果项目使用上述未列出的语言或测试框架，请使用项目已使用的任何测试运行器（检查 `Makefile`、`package.json`、`build.gradle`、`Cargo.toml`、`go.mod`、`setup.py`、`pyproject.toml` 等）并调整模式。如果没有测试运行器可用或语言运行时未安装，请记录 `NOT_RUN` 并附上解释——不要完全跳过日志文件。

**日志捕获格式。** 每个 `BUG-NNN.red.log` 和 `BUG-NNN.green.log` 必须遵循此格式：
```
RED
--- 测试输出为 BUG-NNN 红阶段 ---
命令：[运行的确切命令]
退出代码：[退出代码]
[测试执行的完整 stdout/stderr]
```

第一行的状态标签（`RED`、`GREEN`、`NOT_RUN`、`ERROR`）是机器可读的——`quality_gate.py` 将检查其存在。当测试运行器不可用（例如，C 项目中内核构建环境不存在）时，`NOT_RUN` 状态是可以接受的，但日志文件必须存在并解释为什么无法执行测试。

**现成 TDD 日志模板。** 对于每个已确认的 BUG-NNN，执行此序列（根据上述表格调整测试命令）：

```bash
# ── 红阶段：回滚修复，运行测试，预期 FAIL ──
git apply -R quality/patches/BUG-NNN-fix.patch 2>/dev/null   # 如果已应用，则回滚修复
TEST_CMD="python -m pytest -xvs quality/test_regression.py::test_bug_nnn"  # 根据语言调整
OUTPUT=$($TEST_CMD 2>&1); EXIT=$?
printf 'RED\n--- 测试输出为 BUG-NNN 红阶段 ---\n命令： %s\n退出代码： %d\n%s\n' \
  "$TEST_CMD" "$EXIT" "$OUTPUT" > quality/results/BUG-NNN.red.log

# ── 绿阶段：应用修复，运行测试，预期 PASS ──
git apply quality/patches/BUG-NNN-fix.patch
OUTPUT=$($TEST_CMD 2>&1); EXIT=$?
printf 'GREEN\n--- 测试输出为 BUG-NNN 绿阶段 ---\n命令： %s\n退出代码： %d\n%s\n' \
  "$TEST_CMD" "$EXIT" "$OUTPUT" > quality/results/BUG-NNN.green.log
```

为每个已确认的 Bug 运行此命令。如果测试运行器不可用，请创建带有 `NOT_RUN` 在第一行的日志文件并附上解释。不要跳过此步骤——TDD 日志关闭门在第五阶段会阻止完成，如果日志缺失。

**TDD 执行门。** 在第五阶段的终端门之前，验证 `quality/BUGS.md` 中的每个已确认 Bug 是否存在对应的 `quality/results/BUG-NNN.red.log`。没有红阶段日志的 Bug 是不完整的——回归测试补丁存在但从未被证明可以检测到 Bug。此门存在是因为 v1.3.45 基准测试显示大多数存储库生成回归测试补丁但从未执行它们，导致 TDD 裁决未验证。

### 文件 4: `quality/RUN_INTEGRATION_TESTS.md`

**阅读 `references/review_protocols.md`** 获取模板。

必须包括：安全约束、预飞行检查、具有特定通过标准的测试矩阵、执行 UX 部分、结构化报告格式。涵盖快乐路径、跨变体一致性、输出正确性和组件边界。

**用例可追溯性（强制）。** 测试矩阵必须包括一个**用例可追溯性列**。每个集成测试组必须：

1. **映射到一个用例**——命名它验证的用例（例如，UC-03）并描述测试如何执行该用例的用户结果。这些是主要的集成测试——它们验证用例中描述的端到端行为实际上是否工作。

2. **标记为基础设施**——不映射到用例的测试（构建验证、竞争检测、兼容性检查、现有测试套件回归保护）必须在可追溯性列中明确标记为 `[Infrastructure]`。它们有价值，但不计入用例覆盖率。

生成测试矩阵后，检查：REQUIREMENTS.md 中的每个用例是否至少有一个映射到它的集成测试？如果没有，请将未覆盖的用例标记为差距。映射到用例的集成测试应测试用例中描述的**端到端行为**——而不仅仅是运行恰好触及相同代码路径的现有单元测试。例如，如果用例说“开发人员身份验证并跟随重定向而不泄露秘密”，集成测试应执行跨域的重定向并带有身份验证标头并验证它们被剥离——而不是仅运行 `pytest -k auth`。

**按用例组拆分（强制）。** 每个集成测试组最多映射到**2 个用例**。映射到 3+ 用例的组过于粗略——当测试失败时，它无法区分哪个用例失败。如果单个测试命令（例如，`mvn test`、`go test ./...`）会执行多个用例，请将其拆分为单独的组，并使用有针对性的测试选择器（`-Dtest=`、`-run`、`-k`、`--tests`、`-- test_name` 等），以便每个组隔离 1–2 个用例。覆盖一个用例组的所有用例的命令是明确禁止的——当失败发生时，它们不提供诊断价值。

**无选择器回退。** 如果项目的测试框架无法以所需的粒度选择测试（例如，一个没有标签/过滤支持的庞大测试套件），请在集成协议中记录此限制并使用最可行的命令。记录该组覆盖的用例以及为什么无法进一步拆分。**单个命令的项目必须仍然使用分组 JSON 模式**——将命令包装在一个组中，并覆盖该命令执行的 `use_cases` 列表。命令的平面列表永远不会是 `groups[]` 结构的有效替代品。

**预飞行命令验证（强制）。** 在最终确定 `RUN_INTEGRATION_TESTS.md` 之前，验证每个组的测试命令是否实际发现并运行测试。使用框架的 dry-run 或列表模式进行确认：

- **Python:** `pytest --collect-only -q <selector>` — 必须列出至少一个测试
- **Go:** `go test -list "." <package>` — 必须列出至少一个测试名
- **Java/Kotlin:** `mvn -Dtest=<selector> test -pl <module> --batch-mode -DfailIfNoTests=true`
- **TypeScript (Vitest):** `vitest list <file> --config <config>` — 必须列出至少一个测试
- **TypeScript (Jest):** `jest --listTests <pattern>` — 必须列出至少一个文件
- **Rust:** `cargo test <selector> -- --list` — 必须列出至少一个测试
- **JavaScript (Mocha):** `mocha --dry-run <file>` — 必须列出至少一个测试

如果 dry-run 退出为“未找到测试”、“未找到测试文件”或零测试计数，请在记录组之前修复选择器。常见修复：添加 `--config` 或 `--root` 标志，使用文件路径而不是 `-t` 名称模式，将正则表达式模式锚定到正确的包。不要记录其命令无法发现测试的组——它将产生 `covered_fail` 结果，将选择器错误掩盖为代码错误。

如果 dry-run 失败为**构建错误**（编译失败、导入错误、缺失依赖、测试设置异常）而不是“未找到测试”，请在组的 `notes` 字段中记录失败为 `"pre_flight_error": "environment"`，并且不要尝试修复选择器。预飞行期间的环境错误需要环境设置，而不是选择器更改。

**基础设施组定义。** 单个 `[Infrastructure]` 组可以覆盖构建验证、竞争检测、静态分析和平台兼容性检查，而无需用例映射。基础设施测试验证构建工具链和平台支持，而不是用户可观察的行为。基础设施组：

- 不计入用例覆盖率（用例覆盖率检查会忽略它们）
- 必须包含一行解释其验证的内容
- 不能用于将广泛的用户工作流命令重新标记为避免拆分——如果测试执行了用例中描述的用户面行为，则必须映射到该用例，无论测试如何组织

**所有命令必须使用相对路径。** 生成的协议应在顶部包含一个“工作目录”部分，说明所有命令都从项目根目录使用相对路径运行。永远不要生成 `cd` 到绝对路径的命令——当协议从不同的机器或目录运行时，这会中断。使用 `./scripts/`、`./pipelines/`、`./quality/` 等。

**包含执行用户体验（Execution UX）部分。** 当有人告诉AI代理“运行集成测试”时，代理需要知道如何展示其工作。协议应指定三个阶段：(1) 在运行任何操作之前，将计划显示为编号表格；(2) 在每个测试运行时报告单行进度更新（`✓`/`✗`/`⧗`）；(3) 显示一个包含通过/失败计数和建议的摘要表格。参见`references/review_protocols.md`部分的“执行用户体验”获取模板和示例。没有这个，代理会输出原始输出或保持沉默——两者都无济于事。

**结构化输出（强制要求）。** 协议必须指示代理在Markdown报告旁边生成机器可读的结果，使用**JUnit XML**进行测试执行，并使用**侧边栏JSON**进行QPB特定的元数据。

**JUnit XML输出：** 每个测试组应使用框架的原生JUnit XML报告器运行：
- Python: `pytest --junitxml=quality/results/integration-group-N.xml`
- Go: `gotestsum --junitxml quality/results/integration-group-N.xml -- -run "TestPattern"`
- Java/Kotlin: 将Surefire XML报告复制到`quality/results/`
- TypeScript: `jest --reporters=jest-junit`，并设置`JEST_JUNIT_OUTPUT_DIR=quality/results/`
- Rust: `cargo test 2>&1 | cargo2junit > quality/results/integration-group-N.xml`（如果可用）

如果JUnit XML报告器不可用，则跳过XML，并在侧边栏JSON中注明`"junit_available": false`。

**侧边栏JSON：** 通过复制下面的模板并填写值来生成`quality/results/integration-results.json`。不要编造字段、重命名键或重构模式。一个不包含`groups`数组的命令扁平列表是**无效**的——即使项目通过单个命令运行所有测试，也要将其包装在一个组中。

```json
{
  "schema_version": "1.1",
  "skill_version": "<当前技能版本>",
  "date": "YYYY-MM-DD",
  "project": "<项目名称>",
  "recommendation": "SHIP",
  "groups": [
    {
      "group": 1,
      "name": "核心路由调度",
      "use_cases": ["UC-01", "UC-02"],
      "result": "pass",
      "tests_passed": 5,
      "tests_failed": 0,
      "junit_file": "integration-group-1.xml",
      "junit_available": true,
      "notes": ""
    }
  ],
  "summary": {
    "total_groups": 9,
    "passed": 8,
    "failed": 1,
    "skipped": 0
  },
  "uc_coverage": {
    "UC-01": "covered_pass",
    "UC-02": "covered_pass",
    "UC-03": "not_mapped"
  }
}
```

**必需的顶层字段：** `schema_version`、`skill_version`、`date`、`project`、`recommendation`、`groups`、`summary`、`uc_coverage`。如果输出中缺少这些字段中的任何一个，结果将不符合规范。

**无效示例（不要输出这些）：**
- 一个扁平的`"results": [{"command": "go test ./...", "result": "pass"}]`——这不是分组模式。
- 一个使用`"commands_run"`而不是`"groups"`的模式——键名错误。
- 一个缺少`"uc_coverage"`的模式——REQUIREMENTS.md中的每个用例都必须出现。
- 一个使用`"use_case_traceability"`而不是`"use_cases"`的模式——字段名错误。

有效的`result`值：`"pass"`、`"fail"`、`"skipped"`、`"error"`。有效的`recommendation`值：`"SHIP"`（所有组通过）、`"FIX BEFORE MERGE"`（非阻塞组中的失败）、`"BLOCK"`（关键组中的失败）。`uc_coverage`部分将REQUIREMENTS.md中的每个用例映射到以下一个值：`"covered_pass"`（至少一个映射组通过）、`"covered_fail"`（映射的组但全部失败）或`"not_mapped"`（没有集成测试组映射到此用例）。`covered_fail`和`not_mapped`之间的区别很重要：前者表示测试存在但代码有错误；后者表示测试缺失。

运行器脚本和CI工具应读取侧边栏JSON以获取结果，而不是在Markdown报告中使用grep。这消除了grep-based计数从匹配的文本中产生错误数字的一类错误。

**运行后验证（强制要求）。** 在写入`integration-results.json`后，重新打开文件并验证：(1) 每个必需的顶层字段都存在，(2) 每个`groups[]`条目都有`group`、`name`、`use_cases`、`result`和`notes`，(3) 所有`result`和`recommendation`值仅使用上面列出的允许的枚举值，(4) `uc_coverage`映射了REQUIREMENTS.md中的每个用例，(5) 没有额外的未记录的根键存在。如果任何检查失败，请在继续之前修复文件。

**此协议必须执行真实的依赖项。** 如果项目与API、数据库或外部服务交互，集成测试协议针对这些服务运行真实的端到端执行——而不仅仅是本地验证检查。根据项目的实际执行模式和外部依赖项设计测试矩阵。在探索和构建过程中查找API密钥、提供者抽象和现有的集成测试脚本。

**从代码中而不是通用检查中导出质量门禁。** 在探索过程中读取验证规则、模式枚举和生成逻辑。将它们转换为每个管道的质量检查，具有特定字段和可接受值范围。“所有单元验证”是不够的——协议必须验证特定领域的正确性。

**脚本并行性，而不仅仅是描述它。** 分组运行，以便独立的执行（不同的提供者）可以并发运行。包括带有`&`和`wait`的实际bash命令。每次运行一个提供者，以避免速率限制。

**将单元计数校准到项目。** 读取`chunk_size`或等效配置。使用足够的单元来跨越至少2个块，并足够验证分布检查。通常为10-30个单元用于集成测试。

**深度运行后验证。** 不要在“进程完成”时停止。验证日志文件、清单状态、输出数据存在、样本记录内容以及任何现有的质量检查脚本——对于每个运行。

**查找和使用现有的验证工具。** 搜索现有的验证输出质量的脚本（例如，`integration_checks.py`、验证脚本、质量门禁函数）。如果它们存在，从协议中调用它们。如果项目有TUI或仪表板，请在运行后清单中包括TUI验证命令（例如，`--dump`标志）。

**在编写质量门禁之前构建字段参考表。** 这是协议准确性的最重要步骤。AI模型即使阅读了模式后也会自信地写出错误的字段名——`document_id`变成`doc_id`，`sentiment_score`变成`sentiment`，`float 0-1`变成`int 0-100`。解决方法是程序性的：**在编写每个表格行之前立即重新阅读每个模式文件。** 不要依赖你在对话中读到的内容——你对字段名的记忆在数千个token后会漂移。从文件内容逐字符复制字段名。包括每个模式的所有字段（如果模式有8个字段，表格有8行）。参见`references/review_protocols.md`部分的“字段参考表”获取完整过程和格式。不要跳过这一步——它防止了最常见的协议不准确性。

### 文件5：`quality/RUN_SPEC_AUDIT.md` — 三人理事会

**阅读`references/spec_audit.md`** 获取完整协议。

三个独立的AI模型对代码进行规范审计。为什么是三个？因为每个模型都有不同的盲点——在实践中，不同的审计员会捕获不同的问题。交叉引用可以捕获任何单个模型遗漏的问题。

协议定义了：一个可复制粘贴的审计提示符，带有约束，项目特定的审查区域，一个分诊过程（按置信度级别合并发现），以及修复执行规则（按子系统小批量，而不是巨型提示）。

**次要强调透镜：** 可选地为每个审计模型分配一个次要强调——例如，一个从输入验证开始，一个从资源生命周期开始，一个从并发开始。每个模型仍然执行一个完整的独立审计；强调会偏向注意力，而不会限制覆盖范围。不要将模型划分为按错误类别划分的独立所有权。

**少数派发现规则：** 在分诊过程中，任何只有一个审计员标记的发现（少数派发现）都需要重新调查——阅读特定的代码位置并做出明确的`CONFIRMED`/`FALSE-POSITIVE`决定，而不是默认丢弃。少数派发现更有可能被两个模型遗漏的真实错误。

**分诊不能提高证据标准高于代码路径分析。** 分诊步骤确认或拒绝发现——它不会推迟到运行时证据。如果一个发现包括一个代码路径跟踪，显示行为违规（函数调用、缺失分支、带有文件:行引用的错误返回值），分诊应确认它。不要将代码路径跟踪的发现降级为“候选”或“需要运行时验证”。TDD协议（第5阶段）在确认后提供运行时证据。参见BUGS.md部分“什么构成确认错误足够证据”的完整证据标准。

**代码审查与规范审计冲突：** 如果代码审查和规范审计对同一发现意见不一致，规范审计发现不会自动正确。部署验证探针——阅读特定的代码位置并确定哪个评估是准确的。在BUG跟踪器中记录解决方案。任何规范审计员未标记的代码审查BUG仍然被确认，但在关闭之前应使用定向探针进行验证。

**验证探针必须产生可执行的证据。** 当分诊步骤通过验证探针确认或拒绝发现时，仅有的推理是不够的。探针必须产生一个机械证明决定的测试断言：

- **对于拒绝**（发现是误报）：编写一个通过断言，证明发现是错误的。示例：如果拒绝“函数X缺少空检查”，编写`assert "if (ptr == NULL)" in source_of("X"), "X在行NNN有空检查"`。如果你不能编写一个通过断言来证明你的拒绝，**不要拒绝发现**——将其升级为确认或标记为手动审查。

- **对于确认**（发现是真实错误）：编写一个失败的断言（预期失败），证明错误存在。示例：如果确认“RING_RESET缺失于开关”，编写`assert "case VIRTIO_F_RING_RESET:" in source_of("vring_transport_features"), "RING_RESET应该在开关中但不存在"`。

- **每个断言必须引用确切的行号**以引用它所参考的证据。不是“行3527-3528”而是“行3527: `default:`”——显示该行实际包含的内容。没有行号引用的断言是不充分的。

**为什么存在此规则：** 在v1.3.16 virtio测试中，分诊正确收到了一个少数派发现，即`VIRTIO_F_RING_RESET`缺失于开关/情况白名单。分诊执行的“验证探针”声称行3527-3528“明确保留VIRTIO_F_RING_RESET”——但那些行实际上包含`default:`分支。分诊产生了符合代码的幻觉。如果它被要求编写`assert "case VIRTIO_F_RING_RESET:" in source`，断言将失败，暴露了幻觉。要求拒绝的可执行证据使幻觉的拒绝自我挫败：模型无法为不在代码中的内容编写通过断言。

**分诊证据必须写入磁盘。** 验证探针断言必须出现在磁盘上的一个文件中——要么追加到`quality/mechanical/verify.sh`，要么写入专用的`quality/spec_audits/triage_probes.sh`。在分诊报告中描述的断言但从未写入可执行文件中的断言不是可执行证据。门禁检查分诊输出中探针断言的存在；一个分诊报告说“验证探针确认……”而没有在可执行文件中对应断言的分诊报告是不符合规范的。这防止了模型叙述探针*会*显示什么而没有实际运行的模式失败模式。

### 文件6：`AGENTS.md`（由协调器生成；你在第2阶段*不*编写此文件）

**v1.5.4合同：`AGENTS.md`是在第6阶段成功后由`bin/run_playbook.py`生成的，*不是*你在第2阶段编写。** 协调器的`_safe_write_agents_md`辅助函数使用你在第2阶段生产的`quality/`工件和第6阶段门禁结果作为输入，将文件写入**目标存储库根目录**（`<target>/AGENTS.md`，不是`quality/AGENTS.md`）。生成器在第一个非空行的开头带有`<!-- generated by QPB v… -->`哨兵，以便后续运行检测QPB管理的副本。

**你（第2阶段LLM）必须*不*做：**

1. **不要创建`<target>/AGENTS.md`。** 协调器拥有它。从第2阶段创建它将与协调器的幂等再生路径冲突，并且可以被源未更改的不变量标记。
2. **不要修改现有的`<target>/AGENTS.md`。** 如果目标存储库根目录中存在一个缺少QPB哨兵的，它是操作员编写的——不要动它（协调器将使用`_safe_write_agents_md`的`"preserved"`结果保留它，每个结果都会发出警告）。如果它带有QPB哨兵，协调器将在第6阶段后再生它；你在运行中途编辑它没有帮助。
3. **不要编写`quality/AGENTS.md`。** 那不是合同；AGENTS.md位于存储库根目录，不在`quality/`下。

如果你发现自己想要“向现有的AGENTS.md添加质量文档部分”——停止。协调器会为你做这件事，使用第6阶段门禁验证的规范路径。你的第2阶段交付物是`quality/`工件和nothing else。

**此错误修复防止了在2026-04-30出现的引导测试失败模式：** 第2阶段LLM阅读了v1.5.3时代的“如果`AGENTS.md`已经存在，更新它”指令在此确切部分，将质量文档部分附加到项目的根AGENTS.md，并触发了源未更改的不变量——中止运行并丢弃了20分钟的第2阶段工作。

### 文件7：`quality/RUN_TDD_TESTS.md` — TDD验证协议

此协议在代码审查和规范审计确认错误并生成修复补丁后执行。它为每个确认的错误运行红色-绿色TDD周期：未修复的代码上测试失败，应用修复，测试通过。

**为什么需要一个单独的协议？** 代码审查发现错误并编写带有`xfail`标记的回归测试。TDD协议取那些测试并证明它们实际上检测了错误——以及修复确实修复了它。这比“我们发现了一个错误并编写了一个测试”更强烈的声明。“这是一个测试，它在没有补丁的情况下失败，在它存在时通过。”当报告错误上游时，这种区别很重要：维护者更信任一个FAIL→PASS演示而不是错误描述。

生成的协议必须包括：

1. **基于规范的测试要求。** 对于`quality/BUGS.md`中的每个错误，协议指示代理：
   - 读取错误的**规范基础**字段以识别定义预期行为的文档段落
   - 在引用的章节读取收集到的文档（来自`reference_docs/`或项目的自己的文档）
   - 使用**来自规范的术语**编写测试断言——变量名、常量、函数名和断言消息应回应用户术语，而不是代码的内部命名
   - 在每个测试中包含一个注释块，引用：要求ID（来自REQUIREMENTS.md）、错误ID（来自BUGS.md）和规范段落（文档名、章节和≤15个字的预期行为合同）

2. **红色-绿色执行步骤。** 对于每个带有修复补丁的错误：
   - **红色：** 运行回归测试针对未修复的源。它必须失败。如果它通过，测试没有检测到错误——使用规范基础重写它以了解要断言的行为。
   - **绿色：** 应用修复补丁（`git apply quality/patches/BUG-NNN-fix.patch`），运行相同的测试。它必须通过。
   - **记录：** 在BUG跟踪器中记录两个结果，关闭状态为“TDD验证（FAIL→PASS）”。

3. **框架适配**。协议必须检测项目的测试框架并生成符合规范的测试：
   - **具有测试基础设施的项目**（pytest、JUnit、Go testing、Jest、cargo test等）：使用项目自身的框架编写测试，遵循探索过程中发现的现有测试约定。
   - **没有测试基础设施的项目**（例如Linux内核、嵌入式C）：使用`sed`提取目标函数，编写一个自包含的C测试文件，包含最少的类型适配层，直接编译和运行。在测试文件的头部注释中包含提取命令，使其自文档化。

4. **上游报告格式**。对于每个通过TDD验证的bug，生成一个可直接发送的报告块，包含：
   - 一句话描述，引用违反的规范部分
   - FAIL→PASS的输出（可复制粘贴的终端会话）
   - 测试文件（作为附件或内联）
   - 修复补丁（作为附件或内联）

5. **可追溯性表格**。协议生成`quality/TDD_TRACEABILITY.md`文件，用于映射：

   | Bug ID | Requirement ID | Spec Doc | Spec Section | Behavioral Contract | Test File:Function | Red Result | Green Result |
   |--------|---------------|----------|-------------|--------------------|--------------------|------------|--------------|

   每一行必须完全填充。没有规范文档条目的bug是代码不一致，而不是规范违规——在表格中注明这一点，并相应调整上游报告语言。

6. **结构化输出（强制）**。协议必须在Markdown报告旁边生成机器可读的结果。使用**JUnit XML**表示测试执行结果，使用**侧车JSON**文件表示QPB特定的元数据，JUnit XML无法表示的内容。

   **JUnit XML输出**：对于每个红绿阶段，使用框架的原生JUnit XML输出标志运行测试：
   - Python: `pytest --junitxml=quality/results/tdd-red-BUG-NNN.xml`
   - Go: `gotestsum --junitxml quality/results/tdd-red-BUG-NNN.xml -- -run TestRegression_BUG_NNN`
   - Java/Kotlin: Maven Surefire报告会自动生成在`target/surefire-reports/`；将相关XML复制到`quality/results/`
   - Rust: `cargo test --test regression 2>&1 | cargo2junit > quality/results/tdd-red-BUG-NNN.xml`（如果cargo2junit可用；否则跳过Rust的XML）
   - TypeScript: `jest --reporters=default --reporters=jest-junit` with `JEST_JUNIT_OUTPUT_DIR=quality/results/`

   如果框架的JUnit XML报告器不可用或需要缺失的依赖项，则跳过该语言的XML输出，并在侧车JSON中注明`"junit_available": false`。不要因为缺失XML工具而使TDD运行失败。

   **侧车JSON（严格模式强制）**：通过复制下面的模板**逐字**并填写值来生成`quality/results/tdd-results.json`。不要发明字段、重命名字段或重构模式。模板就是模式——任何偏差（额外键、缺失键、重命名字段、重构嵌套）都会使输出不符合规范。先将模板复制到编辑器中，然后填写值。不要从记忆中编写JSON。

   ```json
   {
     "schema_version": "1.1",
     "skill_version": "<当前技能版本>",
     "date": "YYYY-MM-DD",
     "project": "<项目名称>",
     "bugs": [
       {
         "id": "BUG-001",
         "requirement": "REQ-003",
         "red_phase": "fail",
         "green_phase": "pass",
         "verdict": "TDD verified",
         "regression_patch": "quality/patches/BUG-001-regression-test.patch",
         "fix_patch": "quality/patches/BUG-001-fix.patch",
         "fix_patch_present": true,
         "patch_gate_passed": true,
         "writeup_path": "quality/writeups/BUG-001.md",
         "junit_red": "tdd-red-BUG-001.xml",
         "junit_green": "tdd-green-BUG-001.xml",
         "junit_available": true,
         "notes": ""
       }
     ],
     "summary": {
       "total": 6,
       "verified": 4,
       "confirmed_open": 1,
       "red_failed": 1,
       "green_failed": 0
     }
   }
   ```

   **必需的顶层字段**：`schema_version`、`skill_version`、`date`、`project`、`bugs`、`summary`。**每个bug必需字段**：`id`、`requirement`、`red_phase`、`green_phase`、`verdict`、`fix_patch_present`、`writeup_path`。如果任何必需字段缺失，结果将不符合规范。**可选的每个bug字段**（在上述模板中显示但未进行门禁检查）：`regression_patch`、`fix_patch`、`patch_gate_passed`、`junit_red`、`junit_green`、`junit_available`、`notes`。当数据可用时包含这些字段；否则不包含也不会受到惩罚。

   **必需的摘要子键**：`summary`对象必须包含以下键：`total`、`verified`、`confirmed_open`、`red_failed`、`green_failed`。这五个都是必需的——省略任何键（尤其是`red_failed`或`green_failed`）会使摘要不符合规范。

   **规范补丁文件名**：回归测试补丁必须命名为`BUG-NNN-regression-test.patch`。修复补丁必须命名为`BUG-NNN-fix.patch`。门禁脚本匹配这些确切模式——创意变体如`BUG-001-regression.patch`或`BUG-001-test.patch`将不会被计数。

   **日期字段**：使用此会话的实际日期（例如`"2026-04-12"`），而不是模板占位符`"YYYY-MM-DD"`。门禁验证日期是有效的ISO 8601日期，并拒绝占位符字符串和未来日期。

   **无效示例（不要生成这些）**：
   - `"runs": [{"phase": "red", "command": "...", "result": "4 xfailed"}]`——这是一个扁平的runs数组，而不是bug索引的`"bugs"`模式。
   - 一个带有ad-hoc根键的模板，如`"generated"`、`"scope"`、`"status"`、`"testsRun"`——这些不是标准模式字段。
   - `"verdict": "skipped"`——此值已弃用；使用`"confirmed open"`与`red_phase: "fail"`和`green_phase: "skipped"`。
   - 根部缺少`"schema_version"`——每个tdd-results.json必须包含此字段。

   有效`verdict`值：`"TDD verified"`（FAIL→PASS）、`"red failed"`（测试在未修复的代码上通过——测试未检测到bug）、`"green failed"`（修复后测试仍然失败——修复不完整或补丁损坏）、`"confirmed open"`（红阶段运行并确认了bug，没有修复补丁）、`"deferred"`（TDD在此环境中无法执行——使用`notes`字段解释原因）。**不要使用`"skipped"`作为verdict**——每个确认的bug都必须有红阶段结果。一个`verdict: "confirmed open"`的bug必须具有`red_phase: "fail"`（红运行并确认了bug）和`green_phase: "skipped"`（没有可应用的修复）。有效的`red_phase`/`green_phase`值：`"fail"`、`"pass"`、`"error"`（编译/应用失败）、`"skipped"`（仅绿——红从不跳过）。`patch_gate_passed`字段记录补丁验证门禁（应用检查+编译）是否成功——如果门禁失败并修复了补丁，则为`false`；如果不存在修复补丁，则为`null`。`writeup_path`字段指向每个bug的写文件（见下文“Bug写up生成”）——如果为该bug未生成写up，则为`null`。

   运行脚本和CI工具应从侧车JSON中读取通过/失败计数，而不是从Markdown报告中grep。

   **写up后验证（强制）**。在写入`tdd-results.json`后，重新打开文件并验证：(1) 每个必需的顶层字段都存在，(2) 每个必需的每个bug字段都在每个`bugs[]`条目中存在，(3) 所有`verdict`、`red_phase`和`green_phase`值仅使用上面列出的允许的枚举值，(4) 不存在额外的未记录根键。如果任何检查失败，请在继续之前修复文件。这一步捕获最常见的失败模式：代理从记忆中重新表述模式而不是复制模板，产生看似合理但不符合规范的结果。

**TDD artifact closure gate（强制）**。如果`quality/BUGS.md`包含任何确认的bug，`quality/results/tdd-results.json`是强制性的——不是可选的。如果任何bug有红阶段结果（无论TDD验证还是确认打开），`quality/TDD_TRACEABILITY.md`也是强制性的。零bug仓库可以省略这两个文件。确认bug但未生成tdd-results.json的运行是不完整的——阶段不能关闭。对于TDD无法执行（环境阻止、没有测试基础设施）的仓库，生成tdd-results.json，`verdict: "deferred"`，并在`notes`字段中解释原因（例如`"environment_blocked: missing workspace Cargo.toml"`，`"no_test_infrastructure: kernel C code without userspace harness"`）。延迟verdict使差距可见，而不是沉默地省略文件。

**执行UX**：与集成测试相同的三个阶段模式——(1) 将计划显示为要验证的bug编号表，(2) 在每个红绿循环运行时报告一行进度（`FAIL ✓ → PASS ✓`或`FAIL ✗ — test passes on unpatched code, rewriting`），(3) 显示一个摘要表，包含验证/失败/重写的计数。

7. **Bug写up生成（所有确认的bug适用）**。在成功的红→绿循环（`verdict: "TDD verified"`）或确认没有修复（`verdict: "confirmed open"`）后，在`quality/writeups/BUG-NNN.md`生成一个自包含的写up。此文件设计为通过电子邮件发送给维护者、附加到Jira工单或在外部进行审查——它必须独立，不需要读者导航其他质量工件。

   **模板**（1-4、6、7是每个写up必需的；当深度判断触发时添加5；当存在相关bug时添加8）：

   1. **摘要**——一段话：什么问题，在哪里（文件:行），实际会破坏什么。
   2. **规范引用**——违反的具体规范部分，如果可用则附带URL。引用行为合同（≤15个字），代码未能满足。
   3. **代码**——有问题的代码，附带文件:行引用。用规范解释为什么它是错误的，而不仅仅是“看起来很奇怪”。
   4. **可观察后果**——实际破坏了什么。不是“理论上可能失败”——破坏了什么，在什么条件下，有什么症状。
   5. **深度判断**（仅在需要扩展时包含）——在起草1-4后，评估：后果是否从代码和测试中自明？如果读者会合理地问“为什么没人注意到这个？”或“这影响所有配置是否平等？”，请扩展分析。跟踪有问题的函数的调用者。显示哪些代码路径暴露了bug，哪些掩盖了它。具体扩展触发器：传输/配置依赖行为，某些路径上掩盖bug的功能标志，间接分发隐藏调用者，只在特定运行条件下出现的协商/初始化代码中的bug。如果后果从立即代码中明显（例如空指针解引用、off-by-one），请保持1-4紧凑并省略此部分。
   6. **修复**——作为内联diff（统一diff格式）提出的修复，简要解释为什么这是正确的修复。**始终包含一个具体的diff**——即使是确认打开的bug而没有单独的`.patch`文件。如果修复是一个单行更改（添加一个case标签，修复一个参数），请编写diff。如果修复需要更广泛的变化，请编写解决核心缺陷的最小diff，并注明完整修复需要什么额外更改。写up中的内联diff使写up可操作——一个说“没有包含修复补丁”的写up是不完整且对维护者没有用的。
      ```diff
      --- a/drivers/virtio/virtio_ring.c
      +++ b/drivers/virtio/virtio_ring.c
      @@ -3527,6 +3527,7 @@ void vring_transport_features(...)
       	case VIRTIO_F_ORDER_PLATFORM:
       	case VIRTIO_F_IN_ORDER:
      +	case VIRTIO_F_RING_RESET:
       	default:
      ```
   7. **测试**——测试证明什么，如何运行，以及未修复和修复代码的预期输出。
   8. **相关问题**（仅当存在相关bug时包含）——同一类别的其他bug，如果有。即使它们尚未确认，也请标记它们。如果没有识别出相关问题，请省略此部分。

   **在写up文件顶部包含版本戳**（与其他生成的文件相同的格式）。

   **所有确认bug的写up生成（强制）**。为每个确认的bug生成写up——无论是TDD验证还是确认打开——在`quality/writeups/BUG-NNN.md`使用上述编号部分模板（1-8）。对于确认打开的bug，遵循相同的模板，包括6部分的修复diff（diff始终是必需的，即使没有单独的`.patch`文件）。写up阈值是bug确认，而不是TDD完成。有确认bug但没有写up目录的运行是不完整的。

   **内联diff是门禁强制**。`quality_gate.py`脚本检查每个写up是否包含` ```diff `块。没有内联diff的写up将导致门禁失败。不要写“见补丁文件”——将实际diff内联粘贴到写up正文中的` ```diff `代码块中。这是写up中最重要的元素，因为它使bug对仅阅读写up的维护者可操作。

### 检查点：生成artifact后更新PROGRESS.md

重新阅读`quality/PROGRESS.md`。更新：
- 标记阶段2完成并附带时间戳
- 更新工件清单：将每个生成的artifact设置为“已生成”并附带其文件路径
- 如果尚未存在，添加探索摘要笔记

**阶段2完成门禁（强制）**。在继续阶段3之前，验证：
1. 所有核心工件存在于`quality/`下的磁盘上（`QUALITY.md`、`CONTRACTS.md`、`REQUIREMENTS.md`、`COVERAGE_MATRIX.md`、`COMPLETENESS_REPORT.md`、`test_functional.*`、`RUN_CODE_REVIEW.md`、`RUN_INTEGRATION_TESTS.md`、`RUN_SPEC_AUDIT.md`、`RUN_TDD_TESTS.md`）。`AGENTS.md`不在列表中——协调器在阶段6将其写入目标仓库根目录，而不是阶段2。
2. `REQUIREMENTS.md`包含具有特定满足条件的规范（引用实际代码，文件路径、函数名、行号）——而不是抽象的行为描述。
3. 如果存在分发/枚举合同：`quality/mechanical/verify.sh`存在并已执行。
4. PROGRESS.md标记阶段2完成并附带时间戳。

在开始阶段3之前，重新阅读`quality/PROGRESS.md`和`quality/REQUIREMENTS.md`。要求是代码审查的目标列表——如果代码不满足要求，每个要求都是一个潜在的bug。

**阶段结束消息（强制——在阶段2完成后打印此消息，然后停止）：**

```
# 阶段2完成——质量工件已生成

我已经为这个项目生成了质量基础设施：
[列出创建的关键工件：REQUIREMENTS.md包含N个要求和N个用例，
QUALITY.md包含N个场景、功能测试、审查协议等]

现在要求是阶段3代码审查的目标列表——如果代码不满足要求，
每个要求都是一个潜在的bug。

要继续阶段3（使用回归测试的代码审查），请说：

    Run quality playbook phase 3.

或者说“keep going”以自动继续。
```

**打印此消息后，停止。除非用户明确要求，否则不要继续到阶段3。**

---

## 阶段3：代码审查和回归测试

**v1.5.6 instrumentation**：现在将`phase_start phase=3`追加到`quality/run_state.jsonl`。阶段结束时，交叉验证（`quality/RUN_CODE_REVIEW.md`存在；每个识别的bug一个写up），然后追加`phase_end phase=3`。

> **本阶段所需参考**：
> - `quality/REQUIREMENTS.md`——代码审查的目标列表
> - `references/review_protocols.md`——三阶段协议和回归测试约定

按照文件3中描述的运行代码审查协议（所有三个阶段）。在生成结果后，根据`references/review_protocols.md`中的关闭要求为每个确认的BUG编写回归测试。

**更新 PROGRESS.md：** 将所有已确认的 BUG 添加到累积 BUG 追踪器中，来源为 "代码审查"，包括文件：行号引用、描述、严重程度和关闭状态（回归测试函数名称或豁免原因）。标记阶段 3（代码审查 + 回归测试）完成。

**阶段结束消息（强制执行 — 阶段 3 完成后打印此消息，然后停止）：**

```
# 阶段 3 完成 — 代码审查

三遍代码审查已完成。[总结：确认 N 个 bug，生成 N 个回归测试补丁，生成 N 个修复补丁。列出 bug ID 和简短摘要。]

要继续进入阶段 4（规范审查 — 三人理事会），请说：

    运行质量剧本阶段 4。

或者说 "继续进行" 以自动继续。
```

**打印此消息后，停止。除非用户明确要求，否则不要进入阶段 4。**

---

## 阶段 4：规范审查和分派

**v1.5.6 仪器：** 现在追加 `phase_start phase=4`。对于 A/B/C/D 每一遍，追加 `pass_started phase=4 pass=X` 和 `pass_ended phase=4 pass=X`。阶段结束时，交叉验证（`quality/REQUIREMENTS.md` 非空 AND `quality/COVERAGE_MATRIX.md` 存在）然后追加 `phase_end phase=4`。

> **此阶段所需参考：**
> - `references/spec_audit.md` — 三人理事会协议、分派流程、验证探测

按照文件 5 中描述的规范审查协议运行。分派报告 **必须** 包含一个 `## 预审查文档验证` 部分（有关完整模板，请参阅 `references/spec_audit.md`）。即使 `reference_docs/` 为空，也需要此部分——在这种情况下，请说明审计员使用的基线。分派中的每个验证探测都必须产生可执行的证据（带行号引用的测试断言）。

**有效理事会分派枚举检查。** 如果有效理事会少于 3/3（少于三名审计员返回可用报告），并且运行中包含任何白名单/枚举/分发函数检查或任何转接种子检查，则审计可能不会在没有执行机械证明工件的情况下对那些检查结论为“无确认缺陷”。不完整的理事会配合机械验证是可以接受的。不完整的理事会依赖纯文本验证来确认代码存在性则不可接受——升级为“需要验证”，并在关闭前运行机械检查。

**预审查抽查必须从代码中提取，而不是从文档中断言。** 当规范审查提示包含预验证的抽查声明（例如，“验证函数 X 在行 Z 处处理常量 Y”），分派必须通过提取所引行的实际代码来验证每个声明——而不是确认声明听起来合理。对于关于代码内容的每个抽查声明，预验证必须报告所引行实际包含的内容：“行 3527 包含 `default:` — 不是 `case VIRTIO_F_RING_RESET:` 如所声称。” 如果抽查是从要求或收集的文档生成的，而不是从代码本身生成的，则将其视为要测试的假设，而不是要确认的事实。此规则可防止 v1.3.17 中观察到的污染链，其中虚假的抽查声明（“RING_RESET at 3527-3528”）被接受为“准确”而未读取实际行，然后通过分派传播到每个下游工件。

**更新 PROGRESS.md：** 将规范审查中确认的每个**代码 bug**添加到累积 BUG 追踪器中，来源为“规范审查”。这是至关重要的——如果规范审查的 bug 没有添加到与关闭验证读取相同的追踪器中，它们将系统性地被遗弃。

### 层 2 — 语义引用检查（v1.5.3 理事会子遍）

在主要规范审查分派后，每位理事会成员对每个 Tier 1/2 REQ 的 `citation_excerpt` 运行逐项裁决。这是**层 2** 的幻觉门：层 1 是机械字节相等性检查——`bin/citation_verifier` 由 `bin/reference_docs_ingest` 在摄取时调用，并由 `quality_gate.py` 在门控时重新调用；LLM 从不直接向其外壳。层 2 是语义的——审查员决定摘录是否实际支持所声明的需求，或者需求是否超出了摘录所说的内容。

**协议。**

1. **每位理事会成员一个提示，所有 Tier 1/2 REQ 批量处理。** 不是一次一个 REQ（3×N 提示太多）。不是散文响应（模式匹配风险）。审查员接收包含 `(req_id, citation_excerpt, REQ 描述)` 元组的完整列表，并返回结构化的逐项 JSON 响应。

2. **结构化响应模式（schemas.md §9.2）。** 对于每个 REQ，审查员记录 `{"req_id": "REQ-NNN", "reviewer": "<稳定字符串>", "verdict": "supports" | "overreaches" | "unclear", "notes": "<理由>"}`。有效的 `verdict` 值在 schemas.md §3.5 中枚举。

3. **批量处理阈值。** 当运行产生超过 15 个 Tier 1/2 REQ 时，将它们分成每个提示最多 15 个 REQ 的批次。相同的审查员按顺序看到每个批次；他们的响应条目被连接到一个在相同 `reviewer` 字符串下的 `reviews[]` 数组中。

4. **审查员标识符稳定性。** 使用固定字符串，如 `"claude-opus-4.7"`、`"gpt-5.4"`、`"gemini-2.5-pro"`。schemas.md §10 不变量 #17 中的多数计算基于此字段——一个拼写错误会无声地成为第四位审查员并破坏 2-of-3 多数检查。

5. **输出。** 使用 §1.6 声明包装器将所有理事会成员的响应连接到 `quality/citation_semantic_check.json`，但记录数组命名为 `reviews` 而不是 `records`（schemas.md §9.1）。每运行一个文件，每次审计遍历都会重新生成。

**多数规则（门控强制执行）。** 对于每个 Tier 1/2 REQ，门控按 `req_id` 对审查分组，当 ≥2 的 3 位审查员记录 `verdict == "overreaches"` 时，运行失败。单个成员的 `overreaches` 或 `unclear` 裁决作为警告出现，但不会失败门控。一个少于三位审查员裁决的 REQ（缺少审查员、跳过批次）证据不足——门控将其视为失败。

**规范差距运行的 No-op。** 如果运行产生零 Tier 1/2 REQ，`citation_semantic_check.json` 仍然会使用空的 `reviews` 数组写入——文件的存在是工件合同的一部分，即使检查没有要评估的内容。

### 规范审查后回归测试

在规范审查分派后，检查 PROGRESS.md 中的累积 BUG 追踪器。任何没有回归测试的规范审查 BUG 现在需要一个。使用与代码审查回归测试相同的约定（预期失败标记、测试发现对齐、可执行源文件）为规范审查确认的代码 bug 编写回归测试。

**此步骤存在的原因：** 代码审查的 bug 立即获得回归测试，因为测试是在审查后立即编写的。规范审查在测试编写后运行，所以其确认的 bug 被遗弃——它们出现在分派报告中，但从未获得测试。此步骤关闭了这一差距。

**单个审计员工件（强制执行）。** 规范审查必须在 `quality/spec_audits/` 产生单个审计员报告文件，文件名包含 `auditor`（规范格式：`YYYY-MM-DD-auditor-N.md`，例如，`2026-04-12-auditor-1.md`；也接受：`auditor_<model>_<date>.md`）。门控匹配 `*auditor*`——任何符合的名称都会匹配。每位审计员一个文件，而不仅仅是分派合成。每个审计员报告记录该审计员在分派协调前独立发现的内容。如果只有分派文件存在而没有单个审计员工件，审计不完整——因为无法验证分派，因为没有记录协调前的发现。此要求存在是因为单个分派文件将发现与协调混淆，使得无法判断一个发现是否独立确认或来自单一来源。

**阶段 4 完成门控。** 阶段 4 不会完成，直到 `quality/spec_audits/YYYY-MM-DD-triage.md` 存在一个分派文件 **并且** 存在单个审计员报告。如果只有审计员报告存在而没有分派合成，请在 PROGRESS.md 中标记阶段 4 为“部分 — 分派待定”并完成分派后再继续。如果只有分派存在而没有单个报告，请标记阶段 4 为“部分 — 审计工件缺失”并重新生成它们。PROGRESS.md 复选框必须在确认分派文件和审计员报告都存在后才能设置。

更新 BUG 追踪器条目中的回归测试引用。标记阶段 4（规范审查 + 分派）完成。

**阶段结束消息（强制执行 — 阶段 4 完成后打印此消息，然后停止）：**

```
# 阶段 4 完成 — 规范审查

三人理事会规范审查完成。[总结：运行 N 位审计员，分派确认 N 个新 bug，总 bug 数现在为 N。列出任何新 bug ID 和摘要。]

要继续进入阶段 5（协调 — TDD 验证、报告、关闭），请说：

    运行质量剧本阶段 5。

或者说 "继续进行" 以自动继续。
```

**打印此消息后，停止。除非用户明确要求，否则不要进入阶段 5。**

---

## 阶段 5：审查后协调和关闭验证

**v1.5.6 仪器：** 现在追加 `phase_start phase=5`。对于每个门控检查，追加 `gate_check gate_name=X verdict=pass|fail|warn|skip`。阶段结束时，交叉验证（`quality/results/quality-gate.log` 非空）然后追加 `phase_end phase=5`。

**源代码保护栏（强制执行）。** 阶段 5 产生 *建议* 修复作为补丁工件，位于 `quality/patches/<BUG-NNN>-fix.patch` 和 `quality/patches/<BUG-NNN>-regression-test.patch`。阶段 5 必须**不**将那些补丁应用到 `quality/` 外部的源文件。自我审计运行如果修改了目标源树是缺陷，而不是合法的阶段 5 输出——操作员选择何时在单独的监督步骤中应用补丁。运行结束时剧本调用 `bin.run_state_lib.validate_no_source_edits(target_dir)`；如果该助手报告任何非 `quality/` 路径被污染，追加一个 `error recoverable:false` 事件引用违规并结束运行，状态为 `run_end status=aborted`。此规则在 v1.5.6 边缘震动基准测试后得到重申，因为在 2026-05-02 的 Codex 引导运行中，阶段 5 偏离轨道并编辑了五个 `quality/` 外部的源文件后被终止。

> **此阶段所需参考：**
> - `quality/PROGRESS.md` — 累积 BUG 追踪器（权威发现列表）
> - `references/challenge_gate.md` — 误报检测的两轮挑战协议
> - `references/requirements_pipeline.md` — 审查后协调流程
> - `references/review_protocols.md` — 回归测试清理（逆转后）
> - `references/spec_audit.md` — 冲突验证探测协议

**阶段 5 入门门控（强制执行 — 硬停止）。** 在继续之前，验证以下所有阶段 4 工件存在：

1. `quality/spec_audits/` 目录存在并且包含至少一个 `*triage*` 文件（分派合成）
2. `quality/spec_audits/` 包含至少一个 `*auditor*` 文件（单个审计员报告）
3. `quality/PROGRESS.md` 存在并且其阶段 4 行被标记 `[x]`

如果任何这些缺失，停止并返回阶段 4。不要在规范审查工件确认存在之前继续协调——没有分派数据的协调会产生不完整的关闭报告。

重新阅读 `quality/PROGRESS.md`——特别是累积 BUG 追踪器。这是跨代码审查和规范审查的所有发现的权威列表。

**挑战门控（强制执行 — 协调前）。** 在运行关闭验证之前，对每个匹配自动触发模式的确认 bug 应用挑战门控。阅读 `references/challenge_gate.md` 了解完整协议。简而言之：

1. 扫描 BUG 追踪器查找匹配任何自动触发模式的 bug（安全类发现、在所引位置有设计决策评论的代码、没有规范基础的发现、处理相同问题的兄弟代码路径不同、关于缺失功能的发现）。
2. 对于每个触发的 bug，使用参考中描述的新子代理运行两轮挑战。
3. 在 `quality/challenge/BUG-NNN-challenge.md` 中记录裁决。
4. 应用裁决：确认的 bug 正常进行。降级的 bug 调整严重程度。拒绝的 bug 从 BUG 追踪器中移除，并移至 BUGS.md 的“已审查和驳回”附录，附上挑战理由。

**始终运用常识。** 挑战门控的主要目的是捕获模式匹配压倒了判断的情况。如果 bug 会让你看起来向上游维护者报告它是愚蠢的——一个自我说明的占位符被标记为关键漏洞、一个记录的设计决策被标记为缺陷、一个有意功能差距被标记为安全漏洞——它不应该在挑战后存活。常识测试不是众多因素之一；它是整个审查的框架。

**此门控存在的原因：** 在 v1.4.6 边缘震动基准测试中，代码审查确认了 42 个 bug，包括 7 个被评为 CRITICAL 的 bug。经过人工审查，最强的发现（BUG-001，source_ids 覆盖）是 HIGH，而不是 CRITICAL。六个“CRITICAL”租户隔离 bug 是有明确注释的文档功能差距。一个“CRITICAL”JWT 发现（BUG-041）是一个自我说明的开发占位符，其中包含字面字符串“change-me-in-production。” 模型通过多轮反驳来捍卫这些发现，因为它的本能是寻找和捍卫 bug，而不是应用常识来判断什么构成缺陷。挑战门控强制在发现最终确定之前进行这种常识审查。

1. **运行** `references/requirements_pipeline.md` 中描述的**审查后协调**。更新 COMPLETENESS_REPORT.md。
2. **运行关闭验证：** 对于 BUG 追踪器中的每一行，验证它具有回归测试引用或明确的豁免。如果任何 BUG 缺少两者，现在编写测试或豁免。
3. **分派到 BUGS.md 同步门控（强制执行）。** 重新阅读分派报告（`quality/spec_audits/*-triage.md`）。对于每个确认的代码 bug，验证它出现在 `quality/BUGS.md` 中。如果 BUGS.md 存在但缺少分派确认的 bug，追加它们。一个确认代码 bug 的分派报告和没有对应 BUGS.md 条目的分派报告是不合规的——阶段必须在它们同步后才能标记为完成。此门控存在的原因是在 v1.3.21 基准测试中，javalin 的分派确认了 2 个 bug，但 BUGS.md 从未被创建。
4. **规范审查逆转后的清理：** 如果规范审查将任何代码审查 BUG 重新分类为设计选择或误报，根据 `references/review_protocols.md` 移除或重新定位相应的回归测试。
5. **解决 CR 与规范审查冲突：** 如果代码审查和规范审查对同一发现意见不一致（一个说 BUG，另一个说设计选择），根据 `references/spec_audit.md` 部署验证探测并记录解决方案在 BUG 追踪器中。

**TDD 侧车到日志一致性检查（强制执行）。** 对于 `tdd-results.json` 中的每个 bug 条目，验证相应的日志文件存在并且一致。如果 `tdd-results.json` 包含一个 `verdict: "TDD verified"` 的 bug，那么 `quality/results/BUG-NNN.red.log` 必须存在并且第一行是 `RED`，`quality/results/BUG-NNN.green.log` 必须存在并且第一行是 `GREEN`。如果侧车声称“TDD verified”但没有红色阶段日志存在，裁决未证实——要么通过运行测试创建日志，要么将裁决降级为 `"confirmed open"`。此检查存在的原因是 v1.3.46 基准测试显示代理在 JSON 中写入“TDD verified”裁决，是基于叙事推理而没有执行测试。

**执行证据优先于叙事工件（矛盾门）。** 在运行终端门之前，检查执行证据与散文工件之间的矛盾。执行证据包括：机械验证工件（`quality/mechanical/*`）、验证收据文件（`quality/results/mechanical-verify.log`，`quality/results/mechanical-verify.exit`）、回归测试结果（`test_regression.*`带有`xfail`结果）、TDD红阶段日志文件（`quality/results/BUG-NNN.red.log`），以及管道中保存的任何shell命令输出。散文工件包括：`REQUIREMENTS.md`，`CONTRACTS.md`，代码评审，规范审计分派，以及`BUGS.md`。如果某个执行工件显示常量缺失（机械检查）、测试失败（回归测试）或红阶段确认存在bug（TDD可追溯性）——但散文工件声称常量存在、bug已修复或代码合规——则执行结果优先。在继续之前重新打开并更正矛盾的散文工件。具体来说：如果`mechanical-verify.exit`包含非零值，PROGRESS.md可能不能声称“机械验证：通过”，且终端门可能无法通过——无论其他工件说什么。在v1.3.18中，分派声称`RING_RESET`被保留（`spec_audits/triage.md`），BUGS.md声称“工作树中已修复”，但TDD可追溯性显示当前源中的断言`assert "case VIRTIO_F_RING_RESET:" in func`失败。这三个不可能都为真——执行失败是事实真相。这门会捕获这种矛盾。

**版本戳一致性检查（强制）。** 从SKILL.md元数据中读取`version:`字段（使用参考文件解析顺序）。然后检查每个生成的工件：PROGRESS.md的`Skill version:`字段，每个`> Generated by`归属行，每个代码文件头戳，以及每个侧车JSON的`skill_version`字段。每个版本戳必须与SKILL.md元数据完全匹配。单个不匹配是基准失败——在继续之前修复戳。这个检查存在的原因是v1.3.21基准测试中，9个仓库中有5个来自旧技能版本的版本戳（v1.3.16或v1.3.20），因为PROGRESS.md模板包含硬编码的版本号。

**机械目录一致性检查。** 如果存在`quality/mechanical/`，它必须至少包含一个`verify.sh`文件。空的`quality/mechanical/`目录是不合规的——它意味着步骤被尝试但放弃了。如果此项目的范围内不存在分派函数合约，则完全不要创建`mechanical/`目录。相反，在PROGRESS.md中记录：`机械验证：不适用——范围内没有分派/注册/枚举合约。`如果分派合约确实存在，`verify.sh`必须包含每个`quality/mechanical/`下保存的提取文件的一个验证块（不只是一个）。一个只检查一个工件而存在多个工件的`verify.sh`是不完整的。

**验证收据门（强制，在终端门前）。** 如果存在`quality/mechanical/`，在终端门运行之前，以下收据文件必须也存在：
- `quality/results/mechanical-verify.log` — `bash quality/mechanical/verify.sh`的完整stdout/stderr
- `quality/results/mechanical-verify.exit` — 包含退出代码的单行（例如，`0`）

如果任何一个文件缺失，现在运行`bash quality/mechanical/verify.sh > quality/results/mechanical-verify.log 2>&1; echo $? > quality/results/mechanical-verify.exit`。如果退出代码不是`0`，终端门失败——在解决机械不匹配（通过修复提取，而不是编辑verify.sh或收据）之前不要继续。除非`mechanical-verify.exit`包含`0`，否则PROGRESS.md不能声称“机械验证：通过”。这门存在的原因是v1.3.23 PROGRESS.md声称所有验证通过，而verify.sh实际上返回了退出码1——收据文件使此声明可审计。

**TDD日志关闭门（强制，在终端门前）。** 在继续到终端门之前，枚举`quality/BUGS.md`中的所有确认的bug ID并验证：
1. 每个确认的bug都有`quality/results/BUG-NNN.red.log`存在。
2. 如果存在该bug的`quality/patches/BUG-NNN-fix.patch`，`quality/results/BUG-NNN.green.log`也存在。
3. 每个日志文件的第一行是：`RED`，`GREEN`，`NOT_RUN`，`ERROR`。

如果任何检查失败，停止并立即使用TDD执行强制部分的语言感知测试执行命令生成缺失的日志。不要在缺少TDD日志的情况下继续到终端门——在tdd-results.json中具有“TDD验证”评语的bug但没有相应红阶段日志是一个矛盾。

**终端门（强制，在标记第5阶段完成前）：**

**前提条件检查：** 只有当第3阶段（代码评审）和第4阶段（规范审计）都完成，或PROGRESS.md中明确标记为跳过并给出理由时，终端门才能运行。零bug结果只有在代码评审和规范审计工件存在（即`quality/code_reviews/`和`quality/spec_audits/`目录包含报告文件）的情况下才有效。如果这些工件缺失且阶段未明确跳过，终端门失败——不要标记第5阶段完成。

**BUGS.md始终是必需的。** 每个完成的运行都必须生成`quality/BUGS.md`，无论是否找到bug。如果代码评审和规范审计确认没有源代码bug，创建BUGS.md，并在`## Summary`中声明“未发现确认的源代码bug”，并列出评估和消除的候选数量（例如，“代码评审评估了N个候选；规范审计评估了M个候选；所有都被重新归类为设计选择、仅测试问题或误报”）。这提供了对清洁结果的正面断言，而不是文件缺失的模糊性。没有BUGS.md的完成运行是不合规的。

**BUGS.md标题格式。** 每个确认的bug必须使用标题级别`### BUG-NNN`（例如，`### BUG-001`或`### BUG-H1`）。数字ID（`BUG-001`）和严重性前缀ID（`BUG-H1`，`BUG-M3`，`BUG-L6`）都是有效的。这是规范标题格式——不是`## BUG-001`，不是`**BUG-001**`，不是项目符号。`### BUG-NNN`标题是下游工具grep时用于计数bug的，也是tdd-results.json `id`字段必须匹配的。不一致的标题级别会导致机器可读计数与文档不一致。

重新阅读`quality/PROGRESS.md`。计算BUG跟踪器条目。然后：

1. 向用户打印以下声明（这是强制性的，不是可选的）：

   > "BUG跟踪器有N条条目。N条有回归测试，N条有豁免，N条未解决。代码评审确认了M个bug。规范审计确认了K个代码bug（L个新产生的）。预期总数：M + L。"

2. 将相同的声明写入PROGRESS.md，在BUG跟踪器表格下创建一个新的`## 终端门验证`部分（立即在BUG跟踪器表格之后）。这使门持久化到工件中，以便审阅者无需阅读会话日志即可验证它。

如果跟踪器条目计数不等于M + L，停止并协调——一个BUG从跟踪器中丢失了。直到计数匹配之前不要标记第5阶段完成。这门存在的原因是v1.3.5引导显示代理可靠地跳过规范审计后的跟踪器更新，导致30-50%的确认bug丢失。

**回归测试函数名验证：** 对于每个引用回归测试的BUG跟踪器条目，在回归测试文件中grep测试函数名并确认它存在。代理可以在跟踪器中写一个测试名而没有实际创建测试。如果任何引用的测试函数不存在，在通过门之前现在写入它。

3. 验证PROGRESS.md中的`With docs`元数据字段与实际情况匹配：如果存在`reference_docs/`且包含文件，则应说`yes`；否则`no`。如果错误，修复它。

**工件文件存在门（强制，在标记第5阶段完成前）。** 在写入第5阶段完成复选框之前，验证每个必需工件都作为磁盘上的文件存在——而不仅仅是PROGRESS.md中提到。运行这些检查（使用`ls`或等效命令）：

- `quality/BUGS.md`存在（对所有完成运行都是必需的，根据基准34）
- `quality/REQUIREMENTS.md`存在
- `quality/QUALITY.md`存在
- `quality/PROGRESS.md`存在（显然——你正在写入它）
- `quality/COVERAGE_MATRIX.md`存在
- `quality/COMPLETENESS_REPORT.md`存在
- `quality/formal_docs_manifest.json`存在（v1.5.3 — 由`bin/reference_docs_ingest.py`在第1阶段写入；当没有正式文档时空`records[]`是有效的）
- `quality/requirements_manifest.json`存在（v1.5.3 — 权威REQ记录，渲染为REQUIREMENTS.md）
- `quality/use_cases_manifest.json`存在（v1.5.3 — 权威UC记录，渲染为USE_CASES.md / REQUIREMENTS.md的叙事）
- `quality/citation_semantic_check.json`存在（v1.5.3 — 第4层2层输出；空`reviews[]`对规范差距运行是有效的）
- 如果第3阶段运行：`quality/code_reviews/`至少包含一个`.md`文件
- 如果第4阶段运行：`quality/spec_audits/`包含一个分派文件和单个审计器文件
- 如果第0或0b运行：`quality/SEED_CHECKS.md`作为独立文件存在（不在PROGRESS.md中内联）
- 如果存在确认的bug：`quality/bugs_manifest.json`存在（v1.5.3 — 每个schemas.md §8的权威BUG记录）
- 如果存在确认的bug：`quality/results/tdd-results.json`存在
- 如果存在确认的bug：对于`quality/BUGS.md`中每个确认的bugID，`quality/results/BUG-NNN.red.log`存在
- 如果存在确认的bug且带有修复补丁：对于每个有`quality/patches/BUG-NNN-fix.patch`的bug，`quality/results/BUG-NNN.green.log`存在

对于每个缺失的文件，现在创建它。不要在缺少工件的情况下标记第5阶段完成——如果工件引用的文件不存在，PROGRESS.md中的终端门验证是无意义的。这门存在的原因是v1.3.24基准测试显示express完成所有阶段并在PROGRESS.md中写入终端门部分，但BUGS.md、SEED_CHECKS.md和代码评审/规范审计文件从未写入磁盘。

**侧车JSON后写入验证（强制）。** 在写入`quality/results/tdd-results.json`和/或`quality/results/integration-results.json`后，立即重新打开每个文件并验证它是否包含所有必需的键。对于`tdd-results.json`，必需的根键是：`schema_version`，`skill_version`，`date`，`project`，`bugs`，`summary`。`bugs`中的每个条目必须具有：`id`，`requirement`，`red_phase`，`green_phase`，`verdict`，`fix_patch_present`，`writeup_path`。`summary`对象必须包括`confirmed_open`以及`verified`，`red_failed`，`green_failed`。对于`integration-results.json`，必需的根键是：`schema_version`，`skill_version`，`date`，`project`，`recommendation`，`groups`，`summary`，`uc_coverage`。两个文件都必须有`schema_version: "1.1"`。如果任何键缺失，现在添加它——不要在磁盘上留下不合规的JSON文件。此验证存在的原因是v1.3.25基准测试显示8个仓库中有6个非合规的侧车JSON：httpx发明了替代模式，serde使用了旧形状，jalinin省略了`summary`和每个bug字段，其他使用了无效的枚举值。

**脚本验证关闭门（强制，最终步骤，在标记第5阶段完成前）。** 使用与参考文件相同的后备机制定位`quality_gate.py`——按顺序遍历这六个规范安装布局，取第一个命中：`quality_gate.py`，`.claude/skills/quality-playbook/quality_gate.py`，`.github/skills/quality_gate.py`，`.cursor/skills/quality-playbook/quality_gate.py`，`.continue/skills/quality-playbook/quality_gate.py`，`.github/skills/quality-playbook/quality_gate.py`。从项目根目录运行它。此脚本机械验证：文件存在，BUGS.md标题格式，侧车JSON必需键和每个bug字段名（`id`，`requirement`，`red_phase`，`green_phase`，`verdict`，`fix_patch_present`，`writeup_path`），枚举值和摘要一致性，用例标识符，终端门部分，机械验证收据，版本戳，写完完整性，**每个确认bug的回归测试补丁存在**，以及**每个写完中的内联修复差异**（每个`quality/writeups/BUG-NNN.md`必须包含一个` ```diff `块）。如果脚本报告任何FAIL结果，在继续之前修复每个失败的检查——最常见的FAIL是：(1) 缺少`quality/patches/BUG-NNN-regression-test.patch`文件，(2) 非规范JSON字段名，如`bug_id`而不是`id`，(3) TDD摘要中缺少`confirmed_open`，(4) 写完中没有内联修复差异（第6部分必须包含具体的diff，而不仅仅是“查看补丁文件”）。直到`quality_gate.py`退出0之前不要标记第5阶段完成。将脚本的全输出追加到`quality/results/quality-gate.log`。

**v1.5.3层1机械检查（schemas.md §10不变式#1–#18）。** 除了上述传统门检查，v1.5.3中的`quality_gate.py`还强制执行`schemas.md` §10中定义的层1不变式。每个不变式涵盖的紧凑映射：

- **#1–#10 — 核心合约检查。** 引用层级门控，引用文档存在，引用哈希匹配，引用摘录存在+可定位（仅部分/行；页码从不充分），bug→REQ解析，前向链接解析，处置完整性，功能部分存在，无孤儿正式文档，INDEX.md字段存在。
- **#11 — 引用摘录字节等价。** 门重新运行`schemas.md` §5.4的`bin/citation_verifier.extract_excerpt`在所有Tier 1/2引用上，并拒绝任何存储的`citation_excerpt`与新鲜提取的不字节等价的。这是层1反幻觉机制——即使定位器是真实的，也能捕获虚构或释义的摘录。
- **#12 — 法律`fix_type × disposition`组合**根据`schemas.md` §3.4。
- **#13 — 宣布包装器有效性**根据`schemas.md` §1.6。
- **#14 — REQ层级绑定到引用的FORMAL_DOC层级**（Tier 1 REQ不能引用Tier 2 FORMAL_DOC）。
- **#15 — ID唯一性**在每个宣布中。
- **#16 — 重复引用元数据**（`version`，`date`，`url`，`retrieved`）当存在时必须与FORMAL_DOC匹配。
- **#17 — 语义检查多数规则。** ≥2的3个`overreaches`对同一Tier 1/2 REQ失败门（见第4层的子传递）。
- **#18 — `REQ.use_cases`和`UC.formal_doc_refs`中的数组值唯一性**。

**`citation_stale`是一个门报告标记，不是引用记录上的字段。** 当存储的`citation.document_sha256`与活着的`FORMAL_DOC.document_sha256`不同时，`quality_gate.py`将`citation_stale`条目写入`quality_gate_report.json`（或等效）。不要在引用记录本身上写`citation_stale`——记录保持纯输入，陈旧标记是门报告输出，根据`schemas.md` §5.1 / §10不变式#3。

**不要在此散文中实现门。** 上述层1检查列表是`quality_gate.py`强制执行的内容的摘要——权威定义存在于`schemas.md`中。门的实现（v1.5.3实施的第5阶段）存在于`quality_gate.py`中；SKILL.md描述了协议，但没有重述不变式。

**用例标识符格式。** REQUIREMENTS.md必须对所有派生用例使用规范用例标识符格式`UC-01`，`UC-02`等。每个用例必须标有其标识符。这是必需的，以便机器可读跟踪——标识符格式使`quality_gate.py`和下游工具能够按程序计数和交叉引用用例。作为散文段落写入的用例没有标识符是不合规的。

更新PROGRESS.md：标记第5阶段完成。BUG跟踪器现在应显示每个条目的关闭状态。

**阶段结束消息（强制——在Phase 5完成后打印此消息，然后停止）：**

# 第 5 阶段完成 — 对账与 TDD 验证

所有确认的 Bug 现在都有回归测试、测试报告和 TDD 红绿验证。
[总结：N 个总确认 Bug，N 个 TDD 验证状态，N 个修复补丁。
列出所有 Bug ID 及其单行摘要和 TDD 判定结果。]

要继续到第 6 阶段（最终验证和质量门禁），请说：

    运行质量剧本第 6 阶段。

或者说“继续”以自动继续。

```
# 第 6 阶段：验证
```

**v1.5.6 仪器化：** 现在追加 `phase_start phase=6`。阶段结束时，交叉验证（`quality/BUGS.md` 非空且包含 `^## BUG-` 部分 AND `quality/INDEX.md` 更新了 `gate_verdict` 字段）后追加 `phase_end phase=6`。第 6 阶段结束后，追加 `run_end status=success`（如果适用，则追加 `aborted` / `failed`）。

> **此阶段所需参考：**
> - `references/verification.md` — 45 个自检基准

**为何需要验证阶段？** AI 生成的输出可能看起来很完善，但可能微妙地出错。引用未定义的固定件的测试报告 0 个失败但 16 个错误——而“0 个失败”听起来像成功。集成协议可能列出实际模式中不存在的字段名。验证阶段在用户发现这些问题之前捕获这些问题，这很重要，因为对生成质量剧本的信任很脆弱——一个错误的字段名会破坏对其他所有内容的信心。

**第 6 阶段执行模型：增量而非整体。** 第 6 阶段作为一系列独立的验证步骤运行，每个步骤只读取它需要的文件，检查一个条件，并将结果写入 `quality/results/phase6-verification.log`，然后移动到下一步。不要一次加载所有工件到上下文中。不要尝试在读取工件时在内存中保留完整的验证清单。下面的每个步骤都是自包含的——读取文件，检查条件，追加结果，丢弃上下文。

### 第 6.1 步：机械验证关闭（强制第一步）

如果存在 `quality/mechanical/`，第 6 阶段的**第一个动作**是：

```bash
bash quality/mechanical/verify.sh > quality/results/mechanical-verify.log 2>&1
echo $? > quality/results/mechanical-verify.exit
```

在 shell 中执行此命令。不要用 Python 脚本替换，不要读取工件文件并对其内容进行断言，不要跳过此步骤。命令必须是 `bash quality/mechanical/verify.sh`——不是 `python3 -c "..."`，不是 `cat quality/mechanical/... | grep ...`，也不是任何其他等效方法。

记录退出代码。如果非零，**第 6 阶段立即失败。** 不要继续到下一步。返回提取步骤：删除不匹配的 `*_cases.txt`，用新的 shell 重定向重新运行提取命令，重新验证，并更新所有引用了旧提取的下游工件。

在 PROGRESS.md 下记录 `## 第 6 阶段机械关闭` 并追加到 `quality/results/phase6-verification.log`：
```
[第 6.1 步] 机械验证：通过 (退出 0)
```

**为何不可替代：** 在 v1.3.23 中，模型用 `python3 -c "from pathlib import Path; ..."` 替换了 `bash verify.sh`，该模型读取（伪造的）工件文件并对其内容进行断言——尽管工件是伪造的，但这是一个循环检查，检查通过了。唯一可信的验证是重新运行生成工件的相同 shell 管道并比较结果。任何其他方法都可能被损坏的中间文件欺骗。

### 第 6.2 步：运行 quality_gate.py（脚本验证检查）

运行机械验证门：

```bash
python3 quality_gate.py . > quality/results/quality-gate.log 2>&1  # 通过回退（六种规范布局，按顺序）：quality_gate.py, .claude/skills/quality-playbook/quality_gate.py, .github/skills/quality_gate.py, .cursor/skills/quality-playbook/quality_gate.py, .continue/skills/quality-playbook/quality_gate.py, .github/skills/quality-playbook/quality_gate.py
echo $? >> quality/results/phase6-verification.log
```

读取 `quality/results/quality-gate.log`。如果它报告任何 FAIL 结果，在继续之前修复每个失败的检查。最常见的 FAIL 是：(1) 缺少 `quality/patches/BUG-NNN-regression-test.patch` 文件，(2) 非规范的 JSON 字段名，如 `bug_id` 而不是 `id`，(3) TDD 摘要中缺少 `confirmed_open`，(4) 测试报告没有内联修复差异，(5) 缺少 TDD 红绿日志文件。不要继续，直到 `quality_gate.py` 退出 0。

追加到 `quality/results/phase6-verification.log`：
```
[第 6.2 步] quality_gate.py: 通过 (退出 0) — N 个检查通过，0 个 FAIL，0 个 WARN
```

此步骤涵盖验证基准：14（侧车 JSON），17（测试文件扩展名），18（用例计数），20（测试报告），23（机械工件），26（版本戳），27（机械目录），29（triage-to-BUGS 同步），34（BUGS.md 存在），38（个别审计报告），39（BUGS.md 标题格式），40（工件文件存在），41（侧车 JSON 验证），42（脚本验证关闭），43（用例标识符），44（回归测试补丁），45（测试报告内联差异）。

**v1.5.3 第 1 层不变式也在这里运行。** `quality_gate.py` 还强制执行 schemas.md §10 不变式 #1–#18（在第 5 阶段中总结）。特别是，脚本对每个 Tier 1/2 引用重新运行 `bin/citation_verifier.extract_excerpt` 根据 schemas.md §5.4，并拒绝任何存储的 `citation_excerpt` 与新鲜提取的输出字节相等——这是摄入后的篡改捕获。如果这里任何第 1 层不变式失败，修复底层清单记录（不是门，不是摘要）并重新运行。

### 第 6.3 步：测试执行验证

运行功能测试套件。读取 `quality/test_functional.*` 以确定测试命令：

- **Python:** `pytest quality/test_functional.py -v 2>&1 | tail -20`
- **Java:** `mvn test -Dtest=FunctionalTest` 或 `gradle test --tests FunctionalTest`
- **Go:** `go test -v` 针对生成的测试文件的包
- **TypeScript:** `npx jest functional.test.ts --verbose`
- **Rust:** `cargo test`
- **Scala:** `sbt "testOnly *FunctionalSpec"`

检查失败和错误。来自缺失固定件、失败导入或未解析依赖项的错误计为损坏的测试。预期失败（xfail）回归测试不计入此检查。

追加到 `quality/results/phase6-verification.log`：
```
[第 6.3 步] 功能测试：通过 — N 个测试，0 个失败，0 个错误
```

这涵盖了基准 8（所有测试通过）和 9（现有测试未损坏）。

### 第 6.4 步：验证清单 — 文件逐个检查

从小批量中处理 `references/verification.md` 剩余的验证基准。对于每个批量，只读取需要的文件，检查条件，并追加结果。**每个批量不要读取超过 2 个文件。**

**批量 A — QUALITY.md（基准 1-2，10）：** 读取 `quality/QUALITY.md`。计算场景。验证每个场景引用真实代码（grep 引用的函数名）。追加结果。

**批量 B — 功能测试文件（基准 3-7）：** 读取 `quality/test_functional.*`。检查跨变体覆盖率（~30%），边界测试计数，断言深度（值检查与存在检查），层正确性（结果与机制），变异有效性。

**批量 C — 协议文件（基准 11-13）：** 逐个读取 `quality/RUN_CODE_REVIEW.md`，然后 `quality/RUN_INTEGRATION_TESTS.md`，然后 `quality/RUN_SPEC_AUDIT.md`。检查每个文件都是自包含且可执行的。验证集成测试中的字段引用表。

**批量 D — 回归测试（基准 15-16，24）：** 如果存在 `quality/test_regression.*`，读取它。验证跳过保护引用 Bug ID，验证补丁验证门命令，验证源检查测试不使用 `run=False`。

**批量 E — 枚举和分诊检查（基准 19，21-22，25，36）：** 读取 `quality/code_reviews/*.md`（仅枚举部分）。读取 `quality/spec_audits/*triage*`（仅验证探测部分）。检查两列表比较，可执行探测证据，无机械工件循环引用，矛盾门。

**批量 F — 持续模式（基准 32-33）：** 仅当存在 `quality/SEED_CHECKS.md` 时。读取它，验证机械执行，验证 PROGRESS.md 中的收敛部分。

追加每个批量结果到 `quality/results/phase6-verification.log`：
```
[第 6.4A 步] QUALITY.md 场景：通过 — 8 个场景，所有引用真实代码
[第 6.4B 步] 功能测试质量：通过 — 30% 跨变体，断言深度正常
[第 6.4C 步] 协议文件：通过 — 所有自包含且可执行
[第 6.4D 步] 回归测试：通过 — 所有跳过保护存在
[第 6.4E 步] 枚举/分诊：通过 — 两列表检查存在，探测有断言
[第 6.4F 步] 持续模式：跳过 — 无 SEED_CHECKS.md
```

如果任何批量失败，立即修复问题，然后继续到下一个批量。

### 第 6.5 步：元数据一致性检查

读取 `quality/PROGRESS.md`（仅元数据和工件清单部分）。然后抽查：
- 需求计数在 REQUIREMENTS.md 标头、PROGRESS.md 工件清单和 COVERAGE_MATRIX.md 标头之间保持一致。这三个必须声明相同的数字。
- `With docs` 字段准确反映 `reference_docs/` 是否存在
- 终端门禁验证部分存在并填写完整

然后读取 `quality/COMPLETENESS_REPORT.md`（仅判定部分）。验证没有陈旧的预对账文本——如果存在 `## 判定` 和 `## 更新判定`（或 `## Post-Review Reconciliation`）部分，**删除原始 `## 判定` 部分**。最终文档必须恰好有一个 `## 判定` 标题。

追加到 `quality/results/phase6-verification.log`：
```
[第 6.5 步] 元数据一致性：通过 — 需求计数匹配，版本戳一致
```

如果任何元数据陈旧，立即修复。

### 检查点：最终化 PROGRESS.md

重新读取 `quality/PROGRESS.md`。更新：
- 标记第 6 阶段（验证基准）完成并附带时间戳
- 验证 Bug 追踪器对每个条目都有关闭
- 添加最终总结行：`"运行完成。N 个 Bug 发现 (N 来自代码审查，N 来自规范审计)。N 个回归测试编写。N 个豁免授予。"`
- **向用户打印建议的下一个提示（强制，所有运行）。** 这适用于每次运行，包括基线——它不是迭代特定的。打印以下块，以便用户可以复制粘贴以开始下一个迭代：

  对于基线运行（无迭代策略）：
  ```
  ────────────────────────────────────────────────────────
  下一个迭代建议：
  "使用差距策略运行质量剧本的下一个迭代。"
  ────────────────────────────────────────────────────────
  ```

  对于迭代运行，使用此映射确定下一个策略：
  - **gap** → 建议无过滤
  - **无过滤** → 建议对等
  - **对等** → 建议对抗
  - **对抗** → 建议从零开始运行质量剧本。（循环完成）

PROGRESS.md 的完成是一个永久审计轨迹。它记录了技能做了什么，发现了什么，以及如何解决每个发现。用户可以阅读它以了解运行情况，调试失败，并跨运行进行比较。

### 收敛检查（仅持续模式）

> **范围：** 仅此子节。上述建议下一个提示步骤是无条件的，并且必须在每个运行中无条件执行，无论是否跳过收敛检查。

**此步骤仅在阶段 0 执行**（即 `quality/SEED_CHECKS.md` 从先前的运行分析中存在）。如果是第一次运行且没有先前的历史记录，跳到阶段 7。

将此运行的 Bug 列表与种子列表进行比较：

1. **计算净新 Bug：** 此运行中 BUGS.md 的 Bug 与任何种子不匹配（按文件:行）。如果 Bug 在任何先前的运行中未找到，则它是“净新”的。
2. **计算种子延续：** 在此运行中重新确认的种子（Step 0b 中的 FAIL 结果）。
3. **计算种子解决：** 现在通过（Bug 自上次运行以来已修复）的种子。

在 PROGRESS.md 中写入 `## 收敛` 部分：

```markdown
## 收敛

运行编号：N (N 先前的运行在 quality/previous_runs/)
先前的运行种子：S (S 确认，R 解决)
此运行净新 Bug：K
收敛：[已收敛 | 未收敛]

净新 Bug：
- BUG-NNN：[摘要] (文件:行) — 不在任何先前的运行中
```

**收敛标准：** 如果**净新 Bug = 0**——此运行发现的每个 Bug 都已从先前的运行中知晓，则运行已收敛。这意味着进一步的运行不太可能在声明范围内发现更多 Bug。

**如果已收敛：** 向用户打印：`"此运行未发现超出 N 已从先前的运行中知晓的新 Bug。Bug 发现对此范围已收敛。所有运行中确认的 Bug 总数：T。"` 然后继续到阶段 7。

**如果未收敛——自动重新迭代。** 当收敛检查显示净新 Bug > 0 且迭代计数未达到最大值（默认：5）时，技能自动重新迭代：

1. 在 PROGRESS.md 中记录迭代编号和净新计数。
2. 通过 `bin/run_playbook.archive_previous_run(repo_dir, timestamp)`（或 `bin.archive_lib.archive_run()` 在第 6 阶段成功时）存档当前 `quality/` 目录。这些快照 `quality/` 到 `quality/previous_runs/<timestamp>/quality/` 并写入每个运行的 `INDEX.md` 以及 `RUN_INDEX.md` 行。
3. 从**阶段 0** 重新开始（现在将在 `quality/previous_runs/` 中找到新存档的运行）。
4. 向用户打印：`"迭代 N 发现 K 个净新 Bug。存档并开始迭代 N+1 (最大 M)。"`

迭代计数从 1 开始，第一次运行。每次存档和重启都会递增它。当计数达到最大值时，即使未收敛也停止迭代并打印：`"达到最大迭代次数 (M) 而未收敛。K 个净新 Bug 在最后一次运行中发现。所有运行中确认的 Bug 总数：T。"`

**迭代限制。** 默认最大值是 5 次迭代。如果用户的提示中包含显式限制（例如，`"run the playbook with 3 iterations"`），则使用该限制。如果用户的提示说“单次运行”或“无迭代”，则完全跳过重新迭代，并将未收敛视为与迭代前行为相同：打印净新计数并建议重新运行。

**上下文窗口感知。** 如果在重新迭代过程中任何时候检测到您的上下文窗口被大量消耗（例如，您生成的输出明显比早期迭代短或质量差），停止迭代，将当前状态写入 PROGRESS.md，并打印：`"由于上下文限制而停止迭代。完成了 N 的 M 次迭代。重新运行剧本以继续——阶段 0 将从 quality/previous_runs/ 拾取种子列表。"` 这是一个安全阀，而不是目标——大多数代码库在 2-3 次迭代内收敛。

**为何这很重要：** 单次剧本运行探索代码库的子集非确定性。在 virtio 上的第一次运行可能找到 BUG-001 和 BUG-004，但可能错过 BUG-005。第二次运行可能找到 BUG-005 和 BUG-006。如果到第三次运行没有净新 Bug 出现，探索可能已经覆盖了高价值区域。种子列表确保先前发现的 Bug 不会在运行之间丢失，收敛检查告诉用户何时额外的运行收益递减。自动重新迭代意味着技能是自包含的——调用者不需要外部脚本或手动重新运行来实现收敛。

**阶段结束消息（强制——在第 6 阶段完成后打印，然后停止）：**

# 第6阶段完成 — 所有阶段均已完成

质量手册基线运行已完成。以下是总结：

[包含：已确认的错误总数、质量门禁通过/失败/警告计数，以及所有错误ID列表，每个错误一行摘要和严重性。]

主要输出文件：
- quality/BUGS.md — 所有已确认的错误，包含规范依据和补丁
- quality/results/tdd-results.json — 结构化的TDD验证结果
- quality/patches/ — 每个错误的回归测试和修复补丁

现在您可以运行迭代策略以查找更多错误。迭代通常在基线之上增加40-60%的已确认错误。推荐周期是：
差距 → 未过滤 → 对等 → 对抗。

要自动运行所有四个迭代，请说：

    运行所有迭代。

我将每个策略作为单独的子代理进行协调，并为其提供自己的上下文窗口。

要一次运行一个迭代，请说：

    运行质量手册的下一个迭代。

或者询问我结果：“告诉我关于BUG-001的情况”或“哪些错误优先级最高？”

在您修复错误后，说“重新检查”以验证补丁是否已正确应用。

```
# 迭代完成 — [策略名称]

[总结：本次迭代发现了N个新的错误，总数现在为N。
列出新的错误ID及其一行摘要。]

[如果有推荐周期中剩余的策略，建议下一个策略:]
推荐下一个策略是[下一个策略]。要运行它，请说：

    使用[下一个策略]策略运行下一个迭代。

[如果四个策略都已运行:]
已运行所有四个迭代策略。已确认错误总数：N。
您可以查看结果，询问特定错误，或重新运行任何策略。

在您修复错误后，说“重新检查”以验证补丁是否已正确应用。

或者说“继续”以自动运行下一个迭代。
```

**打印此消息后，停止。除非用户明确要求，否则不要继续下一个迭代。**

---

## 重新检查模式 — 验证错误修复

重新检查模式是一种轻量级的验证过程，检查先前运行中发现的错误是否已被修复。而不是重新运行完整的六个阶段管道（60-90分钟），重新检查会读取现有的`quality/BUGS.md`，将每个错误与当前源树进行比较，并报告哪些错误已修复，哪些仍然打开。典型的重新检查需要2-10分钟。

**何时使用重新检查模式：** 在用户（或另一个代理）已应用手册发现的错误修复后。用户说“重新检查”或“验证错误修复”或“检查哪些错误已修复。”

**不要将重新检查模式用作运行完整手册的替代品。** 重新检查仅验证先前发现的错误 — 它不会发现新错误。

### 重新检查步骤

**步骤1：读取错误清单。**

读取`quality/BUGS.md`并解析每个`### BUG-NNN`条目。对于每个错误，提取：
- 错误ID（例如，BUG-001）
- 文件路径和行号来自`**文件：**`字段
- 描述摘要（`**描述：**`的第一句话）
- 严重性
- 修复补丁路径来自`**修复补丁：**`字段（例如，`quality/patches/BUG-001-fix.patch`）
- 回归测试路径来自`**回归测试：**`字段

**步骤2：将每个错误与当前源进行比较。**

对于每个错误，按顺序执行以下检查：

1. **修复补丁检查。** 如果在引用路径存在修复补丁，则针对当前树运行`git apply --check --reverse quality/patches/BUG-NNN-fix.patch`。如果反向应用成功（退出码0），则修复补丁已应用 — 错误可能已修复。如果失败，则修复未应用或代码已更改。

2. **源检查。** 在引用的行号处打开文件。读取周围上下文（±20行）。将您看到的内容与错误描述进行比较。有问题的代码是否已更改？修复是否解决了错误报告中描述的根本原因？

3. **回归测试执行。** 如果存在回归测试补丁：
   - 应用它：`git apply quality/patches/BUG-NNN-regression-test.patch`
   - 运行测试（使用项目的测试运行器）。如果测试通过，则错误已修复。如果测试失败，则错误仍然存在。
   - 反向补丁：`git apply -R quality/patches/BUG-NNN-regression-test.patch`

   如果回归测试补丁无法干净地应用（因为源已更改），请记录此情况并仅依赖源检查。

4. **结论。** 分配以下状态之一：
   - **已修复** — 修复补丁已应用**并且**回归测试通过（或源检查确认修复，如果测试无法运行）
   - **部分修复** — 有问题的代码已更改但回归测试仍然失败，或者修复仅解决了错误的部分方面
   - **仍然打开** — 原始有问题的代码未更改，或者回归测试仍然失败
   - **无法确定** — 无法确定状态（文件已移动，代码 heavily refactored，补丁无法应用）

**步骤3：生成重新检查结果。**

使用此模式写入`quality/results/recheck-results.json`：

注意：重新检查模式使用`"schema_version": "1.0"`（而不是`"1.1"`），因为它与TDD sidecar具有不同的结构 — `source_run`和每个错误的`status`/`evidence`字段是重新检查模式独有的。质量门禁验证此值为`"1.0"`。

```json
{
  "schema_version": "1.0",
  "skill_version": "1.5.6",
  "date": "YYYY-MM-DD",
  "project": "<项目名称>",
  "source_run": {
    "bugs_md_date": "<BUGS.md 头部的日期>",
    "total_bugs": <N>
  },
  "results": [
    {
      "id": "BUG-001",
      "severity": "HIGH",
      "summary": "<一行摘要>",
      "status": "FIXED",
      "evidence": "<确认修复的内容 — 例如，'反向应用成功 + 回归测试通过'>"
    }
  ],
  "summary": {
    "total": <N>,
    "fixed": <N>,
    "partially_fixed": <N>,
    "still_open": <N>,
    "inconclusive": <N>
  }
}
```

还写入`quality/results/recheck-summary.md`中的人类可读摘要：

```markdown
# 重新检查结果

> 从 <日期> 重新检查 quality/BUGS.md
> 重新检查运行： <今天的日期>
> 技能版本： <版本>

## 总结

| 状态 | 计数 |
|------|-------|
| 已修复 | N |
| 部分修复 | N |
| 仍然打开 | N |
| 无法确定 | N |
| **总计** | **N** |

## 每个错误的结果

| 错误 | 严重性 | 状态 | 证据 |
|-----|----------|--------|----------|
| BUG-001 | HIGH | FIXED | 反向应用成功，回归测试通过 |
| BUG-002 | MEDIUM | STILL_OPEN | 原始代码在 quality_gate.py:125 处未更改 |
| ... | ... | ... | ... |

## 仍然打开 — 详细信息

[对于每个 STILL_OPEN 或 PARTIALLY_FIXED 错误，包括简要说明哪些内容仍需修复。]
```

**步骤4：打印重新检查摘要。**

将摘要表打印给用户，然后停止。示例：

```
# 重新检查完成

检查了 quality/BUGS.md 中的19个错误与当前源。

| 状态 | 计数 |
|--------|-------|
| 已修复 | 17 |
| 仍然打开 | 2 |
| **总计** | **19** |

已修复错误：BUG-001，BUG-002，BUG-003，BUG-004，BUG-005，BUG-006，BUG-007，
BUG-008，BUG-009，BUG-010，BUG-011，BUG-013，BUG-014，BUG-015，BUG-016，
BUG-017，BUG-018

仍然打开：BUG-012（仍然存在 .orig 文件），BUG-019（基准40 艺术品列表未更新）

结果保存到：
- quality/results/recheck-results.json（机器可读）
- quality/results/recheck-summary.md（人类可读）
```

### 触发重新检查模式

当用户说任何以下内容时，重新检查模式将激活： "重新检查"、"验证错误修复"、"检查哪些错误已修复"、"重新检查错误"、"运行重新检查模式"，或类似表明他们想要验证修复而不是查找新错误的措辞。被触发时，完全跳过阶段1-7，仅执行上述重新检查过程。

---

## 第7阶段：呈现、探索、改进（交互式）

生成并验证后，清晰地呈现结果，并让用户控制接下来会发生什么。此阶段有三个部分：可扫描的摘要、按需深入挖掘，以及改进选项菜单。

**不要跳过此阶段。** 第1-6阶段的自动输出是一个坚实的基础，但用户需要了解已生成的内容，探索对他们重要的内容，并选择如何改进它。如果项目所有者不信任并理解质量手册，它就毫无用处。没有解释就丢弃六个文件，会导致无人阅读的工件。

### 第1部分：摘要表

呈现一个用户可以在10秒内扫描的表格：

```
这是我生成的：

| 文件 | 它的作用 | 关键指标 | 置信度 |
|------|-------------|------------|------------|
| REQUIREMENTS.md | 可测试的要求和使用案例 | N个要求，N个使用案例 | ██████░░ 中等 — 来自5阶段管道的坚实基础，通过细化传递改进 |
| QUALITY.md | 质量宪法 | 10个场景 | ██████░░ 高 — 基于代码，但场景是推断的，不是来自真实事件 |
| 功能测试 | 自动化测试 | 47个通过 | ████████ 高 — 所有测试通过，35%跨变体 |
| RUN_CODE_REVIEW.md | 三重代码审查 | 3次通过 | ████████ 高 — 结构 + 要求验证 + 一致性 |
| RUN_INTEGRATION_TESTS.md | 集成测试协议 | 9次运行 × 3个提供者 | ██████░░ 中等 — 质量门禁需要阈值调整 |
| RUN_SPEC_AUDIT.md | 三人委员会审计 | 10个审查领域 | ████████ 高 — 包括护栏 |
| RUN_TDD_TESTS.md | TDD验证协议 | N个要验证的错误 | ████████ 高 — 机械的 red-green 循环，具有规范可追溯性 |
```

根据您实际生成的内容调整表格 — 文件名、指标和置信度因项目而异。置信度列是最重要的：它告诉用户在哪里集中他们的注意力。

**置信度级别：**
- **高** — 直接来自代码、规范或模式。不太可能需要修订。
- **中等** — 合理推断，但可能错误。受益于用户输入。
- **低** — 最佳猜测。绝对需要用户输入才能有用。

表格后，添加一个“快速启动”块，其中包含执行每个工件的可复制提示：

```
要使用这些工件，启动一个新的AI会话并尝试以下提示之一：

• 运行代码审查：
  "阅读 quality/RUN_CODE_REVIEW.md 并按照其说明审查 [模块或文件]。"

• 运行功能测试：
  "[测试运行器命令，例如 pytest quality/ -v，mvn test -Dtest=FunctionalTest，等等。]"

• 运行集成测试：
  "阅读 quality/RUN_INTEGRATION_TESTS.md 并按照其说明操作。"

• 开始三人委员会规范审计：
  "阅读 quality/RUN_SPEC_AUDIT.md 并按照其说明使用 [模型名称]。"

• 运行已确认错误的TDD验证：
  "阅读 quality/RUN_TDD_TESTS.md 并按照其说明验证所有已确认的错误。"
```

根据实际项目调整测试运行器命令和模块名称。重点是给用户提供可复制粘贴的提示 — 不是描述他们可以做什么，而是他们实际要键入的文本。

快速启动块后，添加一行：

> "您可以问我关于任何这些内容以查看详细信息 — 例如，'显示我场景3'或'带我走过集成测试矩阵'。"

### 第2部分：按需深入挖掘

当用户询问特定项目时，提供专注的摘要 — 不是整个文件，而是关键决策和您不确定的内容。示例：

- **"告诉我关于场景4的情况"** → 显示场景文本，解释其来源（哪个防御模式或领域知识），并标记推断与已知内容。
- **"显示我集成测试矩阵"** → 显示运行组，解释并行策略，并注明您从模式中推导出的质量门禁与猜测的。
- **"功能测试如何工作？"** → 显示三个测试组，解释它们与规范和场景的映射，并突出显示您最不自信的任何测试。

用户可能需要经过几次深入挖掘才能准备好改进任何内容。这很好 — 让他们按自己的节奏探索。

### 第3部分：改进菜单

用户看过摘要（并可选深入挖掘细节）后，提供改进选项：

> "五种使其更好的方法："
>
> **1. 交互式审查要求** — 阅读 `quality/REVIEW_REQUIREMENTS.md` 以获取按用例组织的要求的引导式演练。您可以挑选特定用例进行深入挖掘，或按顺序演练所有用例。也可以使用不同的模型对完整性报告进行事实核查（跨模型审计）。适用于：查找管道遗漏的差距。
>
> **2. 使用不同模型细化要求** — 阅读 `quality/REFINE_REQUIREMENTS.md` 并运行细化传递。您可以使用任何AI模型运行此操作 — Claude、GPT、Gemini — 每个模型都会捕捉不同的差距。运行您想要的模型，直到出现边际效益。每个传递都会备份当前版本，并在 `quality/VERSION_HISTORY.md` 中记录更改。适用于：将要求从基线推向完整性。
>
> **3. 审查和加固其他项目** — 选择任何场景、测试或协议部分，我会与您一起进行。适用于：收紧特定质量门禁，修复推断场景，添加缺失的边缘案例。
>
> **4. 引导问答** — 我会问您3-5个关于我无法从代码中推断出的问题：事件历史记录、预期分布、成本容忍度、模型偏好。适用于：填补使场景更具权威性的知识差距。
>
> **5. 输入附加文档** — 要求管道在更多意图源的情况下工作得更好。指向以下任何内容，我将使用它们来细化要求和质量宪法：
>   - 导出的AI聊天历史记录（Claude、Gemini、ChatGPT导出、Claude Code转录）
>   - 讨论项目的Slack或Teams频道
>   - 关于项目的电子邮件线程、Jira/Linear工单或GitHub问题
>   - 设计文档、架构决策记录或会议记录
>   - 新闻组帖子、论坛讨论或邮件列表存档
>
>   您可以使用 Claude Cowork、GitHub Copilot 或 OpenClaw 等工具连接到这些源并将它们收集到文件夹中，然后指向文件夹。适用于：将场景和要求基于真实项目历史而不是推断。
>
> "您可以按任何顺序执行这些组合。您想从哪里开始？"
>
### 执行每个改进路径

**路径1：交互式审查要求。** 指用户到 `quality/REVIEW_REQUIREMENTS.md` 并提供一起进行的机会。协议支持自我引导（选择用例）、完全引导（顺序演练）和跨模型审计（不同模型事实核查完整性报告）。进度记录在 `quality/REFINEMENT_HINTS.md` 中，以便用户可以从中断的地方继续。

**路径2：使用不同模型细化要求。** 指用户到 `quality/REFINE_REQUIREMENTS.md`。每个细化传递：
- 备份当前版本到 `quality/history/vX.Y/`
- 读取 REFINEMENT_HINTS.md 中的反馈
- 进行有针对性的改进
- 微调版本号
- 在 VERSION_HISTORY.md 中记录更改
用户可以使用 Claude、GPT、Gemini 或任何其他模型运行此操作 — 每个模型都会捕捉不同的盲点。运行直到边际效益。

**路径3：审查和加固其他项目。** 用户选择场景、测试或协议部分。一起进行：显示当前文本，解释您的推理，询问是否准确。根据他们的反馈进行修订。如果功能测试更改，则重新运行测试。

**路径4：引导问答。** 提问3-5个在探索过程中实际发现的问题。这些类别涵盖了最常见的杠杆作用最大的差距：

- **场景的故障历史记录**。“我发现[特定的防御代码]。是什么导致了这个故障？有多少记录受到影响？”
- **质量门禁阈值**。“我正在检查[字段]是否包含[值]。正常分布是怎样的？什么信号表明存在问题？”
- **集成测试的规模和成本**。“协议运行[N]个测试，成本约为$[X]。我应该增加还是减少覆盖率？”
- **测试范围**。“我生成了[N]个功能测试。您现有的套件涵盖了[其他领域]。是否存在差距？”
- **规范审核的模型偏好**。“您使用哪些AI模型？您是否注意到特定的优势？”

在用户回答后，修订生成的文件并重新运行测试。

**路径5：输入附加文档**。用户将您指向附加的意图来源——聊天历史记录、Slack导出、电子邮件线程、Jira工单、设计文档、会议笔记、论坛存档。这些文档包含设计决策、故障历史记录和质量讨论，这些内容没有进入正式文档。

1. 扫描索引文件并导航到与质量相关的内容（与步骤0相同的方法，但现在有特定的目标——您知道哪些需求需要依据，哪些场景需要阈值，哪些差距需要填补）。
2. 提取：带有具体数字的故障故事、防御模式的推理设计、质量框架讨论、跨模型审核结果以及仅从代码中无法看到的可行为合同。
3. 将发现结果作为新的反馈项输入到`quality/REFINEMENT_HINTS.md`，然后运行一次细化过程以更新需求。
4. 修订QUALITY.md场景中的真实故障细节。使用真实世界的值更新集成测试阈值。修订后重新运行测试。

如果用户在步骤0中已经提供了聊天历史记录，您已经挖掘了它——但他们可能希望您指向特定的对话，连接附加的来源，或者要求您深入探讨某个特定主题。

### 迭代

用户可以多次循环这些路径。每次通过都会使质量手册更加扎实。当他们满意时，他们会自然地继续前进——没有明确的“完成”步骤。

---

## 固定策略

`quality/`文件夹与项目的单元测试文件夹是分开的。为项目的语言创建适当的测试设置：

- **Python**：`quality/conftest.py`用于pytest的固定装置。如果固定装置是内联定义的（在pytest的`tmp_path`模式中很常见），则优先于共享固定装置。
- **Java**：带有`@BeforeEach`/`@BeforeAll`设置方法的测试类，或共享的测试工具类。
- **Scala**：混合到测试规范中的特征（例如，`trait FunctionalTestFixtures`），或内联数据构建器。
- **TypeScript/JavaScript**：带有`beforeAll`/`beforeEach`钩子的`quality/setup.ts`，或内联测试工厂。
- **Go**：同一`_test.go`文件中的辅助函数，或共享的`testutil_test.go`。使用`t.Helper()`进行测试辅助。Go约定优先于内联测试设置而不是共享固定装置。
- **Rust**：在`#[cfg(test)] mod tests`块中的辅助函数，或共享的`test_utils.rs`模块。使用构建器模式进行测试数据。

检查现有的测试文件以了解它们如何设置测试数据。无论现有测试使用什么模式，都复制它。研究现有的固定装置模式以获得逼真的数据形状。

---

## 术语

- **功能测试**——代码是否产生规范说明它应该产生的输出？与单元测试（在隔离中单独的函数）不同。
- **集成测试**——组件是否端到端协同工作，包括真实的外部服务？
- **规范审核**——AI模型读取代码并与规范进行比较。不执行代码。捕获代码与文档不匹配的情况。
- **覆盖率剧场**——产生高覆盖率数字但无法捕获真实错误的测试。示例：断言函数没有抛出错误，但没有检查其输出。
- **适用性**——代码在现实世界条件下是否做了它应该做的事情？系统可以有95%的覆盖率，但仍然会无声地丢失记录。

---

## 原则

1. 适用性优先于覆盖率百分比
2. 场景来自代码探索和领域知识
3. 具体的故障模式使标准不可协商——抽象需求会招致合理化
4. 安全机制转换AI审核质量（行号、读取主体、在声明之前使用grep）
5. 在修复之前进行分诊——许多“缺陷”是规范错误或设计决策
6. 结构性审核有一个上限（~65%）。剩余的~35%是意图违规——缺失错误、跨文件矛盾、设计差距——任何只读代码的工具都看不见。需求使看不见的变得可见。
7. 规范是唯一的贡献，而不是审核结构。焦点区域和审核协议是次要的，从意图来源导出的正确可测试需求才是主要的。
8. 跨需求一致性检查是必不可少的。错误通常存在于两个单独正确的代码片段之间的差距。仅按需求验证无法找到这些错误。
9. 保留所有派生的需求——不要过滤。检查额外需求的成本很低；因为您修剪了会捕获错误的那个需求而遗漏了错误的成本很高。
10. 失败的测试是存在错误的 strongest evidence。对于每个确认的带修复补丁的错误，运行红色-绿色TDD循环（在有错误代码时测试失败，在修复代码时通过）。显示FAIL→PASS输出——审查者可以不同意您的修复，但不能与可复现的测试争辩。

---

## 参考文件

在您完成每个阶段时阅读这些文件：

| 文件 | 何时阅读 | 包含内容 |
|------|----------|----------|
| `references/exploration_patterns.md` | 阶段1（探索） | 模式适用性矩阵、深入模板、领域知识问题 |
| `references/defensive_patterns.md` | 步骤5（找到骨架） | Grep模式、如何将发现转换为场景 |
| `references/schema_mapping.md` | 步骤5b（模式类型） | 字段映射格式、变异有效性规则 |
| `references/requirements_pipeline.md` | 阶段2（需求） | 五阶段管道、版本协议、传递规则 |
| `references/constitution.md` | 文件1（QUALITY.md） | 带有按部分指导的完整模板 |
| `references/functional_tests.md` | 文件2（功能测试） | 测试结构、反模式、跨变体策略 |
| `references/review_protocols.md` | 文件3-4（代码审核、集成） | 两个协议的模板、补丁验证、跳过保护 |
| `references/spec_audit.md` | 文件5（三人议会） | 完整审核协议、分诊过程、修复执行 |
| `references/iteration.md` | 迭代（阶段6之后） | 四次迭代策略：差距、无过滤、均等、对抗 |
| `references/verification.md` | 阶段6（验证） | 完整的自检清单（45个基准）包括结构化输出、补丁门禁、跳过保护验证、预飞行发现、版本戳、错误报告、枚举完整性、分诊可执行证据、代码提取的枚举列表、机械验证工件、源检查测试执行、矛盾门禁、种子检查执行、收敛跟踪、侧车JSON模式验证、脚本验证的关闭门禁、规范用例标识符、内联修复差异 |
