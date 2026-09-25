# Claude 代码命令开发

## 概述

斜杠命令是 Claude 在交互式会话期间执行的 Markdown 文件中定义的常用提示。理解命令结构、前文选项和动态特性，可以创建强大且可重用的工作流。

**关键概念：**
- 命令的 Markdown 文件格式
- YAML 前文用于配置
- 动态参数和文件引用
- Bash 执行用于上下文
- 命令组织与命名空间

## 命令基础

### 什么是斜杠命令？

斜杠命令是 Claude 在被调用时执行的包含提示的 Markdown 文件。命令提供：
- **可重用性**：定义一次，重复使用
- **一致性**：标准化常用工作流
- **共享性**：跨团队或项目分发
- **效率**：快速访问复杂提示

### 重要提示：命令是给 Claude 的指令

**命令是写给代理消费的，不是给人消费的。**

当用户调用 `/command-name` 时，命令内容成为 Claude 的指令。将命令写为对 Claude 的指令，告诉它该做什么，而不是写给用户的消息。

**正确方法（给 Claude 的指令）：**
```markdown
检查此代码的安全漏洞，包括：
- SQL 注入
- XSS 攻击
- 身份验证问题

提供具体的行号和严重程度评级。
```

**错误方法（给用户的消息）：**
```markdown
此命令将检查您的代码是否存在安全问题。
您将收到包含漏洞详情的报告。
```

第一个示例告诉 Claude 该做什么。第二个示例告诉用户会发生什么，但没有给 Claude 下指令。始终使用第一种方法。

### 命令位置

**项目命令**（与团队共享）：
- 位置：`.claude/commands/`
- 范围：仅在特定项目中可用
- 标签：在 `/help` 中显示为 "(project)"
- 用途：团队工作流、项目特定任务

**个人命令**（到处可用）：
- 位置：`~/.claude/commands/`
- 范围：在所有项目中可用
- 标签：在 `/help` 中显示为 "(user)"
- 用途：个人工作流、跨项目工具

**插件命令**（随插件捆绑）：
- 位置：`plugin-name/commands/`
- 范围：在插件安装时可用
- 标签：在 `/help` 中显示为 "(plugin-name)"
- 用途：插件特定功能

## 文件格式

### 基本结构

命令是带有 `.md` 扩展名的 Markdown 文件：

```
.claude/commands/
├── review.md           # /review 命令
├── test.md             # /test 命令
└── deploy.md           # /deploy 命令
```

**简单命令：**
```markdown
检查此代码的安全漏洞，包括：
- SQL 注入
- XSS 攻击
- 身份验证绕过
- 不安全的数据处理
```

基本命令不需要前文。

### 带有 YAML 前文

使用 YAML 前文添加配置：

```markdown
---
description: 检查代码中的安全问题
allowed-tools: Read, Grep, Bash(git:*)
model: sonnet
---

检查此代码的安全漏洞...
```

## YAML 前文字段

### description

**目的**：在 `/help` 中显示的简短描述
**类型**：字符串
**默认值**：命令提示的第一行

```yaml
---
description: 检查拉取请求中的代码质量
---
```

**最佳实践**：清晰、可操作的描述（不超过 60 个字符）

### allowed-tools

**目的**：指定命令可以使用哪些工具
**类型**：字符串或数组
**默认值**：继承自对话

```yaml
---
allowed-tools: Read, Write, Edit, Bash(git:*)
---
```

**模式：**
- `Read, Write, Edit` - 具体工具
- `Bash(git:*)` - 仅带 git 命令的 Bash
- `*` - 所有工具（很少需要）

**使用场景**：命令需要特定工具访问时

### model

**目的**：指定命令执行的模型
**类型**：字符串（sonnet, opus, haiku）
**默认值**：继承自对话

```yaml
---
model: haiku
---
```

**用例：**
- `haiku` - 快速、简单的命令
- `sonnet` - 标准工作流
- `opus` - 复杂分析

### argument-hint

**目的**：为自动完成记录预期的参数
**类型**：字符串
**默认值**：无

```yaml
---
argument-hint: [pr-number] [priority] [assignee]
---
```

**优点：**
- 帮助用户理解命令参数
- 改进命令发现
- 记录命令接口

### disable-model-invocation

**目的**：防止 SlashCommand 工具程序调用命令
**类型**：布尔值
**默认值**：false

```yaml
---
disable-model-invocation: true
---
```

**使用场景**：命令应仅手动调用时

## 动态参数

### 使用 $ARGUMENTS

将所有参数捕获为单个字符串：

```markdown
---
description: 通过编号修复问题
argument-hint: [issue-number]
---

修复编号为 #$ARGUMENTS 的问题，遵循我们的编码标准和最佳实践。
```

