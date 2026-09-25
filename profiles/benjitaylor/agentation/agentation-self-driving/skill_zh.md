# Agentation 自动驾驶模式

通过 Agentation 工具栏向网页添加设计注释，实现自主批判——在一个可见的浏览器中运行，以便用户可以实时观察代理的工作过程，就像观看自动驾驶汽车导航一样。

## 启动 — 始终可见

浏览器必须可见，绝不能以无头模式运行。用户需要观看您扫描、悬停、点击和注释的过程。

**预检查**：在其他任何操作之前，先验证 `agent-browser` 是否可用：

```bash
command -v agent-browser >/dev/null || { echo "ERROR: agent-browser 未找到。请先安装 agent-browser 技能。"; exit 1; }
```

**启动**：首先尝试直接打开。只有在打开命令因过期的会话而失败时才关闭现有会话——这样可以避免杀死其他人正在使用的浏览器：

```bash
# 尝试打开。如果失败（过期会话），先关闭再重试。
agent-browser --headed open <url> 2>&1 || { agent-browser close 2>/dev/null; agent-browser --headed open <url>; }
```

然后验证 Agentation 工具栏是否存在并展开它：

```bash
# 1. 检查页面上的工具栏是否存在。Agentation 3.1+ 在 <agentation-toolbar> 的 shadow root 中渲染，
#    所以通过它查询（回退到 document 以兼容旧版本）
agent-browser eval "(document.querySelector('agentation-toolbar')?.shadowRoot || document).querySelector('[data-feedback-toolbar]') ? '工具栏找到' : '未找到'"
# 如果 "未找到"：此页面未安装 Agentation — 停止并告知用户

# 2. 如果已折叠，则展开（点击已展开时会折叠它）
agent-browser eval "(document.querySelector('agentation-toolbar')?.shadowRoot || document).querySelector('[data-feedback-toolbar][class*=expanded]') ? '已展开' : ((document.querySelector('agentation-toolbar')?.shadowRoot || document).querySelector('[class*=toggleContent]')?.click(), '展开中')"

# 3. 验证：拍摄快照并查找工具栏控件
agent-browser snapshot -i
# 如果展开：您会看到 "阻止页面交互" 复选框、颜色按钮（紫色、蓝色等）
# 如果折叠：您只会看到小的切换按钮——重试步骤 2
```

"阻止页面交互" 必须被选中（默认开启）。

> **eval 引号规则**：在 eval 字符串中始终使用 `[class*=toggleContent]`（属性值周围不加引号）。不要在 eval 中使用双感叹号，因为 bash 将其视为历史扩展。也不要使用转义的内嵌引号，因为它们在不同 shell 中的行为不可预测。

## 关键：如何创建注释

**标准的元素点击（`click @ref`）不会触发注释对话框。** Agentation 遮罩层在坐标级别拦截指针事件。使用基于坐标的鼠标事件——这也使交互在浏览器中可见，就像光标在页面上移动一样。

> **`@ref` 兼容性**：只有 `click`、`fill`、`type`、`hover`、`focus`、`check`、`select`、`drag` 支持 `@ref` 语法。`scrollintoview`、`get box` 和 `eval` 命令不支持——它们需要 CSS 选择器。使用 `eval` 和 `querySelector` 进行滚动和位置查找。

```bash
# 1. 拍摄交互式快照——识别目标元素并构建 CSS 选择器
agent-browser snapshot -i
# 示例：快照显示标题 "指向错误。" [ref=e10]
# 推导 CSS 选择器：'h1'，或更具体：'h1:first-of-type'

# 2. 通过 eval 滚动元素到视图中（不是 `scrollintoview @ref`——那会出错）
agent-browser eval "document.querySelector('h1').scrollIntoView({block:'center'})"

# 3. 通过 eval 获取其边界框（不是 `get box @ref`——那也会出错）
agent-browser eval "((r) => r.x+','+r.y+','+r.width+','+r.height)(document.querySelector('h1').getBoundingClientRect())"
# 返回："383,245,200,40"  （将这些解析为 x,y,width,height）

# 4. 将光标移动到元素中心，然后点击
# centerX = x + width/2,  centerY = y + height/2
agent-browser mouse move <centerX> <centerY>
agent-browser mouse down left
agent-browser mouse up left

# 5. 获取注释对话框的引用——读取完整的快照输出
#    对话框引用出现在列表的底部，不要用 head/tail 截断
agent-browser snapshot -i
# 查找：文本框 "应该改变什么？" 和 "取消" / "添加" 按钮

# 6. 输入批判——fill 和 click 支持 `@ref`
agent-browser fill @<textboxRef> "您的批判内容"

# 7. 提交（添加按钮在文本填写后启用）
agent-browser click @<addRef>
```

如果点击后没有对话框出现，工具栏可能已折叠。重新展开（如果已折叠）并重试：

```bash
agent-browser eval "(document.querySelector('agentation-toolbar')?.shadowRoot || document).querySelector('[data-feedback-toolbar][class*=expanded]') ? 'ok' : ((document.querySelector('agentation-toolbar')?.shadowRoot || document).querySelector('[class*=toggleContent]')?.click(), '已展开')"
```

### 从快照构建 CSS 选择器

快照显示元素角色、名称和引用。将它们映射到 CSS 选择器：

| 快照行 | CSS 选择器 |
|--------|----------|
| `heading "指向错误。" [ref=e10]` | `h1` 或 `h1:first-of-type` |
| `button "npm install agentation 复制" [ref=e15]` | `button:has(code)` 或通过文本内容 via eval |
| `link "GitHub 星标" [ref=e28]` | `a[href*=github]` |
| `paragraph (长文本...) [ref=e20]` | 通过 section 目标：`section:nth-of-type(2) p` |

