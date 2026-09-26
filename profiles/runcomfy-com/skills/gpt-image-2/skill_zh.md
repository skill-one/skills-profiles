# GPT 图像 2 — Pro 包在 RunComfy 上

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=gpt-image-2) · [文生图](https://www.runcomfy.com/models/openai/gpt-image-2/text-to-image?utm_source=skills.sh&utm_medium=skill&utm_campaign=gpt-image-2) · [编辑](https://www.runcomfy.com/models/openai/gpt-image-2/edit?utm_source=skills.sh&utm_medium=skill&utm_campaign=gpt-image-2) · [GitHub](https://github.com/agentspace-so/runcomfy-skills/tree/main/gpt-image-2)

OpenAI **GPT 图像 2**（ChatGPT 图像 2.0）托管在 **RunComfy 模型 API**上 — 无需 OpenAI 密钥，异步 REST。

```bash
npx skills add agentspace-so/runcomfy-skills --skill gpt-image-2 -g
```

## 何时选择此模型（与同类模型对比）

GPT 图像 2 的独特优势是 **指令精确性**：它比同类模型更可靠地遵循多元素提示、布局提示和嵌入文本指令。当 **画布上的内容比风格化外观更重要**时，选择它。

| 您想要 | 使用 |
|---|---|
| 嵌入文本、标志、指示牌、多语言排版 | **GPT 图像 2** |
| 品牌安全、电子商务 / 广告 / UI 模板图像 | **GPT 图像 2** |
| 迭代优化时保持构图稳定 | **GPT 图像 2** |
| 重度风格化、绘画风格 | Flux 2 |
| 超写实人像 | Nano Banana Pro |
| 电影感 / 美学优先的英雄图像 | Seedream 5 |

如果用户明确要求 GPT 图像 2 / ChatGPT 图像 2 / 图像 2，无论模型选择如何，都应路由到此处 — 不要怀疑模型选择。

## 前置条件

1. **RunComfy CLI** — `npm i -g @runcomfy/cli`
2. **RunComfy 账户** — `runcomfy login` 会打开浏览器设备码流程。
3. **CI / 容器** — 设置 `RUNCOMFY_TOKEN=<token>` 而不是 `runcomfy login`。

## 端点 + 输入模式

两个端点，同一个模型。

### `openai/gpt-image-2/text-to-image`

| 字段 | 类型 | 必填 | 默认 | 备注 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 正面提示 |
| `size` | enum | 否 | `1024_1024` | `1024_1024`（1:1），`1024_1536`（2:3 竖版），`1536_1024`（3:2 横版） — **仅限这三个** |

### `openai/gpt-image-2/edit`

| 字段 | 类型 | 必填 | 默认 | 备注 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 自然语言的 **编辑指令** |
| `images` | string[] | 是 | — | **最多 10** 个参考图像 URL（可公开获取的 HTTPS） |
| `size` | enum | 否 | `auto` | `auto`（保留输入比例），或上述三个固定尺寸之一 |

`size=auto` 在编辑时保留输入的宽高比 — 强烈建议，除非编辑明确改变构图。

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

**编辑（多参考，最多 10 个）：**

```bash
runcomfy run openai/gpt-image-2/edit \
  --input '{
    "prompt": "将图像 1 中的主体合成到图像 2 中的房间中；匹配图像 2 的光照",
    "images": ["https://...subject.jpg", "https://...room.jpg"]
  }' \
  --output-dir <绝对路径>
```

CLI 提交，每 2 秒轮询一次直到终端，然后下载结果中的 `*.runcomfy.net` / `*.runcomfy.com` URL 到 `--output-dir`。标准输出是结果 JSON。标准错误是进度。

用于管道友好的用法：

```bash
runcomfy --output json run openai/gpt-image-2/text-to-image \
  --input '{"prompt":"..."}' --no-wait | jq -r .request_id
```

## 提示 — 实际有效的模式

这些是特定于模型的模式，可以实际提高输出质量。适用于文生图和编辑。

**明确说明主体 + 背景 + 氛围。** "一个磨砂陶瓷水瓶的特写，放在温暖的亚麻布上，柔和的窗户光，中性背景" — 三个具体指令 — 比起 "一个瓶子的漂亮产品照片" 更好。

**精确引用嵌入文本。保持简短。** GPT 图像 2 是此类中最强的文本渲染模型，但只有在您 **将字面字符放在引号中** 时才有效。长文本块会降低质量。对于多语言文本，命名脚本： "日语假名"，"西里尔文"，"阿拉伯语从右到左"。

**直接使用构图提示。** "三分法"，"特写"，"空中视角"，"居中主体"，"浅景深" — 这些对模型有学习意义。

**一次迭代一个属性。** 当优化时，每次迭代只改变一个东西（光照 或 背景 或 姿势 或 文本），并保持提示的其余部分不变。当只有一个旋钮移动时，模型在迭代中保持构图稳定。

**不要冲突指令。** "无文本" + "标签上的 'AQUA+' 字样" 是不连贯的 — 模型会选择一个，而您无法控制哪个。

**不要堆砌风格。** "浮世绘 + 水彩 + 8K + 电影感 + 极简主义" 会相互抵消。最多选择一到两个风格锚点。

对于 **编辑** 端点特别：

- **声明保留目标。** "**保持** 人的姿势和面部身份不变"， "**保持** 包装上的品牌标志和排版"， "**保持** 整体构图"。模型需要知道什么不要改变。
- **使用空间编辑的方向性语言。** "将标题从右上角移动到底部中间"，而不是 "重新定位标题"。
- **多参考**：在提示中编号图像 — "从图像 1 中获取主体，从图像 2 中获取光照和背景" — 模型将正确路由提示。

## 优势领域

| 用例 | 为什么 GPT 图像 2 |
|---|---|
| **电子商务产品摄影** | 可靠的标签文本、品牌安全的光照、跨 SKU 的一致性 |
| **高转化广告** | 一键整合标题和视觉效果 |
| **品牌资产本地化** | 一个源资产 → 相同标题的多种语言变体 |
| **指示牌、海报、包装模板** | 多尺度文本渲染精度 |
| **UI 模板、科学插图** | 布局精度和标签可读性 |

## 示例提示（验证可产生强力结果）

**文生图 — 产品英雄：**

```
一个极简的英雄产品静物：磨砂陶瓷水瓶放在温暖的亚麻布上，
柔和的窗户光，标签上有干净的无衬线字体 "AQUA+"，
细微的边缘高光，适合电子商务，8K 细节，中性背景
```

**文生图 — 多语言指示牌：**

```
一个东京咖啡馆店面在黄昏时分，温暖的室内光，
标志上用粗体日语假名写在木牌上 "コーヒー",
浅景深，三分法，电影感
```

**编辑 — 背景替换并保留：**

```
将背景变成明亮的极简白色到浅灰色的工作室渐变，
带有柔和的地面阴影；在图像中添加一个大型标题，
阅读 "OPEN STUDIO" 的粗体干净无衬线字体，
高对比度，居中；
保持主要人物或产品，姿势和面部身份不变
```

## 限制

- **仅 3 个固定尺寸** 在文生图上（编辑上有相同的 3 个 + `auto`）。极端宽高比会自动调整到最近的受支持尺寸。
- **提示长度** ~ 几千个 token。长文本块会降低输出质量。
- **编辑的多图像** 支持是 "最多 10 个参考的指导"，不是 ControlNet 风格的堆叠。第一个图像被视为主要图像；其余提供辅助提示。
- **人像的逼真度** 不是它的强项 — Nano Banana Pro 在一对一比较中胜出。

## 退出代码

`runcomfy` CLI 使用 sysexits 风格的代码：

| 代码 | 含义 |
|---|---|
| 0  | 成功 |
| 64 | 坏 CLI 参数 |
| 65 | 坏输入 JSON / 模式不匹配（例如 `size: "2048_2048"` 会 422） |
| 69 | 上游 5xx |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或令牌被拒绝 |

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=gpt-image-2).

