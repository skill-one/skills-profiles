# Claude 代码插件钩子开发

## 概述

钩子是响应 Claude 代码事件的事件驱动自动化脚本。使用钩子来验证操作、执行策略、添加上下文并将外部工具集成到工作流中。

**主要功能：**
- 在执行前验证工具调用（PreToolUse）
- 响应工具结果（PostToolUse）
- 执行完成标准（Stop, SubagentStop）
- 加载项目上下文（SessionStart）
- 自动化开发生命周期中的工作流

## 钩子类型

### 基于提示的钩子（推荐）

使用 LLM 驱动的决策进行上下文感知验证：

```json
{
  "type": "prompt",
  "prompt": "评估此工具使用是否适当：$TOOL_INPUT",
  "timeout": 30
}
```

**支持的事件：** Stop, SubagentStop, UserPromptSubmit, PreToolUse

**优点：**
- 基于自然语言推理的上下文感知决策
- 无需 bash 脚本即可实现灵活的评估逻辑
- 更好的边缘情况处理
- 更易于维护和扩展

### 命令钩子

执行 bash 命令进行确定性检查：

```json
{
  "type": "command",
  "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh",
  "timeout": 60
}
```

**用于：**
- 快速确定性验证
- 文件系统操作
- 外部工具集成
- 性能关键检查

## 钩子配置格式

### 插件 hooks.json 格式

**对于插件钩子**在 `hooks/hooks.json` 中，使用包装格式：

```json
{
  "description": "钩子的简要说明（可选）",
  "hooks": {
    "PreToolUse": [...],
    "Stop": [...],
    "SessionStart": [...]
  }
}
```

**要点：**
- `description` 字段是可选的
- `hooks` 字段是必需的包装器，包含实际钩子事件
- 这是**特定于插件的格式**

**示例：**
```json
{
  "description": "代码质量验证钩子",
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks/validate.sh"
          }
        ]
      }
    ]
  }
}
```

### 设置格式（直接）

**对于用户设置**在 `.claude/settings.json` 中，使用直接格式：

```json
{
  "PreToolUse": [...],
  "Stop": [...],
  "SessionStart": [...]
}
```

**要点：**
- 无包装器 - 事件直接位于顶层
- 无描述字段
- 这是**设置格式**

**重要提示：** 以下示例显示了将放入任一格式的钩子事件结构。对于插件 hooks.json，将其包装在 `{"hooks": {...}}` 中。

## 钩子事件

### PreToolUse

在任何工具运行之前执行。用于批准、拒绝或修改工具调用。

**示例（基于提示）：**
```json
{
  "PreToolUse": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "验证文件写入安全性。检查：系统路径、凭证、路径遍历、敏感内容。返回 'approve' 或 'deny'。"
        }
      ]
    }
  ]
}
```

**PreToolUse 的输出：**
```json
{
  "hookSpecificOutput": {
    "permissionDecision": "allow|deny|ask",
    "updatedInput": {"field": "modified_value"}
  },
  "systemMessage": "对 Claude 的解释"
}
```

### PostToolUse

在工具完成后执行。用于响应结果、提供反馈或记录。

**示例：**
```json
{
  "PostToolUse": [
    {
      "matcher": "Edit",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "分析编辑结果以查找潜在问题：语法错误、安全漏洞、破坏性变更。提供反馈。"
        }
      ]
    }
  ]
}
```

**输出行为：**
- 退出码 0：stdout 显示在转录中
- 退出码 2：stderr 反馈给 Claude
- systemMessage 包含在上下文中

### Stop

当主代理考虑停止时执行。用于验证完整性。

**示例：**
```json
{
  "Stop": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "验证任务完成：运行测试、构建成功、问题已回答。返回 'approve' 以停止或 'block' 并提供原因以继续。"
        }
      ]
    }
  ]
}
```

**决策输出：**
```json
{
  "decision": "approve|block",
  "reason": "解释",
  "systemMessage": "附加上下文"
}
```

### SubagentStop

当子代理考虑停止时执行。用于确保子代理完成了其任务。

与 Stop 钩子类似，但用于子代理。

