# 图像优化分析

## 检查项

### 替代文本
- 所有 `<img>` 元素均有替代文本（除装饰性：`role="presentation"`)
- 描述性：描述图像内容，而非 "image.jpg" 或 "photo"
- 自然包含相关关键词，避免关键词堆砌
- 长度：10-125个字符

**良好示例：**
- "专业水管工修理厨房水龙头"
- "红色2024款丰田凯美瑞轿车正面视图"
- "现代办公室会议室团队会议"

**不良示例：**
- "image.jpg"（文件名，非描述）
- "水管工水管服务水管"（关键词堆砌）
- "点击这里"（非描述性）

### 文件大小

**按图像类别分级的阈值：**

| 图像类别 | 目标 | 警告 | 严重
|----------|------|------|------|
| 缩略图 | < 50KB | > 100KB | > 200KB |
| 内容图像 | < 100KB | > 200KB | > 500KB |
| 主图/横幅图像 | < 200KB | > 300KB | > 700KB |

建议在不损失质量的情况下，尽可能压缩至目标阈值。

### 格式
| 格式 | 浏览器支持 | 用例 |
|------|------------|------|
| WebP | 97%+ | 默认推荐 |
| AVIF | 92%+ | 最佳压缩，较新 |
| JPEG | 100% | 照片回退 |
| PNG | 100% | 带透明度的图形 |
| SVG | 100% | 图标、标志、插图 |

推荐使用 WebP/AVIF 而非 JPEG/PNG。检查 `<picture>` 元素是否包含格式回退。

#### 推荐的 `<picture>` 元素模式

使用渐进增强，首先使用最高效的格式：

```html
<picture>
  <source srcset="image.avif" type="image/avif">
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="描述性替代文本" width="800" height="600" loading="lazy" decoding="async">
</picture>
```

浏览器将使用第一个支持的格式。当前浏览器支持：AVIF 93.8%，WebP 95.3%。

#### JPEG XL：新兴格式

第三方报告和维基百科描述了随Chrome 145稳定版（2026-02-10）发布的基于Rust的JPEG XL解码器，通过 `chrome://flags/#enable-jxl-image-format` 标志启用，默认未启用；未在事实包中检索到Google拥有的确认。由于默认支持未确认，目前不适合生产网站交付。继续使用AVIF/WebP并带有JPEG回退，并监控。

### 响应式图像
- `srcset` 属性用于多种尺寸
- `sizes` 属性匹配布局断点
- 适合设备像素比的正确分辨率

```html
<img
  src="image-800.jpg"
  srcset="image-400.jpg 400w, image-800.jpg 800w, image-1200.jpg 1200w"
  sizes="(max-width: 600px) 400px, (max-width: 1200px) 800px, 1200px"
  alt="描述"
>
```

### 懒加载
- `loading="lazy"` 用于折叠下方的图像
- **不要**懒加载折叠上方/主图（会损害LCP）
- 检查原生与基于JavaScript的懒加载

```html
<!-- 折叠下方 - 懒加载 -->
<img src="photo.jpg" loading="lazy" alt="描述">

<!-- 折叠上方 - 优先加载（默认） -->
<img src="hero.jpg" alt="主图">
```

#### 检测到的懒加载方法 (`lazy_method` 字段)

`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run parse_html.py` 通过每个图像条目的 `lazy_method` 字段对图像的懒加载机制进行分类。五个值：

| `lazy_method` | 检测到的信号 | 常见堆栈 |
|--------------|-------------|----------|
| `native` | `loading="lazy"` HTML属性 | 现代浏览器，纯HTML |
| `perfmatters` | `data-perfmatters-src`/`-srcset` OR 类 `perfmatters-lazy` | WordPress + Perfmatters插件 |
| `ewww` | `data-ewww-src` / `data-eio` OR 类 `lazyload-eio` | WordPress + EWWW Image Optimizer |
| `js-generic` | `data-src` / `data-lazy-src` / `data-original` / `data-srcset` OR 类 `lazyload`/`lazyloaded`/`lazy` | Lazysizes，原生懒加载，jQuery插件 |
| `none` | 既无属性也无类信号 | 页面未懒加载此图像 |

