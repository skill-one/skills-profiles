# 编写 Hookify 规则

## 概述

Hookify 规则是带有 YAML 前置的 Markdown 文件，用于定义要监控的模式以及当这些模式匹配时要显示的消息。规则存储在 `.claude/hookify.{rule-name}.local.md` 文件中。

## 规则文件格式

### 基本结构

```markdown
---
name: rule-identifier
enabled: true
event: bash|file|stop|prompt|all
pattern: regex-pattern-here
---

当此规则触发时向 Claude 显示的消息。
可以包含 Markdown 格式化、警告、建议等。
```

### 前置字段

**name** (必需): 规则的唯一标识符
- 使用连字符命名法：`warn-dangerous-rm`，`block-console-log`
- 具有描述性和行动导向性
- 以动词开头：警告、阻止、要求、检查

**enabled** (必需): 布尔值以激活/停用
- `true`：规则处于活动状态
- `false`：规则被禁用（不会触发）
- 可以在不删除规则的情况下切换

**event** (必需): 触发哪个钩子事件
- `bash`：Bash 工具命令
- `file`：编辑、写入、多编辑工具
- `stop`：当代理想要停止时
- `prompt`：当用户提交提示时
- `all`：所有事件

**action** (可选)：当规则匹配时要执行的操作
- `warn`：显示消息但允许操作（默认）
- `block`：阻止操作（PreToolUse）或停止会话（Stop 事件）
- 如果省略，则默认为 `warn`

**pattern** (简单格式)：要匹配的正则表达式模式
- 用于简单的单条件规则
- 匹配命令（bash）或新文本（file）
- Python 正则表达式语法

**示例：**
```yaml
event: bash
pattern: rm\s+-rf
```

### 高级格式（多个条件）

对于具有多个条件的复杂规则：

```markdown
---
name: warn-env-file-edits
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.env$
  - field: new_text
    operator: contains
    pattern: API_KEY
---

你正在将 API 密钥添加到 .env 文件中。确保此文件在 .gitignore 中！
```

**条件字段：**
- `field`：要检查的字段
  - 对于 bash：`command`
  - 对于 file：`file_path`，`new_text`，`old_text`，`content`
- `operator`：如何匹配
  - `regex_match`：正则表达式匹配
  - `contains`：子字符串检查
  - `equals`：精确匹配
  - `not_contains`：子字符串必须不存在
  - `starts_with`：前缀检查
  - `ends_with`：后缀检查
- `pattern`：要匹配的模式或字符串

**所有条件必须匹配，规则才会触发。**

## 消息正文

前置字段后面的 Markdown 内容在规则触发时显示给 Claude。

**好的消息：**
- 解释检测到的内容
- 解释为什么这是有问题的
- 建议替代方案或最佳实践
- 使用格式化以提高清晰度（粗体、列表等）

**示例：**
```markdown
⚠️ **检测到 Console.log！**

你正在将 console.log 添加到生产代码中。

**为什么这很重要：**
- 调试日志不应发送到生产环境
- console.log 可能会暴露敏感数据
- 影响浏览器性能

**替代方案：**
- 使用适当的日志库
- 提交前删除
- 使用条件调试构建
```

## 事件类型指南

### bash 事件

匹配 Bash 命令模式：

```markdown
---
event: bash
pattern: sudo\s+|rm\s+-rf|chmod\s+777
---

检测到危险命令！
```

**常见模式：**
- 危险命令：`rm\s+-rf`，`dd\s+if=`，`mkfs`
- 权限提升：`sudo\s+`，`su\s+`
- 权限问题：`chmod\s+777`，`chown\s+root`

### file 事件

匹配编辑/写入/多编辑操作：

```markdown
---
event: file
pattern: console\.log\(|eval\(|innerHTML\s*=
---

检测到潜在问题的代码模式！
```

**匹配不同字段：**
```markdown
---
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.tsx?$
  - field: new_text
    operator: regex_match
    pattern: console\.log\(
---

TypeScript 文件中的 console.log！
```

**常见模式：**
- 调试代码：`console\.log\(`，`debugger`，`print\(`
- 安全风险：`eval\(`，`innerHTML\s*=`，`dangerouslySetInnerHTML`
- 敏感文件：`\.env$`，`credentials`，`\.pem$`
- 生成的文件：`node_modules/`，`dist/`，`build/`

### stop 事件

匹配代理想要停止时（完成检查）：

```markdown
---
event: stop
pattern: .*
---

停止前请验证：
- [ ] 运行了测试
- [ ] 构建成功
- [ ] 更新了文档
```