### UserPromptSubmit

当用户提交提示时执行。用于添加上下文、验证或阻止提示。

**示例：**
```json
{
  "UserPromptSubmit": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "检查是否需要安全指导。如果讨论身份验证、权限或 API 安全，返回相关警告。"
        }
      ]
    }
  ]
}
```

### SessionStart

当 Claude 代码会话开始时执行。用于加载上下文和设置环境。

**示例：**
```json
{
  "SessionStart": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/load-context.sh"
        }
      ]
    }
  ]
}
```

**特殊功能：** 使用 `$CLAUDE_ENV_FILE` 持续环境变量：
```bash
echo "export PROJECT_TYPE=nodejs" >> "$CLAUDE_ENV_FILE"
```

参考 `examples/load-context.sh` 获取完整示例。

### SessionEnd

当会话结束时执行。用于清理、记录和状态保留。

### PreCompact

在上下文压缩之前执行。用于添加关键信息以保留。

### Notification

当 Claude 发送通知时执行。用于响应用户通知。

## 钩子输出格式

### 标准输出（所有钩子）

```json
{
  "continue": true,
  "suppressOutput": false,
  "systemMessage": "对 Claude 的消息"
}
```

- `continue`：如果为 false，则停止处理（默认为 true）
- `suppressOutput`：隐藏输出在转录中（默认为 false）
- `systemMessage`：显示给 Claude 的消息

### 退出码

- `0` - 成功（stdout 显示在转录中）
- `2` - 阻塞错误（stderr 反馈给 Claude）
- 其他 - 非阻塞错误

## 钩子输入格式

所有钩子通过 stdin 接收带有常见字段的 JSON：

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.txt",
  "cwd": "/current/working/dir",
  "permission_mode": "ask|allow",
  "hook_event_name": "PreToolUse"
}
```

**事件特定字段：**

- **PreToolUse/PostToolUse：** `tool_name`, `tool_input`, `tool_result`
- **UserPromptSubmit：** `user_prompt`
- **Stop/SubagentStop：** `reason`

在提示中使用 `$TOOL_INPUT`, `$TOOL_RESULT`, `$USER_PROMPT` 等访问字段。

## 环境变量

在所有命令钩子中可用：

- `$CLAUDE_PROJECT_DIR` - 项目根路径
- `$CLAUDE_PLUGIN_ROOT` - 插件目录（用于可移植路径）
- `$CLAUDE_ENV_FILE` - SessionStart 仅：在此处持续环境变量
- `$CLAUDE_CODE_REMOTE` - 如果在远程上下文中运行则设置

**始终在钩子命令中使用 ${CLAUDE_PLUGIN_ROOT} 以确保可移植性：**

```json
{
  "type": "command",
  "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh"
}
```

## 插件钩子配置

在插件中，在 `hooks/hooks.json` 中定义钩子：

```json
{
  "PreToolUse": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "验证文件写入安全性"
        }
      ]
    }
  ],
  "Stop": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "验证任务完成"
        }
      ]
    }
  ],
  "SessionStart": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "command",
          "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/load-context.sh",
          "timeout": 10
        }
      ]
    }
  ]
}
```

插件钩子与用户钩子合并并行运行。

## 匹配器

### 工具名称匹配

**精确匹配：**
```json
"matcher": "Write"
```

**多个工具：**
```json
"matcher": "Read|Write|Edit"
```

**通配符（所有工具）：**
```json
"matcher": "*"
```

**正则表达式模式：**
```json
"matcher": "mcp__.*__delete.*"  // 所有 MCP 删除工具
```

**注意：** 匹配器区分大小写。

### 常见模式

```json
// 所有 MCP 工具
"matcher": "mcp__.*"

// 特定插件的 MCP 工具
"matcher": "mcp__plugin_asana_.*"

// 所有文件操作
"matcher": "Read|Write|Edit"

// 仅 bash 命令
"matcher": "Bash"
```

## 安全最佳实践

### 输入验证

在命令钩子中始终验证输入：

```bash
#!/bin/bash
set -euo pipefail

