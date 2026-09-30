---
name: imagencn
description: 通过DashScope/Ark/Hunyuan/Zhipu/StepFun结合Grok/OpenAI/Gemini/FLUX（国际版）实现跨平台AI图像生成，专注于中文文本渲染和照片级真实图像
---

# imagencn - 多云文生图技能

## 概述

**imagencn — 图像生成，云原生：一个命令行工具，所有图像云。** 该项目始于对中国的友好云服务，现已涵盖国际提供商。

使用阿里云百炼API生成图像。**默认端点是中国区域**。

支持跨越十四个模型系列的九个平台：

- **阿里云百炼**（DashScope）：Qwen-Image 2.0，Qwen-Image编辑，Qwen-Image传统，万系列，Z-图像
- **字节跳动火山引擎**：豆包-星梦系列（兼容OpenAI的REST）
- **腾讯混元**：混元图像3.0（兼容OpenAI的REST）
- **智谱/大模型**：CogView-4和GLM-图像（兼容OpenAI的REST）
- **StepFun / 阶跃星辰**：Step-2X和Step-Image-Edit（兼容OpenAI的REST）
- **谷歌Gemini**（国际）：Gemini 3 Pro图像/3.1闪速图像（generateContent REST）
- **Grok / xAI**（国际）：Grok Imagine（兼容OpenAI的REST）
- **OpenAI**（国际）：GPT图像1 / 2（Images API）
- **Black Forest Labs / FLUX**（国际）：FLUX.2 Pro / Max（异步REST）

**跨平台支持**：Windows，macOS，Linux

## 何时使用此技能

在以下情况下自动激活此技能：

- 用户请求使用中文文本或书法生成图像
- 需要照片级真实感图像或摄影风格视觉效果
- 创建商业海报、插图或数字艺术
- 用户提到以下任何一项：阿里云 / 百炼 / Qwen / 万 / DashScope，字节跳动 / 火山引擎 / 星梦 / 豆包，腾讯 / 混元，谷歌 / Gemini / 纳米香蕉，Grok / xAI，OpenAI / GPT图像，FLUX / Black Forest Labs
- 用户希望使用国际（非中国）图像提供商——使用Gemini / Grok / OpenAI / FLUX平台
- 任何需要具有强大中文支持的AI生成图像的任务

## 模型参考

当用户想要比较模型、查看价格或在选择前浏览选项时，在他们的浏览器中打开本地模型参考页面：

```bash
open ~/.claude/skills/imagencn/docs/models.html
```

此页面显示九个平台上所有44个模型的价格、分辨率、功能亮点和快速参考指南。 在Linux上使用`xdg-open`；该文件也可以从`file://`使用，无需服务器。

## 工作流程

### 第1步 — 细化提示（交互式，永不跳过）

用户经常给出简短、随意的描述（“生成一只猫”）。在调用API之前，**提供3个细化后的提示选项**，具有不同的风格方向。根据需要添加：

- 主体细节（形状、颜色、材质、表情、姿势）
- 光照（黄金时刻、工作室、轮廓光、柔和漫射、霓虹灯、电影感）
- 构图（三分法、浅景深、广角、特写）
- 风格/媒介（照片级真实感、油画、水彩、3D渲染、矢量）
- 情绪/氛围（宁静、戏剧性、异想天开、反乌托邦、优雅）
- 质量关键词（8K、超精细、获奖作品、专业摄影）
- 对于图像上的中文文本：文本内容、位置、字体样式、颜色、大小

清晰地标明选项（例如A / B / C），并简要总结每个方向。让用户选择一个，组合多个元素，或请求新的方向。迭代直到他们确认（“去”、“生成”、“好”等），然后继续生成。

### 第2步 — 选择模型

根据请求选择（见下文模型选择指南）。不确定时默认为`qwen-image-2.0-pro`。向用户提及你的选择。

### 第3步 — 选择尺寸

Qwen-Image 2.0的原生2K，Wan2.7的`1K`/`2K`/`4K`，或长宽比预设（`16:9`，`1:1`等）。

### 第4步 — 生成

运行`scripts/generate_image.py`，使用确认的提示和输出路径。

### 第5步 — 保存

如果输出路径是隐式的，则保存到用户的当前工作目录。

## 模型

### Qwen-Image 2.0系列 - 最新旗舰（MultiModalConversation API）