**用于：**
- 提醒必须执行的步骤
- 完成检查清单
- 流程强制执行

### prompt 事件

匹配用户提示内容（高级）：

```markdown
---
event: prompt
conditions:
  - field: user_prompt
    operator: contains
    pattern: deploy to production
---

生产环境部署清单：
- [ ] 测试通过？
- [ ] 团队已审核？
- [ ] 监控已准备？
```

## 模式编写技巧

### 正则表达式基础

**字面字符：** 大多数字符匹配自身
- `rm` 匹配 "rm"
- `console.log` 匹配 "console.log"

**特殊字符需要转义：**
- `.` (任何字符) → `\.` (字面点)
- `(` `)` → `\(` `\)` (字面括号)
- `[` `]` → `\[` `\]` (字面方括号)

**常用元字符：**
- `\s` - 空白（空格、制表符、换行）
- `\d` - 数字（0-9）
- `\w` - 单词字符（a-z，A-Z，0-9，_）
- `.` - 任何字符
- `+` - 一个或多个
- `*` - 零个或多个
- `?` - 零个或一个
- `|` - 或

**示例：**
```
rm\s+-rf         匹配：rm -rf，rm  -rf
console\.log\(   匹配：console.log(
(eval|exec)\(    匹配：eval( 或 exec(
chmod\s+777      匹配：chmod 777，chmod  777
API_KEY\s*=      匹配：API_KEY=，API_KEY =
```

### 测试模式

在使用前测试正则表达式模式：

```bash
python3 -c "import re; print(re.search(r'your_pattern', 'test text'))"
```

或者使用在线正则表达式测试工具（regex101.com 使用 Python 风格）。

### 常见陷阱

**过于宽泛：**
```yaml
pattern: log    # 匹配 "log"，"login"，"dialog"，"catalog"
```
更好：`console\.log\(|logger\.`

**过于具体：**
```yaml
pattern: rm -rf /tmp  # 仅匹配确切路径
```
更好：`rm\s+-rf`

**转义问题：**
- YAML 引用字符串：`"pattern"` 需要双反斜杠 `\\s`
- YAML 未引用：`pattern: \s` 可以直接使用
- **建议**：在 YAML 中使用未引用的模式

## 文件组织

**位置：** 所有规则都在 `.claude/` 目录中
**命名：** `.claude/hookify.{descriptive-name}.local.md`
**Gitignore：** 将 `.claude/*.local.md` 添加到 `.gitignore` 中

**好的名称：**
- `hookify.dangerous-rm.local.md`
- `hookify.console-log.local.md`
- `hookify.require-tests.local.md`
- `hookify.sensitive-files.local.md`

**坏的名称：**
- `hookify.rule1.local.md`（不描述性）
- `hookify.md`（缺少 .local）
- `danger.local.md`（缺少 hookify 前缀）

## 工作流程

### 创建规则

1. 确定不希望的行为
2. 确定涉及的工具（Bash、编辑等）
3. 选择事件类型（bash、file、stop、等）
4. 编写正则表达式模式
5. 在项目根目录创建 `.claude/hookify.{name}.local.md` 文件
6. 立即测试 - 规则在下次工具使用时动态读取

### 优化规则

1. 编辑 `.local.md` 文件
2. 调整模式或消息
3. 立即测试 - 修改在下次工具使用时生效

### 禁用规则

**临时：** 在前置中设置 `enabled: false`
**永久：** 删除 `.local.md` 文件

## 示例

查看 `${CLAUDE_PLUGIN_ROOT}/examples/` 获取完整示例：
- `dangerous-rm.local.md` - 阻止危险的 rm 命令
- `console-log-warning.local.md` - 警告关于 console.log
- `sensitive-files-warning.local.md` - 警告关于编辑 .env 文件

## 快速参考

**最小可行规则：**
```markdown
---
name: my-rule
enabled: true
event: bash
pattern: dangerous_command
---

在此处显示警告消息
```

**带条件的规则：**
```markdown
---
name: my-rule
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.ts$
  - field: new_text
    operator: contains
    pattern: any
---

警告消息
```

**事件类型：**
- `bash` - Bash 命令
- `file` - 文件编辑
- `stop` - 完成检查
- `prompt` - 用户输入
- `all` - 所有事件

**字段选项：**
- Bash：`command`
- File：`file_path`，`new_text`，`old_text`，`content`
- Prompt：`user_prompt`

**操作符：**
- `regex_match`，`contains`，`equals`，`not_contains`，`starts_with`，`ends_with`
