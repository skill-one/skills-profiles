# posterskill — 学术海报生成器

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能集合。

posterskill 是一个 Claude Code 技能，可以从您的 Overleaf 论文源生成可打印的、交互式会议海报。它生成一个包含内置拖放式视觉编辑器的单一、自包含的 HTML 文件 — 无需构建步骤，无需服务器。

## 安装与设置

```bash
git clone git@github.com:ethanweber/posterskill.git poster
cd poster

# 克隆您的 Overleaf 论文源
git clone https://git.overleaf.com/YOUR_PROJECT_ID overleaf

# 可选：添加参考海报以匹配样式
cp ~/Downloads/some_reference_poster.pdf references/
```

启动 Claude Code 并触发该技能：

```bash
claude
```

```
/make-poster
```

Claude 会询问您的项目网站 URL 和任何格式规范，然后生成一个 `poster/` 目录，其中包含 `index.html`。

## 目录结构

```
poster/                  # 此代码库
├── .claude/
│   └── commands/
│       └── make-poster.md   # 技能命令
├── overleaf/            # 您克隆的 Overleaf 项目
├── references/          # 可选的参考 PDF，用于样式匹配
└── poster/              # 生成的输出
    ├── index.html       # 海报（自包含）
    └── logos/           # 下载的机构标志
```

## 生成的文件

输出的 `poster/index.html` 是一个 React 应用程序（通过 CDN 加载），其中包含：

- **`CARD_REGISTRY`** — 每个卡片的标题、颜色和 JSX 正文内容
- **`DEFAULT_LAYOUT`** — 列表结构和卡片顺序
- **`DEFAULT_LOGOS`** — 用于页眉的机构标志
- **`window.posterAPI`** — 用于布局自动化的程序化 API

## 视觉编辑器功能

在 Chrome 中打开 `poster/index.html` 以访问内置编辑器：

| 功能 | 使用方法 |
|---------|-----------|
| 调整列大小 | 拖动列分隔符左右 |
| 调整卡片大小 | 在列内拖动行分隔符上下 |
| 交换卡片 | 点击一个菱形手柄，然后点击另一个 |
| 移动/插入卡片 | 点击一个手柄，然后点击一个放置区域 |
| 调整字体大小 | 点击工具栏中的 **A-** / **A+** 按钮 |
| 预览打印布局 | 点击 **预览** 按钮 |
| 导出布局 | 点击 **复制配置** 获取 JSON |

## 程序化 API (`window.posterAPI`)

可在浏览器控制台或通过 Playwright 自动化使用：

```js
// 通过 ID 交换两个卡片
posterAPI.swapCards('method', 'results')

// 将卡片移动到特定列和位置
posterAPI.moveCard('quant', 'col1', 2)

// 调整列宽度（单位：毫米）
posterAPI.setColumnWidth('col1', 280)

// 设置特定卡片的高度（单位：毫米）
posterAPI.setCardHeight('method', 150)

// 全局缩放所有文本
posterAPI.setFontScale(1.5)

// 测量空白浪费（数值越低，布局越好）
posterAPI.getWaste()

// 获取当前布局作为对象
posterAPI.getLayout()

// 获取完整配置作为 JSON（粘贴回 Claude）
posterAPI.getConfig()

// 重置为默认布局
posterAPI.resetLayout()
```

## 迭代工作流程

优化海报的核心循环：

1. **Claude 生成** 初稿，在您的浏览器中打开 `poster/index.html`
2. **您在浏览器中编辑** — 拖动分隔符，交换卡片，调整列大小
3. **点击工具栏中的“复制配置”** 导出您的布局为 JSON
4. **将 JSON 粘贴回 Claude** — 它会更新 HTML 中的 `DEFAULT_LAYOUT`
5. **重复** 直至布局完美
6. **打印为 PDF**: 文件 → 打印 → 边距：无，背景图形：开启

## Playwright 自动化（Claude 内部使用）

Claude 使用 Playwright 自动化布局验证。您也可以使用它：

