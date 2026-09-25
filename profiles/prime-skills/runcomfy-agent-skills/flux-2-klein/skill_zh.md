# Flux 2 Klein — Pro Pack 在 RunComfy

[runcomfy.com](https://www.runcomfy.com/?utm_source=skills.sh&utm_medium=skill&utm_campaign=flux-2-klein) · [9B 模型](https://www.runcomfy.com/models/blackforestlabs/flux-2-klein/9b/text-to-image?utm_source=skills.sh&utm_medium=skill&utm_campaign=flux-2-klein) · [4B 模型](https://www.runcomfy.com/models/blackforestlabs/flux-2-klein/4b/text-to-image?utm_source=skills.sh&utm_medium=skill&utm_campaign=flux-2-klein) · [GitHub](https://github.com/agentspace-so/runcomfy-skills/tree/main/flux-2-klein)

Black Forest Labs 的 **Flux 2 Klein**（Flux 2 的精炼、低延迟版本）托管在 **RunComfy 模型 API** 上——无需 API 密钥，异步 REST。

```bash
npx skills add agentspace-so/runcomfy-skills --skill flux-2-klein -g
```

## 何时选择此模型（与兄弟模型对比）

Flux 2 Klein 的独特优势是 **以延迟优先的创意迭代**：亚秒级的反馈支持实时艺术指导会话和快速产品可视化，而批量式模型无法持续维持。选择它时，**迭代速度比极限分辨率更重要**。

| 您想要 | 使用 |
|---|---|
| 实时 / 实时艺术指导会话 | **Flux 2 Klein 4B** |
| 快速迭代，最后具有强细节 | **Flux 2 Klein 9B** |
| 多参考品牌风格，保持一致性外观 | **Flux 2 Klein** |
| 2K–4K 英雄图像，最大分辨率 | Seedream 5 |
| 最大提示符遵循 + 极端细节 | Flux 2 Pro |
| 嵌入文本、标志、多语言标识 | GPT Image 2 |
| 超写实肖像 | Nano Banana Pro |

如果用户明确提到 "Flux 2 Klein" / "BFL Klein" / "flux klein"，则无论他们是否提到 "Flux 2" 都应路由到此。如果他们泛指 "Flux 2"，则应在默认之前询问他们是否想要 **Klein**（快速）或 **Pro**（最高质量）。

## 前置条件

1. **RunComfy CLI** — `npm i -g @runcomfy/cli`
2. **RunComfy 账户** — `runcomfy login` 会打开一个浏览器设备码流程。
3. **CI / 容器** — 设置 `RUNCOMFY_TOKEN=<token>` 而不是 `runcomfy login`。

## 端点 + 输入模式

两个变体，相同的端点形状，相同的提示语法。

### `blackforestlabs/flux-2-klein/9b/text-to-image`

高保真度优先变体。用于润色 / 最终输出。

| 字段 | 类型 | 必填 | 默认 | 备注 |
|---|---|---|---|---|
| `prompt` | string | 是 | — | 最高约 512 个 token。更长会降低质量。 |
| `steps` | int | 否 | 25 | 4–50。**步数精炼架构**——4–8 足够用于构思；~25 用于润色；>25 购买不到多少。 |
| `width` | int | 否 | 1024 | 512–1536 典型。**宽高比上限为 16:9**，最大约 2K 总计。 |
| `height` | int | 否 | 1024 | 匹配 `width` 的宽高意图。 |

### `blackforestlabs/flux-2-klein/4b/text-to-image`

延迟优先变体。亚秒级 4 步推理。用于实时迭代 / 构思。

与 9B 相同的字段集。默认 `steps` 实际上是 4——此变体是为该步数构建的。

### 参考图像（两个变体）

最多支持 **4 个同时的参考图像** 在同一端点上用于风格迁移 / 指导构图。JSON 体的确切字段名在 [模型的 API 标签](https://www.runcomfy.com/models/blackforestlabs/flux-2-klein/9b/text-to-image?utm_source=skills.sh&utm_medium=skill&utm_campaign=flux-2-klein) 上有记录——通过 CLI 原样传递。参考图像的使用支持编辑式工作流，无需单独的 `/edit` 端点。

## 如何调用

**快速构思（4B，亚秒级）：**

```bash
runcomfy run blackforestlabs/flux-2-klein/4b/text-to-image \
  --input '{"prompt": "<用户提示>"}' \
  --output-dir <绝对路径>
```

**润色 / 最终（9B，~25 步）：**

```bash
runcomfy run blackforestlabs/flux-2-klein/9b/text-to-image \
  --input '{
    "prompt": "<用户提示>",
    "steps": 25,
    "width": 1024,
    "height": 1024
  }' \
  --output-dir <绝对路径>
```

**宽格式海报：**

```bash
runcomfy run blackforestlabs/flux-2-klein/9b/text-to-image \
  --input '{"prompt": "<用户提示>", "width": 1536, "height": 864}' \
  --output-dir <绝对路径>
```

CLI 提交，每 2 秒轮询一次直到终端，然后将任何 `*.runcomfy.net` / `*.runcomfy.com` URL 下载到 `--output-dir`。标准输出是结果 JSON。标准错误是进度。

对于管道友好使用：

```bash
runcomfy --output json run blackforestlabs/flux-2-klein/4b/text-to-image \
  --input '{"prompt":"..."}' --no-wait | jq -r .request_id
```

## 提示——实际有效的内容

这些是特定于模型的模式，可以实际提高输出质量。

**主语优先的声明式语法**。Flux 2 Klein 训练的结构是 *"主语 + 动作 + 场景 + 风格 + 光照 + 相机 + 质量"*。前置主语；以指令结尾。示例：`"一只充满活力的蜂鸟在飞行中吸食鲜艳的粉色木槿花的花蜜，翠绿和蓝宝石羽毛在晨光中闪烁，浅景深热带花园背景，微距摄影，锐利细节，电影级光照"`。

**具体性胜过华丽的语言**。"4k 产品照片，柔光箱光照，反光桌面，35mm，f/2.8" 指导具有可预测性。"一个真的很漂亮的产品图像" 则没有。

**按阶段调整步数**。
- **构思**：4–8 步在 4B 变体上——亚秒级反馈用于实时探索。
- **细化**：4B 上的 8–15 步，锁定主体 + 构图。
- **润色**：9B 变体上的 ~25 步——纹理，微观细节，精细排版。

**多参考图像对齐**。当传递参考图像时，**保持它们的审美一致**。在同一调用中混合水彩 + 照片真实 + 3D 渲染会使编辑器困惑。在所有参考中保持一致的视觉注册。

**条件编辑**：先说明什么保持不变，再说明什么改变。*"与参考图像相同的构图和光照，但将背景从海滩改为山地工作室。"* 此模式保持构图稳定。

**对于文本渲染**（Klein 拥有 8B Qwen3 嵌入器，不错但不如 GPT Image 2）：添加 `"清晰的排版，高对比度标签"` 并将步数增加到 ~25，如果文本出来是模糊的。对于图像中的文本或多语言渲染，改为 GPT Image 2。

**反模式**：

- 不要冲突形容词。"极简 + 华丽" 会抵消。
- 不要超过 ~512 个 token。模型会降低质量，不会优雅地截断。
- 不要要求 4K——模型的分辨率上限是 ~2K。
- 不要要求超宽 (>16:9)——模型会裁剪。

## 此模型的优势

| 用例 | 为什么 Flux 2 Klein |
|---|---|
| **实时艺术指导会话** | 亚秒级反馈 (4B) 支持实时迭代 |
| **交互式产品可视化** | 快速 UI 预览和产品组合，无需批量等待 |
| **多参考品牌风格** | 参考之间风格一致性强，用于统一资源包 |
| **快速构思 → 润色工作流** | 4B 用于探索，9B 用于最终处理——整个提示语法保持一致 |
| **消费者 GPU 友好推理** | 4B 变体可在普通硬件上运行；对于自托管比较相关，但 RunComfy 托管即可 |

## 示例提示（验证可产生强结果）

**来自模型页面（BFL 示例）：**

```
一只充满活力的蜂鸟在飞行中吸食鲜艳的粉色木槿花
花蜜，翠绿和蓝宝石羽毛在晨光中闪烁，
浅景深热带花园背景，微距摄影，锐利
细节，电影级光照
```

**产品照片模式：**

```
一个磨砂陶瓷马克杯放在回收木材桌子上，
左侧柔和的北窗光照，浅景深，50mm 定焦镜头，
f/2.0，中性背景，电商准备，4K 产品摄影
```

**品牌一致对（多参考）：**

```
与参考图像相同的构图和光照，但瓶标现在是蓝色，
带有白色无衬线字体，阅读 "AURA"；
保持瓶身轮廓、桌子、阴影与参考完全一致
```

## 限制

- **分辨率上限 ~2K**——对于更高原生分辨率，路由到 Seedream 5。
- **宽高比上限 16:9**——极端宽/高比会被裁剪。
- **提示符上限 ~512 token**——更长会降低质量；不会优雅地截断。
- **参考图像上限 4**——超过 4 会增加延迟并稀释指导。
- **文本渲染**——8B Qwen3 嵌入器有所帮助，但 GPT Image 2 仍胜于嵌入文本精度。

## 退出代码

`runcomfy` CLI 使用 sysexits 风格代码：

| 代码 | 含义 |
|---|---|
| 0  | 成功 |
| 64 | 坏 CLI 参数 |
| 65 | 坏输入 JSON / 模式不匹配（例如 `width: 4096` 会 422） |
| 69 | 上游 5xx |
| 75 | 可重试：超时 / 429 |
| 77 | 未登录或令牌被拒绝 |

完整参考：[docs.runcomfy.com/cli/troubleshooting](https://docs.runcomfy.com/cli/troubleshooting?utm_source=skills.sh&utm_medium=skill&utm_campaign=flux-2-klein)。

## 工作原理

1. 技能调用 `runcomfy run blackforestlabs/flux-2-klein/<变体>/text-to-image` 并使用匹配模式的 JSON 正文。
2. CLI POST 到 `https://model-api.runcomfy.net/v1/models/blackforestlabs/flux-2-klein/<变体>/text-to-image` 并使用用户的令牌。
3. 模型 API 返回 `request_id`；CLI 每 2 秒轮询一次 `GET .../requests/<id>/status`。
4. 终端状态时，CLI 获取 `GET .../requests/<id>/result` 并将任何主机以 `.runcomfy.net` 或 `.runcomfy.com` 结尾的 URL 下载到 `--output-dir`。其他 URL 被列出但不会获取。
5. `Ctrl-C` 时轮询会发送 `POST .../requests/<id>/cancel`，因此您不会为停止的 GPU 付费。

## 此技能不是什么

不是自托管的 Flux 运行器。不是能力授予——取决于可工作的 RunComfy 账户。不是多租户。

## 安全与隐私

- **令牌存储**：`runcomfy login` 将 API 令牌写入 `~/.config/runcomfy/token.json`，模式为 0600（仅所有者可读写）。设置 `RUNCOMFY_TOKEN` 环境变量以在 CI / 容器中绕过文件。
- **输入边界**：用户提示作为 JSON 字符串通过 `--input` 传递给 CLI。CLI **不会**展开提示；它将 JSON 正文直接通过 HTTPS 传输到模型 API。提示内容没有 shell 注入表面。
- **第三方内容**：您传递的图像 / 掩码 / 视频URL 由 RunComfy 模型服务器获取，而不是您的机器上的 CLI。将外部 URL 视为不受信任；基于图像的提示注入是任何图像编辑 / 视频编辑模型的已知风险。
- **出站端点**：仅 `model-api.runcomfy.net`（请求提交）和 `*.runcomfy.net` / `*.runcomfy.com`（下载白名单，用于生成的输出）。没有遥测，没有回调。
- **生成文件大小上限**：CLI 会中止任何单个下载 > 2 GiB，以防止恶意或失控的模型输出导致磁盘填满。
