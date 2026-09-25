# imagencn - 多云文生图技能

## 概述

**imagencn — 图像生成，云原生：一个命令行工具，所有图像云。** 该项目始于友好的中国云，现已涵盖国际提供商。

使用阿里云百炼 API 生成图像。**默认端点是中国区域**。

支持跨越十四个模型系列的九个平台：

- **阿里云百炼**（DashScope）：Qwen-Image 2.0，Qwen-Image Edit，Qwen-Image 传统，万系列，Z-Image
- **字节跳动火山岩**：豆包-Seedream 系列（兼容 OpenAI 的 REST）
- **腾讯混元**：混元图像 3.0（兼容 OpenAI 的 REST）
- **智谱 / 大模型**：CogView-4 和 GLM-Image（兼容 OpenAI 的 REST）
- **StepFun / 阶跃星辰**：Step-2X 和 Step-Image-Edit（兼容 OpenAI 的 REST）
- **谷歌 Gemini**（国际）：Gemini 3 Pro Image / 3.1 Flash Image（generateContent REST）
- **Grok / xAI**（国际）：Grok Imagine（兼容 OpenAI 的 REST）
- **OpenAI**（国际）：GPT Image 1 / 2（Images API）
- **Black Forest Labs / FLUX**（国际）：FLUX.2 Pro / Max（异步 REST）

**跨平台支持**：Windows，macOS，Linux

## 何时使用此技能

在以下情况下自动激活此技能：

- 用户请求使用中文文本或书法生成图像
- 需要逼真的照片或摄影风格视觉效果
- 创建商业海报、插图或数字艺术
- 用户提到以下任何一项：阿里云 / 百炼 / Qwen / 万 / DashScope，字节跳动 / 火山岩 / Seedream / 豆包，腾讯 / 混元，谷歌 / Gemini / Nano Banana，Grok / xAI，OpenAI / GPT Image，FLUX / Black Forest Labs
- 用户希望使用国际（非中国）图像提供商——使用 Gemini / Grok / OpenAI / FLUX 平台
- 任何需要具有强大中文支持的 AI 生成图像的任务

## 模型参考

当用户想要比较模型、查看定价或在选择前浏览选项时，在他们的浏览器中打开本地模型参考页面：

```bash
open ~/.claude/skills/imagencn/docs/models.html
```

此页面显示跨越九个平台的 44 个模型，包括定价、分辨率、功能亮点和快速参考指南。在 Linux 上使用 `xdg-open`；该文件也可以从 `file://` 使用，无需服务器。

## 工作流程

### 第一步 — 精炼提示（交互式，永不跳过）

用户经常给出简短、随意的描述（“生成一只猫”）。在调用 API 之前，**提供三个精炼的提示选项**，具有不同的风格方向。根据需要添加：

- 主题细节（形状、颜色、材质、表情、姿势）
- 光照（黄金时刻、工作室、边缘光、柔和漫射、霓虹灯、电影感）
- 构图（三分法、浅景深、广角、特写）
- 风格/媒介（照片逼真、油画、水彩、3D 渲染、矢量）
- 情绪/氛围（宁静、戏剧性、奇幻、反乌托邦、优雅）
- 质量关键词（8K、超精细、获奖、专业摄影）
- 对于图像上的中文文本：文本内容、位置、字体样式、颜色、大小

清晰标记选项（例如 A / B / C），并附上每个方向的简短摘要。让用户选择一个，组合多个元素，或请求新的方向。迭代直到他们确认（“去”、“生成”、“好”等），然后继续生成。

### 第二步 — 选择模型

根据请求选择（见下文模型选择指南）。不确定时默认为 `qwen-image-2.0-pro`。向用户提及你的选择。

### 第三步 — 选择尺寸

Qwen-Image 2.0 的原生 2K，Wan2.7 的 `1K`/`2K`/`4K`，或长宽比预设（`16:9`，`1:1` 等）。

