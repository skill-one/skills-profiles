# 提取设计语言

从任何网站 URL 中提取完整的设计语言。生成 8 个输出文件，涵盖颜色、排版、间距、阴影、组件、断点、动画和可访问性。

## 前置条件

确保 `designlang` 可用。如有需要，请安装：

```bash
npm install -g designlang
```

或使用 npx（无需安装）：

```bash
npx designlang <url>
```

## 流程

1. **在提供的 URL 上运行提取**：

```bash
npx designlang <url> --screenshots
```

对于多页面爬取：`npx designlang <url> --depth 3 --screenshots`
对于暗黑模式：`npx designlang <url> --dark --screenshots`

2. **阅读生成的 markdown 文件以理解设计**：

```bash
cat design-extract-output/*-design-language.md
```

3. **向用户展示关键发现**：
   - 主要色板及十六进制代码
   - 使用的字体家族
   - 间距系统（如检测到基础单位）
   - WCAG 可访问性评分
   - 发现的组件模式
   - 值得注意的设计决策（阴影、圆角等）

4. **提供后续步骤**：
   - 将 `*-tailwind.config.js` 复制到他们的项目中
   - 将 `*-variables.css` 导入他们的样式表
   - 将 `*-shadcn-theme.css` 复制到 globals.css（适用于 shadcn/ui 用户）
   - 为 React/CSS-in-JS 项目导入 `*-theme.js`
   - 将 `*-figma-variables.json` 导入 Figma 以进行设计交接
   - 在浏览器中打开 `*-preview.html` 以获取视觉概览
   - 将 markdown 文件用作 AI 辅助开发的上下文

## 输出文件 (8)

| 文件 | 目的 |
|------|---------|
| `*-design-language.md` | AI 优化的 markdown — 适用于 LLM 的完整设计系统 |
| `*-preview.html` | 带有色板、排版比例、阴影、a11y 的视觉 HTML 报告 |
| `*-design-tokens.json` | W3C 设计标记格式 |
| `*-tailwind.config.js` | 即用型 Tailwind CSS 主题 |
| `*-variables.css` | CSS 自定义属性 |
| `*-figma-variables.json` | Figma 变量导入格式 |
| `*-theme.js` | React/CSS-in-JS 主题对象 |
| `*-shadcn-theme.css` | shadcn/ui 主题 CSS 变量 |

## 额外命令

- **比较两个网站**：`npx designlang diff <urlA> <urlB>`
- **查看历史记录**：`npx designlang history <url>`

## 选项

| 标志 | 描述 |
|------|-------------|
| `--out <dir>` | 输出目录（默认：`./design-extract-output`） |
| `--dark` | 同时提取暗黑模式色板 |
| `--depth <n>` | 爬取 N 个内部页面以进行全站提取 |
| `--screenshots` | 捕获组件截图（按钮、卡片、导航） |
| `--wait <ms>` | 页面加载后的等待时间（适用于 SPAs） |
| `--framework <type>` | 仅生成特定主题（`react` 或 `shadcn`） |
