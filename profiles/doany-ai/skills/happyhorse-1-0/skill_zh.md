# HappyHorse 1.0 — RunComfy上的专业包

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=happyhorse-1-0) · [文本转视频](https://www.runcomfy.com/models/happyhorse/happyhorse-1-0/text-to-video?utm_source=skills.sh&utm_medium=skill&utm_campaign=happyhorse-1-0) · [GitHub](https://github.com/agentspace-so/runcomfy-skills/tree/main/happyhorse-1-0)

**HappyHorse 1.0** — 目前在人工智能分析视频竞技场中排名第一（Elo 1333 t2v / 1392 i2v）— 在**RunComfy模型API**上运行。原生1080p视频，具有**同步音频**（对话、环境音、音效）和多镜头角色一致性。

```bash
npx skills add agentspace-so/runcomfy-skills --skill happyhorse-1-0 -g
```

## 选择此模型的时机（与同类模型对比）

| 您需要 | 使用 |
|---|---|
| 多镜头故事中具有角色/服装一致性 | **HappyHorse 1.0** |
| 同一生成过程中具有原生音频 | **HappyHorse 1.0** |
| 目前排名第一的盲选视频模型 | **HappyHorse 1.0** |
| 详细唇同步对话 + 参考视频 | Seedance 2.0 Pro |
| 精细运动控制 + 多参考条件 | Wan 2.7 |
| 超快迭代（每帧亚秒级） | LTX 2 |
| 对现有素材进行电影级运动编辑 | Kling Video O1 |

如果用户明确提到“HappyHorse” / “happy horse video”，则无论何种情况都路由至此。

## 前置条件

1. **RunComfy CLI** — `npm i -g @runcomfy/cli`
2. **RunComfy账户** — `runcomfy login` 会打开一个浏览器设备码流程。
3. **CI / 容器** — 设置 `RUNCOMFY_TOKEN=<token>` 而不是 `runcomfy login`。

## 端点 + 输入模式

### `happyhorse/happyhorse-1-0/text-to-video`

| 字段 | 类型 | 必填 | 默认 | 备注 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 最多2,500字符。6种语言（CN/EN/JP/KR/DE/FR）。 |
| `aspect_ratio` | enum | 否 | `16:9` | `16:9`, `9:16`, `1:1`, `4:3`, `3:4` 仅限这些值。 |
| `resolution` | enum | 否 | `1080P` | `720P` 或 `1080P`。 |
| `duration` | int | 否 | 5 | 3–15秒。 |
| `seed` | int | 否 | 0 | 0..2^31-1。为变体比较重复使用。 |
| `watermark` | bool | 否 | true | 提供商水印。 |

## 如何调用

**默认（16:9 1080p 5秒）：**

```bash
runcomfy run happyhorse/happyhorse-1-0/text-to-video \
  --input '{"prompt": "<用户提示>"}' \
  --output-dir <绝对路径>
```

**竖屏短视频（9:16, 8秒, 无水印）：**

```bash
runcomfy run happyhorse/happyhorse-1-0/text-to-video \
  --input '{
    "prompt": "<用户提示>",
    "aspect_ratio": "9:16",
    "duration": 8,
    "watermark": false
  }' \
  --output-dir <绝对路径>
```

**更便宜的测试通过（720p）：**

```bash
runcomfy run happyhorse/happyhorse-1-0/text-to-video \
  --input '{"prompt": "<用户提示>", "resolution": "720P", "duration": 3}' \
  --output-dir <绝对路径>
```

CLI提交，每2秒轮询一次直到终端，然后从结果中下载任何 `*.runcomfy.net` / `*.runcomfy.com` URL到 `--output-dir`。标准输出是结果JSON。标准错误是进度。

## 提示 — 实际有效的部分

**描述随时间变化的动作，而不是静态画面。** “一位女士从窗户转身，走两步到书桌旁，拿起杯子，举到脸上，喝了一口” 比 “一位女士在喝咖啡” 更好。

**用普通英语描述相机和镜头。** 先加载镜头：`"广角镜头。..."` / `"跟踪镜头。..."` / `"固定三脚架，低角度。..."` 作为真实指令工作。指定镜头感觉：`"35mm变形镜头"`，`"浅景深"`，`"压缩阴影"`。

**迭代时每个片段一个视觉节奏。** 不要堆积“她走路 AND 狗跑 AND 车经过”。选择节奏，使其清晰，然后用多镜头提示叠加。

**多镜头一致性** — 当描述两个节奏时，在每个节奏中重述锚点：`"镜头1：高个红毛衣女士，蓝色围巾，在雨中巷子里。镜头2：同一位女士穿着红毛衣 / 蓝色围巾，现在在屋檐下躲避。"` HappyHorse保持外观，但需要锚点。

**音频方向** — 说明你想要听到的内容：`"远处寺庙钟声，湿路面脚步声，无对话"` 或 `"温暖友好的语调，英语"`。

**反模式：**
- 静态帧描述（无时间动词）→ 运动将模糊。
- 冲突的风格方向 → 取消。
- > 2500字符的提示 → 退化。
- 5种支持范围之外的宽高比 → 422。

## 优势领域

| 用例 | 为什么选择HappyHorse 1.0 |
|---|---|
| **多镜头品牌故事中具有一个一致的角色** | 原生跨镜头身份保留 |
| **需要视频中唇同步配音 + 环境音的访谈式解说** | 同一通过中同步音频 |
| **多语言短视频广告** | 6种提示语言，无脚本质量下降 |
| **电影级1080p交付** | 原生1080p输出，广播级 |
| **盲选领导者，用于一般视频质量** | 在人工智能分析视频竞技场中排名第一 |

## 示例提示（验证可产生强力结果）

**从模型页面（电影范围）：**

```
广角镜头。一位穿着橙色套服和蓝灰色背心的孤独宇航员
在月球平原上滑雪，留下平行轨迹在灰色土壤中。
中途，插上杆，在1/6重力下推，有轻微向上漂浮。滑雪轨迹沿线的细尘雾。
月球地平线上方的半月地球，蓝白色光芒在黑色天空中。原始阳光，压缩阴影，无补光。8K照片级真实感。
```

**多镜头一致性：**

```
镜头1：中景特写。一位穿着海军夹克的女士进入雨滑的东京霓虹灯巷子，向左看，举起雨伞。
镜头2：同一位女士穿着相同的海军夹克，现在在拉面店的屋檐下，抖落雨伞上的水。温暖的室内光线，柔和的交谈，金属屋顶上轻柔的雨声在音频中。
```

**竖屏平台原生：**

```
9:16竖屏短视频。一位穿着黑色围裙的咖啡师拉出一杯浓缩咖啡，蒸汽升起进入晨光，浓郁的奶油慢慢形成。手持特写，浅景深，温暖咖啡馆氛围和蒸汽喷嘴的嘶嘶声。
```

## 限制

- **时长上限15秒** — 对于更长的叙事，分段为多镜头提示并拼接。
- **宽高比** — 仅支持5种记录值；超宽电影级会裁剪或拒绝。
- **音频仅限通过中** — 你不能传递外部音频来驱动唇同步。对于音频驱动唇同步，使用Wan 2.7（它接受一个 `audio_url`）或Seedance 2.0 Pro。
- **此模板无免费图像转视频** — i2v由HappyHorse通过单独的管道支持；此处t2v端点是纯文本。

## 退出代码

`runcomfy` CLI使用sysexits风格的代码：

| 代码 | 含义 |
|---|---|
| 0  | 成功 |
| 64 | 命令行参数错误 |
| 65 | 输入JSON错误 / 模式不匹配（例如 `duration: 30` 会422） |
| 69 | 上游5xx |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或令牌被拒绝 |

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=happyhorse-1-0).

