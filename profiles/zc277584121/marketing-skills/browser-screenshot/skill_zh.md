# 技能：浏览器截图

对网页上的特定区域进行聚焦截图——例如 Reddit 帖子、推文、文章部分、图表等——而不仅仅是全页面的截图。

> **前提条件**：必须安装 `agent-browser`。此技能使用其自己的带窗口 Chrome，并具有专用的持久化配置文件；用户日常使用的 Chrome 不需要远程调试。

## 专用浏览器配置文件

使用与 `my-chrome-automation` 相同的专用持久化配置文件约定：

```bash
PROFILE_DIR="${AGENT_BROWSER_PROFILE:-$HOME/.agent-browser-chrome}"
NAMESPACE="${NAMESPACE:-browser-screenshot}"
SESSION="${SESSION:-focused-capture}"

ab() {
  agent-browser --namespace "$NAMESPACE" --session "$SESSION" --headed --profile "$PROFILE_DIR" "$@"
}
```

通过 `ab` 运行每个浏览器命令。不要使用 `--auto-connect`、通用 CDP 发现或用户的日常 Chrome 配置文件。专用配置文件可以在任务之间保留 cookie 和登录状态，同时允许用户的正常 Chrome 保持打开且未受影响。

在实用的情况下，为任务选择一个描述性的 `SESSION`。不要同时针对同一配置文件运行多个任务；按顺序重用它以避免配置文件锁定冲突。

如果目标网站需要登录，请使用 `ab` 打开它，在专用的带窗口窗口中暂停，让用户完成登录或验证，然后使用相同的配置文件和会话继续。

### 如果专用配置文件已经在运行

使用相同配置文件启动第二个 Chrome 可能会在创建 DevTools 端点之前退出。永远不要回退到任意打开的 Chrome。要么重用此配置文件的可知 Agent 浏览器会话，要么显式仅附加到命令行包含确切的 `--user-data-dir=$PROFILE_DIR` 值的 Chrome 进程。

在 macOS 上，像这样识别专用进程及其本地 CDP 端口：

```bash
PROFILE_PID="$(ps -axo pid=,command= | awk -v profile="--user-data-dir=$PROFILE_DIR" 'index($0, profile) && index($0, "--remote-debugging-port=") && $0 !~ /Helper/ {print $1; exit}')"
CDP_PORT="$(lsof -nP -a -p "$PROFILE_PID" -iTCP -sTCP:LISTEN | awk 'NR > 1 && $9 ~ /^127\.0\.0\.1:[0-9]+$/ {split($9, parts, ":"); print parts[2]; exit}')"

ab() {
  agent-browser --namespace "$NAMESPACE" --session "$SESSION" --cdp "$CDP_PORT" "$@"
}
```

在附加之前要求非空、无歧义的 `PROFILE_PID` 和 `CDP_PORT` 值。如果它们无法验证，请要求用户关闭专用自动化窗口并重试。不要关闭此任务仅附加到的浏览器。

---

## 概述

此技能处理完整的工作流程：

1. **研究** 要截图的最佳页面（网络搜索、获取）
2. **导航** 到浏览器中的正确页面
3. **定位** 页面上的目标元素/区域
4. **捕获** 仅该区域的聚焦、裁剪截图

### 硬性规则：不允许全屏截图

**绝对不要将未裁剪的全视口或全页面截图作为最终结果输出。** 全屏截图包含过多的噪声（导航栏、侧边栏、广告、无关内容），不适合作为文章插图。每个截图必须裁剪到聚焦区域。

---

## 第 0 步：研究——在打开浏览器之前查找和验证来源

**浏览器用于捕获，而不是浏览。** 在在 Chrome 中打开任何内容之前，使用基于文本的工具（WebSearch、WebFetch）查找候选页面，阅读其内容，并决定哪些页面实际上值得截图。

### 先研究工作流

1. **WebSearch** 以找到主题的候选页面
2. **WebFetch** 每个候选页面以读取其文本内容——检查它是否包含您需要的信息/视觉
3. **评估**：这个页面值得截图吗？它是否有一个清晰、聚焦的区域可以作为插图？
4. **然后** 才打开浏览器以捕获截图

