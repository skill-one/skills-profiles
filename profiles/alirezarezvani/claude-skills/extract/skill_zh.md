# /si:extract — 从模式中创建技能

将重复出现的模式或调试解决方案转换为独立的、可移植的技能，可安装在任何项目中。

## 使用方法

```
/si:extract <模式描述>                  # 交互式提取
/si:extract <模式> --name docker-m1-fixes       # 指定技能名称
/si:extract <模式> --output ./skills/            # 自定义输出目录
/si:extract <模式> --dry-run                     # 预览而不创建文件
```

## 何时提取

当满足以下任意条件时，一个学习内容适合进行技能提取：

| 标准 | 信号 |
|---|---|
| **重复出现** | 在 2 个或更多项目中出现相同问题 |
| **非显而易见** | 需要实际调试才能发现 |
| **广泛适用** | 不特定于某个代码库 |
| **复杂解决方案** | 多步骤修复，容易忘记 |
| **用户标记** | "保存为技能"，"我想重用这个" |

## 工作流程

### 第 1 步：识别模式

阅读用户的描述。在自动记忆库中搜索相关条目：

```bash
MEMORY_DIR="$HOME/.claude/projects/$(pwd | sed 's|/|%2F|g; s|%2F|/|; s|^/||')/memory"
grep -rni "<关键词>" "$MEMORY_DIR/"
```

如果在自动记忆库中找到，则使用这些条目作为源材料。如果没有找到，则直接使用用户的描述。

### 第 2 步：确定技能范围

提问（最多 2 个问题）：
- "这个问题解决了什么？"（如果不清楚）
- "是否应包含代码示例？"（如果适用）

### 第 3 步：生成技能名称

命名规则：
- 小写，单词之间用连字符分隔
- 描述性强但简洁（2-4 个词）
- 示例：`docker-m1-fixes`，`api-timeout-patterns`，`pnpm-workspace-setup`

**保留片段 — 技能名称中绝不能出现：**
- `claude`
- `anthropic`

对于关于 Claude Code 本身的技能，使用 `cc-` 前缀：
- ❌ `claude-code-settings` → ✅ `cc-settings`
- ❌ `claude-code-maintenance` → ✅ `cc-maintenance`
- ❌ `claude-mcp-tools` → ✅ `cc-mcp-tools`
- ❌ `claude-plugin-development` → ✅ `cc-plugin-development`

在写入技能目录之前，请将建议的名称与此列表进行核对。
如果存在保留片段，则将其转换（删除片段或用 `cc-` 替换 `claude*`/`anthropic*` 前缀），并确认用户。

### 第 4 步：创建技能文件

**启动 `skill-extractor` 代理** 进行实际文件生成。

代理创建：

```
<技能名称>/
├── SKILL.md            # 主技能文件，包含 frontmatter
├── README.md           # 人类可读的概述
└── reference/          # (可选) 支持性文档
    └── examples.md     # 具体示例和边界情况
```

### 第 5 步：SKILL.md 结构

生成的 SKILL.md 必须遵循此格式：

```markdown
---
name: "skill-name"
description: "<一句话描述>. 使用场景: <触发条件>."
---

# <技能标题>

> 一句话总结这个技能解决的问题。

## 快速参考

| 问题 | 解决方案 |
|---------|----------|
| {{问题 1}} | {{解决方案 1}} |
| {{问题 2}} | {{解决方案 2}} |

## 问题背景

{{2-3 句话解释问题是什么以及为什么它不明显。}}

## 解决方案

### 选项 1: {{名称}} (推荐)

{{分步说明，包含代码示例。}}

### 选项 2: {{替代方案}}

{{当选项 1 不适用时。}}

## 权衡

| 方法 | 优点 | 缺点 |
|------|------|------|
| 选项 1 | {{优点}} | {{缺点}} |
| 选项 2 | {{优点}} | {{缺点}} |

## 边界情况

- {{边界情况 1 和如何处理}}
- {{边界情况 2 和如何处理}}
```

### 第 6 步：质量门禁

最终确定前，请验证：

- [ ] SKILL.md 包含有效的 YAML frontmatter，包含 `name` 和 `description`
- [ ] `name` 与文件夹名称匹配（小写，连字符）
- [ ] `name` 不包含保留片段 `claude` 或 `anthropic`（Claude Code 技能使用 `cc-` 前缀）
- [ ] 描述包含 "使用场景:" 触发条件
- [ ] 解决方案是自包含的（无需外部上下文）
- [ ] 代码示例完整且可复制粘贴
- [ ] 没有项目特定的硬编码值（路径、URL、凭证）
- [ ] 没有不必要的依赖

### 第 7 步：报告

```
✅ 技能提取：{{skill-name}}

创建的文件：
  {{path}}/SKILL.md          ({{lines}} 行)
  {{path}}/README.md         ({{lines}} 行)
  {{path}}/reference/examples.md  ({{lines}} 行)

安装：/plugin install (复制到你的技能目录)
发布：clawhub publish {{path}}

来源：MEMORY.md 条目在第 {{n, m, ...}} 行（保留 — 技能是可移植的，记忆是项目特定的）
```

## 示例

### 提取调试模式

```
/si:extract "修复在 Apple Silicon 上因平台不匹配导致 Docker 构建失败的方案"
```

创建 `docker-m1-fixes/SKILL.md`，包含：
- 平台不匹配的错误信息
- 三个解决方案（构建标志、Dockerfile、docker-compose）
- 权衡表格
- 关于 Rosetta 2 模拟的性能说明

### 提取工作流模式

```
/si:extract "修改 OpenAPI 规范后总是重新生成 TypeScript API 客户端"
```

创建 `api-client-regen/SKILL.md`，包含：
- 为什么需要手动重新生成
- 精确的命令序列
- CI 集成片段
- 常见失败模式

## 小贴士

- 提取在不同项目中能节省时间的模式
- 保持技能专注 — 每个技能解决一个问题
- 包含人们会搜索的错误信息
- 通过脱离原始上下文阅读来测试技能 — 是否有意义？
