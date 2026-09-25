# Copilot Spaces

使用 Copilot Spaces 将经过筛选的、针对特定项目的上下文引入对话中。一个 Space 是一个包含仓库、文件、文档和说明的共享集合，它使 Copilot 的响应基于您团队的实际代码和知识。

## 可用工具

### MCP Tools (只读)

| 工具 | 用途 |
|------|---------|
| `mcp__github__list_copilot_spaces` | 列出当前用户可访问的所有空间 |
| `mcp__github__get_copilot_space` | 通过所有者和名称加载空间的完整上下文 |

### 通过 `gh api` 的 REST API (完全的 CRUD)

Spaces REST API 支持创建、更新、删除空间以及管理协作者。MCP 服务器只暴露读取操作，因此请使用 `gh api` 进行写入操作。

**用户空间：**

| 方法 | 端点 | 用途 |
|--------|----------|---------|
| `POST` | `/users/{username}/copilot-spaces` | 创建空间 |
| `GET` | `/users/{username}/copilot-spaces` | 列出空间 |
| `GET` | `/users/{username}/copilot-spaces/{number}` | 获取空间 |
| `PUT` | `/users/{username}/copilot-spaces/{number}` | 更新空间 |
| `DELETE` | `/users/{username}/copilot-spaces/{number}` | 删除空间 |

**组织空间：** 在 `/orgs/{org}/copilot-spaces/...` 下采用相同的模式

**协作者：** 在 `.../collaborators` 处添加、列出、更新和删除协作者

**范围要求：** PAT 需要 `read:user` 进行读取，`user` 进行写入。使用 `gh auth refresh -h github.com -s user` 添加。

**注意：** 此 API 功能正常，但尚未在公共 REST API 文档中。它可能需要 `copilot_spaces_api` 功能标志。

## 何时使用 Spaces

- 用户提到 "Copilot space" 或要求 "加载一个空间"
- 用户希望答案基于特定项目的文档、代码或标准
- 用户询问 "有哪些空间可用？" 或 "为 X 找一个空间"
- 用户需要入职上下文、架构文档或团队特定指南
- 用户希望遵循 Space 中定义的结构化工作流（模板、清单、多步骤流程）

## 工作流程

### 1. 发现空间

当用户询问有哪些空间可用或需要找到正确的空间时：

```
调用 mcp__github__list_copilot_spaces
```

这将返回用户可以访问的所有空间，每个空间都有 `name` 和 `owner_login`。向用户展示相关的匹配项。

要过滤特定用户的空间，请将 `owner_login` 与用户名进行匹配（例如，"显示我的空间"）。

### 2. 加载空间

当用户指定了特定空间或您已找到正确的空间时：

```
调用 mcp__github__get_copilot_space，参数为：
  owner: "org-or-user"    (来自列表的 owner_login)
  name: "Space Name"      (确切的空間名稱，區分大小寫)
```

这将返回空间的完整内容：附加的文档、代码上下文、自定义说明以及任何其他经过筛选的材料。使用此上下文来指导您的回答。

### 3. 跟随面包屑

空间内容通常引用外部资源：GitHub 问题、仪表板、仓库、讨论或其他工具。使用其他 MCP 工具主动获取这些资源以收集完整的上下文。例如：
- 空间引用了一个项目跟踪问题。使用 `issue_read` 获取最新评论。
- 空间链接到一个项目看板。使用项目工具检查当前状态。
- 空间提到了仓库的主计划。使用 `get_file_contents` 读取它。

### 4. 回答或执行

加载后，根据其内容使用空间内容：

**如果空间包含参考材料**（文档、代码、标准）：
- 回答有关项目架构、模式或标准的问题
- 生成符合团队约定的代码
- 使用项目特定知识进行调试

**如果空间包含工作流说明**（模板、逐步流程）：
- 按照空间定义的流程逐步执行
- 从工作流指定的来源收集数据
- 按工作流定义的格式生成输出
- 在每一步显示进度，以便用户可以引导

### 5. 管理空间（通过 `gh api`）

当用户希望创建、更新或删除空间时，请使用 `gh api`。首先，从列表端点找到空间编号。

