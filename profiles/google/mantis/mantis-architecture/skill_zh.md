# 架构 (/mantis-architecture)

## 系统目标

知识库综合器。将学习队列（`workspace/learnings.jsonl`）中的临时见解和代码库的结构分析翻译成规范化的、相互链接的 Markdown 知识库（`workspace/kb/`）。

## 命令定义

- **命令:** `/mantis-architecture`
- **描述:** 通过定义系统架构、映射特定实体（组件）和分类历史漏洞模式来构建知识库的基础。
- **参数（所有可选；由 LOCATOR RESOLUTION / 块 A 解析）:**
  `--snapshot_root=<dir>`（或 `SNAPSHOT_ROOT` 环境变量）— 要从中读取目标源代码的固定代码快照；`--snapshot_id=<id>` — 该快照的 `SNAPSHOT_ID`；`--state_root=<dir>` — 所有状态和知识库路径的父目录；`--target_root=<dir>` — 一个已经准备好的树，覆盖快照（很少传递到此阶段）。如果没有传递，行为是字节对字节地使用今天的（降级/未固定）：从当前目录读取源代码并将 `snapshot_pinned` 视为 false。

## 输入/输出契约

- **读取**:
  - `workspace/learnings.jsonl`（当前轮次的原始见解）。
  - `workspace/historical_learnings.jsonl`（可选，过去的漏洞元数据）。
  - 代码库目录结构和关键源文件。
  - `workspace/kb/` 中现有的 Markdown 文件（用于验证/衰减检查）。
  - `workspace/.mantis_state.json`（用于检索通过次数）。
  - `workspace/.mantis_state.json` → `active_snapshot` (`root`, `snapshot_id`, `snapshot_pinned`) 和 `snapshot_history` — 知识库新鲜度门控（步骤 0b）的证据。仅从状态中读取快照；永远不要运行实时 VCS 命令（`git`/`hg`/`repo`）来决定知识库的时效性。
  - `workspace/.mantis_state.json` → `kb_snapshot_id`（当前知识库最后一次构建时使用的 `SNAPSHOT_ID`；在首次/遗留知识库中不存在）。
  - `workspace/.mantis_state.json` → `changed_files` 和 `changed_files_status`（由 mantis-plan 的块 E 写入；被作用域知识库失效在步骤 0b 结果 3 中消耗。从第 2 轮开始存在，但可能已过时（在先前的轮次中写入）— 作用域路径检查 `changed_files_pass` 对 `state.pass_number`，如果不同则回退到完整重建。）
- **写入**:
  - `workspace/kb/` 下的 Markdown 文件（`architecture.md`, `entities/[component_name].md`, `vulnerabilities/[CWE-ID].md`, `index.md`）。
  - `workspace/kb/dependencies.json` — 在架构分析期间提取的导入/依赖边界的 JSON 映射（键 = 相对于 CODE_ROOT 的源文件路径；值 = 导入/依赖于键文件的其他文件数组）。这被 `mantis-plan` 的依赖感知扩散（第 2 阶段）消耗。如果代码库没有可解析的导入结构，则写入 `{}`。在作用域失效期间仅重新派生已更改的条目（见下文结果 3）。
  - 将 `workspace/learnings.jsonl` 归档到 `workspace/archive/learnings/learnings_pass_${N}_${X}.jsonl`。
  - 每个要（重新）写入的 KB 文件（`index.md`, 每个 `entities/*.md`, 每个 `vulnerabilities/*.md`）的第一行添加一个 `<!-- KB_SNAPSHOT: <SNAPSHOT_ID> -->` 标记，并在 `workspace/.mantis_state.json` 中将 `kb_snapshot_id` 设置为 `SNAPSHOT_ID`。
  - 将整个 KB 树的不可变每次通过副本复制到 `workspace/archive/kb/kb_pass_${N}_${X}/`（以便后续撤销的修复不能默默删除第 N 次通过时 KB 声称的记录）。
- **前提条件**:
  - `workspace/learnings.jsonl` 必须存在。
- **幂等性保证**:
  - 事务性：只有在程序验证所有 KB Markdown 更新都成功写入后，才会将 `workspace/learnings.jsonl` 移至存档。KB 文件就地覆盖。

## 指令

分析代码库和待处理的学习，以构建一个永久性的、基于 Markdown 的记忆库，供未来代理使用。

按以下方式执行架构阶段：

