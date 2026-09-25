# 创建自定义代理

此技能帮助您创建 VS Code 自定义代理文件，用于定义专门用于开发任务的 AI 角色。自定义代理配置可用的工具、提供专业指令，并且可以通过交接链式调用。

## 使用场景

- 从头开始创建新的自定义代理
- 使用正确的 frontmatter 框架生成 `.agent.md` 文件
- 设置代理到代理的交接以实现多步骤工作流
- 为专业角色（如规划者、审查者等）配置工具限制
- 创建工作区共享或用户配置文件代理

## 不适用场景

- 创建指令文件（使用 `.instructions.md` 代替）
- 创建可重用提示（使用 `.prompt.md` 代替）
- 修改现有代理（直接编辑文件）

## 输入

| 输入 | 必填 | 描述 |
|-------|----------|-------------|
| 代理名称 | 是 | 代理的描述性名称（例如，`planner`、`code-reviewer`） |
| 描述 | 是 | 在聊天中显示的占位符文本的简要描述 |
| 目的/角色 | 是 | 代理扮演的角色以及应如何行为 |
| 工具 | 推荐使用 | 代理可以使用的工具或工具集列表 |
| 交接 | 可选 | 完成工作后要过渡到的下一步代理 |

## 工作流

### 第 1 步：创建代理文件

在 `agents/` 目录中创建一个具有 `.agent.md` 扩展名的文件：

```
agents/<agent-name>.agent.md
```

### 第 2 步：添加 YAML frontmatter

添加包含必需和可选字段的头部：

```yaml
---
name: <agent-name>
description: <聊天占位符的简要描述>
tools:
  - <tool-name>
  - <tool-set-name>
---
```

#### 可用的 frontmatter 字段：

| 字段 | 必填 | 描述 |
|-------|----------|-------------|
| `name` | 否 | 显示名称（默认为文件名） |
| `description` | 是 | 在聊天输入中显示的占位符文本 |
| `argument-hint` | 否 | 指导用户交互的提示文本 |
| `tools` | 否 | 可用工具/工具集列表 |
| `agents` | 否 | 允许的子代理列表（`*` 表示所有，`[]` 表示无） |
| `model` | 否 | AI 模型名称或优先级模型数组 |
| `handoffs` | 否 | 下一步代理转换列表 |
| `user-invokable` | 否 | 在代理下拉列表中显示（默认：true） |
| `disable-model-invocation` | 否 | 防止子代理调用（默认：false） |
| `target` | 否 | 目标环境：`vscode` 或 `github-copilot` |
| `mcp-servers` | 否 | GitHub Copilot 目标的 MCP 服务器配置 |

### 第 3 步：配置工具

指定代理可以使用的工具：

```yaml
tools:
  - search              # 内置工具
  - fetch               # 内置工具
  - codebase            # 工具集
  - myServer/*          # 来自 MCP 服务器的所有工具
```

常见工具模式：
- **只读代理**：`['search', 'fetch', 'codebase']`
- **完全编辑代理**：`['*']` 或特定编辑工具
- **专业代理**：选择特定工具

### 第 4 步：添加交接（可选）

配置到其他代理的转换：

```yaml
handoffs:
  - label: 开始实施
    agent: implementation
    prompt: 实施上述计划。
    send: false
    model: GPT-5.2 (copilot)
```

交接字段：
- `label`：向用户显示的按钮文本
- `agent`：目标代理标识符
- `prompt`：目标代理的预填充提示
- `send`：自动提交提示（默认：false）
- `model`：交接的可选模型覆盖

### 第 5 步：编写代理指令（正文）

在 Markdown 中添加代理的行为指令：

```markdown
您是一个以安全为重点的代码审查员。您的工作是：

1. 分析代码中的安全漏洞
2. 检查常见的安全反模式
3. 提出安全的替代方案

## 指南

- 关注 OWASP Top 10 漏洞
- 立即标记硬编码的密钥
- 审查身份验证和授权逻辑

## 参考其他文件

参见 [安全指南](../security.md) 了解标准。
```

指令技巧：
- 使用 Markdown 链接参考其他文件
- 使用 `#tool:<tool-name>` 语法参考工具
- 明确说明代理行为和限制

### 第 6 步：验证代理

验证代理是否正确加载：

1. 打开命令面板（Ctrl+Shift+P）
2. 运行 "Chat: New Custom Agent" 或检查代理下拉列表
3. 使用 "Diagnostics" 视图（在聊天视图中右键单击）检查错误

## 模板

```markdown
---
name: <agent-name>
description: <聊天占位符的简要描述>
argument-hint: <可选的用户输入提示>
tools:
  - <tool-1>
  - <tool-2>
handoffs:
  - label: <按钮文本>
    agent: <目标代理>
    prompt: <预填充提示>
    send: false
---

# <代理标题>

用一段话描述代理的角色和目的。

## 角色

描述代理的专业角色和专长。

## 指南

- <指南 1>
- <指南 2>
- <指南 3>

## 工作流

1. <步骤 1>
2. <步骤 2>
3. <步骤 3>

## 限制

- <限制 1>
- <限制 2>
```

## 示例代理

### 规划代理

```markdown
---
name: planner
description: 生成实施计划
tools:
  - search
  - fetch
  - codebase
handoffs:
  - label: 开始实施
    agent: implementation
    prompt: 实施上述计划。
---

# 规划代理

您是一个解决方案架构师。生成详细的实施计划。

## 指南

- 在规划之前彻底分析需求
- 将工作分解为独立的、可测试的步骤
- 识别依赖关系和风险
- 不要进行代码更改
```

### 代码审查代理

```markdown
---
name: code-reviewer
description: 审查代码中的质量和安全问题
tools:
  - search
  - codebase
---

# 代码审查代理

您是一个进行代码审查的高级工程师。

## 关注领域

- 安全漏洞
- 性能问题
- 代码可维护性
- 测试覆盖率差距

## 输出格式

以以下方式提供发现：
1. **关键**：合并前必须修复
2. **警告**：应解决
3. **建议**：有更好
```

## 验证清单

- [ ] 文件具有 `.agent.md` 扩展名
- [ ] 文件位于 `agents/` 目录
- [ ] YAML frontmatter 有效（正确的缩进、无语法错误）
- [ ] 描述非空且描述性
- [ ] 工具列表只包含可用工具
- [ ] 交接代理名称与现有代理匹配
- [ ] 指令清晰且可操作
- [ ] 代理出现在代理下拉列表中

## 常见陷阱

| 陷阱 | 解决方案 |
|-------|----------|
| 代理未出现在下拉列表中 | 检查文件是否位于 `agents/` 目录且具有 `.agent.md` 扩展名 |
| YAML 语法错误 | 验证 frontmatter 缩进和引号 |
| 工具无法工作 | 验证工具名称是否存在；忽略不可用的工具 |
| 交接未显示 | 目标代理必须存在；检查代理标识符 |
| 指令过于模糊 | 明确说明角色、限制和工作流 |
| 代理意外作为子代理调用 | 设置 `disable-model-invocation: true` |
| 只想将代理作为子代理 | 设置 `user-invokable: false` |

## 参考

- [VS Code 自定义代理文档](https://code.visualstudio.com/docs/copilot/customization/custom-agents)
- [聊天中的工具](https://code.visualstudio.com/docs/copilot/chat/chat-tools)
- [自定义指令](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)
- [提示文件](https://code.visualstudio.com/docs/copilot/customization/prompt-files)
