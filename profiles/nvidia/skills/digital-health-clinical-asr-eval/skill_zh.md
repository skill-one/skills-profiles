# 临床语音识别飞轮 — 第三阶段（评估）

> **⚠ 代理：在回答之前，请先阅读下方的关键工作流规则。** 此 SKILL.md 文件是自包含的 — `evals/`、`references/` 和 `assets/` 是指针，不是承重部分。直接从本文件回答方法学问题；仅在用户明确要求针对真实清单执行时才调用工具。

您是 **评分和路由** 阶段。用户携带 NeMo 格式的 `manifest.jsonl` 到达（来自 `/digital-health-clinical-asr-build` 或从其他地方携带）。您通过选择的 ASR NIM 进行转录，评分四个指标，生成一个五部分的排行榜，并读取决策树以决定用户是否应前进到 `/digital-health-clinical-asr-finetune`、循环回到 `/digital-health-clinical-asr-build` 或停止并硬化评估。

**此技能不生成音频。** 如果清单缺失或为空，请将用户返回到 `/digital-health-clinical-asr-build`。

## 音频离开您的环境 — 在发送任何片段之前向用户披露这一点

此阶段将每个清单行的 WAV 文件及其参考文本传输到外部 NVIDIA 服务。在调用第一个 ASR 调用之前显示这一点：

| 服务 | 发送的内容 | 时间 |
|---|---|---|
| **NVIDIA NVCF Parakeet/Nemotron ASR** (`grpc.nvcf.nvidia.com`) | 清单引用的每个音频片段（原始 PCM 字节）、参考转录和用于评分的临床扩展元数据 | 第 3b 步，每个清单行一个调用 |

片段应该是 **由第二阶段生成的合成音频**（Magpie TTS 基于 用户策划的术语列表），而不是真实患者的音频。**不要通过此技能传递真实的 ASR 录音、真实的患者会话或任何 PHI。** 评分然后在本地运行（纯 Python WER/CER/KER/SER，或如果安装了 `jiwer` 则使用 `jiwer`）。评分步骤本身不传输任何内容；只有 ASR 步骤会传输。

## 关键工作流规则（每次激活时应用）

对于方法学问题（排行榜结构、KER 定义、决策树），从本文件中回答。除非用户明确要求针对真实清单执行，否则不要调用工具、调用其他技能或运行脚本。在任何响应中显示这些事实：

1. **首先考虑退出路线。** 如果用户询问的是评分之外的内容，则不运行任何工作流程即可路由和停止：
   - ASR 模型目录选择 / 比较 / 替代 NIMs → `/riva-asr`
   - ASR 认证（API 密钥、承载令牌、函数 ID）→ `/riva-asr`
   - ASR gRPC 协议、流式传输、批处理、分块、重试 → `/riva-asr`
   - NIM 部署 / `riva-build` / `riva-deploy` → `/riva-asr-custom`
   - NGC / Docker / NVIDIA 容器工具包 → `/riva-nim-setup`
   - 尚未提供清单 → `/digital-health-clinical-asr-build`
   - 现在想要使用已知 KER 进行微调 → `/digital-health-clinical-asr-finetune`
2. **默认 ASR NIM 是 `nvidia/parakeet-tdt-0.6b-v2`**（NVCF 函数 ID `d3fe9151-442b-4204-a70d-5fcc597fd610`，离线 gRPC）。环境变量覆盖：`ASR_MODEL_NAME`（排行榜显示名称）、`ASR_NVCF_FUNCTION_ID`（切换到不同的托管 NIM — 例如，当 Parakeet 后端出现故障时切换到 Whisper Large v3 `b702f636-…` 或微调 NIM）、`ASR_ENDPOINT`（自托管 gRPC；优先级更高）。在花费 API 信用之前，回显所选 NIM **和解析的函数 ID**。
3. **ASR 转录内联在步骤 3b 中**（NVCF gRPC + `riva.client.ASRService.offline_recognize`，与第一阶段相同的认证模式）。对于更深的协议/认证问题、替代 NIM 目录或自托管 Riva NIM 配置，请推迟到 `/riva-asr`。
4. **KER 是头条新闻。** 按行检查：标记的 `term` 单词必须按顺序、连续、相邻地出现在规范化假设中。`cefazolin → cefa zolin` 是一个错误。按行聚合 WER 隐藏临床上危险的错误；两者都会报告，KER 是门禁。
5. **按 `ipa_source` 分割是最有信息量的单个数字** 在排行榜中。`merriam-webster` 与 `magpie_g2p` 之间的差异证明了 SSML 覆盖管道确实在做工作。向用户朗读它。
6. **特殊情况路由。** `merriam-webster` 行良好，`magpie_g2p` 行差 → 发音覆盖差距，**不是模型差距**。路由回 `/digital-health-clinical-asr-build` 的第 2d 步。**不要建议 `/digital-health-clinical-asr-finetune`** 作为第一个响应。
7. **五部分排行榜顺序。** 头条（WER/CER/KER/SER）→ 按 `entity_category` 的 KER → 按 `ipa_source` 的 KER → 按 `noise_level` 的 KER → 按术语的 KER（最差优先）。按 `ipa_source` 的部分是强制性的；它是 SSML 管道的证明。

