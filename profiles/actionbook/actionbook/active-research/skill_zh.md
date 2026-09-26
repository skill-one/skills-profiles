# 活跃研究

分析任何主题、领域或论文，并使用 **Actionbook Browser** 生成精美的 HTML 报告——具有 SPA 感知的导航、网络空闲检测、批量操作和智能页面分析功能。

## 增强浏览器功能

| 功能 | 描述 |
|------|-------------|
| 页面加载等待 | `wait-idle` — 监控 fetch/XHR 直到网络稳定 |
| SPA 内容 | `wait-fn` — 等待 JS 条件后再提取 |
| 页面理解 | `snapshot --filter interactive --max-tokens N` — 聚焦、预算友好 |
| 弹窗阻止 | `--auto-dismiss-dialogs` — 自动处理 alert/confirm/prompt |
| 加载速度 | `--block-images` — 跳过图片以加快文本提取速度 |
| 页面稳定性 | `--no-animations` — 冻结 CSS 过渡 |
| 错误检测 | `console --level error` — 检查页面问题 |
| 多步骤表单 | `batch` — 一次性执行多个操作 |
| 元素调试 | `info <selector>` — 检查可见性、位置、属性 |
| 变更跟踪 | `snapshot --diff` — 只看到发生了什么变化 |
| 反检测 | `--stealth` + `fingerprint rotate` 用于受保护网站 |
| 认证管理 | `storage set` — 注入 JWT/tokens 用于受保护内容 |
| 一次性获取 | `browser fetch <url>` — 导航+等待+提取+关闭在一个命令中 |
| 静态页面速度 | `--lite` — HTTP 优先，仅在需要时才回退浏览器 |
| 反爬虫 URL | `--rewrite-urls` — x.com→xcancel.com, reddit→old.reddit |
| 等待调整 | `--wait-hint` — 域名感知等待（快速/正常/慢/重） |
| 日志关联 | `--session-tag` — 为调试标记所有操作 |

## 使用方法

```
/active-research <topic>
/active-research <topic> --output ./reports/my-report.json
```

或者简单地告诉 Claude：“研究 XXX 并生成报告”

### 参数

| 参数 | 是否必需 | 默认值 | 描述 |
|-----------|----------|---------|-------------|
| `topic` | 是 | - | 研究主题（任何文本） |
| `--output` | 否 | `./output/<topic-slug>.json` | JSON 报告的输出路径 |

### 主题检测

| 模式 | 类型 | 策略 |
|------|------|----------|
| `arxiv:XXXX.XXXXX` | 论文 | **arXiv 高级搜索** + ar5iv 深度阅读 |
| `doi:10.XXX/...` | 论文 | 解析 DOI，然后 **arXiv 高级搜索** 查找相关研究 |
| 学术关键词（论文、研究、模型、算法） | 学术主题 | **arXiv 高级搜索** + Google 搜索非学术来源 |
| URL | 特定页面 | 获取并分析页面 |
| 通用文本 | 主题研究 | Google 搜索 + 如果相关则使用 arXiv 高级搜索 |

## 架构

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────┐
│  Claude   │────▶│  Actionbook  │────▶│  Web Pages   │────▶│ Extract  │
│  Code     │     │   Browser    │     │  (multiple)  │     │ Content  │
└──────────┘     └──────────────┘     └──────────────┘     └─────┬────┘
      │           │ wait-idle    │     │ SPA / dynamic │           │
      │           │ batch ops    │     │ protected     │           │
      │           │ --stealth    │     │ mobile-only   │           │
      │           │ snapshot     │     └───────────────┘           │
      │           └──────────────┘                                 │
      │          ┌──────────────┐     ┌──────────────┐            │
      ├─────────▶│  Actionbook  │     │ arXiv Adv.   │            │
      │          │  search/get  │────▶│ Search Form  │───────────▶│
      │          │  (selectors) │     │ (40+ fields) │            │
      │          └──────────────┘     └──────────────┘            │
      │                                                            │
