# 珠子 - AI代理的持久任务内存

基于图的Issue追踪器，能够在对话压缩时存活。为具有复杂依赖关系的多会话工作提供持久化内存。

## bd 与 TodoWrite 对比

**决策测试**：“两周后我是否需要这个上下文？” 是 = bd，否 = TodoWrite。

| bd (持久化) | TodoWrite (易失性) |
|-------------|-------------------|
| 多会话、依赖关系、压缩存活 | 单会话线性任务 |
| Dolt支持的团队同步 | 对话范围 |

详细比较请参阅 [BOUNDARIES.md](resources/BOUNDARIES.md)。

## 前置条件

```bash
bd --version  # 需要 v0.60.0+
```

- **bd CLI** 安装并包含在PATH中
- **Git仓库**（可选 — 使用 `BEADS_DIR` + `--stealth` 进行无git操作）
- **初始化**：运行一次 `bd init`（由人类执行，而非代理）

## CLI参考

**运行 `bd prime`** 获取AI优化的工作流上下文（由钩子自动加载）。
**运行 `bd <命令> --help`** 获取特定命令用法。

核心命令：`bd ready`，`bd create`，`bd show`，`bd update`，`bd close`，`bd dolt push`

## 会话协议

1. `bd ready` — 查找未阻塞的工作
2. `bd show <id>` — 获取完整上下文
3. `bd update <id> --claim` — 原子性申领并开始工作
4. 工作过程中添加笔记（对压缩存活至关重要）
5. `bd close <id> --reason "..."` — 完成任务
6. `bd dolt push` — 推送到Dolt远程（如果已配置）

## 输出

在任何命令后附加 `--json` 获取结构化输出。使用 `bd show <id> --long` 获取扩展元数据。状态图标：`○` 开启 `◐` 进行中 `●` 阻塞 `✓` 已关闭 `❄` 拖延。

## 错误处理

| 错误 | 解决方法 |
|------|---------|
| `database not found` | 在项目根目录运行 `bd init <prefix>` |
| `not in a git repository` | 先运行 `git init` |
| `disk I/O error (522)` | 将 `.beads/` 移离云同步文件系统 |
| 状态更新延迟 | 使用服务器模式：`bd dolt start` |

详细说明请参阅 [TROUBLESHOOTING.md](resources/TROUBLESHOOTING.md)。

## 示例

**追踪多会话功能：**
```bash
bd create "OAuth集成" -t epic -p 1 --json
bd create "令牌存储" -t task --deps blocks:oauth-id --json
bd ready --json                    # 显示未阻塞的工作
bd update <id> --claim --json      # 申领并开始
bd close <id> --reason "使用刷新令牌实现" --json
```

**压缩后恢复：** `bd list --status in_progress --json` 然后 `bd show <id> --long`

**任务中途发现工作：** `bd create "发现bug" -t bug -p 1 --deps discovered-from:<current-id> --json`

## 高级功能

| 功能 | CLI | 资源 |
|------|-----|------|
| 分子（模板） | `bd mol --help` | [MOLECULES.md](resources/MOLECULES.md) |
| 化学（倾倒/薄雾） | `bd pour`，`bd wisp` | [CHEMISTRY_PATTERNS.md](resources/CHEMISTRY_PATTERNS.md) |
| 代理珠子 | `bd agent --help` | [AGENTS.md](resources/AGENTS.md) |
| 异步门 | `bd gate --help` | [ASYNC_GATES.md](resources/ASYNC_GATES.md) |
| 工作树 | `bd worktree --help` | [WORKTREES.md](resources/WORKTREES.md) |

## 资源

| 类别 | 文件 |
|------|------|
| **入门指南** | [BOUNDARIES.md](resources/BOUNDARIES.md)，[CLI_REFERENCE.md](resources/CLI_REFERENCE.md) (实时参考指针)，[WORKFLOWS.md](resources/WORKFLOWS.md) |
| **核心概念** | [DEPENDENCIES.md](resources/DEPENDENCIES.md)，[ISSUE_CREATION.md](resources/ISSUE_CREATION.md)，[PATTERNS.md](resources/PATTERNS.md) |
| **韧性** | [RESUMABILITY.md](resources/RESUMABILITY.md)，[TROUBLESHOOTING.md](resources/TROUBLESHOOTING.md) |
| **高级** | [MOLECULES.md](resources/MOLECULES.md)，[CHEMISTRY_PATTERNS.md](resources/CHEMISTRY_PATTERNS.md)，[AGENTS.md](resources/AGENTS.md)，[ASYNC_GATES.md](resources/ASYNC_GATES.md)，[WORKTREES.md](resources/WORKTREES.md) |
| **参考** | [STATIC_DATA.md](resources/STATIC_DATA.md)，[INTEGRATION_PATTERNS.md](resources/INTEGRATION_PATTERNS.md) |

## 验证

如果 `bd --version` 报告高于 `0.60.0`，此技能可能已过时。运行 `bd prime` 获取当前CLI指导 — 它会随bd版本自动更新，是权威信息来源 ([ADR-0001](adr/0001-bd-prime-as-source-of-truth.md))。
