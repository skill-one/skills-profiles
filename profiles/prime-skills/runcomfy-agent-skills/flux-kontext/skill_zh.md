# Flux Koncontext Pro — RunComfy 平台上的 Pro Pack

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=flux-koncontext) · [模型页面](https://www.runcomfy.com/models/blackforestlabs/flux-1-koncontext-pro/image-to-image?utm_source=skills.sh&utm_medium=skill&utm_campaign=flux-koncontext) · [GitHub](https://github.com/agentspace-so/runcomfy-skills/tree/main/flux-koncontext)

Black Forest Labs 的 **Flux 1 Koncontext Pro** —— 单参考精确本地图片编辑 —— 部署于 **RunComfy 模型 API**。具备强大的提示词控制、一致的结果输出与高保真度。

```bash
npx skills add agentspace-so/runcomfy-skills --skill flux-koncontext -g
```

## 何时选择此模型（与同类模型对比）

| 你需要的 | 使用 |
|---|---|
| 单张图片精确本地编辑（"她现在拿着 X"） | **Flux Koncontext** |
| 高保真保留源图特征 | **Flux Koncontext** |
| 1–20 张图片批量编辑 | Nano Banana Edit |
| 编辑图片中的多语言 / 嵌入文本 | GPT Image 2 edit |
| 从零生成，无源图 | Flux 2 Klein |

若用户明确提及 "Flux Koncontext" / "koncontext" / "BFL Koncontext"，无论其他条件，均直接路由至此。

## 前置条件

1. **RunComfy CLI** — `npm i -g @runcomfy/cli`
2. **RunComfy 账户** — `runcomfy login` 会打开浏览器设备码流程。
3. **CI / 容器** — 设置 `RUNCOMFY_TOKEN=<token>` 以替代 `runcomfy login`。

## 接口端点 + 输入模式

### `blackforestlabs/flux-1-koncontext/pro/edit`

| 字段 | 类型 | 是否必填 | 默认值 | 备注 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 单条明确编辑指令。 |
| `image` | string | 是 | — | 单张源图 URL（可公开获取的 HTTPS）。 |
| `aspect_ratio` | enum | 否 | (输入) | 在模型页面中选择支持的 W:H 选项之一。 |
| `seed` | int | 否 | — | 用于变体对比。 |

模式设计刻意保持精简 —— Koncontext 依赖提示词与单张参考。如需多图或基于网页的编辑，请路由至 Nano Banana Edit。

## 如何调用

**默认 —— 本地编辑，保留其余内容不变：**

```bash
runcomfy run blackforestlabs/flux-1-koncontext/pro/edit \
  --input '{
    "prompt": "Keep the person'\''s face, pose, and clothing unchanged. Add an orange umbrella in her left hand and a slight smile.",
    "image": "https://.../portrait.jpg"
  }' \
  --output-dir <absolute/path>
```

**通过 seed 生成可复现的变体系列：**

```bash
runcomfy run blackforestlabs/flux-1-koncontext/pro/edit \
  --input '{
    "prompt": "Keep the bottle, label, and lighting unchanged. Replace the brand text on the label from \"ALPHA\" to \"AURA\".",
    "image": "https://.../bottle.jpg",
    "seed": 42
  }' \
  --output-dir <absolute/path>
```

## 提示词编写 —— 实用技巧

**单条明确指令。** Koncontext 在形如官方文档示例的提示词上表现最佳，例如：`"She is now holding an orange umbrella and smiling"`。使用祈使语气，只表达一处更改。

**优先保证保留。** 以 `"Keep [身份 / 姿态 / 构图 / 品牌] unchanged."` 开头，再接更改内容。模型会优先遵循提前明确的保留要求。

**仅使用单张参考 —— 选择正确的参考图。** 此处不支持多图分发。若有多张参考，需决定主参考图并仅传入该张。多图流程请路由至 Nano Banana Edit。

**针对小幅调整进行迭代。** 若 Koncontext 出现偏差，将复合编辑拆分为多次顺序的单指令操作（第 1 步：更改背景，第 2 步：更改服装）。

**宽高比 —— 从支持的枚举中选择。** 未在列表中的值将返回 422 或进行裁剪。

**反模式：**
- 复合提示词（"change A and add B and remove C"）→ 会导致偏差。
- 尝试分发到多张源图 → 使用错误的模型（请使用 Nano Banana Edit）。
- 使用被动语态编写提示词 → 可靠性较低。
- 要求在不提供源图的情况下进行全新构图 → 使用错误的模型（请使用 Flux 2 Klein t2i）。

## 适用场景

| 使用场景 | Flux Koncontext 的优势 |
|---|---|
| **单次精确本地编辑** | 专为该类场景设计，保真度高 |
| **在针对性更改中保留源图特征** | 在明确指令下实现强大的保留能力 |
| **品牌资产文字或颜色替换** | 引述文字 + 保留引导句效果良好 |
| **单图快速迭代** | 短提示词 + 单张参考 = 快速的结果迭代流程 |

## 示例提示词（经验证可产生优质结果）

**页面示例：**

```
She is now holding an orange umbrella and smiling
```

**以保留为先的品牌编辑：**

```
Keep the bottle silhouette, table, and lighting exactly as in the input.
Replace only the brand text on the label, from "ALPHA" to "AURA".
Same font weight, white on black, centered.
```

**构图微调：**

```
Keep the person's face, pose, and clothing unchanged. Add a leather
shoulder bag, dark brown, hanging on the right shoulder.
```

## 局限性

- **仅支持单张源图。** 多图流程请使用 Nano Banana Edit（支持 1–20 张）。
- **RunComfy 公开文档较为精简** —— schema 字段除 prompt、image、aspect_ratio 与 seed 外可能存在；请查看 [模型页面](https://www.runcomfy.com/models/blackforestlabs/flux-1-koncontext-pro/image-to-image?utm_source=skills.sh&utm_medium=skill&utm_campaign=flux-koncontext) 获取最新字段列表。
- **复合提示词会导致偏差** —— 请拆分为多次顺序操作。
- **编辑多语言 / 嵌入文本时，GPT Image 2 edit 通常更优。**

## 退出码

| code | 含义 |
|---|---|
| 0 | 成功 |
| 64 | CLI 参数错误 |
| 65 | 输入 JSON 错误 / 模式不匹配 |
| 69 | 上游 5xx |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或令牌被拒绝 |

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=flux-koncontext)。

## 工作原理

该技能调用 `runcomfy run blackforestlabs/flux-1-koncontext/pro/edit`，传入匹配 schema 的 JSON 请求体。CLI 向 `https://model-api.runcomfy.net/v1/models/blackforestlabs/flux-1-koncontext/pro/edit` 发起 POST 请求，轮询请求状态，获取结果，并将任何 `.runcomfy.net` / `.runcomfy.com` 链接下载至 `--output-dir`。退出前按 `Ctrl-C` 可取消远程请求。

## 安全与隐私

- **令牌存储**：`runcomfy login` 将 API 令牌写入 `~/.config/runcomfy/token.json`，权限设置为 0600（仅所有者可读写）。在 CI / 容器中可设置 `RUNCOMFY_TOKEN` 环境变量以完全绕过文件写入。
- **输入边界**：用户提示词通过 `--input` 作为 JSON 字符串传递给 CLI。CLI 不会对提示词进行 shell 展开，而是直接将 JSON 请求体通过 HTTPS 传输至模型 API。提示词内容不存在 shell 注入风险。
- **第三方内容**：您传入的图像 / 遮罩 / 视频 URL 由 RunComfy 模型服务器抓取，而非您的本地 CLI 抓取。请将外部 URL 视为不可信；基于图像提示词注入是任何图像编辑 / 视频编辑模型均已知的风险。
- **出站端点**：仅 `model-api.runcomfy.net`（请求提交）以及 `*.runcomfy.net` / `*.runcomfy.com`（生成结果的下载白名单）。无遥测，无回调。
- **生成文件大小上限**：CLI 会中止任何单个下载大于 2 GiB 的操作，以防止恶意或失控模型输出导致磁盘填充。