**用法：**
```
> /fix-issue 123
> /fix-issue 456
```

**展开为：**
```
修复编号为 #123 的问题，遵循我们的编码标准...
修复编号为 #456 的问题，遵循我们的编码标准...
```

### 使用位置参数

使用 `$1`、`$2`、`$3` 等捕获单个参数：

```markdown
---
description: 带优先级和指派者的 PR 审查
argument-hint: [pr-number] [priority] [assignee]
---

审查编号为 #$1 的拉取请求，优先级级别为 $2。
审查后，指派给 $3 进行后续处理。
```

**用法：**
```
> /review-pr 123 high alice
```

**展开为：**
```
审查编号为 #123 的拉取请求，优先级级别为 high。
审查后，指派给 alice 进行后续处理。
```

### 组合参数

混合位置参数和剩余参数：

```markdown
将 $1 部署到 $2 环境，选项为 $3
```

**用法：**
```
> /deploy api staging --force --skip-tests
```

**展开为：**
```
将 api 部署到 staging 环境，选项为 --force --skip-tests
```

## 文件引用

### 使用 @ 语法

在命令中包含文件内容：

```markdown
---
description: 审查特定文件
argument-hint: [file-path]
---

审查 @$1，包括：
- 代码质量
- 最佳实践
- 潜在错误
```

**用法：**
```
> /review-file src/api/users.ts
```

**效果**：Claude 在处理命令前读取 `src/api/users.ts`

### 多个文件引用

引用多个文件：

```markdown
比较 @src/old-version.js 与 @src/new-version.js

识别：
- 断开连接的更改
- 新功能
- 修复的错误
```

### 静态文件引用

无需参数引用已知文件：

```markdown
审查 @package.json 和 @tsconfig.json 以确保一致性

确保：
- TypeScript 版本匹配
- 依赖项一致
- 构建配置正确
```

## 命令中的 Bash 执行

命令可以在 Claude 处理命令之前执行内联 Bash 命令，以动态收集上下文。这对于包含仓库状态、环境信息或项目特定上下文非常有用。

**何时使用：**
- 包含动态上下文（git 状态、环境变量等）
- 收集项目/仓库状态
- 构建上下文感知工作流

**实现细节：**
有关完整语法、示例和最佳实践的详细信息，请参阅 `references/plugin-features-reference.md` 中的 bash 执行部分。参考包括确切语法和多个工作示例，以避免执行问题

## 命令组织

### 扁平结构

小型命令集的简单组织：

```
.claude/commands/
├── build.md
├── test.md
├── deploy.md
├── review.md
└── docs.md
```

**使用场景**：5-15 个命令，没有明确的类别

### 命名空间结构

在子目录中组织命令：

```
.claude/commands/
├── ci/
│   ├── build.md        # /build (项目:ci)
│   ├── test.md         # /test (项目:ci)
│   └── lint.md         # /lint (项目:ci)
├── git/
│   ├── commit.md       # /commit (项目:git)
│   └── pr.md           # /pr (项目:git)
└── docs/
    ├── generate.md     # /generate (项目:docs)
    └── publish.md      # /publish (项目:docs)
```

**优点：**
- 逻辑分类
- 在 `/help` 中显示命名空间
- 更容易找到相关命令

**使用场景**：15+ 个命令，明确的类别

## 最佳实践

### 命令设计

1. **单一职责**：一个命令，一个任务
2. **清晰的描述**：在 `/help` 中自我解释
3. **明确的依赖项**：在需要时使用 `allowed-tools`
4. **记录参数**：始终提供 `argument-hint`
5. **一致的命名**：使用动名词模式（review-pr, fix-issue）

### 参数处理

1. **验证参数**：在提示中检查必需的参数
2. **提供默认值**：当缺少参数时建议默认值
3. **记录格式**：解释预期的参数格式
4. **处理边缘情况**：考虑缺少或无效的参数

```markdown
---
argument-hint: [pr-number]
---

$IF($1,
  审查 PR #$1,
  请提供 PR 编号。用法：/review-pr [number]
)
```

### 文件引用

1. **明确的路径**：使用清晰的文件路径
2. **检查存在性**：优雅地处理缺失文件
3. **相对路径**：使用项目相对路径
4. **Glob 支持**：考虑使用 Glob 工具进行模式匹配

### Bash 命令

1. **限制范围**：使用 `Bash(git:*)` 而不是 `Bash(*)`
2. **安全的命令**：避免破坏性操作
3. **处理错误**：考虑命令失败
4. **保持快速**：长运行命令会减慢调用

### 文档

1. **添加注释**：解释复杂逻辑
2. **提供示例**：在注释中显示用法
3. **列出要求**：记录依赖项
4. **版本命令**：注意破坏性更改

