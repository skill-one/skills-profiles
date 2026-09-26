# Nano Banana 2 — 专业包在 RunComfy

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=nano-banana-2) · [模型页面](https://www.runcomfy.com/models/google/nano-banana-2?utm_source=skills.sh&utm_medium=skill&utm_campaign=nano-banana-2) · [GitHub](https://github.com/agentspace-so/runcomfy-skills/tree/main/nano-banana-2)

Google **Nano Banana 2** — Gemini 家族中的快速文本到图像模型 — 在 **RunComfy 模型 API** 上托管。针对创意构思、社交缩略图批处理和具有强大图像内排版的快速草稿进行了优化。

```bash
npx skills add agentspace-so/runcomfy-skills --skill nano-banana-2 -g
```

## 何时选择此模型（与兄弟模型对比）

Nano Banana 2 是 Google 图像生成系列的快速模型。当迭代速度和可预测的构图比最大细节更重要时，选择它。

| 您想要 | 使用 |
|---|---|
| 快速草稿、社交缩略图、批量变体 | **Nano Banana 2** |
| 图像内排版，可预测渲染 | **Nano Banana 2** |
| 基于网络的图像（当前事件 / 真实实体） | **Nano Banana 2** + `enable_web_search` |
| 图像 **编辑**（保留主体，更换背景） | **Nano Banana Edit**（兄弟技能） |
| 重度风格化，绘画风格 | Flux 2 |
| 最大提示符遵循 + 多语言文本 | GPT Image 2 |
| 2K–4K 主角图，最大逼真度 | Seedream 5 |
| 超逼真肖像 | Nano Banana Pro |

如果用户明确提到 "Nano Banana" / "nano-banana-2" / "Gemini 图像"，无论是否指定 2 与 Pro，都直接路由到此处。如果用户提到 "Nano Banana" 而未指定 2 与 Pro，默认为 **Pro** 用于肖像，**2** 用于其他所有内容。

## 前置条件

1. **RunComfy CLI** — `npm i -g @runcomfy/cli`
2. **RunComfy 账户** — `runcomfy login` 会打开浏览器设备码流程。
3. **CI / 容器** — 设置 `RUNCOMFY_TOKEN=<token>` 而不是 `runcomfy login`。

## 端点 + 输入模式

### `google/nano-banana-2/text-to-image`

| 字段 | 类型 | 必填 | 默认 | 备注 |
|---|---|---|---|---|
| `prompt` | 字符串 | 是 | — | 主体优先描述。 |
| `num_images` | 整数 | 否 | 1 | 1–4。用于创意轮次使用 4。 |
| `seed` | 整数 | 否 | 0 | 用于可重复性。 |
| `aspect_ratio` | 枚举 | 否 | `auto` | `auto`、`21:9`、`16:9`、`3:2`、`4:3`、`5:4`、`1:1`、`4:5`、`3:4`、`2:3`、`9:16`。 |
| `resolution` | 枚举 | 否 | `1K` | `0.5K`（草稿）、`1K`（默认）、`2K`（最终）、`4K`（最大）。 |
| `output_format` | 枚举 | 否 | `png` | `png`、`jpeg`、`webp`。 |
| `safety_tolerance` | 整数 | 否 | 4 | 1（严格）– 6（宽松）。 |
| `limit_generations` | 布尔值 | 否 | true | 限制每个提示轮次为一个生成。 |
| `enable_web_search` | 布尔值 | 否 | false | 添加网络基础（额外成本 + 延迟）。 |

对于图像编辑（保留主体 + 应用更改），请参阅兄弟 [`nano-banana-edit`](../nano-banana-edit) 技能。

## 如何调用

**默认草稿（1K，方形，png）：**

```bash
runcomfy run google/nano-banana-2/text-to-image \
  --input '{"prompt": "<用户提示>"}' \
  --output-dir <绝对路径>
```

**垂直 4-up 批量用于创意构思：**

```bash
runcomfy run google/nano-banana-2/text-to-image \
  --input '{
    "prompt": "<用户提示>",
    "num_images": 4,
    "aspect_ratio": "9:16",
    "resolution": "0.5K"
  }' \
  --output-dir <绝对路径>
```

**最终 2K，带种子锁定：**

```bash
runcomfy run google/nano-banana-2/text-to-image \
  --input '{
    "prompt": "<用户提示>",
    "resolution": "2K",
    "aspect_ratio": "16:9",
    "seed": 42
  }' \
  --output-dir <绝对路径>
```

**网络基础（当前事件 / 真实实体）：**

```bash
runcomfy run google/nano-banana-2/text-to-image \
  --input '{
    "prompt": "<提示引用本周的一个真实世界事件>",
    "enable_web_search": true
  }' \
  --output-dir <绝对路径>
```

## 提示 — 实际有效的部分

**主体优先的声明性语法。** "一部电影感的特写肖像，一位美国女性站在东京的霓虹灯下，浅景深，反射的湿街道，超精细，逼真的皮肤纹理" — 优先主体，然后是动作、环境、风格、相机。前置主体；后跟指令。

**精确文本引用用于图像内排版。** "标签上写着 'AURA'，干净粗体无衬线字体，居中，白色在黑色上" — 引用实际字符。指定位置和字体样式。不要说 "带有品牌名称" 并希望。

**一致的种子用于细化。** 当迭代单个提示的小变体时锁定 `seed` — 保持构图稳定。

**网络基础，适度使用。** 只有当提示命名当前事件 / 真实实体时才打开 `enable_web_search`。增加延迟 + 成本；默认关闭。

**不要冲突风格。** "极简 + 装饰 + 复古 + 赛博朋克" 会取消。选择 1–2 个锚点。

**反模式：**
- 尝试用语言描述稳定的主体身份 — 使用 **编辑** 端点并参考图像。
- 要求分辨率超出 4 个等级 → 422。
- 纵横比超出 11 个支持值 → 422。
- 非引用的图像内文本 → 无法预测的渲染。

## 此模型的优势

| 用例 | 为什么选择 Nano Banana 2 |
|---|---|
| **营销草稿缩略图（4 个批量）** | 0.5K 的快速迭代，然后将获胜者提升到 2K |
| **社交平台原生** | 支持宽纵横比，包括 9:16、4:5、21:9 |
| **图像内排版用于海报 / 卡片** | 当字符被引用时，可预测的文本渲染 |
| **网络基础的当前事件图像** | `enable_web_search` 集成最新信息 |
| **可重复的变体测试** | 强大的种子 + 一致的构图 |

## 示例提示（验证可产生强结果）

**电影感肖像（页面示例）：**

```
一部电影感的特写肖像，一位美国女性站在东京的霓虹灯下，浅景深，反射的湿街道，超精细，逼真的皮肤纹理
```

**带引用文本的品牌资产卡片：**

```
一个极简 16:9 产品卡片：一个磨砂黑陶瓷马克杯居中放置在柔和暖灰色纸张背景上，从左上角反射高光，标题 "Brewed Quietly" 在右上角干净粗体无衬线字体，下方平衡的负空间，电子商务准备，干净工作室灯光
```

**垂直平台原生：**

```
一个 9:16 垂直主角用于一个健康品牌：一个陶瓷茶杯在亚麻跑道上，柔和的晨光侧面照明，顶部大号手写衬线字体 "Slow Down"，轻柔的蒸汽升起，中性调色板，无杂乱
```

## 限制

- **仅限静态图像。** 此端点不支持视频。
- **每请求最多 4 个输出。**
- **网络搜索增加延迟 + 成本** — 仅按需启用。
- **2K / 4K 成本更高** — 除非用户要求更高，否则默认为 1K。
- **对于图像编辑，使用 `/edit` 端点** — 不是这个。

## 退出代码

| 代码 | 含义 |
|---|---|
| 0  | 成功 |
| 64 | 命令行参数错误 |
| 65 | 输入 JSON 错误 / 模式不匹配 |
| 69 | 上游 5xx |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或令牌被拒绝 |

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=nano-banana-2).

