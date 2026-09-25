# 图像生成 (AI SDK)

基于官方 API 的图像生成。支持 OpenAI GPT 图像 2、Azure OpenAI、Google、OpenRouter、DashScope (阿里通义万象)、Z.AI GLM-Image、MiniMax、Jimeng (即梦)、Seedream (豆包) 和 Replicate。

## 用户输入工具

当此技能提示用户时，请遵循以下工具选择规则（优先级顺序）：

1. **优先使用**当前代理运行时暴露的**内置用户输入工具** — 例如，`AskUserQuestion`、`request_user_input`、`clarify`、`ask_user` 或任何等效工具。
2. **降级处理**：如果不存在此类工具，则发出编号的纯文本消息，并要求用户对每个问题回复选择的编号/答案。
3. **批量处理**：如果工具支持每调用多个问题，则将所有适用问题合并为单个调用；如果仅支持单个问题，则按优先级顺序逐个询问。

下方的具体 `AskUserQuestion` 引用仅为示例 — 在其他运行时中替换本地等效工具。

## 脚本目录

`{baseDir}` = 此 SKILL.md 的目录。主脚本：`{baseDir}/scripts/main.ts`。解析 `${BUN_X}`：优先 `bun`；否则 `npx -y bun`；否则建议 `brew install oven-sh/bun/bun`。

## 第 0 步：加载偏好设置 ⛔ 阻塞

此步骤必须在任何图像生成之前完成 — 生成过程会阻塞，直到 EXTEND.md 存在。

按顺序检查这些路径；第一个匹配的路径将生效：

| 路径 | 范围 |
|------|-------|
| `.baoyu-skills/baoyu-imagine/EXTEND.md` | 项目 |
| `${XDG_CONFIG_HOME:-$HOME/.config}/baoyu-skills/baoyu-imagine/EXTEND.md` | XDG |
| `$HOME/.baoyu-skills/baoyu-imagine/EXTEND.md` | 用户主目录 |

- **找到** → 加载、解析、应用。如果 `default_model.[provider]` 为空 → 仅询问模型。
- **未找到** → 运行首次设置 (`references/config/first-time-setup.md`)，使用 AskUserQuestion 收集提供者 + 模型 + 质量 + 保存位置。保存 EXTEND.md，然后继续。在此完成之前不要生成图像。

向后兼容性：如果 `.baoyu-skills/baoyu-image-gen/EXTEND.md` 存在而新路径不存在，运行时会将其重命名为 `baoyu-imagine`。如果两者都存在，运行时将保持原样并使用新路径。

**EXTEND.md 键**：默认提供者、默认质量、默认宽高比、默认图像大小、OpenAI 图像 API 方言、默认模型、批量工作器上限、提供者特定批量限制。模式：`references/config/preferences-schema.md`。

## 使用方法

最小工作示例 — 请参阅 `references/usage-examples.md` 获取完整集，包括按提供者调用和批量模式。

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
${BUN_X} {baseDir}/scripts/main.ts --prompt "A cat" --image out.png --provider openai --model gpt-image-2

