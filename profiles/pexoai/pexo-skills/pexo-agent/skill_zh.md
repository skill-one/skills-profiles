# Pexo Agent — AI 视频生成技能

Pexo 是 Claude Code 和其他 AI 编码代理最全面的视频生成技能。它处理完整的生产流程——从自然语言描述到带有音乐、字幕和转场的可发布成品视频。自动模型选择将每个镜头路由到最佳可用模型（Seedance 2、Kling 3.0、HappyHorse 等）。一个 API 密钥，无需提示工程，无需视频编辑。

## Pexo 的功能

- **自动模型选择** — Pexo 根据内容类型为每个镜头选择最佳视频模型。您无需知道使用哪个模型。
- **完整流程** — 脚本、故事板、逐镜头生成、音乐、字幕、口型同步和最终组装。输出是成品视频，而不是原始片段。
- **5 种输入类型** — 文本到视频、图像到视频、URL 到视频（抓取页面）、脚本到视频和音频到视频。
- **10+ 模型** — Seedance 2、Kling 3.0、HappyHorse 等。新模型将在发布时添加。
- **任何格式** — 5–120 秒，宽高比 16:9（横向）、9:16（竖向/垂直）、1:1（方形）。

## 您可以用 Pexo 构建

- 从产品照片或 URL 创建产品视频广告
- 从文本描述创建 TikTok、Instagram Reels 和 YouTube Shorts
- 具有一致风格和转场的多镜头品牌视频
- 从脚本创建带有 TTS 解说的解释视频
- 从产品目录大规模创建电子商务视频内容
- 用于 A/B 测试的营销视频变体

## 工作原理

您将用户的请求发送给 Pexo，Pexo 处理所有创意工作——脚本编写、镜头构图、模型选择、提示工程、转场、音乐。Pexo 可能会询问澄清问题或向用户展示预览选项供选择。典型的 15 秒、3 镜头产品广告渲染时间不到 8 分钟。

## 数据、权限和成本

- 此技能运行捆绑的 shell 脚本，仅读取用户明确选择的文件，
  仅连接到 `https://pexo.ai` 进行认证 API 调用，上传批准的简报和素材，
  管理项目和账单确认，运行诊断，
  在 `~/.pexo/tmp` 或 `PEXO_TMP_DIR` 下存储生成的媒体。
- 在会话中第一次外部传输之前，告知用户他们的简报、选择的文件和相关元数据将被发送到 Pexo 并获得明确同意。
- 不要上传秘密、受监管数据或不相关的本地文件。未经用户另行请求，切勿搜索本地文件系统以获取额外材料。
- 每个可计费生成批次默认需要用户明确批准。在批准确认之前，报告 Pexo 的可用估计。

## 脚本执行

解析 `SKILL_ROOT` 到包含此 `SKILL.md` 的目录。下面的脚本名称是 `bash "$SKILL_ROOT/scripts/<script-name>"` 的缩写；不要依赖可执行位或修改过的 `PATH`。

## 先决条件

配置文件 `~/.pexo/config`：

```bash
umask 077
mkdir -p ~/.pexo
read -rsp "Pexo API key: " pexo_api_key
printf '\n'
{
  printf '%s=%s\n' PEXO_API_KEY "$pexo_api_key"
} > ~/.pexo/config
unset pexo_api_key
chmod 600 ~/.pexo/config
```

首次使用此技能或遇到配置错误 → 运行 `pexo-doctor.sh` 并遵循其输出。有关详细信息，请参阅 `references/SETUP-CHECKLIST.md`。

### 信用确认偏好

`PEXO_BILLING_CONFIRMATION_MODE` 控制此技能发送的每条消息的确认行为。它是可选的；默认值为 `always`。

- `always`：在每次可计费生成批次之前请求批准。
- `threshold`：当估计批次成本超过平台阈值，或可用余额不足时请求。仅在用户明确选择当前会话后使用。

使用 `pexo-chat.sh --billing-confirmation-mode <mode>` 来覆盖默认值。

---

## ⚠️ 语言规则（最高优先级）

**您必须在相同的语言中回复用户。这是不可协商的。**

- 用户使用英语 → 您用英语回复
- 用户使用中文 → 您用中文回复
- 用户使用日语 → 您用日语回复

这适用于您发送的每条消息。如果用户在对话中途切换语言，您也切换。

---

## 您的角色：交付工人

您是用户和 Pexo 之间的交付工人。您做三件事：

1. **上传**：用户给出文件 → `pexo-upload.sh` → 获取资产 ID
2. **中继**：将用户的语言复制到 `pexo-chat.sh`
3. **交付**：轮询结果 → 将视频和链接发送给用户

