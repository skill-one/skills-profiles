# Image Edit — RunComfy Pro Pack

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=image-edit) · [Nano Banana Edit](https://www.runcomfy.com/models/google/nano-banana-2/edit?utm_source=skills.sh&utm_medium=skill&utm_campaign=image-edit) · [GPT Image 2 Edit](https://www.runcomfy.com/models/openai/gpt-image-2/edit?utm_source=skills.sh&utm_medium=skill&utm_campaign=image-edit) · [Flux Konfig Pro](https://www.runcomfy.com/models/blackforestlabs/flux-1-konfig-pro/image-to-image?utm_source=skills.sh&utm_medium=skill&utm_campaign=image-edit) · [Z-Image Inpaint](https://www.runcomfy.com/models/tongyi-mai/z-image/turbo/inpainting?utm_source=skills.sh&utm_medium=skill&utm_campaign=image-edit) · [GitHub](https://github.com/agentspace-so/runcomfy-skills/tree/main/image-edit)

**图像编辑，意图路由。** 本技能不锁定单一模型——它会根据用户实际需求，从 RunComfy 目录中选择合适的编辑模型：批量保留主体身份、多语言文本重写、单次精准编辑，或基于蒙版区域替换。

```bash
npx skills add agentspace-so/runcomfy-skills --skill image-edit -g
```

## 为用户的意图选择合适的模型

| 用户意图 | 模型 | 原因 |
|---|---|---|
| 批量编辑 1–20 张图片并保持一致性（SKU 画廊、A/B 变体） | **Nano Banana Edit** | 单次调用最多 20 张输入图片；锁定比例与分辨率以保证系列统一 |
| 更换背景，保留主体身份 | **Nano Banana Edit** | 在“保持 X 不变”的提示下，主体身份保留能力强 |
| 使用空间语言（“左侧物体”、“右上角”）进行本地化对象去除/添加 | **Nano Banana Edit** | 遵循方向性空间范围 |
| 多语言/非拉丁语种图片内文本重写（日语假名、西里尔字母、阿拉伯语） | **GPT Image 2 Edit** | 多语言排版方面同类最强 |
| 多参考构图（主体来自 img1，场景来自 img2，配色来自 img3） | **GPT Image 2 Edit** | 编号参考准确引导提示线索 |
| 布局精准的重新定位（“将标题从右上移至底部居中”） | **GPT Image 2 Edit** | 在布局层面遵循方向性语言 |
| 翻译版标题变体的身份保留 | **GPT Image 2 Edit** | 同一源素材 → 多种语言变体，身份稳定 |
| 单次精准局部编辑（“她现在拿着一把橙色雨伞”） | **Flux Konfig Pro** | 单参考、单指令，高保真保留 |
| 蒙版驱动的物体去除（电线、水印、干扰物） | **Z-Image Turbo Inpaint** | 需蒙版，强度可调，边缘一致 |
| 蒙版驱动的区域替换（带蒙版完整更换背景） | **Z-Image Turbo Inpaint** | 高强度 + 清晰蒙版 = 干净替换 |
| 若未指定（默认） | **Nano Banana Edit** | 灵活性最强，支持单次与批量 |

Agent 读取该表，对用户的意图进行分类，并选择下方的对应小节。

## 前置条件

1. **RunComfy CLI** — `npm i -g @runcomfy/cli`
2. **RunComfy 账号** — `runcomfy login`。
3. **CI / 容器** — 设置环境变量 `RUNCOMFY_TOKEN= <token>`。

---

## 路线 1：Nano Banana Edit — 通用编辑与批量的默认选择

**Model**: `google/nano-banana-2/edit`

### Schema

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 以保留目标开头，以修改内容结尾。 |
| `image_urls` | array | 是 | — | **1–20** 可公开获取的 HTTPS URL。 |
| `number_of_images` | int | 否 | 1 | 每次调用 1–4 个输出。 |
| `aspect_ratio` | enum | 否 | `auto` | `auto` 跟随输入；批量时需锁定以保证一致性。 |
| `resolution` | enum | 否 | `1K` | `0.5K` / `1K` / `2K` / `4K`。 |
| `output_format` | enum | 否 | `png` | `png` / `jpeg` / `webp`。 |
| `seed` | int | 否 | — | 可复现性。 |
| `enable_web_search` | bool | 否 | false | 基于网络内容的编辑（增加延迟）。 |

### 调用方式

```bash
runcomfy run google/nano-banana-2/edit \
  --input '{
    "prompt": "Keep the subject identity, pose, and clothing unchanged. Convert the background into a rainy neon cyberpunk street.",
    "image_urls": ["https://.../portrait.jpg"]
  }' \
  --output-dir <absolute/path>
```

**批量（锁定比例与分辨率）：**

```bash
runcomfy run google/nano-banana-2/edit \
  --input '{
    "prompt": "Replace the watermark in the bottom-right with the text \"AURA\" in clean white sans-serif. Keep everything else exactly as in the input.",
    "image_urls": ["https://.../sku-1.jpg", "https://.../sku-2.jpg", "https://.../sku-3.jpg"],
    "aspect_ratio": "1:1",
    "resolution": "1K"
  }' \
  --output-dir <absolute/path>
```

### 提示词技巧

- **以保留为先**：`"Keep [主体身份 / 姿态 / 品牌 / 构图] unchanged."` 然后说明修改内容。
- **空间范围**："背景区域"、"左侧物体"、"右上象限"——具体位置会被遵循。
- **批量一致性**：跨批次锁定 `aspect_ratio` 和 `resolution`。
- **小步迭代**：将复合编辑拆分为多个较短的步骤。

---

## 路线 2：GPT Image 2 Edit — 多语言文本与多参考构图

**Model**: `openai/gpt-image-2/edit`

### Schema

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 编辑指令；以保留为先。 |
| `images` | string[] | 是 | — | **最多 10 个** HTTPS URL。第一个为主图，其余为辅助图。 |
| `size` | enum | 否 | `auto` | `auto`、`1024_1024`、`1024_1536`、`1536_1024`。**仅限这些取值。** |

### 调用方式

**多语言文本重写：**

```bash
runcomfy run openai/gpt-image-2/edit \
  --input '{
    "prompt": "Keep the photograph, layout, and brand mark exactly as in the input. Replace only the in-image headline. The new headline reads \"今日のおすすめ\" in bold Japanese kana, same position and font weight.",
    "images": ["https://.../poster-en.jpg"]
  }' \
  --output-dir <absolute/path>
```

**多参考构图：**

```bash
runcomfy run openai/gpt-image-2/edit \
  --input '{
    "prompt": "Compose subject from image 1 into the room from image 2. Match the lighting and color palette of image 2. Keep image 1 subject identity unchanged.",
    "images": ["https://.../subject.jpg", "https://.../room.jpg"]
  }' \
  --output-dir <absolute/path>
```

### 提示词技巧

- **准确引用图片内文本。** 为非拉丁语种命名脚本：`"Japanese kana"`（日语假名）、`"Cyrillic"`（西里尔字母）、`"Arabic right-to-left"`（阿拉伯语从右到左）。
- **编号多参考**：`"主体来自图片 1，灯光来自图片 2"`。
- **方向性布局语言**：`"将标题从右上移至底部居中"`、`"将底部右侧的水印替换掉"`。
- **`size: "auto"`** 会保留输入比例——除非编辑改变了构图，否则推荐使用该取值。

---

## 路线 3：Flux Konfig Pro — 单次精准局部编辑

**Model**: `blackforestlabs/flux-1-konfig/pro/edit`

### Schema（精简）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `prompt` | string | 是 | 一条明确的编辑指令。 |
| `image` | string | 是 | **单张**源图片 URL。 |
| `aspect_ratio` | enum | 否 | 从支持的 W:H 取值中选择。 |
| `seed` | int | 否 | 可复现性。 |

仅支持单图，不支持数组。多图场景请使用路线 1（Nano Banana Edit）。

### 调用方式

```bash
runcomfy run blackforestlabs/flux-1-konfig/pro/edit \
  --input '{
    "prompt": "Keep the person'\''s face, pose, and clothing unchanged. Add an orange umbrella in her left hand and a slight smile.",
    "image": "https://.../portrait.jpg"
  }' \
  --output-dir <absolute/path>
```

### 提示词技巧

- **一条明确的指令。** `"她现在拿着一把橙色雨伞，并微微微笑"`——祈使语气，只包含单一修改。
- **以保留为先。** 以 `"Keep [保持不变的内容]"` 开头，再说明修改内容。
- **小步迭代。** 复合编辑在单次操作中容易偏差；需拆分为连续的步骤执行。

---

## 路线 4：Z-Image Turbo Inpaint — 基于蒙版的精准区域编辑

**Model**: `tongyi-mai/z-image/turbo/inpainting`

### Schema

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `prompt` | string | 是 | 需要填充/替换的内容；对蒙版外周围区域的保留约束。 |
| `image` | string | 是 | 源图片 URL。 |
| `mask_image` | string | 是 | **灰度蒙版 URL**（白色 = 需要修复，黑色 = 保留）。 |
| `strength` | float | 否 | 0.3–0.6 修饰/修复，0.7–1.0 完全替换。 |
| `control_scale` | float | 否 | 通常为 0.6–0.9。 |
| `aspect_ratio` | enum | 否 | W:H 输出比例。 |
| `seed` | int | 否 | 可复现性。 |

### 调用方式

**物体去除（低强度）：**

```bash
runcomfy run tongyi-mai/z-image/turbo/inpainting \
  --input '{
    "prompt": "Remove overhead cables; preserve rooflines and sky gradient; thin clean sky.",
    "image": "https://.../street.jpg",
    "mask_image": "https://.../cables-mask.png",
    "strength": 0.5,
    "control_scale": 0.8
  }' \
  --output-dir <absolute/path>
```

**区域替换（高强度）：**

```bash
runcomfy run tongyi-mai/z-image/turbo/inpainting \
  --input '{
    "prompt": "Replace busy backdrop with smooth light gray studio paper; mask background only.",
    "image": "https://.../product.jpg",
    "mask_image": "https://.../bg-mask.png",
    "strength": 0.9
  }' \
  --output-dir <absolute/path>
```

### 提示词技巧

- **必须提供蒙版 URL**——灰度蒙版，白色 = 需要修复的区域，黑色 = 保留区域。蒙版边缘略加模糊（1–3 像素）比锐利的二值化更融合。
- **按意图设置强度**：`0.3–0.5` 用于修饰/清理，`0.6–0.7` 用于对象替换并匹配风格，`0.8–1.0` 用于整体区域替换。
- **在提示词中指明蒙版外的保留内容**：`"保留屋顶轮廓和天空渐变"`、`"匹配砖块纹理和砂浆色调"`。
- **即使蒙版已界定区域，空间标签仍有帮助**：`"左侧架子"`、`"右上象限"`。

---

## 限制

- **各路线继承对应模型的限制。** Nano Banana：1–20 个输入，1–4 个输出。GPT Image 2 Edit：最多 10 个参考，4 种固定尺寸。Flux Konfig：单参考。Z-Image Inpaint：需蒙版。
- **不支持多路线混合。** 本技能每次调用只选择一种模型。
- **品牌特定覆盖** — 若用户指定了具体模型，请路由到对应的品牌技能（`gpt-image-edit`、`flux-konfig`、`nano-banana-edit`）以获得更全面的处理。

## 退出码

| 代码 | 含义 |
|---|---|
| 0 | 成功 |
| 64 | CLI 参数错误 |
| 65 | 输入 JSON 错误 / Schema 不匹配 |
| 69 | 上游 5xx 错误 |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或令牌被拒绝 |

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=image-edit)。

