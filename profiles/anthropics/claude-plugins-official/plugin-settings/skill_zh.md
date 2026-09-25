# Claude 代码插件设置模式

## 概述

插件可以存储用户可配置的设置和状态在项目目录的 `.claude/plugin-name.local.md` 文件中。此模式使用 YAML 前置文本进行结构化配置，并使用 Markdown 内容作为提示或附加上下文。

**主要特点：**
- 文件位置：项目根目录下的 `.claude/plugin-name.local.md`
- 结构：YAML 前置文本 + Markdown 正文
- 目的：项目级插件配置和状态
- 使用方式：从钩子、命令和代理中读取
- 生命周期：用户管理（不在 git 中，应放在 `.gitignore` 中）

## 文件结构

### 基本模板

```markdown
---
enabled: true
setting1: value1
setting2: value2
numeric_setting: 42
list_setting: ["item1", "item2"]
---

# 附加上下文

此 Markdown 正文可以包含：
- 任务描述
- 附加指令
- 反馈给 Claude 的提示
- 文档或笔记
```

### 示例：插件状态文件

**.claude/my-plugin.local.md:**
```markdown
---
enabled: true
strict_mode: false
max_retries: 3
notification_level: info
coordinator_session: team-leader
---

# 插件配置

此插件配置为标准验证模式。
如有问题，请联系 @team-lead。
```

## 读取设置文件

### 从钩子（Bash 脚本）

**模式：检查存在并解析前置文本**

```bash
#!/bin/bash
set -euo pipefail

# 定义状态文件路径
STATE_FILE=".claude/my-plugin.local.md"

# 如果文件不存在则快速退出
if [[ ! -f "$STATE_FILE" ]]; then
  exit 0  # 插件未配置，跳过
fi

# 解析 YAML 前置文本（在 --- 标记之间）
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$STATE_FILE")

# 提取单个字段
ENABLED=$(echo "$FRONTMATTER" | grep '^enabled:' | sed 's/enabled: *//' | sed 's/^"\(.*\)"$/\1/')
STRICT_MODE=$(echo "$FRONTMATTER" | grep '^strict_mode:' | sed 's/strict_mode: *//' | sed 's/^"\(.*\)"$/\1/')

# 检查是否启用
if [[ "$ENABLED" != "true" ]]; then
  exit 0  # 禁用
fi

# 在钩子逻辑中使用配置
if [[ "$STRICT_MODE" == "true" ]]; then
  # 应用严格验证
  # ...
fi
```

参考 `examples/read-settings-hook.sh` 获取完整工作示例。

### 从命令

命令可以读取设置文件来自定义行为：

```markdown
---
description: 使用插件处理数据
allowed-tools: ["Read", "Bash"]
---

# 处理命令

步骤：
1. 检查 `.claude/my-plugin.local.md` 中的设置是否存在
2. 使用 Read 工具读取配置
3. 解析 YAML 前置文本以提取设置
4. 将设置应用于处理逻辑
5. 使用配置行为执行
```

### 从代理

代理可以在其指令中引用设置：

```markdown
---
name: configured-agent
description: 适应项目设置的代理
---

检查 `.claude/my-plugin.local.md` 中的插件设置。
如果存在，解析 YAML 前置文本并根据以下内容调整行为：
- enabled：插件是否激活
- mode：处理模式（严格、标准、宽松）
- 其他配置字段
```

## 解析技术

### 提取前置文本

```bash
# 提取 --- 标记之间的所有内容
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$FILE")
```

### 读取单个字段

**字符串字段：**
```bash
VALUE=$(echo "$FRONTMATTER" | grep '^field_name:' | sed 's/field_name: *//' | sed 's/^"\(.*\)"$/\1/')
```

**布尔字段：**
```bash
ENABLED=$(echo "$FRONTMATTER" | grep '^enabled:' | sed 's/enabled: *//')
# 比较：if [[ "$ENABLED" == "true" ]]; then
```

**数字字段：**
```bash
MAX=$(echo "$FRONTMATTER" | grep '^max_value:' | sed 's/max_value: *//')
# 使用：if [[ $MAX -gt 100 ]]; then
```

### 读取 Markdown 正文

提取第二个 `---` 之后的内容：

```bash
# 获取关闭 --- 之后的所有内容
BODY=$(awk '/^---$/{i++; next} i>=2' "$FILE")
```