┌──────────┐     ┌──────────────┐     ┌──────────────┐            │
│  Open in │◀────│   json-ui    │◀────│  Write JSON  │◀───────────┘
│  Browser │     │   render     │     │  Report      │  Synthesize
└──────────┘     └──────────────┘     └──────────────┘
```

## 必须使用 Actionbook CLI

**始终使用 `actionbook browser` 命令进行网页浏览。永远不要使用任何其他方法来访问网页：**

- **永远不要**使用 `curl`, `wget`, `httpie` 或任何通过 bash 的 HTTP CLI 工具
- **永远不要**使用 `python -c "import requests"` 或任何通过 bash 的脚本语言 HTTP 库
- **永远不要**使用 WebFetch 或 WebSearch 工具
- **仅**使用 `actionbook browser` 和 `actionbook search`/`actionbook get` 命令

如果您需要网页内容，首选路径是：`actionbook browser fetch <url> --format text --json`（一次性）。
对于交互式多步骤工作流，使用：`actionbook browser open <url>` → `actionbook browser wait-idle` → `actionbook browser text`。

## 浏览器标志 — 研究默认值

**关键：在打开浏览器进行研究时始终使用这些标志。**

```bash
# 首选：一次性获取（I1）— 自动处理打开+等待+提取+关闭
actionbook --block-images --rewrite-urls browser fetch "<url>" --format text --json

# 对于交互式多步骤工作流，使用显式打开：
actionbook --block-images --auto-dismiss-dialogs --no-animations --rewrite-urls browser open "<url>"
```

| 标志 | 原因 |
|------|-----|
| `--block-images` | 跳过图片下载 — 2-5 倍更快地加载页面以进行文本提取 |
| `--auto-dismiss-dialogs` | 防止 alert/confirm/prompt 阻止自动化 |
| `--no-animations` | 冻结 CSS 动画 — 稳定的快照，没有时间问题 |
| `--rewrite-urls` | 重写 x.com→xcancel.com, reddit→old.reddit 以避免反爬虫阻止 |
| `--wait-hint <hint>` | 域名感知等待：`instant`, `fast`, `normal`, `slow`, `heavy` 或 ms |
| `--session-tag <tag>` | 为日志关联和调试标记所有操作 |
| `--lite` (仅获取) | 尝试 HTTP 首选，对于静态页面（Wikipedia、文档、博客）完全跳过浏览器 |

对于具有反爬虫保护的网站，添加 `--stealth`：
```bash
actionbook --block-images --auto-dismiss-dialogs --no-animations --stealth --rewrite-urls browser open "<url>"
```

## 导航模式 — 始终遵循

**选项 A：一次性获取（首选用于只读页面提取）：**

```bash
# 单个命令：导航 → 等待（域名感知）→ 提取 → 关闭
actionbook --block-images --rewrite-urls browser fetch "<url>" --format text --json
# 对于静态页面（Wikipedia、文档、博客），添加 --lite 以完全跳过浏览器：
actionbook --rewrite-urls browser fetch "<url>" --format text --lite --json
# 对于可访问性树：
actionbook --block-images --rewrite-urls browser fetch "<url>" --format snapshot --max-tokens 2000 --json
```

**选项 B：交互式多步骤模式（用于表单、点击、多页面流程）：**

```bash
# 第 1 步：导航
actionbook browser open "<url>"          # 或：goto, click a link

# 第 2 步：等待加载（交互式模式下强制要求）
actionbook browser wait-idle             # 等待 fetch/XHR 结束

