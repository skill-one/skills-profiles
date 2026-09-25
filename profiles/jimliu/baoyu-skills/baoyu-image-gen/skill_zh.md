# 图像生成 (AI SDK)

基于官方 API 的图像生成。支持 OpenAI GPT 图像 2.5、Azure OpenAI、Google、OpenRouter、DashScope (阿里通义万象)、Z.AI GLM-Image、MiniMax、Jimeng (即梦)、Seedream (豆包)、Replicate 和 Agnes。

## 用户输入工具

当此技能提示用户时，请遵循以下工具选择规则（优先顺序）：

1. **优先使用**当前代理运行时暴露的**内置用户输入工具** — 例如，`AskUserQuestion`、`request_user_input`、`clarify`、`ask_user` 或任何等效工具。
2. **降级**：如果不存在此类工具，则发出编号的纯文本消息，并要求用户回复所选编号/答案以回答每个问题。
3. **批处理**：如果该工具支持每调用多个问题，则将所有适用问题合并为单个调用；如果仅支持单个问题，则按优先顺序一次询问一个问题。

下方的具体 `AskUserQuestion` 引用只是示例 — 在其他运行时中替换本地等效项。

## 脚本目录

`{baseDir}` = 此 SKILL.md 的目录。以下所有 `scripts/...` 路径相对于 `{baseDir}`。主脚本：`{baseDir}/scripts/main.ts`。批处理负载辅助工具：`{baseDir}/scripts/build-batch.ts`。解析 `${BUN_X}`：优先使用 `bun`；否则 `npx -y bun`；否则建议 `brew install oven-sh/bun/bun`。

## 第 0 步：加载偏好设置 ⛔ 阻塞

此步骤必须在任何图像生成之前完成 — 生成被阻塞，直到 EXTEND.md 存在。

按顺序检查这些路径；第一个命中者胜出：

| 路径 | 范围 |
|------|-------|
| `.baoyu-skills/baoyu-image-gen/EXTEND.md` | 项目 |
| `${XDG_CONFIG_HOME:-$HOME/.config}/baoyu-skills/baoyu-image-gen/EXTEND.md` | XDG |
| `$HOME/.baoyu-skills/baoyu-image-gen/EXTEND.md` | 用户主目录 |

- **找到** → 加载、解析、应用。如果 `default_model.[provider]` 为空 → 仅询问模型。
- **未找到** → 运行首次设置 (`references/config/first-time-setup.md`)，使用 AskUserQuestion 收集提供者 + 模型 + 质量 + 保存位置。保存 EXTEND.md，然后继续。在此完成之前不要生成图像。

向后兼容性：如果 `.baoyu-skills/baoyu-imagine/EXTEND.md` 存在而新路径不存在，运行时将其重命名为 `baoyu-image-gen`。如果两者都存在，运行时将它们保留原样并使用新路径。

**EXTEND.md 键**：默认提供者、默认质量、默认宽高比、默认图像大小、OpenAI 图像 API 方言、默认模型、批处理工作器上限、提供者特定批处理限制。模式：`references/config/preferences-schema.md`。

## 使用方法

最小工作示例 — 请参阅 `references/usage-examples.md` 以获取完整集，包括按提供者调用和批处理模式。

### 保留身份的参考提示

当用户希望从参考图像中保留真实人物/角色/物体时，**不要**用长篇通用描述替换参考。优先使用简短、硬性的身份保留语言：

- "使用参考图像中的相同人物/物体作为身份。不要重新设计它或创建一个看起来相似的全新主题。"
- "仅更改场景、服装、姿势、光照、渲染风格和构图。保留参考中的面部/比例/头发/关键配饰/整体身份。"
- 如果使用多个参考，请说明它们是同一主题，应共同定义身份。

陷阱：长描述如 "年轻东亚女性，椭圆形脸，清晰眼睛..." 可能会导致模型合成一个符合描述的新人物，而不是保留参考中的人物。