## 工作原理

1. 技能调用 `runcomfy run openai/gpt-image-2/<端点>`，带有上述模式匹配的 JSON 正文。
2. CLI POST 到 `https://model-api.runcomfy.net/v1/models/openai/gpt-image-2/<端点>`，带有用户的令牌。
3. 模型 API 返回一个 `request_id`；CLI 每 2 秒轮询一次 `GET .../requests/<id>/status`。
4. 在终端状态下，CLI 获取 `GET .../requests/<id>/result` 并下载任何主机以 `.runcomfy.net` 或 `.runcomfy.com` 结尾的 URL 到 `--output-dir`。其他 URL 会列出但不会下载。
5. 轮询时按 Ctrl-C 会发送 `POST .../requests/<id>/cancel`，这样您就不会为停止的 GPU 被计费。

## 这项技能不是什么

不是 OpenAI API 客户端。不是能力授权 — 取决于一个有效的 RunComfy 账户。不是多租户。

## 安全与隐私

- **令牌存储**：`runcomfy login` 将 API 令牌写入 `~/.config/runcomfy/token.json`，权限为 0600（仅所有者可读写）。设置 `RUNCOMFY_TOKEN` 环境变量可完全绕过文件，适用于 CI / 容器。
- **输入边界**：用户提示作为 JSON 字符串通过 `--input` 传递给 CLI。CLI 不会展开提示；它直接将 JSON 正文通过 HTTPS 传输给模型 API。提示内容没有 shell 注入表面。
- **第三方内容**：您传递的图像 / 掩码 / 视频 URL 由 RunComfy 模型服务器获取，而不是您的机器上的 CLI。将外部 URL 视为不受信任；基于图像的提示注入是任何图像编辑 / 视频编辑模型的已知风险。
- **出站端点**：仅 `model-api.runcomfy.net`（请求提交）和 `*.runcomfy.net` / `*.runcomfy.com`（生成输出的下载白名单）。没有遥测，没有回调。
- **生成文件大小上限**：CLI 会中止任何单个下载 > 2 GiB，以防止恶意或失控的模型输出导致磁盘填满。