### 第四步 — 生成

运行 `scripts/generate_image.py`，并使用确认的提示和输出路径。

### 第五步 — 保存

如果输出路径是隐式的，则保存到用户的当前工作目录。

## 模型

### Qwen-Image 2.0 系列 - 最新旗舰（MultiModalConversation API）

| 模型 | 描述 |
| ------- | ------------- |
| `qwen-image-2.0-pro` | **默认**。最新旗舰，原生 2K，最强的排版和细节 |
| `qwen-image-2.0-pro-2026-06-22` | 最新快照（2026 年 6 月）：生成 + 编辑融合，更好的文本渲染和提示遵循 |
| `qwen-image-2.0` | 标准 2.0 级，原生 2K |
| `qwen-image-max` | 前代旗舰（2025 年 12 月） |
| `qwen-image-max-2025-12-30` | qwen-image-max 快照：改进逼真度，更少的 AI 伪影 |

### Qwen-Image Edit 系列 - 图像编辑（MultiModalConversation API）

编辑模型需要通过 `--image`（本地路径或 URL）提供输入图像。省略 `--size` 以匹配输入图像的尺寸。

| 模型 | 描述 |
| ------- | ------------- |
| `qwen-image-edit-max` | 旗舰编辑模型，最强的指令遵循 |
| `qwen-image-edit-max-2026-01-16` | 最新 max 快照（2026 年 1 月） |
| `qwen-image-edit-plus` | 更快、更便宜的编辑 |

### Qwen-Image 传统（ImageSynthesis API）

| 模型 | 描述 |
| ------- | ------------- |
| `qwen-image-plus` | qwen-image-max 的蒸馏加速版本 |
| `qwen-image-plus-2026-01-09` | qwen-image-plus 快照（2026 年 1 月）：更快的高质量生成 |
| `qwen-image` | 基础模型 |

### 万系列 - 照片逼真生成（ImageGeneration API）

| 模型 | 描述 |
| ------- | ------------- |
| `wan2.7-image-pro` | **最新**。最高 4K 输出，统一架构（T2I + 编辑 + 多图像） |
| `wan2.7-image` | Wan 2.7 标准，最高 2K |
| `wan2.6-t2i` | Wan 2.6，灵活的尺寸 |
| `wan2.5-t2i-preview` | 高质量，最高 768x2700 |
| `wan2.2-t2i-flash` | 速度优化 |
| `wan2.2-t2i-plus` | 专业级别 |
| `wanx2.1-t2i-turbo` | 快速执行 |
| `wanx2.1-t2i-plus` | 专业级别 |
| `wanx2.0-t2i-turbo` | 更早一代 |

### Z-Image - 轻量级和快速（MultiModalConversation API）

| 模型 | 描述 |
|-------|-------------|
| `z-image-turbo` | 快速、低成本生成；双语文本渲染（中/英），高保真肖像和产品图像。像素区域 512x512 到 2048x2048 |

### 火山岩 - 字节跳动 Seedream（兼容 OpenAI 的 API）

| 模型 | 描述 |
| ------- | ------------- |
| `doubao-seedream-5-0-260128` | **火山岩默认**。最新，最高 3K，PNG/JPEG 输出，最佳文本渲染 |
| `doubao-seedream-4-5-251128` | Seedream 4.5，最高 4K |
| `doubao-seedream-4-0-250828` | Seedream 4.0，最高 4K，经济实惠 |

### 腾讯混元（兼容 OpenAI 的 API）

| 模型 | 描述 |
|-------|-------------|
| `hy-image-v3.0` | **混元默认**。旗舰 3.0，强烈的构图感知，处理复杂的中文字符提示（最高 8K 字符） |

### 智谱 / 大模型 - CogView-4 & GLM-Image（兼容 OpenAI 的 API）

