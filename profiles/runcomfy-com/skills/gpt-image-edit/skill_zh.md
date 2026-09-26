# GPT 图像编辑 — RunComfy 上的 Pro 包

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=gpt-image-edit) · [编辑端点](https://www.runcomfy.com/models/openai/gpt-image-2/edit?utm_source=skills.sh&utm_medium=skill&utm_campaign=gpt-image-edit) · [文本到图像的兄弟功能](https://www.runcomfy.com/models/openai/gpt-image-2/text-to-image?utm_source=skills.sh&utm_medium=skill&utm_campaign=gpt-image-edit) · [GitHub](https://github.com/agentspace-so/runcomfy-skills/tree/main/gpt-image-edit)

在 **RunComfy 模型 API** 上的 OpenAI **GPT 图像 2 — `/edit` 端点**（ChatGPT 图像 2.0 图像到图像）。在同类产品中，它最擅长通过目标编辑保留身份，并在任何脚本（拉丁文、假名、CJK、西里尔文、阿拉伯文）中重写嵌入的文本。

```bash
npx skills add agentspace-so/runcomfy-skills --skill gpt-image-edit -g
```

## 何时选择此模型（与兄弟功能对比）

| 您想要 | 使用 |
|---|---|
| 编辑图像中的多语言/嵌入文本 | **GPT 图像编辑** |
| 通过翻译标题变体保留身份 | **GPT 图像编辑** |
| 精确布局编辑（移动标题、交换行动号召等） | **GPT 图像编辑** |
| 最高支持 10 张参考图像 | **GPT 图像编辑** |
| 一致地批量处理最多 20 张图像 | Nano Banana 编辑 |
| 精确本地单次编辑，优先考虑源保真度 | Flux Kontext |
| 使用 GPT 图像 2 从头开始生成 | 兄弟功能 [`gpt-image-2`](../gpt-image-2) 技能 |
| 批量处理具有稳定身份的 SKU 画廊 | Nano Banana 编辑 |

## 前置条件

1. **RunComfy CLI** — `npm i -g @runcomfy/cli`
2. **RunComfy 账户** — `runcomfy login` 会打开一个浏览器设备码流程。
3. **CI / 容器** — 设置 `RUNCOMFY_TOKEN=<token>` 而不是 `runcomfy login`。

## 端点 + 输入模式

### `openai/gpt-image-2/edit`

| 字段 | 类型 | 必填 | 默认 | 备注 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 编辑指令。以保留开头，以更改结尾。 |
| `images` | string[] | 是 | — | **最多 10** 张可公开获取的 HTTPS URL。第一个是主要的；其余是辅助的。 |
| `size` | enum | 否 | `auto` | `auto`（保留输入），`1024_1024`（1:1），`1024_1536`（2:3 竖版），`1536_1024`（3:2 横版）。 |

`size=auto` 保留输入比例——除非编辑明确更改了构图，否则强烈推荐。

## 如何调用

**单参考保留编辑：**

```bash
runcomfy run openai/gpt-image-2/edit \
  --input '{
    "prompt": "保留人物的面部、姿势和品牌标志不变。将背景替换为柔和的暖灰色工作室扫掠和轻柔的地板阴影。",
    "images": ["https://.../portrait.jpg"]
  }' \
  --output-dir <绝对路径>
```

**多语言文本重写（保留除标题之外的所有内容）：**

```bash
runcomfy run openai/gpt-image-2/edit \
  --input '{
    "prompt": "保留输入中的照片、布局和品牌标志完全不变。仅替换图像中的标题。新的标题以粗体日语假名显示为“今日のおすすめ”，位置和字体粗细与之前相同。",
    "images": ["https://.../poster-en.jpg"]
  }' \
  --output-dir <绝对路径>
```

**多参考组合：**

```bash
runcomfy run openai/gpt-image-2/edit \
  --input '{
    "prompt": "将图像 1 的主体组合到图像 2 的房间中。匹配图像 2 的光照和调色板。保留图像 1 主体身份（面部、姿势、服装）不变。",
    "images": ["https://.../subject.jpg", "https://.../room.jpg"]
  }' \
  --output-dir <绝对路径>
```

## 提示语 — 实际有效的内容

**首先提出保留目标。** 始终：`"保留 [面部 / 姿势 / 衣物 / 品牌 / 构图] 不变。"` 然后说明更改。模型会尊重前面说明的内容。

**多语言文本——引用字符，命名脚本。** `"标题显示为“コーヒー”的粗体日语假名"`, `"标签显示为“АРОМА”的西里尔文，白色背景"`, `"右侧边距标题显示为“تخفيض”的阿拉伯文从右到左"`。不要释义——直接引用。

**空间编辑的方向性语言。** 具体的空间范围有效：`"将标题从右上角移动到底部中心"`, `"仅移除最左侧的对象"`, `"替换右下角的水印"`。

**多参考编号。** 当传递多个 `images` 时，通过编号引用它们：`"主体来自图像 1，光照来自图像 2，调色板来自图像 3"`。模型正确路由提示。

**使用 `size: "auto"` 保留输入比例。** 仅在编辑明确更改构图时覆盖（例如将 16:9 裁剪为 1:1）。

**反模式：**
- 长复合编辑指令（"更改 A 和 B 和 C 和 D"）→ 每增加一个范围，漂移增加。
- 缺少保留目标 → 模型会微妙地重写面部 / 品牌 / 构图。
- 释义图像中的文本而不是引用它 → 文本会不同。
- 请求 `size` 在 3 个固定值 + `auto` 之外 → 422。

## 它的优势所在

| 用例 | 为什么选择 GPT 图像编辑 |
|---|---|
| **多语言广告本地化** | 一个源资产 → 相同标题的多种语言变体 |
| **品牌安全的标题 / 行动号召交换** | 布局精确度 + 保留语言保持其余内容稳定 |
| **多参考组合（主体来自一个，场景来自另一个）** | 编号参考正确路由提示 |
| **布局精确的重新定位** | 方向性语言（"右上角到底部中心"）被尊重 |
| **跨标志编辑保留身份** | 在通过目标编辑保留面部 / 品牌方面，同类产品中最强 |

## 示例提示语（验证可产生强结果）

**背景替换，完整保留（页面示例）：**

```
将背景变为明亮的极简白到柔和灰色的工作室扫掠，带有轻柔的地板阴影；在图像中添加一个大的标题，显示“OPEN STUDIO”，使用粗体清洁的无衬线字体，高对比度，居中；保留主要人物或产品、姿势和面部身份不变
```

**多语言变体：**

```
保留输入中的照片、布局、光照和品牌标志完全不变。仅替换图像中的标题。
新的标题以粗体日语假名显示为“コーヒー”，位置和字体粗细与之前相同。
```

**多参考组合：**

```
将主体从图像 1 组合到图像 2 的厨房中。
匹配图像 2 的温暖窗户光照和调色板。
保留图像 1 主体身份（面部、姿势、服装）不变。
```

## 限制

- **`size`：3 个固定值 + `auto`** — 任何其他内容 422s。
- **`images`：最多 10 张** — 第一个是主要的，其余是辅助提示。
- **长复合提示漂移** — 需要时分成多个步骤。
- **对于跨许多 SKU 图像的批量一致性，Nano Banana 编辑（最多 20 张）更好。**
- **肖像上的照片逼真度** — Nano Banana Pro 头对头胜出。

## 退出代码

| 代码 | 含义 |
|---|---|
| 0  | 成功 |
| 64 | 坏 CLI 参数 |
| 65 | 坏输入 JSON / 模式不匹配 |
| 69 | 上游 5xx |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或令牌被拒绝 |

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=gpt-image-edit).

