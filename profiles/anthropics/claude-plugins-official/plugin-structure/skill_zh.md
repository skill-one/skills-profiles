# Claude Code 插件结构

## 概述

Claude Code 插件遵循标准化的目录结构，并支持自动组件发现。理解这种结构有助于创建组织良好、易于维护的插件，使其能够与 Claude Code 无缝集成。

**关键概念：**
- 传统的目录布局以实现自动发现
- 在 `.claude-plugin/plugin.json` 中进行声明式配置
- 基于组件的组织（命令、代理、技能、钩子）
- 使用 `${CLAUDE_PLUGIN_ROOT}` 进行可移植路径引用
- 显式加载与自动发现组件的对比

## 目录结构

每个 Claude Code 插件都遵循这种组织模式：

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # 必须项：插件声明文件
├── commands/                 # 命令（.md 文件）
├── agents/                   # 子代理定义（.md 文件）
├── skills/                   # 代理技能（子目录）
│   └── skill-name/
│       └── SKILL.md         # 每个技能必须包含
├── hooks/
│   └── hooks.json           # 事件处理器配置
├── .mcp.json                # MCP 服务器定义
└── scripts/                 # 辅助脚本和工具
```

**关键规则：**

1. **声明文件位置**：`plugin.json` 声明文件必须位于 `.claude-plugin/` 目录下
2. **组件位置**：所有组件目录（命令、代理、技能、钩子）必须位于插件根级别，不能嵌套在 `.claude-plugin/` 内
3. **可选组件**：仅创建插件实际使用的组件目录
4. **命名规范**：所有目录和文件名使用连字符命名法（kebab-case）

## 插件声明文件 (plugin.json)

声明文件定义插件元数据和配置。位于 `.claude-plugin/plugin.json`：

### 必填字段

```json
{
  "name": "plugin-name"
}
```

**命名要求：**
- 使用连字符命名法（全小写，用连字符连接）
- 必须在所有已安装插件中唯一
- 不能包含空格或特殊字符
- 示例：`code-review-assistant`，`test-runner`，`api-docs`

### 推荐元数据

```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "简要说明插件用途",
  "author": {
    "name": "作者名称",
    "email": "author@example.com",
    "url": "https://example.com"
  },
  "homepage": "https://docs.example.com",
  "repository": "https://github.com/user/plugin-name",
  "license": "MIT",
  "keywords": ["测试", "自动化", "ci-cd"]
}
```

**版本格式**：遵循语义化版本控制（MAJOR.MINOR.PATCH）
**关键词**：用于插件发现和分类

### 组件路径配置

指定组件的自定义路径（补充默认目录）：

```json
{
  "name": "plugin-name",
  "commands": "./custom-commands",
  "agents": ["./agents", "./specialized-agents"],
  "hooks": "./config/hooks.json",
  "mcpServers": "./.mcp.json"
}
```

**重要提示**：自定义路径补充默认路径——它们不会替换它们。默认目录和自定义路径中的组件都会被加载。

**路径规则：**
- 必须相对于插件根目录
- 必须以 `./` 开头
- 不能使用绝对路径
- 支持数组以指定多个位置

## 组件组织

### 命令

**位置**：`commands/` 目录
**格式**：带 YAML 前置的 Markdown 文件
**自动发现**：`commands/` 中的所有 `.md` 文件都会自动加载

**示例结构**：
```
commands/
├── review.md        # /review 命令
├── test.md          # /test 命令
└── deploy.md        # /deploy 命令
```

**文件格式**：
```markdown
---
name: command-name
description: 命令描述
---

命令实现说明...
```

**用途**：命令作为原生斜杠命令集成到 Claude Code 中

### 代理

**位置**：`agents/` 目录
**格式**：带 YAML 前置的 Markdown 文件
**自动发现**：`agents/` 中的所有 `.md` 文件都会自动加载

**示例结构**：
```
agents/
├── code-reviewer.md
├── test-generator.md
└── refactorer.md
```

**文件格式**：
```markdown
---
description: 代理角色和专长
capabilities:
  - 特定任务 1
  - 特定任务 2
---