```bash
# 基本
${BUN_X} {baseDir}/scripts/main.ts --prompt "A cat" --image cat.png

# 带宽高比和高质量
${BUN_X} {baseDir}/scripts/main.ts --prompt "A landscape" --image out.png --ar 16:9 --quality 2k

# 从文件中获取提示
${BUN_X} {baseDir}/scripts/main.ts --promptfiles system.md content.md --image out.png

# 带参考图像
${BUN_X} {baseDir}/scripts/main.ts --prompt "Make blue" --image out.png --ref source.png

# 特定提供者
${BUN_X} {baseDir}/scripts/main.ts --prompt "A cat" --image out.png --provider dashscope --model qwen-image-2.0-pro

# OpenAI GPT 图像 2
${BUN_X} {baseDir}/scripts/main.ts --prompt "A cat" --image out.png --provider openai --model gpt-image-2.5-flare

# Codex CLI (使用登录的 Codex 订阅 — 无需 OPENAI_API_KEY；需要 `codex` 在 PATH 上)
${BUN_X} {baseDir}/scripts/main.ts --prompt "A cat" --image out.png --provider codex-cli --ar 16:9

# 批处理模式
${BUN_X} {baseDir}/scripts/main.ts --batchfile batch.json --jobs 4

# 从 outline.md + prompts/ (例如 baoyu-article-illustrator 输出) 构建批处理文件
${BUN_X} {baseDir}/scripts/build-batch.ts --outline outline.md --prompts prompts --output batch.json --images-dir attachments
${BUN_X} {baseDir}/scripts/main.ts --batchfile batch.json --jobs 4
```

## 参考图像身份保留

当用户希望从参考图像中保留人物/物体时：

- 优先使用一小部分经过筛选的现有源参考图像（通常 2-4 张），而不是许多图像；大型多兆字节的参考图像可能会使流式提供者不稳定。
- 在提示中说明参考图像是同一主题，输出必须使用该身份。避免长篇通用面部特征描述，这可能导致模型合成一个看起来相似的新人物。
- 除非用户明确要求，否则**不要**将新生成的输出用作参考图像；生成的参考图像会加剧漂移。
- 如果结果变得过于精致或网红风格，请减少风格化参考图像并添加显式的反美化约束（不要瘦脸、放大眼睛、浓妆、商业旅行拍摄、过度平滑）。
- 如果主题应该看起来更年轻/更年长，请保留面部并通过服装、姿势、场景和风格表达年龄；不要要求模型改变面部身份。

## 选项

| 选项 | 描述 |
|------|-------|
| `--prompt <text>`, `-p` | 提示文本 |
| `--promptfiles <files...>` | 从文件中读取提示（连接） |
| `--image <path>` | 输出图像路径（单图像模式下必需） |
| `--batchfile <path>` | 用于多图像生成的 JSON 批处理文件 |
| `--jobs <count>` | 批处理模式的工作器数量（默认：自动，来自配置的最大值，内置默认 10） |
| `--provider google\|openai\|azure\|openrouter\|dashscope\|zai\|minimax\|jimeng\|seedream\|replicate\|codex-cli\|agnes` | 强制使用提供者（默认：自动检测；`codex-cli` 永不自动选择 — 必须通过 CLI 或 EXTEND.md 指定） |
| `--model <id>`, `-m` | 模型 ID — 请参阅提供者参考以获取默认值和允许的值 |
| `--ar <ratio>` | 宽高比 (`16:9`, `1:1`, `4:3`, …) |
| `--size <WxH>` | 显式大小（例如，`1024x1024`；对于 `gpt-image-2.5-*` 和 `gpt-image-2`，宽/高必须是 16 的倍数，最大边 3840px，宽高比不超过 3:1） |
| `--quality normal\|2k` | 质量预设（默认：`2k`） |
| `--imageSize 1K\|2K\|4K` | Google/OpenRouter 的图像大小（默认：来自质量） |
| `--imageApiDialect openai-native\|ratio-metadata` | OpenAI 兼容端点方言 — 对于期望宽高比 `size` 加上 `metadata.resolution` 的网关，请使用 `ratio-metadata` |
| `--ref <files...>` | 参考图像。由 Google 多模态、OpenAI GPT 图像编辑、Azure OpenAI 编辑（仅限 PNG/JPG）、OpenRouter 多模态模型、Replicate 支持的系列、MiniMax 主题参考、Seedream 5.0/4.5/4.0、DashScope `wan2.7-image-pro`/`wan2.7-image` 支持。Jimeng、Seedream 3.0、SeedEdit 3.0 或任何 DashScope 模型（除 `wan2.7-image*` 系列外）不支持。 |
| `--n <count>` | 图像数量。Replicate 需要 `--n 1`（单输出保存语义） |
| `--json` | JSON 输出 |

