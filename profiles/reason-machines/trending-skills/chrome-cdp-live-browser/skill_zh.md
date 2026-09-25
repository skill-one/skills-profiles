# chrome-cdp: AI 代理的实时 Chrome 会话

> 技能由 [ara.so](https://ara.so) 提供 — 2026 每日技能集合。

`chrome-cdp` 通过 Chrome 开发者工具协议 (CDP) 将您的 AI 代理直接连接到正在运行的 Chrome 浏览器。与启动全新隔离浏览器的浏览器自动化工具不同，此工具连接到您已经打开的标签页，保留您的登录信息、Cookie 和当前页面状态。

## 功能

- **实时会话访问** — 读取并与您已登录的标签页交互
- **持久守护进程** — 每个标签页一个 WebSocket 守护进程；"允许调试"的模态框只会出现一次，而不会在每次命令时都出现
- **无需 npm 安装** — 仅需 Node.js 22+
- **支持 100+ 个标签页** — 可靠处理大量打开的标签页
- **跨域 iframe 支持** — 即使在跨域 iframe 内，`type` 命令也能正常工作

## 安装

### 作为 pi 技能

```bash
pi install git:github.com/pasky/chrome-cdp-skill@v1.0.1
```

### 手动安装（适用于 Amp、Claude Code、Cursor、Codex 等）

```bash
git clone https://github.com/pasky/chrome-cdp-skill
# 将 skills/chrome-cdp/ 目录复制到您的代理加载上下文的位置
```

### 在 Chrome 中启用远程调试

1. 打开 Chrome 并导航到：`chrome://inspect/#remote-debugging`
2. 切换 **"启用远程调试"** 开关

就这样。无需标志，无需重新启动 Chrome。

脚本会自动检测 macOS、Linux 和 Windows 上的 Chrome、Chromium、Brave、Edge 和 Vivaldi。对于非标准安装：

```bash
export CDP_PORT_FILE=/path/to/DevToolsActivePort
```

## 主要命令

所有命令都使用 `scripts/cdp.mjs` 作为入口点。`<target>` 是 `list` 命令显示的目标 ID 的唯一前缀。

### 列出打开的标签页

```bash
node scripts/cdp.mjs list
# 输出：
# A1B2C3  https://github.com/pasky/chrome-cdp-skill  chrome-cdp-skill
# D4E5F6  https://mail.google.com/mail/u/0/           Gmail
```

### 截取标签页屏幕截图

```bash
node scripts/cdp.mjs shot A1B2
# 保存屏幕截图到运行时目录，并打印文件路径
```

### 可访问性树（语义快照）

```bash
node scripts/cdp.mjs snap A1B2
# 返回紧凑的语义可访问性树 — 最佳用于理解页面结构
```

### 完整 HTML 或作用域 HTML

```bash
node scripts/cdp.mjs html A1B2                    # 完整页面 HTML
node scripts/cdp.mjs html A1B2 ".main-content"    # 作用域到 CSS 选择器
node scripts/cdp.mjs html A1B2 "#article-body"    # 作用域到 ID
```

### 执行 JavaScript

```bash
node scripts/cdp.mjs eval A1B2 "document.title"
node scripts/cdp.mjs eval A1B2 "window.location.href"
node scripts/cdp.mjs eval A1B2 "document.querySelectorAll('a').length"
```

### 导航到 URL

```bash
node scripts/cdp.mjs nav A1B2 https://example.com
# 导航并等待页面加载
```

### 网络资源时间

```bash
node scripts/cdp.mjs net A1B2
# 显示当前页面的网络资源时间
```

### 点击元素

```bash
node scripts/cdp.mjs click A1B2 "button.submit"
node scripts/cdp.mjs click A1B2 "#login-btn"
node scripts/cdp.mjs click A1B2 "[data-testid='confirm']"
```

### 在坐标处点击

```bash
node scripts/cdp.mjs clickxy A1B2 320 480
# 在 CSS 像素坐标 (x=320, y=480) 处点击
```

### 输入文本

```bash
node scripts/cdp.mjs type A1B2 "Hello, world!"
# 在当前聚焦的元素处输入 — 在跨域 iframe 中也能工作
```

### 加载更多（点击直到消失）

```bash
node scripts/cdp.mjs loadall A1B2 "button.load-more"
# 持续点击选择器，直到它从 DOM 中消失
```

### 打开新标签页

```bash
node scripts/cdp.mjs open
node scripts/cdp.mjs open https://example.com
# 注意：会触发 Chrome 的 "允许" 提示
```

### 停止守护进程

```bash
node scripts/cdp.mjs stop          # 停止所有守护进程
node scripts/cdp.mjs stop A1B2     # 停止特定标签页的守护进程
```

### 原生 CDP 命令透传

```bash
node scripts/cdp.mjs evalraw A1B2 "Page.getFrameTree"
node scripts/cdp.mjs evalraw A1B2 "Runtime.evaluate" '{"expression":"1+1"}'
```

## 常见模式

### 模式：读取已登录的页面

```bash
# 列出标签页以找到您的目标
node scripts/cdp.mjs list

# 获取语义视图的可访问性树
node scripts/cdp.mjs snap D4E5

# 或者获取特定部分的作用域 HTML
node scripts/cdp.mjs html D4E5 ".email-list"
```

### 模式：填写并提交表单

```bash
# 点击输入字段
node scripts/cdp.mjs click A1B2 "input[name='search']"

# 输入内容
node scripts/cdp.mjs type A1B2 "my search query"

# 点击提交
node scripts/cdp.mjs click A1B2 "button[type='submit']"

# 拍摄屏幕截图以验证结果
node scripts/cdp.mjs shot A1B2
```

### 模式：使用 JavaScript 提取数据

```bash
# 获取页面上的所有链接 href
node scripts/cdp.mjs eval A1B2 "Array.from(document.querySelectorAll('a')).map(a => a.href)"

# 获取特定元素的文本内容
node scripts/cdp.mjs eval A1B2 "document.querySelector('.price').textContent.trim()"

# 将表格数据作为 JSON 获取
node scripts/cdp.mjs eval A1B2 "
  Array.from(document.querySelectorAll('table tr')).map(row =>
    Array.from(row.querySelectorAll('td,th')).map(cell => cell.textContent.trim())
  )
"
```

### 模式：导航并等待

```bash
# 导航并立即读取页面
node scripts/cdp.mjs nav A1B2 https://news.ycombinator.com
node scripts/cdp.mjs snap A1B2
```

### 模式：分页内容

```bash
# 持续加载内容，直到 "加载更多" 按钮消失
node scripts/cdp.mjs loadall A1B2 "button[data-action='load-more']"

# 然后提取所有加载的内容
node scripts/cdp.mjs eval A1B2 "document.querySelectorAll('.item').length"
```

### 模式：脚本集成（Node.js）

```javascript
import { execFile } from 'node:child_process';
import { promisify } from 'node:util';

const exec = promisify(execFile);
const CDP = (...args) => exec('node', ['scripts/cdp.mjs', ...args]);

async function getPageTitle(tabPrefix) {
  const { stdout } = await CDP('eval', tabPrefix, 'document.title');
  return stdout.trim();
}

async function takeScreenshot(tabPrefix) {
  const { stdout } = await CDP('shot', tabPrefix);
  return stdout.trim(); // 返回文件路径
}

async function navigateAndSnap(tabPrefix, url) {
  await CDP('nav', tabPrefix, url);
  const { stdout } = await CDP('snap', tabPrefix);
  return stdout;
}

// 使用示例
const tabs = (await CDP('list')).stdout;
console.log(tabs);
```

## 配置

| 环境变量       | 目的         |
|----------------|-------------|
| `CDP_PORT_FILE` | 非标准浏览器安装的 `DevToolsActivePort` 文件路径 |

守护进程在 **20 分钟不活动** 后自动退出 — 正常使用无需手动清理。

## 故障排除

### "允许调试" 模态框持续出现
如果守护进程没有持久化，就会发生这种情况。确保您使用相同的 `scripts/cdp.mjs` 入口点 — 它会自动管理守护进程的生命周期。如果您在会话中途切换了工具，请运行 `stop` 并让守护进程重新启动。

### 未检测到浏览器
如果自动检测失败，请找到您的 `DevToolsActivePort` 文件并设置环境变量：

```bash
# macOS Chrome 示例
export CDP_PORT_FILE="$HOME/Library/Application Support/Google/Chrome/Default/DevToolsActivePort"

# Linux Chrome 示例
export CDP_PORT_FILE="$HOME/.config/google-chrome/Default/DevToolsActivePort"
```

### 目标未找到 / 前缀模糊
再次运行 `list` — 当标签页关闭/重新打开时，标签页 ID 会改变。如果多个标签页共享相同的前缀字符，请使用更长的前缀。

### 远程调试切换不可见
确保您在 `chrome://inspect/#remote-debugging`（而不仅仅是 `chrome://inspect/`）。切换按钮位于页面的右上角。

### Node.js 版本错误
此项目需要 **Node.js 22+**。使用 `node --version` 检查版本，并需要通过 [nvm](https://github.com/nvm-sh/nvm) 或您的包管理器升级。

### 屏幕截图为空或尺寸错误
屏幕截图反映了实际渲染的视口。如果标签页在后台窗口中，或者操作系统有显示缩放，`clickxy` 的像素坐标可能需要调整。使用 `snap` 或 `eval` 检查 DOM 状态，而不是完全依赖屏幕截图。

## 架构说明

- 无 Puppeteer，无 Playwright，无中介 — 纯 CDP WebSocket
- 每个标签页一个持久守护进程进程（在首次访问时自动启动）
- 守护进程重用是 100+ 标签页可靠工作的原因（目标枚举没有超时）
- `type` 直接使用 CDP Input 域，绕过 iframe 来源限制