在审计图像SEO时，请与 `loading` 一起报告 `lazy_method`，以便用户知道其网站是否使用JS驱动的懒加载器（在这种情况下，原生 `loading="lazy"` 属性是故意缺失的，这不是回归）。

### `fetchpriority="high"` 用于LCP图像

在主图/LCP图像上添加 `fetchpriority="high"` 以在浏览器的网络队列中优先下载：

```html
<img src="hero.webp" fetchpriority="high" alt="主图描述" width="1200" height="630">
```

**关键：** **不要**懒加载折叠上方/LCP图像。在LCP图像上直接使用 `loading="lazy"` 会损害LCP分数。仅将 `loading="lazy"` 用于折叠下方图像。

### `decoding="async"` 用于非LCP图像

在非LCP图像上添加 `decoding="async"` 以防止图像解码阻塞主线程：

```html
<img src="photo.webp" alt="描述" width="600" height="400" loading="lazy" decoding="async">
```

### 防止内容布局偏移 (CLS)
- 所有 `<img>` 元素均设置 `width` 和 `height` 属性
- 使用CSS `aspect-ratio` 作为替代
- 标记无尺寸的图像

```html
<!-- 良好 - 尺寸已设置 -->
<img src="photo.jpg" width="800" height="600" alt="描述">

<!-- 良好 - CSS aspect ratio -->
<img src="photo.jpg" style="aspect-ratio: 4/3" alt="描述">

<!-- 不良 - 无尺寸 -->
<img src="photo.jpg" alt="描述">
```

### 文件名
- 描述性：`blue-running-shoes.webp` 而非 `IMG_1234.jpg`
- 连字符，小写，无特殊字符
- 包含相关关键词

### CDN使用
- 检查图像是否从CDN提供（不同域名，CDN头部）
- 建议图像密集型网站使用CDN
- 检查边缘缓存头部

## 输出

### 图像审计摘要

| 指标 | 状态 | 数量 |
|------|------|------|
| 总图像 | - | XX |
| 缺少替代文本 | ❌ | XX |
| 文件过大 (>200KB) | ⚠️ | XX |
| 错误格式 | ⚠️ | XX |
| 无尺寸 | ⚠️ | XX |
| 未懒加载 | ⚠️ | XX |

### 优先优化列表

按文件大小影响排序（最大节省优先）：

| 图像 | 当前大小 | 格式 | 问题 | 估计节省 |
|------|----------|------|------|----------|
| ... | ... | ... | ... | ... |

### 建议
1. 将X张图像转换为WebP格式（估计节省XX KB）
2. 为X张图像添加替代文本
3. 为X张图像添加尺寸
4. 在X张折叠下方图像上启用懒加载
5. 压缩X张过大图像

---

## 图像SERP分析

当DataForSEO MCP可用时，增强图像审计以包含竞争数据。

### `/seo images serp <关键词>`

将页面图像与Google SERP中可见的图像结果进行交叉引用。

**工作流程：**
1. 固定的DataForSEO MCP服务器（2.8.10）没有Google Images SERP工具。
   当SERP有 `images` 元素时，使用 `serp_organic_live_advanced`（深度=100），否则明确说明没有图像SERP数据
2. 提取：顶级域名，图像类型，替代文本模式
3. 输出竞争对手图像SERP格局

**输出：**

| 排名 | 域名 | 标题/替代 | 图像URL | 页面URL |
|------|------|-----------|-----------|----------|
| 1 | example.com | "蓝色跑步鞋..." | .../shoes.webp | /products/... |

**分析包括：**
- **域名主导权**：哪些网站拥有最多的图像位置（按数量排名前10）
- **替代文本模式**：排名靠前图像中常见的标题/替代模式
- **格式分布**：WebP与JPEG/PNG在顶部结果中的分布
- **机会分数**：您有页面排名但无图像存在的关键词

如果DataForSEO MCP不可用，请通知用户并建议安装扩展。

---

## 图像文件优化

为SEO优化图像文件：格式转换，元数据注入，压缩。

### `/seo images optimize <路径>`

为网络和SEO优化图像文件。转换为WebP/AVIF，注入IPTC元数据，压缩，并生成响应式变体。

