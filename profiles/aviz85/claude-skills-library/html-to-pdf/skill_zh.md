# HTML转PDF转换器

使用Puppeteer（Chrome无头浏览器）实现像素级完美的HTML转PDF转换。为希伯来语、阿拉伯语和其他RTL语言提供出色的支持，并自动检测方向。

## 为什么选择Puppeteer？

- **像素级渲染**：使用真实的Chrome引擎
- **完整的CSS3/HTML5支持**：Flexbox、Grid、自定义字体、背景
- **JavaScript执行**：渲染动态内容
- **自动RTL检测**：检测希伯来语/阿拉伯语并设置方向
- **网络字体支持**：正确加载自定义字体

## 自动适配（内置，无需标志）

脚本自动处理内容溢出：

- **小溢出（高达~18%）** → 自动缩小字体大小以适应页面
- **大内容** → 流畅地跨多页显示，使用智能分页规则（不分割页眉、表格行或图像）
- **完美适配** → 无需操作

此功能在每次生成PDF时自动运行。无需标志。

## 关键：内容适配单页

**背景在`html`或`body`上会导致额外页面！** 将背景放在容器元素上：

```css
@page { size: A4; margin: 0; }

html, body {
  width: 210mm;
  height: 297mm;
  margin: 0;
  padding: 0;
  overflow: hidden;
  /* 这里不能有背景！ */
}

.container {
  width: 100%;
  height: 100%;
  padding: 20mm;
  box-sizing: border-box;
  background: linear-gradient(...); /* 背景放在这里 */
}
```

**导致额外页面的常见原因：**
1. **`html/body`上的背景** - 始终放在`.container`上
2. 内容溢出 - 使用`overflow: hidden`
3. 边距/填充推内容超出范围

**提示：**
- 如果内容仍然溢出，使用`--scale=0.75 --margin=0`
- 对于横向页面：使用`--landscape`

## 设置（一次性）

首次使用前，安装依赖项：

```bash
cd ~/.claude/skills/html-to-pdf && npm install
```

## 快速使用

### 转换本地HTML文件：
```bash
node ~/.claude/skills/html-to-pdf/scripts/html-to-pdf.js input.html output.pdf
```

### 将URL转换为PDF：
```bash
node ~/.claude/skills/html-to-pdf/scripts/html-to-pdf.js https://example.com page.pdf
```

### 带强制RTL的希伯来语文档：
```bash
node ~/.claude/skills/html-to-pdf/scripts/html-to-pdf.js hebrew.html hebrew.pdf --rtl
```

### 管道HTML内容：
```bash
echo "<h1>שלום עולם</h1>" | node ~/.claude/skills/html-to-pdf/scripts/html-to-pdf.js - output.pdf --rtl
```

## 选项参考

| 选项 | 描述 | 默认值 |
|------|------|--------|
| `--format=<format>` | 页面格式：A4、Letter、Legal、A3、A5 | A4 |
| `--landscape` | 使用横向方向 | false |
| `--margin=<value>` | 设置所有边距（例如，"20mm"、"1in"） | 20mm |
| `--margin-top=<value>` | 顶部边距 | 20mm |
| `--margin-right=<value>` | 右侧边距 | 20mm |
| `--margin-bottom=<value>` | 底部边距 | 20mm |
| `--margin-left=<value>` | 左侧边距 | 20mm |
| `--scale=<number>` | 缩放因子 0.1-2.0 | 1 |
| `--background` | 打印背景图形 | true |
| `--no-background` | 不打印背景 | - |
| `--header=<html>` | 头部HTML模板 | - |
| `--footer=<html>` | 尾部HTML模板 | - |
| `--wait=<ms>` | 等待字体/JS的时间 | 1000 |
| `--rtl` | 强制RTL方向 | auto-detect |
| `--expect-pages=<N>` | 预期页数（如果不同则警告） | 1 |
| `--no-page-check` | 禁用页数警告 | - |

## 自动溢出检测

脚本在生成PDF后自动检查页数。默认情况下，它期望1页，并在输出有更多页时发出警告：

```
⚠️  警告：检测到页面溢出！
   期望：1页
   实际：2页

   解决方法：减少内容、边距或字体大小
   使用--no-page-check禁用此警告
```

**用法：**
- 默认：期望1页，溢出时警告
- `--expect-pages=3`：期望3页（用于多页文档）
- `--no-page-check`：完全禁用检查

**注意：** 需要`pdfinfo`已安装（是poppler-utils的一部分）。如果不可用，检查将静默跳过。

## 示例

### 基本转换：
```bash
node ~/.claude/skills/html-to-pdf/scripts/html-to-pdf.js report.html report.pdf
```

### Letter格式带自定义边距：
```bash
node ~/.claude/skills/html-to-pdf/scripts/html-to-pdf.js doc.html doc.pdf --format=Letter --margin=1in
```

### 希伯来语发票：
```bash
node ~/.claude/skills/html-to-pdf/scripts/html-to-pdf.js invoice-he.html invoice.pdf --rtl
```

### 横向演示：
```bash
node ~/.claude/skills/html-to-pdf/scripts/html-to-pdf.js slides.html slides.pdf --landscape --format=A4
```

### 无边距（全出血）：
```bash
node ~/.claude/skills/html-to-pdf/scripts/html-to-pdf.js poster.html poster.pdf --margin=0
```

## 希伯来语/RTL最佳实践

为在HTML中获得最佳希伯来语渲染效果：