## 常见模式

### 模式 1：临时激活的钩子

使用设置文件控制钩子激活：

```bash
#!/bin/bash
STATE_FILE=".claude/security-scan.local.md"

# 如果未配置则快速退出
if [[ ! -f "$STATE_FILE" ]]; then
  exit 0
fi

# 读取启用标志
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$STATE_FILE")
ENABLED=$(echo "$FRONTMATTER" | grep '^enabled:' | sed 's/enabled: *//')

if [[ "$ENABLED" != "true" ]]; then
  exit 0  # 禁用
fi

# 运行钩子逻辑
# ...
```

**用例：** 无需编辑 hooks.json 即可启用/禁用钩子（需要重启）。

### 模式 2：代理状态管理

存储特定于代理的状态和配置：

**.claude/multi-agent-swarm.local.md:**
```markdown
---
agent_name: auth-agent
task_number: 3.5
pr_number: 1234
coordinator_session: team-leader
enabled: true
dependencies: ["Task 3.4"]
---

# 任务分配

为 API 实现 JWT 认证。

**成功标准：**
- 创建认证端点
- 测试通过
- 创建 PR 并 CI 变绿
```

从钩子中读取以协调代理：

```bash
AGENT_NAME=$(echo "$FRONTMATTER" | grep '^agent_name:' | sed 's/agent_name: *//')
COORDINATOR=$(echo "$FRONTMATTER" | grep '^coordinator_session:' | sed 's/coordinator_session: *//')

# 向协调器发送通知
tmux send-keys -t "$COORDINATOR" "Agent $AGENT_NAME 完成了任务" Enter
```

### 模式 3：配置驱动行为

**.claude/my-plugin.local.md:**
```markdown
---
validation_level: strict
max_file_size: 1000000
allowed_extensions: [".js", ".ts", ".tsx"]
enable_logging: true
---

# 验证配置

此项目启用了严格模式。
所有写入都将根据安全策略进行验证。
```

在钩子或命令中使用：

```bash
LEVEL=$(echo "$FRONTMATTER" | grep '^validation_level:' | sed 's/validation_level: *//')

case "$LEVEL" in
  strict)
    # 应用严格验证
    ;;
  standard)
    # 应用标准验证
    ;;
  lenient)
    # 应用宽松验证
    ;;
esac
```

## 创建设置文件

### 从命令

命令可以创建设置文件：

```markdown
# 设置命令

步骤：
1. 询问用户配置偏好
2. 创建 `.claude/my-plugin.local.md` 并带 YAML 前置文本
3. 根据用户输入设置适当值
4. 告知用户设置已保存
5. 提醒用户重启 Claude Code 以使钩子识别更改
```

### 模板生成

在插件 README 中提供模板：

```markdown
## 配置

在您的项目中创建 `.claude/my-plugin.local.md`：

\`\`\`markdown
---
enabled: true
mode: standard
max_retries: 3
---

# 插件配置

您的设置已生效。
\`\`\`

创建或编辑后，重启 Claude Code 以使更改生效。
```

## 最佳实践

### 文件命名

✅ **要：**
- 使用 `.claude/plugin-name.local.md` 格式
- 精确匹配插件名称
- 使用 `.local.md` 后缀表示用户本地文件

❌ **不要：**
- 使用不同目录（不是 `.claude/`）
- 使用不一致的命名
- 使用不带 `.local` 的 `.md`（可能会被提交）

### Gitignore

始终添加到 `.gitignore`：

```gitignore
.claude/*.local.md
.claude/*.local.json
```

在插件 README 中记录此内容。

### 默认值

当设置文件不存在时提供合理的默认值：

```bash
if [[ ! -f "$STATE_FILE" ]]; then
  # 使用默认值
  ENABLED=true
  MODE=standard
else
  # 从文件读取
  # ...
fi
```

### 验证

验证设置值：

```bash
MAX=$(echo "$FRONTMATTER" | grep '^max_value:' | sed 's/max_value: *//')

# 验证数字范围
if ! [[ "$MAX" =~ ^[0-9]+$ ]] || [[ $MAX -lt 1 ]] || [[ $MAX -gt 100 ]]; then
  echo "⚠️  设置中的 max_value 无效（必须在 1-100 之间）" >&2
  MAX=10  # 使用默认值
fi
```

### 重启要求

**重要：** 设置更改需要重启 Claude Code。