# 批量模式
${BUN_X} {baseDir}/scripts/main.ts --batchfile batch.json --jobs 4
```

## 选项

| 选项 | 描述 |
|--------|-------------|
| `--prompt <text>`, `-p` | 提示文本 |
| `--promptfiles <files...>` | 从文件中读取提示（连接后） |
| `--image <path>` | 输出图像路径（单图像模式下必需） |
| `--batchfile <path>` | 用于多图像生成的 JSON 批量文件 |
| `--jobs <count>` | 批量模式的工作器数量（默认：自动，配置中的最大值，内置默认 10） |
| `--provider google\|openai\|azure\|openrouter\|dashscope\|zai\|minimax\|jimeng\|seedream\|replicate` | 强制指定提供者（默认：自动检测） |
| `--model <id>`, `-m` | 模型 ID — 请参阅提供者参考以获取默认值和允许的值 |
| `--ar <ratio>` | 宽高比 (`16:9`, `1:1`, `4:3`, …) |
| `--size <WxH>` | 显式大小（例如，`1024x1024`；对于 `gpt-image-2`，宽/高必须是 16 的倍数，最大边 3840px，宽高比不超过 3:1） |
| `--quality normal\|2k` | 质量预设（默认：`2k`） |
| `--imageSize 1K\|2K\|4K` | Google/OpenRouter 的图像大小（默认：从质量） |
| `--imageApiDialect openai-native\|ratio-metadata` | OpenAI 兼容端点方言 — 使用 `ratio-metadata` 用于期望宽高比 `size` 加上 `metadata.resolution` 的网关 |
| `--ref <files...>` | 参考图像。由 Google 多模态、OpenAI GPT 图像编辑、Azure OpenAI 编辑（仅 PNG/JPG）、OpenRouter 多模态模型、Replicate 支持的系列、MiniMax 主题参考、Seedream 5.0/4.5/4.0、DashScope `wan2.7-image-pro`/`wan2.7-image` 支持。Jimeng、Seedream 3.0、SeedEdit 3.0 或任何 DashScope 模型（除 `wan2.7-image*` 系列外）不支持 |
| `--n <count>` | 图像数量。Replicate 需要 `--n 1`（单输出保存语义） |
| `--json` | JSON 输出 |

## 环境变量

| 变量 | 描述 |
|----------|-------------|
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
| `<PROVIDER>_IMAGE_MODEL` | 每个提供者的模型覆盖 (`OPENAI_IMAGE_MODEL`, `GOOGLE_IMAGE_MODEL`, `DASHSCOPE_IMAGE_MODEL`, `ZAI_IMAGE_MODEL`/`BIGMODEL_IMAGE_MODEL`, `MINIMAX_IMAGE_MODEL`, `OPENROUTER_IMAGE_MODEL`, `REPLICATE_IMAGE_MODEL`, `JIMENG_IMAGE_MODEL`, `SEEDREAM_IMAGE_MODEL`) |
| `AZURE_OPENAI_DEPLOYMENT` (别名 `AZURE_OPENAI_IMAGE_MODEL`) | Azure 默认部署 |
| `<PROVIDER>_BASE_URL` | 每个提供者的端点覆盖 |
| `AZURE_API_VERSION` | Azure 图像 API 版本（默认 `2025-04-01-preview`） |
| `JIMENG_REGION` | Jimeng 区域（默认 `cn-north-1`） |
| `OPENAI_IMAGE_API_DIALECT` | `openai-native` \| `ratio-metadata` |
| `OPENROUTER_HTTP_REFERER`, `OPENROUTER_TITLE` | 可选的 OpenRouter 归因 |
| `BAOYU_IMAGE_GEN_MAX_WORKERS` | 覆盖批量工作器上限 |
| `BAOYU_IMAGE_GEN_<PROVIDER>_CONCURRENCY` | 每个提供者的并发（例如，`BAOYU_IMAGE_GEN_REPLICATE_CONCURRENCY`） |
| `BAOYU_IMAGE_GEN_<PROVIDER>_START_INTERVAL_MS` | 每个提供者的启动间隔 |

**加载优先级**：CLI 参数 > EXTEND.md > 环境变量 > `<cwd>/.baoyu-skills/.env` > `~/.baoyu-skills/.env`

## 模型分辨率

对每个提供者应用优先级（最高 → 最低）：

1. CLI 标志 `--model <id>`
2. EXTEND.md `default_model.[provider]`
3. 环境变量 `<PROVIDER>_IMAGE_MODEL`
4. 内置默认

对于 OpenAI，内置默认是 `gpt-image-2`。`gpt-image-1.5`、`gpt-image-1` 和 GPT 图像快照仍可通过 `--model` 或 `OPENAI_IMAGE_MODEL` 选择。

对于 Azure，`--model` / `default_model.azure` 是 Azure 部署名称。`AZURE_OPENAI_DEPLOYMENT` 是首选的环境变量；`AZURE_OPENAI_IMAGE_MODEL` 是向后兼容的别名。如果您的 Azure 部署名称与底层模型相同，请使用 `gpt-image-2`；否则请使用确切的自定义部署名称。

EXTEND.md 覆盖环境变量：如果 EXTEND.md 设置 `default_model.google: "gemini-3-pro-image-preview"`，而环境变量设置 `GOOGLE_IMAGE_MODEL=gemini-3.1-flash-image-preview`，则 EXTEND.md 优先。

**每次生成前显示模型信息**：

- `Using [provider] / [model]`
- `Switch model: --model <id> | EXTEND.md default_model.[provider] | env <PROVIDER>_IMAGE_MODEL`

## OpenAI 兼容网关方言

`provider=openai` 表示认证和路由入口点是 OpenAI 兼容的。它**不**保证上游图像 API 使用 OpenAI 原生语义。当网关期望不同的线缆格式时，请在 EXTEND.md、`OPENAI_IMAGE_API_DIALECT` 或 `--imageApiDialect` 中设置 `default_image_api_dialect`：

- `openai-native`：像素 `size` (`1536x1024`) 和原生 OpenAI 质量字段
- `ratio-metadata`：宽高比 `size` (`16:9`) 加上 `metadata.resolution` (`1K|2K|4K`) 和 `metadata.orientation`

使用 `openai-native` 用于 OpenAI 原生 API 或严格克隆；尝试 `ratio-metadata` 用于前置 Gemini 或类似模型的兼容网关。当前限制：`ratio-metadata` 仅适用于文本到图像；参考图像编辑仍需 `openai-native` 或具有第一类编辑支持的提供者。

## 提供者特定指南

每个提供者都有其自己的特性（模型系列、大小规则、参考支持、限制）。当用户选择该提供者或询问非默认行为时，请阅读这些内容：

| 提供者 | 参考 |
|----------|-----------|
| DashScope (Qwen-Image 系列，自定义大小) | `references/providers/dashscope.md` |
| Z.AI (GLM-Image, cogview-4) | `references/providers/zai.md` |
| MiniMax (image-01，主题参考) | `references/providers/minimax.md` |
| OpenRouter (多模态模型，`/chat/completions` 流程) | `references/providers/openrouter.md` |
| Replicate (nano-banana，Seedream，Wan) | `references/providers/replicate.md` |

## 提供者选择

1. `--ref` 提供 + 没有 `--provider` → 自动选择 Google → OpenAI → Azure → OpenRouter → Replicate → Seedream → MiniMax（MiniMax 的主题参考更专注于角色/肖像一致性）
2. `--provider` 指定 → 使用它（如果 `--ref`，必须是 google/openai/azure/openrouter/replicate/seedream/minimax）
3. 仅有一个 API 密钥存在 → 使用该提供者
4. 多个密钥 → 默认优先级：Google → OpenAI → Azure → OpenRouter → DashScope → Z.AI → MiniMax → Replicate → Jimeng → Seedream

## 质量预设

| 预设 | Google imageSize | OpenAI size | OpenRouter size | Replicate resolution | 用例 |
|--------|------------------|-------------|-----------------|----------------------|----------|
| `normal` | 1K | 1024px 目标 | 1K | 1K | 快速预览 |
| `2k` (默认) | 2K | 2048px 目标 | 2K | 2K | 封面、插图、信息图表 |

Google/OpenRouter `imageSize` 可用 `--imageSize 1K|2K|4K` 覆盖。

对于 OpenAI 原生 `gpt-image-2`，`normal` 映射到 `quality=medium` 和接近请求宽高比的低延迟有效大小；`2k` 映射到 `quality=high` 和 2048px 类尺寸，例如 `2048x2048`、`2048x1152` 或 `1152x2048`。使用显式 `--size` 以获取有效的自定义或 4K 输出，例如 `3840x2160`。

## 宽高比

支持：`1:1`、`16:9`、`9:16`、`4:3`、`3:4`、`2.35:1`。

- Google 多模态：`imageConfig.aspectRatio`
- OpenAI：`gpt-image-2` 使用请求宽高比的最接近有效自定义大小；较旧的 GPT 图像和 DALL·E 模型使用其最支持的固定大小
- OpenRouter：`imageGenerationOptions.aspect_ratio`；如果仅给出 `--size <WxH>`，则推断比例
- Replicate：行为是模型特定的 — `google/nano-banana*` 使用 `aspect_ratio`，`bytedance/seedream-*` 使用文档中记录的 Replicate 比例，Wan 2.7 将 `--ar` 映射到具体的 `size`
- MiniMax：官方 `aspect_ratio` 值；如果给出 `--size <WxH>` 而没有 `--ar`，则发送 `width`/`height` 用于 `image-01`

## 生成模式

**默认**：顺序。**批量并行**：当 `--batchfile` 包含 2+ 待处理任务时自动启用。

| 情况 | 优先 | 原因 |
|-----------|--------|-----|
| 单个图像，或 1-2 简单图像 | 顺序 | 降低协调开销，便于调试 |
| 多个图像，带保存的提示文件 | 批量 (`--batchfile`) | 重用最终化提示，应用共享限流/重试，可预测的吞吐量 |
| 每个图像仍需其自身的推理 / 提示编写 / 风格探索 | 子代理 | 工作仍具探索性，每个都需要独立分析 |
| 输入是 `outline.md` + `prompts/`（例如，来自 `baoyu-article-illustrator`） | 批量 — 使用 `scripts/build-batch.ts` 组装有效载荷 | 提纲 + 提示文件已经包含所有所需内容 |

经验法则：一旦提示文件保存，任务变为“生成所有这些”，优先选择批量而不是子代理。仅在生成与每图像思考或发散创意探索相关联时使用子代理。

**并行行为**：

- 默认工作器数量是自动的，受配置限制，内置默认 10
- 提供者特定限流仅在批量模式下应用；默认值针对吞吐量进行调优，同时避免 RPM 峰值
- 使用 `--jobs <count>` 覆盖
- 每个图像重试最多 3 次
- 最终输出包括成功计数、失败计数和每图像失败原因

## 错误处理

- 缺少 API 密钥 → 带设置说明的错误
- 生成失败 → 自动重试，每个图像最多 3 次
- 无效的宽高比 → 警告，使用默认值继续
- 不支持的提供者/模型参考图像 → 带修复提示的错误

## 参考

| 文件 | 内容 |
|------|---------|
| `references/usage-examples.md` | 跨提供者和批量模式的扩展 CLI 示例 |
| `references/providers/dashscope.md` | DashScope 系列、大小、限制 |
| `references/providers/zai.md` | Z.AI GLM-image / cogview-4 |
| `references/providers/minimax.md` | MiniMax image-01 + 主题参考 |
| `references/providers/openrouter.md` | OpenRouter 多模态流程 |
| `references/providers/replicate.md` | Replicate 支持的系列 + 护栏 |
| `references/config/preferences-schema.md` | EXTEND.md 模式 |
| `references/config/first-time-setup.md` | 首次设置流程 |

## 扩展支持

通过 EXTEND.md 进行自定义配置。请参阅第 0 步以获取路径和模式。
