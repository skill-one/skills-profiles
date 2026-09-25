从变更中同步 delta 规格到主规格。

这是一个 **代理驱动** 的操作 - 你将读取 delta 规格并直接编辑主规格以应用变更。这允许智能合并（例如，添加场景而不复制整个需求）。

**存储选择**：如果用户命名了一个存储（存储是一个独立于 OpenSpec 仓库的、在本机上注册的存储）或工作存在于其中，运行 `openspec store list --json` 来发现已注册的存储 ID，然后在读取或写入规格和变更的命令（`new change`、`status`、`instructions`、`list`、`show`、`validate`、`archive`、`doctor`、`context`、`schemas`、`view`）中传递 `--store <id>`。一旦选择，将 `--store <id>` 视为整个工作流程中粘性的。下面那些命令的每个未限定示例都是简称：在运行它之前，附加该标志。例如，运行 `openspec status --change "<name>" --json --store "<id>"`，而不是下面显示的未限定形式。其他命令不接受该标志。命令打印的提示已经包含该标志；在后续操作中保持它。没有存储时，命令作用于最近的本地 `openspec/` 根目录。

**项目检查**：这些步骤期望一个已经使用 OpenSpec 的项目。在第一个写入任何内容的步骤（`new change`、`archive`、`sync specs` 或编写工件文件）之前，确认项目有一个根：运行 `openspec list --json`（选择存储时使用 `--store <id>`，因为存储是根）并读取 `root`。根对象表示项目已设置。`"root": null` 表示未设置 - 这里没有 `openspec/` 目录，并且 `openspec new change` 会作为副作用创建一个。该命令退出非零，这是答案而不是损坏的 CLI，因此读取 JSON 而不是重试或绕过它。

一个 `"root": null` 不是关于设置：当 `status` 错误消息以 `Declared in` 或 `Invalid store declaration in` 开头并命名此项目的 `openspec/config.yaml`（或 `config.yml`）时，项目确实通过它声明的存储使用 OpenSpec，但本机无法解析（存储未注册，或 `store:` 行格式不正确）。不要将其视为未初始化并跳过下面的分支：在写入之前停止并显示该错误的 `message` 和 `fix`。

否则，没有根时，接下来会发生什么取决于如何到达此工作流程：

- **自动选择**：你选择了此工作流程，而用户没有命名 OpenSpec、命名此技能或运行其斜杠命令。停止使用 OpenSpec 并像没有安装 OpenSpec 时一样正常回答请求。不要让他们设置任何内容，也不要提及 OpenSpec 设置。
- **明确的 OpenSpec 请求**：用户命名了 OpenSpec、命名了此技能或运行了其斜杠命令。在写入之前停止并询问如何进行：设置此项目（`openspec init`）、目标他们已有的存储（`--store <id>`）或为此次请求不使用 OpenSpec 继续进行。等待他们的回答。

在这两种分支中，永远不要作为副作用创建根：直到用户要求之前不要运行 `openspec init`，不要手动创建 `openspec/` 文件，也不要让命令创建它。

`<capability-path>` 是相对于 `specs/` 的规格目录（例如，`user-auth` 或 `identity/user-auth`）。在解析其主规格时保留每个 delta 规格的完整路径。

**输入**：可选地指定变更名称。如果省略，检查是否可以从对话上下文中推断。如果模糊或歧义，你必须提示可用的变更。

**步骤**

1. **选择变更**

   如果提供了名称，则使用它。否则：
   - 如果用户在对话中提到了变更，则从对话上下文中推断
   - 如果只有一个活动变更，则自动选择
   - 如果歧义，运行 `openspec list --json` 获取可用变更并要求用户选择一个

   提示时，显示具有 delta 规格的变更（在 `specs/` 目录下）。

   总是宣布：`使用变更：<name>` 以及如何覆盖（例如，`/openspec-sync-specs <other>`）。

2. **解析变更上下文**

   运行：
   ```bash
   openspec status --change "<name>" --json
   ```

   JSON 包括 `planningHome.root`。主规格位于 `<planningHome.root>/openspec/specs/` 下 — 使用该（存储感知）根作为下面每个主规格路径，而不是硬编码的仓库路径。当选择存储时，它指向存储，而不是当前仓库。

