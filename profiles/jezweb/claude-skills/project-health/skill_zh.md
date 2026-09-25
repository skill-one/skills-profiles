# 项目健康

一项关于你的项目 Claude 代码配置的所有技能。在项目的开始、中间或结束时运行它——它会弄清楚需要什么。

**目标**：零权限提示、组织良好的上下文文件、无冗余。

## 使用时机

| 你说... | 会发生什么 |
|-----------|-------------|
| "项目健康" / "检查项目" | 全面审计：权限 + 上下文 + 文档 |
| "设置项目" / "启动" / "引导" | 从头开始设置新项目 |
| "整理权限" / "清理设置" | 仅修复权限文件 |
| "捕获学习" / "更新 CLAUDE.md" | 保存会话发现 |
| "添加 python" / "添加 docker 权限" | 向现有设置添加预设 |
| "审计上下文" / "审计内存" | 仅进行上下文聚焦的审计 |

## 架构：子代理

**重型分析在子代理中运行**以保持主对话的简洁。主代理进行协调；子代理进行扫描并返回摘要。

### 代理 1：权限审计员

使用 `Task(subagent_type: "general-purpose")` 启动。提示：

```
读取 .claude/settings.local.json。

**发现连接的 MCP 服务器**：使用 ToolSearch（搜索 "mcp"）并从工具名称中提取唯一服务器前缀（例如 mcp__vault__secret_list → vault）。

**发现已安装的技能**：使用 Skill 工具或 ToolSearch 列出可用技能。
对于其目录中包含 scripts/ 的每个技能，记录它需要的 Bash 模式（python3、环境变量前缀如 GEMINI_API_KEY=* 等）。检查 SKILL.md 中技能引用的任何 MCP 工具（例如 mcp__vault__secret_get）。

报告：
1. 连接的 MCP 服务器但不在设置中（缺失）
2. 设置中但未连接的 MCP 服务器（陈旧）
3. 技能权限：Bash 模式和已安装技能需要但未批准的 MCP 工具
4. 文件访问：检查项目设置中 .claude/** 和 //tmp/** 的 Read/Edit/Write 模式，以及全局设置中 ~/Documents/**/~/.claude/** 的文件访问模式
5. 泄露的秘密：包含 API 密钥、令牌、bearer 字符串、十六进制 >20 个字符、base64 >20 个字符的条目
6. 遗留冒号语法：如 Bash(git:*) 而不是 Bash(git *)
7. 无用条目：shell 片段（Bash(do)、Bash(fi)、Bash(then)、Bash(else)、Bash(done)）、__NEW_LINE_* 艺术品、循环体片段（Bash(break)、Bash(continue)、Bash(echo *))
8. 重复项：由更广泛的模式覆盖的条目（例如 Bash(git add *) 如果存在 Bash(git *) 则冗余）
9. 缺失预设：根据现有文件，建议来自 [permission-presets.md] 的预设

优先选择 Read/Glob/Grep 工具而不是 Bash。如果你需要扫描多个文件或为一次分析运行 3+ 命令，请将 Python 脚本写入 .jez/scripts/ 并运行一次（首先运行 mkdir -p .jez/scripts）。

返回结构化摘要，而不是原始数据。
```

### 代理 2：上下文审计员

使用 `Task(subagent_type: "general-purpose")` 启动。提示：

```
在 [repo-path] 处审计项目上下文环境：

1. 查找所有 CLAUDE.md 文件。对于每个：
   - 计算行数（目标：根目录 50-150 行，子目录 15-50 行）
   - 在 6 个标准上评分质量（见 quality-criteria.md）
   - 检查陈旧的文件/路径引用
   - 标记过大的文件

2. 查找 .claude/rules/ 主题文件。检查大小（目标：20-80 行）。

3. 从现有文件中检测项目类型（见 project-types.md）。
   检查是否存在预期的文档（ARCHITECTURE.md、DATABASE_SCHEMA.md 等）。

4. 查找公共 Markdown（README.md、LICENSE、CONTRIBUTING.md）。
   检查与 CLAUDE.md 内容的重叠。

5. 检查 auto-memory 在 ~/.claude/projects/*/memory/MEMORY.md

6. 如果 Cloudflare 项目：查找所有 wrangler.jsonc/wrangler.toml 文件。
   检查每个文件是否包含 "observability": { "enabled": true }。标记任何缺少它的文件。

优先选择 Read/Glob/Grep 工具而不是 Bash。如果你需要扫描许多文件或跨仓库聚合数据，请将 Python 脚本写入 .jez/scripts/ 并运行一次，而不是运行许多单独的 bash 命令（首先运行 mkdir -p .jez/scripts）。

返回：项目类型、质量分数、缺失文档、陈旧引用、重叠、大小违规、可观察性差距和总 Markdown 脚本足迹。
```

