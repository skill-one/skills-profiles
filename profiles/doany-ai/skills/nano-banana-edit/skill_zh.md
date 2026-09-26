# Nano Banana Edit — Pro Pack on RunComfy

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=nano-banana-edit) · [Edit endpoint](https://www.runcomfy.com/models/google/nano-banana-2/edit?utm_source=skills.sh&utm_medium=skill&utm_campaign=nano-banana-edit) · [GitHub](https://github.com/agentspace-so/runcomfy-skills/tree/main/nano-banana-edit)

Google **Nano Banana 2 Edit** — Gemini系列快速级图像模型的图像到图像编辑端点 — 在 **RunComfy Model API** 上托管。每次调用最多支持 **20 张输入图像**，用于批量编辑和多参考变化。

```bash
npx skills add agentspace-so/runcomfy-skills --skill nano-banana-edit -g
```

## 何时选择此模型（与兄弟模型对比）

| 您想要 | 使用 |
|---|---|
| 保留主体身份，交换背景或服装 | **Nano Banana Edit** |
| 一批次一致地编辑最多 20 张图像 | **Nano Banana Edit** |
| 使用空间语言将编辑本地化到“仅 X” | **Nano Banana Edit** |
| 编辑图像中的多语言文本（标志、标签） | GPT Image 2 edit |
| 单参考 + 精确局部编辑（“她现在拿着 X”） | Flux Kontext |
| 从头生成新图像 | Nano Banana 2 t2i（兄弟技能） |

如果用户明确说了“nano banana edit” / “使用 nano banana 编辑”，无论何种情况都应路由到此处。

## 前置条件

1. **RunComfy CLI** — `npm i -g @runcomfy/cli`
2. **RunComfy 账户** — `runcomfy login` 会打开浏览器设备码流程。
3. **CI / 容器** — 设置 `RUNCOMFY_TOKEN=<token>` 而不是 `runcomfy login`。

## 端点 + 输入模式

### `google/nano-banana-2/edit`

| 字段 | 类型 | 必填 | 默认 | 备注 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 编辑指令。开头保留，结尾变更。 |
| `image_urls` | array | 是 | — | **1–20** 公开可获取的 HTTPS URL。 |
| `number_of_images` | int | 否 | 1 | 每次调用 1–4 个输出。 |
| `seed` | int | 否 | — | 可重复性。 |
| `aspect_ratio` | enum | 否 | `auto` | `auto`（跟随输入）或固定比例 — 固定以保持批量一致性。 |
| `resolution` | enum | 否 | `1K` | `0.5K` / `1K` / `2K` / `4K`。 |
| `output_format` | enum | 否 | `png` | `png` / `jpeg` / `webp`。 |
| `safety_tolerance` | int | 否 | 4 | 1（严格）– 6（宽松）。 |
| `limit_generations` | bool | 否 | — | 如果为真，则限制每轮一个输出。 |
| `enable_web_search` | bool | 否 | false | 网络基础（额外成本 / 延迟）。 |

## 如何调用

**单图像背景替换，身份保留：**

```bash
runcomfy run google/nano-banana-2/edit \
  --input '{
    "prompt": "保留主体身份、姿势和服装不变。将背景转换为雨天霓虹赛博朋克街道。",
    "image_urls": ["https://.../portrait.jpg"]
  }' \
  --output-dir <绝对路径>
```

**批量编辑，固定构图：**

```bash
runcomfy run google/nano-banana-2/edit \
  --input '{
    "prompt": "将右下角的标志替换为干净的白色无衬线字体文本“AURA”。保留输入中的其他所有内容。",
    "image_urls": ["https://.../sku-1.jpg", "https://.../sku-2.jpg", "https://.../sku-3.jpg"],
    "aspect_ratio": "1:1",
    "resolution": "1K"
  }' \
  --output-dir <绝对路径>
```

**目标空间编辑（“仅左侧对象”）：**

```bash
runcomfy run google/nano-banana-2/edit \
  --input '{
    "prompt": "仅移除最左侧的对象。保留右侧两个对象、桌子和光照不变。",
    "image_urls": ["https://.../still-life.jpg"]
  }' \
  --output-dir <绝对路径>
```

## 提示 — 实际效果

**先保留，后变更。** 始终以 `"保留[身份 / 姿势 / 服装 / 品牌标志 / 构图]不变。"` 开头，然后以一句简洁的话说明变更。模型会尊重开头的说明；尾部的保留内容会被忽略。

**使用空间语言进行本地化。** "仅背景"、"左侧对象"、"右上角"、"标题上方" — 具体的空间范围会被尊重。"让它更 X" 是模糊的，会导致漂移。

**批量一致性** — 编辑一系列图像时，锁定 `aspect_ratio` 和 `resolution`。跨批量使用相同的提示语法，使每个输出看起来像兄弟，而不是混音。

**小步迭代。** 如果一次编辑漂移，分成两次：第一次仅更换背景，第二次交换主体的服装。编辑更干净，总成本相同（假设分辨率相似）。

**多图像变化** — 最多传递 20 个输入以获得一致的批量。适用于 SKU 图库、A/B 测试、角色表变化。

**反模式：**
- 长复合指令（“更改 A 和 B 和 C 和 D”） — 每增加一个范围，漂移会增加。
- 被动语态的编辑指令（“背景应该被更改”） — 使用祈使句。
- 缺少保留目标 — 模型会微妙地重写面部 / 品牌标志。
- 与输入不匹配的纵横比 — 导致裁剪或拉伸。

## 此模型的优势

| 用例 | 为什么选择 Nano Banana Edit |
|---|---|
| **SKU 图库 — 同一产品在不同背景上** | 20 张批处理，身份保留，构图锁定 |
| **网红 / 品牌代言人背景替换** | 跨编辑强身份保留 |
| **空间语言保留对象移除 / 添加** | 尊重空间语言 |
| **广告创意的 A/B 变体** | 种子锁定 + 多个 `number_of_images` |
| **品牌资产重新定位** | 相同构图，文本 / 色板交换 |

## 示例提示（验证可产生强结果）

**背景替换（页面示例）：**

```
保留主体身份不变。将背景转换为雨天霓虹赛博朋克街道。
```

**目标文本替换：**

```
保留瓶子、标签和光照与输入完全一致。
仅将标签上的品牌文本从“ALPHA”更改为“AURA”，相同字体粗细，居中，白色在黑色上。
```

**多图像批量一致性：**

```
对于每个输入图像：保留主体的姿势和身份不变。
将背景转换为柔和的暖灰色工作室扫射，带有微妙的地面阴影。将主体保持在输入帧相同比例的位置。
```

## 限制

- **每次调用 1–20 张输入图像** — 第一个是主要图像；其余提供辅助提示。
- **每次调用 1–4 个输出。**
- **长复合提示漂移** — 分成多个步骤。
- **网络搜索增加延迟 + 成本** — 仅按需启用。
- **对于图像内多语言文本编辑，GPT Image 2 edit 更优。**

## 退出代码

| 代码 | 含义 |
|---|---|
| 0  | 成功 |
| 64 | 命令行参数错误 |
| 65 | 输入 JSON 错误 / 模式不匹配 |
| 69 | 上游 5xx 错误 |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或令牌被拒绝 |

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=nano-banana-edit).