不确定时，使用更广泛的选择器并通过 eval 验证：
```bash
agent-browser eval "document.querySelector('h2').textContent"
```

## 循环

从上到下遍历页面。对于每个注释：

1. 通过 eval 滚动到目标区域（`scrollIntoView`）
2. 选择一个特定元素——标题、段落、按钮、容器
3. 通过 eval 获取其边界框（`getBoundingClientRect`）
4. 执行坐标点击序列（`mouse move` → `mouse down` → `mouse up`）
5. 读取**完整**的快照输出以查找对话框引用（在底部）
6. 输入批判（`fill @ref`）并提交（`click @ref`）
7. 验证注释是否已添加（见下文）
8. 移动到下一个区域

### 验证注释

提交每个注释后，确认数量增加：

```bash
agent-browser eval "(document.querySelector('agentation-toolbar')?.shadowRoot || document).querySelectorAll('[data-annotation-marker]').length"
# 应返回预期数量（第一次后为 1，第二次后为 2 等）
```

如果数量未增加，提交失败——对话框可能仍然打开，重新快照并检查。

目标是每页 5-8 个注释，除非另有指示。

## 需要批判的内容

| 区域 | 查找内容 |
|------|--------|
| **英雄区域 / 可见区域** | 标题层级、CTA 位置、视觉分组 |
| **导航** | 标签样式、分类分组、视觉权重 |
| **演示 / 插图** | 清晰度、深度、动画可读性 |
| **内容区域** | 间距节奏、注释处理、排版层级 |
| **关键标语** | 是否有足够的视觉强调 |
| **CTA 和页脚** | 转化权重、视觉分离、最终操作 |

## 批判风格

每条注释最多 2-3 句话：

- **具体且可操作**："将安装命令堆叠在副标题下方 16px" 而不是 "修复布局"
- **1-2 个具体替代方案**：参考 CSS 值、布局模式或设计系统
- **命名原则**：视觉层级、格式塔分组、空白、强调、转化设计
- **参考可比产品**："像 Stripe/Linear/Vercel 这样处理"

差： "这个区域需要改进"
好： "这个项目列表读起来像文档，而不是展示。使用 3 列卡片网格加图标——参考 Stripe 的指南模式。创建视觉节奏和可扫描性。"

## 安装

技能必须链接到 `~/.claude/skills/`，以便 Claude Code 发现它：

```bash
ln -s "$(pwd)/skills/agentation-self-driving" ~/.claude/skills/agentation-self-driving
```

安装后重启 Claude Code。使用 `/agentation-self-driving` 验证——如果加载技能说明，则链接正常工作。

## 故障排除

- **"浏览器未启动。请先调用 launch。"**：来自先前运行的过期会话——运行 `agent-browser close 2>/dev/null` 然后重试 `--headed open` 命令
- **页面未找到工具栏**：未安装 Agentation——先运行 `/agentation` 设置它
- **点击后无对话框**：工具栏已折叠——用状态感知的 eval 重新展开（先检查 `[class*=expanded]`），重试
- **目标元素错误**：点击取消，滚动到目标元素，用正确坐标重试
- **添加按钮保持禁用**：未填写文本——重新快照并填写文本框
- **页面导航**： "阻止页面交互" 已关闭——通过工具栏设置启用
- **注释数量未增加**：提交失败——对话框可能仍然打开，重新快照并检查
- **运行中断（Ctrl+C）**：浏览器保持打开，处于任何状态。运行 `agent-browser close` 清理，然后开始新会话

## agent-browser 陷阱

如果不注意，这些会无声地破坏工作流程：

| 陷阱 | 发生什么 | 修复 |
|------|--------|------|
| `scrollintoview @ref` |崩溃："解析 css 选择器时遇到不支持的标记 @ref" | 使用 `eval "document.querySelector('sel').scrollIntoView({block:'center'})"` |
| `get box @ref` | 同样崩溃——`get box` 将引用解析为 CSS 选择器 | 使用 `eval "((r)=>r.x+','+r.y+','+r.width+','+r.height)(document.querySelector('sel').getBoundingClientRect())"` |
| `eval` 双感叹号 | Bash 在命令运行前扩展双感叹号作为历史替换 | 使用 `expr !== null` 或 `expr ? true : false` 代替 |
| `eval` 转义引号 | 转义的内嵌引号跨 shell 行为不可预测 | 删除引号：`[class*=toggleContent]` 适用于没有空格的简单值 |
| `snapshot -i \| head -50` | 注释对话框引用（`textbox "应该改变什么？"`，`添加`，`取消`）出现在快照的底部 | 始终读取**完整**的快照输出——不要截断 |
| `click @ref` 在遮罩元素上 | 点击穿透到真实 DOM，绕过 Agentation 遮罩层 | 使用 `mouse move` → `mouse down left` → `mouse up left` 进行基于坐标的点击，遮罩层会拦截 |
| `--headed open` 因 "Browser not launched" 失败 | 来自先前运行的过期会话阻止新启动 | 运行 `agent-browser close 2>/dev/null` 然后重试打开命令 |

**经验法则**：`@ref` 适用于交互命令（`click`、`fill`、`type`、`hover`）。对于其他命令（`eval`、`get`、`scrollintoview`），使用 eval 中的 CSS 选择器 `querySelector`。

## 双会话工作流（完整自动驾驶）

连接 MCP（工具栏显示 "MCP Connected"），注释自动发送到任何监听的代理。这使能够：

- **会话 1**（此技能）：观察页面，在可见浏览器中添加批判性注释
- **会话 2**：运行 `agentation_watch_annotations` 在循环中，接收注释，编辑代码以解决每个问题

用户在浏览器中观察会话 1 驾驶页面，同时会话 2 在代码库中修复问题——实现完全自主的设计审查和实施。