input=$(cat)
tool_name=$(echo "$input" | jq -r '.tool_name')

# 验证工具名称格式
if [[ ! "$tool_name" =~ ^[a-zA-Z0-9_]+$ ]]; then
  echo '{"decision": "deny", "reason": "无效的工具名称"}' >&2
  exit 2
fi
```

### 路径安全

检查路径遍历和敏感文件：

```bash
file_path=$(echo "$input" | jq -r '.tool_input.file_path')

# 拒绝路径遍历
if [[ "$file_path" == *".."* ]]; then
  echo '{"decision": "deny", "reason": "检测到路径遍历"}' >&2
  exit 2
fi

# 拒绝敏感文件
if [[ "$file_path" == *".env"* ]]; then
  echo '{"decision": "deny", "reason": "敏感文件"}' >&2
  exit 2
fi
```

参考 `examples/validate-write.sh` 和 `examples/validate-bash.sh` 获取完整示例。

### 所有变量加引号

```bash
# 好：加引号
echo "$file_path"
cd "$CLAUDE_PROJECT_DIR"

# 不好：未加引号（存在注入风险）
echo $file_path
cd $CLAUDE_PROJECT_DIR
```

### 设置适当的超时

```json
{
  "type": "command",
  "command": "bash script.sh",
  "timeout": 10
}
```

**默认值：** 命令钩子（60 秒），提示钩子（30 秒）

## 性能考虑

### 并行执行

所有匹配的钩子**并行**执行：

```json
{
  "PreToolUse": [
    {
      "matcher": "Write",
      "hooks": [
        {"type": "command", "command": "check1.sh"},  // 并行
        {"type": "command", "command": "check2.sh"},  // 并行
        {"type": "prompt", "prompt": "验证..."}   // 并行
      ]
    }
  ]
}
```

**设计影响：**
- 钩子看不到其他钩子的输出
- 非确定性顺序
- 设计为独立

### 优化

1. 使用命令钩子进行快速确定性检查
2. 使用提示钩子进行复杂推理
3. 在临时文件中缓存验证结果
4. 在热点路径中减少 I/O

## 临时激活的钩子

创建在条件性检查时激活的钩子，通过检查标志文件或配置：

**模式：标志文件激活**
```bash
#!/bin/bash
# 仅当标志文件存在时才激活
FLAG_FILE="$CLAUDE_PROJECT_DIR/.enable-strict-validation"

if [ ! -f "$FLAG_FILE" ]; then
  # 标志不存在，跳过验证
  exit 0
fi

# 标志存在，运行验证
input=$(cat)
# ... 验证逻辑 ...
```

**模式：基于配置的激活**
```bash
#!/bin/bash
# 检查配置是否激活
CONFIG_FILE="$CLAUDE_PROJECT_DIR/.claude/plugin-config.json"

if [ -f "$CONFIG_FILE" ]; then
  enabled=$(jq -r '.strictMode // false' "$CONFIG_FILE")
  if [ "$enabled" != "true" ]; then
    exit 0  # 未启用，跳过
  fi
fi

# 启用，运行钩子逻辑
input=$(cat)
# ... 钩子逻辑 ...
```

**用例：**
- 仅在需要时启用严格验证
- 临时调试钩子
- 项目特定钩子行为
- 钩子功能标志

**最佳实践：** 在插件 README 中记录激活机制，以便用户知道如何启用/禁用临时钩子。

## 钩子生命周期和限制

### 钩子在会话开始时加载

**重要提示：** 钩子在 Claude 代码会话开始时加载。需要重启 Claude 代码才能更改钩子配置。

**无法热交换钩子：**
- 编辑 `hooks/hooks.json` 不会影响当前会话
- 添加新的钩子脚本不会被识别
- 更改钩子命令/提示不会更新
- 必须重启 Claude 代码：退出并运行 `claude` 再次

**要测试钩子更改：**
1. 编辑钩子配置或脚本
2. 退出 Claude 代码会话
3. 重启：`claude` 或 `cc`
4. 新的钩子配置加载
5. 使用 `claude --debug` 测试钩子

### 启动时钩子验证

钩子在 Claude 代码启动时验证：
- hooks.json 中的无效 JSON 导致加载失败
- 缺失脚本导致警告
- 调试模式下报告语法错误

使用 `/hooks` 命令查看当前会话中加载的钩子。

## 调试钩子

### 启用调试模式

```bash
claude --debug
```

查找钩子注册、执行日志、输入/输出 JSON 和时间信息。

### 测试钩子脚本

直接测试命令钩子：

```bash
echo '{"tool_name": "Write", "tool_input": {"file_path": "/test"}}' | \
  bash ${CLAUDE_PLUGIN_ROOT}/scripts/validate.sh