## 工作原理

该技能调用 `runcomfy run google/nano-banana-2/edit` 并使用符合模式的 JSON 正文。CLI 向 `https://model-api.runcomfy.net/v1/models/google/nano-banana-2/edit` 发送 POST 请求，轮询请求，获取结果，并将 `.runcomfy.net`/`.runcomfy.com` URL 下载到 `--output-dir`。`Ctrl-C` 在退出前取消远程请求。

## 安全与隐私

- **令牌存储**：`runcomfy login` 将 API 令牌写入 `~/.config/runcomfy/token.json`，权限为 0600（仅所有者可读写）。设置 `RUNCOMFY_TOKEN` 环境变量可完全绕过文件（在 CI / 容器中）。
- **输入边界**：用户提示作为 JSON 字符串通过 `--input` 传递给 CLI。CLI 不会对提示进行 shell 扩展；它直接将 JSON 正文通过 HTTPS 传输到 Model API。提示内容不会产生 shell 注入风险。
- **第三方内容**：您传递的图像 / 掩码 / 视频URL由 RunComfy 模型服务器获取，而不是您的机器上的 CLI。将外部 URL 视为不受信任；基于图像的提示注入是任何图像编辑 / 视频编辑模型的已知风险。
- **出站端点**：仅 `model-api.runcomfy.net`（请求提交）和 `*.runcomfy.net` / `*.runcomfy.com`（生成输出的下载白名单）。无遥测数据，无回调。
- **生成文件大小上限**：CLI 会中止任何大于 2 GiB 的单个下载，以防止恶意或失控的模型输出导致磁盘填满。