# 第 3 步：提取内容
actionbook browser text [selector]       # 提取文本
# 或
actionbook browser snapshot --filter interactive --max-tokens 500  # 理解页面结构
```

**为什么 `wait-idle` 至关重要：**
- SPAs（React、Vue、Next.js）在初始 HTML 之后通过 fetch/XHR 加载内容
- 如果不等待，`text` 返回空或内容不完整
- `wait-idle` 监控所有挂起的网络请求，等待 500ms 后安静

**对于网络空闲后动态加载内容的页面：**
```bash
actionbook browser wait-idle
actionbook browser wait-fn "document.querySelector('.results')"    # 等待特定元素
actionbook browser text ".results"
```

## 完整工作流程

> **提醒：** 本工作流程中的任何网页访问都必须使用 `actionbook browser` 命令。
> 使用 `curl`, `wget`, `python requests` 或任何其他 HTTP 工具是 **严格禁止** 的。
> bash 工具仅用于 `actionbook` CLI 命令和本地文件操作（json-ui render, `open`）。

### 第 1 步：规划搜索策略

根据主题，生成 5-8 个从不同角度的搜索查询：
- 核心定义 / 概述
- 最新发展 / 新闻
- 技术细节 / 实现
- 比较 / 替代方案
- 专家意见 / 分析
- 用例 / 应用

**搜索顺序 — 始终先查询 Actionbook API，然后搜索：**

| 步骤 | 操作 | 原因 |
|------|------|-----|
| **步骤 2（首先）** | **查询 Actionbook API** | 获取 arXiv、ar5iv 和其他已知网站的验证选择器，在进行浏览之前。 |
| **步骤 3（其次）** | **arXiv 高级搜索** | 使用 Actionbook 选择器进行多字段、过滤的学术搜索。 |
| **步骤 4（第三）** | Google / Bing 搜索 | 补充博客、新闻、代码、讨论、非学术来源。 |

### 第 2 步：查询 Actionbook API 以获取选择器（始终先做）

**在进行任何 URL 浏览之前，查询 Actionbook 的索引选择器。**

```bash
# 搜索按域名索引的操作
actionbook search "<keywords>" -d "<domain>"

# 获取特定页面的详细选择器
actionbook get "<domain>:/<path>:<area>"
```

**对研究有用的预索引网站：**

| 网站 | area_id | 关键选择器 |
|------|---------|---------------|
| arXiv 高级搜索 | `arxiv.org:/search/advanced:default` | **40+ 选择器**：字段选择、术语输入、分类复选框、日期范围过滤器 |
| ar5iv 论文 | `ar5iv.labs.arxiv.org:/html/{paper_id}:default` | `h1.ltx_title_document`, `div.ltx_authors`, `div.ltx_abstract`, `section.ltx_section` |
| Google Scholar | `scholar.google.com:/:default` | `#gs_hdr_tsi`（搜索），`#gs_hdr_tsb`（提交） |
| arXiv 主页 | `arxiv.org:/:default` | 跨 2.4M+ 文章的全局搜索 |

**对于您计划访问的任何 URL**，运行 `actionbook search "<keywords>" -d "<domain>"` 以检查是否已索引。

### 第 3 步：arXiv 搜索（URL 优先，表单作为备用）

**经验教训：通过浏览器自动化提交 arXiv 表单不可靠。使用基于 URL 的搜索作为首选方法。**

**选项 A：基于 URL 的搜索（首选 — 最可靠）：**

```bash
# 简单关键词搜索
actionbook --block-images --auto-dismiss-dialogs --no-animations browser open "https://arxiv.org/search/?query=large+language+model+agent&searchtype=all"
actionbook browser wait-idle
actionbook browser text "#main-container"

# 高级 URL 搜索带过滤器
# searchtype: all, title, author, abstract
# start: 结果偏移量 (0, 50, 100, ...)
actionbook browser open "https://arxiv.org/search/?query=Rust+machine+learning&searchtype=all&start=0"
actionbook browser wait-idle
actionbook browser text "#main-container"
```

**搜索策略：从广泛开始，然后缩小：**
1. 第一次搜索：广泛术语（例如，`"Rust" "machine learning"”） — 目标是 50+ 结果
2. 如果结果太少（< 10）：进一步放宽，移除日期/分类过滤器
3. 如果结果太多（> 200）：添加更多具体术语，使用 `searchtype=title`
4. 尝试 2-3 种不同的查询角度（例如，框架名称、用例、基准测试）

**选项 B：通过批量交互表单（备用 — 如果 URL 搜索不足够）：**

```bash
# 打开 arXiv 并使用研究标志
actionbook --block-images --auto-dismiss-dialogs --no-animations browser open "https://ariv.org/search/advanced"
actionbook browser wait-idle

# 使用批量进行表单 — 更少的往返次数，更可靠的
cat <<'EOF' | actionbook browser batch --delay 150
{
  "actions": [
    {"kind": "click", "selector": "#terms-0-field"},
    {"kind": "click", "selector": "option[value='title']"},
    {"kind": "type", "selector": "#terms-0-term", "text": "large language model agent"},
    {"kind": "click", "selector": "#classification-computer_science"},
    {"kind": "click", "selector": "#date-filter_by-3"},
    {"kind": "type", "selector": "#date-from_date", "text": "2025-01-01"},
    {"kind": "type", "selector": "#date-to_date", "text": "2026-02-23"},
    {"kind": "click", "selector": "button:has-text('Search'):nth(2)"}
  ],
  "stopOnError": true
}
EOF
actionbook browser wait-idle
actionbook browser text "#main-container"

