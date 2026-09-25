# 生成图像

使用 OpenRouter 的图像生成模型（包括 FLUX.2 Pro 和 Gemini 3 Pro）生成和编辑高质量图像。

## 使用此技能的场景

**使用 generate-image 用于：**
- 照片和照片级真实图像
- 艺术插图和艺术作品
- 概念艺术和视觉概念
- 演示文稿或文档的视觉素材
- 图像编辑和修改
- 任何通用图像生成需求

**使用 scientific-schematics 代替：**
- 流程图和流程图
- 电路图和电气原理图
- 生物通路和信号级联
- 系统架构图
- CONSORT 图和方法学流程图
- 任何技术/原理图

## 快速入门

使用 `scripts/generate_image.py` 脚本生成或编辑图像：

```bash
# 生成新图像
python scripts/generate_image.py "山脉上美丽的日落"

# 编辑现有图像
python scripts/generate_image.py "将天空变成紫色" --input photo.jpg
```

这将在当前目录下生成/编辑图像并保存为 `generated_image.png`。

## API 密钥设置

**关键提示**：脚本需要 OpenRouter API 密钥。在运行之前，检查用户是否已配置其 API 密钥：

1. 在项目目录或父目录中查找 `.env` 文件
2. 检查 `.env` 文件中是否存在 `OPENROUTER_API_KEY=<key>`
3. 如果未找到，通知用户需要：
   - 创建 `.env` 文件并写入 `OPENROUTER_API_KEY=your-api-key-here`
   - 或设置环境变量：`export OPENROUTER_API_KEY=your-api-key-here`
   - 从 https://openrouter.ai/keys 获取 API 密钥

脚本将自动检测 `.env` 文件，并在 API 密钥缺失时提供清晰的错误消息。

## 模型选择

**默认模型**：`google/gemini-3-pro-image-preview`（高质量，推荐）

**可用于生成和编辑的模型**：
- `google/gemini-3-pro-image-preview` - 高质量，支持生成 + 编辑
- `black-forest-labs/flux.2-pro` - 快速，高质量，支持生成 + 编辑

**仅用于生成**：
- `black-forest-labs/flux.2-flex` - 快速且便宜，但质量不如 pro

根据以下因素选择：
- **质量**：使用 gemini-3-pro 或 flux.2-pro
- **编辑**：使用 gemini-3-pro 或 flux.2-pro（两者都支持图像编辑）
- **成本**：使用 flux.2-flex 仅用于生成

## 常见使用模式

### 基本生成
```bash
python scripts/generate_image.py "您的提示内容"
```

### 指定模型
```bash
python scripts/generate_image.py "太空中的猫" --model "black-forest-labs/flux.2-pro"
```

### 自定义输出路径
```bash
python scripts/generate_image.py "抽象艺术" --output artwork.png
```

### 编辑现有图像
```bash
python scripts/generate_image.py "将背景改为蓝色" --input photo.jpg
```

### 使用特定模型编辑
```bash
python scripts/generate_image.py "给人物添加太阳镜" --input portrait.png --model "black-forest-labs/flux.2-pro"
```

### 自定义输出
```bash
python scripts/generate_image.py "从图像中移除文字" --input screenshot.png --output cleaned.png
```

### 多个图像
多次运行脚本，使用不同的提示或输出路径：
```bash
python scripts/generate_image.py "图像1描述" --output image1.png
python scripts/generate_image.py "图像2描述" --output image2.png
```

## 脚本参数

- `prompt`（必填）：生成图像的文本描述或编辑指令
- `--input` 或 `-i`：编辑的输入图像路径（启用编辑模式）
- `--model` 或 `-m`：OpenRouter 模型 ID（默认：google/gemini-3-pro-image-preview）
- `--output` 或 `-o`：输出文件路径（默认：generated_image.png）
- `--api-key`：OpenRouter API 密钥（覆盖 .env 文件）

## 示例用例

### 用于科学文档
```bash
# 为论文生成概念插图
python scripts/generate_image.py "显微镜下癌细胞被免疫治疗药物攻击的视图，科学插图风格" --output figures/immunotherapy_concept.png

# 创建演示文稿视觉素材
python scripts/generate_image.py "DNA 双螺旋结构，突出显示突变位点，现代科学可视化" --output slides/dna_mutation.png
```

### 用于演示文稿和海报
```bash
# 标题幻灯片背景
python scripts/generate_image.py "抽象的蓝白背景，带有微妙的分子图案，专业演示文稿风格" --output slides/background.png

# 海报主视觉
python scripts/generate_image.py "实验室环境，配备现代设备，照片级真实感，光线充足" --output poster/hero.png
```

### 用于通用视觉内容
```bash
# 网站或文档图像
python scripts/generate_image.py "专业团队在数字白板周围协作，现代办公室" --output docs/team_collaboration.png

# 营销材料
python scripts/generate_image.py "未来主义 AI 大脑概念，带有发光神经网络" --output marketing/ai_concept.png
```

## 错误处理

脚本会提供清晰的错误消息，用于：
- 缺失 API 密钥（附带设置说明）
- API 错误（附带状态码）
- 预期之外的响应格式
- 缺少依赖项（requests 库）

如果脚本失败，请阅读错误消息并解决问题后再重试。

## 注意事项

- 图像以 base64 编码的数据 URL 返回，并自动保存为 PNG 文件
- 脚本支持来自不同 OpenRouter 模型的 `images` 和 `content` 响应格式
- 生成时间因模型而异（通常为 5-30 秒）
- 对于图像编辑，输入图像会编码为 base64 并发送到模型
- 支持的输入图像格式：PNG、JPEG、GIF、WebP
- 查看 OpenRouter 定价信息：https://openrouter.ai/models

## 图像编辑技巧

- 明确说明您希望进行的更改（例如，“将天空改为日落颜色”与“编辑天空”）
- 尽可能参考图像中的特定元素
- 为获得最佳结果，使用清晰详细的编辑指令
- Gemini 3 Pro 和 FLUX.2 Pro 都通过 OpenRouter 支持图像编辑

## 与其他技能的集成

- **scientific-schematics**：用于技术图表、流程图、电路、通路
- **generate-image**：用于照片、插图、艺术作品、视觉概念
- **scientific-slides**：与 generate-image 结合，用于视觉丰富的演示文稿
- **latex-posters**：使用 generate-image 用于海报视觉和主视觉