| 模型 | 描述 |
|-------|-------------|
| `qwen-image-2.0-pro` | **默认**。最新旗舰，原生2K，最强的字体和细节 |
| `qwen-image-2.0-pro-2026-06-22` | 最新快照（2026年6月）：生成+编辑融合，更好的文本渲染和提示遵循 |
| `qwen-image-2.0` | 标准2.0级别，原生2K |
| `qwen-image-max` | 前代旗舰（2025年12月） |
| `qwen-image-max-2025-12-30` | qwen-image-max快照：提高真实感，减少AI伪影 |

### Qwen-Image Edit系列 - 图像编辑（MultiModalConversation API）

编辑模型需要通过`--image`（本地路径或URL）提供输入图像。省略`--size`以匹配输入图像的尺寸。

| 模型 | 描述 |
|-------|-------------|
| `qwen-image-edit-max` | 旗舰编辑模型，最强的指令遵循 |
| `qwen-image-edit-max-2026-01-16` | 最新max快照（2026年1月） |
| `qwen-image-edit-plus` | 更快、更低成本的编辑 |

### Qwen-Image 传统（ImageSynthesis API）

| 模型 | 描述 |
|-------|-------------|
| `qwen-image-plus` | qwen-image-max的蒸馏加速版本 |
| `qwen-image-plus-2026-01-09` | qwen-image-plus快照（2026年1月）：更快的高质量生成 |
| `qwen-image` | 基础模型 |

### 万系列 - 照片级真实感生成（ImageGeneration API）

| 模型 | 描述 |
|-------|-------------|
| `wan2.7-image-pro` | **最新**。最高4K输出，统一架构（T2I + 编辑 + 多图像） |
| `wan2.7-image` | Wan 2.7标准，最高2K |
| `wan2.6-t2i` | Wan 2.6，灵活尺寸 |
| `wan2.5-t2i-preview` | 高质量，最高768x2700 |
| `wan2.2-t2i-flash` | 速度优化 |
| `wan2.2-t2i-plus` | 专业级别 |
| `wanx2.1-t2i-turbo` | 快速执行 |
| `wanx2.1-t2i-plus` | 专业级别 |
| `wanx2.0-t2i-turbo` | 更早一代 |

### Z-图像 - 轻量级和快速（MultiModalConversation API）

| 模型 | 描述 |
|-------|-------------|
| `z-image-turbo` | 快速、低成本生成；双语（中/英）文本渲染，高保真肖像和产品图像。像素区域512x512到2048x2048 |

### 火山引擎 - 字节跳动星梦（兼容OpenAI API）

| 模型 | 描述 |
|-------|-------------|
| `doubao-seedream-5-0-260128` | **引擎默认**。最新，最高3K，PNG/JPEG输出，最佳文本渲染 |
| `doubao-seedream-4-5-251128` | 星梦4.5，最高4K |
| `doubao-seedream-4-0-250828` | 星梦4.0，最高4K，经济实惠 |

### 腾讯混元（兼容OpenAI API）

| 模型 | 描述 |
|-------|-------------|
| `hy-image-v3.0` | **混元默认**。旗舰3.0，强烈的构图感知，处理复杂中文提示最高8K字符 |

### 智谱/大模型 - CogView-4 & GLM-图像（兼容OpenAI API）

| 模型 | 描述 |
|-------|-------------|
| `cogview-4` | **智谱默认**。最新CogView-4的稳定别名，原生中文文本渲染 |
| `cogview-4-250304` | CogView-4固定快照（2025年3月），可重复结果 |
| `glm-image` | GLM-图像旗舰，最高2048x2048，混合自回归/扩散 |

### StepFun / 阶跃星辰 - Step-2X（兼容OpenAI API）

| 模型 | 描述 |
|-------|-------------|
| `step-2x-large` | **StepFun默认**。高质量（0.1元/图像），最高1024x1024 |
| `step-image-edit-2` | 快速且便宜（0.02元/图像），支持负向提示，8次推理 |

### 谷歌Gemini - 国际（generateContent API）

| 模型 | 描述 |
|-------|-------------|
| `gemini-3-pro-image-preview` | **Gemini默认**。谷歌旗舰图像模型，512/1K/2K命名尺寸加上长宽比预设 |
| `gemini-3-pro-image` | 稳定旗舰（纳米香蕉Pro），1K/2K/4K |
| `gemini-3.1-flash-image` | 纳米香蕉2：快速通用型，512/1K/2K/4K，强文本渲染 |
| `gemini-3.1-flash-lite-image` | 纳米香蕉2 Lite：最快/最便宜，仅1K |