# 如果批量表单提交失败（页面显示表单再次出现）：
# → 立即回退到选项 A URL-based 搜索
# → 不要重试表单 — 浪费时间
```

**arXiv 搜索功能（来自索引选择器 — 用于选项 B）：**

| 功能 | 选择器 |
|------|----------|
| 搜索字段（标题/作者/摘要） | `#terms-0-field` select |
| 搜索术语 | `#terms-0-term` input |
| 学术过滤器 | `#classification-computer_science` |
| 过滤器：物理、数学等 | `#classification-physics`, `#classification-mathematics` |
| 日期：过去 12 个月 | `#date-filter_by-1` radio |
| 日期：特定年份 | `#date-filter_by-2` radio + `#date-year` |
| 日期：自定义范围 | `#date-filter_by-3` radio + `#date-from_date` / `#date-to_date` |
| 显示摘要 | `#abstracts-0` radio |

### 第 4 步：补充 Google / Bing 搜索

```bash
# 通过 Google 搜索（带 wait-idle 以获取 SPA 结果）
actionbook browser open "https://www.google.com/search?q=<encoded_query>"
actionbook browser wait-idle
actionbook browser text "#search"

# 或通过 Bing 搜索
actionbook browser open "https://www.bing.com/search?q=<encoded_query>"
actionbook browser wait-idle
actionbook browser text "#b_results"
```

解析搜索结果以提取 URL。对于每个发现的 URL，查询 Actionbook API 以检查是否已索引。

**关键：URL 处理规则（从生产使用中学习）**

1. **永远不要**手动构建从搜索片段的 URL。许多 Google 片段 URL 是截断的或重新格式化的。相反：
   - 使用 `actionbook browser snapshot --filter interactive` 以发现实际的链接元素
   - 直接点击链接：`actionbook browser click "a[href*='domain.com']"`
   - 或从 snapshot refs 提取 href

2. **预期 20-30% 的 URL 会失效。** 在实践中，~5 out of 20 URL 返回 404。处理这种情况：
   ```bash
   actionbook browser open "<url>"
   actionbook browser wait-idle
   # 检查页面是否为 404 或错误页面
   actionbook browser wait-fn "!document.title.includes('404') && !document.title.includes('Not Found')" --timeout 3000
   # 如果超时 → 页面已失效，立即跳过。**不要重试。**
   ```

3. **从 Google 片段中抢救信息。** 如果 URL 失效但 Google 片段中有有用信息：
   - 您已经提取的片段文本是有效的数据
   - 使用它报告中的信息，并注明来源不再可用
   - 在其他网站（archive.org、缓存的版本）搜索相同的内容

4. **使用 4+ 多样化的搜索查询。** 不要依赖单一搜索角度：
   - 查询 1：核心主题概述（例如，"Rust AI 生态系统 2026"）
   - 查询 2：特定框架/工具（例如，"Candle vs Burn Rust ML 框架"）
   - 查询 3：用例/基准测试（例如，"Rust LLM 推理性能基准测试"）
   - 查询 4：最新新闻/发展（例如，"Rust LLM 最新 2026"）
   - 查询 5：社区/生态系统（例如，"Rust AI 代理框架比较"）

### 第 5 步：深度阅读来源

**首选：使用 `browser fetch` 进行一次性页面提取（处理等待 + 提取 + 清理）：**

```bash
# 快速文本提取（最常见）
actionbook --block-images --rewrite-urls browser fetch "<url>" --format text --json

# 静态页面（Wikipedia、文档、博客）— 完全跳过浏览器
actionbook --rewrite-urls browser fetch "<url>" --format text --lite --json

# 页面结构分析
actionbook --block-images --rewrite-urls browser fetch "<url>" --format snapshot --max-tokens 2000 --json

# 带有令牌预算以管理 LLM 上下文
actionbook --block-images --rewrite-urls browser fetch "<url>" --format text --max-tokens 4000 --json
```

