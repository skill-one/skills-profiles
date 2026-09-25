# Gemini 图像生成 (Nano Banana Pro)

使用 Google 的 Gemini API 生成和编辑图像。必须设置环境变量 `GEMINI_API_KEY`。

## 默认模型

| 模型 | 分辨率 | 适用于 |
|------|--------|--------|
| `gemini-3-pro-image-preview` | 1K-4K | 所有图像生成（默认） |

**注意：** 始终使用此 Pro 模型。除非明确要求，否则不要使用其他模型。

## 快速参考

### 默认设置
- **模型：** `gemini-3-pro-image-preview`
- **分辨率：** 1K（默认，选项：1K、2K、4K）
- **宽高比：** 1:1（默认）

### 可用的宽高比
`1:1`、`2:3`、`3:2`、`3:4`、`4:3`、`4:5`、`5:4`、`9:16`、`16:9`、`21:9`

### 可用的分辨率
`1K`（默认）、`2K`、`4K`

## 核心API模式

```python
import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# 基本生成（1K，1:1 - 默认）
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=["在此处输入您的提示"],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
    ),
)

for part in response.parts:
    if part.text:
        print(part.text)
    elif part.inline_data:
        image = part.as_image()
        image.save("output.png")
```

## 自定义分辨率和宽高比

```python
from google.genai import types

response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[prompt],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        image_config=types.ImageConfig(
            aspect_ratio="16:9",  # 宽屏格式
            image_size="2K"       # 更高分辨率
        ),
    )
)
```

### 分辨率示例

```python
# 1K（默认）- 快速，适合预览
image_config=types.ImageConfig(image_size="1K")

# 2K - 质量与速度平衡
image_config=types.ImageConfig(image_size="2K")

# 4K - 最高质量，较慢
image_config=types.ImageConfig(image_size="4K")
```

### 宽高比示例

```python
# 正方形（默认）
image_config=types.ImageConfig(aspect_ratio="1:1")

# 横向宽屏
image_config=types.ImageConfig(aspect_ratio="16:9")

# 超宽全景
image_config=types.ImageConfig(aspect_ratio="21:9")

# 竖向
image_config=types.ImageConfig(aspect_ratio="9:16")

# 照片标准
image_config=types.ImageConfig(aspect_ratio="4:3")
```

## 编辑图像

传入现有图像和文本提示：

```python
from PIL import Image

img = Image.open("input.png")
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=["为这个场景添加日落", img],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
    ),
)
```

## 多轮细化

使用聊天进行迭代编辑：

```python
from google.genai import types

chat = client.chats.create(
    model="gemini-3-pro-image-preview",
    config=types.GenerateContentConfig(response_modalities=['TEXT', 'IMAGE'])
)

response = chat.send_message("为 'Acme Corp' 创建标志")
# 保存第一张图像...

response = chat.send_message("使文字更粗，并添加蓝色渐变")
# 保存细化图像...
```

## 提示最佳实践

### 照片级真实场景
包含相机细节：镜头类型、光照、角度、氛围。
> "一张照片级真实的中近景肖像，85mm镜头，柔和的黄金时刻光线，浅景深"

### 风格化艺术
明确指定风格：
> "一个可爱的红色熊猫贴纸，粗轮廓，赛璐璐着色，白色背景"

### 图像中的文字
明确说明字体风格和位置：
> "创建带有文字 'Daily Grind' 的标志，使用干净的无衬线字体，黑白，咖啡豆图案"

### 产品样机
描述光照设置和表面：
> "在抛光混凝土上的工作室照明产品照片，三点式柔光箱设置，45度角"

## 高级功能

### Google搜索基础
根据实时数据生成图像：

```python
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=["将东京今天的天气可视化为信息图表"],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
        tools=[{"google_search": {}}]
    )
)
```

### 多个参考图像（最多14个）
组合来自多个来源的元素：

```python
response = client.models.generate_content(
    model="gemini-3-pro-image-preview",
    contents=[
        "为这些人创建办公室合影",
        Image.open("person1.png"),
        Image.open("person2.png"),
        Image.open("person3.png"),
    ],
    config=types.GenerateContentConfig(
        response_modalities=['TEXT', 'IMAGE'],
    ),
)
```

## 重要：文件格式和媒体类型

**关键：** Gemini API 默认以JPEG格式返回图像。保存时，始终使用 `.jpg` 扩展名以避免媒体类型不匹配。

```python
# 正确 - 使用 .jpg 扩展名（Gemini返回JPEG）
image.save("output.jpg")

# 错误 - 将导致 "Image does not match media type" 错误
image.save("output.png")  # 创建带有PNG扩展名的JPEG！
```

### 转换为PNG（如果需要）

如果您需要PNG格式：

```python
from PIL import Image

# 使用Gemini生成
for part in response.parts:
    if part.inline_data:
        img = part.as_image()
        # 通过显式格式保存转换为PNG
        img.save("output.png", format="PNG")
```

### 验证图像格式

使用 `file` 命令检查实际格式与扩展名是否一致：

```bash
file image.png
# 如果输出显示 "JPEG image data" - 重命名为 .jpg！
```

## 注意事项

- 所有生成的图像都包含 SynthID 水印
- Gemini 默认返回 **JPEG格式** - 始终使用 `.jpg` 扩展名
- 图像模式 (`responseModalities: ["IMAGE"]`) 无法与 Google 搜索基础配合使用
- 对于编辑，以对话方式描述更改——模型理解语义遮罩
- 默认使用1K分辨率以加快速度；在质量关键时使用2K/4K
