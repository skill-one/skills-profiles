继续进行一项更改，通过创建下一个工件。

**存储选择：** 如果用户指定了一个商店（商店是一个独立于 OpenSpec 仓库，并在本机注册的商店）或工作存在于其中，运行 `openspec store list --json` 来发现已注册的商店 ID，然后在读取或写入规范和更改的命令（`new change`、`status`、`instructions`、`list`、`show`、`validate`、`archive`、`doctor`、`context`、`schemas`、`view`）中传递 `--store <id>`。一旦选定，将 `--store <id>` 视为后续工作流程中的粘性选项。下面未限定范围的示例命令是简写：在运行它之前，附加该标志。例如，运行 `openspec status --change "<name>" --json --store "<id>"`，而不是下面显示的未限定范围形式。其他命令不接受该标志。命令打印的提示信息已经包含该标志；在后续操作中保持它。没有商店时，命令作用于最近的本地 `openspec/` 根目录。

**项目检查：** 这些步骤期望一个已经使用 OpenSpec 的项目。在第一个写入任何内容的步骤（`new change`、`archive`、`sync specs` 或编写工件文件）之前，确认项目有一个根：运行 `openspec list --json`（选择商店时使用 `--store <id>`，因为商店是根）并读取 `root`。根对象表示项目已设置。`"root": null` 表示未设置 - 这里没有 `openspec/` 目录，并且写入操作（如 `openspec new change`）会作为副作用创建一个。该命令退出非零状态，这是答案而不是损坏的 CLI，因此请读取 JSON 而不是重试或绕过它。

一个 `"root": null` 并不意味着未设置：当 `status` 错误消息以 `Declared in` 或 `Invalid store declaration in` 开头并命名此项目的 `openspec/config.yaml`（或 `config.yml`）时，该项目通过它声明的商店使用 OpenSpec，但本机无法解析（商店未注册，或 `store:` 行格式不正确）。不要将其视为未初始化并跳过下面的分支：在写入之前停止并显示该错误的 `message` 和 `fix`。

否则，没有根时，接下来会发生什么取决于如何进入此工作流程：

- **自动选择**：您自己选择了此工作流程，而未指定 OpenSpec、指定此技能或运行其斜杠命令。停止使用 OpenSpec 并正常回答请求，就像未安装 OpenSpec 一样。不要让他们设置任何内容，也不要提及 OpenSpec 设置。
- **明确的 OpenSpec 请求**：用户指定了 OpenSpec、指定了此技能或运行了其斜杠命令。在写入之前停止并询问如何进行：设置此项目（`openspec init`）、目标他们已有的商店（`--store <id>`）或为此次请求不使用 OpenSpec。等待他们的回答。

在这两个分支中，永远不要作为副作用创建根：直到用户要求它之前，不要运行 `openspec init`，不要手动创建 `openspec/` 文件，也不要让命令创建它。

**输入**：可选地指定更改名称。如果省略，则检查是否可以从对话上下文中推断。如果模糊或歧义，您必须提示可用的更改。

**步骤**

1. **选择更改**

   如果提供了名称，则使用它。否则：
   - 如果用户在对话中提到了更改，则从对话上下文中推断
   - 如果只有一个活动更改，则自动选择
   - 如果模糊，运行 `openspec list --json` 获取按最近修改时间排序的可用更改，并要求用户选择一个

   当提示时，显示最近修改的 3-4 个更改作为选项，显示：
   - 更改名称
   - 状态（例如，“0/5 任务”、“完成”、“无任务”）
   - 最近修改的时间（从 `lastModified` 字段）

   将最近修改的更改标记为“(推荐)”，因为它可能是用户想要继续的。

   总是宣布：“使用更改：<name>”以及如何覆盖（例如，`/openspec-continue-change <other>`）。

