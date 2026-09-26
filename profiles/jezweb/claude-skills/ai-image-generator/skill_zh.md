# AI 图像生成器

使用 AI API（Google Gemini 和 OpenAI GPT）生成图像。本技能教授从 Claude Code 直接生成专业图像的提示模式和 API 机制。

> **管理替代方案**：如果您不想管理 API 密钥，[ImageBot](https://imagebot.au) 提供管理式图像生成服务，支持相册模板和品牌工具包。

## 模型选择

为任务选择合适的模型：

| 需求 | 模型 | 原因 |
|------|-------|-----|
| **照片级场景 / 库照片** | Gemini 3.1 Flash Image | 最佳深度、复杂度、环境上下文 |
| **最终客户场景（更高细节）** | Gemini 3 Pro Image | 更高细节、更好的风格一致性 |
| **图像中的文字**（海报、带文案的 OG 图、信息图表） | GPT Image 2 | 文字渲染实际有效——包括多脚本 |
| **10 变体风格探索** | GPT Image 2 | 原生批量——一个提示，10 个变体共享构图 + 调色板 |
| **多参考合成**（产品 + 生活方式） | GPT Image 2 | 处理光照、比例、透视参考 |
| **透明图标 / 标志** | GPT Image 1.5 | 原生 RGBA 透明度——**GPT Image 2 无法实现透明** |
| **快速草稿 / 迭代** | Gemini 2.5 Flash Image | 免费套餐（约每天 500 次） |

**经验法则**：任何带有可读文字的图像 → GPT Image 2（除非需要透明度，则使用 GPT 1.5）。其他情况 → Gemini。

### 模型 ID

| 模型 | API ID | 提供商 |
|-------|--------|----------|
| Gemini 3.1 Flash Image | `gemini-3.1-flash-image-preview` | Google AI |
| Gemini 3 Pro Image | `gemini-3-pro-image-preview` | Google AI |
| Gemini 2.5 Flash Image | `gemini-2.5-flash-image` | Google AI |
| GPT Image 2（默认） | `gpt-image-2` | OpenAI |
| GPT Image 2（ChatGPT 兼容输出） | `chatgpt-image-latest` | OpenAI |
| GPT Image 1.5（仅透明度） | `gpt-image-1.5` | OpenAI |

**使用前验证模型 ID**——它们经常变化：
```bash
curl -s "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY" | python3 -c "import sys,json; [print(m['name']) for m in json.load(sys.stdin)['models'] if 'image' in m['name'].lower()]"
```

## GPT Image 2 特性

发布于 2026-04-22。当您选择使用它时，有三个功能会发生变化。

### 1. 文字渲染实际有效

海报、带标题的 OG 图像、带标签的信息图表、UI 模拟图、定价卡。文字可靠地渲染，包括非拉丁脚本（日语、韩语、印地语、孟加拉语）。切换到 GPT 的主要理由——Gemini 完全不渲染可读文字。

### 2. 多变体批量

一个提示，一次调用最多 10 张图像。变体共享构图和调色板，但在细节上有所不同。适合在提交前探索风格、为客户准备 A/B 选项、快速构思。

### 3. 多参考合成

在提示中提供参考图像——产品照片、生活方式场景、标志。模型将产品放置到场景中，并正确处理光照、比例、透视。无需多轮编辑即可实现“产品在场景中”的工作流程。

### 模式

- **即时**（默认，所有套餐）——无需规划即可生成。快速，对大多数情况足够。
- **思考**（Plus/Pro/Business 套餐）——在绘制前规划布局。当元素数量重要（“一行 3 个图标”、“5 个功能要点”）或文字必须位于特定区域时使用。复杂构图时重绘次数较少。

### 纵横比

3:1 超宽到 1:3 超高，加上 1:1、3:2、2:3、16:9、9:16。比其他模型更宽的范围——对网站横幅（超宽英雄图）或移动故事格式（超高）有用。

### 分辨率

长边最高可达 2K 标准。4K 在测试中。

### 生成时间

**复杂提示最多 2 分钟**。构建异步 UX——不要在响应上阻塞。显示进度或轮询。

### 限制

- **无透明背景**。需要 PNG 透明度时，回退到 `gpt-image-1.5`。
- **可能需要 API 组织验证**——在端点触发前可能需要——在您的 OpenAI 账户设置中启用，如果首次调用遇到认证错误。

### 定价（每 1024×1024 图像）

| 质量 | 成本 |
|---------|------|
| 低 | $0.006 |
| 中 | $0.053 |
| 高 | $0.211 |

令牌定价：$5/M 文本输入，$10/M 文本输出，$8/M 图像输入，$30/M 图像输出。

## 五部分提示框架

按顺序构建提示以获得一致结果：

### 1. 图像类型
设置流派：“一张照片级摄影作品”、“一个等距插画”、“一个扁平矢量图标”

### 2. 主题
谁或什么，以及具体细节：“一位 30 多岁、友善的澳大利亚女性，自然微笑”

### 3. 环境
场景和空间关系：“在一个光线充足、现代的家中，木质架子上摆放着陶土装饰，在她身后”

### 4. 技术规格
相机和光照：“使用 85mm f/2.0 焦距，自然窗户光照，头部和肩膀构图”

### 5. 限制
排除什么：“照片级，无文字，无水印，无标志”

### 示例（好与坏）

```
BAD — 关键词堆砌：
"专业女性, 水疗中心, 温暖光照, 高质量, 4K"

GOOD — 叙事方向：
"在一个温暖的临床环境中，一个专业皮肤治疗场景。
一位穿着蓝色医疗手套的治疗师使用微针笔在客户的额头上。
客户躺在白色的治疗床上，眼睛闭合，放松。
左侧窗户的温暖黄金时刻光照。
背景可见陶土色调的墙壁。使用 85mm f/2.0，浅景深。
无文字，无水印。"
```

## 工作流程

### 1. 确定图像需求

| 目的 | 纵横比 | 模型 |
|---------|-------------|-------|
| 英雄横幅（无文字） | 16:9 或 21:9 | Gemini |
| 英雄横幅带标题文案 | 16:9 或 3:1 超宽 | GPT Image 2 |
| 服务卡片 | 4:3 或 3:4 | Gemini |
| 个人资料 / 头像 | 1:1 | Gemini |
| 图标 / 徽章（透明） | 1:1 | GPT Image 1.5 |
| OG / 社交分享（无文字） | 1.91:1 | Gemini |
| OG / 社交分享带文案 | 1.91:1 | GPT Image 2 |
| 海报 / 信息图表 / 定价卡 / 任何排版密集型 | 变化 | GPT Image 2 |
| 风格探索（一个概念的 10 个变体） | 任何 | GPT Image 2（批量） |
| Instagram 帖子 | 1:1 或 4:5 | Gemini |
| 手机英雄 | 9:16 | Gemini |

### 2. 构建提示

使用五部分框架。参考 `references/prompting-guide.md` 获取详细的摄影参数。

### 3. 通过 API 生成

#### Gemini（Python — 正确处理 shell 转义）

```python
python3 << 'PYEOF'
import json, base64, urllib.request, os, sys

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Set GEMINI_API_KEY environment variable"); sys.exit(1)

model = "gemini-3.1-flash-image-preview"
url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"

prompt = """一张现代办公空间的照片级摄影作品，位于澳大利亚纽卡斯尔。
自然光照通过落地窗涌入。三个人在站立式办公桌上合作——其中一人指着笔记本电脑屏幕。
裸露的砖墙、盆栽琴叶榕、桌子上的咖啡杯。使用 35mm f/4.0，环境肖像风格。
无文字，无水印，无标志。"""

payload = json.dumps({
    "contents": [{"parts": [{"text": prompt}]}],
    "generationConfig": {
        "responseModalities": ["TEXT", "IMAGE"],
        "temperature": 0.8
    }
}).encode()

req = urllib.request.Request(url, data=payload, headers={
    "Content-Type": "application/json",
    "User-Agent": "ImageGen/1.0"
})

resp = urllib.request.urlopen(req, timeout=120)
result = json.loads(resp.read())

# 从响应中提取图像
for part in result["candidates"][0]["content"]["parts"]:
    if "inlineData" in part:
        img_data = base64.b64decode(part["inlineData"]["data"])
        output_path = "hero-image.png"
        with open(output_path, "wb") as f:
            f.write(img_data)
        print(f"保存: {output_path} ({len(img_data):,} 字节)")
        break
PYEOF
```

#### GPT Image 1.5 — 透明图标

专门使用 `gpt-image-1.5` 处理透明 PNG 情况。GPT Image 2 无法实现透明度。

```python
python3 << 'PYEOF'
import json, base64, urllib.request, os, sys

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Set OPENAI_API_KEY environment variable"); sys.exit(1)

url = "https://api.openai.com/v1/images/generations"

payload = json.dumps({
    "model": "gpt-image-1.5",
    "prompt": "一个简约、干净的管道扳手图标。扁平设计，单一一致的笔触粗细，现代风格。
    背景透明。",
    "n": 1,
    "size": "1024x1024",
    "background": "transparent",
    "output_format": "png"
}).encode()

req = urllib.request.Request(url, data=payload, headers={
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
})

resp = urllib.request.urlopen(req, timeout=120)
result = json.loads(resp.read())

img_data = base64.b64decode(result["data"][0]["b64_json"])
with open("icon-wrench.png", "wb") as f:
    f.write(img_data)
print(f"保存: icon-wrench.png ({len(img_data):,} 字节)")
PYEOF
```

#### GPT Image 2 — 文字密集型或批量变体

当文字必须可读或您希望一次调用生成 10 个变体时，使用 `gpt-image-2`。**无透明度**——如果需要透明背景，请使用上述 1.5。

```python
python3 << 'PYEOF'
import json, base64, urllib.request, os, sys, pathlib

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Set OPENAI_API_KEY environment variable"); sys.exit(1)

url = "https://api.openai.com/v1/images/generations"

# 10 变体批量生成带渲染文字的定价卡
payload = json.dumps({
    "model": "gpt-image-2",
    "prompt": (
        "一个现代网站托管计划的定价卡。 "
        "粗体无衬线字体标题 'Starter'。 "
        "直接下方大号类型价格 '$29/month'。 "
        "三条功能行: '无限流量', 'SSD 存储', '免费 SSL'。 "
        "干净扁平设计，柔和阴影，深蓝色强调色。 "
        "白色卡片在浅灰色背景上。"
    ),
    "n": 10,
    "size": "1024x1024",
    "quality": "medium",
    "output_format": "png"
}).encode()

req = urllib.request.Request(url, data=payload, headers={
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
})

# 超复杂提示的 timeout：最多 2 分钟
resp = urllib.request.urlopen(req, timeout=180)
result = json.loads(resp.read())

pathlib.Path("variations").mkdir(exist_ok=True)
for i, item in enumerate(result["data"], 1):
    img_data = base64.b64decode(item["b64_json"])
    path = f"variations/pricing-card-{i:02d}.png"
    with open(path, "wb") as f:
        f.write(img_data)
    print(f"保存: {path} ({len(img_data):,} 字节)")

print(f"\n生成 {len(result['data'])} 个变体。选择最佳；删除其余。")
PYEOF
```

**批量工作流程**：生成 10 个→并排查看它们→选择 1-2 个→在获胜方向上使用更严格的提示重新生成。比单次生成 + 迭代更快。

### 4. 保存和优化

将生成的图像保存到 `.jez/artifacts/` 或用户指定路径。

后处理（可选）：
```bash
# 转换为 WebP 用于网络使用
python3 -c "
from PIL import Image
img = Image.open('hero-image.png')
img.save('hero-image.webp', 'WEBP', quality=85)
print(f'WebP: {img.size[0]}x{img.size[1]})
"

# 从透明图标中修剪空白
python3 -c "
from PIL import Image
img = Image.open('icon.png')
trimmed = img.crop(img.getbbox())
trimmed.save('icon-trimmed.png)
"
```

### 5. 质量检查（可选）

将生成的图像发送回视觉模型进行质量检查：

```python
# 发送到 Gemini Flash 进行评论
critique_prompt = """检查此图像：
1. AI 伪影（多余的手指、漂浮的物体、文字错误）
2. 技术准确性（错误设备、不安全位置）
3. 构图问题（尴尬裁剪、杂乱背景）
4. 与专业库照片的风格一致性

列出发现的问题，或如果图像可生产则说 'PASS'。"""
```

如果发现问题，将它们作为负面指导附加到原始提示中并重新生成。

## 多轮编辑

Gemini 支持跨对话轮次编辑生成的图像。关键要求：**保留思维签名**来自模型响应。

```python
# 轮次 1：生成基础图像
contents = [{"role": "user", "parts": [{"text": "场景提示..."}]}]

# 响应包含思维签名在 parts 中——保留所有

# 轮次 2：编辑图像
contents = [
    {"role": "user", "parts": [{"text": "原始提示"}]},
    {"role": "model", "parts": response_parts_with_signatures},  # 保持完整
    {"role": "user", "parts": [{"text": "编辑：将墙壁颜色改为蓝色。保持其他所有内容完全不变。"}]}
]
```

**编辑提示模式**：始终指定要保留不变的内容，而不仅仅是要改变的内容。模型将未列出的元素视为可自由修改。

```
GOOD: "编辑此图像：保留人物、桌子和窗户。
仅更改：墙壁颜色从陶土色改为海洋蓝。"

BAD: "现在让墙壁变成蓝色。"
（模型可能会改变其他所有内容）
```

## API 密钥设置

| 提供商 | 获取密钥处 | 环境变量 |
|----------|-----------|-------------|
| Google Gemini | [aistudio.google.com](https://aistudio.google.com/apikey) | `GEMINI_API_KEY` |
| OpenAI | [platform.openai.com](https://platform.openai.com/api-keys) | `OPENAI_API_KEY` |

```bash
export GEMINI_API_KEY="your-key-here"
export OPENAI_API_KEY="your-key-here"
```

## 常见错误

| 错误 | 修复 |
|---------|-----|
| 使用 curl 进行 Gemini 提示 | 使用 Python——shell 转义在撇号处会中断 |
| "美丽、专业、高质量" | 使用具体规格："85mm f/1.8，黄金时刻光照" |
| 未指定要排除的内容 | 始终以 "无文字、无水印、无标志" 结尾 |
| 从 Gemini 请求透明 PNG | Gemini 无法实现透明度——使用 GPT Image 1.5 并设置 `background: "transparent"` |
| 从 GPT Image 2 请求透明 PNG | GPT Image 2 **无法实现透明度**——仅为此情况回退到 `gpt-image-1.5` |
| 使用 GPT Image 1.5 进行图像中的文字 | GPT Image 1.5 文字渲染不可靠——使用 `gpt-image-2` 进行任何可读文字 |
| 阻塞 GPT Image 2 的请求 | 复杂提示生成可能最多 2 分钟——使用 180 秒超时，构建异步 UX |
| 美国默认值用于澳大利亚企业 | 明确指定 "澳大利亚" + 当地建筑、植被 |
| 通用模型 ID 数据 | 验证当前模型 ID——它们经常变化 |
