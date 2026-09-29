---
name: openspec-bulk-archive-change
description: 一次性归档多个已完成的OpenSpec变更。适用于归档多个并行变更。也适用于复数归档请求 - "openspec bulk-archive"、"opsx bulk-archive"、"openspec archive all"或"openspec archive these changes"。
---

批量归档多个已完成变更。

这项技能允许您批量归档变更，通过检查代码库智能处理规范冲突。

**存储选择**：如果用户命名了存储（存储是注册在此计算机上的独立 OpenSpec 仓库）或工作存在于其中，运行 `openspec store list --json` 以发现注册的存储 ID，然后在读取或写入规范的命令（`new change`、`status`、`instructions`、`list`、`show`、`validate`、`archive`、`doctor`、`context`、`schemas`、`view`）中传递 `--store <id>`。选择后，将 `--store <id>` 视为工作流程其余部分的粘性参数。以下命令的每个无作用域示例都是简称：在运行它之前，附加该标志。例如，运行 `openspec status --change "<name>" --json --store "<id>"`，而不是下面显示的无作用域形式。其他命令不接受该标志。命令打印的提示信息已经包含该标志；在后续操作中保留它。如果没有存储，命令将作用于最近的本地 `openspec/` 根目录。

**项目检查**：这些步骤期望一个已经使用 OpenSpec 的项目。在第一个写入任何内容（`new change`、`archive`、`sync specs` 或创建工件文件）的步骤之前，确认项目具有根目录：运行 `openspec list --json`（如果选择了存储，请使用 `--store <id>`，因为存储现在是根目录），并读取 `root`。根对象表示项目已设置。`"root": null` 表示未设置 - 这里没有 `openspec/` 目录，并且 `openspec new change` 会作为副作用创建一个。该命令退出非零状态，这是答案而不是损坏的 CLI，因此请读取 JSON 而不是重试或绕过它。

一个 `"root": null` 并不是关于设置：当 `status` 错误消息以 `Declared in` 或 `Invalid store declaration in` 开头并命名此项目的 `openspec/config.yaml`（或 `config.yml`）时，该项目通过它声明的存储使用 OpenSpec，而此计算机无法解析（存储未注册，或 `store:` 行格式不正确）。不要将其视为未初始化并跳过以下分支：在写入之前停止并显示该错误的 `message` 和 `fix`。

否则，如果没有根目录，接下来会发生什么取决于如何到达此工作流程：

- **自动选择**：您自己选择了此工作流程，而用户没有命名 OpenSpec、命名此技能或运行其斜杠命令。停止使用 OpenSpec 并像没有安装 OpenSpec一样正常回答请求。不要要求他们设置任何内容，也不要提及 OpenSpec 设置。
- **显式 OpenSpec 请求**：用户命名了 OpenSpec、命名了此技能或运行了其斜杠命令。在写入之前停止并询问如何进行：设置此项目（`openspec init`）、目标他们已有的存储（`--store <id>`）或为此请求不使用 OpenSpec 继续进行。等待他们的回答。

在这两种分支中，永远不要作为副作用创建根目录：直到用户要求它之前，不要运行 `openspec init`，不要手动创建 `openspec/` 文件，也不要让命令创建它。

`<capability-path>` 是相对于 `specs/` 的规范目录（例如，`user-auth` 或 `identity/user-auth`）。在解析其主规范时保留从每个 delta 规范获取的完整路径。

**输入**：无需（提示选择）

**步骤**

1. **获取活动变更**

   运行 `openspec list --json` 获取所有活动变更。

   如果没有活动变更，通知用户并停止。

