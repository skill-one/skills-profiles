# Kling 3.0 - 专业包在 RunComfy

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=kling-3-0) · [文档](https://docs.runcomfy.com/cli/introduction) · [GitHub](https://github.com/agentspace-so/runcomfy-agent-skills/tree/main/kling-3-0)

[Kling 3.0](https://www.runcomfy.com/models/kling/kling-3.0) 是快手科技出品的第三代电影级视频模型。该技能涵盖了 RunComfy 上所有六个 Kling 3.0 渲染端点：两种模式（文本到视频和图像到视频）中的三个质量等级（标准、专业、4K）。

## Kling 3.0 是什么

Kling 3.0 是 Kling 视频模型的 V3 代。它生成具有同步原生音频、跨镜头一致角色身份和物理感知运动的多镜头电影级视频。与 Kling 2.x 相比，Kling 3.0 支持更长的片段（最长15秒），4K 等级上的原生 4K 输出，以及一个统一的多个提示段系统，允许一个 Kling 3.0 生成包含多个具有可控过渡的独立场景。

Kling 3.0 在 RunComfy 上以三个渲染等级提供，每个等级都可作为文本到视频或图像到视频：

- **标准** - 最便宜等级，最高1080p输出。使用 Kling 3.0 标准，用于快速迭代、预览、A/B 变体、社交短片。
- **专业** - 1080p 最高保真度。使用 Kling V3.0 专业，用于需要最高运动真实感和身份保留的英雄级 1080p 片段。
- **4K** - 原生 3840x2160 输出。使用 Kling V3.0 4K，用于高分辨率品牌电影、大屏幕电影级序列和原生分辨率完成母带。

这三个等级共享相同的 Kling 3.0 多镜头架构。等级之间的差异在于分辨率上限、运动保真度预算和定价。

## Kling 3.0 的六个端点

每个端点对应一个（等级，模式）对。所有六个端点共享相同的 Kling 3.0 基础模型。

| 端点 | 锚点 | 分辨率 | 无音频速率 | 带音频速率 |
|---|---|---|---|---|
| `kling/kling-3.0/standard/text-to-video` | [Kling 3.0](https://www.runcomfy.com/models/kling/kling-3.0) 标准 t2v | 最高1080p | $0.084/秒 | $0.126/秒 |
| `kling/kling-3.0/standard/image-to-video` | [Kling 3.0 标准 图像到视频](https://www.runcomfy.com/models/kling/kling-3.0) | 最高1080p | $0.084/秒 | $0.126/秒 |
| `kling/kling-3.0/pro/text-to-video` | [Kling V3.0 专业 文本到视频](https://www.runcomfy.com/models/kling/kling-3.0) | 1080p | $0.112/秒 | $0.168/秒 |
| `kling/kling-3.0/pro/image-to-video` | [Kling V3.0 专业 图像到视频](https://www.runcomfy.com/models/kling/kling-3.0) | 1080p | $0.112/秒 | $0.168/秒 |
| `kling/kling-3.0/4k/text-to-video` | [Kling V3.0 4K 文本到视频](https://www.runcomfy.com/models/kling/kling-3.0) | 3840x2160 | $0.42/秒 固定 | $0.42/秒 固定 |
| `kling/kling-3.0/4k/image-to-video` | [Kling V3.0 4K 图像到视频](https://www.runcomfy.com/models/kling/kling-3.0) | 3840x2160 | $0.42/秒 固定 | $0.42/秒 固定 |

4K 等级无论是否带音频，价格都相同。标准和专业等级在启用音频时每秒收费约高50%。

## 何时选择哪个 Kling 3.0 等级

根据输出在流程中的作用选择 Kling 3.0 等级。

- **草稿、预览、社交短片、A/B 变体**：Kling 3.0 标准。最便宜。质量对于英雄镜头以外的所有内容都足够好。
- **英雄级 1080p 片段、广告创意、高运动保真度的访谈**：Kling V3.0 专业。比标准贵约33%，在相同分辨率下运动更紧密，身份保留更明显。
- **4K 品牌电影、大屏幕电影级、完成母带**：Kling V3.0 4K。原生 3840x2160（无放大步骤）。固定 $0.42/秒 使预算更可预测。仅在输出确实需要 4K 时使用——它比标准贵约5倍。

根据是否有源图像选择模式：

- **文本到视频 (t2v)**：仅提示，Kling 3.0 从头开始生成外观。使用 Kling 3.0 t2v，用于全新场景、全新构图、没有现有参考的环境。
- **图像到视频 (i2v)**：提示 + 源图像，Kling 3.0 动画化图像。当您有必须保留到输出中的精确参考（面部、产品、场景）时使用 Kling 3.0 i2v。

如果用户明确要求 Kling 3.0、Kling V3.0、Kling 专业或 Kling 4K，则无论如何都路由到此技能。

## 前置条件

1. **RunComfy CLI**：`npm i -g @runcomfy/cli`
2. **RunComfy 账户**：`runcomfy login` 打开浏览器设备码流程。
3. **CI / 容器**：设置 `RUNCOMFY_TOKEN=<token>` 而不是 `runcomfy login`。
4. **对于 i2v 端点**：一个公开可获取的源图像 URL（HTTPS，JPEG/PNG/WebP）。

## 输入模式（所有六个 Kling 3.0 端点共享）

| 字段 | 类型 | 必填 | 默认 | 备注 |
|---|---|---|---|---|
| `prompt` | 字符串 | 是 | - | 场景、运动、摄像机、氛围的文本描述。通过 `prompt_segments` 在一个 Kling 3.0 生成中支持多镜头提示，用于场景过渡。 |
| `image_url` | 字符串 | 是（i2v 仅限） | - | Kling 3.0 i2v 的源图像。HTTPS URL。JPEG/PNG/WebP。 |
| `tail_image_url` | 字符串 | 否（i2v 仅限） | - | Kling 3.0 i2v 控制从开始到结束的帧过渡的可选结束图像。 |
| `negative_prompt` | 字符串 | 否 | - | 要从 Kling 3.0 输出中排除的元素。 |
| `duration` | 整数 | 否 | 5 | 每个 Kling 3.0 生成 3-15 秒。 |
| `aspect_ratio` | 枚举 | 否 | `16:9` | `16:9`、`9:16`、`1:1`、`4:3`、`3:4`、`21:9`。 |
| `cfg_scale` | 浮点数 | 否 | 0.5 | 提示指导强度。更高 = 更严格地遵循提示。 |
| `generate_audio` | 布尔值 | 否 | false | 启用 Kling 3.0 同步音频。在标准和专业等级上增加成本；4K 上为固定费率。 |
| `seed` | 整数 | 否 | - | Kling 3.0 变体测试的可重复性。 |

## 如何调用每个 Kling 3.0 端点

**Kling 3.0 标准文本到视频（最便宜的 1080p 草稿）：**

```bash
runcomfy run kling/kling-3.0/standard/text-to-video \
  --input '{
    "prompt": "<Kling 3.0 提示>",
    "duration": 5,
    "aspect_ratio": "16:9"
  }' \
  --output-dir <绝对路径>
```

**Kling 3.0 标准图像到视频（动画静态图像）：**

```bash
runcomfy run kling/kling-3.0/standard/image-to-video \
  --input '{
    "prompt": "<Kling 3.0 i2v 的运动描述>",
    "image_url": "https://.../source.jpg",
    "duration": 5
  }' \
  --output-dir <绝对路径>
```

**Kling V3.0 专业文本到视频（最高 1080p 保真度）：**

```bash
runcomfy run kling/kling-3.0/pro/text-to-video \
  --input '{
    "prompt": "<Kling 3.0 专业提示>",
    "duration": 8,
    "aspect_ratio": "16:9",
    "generate_audio": true
  }' \
  --output-dir <绝对路径>
```

**Kling V3.0 专业图像到视频（从源图像进行英雄动画）：**

```bash
runcomfy run kling/kling-3.0/pro/image-to-video \
  --input '{
    "prompt": "<Kling V3.0 专业 i2v 的运动描述>",
    "image_url": "https://.../主体.jpg",
    "duration": 8,
    "generate_audio": true
  }' \
  --output-dir <绝对路径>
```

**Kling V3.0 4K 文本到视频（原生 4K 电影级）：**

```bash
runcomfy run kling/kling-3.0/4k/text-to-video \
  --input '{
    "prompt": "<Kling V3.0 4K 提示>",
    "duration": 10,
    "aspect_ratio": "16:9",
    "generate_audio": true
  }' \
  --output-dir <绝对路径>
```

**Kling V3.0 4K 图像到视频（参考图像的 4K 动画）：**

```bash
runcomfy run kling/kling-3.0/4k/image-to-video \
  --input '{
    "prompt": "<Kling V3.0 4K i2v 的运动描述>",
    "image_url": "https://.../source-4k.jpg",
    "duration": 10,
    "generate_audio": true
  }' \
  --output-dir <绝对路径>
```

CLI 提交 Kling 3.0 请求，每 2 秒轮询一次，获取结果，并将任何 `.runcomfy.net` / `.runcomfy.com` URL 下载到 `--output-dir`。

## Kling 3.0 提示技巧 - 哪些有效

Kling 3.0 对特定的提示模式比朴素文本响应更好。

**以运动和摄像机语言开头。** Kling 3.0 将 "广角镜头，慢速推近"、"跟拍镜头，低角度"、"手持跟拍" 作为真实指令来读取。将这些放在前面。

**在一个 Kling 3.0 生成中实现多镜头。** 单个 Kling 3.0 提示可以描述一系列镜头。编号它们："镜头 1：黄昏时咖啡馆的广角。镜头 2：中景双人镜头，举杯。镜头 3：特写女人微笑，柔和虚化，暖填充光。微妙的弦乐，轻柔的风声，远处车流声。"

**i2v 的身份锚点。** 使用 Kling 3.0 i2v 时，重申应保持稳定的内容："保留主体的面部、姿势和服装；只有摄像机移动，背景发生变化。"

**`tail_image_url` 用于控制结尾。** 在 Kling 3.0 i2v 中，提供一个尾图像以锁定最后一帧。Kling 3.0 将从源图像插值到尾图像的运动。

**`generate_audio: true` 用于单次通过对话。** 描述 Kling 3.0 应在音频中生成的内容："温暖友好的语调，英语旁白" 或 "城市环境音，远处车流声，无对话"。音频在标准和专业上增加成本；4K 上为固定费率。

**`cfg_scale` 调整。** 默认 0.5 对大多数 Kling 3.0 提示有效。提高到 0.7-0.9 以便在风格化输出上严格遵循提示。降低到 0.3-0.4 以便在提示松散时实现自然运动。

**反模式：**

- 在一个 Kling 3.0 提示中存在冲突的风格提示 -> 简化，选择一个或两个风格锚点。
- 在一个 Kling 3.0 调用中请求超过 15 秒 -> 422 错误；将脚本分割成多个 Kling 3.0 调用并拼接。
- 不支持的宽高比 -> 被拒绝。
- 对于 Kling V3.0 4K，要求激进的多镜头故事、15 秒、对话和 6 个剪辑 -> Kling 3.0 将会生成，但成本会上升到每个生成约 $6.30。先使用标准进行验证。

## Kling 3.0 的优势领域

| 用例 | 最佳 Kling 3.0 端点 |
|---|---|
| 具有一致角色的电影级 1080p 品牌故事 | Kling V3.0 专业 (t2v 或 i2v) |
| 原生 4K 英雄级电影和电影级序列 | Kling V3.0 4K (t2v 或 i2v) |
| 低价迭代、社交优先短片、A/B 变体 | Kling 3.0 标准 t2v |
| 动画品牌资产、产品照片、角色艺术 | Kling 3.0 标准 i2v 或 Kling V3.0 专业 i2v |
| 具有同步对话的单次通过多镜头广告 | Kling V3.0 专业与 `generate_audio: true` |
| 高级 4K 完成母带，带原生音频 | Kling V3.0 4K 与 `generate_audio: true` (固定费率) |

## Kling 3.0 示例提示

**Kling 3.0 电影级多镜头（推荐使用专业等级）：**

```
电影级多镜头：一对美国年轻人在烛光屋顶餐厅庆祝周年纪念。镜头 1：黄金时刻的城市天际线广角。镜头 2：中景双人镜头，举杯。镜头 3：特写女人微笑，柔和虚化，暖填充光。微妙的弦乐，轻柔的风声，远处车流声。
```

**Kling 3.0 i2v（动画肖像，4K 等级）：**

```
从源图像缓慢推近镜头。轻微的呼吸运动，身份稳定的特征，柔和的自然光，浅景深。背景：暖金色时光的柔和光晕，有缓慢漂浮的尘埃。无对话，只有房间环境音。
```

**Kling 3.0 垂直短片（标准等级，9:16）：**

```
9:16 垂直。穿着黑色围裙的咖啡师拉取单份浓缩咖啡，蒸汽升入晨光，浓郁的奶油慢慢形成。手持拍摄，浅景深，温暖的咖啡馆氛围和蒸汽喷嘴的嘶嘶声。
```

## Kling 3.0 常见问题解答

**Kling 3.0 片段的最大持续时间是多少？** 所有三个等级每个生成最多 15 秒。对于更长的叙事，将脚本分割成多个 Kling 3.0 调用并拼接。

**Kling V3.0 4K 与标准和专业相比如何定价？** Kling V3.0 4K 每秒固定 $0.42，无论是否启用音频。标准是无音频时 $0.084/秒（最便宜）。专业是无音频时 $0.112/秒。4K 等级在分辨率升级上比标准贵约 5 倍。

**Kling 3.0 支持在单个生成中实现多镜头吗？** 是的。所有 Kling 3.0 端点都接受多段提示。编号镜头（"镜头 1："、"镜头 2："等），Kling 3.0 将在它们之间保留角色身份。

**Kling 3.0 可以生成音频吗？** 是的。设置 `generate_audio: true`。Kling 3.0 在同一生成过程中生成同步对话、环境音和音乐。在 4K 上，价格保持在 $0.42/秒；在标准和专业上，启用音频时费率约增加 50%。

**Kling 3.0 支持哪些宽高比？** 16:9、9:16、1:1、4:3、3:4、21:9。4K 等级将 21:9 渲染为宽电影裁剪，原生 3840x2160。

**Kling 3.0 i2v 支持尾图像吗？** 是的。`tail_image_url` 锁定最后一帧；Kling 3.0 从源图像插值到尾图像的运动。

**Kling 3.0 与 Kling 2.x 有什么区别？** Kling 3.0 具有更强的多镜头身份保留，最大持续时间更长（15 秒，2.x 旗舰为 10 秒），4K 等级上的原生 4K，以及所有等级的统一多提示段输入。

## 限制

- **每个调用持续时间上限 15 秒** 在每个 Kling 3.0 等级上。
- **最大 6 个连续镜头** 在一个 Kling 3.0 4K 生成中。
- **i2v 需要一个公开可获取的 HTTPS 图像 URL。** 不支持本地文件。
- **宽高比是固定的** 到文档中列出的六个。其他比例会被裁剪或拒绝。
- **4K 输出文件很大。** 在批量 Kling V3.0 4K 运行之前计划磁盘和带宽。

## 退出代码

`runcomfy` CLI 使用 sysexits 风格的代码：

| 代码 | 含义 |
|---|---|
| 0  | Kling 3.0 生成成功 |
| 64 | 命令行参数错误 |
| 65 | Kling 3.0 输入 JSON 错误 / 模式不匹配 |
| 69 | 上游 5xx 错误 |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或令牌被拒绝 |

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting)。

## 工作原理

1. 技能根据用户的等级（标准 / 专业 / 4K）和模式（t2v / i2v）意图选择其中一个六个 Kling 3.0 端点。
2. 它调用 `runcomfy run kling/kling-3.0/<等级>/<模式>`，带有与模式匹配的 JSON 正文。
3. CLI 向 RunComfy 模型 API 发送 POST 请求，附带用户的令牌。
4. 模型 API 返回 `request_id`；CLI 每 2 秒轮询一次，直到 Kling 3.0 生成完成。
5. 在终端状态时，CLI 获取 Kling 3.0 结果，并将任何 `.runcomfy.net` / `.runcomfy.com` URL 下载到 `--output-dir`。
6. `Ctrl-C` 在计费之前取消正在进行的 Kling 3.0 请求。

## 安全与隐私

- **令牌存储**：`runcomfy login` 将 API 令牌写入 `~/.config/runcomfy/token.json`，权限为 0600。在 CI / 容器中设置 `RUNCOMFY_TOKEN` 环境变量。
- **输入边界**：Kling 3.0 提示作为 JSON 通过 `--input` 传递。CLI 不进行 shell 扩展。没有 shell 注入表面。
- **第三方内容**：您传递的图像 URL 由 RunComfy 服务器获取，而不是您的机器上的 CLI。将外部 URL 视为不受信任；基于图像的提示注入是任何接受图像输入的视频模型的已知风险。
- **出站端点**：仅 `model-api.runcomfy.net`（请求提交）和 `*.runcomfy.net` / `*.runcomfy.com`（下载白名单）。
- **生成文件大小上限**：CLI 中止任何大于 2 GiB 的单个下载，以防止 Kling 3.0 4K 输出导致磁盘填满。