1. **设置lang属性**：`<html lang="he" dir="rtl">`
2. **使用UTF-8**：`<meta charset="UTF-8">`
3. **CSS方向**：为body添加`direction: rtl; text-align: right;`
4. **字体**：使用支持希伯来语的Web字体（Noto Sans Hebrew、Heebo、Assistant）

### 示例希伯来语HTML结构（单页）：
```html
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=Heebo:wght@400;700&display=swap" rel="stylesheet">
  <style>
    @page { size: A4; margin: 0; }
    html, body {
      width: 210mm;
      height: 297mm;
      margin: 0;
      padding: 0;
      overflow: hidden;
    }
    .container {
      width: 100%;
      height: 100%;
      padding: 20mm;
      box-sizing: border-box;
      font-family: 'Heebo', sans-serif;
      direction: rtl;
      text-align: right;
      background: #f5f5f5; /* 背景在容器上，不在body上 */
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>שלום עולם</h1>
    <p>זהו מסמך בעברית</p>
  </div>
</body>
</html>
```

## 关键：始终使用scale=1.0生成多页PDF

**绝对不要为多页文档使用`--scale` < 1.0。** 它会导致：
- 内容偏移（页面未居中）
- RTL文本在网格布局中溢出/裁剪
- 无法预测的视口宽度计算

**相反：减少CSS字体大小和间距以在scale=1.0时适应内容。**

```css
.page {
  width: 210mm;         /* 在scale=1.0时精确匹配A4 */
  height: 297mm;        /* 在scale=1.0时精确匹配A4 */
  padding: 8mm 10mm 12mm;
  page-break-after: always;
  position: relative;
  background: #f7f8fa;
  overflow: hidden;
  box-sizing: border-box;
}
```

**如果内容在scale=1.0时溢出：** 减小字体大小（10-11px基础），填充，边距——**不要缩小scale**。这保持了CSS与PDF之间的1:1映射，消除了所有布局问题。

**颜色提示：** 纯白色(#fff)背景会冲淡彩色点缀。使用#f7f8fa或#f8fafb以获得微妙对比，使颜色更突出。

## 故障排除

### 字体渲染不正确
- 添加`--wait=2000`以获得更多字体加载时间
- 确保通过`@font-face`或Google Fonts加载字体

### 希伯来语显示为从左到右
- 使用`--rtl`标志强制RTL方向
- 为HTML元素添加`dir="rtl"`

### 分页不工作
使用CSS分页属性：
```css
.page-break { page-break-after: always; }
.no-break { page-break-inside: avoid; }
```

### 背景不显示
- 确保`--background`已设置（默认为true）
- 仅在要排除背景时使用`--no-background`

## 自动适配内容（强制验证）

**关键 - Claude必须在每次PDF生成后执行：**

1. **使用读取工具读取PDF文件**以视觉检查
2. 检查垂直溢出（空页、内容溢出到下一页）
3. 检查水平溢出（文本被两侧裁剪）
4. **如果发现任何问题→修复并重新生成**（最多5次尝试）
5. **验证通过后才能将PDF交付给用户**

这不是可选的。未经视觉验证，切勿交付PDF。

### 要查找的问题

| 问题 | 症状 | 解决方法 |
|------|------|----------|
| **垂直溢出** | 页面底部有空白，内容溢出到下一页 | 减少`--scale` |
| **水平裁剪** | 文本被左右边缘裁剪 | 减少`--margin`并修复HTML宽度 |
| **两者问题** | 内容被裁剪且有多页 | 首先修复HTML CSS，然后调整scale |

### 修复策略（最多5次尝试）

**尝试1：默认设置**
```bash
node scripts/html-to-pdf.js input.html output.pdf
```

**尝试2：如果垂直溢出→减少scale**
```bash
node scripts/html-to-pdf.js input.html output.pdf --scale=0.9
```

**尝试3：如果水平裁剪→减少边距**
```bash
node scripts/html-to-pdf.js input.html output.pdf --scale=0.9 --margin=10mm
```

**尝试4：如果仍有问题→更小的scale+边距**
```bash
node scripts/html-to-pdf.js input.html output.pdf --scale=0.8 --margin=5mm
```

**尝试5：如果仍然失败→修复HTML CSS：**
```css
/* 添加到HTML以防止水平溢出 */
.container {
  width: 100%;
  max-width: 100%;
  overflow-wrap: break-word;
  word-wrap: break-word;
  box-sizing: border-box;
}
```

**5次尝试后停止** - 重新生成具有适当约束的HTML。

### HTML宽度修复（水平适配必需）

如果内容在两侧被裁剪，HTML必须具有：

```css
html, body {
  width: 210mm;  /* A4宽度 */
  margin: 0;
  padding: 0;
  overflow: hidden;
}

.container {
  width: 100%;
  max-width: 100%;
  padding: 15mm;
  box-sizing: border-box;
  overflow-wrap: break-word;
}
```

### 验证清单

每次生成PDF后，验证：
- [ ] 所有文本可见（边缘未裁剪）
- [ ] 没有空余页
- [ ] 内容正确填充页面
- [ ] 各部分之间没有大间隙

如果任何检查失败→调整并重新生成（最多5次）。

## 技术说明

- 使用Puppeteer与Chrome无头浏览器渲染
- 等待`networkidle0`以确保所有资源加载
- 自动等待`document.fonts.ready`
- 支持`@page` CSS规则用于打印样式
- 设备缩放因子设置为2以获得清晰的渲染