3. **查找 delta 规格**

   使用状态 JSON 中的 `artifactPaths.specs.existingOutputPaths` 作为 delta 规格路径的唯一来源。如果 `specs` 条目缺失或 `existingOutputPaths` 为空，报告没有要同步的 delta 规格并停止，不要从其他工件中推断它们，也不要请求工件指令或编写主规格。

   同步 `existingOutputPaths` 中的每个路径，除非调用者缩小了该集合。调用者通过命名 `existingOutputPaths` 的完整条目列表来缩小它 — 复制这些绝对值。归档就是这样做的，用户也可以这样做（例如，通过选择以 `/specs/billing/invoices/spec.md` 结尾的条目）。
   然后仅同步命名的路径并将剩余的 delta 规格保持不变：
   批量归档排除它无法找到实现的 delta，并且无论如何同步它将写入调用者故意保留的主规格。
   将该缩小选择传递到步骤 4；永远不要将其扩展回完整列表。如果命名的路径不在 `existingOutputPaths` 中，不要同步它 — 报告它并停止，而不是无声地丢弃它。如果命名的列表为空，报告没有要同步的内容并停止，不编写主规格。

   每个delta 规格文件包含如下部分：
   - `## ADDED Requirements` - 新增的需求
   - `## MODIFIED Requirements` - 现有需求的变更
   - `## REMOVED Requirements` - 要删除的需求
   - `## RENAMED Requirements` - 要重命名的需求（FROM:/TO: 格式）

   如果没有找到 delta 规格则通知用户并停止。

4. **对于每个 delta 规格应用变更到主规格**

   在第一个主规格写入之前，获取一个当前规格规则快照：
   - 如果归档内联调用了此工作流程并从 `openspec instructions specs --change "<name>" --json` 提供了有效的快照，则重用它并不要再获取相同的指令。
   - 否则现在运行该命令一次，使用相同的选定的根标志。
   - 如果直接查找退出非零或返回无效工件指令 JSON，报告错误并在写入任何主规格之前停止。不要将失败视为缺失规则集。
   - 有效响应中省略 `rules` 表示没有配置工件规则，现有的语义合并继续。

   仅将返回的 `rules` 应用于此合并产生的主规格的内容和形式。工件规则不是操作指导，不能更改选定的根、delta 路径、CLI 检查或工作流程步骤。使用其文本作为约束，但不要将其逐字复制到输出文件中。

   对于步骤 3 中选择的每个能力 delta 规格路径（完整的 `existingOutputPaths` 列表，或者当调用者提供了一个缩小的子集时（这些可能属于选定的存储，而不是仓库））：
   a. **读取 delta 规格以理解预期变更**

   b. **读取主规格** 在 `<planningHome.root>/openspec/specs/<capability-path>/spec.md`（可能还不存在）

      **如果它还不存在**（一个新的能力），匹配 `openspec archive` 的行为：
      只能应用 ADDED 需求 - 步骤 d 从它们创建规格。
      MODIFIED 和 RENAMED 没有要应用的需求，因此停止同步该能力并报告其主规格不存在，并且新规格只允许 ADDED。
      REMOVED 没有要删除的内容 - 跳过并警告。

   c. **智能应用变更**：

      **ADDED Requirements:**
      - 如果需求在主规格中不存在 → 添加它
      - 如果需求已存在 → 更新它以匹配（视为隐式 MODIFIED）

      **MODIFIED Requirements:**
      - 在主规格中找到该需求
      - 应用变更 - 这可以是：
        - 添加主规格中还没有的新场景
        - 修改现有场景
        - 更改需求描述
      - 保留 delta 中未提及的任何内容

      **REMOVED Requirements:**
      - 从主规格中删除整个需求块
      - 停用该能力。删除整个 `spec.md` - 并且一旦其中不再有任何其他内容，删除该目录 - 只有当所有这些条件都满足时：
        1. 这次运行删除的需求 *没有留下* 需求块；
        2. 规格的其余部分格式良好（它仍然有 `## Purpose`）；
        3. 主规格在此同步之前不是空的 - 如果你删除了任何内容，则不更改任何内容；
        4. 文件中所有其他非空行都被视为标题、Purpose、Requirements 标题或规范需求的声明、场景或围栏示例；
        5. 变更的 `.openspec.yaml` 声明 `retire_capabilities: true`；
        6. `spec.md` 在真实的规格根内解析（不要跟随能力目录的符号链接以删除外部文件）。
      如果删除选定的需求会导致没有需求块，并且任何停用条件不满足，不要修改主规格。停止同步该能力，报告阻塞条件，并告诉用户如何解决。永远不要写入或留下空的 `## Requirements` 部分。
      当只有标记缺失时，也要说明这一点 - 这是用户可以添加以使停用通过的唯一事情。
      - 删除文件也会删除其 `## Purpose`；任何其他部分都会阻止停用。报告停用时命名 Purpose。仅在规格存在于调用者的签出中时提供可粘贴的 `git checkout`；否则提供签出范围的恢复指导。

      **RENAMED Requirements:**
      - 找到 FROM 需求，重命名为 TO

      **delta 中的 `## Purpose`：**
      - 主规格已经有一个且是权威的 - 不要更改（这是 `openspec archive` 做的；它会警告并继续）

   d. **如果能力还不存在，则创建新的主规格**：
      - 只有当 delta 有要放入的 ADDED 需求且没有 MODIFIED 或 RENAMED 需求阻塞步骤 b 中的该能力时才创建。否则不创建任何内容并保留规格目录不变。对于只有 REMOVED 的 delta，如果变更的 `.openspec.yaml` 声明 `retire_capabilities: true`，报告它已经停用并继续，不重新创建规格。没有该标记，报告同步被阻塞：`openspec archive` 使用 `Spec must have at least one requirement` 拒绝它。空的 delta 没有要同步的操作；也报告它被阻塞。
      - 创建 `<planningHome.root>/openspec/specs/<capability-path>/spec.md`
      - 添加 Purpose 部分：当它有 one 时，逐字复制 delta 的 `## Purpose` 正文（这是 `openspec archive` 做的）；如果没有，则写入一个简短的 TBD 占位符
      - 添加 Requirements 部分与 ADDED 需求
      - 遵循下面的 **主规格格式参考**