```js
const { chromium } = require('playwright');

async function optimizePoster() {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  await page.goto(`file://${__dirname}/poster/index.html`);
  
  // 使用 posterAPI 程序化调整布局
  const waste = await page.evaluate(() => posterAPI.getWaste());
  console.log('空白浪费:', waste);
  
  // 调整列大小
  await page.evaluate(() => posterAPI.setColumnWidth('col1', 300));
  
  // 截屏进行视觉验证
  await page.screenshot({ path: 'poster-preview.png', fullPage: true });
  
  // 以打印分辨率生成 PDF
  await page.pdf({
    path: 'poster.pdf',
    width: '841mm',   // A0 横向宽度
    height: '1189mm',
    printBackground: true,
  });
  
  await browser.close();
}
```

## 卡片注册结构

海报中的每个卡片都在 `CARD_REGISTRY` 中定义：

```js
const CARD_REGISTRY = {
  abstract: {
    title: "摘要",
    color: "#f0f4ff",
    body: `
      <p>您的摘要文本。支持完整的 JSX，包括
      <strong>粗体</strong>、<em>斜体</em> 和内联数学。</p>
    `
  },
  method: {
    title: "方法",
    color: "#fff8f0",
    body: `
      <img src="figures/pipeline.png" style={{width:'100%'}} />
      <p>描述上述流程的说明。</p>
    `
  },
  results: {
    title: "结果",
    color: "#f0fff4",
    body: `
      <table>...</table>
    `
  }
};
```

## 默认布局结构

```js
const DEFAULT_LAYOUT = {
  columns: [
    {
      id: 'col1',
      widthMm: 280,
      cards: ['abstract', 'method']
    },
    {
      id: 'col2', 
      widthMm: 320,
      cards: ['results', 'quant']
    },
    {
      id: 'col3',
      widthMm: 280,
      cards: ['结论', '参考文献']
    }
  ]
};
```

## Claude 使用的输入

| 输入 | 来源 | 必填 |
|-------|--------------------|---------:|
| 论文内容 | `overleaf/` 目录 | 是 |
| 项目网站 | URL（在运行时询问） | 是 |
| 参考海报 | `references/*.pdf` | 否 |
| 作者网站 | 用于品牌匹配的 URL | 否 |
| 格式规范 | 会议 URL 或文本 | 缺失时询问 |
| 标志 | 自动下载到 `poster/logos/` | 自动 |

## 常见模式

### 添加自定义图表卡片

```js
// 在 CARD_REGISTRY 中添加新卡片
custom_fig: {
  title: "定性结果",
  color: "#fafafa",
  body: `
    <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:'8px'}}>
      <img src="figures/result1.png" style={{width:'100%'}} />
      <img src="figures/result2.png" style={{width:'100%'}} />
    </div>
    <p style={{fontSize:'0.85em', textAlign:'center'}}>
      在保留测试场景上的比较。
    </p>
  `
}
```

然后添加到 `DEFAULT_LAYOUT`：

```js
{ id: 'col2', widthMm: 320, cards: ['results', 'custom_fig'] }
```

### 标志配置

```js
const DEFAULT_LOGOS = [
  { src: 'logos/university.png', height: 60 },
  { src: 'logos/lab.png', height: 50 },
  { src: 'logos/sponsor.png', height: 45 },
];
```

### 打印为 PDF

在 Chrome 中：
1. 打开 `poster/index.html`
2. 点击 **预览** 验证布局
3. `Ctrl+P` / `Cmd+P`
4. 设置 **边距：无**
5. 启用 **背景图形**
6. 设置纸张大小为会议规范（A0、36×48英寸等）
7. 保存为 PDF

## 故障排除

**打印和浏览器中的海报外观不同**
→ 使用 Chrome（不要使用 Firefox/Safari）。在打印对话框中启用 "背景图形"。

**图表无法加载**
→ 确保 HTML 中的图表路径相对于 `poster/index.html` 是相对的。Claude 将图表复制到 `poster/figures/` — 验证目录是否存在。

**标志未获取**
→ Claude 使用 Playwright 从您的项目网站下载标志。如果失败，手动将标志文件复制到 `poster/logos/` 并更新 `DEFAULT_LOGOS` 路径。

**布局配置粘贴后未更新**
→ 确保您粘贴了完整的 **复制配置** JSON — Claude 寻找完整的 `DEFAULT_LAYOUT` 和 `DEFAULT_LOGOS` 对象进行替换。

**字体太小/太大**
→ 使用 `posterAPI.setFontScale(1.2)` 在浏览器控制台中，或点击 **A+** / **A-** 按钮，然后复制配置并粘贴回 Claude。

**卡片之间有空白间隙**
→ 运行 `posterAPI.getWaste()` 在控制台量化。使用 `posterAPI.setCardHeight('cardId', heightMm)` 调整卡片高度，或手动拖动行分隔符。

## 示例输出

查看 [Fillerbuster 海报](http://ethanweber.me/fillerbuster-poster)（[代码库](https://github.com/ethanweber/fillerbuster-poster)）作为 posterskill 输出的实时示例。
