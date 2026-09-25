# 临床语音识别飞轮 — 第二阶段（构建基准）

> **⚠ 代理：在回答之前，请阅读整个 SKILL.md。** 这一阶段是对话式的，并且有门槛。具体来说：在提出术语（步骤 2a）之前，请向用户询问 1-2 个与专业相关的澄清问题，引导他们通过双层 IPA 管道（覆盖 → 麦理浩 → magpie_g2p）（步骤 2c），在完整的笛卡尔合成之前，在步骤 2d 中命中明确的 QA 模式试听门禁，并在第三阶段中命名 **KER** 作为他们将在第三阶段看到的头条指标。跳过任何这些都会使方法失效。

你是 **策展和综合** 阶段。用户从 `/digital-health-clinical-asr-setup` 到来，并带有 NeMo 格式的 `manifest.jsonl` 以及它引用的音频——两者都准备好在 `/digital-health-clinical-asr-eval` 进行评分。

保持对话式。这是飞轮中最温暖、最了解领域的步骤：你正在询问临床医生（或与他们一起工作的人）哪些术语今天造成了困扰，并围绕他们的现实塑造基准。问简短、专注的问题。向用户展示正在添加的内容。不要说教。

## 数据离开你的环境——在任何术语发送之前向用户披露这一点

这一阶段将用户策展的内容传输到两个外部服务。在调用任何调用之前向用户展示这一点：

| 服务 | 发送什么 | 何时 |
|---|---|---|
| **麦理浩** (`dictionaryapi.com` API 或 `merriam-webster.com` 公共网站) | 种子列表中的每个术语一个 HTTP 请求——术语在 URL 路径中 | 步骤 2c — 下方 MW 路径要点 |
| **NVIDIA NVCF Magpie TTS** (`grpc.nvcf.nvidia.com`) | 每个生成的临床句子（文本，以及任何 SSML IPA 包装） | 步骤 2d 和 2e，每次合成调用 |

两个端点都期望 **非 PHI 合成内容**——你策展的术语列表，`/data-designer`（或你的备用模板）从它生成的句子。**不要通过这个技能传递真实的患者记录、真实的 ASR 文本或任何 PHI。** 如果术语列表本身是敏感的（专有药物名称、未发布的产品名称、客户机密适应症），请在继续之前与用户确认外部 API 传输是否符合其组织的数据治理政策。

如果没有可接受的 MW 传输：采取下方的路径 C（跳过 MW；管道落入 Magpie G2P，对长尾术语的覆盖率降低）。

## 目的

策展临床专业术语列表，通过 Magpie TTS 使用双层 IPA 管道生成评估音频，并编写带有临床扩展字段的 NeMo 格式 manifest（`term`、`entity_category`、`ipa_source`、`voice_id`、`noise_level`、`context_type`）。输出是第三阶段的输入。

到结束时，用户将拥有：

```
$EVAL_DIR/cycle<N>/
├── audio/<slug>.wav        合成的片段
├── manifest.jsonl          NeMo 格式 + 临床扩展
├── term_seed.csv           策展的输入
└── pronunciation_overrides.csv   可跨周期追加
```

（`$EVAL_DIR` 是用户自己的选择——这个技能不会强加布局。上面的结构是一个建议，不是一个要求。）

## 何时使用此技能

在以下用户短语激活：

- "构建临床 ASR 基准"
- "策展用于 ASR 评估的药物名称/程序名称"
- "为医疗术语生成评估音频"
- "从临床术语创建 NeMo manifest"
- "将肿瘤学/心脏病学/骨科术语添加到我的基准"
- "试听这些药物名称的 TTS 发音"
- "为我制作 cycle-N manifest"

**不要** 在以下情况下激活（也：如果消息提到 `auth`、`API key`、`gRPC`、`streaming`、`riva-build`、`NIM deploy`、`NGC` 或 `Docker`，按照下方的要点路由并停止）：