5. **验证更新后的主规格**

   运行 `openspec validate --specs` 使用之前相同的选定的根标志。如果验证失败，报告问题并不要声称同步成功。

6. **显示摘要**

   应用所有变更后，总结：
   - 哪些能力被更新
   - 做了什么变更（需求添加/修改/删除/重命名）
   - 任何新的主规格留有 TBD Purpose 占位符，以便现在写入而不是悬置
   - 任何停用的能力，命名删除的 `spec.md`、其 Purpose，以及可粘贴的 `git checkout` 或签出范围的恢复指导

**Delta 规格格式参考**

```markdown
# Spec Delta

## Purpose

仅在引入全新能力的 delta 中出现。为新主规格提供种子。

## ADDED Requirements

### Requirement: New Feature
The system SHALL do something new.

#### Scenario: Basic case
- **WHEN** user does X
- **THEN** system does Y

## MODIFIED Requirements

### Requirement: Existing Feature
The system SHALL keep doing the existing thing, now also handling A.

#### Scenario: Scenario the main spec already has
- **WHEN** user does X
- **THEN** system does Y

#### Scenario: New scenario to add
- **WHEN** user does A
- **THEN** system does B

## REMOVED Requirements

### Requirement: Deprecated Feature

## RENAMED Requirements

- FROM: `### Requirement: Old Name`
- TO: `### Requirement: New Name`
```

**主规格格式参考**

主规格是 delta 合并到的目标。它们永远不会包含 delta 操作标题（`## ADDED/MODIFIED/REMOVED/RENAMED Requirements`）- 同步后，每个需求都位于单个 `## Requirements` 部分下：

```markdown
# <capability> Specification

## Purpose
简短描述此能力的作用及其存在的原因。

## Requirements

### Requirement: New Feature
The system SHALL do something new.

#### Scenario: Basic case
- **WHEN** user does X
- **THEN** system does Y
```

**关键原则：智能合并**

与程序化合并不同，你合并而不是覆盖：
- 一个 MODIFIED 块包含整个需求 - 正文加上所有在变更中存活的场景。`openspec validate` 和 `openspec archive` 都会拒绝丢弃主规格仍然拥有的场景的那个块。
- 保留 delta 未提及的任何内容，并按主规格中的现有顺序排列
- 使用你的判断来合理合并变更

**成功输出**

```markdown
## Specs Synced: <change-name>

Updated main specs:

**<capability-1>**:
- Added requirement: "New Feature"
- Modified requirement: "Existing Feature" (added 1 scenario)

**<capability-2>**:
- Created new spec file
- Added requirement: "Another Feature"

Main specs are now updated. The change remains active - archive when implementation is complete.
```

**约束条件**
- 在做出变更之前读取 delta 和主规格
- 保留 delta 中未提及的现有内容
- 不要将 delta 文件原样复制到主规格中 - 合并其内容，以便主规格保持 **主规格格式参考** 结构，且没有 delta 操作标题
- 如果不清楚，请求澄清
- 显示你正在更改的内容
- 操作应该是幂等的 - 运行两次应该给出相同的结果
- 仅使用 `artifactPaths.specs.existingOutputPaths`；永远不要从无关的工件中推断 delta 规格。
- 尊重调用者提供的 `existingOutputPaths` 子集；永远不要将其扩展回完整列表
- 直接同步时一次获取规格指令，或内联重用归档提供的快照
- 在非零或无效的 JSON 规格指令响应之前停止每个主规格写入
- 工件规则仅约束正在写入的规格，并且永远不会被复制到输出文件中
