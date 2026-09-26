# Clui CC — Claude Code 桌面悬浮窗

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能集合。

Clui CC 将 Claude Code CLI 封装在一个透明的、浮动的 macOS 悬浮窗中，支持多标签会话、权限审批 UI（PreToolUse HTTP 钩子）、通过 Whisper 的语音输入、对话历史记录和技能市场。它需要一个经过身份验证的 `claude` CLI，并且完全在本地运行 — 无需遥测数据或云依赖。

---

## 前置条件

| 要求 | 最低版本 | 备注 |
|---|---|---|
| macOS | 13+ | 悬浮窗仅限 macOS |
| Node.js | 18+ | 推荐使用 LTS 20 或 22 |
| Python | 3.10+ | 3.12+ 需要安装 `setuptools` |
| Claude Code CLI | 任意 | 必须经过身份验证 |
| Whisper CLI | 任意 | 用于语音输入 |

```bash
# 1. Xcode CLI 工具（本地模块编译）
xcode-select --install

# 2. 通过 Homebrew 安装 Node.js
brew install node
node --version   # 确认 ≥18

# 3. Python setuptools（3.12+ 需要安装）
python3 -m pip install --upgrade pip setuptools

# 4. Claude Code CLI
npm install -g @anthropic-ai/claude-code

# 5. 认证 Claude Code
claude

# 6. 用于语音输入的 Whisper
brew install whisper-cli
```

---

## 安装

### 推荐：应用安装程序（非开发者）

```bash
git clone https://github.com/lcoutodemos/clui-cc.git
# 然后在 Finder 中打开 clui-cc 文件夹并双击 install-app.command
```

首次启动时 macOS 可能会阻止未签名的应用 — 前往 **系统设置 → 隐私与安全性 → 无论如何都打开**。

### 开发者工作流程

```bash
git clone https://github.com/lcoutodemos/clui-cc.git
cd clui-cc
npm install
npm run dev       # 热重载渲染器；主进程更改时重启
```

### 命令脚本

```bash
./commands/setup.command    # 环境检查 + 安装依赖
./commands/start.command    # 从源代码构建并启动
./commands/stop.command     # 停止所有 Clui CC 进程

npm run build               # 生产构建（无打包）
npm run dist                # 打包为 macOS .app → release/
npm run doctor              # 环境诊断
```

---

## 快捷键

| 快捷键 | 动作 |
|---|---|
| `⌥ + Space` | 显示/隐藏悬浮窗 |
| `Cmd + Shift + K` | 备用切换（如果 `⌥+Space` 被占用） |

---

## 架构

```
UI 提示 → 主进程启动 claude -p → NDJSON 流 → 实时渲染
                                         → 工具调用？ → 权限 UI → 批准/拒绝
```

### 进程流程

1. 每个标签启动 `claude -p --output-format stream-json` 作为子进程。
2. `RunManager` 解析 NDJSON；`EventNormalizer` 规范化事件。
3. `ControlPlane` 管理标签生命周期：`连接中 → 空闲 → 运行中 → 完成/失败/已死`。
4. 工具权限请求通过 HTTP 钩子到达 `PermissionServer`（仅限本地主机）。
5. 渲染器每 1.5 秒轮询后端健康状态并协调标签状态。
6. 会话使用 `--resume <session-id>` 恢复。

### 项目结构

```
src/
├── main/
│   ├── claude/       # ControlPlane, RunManager, EventNormalizer
│   ├── hooks/        # PermissionServer (PreToolUse HTTP 钩子)
│   ├── marketplace/  # 插件目录获取 + 安装
│   ├── skills/       # 技能自动安装器
│   └── index.ts      # 窗口创建、IPC 处理器、托盘
├── renderer/
│   ├── components/   # TabStrip, ConversationView, InputBar, …
│   ├── stores/       # Zustand 会话存储
│   ├── hooks/        # 事件监听器、健康状态协调
│   └── theme.ts      # 双色板 + CSS 自定义属性
├── preload/          # 安全 IPC 桥接（window.clui API）
└── shared/           # 标准类型、IPC 通道定义
```

---

## IPC API (`window.clui`)

预加载桥接在渲染器中暴露 `window.clui`。关键方法：

```typescript
// 向活动标签的 claude 进程发送提示
window.clui.sendPrompt(tabId: string, text: string): Promise<void>

// 批准或拒绝待处理的工具使用权限
window.clui.resolvePermission(requestId: string, approved: boolean): Promise<void>

// 创建新标签（启动新的 claude -p 进程）
window.clui.createTab(): Promise<{ tabId: string }>

// 通过 ID 恢复过去会话
window.clui.resumeSession(tabId: string, sessionId: string): Promise<void>

// 订阅来自标签的规范化事件
window.clui.onTabEvent(tabId: string, callback: (event: NormalizedEvent) => void): () => void

// 获取对话历史记录列表
window.clui.getHistory(): Promise<SessionMeta[]>
```

---

## 使用标签和会话

### 创建标签并发送提示（渲染器）

```typescript
import { useEffect, useState } from 'react'

export function useClaudeTab() {
  const [tabId, setTabId] = useState<string | null>(null)
  const [messages, setMessages] = useState<NormalizedEvent[]>([])

  useEffect(() => {
    window.clui.createTab().then(({ tabId }) => {
      setTabId(tabId)

      const unsubscribe = window.clui.onTabEvent(tabId, (event) => {
        setMessages((prev) => [...prev, event])
      })

      return unsubscribe
    })
  }, [])

  const send = (text: string) => {
    if (!tabId) return
    window.clui.sendPrompt(tabId, text)
  }

  return { messages, send }
}
```

