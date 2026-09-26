# 图像编辑 — RunComfy 专业版

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=image-edit) · [Nano Banana Edit](https://www.runcomfy.com/models/google/nano-banana-2/edit?utm_source=skills.sh&utm_medium=skill&utm_campaign=image-edit) · [GPT Image 2 Edit](https://www.runcomfy.com/models/openai/gpt-image-2/edit?utm_source=skills.sh&utm_medium=skill&utm_campaign=image-edit) · [Flux Kontext](https://www.runcomfy.com/models/blackforestlabs/flux-1-kontext-pro/image-to-image?utm_source=skills.sh&utm_medium=skill&utm_campaign=image-edit) · [Z-Image Inpaint](https://www.runcomfy.com/models/tongyi-mai/z-image/turbo/inpainting?utm_source=skills.sh&utm_medium=skill&utm_campaign=image-edit) · [GitHub](https://github.com/agentspace-so/runcomfy-skills/tree/main/image-edit)

**图像编辑，意图路由。** 此技能不会将你锁定在单一模型上——它会根据用户实际需求，在 RunComfy 目录中挑选合适的编辑模型：批量保持身份、多语言文本重写、单次精确编辑或基于掩码的区域替换。

```bash
npx skills add agentspace-so/runcomfy-skills --skill image-edit -g
```

## 根据用户意图选择合适的模型

| 用户意图 | 模型 | 原因 |
|---|---|---|
| 批量编辑 1-20 张图像（SKU 画廊、A/B 变体） | **Nano Banana Edit** | 每次调用最多 20 张输入图像；锁定系列宽高比/分辨率 |
| 替换背景，保持主体身份 | **Nano Banana Edit** | 在“保持 X 不变”提示下，身份保持效果强 |
| 基于空间语言的本地化对象移除/添加（“左侧对象”、“右上角”） | **Nano Banana Edit** | 尊重方向性空间范围 |
| 图像内多语言/非拉丁文本重写（日语假名、西里尔字母、阿拉伯语） | **GPT Image 2 Edit** | 在多语言排版方面表现最强 |
| 多参考组合（主体来自 img1、场景来自 img2、调色板来自 img3） | **GPT Image 2 Edit** | 编号参考正确路由提示 |
| 布局精确的重新定位（“将标题从右上角移动到底部中心”） | **GPT Image 2 Edit** | 方向性语言在布局级别得到尊重 |
| 跨翻译标题变体的身份保持 | **GPT Image 2 Edit** | 同一源资产→多种语言变体，身份稳定 |
| 单次精确局部编辑（“她现在拿着一把橙色雨伞”） | **Flux Kontext Pro** | 单参考单指令，高保真度保持 |
| 掩码驱动对象移除（电线、水印、干扰物） | **Z-Image Turbo Inpaint** | 需要掩码，强度可调，边缘一致 |
| 掩码驱动区域替换（使用掩码的全背景替换） | **Z-Image Turbo Inpaint** | 高强度+干净掩码=干净替换 |
| 未指定时的默认值 | **Nano Banana Edit** | 最灵活，支持单次和批量 |

代理读取此表格，分类用户意图，并选择匹配的下方子部分。

## 前置条件

1. **RunComfy CLI** — `npm i -g @runcomfy/cli`
2. **RunComfy 账户** — `runcomfy login`.
3. **CI / 容器** — 设置 `RUNCOMFY_TOKEN=<token>`。

---

## 路由 1：Nano Banana Edit — 默认用于一般编辑 + 批量

**模型**: `google/nano-banana-2/edit`

### Schema

| 字段 | 类型 | 必填 | 默认 | 备注 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 以保持目标开头，以变更结尾。 |
| `image_urls` | array | 是 | — | **1-20** 公开可获取的 HTTPS URL。 |
| `number_of_images` | int | 否 | 1 | 每次调用 1-4 个输出。 |
| `aspect_ratio` | enum | 否 | `auto` | `auto` 跟随输入；锁定以保持批量一致性。 |
| `resolution` | enum | 否 | `1K` | `0.5K` / `1K` / `2K` / `4K`. |
| `output_format` | enum | 否 | `png` | `png` / `jpeg` / `webp`. |
| `seed` | int | 否 | — | 可重复性。 |
| `enable_web_search` | bool | 否 | false | 基于网络的编辑（额外延迟）。 |

### 调用

```bash
runcomfy run google/nano-banana-2/edit \
  --input '{
    "prompt": "保持主体身份、姿势和服装不变。将背景转换为下雨的霓虹赛博朋克街道。",
    "image_urls": ["https://.../肖像.jpg"]
  }' \
  --output-dir <绝对路径>
```

**批量（锁定宽高比 + 分辨率）：**

```bash
runcomfy run google/nano-banana-2/edit \
  --input '{
    "prompt": "将右下角的商标替换为干净的白色无衬线字体“AURA”。保持其他所有内容与输入完全一致。",
    "image_urls": ["https://.../sku-1.jpg", "https://.../sku-2.jpg", "https://.../sku-3.jpg"],
    "aspect_ratio": "1:1",
    "resolution": "1K"
  }' \
  --output-dir <绝对路径>
```

### 提示技巧

- **优先保持**：`"保持[身份/姿势/品牌/构图]不变。"` 然后说明变更。
- **空间范围**："背景仅"，"左侧对象"，"右上象限" — 具体位置得到尊重。
- **批量一致性**：跨批量锁定 `aspect_ratio` 和 `resolution`。
- **小步迭代**：将复合编辑拆分为多个较短的步骤。

---

## 路由 2：GPT Image 2 Edit — 多语言文本 + 多参考组合

**模型**: `openai/gpt-image-2/edit`

### Schema

| 字段 | 类型 | 必填 | 默认 | 备注 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 编辑指令；以保持目标开头。 |
| `images` | string[] | 是 | — | **最多 10** HTTPS URL。第一个是主要参考；其余为辅助。 |
| `size` | enum | 否 | `auto` | `auto`, `1024_1024`, `1024_1536`, `1536_1024`. **仅限这些。** |

### 调用

**多语言文本重写：**

```bash
runcomfy run openai/gpt-image-2/edit \
  --input '{
    "prompt": "保持照片、布局和品牌标记与输入完全一致。仅替换图像内的标题。新的标题为粗体日语假名“今日のおすすめ”，位置和字体粗细相同。",
    "images": ["https://.../海报-en.jpg"]
  }' \
  --output-dir <绝对路径>
```

**多参考组合：**

```bash
runcomfy run openai/gpt-image-2/edit \
  --input '{
    "prompt": "将主体从图像 1 组合到图像 2 的房间中。匹配图像 2 的光照和调色板。保持图像 1 主体身份不变。",
    "images": ["https://.../主体.jpg", "https://.../房间.jpg"]
  }' \
  --output-dir <绝对路径>
```

### 提示技巧

- **精确引用图像内文本**。为非拉丁文本命名：`"日语假名"`, `"西里尔字母"`, `"阿拉伯语从右到左"`。
- **编号多参考**：`"主体来自图像 1，光照来自图像 2"`。
- **方向性布局语言**：`"将标题从右上角移动到底部中心"`，`"替换右下角的商标"`。
- **`size: "auto"`** 保持输入比例——除非编辑改变构图，否则推荐使用。

---

## 路由 3：Flux Kontext Pro — 单次精确局部编辑

**模型**: `blackforestlabs/flux-1-kontext/pro/edit`

### Schema（最小化）

| 字段 | 类型 | 必填 | 备注 |
|---|---|---|---|
| `prompt` | string | 是 | 一个声明性编辑指令。 |
| `image` | string | 是 | **单个**源图像 URL。 |
| `aspect_ratio` | enum | 否 | 从支持的 W:H 值中选择。 |
| `seed` | int | 否 | 可重复性。 |

仅单个图像——无数组。对于多图像流程，使用路由 1（Nano Banana Edit）。

### 调用

```bash
runcomfy run blackforestlabs/flux-1-kontext/pro/edit \
  --input '{
    "prompt": "保持人物的面部、姿势和服装不变。在她的左手添加一把橙色雨伞，并露出轻微的笑容。",
    "image": "https://.../肖像.jpg"
  }' \
  --output-dir <绝对路径>
```

### 提示技巧

- **一个声明性指令**。 "她现在拿着一把橙色雨伞并露出笑容" — 疑问句，单次变更。
- **优先保持**。以 `"保持[不变元素]"` 开头，然后说明变更。
- **小步迭代**。单次通过上的复合编辑会漂移；拆分为顺序通过。

---

## 路由 4：Z-Image Turbo Inpaint — 掩码驱动精确区域编辑

**模型**: `tongyi-mai/z-image/turbo/inpainting`

### Schema

| 字段 | 类型 | 必填 | 备注 |
|---|---|---|---|
| `prompt` | string | 是 | 要填充/替换的内容；未掩码周围保持目标约束。 |
| `image` | string | 是 | 源图像 URL。 |
| `mask_image` | string | 是 | **灰度掩码 URL**（白色=填充，黑色=保持）。 |
| `strength` | float | 否 | 0.3–0.6 精修，0.7–1.0 全部替换。 |
| `control_scale` | float | 否 | 0.6–0.9 典型。 |
| `aspect_ratio` | enum | 否 | 输出宽高比。 |
| `seed` | int | 否 | 可重复性。 |

### 调用

**对象移除（低强度）：**

```bash
runcomfy run tongyi-mai/z-image/turbo/inpainting \
  --input '{
    "prompt": "移除天花板上的电线；保持屋顶线和天空渐变；使天空薄而干净。",
    "image": "https://.../街道.jpg",
    "mask_image": "https://.../电线掩码.png",
    "strength": 0.5,
    "control_scale": 0.8
  }' \
  --output-dir <绝对路径>
```

**区域替换（高强度）：**

```bash
runcomfy run tongyi-mai/z-image/turbo/inpainting \
  --input '{
    "prompt": "用光滑的浅灰色工作室纸替换繁忙的背景；仅掩码背景。",
    "image": "https://.../产品.jpg",
    "mask_image": "https://.../背景掩码.png",
    "strength": 0.9
  }' \
  --output-dir <绝对路径>
```

### 提示技巧

- **需要掩码 URL** — 灰度，白色=填充区域，黑色=保持。掩码边缘轻微模糊（1-3px）比锐利的二值更融合。
- **强度按意图**：`0.3–0.5` 用于精修/清理，`0.6–0.7` 用于对象替换并匹配风格，`0.8–1.0` 用于全部区域替换。
- **在提示中命名掩码外保持的内容**：`"保持屋顶线和天空渐变"`，`"匹配砖块图案和灰泥色调"`。
- **空间标签仍然有帮助** 即使掩码定义了区域：`"左侧货架"`，`"右上象限"`。

---

## 限制

- **每个路由继承其模型的限制**。 Nano Banana：1-20 输入，1-4 输出。 GPT Image 2 Edit：最多 10 参考项，4 个固定尺寸。 Flux Kontext：单个参考。 Z-Image Inpaint：需要掩码。
- **无多路由混合**。此技能每次调用选择一个模型。
- **品牌特定覆盖** — 如果用户指定了特定模型，路由到相应的品牌技能（`gpt-image-edit`，`flux-kontext`，`nano-banana-edit`）以获得更全面的处理。

## 退出代码

| 代码 | 含义 |
|---|---|
| 0  | 成功 |
| 64 | 命令行参数错误 |
| 65 | 输入 JSON 错误 / 模式不匹配 |
| 69 | 上游 5xx |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或令牌被拒绝 |

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=image-edit).

