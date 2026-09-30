---
name: gpt-image-2
description: 在RunComfy上使用OpenAI GPT Image 2（ChatGPT Images 2.0）生成和编辑图像。记录GPT Image 2的优势（嵌入文本、标志、多语言排版、指令精确性），其3种固定尺寸，编辑时保留语言的特性，以及何时应路由到兄弟模型（Flux 2 / Nano Banana Pro / Seedream）。通过本地RunComfy CLI调用`runcomfy run openai/gpt-image-2/text-to-image`或`/edit`。当触发“gpt image 2”、“gpt-image-2”、“ChatGPT Images 2”、“image 2”，或明确要求使用此模型进行生成或编辑时，将自动执行。
---

# GPT 图像 2 — RunComfy 专业版

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=gpt-image-2) · [文生图](https://www.runcomfy.com/models/openai/gpt-image-2/text-to-image?utm_source=skills.sh&utm_medium=skill&utm_campaign=gpt-image-2) · [编辑](https://www.runcomfy.com/models/openai/gpt-image-2/edit?utm_source=skills.sh&utm_medium=skill&utm_campaign=gpt-image-2) · [GitHub](https://github.com/agentspace-so/runcomfy-skills/tree/main/gpt-image-2)

OpenAI **GPT 图像 2**（ChatGPT 图像 2.0）在 **RunComfy 模型 API** 上托管——无需 OpenAI 密钥，异步 REST。

```bash
npx skills add agentspace-so/runcomfy-skills --skill gpt-image-2 -g
```

## 何时选择此模型（与同类模型对比）

GPT 图像 2 的独特优势是 **指令精确性**：它比同类模型更可靠地遵循多元素提示、布局提示和嵌入文本指令。当 **画布上的内容比风格化外观更重要** 时，选择它。

| 您想要 | 使用 |
|---|---|
| 嵌入文本、标志、指示牌、多语言排版 | **GPT 图像 2** |
| 品牌安全、电子商务/广告/UI 模板图像 | **GPT 图像 2** |
| 迭代优化时保持构图稳定 | **GPT 图像 2** |
| 重度风格化、绘画感 | Flux 2 |
| 超写实人像 | Nano Banana Pro |
| 电影感/优先美观的英雄图像 | Seedream 5 |

如果用户明确要求 GPT 图像 2 / ChatGPT 图像 2 / 图像 2，无论模型选择如何，都应路由到此路径——不要质疑模型选择。

## 前置条件

1. **RunComfy CLI** — `npm i -g @runcomfy/cli`
2. **RunComfy 账户** — `runcomfy login` 会打开浏览器设备码流程。
3. **CI / 容器** — 设置 `RUNCOMFY_TOKEN=<token>` 而不是 `runcomfy login`。

## 端点 + 输入模式

两个端点，使用同一模型。

### `openai/gpt-image-2/text-to-image`

| 字段 | 类型 | 必填 | 默认 | 备注 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 积极提示 |
| `size` | enum | 否 | `1024_1024` | `1024_1024`（1:1）、`1024_1536`（2:3 竖版）、`1536_1024`（3:2 横版）——**仅限这三个** |

### `openai/gpt-image-2/edit`

| 字段 | 类型 | 必填 | 默认 | 备注 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 自然语言**编辑指令** |
| `images` | string[] | 是 | — | **最多 10** 个参考图像 URL（可公开获取的 HTTPS） |
| `size` | enum | 否 | `auto` | `auto`（保留输入比例），或上述三个固定尺寸之一 |

`size=auto` 在编辑时保留输入的宽高比——除非编辑明确改变构图，否则强烈推荐。

## 如何调用

**文生图：**

```bash
runcomfy run openai/gpt-image-2/text-to-image \
  --input '{"prompt": "<用户提示>", "size": "1024_1536"}' \
  --output-dir <绝对路径>
```

**编辑（单个参考）：**

```bash
runcomfy run openai/gpt-image-2/edit \
  --input '{
    "prompt": "<编辑指令>",
    "images": ["https://..."]
  }' \
  --output-dir <绝对路径>
```

**编辑（多参考，最多 10）：**

```bash
runcomfy run openai/gpt-image-2/edit \
  --input '{
    "prompt": "将图像 1 中的主体合成到图像 2 中的房间中；匹配图像 2 的光照",
    "images": ["https://...subject.jpg", "https://...room.jpg"]
  }' \
  --output-dir <绝对路径>
```

CLI 提交，每 2 秒轮询一次直到终端，然后下载结果中的 `*.runcomfy.net` / `*.runcomfy.com` URL 到 `--output-dir`。标准输出是结果 JSON。标准错误是进度。

用于管道友好用法：

```bash
runcomfy --output json run openai/gpt-image-2/text-to-image \
  --input '{"prompt":"..."}' --no-wait | jq -r .request_id
```

## 提示——实际有效的内容

这些是特定于模型的模式，可以实际提高输出质量。适用于文生图和编辑。

**明确说明主体 + 背景 + 氛围。** "一个磨砂陶瓷水瓶的特写，放在温暖的亚麻布上，柔和的窗户光，标签上有干净的衬线字体 'AQUA+'，边缘微妙高光，适合电子商务，8K 细节，中性背景"——三个具体指令——胜过 "一个瓶子的漂亮产品照片"。

**精确引用嵌入文本。保持简短。** GPT 图像 2 是此类中最强的文本渲染模型，但只有当您**将字面字符放在引号中**时才如此。长文本块会降低质量。对于多语言文本，命名脚本： "日语假名"，"西里尔文"，"阿拉伯语从右到左"。

**直接使用构图提示。** "三分法"，"特写"，"空中视角"，"居中主体"，"浅景深"——这些对模型有学习意义。

**一次迭代一个属性。** 当优化时，每次迭代更改一个东西（光照或背景或姿势或文本），并保持提示的其余部分不变。当只有一个旋钮移动时，模型在迭代中保持构图稳定。

**不要冲突指令。** "无文本" + "标签上有 'AQUA+' 字样" 是不连贯的——模型会选择一个，而您无法控制哪个。

**不要堆叠风格。** "浮世绘 + 水彩 + 8K + 电影感 + 极简主义" 会相互抵消。最多选择一到两个风格锚点。

针对**编辑**端点的特定说明：

- **声明保留目标。** "**保持**人物姿势和面部身份不变"， "**保持**包装上的品牌标志和排版"， "**保持**整体构图"。模型需要知道什么不要改变。
- **使用空间编辑的方向性语言。** "将标题从右上角移动到底部中间"，而不是 "重新定位标题"。
- **多参考**：在提示中编号图像——"从图像 1 中提取主体，从图像 2 中提取光照和背景"——模型将正确路由提示。

## 优势领域

| 用例 | 为什么选择 GPT 图像 2 |
|---|---|
| **电子商务产品摄影** | 可靠的标签文本、品牌安全的光照、跨 SKU 的一致性 |
| **高转化广告** | 一键整合标题和视觉效果 |
| **品牌资产本地化** | 一个源资产 → 相同标题的多种语言变体 |
| **指示牌、海报、包装模板** | 多尺度文本渲染精度 |
| **UI 模板、科学插图** | 布局精确性和标签可读性 |

## 示例提示（经验证可产生强力结果）

**文生图——产品英雄：**

```
一个极简的英雄产品静物：磨砂陶瓷水瓶放在温暖的亚麻布上，
柔和的窗户光，标签上有干净的衬线字体 "AQUA+"，
边缘微妙高光，适合电子商务，8K 细节，中性背景
```

**文生图——多语言指示牌：**

```
一个东京咖啡馆店面在黄昏时分，温暖的室内光，
标志上用粗体日语假名写在木牌上 "コーヒー"，
浅景深，三分法，电影感
```

**编辑——背景替换并保留：**

```
将背景变成明亮的极简白到浅灰工作室渐变，
带有柔和的地面阴影；在图像中添加一个大型标题，
读取 "OPEN STUDIO"，使用粗体干净的无衬线字体，
高对比度，居中；
保持主要人物或产品，姿势和面部身份不变
```

## 限制

- **仅 3 个固定尺寸**在文生图上（编辑上有相同的 3 个 + `auto`）。极端宽高比会自动调整到最近的支持尺寸。
- **提示长度**~ 几千个 token。长文本块会降低输出质量。
- **编辑的多图像**支持是 "最多 10 个参考的指导"，不是 ControlNet 风格的堆叠。第一个图像被视为主要图像；其余图像提供辅助提示。
- **人像的逼真度**不是它的强项——Nano Banana Pro 在一对一比较中胜出。

## 退出代码

`runcomfy` CLI 使用 sysexits 风格的代码：

| 代码 | 含义 |
|---|---|
| 0  | 成功 |
| 64 | 命令行参数错误 |
| 65 | 输入 JSON 错误 / 模式不匹配（例如 `size: "2048_2048"` 会 422） |
| 69 | 上游 5xx |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或令牌被拒绝 |

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=gpt-image-2).

