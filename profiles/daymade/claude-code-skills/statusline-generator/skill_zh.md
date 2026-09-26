# 状态行生成器

Claude Code 的单一事实来源状态行。一个脚本，两种布局，端到端自我验证。

## 快速健康检查（当出现问题时从这里开始）

每次状态行行为异常时，首先运行此命令。它捕获了大多数“配置但未工作”报告的静默失败：

```bash
bash scripts/health_check.sh
```

它验证四个层级：
1. `~/.claude/statusline.sh` 存在且可执行。**缺少 `chmod +x` 是最常见的静默失败原因** — Claude Code 运行脚本，`exec` 失败，状态行变空白。
2. `~/.claude/settings.json` 包含指向脚本的有效的 `statusLine` 块。
3. 模拟标准输入测试，覆盖完整数据、零令牌、缺失字段、`$HOME` 路径缩短和零分叉 git 分支渲染（通过合成 `.git/HEAD` — 无需 git 二进制文件）。
4. 如果您之前使用 `CLAUDE_STATUSLINE_DEBUG=1` 运行，则从 `/tmp/.claude-statusline-last-stdin.json` 重放真实标准输入。

每个失败都会打印一条修复命令 — 您无需阅读文档即可恢复。

## 快速安装

```bash
bash scripts/install_statusline.sh
```

此脚本：
- 备份任何现有的 `~/.claude/statusline.sh` 和 `settings.json`。
- 将 `generate_statusline.sh` 复制到 `~/.claude/statusline.sh` 并执行 `chmod +x`。
- 通过 `jq` 更新 `settings.json` 的 `statusLine` 块（保留其他设置）。
- **强制运行 `health_check.sh` 并显示结果** — 验证通过前安装不算是“完成”。

重启 Claude Code（或发送任何新消息）以查看状态行更新。

## 您将获得什么

### 默认 — 最小单行布局

```
~/code/myproject  [main]  Opus 4.7 (1M 上下文)  ctx: 108K / 1M
```

仅包含基本内容：短路径、git 分支、模型名称、绝对令牌计数。
无颜色、无成本、无百分比。分支读取 **零分叉** — 脚本将 `.git/HEAD` 作为普通文件读取（具有 worktree/子模块 `gitdir:` 指向和分离 HEAD 短 SHA 处理），而不是生成 `git`，因此成本为零，即使在没有 git 二进制文件的主机上也能工作。

### 全部 — 多行带成本和 git

在您的 shell 配置文件中设置 `CLAUDE_STATUSLINE_LAYOUT=full` 以启用：

```
alex (Sonnet 4.6) [$0.42/$25.93]  ctx: 108K/1M (11%)
~/code/myproject
[git:main*+]
```

- 行 1：用户、模型、ccusage 会话/每日成本、颜色编码的 ctx（绿色 ≤50%、黄色 51–80%、红色 >80%）。
- 行 2：短路径。
- 行 3：git 分支，`*` 表示已修改，`+` 表示未跟踪。

## 布局：如何切换

脚本从环境变量读取布局，而不是标志（Claude Code 通过标准输入传递 JSON，因此标志会冲突）。在 `~/.zshrc` 或 `~/.bashrc` 中设置：

```bash
# 最小（默认 — 与不设置相同）
export CLAUDE_STATUSLINE_LAYOUT=minimal

# 全部
export CLAUDE_STATUSLINE_LAYOUT=full
```

重启您的 shell（或 `source` 配置文件）以便 Claude Code 继承更改，然后发送消息 — 状态行将在 300 毫秒内刷新。

## 调试标准输入捕获

要查看 Claude Code 发送给您的脚本的确切 JSON：

```bash
export CLAUDE_STATUSLINE_DEBUG=1
```

每次调用都会将其标准输入写入 `/tmp/.claude-statusline-last-stdin.json`
（每次刷新时覆盖）。使用 `jq .` 检查。适用于：

- 诊断为什么某个字段未按预期渲染。
- 使用真实输入重新运行脚本：`cat /tmp/.claude-statusline-last-stdin.json | ~/.claude/statusline.sh`。
- 提交错误报告 — 将转储粘贴为基准事实。

## 编写规则（为什么这项技能是这样设计的）

三种生产失败模式驱动了当前设计。所有这些都封闭在代码中，而不仅仅是文档：

### 规则 1 — 始终 `chmod +x`，始终通过运行验证

任何状态行的最大静默失败原因是缺少可执行位：Claude Code 的 `exec` 静默失败，条形图变空白且无错误。`install_statusline.sh` 始终 `chmod +x`；`health_check.sh` 如果缺少则标记该位。**如果您手写或手编辑状态行脚本，请在声明完成前进行模拟测试**：`echo '{}' | bash your-script.sh`。