**更新空间的说明：**
```bash
gh api users/{username}/copilot-spaces/{number} \
  -X PUT \
  -f general_instructions="新的说明..."
```

**一起更新名称、描述或说明：**
```bash
gh api users/{username}/copilot-spaces/{number} \
  -X PUT \
  -f name="更新后的名称" \
  -f description="更新后的描述" \
  -f general_instructions="更新后的说明"
```

**创建新空间：**
```bash
gh api users/{username}/copilot-spaces \
  -X POST \
  -f name="我的新空间" \
  -f general_instructions="帮助我..." \
  -f visibility="private"
```

**附加资源（替换整个资源列表）：**
```json
{
  "resources_attributes": [
    { "resource_type": "free_text", "metadata": { "name": "笔记", "text": "内容..." } },
    { "resource_type": "github_issue", "metadata": { "repository_id": 12345, "number": 42 } },
    { "resource_type": "github_file", "metadata": { "repository_id": 12345, "file_path": "docs/guide.md" } }
  ]
}
```

**删除空间：**
```bash
gh api users/{username}/copilot-spaces/{number} -X DELETE
```

**可更新字段：** `name`, `description`, `general_instructions`, `icon_type`, `icon_color`, `visibility` ("private"/"public"), `base_role` ("no_access"/"reader"), `resources_attributes`

## 示例

### 示例 1：用户请求空间

**用户**: "加载可访问性 copilot 空间"

**操作**：
1. 调用 `mcp__github__get_copilot_space`，所有者 `"github"`，名称 `"Accessibility"`
2. 使用返回的上下文回答有关可访问性标准、MAS 分级、合规流程等问题。

### 示例 2：用户希望找到空间

**用户**: "我们团队有哪些可用的 copilot 空间？"

**操作**：
1. 调用 `mcp__github__list_copilot_spaces`
2. 过滤/展示与用户的组织或兴趣相关的空间
3. 提供加载他们感兴趣的空间的选项

### 示例 3：基于上下文的提问

**用户**: "使用安全空间，我们的密钥扫描政策是什么？"

**操作**：
1. 调用 `mcp__github__get_copilot_space`，使用适当的所有者和名称
2. 在空间内容中找到相关政策
3. 基于实际内部文档回答

### 示例 4：空间作为工作流引擎

**用户**: "使用 PM 周报空间编写我的周报"

**操作**：
1. 调用 `mcp__github__get_copilot_space` 加载空间。它包含模板格式和逐步说明。
2. 遵循空间的工作流：从附加的项目问题中拉取数据，收集指标，起草每个部分。
3. 使用其他 MCP 工具获取空间引用的外部资源（跟踪问题、仪表板）。
4. 在每一步显示草稿，以便用户可以审查和补充内容。
5. 按空间定义的格式生成最终输出。

### 示例 5：程序化更新空间说明

**用户**: "更新我的 PM 周报空间，以包含新的写作指南"

**操作**：
1. 调用 `mcp__github__list_copilot_spaces` 并找到空间编号（例如，19）。
2. 调用 `mcp__github__get_copilot_space` 读取当前说明。
3. 按照要求修改说明文本。
4. 推送更新：
```bash
gh api users/labudis/copilot-spaces/19 -X PUT -f general_instructions="更新后的说明..."
```

## 小贴士

- 空间名称是 **区分大小写的**。使用 `list_copilot_spaces` 中的确切名称。
- 空间可以由用户或组织拥有。始终提供 `owner` 和 `name`。
- 空间内容可能很大（20KB+）。如果作为临时文件返回，使用 grep 或 view_range 找到相关部分，而不是一次性读取所有内容。
- 如果找不到空间，建议列出可用空间以找到正确的名称。
- 空间会随着底层仓库的变化自动更新，因此上下文始终是最新的。
- 一些空间包含自定义说明，应指导您的行为（编码标准、首选模式、工作流）。将这些视为指令，而不是建议。
- **写入操作**（`gh api` 用于创建/更新/删除）需要 `user` PAT 范围。如果写入操作返回 404，请运行 `gh auth refresh -h github.com -s user`。
- 资源更新 **替换整个数组**。要添加资源，请包含所有现有资源和新资源。要删除一个，请在数组中包含 `{ "id": 123, "_destroy": true }`。