2. **提示选择变更**

   要求用户选择变更（多选）：
   - 显示每个变更名称和任务状态（来自列表输出）
   - 包括“所有变更”的选项
   - 允许任意数量的选择（1+ 有效，2+ 是典型用例）

   **重要**：不要自动选择。始终让用户选择。

   **在批量验证之前，为选定的根目录加载当前的归档输入一次**：

   从此根目录中选择一个选定的变更，并运行
   `openspec instructions archive --change "<selected-change>" --json` 并使用相同的选定根目录标志。此查找是建议性的且可选的：它仅提供额外的提示输入，因此必须永远不会阻塞批量。如果它失败或返回无效的 JSON——例如在还不支持此命令的旧 CLI 上——继续批量操作，不提供上下文和操作指导。不要报告错误并停止。

   有效响应可能省略 `context` 和 `operationGuidance`。将 `context` 视为跨批量的必需提示级输入：读取并考虑它，并应用相关的项目事实、约定和约束。将 `operationGuidance` 视为可选的附加建议：读取并考虑每个条目，并遵循适用且与内置批量工作流程兼容的条目。

   将两个字段与冲突分析、显式用户选择、解析路径、CLI 检查和命令契约分开。如果上下文与其中一个控制输入冲突，请报告冲突并保留控制值。如果指导不适用或与控制输入冲突，请不要遵循它并解释原因。不要从这两个字段推断跳过的提示、替换路径或标志，也不要将它们的文本逐字复制到规范、变更或摘要中。这些是提示级行为契约，不是可执行的检查。

3. **批量验证 - 为所有选定的变更收集状态**

   使用相同的选定根目录标志运行一次 `openspec list --json` 以获取任务进度。如果查找失败、返回无效的 JSON 或省略任何选定的变更、包含重复的选定变更或返回无效计数，请报告问题并在同步或归档批量之前停止。

   对于每个选定的变更，收集：

   a. **工件状态** - 运行 `openspec status --change "<name>" --json`
      - 解析 `schemaName`、`artifacts`、`planningHome`、`changeRoot`、`artifactPaths` 和 `actionContext`
      - 注意哪些工件是 `done` 而其他状态

   b. **任务完成** - 查找列表响应中的 `changes` 条目，其 `name` 与此变更完全匹配
      - 要求非负整数 `totalTasks` 和 `completedTasks`，且 `completedTasks <= totalTasks`
      - 不完整的任务 = `totalTasks - completedTasks`
      - CLI 解析规范的跟踪任务文件，包括自定义工件名称、输出路径和通配符
      - 不要从工件状态、工件 ID 为 `tasks` 或缺少顶层 `tasks.md` 推断任务完成
      - CLI 仅计算 `x`/`X` 复选标记为完成；其他标记保持不完整
      - 如果 `totalTasks` 为零，记为“无任务”

   c. **Delta 规范** - 检查状态 JSON 中的 `artifactPaths.specs.existingOutputPaths`
      - 列出哪些能力规范存在
      - 对于每个规范，提取要求名称（匹配 `### Requirement: <name>` 的行）
      - 将此列表视为唯一的 delta 规范源。如果 `specs` 条目缺失或列表为空，则对该变更不执行规范同步或规范指令查找；不要从无关工件推断 delta。
      - 独立地针对每个变更评估此内容，包括混合架构批量的情况，其中某些架构没有 `specs` 工件。

   d. **归档目标** - 一次计算每个变更的目标名称并记录为该变更的 `<target-name>`
      - 当变更名称已经以 `YYYY-MM-DD-` 前缀开头时，使用变更名称本身；否则，添加当前日期作为 `YYYY-MM-DD-<name>`（与 `openspec archive` 的规则相同）
      - 检查 `<planningHome.changesDir>/archive/<target-name>` 是否已存在
      - 如果存在，或另一个选定的变更解析到相同的目标名称，请将每个此类变更标记为 `Blocked` 并显示 `归档目录已存在`
      - 被阻止的变更永远不会同步或移动：在步骤 6 表中显示为 `Blocked`，将其排除在冲突解决之外（使用其他变更解决其冲突），并在步骤 8d 中记录为失败
      - 在写入任何主规范之前检查这里，与 `openspec archive` 匹配：在同步后发现的冲突将导致重写主规范，而归档从未发生

4. **检测规范冲突**

   构建一个以 `<capability-path>` 为键的映射：

   ```text
   identity/user-auth -> [change-a, change-b]  <- 冲突（2+ 变更）
   billing/user-auth  -> [change-c]            <- 正常（不同的完整路径）
   ```

   当 2+ 选定的变更有 delta 规范时，存在冲突。