echo "退出码: $?"
```

### 验证 JSON 输出

确保钩子输出有效的 JSON：

```bash
output=$(./your-hook.sh < test-input.json)
echo "$output" | jq .
```

## 快速参考

### 钩子事件总结

| 事件 | 当...时 | 用于 |
|------|--------|------|
| PreToolUse | 在工具之前 | 验证、修改 |
| PostToolUse | 在工具之后 | 反馈、记录 |
| UserPromptSubmit | 用户输入 | 上下文、验证 |
| Stop | 代理停止 | 完整性检查 |
| SubagentStop | 子代理完成 | 任务验证 |
| SessionStart | 会话开始 | 上下文加载 |
| SessionEnd | 会话结束 | 清理、记录 |
| PreCompact | 压缩之前 | 保留上下文 |
| Notification | 用户通知 | 记录、反应 |

### 最佳实践

**做：**
- ✅ 使用提示钩子进行复杂逻辑
- ✅ 使用 ${CLAUDE_PLUGIN_ROOT} 以确保可移植性
- ✅ 在命令钩子中验证所有输入
- ✅ 加引号 bash 变量
- ✅ 设置适当的超时
- ✅ 返回结构化 JSON 输出
- ✅ 彻底测试钩子

**不要：**
- ❌ 使用硬编码路径
- ❌ 无验证信任用户输入
- ❌ 创建长时间运行的钩子
- ❌ 依赖钩子执行顺序
- ❌ 预测性地修改全局状态
- ❌ 记录敏感信息

## 额外资源

### 参考文件

有关详细模式和高级技术，请参阅：

- **`references/patterns.md`** - 常见钩子模式（8+ 经过验证的模式）
- **`references/migration.md`** - 从基本到高级钩子的迁移
- **`references/advanced.md`** - 高级用例和技术

### 示例钩子脚本

`examples/` 中的工作示例：

- **`validate-write.sh`** - 文件写入验证示例
- **`validate-bash.sh`** - bash 命令验证示例
- **`load-context.sh`** - SessionStart 上下文加载示例

### 实用脚本

开发工具在 `scripts/` 中：

- **`validate-hook-schema.sh`** - 验证 hooks.json 结构和语法
- **`test-hook.sh`** - 在部署前使用样本输入测试钩子
- **`hook-linter.sh`** - 检查钩子脚本中的常见问题和最佳实践

### 外部资源

- **官方文档**：https://docs.claude.com/en/docs/claude-code/hooks
- **示例**：查看 marketplace 中的 security-guidance 插件
- **测试**：使用 `claude --debug` 获取详细日志
- **验证**：使用 `jq` 验证钩子 JSON 输出

## 实现工作流

要在插件中实现钩子：

1. 确定要挂钩的事件（PreToolUse, Stop, SessionStart 等）
2. 决定使用基于提示（灵活）还是命令（确定性）钩子
3. 在 `hooks/hooks.json` 中编写钩子配置
4. 对于命令钩子，创建钩子脚本
5. 使用 ${CLAUDE_PLUGIN_ROOT} 进行所有文件引用
6. 使用 `scripts/validate-hook-schema.sh hooks/hooks.json` 验证配置
7. 在部署前使用 `scripts/test-hook.sh` 测试钩子
8. 在 Claude 代码中使用 `claude --debug` 测试
9. 在插件 README 中记录钩子

对于大多数用例，请专注于提示钩子。将命令钩子保留用于性能关键或确定性检查。