**使用的工具（按优先级顺序）：**
- `exiftool` -- EXIF/IPTC/XMP读写（安装：`sudo apt install libimage-exiftool-perl`）
- `cwebp` -- WebP转换（安装：`sudo apt install webp`）
- ImageMagick `convert` -- 格式转换，调整大小（大多数系统预安装）
- FFmpeg -- 格式转换回退（预安装）

**运行前：** 使用 `which exiftool cwebp convert ffmpeg` 检查哪些工具可用。

### 格式转换

将图像转换为现代格式并保留元数据：

```bash
# WebP（推荐默认） - 保留元数据
cwebp -q 82 -metadata all input.jpg -o output.webp

# WebP via ImageMagick（cwebp未安装时的回退）
convert input.jpg -quality 82 output.webp

# AVIF via FFmpeg（较慢编码，最佳压缩）
ffmpeg -i input.jpg -c:v libaom-av1 -crf 30 -still-picture 1 output.avif

# 响应式变体（400w，800w，1200w）
convert input.jpg -resize 400x -quality 82 image-400.webp
convert input.jpg -resize 800x -quality 82 image-800.webp
convert input.jpg -resize 1200x -quality 82 image-1200.webp
```

### 元数据注入（IPTC用于Google Images显示）

Google Images在搜索结果中显示IPTC创作者，署名行和版权。
这**不是**排名因素，但可以改善Google Images显示和品牌归属。

**使用exiftool（首选）：**
```bash
# 读取所有元数据
exiftool image.jpg

# 注入IPTC + XMP元数据用于Google Images丰富结果
exiftool \
  -IPTC:ObjectName="产品照片描述" \
  -IPTC:Caption-Abstract="详细图像描述" \
  -IPTC:By-line="品牌名称摄影" \
  -IPTC:Credit="品牌名称" \
  -IPTC:CopyrightNotice="版权2026品牌名称" \
  -IPTC:Source="brandname.com" \
  -XMP:Title="产品照片描述" \
  -XMP:Description="详细图像描述" \
  -XMP:Creator="品牌名称摄影" \
  -XMP:Rights="版权2026品牌名称" \
  image.jpg

# 批量注入到目录中所有图像
exiftool -overwrite_original \
  -IPTC:By-line="品牌名称" \
  -IPTC:CopyrightNotice="版权2026品牌名称" \
  *.jpg *.webp *.png
```

**使用ImageMagick（回退）：**
```bash
identify -verbose image.jpg | head -50

convert input.jpg \
  -set comment "产品照片描述" \
  -set IPTC:2:80 "品牌名称摄影" \
  -set IPTC:2:116 "版权2026品牌名称" \
  output.jpg
```

注意：WebP原生支持EXIF和XMP，但不支持IPTC。对于WebP文件，请使用XMP字段而不是IPTC。exiftool自动处理此转换。

### AI生成图像：`DigitalSourceType`（Merchant Center要求）

对于由生成式AI生成的产品图像，**Google Merchant Center要求**
IPTC `DigitalSourceType: TrainedAlgorithmicMedia` 元数据。这是操作政策要求，不是排名因素：缺少此标签的AI生成图像可能会被拒。

主要来源（Merchant Center AI生成内容政策）：
https://support.google.com/merchants/answer/14743464
（`ai-optimization-guide` 未记录DigitalSourceType/IPTC/Merchant标签。）

**审计命令：**

```bash
# 审计目录中的IPTC标签（计数：缺失，AI，捕获，等）
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run iptc_ai_label.py audit ./images/ --json

# 审计单个图像
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run iptc_ai_label.py audit ./hero.webp --json

# 将AI标签注入图像
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run iptc_ai_label.py inject ./ai-hero.webp \
    --source-type trainedAlgorithmicMedia

# 其他词汇值：
#   compositeSynthetic               （捕获+AI元素混合）
#   algorithmicMedia                 （完全由算法创建，**不**来自采样训练数据）
#   compositeWithTrainedAlgorithmicMedia (例如AI修复/扩展真实媒体)
#   digitalCapture                   （完全捕获的摄影）
```

**exiftool等效命令**（用于临时使用）：

```bash
# 手动注入
exiftool \
  -XMP-iptcExt:DigitalSourceType="https://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia" \
  ai-generated-product.jpg

# 审计：跨目录查找缺少标签的图像
exiftool -if 'not $XMP-iptcExt:DigitalSourceType' \
  -filename *.jpg *.webp *.png
```

