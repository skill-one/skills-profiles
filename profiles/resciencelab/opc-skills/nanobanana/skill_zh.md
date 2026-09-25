# Nano Banana - AI 图像生成

使用 Google 的 Gemini 3 Pro 图像模型（`gemini-3-pro-image-preview`，简称“Nano Banana Pro” 🍌）生成和编辑图像。

## 前置条件

**必需：**
- `GEMINI_API_KEY` - 从 [Google AI Studio](https://aistudio.google.com/apikey) 获取
- Python 3.10+ 及 `google-genai` 包

**安装依赖项：**
```bash
pip install google-genai pillow
```

## 快速入门

### 生成图像：
```bash
python3 <skill_dir>/scripts/generate.py "一个可爱的机器人吉祥物，像素艺术风格" -o robot.png
```

### 编辑现有图像：
```bash
python3 <skill_dir>/scripts/generate.py "将背景改为蓝色" -i input.jpg -o output.png
```

### 使用特定宽高比生成：
```bash
python3 <skill_dir>/scripts/generate.py "电影感风景" --ratio 21:9 -o landscape.png
```

### 生成高分辨率 4K 图像：
```bash
python3 <skill_dir>/scripts/generate.py "专业产品照片" --size 4K -o product.png
```

## 脚本参考

### `scripts/generate.py`

主要图像生成脚本。

```
用法：generate.py [选项] 提示

参数：
  提示              图像生成的文本提示

选项：
  -o, --output 路径   输出文件路径（默认：自动生成）
  -i, --input 路径    用于编辑的输入图像（可选）
  -r, --ratio 宽高比   宽高比（1:1, 16:9, 9:16, 21:9 等）
  -s, --size 尺寸     图像尺寸：2K 或 4K（默认：标准）
  --search            启用 Google 搜索基础以提高准确性
  -v, --verbose       显示详细输出
```

**支持的宽高比：**
- `1:1` - 方形（默认）
- `2:3`, `3:2` - 竖屏/横屏
- `3:4`, `4:3` - 标准
- `4:5`, `5:4` - 照片
- `9:16`, `16:9` - 宽屏
- `21:9` - 超宽屏/电影感

### `scripts/batch_generate.py`

使用顺序命名生成多个图像。

```
用法：batch_generate.py [选项] 提示

参数：
  提示              图像生成的文本提示

选项：
  -n, --count N       要生成的图像数量（默认：10）
  -d, --dir 路径      输出目录
  -p, --prefix STR    文件名前缀（默认："image"）
  -r, --ratio 宽高比   宽高比
  -s, --size 尺寸     图像尺寸（2K/4K）
  --delay 秒         生成之间的延迟（默认：3）
```

**示例：**
```bash
python3 <skill_dir>/scripts/batch_generate.py "像素艺术标志" -n 20 -d ./logos -p logo
```

## Python API

您也可以直接使用该模块：

```python
from generate import generate_image, edit_image

# 生成图像
result = generate_image(
    prompt="一个夜晚的未来城市",
    output_path="city.png",
    aspect_ratio="16:9",
    image_size="4K"
)

# 编辑现有图像
result = edit_image(
    prompt="给天空添加飞行汽车",
    input_path="city.png",
    output_path="city_edited.png"
)
```

## 环境变量

| 变量           | 描述               | 默认值       |
|---------------|--------------------|-------------|
| `GEMINI_API_KEY` | Google Gemini API 密钥 | 必需       |
| `IMAGE_OUTPUT_DIR` | 默认输出目录       | `./nanobanana-images` |

## 功能

### 文本到图像生成
从文本描述创建图像。该模型擅长：
- 照片级真实图像
- 艺术风格（像素艺术、插画等）
- 产品摄影
- 风景和场景

### 图像编辑
使用自然语言转换现有图像：
- 风格迁移
- 对象添加/删除
- 背景更改
- 颜色调整

### 高分辨率输出
- **标准**：快速生成，良好质量
- **2K**：增强细节（2048px）
- **4K**：最高质量（3840px），最适合文本渲染

### Google 搜索基础
启用 `--search` 以生成涉及以下内容的具有事实准确性的图像：
- 真实人物、地点、地标
- 当前事件
- 特定产品或品牌

## 最佳实践

### 提示编写

**良好的提示包括：**
- 主题描述
- 风格/美学
- 光照和氛围
- 构图细节
- 色彩搭配

**示例：**
```
"一个舒适的咖啡馆内部，温暖的光照，复古美学，
木质家具，架子上放有植物，晨光透过窗户，
背景模糊，35mm 电影摄影风格"
```

### 批量生成技巧

1. 生成 10-20 个变体以探索选项
2. 使用一致的提示以保持风格一致性
3. 添加 3-5 秒的延迟以避免速率限制
4. 审查结果并在最佳候选者上迭代

## 速率限制

- Gemini API 有使用配额
- 在批量生成之间添加延迟
- 在 [Google AI Studio](https://aistudio.google.com/) 检查您的配额

## 故障排除

**"API 密钥未找到"**
- 设置 `GEMINI_API_KEY` 环境变量
- 或通过 `--api-key` 选项传递

**"响应中无图像"**
- 提示可能触发了安全过滤器
- 尝试重新措辞以避免敏感内容

**"速率限制超出"**
- 等待几秒钟后重试
- 减小批量大小或添加更长的延迟

## 参考

- [references/prompts.md](./references/prompts.md) - 按类别划分的提示示例
- [examples/](./examples/) - 示例使用脚本