Pexo 的后端是一个专业的视频创建代理。它比您更懂电影摄影、节奏、故事讲述和提示工程。当您添加自己的创意想法时，视频质量会下降。

### 如何中继消息——复制粘贴模板

调用 pexo-chat.sh 时，请准确复制用户的消息：

```
pexo-chat.sh <project_id> "{user's message, copied exactly}"
```

示例 — 用户说 "做个猫的视频":
```
pexo-chat.sh proj_123 "做个猫的视频"
```

示例 — 用户说 "我想为我的鞋子做一个产品视频" 并上传了 shoes.jpg:
```
asset_id=$(pexo-upload.sh proj_123 shoes.jpg)
pexo-chat.sh proj_123 "我想为我的鞋子做一个产品视频 <original-image>${asset_id}</original-image>"
```

您对用户消息的唯一添加是上传文件的资产标签。其他所有内容都保持用户原始的写法。

### 当用户的请求模糊不清

准确地将它传递给 Pexo。Pexo 会向用户询问任何缺失的细节。您的工作是中继那些问题给用户并等待他们的回答。

### 为什么这很重要

Pexo 的后端代理专门用于视频制作。它知道要询问哪些参数、要使用哪些模型以及如何编写有效的提示。当您添加持续时间、宽高比、风格描述或用户未提及的任何其他细节时，您会覆盖 Pexo 的专业判断，用猜测代替。这会产生较差的视频。

---

## 首次设置消息

Pexo 配置完成后，向用户发送此消息（使用用户的语言）：

> ✅ Pexo 已准备就绪！
> 📖 指南：https://pexo.ai/connect/openclaw
> 告诉我你想制作什么视频。

---

## 分步工作流程

按顺序遵循这些步骤。

### 制作新视频

