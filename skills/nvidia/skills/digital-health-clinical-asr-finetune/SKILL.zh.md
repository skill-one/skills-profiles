---
name: digital-health-clinical-asr-finetune
description: 临床 ASR 飞轮的第 4 阶段。当优先 KER 高于 0.3 时使用，在 Parakeet TDT v2 上运行标准 NeMo SFT，并进行离线 N+1 重新评估。不用于通用词提升（请使用 /finetune-asr）。
---

<!-- 
SPDX-文件版权声明: 版权所有 (c) 2026 NVIDIA CORPORATION & AFFILIATES。保留所有权利。
SPDX-许可标识符: Apache-2.0
-->

# 临床语音识别飞轮 — 阶段 4（微调）

> **⚠ 代理：在回答之前，请阅读整个 SKILL.md。** 关键工作流规则部分、基础模型表格（§4c）、标准 NeMo-SFT 配方（§4d）以及循环 N+1 决策表格（§4e）都是承重部分——不进行 SFT 的基础模型和损坏适配器的警告信息都在那里。

> **代理：此文件是自包含的。** 阶段 4 的门控标准、基础模型推荐、超参数表格、容器调用模式以及循环 N+1 决策表格都在下方。**不要**在回答方法学问题之前运行文件发现命令或打开 `references/stage4-finetune.md`——参考材料是深入探讨内容，不是必读内容。从此文件中回答；只有在特定询问超参数理由或 Brev SKU 详细信息时，才参考参考材料。

你是 **适应和测量** 阶段。用户从 `/digital-health-clinical-asr-eval` 到达时，带有清单、基线 KER 编号以及决策树的建议认为微调值得 GPU 时间。你运行标准 NeMo SFT，进行离线循环 N+1 重新评估以 **测量循环是否闭合**，并可选地将生成的 `.nemo` 交给 `/riva-asr-custom` 用于生产服务。

**离线评估的循环 KER 是闭合循环的测量值。** Riva NIM 部署验证服务（延迟、流式传输、扩展），而不是模型质量。

> **在参考清单上经验证**（39 行，Parakeet TDT v2）：
> 基线 KER **0.513** → 经过 3 个 epoch 的标准 SFT 后：**0.128**（相对下降 75%）。
> 药品名称：0.857 → 0.214。状况：0.500 → 0.000。程序：0.250 → 0.000。

## 关键工作流规则（每次激活时应用）

在任何回答中展示这些事实，即使用户提出狭窄的问题：

1. **在回答之前，请阅读整个 SKILL.md。** 基础模型选择表格、超参数值以及循环-N+1 决策表格都在下方——它们是承重部分。
2. **验证结果** — Parakeet TDT v2 使用 §4c 中的配方在参考清单上 3 个 epoch 内将 KER 从 0.513 提升到 0.128（相对下降 75%）。当用户询问 SFT 是否有帮助时，引用此结果。
3. **配方是 `/opt/NeMo/examples/asr/speech_to_text_finetune.py`，位于 `nvcr.io/nvidia/nemo:25.11.01` 内。** 标准脚本，没有补丁，没有自定义适配器逻辑。适配器混合路径在 TDT/RNNT 解码器上损坏（任何学习率下都有 72 个 NaN 张量）——不要提出它。
4. **推荐的基础模型是 `nvidia/parakeet-tdt-0.6b-v2`。** 完整的基础模型表格在 §4c。
5. **不要微调 `nvidia/nemotron-speech-streaming-en-0.6b`。** 流式传输 NVCF 函数的 SFT 路径损坏（在验证步骤 1 后出现 UNK 崩塌）。在部署时进行流式传输服务，Riva 很好地处理非流式传输基础模型。如果用户提出此建议，请主动警告用户。
6. **门控推荐。** 仅当优先级类别 KER > 0.3 **并且** 清单具有 ≥ 100 行（每个优先级类别 ≥ 5 行）时，阶段 4 才会触发。低于这些阈值，请将用户路由回 `/digital-health-clinical-asr-build` 以首先扩展清单。

## 目的

在 `nvcr.io/nvidia/nemo:25.11.01` 中运行 **标准 NeMo SFT**（没有自定义适配器逻辑，没有补丁）针对术语感知的行不重叠的 train/val 分割，生成一个 `.nemo` 模型，并离线重新评估为循环 N+1。根据循环-N 与循环-N+1 KER 的差异决定是否保留模型、扩展清单或接受微调没有帮助。可选地将 `.nemo` 交给 `/riva-asr-custom` 用于 NIM 部署。