在您的 README 中记录：

```markdown
## 更改设置

编辑 `.claude/my-plugin.local.md` 后：
1. 保存文件
2. 退出 Claude Code
3. 重启：`claude` 或 `cc`
4. 新设置将被加载
```

钩子无法在会话内热替换。

## 安全注意事项

### 清理用户输入

从用户输入写入设置文件时：

```bash
# 转义用户输入中的引号
SAFE_VALUE=$(echo "$USER_INPUT" | sed 's/"/\\"/g')

# 写入文件
cat > "$STATE_FILE" <<EOF
---
user_setting: "$SAFE_VALUE"
---
EOF
```

### 验证文件路径

如果设置包含文件路径：

```bash
FILE_PATH=$(echo "$FRONTMATTER" | grep '^data_file:' | sed 's/data_file: *//')

# 检查路径遍历
if [[ "$FILE_PATH" == *".."* ]]; then
  echo "⚠️  设置中的路径无效（路径遍历）" >&2
  exit 2
fi
```

### 权限

设置文件应：
- 仅用户可读（`chmod 600`）
- 不提交到 git
- 不在用户间共享

## 实际示例

### multi-agent-swarm 插件

**.claude/multi-agent-swarm.local.md:**
```markdown
---
agent_name: auth-implementation
task_number: 3.5
pr_number: 1234
coordinator_session: team-leader
enabled: true
dependencies: ["Task 3.4"]
additional_instructions: 使用 JWT tokens，不是会话
---

# 任务：实现认证

为 REST API 构建基于 JWT 的认证。
与 auth-agent 协调共享类型。
```

**钩子使用（agent-stop-notification.sh）：**
- 检查文件是否存在（行 15-18：如果不存在则快速退出）
- 解析前置文本以获取 coordinator_session、agent_name、enabled
- 如果启用，则向协调器发送通知
- 允许通过 `enabled: true/false` 快速激活/禁用

### ralph-loop 插件

**.claude/ralph-loop.local.md:**
```markdown
---
iteration: 1
max_iterations: 10
completion_promise: "所有测试通过且构建成功"
---

修复项目中的所有 linting 错误。
确保每次修复后测试通过。
```

**钩子使用（stop-hook.sh）：**
- 检查文件是否存在（行 15-18：如果未激活则快速退出）
- 读取迭代次数和 max_iterations
- 提取 completion_promise 以用于循环终止
- 读取正文作为反馈提示
- 每次循环更新迭代次数

## 快速参考

### 文件位置

```
project-root/
└── .claude/
    └── plugin-name.local.md
```

### 前置文本解析

```bash
# 提取前置文本
FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$FILE")

# 读取字段
VALUE=$(echo "$FRONTMATTER" | grep '^field:' | sed 's/field: *//' | sed 's/^"\(.*\)"$/\1/')
```

### 正文解析

```bash
# 提取第二个 --- 之后的内容
BODY=$(awk '/^---$/{i++; next} i>=2' "$FILE")
```

### 快速退出模式

```bash
if [[ ! -f ".claude/my-plugin.local.md" ]]; then
  exit 0  # 未配置
fi
```

## 额外资源

### 参考文件

有关详细实现模式的参考：

- **`references/parsing-techniques.md`** - 解析 YAML 前置文本和 Markdown 正文的综合指南
- **`references/real-world-examples.md`** - 深入探讨 multi-agent-swarm 和 ralph-loop 实现的参考

### 示例文件

`examples/` 中的工作示例：

- **`read-settings-hook.sh`** - 读取并使用设置的钩子
- **`create-settings-command.md`** - 创建设置文件的命令
- **`example-settings.md`** - 模板设置文件

### 实用脚本

`scripts/` 中的开发工具：

- **`validate-settings.sh`** - 验证设置文件结构
- **`parse-frontmatter.sh`** - 提取前置文本字段

## 实现工作流

向插件添加设置：

1. 设计设置模式（哪些字段、类型、默认值）
2. 在插件文档中创建模板文件
3. 添加 `.claude/*.local.md` 的 gitignore 条目
4. 在钩子/命令中实现设置解析
5. 使用快速退出模式（检查文件是否存在、检查启用字段）
6. 在插件 README 中记录设置，并提供模板
7. 提醒用户更改需要重启 Claude Code

专注于保持设置简单，并在设置文件不存在时提供良好的默认值。
