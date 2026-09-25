修订变更的现有规划文档并保持其一致性。切勿编辑代码。

**存储选择**：如果用户指定了商店（商店是注册在此机器上的独立 OpenSpec 仓库）或工作存在于其中，运行 `openspec store list --json` 以发现已注册的商店 ID，然后在读取或写入规范和变更的命令（`new change`、`status`、`instructions`、`list`、`show`、`validate`、`archive`、`doctor`、`context`、`schemas`、`view`）中传递 `--store <id>`。选择后，将 `--store <id>` 视为整个工作流程中粘性参数。以下命令的每个未作用域示例都是简称：在运行它之前，附加该标志。例如，运行 `openspec status --change "<name>" --json --store "<id>"`，而不是下面显示的未作用域形式。其他命令不接受该标志。命令打印的提示信息已经包含该标志；在后续操作中保持它。没有商店时，命令作用于最近的本地 `openspec/` 根目录。

**项目检查**：这些步骤期望一个已经使用 OpenSpec 的项目。在第一个写入任何内容的步骤（`new change`、`archive`、`sync specs` 或创建文档文件）之前，确认项目具有根目录：运行 `openspec list --json`（选择商店时使用 `--store <id>`，因为商店是根目录）并读取 `root`。根对象表示项目已设置。`"root": null` 表示未设置 - 这里没有 `openspec/` 目录，并且 `openspec new change` 会作为副作用创建一个。该命令退出非零状态，这是答案而不是损坏的 CLI，因此请读取 JSON 而不是重试或绕过它。

一个 `"root": null` 并非关于设置：当 `status` 错误消息以 `Declared in` 或 `Invalid store declaration in` 开头并命名为此项目的 `openspec/config.yaml`（或 `config.yml`）时，该项目通过它声明的商店使用 OpenSpec，而此机器无法解析（商店未注册，或 `store:` 行格式不正确）。不要将其视为未初始化并跳过以下分支：在写入之前停止并显示该错误的 `message` 和 `fix`。

否则，没有根目录时，接下来会发生什么取决于如何进入此工作流程：

- **自动选择**：您自己选择了此工作流程，而未指定 OpenSpec、指定此技能或运行其斜杠命令。停止使用 OpenSpec 并正常回答请求，就像未安装 OpenSpec 时一样。不要要求他们设置任何内容，也不要提及 OpenSpec 设置。
- **明确的 OpenSpec 请求**：用户指定了 OpenSpec、指定了此技能或运行了其斜杠命令。在写入之前停止并询问如何进行：设置此项目（`openspec init`）、目标他们已有的商店（`--store <id>`）或继续不使用 OpenSpec 进行此请求。等待他们的回答。

在这两个分支中，切勿作为副作用创建根目录：在用户要求之前不要运行 `openspec init`，不要手动创建 `openspec/` 文件，并且不要让命令创建它。

**输入**：可选地指定变更名称。如果省略，则检查是否可以从对话上下文中推断。如果模糊或歧义，您必须提示可用的变更。

此工作流程修订已存在的文档；`/openspec-continue-change` 是创建不存在的文档的操作。

**步骤**

1. **选择变更**

   如果提供了名称，则使用它。否则：
   - 如果用户在对话中提到了变更，则从对话上下文中推断
   - 如果只有一个活动变更，则自动选择
   - 如果模糊，则运行 `openspec list --json` 获取按最近修改排序的可用的变更，并要求用户选择一个

   提示时，显示最近修改的 3-4 个变更作为选项，显示：
   - 变更名称
   - 状态（例如，“0/5 任务”、“完成”、“无任务”）
   - 最近修改的时间（来自 `lastModified` 字段）

   将最近修改的变更标记为“(推荐)”，因为它可能是用户想要更新的。

   始终宣布：“使用变更：<name>”以及如何覆盖（例如，`/openspec-update-change <other>`）。

2. **获取变更的文档**
   ```bash
   openspec status --change "<name>" --json
   ```
   解析 JSON 以了解当前状态。响应包括：
   - `schemaName`：正在使用的 workflow 规范（例如，“spec-driven”）
   - `artifacts`：其状态的文档数组（“done”、“skipped”、“ready”、“blocked”）
   - `isPlanningComplete`：指示所有规划文档是否完成的布尔值。旧版 CLI 版本将相同的值暴露为 `isComplete`。
   - `planningHome`、`changeRoot`、`artifactPaths` 和 `actionContext`：路径和作用域上下文。使用这些而不是假设仓库本地路径。

   文档 ID 和路径来自活动规范 - 不要假设它们，也不要基于硬编码的文档名称分支。自定义规范必须保持不变。

   要编辑的文件是 `artifactPaths.<id>.existingOutputPaths` - 存在于磁盘上的具体文件，对于 glob 文档已经进行了 glob 展开（例如 `specs/**/*.md`）。不要写入 `resolvedOutputPath`：对于 glob 文档，它仍然是 glob 模式，而不是实际文件。

