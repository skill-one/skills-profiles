# 记忆合并器

您将一个领域记忆文件中的成熟学习内容合并到其指令文件中，确保知识保留且冗余最小。

**使用待办事项列表**来跟踪流程步骤的进度，并通知用户。

## 范围

记忆指令可以存储在两个范围中：

- **全局** (`global` 或 `user`) - 存储在 `<global-prompts>` (`vscode-userdata:/User/prompts/`)，适用于所有 VS Code 项目
- **工作区** (`workspace` 或 `ws`) - 存储在 `<workspace-instructions>` (`<workspace-root>/.github/instructions/`)，仅适用于当前项目

默认范围是 **全局**。

在本提示中，`<global-prompts>` 和 `<workspace-instructions>` 指代这些目录。

## 语法

```
/memory-merger >领域名称 [范围]
```

- `>领域名称` - 必须项。要合并的领域（例如，`>clojure`、`>git-workflow`、`>prompt-engineering`）
- `[范围]` - 可选。`global`、`user`（两者都表示全局）、`workspace` 或 `ws` 之一。默认为 `global`

**示例：**
- `/memory-merger >prompt-engineering` - 合并全局提示工程记忆
- `/memory-merger >clojure workspace` - 合并工作区 clojure 记忆
- `/memory-merger >git-workflow ws` - 合并工作区 git-workflow 记忆

## 流程

### 1. 解析输入并读取文件

- **提取** 用户输入中的领域和范围
- **确定** 文件路径：
  - 全局：`<global-prompts>/{domain}-memory.instructions.md` → `<global-prompts>/{domain}.instructions.md`
  - 工作区：`<workspace-instructions>/{domain}-memory.instructions.md` → `<workspace-instructions>/{domain}.instructions.md`
- 用户可能输入了错误的领域，如果找不到记忆文件，请在该目录中进行模糊匹配并确定是否有匹配项。如有疑问，请向用户请求输入。
- **读取** 两个文件（记忆文件必须存在；指令文件可能不存在）

### 2. 分析并提议

审查所有记忆部分，并呈递合并考虑：

```
## 提议合并的记忆

### 记忆：[标题]
**内容：** [要点]
**位置：** [在指令中的位置]

[更多记忆]...
```

说：“请审查这些记忆。使用 'go' 批准所有，或指定要跳过的部分。”

**停止并等待用户输入。**

### 3. 定义质量标准

建立 10/10 的标准，用于定义构成优秀合并结果的指令：

1. **零知识损失** - 保留所有细节、示例和细微差别
2. **最小冗余** - 合并重叠的指导
3. **最大可扫描性** - 清晰的层次结构、平行结构、策略性加粗、逻辑分组

### 4. 合并并迭代

开发最终合并的指令 **但尚未更新文件**：

1. 起草合并的指令，包含批准的记忆
2. 对照质量标准进行评估
3. 优化结构、措辞、组织
4. 重复直到合并的指令达到 10/10 标准

### 5. 更新文件

一旦最终合并的指令达到 10/10 标准：

- **创建或更新** 指令文件，包含最终合并的内容
  - 创建新文件时包含正确的 frontmatter
  - 如果两个文件都存在，**合并 `applyTo` 模式**，确保全面覆盖且无重复
- **删除** 合并的记忆部分

## 示例

```
用户: "/memory-merger >clojure"

代理：
1. 读取 clojure-memory.instructions.md 和 clojure.instructions.md
2. 提议 3 个记忆进行合并
3. [停止]

用户: "go"

代理：
4. 定义 10/10 的质量标准
5. 合并新的指令候选，迭代至 10/10
6. 更新 clojure.instructions.md
7. 清理 clojure-memory.instructions.md
```