- 用户已经有一个 manifest 并想对其进行评分 → `/digital-health-clinical-asr-eval`
- 用户想对现有的 manifest 进行微调 → `/digital-health-clinical-asr-finetune`
- 用户在问通用的 TTS / SSML / 语音克隆 / 语音目录问题 → `/read-aloud`（或 `/riva-tts`）
- TTS/ASR **auth / API keys / gRPC / streaming** → `/riva-tts` 或 `/riva-asr`
- **NIM deploy** 或 `riva-build` / `riva-deploy` 标志 → `/riva-asr-custom` 或 `/riva-tts-custom`
- **NGC / Docker / NVIDIA 容器工具包** → `/riva-nim-setup`
- 用户在问通用的合成数据问题 → `/data-designer`

## 前提条件

- **`/digital-health-clinical-asr-setup` 已完成** — `NVIDIA_API_KEY` 导出，Python 依赖项安装，六个上游技能确认。
- **`/read-aloud`**（或 `/riva-tts`）可到达。默认通过 NVCF 托管的 Magpie。自托管的 Magpie NIM 可以工作，但会增加 `/riva-nim-setup` 到前提条件链。
- **`/data-designer`** 可到达。如果 `/data-designer` 不可用，对于第一个周期可以使用 4 个模板的备用方案，但请标记那些行，以便未来的周期可以重新生成。
- **一个用户拥有的工作目录**。该技能建议 `$EVAL_DIR/cycle<N>/`，但不强制执行它。

## 说明

### 2a. 专业访谈 → `term_seed.csv`

一次问 **一个问题**。目标是在正确的 `entity_category` 下浮现 4-10 个候选术语，而不是写教科书。

问题按顺序：

1. *这个专业/工作流程是什么？*（肿瘤学听写、ICU 交接、精神科入院、骨科术后、…）
2. *你见过哪些 ASR 失效模式？* — 药物名称、多词程序、缩写、复合疾病。
3. *哪些术语是日常出现的，哪些是困难的？* — 日常常见术语成为基准；日常困难术语成为信号。

提出 4-10 个具有 `entity_category` 的候选术语。在写入之前与用户确认。然后写入 `term_seed.csv`：

```csv
term,entity_category
cefazolin,drug
acetabular reamer,procedure
tibial plateau,anatomy
femoroacetabular impingement,condition
hemoglobin a1c,lab
respiratory therapist,role
```

**类别词汇是固定的。** KER 依赖于此。允许的值：

```
drug | procedure | anatomy | condition | lab | role
```

如果用户提出一个新的类别，请反对：要么它映射到六个之一，要么方法论需要故意的扩展（这是未来周期的任务，而不是一次性临时添加）。

### 2b. 通过 `/data-designer` 生成句子

简要 `/data-designer`：

> 对于 `term_seed.csv` 中的每一行，生成一个或多个嵌入 `term` 的自然英语句子，使其适合行的 `entity_category`。输出模式：`{term, entity_category, sentence, context_type}`。每个术语生成 3-5 个 `context_type` 变体。初始 `context_type` 词汇：`dictation`、`handoff`、`chart_note`、`history`。句子长度 10-30 个词。

这一步的输出是每个术语的句子变体文件。任何文件名都可以——选择一个并跨周期目录一致地使用它。

**模板备用。** 如果 `/data-designer` 不可用，使用 4 个模板备用（每个 `context_type` 一个），并机械地替换 `term`。在 manifest 中标记这些行（`context_type` 已设置，句子只是不那么自然），以便未来的周期可以重新生成。

### 2c. 双层 IPA 标记（承重质量杠杆）

每个术语都通过一个 3 层管道，按顺序通过：

1. **覆盖** — `pronunciation_overrides.csv` 携带团队已审核的 IPA。如果 `term` 匹配这里的行，覆盖将获胜。
2. **麦理浩** — 对于未覆盖的术语，获取 MW 重写，转换为 IPA，验证 Magpie 的 en-US 音素集。如果两者都成功，则该术语标记为 `merriam-webster`。
3. **Magpie G2P（默认）** — 如果覆盖或 MW 都未产生有效的 IPA，则将纯文本传递给合成时间的 Magpie 神经 G2P。该行标记为 `magpie_g2p`。