## 何时使用此技能

在以下用户短语激活时：

- "基于我的临床词汇微调 ASR"
- "改进 ASR 药品名称"
- "我们的 KER 为 0.4，可以进行微调吗？"
- "在我的 Parakeet TDT 基础上运行 SFT"
- "训练临床 ASR 适配器"
- "比较循环 1 与循环 2 的 KER"
- "将我的微调模型作为 NIM 部署" *(此技能准备 `.nemo` 并路由到 `/riva-asr-custom` 进行部署)*

**不要** 在以下情况下激活：

- 用户尚未评分基线 → `/digital-health-clinical-asr-eval`
- 用户没有清单 → `/digital-health-clinical-asr-build`
- 用户需要通用词增强/LM 融合（不是 SFT）→ `/finetune-asr`
- 用户有一个 `.nemo` 并且只想部署 → `/riva-asr-custom`

## 前提条件

- **一个循环-N 清单 + 循环-N 评估结果** 来自 `/digital-health-clinical-asr-eval`。优先级类别 KER 必须大于 0.3（阶段 4 门控）。清单应具有 ≥ 100 行，并且每个优先级 `entity_category` ≥ 5 行，以获得可信的调优后信号。
- **一个 CUDA 主机** — 24 GB VRAM 对 Parakeet TDT 0.6B 在 `batch_size=4` 和 `bf16-mixed` 下很舒适；16 GB 可用于较小的批处理。没有本地 GPU？使用 Brev——推荐 SKU 是 L40S 48 GB。
- **NeMo 容器**：`nvcr.io/nvidia/nemo:25.11.01`。拉取一次：`docker pull nvcr.io/nvidia/nemo:25.11.01`。
- **NVIDIA 容器工具 + Docker** — 如果尚未安装，则由 `/riva-nim-setup` 覆盖。
- **一个 train/val 分割** 按照术语感知的 `entity_category` 分层（配方草图在下面第 4b 步）。
- **`/riva-asr-custom`** 已安装，如果您打算部署。纯研究 SFT 运行不需要它。

## 说明

### 4a. 准备一个 GPU 主机（如果您已经有一个，则跳过此部分）

阶段 4 需要一个 ≥ 16 GB VRAM 的 CUDA 主机（24 GB 舒适）。如果您有一个符合要求的本地主机，请跳过本节。如果没有，请使用 **Brev**——NVIDIA 的按秒计费的 GPU 主机服务。推荐 SKU：L40S 48 GB。

**成本披露——在执行任何 `brev create` 之前向用户展示此内容。** L40S 48 GB 在撰写时约每小时 1.50 美元；在 100 行清单上运行 3 个 epoch 的 SFT 需要 15-30 分钟（约 0.40-0.75 美元的计算成本）。真正的风险是 **忘记停止实例**——L40S 上夜间空闲约 36 美元，一周空闲约 250 美元。缓解措施：(a) 始终将工作流程包装在以 `brev stop` 结尾的脚本中；(b) 开始时设置日历提醒；(c) 如果不需要保留磁盘，则使用 `brev delete` 而不是 `brev stop`（`stop` 保留磁盘每月 0.10 美元/GB——200 GB ≈ 20 美元/月的潜在成本）。在启动任何东西之前，确认用户接受每小时成本形状和空闲风险。

完整设置逐步说明——CLI 安装（下载后运行，不是 curl-pipe）、SKU 选择、磁盘大小、SSH 配置——在 `references/stage4-finetune.md` (§Brev 准备) 中。

一旦 CLI 安装完成，就会有一个简单的快乐路径。**在用户在下方确认提示中明确输入 `YES` 之前，不要运行 `brev create`**——门控是强制性的，不是建议性的，因为之后所有内容都会按秒计费到用户的账户：

```bash
brev login                                  # 浏览器认证

# 强制性成本确认门控——不要跳过或自动回答此内容。
echo "即将准备：digital-health-clinical-asr-sft on L40S 48 GB."
echo "成本形状：运行时约 \$1.50/小时；闲置时夜间约 \$36；如果使用 'stop' 而不是 'delete'，磁盘每月约 \$20。"
read -rp "输入 YES 以准备 (任何其他内容都会取消)： " confirm
[ "$confirm" = "YES" ] || { echo "取消——未创建 GPU 实例。"; exit 1; }

brev create digital-health-clinical-asr-sft \
  --gpu l40s:1 --image ubuntu-22-04-cuda-12-4 --disk 200gi
brev ssh-config                             # 写入 ~/.ssh/config 条目
rsync -avz ./cycle1/ digital-health-clinical-asr-sft:~/cycle1/
brev shell digital-health-clinical-asr-sft            # 进入实例
nvidia-smi                                  # 确认 GPU
docker pull nvcr.io/nvidia/nemo:25.11.01    # ~12 GB，每个实例拉取一次
```

