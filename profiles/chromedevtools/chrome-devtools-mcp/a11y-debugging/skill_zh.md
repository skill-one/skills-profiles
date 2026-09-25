## 核心概念

**页面目标定位**：页面范围的工具（`take_snapshot`、`list_console_messages`、`evaluate_script`、`press_key`、`take_screenshot`、`lighthouse_audit` 等）需要 `pageId` 参数。使用 `list_pages` 或从 `new_page` 获取可用的页面 ID。

**可访问性树与 DOM**：视觉隐藏元素（例如 `CSS opacity: 0`）与 `display: none` 或 `aria-hidden="true"` 对屏幕阅读器的行为不同。`take_snapshot` 工具返回页面的可访问性树，它代表了辅助技术“看到”的内容，使其成为语义结构的可靠信息来源。

**阅读 web.dev 文档**：如果您需要研究特定的可访问性指南（例如 `https://web.dev/articles/accessible-tap-targets`），可以将 `.md.txt` 追加到 URL 后面（例如 `https://web.dev/articles/accessible-tap-targets.md.txt`）以获取干净的原始 Markdown 版本。这样更容易阅读！

## 工作流模式

### 1. 自动化审计（Lighthouse）

首先运行 Lighthouse 可访问性审计以获取全面的基准。该工具提供高级评分并列出特定失败的元素及修复建议。

1.  运行审计：
    - 将 `mode` 设置为 `"navigation"` 以刷新页面并捕获加载问题。
    - 设置 `outputDirPath`（例如 `/tmp/lh-report`）以保存完整的 JSON 报告。
2.  **分析摘要**：
    - 检查 `scores`（0-1 分数）。分数小于 1 表示存在违规。
    - 查看 `audits.failed` 数量。
3.  **审查报告（关键）**：
    - **解析**：不要逐行读取整个文件。使用 `jq` 或 Node.js 单行命令等 CLI 工具过滤失败项：
      ```bash
      # 提取失败的审计及其详细信息
      node -e "const r=require('./report.json'); Object.values(r.audits).filter(a=>a.score!==null && a.score<1).forEach(a=>console.log(JSON.stringify({id:a.id, title:a.title, items:a.details?.items})))"
      ```
    - 这可以高效地提取失败元素的 `selector` 和 `snippet`，而无需将完整报告加载到上下文中。

### 2. 浏览器问题与审计

Chrome 自动检查常见的可访问性问题。使用 `list_console_messages` 检查这些原生审计：

- `types`: `["issue"]`
- `includePreservedMessages`: `true`（以捕获页面加载期间出现的问题）

这通常可以揭示缺少标签、无效的 ARIA 属性和其他关键错误，而无需手动调查。

### 3. 语义与结构

可访问性树暴露了标题层次结构和语义地标。

1.  导航到页面。
2.  使用 `take_snapshot` 捕获可访问性树。
3.  **检查标题级别**：确保标题级别（`h1`、`h2`、`h3` 等）是逻辑的，并且不跳过级别。快照将包括标题角色。
4.  **内容重新排序**：验证 DOM 顺序（它驱动可访问性树）是否与视觉阅读顺序匹配。使用 `take_screenshot` 检查视觉布局，并将其与快照结构进行比较，以捕获 CSS 浮动或绝对定位打乱逻辑流程的情况。

### 4. 标签、表单与文本替代

1.  在 `take_snapshot` 输出中定位按钮、输入和图像。
2.  确保交互元素具有可访问的名称（例如，如果按钮仅包含图标，则不应只显示 `""`）。
3.  **孤立的输入**：验证所有表单输入都有关联的标签。使用 `evaluate_script` 并使用在 [references/a11y-snippets.md](references/a11y-snippets.md) 中找到的 **“查找孤立表单输入”代码片段**。
4.  检查图像的 `alt` 文本。

### 5. 聚焦与键盘导航

测试“键盘陷阱”和适当的焦点管理而不依赖视觉反馈依赖于跟踪聚焦的元素。

1.  使用 `press_key` 工具并使用 `"Tab"` 或 `"Shift+Tab"` 移动焦点。
2.  使用 `take_snapshot` 捕获更新后的可访问性树。
3.  在快照中定位标记为聚焦的元素以验证焦点移动到预期的交互元素。
4.  如果打开模态，焦点必须移动到模态中并在关闭前“困住”在其中。

### 6. 点击目标与视觉

根据 web.dev，点击目标应至少为 48x48 像素并具有足够的间距。由于可访问性树不显示大小，使用 `evaluate_script` 并使用在 [references/a11y-snippets.md](references/a11y-snippets.md) 中找到的 **“测量点击目标大小”代码片段**。

_将快照中的元素的 `uid` 作为参数传递给 `evaluate_script`。_

### 7. 颜色对比度

为验证颜色对比度比率，首先检查原生可访问性问题：

1.  调用 `list_console_messages` 并设置 `types: ["issue"]`。
2.  在输出中查找“低对比度”问题。

如果原生审计未报告问题（这可能发生在某些无头环境中）或如果您需要手动检查特定元素，使用 `evaluate_script` 并使用在 [references/a11y-snippets.md](references/a11y-snippets.md) 中找到的 **“检查颜色对比度”代码片段**。

### 8. 全局页面检查

使用在 [references/a11y-snippets.md](references/a11y-snippets.md) 中找到的 **“全局页面检查”代码片段**，验证文档级可访问性设置，这些设置在组件测试中经常被遗漏。

## 故障排除

如果标准 a11y 查询失败或 `evaluate_script` 代码片段返回意外结果：

- **视觉检查**：如果自动化脚本无法确定对比度（例如，文本覆盖渐变图像或复杂背景），使用 `take_screenshot` 捕获元素。虽然模型无法从图像测量精确的对比度比率，但它们可以视觉评估可读性并识别明显问题。