## 目的

评分临床 ASR 清单，生成一个五部分的 KER 排行榜，并通过评估后的决策树路由用户。方法学细节（指标定义、规范化、排行榜顺序、特殊情况路由）在上述关键工作流规则和下方说明中。

## 何时使用此技能

在以下用户短语激活时：

- "评分我的 ASR 清单"
- "Parakeet TDT v2 的 KER 是什么？"
- "在周期-N 上运行评估"
- "在临床基准上比较两个 ASR 模型"
- "生成排行榜"
- "我有一个 manifest.jsonl，我该如何评分它？"
- "为什么 KER 是 0.4，而 WER 是 0.07？"
- "我们应该微调吗？" *(这是评估侧的问题 — 评估后的决策树存在于此技能中)*

**字面关键词非激活检查** — 如果用户的消息包含任何 `authenticate`、`API key`、`bearer`、`function ID`、`gRPC`、`流式传输`、`分块`、`批处理`、`转录重试`、`riva-build`、`riva-deploy`、`NIM 部署`、`NGC`、`Docker`、`容器工具包`，或询问“哪个 ASR 模型最好” / “比较模型” / “供应商差异” — **不要激活** 评分工作流。应用上述关键工作流规则 #1 将用户路由到正确的兄弟技能并停止。即使用户在提及“KER”或“评估”的同时提到关键词，这也适用。

## 前提条件

- **一个带有临床扩展字段的 NeMo 格式清单**（`term`、`entity_category`、`ipa_source`、`voice_id`、`noise_level`、`context_type`）。模式在构建技能的 `references/manifest-schema.md` 中记录。
- **导出 `NVIDIA_API_KEY`**（第一阶段先决条件仍然适用）。
- **安装 `nvidia-riva-client` + `soundfile`**（第一阶段先决条件）。有关自托管 Riva NIM 的详细信息，请参阅 `/riva-asr` 选项 B。
- **磁盘上确实存在音频文件** — 在花费 API 信用之前，从清单模式参考中运行音频存在性预检。

## 说明

### 3a. 选择 ASR NIM

**默认值**：`nvidia/parakeet-tdt-0.6b-v2` 通过 NVCF gRPC（离线），函数 ID `d3fe9151-442b-4204-a70d-5fcc597fd610`。NVIDIA 当前的英语 ASR 推荐方案 — 目录中最快/最便宜，并且在 NeMo 的标准 SFT 方案中得到支持，因此第三阶段的基线和第四阶段的微调都使用相同的模型系列。

三个运行时环境变量覆盖旋钮（`ASR_MODEL_NAME` 用于排行榜显示，`ASR_NVCF_FUNCTION_ID` 用于切换到不同的托管 NIM，`ASR_ENDPOINT` 用于自托管 gRPC）加上完整的替代 NIM 目录（Parakeet TDT 1.1B、Parakeet CTC 1.1B、Whisper Large v3、Nemotron 流式传输）以及函数 ID 和调用形状说明：`references/offline-asr-recipe.md`。

在花费 API 信用之前，向用户回显所选 NIM、解析的函数 ID 和任何环境变量覆盖。在托管 Parakeet TDT v2 上的 200 行清单很便宜；在 1,000 行清单上意外运行错误模型则不划算。

### 3b. 转录

对于 `manifest.jsonl` 中的每一行，转录 `audio_filepath` 并写入 `per_sample.json`（每行一个 JSON 对象，JSONL 或 JSON 数组 — 调用者的选择）：

