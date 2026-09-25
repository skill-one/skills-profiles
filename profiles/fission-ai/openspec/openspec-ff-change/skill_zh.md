快速跳过工件创建过程 - 一次性生成所有所需内容以开始实施。

**存储库选择**：如果用户指定了存储库（存储库是注册在此机器上的独立 OpenSpec 仓库）或工作存在于其中，运行 `openspec store list --json` 以发现已注册的存储库 ID，然后在读取或写入规范的命令（`new change`、`status`、`instructions`、`list`、`show`、`validate`、`archive`、`doctor`、`context`、`schemas`、`view`）中传递 `--store <id>`。选择后，将 `--store <id>` 视为工作流程其余部分的粘性选项。下面未限定范围的示例命令是简写：在运行它之前，附加该标志。例如，运行 `openspec status --change "<name>" --json --store "<id>"`，而不是下面显示的无限定范围形式。其他命令不接受该标志。命令打印的提示信息已经包含该标志；在后续操作中保持它。没有存储库时，命令作用于最近的本地 `openspec/` 根目录。

**项目检查**：这些步骤期望一个已经使用 OpenSpec 的项目。在第一个写入任何内容的步骤（`new change`、`archive`、`sync specs` 或编写工件文件）之前，确认项目有一个根：运行 `openspec list --json`（选择存储库时使用 `--store <id>`，因为存储库是根）并读取 `root`。根对象表示项目已设置。“root”: null 表示未设置 - 这里没有 `openspec/` 目录，并且 `openspec new change` 会作为副作用创建一个。该命令退出非零，这是答案而不是损坏的 CLI，因此请读取 JSON 而不是重试或绕过它。

一个 `"root": null` 不是关于设置：当 `status` 错误消息以 `Declared in` 或 `Invalid store declaration in` 开头并命名此项目的 `openspec/config.yaml`（或 `config.yml`）时，项目通过它声明的存储库使用 OpenSpec，而此机器无法解析（存储库未注册，或 `store:` 行格式不正确）。不要将其视为未初始化并跳过下面的分支：在写入之前停止并显示该错误的 `message` 和 `fix`。

否则，没有根时，接下来会发生什么取决于如何到达此工作流程：

- **自动选择**：您自己选择了此工作流程，而用户没有指定 OpenSpec、指定此技能或运行其斜杠命令。停止使用 OpenSpec 并像没有安装 OpenSpec 时一样正常回答请求。不要让他们设置任何内容，也不要提及 OpenSpec 设置。
- **显式 OpenSpec 请求**：用户指定了 OpenSpec、指定了此技能或运行了其斜杠命令。在写入之前停止并询问如何继续：设置此项目（`openspec init`）、目标他们已有的存储库（`--store <id>`）或继续不使用 OpenSpec 处理此请求。等待他们的回答。

在这两个分支中，永远不要作为副作用创建根：直到用户要求它之前，不要运行 `openspec init`，不要手动创建 `openspec/` 文件，并且不要让命令创建它。

**输入**：用户的请求应包含变更名称（蛇形命名法）或他们想要构建内容的描述。

**步骤**

1. **如果未提供明确输入，询问他们想要构建什么**

   向用户（开放式，无预设选项）提问：
   > "您想处理哪个变更？描述您想要构建或修复的内容。"

   从他们的描述中推导出蛇形命名法名称（例如，"添加用户身份验证" → `add-user-auth`）。

   **重要**：在理解用户想要构建什么之前，不要继续。

2. **创建变更目录**
   ```bash
   openspec new change "<name>"
   ```
   这会在 CLI 解析的规划主页创建一个脚手架变更。

3. **获取工件构建顺序**
   ```bash
   openspec status --change "<name>" --json
   ```
   解析 JSON 以获取：
   - `applyRequires`：实现前需要的工件 ID 数组（例如，`["tasks"]`）
   - `artifacts`：所有工件的列表，每个工件都有其 `status` 和其 `requires` 边（它直接依赖的工件 ID）
   - `planningHome`、`changeRoot`、`artifactPaths` 和 `actionContext`：路径和范围上下文。使用这些而不是假设仓库本地路径。