### 规则 2 — “配置完成”在没有证据的情况下是无意义的

“编写了文件并更新了 settings.json” 与“脚本运行并产生预期输出”并不相同。因此，`install_statusline.sh` 始终在末尾运行 `health_check.sh`，如果任何检查失败则非零退出。
将任何缺乏证据的代理的“完成！”报告视为可疑。

### 规则 3 — 状态行是热点路径：预算子进程，而不仅仅是正确性

状态行脚本看起来像 UI 美化，但它在每个并发代理会话的每次刷新时执行。它生成的任何内容都会被刷新速率 × 活会话数相乘，全天。在运行许多并发会话的机器上测量：一个包运行器状态行（`bunx <pkg>@latest` 风格，每次刷新都会重新解析注册表并重新写入锁文件，然后运行 `git status` + `git branch`）每次刷新成本约 0.4 秒 CPU；此脚本成本约 0.01 秒。在许多会话中，这个差异是机器级进程波动、热量和电池的可测量份额 — 在一项真实的电池消耗调查（2026-07）中发现，状态行是顶级贡献者之一。

具体来说：
- **刷新时切勿解析包。** `statusLine.command` 中没有 `bunx`/`npx` `@latest` — 固定并安装一次，或使用本地脚本。
- **不要为分支生成 `git`。** 将 `.git/HEAD` 作为文件读取（见脚本中的 `git_branch_fast`）— 相同答案，零子进程。
- **将 `git status`（脏状态）视为奢侈品。** 它在每次刷新时遍历工作树；只有完整布局运行它，并且只有在明确启用时才运行。
- **预算：状态行刷新应成本为个位数毫秒，最多几个分叉**（这里有一个 `jq` + 一个 `awk`）。

有关字段级陷阱（`used_percentage` 在会话开始时为空、`total_input_tokens` 在 Claude Code 版本之间的语义、硬编码 `context_window_size`），请参阅 [`references/context-window-schema.md`](references/context-window-schema.md)。

## 自定义

有关颜色、自定义段（主机名、时间等）和禁用成本跟踪，请参阅 [`references/customization.md`](references/customization.md)。

## 依赖项

脚本自动检测可用工具并优雅降级：

| 工具 | 用于 | 回退 |
|------|-------------|----------|
| `jq` | JSON 解析（首选） | 回退到 `python3` |
| `python3` | JSON 解析回退 | 仅当前工作目录 |
| `awk` | 令牌 K/M 格式化 | 两种布局都需要 |
| `git` | 脏状态 `*`/`+` 标记（仅完整布局 — 最小从 `.git/HEAD` 读取分支而不需要 git） | 缺失或不在代码库中时静默跳过 |
| `ccusage` | 成本（完整布局） | 缺失时静默跳过 |

在 macOS 上安装：`brew install jq`。在 Debian/Ubuntu 上：`apt install jq`。

## 故障排除

有关按症状诊断，请参阅
[`references/troubleshooting-decision-tree.md`](references/troubleshooting-decision-tree.md)。
它将引导您完成：

1. 状态行空白或从未更新（chmod 原因）
2. ctx 段缺失或错误（字段陷阱）
3. 想要令牌计数而不是百分比（布局切换）
4. 颜色渲染为原始转义码（终端兼容性）
5. git 段缺失（完整布局）
6. 成本段缺失（ccusage / 缓存）
7. 编辑无效果（路径不匹配）
8. 刷新缓慢（jq vs python3）

## 资源

| 文件 | 目的 |
|------|---------|
| `scripts/generate_statusline.sh` | 状态行脚本。单一事实来源。通过 `CLAUDE_STATUSLINE_LAYOUT` 提供两种布局。 |
| `scripts/install_statusline.sh` | 不可变性安装器。备份、复制、chmod、连接 `settings.json`、运行健康检查。 |
| `scripts/health_check.sh` | 四层验证：文件权限、settings.json 连接、模拟标准输入测试、真实标准输入重放。 |
| `references/troubleshooting-decision-tree.md` | 症状驱动诊断流程图。状态行行为异常时加载。 |
| `references/customization.md` | 颜色更改、自定义段、阈值调整、单行完整布局。用户想要修改状态行外观时加载。 |
| `references/context-window-schema.md` | Claude Code 状态行 JSON 架构。记录每个字段以及 `current_usage` 与 `total_input_tokens` 在不同版本中的语义。 |
| `references/color_codes.md` | ANSI 颜色代码参考。颜色自定义时加载。 |
| `references/ccusage_integration.md` | ccusage 集成深入分析：缓存、JSON 形状、故障排除。成本相关问题时加载。 |