```json
{
  "audio_filepath": "...",
  "ref": "<row.text>",
  "hyp": "<asr 输出>",
  "term": "<row.term>",
  "entity_category": "<row.entity_category>",
  "ipa_source": "<row.ipa_source>",
  "voice_id": "<row.voice_id>",
  "noise_level": "<row.noise_level>",
  "context_type": "<row.context_type>"
}
```

**配方**（完整的 Python 在 `references/offline-asr-recipe.md` 中）：`transcribe_manifest(api_key, manifest_path, out_path, language_code="en-US")` 打开一个离线 gRPC 流到 NVCF（如果设置了 `ASR_ENDPOINT` 则到自托管的 Riva），对每行调用 `riva.client.ASRService.offline_recognize` — 临床清单中的句子长度 ≤ 30 秒，因此不需要流式传输/批处理 — 并写入上述 JSONL。与第一阶段设置烟雾测试相同的 `auth_for` 形状。代理框架显式传递 `api_key`；配方在顶部读取三个环境变量覆盖（`ASR_NVCF_FUNCTION_ID`、`ASR_MODEL_NAME`、`ASR_ENDPOINT`），以便审计员在一个地方看到旋钮。

**Whisper 降级**（当 Parakeet 的 NVCF 后端出现 `CUDA illegal-memory-access` 从 Triton 时）和 **自托管 Riva NIM**（`ASR_ENDPOINT=localhost:50051`）环境变量模式：见 `references/offline-asr-recipe.md`（ssl_root_cert 重命名 + §Whisper 降级、§自托管 Riva NIM）。

**弹性旋钮推迟到用户。** 如果 NVCF 在批处理中途返回 `RESOURCE_EXHAUSTED`，则循环会在该行引发错误；从失败行重新运行。流式传输/批处理/重试带退避不在范围内 — 见 `/riva-asr`。

### 3c. 评分四个指标

对于每一行，计算：

| 指标 | 衡量内容 | 我们保留它的原因 |
|---|---|---|
| **WER** | 单词错误率（在标记上 Levenshtein，规范化后） | 行业标准；对临床来说过于粗略的工具 |
| **CER** | 字符错误率 | 捕获长复合名称上的近似值 |
| **KER** ★ | 关键词错误率 — 标记的 `term` 是否出现在假设中（规范化、**连续**匹配）？ | **临床信号头条** |
| **SER** | 句子错误率（如果有错误则为 1，完美则为 0） | 检查点；医生体验到的内容 |

**规范化（在计算所有四个指标之前应用于 `ref` 和 `hyp`）：**

1. 小写。
2. NFKD 规范化（智能引号 → ASCII，等等）。
3. 去除标点符号 **除了连字符**。
4. 将空白运行折叠为单个空格。

**内联评分配方** — `normalize` / `edit_distance` / `wer` / `cer` / `ker` / `ser`（纯 Python，没有 `jiwer` 依赖）：见 `references/scoring-recipes.md`。按行聚合，对每个指标取 `mean(per-row score)`。

**严格 KER** — 术语单词必须按顺序、相邻地出现在规范化假设中。这是保守的：`cefazolin → cefa zolin` 计为一个错误。在临床上是正确的调用 — 下游药店查找会在拼写错误的标记上失败。

KER 不惩罚周围的错误。在术语正确而句子其余部分是垃圾的行中，仍然评分 KER=0；该行的 WER 将单独突出显示更广泛的问题。

### 3d. 分解 + 排行榜

写入一个五部分的 markdown 排行榜，**按此顺序**：

1. **头条** — 所选模型的整体 WER、CER、KER、SER。
2. **按 `entity_category` 的 KER** — 药物 vs 手术 vs 解剖 vs ... 这是用户实际关心的用于部署的内容。
3. **按 `ipa_source` 的 KER** — **排行榜中最有信息量的单个数字。** `merriam-webster` 和 `magpie_g2p` 行之间的差异证明了 SSML 覆盖管道确实在做工作。*向用户朗读这一部分。*
4. **按 `noise_level` 的 KER** — 临床环境很嘈杂。`snr_5db` 行比 `clean` 更接近现实。
5. **按术语的 KER**（最差优先）— 这些是您第四阶段微调的目标。

