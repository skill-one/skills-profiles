# Chrome CDP

轻量级 Chrome DevTools 协议命令行工具。通过 WebSocket 直接连接——无需 Puppeteer，支持 100+ 标签页，即时连接。

## 前置条件

- 带启用了远程调试的 Chrome（或 Chromium、Brave、Edge、Vivaldi）：打开 `chrome://inspect/#remote-debugging` 并切换开关
- Node.js 22+（使用内置 WebSocket）
- 如果你的浏览器的 `DevToolsActivePort` 位于非标准位置，设置 `CDP_PORT_FILE` 为其完整路径

## 命令

所有命令使用 `scripts/cdp.mjs`。`<target>` 是 `list` 中提供的**唯一**的 targetId 前缀（例如 `6BE827FA`）。CLI 会拒绝模糊的前缀。

### 列出打开的页面

```bash
scripts/cdp.mjs list
```

### 截图

```bash
scripts/cdp.mjs shot <target> [file]    # 默认：runtime 目录下的 screenshot-<target>.png
```

仅捕获**视口**。如果需要获取折叠内容下的内容，先用 `eval` 滚动。输出包含页面的 DPR 和坐标转换提示（见下文**坐标**）。

### 可访问性树快照

```bash
scripts/cdp.mjs snap <target>
```

### 执行 JavaScript

```bash
scripts/cdp.mjs eval <target> <expr>
```

> **注意**：避免在 DOM 在多次 `eval` 调用间发生变化时使用基于索引的选择（`querySelectorAll(...)[i]`）（例如点击 Ignore 后，卡片索引会变化）。将所有数据集中在一个 `eval` 中，或使用稳定的选择器。

### 其他命令

```bash
scripts/cdp.mjs html    <target> [selector]   # 全页或元素 HTML
scripts/cdp.mjs nav     <target> <url>         # 导航并等待加载
scripts/cdp.mjs net     <target>               # 资源时间线条目
scripts/cdp.mjs click   <target> <selector>    # 通过 CSS 选择器点击元素
scripts/cdp.mjs clickxy <target> <x> <y>       # 在 CSS 像素坐标处点击
scripts/cdp.mjs type    <target> <text>         # Input.insertText 在当前焦点处输入；与 `eval` 不同，在跨域 iframe 中有效
scripts/cdp.mjs loadall <target> <selector> [ms]  # 点击 "加载更多" 直到消失（默认点击间隔 1500ms）
scripts/cdp.mjs evalraw <target> <method> [json]  # 原始 CDP 命令透传
scripts/cdp.mjs open    [url]                  # 打开新标签页（每个都会触发 Allow 提示）
scripts/cdp.mjs stop    [target]               # 停止守护进程
```

## 坐标

`shot` 以原生分辨率保存图像：图像像素 = CSS 像素 × DPR。CDP Input 事件（`clickxy` 等）使用**CSS 像素**。

```
CSS px = 截图图像 px / DPR
```

`shot` 会打印当前页面的 DPR。典型 Retina（DPR=2）：将截图坐标除以 2。

## 小贴士

- 优先使用 `snap --compact` 而不是 `html` 获取页面结构。
- 使用 `type`（而非 `eval`）在跨域 iframe 中输入文本——先用 `click`/`clickxy` 聚焦，然后 `type`。
- Chrome 在首次访问每个标签页时会显示 "Allow debugging" 模态框。后台守护进程保持会话活跃，因此后续命令无需再次授权。守护进程在 20 分钟无活动后自动退出。