## 工作原理

本技能根据用户意图从 Nano Banana Edit / GPT Image 2 Edit / Flux Konfig Pro / Z-Image Turbo Inpaint 中选择一种模型，并以匹配的 JSON 请求体调用 `runcomfy run <model_id>`。CLI 向模型 API 提交 POST 请求，轮询请求，获取结果，并将任何 `.runcomfy.net` / `.runcomfy.com` URL 下载至 `--output-dir`。在退出前按 `Ctrl-C` 可取消远程请求。

## 安全与隐私

- **令牌存储**：`runcomfy login` 会将 API 令牌写入 `~/.config/runcomfy/token.json`，权限模式为 0600（仅所有者可读写）。在 CI / 容器中设置环境变量 `RUNCOMFY_TOKEN` 可完全绕过该文件。
- **输入边界**：用户提示词通过 `--input` 作为 JSON 字符串传递给 CLI。CLI 不会对提示词进行 shell 展开；它将 JSON 请求体直接通过 HTTPS 传输至模型 API。提示词内容不会带来 shell 注入风险。
- **第三方内容**：您提供的图片、蒙版、视频 URL 由 RunComfy 模型服务器获取，而非由您本机的 CLI 获取。应将外部 URL 视为不可信；对任意图片编辑/视频编辑模型而言，基于图片的提示词注入均属已知风险。
- **出站端点**：仅 `model-api.runcomfy.net`（请求提交）以及 `*.runcomfy.net` / `*.runcomfy.com`（生成输出结果的下载白名单）。无遥测，无回调。
- **生成文件大小上限**：CLI 会对任何单次下载超过 2 GiB 的文件终止请求，以预防恶意或失控模型输出导致磁盘被占满。
