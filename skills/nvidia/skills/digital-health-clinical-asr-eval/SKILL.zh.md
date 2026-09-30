---
name: digital-health-clinical-asr-eval
description: 临床 ASR 飞轮第 3 阶段。评分 NeMo 清单，生成五部分 KER 排行榜（按 ipa_source 诊断）。不适用于 ASR 认证（/riva-asr）。
---

/*
SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
SPDX-License-Identifier: Apache-2.0
*/

# 临床语音识别飞轮 — 第三阶段（评估）

> **⚠ 代理：在回答之前，请先阅读下方的关键工作流规则部分。** 此 SKILL.md 是自包含的 — `evals/`、`references/` 和 `assets/` 是指针，不是承重部分。直接从本文件回答方法学问题；仅在用户明确要求针对真实清单执行时才调用工具。

您是 **评分和路由** 阶段。用户带有 NeMo 格式的 `manifest.jsonl`（来自 `/digital-health-clinical-asr-build` 或从其他地方携带）。您通过选择的 ASR NIM 进行转录，评分四个指标，生成一个五部分的排行榜，并读取决策树以决定用户是否应前进到 `/digital-health-clinical-asr-finetune`、循环回到 `/digital-health-clinical-asr-build` 或停止并固化评估。

**此技能不生成音频。** 如果清单缺失或为空，请将用户返回到 `/digital-health-clinical-asr-build`。

## 音频将离开您的环境 — 在发送任何片段之前向用户披露此信息

此阶段将每个清单行的 WAV 文件及其参考文本传输到外部 NVIDIA 服务。在调用第一个 ASR 调用之前显示此信息：

| 服务 | 发送内容 | 时间 |
|---|---|---|
| **NVIDIA NVCF Parakeet/Nemotron ASR** (`grpc.nvcf.nvidia.com`) | 清单引用的每个音频片段（原始 PCM 字节）、参考转录文本以及用于评分的临床扩展元数据 | 第 3b 步，每个清单行一个调用 |

片段应该是 **由第二阶段生成的合成音频**（用户策划术语列表上的 Magpie TTS）——而不是真实患者音频。**不要通过此技能传递真实 ASR 录音、真实患者会话或任何 PHI。** 评分然后在本地运行（纯 Python WER/CER/KER/SER，或如果已安装则使用 `jiwer`）。评分步骤本身不传输任何内容；只有 ASR 步骤会传输。

## 关键工作流规则（每次激活时应用）

对于方法学问题（排行榜结构、KER 定义、决策树），从本文件中回答。除非用户明确要求针对真实清单执行，否则不要调用工具、调用其他技能或运行脚本。在任何响应中显示这些事实：

1. **优先退出。** 如果用户询问的是评分之外的内容，则不运行任何工作流即可路由和停止：
   - ASR 模型目录选择 / 比较 / 替代 NIMs → `/riva-asr`
   - ASR 认证（API 密钥、bearer 令牌、函数 ID）→ `/riva-asr`
   - ASR gRPC 协议、流式传输、批处理、分块、重试 → `/riva-asr`
   - NIM 部署 / `riva-build` / `riva-deploy` → `/riva-asr-custom`
   - NGC / Docker / NVIDIA 容器工具包 → `/riva-nim-setup`
   - 尚无清单 → `/digital-health-clinical-asr-build`
   - 现在想要使用已知 KER 进行微调 → `/digital-health-clinical-asr-finetune`