5. **代理解决冲突**

   **对于每个冲突**，调查代码库：

   a. **从每个冲突变更中读取 delta 规范** 以了解每个变更声称要添加/修改的内容

   b. **搜索代码库** 以查找实现证据：
      - 查找实现每个 delta 规范要求的代码
      - 检查相关文件、函数或测试

   c. **确定解决方案**：
      - 如果只有一个变更实际实现 -> 同步该变更的规范
      - 如果两个都实现 -> 按时间顺序应用（旧的优先，新的覆盖）
      - 如果都没有实现 -> 跳过规范同步，警告用户

   d. **记录解决方案** 以每个冲突：
      - 每个 delta 规范的包含或排除决策，按变更和 `<capability-path>` 键
      - 要应用和按什么顺序应用的包含 delta 规范
      - 因为其实现缺失而从同步中排除的 delta 规范
      - 代码库中找到的依据

6. **显示合并状态表**

   显示一个总结所有变更的表：

   ```markdown
   | 变更              | 工件 | 任务 | 规范   | 冲突 | 状态 |
   |---------------------|-------|-------|---------|-----------|--------|
   | schema-management   | 完成 | 5/5   | 2 delta | 无      | 准备  |
   | project-config      | 完成 | 3/3   | 1 delta | 无      | 准备  |
   | add-oauth           | 完成 | 4/4   | 1 delta | identity/user-auth (!) | 准备* |
   | add-verify-skill    | 1 剩余 | 2/5   | 无    | 无      | 警告   |
   ```

   对于冲突，显示解决方案：
   ```text
   * 冲突解决方案：
     - identity/user-auth 规范：将先应用 add-oauth 然后应用 add-jwt（两者都实现，按时间顺序）
   ```

   对于不完整的变更，显示警告：
   ```text
   警告：
   - add-verify-skill: 1 个不完整的工件，3 个不完整的任务
   ```

7. **确认批量操作**

   向用户提出一个确认问题：

   - "归档 N 个变更？" 选项基于状态
   - 选项可能包括：
     - "归档所有 N 个变更"
     - "仅归档 N 个准备好的变更（跳过不完整）"
     - "取消"

   如果有不完整的变更，请明确它们将带有警告归档。

   根据意图而不是确切标签进行路由——您编写了这些标签，因此请匹配用户的选择而不是上面的措辞：
   - "取消" — 停止，不归档。报告未归档任何内容并跳过其余步骤。
   - 归档所有选项 — 继续进行每个选定的变更，该变更不是 `Blocked`
   - 仅准备选项 — 仅进行步骤 6 表中标记为 `Ready` 或 `Ready*` 的变更，并将其余变更记录为步骤 8d 中的跳过，除了 `Blocked` 变更，它们保持失败并带有 `归档目录已存在`。如果 `Ready*` 变更的冲突伙伴被跳过，请使用仅要归档的变更重新推导该冲突的解决方案。
   - 任何其他内容 — 询问而不是归档

   在步骤 8 写入第一个主规范或移动任何变更之前，获取确认批量中每个必需的规范规则快照。对于将要同步具体 `artifactPaths.specs.existingOutputPaths` 的每个变更，使用相同的选定根目录标志运行一次 `openspec instructions specs --change "<name>" --json`。在第一个写入或移动之前获取所有快照。如果任何查找退出非零状态或返回无效的工件指令 JSON，请识别受影响的变更，报告错误，并在任何主规范写入或变更移动之前停止整个批量。不要将查找失败视为省略的规则。有效的响应而 `rules` 不存在是无规则的情况。

