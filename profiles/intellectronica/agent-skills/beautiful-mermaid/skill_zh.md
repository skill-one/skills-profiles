# 美丽的 Mermaid 图表渲染

使用 Beautiful Mermaid 库将 Mermaid 图表渲染为 SVG 和 PNG 图片。

## 依赖项

此技能需要 `agent-browser` 技能用于 PNG 渲染。在进行 PNG 捕获之前加载它。

## 支持的图表类型

- **流程图** - 流程、决策树、CI/CD 管道
- **时序图** - API 调用、OAuth 流程、数据库事务
- **状态图** - 状态机、连接生命周期
- **类图** - UML 类图、设计模式
- **实体关系图** - 数据库模式、数据模型

## 可用主题

默认、Dracula、Solarized、Zinc Dark、Tokyo Night、Tokyo Night Storm、Tokyo Night Light、Catppuccin Latte、Nord、Nord Light、GitHub Dark、GitHub Light、One Dark。

如果没有指定主题，则使用 `default`。

## 常见语法模式

### 流程图边标签

使用管道语法为边标签：

```mermaid
A -->|标签| B
A ---|标签| B
```

避免使用空格短横线语法，这可能导致渲染不完整：

```mermaid
A -- 标签 --> B   # 可能导致问题
```

### 带特殊字符的节点标签

用引号括起包含特殊字符的标签：

```mermaid
A["标签带括号 (parens)"]
B["标签带 / 斜杠"]
```

## 工作流程

### 第 1 步：生成或验证 Mermaid 代码

如果用户提供的是描述而不是代码，则生成有效的 Mermaid 语法。参考 `references/mermaid-syntax.md` 获取完整的语法细节。

### 第 2 步：渲染 SVG

运行渲染脚本以生成 SVG 文件：

```bash
bun run scripts/render.ts --code "graph TD; A-->B" --output diagram --theme default
```

或从文件：

```bash
bun run scripts/render.ts --input diagram.mmd --output diagram --theme tokyo-night
```

替代运行时：

```bash
npx tsx scripts/render.ts --code "..." --output diagram
deno run --allow-read --allow-write --allow-net scripts/render.ts --code "..." --output diagram
```

这会在当前工作目录生成 `<output>.svg`。

### 第 3 步：创建 HTML 包装器

运行 HTML 包装器脚本以准备截图：

```bash
bun run scripts/create-html.ts --svg diagram.svg --output diagram.html
```

这会创建一个显示 SVG 并具有适当填充和背景的最小 HTML 文件。

### 第 4 步：使用 agent-browser 捕获高分辨率 PNG

使用 agent-browser CLI 捕获高质量截图。参考 `agent-browser` 技能获取完整的 CLI 文档。

```bash
# 设置 4K 视口以进行高分辨率捕获
agent-browser set viewport 3840 2160

# 打开 HTML 包装器
agent-browser open "file://$(pwd)/diagram.html"

# 等待渲染完成
agent-browser wait 1000

# 捕获全页截图
agent-browser screenshot --full diagram.png

# 关闭浏览器
agent-browser close
```

对于更复杂的图表，要获得更高的分辨率，可以进一步增加视口或在使用 HTML 包装器脚本创建时使用 `--padding` 选项，为图表提供更多空间。

### 第 5 步：清理中间文件

渲染完成后，删除所有中间文件。只有最终的 `.svg` 和 `.png` 应保留。

要清理的文件：

- HTML 包装器文件（例如，`diagram.html`）
- 任何创建的临时 `.mmd` 文件以保存图表代码
- 渲染过程中创建的任何其他文件

```bash
rm diagram.html
```

如果创建了临时 `.mmd` 文件，也请删除它。

## 输出

始终会生成两种输出：

- **SVG**：矢量格式，无限可缩放，文件大小小
- **PNG**：高分辨率光栅，以 4K（3840×2160）视口捕获，图表宽度最小为 1200px

文件保存在当前工作目录，除非用户明确指定了其他路径。

## 主题选择指南

| 主题 | 背景 | 适用于 |
|------|------|--------|
| default | 浅灰色 | 通用使用 |
| dracula | 深紫色 | 深色模式偏好 |
| tokyo-night | 深蓝色 | 现代深色美学 |
| tokyo-night-storm | 更深的蓝色 | 更高的对比度 |
| nord | 深极地 | 柔和、平静的视觉效果 |
| nord-light | 浅极地 | 浅色模式，柔和色调 |
| github-dark | GitHub 深色 | 匹配 GitHub UI |
| github-light | GitHub 浅色 | 匹配 GitHub UI |
| catppuccin-latte | 温暖浅色 | 柔和的粉彩色美学 |
| solarized | 茶色/奶油色 | Solarized 色彩方案 |
| one-dark | Atom 深色 | Atom 编辑器美学 |
| zinc-dark | 中性深色 | 极简，无颜色偏好 |

## 故障排除

### 主题未应用

检查渲染脚本输出中的 `bg` 和 `fg` 值，或检查 SVG 的开头标签中的 `--bg` 和 `--fg` CSS 自定义属性。

### 图表显示被裁剪或未完整

- 检查边标签语法 — 使用 `-->|标签|` 管道符号，而不是 `-- 标签 -->`
- 验证所有节点 ID 是否唯一
- 检查节点标签中的括号是否未关闭

### 渲染产生空或格式错误的 SVG

- 在渲染前在 https://mermaid.live 验证 Mermaid 语法
- 检查需要转义的特殊字符（用引号括起）
- 确保指定了流程图方向 (`graph TD`, `graph LR` 等)