## 环境变量

| 变量 | 描述 |
|------|-------|
| `OPENAI_API_KEY` | OpenAI API 密钥 |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API 密钥 |
| `OPENROUTER_API_KEY` | OpenRouter API 密钥 |
| `GOOGLE_API_KEY` | Google API 密钥 |
| `DASHSCOPE_API_KEY` | DashScope API 密钥 |
| `ZAI_API_KEY` (别名 `BIGMODEL_API_KEY`) | Z.AI API 密钥 |
| `MINIMAX_API_KEY` | MiniMax API 密钥 |
| `REPLICATE_API_TOKEN` | Replicate API 令牌 |
| `JIMENG_ACCESS_KEY_ID`, `JIMENG_SECRET_ACCESS_KEY` | Jimeng (即梦) Volcengine 凭证 |
| `ARK_API_KEY` | Seedream (豆包) Volcengine ARK API 密钥 |
| `<PROVIDER>_IMAGE_MODEL` | 每个提供者模型覆盖 (`OPENAI_IMAGE_MODEL`, `GOOGLE_IMAGE_MODEL`, `DASHSCOPE_IMAGE_MODEL`, `ZAI_IMAGE_MODEL`/`BIGMODEL_IMAGE_MODEL`, `MINIMAX_IMAGE_MODEL`, `OPENROUTER_IMAGE_MODEL`, `REPLICATE_IMAGE_MODEL`, `JIMENG_IMAGE_MODEL`, `SEEDREAM_IMAGE_MODEL`, `AGNES_IMAGE_MODEL`) |
| `AZURE_OPENAI_DEPLOYMENT` (别名 `AZURE_OPENAI_IMAGE_MODEL`) | Azure 默认部署 |
| `<PROVIDER>_BASE_URL` | 每个提供者端点覆盖 |
| `AZURE_API_VERSION` | Azure 图像 API 版本（默认 `2025-04-01-preview`） |
| `JIMENG_REGION` | Jimeng 区域（默认 `cn-north-1`） |
| `OPENAI_IMAGE_API_DIALECT` | `openai-native` \| `ratio-metadata` |
| `OPENROUTER_HTTP_REFERER`, `OPENROUTER_TITLE` | 可选的 OpenRouter 归因 |
| `BAOYU_IMAGE_GEN_MAX_WORKERS` | 覆盖批处理工作器上限 |
| `BAOYU_IMAGE_GEN_<PROVIDER>_CONCURRENCY` | 每个提供者并发（例如，`BAOYU_IMAGE_GEN_REPLICATE_CONCURRENCY`；对于 codex-cli 使用 `BAOYU_IMAGE_GEN_CODEX_CLI_CONCURRENCY`） |
| `BAOYU_IMAGE_GEN_<PROVIDER>_START_INTERVAL_MS` | 每个提供者启动间隔 |
| `BAOYU_CODEX_IMAGEGEN_BIN` | 覆盖 codex-cli 提供者的 codex-imagegen 包装器路径（默认：捆绑的 `scripts/codex-imagegen/main.ts`；接受 `.ts` 或遗留的 `.sh`/二进制文件） |
| `BAOYU_CODEX_IMAGEGEN_CACHE_DIR` | 启用 codex-cli 提供者的幂等性缓存（默认关闭） |
| `BAOYU_CODEX_IMAGEGEN_TIMEOUT_MS` | codex-cli 提供者的每次尝试 `codex exec` 超时（默认：300000 ms） |
| `BAOYU_CODEX_IMAGEGEN_RETRIES` | 在可重试错误上包装器侧重试尝试次数（对于 codex-cli 提供者，默认：2） |
| `BAOYU_CODEX_IMAGEGEN_LOG_FILE` | codex-cli 提供者的 JSONL 诊断日志追加文件 |