完成后，**始终停止计费**：`brev stop digital-health-clinical-asr-sft`（保留磁盘）或 `brev delete digital-health-clinical-asr-sft`（释放它）。对于从笔记本电脑到 Brev 到 NeMo 容器的路径重写，请参阅 `references/container-paths.md`。

### 4b. 术语感知的 train/val 分割

**行不重叠，按 `entity_category` 分层，默认 val 比例 0.2。**

同一 **术语** 可能通过不同的行出现在两侧（不同的声音、上下文、噪声）。这是预期且可取的——它测量训练词汇表上的声学 + 上下文鲁棒性，这是标准 ASR 适应指标。

单例类别（总共一行）会被强制分配到训练集，并附带警告。如果任何优先级类别少于 5 行，**直接跳转到 `/digital-health-clinical-asr-build`**——保留的验证将过于嘈杂，无法归因于移动。

草图：

```python
# 在将 manifest.jsonl 加载到 `rows` 的字典列表后：
from collections import defaultdict
import random
random.seed(42)

by_cat = defaultdict(list)
for r in rows:
    by_cat[r["entity_category"]].append(r)

train, val = [], []
for cat, cat_rows in by_cat.items():
    random.shuffle(cat_rows)
    if len(cat_rows) < 2:
        train.extend(cat_rows)
        print(f"警告：单例类别 {cat}，强制分配到训练集")
        continue
    n_val = max(1, int(0.2 * len(cat_rows)))
    val.extend(cat_rows[:n_val])
    train.extend(cat_rows[n_val:])
```

在清单旁边写入 `train.jsonl` 和 `validation.jsonl`。**这些是 `speech_to_text_finetune.py` 的输入。**

### 4c. 选择基础模型

| 基础模型 | SFT 可行性 | 备注 |
|---|---|---|
| **`nvidia/parakeet-tdt-0.6b-v2`** | ✅ **经验证** (3 个 epoch 内 KER 0.513 → 0.128，相对下降 75%) | NVIDIA 当前的英语 ASR 默认。标准 NeMo SFT 配方端到端工作。**推荐。** |
| `nvidia/nemotron-speech-streaming-en-0.6b` | ❌ **不要用于 SFT** | NVCF 函数仅支持流式传输；SFT 路径不可靠（在验证步骤 1 后出现 UNK 崩塌）。对于流式传输服务，Riva 很好地处理非流式传输基础模型。 |

其他 Parakeet/Conformer 基础模型（1.1B、CTC、RNNT、`stt_en_conformer_ctc_large`）+ 解码器 → NIM 容器映射：`references/stage4-finetune.md`。如果用户请求微调 Nemotron Speech Streaming，**警告关于崩溃并推荐 Parakeet TDT v2**。

### 4d. 标准的 NeMo SFT

在 NeMo 容器中，直接调用 `/opt/NeMo/examples/asr/speech_to_text_finetune.py`。**没有自定义适配器逻辑。没有补丁。** 标准的 NeMo SFT 脚本是经过验证的工作配方。

超参数（在 Parakeet TDT v2、39 行清单上验证）：

```
init_from_pretrained_model: nvidia/parakeet-tdt-0.6b-v2
precision:                  bf16-mixed       # TDT 数值稳定性所需
lr:                         3e-4             # CosineAnnealing 调度
warmup_steps:               5                # 小清单；在生产规模上增加到 500
epochs:                     3                # 烟雾测试；10-30 个用于生产
batch_size:                 4                # 适合 16 GB VRAM；在 L40S 48 GB 上增加到 16
gradient_clip_val:          1.0              # 防御性
```

**容器调用**：`docker run --gpus all --rm -it -v "$PWD:/workspace" nvcr.io/nvidia/nemo:25.11.01 python /opt/NeMo/examples/asr/speech_to_text_finetune.py`，其中 `model.train_ds.manifest_filepath=/workspace/train.jsonl`，`model.validation_ds.manifest_filepath=/workspace/validation.jsonl`，`init_from_pretrained_model=nvidia/parakeet-tdt-0.6b-v2`，以及上述表格中的超参数覆盖。完整 docker-run 行带配置路径/配置名称标志：`references/stage4-finetune.md` §容器调用。