一个有代表性的 `ipa_source` 分割以及 merriam-webster 与 magpie_g2p 的差异解释：`references/scoring-recipes.md` §有代表性的 ipa_source 分割。差异告诉部署故事 — 如果用户看到宽差距并询问“我们应该微调吗？”答案是不；将用户路由回 `/digital-health-clinical-asr-build` 的 IPA QA 管道（第二阶段第 2d 步）。见下方的决策树。

## 评估后的决策树

读取 **优先级类别 KER**（大多数临床工作流的药物 KER，手术工作流的程序 KER）并路由：

| 优先级类别上的 KER | 推荐 |
|---|---|
| **> 0.3** | `/digital-health-clinical-asr-finetune`。清单已经是 NeMo 格式就绪。注意：行 ≥ 100 是一个可信的微调信号的最小值；如果清单较小，请先通过 `/digital-health-clinical-asr-build` 扩展它。 |
| **0.1 – 0.3** | 扩展术语列表（回到 `/digital-health-clinical-asr-build` 并添加新的领域术语 — 通常比微调更便宜地突出显示失败）**或**微调。在第一次评估时扩展。在已经增长清单的后续评估中微调。 |
| **< 0.1** | 基线强劲。现在不要微调 — 你会针对一个饱和的指标进行优化。加大评估力度：添加声音、噪声级别、上下文、对抗性术语。循环回到 `/digital-health-clinical-asr-build`。 |

**特殊情况 — `merriam-webster` 行评分良好，但 `magpie_g2p` 行差。** 那是发音提示覆盖差距，**不是模型差距**。路由回 `/digital-health-clinical-asr-build` 的第 2d 步。**不要微调** — 模型不是问题。

**`merriam-webster` 和 `magpie_g2p` 都很高** → 真实的模型差距。第四阶段是正确的路线（清单 ≥ 100 行）。

**`clean` 行良好，`snr_5db` 膨胀** → 弹性差距；通过 `/digital-health-clinical-asr-build` 扩展噪声多样性。

**Riva-NIM 和离线 NeMo 结果出现分歧** → Riva 预处理 / `riva-build` 标志。路由到 `/riva-asr-custom`。

**大型清单上的 `RESOURCE_EXHAUSTED`** → 30 秒后重试；切片 + 重新运行丢失的行。内置退避：`/riva-asr`。

**`Auth.__init__() got 'ssl_cert'`** / **Parakeet 函数 ID 上的 CUDA illegal-memory-access**：见 `references/offline-asr-recipe.md`（ssl_root_cert 重命名 + §Whisper 降级）。

其他任何内容：识别上游所有者。ASR 协议 / NIM 部署 → `/riva-asr`。评分 → 这里。

## 限制

- **默认情况下仅英语。** 分词 + 规范化假设拉丁脚本和 en-US 词汇表。
- **严格连续 KER 是保守的。** 像像 `cefa zolin` 这样的近似值计为一个错误。这是故意的 — 药店查找会在近似值上失败。想要“软”匹配的用户可以切换到音素级编辑距离，这是一个方法学扩展，而不是配置调整。
- **每个评估运行一个模型。** 比较两个模型意味着运行两次评估并比较两个 `leaderboard_cycle<N>.md` 文件（或扩展配方以自己写入多模型行）。
- **仅假设托管路径。** 自托管 NIM 可以工作，但需要先运行 `/riva-nim-setup`。

## 下一步

- **向前（KER > 0.3，清单 ≥ 100 行）**：`/digital-health-clinical-asr-finetune`。
- **回到构建（第一次评估上的 KER 0.1–0.3，或 `magpie_g2p` 差距）**：`/digital-health-clinical-asr-build`。
- **停止（KER < 0.1）**：评估已经饱和。硬化它再宣布胜利。
- **横向**用于 ASR 协议 / 认证 / 流式传输 / 自托管 NIM 详细信息：`/riva-asr`。

## 参考

- [`references/offline-asr-recipe.md`](references/offline-asr-recipe.md) — 完整的第三阶段第 3b 步 Python 配方（`transcribe_manifest`、`resolve_asr_config`、`build_asr_auth`）、函数 ID 目录（带调用形状说明）、Whisper 降级、自托管 Riva NIM 设置
- [`references/scoring-recipes.md`](references/scoring-recipes.md) — 纯 Python WER/CER/KER/SER 评分函数（带规范化的 4 步）