3. **理解请求**
   - 如果用户要求特定修订（“现在使用 X”），那是起始编辑。
   - 如果他们只说“更新”/“使其一致”，将其视为一致性审查：读取现有文档并检查它们之间是否存在矛盾、缺失和重复。

4. **读取和协调**
   - 读取请求涉及的文档以及变更的其他现有文档。
   - 在对话中起草请求的编辑，而不是在文件中。确切地确定它更改了什么；步骤 5 拥有所有写入。然后检查每个现有文档相对于起草的编辑 - 在任何方向：对后期文档的编辑可能需要修改早期文档，而不仅仅是反过来。构建顺序是有用的阅读顺序，而不是限制可以修订的文档。

   - 记录所有不一致、缺失或矛盾的内容。
   - 对已存在的文件（`existingOutputPaths`）提出修订。如果文档没有现有输出文件且状态为 `ready` 或 `blocked`，记录它并指向 `/openspec-continue-change` 以创建它们。保留 `skipped` 文档不变；不要将它们视为缺失或推迟到继续工作流程。

   - 对于 glob 文档（例如 `specs/**/*.md`），至少匹配一个文件后标记为 `done`，继续工作流程只处理 `ready` 文档。当协调确定 glob 文档的 `existingOutputPaths` 非空时缺少文件：
     1. 运行 `openspec instructions "<artifact-id>" --change "<name>" --json` 并使用其 `instruction` 和 `template`。将 `context` 和 `rules` 视为约束；不要将它们复制到文件中。如果指令报告 `skipped: true`，则不要创建文件。从磁盘读取当前依赖文件；如果缺少必需的非跳过依赖项，则停止并要求用户首先恢复它。
     2. 在 `changeRoot` 内选择一个具体的路径，该路径匹配 `artifactPaths.<id>.outputPath` 且不存在。验证它在解析任何符号链接的父目录后仍然在 `changeRoot` 内。glob `resolvedOutputPath` 不是有效目标。
     3. 在步骤 5 的提议修订中包含新文件，并在用户确认后创建它。
     4. 确认后，立即在创建之前刷新状态和指令。验证文档仍然在作用域内，未被跳过，并且部分填充；重复上述具体路径检查。
     5. 使用创建操作，如果目标已存在则失败。如果 `instruction` 将创建委托给另一个技能或命令，仅在它可以尊重确认的路径和这些约束时调用它；否则停止。如果任何检查失败或确认的草稿不再有效，则停止并与用户协调，而不是替换现有内容或选择不同路径。

   - 如果变更已经一致，则说明并提议不进行修订。

5. **确认并应用，一次一个文档**
   - 此步骤执行此工作流程中的每个文档写入；没有更早的步骤编辑文档。
   - 显示每个提议的修订及其原因，包括步骤 4 中起草的请求编辑。在用户确认后写入。
   - 如果用户拒绝修订，则不要写入它 - 保留该文档不变。
   - 当需要重大重写时，首先获取该文档的规则和模板：
     ```bash
     openspec instructions "<artifact-id>" --change "<name>" --json
     ```

6. **指向下一步（仅提供指导 - 绝对不要执行）**
   - `existingOutputPaths` 为空且状态为 `ready` 或 `blocked` 的文档 -> 建议使用 `/openspec-continue-change` 创建它们。
   - 变更已实现（任务已勾选/已应用）-> 代码可能不再与修订后的计划匹配；建议使用 `/openspec-apply-change` 将增量应用到代码。
   - 一切完成并实现 -> 建议使用 `/openspec-archive-change`。

**输出**

每次调用后显示：
- 修订了哪些文档（以及哪些提议的修订被拒绝）
- 在 glob 文档下创建的任何已部分填充的文件
- 推迟到 `/openspec-continue-change` 的任何内容（没有文件且状态为 `ready` 或 `blocked` 的文档，永远不会是 `skipped` 文档）
- 变更的状态和推荐的下一个命令

**约束条件**
- 仅针对规划文档 - 绝对不要编辑实现代码。如果修订后的计划暗示代码更改，则停止并指向 `/openspec-apply-change`。
- 使用 `openspec status` 报告的文档 ID 和路径；永远不要基于硬编码的文档名称分支。
- 仅编辑 `existingOutputPaths` 中的具体文件；永远不要写入 glob `resolvedOutputPath`。
- 不要推进构建前沿：如果文档的 `existingOutputPaths` 为空且状态为 `ready` 或 `blocked`，那是 `/openspec-continue-change` 的工作。保留 `skipped` 文档不变。唯一的新文件范围是确认的具体路径，该路径在 glob 文档的 `existingOutputPaths` 非空时存在。
- 在写入之前始终与用户确认每个编辑。
- 如果请求更改了变更的 *意图* 而不是细化它，建议使用 `/openspec-new-change`（“更新与重新开始”启发式）。