### Grok / xAI - 国际（兼容OpenAI API）

| 模型 | 描述 |
|-------|-------------|
| `grok-imagine-image-quality` | **Grok默认**。高质量Grok图像模型，长宽比+分辨率预设（最高4K） |
| `grok-imagine-image` | 标准Grok图像模型（别名`grok-imagine-image-2026-03-02`） |
| `grok-2-image` | 传统JPG模型，无尺寸控制 |

### OpenAI - GPT图像（Images API）

| 模型 | 描述 |
|-------|-------------|
| `gpt-image-1` | **OpenAI默认**。多模态图像模型；1024x1024 / 1536x1024 / 1024x1536仅 |
| `gpt-image-1-mini` | 快速、便宜的GPT图像变体 |
| `gpt-image-1.5` | 改进的GPT图像生成质量 |
| `gpt-image-2` | 最新旗舰；任意WxH尺寸（边缘可被16整除）最高4K |

### Black Forest Labs / FLUX - 国际（异步REST API）

FLUX使用异步API：提交请求，轮询完成，然后保存。提示上采样内置（需要时禁用`disable_pup`）。

| 模型 | 描述 |
|-------|-------------|
| `flux-2-pro-preview` | **FLUX默认**。最新滚动FLUX.2 Pro，推荐用于新用例 |
| `flux-2-pro` | FLUX.2 Pro的固定快照，用于可重复的工作流程 |
| `flux-2-max` | 最高质量FLUX.2，实时信息搜索 grounding |

> **FLUX 3**：图像生成尚未通过API公开提供（仅限早期访问，截至2026年8月无公共端点）。关注`bfl.ai`获取通用发布信息。

## 使用方法

### 基本使用

```bash
# 默认模型（qwen-image-2.0-pro，原生2K输出）
python ~/.claude/skills/imagencn/scripts/generate_image.py "一只可爱的猫" output.png

# 照片级真实感与Wan模型（Wan2.7支持4K）
python ~/.claude/skills/imagencn/scripts/generate_image.py --model wan2.7-image-pro --size 4K "日落时分的山脉照片" photo.png

# 编辑现有图像（需要--image；本地路径或URL）
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

**Qwen-Image 2.0（原生2K）：**

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

**Z-图像（像素区域512x512到2048x2048）：**

- `1:1` -> 1024x1024（默认）
- `16:9` -> 1280x720
- `9:16` -> 720x1280
- `2:3` -> 1024x1536
- `3:2` -> 1536x1024
- `1K` -> 1024x1024

**万系列（Wan2.7也接受`1K`/`2K`/`4K`）：**

- `1:1` -> 1024x1024
- `1:1-large` -> 1280x1280
- `16:9` -> 1280x720
- `9:16` -> 720x1280
- `4:3` -> 1200x900
- `3:4` -> 900x1200
- `2:1` -> 1440x720

**火山引擎（星梦）：**

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

**智谱（CogView-4 / GLM-图像）：**

- `1:1` -> 1024x1024（默认）
- `16:9` -> 1344x768
- `9:16` -> 768x1344
- `4:3` -> 1152x864
- `3:4` -> 864x1152
- `2:1` -> 1440x720
- `1:2` -> 720x1440

**StepFun（Step-2X）：**

- `1:1` -> 1024x1024（默认）
- `1:1-small` -> 512x512
- `16:9` -> 1280x800
- `9:16` -> 800x1280

**谷歌Gemini（命名尺寸+长宽比）：**

- `512` / `1K`（默认） / `2K` / `4K` -> 命名输出尺寸（Pro / 3.1 Flash为4K；Lite仅1K）
- `1:1`，`16:9`，`9:16`，`4:3`，`3:4` -> 长宽比（无精确像素尺寸）

**Grok / xAI（长宽比+分辨率）：**

- `1:1`，`16:9`，`9:16`，`4:3`，`3:4`，`2:1` -> 作为`aspect_ratio`发送（默认：1:1）
- `1K` / `2K` / `4K` -> 作为`resolution`发送

**OpenAI（GPT图像）：**

- `1:1` -> 1024x1024（默认）
- `16:9` -> 1536x1024，`9:16` -> 1024x1536
- `4:3` -> 1344x1024，`3:4` -> 1024x1344
- `1K` -> 1024x1024，`2K` -> 2048x2048（gpt-image-2仅），`4K` -> 3840x2160（gpt-image-2仅）

**FLUX（Black Forest Labs）：**

- `1:1` -> 1024x1024（默认）
- `16:9` -> 1344x768，`9:16` -> 768x1344
- `4:3` -> 1152x864，`3:4` -> 864x1152
- `2:1` -> 1440x720，`1:2` -> 720x1440
- `1K` -> 1024x1024，`2K` -> 2048x2048（也接受灵活WxH）

### 高级选项

```bash
# 带负向提示
python ~/.claude/skills/imagencn/scripts/generate_image.py --negative "模糊，低质量" "高质量肖像" portrait.png