详细代理说明和知识...
```

**用途**：用户可以手动调用代理，或 Claude Code 根据任务上下文自动选择

### 技能

**位置**：`skills/` 目录，每个技能一个子目录
**格式**：每个技能在其自己的目录中，包含 `SKILL.md` 文件
**自动发现**：技能子目录中的所有 `SKILL.md` 文件都会自动加载

**示例结构**：
```
skills/
├── api-testing/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── test-runner.py
│   └── references/
│       └── api-spec.md
└── database-migrations/
    ├── SKILL.md
    └── examples/
        └── migration-template.sql
```

**SKILL.md 格式**：
```markdown
---
name: 技能名称
description: 何时使用此技能
version: 1.0.0
---

技能说明和指导...
```

**辅助文件**：技能可以包含脚本、参考文件、示例或资源文件在子目录中

**用途**：Claude Code 根据任务上下文匹配描述自动激活技能

### 钩子

**位置**：`hooks/hooks.json` 或在 `plugin.json` 中内联
**格式**：定义事件处理器的 JSON 配置
**注册**：钩子在插件启用时自动注册

**示例结构**：
```
hooks/
├── hooks.json           # 钩子配置
└── scripts/
    ├── validate.sh      # 钩子脚本
    └── check-style.sh   # 钩子脚本
```

**配置格式**：
```json
{
  "PreToolUse": [{
    "matcher": "Write|Edit",
    "hooks": [{
      "type": "command",
      "command": "bash ${CLAUDE_PLUGIN_ROOT}/hooks/scripts/validate.sh",
      "timeout": 30
    }]
  }]
}
```

**可用事件**：PreToolUse、PostToolUse、Stop、SubagentStop、SessionStart、SessionEnd、UserPromptSubmit、PreCompact、Notification

**用途**：钩子响应 Claude Code 事件自动执行

### MCP 服务器

**位置**：插件根目录的 `.mcp.json` 或在 `plugin.json` 中内联
**格式**：用于 MCP 服务器定义的 JSON 配置
**自动启动**：服务器在插件启用时自动启动

**示例格式**：
```json
{
  "mcpServers": {
    "server-name": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/servers/server.js"],
      "env": {
        "API_KEY": "${API_KEY}"
      }
    }
  }
}
```

**用途**：MCP 服务器与 Claude Code 的工具系统无缝集成

## 可移植路径引用

### ${CLAUDE_PLUGIN_ROOT}

使用 `${CLAUDE_PLUGIN_ROOT}` 环境变量进行所有插件内部路径引用：

```json
{
  "command": "bash ${CLAUDE_PLUGIN_ROOT}/scripts/run.sh"
}
```

**为什么重要**：插件安装位置取决于：
- 用户安装方式（市场、本地、npm）
- 操作系统约定
- 用户偏好

**使用场景**：
- 钩子命令路径
- MCP 服务器命令参数
- 脚本执行引用
- 资源文件路径

**绝对避免**：
- 硬编码绝对路径（`/Users/name/plugins/...`）
- 从工作目录的相对路径（命令中的 `./scripts/...`）
- 家目录快捷方式（`~/plugins/...`）

### 路径解析规则

**在声明文件 JSON 字段**（钩子、MCP 服务器）：
```json
"command": "${CLAUDE_PLUGIN_ROOT}/scripts/tool.sh"
```

**在组件文件**（命令、代理、技能）：
```markdown
引用脚本位置：${CLAUDE_PLUGIN_ROOT}/scripts/helper.py
```

**在执行脚本**：
```bash
#!/bin/bash
# ${CLAUDE_PLUGIN_ROOT} 作为环境变量可用
source "${CLAUDE_PLUGIN_ROOT}/lib/common.sh"
```

## 文件命名规范

### 组件文件

**命令**：使用连字符命名法的 `.md` 文件
- `code-review.md` → `/code-review`
- `run-tests.md` → `/run-tests`
- `api-docs.md` → `/api-docs`

**代理**：使用描述角色的连字符命名法的 `.md` 文件
- `test-generator.md`
- `code-reviewer.md`
- `performance-analyzer.md`

**技能**：使用连字符命名的目录
- `api-testing/`
- `database-migrations/`
- `error-handling/`

### 辅助文件

**脚本**：使用描述性连字符命名法并带有适当扩展名
- `validate-input.sh`
- `generate-report.py`
- `process-data.js`

**文档**：使用连字符命名的 Markdown 文件
- `api-reference.md`
- `migration-guide.md`
- `best-practices.md`

**配置**：使用标准名称
- `hooks.json`
- `.mcp.json`
- `plugin.json`

## 自动发现机制

Claude Code 自动发现并加载组件：

1. **插件声明文件**：插件启用时读取 `.claude-plugin/plugin.json`
2. **命令**：扫描 `commands/` 目录中的 `.md` 文件
3. **代理**：扫描 `agents/` 目录中的 `.md` 文件
4. **技能**：扫描 `skills/` 中的包含 `SKILL.md` 的子目录
5. **钩子**：从 `hooks/hooks.json` 或声明文件加载配置
6. **MCP 服务器**：从 `.mcp.json` 或声明文件加载配置

**发现时机**：
- 插件安装：组件向 Claude Code 注册
- 插件启用：组件变为可用状态
- 无需重启：更改在下次 Claude Code 会话中生效

**覆盖行为**：`plugin.json` 中的自定义路径补充（而非替换）默认目录

## 最佳实践

### 组织

1. **逻辑分组**：将相关组件组合在一起
   - 将与测试相关的命令、代理和技能放在一起
   - 在 `scripts/` 中按用途创建子目录

2. **精简声明文件**：保持 `plugin.json` 简洁
   - 仅在必要时指定自定义路径
   - 依赖自动发现标准布局
   - 仅在简单情况下使用内联配置

3. **文档**：包含 README 文件
   - 插件根目录：总体用途和用法
   - 组件目录：具体指导
   - 脚本目录：用法和需求

### 命名

1. **一致性**：跨组件使用一致命名
   - 如果命令是 `test-runner`，相关代理命名为 `test-runner-agent`
   - 匹配技能目录名称与其用途

2. **清晰性**：使用描述性名称表明用途
   - 好：`api-integration-testing/`，`code-quality-checker.md`
   - 避免：`utils/`，`misc.md`，`temp.sh`

3. **长度**：平衡简洁性与清晰度
   - 命令：2-3 个词（`review-pr`，`run-ci`）
   - 代理：清晰描述角色（`code-reviewer`，`test-generator`）
   - 技能：主题导向（`error-handling`，`api-design`）

### 可移植性

1. **始终使用 ${CLAUDE_PLUGIN_ROOT}**：绝不硬编码路径
2. **跨系统测试**：在 macOS、Linux、Windows 上验证
3. **记录依赖**：列出所需工具和版本
4. **避免系统特定特性**：使用可移植的 bash/Python 语法

### 维护

1. **版本控制**：为发布更新插件.json 中的版本号
2. **优雅弃用**：在移除前清晰标记旧组件
3. **记录破坏性变更**：注明影响现有用户的变更
4. **彻底测试**：变更后验证所有组件

## 常见模式

### 简单插件

单个命令且无依赖：
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json    # 仅包含名称字段
└── commands/
    └── hello.md       # 单个命令
```