### 恢复过去会话

```typescript
async function resumeLastSession() {
  const history = await window.clui.getHistory()
  if (history.length === 0) return

  const { tabId } = await window.clui.createTab()
  const lastSession = history[0] // 最新的在前面
  await window.clui.resumeSession(tabId, lastSession.sessionId)
}
```

---

## 权限审批 UI

工具调用在执行前通过 PreToolUse HTTP 钩子被 `PermissionServer` 拦截。渲染器接收 `permission_request` 事件并必须解决它。

```typescript
// 渲染器：监听权限请求
window.clui.onTabEvent(tabId, async (event) => {
  if (event.type !== 'permission_request') return

  const { requestId, toolName, toolInput } = event

  // 显示你的审批 UI，然后：
  const approved = await showApprovalDialog({ toolName, toolInput })
  await window.clui.resolvePermission(requestId, approved)
})
```

```typescript
// 主进程：PermissionServer 使用 claude -p 注册钩子
// 钩子端点接收来自 Claude Code 的 POST 请求，例如：
// { "tool": "bash", "input": { "command": "rm -rf dist/" }, "session_id": "..." }
// 它会保留请求，直到渲染器解决它。
```

---

## 语音输入

语音输入使用本地 Whisper。它由 `install-app.command` 自动安装或通过 `brew install whisper-cli` 安装。无需 API 密钥 — 文本转录完全在设备上运行。

```typescript
// 从 InputBar 组件通过 IPC 触发
window.clui.startVoiceInput(): Promise<void>
window.clui.stopVoiceInput(): Promise<{ transcript: string }>
```

---

## 技能市场

无需离开 UI 即可从 Anthropic 的 GitHub 仓库安装技能（插件）。

```typescript
// 获取可用技能（5 分钟缓存，从 raw.githubusercontent.com 获取）
const skills = await window.clui.marketplace.list()
// [{ id, name, description, repoUrl, version }, ...]

// 安装技能（从 api.github.com 下载 tarball）
await window.clui.marketplace.install(skillId: string)

// 列出已安装技能
const installed = await window.clui.marketplace.listInstalled()
```

市场进行的网络调用：

| 端点 | 目的 | 是否必需 |
|---|---|---|
| `raw.githubusercontent.com/anthropics/*` | 技能目录（5 分钟缓存） | 否 — 优雅回退 |
| `api.github.com/repos/anthropics/*/tarball/*` | 技能 tarball 下载 | 否 — 失败时跳过 |

---

## 主题配置

```typescript
// src/renderer/theme.ts — 双色板与 CSS 自定义属性
// 通过 UI 或程序化切换：
window.clui.setTheme('dark' | 'light' | 'system')
```

自定义 CSS 属性应用于 `:root` 并可以在渲染器样式表中覆盖：

```css
:root {
  --clui-bg: rgba(20, 20, 20, 0.85);
  --clui-text: #f0f0f0;
  --clui-accent: #7c5cfc;
  --clui-pill-radius: 24px;
}
```

---

## 添加自定义技能

技能自动从 `~/.clui/skills/` 加载。一个技能是一个包含 `skill.js` 入口的目录：

```typescript
// ~/.clui/skills/my-skill/skill.js
module.exports = {
  name: 'my-skill',
  version: '1.0.0',
  description: '做一些有用的事',

  // 当技能通过匹配的提示被激活时调用
  async onPrompt(context) {
    const { prompt, tabId, clui } = context
    if (!prompt.includes('my trigger')) return false   // 透传

    await clui.sendMessage(tabId, `由 my-skill 处理：${prompt}`)
    return true  // 消耗 — 不要转发给 claude
  },
}
```

---

## 故障排除

### 自检

```bash
npm run doctor
```

### 常见问题

**首次启动应用被阻止**
→ 系统设置 → 隐私与安全性 → 无论如何都打开

**`node-pty` 编译失败**
```bash
xcode-select --install
python3 -m pip install --upgrade pip setuptools
npm install
```

**找不到 `claude`**
```bash
npm install -g @anthropic-ai/claude-code
claude   # 认证
which claude   # 确认它在 PATH 中
```

**找不到 Whisper**
```bash
brew install whisper-cli
which whisper-cli
```

**PermissionServer 端口冲突**
HTTP 钩子服务器仅在本机运行。如果另一个进程占用了它的端口，使用以下命令重启：
```bash
./commands/stop.command
./commands/start.command
```

**`setuptools` 缺失（Python 3.12+）**
```bash
python3 -m pip install --upgrade pip setuptools
```

**悬浮窗不显示**
- 尝试备用快捷键：`Cmd + Shift + K`
- 确认 Clui CC 拥有辅助功能权限：系统设置 → 隐私与安全性 → 辅助功能

---

## 测试版本

| 组件 | 版本 |
|---|---|
| macOS | 15.x Sequoia |
| Node.js | 20.x LTS, 22.x |
| Python | 3.12 (+ setuptools) |
| Electron | 33.x |
| Claude Code CLI | 2.1.71 |

---

## 参考

- [Claude Code 文档](https://docs.anthropic.com/en/docs/claude-code)
- [架构深入](docs/ARCHITECTURE.md)
- [故障排除指南](docs/TROUBLESHOOTING.md)
- [MIT 许可证](LICENSE)