2. **默认 ASR NIM 是 `nvidia/parakeet-tdt-0.6b-v2`**（NVCF 函数 ID `d3fe9151-442b-4204-a70d-5fcc597fd610`，离线 gRPC）。环境变量覆盖：`ASR_MODEL_NAME`（排行榜显示名称）、`ASR_NVCF_FUNCTION_ID`（切换到不同的托管 NIM — 例如，当 Parakeet 后端出现故障时切换到 Whisper Large v3 `b702f636-…`，或微调 NIM）、`ASR_ENDPOINT`（自托管 gRPC；优先级更高）。在花费 API 信用之前，回显所选 NIM **和解析的函数 ID**。
3. **ASR 转录嵌入在第 3b 步中**（NVCF gRPC + `riva.client.ASRService.offline_recognize`，与第一阶段相同的认证模式）。对于更深的协议/认证问题、替代 NIM 目录或自托管 Riva NIM 配置，委托给 `/riva-asr`。
4. **KER 是头条新闻。** 按行检查：标记的 `term` 单词必须在归一化假设中按顺序、连续、相邻出现。`cefazolin → cefa zolin` 是一个错误。聚合 WER 隐藏了临床上的危险错误；两者都报告，KER 是门禁。
5. **按 `ipa_source` 分割是最有信息量的单个数字** 在排行榜中。`merriam-webster` 与 `magpie_g2p` 的差异证明了 SSML 覆盖管道确实在做工作。向用户朗读它。
6. **特殊情况路由。** `merriam-webster` 行良好，`magpie_g2p` 行差 → 发音覆盖差距，**不是模型差距**。路由回 `/digital-health-clinical-asr-build` 第 2d 步。**不要建议 `/digital-health-clinical-asr-finetune`** 作为第一个响应。
7. **五部分排行榜顺序。** 头条（WER/CER/KER/SER）→ 按 `entity_category` 的 KER → 按 `ipa_source` 的 KER → 按 `noise_level` 的 KER → 按术语的 KER（最差优先）。按 `ipa_source` 的部分是强制性的；它是 SSML 管道工作的证明。

## 目的

评分临床 ASR 清单，生成一个五部分的 KER 排行榜，并通过评估后的决策树路由用户。方法学细节（指标定义、归一化、排行榜顺序、特殊情况路由）在上述关键工作流规则和下方说明中。

## 何时使用此技能

在用户短语激活时：

- "评分我的 ASR 清单"
- "Parakeet TDT v2 的 KER 是什么？"
- "在周期-N上运行评估"
- "在临床基准上比较两个 ASR 模型"
- "生成排行榜"
- "我有 manifest.jsonl，我该如何评分它？"
- "为什么 KER 为 0.4，而 WER 为 0.07？"
- "我们应该微调吗？" *(这是评估侧的问题 — 评估后的决策树存在于此技能中)*

**字面关键词非激活检查** — 如果用户的消息包含任何 `authenticate`、`API 密钥`、`bearer`、`函数 ID`、`gRPC`、`流式传输`、`分块`、`批处理`、`转录重试`、`riva-build`、`riva-deploy`、`NIM 部署`、`NGC`、`Docker`、`容器工具包`，或询问“哪个 ASR 模型最好” / “比较模型” / “供应商差异” — **不要激活** 评分工作流。应用上述关键工作流规则 #1 将用户路由到正确的兄弟技能并停止。即使用户在提及“KER”或“评估”的同时提到关键词，这也适用。

## 前提条件

- **一个 NeMo 格式的清单**，包含临床扩展字段（`term`、`entity_category`、`ipa_source`、`voice_id`、`noise_level`、`context_type`）。模式在构建技能的 `references/manifest-schema.md` 中记录。
- **导出 `NVIDIA_API_KEY`**（第一阶段先决条件仍然适用）。
- **安装 `nvidia-riva-client` + `soundfile`**（第一阶段先决条件）。对于自托管 Riva NIM 的详细信息，请参阅 `/riva-asr` 选项 B。
- **磁盘上确实存在音频文件** — 在花费 API 信用之前，从清单模式参考中运行音频存在性预检。

## 说明

### 3a. 选择 ASR NIM

**默认值**：`nvidia/parakeet-tdt-0.6b-v2` 通过 NVCF gRPC（离线），函数 ID `d3fe9151-442b-4204-a70d-5fcc597fd610`。NVIDIA 当前的英语 ASR 推荐 — 目录中最快/最便宜，并且在 NeMo 的标准 SFT 配方中得到支持，因此第三阶段的基线和第四阶段的微调都使用相同的模型系列。

三个运行时环境变量覆盖旋钮（`ASR_MODEL_NAME` 用于排行榜显示、`ASR_NVCF_FUNCTION_ID` 切换到不同的托管 NIM、`ASR_ENDPOINT` 用于自托管 gRPC）加上完整的替代 NIM 目录（Parakeet TDT 1.1B、Parakeet CTC 1.1B、Whisper Large v3、Nemotron 流式传输）以及函数 ID 和调用形状注释：`references/offline-asr-recipe.md`。

在花费 API 信用之前，向用户回显所选 NIM、解析的函数 ID 和任何环境变量覆盖。一个 200 行的清单在托管 Parakeet TDT v2 上很便宜；在一个 1,000 行的清单上意外运行错误模型则不便宜。

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