**加载优先级**：CLI 参数 > EXTEND.md > 环境变量 > `<cwd>/.baoyu-skills/.env` > `~/.baoyu-skills/.env`

### Codex/ChatGPT OAuth 不是 OpenAI API 密钥

`--provider openai --model gpt-image-2.5-flare` 使用标准 OpenAI 图像 API (`/v1/images/generations` 或 `/v1/images/edits`) 并需要 `OPENAI_API_KEY`。Codex 或 ChatGPT 桌面登录是不同的权限，不能作为 `OPENAI_API_KEY` 的直接替代；不要将 Codex OAuth 令牌粘贴到 `OPENAI_API_KEY` 或仅设置 `OPENAI_BASE_URL` 为 Codex 后端。

如果用户希望使用他们的 Codex 订阅 / GPT 图像 2 权限而无需 OpenAI API 密钥，请通过 Codex 本地后端路由，而不是此技能的 `openai` 提供者：

- 在 Codex 运行时：使用本地的 `imagegen` 技能/工具。
- 在非 Codex 运行时，如果已安装 `codex` CLI 并登录：使用 `baoyu-image-gen --provider codex-cli`（首选 — 它为您提供与其他提供者相同的重试 / 缓存 / 批处理流程）。提供者会通过捆绑的 `scripts/codex-imagegen/main.ts` TS 入口点（使用 `bun` 运行）生成 `codex exec`，相同的代码在 `packages/baoyu-codex-imagegen/src/main.ts` 中为独立调用者提供。
- 在 Hermes 运行时，如果具有本地的 `image_generate` 工具：使用该工具作为降级，并说明是否直接传递参考图像或从提取的特征中重建。

不要修改现有的 `openai` 提供者以无声地消耗 Codex OAuth。首选的 Codex-CLI 路径是专用的 `codex-cli` 提供者，它有自己的身份验证（Codex 登录）、路由 (`codex exec`)、请求形状和测试。请参阅 `references/codex-oauth-vs-openai-api-key.md`。

## 模型分辨率

对每个提供者都应用优先级（最高 → 最低）：

1. CLI 标志 `--model <id>`
2. EXTEND.md `default_model.[provider]`
3. 环境变量 `<PROVIDER>_IMAGE_MODEL`
4. 内置默认值

对于 OpenAI，内置默认值是 `gpt-image-2.5-flare`（快速，最低延迟）。`gpt-image-2.5-sunburst` 是最强大的变体，适用于复杂场景和精确编辑；`gpt-image-2`、`gpt-image-1.5`、`gpt-image-1` 和日期较旧的 GPT 图像快照（例如 `gpt-image-2.5-flare-2026-09-08`、`gpt-image-2-2026-04-21`）仍然可以通过 `--model` 或 `OPENAI_IMAGE_MODEL` 选择。

对于 Google，内置默认值是 `gemini-3-pro-image`。`gemini-3.1-flash-image` 是更快的低成本选项，而 `gemini-3.1-flash-lite-image` 是最便宜的 — 它仅生成 1K 输出，因此 `--quality 2k` / `--imageSize 2K|4K` 会被限制为 1K 并附带警告。

对于 DashScope，内置默认值是 `qwen-image-2.0-pro`；`qwen-image-3.0-pro` 是最新的旗舰产品，并使用相同的尺寸规则。

对于 Azure，`--model` / `default_model.azure` 是 Azure 部署名称。`AZURE_OPENAI_DEPLOYMENT` 是首选的环境变量；`AZURE_OPENAI_IMAGE_MODEL` 是作为向后兼容的别名保留的。如果您的 Azure 部署名称与底层模型相同，请使用 `gpt-image-2.5-flare`；否则请使用确切的自定义部署名称。

EXTEND.md 覆盖环境变量：如果 EXTEND.md 设置 `default_model.google: "gemini-3-pro-image"`，而环境变量设置 `GOOGLE_IMAGE_MODEL=gemini-3.1-flash-image`，则 EXTEND.md 胜出。

**在每次生成之前显示模型信息**：

- `Using [provider] / [model]`
- `Switch model: --model <id> | EXTEND.md default_model.[provider] | env <PROVIDER>_IMAGE_MODEL`

## OpenAI 兼容网关方言