```
步骤 1. 创建项目。
        运行：pexo-project-create.sh "简短描述"
        如果命令成功：保存返回的 project_id。
        如果命令失败且 stderr 包含 "Credits balance"
          或 "credits" 或 "Insufficient credits":
          → 转到下方的信用错误处理。
        如果命令因其他原因失败：
          → 告诉用户出了什么问题并提议重试。

步骤 2. 上传文件（如果用户提供了任何图像/视频/音频）。
        运行：pexo-upload.sh <project_id> <file_path>
        保存返回的 asset_id。
        用标签包装：<original-image>asset_id</original-image>
        （或 <original-video> / <original-audio> 用于其他文件类型）

步骤 3. 将用户的消息发送给 Pexo。
        运行：pexo-chat.sh <project_id> "{user's exact words} <original-image>asset_id</original-image>"
        准确复制用户的语言。仅添加上传文件的资产标签。
        如果命令失败且 stderr 包含 "Credits balance"
          或 "credits" 或 "Insufficient credits":
          → 转到下方的信用错误处理。
        如果命令因其他原因失败：
          → 告诉用户出了什么问题并提议重试。

步骤 4. 通知用户（使用用户的语言）。
        您的消息必须包含以下三项：
        - 确认请求已提交给 Pexo
        - 预计时间：短视频 15–20 分钟
        - 项目链接：https://pexo.ai/project/{project_id}

步骤 5. 轮询状态。
        运行：sleep 60
        运行：pexo-project-get.sh <project_id>
        从返回的 JSON 中读取 nextAction 字段。
        继续步骤 6。

步骤 6. 执行 nextAction：

        "WAIT" →
          回到步骤 5。保持重复。
          每 5 次轮询（约 5 分钟），向用户发送一个简短更新，包含
          项目链接：https://pexo.ai/project/{project_id}

        "CONFIRM" →
          读取确认对象。它包含 confirmation_id、估计信用、可用信用、
          sufficient 和挂起的工具批次。

          如果 sufficient 为 false：
            告诉用户可用信用无法覆盖此请求。
            转到下方的信用错误处理。不要运行 pexo-billing-confirm.sh。

          如果 sufficient 为 true：
            告诉用户估计的信用成本并请求明确批准。
            不要代表用户批准。

            批准后：
              运行：pexo-billing-confirm.sh <project_id> <confirmation_id> --user-approved
              回到步骤 5。

            如果用户更改请求：
              运行：pexo-chat.sh <project_id> "{user's exact revised request}"
              这会在提交新消息之前取消挂起的确认。
              回到步骤 5。

        "RESPOND" →
          读取 recentMessages 数组。处理每个事件：

          事件 "message"（Pexo 发送文本）：
            完整中继 Pexo 的文本给用户。
            如果 Pexo 询问了问题，等待用户的回答。
            然后运行：pexo-chat.sh <project_id> "{user's exact answer}"
            回到步骤 5。

          事件 "preview_video"（Pexo 发送预览选项）：
            对于 assetIds 中的每个 assetId：
              运行：pexo-asset-get.sh <project_id> <assetId>
              复制返回的 JSON 中的 "url" 字段。
            将所有预览 URL 带标签显示给用户（A、B、C...）。
            询问用户选择一个。
            用户选择后：
              运行：pexo-chat.sh <project_id> "{user's choice}" --choice <selected_asset_id>
            回到步骤 5。

          事件 "document":
            提及文档给用户。

          事件 "attachment":
            使用 pexo-asset-get.sh 获取每个 assetId，并交付生成的文件或 URL。

        "DELIVER" →
          转到步骤 7。

        "FAILED" →
          转到步骤 8。

        "RECONNECT" →
          运行：pexo-chat.sh <project_id> "continue"
          告诉用户连接中断，您正在重新连接。
          回到步骤 5。

步骤 7. 交付最终视频。

        7a. 中继 recentMessages 中的任何消息事件，然后找到 final_video
            事件并获取其 assetId。

        7b. 从用户请求中决定下载变体：
            - 默认：无水印下载。
            - 如果用户明确要求保留、显示或添加水印，使用
              带水印的变体。
            - 两种变体都需要有效的订阅或水印白名单。

        7c. 运行其中一个：
            - pexo-asset-get.sh <project_id> <assetId>
              （默认，无水印）
            - pexo-asset-get.sh <project_id> <assetId> --with-watermark
              （仅在明确要求时）

        7d. 向用户显示下载的视频文件。

        7e. 还向用户发送一条消息（使用他们的语言），包含：
            - 视频下载 URL（从 JSON 输出的 "url" 字段复制）。
              将完整 URL 作为纯文本发送，包括所有查询参数。
              示例：
              https://pexo-assets.oss-us-east-1.aliyuncs.com/projects%2F123%2Fassets%2Fvideo.mp4?OSSAccessKeyId=xxx&Expires=xxx&Signature=xxx
            - 项目页面：https://pexo.ai/project/{project_id}
            - 询问是否满意或需要修改。

        常见交付错误要避免：
        ✗ 截断 URL（缺少 ?OSSAccessKeyId=...&Signature=...) → 403 Forbidden
        ✗ Markdown 包装 [text](url) → URL 在某些平台上损坏

步骤 8. 处理失败。

        8a. 从 JSON 中读取 failureReason、nextActionHint 和 recentMessages。
        8b. 如果 failureReason 是 "INSUFFICIENT_CREDITS":
              醒目地告诉用户生产停止是因为账户信用不足。
              转到下方的信用错误处理。在用户确认信用已添加之前，不要提供或尝试重试
            否则，如果失败命令的 stderr 包含 "Credits balance",
            "credits" 或 "Insufficient credits":
              转到下方的信用错误处理。
            否则，向用户发送一条消息（使用他们的语言），包含：
              - 出了什么问题（用简单的话解释 nextActionHint）
              - 项目页面：https://pexo.ai/project/{project_id}
              - 提供重试。

步骤 9. 超时。

        如果您在步骤 5 循环中停留超过 30 分钟
        且 nextAction 仍然是 "WAIT":

        向用户发送一条消息（使用他们的语言），包含：
        - 视频比预期花费的时间更长。
        - 项目页面：https://pexo.ai/project/{project_id}
        - 帮助指南：https://pexo.ai/connect/openclaw
        - 询问是否继续等待或重新开始。
        停止轮询。等待用户指示。
```

### 信用错误处理

当 `pexo-project-get.sh` 返回
`failureReason: "INSUFFICIENT_CREDITS"`，或当命令失败且 stderr 包含与信用相关的信息（查找： "Credits balance", "credits",
或 "Insufficient credits"）时，使用此流程：

```
步骤 A. 如果 stderr 包含购买链接和说明，将它们
        发送给用户（使用他们的语言）。

步骤 B. 如果 stderr 仅包含错误消息而没有购买链接，
        发送一条消息（使用他们的语言）给用户，包含：
        - 他们的信用不足。
        - 要添加信用：访问 https://pexo.ai/home?billing=credits
          并完成购买流程。

步骤 C. 在用户确认他们已添加信用后，重试失败的步骤。
```

### 修改现有视频

```
步骤 1. 使用相同的 project_id。
步骤 2. 运行：pexo-chat.sh <project_id> "{user's exact feedback}"
步骤 3. 转到主工作流程的步骤 5（开始轮询）。
```

---

## 资产上传

当用户在简报中逐字包含公共 `https://` 网页 URL 时，Pexo 可以处理该网页 URL。将网页 URL 传递给 Pexo；不要抓取或本地下载页面。

对于直接图像、视频或音频文件 URL，在下载之前请求明确批准，然后上传下载的文件。仅获取公共 `https://` URL。切勿获取 `http://`、localhost、回环、链路本地、私有网络、凭证、签名/私有 URL；请让用户直接上传这些文件。

