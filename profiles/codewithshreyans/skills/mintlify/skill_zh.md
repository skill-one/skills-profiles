# Mintlify 参考

使用 Mintlify 构建文档的参考指南。本文件涵盖了适用于所有任务的要点。有关特定主题的详细参考，请阅读下方参考索引中列出的文件。

## 参考索引

**仅在您的任务需要时才阅读这些文件**。它们位于与此文件相邻的 `reference/` 目录中。要查找它们，请查看与该技能文件相同的目录（例如，`.claude/skills/mintlify/reference/`）。

| 文件 | 阅读时机 |
|------|-------------|
| `reference/components.md` | 添加或修改组件（提示、卡片、步骤、选项卡、手风琴、代码组、字段、框架、图标、工具提示、徽章、树形结构、mermaid、面板、提示、颜色、瓦片、更新、视图）。 |
| `reference/configuration.md` | 更改 `docs.json` 设置（主题、颜色、标志、字体、外观、导航栏、页脚、横幅、重定向、SEO、集成、API 配置）。还涵盖了代码片段、隐藏页面、`.mintignore`、自定义 CSS/JS 以及完整的 frontmatter 字段表。 |
| `reference/navigation.md` | 修改网站导航结构（分组、选项卡、锚点、下拉菜单、产品、版本、语言、导航中的 OpenAPI）。 |
| `reference/api-docs.md` | 设置 API 文档（OpenAPI、AsyncAPI、MDX 手动 API 页面、扩展、playground 配置）。 |

## 开始前

首先阅读项目的 `docs.json` 文件。它定义了网站的导航、主题、颜色和配置。

在创建新页面之前搜索现有内容。您可能需要更新现有页面、添加一个部分或链接到现有内容，而不是重复。

阅读 2-3 个类似的页面，以匹配网站的声音、结构和格式。

## 文件格式

Mintlify 使用带有 YAML frontmatter 的 MDX 文件（`.mdx` 或 `.md`）。

```
project/
├── docs.json           # 网站配置（必需）
├── index.mdx
├── quickstart.mdx
├── guides/
│   └── example.mdx
├── openapi.yml         # API 规范（可选）
├── images/             # 静态资源
│   └── example.png
└── snippets/           # 可重用组件
    └── component.jsx
```

### 文件命名

- 匹配目录中现有的命名模式
- 如果没有现有文件或混合文件命名模式，请使用连字符命名法：`getting-started.mdx`
- 将新页面添加到 `docs.json` 导航中，否则它们不会出现在侧边栏中

### 内部链接

- 使用不带文件扩展名的根相对路径：`/getting-started/quickstart`
- 不要使用相对路径（`../`）或绝对 URL 来引用内部页面

### 图片

将图片存储在 `images/` 目录中。使用根相对路径引用。所有图片都需要描述性 alt 文本。

```mdx
![显示分析概览的仪表板](/images/dashboard.png)
```

## 页面 frontmatter

每个页面都需要在 frontmatter 中包含 `title`。为 SEO 包含 `description` 和 `keywords`。

```yaml
---
title: "清晰、描述性的标题"
description: "用于 SEO 和导航的简洁摘要。"
keywords: ["相关", "搜索", "术语"]
---
```

### 常见的 frontmatter 字段

| 字段 | 类型 | 是否必需 | 描述 |
|-------|------|----------|-------------|
| `title` | string | 是 | 导航和浏览器选项卡中的页面标题。 |
| `description` | string | 否 | 用于 SEO 的简短描述。在标题下方显示。 |
| `sidebarTitle` | string | 否 | 侧边栏导航的简短标题。 |
| `icon` | string | 否 | Lucide、Font Awesome 或 Tabler 图标名称。也接受 URL 或文件路径。 |
| `tag` | string | 否 | 侧边栏中页面标题旁边的标签（例如，“NEW”）。 |
| `hidden` | boolean | 否 | 从侧边栏中隐藏。页面仍然可以通过 URL 访问。 |
| `mode` | string | 否 | 页面布局：`default`、`wide`、`custom`、`frame`、`center`。 |
| `keywords` | array | 否 | 用于内部搜索和 SEO 的搜索术语。 |
| `api` | string | 否 | 交互式 playground 的 API 端点（例如，`"POST /users"`）。 |
| `openapi` | string | 否 | OpenAPI 端点引用（例如，`"GET /endpoint"`）。 |

## 快速组件参考

下方列出了最常用的组件。有关完整属性和所有 24 个组件，请阅读 `reference/components.md`。

### 提示

```mdx
<Note>补充信息，可以安全跳过。</Note>
<Info>有帮助的上下文，例如权限或先决条件。</Info>
<Tip>建议或最佳实践。</Tip>
<Warning>可能具有破坏性的操作或重要注意事项。</Warning>
<Check>成功确认或完成状态。</Check>
<Danger>关于数据丢失或破坏性更改的严重警告。</Danger>
```

### 步骤

```mdx
<Steps>
  <Step title="第一步">
    第一步的说明。
  </Step>
  <Step title="第二步">
    第二步的说明。
  </Step>
</Steps>
```

### 选项卡和代码组

```mdx
<Tabs>
  <Tab title="npm">
    ```bash
    npm install package-name
    ```
  </Tab>
  <Tab title="yarn">
    ```bash
    yarn add package-name
    ```
  </Tab>
</Tabs>
```

```mdx
<CodeGroup>

```javascript example.js
const greeting = "Hello, world!";
```

```python example.py
greeting = "Hello, world!"
```

</CodeGroup>
```

### 卡片和列

```mdx
<Columns cols={2}>
  <Card title="第一张卡片" icon="rocket" href="/quickstart">
    卡片描述文本。
  </Card>
  <Card title="第二张卡片" icon="book" href="/guides">
    卡片描述文本。
  </Card>
</Columns>
```

使用 `<Columns>` 将卡片（或其他内容）排列成网格。`cols` 接受 1-4。

### 手风琴

```mdx
<AccordionGroup>
  <Accordion title="第一个部分">内容一。</Accordion>
  <Accordion title="第二个部分">内容二。</Accordion>
</AccordionGroup>
```

## CLI 命令

- `npm i -g mint` — 安装 Mintlify CLI。
- `mint dev` — 本地预览在 localhost:3000。
- `mint broken-links` — 检查内部链接。
- `mint a11y` — 检查可访问性问题。
- `mint validate` — 验证文档构建。
- `mint upgrade` — 从 `mint.json` 升级到 `docs.json`。

## 写作标准

- 第二人称语气（“你”）。
- 使用主动语气、直接语言。
- 标题使用句子大小写（“Getting started”，而不是“Getting Started”）。
- 代码块标题使用句子大小写。
- 所有代码块都必须有语言标签。
- 所有图片都必须有描述性 alt 文本。
- 不要使用营销语言、填充短语或表情符号。
- 保持代码示例简单、实用、经过测试。

## 常见错误

- 代码块缺少语言标签（使用 ` ```python `，而不是 ` ``` `）。
- 使用相对路径（`../page`）而不是根相对路径（`/section/page`）。
- 忘记将新页面添加到 `docs.json` 导航中。
- 缺少 alt 文本的图片。
- 内部链接添加了文件扩展名（`/page.mdx` 而不是 `/page`）。