### 并行执行

对于全面健康检查，**并行启动两个代理**：

```
Task(subagent_type: "general-purpose", name: "permission-audit", prompt: "...")
Task(subagent_type: "general-purpose", name: "context-audit", prompt: "...")
```

两个都返回摘要。主代理将它们合并成一个报告并提出修复建议。

## 模式 1：全面健康检查

**默认模式。** 随时运行。

### 步骤

1. 并行启动权限审计员和上下文审计员代理
2. 将发现结果合并到一个报告中：

   ```
   ## 项目健康报告

   **项目类型**：[检测到的类型]
   **CLAUDE.md 质量**：[分数]/100 ([等级])

   ### 权限
   - 缺失 MCP 服务器：[列表]
   - 泄露的秘密：[数量] 找到
   - 遗留语法：[数量] 条目
   - 缺失预设：[列表]

   ### 上下文
   - 过大的文件：[列表]
   - 陈旧引用：[列表]
   - 缺失文档：[列表]
   - 重叠：[列表]

   ### 推荐修复
   1. [修复 1]
   2. [修复 2]
   ...
   ```

3. 在单次是/否确认后应用修复

## 模式 2：新项目设置

**当**：不存在 .claude/settings.local.json，或用户说 "设置" / "启动"。

### 步骤

1. **检测项目类型** 从现有文件：

   | 指示器 | 类型 | 预设 |
   |-----------|------|--------|
   | `wrangler.jsonc` 或 `wrangler.toml` | cloudflare-worker | JS/TS + Cloudflare |
   | `vercel.json` 或 `next.config.*` | vercel-app | JS/TS + Vercel |
   | `astro.config.*` | astro | JS/TS + 静态网站 |
   | `package.json`（无部署目标） | javascript-typescript | JS/TS |
   | `pyproject.toml` 或 `setup.py` 或 `requirements.txt` | python | Python |
   | `Cargo.toml` | rust | Rust |
   | `go.mod` | go | Go |
   | `Gemfile` 或 `Rakefile` | ruby | Ruby |
   | `composer.json` 或 `wp-config.php` | php | PHP |
   | `pom.xml` 或 `build.gradle*` | java | Java/JVM |
   | `*.sln` 或 `*.csproj` | dotnet | .NET |
   | `mix.exs` | elixir | Elixir |
   | `Package.swift` | swift | Swift + macOS |
   | `pubspec.yaml` | flutter | 移动端 |
   | `Dockerfile` 或 `docker-compose.yml` | docker | Docker |
   | `fly.toml` 或 `railway.json` 或 `netlify.toml` | hosted-app | 托管平台 |
   | `supabase/config.toml` | supabase | 托管 + 数据库 |
   | `.claude/agents/` 或操作脚本 | ops-admin | — |
   | 空目录 | 询问用户 | — |

   类型堆叠（例如 cloudflare-worker + javascript-typescript）。