## 工作原理

该技能根据用户意图选择 Nano Banana Edit / GPT Image 2 Edit / Flux Kontext Pro / Z-Image Turbo Inpaint 中的一个，并使用匹配的 JSON 正文调用 `runcomfy run <model_id>`。 CLI 向模型 API 发送 POST 请求，轮询请求，获取结果，并将任何 `.runcomfy.net`/`.runcomfy.com` URL 下载到 `--output-dir`。 `Ctrl-C` 在退出前取消远程请求。

## 安全与隐私

- **令牌存储**：`runcomfy login` 将 API 令牌写入 `~/.config/runcomfy/token.json`，权限为 0600（仅所有者可读写）。设置 `RUNCOMFY_TOKEN` 环境变量可完全绕过文件，在 CI / 容器中使用。
- **输入边界**：用户提示作为 JSON 字符串通过 `--input` 传递给 CLI。CLI **不会** 扩展提示；它将 JSON 正文直接通过 HTTPS 传输到模型 API。从提示内容没有 shell 注入表面。
- **第三方内容**：您传递的图像/掩码/视频 URL 由 RunComfy 模型服务器获取，而不是您的机器上的 CLI。将外部 URL 视为不受信任；基于图像的提示注入是任何图像编辑/视频编辑模型的已知风险。
- **出站端点**：仅 `model-api.runcomfy.net`（请求提交）和 `*.runcomfy.net` / `*.runcomfy.com`（生成输出的下载白名单）。无遥测，无回调。
- **生成文件大小上限**：CLI 会中止任何单个下载 > 2 GiB，以防止恶意或失控的模型输出导致磁盘填满。