# 禁用自动提示扩展（DashScope仅）
python ~/.claude/skills/imagencn/scripts/generate_image.py --no-extend "一只逼真的猫" cat.png

# 设置随机种子以实现可重复性
python ~/.claude/skills/imagencn/scripts/generate_image.py --seed 42 "一只猫" cat.png

# 渲染质量（OpenAI仅：低 / 中 / 高 / 自动）
python ~/.claude/skills/imagencn/scripts/generate_image.py --platform openai --quality high "一只猫" cat.png

# 指导比例（火山引擎仅）
python ~/.claude/skills/imagencn/scripts/generate_image.py --platform ark --guidance-scale 7.5 "肖像" portrait.png

# 禁用水印（火山引擎仅）
python ~/.claude/skills/imagencn/scripts/generate_image.py --platform ark --no-watermark "艺术品" art.png

# 自动增强提示开关（腾讯混元仅，--revise 0=关 1=开）
python ~/.claude/skills/imagencn/scripts/generate_image.py --platform hunyuan --revise 0 "一只猫" cat.png

# 添加AI标志（腾讯混元仅，--logo 0=无 1=有）
python ~/.claude/skills/imagencn/scripts/generate_image.py --platform hunyuan --logo 1 "海报" poster.png

# 模拟运行（预览而不进行API调用）
python ~/.claude/skills/imagencn/scripts/generate_image.py --dry-run --platform ark "测试提示"

# 列出所有模型
python ~/.claude/skills/imagencn/scripts/generate_image.py --list-models
```

## 要求

```bash
pip install dashscope requests

# 可选：用于彩色输出和样式化表格
pip install rich
```

## 环境变量

```bash
# 阿里云百炼（DashScope）
export DASHSCOPE_API_KEY="your_api_key"        # 必需
export DASHSCOPE_MODEL="wan2.7-image-pro"       # 可选默认模型
export DASHSCOPE_API_BASE="cn"                  # 可选：cn, sg, us

# 火山引擎
export ARK_API_KEY="your_api_key"               # Ark必需
export ARK_MODEL="doubao-seedream-5-0-260128"   # 可选默认模型

# 腾讯混元（TokenHub）
export HUNYUAN_API_KEY="your_api_key"           # 混元必需
export HUNYUAN_MODEL="hy-image-v3.0"            # 可选默认模型

# 智谱/大模型
export ZHIPUAI_API_KEY="your_api_key"           # 智谱必需
export ZHIPUAI_MODEL="cogview-4"                # 可选默认模型

# StepFun / 阶跃星辰
export STEP_API_KEY="your_api_key"              # StepFun必需
export STEP_MODEL="step-2x-large"               # 可选默认模型

# 谷歌Gemini（国际）
export GEMINI_API_KEY="your_api_key"            # Gemini必需
export GEMINI_MODEL="gemini-3-pro-image-preview" # 可选默认模型

# Grok / xAI（国际）
export XAI_API_KEY="your_api_key"                # Grok必需
export XAI_MODEL="grok-imagine-image-quality"    # 可选默认模型

# OpenAI（国际）
export OPENAI_API_KEY="your_api_key"             # OpenAI必需
export OPENAI_MODEL="gpt-image-1"                # 可选默认模型