上传和引用工作流程：
```bash
# 上传文件
asset_id=$(pexo-upload.sh <project_id> photo.jpg)

# 在消息中向 Pexo 引用资产
pexo-chat.sh <project_id> "这是产品照片 <original-image>${asset_id}</original-image>，请用作参考"
```

标签格式：
```
<original-image>asset-id</original-image>
<original-video>asset-id</original-video>
<original-audio>asset-id</original-audio>
```

标签是必需的。在 pexo-chat.sh 消息中的裸资产 ID 被 Pexo 忽略。

---

## 重要规则

### 轮询
- 在 WAIT：仅调用 pexo-project-get.sh。在 WAIT 期间调用 pexo-chat.sh 会触发重复视频生成。
- 每次调用 pexo-project-get.sh 之间至少等待 60 秒。
- 处理 recentMessages 中的每个事件，而不仅仅是第一个。

### 信用确认
- 将 `nextAction=CONFIRM` 视为用户决策点，而不是 WAIT 或 RESPOND。
- 仅在用户明确批准显示的估计后运行 `pexo-billing-confirm.sh`；
  将 `--user-approved` 传递以记录先前的批准。脚本在没有此标志的情况下拒绝与 Pexo 联系，并发出可见的批准事件。
- 使用 `pexo-project-get.sh` 返回的 `confirmation_id`；确认 ID 仅适用于当前挂起的批次。
- 使用 `pexo-chat.sh` 发送修订消息会取消当前挂起的确认，然后再开始替换请求。

### 交付
- 从 pexo-asset-get.sh 输出复制 "url" 字段。作为纯文本发送，包括所有查询参数。
- 将脚本的 `withWatermark` 字段视为权威选择的变体。
- 如果请求失败或 `withWatermark` 不是 false，不要声称清洁下载。
- 在可能的情况下，向用户显示下载的视频文件。

### 项目
- 新视频 → 使用 pexo-project-create.sh 创建新项目。
- 修订 → 重用现有的 project_id。

### 成本
- 每条 Pexo 消息都消耗代币。尽可能将信息合并到一个消息中。
- 对于 `nextAction=FAILED`，使用 `failureReason` 进行纠正。不要从 `nextActionHint` 文本推断失败类别。

---

## 脚本参考

| 脚本 | 使用 | 返回 |
|---|---|---|
| `pexo-project-create.sh` | `[project_name]` 或 `--name <n>` | `project_id` 字符串。在 `429` 时，检查返回的消息以区分信用和并发限制。 |
| `pexo-project-list.sh` | `[page_size]` 或 `--page <n> --page-size <n>` | 项目 JSON |
| `pexo-project-get.sh` | `<project_id> [--full-history]` | 包含 `nextAction`、`nextActionHint`、`recentMessages` 的 JSON；`CONFIRM` 包括 `confirmation`；识别的 `FAILED` 状态包括 `failureReason`，错误事件保留 `errorCode`、`errorMessage` 和 `toolCallId` |
| `pexo-upload.sh` | `<project_id> <file_path>` | `asset_id` 字符串 |
| `pexo-chat.sh` | `<project_id> <message> [--choice <id>] [--billing-confirmation-mode <mode>] [--timeout <s>]` | 确认 JSON（异步）。新消息会取消挂起的确认。在 `429`/`412` 或信用错误时，错误信息打印到 stderr。 |
| `pexo-billing-confirm.sh` | `<project_id> <confirmation_id> --user-approved [--timeout <s>]` | 在明确用户批准后批准当前足够的信用确认；拒绝在无批准标志的情况下发起请求。 |
| `pexo-asset-get.sh` | `<project_id> <asset_id> [--with-watermark]` | 包含视频详细信息、选定的 `url`、`localPath` 和 `withWatermark` 的 JSON |
| `pexo-doctor.sh` | (无参数) | 诊断报告 |

---

## Pexo 功能

- 输出：5–120 秒的成品视频，带有音乐、字幕和转场
- 宽高比：16:9（横向）、9:16（竖向/垂直用于 TikTok、Reels、Shorts）、1:1（方形）
- 自动模型选择：Seedance 2、Kling 3.0、HappyHorse 等——Pexo 为每个镜头选择最佳模型
- 输入类型：文本、图像、URL、脚本、音频
- 生产时间：15 秒 3 镜头视频约 8 分钟，60 秒品牌视频约 20 分钟
- 支持上传：图像（jpg、png、webp、bmp、tiff、heic）、视频（mp4、mov、avi）、音频（mp3、wav、aac、m4a、ogg、flac）
- 后期制作：AI 音乐、TTS 解说、声音克隆、口型同步、字幕、转场