## 工作原理

该技能调用 `runcomfy run openai/gpt-image-2/edit` 并使用符合模式的 JSON 正文。CLI POST 到 `https://model-api.runcomfy.net/v1/models/openai/gpt-image-2/edit`，轮询请求，获取结果，并将任何 `.runcomfy.net`/`.runcomfy.com` URL 下载到 `--output-dir`。`Ctrl-C` 在退出前取消远程请求。

## 安全与隐私

- **令牌存储**：`runcomfy login` 将 API 令牌写入 `~/.config/runcomfy/token.json`，权限为 0600（仅所有者可读写）。设置 `RUNCOMFY_TOKEN` 环境变量以在 CI / 容器中完全绕过文件。
- **输入边界**：用户提示作为 JSON 字符串通过 `--input` 传递给 CLI。CLI 不会 shell 扩展提示；它直接将 JSON 正文传输到模型 API。提示内容没有 shell 注入表面。
- **第三方内容**：您传递的图像 / 掩码 / 视频URL由 RunComfy 模型服务器获取，而不是您的机器上的 CLI。将外部 URL 视为不受信任；基于图像的提示注入是任何图像编辑 / 视频编辑模型的已知风险。
- **出站端点**：仅 `model-api.runcomfy.net`（请求提交）和 `*.runcomfy.net` / `*.runcomfy.com`（生成输出的下载白名单）。没有遥测，没有回调。
- **生成文件大小上限**：CLI 会中止任何单个下载 > 2 GiB，以防止恶意或失控的模型输出导致磁盘填满。