这可以节省大量时间——大多数候选页面不值得截图，并且您可以在浏览器导航的开销之前排除它们。

### 何时使用先浏览器后

跳过 WebSearch/WebFetch 阶段并直接使用 Chrome 浏览，当：

- **目标平台需要登录**——Reddit、LinkedIn、X/Twitter 和其他社交平台通常将内容置于登录墙之后。直接使用专用配置文件，以便其保存的登录状态可以被重用。
- **用户指定了一个具有明确搜索需求的平台**——例如，“查找关于 X 的 Reddit 帖子”或“截图关于 Y 的推文”。直接在 Chrome 中进入平台的搜索页面。
- **WebFetch 返回被阻止/不完整的内容**——一些网站会积极阻止非浏览器请求。如果您收到 403、验证码页面或剥离的内容，请切换到 Chrome。

在这些情况下，Chrome 浏览取代了 WebSearch——导航到平台的搜索页面，浏览结果，并在决定要截图之前 visually 评估页面。

### 页面选择策略

正确的页面取决于文章的上下文以及主题是最新还是值得注意：

| 主题类型 | 最佳查找页面 | 如何查找 |
|--------------|-------------------|----------------|
| **新模型/功能发布**（< 6 个月） | 官方博客帖子宣布它 | WebSearch `"<model name>" site:<vendor-domain> blog` |
| **成熟产品**（> 6 个月） | 产品着陆页或文档概述 | WebSearch `"<model name>" 官方页面` |
| **开源模型** | HuggingFace 模型卡或 GitHub 仓库 | 直接 URL：`huggingface.co/<org>/<model>` |
| **API 服务** | API 文档页面 | WebSearch `"<service name>" API docs` |

> **注意**：此表格列出了常见的主题类型，但**不是详尽的**。将相同的先研究策略应用于任何主题类型——为当前主题找到最权威和视觉干净的源页面。

### 好截图来源的标准

**核心原则：少即是多。关注内容，而不是 Chrome。**

一个好的截图来源包含一个**聚焦、自包含的信息片段**——一段文本、一个关键引言、一个数据表、一个图表。它**不应该是**一个充满按钮、导航、侧边栏和交互元素的繁忙页面。

- **优先选择**：带有清晰标题和 1-2 段文本的博客帖子部分。一个图表或图表。带有名称和描述的模型卡标题。一个引言或关键发现。
- **避免**：带有 CTA 和导航的全着陆页。带有多个面板的仪表板视图。由 UI 控件（按钮、下拉列表、表单）而不是可读内容主导的页面。
- **官方博客帖子** 是理想的：它们有英雄图像、显眼的标题和为分享而设计的简洁描述
- **产品着陆页** 可以使用，但仅当您裁剪到英雄部分——忽略其余部分
- **HuggingFace 模型卡** 对于开源模型是可靠的：一致的布局，模型名称 + 描述始终在顶部
- **API 文档** 是可接受的回退：显示产品名称和关键规格

> **经验法则**：如果您计划捕获的区域包含比可读文本内容更多的交互式 UI 元素（按钮、链接、导航项），则它是一个糟糕的裁剪。找到一个更内容丰富的区域，或者完全选择一个不同的页面。

### 飞行前 URL 验证

在浏览器中打开之前，使用 WebFetch（轻量级 HEAD/GET）验证 URL，以避免浪费时间在 404 上或重定向：

```
WebFetch: <candidate-url>
→ 检查状态代码、标题和内容片段
→ 如果 404 或重定向到无关页面，则尝试下一个候选
```

### 区域选择策略

思考一下**文章读者需要在这个截图看到什么**：

| 文章上下文 | 捕获什么 | 目标区域 |
|-----------------|----------------|---------------|
| 介绍一个模型在系列中 | 模型名称 + 关键标语/描述 | 博客英雄部分或 HF 模型卡标题 |
| 比较功能 | 功能亮点或规格表 | 显示规格/功能的博客部分 |
| 讨论特定功能 | 功能描述 | 相关部分标题 + 1-2 段文本 |
| 显示产品/服务 | 品牌标识 + 价值主张 | 着陆页英雄（标题 + 副标题 + 视觉） |

截图应该让读者想到“啊，这就是这个模型/产品的样子”——而不是“我在看什么？”