| 模型 | 描述 |
|-------|-------------|
| `cogview-4` | **智谱默认**。稳定别名，用于最新 CogView-4，原生中文文本渲染 |
| `cogview-4-250304` | CogView-4 固定快照（2025 年 3 月），可重复结果 |
| `glm-image` | GLM-Image 旗舰，最高 2048x2048，混合自回归/扩散 |

### 阶跃星辰 / StepFun - Step-2X（兼容 OpenAI 的 API）

| 模型 | 描述 |
|-------|-------------|
| `step-2x-large` | **阶跃星辰默认**。高质量（0.1 人民币/图像），最高 1024x1024 |
| `step-image-edit-2` | 快速且便宜（0.02 人民币/图像），支持负向提示，8 次推理 |

### 谷歌 Gemini - 国际（generateContent API）

| 模型 | 描述 |
|-------|-------------|
| `gemini-3-pro-image-preview` | **Gemini 默认**。谷歌旗舰图像模型，512/1K/2K 命名尺寸加上长宽比预设 |
| `gemini-3-pro-image` | 稳定旗舰（Nano Banana Pro），1K/2K/4K |
| `gemini-3.1-flash-image` | Nano Banana 2：快速通用，512/1K/2K/4K，强大的文本渲染 |
| `gemini-3.1-flash-lite-image` | Nano Banana 2 Lite：最快/最便宜，仅 1K |

### Grok / xAI - 国际（兼容 OpenAI 的 API）

| 模型 | 描述 |
|-------|-------------|
| `grok-imagine-image-quality` | **Grok 默认**。高质量 Grok 图像模型，长宽比 + 分辨率预设（最高 4K） |
| `grok-imagine-image` | 标准 Grok 图像模型（别名 `grok-imagine-image-2026-03-02`) |
| `grok-2-image` | 传统 JPG 模型，无尺寸控制 |

### OpenAI - GPT Image（Images API）

| 模型 | 描述 |
|-------|-------------|
| `gpt-image-1` | **OpenAI 默认**。多模态图像模型；1024x1024 / 1536x1024 / 1024x1536 仅限 |
| `gpt-image-1-mini` | 快速、便宜的 GPT 图像变体 |
| `gpt-image-1.5` | 改进 GPT 图像生成质量 |
| `gpt-image-2` | 最新旗舰；任意 WxH 尺寸（边缘可被 16 整除）最高 4K |

### Black Forest Labs / FLUX - 国际（异步 REST API）

FLUX 使用异步 API：提交请求，轮询完成，然后保存。提示上采样是内置的（需要时使用 `disable_pup` 禁用）。

| 模型 | 描述 |
|-------|-------------|
| `flux-2-pro-preview` | **FLUX 默认**。最新滚动 FLUX.2 Pro，推荐用于新用例 |
| `flux-2-pro` | FLUX.2 Pro 的固定快照，用于可重复的工作流程 |
| `flux-2-max` | 最高质量的 FLUX.2，实时信息搜索 |

> **FLUX 3**：图像生成尚未通过 API 公开提供（仅限早期访问，截至 2026 年 8 月没有公共端点）。关注 `bfl.ai` 获取一般发布。

## 使用方法

### 基本使用

```bash
# 默认模型（qwen-image-2.0-pro，原生 2K 输出）
python ~/.claude/skills/imagencn/scripts/generate_image.py "一只可爱的猫" output.png

# 照片逼真，使用 Wan 模型（Wan2.7 支持 4K）
python ~/.claude/skills/imagencn/scripts/generate_image.py --model wan2.7-image-pro --size 4K "日落山脉的逼真照片" photo.png

# 编辑现有图像（需要 --image；本地路径或 URL）
python ~/.claude/skills/imagencn/scripts/generate_image.py --model qwen-image-edit-max --image input.png "将背景改为日落海滩" edited.png
```

### 尺寸选项

```bash
# 使用比例预设
python ~/.claude/skills/imagencn/scripts/generate_image.py --size 16:9 "宽景观" landscape.png

# 使用精确尺寸
python ~/.claude/skills/imagencn/scripts/generate_image.py --size 1280*720 "自定义尺寸" custom.png
```