每个 manifest 行都带有 `ipa_source` 标签（`override | merriam-webster | magpie_g2p`）。第三阶段排行榜中 `merriam-webster` 和 `magpie_g2p` 之间的差异**是证明**发音策略正在起作用的证据——在生成排行榜时明确指出。

**三个 MW 查找选择**——都标记为 `merriam-webster`。**A**：`dictionaryapi.com` JSON API + `DICTIONARY_API_KEY`（dictionaryapi.com 上的免费）——推荐用于独立使用。**B**：`merriam-webster.com` 的 HTML 抓取——没有密钥，对网站 HTML 变化很脆弱；配方在 `references/pronunciation-pipeline.md` 中内联。**C**：跳过 MW，默认落入 Magpie G2P，长尾术语覆盖率较弱。两个配方 + 完整的 respelling→IPA 表在 `references/pronunciation-pipeline.md` 中。路径 A 函数将 `api_key` 作为参数（从不读取 `os.environ`）；传递 `None` 跳过 MW。

`pronunciation_overrides.csv` 模式：

```csv
term,ipa,verified_by,verified_at,notes
cefazolin,sɛfəˈzoʊlɪn,brandoing,2026-05-13,确认与 MW 重写 + 耳朵测试
```

可跨周期追加。稍后重新运行构建会自动获取新条目。

### 2d. QA 模式合成（**不要**跳过此门禁）

在运行完整的笛卡尔乘积之前，使用：第一个声音、干净噪音、默认上下文合成**每个术语一个 wav**。与用户试听每个片段。

对于标记为 `magpie_g2p` 的每个术语，使用临床后缀模式提出 IPA 候选方案，并在建议之前验证它是否与 Magpie 的 en-US 音素集匹配：

| 后缀 | 重音模式（示例） |
|---|---|
| `-mycin` | …ˈmaɪsɪn（万古霉素、庆大霉素） |
| `-prazole` | …ˈpreɪzoʊl（埃索美拉唑、奥美拉唑） |
| `-statin` | …ˈstætɪn（阿托伐他汀、瑞舒伐他汀） |
| `-sartan` | …ˈsɑːrtən（洛沙坦、缬沙坦） |
| `-azole` | …ˈeɪzoʊl（氟康唑、酮康唑） |
| `-cillin` | …ˈsɪlɪn（阿莫西林、哌拉西林） |
| `-parin` | …ˈpɛərɪn（依诺肝素、肝素） |

**音素验证模式** — 使用候选 IPA 实时探查 Magpie 的 en-US 神经 G2P。如果 Magpie 接受 SSML，则 IPA 在其库存中。使用上述后缀模式作为 *预过滤器*（廉价的启发式方法），并使用实时探查来确认，然后再提交覆盖。`magpie_validates_ipa(ipa, api_key, voice_id)` 配方——一个最小的 NVCF gRPC 合成调用，返回 `True`/`False` 封闭失败——在 `references/pronunciation-pipeline.md` 中（§合成调用）。

在向用户展示候选 IPA 之前调用一次。在用户批准后，将验证的 IPA 追加到 `pronunciation_overrides.csv`。在下一个 manifest 生成时，该行的 `ipa_source` 从 `magpie_g2p` 转换为 `override`。

**在步骤 2e 之前进行 HITL 试听门禁——封闭失败。** 不要合成完整的笛卡尔乘积，不要将任何阶段 IPA 候选方案提升到 `pronunciation_overrides.csv`，并且不要进入第三阶段，直到**在对话中明确发生了以下之一**：