**配方**（完整的 Python 在 `references/offline-asr-recipe.md` 中）：`transcribe_manifest(api_key, manifest_path, out_path, language_code="en-US")` 打开一个离线 gRPC 流到 NVCF（如果设置了 `ASR_ENDPOINT` 用于自托管 Riva，则到 `ASR_ENDPOINT`），按行调用 `riva.client.ASRService.offline_recognize` — 临床清单中的句子 ≤ 30 秒，因此不需要流式传输/批处理 — 并写入上述 JSONL。与第一阶段设置烟雾测试相同的 `auth_for` 形状。代理框架显式传递 `api_key`；配方在顶部读取三个环境变量覆盖（`ASR_NVCF_FUNCTION_ID`、`ASR_MODEL_NAME`、`ASR_ENDPOINT`），以便审计员在一个地方看到旋钮。

**Whisper 回退**（当 Parakeet 的 NVCF 后端因 Triton 报告 `CUDA illegal-memory-access` 时）和 **自托管 Riva NIM**（`ASR_ENDPOINT=localhost:50051`）环境变量模式：请参阅 `references/offline-asr-recipe.md`（ssl_root_cert 重命名 + §Whisper 回退、§自托管 Riva NIM）。

**弹性旋钮委托给用户。** 如果 NVCF 在批处理中途返回 `RESOURCE_EXHAUSTED`，则循环在那一行引发；从失败行重新运行。流式传输/批处理/重试带退避不在范围内 — 请参阅 `/riva-asr`。

### 3c. 评分四个指标

对于每一行，计算：

| 指标 | 衡量内容 | 我们保留它的原因 |
|---|---|---|
| **WER** | 单词错误率（在标记上 Levenshtein，归一化后） | 行业标准；临床上的钝器 |
| **CER** | 字符错误率 | 捕获长复合名称上的近似值 |
| **KER** ★ | 关键词错误率 — 标记的 `term` 是否出现在假设中（归一化，**连续**匹配）？ | **临床信号头条** |
| **SER** | 句子错误率（如果有错误则为 1，完美则为 0） | 检查点；医生体验 |

**归一化（在所有四个指标之前应用于 `ref` 和 `hyp`）：**

1. 小写。
2. NFKD 归一化（智能引号 → ASCII 等）。
3. 去除标点（除连字符外）。
4. 将空白运行折叠为单个空格。

**内联评分配方** — `normalize` / `edit_distance` / `wer` / `cer` / `ker` / `ser`（纯 Python，无 `jiwer` 依赖）：请参阅 `references/scoring-recipes.md`。按行聚合，对每个指标取 `mean(per-row score)`。

**严格 KER** — 术语单词必须在归一化假设中按顺序、相邻出现。这是保守的：`cefazolin → cefa zolin` 计数为一个错误。在临床上是正确的调用 — 下游药房查找将在拼写错误的标记上失败。

KER 不惩罚周围错误。一行中术语正确而句子其余部分是垃圾仍然评分 KER=0；该行的 WER 将单独突出显示更广泛的问题。

### 3d. 拆分 + 排行榜

写入一个五部分的 markdown 排行榜，**按此顺序**：

1. **头条** — 所选模型的整体 WER、CER、KER、SER。
2. **按 `entity_category` 的 KER** — 药物 vs 手术 vs 解剖 vs ... 这是用户实际关心的部署内容。
3. **按 `ipa_source` 的 KER** — **排行榜中最有信息量的单个数字。** `merriam-webster` 和 `magpie_g2p` 之间的差异证明了 SSML 覆盖管道确实在做工作。*向用户朗读这一部分。*
4. **按 `noise_level` 的 KER** — 临床环境很嘈杂。`snr_5db` 行比 `clean` 更接近现实。
5. **按术语的 KER**（最差优先）— 这些是您第四阶段的微调目标。

一个有代表性的 `ipa_source` 分割，以及 merriam-webster 与 magpie_g2p 差异解释：`references/scoring-recipes.md` §有代表性的 ipa_source 分割。差异告诉部署故事 — 如果用户看到一个宽差距并询问“我们应该微调吗？”，答案是*不*；将他们路由回 `/digital-health-clinical-asr-build` 的 IPA QA 管道（第二阶段第 2d 步）。见下方的决策树。

## 评估后的决策树

读取**优先级类别 KER**（大多数临床工作流的药物 KER，手术工作流的程序 KER）并路由：