**对于交互式工作流（表单、点击），回退到多步骤：**

```bash
actionbook browser open "<url>"
actionbook browser wait-idle
actionbook browser text
actionbook browser text "<selector>"
```

**如果页面内容似乎不完整，则进行调试：**

```bash
# 检查可能阻止渲染的 JS 错误
actionbook browser console --level error

# 检查是否存在特定元素
actionbook browser wait-fn "document.querySelector('.content')" --timeout 5000

# 检查元素属性
actionbook browser info ".content"
```

**对于 arXiv 论文**，尝试按此顺序使用来源：

```bash
# 1. arXiv 摘要（最可靠）— 使用 fetch
actionbook --block-images browser fetch "https://arxiv.org/abs/<arxiv_id>" --format text --json

# 2. HuggingFace 论文页面
actionbook --block-images browser fetch "https://huggingface.co/papers/<arxiv_id>" --format text --json

# 3. ar5iv HTML（结构化，但新论文上会失效）— 使用 --lite 以获取静态 HTML
actionbook browser fetch "https://ar5iv.org/html/<arxiv_id>" --format text --lite --json
# 注意：如果内容太短，ar5iv 没有渲染。回退到其他来源。

# 4. GitHub 仓库（从搜索结果）— 使用 fetch
actionbook --block-images browser fetch "<github_repo_url>" --format text --json
```

**对于受保护网站（Cloudflare、反爬虫检测）— 使用交互模式并使用 stealth：**

```bash
actionbook --stealth --block-images --auto-dismiss-dialogs --rewrite-urls browser open "<protected_url>"
actionbook browser wait-idle
actionbook browser text
```

**对于仅限移动设备的内容：**

```bash
actionbook browser emulate iphone-14
actionbook browser open "<url>"
actionbook browser wait-idle
actionbook browser text
```

**对于 Google Scholar**（由 Actionbook 索引）：

```bash
actionbook browser open "https://scholar.google.com"
actionbook browser wait-idle
actionbook browser click "#gs_hdr_tsi"
actionbook browser type "#gs_hdr_tsi" "<query>"
actionbook browser click "#gs_hdr_tsb"
actionbook browser wait-idle
actionbook browser text "#gs_res"
```

**对于未索引的网站**，使用 snapshot 以发现结构：

```bash
actionbook --block-images browser fetch "<url>" --format snapshot --max-tokens 800 --json
```

### 第 6 步：综合发现

将收集到的信息组织成一个连贯的报告：
1. 概述 / 执行摘要
2. 关键发现
3. 详细分析
4. 支持数据 / 证据
5. 含义 / 重要性
6. 来源

### 第 7 步：生成 json-ui JSON 报告

编写遵循 `@actionbookdev/json-ui` 范式的 JSON 文件。使用写入工具。

**输出路径：** `./output/<topic-slug>.json`（或用户指定的 `--output` 路径）

### 第 8 步：渲染 HTML

**关键：您必须尝试所有回退方法，在失败之前不要停止。**

**重要：始终使用绝对路径 for JSON_FILE 和 HTML_FILE。**

逐一尝试每个方法，直到一个成功：

```bash
# 方法 1：Monorepo 绝对路径（如果 Actionbook 项目内最可靠）
node "$(git rev-parse --show-toplevel)/packages/json-ui/dist/cli.js" render /absolute/path/to/report.json -o /absolute/path/to/report.html

# 方法 2：全局安装（如果用户运行: cd packages/json-ui && npm link）
json-ui render /absolute/path/to/report.json -o /absolute/path/to/report.html

# 方法 3：npx（如果发布到 npm）
npx @actionbookdev/json-ui render /absolute/path/to/report.json -o /absolute/path/to/report.html
```

**永远不要**沉默地失败。如果所有方法都失败，告诉用户：
1. JSON 报告保存在 `<path>`
2. 要启用 HTML 渲染，请运行：`cd <actionbook-repo>/packages/json-ui && npm link`

### 第 9 步：在浏览器中打开

```
# macOS
open <report.html>

# Linux
xdg-open <report.html>
```

### 第 10 步：关闭浏览器

**完成时始终关闭浏览器：**

```bash
actionbook browser close
```