0. **LOCATOR RESOLUTION（块 A，下方内联）:**

```
LOCATOR RESOLUTION（在读取任何目标代码或工件之前）:
0. 角色：如果此技能永远不会读取目标源（报告、校准、反映），则为仅发现结果的阶段：跳过步骤 2-6；仍然从状态中读取 active_snapshot 以进行证据/注释；永远不要因为代码根未设置而停止。
1. 确定 CODE_ROOT，按此优先级顺序：
   a. 如果在本次调用中传递了 `--target_root`，CODE_ROOT = `--target_root`。它是权威的，覆盖 SNAPSHOT_ROOT 和状态回退（在调用者将准备好的树（例如修补的阴影）交给你时使用）。
   b. 否则，如果传递了 `--snapshot_root`（或 SNAPSHOT_ROOT），使用它。
   c. 否则，读取状态根 `workspace/.mantis_state.json`（如果传递了 `--state_root`，则相对于当前目录的 `./workspace/...`）-> active_snapshot.root / .snapshot_id / .snapshot_pinned。
   d. 否则（没有参数且没有可读的 active_snapshot）：CODE_ROOT = 当前目录，将 snapshot_pinned 视为 false（模式关闭）。不要停止。
2. SENTINEL CHECK（仅当 snapshot_pinned 为 true 且你没有采取路径 1a 时）：
   验证 CODE_ROOT/.mantis_snapshot_id 存在且等于 SNAPSHOT_ID。如果缺失或不同 -> 停止 "snapshot sentinel mismatch"。（--target_root 树（1a）故意被修改，并且是 sentinel 免责的。）
3. PATH 字段：
   - SNAPSHOT-RELATIVE（在 CODE_ROOT 下读取）：code_paths 条目；plan 目标文件是文件路径。仅删除尾部的 ":<digits>"。包含 "://" 的 code_paths 条目是 URL/端点，不是文件读取。不是 <现有路径>:<整数> 形式的 code_paths 条目是非源定位器（符号/偏移/端点）：仅检查工件/符号是否存在；跳过所有行范围和行存在逻辑。
   - STATE-RELATIVE（在状态根 `workspace` 下读取/写入，永远不要以 CODE_ROOT 为前缀）：
     kb_references, repro_file_path, reattack_file_path, 帮助脚本、报告文件，以及所有状态/发现 JSON。
4. 当 snapshot_pinned 为 true 时，永远不要在 CODE_ROOT 下写入。任何编译、生成或写入工件的命令都必须在 CODE_ROOT 的私有阴影副本中运行（从 CODE_ROOT 使用 mktemp -d），永远不会以 cwd=CODE_ROOT 运行。只读检查可以 cd 到 CODE_ROOT。
5. VCS-METADATA 切割：历史日志提取和在 LIVE 仓库根（仍然有 .git/.hg/.repo）中运行的任何 VCS diff/blame 命令，而不是 CODE_ROOT（快照副本会删除 VCS 元数据）。不要因为 CODE_ROOT 缺少 .git/.hg/.repo 而停止。
6. 每个 shell 命令使用绝对路径，并在调用时设置它自己的工作目录。不要假设工作目录在调用之间持久存在。
```

这是一个读取代码的阶段（步骤 2 和 4 读取目标源），因此块 A 的步骤 1-6 都适用；它不是仅发现结果的。在执行以下任何操作之前，从状态中解析 `CODE_ROOT`、`SNAPSHOT_ID` 和 `snapshot_pinned`。根据块 A 步骤 3，所有 `workspace/kb/...` 路径都是 STATE-RELATIVE：在 `state_root/workspace` 下读取和写入它们，永远不要在 `CODE_ROOT` 下。在 `CODE_ROOT` 下读取所有目标源。不要运行任何 VCS 命令来决定知识库的新鲜性（块 A 步骤 5 的切割仅用于历史/ diff/blame，此阶段不使用）。

0b. **KB 快照新鲜度门控（机械；仅状态 + KB 标记，无实时 VCS）:**

````
- `CUR` = `SNAPSHOT_ID`（由块 A 解析；如果 `active_snapshot` 缺失则为空字符串）。`PINNED` = `snapshot_pinned`（如果缺失则为 false）。
- **模式关闭短路（3 状态规则）:** 如果状态中 `active_snapshot` 缺失（模式关闭 — 未请求 `--sync`），完全跳过新鲜度门控：对 `CODE_ROOT` 进行最佳努力构建/更新，不要添加任何过时的横幅，并且
  不要标记 `kb_snapshot_id`。这是字节对字节今天的默认行为。（只有 HALT 和 PINNED 运行下面的门控。）