```markdown
---
description: 部署应用程序到环境
argument-hint: [environment] [version]
---

<!--
用法：/deploy [staging|production] [version]
需要：配置 AWS 凭证
示例：/deploy staging v1.2.3
-->

将应用程序部署到 $1 环境，使用版本 $2...
```

## 常见模式

### 审查模式

```markdown
---
description: 审查代码更改
allowed-tools: Read, Bash(git:*)
---

已更改的文件：!`git diff --name-only`

审查每个文件，包括：
1. 代码质量和风格
2. 潜在错误或问题
3. 测试覆盖率
4. 文档需求

为每个文件提供具体反馈。
```

### 测试模式

```markdown
---
description: 运行特定文件的测试
argument-hint: [test-file]
allowed-tools: Bash(npm:*)
---

运行测试：!`npm test $1`

分析结果并建议修复失败的测试。
```

### 文档模式

```markdown
---
description: 为文件生成文档
argument-hint: [source-file]
---

生成全面的文档，包括 @$1：
- 函数/类的描述
- 参数文档
- 返回值描述
- 使用示例
- 边缘情况和错误
```

### 工作流模式

```markdown
---
description: 完成 PR 工作流
argument-hint: [pr-number]
allowed-tools: Bash(gh:*), Read
---

PR #$1 工作流：

1. 获取 PR：!`gh pr view $1`
2. 审查更改
3. 运行检查
4. 批准或请求更改
```

## 故障排除

**命令未出现：**
- 检查文件是否在正确目录
- 验证存在 `.md` 扩展名
- 确保有效的 Markdown 格式
- 重新启动 Claude Code

**参数不工作：**
- 验证 `$1`、`$2` 语法正确
- 检查 `argument-hint` 是否与用法匹配
- 确保没有多余的空间

**Bash 执行失败：**
- 检查 `allowed-tools` 是否包含 Bash
- 验证反引号中的命令语法
- 首先在终端中测试命令
- 检查所需的权限

**文件引用不工作：**
- 验证 `@` 语法正确
- 检查文件路径是否有效
- 确保允许 Read 工具
- 使用绝对或项目相对路径

## 插件特定功能

### CLAUDE_PLUGIN_ROOT 变量

插件命令可以访问 `${CLAUDE_PLUGIN_ROOT}`，这是一个解析为插件绝对路径的环境变量。

**目的：**
- 可移植地引用插件文件
- 执行插件脚本
- 加载插件配置
- 访问插件模板

**基本用法：**

```markdown
---
description: 使用插件脚本分析
allowed-tools: Bash(node:*)
---

运行分析：!`node ${CLAUDE_PLUGIN_ROOT}/scripts/analyze.js $1`

审查结果并报告发现。
```

**常见模式：**

```markdown
# 执行插件脚本
!`bash ${CLAUDE_PLUGIN_ROOT}/scripts/script.sh`

# 加载插件配置
@${CLAUDE_PLUGIN_ROOT}/config/settings.json

# 使用插件模板
@${CLAUDE_PLUGIN_ROOT}/templates/report.md

# 访问插件资源
@${CLAUDE_PLUGIN_ROOT}/docs/reference.md
```

**为什么使用它：**
- 跨所有安装工作
- 在系统之间可移植
- 无需硬编码路径
- 对于多文件插件至关重要

### 插件命令组织

插件命令自动从 `commands/` 目录发现：

```
plugin-name/
├── commands/
│   ├── foo.md              # /foo (插件:plugin-name)
│   ├── bar.md              # /bar (插件:plugin-name)
│   └── utils/
│       └── helper.md       # /helper (插件:plugin-name:utils)
└── plugin.json
```

**命名空间的好处：**
- 逻辑命令分组
- 在 `/help` 输出中显示
- 避免名称冲突
- 组织相关命令

**命名约定：**
- 使用描述性动作名称
- 避免通用名称（test, run）
- 考虑插件特定前缀
- 使用连字符进行多词名称

### 插件命令模式

**基于配置的模式：**

```markdown
---
description: 使用插件配置部署
argument-hint: [environment]
allowed-tools: Read, Bash(*)
---

加载配置：@${CLAUDE_PLUGIN_ROOT}/config/$1-deploy.json

使用配置设置将 $1 部署到...
监控部署并报告状态。
```

**基于模板的模式：**

```markdown
---
description: 从模板生成文档
argument-hint: [component]
---

模板：@${CLAUDE_PLUGIN_ROOT}/templates/docs.md

遵循模板结构，为 $1 生成文档。
```

**基于多脚本的模式：**