2. **生成 .claude/settings.local.json**：
   - 阅读 [references/permission-presets.md](references/permission-presets.md)
   - 总是包含通用基础（包含 .claude/** 和 //tmp/** 的文件访问）
   - 添加检测到的语言 + 部署预设
   - 检查全局 `~/.claude/settings.local.json` 是否有相对于家的文件访问模式（`~/Documents/**`、`~/.claude/**`）。如果没有，建议在那里添加它们（不在项目文件中——家路径仅应在全局设置中）
   - **启动权限审计员代理** 以发现 MCP 服务器并添加每台服务器的通配符
   - 总是包含 `WebSearch`、`WebFetch`
   - 总是包含显式的 `gh` 子命令（workaround for `Bash(gh *)` bug）
   - 使用 `//` 注释组写入

3. **生成 CLAUDE.md**：
   - 阅读 [references/templates.md](references/templates.md)
   - 使用适合项目类型的模板

4. **生成 .gitignore**：
   - 阅读 [references/templates.md](references/templates.md)
   - 总是包含 `.claude/settings.local.json`、`.claude/plans/`、`.jez/screenshots/`、`.jez/artifacts/`
   - 不要 gitignore `.jez/scripts/`——生成的脚本值得保留

5. **可选**（先询问）：`git init` + `gh repo create`

6. **警告**： "项目 settings.local.json 遮蔽全局设置（不会合并）。会话需要重新启动。"

## 模式 3：整理权限

**当**：用户说 "整理权限" 或健康检查发现权限问题。

启动权限审计员代理，然后应用其推荐的修复。

## 模式 4：捕获学习

**当**：会话结束，"捕获学习" 或 "保存我们学到的"。

这将在 **主上下文中运行**（不是子代理），因为它需要访问对话历史。

1. 审查对话以保存值得保留的发现
2. 决定放置：
   ```
   应用于所有项目？
   ├── 是 → ~/.claude/rules/<主题>.md
   └── 否  → 特定于子目录？
       ├── 是 → <目录>/CLAUDE.md
       └── 否  → 引用或操作？
           ├── 引用 → docs/ 或 ARCHITECTURE.md
           └── 操作 → ./CLAUDE.md（根）
   ```
3. 将所有更改作为单个批次的差异草稿
4. 单次是/否确认后应用

**保持简洁**：每个概念一行。

## 模式 5：添加预设

**当**： "添加 python 权限"、"添加 docker"、"添加 MCP 服务器"。

1. 从 [references/permission-presets.md](references/permission-presets.md) 读取预设
2. 读取现有的 .claude/settings.local.json
3. 合并而不重复
4. 提醒：**会话需要重新启动**

## 模式 6：重构上下文

**当**：根 CLAUDE.md 超过 200 行，"重构内存"。

1. 首先启动上下文审计员代理
2. 根据发现：
   - 将过大的 CLAUDE.md 分割为 `.claude/rules/<主题>.md`
   - 将目录特定内容提取到子目录 CLAUDE.md
   - 将参考材料移动到 `docs/`
   - 解决重叠
   - 为项目类型创建缺失的文档
3. 提出计划，批准后应用

### 大小目标

| 文件 | 目标 | 最大值 |
|------|--------|---------|
| 根 CLAUDE.md | 50-150 行 | 200 |
| 子目录 CLAUDE.md | 15-50 行 | 80 |
| 规则主题文件 | 20-80 行 | 120 |

## 权限语法快速参考

| 模式 | 含义 |
|---------|---------|
| `Bash(git *)` | 推荐——空格在 `*` 前面 = 单词边界 |
| `Bash(nvidia-smi)` | 完全匹配，无参数 |
| `WebFetch` | 普通网络获取 |
| `WebSearch` | 普通网络搜索 |
| `mcp__servername__*` | 一个 MCP 服务器上的所有工具 |

### 什么不起作用

| 模式 | 原因 |
|---------|-----|
| `mcp__*` | 通配符不能跨越 `__` 边界 |
| `mcp__*__*` | 仍然不起作用 |
| `Bash(git:*)` | 已弃用的冒号语法（工作但推荐空格） |

### 重要行为

- **不热重载**：`settings.local.json` 编辑需要会话重新启动
- **"不再询问"** 在运行时注入（无需重新启动）使用冒号格式——正常
- **遮蔽，不合并**：项目设置完全替换全局
- **`gh` 错误**：`Bash(gh *)` 有时错过子命令——包括显式的 `Bash(gh issue *)` 等

## 自主性

- **直接做**：检测项目类型、启动审计代理、发现 MCP 服务器
- **简短确认**：写入/更新文件（单次批量是/否）
- **先询问**：git init、GitHub 仓库、删除现有内容、重大重构

## 参考文件

| 当**时** | 读取 |
|------|------|
| 构建权限预设 | [references/permission-presets.md](references/permission-presets.md) |
| 生成 CLAUDE.md、.gitignore | [references/templates.md](references/templates.md) |
| 评分 CLAUDE.md 质量 | [references/quality-criteria.md](references/quality-criteria.md) |
| 检测项目类型 + 预期文档 | [references/project-types.md](references/project-types.md) |
| 设置提交捕获钩子 | [references/commit-hook.md](references/commit-hook.md) |
