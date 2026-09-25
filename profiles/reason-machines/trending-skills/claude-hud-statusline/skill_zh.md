# Claude HUD

> 技能来自 [ara.so](https://ara.so) — 2026每日技能集合。

Claude HUD 是一个 Claude Code 插件，它为您的终端添加一个持续的状态行，实时显示上下文窗口使用情况、活动工具调用、运行的子代理和待办进度 — 始终显示在您的输入提示下方。

## 功能

| 功能 | 描述 |
|------|------|
| **上下文健康度** | 显示上下文窗口已满程度（绿色 → 黄色 → 红色）的状态条 |
| **工具活动** | 实时显示文件读取、编辑和搜索 |
| **代理跟踪** | 显示正在运行的子代理及其操作 |
| **待办进度** | 实时任务完成跟踪 |
| **使用限制** | Claude 订阅者的速率限制消耗 |
| **Git 状态** | 当前分支、脏状态、远程 ahead/behind |

## 要求

- Claude Code v1.0.80+
- Node.js 18+ 或 Bun

## 安装

在 Claude Code 会话中运行以下命令：

**步骤 1：添加市场**
```
/plugin marketplace add jarrodwatts/claude-hud
```

**步骤 2：安装插件**
```
/plugin install claude-hud
```

> **Linux 用户**：如果出现 `EXDEV: cross-device link not permitted`，请先设置 TMPDIR：
> ```bash
> mkdir -p ~/.cache/tmp && TMPDIR=~/.cache/tmp claude
> ```

**步骤 3：配置状态行**
```
/claude-hud:setup
```

> **Windows 用户**：如果设置报告未找到 JavaScript 运行时，请先安装 Node.js LTS：
> ```powershell
> winget install OpenJS.NodeJS.LTS
> ```

**步骤 4：重启 Claude Code** 以加载新的 `statusLine` 配置。

## 您将看到的内容

### 默认 2 行布局
```
[Opus] │ my-project git:(main*)
Context █████░░░░░ 45% │ Usage ██░░░░░░░░ 25% (1h 30m / 5h)
```

### 启用可选行
```
[Opus] │ my-project git:(main*)
Context █████░░░░░ 45% │ Usage ██░░░░░░░░ 25% (1h 30m / 5h)
◐ 编辑：auth.ts | ✓ 读取 ×3 | ✓ Grep ×2
◐ explore [haiku]: 查找 auth 代码 (2m 15s)
▸ 修复认证错误 (2/5)
```

## 配置

### 交互式配置（推荐）
```
/claude-hud:configure
```

这将打开一个带预设选项的引导流程：

| 预设 | 显示内容 |
|------|----------|
| **完整** | 所有内容 — 工具、代理、待办、Git、使用情况、持续时间 |
| **核心** | 活动行 + Git，最小化杂乱 |
| **最小** | 仅模型名称和上下文条 |

### 手动配置

直接编辑 `~/.claude/plugins/claude-hud/config.json`：

```json
{
  "lineLayout": "expanded",
  "pathLevels": 2,
  "elementOrder": ["project", "context", "usage", "tools", "agents", "todos"],
  "gitStatus": {
    "enabled": true,
    "showDirty": true,         // "main*" 表示未提交的更改
    "showAheadBehind": true,   // "main ↑2 ↓1"
    "showFileStats": true      // "main* !3 +1 ?2" (已修改/添加/删除/未跟踪)
  },
  "display": {
    "showModel": true,
    "showContextBar": true,
    "contextValue": "percent",
    "showUsage": true,
    "usageBarEnabled": true,
    "showTools": true,
    "showAgents": true,
    "showTodos": true,
    "showDuration": false,
    "showSpeed": false,
    "showConfigCounts": false,
    "showMemoryUsage": false,
    "showSessionName": false,
    "showClaudeCodeVersion": false,
    "sevenDayThreshold": 80,
    "showTokenBreakdown": true
  },
  "colors": {
    "context": "green",
    "usage": "brightBlue",
    "warning": "yellow",
    "usageWarning": "brightMagenta",
    "critical": "red",
    "model": "cyan",
    "project": "yellow",
    "git": "magenta",
    "gitBranch": "cyan",
    "label": "dim",
    "custom": "208"
  }
}
```

## 关键配置选项

### 布局
```json
{
  "lineLayout": "expanded",   // "expanded"（多行）或 "compact"（单行）
  "pathLevels": 1             // 1-3 级目录路径
}
```

路径级别示例：
- `1` → `[Opus] │ my-project git:(main)`
- `2` → `[Opus] │ apps/my-project git:(main)`
- `3` → `[Opus] │ dev/apps/my-project git:(main)`

### 上下文显示格式
```json
{
  "display": {
    "contextValue": "percent"    // "45%"
    // "contextValue": "tokens"  // "45k/200k"
    // "contextValue": "remaining" // "55% remaining"
    // "contextValue": "both"    // "45% (45k/200k)"
  }
}
```

### 元素排序（扩展布局）
```json
{
  "elementOrder": ["project", "context", "usage", "memory", "environment", "tools", "agents", "todos"]
}
```
省略数组中的任何条目以完全隐藏它。

### Git 状态选项
```json
{
  "gitStatus": {
    "enabled": true,
    "showDirty": true,         // "main*" 表示未提交的更改
    "showAheadBehind": true,   // "main ↑2 ↓1"
    "showFileStats": true      // "main* !3 +1 ?2" (已修改/添加/删除/未跟踪)
  }
}
```

### 颜色

支持的颜色值：命名颜色（`dim`、`red`、`green`、`yellow`、`magenta`、`cyan`、`brightBlue`、`brightMagenta`）、256 色编号（`0-255`）或十六进制（`#rrggbb`）。

```json
{
  "colors": {
    "context": "#00FF88",
    "model": "208",
    "project": "#FF6600"
  }
}
```

## 工作原理

Claude HUD 使用 Claude Code 的原生 **状态行 API** — 无需单独窗口，无需 tmux：

```
Claude Code → stdin JSON → claude-hud → stdout → 终端状态行
           ↘ transcript JSONL (工具、代理、待办实时解析)
```

- 令牌数据直接来自 Claude Code（非估计）
- 随报告的上下文窗口大小扩展，包括 1M 上下文会话
- 解析 transcript 以获取工具/代理活动
- 每 ~300ms 更新一次

## 常见模式

### 聚焦工作的最小配置
```json
{
  "lineLayout": "compact",
  "display": {
    "showModel": true,
    "showContextBar": true,
    "contextValue": "percent",
    "showUsage": false,
    "showTools": false,
    "showAgents": false,
    "showTodos": false
  }
}
```

### 完全监控配置
```json
{
  "lineLayout": "expanded",
  "pathLevels": 2,
  "gitStatus": {
    "enabled": true,
    "showDirty": true,
    "showAheadBehind": true,
    "showFileStats": true
  },
  "display": {
    "showTools": true,
    "showAgents": true,
    "showTodos": true,
    "showDuration": true,
    "showMemoryUsage": true,
    "showConfigCounts": true,
    "contextValue": "both",
    "showTokenBreakdown": true
  }
}
```

### 始终显示 7 天使用情况
```json
{
  "display": {
    "showUsage": true,
    "sevenDayThreshold": 0
  }
}
```
输出：`Context █████░░░░░ 45% │ Usage ██░░░░░░░░ 25% (1h 30m / 5h) | ██████████ 85% (2d / 7d)`

## 故障排除

**HUD 设置后未出现**
- 完全重启 Claude Code（在终端中退出并重新运行 `claude`）
- 在 macOS 上，确保您已完全退出应用程序，而不仅仅是关闭窗口

**配置未应用**
- 检查 JSON 语法错误 — 无效的 JSON 会静默回退到默认值
- 验证：`cat ~/.claude/plugins/claude-hud/config.json | node -e "JSON.parse(require('fs').readFileSync('/dev/stdin','utf8'))"`
- 删除配置并运行 `/claude-hud:configure` 以重新生成

**Git 状态缺失**
- 验证您处于 git 仓库中（`git status`）
- 确保 `gitStatus.enabled` 在配置中不是 `false`

**工具/代理/待办行未显示**
- 这些行默认隐藏 — 使用 `showTools`、`showAgents`、`showTodos` 启用
- 仅在有活动要显示时才渲染行

**使用限制未显示**
- 需要一个 Claude 订阅账户（不仅是 API 密钥）
- AWS Bedrock 用户会看到 `Bedrock` 标签；使用情况在 AWS 控制台中管理
- 使用数据可能为空，直到新会话中的第一个模型响应后
- 不支持 `rate_limits` 的旧 Claude Code 版本不会显示订阅者使用情况

**Linux 安装时出现跨设备错误**
```bash
mkdir -p ~/.cache/tmp && TMPDIR=~/.cache/tmp claude
# 然后在会话中运行 /plugin install claude-hud
```

**Windows：未找到 JavaScript 运行时**
```powershell
winget install OpenJS.NodeJS.LTS
# 重启 Shell，然后再次运行 /claude-hud:setup
```

## 插件命令参考

| 命令 | 描述 |
|------|------|
| `/plugin marketplace add jarrodwatts/claude-hud` | 注册插件源 |
| `/plugin install claude-hud` | 安装插件 |
| `/claude-hud:setup` | 初始设置向导，写入 `statusLine` 配置 |
| `/claude-hud:configure` | 带预览的交互式配置 |

## 配置文件位置

```
~/.claude/plugins/claude-hud/config.json
```
