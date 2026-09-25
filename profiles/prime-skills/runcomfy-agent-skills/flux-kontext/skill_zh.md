# Flux Kontext Pro — Pro Pack on RunComfy

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=flux-kontext) · [模型页面](https://www.runcomfy.com/models/blackforestlabs/flux-1-kontext-pro/image-to-image?utm_source=skills.sh&utm_medium=skill&utm_campaign=flux-kontext) · [GitHub](https://github.com/agentspace-so/runcomfy-skills/tree/main/flux-kontext)

Black Forest Labs 的 **Flux 1 Kontext Pro** — 单参考精确局部图像编辑 — 在 **RunComfy 模型 API** 上托管。强大的提示控制，一致的输出，高保真度。

```bash
npx skills add agentspace-so/runcomfy-skills --skill flux-kontext -g
```

## 何时选择此模型（与兄弟模型对比）

| 您想要 | 使用 |
|---|---|
| 单图像精确局部编辑（“她现在拿着 X”） | **Flux Kontext** |
| 高保真度保留源身份 | **Flux Kontext** |
| 1–20 图像的批量编辑 | Nano Banana Edit |
| 编辑图像中的多语言/嵌入文本 | GPT Image 2 编辑 |
| 从头生成，无源图像 | Flux 2 Klein |

如果用户明确说了“Flux Kontext” / “kontext” / “BFL Kontext”，无论什么情况都路由到这里。

## 前置条件

1. **RunComfy CLI** — `npm i -g @runcomfy/cli`
2. **RunComfy 账户** — `runcomfy login` 会打开一个浏览器设备码流程。
3. **CI / 容器** — 设置 `RUNCOMFY_TOKEN=<token>` 而不是 `runcomfy login`。

## 端点 + 输入模式

### `blackforestlabs/flux-1-kontext/pro/edit`

| 字段 | 类型 | 必填 | 默认 | 备注 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 单个声明性编辑指令。 |
| `image` | string | 是 | — | 单个源图像 URL（可公开获取的 HTTPS）。 |
| `aspect_ratio` | enum | 否 | (输入) | 从模型页面上的支持 W:H 选项中选择。 |
| `seed` | int | 否 | — | 用于变体比较时重复使用。 |

模式故意保持最小化 — Kontext 依赖提示 + 单参考。对于多图像或基于网络的编辑，路由到 Nano Banana Edit。

## 如何调用

**默认 — 本地编辑，保留所有其他内容：**

```bash
runcomfy run blackforestlabs/flux-1-kontext/pro/edit \
  --input '{
    "prompt": "保持人物的面部、姿势和服装不变。在她的左手添加一把橙色雨伞，并露出轻微的微笑。",
    "image": "https://.../portrait.jpg"
  }' \
  --output-dir <绝对路径>
```

**带种子以实现可重复的变体系列：**

```bash
runcomfy run blackforestlabs/flux-1-kontext/pro/edit \
  --input '{
    "prompt": "保持瓶子、标签和光照不变。将标签上的品牌文字从 \"ALPHA\" 替换为 \"AURA\"。",
    "image": "https://.../bottle.jpg",
    "seed": 42
  }' \
  --output-dir <绝对路径>
```

## 提示 — 实际有效的部分

**一个声明性指令。** Kontext 在文档示例形状的提示上表现最佳：`"她现在拿着一把橙色雨伞并微笑"`。祈使语气，单一变化。

**优先保留。** 首先使用 `"保持 [身份 / 姿势 / 构图 / 品牌] 不变。"` 然后是变化。模型会尊重前面声明的部分。

**仅单参考 — 选择正确的参考。** 这里没有多图像分叉。如果您有多个参考，请决定哪个是主要的，并传递那个。对于多图像流程，路由到 Nano Banana Edit。

**逐步进行小变化。** 如果 Kontext 偏移，将复合编辑拆分为顺序单指令传递（传递 1：改变背景，传递 2：改变服装）。

**宽高比 — 从支持的枚举中选择。** 列表外值 422 或裁剪。

**反模式：**
- 复合提示（“改变 A 并添加 B 并删除 C”）→ 偏移。
- 尝试分叉到多个源图像 → 错误模型（使用 Nano Banana Edit）。
- 使用被动语气的提示 → 可靠性较低。
- 没有源图像请求新构图 → 错误模型（使用 Flux 2 Klein t2i）。

## 它的优势

| 用例 | 为什么选择 Flux Kontext |
|---|---|
| **单次精确局部编辑** | 专为这个设计；高保真度 |
| **通过目标变化保留源身份** | 在明确指令下强保留 |
| **品牌资产文本或颜色替换** | 引用文本 + 保留引导效果良好 |
| **对单图像快速迭代** | 短提示 + 单参考 = 快速结果循环 |

## 示例提示（验证可产生强力结果）

**页面示例：**

```
她现在拿着一把橙色雨伞并微笑
```

**以保留为主导的品牌编辑：**

```
保持瓶子轮廓、桌子、光照与输入完全一致。
仅替换标签上的品牌文字，从 "ALPHA" 替换为 "AURA"。
相同的字体粗细，白色在黑色上，居中。
```

**构图微编辑：**

```
保持人物的面部、姿势和服装不变。在右肩添加一个棕色皮革肩包。
```

## 限制

- **仅限单个源图像。** 对于多图像流程，使用 Nano Banana Edit（1–20）。
- **公共 RunComfy 文档很少** — 模式字段可能存在 prompt + image + aspect_ratio + seed 之外的字段；检查 [模型页面](https://www.runcomfy.com/models/blackforestlabs/flux-1-kontext-pro/image-to-image?utm_source=skills.sh&utm_medium=skill&utm_campaign=flux-kontext) 获取最新字段列表。
- **复合提示偏移** — 分为顺序传递。
- **对于多语言/嵌入文本编辑，GPT Image 2 编辑通常更优。**

## 退出代码

| 代码 | 含义 |
|---|---|
| 0  | 成功 |
| 64 | 命令行参数错误 |
| 65 | 输入 JSON 错误 / 模式不匹配 |
| 69 | 上游 5xx |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或令牌被拒绝 |

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=flux-kontext).

## 工作原理

技能调用 `runcomfy run blackforestlabs/flux-1-kontext/pro/edit` 并使用匹配模式的 JSON 正文。CLI POST 到 `https://model-api.runcomfy.net/v1/models/blackforestlabs/flux-1-kontext/pro/edit`，轮询请求，获取结果，并将 `.runcomfy.net`/`.runcomfy.com` URL 下载到 `--output-dir`。`Ctrl-C` 在退出前取消远程请求。

## 安全与隐私

- **令牌存储**：`runcomfy login` 将 API 令牌写入 `~/.config/runcomfy/token.json`，权限为 0600（仅所有者可读写）。设置 `RUNCOMFY_TOKEN` 环境变量可完全绕过文件，适用于 CI / 容器。
- **输入边界**：用户提示作为 JSON 字符串通过 `--input` 传递给 CLI。CLI 不会 shell 扩展提示；它直接将 JSON 正文传输到 Model API。提示内容没有 shell 注入表面。
- **第三方内容**：您传递的图像 / 掩码 / 视频将通过 RunComfy 模型服务器获取，而不是在您的机器上通过 CLI 获取。将外部 URL 视为不受信任；基于图像的提示注入是任何图像编辑 / 视频编辑模型的已知风险。
- **出站端点**：仅 `model-api.runcomfy.net`（请求提交）和 `*.runcomfy.net` / `*.runcomfy.com`（下载白名单，用于生成输出）。没有遥测，没有回调。
- **生成文件大小上限**：CLI 会中止任何大于 2 GiB 的单个下载，以防止恶意或失控的模型输出导致磁盘填满。