- `KB_ID` = `.mantis_state.json` 中的 `kb_snapshot_id` 值（主要）；否则是 `state_root/workspace/kb/index.md` 第一行 `KB_SNAPSHOT:` 后面的文本（如果该文件存在）（次要回退，用于没有状态的遗留运行）；否则 `""`（没有先前的 KB）。状态是主要的，这样文件标记陷阱（第一行被注释包裹，没有 `-->` 删除）永远不会让 `KB_ID` 与注释更近并强制每次通过都构建新鲜。）
- 通过字符串检查精确选择一个结果，从上到下，第一个匹配的胜出：
  1. `PINNED` 为 false（HALT 模式 — `active_snapshot` 存在但未固定）-> **过时 / HALT。** 对 `CODE_ROOT` 进行最佳努力构建/更新，但将过时横幅（如下）作为 `index.md` 的第一行添加。不要声称时效性：保留横幅。设置 `kb_snapshot_id` = `CUR`（一个 `live:` ID）。
  2. 否则 `KB_ID` == `CUR`（两者非空） -> **当前。** 执行增量更新 + 衰减检查（步骤 4）如今天。在所有（重新）写入的文件上重新标记 `KB_SNAPSHOT: CUR`。删除 `index.md` 中之前添加的任何过时横幅。
  3. 否则（`PINNED` 为 true 且 (`KB_ID` 为空 OR `KB_ID` != `CUR`)) -> **构建新鲜（完整或作用域重新架构）。** 固定的代码自知识库构建以来已推进（同步 / 通过边界更改），或知识库未标记/遗留。选择完整或作用域：
     - **作用域失效（第 2 阶段增量效率）:** 如果 `changed_files_status` 已知（不是 UNKNOWN）并且 KB 已经有 `KB_SNAPSHOT` 标记（KB_ID 非空，只是不同）并且 `changed_files_pass` 等于当前 `state.pass_number`（差异来自本次通过，而不是过时的先前通过 — 缺失或不同 → 视为 UNKNOWN → 下方完整重建），尝试作用域重建：仅使源文件在 `changed_files` 中的 KB 条目失效，加上它们的父级汇总依赖项（导入/引用已更改文件的知识库实体）。仅从 `CODE_ROOT` 重新派生这些条目；保留所有其他 KB 条目不变（它们针对的是相同的代码，只是不同的快照 ID）。在所有（重新）写入的文件上重新标记 `KB_SNAPSHOT: CUR`。
        - **父级汇总（2 跳，匹配 plan 的 fan-out）:** 当为已更改文件 F 失效 KB 条目时，还要失效任何直接引用 F 的 KB 条目（1 跳）以及引用 F 的 1 跳依赖项的条目（2 跳）。这匹配 `mantis-plan` 的依赖感知 fan-out（最多扩展 2 跳），确保一个孙辈实体（H 导入 G，G 导入已更改的 F）不会被保留过时，并在其依赖项已更改时将其作为 `kb_reference` 提供。
       - **安全阀:** 如果出现任何不确定性（无法确定哪些 KB 条目映射到哪些源文件，KB 结构不明确，或 `changed_files` 为空但 `KB_ID` != `CUR`），回退到下方的完整重建。永远不要保留已更改文件的过时条目。
     - **完整重建（第 1 阶段回退）:** 如果 KB_ID 为空（没有先前的 KB），或 `changed_files_status` 为 UNKNOWN，或作用域失效安全阀触发，从 `CODE_ROOT` 从头开始重建每个 KB 文件。不要保留你这次通过没有从 `CODE_ROOT` 重新派生的任何先前的断言。标记 `KB_SNAPSHOT: CUR`。删除任何过时横幅。
- **过时横幅（粘贴原文，替换 `<KB_ID>` 和 `<CUR>`；保持每一行的开头 `>` 以便它作为可见块引用渲染）:

  ```
  > **过时 KB 警告 — 未经重新验证不要信任。**
  > snapshot_pinned=false，或知识库构建自不同的快照。
  > KB_SNAPSHOT=<KB_ID> 与 active_snapshot.snapshot_id=<CUR> 不匹配。
  > 以下每个 SECURE/FIXED/NON_VIABLE/SAMPLE_OR_TEST 声明都未针对当前代码进行验证。在信任之前重新验证；不要基于此 KB 过滤、跳过或降优先级工作。
  ```