## 错误恢复模式

**使用高级浏览器功能进行智能错误恢复：**

### 模式：页面加载失败

```bash
# 1. 打开页面
actionbook browser open "<url>"
actionbook browser wait-idle --timeout 15000

# 2. 检查 JS 错误
actionbook browser console --level error
# 如果发现错误 → 页面已损坏，跳过到下一个来源

# 3. 检查内容是否渲染
actionbook browser wait-fn "document.body.innerText.length > 100" --timeout 5000
# 如果超时 → 内容没有渲染，尝试回退
```

### 模式：选择器未找到

```bash
# 1. 使用 snapshot 以发现实际的页面结构
actionbook browser snapshot --filter interactive --max-tokens 800

# 2. 或检查特定区域
actionbook browser info "<parent_selector>"
# 返回：建议选择器、可见性、标签信息

# 3. 调整选择器并重试
```

### 模式：反检测

```bash
# 1. 如果初始加载返回 CAPTCHA 或访问被拒绝：
actionbook browser close

# 2. 使用 stealth 重新打开
actionbook --stealth --no-animations --auto-dismiss-dialogs browser open "<url>"
actionbook browser wait-idle

# 3. 如果仍然被阻止，旋转指纹
actionbook browser fingerprint rotate --os windows
actionbook browser open "<url>"
actionbook browser wait-idle
```

### 模式：SPA 内容未加载

```bash
# 1. 等待网络
actionbook browser wait-idle --idle-time 1000 --timeout 15000

# 2. 等待特定元素
actionbook browser wait-fn "document.querySelector('.results')" --timeout 10000

# 3. 如果仍然为空，检查控制台
actionbook browser console --level error

# 4. 尝试点击加载触发器
actionbook browser snapshot --filter interactive --max-tokens 300
# 查找 "Load More", "Show Results", 等.
```

## 完整错误处理参考

| 错误 | 恢复策略 |
|------|-------------------|
| 浏览器无法打开 | `actionbook browser status`, 重试 + 检查 `console --level error` 以诊断 |
| 页面加载超时 | `wait-idle --timeout 15000`, 然后 `console --level error` 进行诊断 |
| **URL 返回 404** | `wait-fn "!document.title.includes('404')"` 以检测快速。**立即跳过**。不要重试。使用 Google 片段文本作为备用数据。 |
| **arXiv 表单提交失败** | 回退到 URL-based 搜索：`arxiv.org/search/?query=...&searchtype=all` |
| ar5iv 内容被截断 | 回退到 arxiv 摘要 + `wait-fn "document.body.innerText.length > 5000"` 以验证 |
| 选择器未找到 | `snapshot --filter interactive` 以发现实际结构 |
| 动态内容缺失 | `wait-idle` + `wait-fn` 等待特定条件出现 |
| 提示阻止 | `--auto-dismiss-dialogs` 完全防止此问题 |
| 反检测 | `--stealth` + `fingerprint rotate` |
| 速度慢的媒体密集型页面 | `--block-images` 或 `--block-media` 以 2-5 倍速度提升页面加载 |
| CSS 动画干扰 | `--no-animations` 冻结所有过渡 |
| json-ui 渲染崩溃 | 检查 MetricsGrid — `suffix`/`value` 必须是纯字符串 |
| `npx json-ui` 404 | 尝试所有 3 种方法（monorepo, global, npx） |
| 没有搜索结果 | 从广泛（50+ 结果）开始，然后缩小。使用 4+ 多种查询角度。 |

**重要提示：** 始终在完成研究后验证您使用了这些功能：

