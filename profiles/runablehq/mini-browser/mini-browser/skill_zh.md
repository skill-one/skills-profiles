# mini-browser (mb) — Agent的浏览器CLI

`mb`是一个浏览器CLI，其中每个命令都是一个小的Unix工具。它通过puppeteer-core与Chrome（端口9222）通过CDP进行通信。

## 安装（如果尚未安装）

只有在`mb`未安装或Chrome无法访问时才需要安装。
首先运行这些检查——如果两者都通过，则直接跳转到命令参考。

### 检查是否就绪

```bash
# 1. mb是否已安装？
which mb && echo "mb: ok" || echo "mb: MISSING"

# 2. Chrome是否在CDP上监听？
curl -sf http://127.0.0.1:9222/json/version > /dev/null && echo "chrome: ok" || echo "chrome: NOT RUNNING"
```

如果**两者**都打印"ok"，则一切就绪——直接使用`mb`命令。

### 安装（仅当`mb`缺失时）

```bash
npm install -g @runablehq/mini-browser
```

### 启动Chrome（仅当未运行时）

```bash
mb-start-chrome
```

这会以`--remote-debugging-port=9222`、新配置文件和1024×768窗口启动Chrome。如果Chrome已经运行，则此操作无效。

要终止并重新启动：

```bash
mb-restart-chrome
```

### 验证

```bash
mb go "https://example.com" && mb text
```

### 环境变量

| 变量 | 默认值 | 描述 |
|---|---|---|
| `CHROME_PORT` | `9222` | CDP端口 |
| `CHROME_BIN` | 自动检测 | Chrome/Chromium二进制文件路径 |
| `CHROME_PID_FILE` | `<scripts>/.chrome-pid` | PID文件位置 |
| `CHROME_USER_DATA_DIR` | `<scripts>/.chrome-profile` | Chrome配置文件目录 |

## 命令参考

### 导航

| 命令 | 描述 |
|---|---|
| `mb go <url>` | 导航到URL（等待networkidle） |
| `mb url` | 打印当前URL |
| `mb back` | 返回 |
| `mb forward` | 前进 |

### 观察

| 命令 | 描述 |
|---|---|
| `mb text [selector]` | 可见文本内容（默认：body） |
| `mb shot [file]` | 截图到PNG（默认：./shot.png） |
| `mb snap` | 列出带坐标的交互元素 |

### 交互

| 命令 | 描述 |
|---|---|
| `mb click <x> <y>` | 在坐标处点击 |
| `mb type [x y] <text>` | 输入文本（带坐标：选择第一个） |
| `mb fill <k=v...>` | 通过标签/名称/占位符填充表单字段 |
| `mb key <key...>` | 按键（Enter、Tab、Meta+a） |
| `mb move <x> <y>` | 在坐标处悬停 |
| `mb drag <x1> <y1> <x2> <y2>` | 在点之间拖动 |
| `mb scroll [dir] [px]` | 滚动（默认：向下500） |

### 录制

| 命令 | 描述 |
|---|---|
| `mb record start <file>` | 开始录制（.webm、.mp4、.gif） |
| `mb record stop` | 停止录制并保存 |
| `mb record status` | 检查是否正在录制 |

### 标签页

| 命令 | 描述 |
|---|---|
| `mb tab list` | 列出打开的标签页 |
| `mb tab new [url]` | 打开新标签页，打印索引 |
| `mb tab close [n]` | 关闭标签页（默认：最后一个） |

### 其他

| 命令 | 描述 |
|---|---|
| `mb js <code>` | 在页面上下文中运行JavaScript |
| `mb wait <target>` | 等待ms / 选择器 / networkidle / url:pattern |
| `mb audit` | 设计审核（调色板、排版、对比度、a11y、SEO） |
| `mb logs` | 流式传输控制台日志（Ctrl+C停止） |

### 标志

| 标志 | 默认值 | 描述 |
|---|---|---|
| `--timeout <ms>` | 30000 | 命令超时 |
| `--tab <n>` | 0 | 目标标签页索引 |
| `--json` | false | 结构化JSON输出 |
| `--right` | false | 右键点击 |
| `--double` | false | 双击 |
| `--fps <n>` | 30 | 录制帧率 |
| `--scale <n>` | 1 | 录制缩放因子 |

## 使用模式

### 观察→操作循环

标准代理循环：快照页面，选择元素，对其进行操作。

```bash
mb snap                          # 列出带(x, y)的交互元素
mb click 512 380                 # 在这些坐标处点击按钮
mb wait networkidle              # 等待页面稳定
mb snap                          # 再次观察
```

### 填写并提交表单

```bash
mb go "https://example.com/login"
mb fill "Email=user@example.com" "Password=hunter2"
mb key Enter
mb wait url:/dashboard
```

### 拍摄截图

```bash
mb shot page.png
mb shot page.png --width 1440 --height 900
```

### 提取文本

```bash
mb text "main"                   # 从<main>获取文本
mb text "#content"               # 从#content获取文本
mb text                          # 完整body文本
```

### 运行JavaScript

```bash
mb js 'document.title'
echo 'document.querySelectorAll("a").length' | mb js -
```

### 录制屏幕录制

```bash
mb record start demo.mp4 --fps 30 --scale 1
# ... 与页面交互 ...
mb record stop
```

### 设计审核

```bash
mb audit                         # 人类可读报告
mb audit --json                  # 结构化JSON输出
```

### 关闭覆盖层

Cookie横幅和模态框会阻挡点击。使用JS将其移除：

```bash
mb js 'document.querySelector("[class*=cookie]")?.remove()'
```

### 等待策略

```bash
mb wait 2000                     # 睡眠2秒
mb wait ".modal"                 # 等待选择器出现
mb wait networkidle              # 等待无网络活动
mb wait url:/dashboard           # 等待URL包含字符串
```

## 重要提示

- **视口是1024×768。** `snap`仅返回当前视口中的元素——滚动并再次快照以找到更多。
- **`text`使用querySelector**——仅返回第一个匹配项。使用`text "main"`优于`text "p"`以获得更好的结果。
- **`go`等待networkidle。** 对于重型SPAs，随后使用`wait ".selector"`。
- **带坐标的`type`会三击**以选择现有文本，然后输入替换内容。
- **`fill`字段匹配顺序：** aria-label → placeholder → name属性 → id → 标签文本 → CSS选择器（使用`#`/`.`/`[`前缀）。
- **`--json`输出：** `snap` → `[{role, name, x, y, state}]`，`tab list` → `[{index, url, title}]`，`logs` → JSON行，`audit` → 完整审核对象。
- **录制状态**存储在`~/.mb-recorder.json`中。一次只能有一个录制。
- **`tab close`**无法关闭最后一个剩余的标签页。

## 故障排除

| 问题 | 解决方法 |
|---|---|
| "Chrome未找到" | 设置`CHROME_BIN=/path/to/chrome` |
| 连接被拒绝 | 首先运行`mb-start-chrome` |
| 过时的录制状态 | 删除`~/.mb-recorder.json` |
| Chrome窗口大小不正确 | `mb-restart-chrome`（创建新配置文件） |
| 快照输出中元素不存在 | `mb scroll down 500`然后`mb snap`再次 |