### 尺寸预设

**Qwen-Image 2.0（原生 2K）：**

- `1:1` -> 2048x2048（默认）
- `16:9` -> 2688x1536
- `9:16` -> 1536x2688
- `4:3` -> 2304x1728
- `3:4` -> 1728x2304
- `1K` -> 1024x1024
- `2K` -> 2048x2048

**Qwen-Image 传统：**

- `1:1` -> 1328x1328
- `16:9` -> 1664x928
- `9:16` -> 928x1664
- `4:3` -> 1472x1104
- `3:4` -> 1104x1472

**Z-Image（像素区域 512x512 到 2048x2048）：**

- `1:1` -> 1024x1024（默认）
- `16:9` -> 1280x720
- `9:16` -> 720x1280
- `2:3` -> 1024x1536
- `3:2` -> 1536x1024
- `1K` -> 1024x1024

**Wan 系列（Wan2.7 也接受 `1K`/`2K`/`4K`）：**

- `1:1` -> 1024x1024
- `1:1-large` -> 1280x1280
- `16:9` -> 1280x720
- `9:16` -> 720x1280
- `4:3` -> 1200x900
- `3:4` -> 900x1200
- `2:1` -> 1440x720

**火山岩（Seedream）：**

- `1:1` -> 2048x2048
- `16:9` -> 2848x1600
- `9:16` -> 1600x2848
- `4:3` -> 2304x1728
- `3:4` -> 1728x2304
- `3:2` -> 2496x1664
- `2:3` -> 1664x2496
- `1K` / `2K` / `3K` / `4K`（模型依赖的最大分辨率）

**腾讯混元（冒号分隔格式）：**

- `1:1` -> 1024:1024
- `16:9` -> 1920:1080
- `9:16` -> 1080:1920
- `4:3` -> 1600:1200
- `3:4` -> 1200:1600

**智谱（CogView-4 / GLM-Image）：**

- `1:1` -> 1024x1024（默认）
- `16:9` -> 1344x768
- `9:16` -> 768x1344
- `4:3` -> 1152x864
- `3:4` -> 864x1152
- `2:1` -> 1440x720
- `1:2` -> 720x1440

**阶跃星辰（StepFun）：**

- `1:1` -> 1024x1024（默认）
- `1:1-small` -> 512x512
- `16:9` -> 1280x800
- `9:16` -> 800x1280

**谷歌 Gemini（命名尺寸 + 长宽比）：**

- `512` / `1K`（默认） / `2K` / `4K` -> 命名输出尺寸（Pro / 3.1 Flash；Lite 仅限 1K）
- `1:1`, `16:9`, `9:16`, `4:3`, `3:4` -> 长宽比（没有精确像素尺寸）

**Grok / xAI（长宽比 + 分辨率）：**

- `1:1`, `16:9`, `9:16`, `4:3`, `3:4`, `2:1` -> 作为 `aspect_ratio` 发送（默认：1:1）
- `1K` / `2K` / `4K` -> 作为 `resolution` 发送

**OpenAI（GPT Image）：**

- `1:1` -> 1024x1024（默认）
- `16:9` -> 1536x1024, `9:16` -> 1024x1536
- `4:3` -> 1344x1024, `3:4` -> 1024x1344
- `1K` -> 1024x1024, `2K` -> 2048x2048（gpt-image-2 仅限），`4K` -> 3840x2160（gpt-image-2 仅限）

**FLUX（Black Forest Labs）：**

- `1:1` -> 1024x1024（默认）
- `16:9` -> 1344x768, `9:16` -> 768x1344
- `4:3` -> 1152x864, `3:4` -> 864x1152
- `2:1` -> 1440x720, `1:2` -> 720x1440
- `1K` -> 1024x1024, `2K` -> 2048x2048（也接受灵活 WxH）