8. **为每个确认的变更执行归档**

   在处理之前，将步骤 5（在步骤 7 重新推导之后）记录的决策转换为两个每个 delta 集合：
   - `includedDeltas`：来自确认变更的所有非冲突 delta 规范加上为同步选择的冲突 delta
   - `excludedDeltas`：因其实现缺失而从确认变更中排除的冲突 delta
   - 一个变更可以同时具有包含和排除的 delta 规范。保持每个 delta 的决策；不要将其合并为每个变更的同步标志。

   按确定的顺序处理变更（尊重冲突解决）：

   a. **同步包含的 delta 规范**：
      - 仅对 `includedDeltas` 中的变更运行 `openspec-sync-specs` 工作流（代理驱动的智能合并），传递仅包含的 delta 路径，并明确指示它忽略该变更的 `excludedDeltas`。等待它完成。
      - 对于冲突，按解析顺序应用。
      - 将该变更获取的规范规则快照传递到内联同步；内联同步必须重用它而不再次获取指令
      - 仅将工件规则应用于该变更生成的主规范。它们不会改变冲突解决、归档行为或 CLI 合约，并且它们的文本不会逐字复制到输出文件
      - 不要委托给后台任务——步骤 8c 会将 `changeRoot` 从仍在读取它的同步中移除。
      - 如果一个变更没有包含的 delta 规范，不要为它运行同步工作流。

   b. **在移动 `changeRoot` 之前验证包含的 delta 规范**：
      - 仅对 `includedDeltas` 中的 delta 规范重新运行比较，与 `<planningHome.root>/openspec/specs/<capability-path>/spec.md` 中的主规范（使用步骤 3 状态 JSON 中的存储感知 `planningHome.root`，而不是硬编码的仓库路径）进行比较。
      - 验证主规范已更新：
        - ADDED 要求存在
        - MODIFIED 要求携带 delta 中命名的场景和描述更改，其其他场景完整
        - REMOVED 要求消失——并且当此同步退役了能力（删除了其最后一个要求，留下 `## Requirements` 为空）时，其主规范被删除而不是留空；同步故意保留并报告的规范也是匹配的
        - RENAMED 要求以新名称存在并在旧名称下不存在
      - 不要验证 `excludedDeltas` 中的 delta 规范；它们有意不同步。
      - 如果同步失败或任何能力不匹配验证，报告差异并失败/跳过移动该变更的 `changeRoot`——不要归档该变更。`changeRoot` 保持完整。

   c. **执行归档**：

      目标名称：使用步骤 3d 为此变更记录的 `<target-name>`，保持不变。在这里永远不要重新计算它：运行到午夜后的批量将检查一个日期在步骤 3，然后移动到另一个日期。

      **检查目标是否已存在**：
      - 在移动之前立即再次检查，即使步骤 3 已经检查：目标可以在批量中期间出现
      - 如果是：将此变更记录为失败并带有 `归档目录已存在`，将 `changeRoot` 保留在原地，报告它已经为该变更同步的任何主规范，并继续处理剩余的变更
      - 如果不是：将 `changeRoot` 移动到归档目录

      ```bash
      mkdir -p "<planningHome.changesDir>/archive"
      mv "<changeRoot>" "<planningHome.changesDir>/archive/<target-name>"
      ```

**确认移动操作未嵌套：** `mv` 即使在检查后目标出现，也会退出状态码 0，将变更移动到其 *内部*。如果 `<planningHome.changesDir>/archive/<目标名称>/<变更目录名称>` 现在存在（`changeRoot` 的最后一个路径段），将此目录移回 `changeRoot` 并记录此变更失败，错误信息为 `归档目录已存在`。切勿报告其已归档。

   d. **跟踪每个变更的结果**：
      - 成功：成功归档
      - 失败：归档过程中出错或规范验证失败（记录错误）
      - 跳过：用户选择不归档（如适用）
      - 同步跳过：对于 `excludedDeltas` 中的每个增量，报告 `sync skipped` 并附带变更、`<能力路径>` 和记录的原因。这与跳过归档不同。

9. **显示摘要**

   显示最终结果：

   ```markdown
   ## 批量归档完成

   归档了 3 个变更：
   - schema-management-cli -> archive/2026-01-19-schema-management-cli/
   - project-config -> archive/2026-01-19-project-config/
   - add-oauth -> archive/2026-01-19-add-oauth/

   跳过了 1 个变更：
   - add-verify-skill（用户选择不归档不完整的）

   规范同步摘要：
   - 4 个增量规范同步到主规范
   - 1 个增量规范同步跳过（add-jwt, identity/user-auth: 实现未找到）
   - 1 个冲突已解决（identity/user-auth: 同步了 add-oauth，跳过了 add-jwt）
   ```

   如果有任何失败：
   ```text
   失败了 1 个变更：
   - some-change: 归档目录已存在
   ```

**冲突解决示例**

