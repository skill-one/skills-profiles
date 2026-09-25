# 图像处理

使用 `img-process`（包含在 `bin/` 目录中）执行常见操作。对于复杂或自定义工作流，生成适用于用户环境的 Pillow 脚本。

## 快速参考 — img-process 命令行界面

```bash
img-process resize hero.png --width 1920
img-process convert logo.png --format webp
img-process trim logo-raw.jpg -o logo-clean.png --padding 10
img-process thumbnail photo.jpg --size 200
img-process optimise hero.jpg --quality 85 --max-width 1920
img-process og-card -o og.png --title "My App" --subtitle "Built for speed"
img-process batch ./images --action convert --format webp -o ./optimised
```

**使用 `img-process` 当**：操作是标准的（调整大小、转换、裁剪、缩略图、优化、OG 卡片、批量处理）。这更快，并且避免了每次都生成脚本。

**生成自定义脚本当**：操作需要 `img-process` 未涵盖的逻辑（组合多个图像、水印、复杂文本布局、条件处理）。

## 先决条件

`img-process` 和自定义脚本都需要 Pillow：

```bash
pip install Pillow
```

如果 Pillow 不可用，请使用替代方案：

| 替代方案 | 平台 | 安装 | 适用于 |
|-------------|----------|---------|----------|
| `sips` | macOS（内置） | 无 | 调整大小、转换（无裁剪/OG） |
| `sharp` | Node.js | `npm install sharp` | 完整功能集、高性能 |
| `ffmpeg` | 跨平台 | `brew install ffmpeg` | 调整大小、转换 |

## 输出格式指南

| 使用场景 | 格式 | 原因 |
|----------|--------|-----|
| 照片、主图像 | WebP | 最佳压缩、广泛的浏览器支持 |
| Logo、图标（需要透明度） | PNG | 无损、支持 alpha |
| 旧浏览器的回退 | JPG | 通用支持 |
| 缩略图 | WebP 或 JPG | 优先考虑小文件大小 |
| OG 卡片 | PNG | 社交平台最佳处理 PNG |

## 核心模式

### 带特定格式质量的保存

不同格式需要不同的保存参数。始终处理 RGBA 到 JPG 的合成 — JPG 不支持透明度，因此首先合成到白色背景上。

```python
from PIL import Image
import os

def save_image(img, output_path, quality=None):
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    kwargs = {}
    ext = output_path.lower().rsplit(".", 1)[-1]

    if ext == "webp":
        kwargs = {"quality": quality or 85, "method": 6}
    elif ext in ("jpg", "jpeg"):
        kwargs = {"quality": quality or 90, "optimize": True}
        # RGBA → RGB: 合成到白色背景
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            img = bg
    elif ext == "png":
        kwargs = {"optimize": True}

    img.save(output_path, **kwargs)
```

### 保持宽高比的调整大小

当只给出宽度或高度时，根据宽高比计算另一个值。使用 `Image.LANCZOS` 进行高质量的下采样。

```python
def resize_image(img, width=None, height=None):
    if width and height:
        return img.resize((width, height), Image.LANCZOS)
    elif width:
        ratio = width / img.width
        return img.resize((width, int(img.height * ratio)), Image.LANCZOS)
    elif height:
        ratio = height / img.height
        return img.resize((int(img.width * ratio), height), Image.LANCZOS)
    return img
```

### 裁剪空白（自动裁剪）

从 Logo 和图标中移除周围的空白。首先转换为 RGBA，然后使用 `getbbox()` 找到内容边界。

```python
img = Image.open(input_path)
if img.mode != "RGBA":
    img = img.convert("RGBA")
bbox = img.getbbox()  # 非零像素的边界框
if bbox:
    img = img.crop(bbox)
```

### 缩略图

保持宽高比的同时适应最大尺寸：

```python
img.thumbnail((size, size), Image.LANCZOS)
```

### 优化用于网络

一步完成调整大小 + 压缩。转换为 WebP 以获得最佳压缩。典型设置：宽度 1920，质量 85。

### 跨平台字体发现

系统字体路径因操作系统而异。尝试多个路径，回退到 Pillow 的默认值。在 Linux 上，`fc-list` 可以动态发现字体。

```python
from PIL import ImageFont

def get_font(size):
    font_paths = [
        # macOS
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNSText.ttf",
        # Linux
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        # Windows
        "C:/Windows/Fonts/arial.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()
```

### OG 卡片生成（1200x630）

在背景图像或纯色上合成文本。应用半透明覆盖层以提高文本可读性。水平居中文本。

```python
from PIL import Image, ImageDraw, ImageFont

width, height = 1200, 630

# 背景：图像或纯色
if background_path:
    img = Image.open(background_path).resize((width, height), Image.LANCZOS)
else:
    img = Image.new("RGB", (width, height), bg_color or "#1a1a2e")

# 半透明覆盖层以提高文本可读性
overlay = Image.new("RGBA", (width, height), (0, 0, 0, 128))
img = img.convert("RGBA")
img = Image.alpha_composite(img, overlay)

draw = ImageDraw.Draw(img)
font_title = get_font(48)
font_sub = get_font(24)

# 居中标题
if title:
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw) // 2, height // 2 - 60), title, fill="white", font=font_title)

img = img.convert("RGB")
```

## 常见工作流

### Logo 清理（客户提供带白色背景的 JPG）

```bash
img-process trim logo-raw.jpg -o logo-trimmed.png --padding 10
img-process thumbnail logo-trimmed.png --size 512 -o favicon-512.png
```

### 准备用于生产的 Hero 图像

```bash
img-process optimise hero.jpg --max-width 1920 --quality 85
# 输出 hero.webp — 调整大小并压缩
```

### 批量处理

```bash
img-process batch ./raw-images --action convert --format webp --quality 85 -o ./optimised
img-process batch ./photos --action resize --width 800 -o ./thumbnails
```

### 使用 Gemini Image Gen 的流水线

使用 gemini-image-gen 技能生成图像，然后处理它们：

```bash
# 使用 Gemini 生成后（原始 PNG 输出）：
img-process optimise generated-image.png --max-width 1920 --quality 85
# 或批量处理所有生成的图像：
img-process batch ./generated --action optimise -o ./production
```