`provider=openai` 意味着身份验证和路由入口点是 OpenAI 兼容的。它**不**保证上游图像 API 使用 OpenAI 原生语义。当网关期望不同的线形格式时，请在 EXTEND.md、`OPENAI_IMAGE_API_DIALECT` 或 `--imageApiDialect` 中设置 `default_image_api_dialect`：

- `openai-native`：像素 `size` (`1536x1024`) 和原生 OpenAI 质量字段
- `ratio-metadata`：宽高比 `size` (`16:9`) 加上 `metadata.resolution` (`1K|2K|4K`) 和 `metadata.orientation`

使用 `openai-native` 用于原生 OpenAI API 或严格克隆；尝试 `ratio-metadata` 用于在 Gemini 或类似模型前面的兼容网关。当前限制：`ratio-metadata` 仅适用于文本到图像；参考图像编辑仍然需要 `openai-native` 或具有第一类编辑支持的提供者。

## 提供者特定指南

每个提供者都有其自己的怪癖（模型系列、尺寸规则、参考图像支持、限制）。当用户选择该提供者或询问非默认行为时，请阅读这些内容：

| 提供者 | 参考 |
|----------|-----------|
| DashScope (Qwen-Image 系列，自定义尺寸) | `references/providers/dashscope.md` |
| Z.AI (GLM-Image, cogview-4) | `references/providers/zai.md` |
| MiniMax (image-01, subject-reference) | `references/providers/minimax.md` |
| OpenRouter (多模态模型，`/chat/completions` 流程) | `references/providers/openrouter.md` |
| Replicate (nano-banana, Seedream, Wan) | `references/providers/replicate.md` |
| Codex CLI (包装捆绑的 `scripts/codex-imagegen/`；Codex 登录，无需 `OPENAI_API_KEY`) | `references/providers/codex-cli.md` |
| Agnes (agnes-image-2.5-flash, 参考图像支持) | `references/providers/agnes.md` |

## 提供者选择

1. `--ref` 提供的 + 无 `--provider` → 自动选择 Google → OpenAI → Azure → OpenRouter → Replicate → Seedream → MiniMax → Agnes（MiniMax 的主题参考更专门于角色/肖像一致性）
2. `--provider` 指定 → 使用它（如果 `--ref`，必须是 google/openai/azure/openrouter/replicate/seedream/minimax/codex-cli/agnes）
3. 只有一个 API 密钥存在 → 使用该提供者
4. 多个密钥 → 默认优先级：Google → OpenAI → Azure → OpenRouter → DashScope → Z.AI → MiniMax → Replicate → Jimeng → Seedream → Agnes
5. `codex-cli` 永不自动选择 — 在 EXTEND.md 中设置 `default_provider: codex-cli` 或传递 `--provider codex-cli`。它通过捆绑的 `scripts/codex-imagegen/main.ts` TS 入口点（使用 `bun` 运行）生成 `codex exec`，并使用用户的 Codex 订阅（无需 `OPENAI_API_KEY`）。需要 `codex` 在 `PATH` 上并具有活动的 `codex login`。

## 质量预设

| 预设 | Google imageSize | OpenAI size | OpenRouter size | Replicate resolution | 用例 |
|--------|------------------|-------------|-----------------|----------------------|----------|
| `normal` | 1K | 1024px 目标 | 1K | 1K | 快速预览 |
| `2k` (默认) | 2K | 2048px 目标 | 2K | 2K | 封面、插图、信息图表 |

Google/OpenRouter `imageSize` 可以使用 `--imageSize 1K|2K|4K` 覆盖。

对于 OpenAI 原生 `gpt-image-2.5-*` 和 `gpt-image-2`，`normal` 映射到 `quality=medium` 和接近请求宽高比的低延迟有效尺寸；`2k` 映射到 `quality=high` 和 2048px 类尺寸，例如 `2048x2048`、`2048x1152` 或 `1152x2048`。使用显式 `--size` 以获取有效的自定义或 4K 输出，例如 `3840x2160`。

## 宽高比

支持：`1:1`、`16:9`、`9:16`、`4:3`、`3:4`、`2.35:1`。