````

1. **读取收件箱（`workspace/learnings.jsonl` 和 `workspace/historical_learnings.jsonl`）:**

   - 解析 `workspace/learnings.jsonl` 的内容（如果存在 `workspace/historical_learnings.jsonl`，也解析它）。提取所有轨迹见解、发现的漏洞、可行的崩溃路径和已验证的补丁。

2. **分析源代码边界:**

   - 检查 `CODE_ROOT`（由块 A 解析的固定快照）下的目录结构和关键源文件（使用块 A 步骤 6 的绝对路径，并且不要运行 VCS 命令）。根据存储库的内容动态识别系统的核心组件、接口和信任边界。这适用于所有领域：无论是软件系统（例如，识别解析器、控制器或网络守护程序）、硬件/RTL 设计（例如，识别 IP 模块、JTAG 接口或内存控制器）、基础设施即代码（例如，识别云权限、VPC 边界或部署描述符），还是数据/ML 管道（例如，识别数据入口点、模型序列化机制或训练边界）。

3. **构建或更新知识库 (KB):**

   - 使用标准 Markdown 创建或更新 `workspace/kb/` 目录中的文件。遵循以下严格路径：

     - `workspace/kb/architecture.md`：高级数据流、区域定义、系统设计和整体可用性/正常运行时间要求（如果记录或可从 systemd、kubernetes 或负载均衡器等配置中推断）。
     - `workspace/kb/entities/[component_name].md`：组件的特定定义（例如，`auth_module.md`）。必须包括与相关漏洞类链接，并记录已知约束（例如，“此模块清理输入 X”）。记录组件的关键性和可用性要求（如果适用，将其分类为 CRITICAL、STANDARD 或 LOW_CRITICALITY）。在此处包含轨迹见解。
     - `workspace/kb/vulnerabilities/[CWE-ID_or_BugClass].md`：历史上与此代码库相关的漏洞类（例如，`CWE-79.md` 或 `Memory-Corruption.md`）的描述，包括示例说明什么不应该做。
     - `workspace/kb/index.md`：包含到上述每个文件链接和 1 行摘要的根目录。这是规划器将读取的地图。

   - **重要格式规则**：使用相对链接跨参考实体和漏洞（例如，
     `[Auth Module](entities/auth_module.md)`）。确保所有 markdown 文件简洁，专注于可操作的安全上下文。

   - **快照标记（在运行新鲜度门控时每个（重新）写入的 KB 文件上必须标记，即 HALT 或 PINNED；永远不会在模式关闭中）:** 使 `index.md`、每个 `entities/*.md` 和每个 `vulnerabilities/*.md` 的第一行正好为 `<!-- KB_SNAPSHOT: <SNAPSHOT_ID> -->`（替换 `CUR` 来自步骤 0b；它是一个 HTML 注释，所以不会渲染）。这是下次通过的新鲜度门控（步骤 0b）检测漂移的方法。**模式关闭门控（3 状态规则）:** 如果 `active_snapshot` 缺失（模式关闭 — 未请求 `--sync`），不要标记每个文件的 `KB_SNAPSHOT` 标记：`CUR` 是空字符串（如果 `active_snapshot` 缺失），所以强制的标记将是 `<!-- KB_SNAPSHOT:  -->`（空值）— 一个快照时代的产品，它在第 1 阶段不存在。每个文件标记仅由步骤 0b 的新鲜度门控消耗，该门控跳过模式关闭完全 (`arch:147-152`: "完全跳过新鲜度门控... 这是字节对字节今天的行為。只有 HALT 和 PINNED 运行下面的门控。")。此模式关闭门控镜像下方的新鲜度门控逻辑和步骤 0b 的结果子句，这些子句仅在 HALT/PINNED 结果中提到每个文件的 `KB_SNAPSHOT: CUR` 标记。

   - **每个文件的 `KB_SNAPSHOT` 标记是 KB 断言的唯一证据机制。** 不要写入每个断言 `(AS_OF:<snapshot>)` 标签 — `AS_OF` 重新验证读取器从未构建，并且过时保护已经由新鲜度门控（步骤 0b）比较 `kb_snapshot_id` 到 `SNAPSHOT_ID`，加上每个发现的 `discovery_commit`（由 `mantis-critic` 块 B 强制）。一个后续撤销的修复是通过这些机制捕获的，而不是通过每个断言标签。