## 工作原理

1. 技能调用 `runcomfy run openai/gpt-image-2/<端点>`，使用上述模式匹配的 JSON 正文。
2. CLI 向 `https://model-api.runcomfy.net/v1/models/openai/gpt-image-2/<端点>` 发送 POST 请求，附带用户的令牌。
3. 模型 API 返回 `request_id`；CLI 每 2 秒轮询一次 `GET .../requests/<id>/status`。
4. 终端状态时，CLI 获取 `GET .../requests/<id>/result` 并下载以 `.runcomfy.net` 或 `.runcomfy.com` 结尾的任何 URL 到 `--output-dir`。其他 URL 会列出但不会下载。
5. 轮询时按 `Ctrl-C` 会发送 `POST .../requests/<id>/cancel`，以免为停止的 GPU 付费。

## 这项技能不是什么

不是 OpenAI API 客户端。不是能力授权——需要有效的 RunComfy 账户。不是多租户。

## 安全与隐私

- **令牌存储**：`runcomfy login` 将 API 令牌写入 `~/.config/runcomfy/token.json`，权限为 0600（仅所有者可读写）。设置 `RUNCOMFY_TOKEN` 环境变量可完全绕过文件，适用于 CI / 容器。
- **输入边界**：用户提示作为 JSON 字符串通过 `--input` 传递给 CLI。CLI 不会展开提示；它直接将 JSON 正文通过 HTTPS 传输到模型 API。提示内容没有 shell 注入表面。
- **第三方内容**：您传递的图像/掩码/视频 URL 由 RunComfy 模型服务器获取，而不是您的机器上的 CLI。将外部 URL 视为不受信任；基于图像的提示注入是任何图像编辑/视频编辑模型的已知风险。
- **出站端点**：仅 `model-api.runcomfy.net`（请求提交）和 `*.runcomfy.net` / `*.runcomfy.com`（生成输出的下载白名单）。没有遥测，没有回调。
- **生成文件大小上限**：CLI 会中止任何单个下载 > 2 GiB，以防止恶意或失控的模型输出导致磁盘填满。