```markdown
---
description: 完整构建工作流
allowed-tools: Bash(*)
---

构建：!`bash ${CLAUDE_PLUGIN_ROOT}/scripts/build.sh`
测试：!`bash ${CLAUDE_PLUGIN_ROOT}/scripts/test.sh`
打包：!`bash ${CLAUDE_PLUGIN_ROOT}/scripts/package.sh`

审查输出并报告工作流状态。
```

**有关详细模式，请参阅 `references/plugin-features-reference.md`。**

## 与插件组件的集成

命令可以与其他插件组件集成，以创建强大的工作流。

### 代理集成

启动插件代理执行复杂任务：

```markdown
---
description: 深度代码审查
argument-hint: [file-path]
---

使用代码审查者代理，对 @$1 进行全面审查。

代理将分析：
- 代码结构
- 安全问题
- 性能
- 最佳实践

代理使用插件资源：
- ${CLAUDE_PLUGIN_ROOT}/config/rules.json
- ${CLAUDE_PLUGIN_ROOT}/checklists/review.md
```

**关键点：**
- 代理必须存在于 `plugin/agents/` 目录
- Claude 使用 Task 工具启动代理
- 记录代理功能
- 引用代理使用的插件资源

### 技能集成

利用插件技能进行专业知识：

```markdown
---
description: 使用标准文档 API
argument-hint: [api-file]
---

按照插件标准，在 @$1 中文档化 API。

使用 api-docs-standards 技能确保：
- 完整的端点文档
- 一致的格式
- 示例质量
- 错误文档

生成生产就绪的 API 文档。
```

**关键点：**
- 技能必须存在于 `plugin/skills/` 目录
- 提及技能名称以触发调用
- 记录技能目的
- 解释技能提供的内容

### 钩子协调

设计与插件钩子协同工作的命令：
- 命令可以准备钩子处理的状态
- 钩子在工具事件上自动执行
- 命令应记录预期的钩子行为
- 指导 Claude 解释钩子输出

有关与钩子协同工作的命令示例，请参阅 `references/plugin-features-reference.md`

### 多组件工作流

组合代理、技能和脚本：

```markdown
---
description: 全面审查工作流
argument-hint: [file]
allowed-tools: Bash(node:*), Read
---

目标：@$1

阶段 1 - 静态分析：
!`node ${CLAUDE_PLUGIN_ROOT}/scripts/lint.js $1`

阶段 2 - 深度审查：
启动代码审查者代理进行详细分析。

阶段 3 - 标准检查：
使用编码标准技能进行验证。

阶段 4 - 报告：
模板：@${CLAUDE_PLUGIN_ROOT}/templates/review.md

按照模板结构，将发现汇总为报告。
```

**何时使用：**
- 复杂的多步骤工作流
- 利用多个插件功能
- 需要专业分析
- 需要结构化输出

## 验证模式

命令应在处理前验证输入和资源。

### 参数验证

```markdown
---
description: 部署时验证
argument-hint: [environment]
---

验证环境：!`echo "$1" | grep -E "^(dev|staging|prod)$" || echo "INVALID"`

如果 $1 是有效的环境：
  部署到 $1
否则：
  解释有效环境：dev, staging, prod
  显示用法：/deploy [environment]
```

### 文件存在性检查

```markdown
---
description: 处理配置
argument-hint: [config-file]
---

检查文件是否存在：!`test -f $1 && echo "EXISTS" || echo "MISSING"`

如果文件存在：
  处理配置：@$1
否则：
  解释配置文件的位置
  显示预期格式
  提供示例配置
```

### 插件资源验证

```markdown
---
description: 运行插件分析器
allowed-tools: Bash(test:*)
---

验证插件设置：
- 脚本：!`test -x ${CLAUDE_PLUGIN_ROOT}/bin/analyze && echo "✓" || echo "✗"`
- 配置：!`test -f ${CLAUDE_PLUGIN_ROOT}/config.json && echo "✓" || echo "✗"`

如果所有检查都通过，则运行分析。
否则，报告缺失组件。
```

### 错误处理

```markdown
---
description: 构建时错误处理
allowed-tools: Bash(*)
---

执行构建：!`bash ${CLAUDE_PLUGIN_ROOT}/scripts/build.sh 2>&1 || echo "BUILD_FAILED"`

如果构建成功：
  报告成功和输出位置
如果构建失败：
  分析错误输出
  建议可能的原因
  提供故障排除步骤
```

**最佳实践：**
- 在命令早期验证
- 提供有帮助的错误消息
- 建议纠正措施
- 优雅地处理边缘情况

---

有关前文字段规范的详细信息，请参阅 `references/frontmatter-reference.md`。
有关插件特定功能和模式，请参阅 `references/plugin-features-reference.md`。
有关命令模式示例，请参阅 `examples/` 目录。