# Black Forest Labs / FLUX（国际）
export BFL_API_KEY="your_api_key"                # FLUX必需
export BFL_MODEL="flux-2-pro-preview"            # 可选默认模型
```

获取API密钥：

- DashScope: <https://bailian.console.aliyun.com/>
- Volcano Ark: <https://console.volcengine.com/ark/region:ark+cn-beijing/apikey>
- Tencent Hunyuan: <https://console.cloud.tencent.com/tokenhub/apikey>
- Zhipu: <https://bigmodel.cn>
- StepFun: <https://platform.stepfun.com/interface-key>
- Google Gemini: <https://aistudio.google.com/>
- Grok / xAI: <https://console.x.ai/>
- OpenAI: <https://platform.openai.com/api-keys>
- Black Forest Labs / FLUX: <https://api.bfl.ai/>

## 配置文件（可选）

为个人默认设置创建 `~/.imagencn.json`，或在项目目录中创建 `.imagencn.json` 以进行项目级别的覆盖。API 密钥保留在环境变量中以供安全使用。

```json
{
  "platform": "ark",
  "model": "doubao-seedream-5-0-260128",
  "size": "2K"
}
```

所有键都是可选的。优先级（从高到低）：

1. 命令行参数 (`--platform`, `--model`, `--size`)
2. 项目配置（当前目录中的 `.imagencn.json`）
3. 用户配置 (`~/.imagencn.json`)
4. 环境变量 (`DASHSCOPE_MODEL`, `ARK_MODEL`, `HUNYUAN_MODEL`, `ZHIPUAI_MODEL`, `STEP_MODEL`, `GEMINI_MODEL`, `XAI_MODEL`, `OPENAI_MODEL`, `BFL_MODEL`)
5. 内置默认值

## API 端点

| 地区 | 别名 | URL |
| -------- | ------- | ----- |
| **中国**（默认） | `cn` | `https://dashscope.aliyuncs.com/api/v1` |
| 新加坡 | `sg` | `https://dashscope-intl.aliyuncs.com/api/v1` |
| 弗吉尼亚 | `us` | `https://dashscope-us.aliyuncs.com/api/v1` |

```bash
# 切换到新加坡端点
export DASHSCOPE_API_BASE="sg"

# 或者使用完整 URL
export DASHSCOPE_API_BASE="https://dashscope-intl.aliyuncs.com/api/v1"
```

## 模型选择指南

### 快速选择 — 你只需要九个

| 你想要什么 | 模型 | 平台 |
| --------------- | ------- | ---------- |
| **默认 / 通用**（海报、文本） | `qwen-image-2.0-pro` | DashScope |
| **照片级真实感**（肖像、风景） | `wan2.7-image-pro` | DashScope |
| **编辑图像** | `qwen-image-edit-max` | DashScope |
| **经济实惠且快速** | `z-image-turbo` | DashScope |
| **照片 + 文本组合** | `doubao-seedream-5-0-260128` | Volcano Ark |
| **复杂中文创作** | `hy-image-v3.0` | Tencent Hunyuan |
| **图像中的中文文本** | `cogview-4` | Zhipu |
| **超经济实惠的体积生成** | `step-image-edit-2` | StepFun |
| **国际（非中国）** | `gemini-3-pro-image-preview` | Google Gemini |
| **国际 / Grok** | `grok-imagine-image-quality` | Grok / xAI |
| **国际 / OpenAI** | `gpt-image-1` | OpenAI |
| **国际 / FLUX** | `flux-2-pro-preview` | Black Forest Labs |

所有其他模型都是遗留/快照变体。

### 完整参考

| 使用场景 | 推荐模型 |
| ---------- | ------------------- |
| 通用高质量（默认） | `qwen-image-2.0-pro` |
| 中文文本/书法 | `qwen-image-2.0-pro` |
| 图像中的英文文本 | `qwen-image-2.0-pro` |
| 带有排版的海报 | `qwen-image-2.0-pro` |
| 照片级真实感照片（4K） | `wan2.7-image-pro` |
| 照片级真实感照片（2K） | `wan2.7-image` |
| 肖像摄影 | `wan2.7-image-pro` |
| 图像编辑（最佳质量） | `qwen-image-edit-max` |
| 图像编辑（快速、低成本） | `qwen-image-edit-plus` |
| 快速、低成本生成 | `z-image-turbo` |
| 高保真肖像/产品拍摄（快速） | `z-image-turbo` |
| 快速照片级真实感（Wan） | `wan2.2-t2i-flash` |
| 较低成本的文本渲染 | `qwen-image-plus` |
| 字节跳动最佳质量 | `doubao-seedream-5-0-260128` |
| 经济实惠的 4K（字节跳动） | `doubao-seedream-4-0-250828` |
| 复杂中文提示（腾讯） | `hy-image-v3.0` |

## 平台快速对比