4. **创建所需集中的每个工件**

   使用待办列表跟踪通过工件的进度。

   按依赖顺序（没有待处理依赖的工件首先）循环遍历工件：

   a. **对于每个 `ready`（依赖满足）的工件**：
      - 获取指令：
        ```bash
        openspec instructions <artifact-id> --change "<name>" --json
        ```
      - 指令 JSON 包括：
        - `context`：项目背景（对您约束 - 不要包含在输出中）
        - `rules`：工件特定规则（对您约束 - 不要包含在输出中）
        - `template`：用于输出文件的结构
        - `instruction`：针对此工件类型的模式特定指导
        - `skipped`/`warning`：当变更声明 `skip_specs` 且此工件必须不创建时出现 - 停止并选择另一个工件
        - `resolvedOutputPath`：写入工件的解析路径或模式
        - `dependencies`：完成的工件以供上下文读取
      - 读取任何完成的依赖文件以供上下文 - 始终从磁盘重新读取，即使您之前在对话中看到过它们（用户可能已编辑它们）
      - **在起草前检查相关项目**：首先读取 `context` 和 `rules`，然后检查相关实现、附近测试、配置和 `openspec/` 外的文档。保持检查只读且与变更成比例；重用对后续工件的发现，仅在需要时检查更多。
        - 从请求和项目上下文中识别目标项目；规划主页可能与代码分离。如果目标不明确，请询问。对于绿野或非代码变更，检查可用结构和相关文档。如果源不可用，说明限制并询问何时会影响计划。
        - 将范围、方法和任务基于您发现的内容进行定位。区分观察到的行为与假设和提议的添加；而不是默默地决定哪个是正确的，揭示与现有规范的冲突。
        - 现在执行此发现，而不是为实施留下通用的“探索代码库”或“制定计划”任务。保持任何必要的后续调查特定于未解决的问题。
      - 如果 `instruction` 字段将创建委托给特定技能或命令，调用它以生成工件，而不是自己编写文件，然后验证工件文件存在于 `resolvedOutputPath`
      - 否则，使用 `template` 作为结构创建工件文件并将其写入 `resolvedOutputPath`。如果 `resolvedOutputPath` 是通配符，遵循 `instruction` 选择具体文件路径
      - 应用 `context` 和 `rules` 作为约束 - 但不要将它们复制到文件中
      - 显示简要进度：“✓ 创建了 <artifact-id>”

   b. **继续直到所需集中的每个工件都存在（不仅仅是 `apply.requires`）**
      - 创建每个工件后，重新运行 `openspec status --change "<name>" --json`
      - 所需集是 `applyRequires` 加上通过 `status --json` 中的 `requires` 边从这些工件可达的每个工件 - 递归地遍历（规范驱动的关闭覆盖提议、规范、设计、任务）。忽略该集中之外的工件
      - `status` 仅文件存在，所以 `applyRequires` 工件读取 `done` 并不表示其依赖存在 - 早期编写 `tasks.md` 标记 `tasks` 完成，而 `specs` 从未编写。使用每个工件的 `requires` 边，而不是其 `status`，来构建所需集：`done` 工件仍然列出了它依赖的内容
      - 已经读取 `status: "skipped"` 的工件已满足：变更在 `.openspec.yaml` 中声明 `skip_specs`，因此其文件必须不存在。永远不要尝试创建一个
      - 创建所需集中缺失的每个工件，然后重新检查 - 创建一个可以解锁其他工件
      - 仅当 `status` 已经报告它 `skipped`，或当其自己的 `instruction` 说它是条件性的时才跳过：运行 `openspec instructions <artifact-id> --change "<name>" --json` 并仅在它的 `instruction` 字段将其标记为可选（例如，“仅当...创建”）时才跳过。Spec-driven 的 `design.md` 合格；`specs` 仅通过上述 `skipped` 状态合格，永远不会通过您自己的判断。告诉用户，并且不要重新考虑它
      - 依赖项是使能器，不是门：如果所需工件仍然 `blocked` 只是因为您跳过了一个条件依赖，仍然编写它
      - 当每个所需集中的工件都是 `done`、`skipped` 或故意跳过时停止

   c. **如果工件需要用户输入**（关键上下文不明确）：
      - 询问用户澄清
      - 然后继续创建

5. **显示最终状态**
   ```bash
   openspec status --change "<name>"
   ```

**输出**

完成所有工件后，总结：
- 变更名称和位置
- 创建的工件列表及其简要描述，以及任何跳过的条件工件及其原因
- 准备情况：“所有实现所需的工件已准备就绪。”
- 提示：“运行 `/openspec-apply-change` 或让我实施以开始处理任务。”

**工件创建指南**

- 遵循 `openspec instructions` 的 `instruction` 字段为每个工件类型提供权威指导，即使对于熟悉的工件名称也是如此
- 如果 `instruction` 字段指导您使用特定技能或命令创建工件，调用它而不是直接编写工件
- 模式定义了每个工件应包含的内容 - 遵循它
- 在创建新工件之前读取依赖工件以供上下文
- 使用 `template` 作为输出文件的结构 - 填写其部分
- **重要**：`context` 和 `rules` 是对您的约束，而不是文件的 内容
  - 不要将 `<context>`、`<rules>`、`<project_context>` 块复制到工件中
  - 这些指导您编写的内容，但绝不应出现在输出中

**守卫**
- 创建 apply 阶段递归依赖的每个工件，而不仅仅是 `apply.requires` 中列出的 ID
- 始终在创建新工件之前读取依赖工件 - 从磁盘重新读取，而不是从对话内存中（文件可能自上次看到以来已更改）
- 如果上下文关键不明确，请询问用户 - 但优先做出合理决定以保持势头
- 如果已存在同名变更，建议继续该变更
- 在继续到下一步之前，验证每个工件文件是否存在