| 优先级类别上的 KER | 推荐 |
|---|---|
| **> 0.3** | `/digital-health-clinical-asr-finetune`。清单已经是 NeMo 格式就绪。注意：行 ≥ 100 是一个可信微调信号的最低值；如果清单较小，请先通过 `/digital-health-clinical-asr-build` 增加它。 |
| **0.1 – 0.3** | 扩展术语列表（回到 `/digital-health-clinical-asr-build` 并添加新领域术语 — 通常比微调更便宜地突出显示失败）**或**微调。在*第一次*评估时扩展。在*后续*评估中，如果清单已经增长，则微调。 |
| **< 0.1** | 基线强劲。现在不要微调 — 你会针对饱和指标进行优化。加大评估力度：添加声音、噪声级别、上下文、对抗性术语。循环回到 `/digital-health-clinical-asr-build`。 |

**特殊情况 — `merriam-webster` 行评分良好，但 `magpie_g2p` 行很差。** 那是一个发音提示覆盖差距，**不是模型差距**。路由回 `/digital-health-clinical-asr-build` 第 2d 步。**不要微调** — 模型不是问题。

## 示例

**场景 A — 在一个新鲜周期-1 清单上的第一次评估。** 用户：*"我有一个带有 200 行临床音频的 `manifest.jsonl`，其中包含 `term` 和 `entity_category` 字段。我该如何评分它？"* → 完全跳过第二阶段。运行音频存在性预检。选择 `parakeet-tdt-0.6b-v2`（默认）并回显选择 + 解析的函数 ID。运行内联第 3b 步配方（`transcribe_manifest(...)`）。评分四个指标。生成五部分排行榜。向用户朗读按 `ipa_source` 的分割。应用决策树针对药物 KER。

**场景 B — 解释一个混合结果。** 用户：*"评估显示标记为 `merriam-webster` 的行 KER 为 0.05，但标记为 `magpie_g2p` 的行 KER 为 0.40。我应该微调吗？"* → 不 — 这是特殊情况。模型很好；发音提示没有覆盖长尾术语。将用户路由回 `/digital-health-clinical-asr-build` 第 2d 步试听 `magpie_g2p` 行并追加验证的 IPA 到 `pronunciation_overrides.csv`。在重新构建后再次运行第三阶段，然后再考虑第四阶段。

## 生成的工件

- `per_sample.json` — 每行转录结果，保留所有临床扩展字段（ASR `hyp` 与清单的 `ref` 和元数据连接）
- `results.csv` — 每行 WER/CER/KER/SER 分数
- `leaderboard_cycle<N>.md` — 五部分 markdown 报告

（文件名由用户选择；此技能假设的上述名称是约定。）

其他：识别上游负责人。ASR 协议 / NIM 部署 → `/riva-asr`。评分 → 此处。

## 限制

- **默认仅英语。** 分词 + 规范化假设使用拉丁字母和 en-US 词汇。
- **严格的连续 KER 是保守的。** 类似 `cefa zolin` 的近似匹配计为错。这是有意为之 — 药房查询对近似匹配无效。想要“软”匹配的用户可以切换到音素级编辑距离，这是一种方法扩展，而不是配置调整。
- **每次评估运行一个模型。** 比较两个模型意味着运行评估两次并比较两个 `leaderboard_cycle<N>.md` 文件（或扩展配方以自行编写多模型行）。
- **仅假设托管路径。** 自托管 NIM 可以工作，但需要先执行 `/riva-nim-setup`。

## 下一步

- **前进（KER > 0.3，manifest ≥ 100 行）：** `/digital-health-clinical-asr-finetune`。
- **返回构建（首次评估 KER 0.1–0.3，或 `magpie_g2p` 间隙）：** `/digital-health-clinical-asr-build`。
- **停止（KER < 0.1）：** 评估已饱和。在宣布胜利前先加固它。
- **横向**用于 ASR 协议 / 认证 / 流式传输 / 自托管 NIM 详情：`/riva-asr`。

## 参考

- [`references/offline-asr-recipe.md`](references/offline-asr-recipe.md) — 完整的 Step 3b Python 配方（`transcribe_manifest`，`resolve_asr_config`，`build_asr_auth`），带调用形状注释的函数-ID 目录，Whisper 降级，自托管 Riva NIM 设置
- [`references/scoring-recipes.md`](references/scoring-recipes.md) — 纯 Python WER/CER/KER/SER 评分函数，带规范 4 步骤规范化