- Google 多模态：`imageConfig.aspectRatio`
- OpenAI：`gpt-image-2.5-*` 和 `gpt-image-2` 使用请求的宽高比的最接近有效自定义尺寸；较旧的 GPT 图像和 DALL·E 模型使用它们最支持的固定尺寸
- OpenRouter：`imageGenerationOptions.aspect_ratio`；如果仅给出 `--size <WxH>`，则推断比例
- Replicate：行为是模型特定的 — `google/nano-banana*` 使用 `aspect_ratio`，`bytedance/seedream-*` 使用文档中记录的 Replicate 比例，Wan 2.7 将 `--ar` 映射到具体的 `size`
- MiniMax：官方 `aspect_ratio` 值；如果给出 `--size <WxH>` 而未给出 `--ar`，则发送 `width`/`height` 以 `image-01`

## 生成模式

**默认**：顺序。**批处理并行**：当 `--batchfile` 包含 2+ 待处理任务时自动启用。

| 情况 | 优先 | 原因 |
|-----------|--------|-----|
| 单图像，或 1-2 简单图像 | 顺序 | 降低协调开销，便于调试 |
| 多图像，具有保存的提示文件 | 批处理 (`--batchfile`) | 重用最终化的提示，应用共享的速率限制/重试，可预测的吞吐量 |
| 每个图像仍需要其自己的推理 / 提示编写 / 风格探索 | 子代理 | 工作仍然是探索性的，每个都需要独立分析 |
| 输入是 `outline.md` + `prompts/`（例如从 `baoyu-article-illustrator`） | 批处理 — 使用 `{baseDir}/scripts/build-batch.ts` 组装负载 | 提纲 + 提示文件已经包含了一切所需 |

经验法则：一旦提示文件保存，任务变为“生成所有这些”，优先选择批处理而不是子代理。仅在生成与每图像思考或发散的创意探索相关联时使用子代理。

**并行行为**：

- 默认工作器数量是自动的，受配置限制，内置默认 10
- 提供者特定速率限制仅适用于批处理模式；默认值针对吞吐量进行了调整，同时避免 RPM 爆发
- 使用 `--jobs <count>` 覆盖
- 每个图像最多重试 3 次
- 最终输出包括成功计数、失败计数和每个图像的失败原因

## 错误处理

- 缺少 API 密钥 → 带设置说明的错误
- 生成失败 → 自动重试，每个图像最多 3 次尝试
- 无效的宽高比 → 警告，继续使用默认值
- 参考图像具有不受支持的提供者/模型 → 带修复提示的错误

### Codex image2 降级

如果 `--provider openai --model gpt-image-2.5-flare` 因 `OPENAI_API_KEY` 缺失而失败，但当前运行时具有本地的图像生成后端或仓库级别的 `codex-imagegen` 包装器可用，则使用该路径，而不是让用户等待。明确说明降级是真正的参考图像生成还是仅从提取的视觉特征进行文本提示重建。请参阅 `references/codex-image2-fallback.md`。

## 参考

| 文件 | 内容 |
|------|---------|
| `references/usage-examples.md` | 跨提供者和批处理模式的扩展 CLI 示例 |
| `references/codex-oauth-vs-openai-api-key.md` | 为什么 Codex/ChatGPT OAuth 图像2 权限不能通过 baoyu-image-gen 的标准 OpenAI API 密钥提供者使用 |
| `references/codex-image2-fallback.md` | 当 OpenAI API 凭证缺失但 Codex/本地图像生成可用时的实际降级行为 |
| `references/providers/dashscope.md` | DashScope 系列、尺寸、限制 |
| `references/providers/zai.md` | Z.AI GLM-image / cogview-4 |
| `references/providers/minimax.md` | MiniMax image-01 + 主题参考 |
| `references/providers/openrouter.md` | OpenRouter 多模态流程 |
| `references/providers/replicate.md` | Replicate 支持的系列 + 守护 |
| `references/providers/agnes.md` | Agnes (agnes-image-2.5-flash) 尺寸、参考图像和限制 |
| `references/config/preferences-schema.md` | EXTEND.md 模式 |
| `references/config/first-time-setup.md` | 首次设置流程 |

## 扩展支持

通过 EXTEND.md 进行自定义配置。请参阅第 0 步的路径和模式。