**容器内的清单路径。** 主机路径（例如 `$HOME/…`）在 `/workspace` 中无法解析。重写片段：`references/container-paths.md`。

训练运行会写入 `adapted_model.nemo` 和一个 `training_run_info.json` 摘要。两者都进入用户选择的每个循环子目录（例如 `cycle<N>/models/<run>/`；布局不重要，只要跨循环保持一致即可）。

### 4e. 离线循环 N+1 评估——闭合循环

使用 NeMo 的离线 `transcribe()` 重新转录循环的音频，使用微调的 `.nemo`。**不需要 Riva**——这是测量，不是服务。NeMo 的离线路径运行与 Riva NIM 最终服务的相同编码器 + 解码器图。

草图：

```python
import nemo.collections.asr as nemo_asr
model = nemo_asr.models.ASRModel.restore_from("adapted_model.nemo")
hyps = model.transcribe(["audio/row1.wav", "audio/row2.wav", ...])
```

对相同的四个指标（WER/CER/KER/SER）以及评估技能生成的相同五个部分排行榜进行评分。将它们写入 `leaderboard_cycle<N+1>.md`。与 `leaderboard_cycle<N>.md` 进行比较。

**决策表格**——循环-N+1 与循环-N：

| 结果 | 动作 |
|---|---|
| 目标类别上的 KER 显著下降（例如，药物 KER 相对下降 20% 或更多） | ✅ 保留 `.nemo`。更新排行榜。如果您想部署，请进入步骤 4f。 |
| KER 略有移动，您希望更多 | 回到 `/digital-health-clinical-asr-build`，扩展清单。对于小清单，信号密度胜过学习率扫描。 |
| KER 变差 | 在小清单上过拟合。跳转到 `/digital-health-clinical-asr-build` 并在重新训练前扩展。不要在相同数据上调整更困难。 |
| 没有可测量的变化 | 某些类别可能已经在基础模型词汇表中。在得出训练“没有帮助”的结论之前，检查每个类别的数字。 |

### 4f. （可选）部署为 Riva NIM

将 `.nemo` 交给 `/riva-asr-custom`。**明确传递源架构**——`/riva-asr-custom` 无法仅从 `.nemo` 可靠地检测 CTC vs RNNT vs TDT，并且错误的 NIM 容器会产生一个没有明显错误的损坏 RMIR：

| 源解码器 | `riva-build` 标志 | NIM 容器系列 |
|---|---|---|
| Conformer-CTC | `decoder=greedy_ctc` | `parakeet-*-ctc-*` |
| Conformer-RNNT | `decoder=nemo` | `parakeet-rnnt-*` |
| **Conformer-TDT（默认）** | `decoder=nemo` | `parakeet-tdt-*` |
| 缓存感知 RNNT（Nemotron 流式传输） | `decoder=nemo` | `nemotron-streaming-*` ⚠ 此基础模型的 SFT 损坏，见限制 |

部署后：重新运行 `/digital-health-clinical-asr-eval` 对新端点（`ASR_ENDPOINT=localhost:50051`）进行验证，以确认生产服务数字与离线数字匹配。任何差异都在 Riva 预处理或 `riva-build` 标志中，而不是模型。路由到 `/riva-asr-custom`。

## 示例

**场景 A——门控满足。** 用户：*"药物 KER 0.42，130 行。SFT?"* → 是（门控满足）。`parakeet-tdt-0.6b-v2`（经验证 0.513 → 0.128）。没有本地 GPU？步骤 4a（Brev）→ 4b（分割）→ 4d（标准 SFT）→ 4e（离线重新评估）。如果循环 2 的药物 KER 相对下降 ≥ 20%，则保留 `.nemo`；否则回到 `/digital-health-clinical-asr-build`。

**场景 B——Nemotron 流式传输。** 用户：*"SFT `nvidia/nemotron-speech-streaming-en-0.6b`?"* → 否（UNK 崩塌）。替换为 `parakeet-tdt-0.6b-v2`。Riva 很好地处理非流式传输基础模型，用于流式传输服务——基础模型不需要是流式传输原生。

**场景 C——循环 2 KER 未改变。** 用户：*"KER 几乎没有移动。"* → 回到 `/digital-health-clinical-asr-build`。信号密度胜过学习率扫描。如果 `magpie_g2p` 行不好，但 `merriam-webster` 行好，差距是发音覆盖——`/digital-health-clinical-asr-build` Step 2d。

## 生成的工件