示例 1：仅一个已实现
```text
冲突：<planningHome.root>/openspec/specs/auth/spec.md 被 [add-oauth, add-jwt] 修改

检查 add-oauth：
- 增量添加了 "OAuth 提供商集成" 要求
- 搜索代码库... 找到 src/auth/oauth.ts 实现 OAuth 流

检查 add-jwt：
- 增量添加了 "JWT 令牌处理" 要求
- 搜索代码库... 未找到 JWT 实现

解决：仅 add-oauth 已实现。将仅同步 add-oauth 规范。
```

示例 2：两个都实现了
```text
冲突：<planningHome.root>/openspec/specs/api/spec.md 被 [add-rest-api, add-graphql] 修改

检查 add-rest-api（创建于 2026-01-10）：
- 增量添加了 "REST 端点" 要求
- 搜索代码库... 找到 src/api/rest.ts

检查 add-graphql（创建于 2026-01-15）：
- 增量添加了 "GraphQL 模式" 要求
- 搜索代码库... 找到 src/api/graphql.ts

解决：两个都实现了。将首先应用 add-rest-api 规范，
然后应用 add-graphql 规范（按时间顺序，较新的优先）。
```

**成功时的输出**

```markdown
## 批量归档完成

归档了 N 个变更：
- <变更-1> -> archive/<目标名称-1>/
- <变更-2> -> archive/<目标名称-2>/

规范同步摘要：
- N 个增量规范同步到主规范
- 无冲突（或：M 个冲突已解决）
```

**部分成功时的输出**

```markdown
## 批量归档完成（部分）

归档了 N 个变更：
- <变更-1> -> archive/<目标名称-1>/

跳过了 M 个变更：
- <变更-2>（用户选择不归档不完整的）

失败了 K 个变更：
- <变更-3>: 归档目录已存在
```

**无变更时的输出**

```markdown
## 无需归档的变更

未发现活动变更。创建新变更以开始。
```

**约束条件**
- 允许任意数量的变更（1+ 是可以的，2+ 是典型用例）
- 始终提示选择，从不自动选择
- 早期检测规范冲突并通过检查代码库解决
- 当两个变更都实现时，按时间顺序应用规范
- 仅当实现缺失时才跳过规范同步（警告用户）
- 在确认前显示每个变更的清晰状态
- 对整个批次使用单一确认
- 用户取消确认后永不归档——已取消的批次不会归档任何内容
- 跟踪并报告所有结果（成功/跳过/失败）
- 移动到归档时保留 .openspec.yaml
- 归档目录目标使用当前日期，在步骤 3d 中计算一次并在移动时重用：YYYY-MM-DD-<名称>；如果名称已以 `YYYY-MM-DD-` 前缀开头，则直接使用（永不叠加第二个日期）
- 如果归档目标存在，则失败该变更但继续处理其他变更
- 在第一个主规范写入前，步骤 3 中检查每个归档目标；目标存在的变更永远不会同步或移动
- 如果请求同步，为每个变更以 agent 驱动的方式内联运行 `openspec-sync-specs` 工作流，包含增量规范
- 将每个增量的 `includedDeltas` 和 `excludedDeltas` 决策带入执行；仅同步和验证包含的增量
- 将每个排除的增量报告为 `sync skipped`，而不将归档本身视为跳过
- 规范同步仍在进行时永不归档变更——内联运行同步并在移动 `changeRoot` 前在 `<planningHome.root>/openspec/specs/<能力路径>/spec.md` 验证主规范
- 在规范检查或移动前，为每个选定的根一次性获取归档输入
- 在批次的第一个主规范写入或移动前获取所有必需的 specs-rule 快照
- 归档输入查找失败不会阻止批次；它将无上下文或指导继续进行
- 规范指令查找失败将原子性地停止整个批次
- 没有 concrete `artifactPaths.specs.existingOutputPaths` 的变更将不进行规范同步
- 跨批次应用相关运行时上下文并报告冲突
- 操作指导保持建议性；考虑每个条目并解释拒绝的建议
- 将运行时输入、冲突分析、CLI 派生的值和工件规则分开
- 工件规则仅约束写入的规范
- 从不将运行时输入或工件规则文本逐字复制到输出文件