## 工作原理

1. 技能调用 `runcomfy run happyhorse/happyhorse-1-0/text-to-video` 并使用符合模式的JSON体。
2. CLI POST到 `https://model-api.runcomfy.net/v1/models/happyhorse/happyhorse-1-0/text-to-video` 并使用用户的bearer令牌。
3. 模型API返回一个 `request_id`；CLI每2秒轮询 `GET .../requests/<id>/status`。
4. 在终端状态下，CLI获取 `GET .../requests/<id>/result` 并下载任何主机以 `.runcomfy.net` 或 `.runcomfy.com` 结尾的URL到 `--output-dir`。其他URL会列出但不会下载。
5. 轮询时按 `Ctrl-C` 发送 `POST .../requests/<id>/cancel`，这样你就不会为停止的GPU付费。

## 这项技能不是什么

不是自托管视频运行器。不是能力授权 — 依赖于一个有效的RunComfy账户。

## 安全与隐私

- **令牌存储**：`runcomfy login` 将API令牌写入 `~/.config/runcomfy/token.json`，权限为0600（仅所有者可读写）。设置 `RUNCOMFY_TOKEN` 环境变量以在CI / 容器中完全绕过文件。
- **输入边界**：用户提示作为JSON字符串通过 `--input` 传递给CLI。CLI不会对提示进行shell扩展；它直接将JSON体通过HTTPS传输到模型API。提示内容没有shell注入表面。
- **第三方内容**：你传递的图像/蒙版/视频URL由RunComfy模型服务器获取，而不是你的机器上的CLI。将外部URL视为不受信任；基于图像的提示注入是任何图像编辑/视频编辑模型的已知风险。
- **出站端点**：仅 `model-api.runcomfy.net`（请求提交）和 `*.runcomfy.net` / `*.runcomfy.com`（生成输出的下载白名单）。无遥测，无回调。
- **生成文件大小上限**：CLI中止任何单个下载 > 2 GiB，以防止恶意或失控的模型输出导致磁盘填满。