---

## 第 1 步：导航到目标页面

### 总是先列出选项卡

```bash
ab tab list
```

检查页面是否已经在专用会话中打开。当它们具有正确的登录和页面状态时，重用其现有选项卡。

### 通过输入类型导航

| 用户提供 | 策略 |
|---------------|----------|
| 直接 URL | `ab open <url>` |
| 搜索查询 | `ab open https://www.google.com/search?q=<encoded-query>` → 找到并点击最佳结果 |
| 平台 + 主题 | 构建平台搜索 URL（见下文）→ 定位目标内容 |
| 模糊描述 | Google 搜索 → 评估结果 → 导航到最佳匹配 |

### 平台特定搜索 URL

| 平台 | 搜索 URL 模式 |
|----------|-------------------|
| Reddit | `https://www.reddit.com/search/?q=<query>` |
| X / Twitter | `https://x.com/search?q=<query>` |
| LinkedIn | `https://www.linkedin.com/search/results/content/?keywords=<query>` |
| Hacker News | `https://hn.algolia.com/?q=<query>` |
| GitHub | `https://github.com/search?q=<query>` |
| YouTube | `https://www.youtube.com/results?search_query=<query>` |

### 等待页面加载

导航后，等待内容稳定：

```bash
ab wait --load networkidle
```

> **注意**：某些网站（Reddit、X、LinkedIn）永远不会达到 `networkidle`。如果 `open` 已经在其输出中显示页面标题，请跳过等待。使用 `wait 2000` 作为安全的替代方案。

---

## 第 2 步：定位目标区域

这是关键步骤。目标是找到一个**CSS 选择器**，它精确地包装要捕获的内容。

### 主要方法：DOM 选择器发现

1. **拍摄一个带注释的截图**以了解页面布局：
   ```bash
   ab screenshot --annotate
   ```

2. **拍摄一个快照**以查看页面的可访问性树：
   ```bash
   ab snapshot -i
   ```