2. **检查当前状态**
   ```bash
   openspec status --change "<name>" --json
   ```
   解析 JSON 以了解当前状态。响应包括：
   - `schemaName`：正在使用的工作流模式（例如，“spec-driven”）
   - `artifacts`：具有其状态（“done”、“skipped”、“ready”、“blocked”）的工件数组
   - `isPlanningComplete`：布尔值，指示所有规划工件是否完成。旧版 CLI 版本将相同的值暴露为 `isComplete`。
   - `planningHome`、`changeRoot`、`artifactPaths` 和 `actionContext`：路径和范围上下文。使用这些而不是假设仓库本地路径。

3. **根据状态采取行动**：

   ---

   **如果所有规划工件都已完成（`isPlanningComplete: true`，或旧版 `isComplete: true`）**：
   - 祝贺用户
   - 显示最终状态，包括使用模式
   - 建议：“规划已完成！您现在可以实施此更改。一旦实施和任何跟踪的工作完成，请存档它。”
   - 停止

   ---

   **如果工件准备创建**（状态显示具有 `status: "ready"` 的工件）：
   - 从状态输出中选择第一个具有 `status: "ready"` 的工件
   - 获取其说明：
     ```bash
     openspec instructions <artifact-id> --change "<name>" --json
     ```
   - 解析 JSON。关键字段是：
     - `context`：项目背景（约束条件，您不要将其包含在输出中）
     - `rules`：特定工件的规则（约束条件，您不要将其包含在输出中）
     - `template`：用于您的输出文件的结构
     - `instruction`：特定模式的指导
     - `resolvedOutputPath`：解析的路径或模式以写入工件
     - `dependencies`：为上下文读取的已完成工件（具有 `skipped: true` 的条目没有文件 - 不要查找它们）
     - `skipped`/`warning`：当更改声明 `skip_specs` 且此工件必须不创建时出现 - 选择另一个工件
   - **创建工件文件**：
     - 读取任何已完成的依赖文件以获取上下文 - 始终从磁盘重新读取它们，即使您之前在对话中看到过它们（用户可能已编辑它们）
     - 如果 `instruction` 字段将创建委托给特定技能或命令，则调用它以生成工件，而不是自己编写文件，然后验证工件文件存在于 `resolvedOutputPath`
     - 否则使用 `template` 作为结构 - 填写其部分
     - 在写入时应用 `context` 和 `rules` 作为约束 - 但不要将它们复制到文件中
     - 写入 `instructions` 中指定的 `resolvedOutputPath`。如果它是 glob 模式，则使用模式指令和更改的上下文选择具体的文件路径
   - 显示已创建的内容和现在解锁的内容
   - 创建一个工件后停止

   ---

   **如果没有工件准备（所有被阻塞）**：
   - 这在有效模式下不应发生
   - 显示状态并建议检查问题

4. **创建工件后显示进度**
   ```bash
   openspec status --change "<name>"
   ```

**输出**

每次调用后显示：
- 哪个工件被创建
- 正在使用的模式工作流
- 当前进度（N/M 完成）
- 现在解锁的工件
- 提示：“要继续吗？只需问我继续或告诉我下一步该做什么。”

**工件创建指南**

工件类型及其目的取决于模式。来自说明输出中的 `instruction` 字段是每个工件的权威指导 - 即使工件具有熟悉的名称（proposal.md、tasks.md 等），也请遵循它，因为自定义模式可能定义不同的内容或相同文件名的不同过程。

如果 `instruction` 字段指示您使用特定技能或命令来创建工件，则调用它而不是直接编写工件。

**约束条件**
- 每次调用创建一个工件
- 在创建新工件之前始终读取依赖工件 - 从磁盘重新读取，而不是从对话内存中读取（文件可能自上次看到以来已更改）
- 永远不要跳过工件或顺序创建
- 如果上下文不明确，请在创建之前询问用户
- 写入后验证工件文件是否存在，然后再标记进度
- 使用模式的工件顺序，不要假设特定的工件名称
- **重要**：`context` 和 `rules` 是您的约束条件，而不是文件的内容
  - 不要将 `<context>`、`<rules>`、`<project_context>` 块复制到工件中
  - 这些指导您要写入的内容，但永远不应出现在输出中