1. **用户确认他们已试听过 QA 片段** 并报告每个片段（或每个桶）的裁决（例如：“MW 集合听起来很好”，“修复 `pembrolizumab`” 等）。提供 `afplay`（macOS）或 `paplay`/`aplay`（Linux）命令，以便用户可以播放它们——然后 **暂停并等待他们听完后回复**。仅通过 AskUserQuestion 提示的纸质批准——点击“全部提升”或“锁定”——**不满足此门禁**。Magpie 验证 IPA 证明它存在于音素库存中；它不能证明它与 *预期的* 发音匹配。只有用户的耳朵才能做到。
2. **用户明确选择跳过此周期的试听**，使用明确的语言（例如 *"跳过试听，接受发音错误可能稀释第三阶段 KER 信号的风险——将其记录为 cycle-N 备注"*），而不是作为单个点击通过的效果。在周期级注释中记录跳过（例如 `eval/cycle<N>/cycle_notes.md`），以便未来的操作员可以看到试听被推迟。

Magpie NVCF 对大于 100 行的工作进行激进的限制，重跑既消耗 API 信用也消耗时间——但更大的风险是发布带有发音错误的参考音频，这会悄悄地破坏第三阶段的 KER 信号。花时间试听比重新运行周期更便宜。

### 2e. 完整基准生成

在发音锁定后，生成完整的笛卡尔乘积 `|terms| × |voices| × |noise_levels| × |context_types|`。默认：2-4 个 Magpie en-US 声音（Mia/Jason/Ray）、`[clean, snr_15db, snr_5db]`、`[dictation, handoff, chart_note, history]`。

自包含合成——不需要 `/read-aloud`。`synthesize_row(row, all_overrides, out_dir, api_key)` 配方——打开 NVCF gRPC 流，通过 `render_sentence_with_overrides` 将覆盖包装到 SSML，将 16 位单声道 PCM 写入 `<out_dir>/audio/<slug>.wav`——在 `references/pronunciation-pipeline.md` 中（§合成调用）。关键不变量：`all_overrides` 携带 `pronunciation_overrides.csv` 中的 *每个* 条目（包括上下文词覆盖，如 `intravenously`），以便渲染器包装任何覆盖，其纯文本出现在 `row['text']` 中。仅包装 `row['term']` 会默默地丢失上下文词覆盖。

噪音注入（干净 → `snr_15db` → `snr_5db`）和 manifest 模式（NeMo 标准字段 + 临床扩展，加上预飞行模式和音频存在检查）都住在 `references/manifest-schema.md` 中。

**当产品大于 100 行时发出警告。** Magpie NVCF 在大运行中大约有 5-10% 的 `RESOURCE_EXHAUSTED` 落差。预算一个重跑通过。

### 第二阶段完成清单

在所有五个子步骤运行之前，不要认为第二阶段完成。代理通常在 2a 或 2b 后停止；目标是合成 manifest 加上交接：

- **2a** — `term_seed.csv`，4-10 个术语，`entity_category ∈ {drug, procedure, anatomy, condition, lab, role}`
- **2b** — 每个术语 3-5 个 `context_type` 句子变体
- **2c** — 每个术语标记 `ipa_source ∈ {override, merriam-webster, magpie_g2p}`
- **2d** — QA wavs 试听过，IPA 覆盖通过明确的用户批准锁定
- **2e** — `manifest.jsonl` + 符合笛卡尔乘积的每行音频
- **交接** — 将 `/digital-health-clinical-asr-eval` 命名为下一个技能，并将 **KER** 命名为其头条指标

写入仅进入用户选择的 `$EVAL_DIR/cycle<N>/`。不要写入其他地方，修改环境或安装包——这些属于 `/digital-health-clinical-asr-setup`。

## 示例

**场景 A — 新鲜肿瘤学基准。** 用户：*"我们正在看到化疗药物名称被错误转录。我从哪里开始？"* → Step 2a：确认专业是肿瘤学，询问哪些药物（免疫疗法生物制剂、铂类制剂、紫杉类）。提出 ~10 个候选：`cisplatin`、`paclitaxel`、`pembrolizumab`、`nivolumab`、`carboplatin`、`docetaxel`、`bevacizumab`、`trastuzumab`、`cetuximab`、`pemetrexed`。写入 `term_seed.csv`，所有 `entity_category=drug`。Step 2b：简要 `/data-designer`，每个上下文变体 4 个 = 40 个句子。Step 2c：为每个术语进行 MW 查找——生物制剂如 `pembrolizumab` 可能会落入 `magpie_g2p`；铂类制剂可能命中 MW。Step 2d：合成每个术语的 QA wav，引导用户通过 `pembrolizumab` 等片段，提出 `-mab` 后缀重音模式。Step 2e：在批准后，运行 10 个术语 × 2 个声音 × 2 个噪音级别 × 3 个上下文 = 120 行。