## 工作原理

该技能调用 `runcomfy run google/nano-banana-2/text-to-image` 并使用匹配模式的 JSON 正文。CLI POST 到 `https://model-api.runcomfy.net/v1/models/google/nano-banana-2/text-to-image`，轮询请求，获取结果，并将任何 `.runcomfy.net`/`.runcomfy.com` URL 下载到 `--output-dir`。`Ctrl-C` 在退出前取消远程请求。

## 安全与隐私

- **令牌存储**：`runcomfy login` 将 API 令牌写入 `~/.config/runcomfy/token.json`，模式为 0600（仅所有者读写）。设置 `RUNCOMFY_TOKEN` 环境变量以在 CI / 容器中完全绕过文件。
- **输入边界**：用户提示作为 JSON 字符串通过 `--input` 传递给 CLI。CLI 不会 shell 扩展提示；它直接将 JSON 正文传输到 Model API。提示内容没有 shell 注入表面。
- **第三方内容**：您传递的图像 / 掩码 / 视频URL 由 RunComfy 模型服务器获取，而不是您的机器上的 CLI。将外部 URL 视为不受信任；基于图像的提示注入是任何图像编辑 / 视频编辑模型的已知风险。
- **出站端点**：仅 `model-api.runcomfy.net`（请求提交）和 `*.runcomfy.net` / `*.runcomfy.com`（生成输出的下载白名单）。没有遥测，没有回调。
- **生成文件大小上限**：CLI 中止任何单个下载 > 2 GiB，以防止恶意或失控的模型输出导致磁盘填满。