| 功能 | 使用场景 | 检查 |
|------|----------|-------|
| `browser fetch` | 只读页面提取（首选） | 使用 `actionbook browser fetch` 进行大多数页面读取 |
| `--lite` | 静态页面（Wikipedia、文档、博客）— 完全跳过浏览器 | 添加到 `fetch` 以完全跳过浏览器 |
| `--rewrite-urls` | 始终（避免 x.com、reddit 上的反爬虫阻止） | 在打开浏览器进行研究时始终使用 |
| `--wait-hint` | 域名感知等待调整（快速/正常/慢/重） | 使用 `fetch` 或手动流程 |
| `--session-tag` | 多步骤操作需要日志关联 | 为调试标记所有操作 |
| `wait-idle` | 在每次 `open`/`goto`/`click` 触发导航后 | 必须在每次页面 |
| `--block-images` | 始终（研究不需要图片） | 在打开浏览器时始终使用 |
| `--auto-dismiss-dialogs` | 始终（防止 alert/confirm/prompt 阻止自动化） | 在打开浏览器时始终使用 |
| `--no-animations` | 始终（稳定的快照） | 在打开浏览器时始终使用 |
| `wait-fn` | 当内容在网络空闲后异步加载时 | 使用 SPA、动态页面 |
| `console --level error` | 当页面内容似乎不完整或损坏时 | 用于调试 |
| `batch` | 当填写多步骤表单（arXiv、Google Scholar）时 | 替代 5+ 顺序命令 |
| `snapshot --filter interactive` | 当发现未索引的网站时 | 使用 snapshot 以发现页面结构 |
| `info <selector>` | 当点击/类型不起作用时 | 调试元素可见性 |
| `change tracking` | `snapshot --diff` | 只看到发生了什么变化 |
| `anti-detection` | `--stealth` + `fingerprint rotate` 用于受保护的网站 | |
| `auth management` | `storage set` — 注入 JWT/tokens 用于受保护内容 | |
| `one-shot fetch` | `browser fetch <url>` — 导航+等待+提取+关闭在一个命令中 | |
| `static page speed` | `--lite` — HTTP 优先，仅在需要时才回退浏览器 | |
| `anti-scrape URLs` | `--rewrite-urls` — x.com→xcancel.com, reddit→old.reddit | |
| `wait tuning` | `--wait-hint` — 域名感知等待（快速/正常/慢/重） | 使用 `fetch` 或手动流程 |
| `log correlation` | `--session-tag` — 为调试标记所有操作 | |

## 学术论文支持

### arXiv 论文

**ar5iv.org HTML**（首选用于阅读，但新论文 3 个月内通常不完整）：

| 元素 | 选择器 | 可靠性 | 备用 |
|------|----------|-------------|----------|
| 标题 | `h1.ltx_title_document` | 高 | — |
| 作者 | `div.ltx_authors` | 高 | — |
| 摘要 | `div.ltx_abstract` | 高 | — |
| 完整文章 | `article` | 中等 | — |
| 章节 | `section.ltx_section` | **低** | `article` |
| 图像 | `figure.ltx_figure` | 中等 | — |
| 表格 | `table.ltx_tabular` | 中等 | — |

**推荐方法：** 尝试 `wait-idle` + `wait-fn` 以验证 ar5iv 内容是否加载：

```bash
actionbook browser open "https://ar5iv.org/html/<arxiv_id>" --format text --json
actionbook browser wait-idle --timeout 15000
actionbook browser wait-fn "document.body.innerText.length > 5000" --timeout 10000
# 如果 wait-fn 超时 → ar5iv 没有渲染。回退到其他来源。
```

### 推荐来源优先级

| 优先级 | 来源 | 您获得的内容 | 可靠性 |
|------|------|-------------|-------------|
| 1 | `arxiv.org/abs/<id>` | 摘要、元数据、提交历史 | 非常高 |
| 2 | `huggingface.co/papers/<id>` | 摘要、社区、相关模型 | 非常高 |
| 3 | GitHub 仓库 | README、代码、模型库 | 高 |
| 4 | HuggingFace 模型卡 | 训练配方、基准测试 | 高 |
| 5 | `ar5iv.org/html/<id>` | 静态 HTML | 中等 |
| 6 | Google Scholar | 引用、相关研究 | 中等 |

### 其他学术来源

- Google Scholar (`scholar.google.com`) — Actionbook 索引
- Semantic Scholar (`semanticscholar.org`)
- Papers With Code (`paperswithcode.com`)
- 会议论文网站

## 质量指南

1. **广度**：从至少 3-5 个不同来源进行研究
2. **深度**：阅读完整文章，而不仅仅是片段
3. **准确性**：跨来源交叉引用事实
4. **结构**：为每种内容类型使用适当的 json-ui 组件
5. **归属**：始终在报告中包含来源链接
6. **新鲜度**：当相关性相同时，优先选择最近的来源