Google提取这些IPTC `DigitalSourceType` 值：
- `trainedAlgorithmicMedia`：完全AI生成（用于扩散模型产品图像）
- `compositeSynthetic`：混合捕获+AI生成元素
- `algorithmicMedia`：完全由算法创建，**不**来自采样训练数据
- `compositeWithTrainedAlgorithmicMedia`：训练算法媒体+其他媒体组合（例如AI修复/扩展真实照片）
- `digitalCapture`：完全捕获的摄影（注意：`digitalCapture`是**不**在Google提取值列表中，但是一个有效的IPTC值）

> **来源信号（面向消费者）**：**SynthID** 水印和 **C2PA** 内容凭证正在作为AI媒体识别的信号出现。将产品表面覆盖率视为可能变化，除非从当前Google拥有的来源验证。这是检测/透明度，**不是**额外的Merchant feed字段，除了IPTC DigitalSourceType。

> **可许可图像**：为获得Licensable徽章，提供结构化数据（`ImageObject` 带有 `license` 属性 + `acquireLicensePage` 用于“获取此图像”链接）或嵌入IPTC照片元数据（许可人URL/权利声明）。交叉引用 `seo-schema` 以获取ImageObject标记。

> **发现说明**：图像发现现在包括**视觉搜索发散**，跨越Lens / AI Mode / Circle to Search（Gemini多模态场景/对象理解），图像通过场景、对象和材料而非仅alt文本呈现。目前没有新的发布图像SEO杠杆；保持描述性alt文本+干净的结构化数据。

当 `/seo images optimize` 在AI生成资产上运行时，提示用户确认源类型并自动注入匹配的IPTC值。

对于**AI生成的产品标题和描述**，Google Merchant Center还要求AI生成的文本单独指定并标记在feed中。这由feed层而非页面层强制执行，在与 `seo-ecommerce` 交叉引用时标记。

### 元数据审计

```bash
# 快速审计使用exiftool
exiftool -IPTC:all -XMP:all -EXIF:ImageDescription image.jpg

# 批量审计 - 查找缺少IPTC Creator的图像
exiftool -if 'not $IPTC:By-line' -filename *.jpg *.webp *.png
```

### 完整优化流程

为最大图像SEO，对每个图像运行此流程：

1. **审计现有元数据**：`exiftool -IPTC:all -XMP:all image.jpg`
2. **注入IPTC/XMP元数据**：创作者，版权，描述
3. **转换为WebP**：`cwebp -q 82 -metadata all image.jpg -o image.webp`
4. **生成响应式变体**：400w，800w，1200w
5. **验证元数据保留**：`exiftool image.webp`
6. **生成 `<picture>` HTML**：AVIF > WebP > JPEG回退链

### 对Google Images重要与不重要

| 因素 | 影响 | 设置位置 |
|------|------|----------|
| 替代文本 | **关键**（排名） | HTML `<img alt="">` |
| 文件名 | **高**（排名） | 文件系统（描述性，连字符） |
| 页面上下文 | **高**（排名） | 周围HTML内容 |
| 文件大小/速度 | **中**（间接通过CWV） | 压缩+格式转换 |
| IPTC Creator/Copyright | **低**（仅显示） | 图像文件元数据 |
| EXIF相机数据 | 无 | 对SEO无关紧要 |
| IPTC关键词 | 无 | Google忽略这些 |

---

## 错误处理

| 场景 | 操作 |
|------|------|
| URL无法访问 | 报告连接错误和状态码。建议验证URL并检查是否需要身份验证。 |
| 页面上未找到图像 | 报告未检测到 `<img>` 元素。建议检查图像是否通过JavaScript加载或CSS background-image加载。 |
| 图像位于CDN或身份验证后 | 注释图像文件无法直接访问以进行大小分析。报告可用元数据（替代文本，尺寸，格式来自标记）并标记无法访问的资源。 |
| exiftool未安装 | 回退到ImageMagick进行元数据。建议：`sudo apt install libimage-exiftool-perl` |
| cwebp未安装 | 回退到ImageMagick或FFmpeg进行WebP转换。建议：`sudo apt install webp` |
| DataForSEO MCP不可用 | 跳过图像SERP分析部分。注释未安装扩展。 |