3. **识别目标容器元素**。查找：
   - 语义 HTML 容器：`<article>`、`<main>`、`<section>`
   - 平台特定组件（见 [平台选择器](#platform-selectors)）
   - 数据属性：`[data-testid="..."]`、`[data-id="..."]`

4. **使用 `get box` 验证**以确认元素具有合理的边界框：
   ```bash
   ab get box "<selector>"
   ```
   这返回 `{ x, y, width, height }`。进行合理性检查：
   - 宽度应 > 100px 且 < 视口宽度
   - 高度应 > 50px
   - 如果边界框是整个页面，则选择器太宽泛——请细化它

5. **如果选择器难以找到**，使用 `eval` 探索 DOM：
   ```bash
   ab eval "document.querySelector('article')?.getBoundingClientRect()"
   ```

### 平台选择器

流行平台的常见容器选择器：

| 平台 | 目标 | 典型选择器 |
|----------|--------|-----------------|
| Reddit | 一个帖子 | `shreddit-post`、`[data-testid="post-container"]` |
| X / Twitter | 一个推文 | `article[data-testid="tweet"]` |
| LinkedIn | 一个信息流帖子 | `.feed-shared-update-v2` |
| Hacker News | 一个故事 + 评论 | `#hnmain .fatitem` |
| GitHub | 一个仓库卡片 | `[data-hpc]`、`.repository-content` |
| YouTube | 视频播放器区域 | `#player-container-outer` |
| 通用文章 | 主要内容 | `article`、`main`、`[role="main"]`、`.post-content`、`.article-body` |

> 这些选择器可能会随时间变化。在使用之前始终使用 `get box` 验证。

### 多个匹配元素

如果选择器匹配多个元素（例如，时间线上的多个推文），请缩小范围：

```bash
# 计数匹配
ab get count "article[data-testid='tweet']"

# 使用 nth-child 或 :first-of-type，或更具体的选择器
# 或者使用 eval 通过文本内容找到正确的：
ab eval --stdin <<'EOF'
const posts = document.querySelectorAll('article[data-testid="tweet"]');
for (let i = 0; i < posts.length; i++) {
  const text = posts[i].textContent.substring(0, 80);
  console.log(i, text);
}
EOF
```

然后使用 `:nth-of-type(N)` 或唯一的父选择器定位特定的一个。

---

## 第 3 步：捕获聚焦截图

### 方法 A：滚动 + 视口截图（首选用于视口尺寸目标）

当目标元素适合在视口内时最佳。

```bash
# 将目标滚动到视口内
ab scrollintoview "<selector>"
ab wait 500

# 拍摄视口截图
ab screenshot /tmp/browser-screenshot-raw.png
```

然后使用边界框（见 [裁剪](#cropping)）进行裁剪。

### 方法 B：全页面截图 + 裁剪（适用于任何尺寸目标）

当目标可能大于视口或需要精确裁剪时最佳。

```bash
# 拍摄全页面截图
ab screenshot --full /tmp/browser-screenshot-full.png

# 获取目标元素的边界框
ab get box "<selector>"
# 输出：{ x: 200, y: 450, width: 680, height: 520 }
```

然后进行裁剪（见 [裁剪](#cropping)）。

### 裁剪

使用 ImageMagick（`magick` 在 IMv7 上，`convert` 已弃用）将截图裁剪为目标区域。添加填充以获得视觉呼吸空间。

#### 高分辨率显示处理

**关键**：在 macOS 高分辨率显示上，截图以 2x 分辨率捕获。一个 1728x940 视口产生一个 3456x1880 图像。您**必须**考虑这一点：

1. **检测缩放因子**：比较视口大小与实际图像尺寸：
   ```bash
   # 检查实际图像尺寸
   magick identify /tmp/screenshot.png
   # → 3456x1880 表示在 1728x940 视口上的 2x 缩放
   ```

2. **在裁剪之前将 `get box` 坐标乘以缩放因子**：
   ```bash
   # get box 返回视口坐标：{ x: 200, y: 450, width: 680, height: 520 }
   # 对于 2x Retina，实际图像坐标是：
   SCALE=2
   X=$((200 * SCALE))
   Y=$((450 * SCALE))
   W=$((680 * SCALE))
   H=$((520 * SCALE))
   PADDING=$((16 * SCALE))
   ```

#### 裁剪命令

```bash
magick /tmp/browser-screenshot-full.png \
  -crop $((W + PADDING*2))x$((H + PADDING*2))+$((X - PADDING))+$((Y - PADDING)) \
  +repage \
  <output-path>.png
```

> **重要**：`get box` 返回浮点值。将它们舍入为整数后再传递给 ImageMagick。

> **填充**：使用 12–20px（视口 px）。如果目标具有明确的视觉边界（卡片、带边框的框），请增加到约 30px。如果用户想要紧密裁剪，则使用 0。

### 输出路径

- 如果用户指定了输出路径，则使用该路径
- 否则，将保存到当前目录中的描述性名称，例如 `reddit-post-screenshot.png`、`tweet-screenshot.png`

---

## 第 4 步：验证结果

裁剪后，**阅读输出图像**以验证它是否捕获了正确的内容：

```bash
# 使用 Read 工具 visually 检查裁剪后的截图
```

如果裁剪不正确（遗漏内容、过多的空白、错误的元素），请调整选择器或边界框并重试。

---

## 回退：视觉高亮确认

当基于 DOM 的定位不确定——选择器可能错误、存在多个候选者或目标不明确时——使用**注入的 JS 高亮**在裁剪之前 visually 确认。

### 工作原理

1. **在候选元素上注入高亮边框**：
   ```bash
   ab eval --stdin <<'EOF'
   (function() {
     const el = document.querySelector('<selector>');
     if (!el) { console.log('NOT_FOUND'); return; }
     el.style.outline = '4px solid red';
     el.style.outlineOffset = '2px';
     el.scrollIntoView({ block: 'center' });
   })();
   EOF
   ```

2. **拍摄截图** 并 visually 检查：
   ```bash
   ab screenshot /tmp/highlight-check.png
   ```
   阅读截图以检查红色边框是否包围了正确的內容。

3. **如果正确**，移除高亮并继续裁剪：
   ```bash
   ab eval "document.querySelector('<selector>').style.outline = ''; document.querySelector('<selector>').style.outlineOffset = '';"
   ```

4. **如果错误**，尝试下一个候选者或细化选择器，重新高亮，并重新检查。

### 何时使用此回退

- 页面具有复杂的/嵌套组件，您不确定哪个容器是正确的
- 存在多个相似元素，您需要选择正确的元素
- 用户的描述模糊（“页面中间的那个图表”）
- `get box` 结果看起来可疑（太大、太小、零大小）

---

## 页面准备：在捕获之前清理

在拍摄最终截图之前，清理页面以获得更好的结果：

```bash
# 关闭 cookie 横幅、弹窗、覆盖层
ab eval --stdin <<'EOF'
(function() {
  // 常见的 cookie/弹窗选择器
  const selectors = [
    '[class*="cookie"] button',
    '[class*="consent"] button',
    '[class*="banner"] [class*="close"]',
    '[class*="modal"] [class*="close"]',
    '[class*="popup"] [class*="close"]',
    '[aria-label="Close"]',
    '[data-testid="close"]'
  ];
  selectors.forEach(sel => {
    document.querySelectorAll(sel).forEach(el => {
      if (el.offsetParent !== null) el.click();
    });
  });

  // 隐藏固定/粘性元素，这些元素覆盖内容（导航栏、横幅）
  document.querySelectorAll('*').forEach(el => {
    const style = getComputedStyle(el);
    if ((style.position === 'fixed' || style.position === 'sticky') && el.tagName !== 'HTML' && el.tagName !== 'BODY') {
      el.style.display = 'none';
    }
  });
})();
EOF
```

> **谨慎使用**：隐藏固定元素可能会移除重要上下文。仅在覆盖层明显遮挡目标区域时运行此操作。

### 不会关闭的 Cookie 横幅

一些 Cookie 同意横幅（例如 Jina AI 的 Usercentrics）生活在阴影 DOM 或 iframe 中，无法通过 JS `click()` 或 `remove()` 关闭。不要浪费时间在多次 JS 尝试上。相反：

1. **裁剪它**——如果横幅在顶部或底部，只需调整裁剪区域以排除它。这是最快且最可靠的方法。
2. **滚动过去它**——在捕获之前将目标内容滚动到横幅区域之外。

---

## 视口大小

为了获得一致、高质量的截图，在捕获之前设置视口：

```bash
# 标准桌面视口
ab set viewport 1280 800

# 宽一些，用于仪表板/数据密集型页面
ab set viewport 1440 900

# 窄一些，用于类似移动的内容（社交媒体帖子）
ab set viewport 800 600
```

选择一个视口宽度，使目标内容清晰渲染——不要太拥挤，也不要太拉伸。

---

## 故障排除

### `get box` 返回 null 或零大小
- 选择器没有匹配任何元素。使用 `get count "<selector>"` 进行验证。
- 元素可能被隐藏或尚未渲染。尝试 `wait 2000` 并重试。

### 裁剪图像为空或区域错误
- 全页面截图坐标可能与视口坐标不同。使用 `screenshot --full` 与 `get box`（它们使用相同的坐标系统）。
- 检查页面是否有水平滚动——`get box` x 值可能偏移。

### 目标元素在 iframe 内
- `get box` 和 `snapshot -i` 无法看到 iframe 内的内容。
- 使用 `eval` 访问 iframe 内容：
  ```bash
  ab eval "document.querySelector('iframe').contentDocument.querySelector('<sel>').getBoundingClientRect()"
  ```
  注意：仅适用于同源 iframe。

### `open` 成功但页面内容错误
- 浏览器可能会切换到不同的选项卡（例如，弹窗或重定向打开了一个新选项卡）。始终在导航后验证：
  ```bash
  ab eval "document.location.href"
  ```
- 如果 URL 错误，使用 `tab list` 找到正确的选项卡并 `tab goto <N>` 切换。

### 截图命令在字体上超时
- 某些页面（例如 Google 开发者文档）在 `document.fonts.ready` 上挂起。首先强制解决它：
  ```bash
  ab eval "document.fonts.ready.then(() => 'ok')"
  ```
  然后重试截图。

### 页面有惰性加载内容
- 向下滚动以触发加载，然后再拍摄截图：
  ```bash
  ab scroll down 1000
  ab wait 1500
  ab scroll up 1000
  ```