### 完整功能插件

包含所有组件类型的完整插件：
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/          # 用户界面命令
├── agents/            # 特化子代理
├── skills/            # 自动激活技能
├── hooks/             # 事件处理器
│   ├── hooks.json
│   └── scripts/
├── .mcp.json          # 外部集成
└── scripts/           # 共享工具
```

### 技能导向插件

仅提供技能的插件：
```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    ├── skill-one/
    │   └── SKILL.md
    └── skill-two/
        └── SKILL.md
```

## 故障排除

**组件未加载**：
- 验证文件位于正确目录且扩展名正确
- 检查命令、代理、技能的 YAML 前置语法
- 确保技能包含 `SKILL.md`（不是 `README.md` 或其他名称）
- 确认插件在 Claude Code 设置中已启用

**路径解析错误**：
- 将所有硬编码路径替换为 `${CLAUDE_PLUGIN_ROOT}`
- 验证声明文件中的路径是相对的且以 `./` 开头
- 确认指定路径处的文件存在
- 在钩子脚本中测试 `echo $CLAUDE_PLUGIN_ROOT`

**自动发现不工作**：
- 确认目录位于插件根（不在 `.claude-plugin/` 内）
- 检查文件命名是否遵循规范（连字符命名法，正确扩展名）
- 验证声明文件中的自定义路径是否正确
- 重启 Claude Code 以重新加载插件配置

**插件冲突**：
- 使用唯一、描述性的组件名称
- 如有必要，使用插件名称命名空间命令
- 在插件 README 中记录潜在冲突
- 考虑为相关功能使用命令前缀

---

有关详细示例和高级模式，请参阅 `references/` 和 `examples/` 目录中的文件。