4. **验证和衰减知识（漂移预防）:**

   - 当代码被修补或重构时，知识会过时。在最终确定 KB 更新之前，在现有的 `workspace/kb/entities/` 中对断言进行快速检查，以与 `CODE_ROOT` 下（固定快照 — 不是实时 VCS 查询，也不是实时工作树）的源进行对比。在 **构建新鲜** 结果（步骤 0b）中，不要进行任何快速检查：丢弃先前的断言，并在此通过中从 `CODE_ROOT` 重新派生每个实体。在 **过时 / HALT** 结果中，仅进行最佳努力快速检查，无论结果如何都保留过时横幅。
   - 如果实体文件声称变量未清理（基于旧学习），但当前代码现在包含清理函数（因为修补程序已着陆），**删除或更正 KB 中的过时学习**。
   - 如果学习被当前轨迹见解反复证明是错误的，积极纠正它，以防止“错误学习”持续存在并使未来代理失明。
   - 当你纠正或重新确认派生自发现的断言时，重新标记该 KB 文件的 `KB_SNAPSHOT` 标记。

5. **事务性收件箱清除和存档:**

   - 为了防止无限循环和令牌膨胀，你必须清除队列并存档学习。
   - **验证和最终确定：** 程序验证所有 Markdown KB 更新是否成功写入磁盘，以及交叉引用是否有效。还验证，在提交之前，每个（重新）写入的 KB 文件都以其 `<!-- KB_SNAPSHOT: <SNAPSHOT_ID> -->` 标记开头，并且每个发现派生的裁决都基于当前的 `SNAPSHOT_ID`。
   - **通过移动提交：** 只有在验证合成成功后，才将 `workspace/learnings.jsonl` 移动到存档目录：
     - 确保目标目录存在（例如，
       `mkdir -p workspace/archive/learnings/`）。
     - 通过读取 `"pass_number"` 从 `workspace/.mantis_state.json` 确定循环通过次数 `N`。如果缺失或无效，扫描 `workspace/archive/` 以查找匹配 `findings_pass_N` 或 `loopN_findings` 的文件夹，并解析 `N` 为 `max_found + 1`，如果不存在存档则默认为 1。
     - 通过计算 `workspace/archive/learnings/` 中匹配 `learnings_pass_${N}_*.jsonl` 的现有文件数量并加 1 来确定子索引 `X`。
     - 移动文件：
       `mv workspace/learnings.jsonl workspace/archive/learnings/learnings_pass_${N}_${X}.jsonl`.
   - **快照 KB（每次通过存档）：** 在成功合成后，将整个 KB 树复制到每次通过存档：
     - 确保目录存在 (`mkdir -p workspace/archive/kb/`)。
     - 计算子索引 `X_kb` = (在 `workspace/archive/kb/` 中现有 `kb_pass_${N}_*` 目录的数量) + 1。
     - 复制（不要移动 — 活的 `workspace/kb/` 必须持久存在以供下次通过使用）：`cp -a workspace/kb/. workspace/archive/kb/kb_pass_${N}_${X_kb}/`.
   - **标记状态：** 将 `kb_snapshot_id` = `SNAPSHOT_ID` (`CUR` 来自步骤 0b) 写入 `workspace/.mantis_state.json`。如果 `active_snapshot` 缺失（模式关闭），不要写入 `kb_snapshot_id` 并不要在 `index.md` 中添加任何过时横幅（新鲜度门控被跳过）。在 HALT 模式下，写入 `kb_snapshot_id` = `CUR` 并保留 `index.md` 中的过时横幅。
   - 如果合成失败或中断，保留 `workspace/learnings.jsonl` 在其原始位置完整，以确保没有数据丢失。
   - 如果在输入时 `workspace/learnings.jsonl` 缺失（例如，第 15 轮调用，因为第 2 轮调用已经在此通过中存档了它），仅跳过学习移动；仍然运行新鲜度门控（步骤 0b），标记 `KB_SNAPSHOT` 标记，写入 `kb_snapshot_id`，并复制每个通过 KB 存档。必须记录 KB 证据的每个调用。

完成时，通知用户。