**场景 B — 追加到现有周期。** 用户：*"我有一个 cycle-1 manifest，我想添加 5 个程序。"* → 仅重新运行步骤 2a（仅针对新术语的专业访谈）、2b（为新增生成句子）、2c（为新增进行 IPA 管道）、2d（试听新术语）和 2e（仅合成新术语行）。追加到现有的 `manifest.jsonl`。**不要**重新生成现有术语的音频——周期隔离是故意的，以便排行榜干净地比较 cycle N vs cycle N+1。

## 产出物

- `term_seed.csv` — 策展的术语与 `entity_category`
- `pronunciation_overrides.csv` — 验证的 IPA，**可跨周期追加**
- `manifest.jsonl` — NeMo 格式，带有临床扩展字段（每行一个 JSON 对象）
- `audio/<slug>.wav` — 合成的片段，每个 manifest 行一个

## 故障排除

- **TTS rate-limit 落差 (`RESOURCE_EXHAUSTED`)** 在 >100 行生成时 → 预期在 Magpie NVCF 上。确认指数退避在 `/read-aloud` 中激活；预期在大运行中 ~5-10% 落差，并重新运行以填补空白。
- **所有 `ipa_source` 行标记为 `magpie_g2p`** → MW 查找全面失败，或者候选 IPA 失败音素验证。重新验证你配置的 MW 路径（`DICTIONARY_API_KEY` 对于 A；HTTPS 可达性 + 解析器对于 B），然后检查候选是否与 Magpie 的 en-US 音素库存匹配。
- **Magpie 发音错误，即使有 IPA 覆盖** → 首先验证 IPA 在 Magpie en-US 音素库存中，并且 SSML 包装在语法上有效。如果两者都检查合格，则底层 TTS 错误由 `/read-aloud` (`/riva-tts`) 拥有——路由到那里进行诊断。这个技能提供覆盖机制，但不拥有神经 G2P 或 SSML 解析器。
- **来自 `/data-designer` 的句子变体平淡/模板化** → 检查简要；模式提示有时会产生刻板印象的输出。在简要中添加 1-2 个上下文示例并重新运行。
- **音频文件存在，但 `manifest.jsonl` 很短** → manifest 写入器跳过了返回 NVCF 错误的行。重新运行构建，仅使用缺失的行。

对于此列表中未提及的任何内容，确定哪个上游技能受影响并路由到那里。`digital-health-clinical-asr-build` 技能拥有方法论，而不是 TTS 或 DataDesigner 内部。

## 限制

- **默认英文。** Magpie 的 en-US 音素库存是双层 IPA 管道验证的。其他地区需要不同的上游音素集 + 覆盖 CSV 格式。
- **六个固定的实体类别。** 扩展 `entity_category` 是故意的方法论变化，而不是一次性调整——KER 分解、排行榜部分和下游微调脚本都依赖这个词汇。
- **第一个周期很小。** 低于 ~20 个术语，`by-` `ipa_source` 排行榜分割在每个桶中不会足够多，以具有统计学意义。即使成本很高，也要构建一个有意义的周期。

## 下一步

- **向前：** `/digital-health-clinical-asr-eval` — 转录 manifest，评分 WER/CER/KER/SER，生成五部分排行榜。
- **回到设置**（如果环境中的任何内容都损坏）：`/digital-health-clinical-asr-setup`。
- **横向**用于 TTS 特定调试：`/read-aloud` 或 `/riva-tts`。

## 参考

- [`references/manifest-schema.md`](references/manifest-schema.md) — NeMo 标准字段 + 临床扩展；预飞行模式和音频存在检查；跨周期稳定性规则