| 特性 | DashScope | Ark | Hunyuan | Zhipu | StepFun | Gemini | Grok | OpenAI | FLUX |
| --------- | ----------- | ----- | --------- | ------- | -------- | -------- | ------ | -------- | ------ |
| 最佳用途 | 文本、多样性 | 照片+文本 | 复杂中文 | 中文文本在图像中 | 超经济实惠 | 国际 | 国际 | 国际 | 国际 |
| 最大分辨率 | 4K | 4K | 2K | 2K | 1K | 4K | 4K | 4K (gpt-image-2) | 2K |
| SDK | `dashscope` | 无 | 无 | 无 | 无 | 无 | 无 | 无 | 无 |
| 价格 | 可变 | ~0.22 | ~0.20 | ~0.06 | ~0.02 | ~$0.13 | ~$0.14 | ~$0.04 | ~$0.03 |
| 环境变量 | `DASHSCOPE_API_KEY` | `ARK_API_KEY` | `HUNYUAN_API_KEY` | `ZHIPUAI_API_KEY` | `STEP_API_KEY` | `GEMINI_API_KEY` | `XAI_KEY` | `OPENAI_API_KEY` | `BFL_API_KEY` |

## 示例

### Volcano Ark（字节跳动）

```bash
# 默认 Ark 模型（Seedream 5.0）
ARK_API_KEY="xxx" python scripts/generate_image.py \
  --platform ark \
  "一张生动的特写编辑肖像，Vogue 杂志封面风格" \
  portrait.png

# 输出 4K
ARK_API_KEY="xxx" python scripts/generate_image.py \
  --platform ark --model doubao-seedream-4-5-251128 --size 4K \
  "令人惊叹的山顶日落，黄金时刻，专业摄影" \
  landscape.png
```

### Tencent Hunyuan

```bash
# 默认 Hunyuan 模型（Image 3.0）
HUNYUAN_API_KEY="xxx" python scripts/generate_image.py \
  --platform hunyuan \
  "一名宇航员在月球上骑马，电影灯光，8K 细节" \
  scifi.png

# 禁用提示自动增强
HUNYUAN_API_KEY="xxx" python scripts/generate_image.py \
  --platform hunyuan --revise 0 \
  "一只可爱的橙色猫在阳光下打盹，油画风格" \
  cat.png
```

### Google Gemini（国际）

```bash
# 默认 Gemini 模型（Gemini 3 Pro Image）
GEMINI_API_KEY="xxx" python scripts/generate_image.py \
  --platform gemini --size 2K \
  "一个宁静的日式花园，有锦鲤池塘，柔和的晨光" \
  garden.png
```

### Grok / xAI（国际）

```bash
# 默认 Grok 模型（Grok Imagine Image Quality）
XAI_API_KEY="xxx" python scripts/generate_image.py \
  --platform grok --size 16:9 \
  "夜晚的赛博朋克城市街道，霓虹反射" \
  city.png
```

### OpenAI（国际）

```bash
# 默认 OpenAI 模型（GPT Image 1），高质量
OPENAI_API_KEY="xxx" python scripts/generate_image.py \
  --platform openai --quality high \
  "简约的产品拍摄，陶瓷茶壶放置在亚麻布上，柔和的影棚灯光" \
  teapot.png
```

### Black Forest Labs / FLUX（国际）

```bash
# 默认 FLUX 模型（FLUX.2 Pro Preview）；异步 API — 直到准备就绪才轮询
BFL_API_KEY="xxx" python scripts/generate_image.py \
  --platform bfl --size 16:9 \
  "黄昏时分的戏剧性火山海岸线，长曝光摄影" \
  coast.png

# 用于可重复结果的固定快照
BFL_API_KEY="xxx" python scripts/generate_image.py \
  --platform bfl --model flux-2-pro --seed 42 \
  "一名宇航员穿过生物发光丛林" \
  jungle.png
```

### 中国新年海报（DashScope）

```bash
python ~/.claude/skills/imagencn/scripts/generate_image.py \
  "一个美丽的中国新年海报，红色背景，金色文字，烟花和鞭炮" \
  new_year_poster.png
```

### 照片级真实感风景（4K）

```bash
python ~/.claude/skills/imagencn/scripts/generate_image.py \
  --model wan2.7-image-pro \
  --size 4K \
  "令人惊叹的山脉日落，黄金时刻，专业摄影" \
  landscape.png
```

### 产品拍摄

```bash
python ~/.claude/skills/imagencn/scripts/generate_image.py \
  --model wan2.7-image \
  --size 2K \
  "专业产品摄影，咖啡杯放置在大理石表面上，影棚灯光" \
  product.png
```