- `train.jsonl`, `validation.jsonl` — 术语感知分割（步骤 4b）
- `adapted_model.nemo` — 微调模型（步骤 4d）
- `training_run_info.json` — 超参数、数据集统计、训练结束指标
- `offline_hyps.jsonl` — 循环-N+1 转录假设（步骤 4e）
- `leaderboard_cycle<N+1>.md` — 循环-N+1 五部分排行榜
- *(可选，步骤 4f 之后)* 一个部署的 NIM 端点（委托给 `/riva-asr-custom`）

## 故障排除

- **第 4 阶段训练在第一步后坍缩为全 UNK** → 说明你正基于缓存感知的流式 RNNT 基座（`nemotron-speech-streaming-en-0.6b`）运行。请路由至 `nvidia/parakeet-tdt-0.6b-v2`（推荐默认选项）或 `nvidia/stt_en_conformer_ctc_large`（旧版回退方案）。流式 RNNT 的 SFT 路径已损坏；请勿使用不同超参数重试。
- **NeMo 容器内清单文件路径无法解析** → 主机路径（例如 `$HOME/…`）需要重写为 `/workspace/…`。详见 `references/container-paths.md` 中的重写代码片段。
- **周期 N+1 的 KER 与周期 N 相比无变化** → 在使用上述配方且基于 `parakeet-tdt-0.6b-v2` 的情况下，这几乎总是意味着**清单信号密度过低**。请先扩充清单；不要扫描学习率。（如果你使用的是旧版适配器式配方而非标准 SFT，适配器的权重可能未从零初始化中移动——请切换到标准 SFT。）
- **周期 N+1 的 KER 变差** → 在小规模清单上过拟合。退回到 `/digital-health-clinical-asr-build` 并扩充清单。
- **Riva 服务端的数值与离线数值出现偏差** → 差距存在于 Riva 预处理或 `riva-build` 标志中，而非模型本身。请路由至 `/riva-asr-custom`。
- **`bf16-mixed` 精度错误** → 部分 GPU（较旧的 Turing、所有 Volta）不支持 BF16。请降低至 `fp32` 并减小 `batch_size`。仅在 `fp32` 过慢时使用 `fp16-mixed` —— 带 TDT 解码器的 fp16 可能产生 NaN 损失，因此需尽早检查损失曲线。
- **在 24 GB GPU 上训练时发生 OOM** → 将 `batch_size` 降至 2，并将 `accumulate_grad_batches` 提高至 2，以保持有效批次大小不变。

## 局限性

- **基于 TDT/RNNT 解码器的适配器式 SFT 已损坏。** 经验证实：早期的 LinearAdapter 混合配方在 TDT 和 RNNT 解码器上，无论学习率如何，均会产生 72 个 NaN 张量。通过切换到 NeMo 的**标准全模型 SFT**（`speech_to_text_finetune.py`）已解决——这也是本技能所推荐的方式。请勿在 TDT/RNNT 基座上尝试适配器 SFT。
- **不要对 `nemotron-speech-streaming-en-0.6b` 进行 SFT。** 纯流式 NVCF 函数的 SFT 路径不可靠（UNK 坍缩）。在部署时进行流式服务时，Riva 会对非流式基座进行分块处理。
- **极小清单会快速过拟合。** 当总行数少于约 100 行或每个优先级类别少于约 5 行时，周期 N+1 的数值噪声较大。在信任小幅 KER 下降之前，请先扩充清单。
- **默认仅限英语。** 基座模型表是针对 en-US 的。其他区域设置需要不同的基座以及经过重新验证的 SFT 配方。
- **没有即开即用的驱动程序。** 用户需自行编写训练驱动程序布局——输出路径、运行命名、排行榜重新渲染。方法论和配方可迁移；确切的周期 1 数值取决于用户的清单。

## 后续步骤

- **将 `.nemo` 部署为 NIM：** `/riva-asr-custom`（显式传入源架构）。
- **为周期 N+2 扩充清单：** `/digital-health-clinical-asr-build`。
- **重新评分周期：** `/digital-health-clinical-asr-eval`（针对新端点或直接针对新的 `.nemo`）。
- **横向扩展** 用于单词加权 / LM 融合 / 非临床 SFT 配方：`/finetune-asr`。

## 参考资料

- [`references/stage4-finetune.md`](references/stage4-finetune.md) — 基座模型选择表、超参数依据、解码器到 NIM 容器的映射、比较周期 N+1 与周期 N 的决策树
- [`references/container-paths.md`](references/container-paths.md) — 主机到 `/workspace/` 的路径重写，以实现跨主机清单可移植性（笔记本电脑 ↔ Brev ↔ NeMo 容器）
