# AI 图像生成

通过 [RunComfy](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation) CLI 生成和编辑图像，支持 11 款以上 AI 模型 — 文本到图像和图像到图像，单一认证，单一命令。该技能根据用户的意图选择合适的模型，并提供文档化的提示模式 + 每个 `runcomfy run` 调用的精确指令。

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation) · [浏览所有模型](https://www.runcomfy.com/models?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation) · [CLI 文档](https://docs.runcomfy.com/cli/introduction?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation)

## 由 RunComfy CLI 驱动

```bash
# 1. 安装（任选其一 — 详细信息请参阅 runcomfy-cli 技能）
npm i -g @runcomfy/cli                              # 全局安装
npx -y @runcomfy/cli --version                      # 无需安装

# 2. 登录（交互式 — 打开浏览器）
runcomfy login
# 或在 CI / 容器中：
export RUNCOMFY_TOKEN=<从 runcomfy.com/profile 获取的 token>

# 3. 生成
runcomfy run <vendor>/<model>/<endpoint> \
  --input '{"prompt": "..."}' \
  --output-dir ./out
```

CLI 文档：[安装](https://docs.runcomfy.com/cli/install?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation) · [快速入门](https://docs.runcomfy.com/cli/quickstart?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation) · [命令](https://docs.runcomfy.com/cli/commands?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation) · [认证](https://docs.runcomfy.com/cli/auth?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation) · [故障排除](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation)

## 安装此技能

```bash
npx skills add agentspace-so/runcomfy-agent-skills --skill ai-image-generation -g
```

---

## 根据用户意图选择合适的模型

### 文本到图像 (t2i) — 最新优先

**FLUX 2 Klein 9B** — `blackforestlabs/flux-2-klein/9b/text-to-image` *(默认)*
> 步骤蒸馏，4–25 步，原生多参考条件，强大的照片真实 + 插画全能。
> 选择原因：意图不明确，快速迭代，多参考风格，通用用途。
> 避免原因：图像中的文本 — 使用 **GPT Image 2**。

**FLUX 2 Klein 4B** — `blackforestlabs/flux-2-klein/4b/text-to-image`
> Klein 9B 的亚秒级变体，相同的领域集。
> 选择原因：故事板，情绪板，快速批量构思。
> 避免原因：最终交付 — 与 9B 相比质量略有下降。

**FLUX 2 Pro / Dev / Flash / Turbo / Max** — `blackforestlabs/flux-2/max`，[`flux-2-dev`](https://www.runcomfy.com/models/blackforestlabs/flux-2-dev/text-to-image?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation) ，[`flux-2-flash`](https://www.runcomfy.com/models/blackforestlabs/flux-2-flash?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation) ，[`flux-2-turbo`](https://www.runcomfy.com/models/blackforestlabs/flux-2-turbo?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation)
> FLUX 2 基础的更高保真度层级。电影 + 品牌工作，主角镜头。
> 选择原因：生产光泽，品牌活动。
> 避免原因：亚秒级速度 — 使用 **Klein 4B**。

**Nano Banana Pro** — [`google/nano-banana-pro/text-to-image`](https://www.runcomfy.com/models/google/nano-banana-pro/text-to-image?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation)
> 最高质量的 Nano Banana 层级。基于 Gemini，可选网络搜索以获取现实世界参考（产品，地标）。
> 选择原因：NB 风格指令遵循，更高保真度。
> 避免原因：成本敏感的迭代 — 降至 **Nano Banana 2**。

**Nano Banana 2** — `google/nano-banana-2/text-to-image`
> Flash 层级延迟，可预测的构图，`enable_web_search` 标志用于现实产品 / 现实人物基础。
> 选择原因：快速迭代，4-up 批量，现实世界基础提示。
> 避免原因：长构图指令 — 使用 **GPT Image 2**。

**GPT Image 2** — `openai/gpt-image-2/text-to-image`
> 图像中文本渲染的最佳选择（日语假名，西里尔文，阿拉伯文）。布局精确的指令遵循。
> 选择原因：海报，广告，多行文本，多语言创意，精确文本标题。
> 避免原因：照片真实肖像 — **Seedream 5** 在肤色和光照方面更胜一筹。

**Seedream 5 Lite** — [`bytedance/seedream-5/lite/text-to-image`](https://www.runcomfy.com/models/bytedance/seedream-5/lite/text-to-image?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation)
> 最新字节跳动 Seedream 层级。照片真实肤色，自然光照，强烈的东亚美学。
> 选择原因：照片真实肖像，产品拍摄，时尚 / 生活方式。
> 避免原因：字体精确度 — 使用 **GPT Image 2**。

**Seedream 4-5** — [`bytedance/seedream-4-5/text-to-image`](https://www.runcomfy.com/models/bytedance/seedream-4-5/text-to-image?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation)
> 之前的 Seedream 旗舰，在照片真实方面仍然很强。
> 选择原因：Seedream-5 代际之间的身份稳定批量；更便宜的 Seedream 层级。
> 避免原因：新工作 — 优先选择 **Seedream 5 Lite**。

**Dreamina 4-0** — [`bytedance/dreamina-4-0/text-to-image`](https://www.runcomfy.com/models/bytedance/dreamina-4-0/text-to-image?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation)
> 字节跳动的插画 / 概念艺术倾向，风格化角色。
> 选择原因：概念艺术，插画英雄，绘画式资源。
> 避免原因：照片真实 — 使用 **Seedream**。

**Qwen Image 2512** — [`qwen/qwen-image/qwen-image-2512`](https://www.runcomfy.com/models/qwen/qwen-image/qwen-image-2512?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation)
> 阿里巴巴 Qwen 最新，开放权重，兼容 LoRA (`/lora` 变体)。
> 选择原因：开放权重工作流，与 Qwen 对齐的 LoRA 链。
> 避免原因：封闭权重光泽 — 使用 **FLUX 2** 或 **GPT Image 2**。

**Wan 2-7** — [`wan-ai/wan-2-7/text-to-image`](https://www.runcomfy.com/models/wan-ai/wan-2-7/text-to-image?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation) ，[`wan-ai/wan-2-7/pro/text-to-image`](https://www.runcomfy.com/models/wan-ai/wan-2-7/pro/text-to-image?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation)
> 开放权重，原生与 Wan 2-7 视频模型配对，统一栈工作流。
> 选择原因：Wan 栈管道（图像 + 视频同一品牌），开放权重要求。
> 避免原因：仅图像质量顶级。

**Z-Image Turbo** — [`tongyi-mai/z-image/turbo`](https://www.runcomfy.com/models/tongyi-mai/z-image/turbo?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation)
> 亚秒级开放权重，原生 LoRA `/lora` 变体。
> 选择原因：速度定制开放权重工作流。
> 避免原因：封闭权重光泽。

### 图像到图像 / 编辑 (i2i) — 最新优先

**Nano Banana Pro Edit** — [`google/nano-banana-pro/edit`](https://www.runcomfy.com/models/google/nano-banana-pro/edit?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation)
> 最高质量的 Nano Banana 编辑层级。身份保留，多参考。
> 选择原因：高级 NB 编辑工作，身份锁定变体。
> 避免原因：成本敏感的迭代 — 降至 **Nano Banana 2 Edit**。

**Nano Banana 2 Edit** — `google/nano-banana-2/edit` *(默认 i2i)*
> 每次调用最多 1–20 输入图像，默认保留身份，尊重空间语言（"右上角"，"左侧对象"）。
> 选择原因：默认 i2i，批量身份保留，背景替换，方向性对象移除/添加。
> 避免原因：精确掩码区域 — 使用 [`image-edit`](https://www.skills.sh/agentspace-so/runcomfy-agent-skills/image-edit) 技能（Z-Image Inpaint）。

**GPT Image 2 Edit** — `openai/gpt-image-2/edit`
> 最多 10 个参考图像，多语言图像中文本重写，布局精确的重新定位。
> 选择原因：多语言标题替换，多参考构图，布局重新定位，跨翻译的品牌锁定身份。
> 避免原因：掩码驱动修复 — 使用 [`image-edit`](https://www.skills.sh/agentspace-so/runcomfy-agent-skills/image-edit) 技能。

**Seedream 5 Lite Edit** — [`bytedance/seedream-5/lite/edit`](https://www.runcomfy.com/models/bytedance/seedream-5/lite/edit?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation)
> 最新 Seedream 编辑层级，照片真实保留。
> 选择原因：从 Seedream t2i 开始的照片真实编辑（身份在配对中保持一致）。
> 避免原因：多语言文本重写。

**Seedream 4-5 Edit** — [`bytedance/seedream-4-5/edit`](https://www.runcomfy.com/models/bytedance/seedream-4-5/edit?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation)
> 之前的 Seedream 编辑。
> 选择原因：4-5 代际之间的身份稳定批量。
> 避免原因：新工作 — 优先选择 **Seedream 5 Lite Edit**。

**Dreamina 4-0 Edit** — [`bytedance/dreamina-4-0/edit`](https://www.runcomfy.com/models/bytedance/dreamina-4-0/edit?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation)
> 字节跳动的插画编辑。
> 选择原因：编辑 Dreamina 生成的插画。
> 避免原因：照片真实主题。

**Qwen Image Edit 2511** — [`qwen/qwen-image/qwen-image-edit-2511`](https://www.runcomfy.com/models/qwen/qwen-image/qwen-image-edit-2511?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation)
> 阿里巴巴开放权重编辑。
> 选择原因：开放权重编辑管道。
> 避免原因：封闭权重光泽。

**Wan 2.6 i2i** — [`wan-ai/wan-v2.6/image-to-image`](https://www.runcomfy.com/models/wan-ai/wan-v2.6/image-to-image?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation)
> Wan 生态系统图像到图像。
> 选择原因：Wan 栈集成。
> 避免原因：新工作 — 老一代；优先选择 NB 或 GPT Image 2。

**FLUX Kontext Pro** — `blackforestlabs/flux-1-kontext/pro/edit`
> 单参考单指令，最高的保留保真度（"保留所有内容除了 X"）。
> 选择原因：单图像精确本地编辑（"仅将她的雨伞改为橙色"）。
> 避免原因：批量工作，多参考构图，掩码驱动修复。

> **需要掩码驱动修复，受控的扩展，或完整的编辑处理？** → 使用 [`image-edit`](https://www.skills.sh/agentspace-so/runcomfy-agent-skills/image-edit) 技能。

---

## t2i 路径 1：FLUX 2 Klein — 默认

**模型**: `blackforestlabs/flux-2-klein/9b/text-to-image` (默认), `blackforestlabs/flux-2-klein/4b/text-to-image` (亚秒级)
**目录**: [9B](https://www.runcomfy.com/models/blackforestlabs/flux-2-klein/9b/text-to-image?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation) · [4B](https://www.runcomfy.com/models/blackforestlabs/flux-2-klein/4b/text-to-image?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation)

### 模式 (两种变体)

| 字段 | 类型 | 必填 | 默认 | 备注 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 约 512 个 token；更长会退化。主语优先，陈述式 |
| `steps` | int | 否 | 25 (9B) / 4 (4B) | 步骤蒸馏；4–8 足够用于构思，~25 用于光泽，>25 买不到什么 |
| `width` | int | 否 | 1024 | 512–1536 典型，最大 ~2K 总计。长宽比上限 16:9 |
| `height` | int | 否 | 1024 | 与 width 的长宽比意图匹配 |

在同一个端点上最多支持 **4 个参考图像**，用于风格迁移 / 指导构图。字段名在模型页面文档中记录 [模型页面](https://www.runcomfy.com/models/blackforestlabs/flux-2-klein/9b/text-to-image?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation)。

### 调用

**光泽 / 最终 (9B):**

```bash
runcomfy run blackforestlabs/flux-2-klein/9b/text-to-image \
  --input '{
    "prompt": "一只紫色的小猫坐在覆盖着苔藓的石头上，黄金时刻的边缘光，浅景深，照片真实",
    "steps": 25,
    "width": 1536,
    "height": 864
  }' \
  --output-dir ./out
```

**亚秒级构思 (4B):**

```bash
runcomfy run blackforestlabs/flux-2-klein/4b/text-to-image \
  --input '{"prompt": "一只紫色的小猫在日落时分，照片真实"}' \
  --output-dir ./out
```

### 提示技巧

- **主语优先，场景其次，修饰语最后。** "一只紫色的小猫 … 在苔藓石头上 … 黄金时刻，浅景深。"
- **步骤策略**: 4–8 用于构思，~25 用于光泽。不要超过 28 — 收益递减。
- **9B vs 4B**: 默认 9B；仅在需要亚秒级批量构思时降至 4B。
- **多参考**: 1–4 个参考 URL；在提示中描述角色 (`"主体来自 ref 1，调色板来自 ref 2"`).

---

## t2i 路径 2：GPT Image 2 — 字体 & 图像中文本

**模型**: `openai/gpt-image-2/text-to-image`
**目录**: [runcomfy.com/models/openai/gpt-image-2](https://www.runcomfy.com/models/openai/gpt-image-2/text-to-image?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation)

### 模式

| 字段 | 类型 | 必填 | 默认 | 备注 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 精确引用图像中文本，用 `"…"` |
| `size` | enum | 否 | `1024_1024` | `1024_1024` (1:1), `1024_1536` (2:3 竖版), `1536_1024` (3:2 横版) — **仅这三个** |

### 调用

**标志 / 海报，标题精确读取 X**:

```bash
runcomfy run openai/gpt-image-2/text-to-image \
  --input '{
    "prompt": "极简产品海报。居中粗体标题精确读取 \"AURORA — Spring 2026\"，使用干净的白色无衬线字体，深海军蓝背景。标题下方有一行小字，使用等宽字体读取 \"runs on water\"。3:2 布局。",
    "size": "1536_1024"
  }' \
  --output-dir ./out
```

**多语言**:

```bash
runcomfy run openai/gpt-image-2/text-to-image \
  --input '{
    "prompt": "日本杂志封面。垂直标题精确读取 \"今日のおすすめ\"，使用粗体日语假名，右边缘对齐，照片真实的女性肖像。",
    "size": "1024_1536"
  }' \
  --output-dir ./out
```

### 提示技巧

- **精确引用图像中文本。** `"标志读取精确为 'CLOSED'"` — 如果不添加引号，模型会意译。
- **为非拉丁文本命名脚本**: `"日语假名"`, `"西里尔文"`, `"阿拉伯文从右到左"`. 如果不这样，它会回退到罗马化。
- **布局语言得到尊重**: `"左上角"`, `"居中"`, `"两行堆叠"`, `"基线对齐"`.
- **只有 3 个尺寸。** 不要传递任意宽度。

---

## t2i 路径 3：Nano Banana 2 — 速度迭代

**模型**: `google/nano-banana-2/text-to-image`
**目录**: [runcomfy.com/models/google/nano-banana-2](https://www.runcomfy.com/models/google/nano-banana-2?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation) · [`nano-banana` 收藏夹](https://www.runcomfy.com/models/collections/nano-banana?utm_source=skills.sh&utm_medium=skill&utm_campaign=ai-image-generation)

### 模式

| 字段 | 类型 | 必填 | 默认 | 备注 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 主语优先描述 |
| `num_images` | int | 否 | 1 | 1–4. 使用 4 进行构思轮次 |
| `seed` | int | 否 | 0 | 重复以实现可重现性 |
| `aspect_ratio` | enum | 否 | `auto` | `auto`, `21:9`, `16:9`, `3:2`, `4:3`, `5:4`, `1:1`, `4:5`, `3:4`, `2:3`, `9:16` |
| `resolution` | enum | 否 | `1K` | `0.5K` (草稿), `1K` (默认), `2K` (最终), `4K` (最大) |
| `output_format` | enum | 否 | `png` | `png`, `jpeg`, `webp` |
| `safety_tolerance` | int | 否 | 4 | 1 (严格) – 6 (宽松) |
| `enable_web_search` | bool | 否 | false | 添加网络基础 (额外成本 + 延迟) |

### 调用

**默认草稿**:

```bash
runcomfy run google/nano-banana-2/text-to-image \
  --input '{"prompt": "一个咖啡杯放在大理石台面上，俯视角度，温暖的早晨光线"}' \
  --output-dir ./out
```

**4-up 批量用于构思**:

```bash
runcomfy run google/nano-banana-2/text-to-image \
  --input '{
    "prompt": "三个产品照片，一个陶瓷咖啡杯放在大理石台面上，温暖的早晨光线，俯视角度，极简风格",
    "num_images": 4,
    "aspect_ratio": "1:1",
    "resolution": "0.5K"
  }' \
  --output-dir ./out
```

### 提示技巧

- **主语优先，陈述式。** "一个咖啡杯放在大理石上" 比 "生成一个创意咖啡杯镜头" 更好。
- **`enable_web_search: true`** 当提示中命名真实产品，地点或人物，其外观必须与现实匹配（标志，地标）。
- **降至 `0.5K` 进行构思，仅在最终时跳至 `2K`+ — `4K` ~16× `0.5K` 的成本。
