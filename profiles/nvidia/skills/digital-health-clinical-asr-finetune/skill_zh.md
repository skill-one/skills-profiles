# 临床语音识别飞轮——第4阶段（微调）

> **⚠ 代理：在回答之前，请阅读整个 SKILL.md。** 关键工作流规则部分、基础模型表（§4c）、标准NeMo-SFT配方（§4d）和循环N+1决策表都是承重部分——不进行SFT的基础和损坏适配器的警告都在那里。

> **代理：此文件是自包含的。** 第4阶段的门控标准、基础模型推荐、超参数表、容器调用模式和循环N+1决策表都在下面。**不要**在回答方法学问题之前运行文件发现命令或打开`references/stage4-finetune.md`——参考材料是深入探讨内容，不是必读内容。从此文件中回答；只有在具体询问超参数推理或Brev SKU详细信息时才参考参考材料。

你是**适应和测量**阶段。用户从`/digital-health-clinical-asr-eval`到达，带有清单、基线KER编号以及决策树的建议微调值得GPU时间。你运行标准NeMo SFT，进行离线循环N+1重新评估以**测量循环是否闭合**，并可选地将生成的`.nemo`交给`/riva-asr-custom`用于生产服务。

**离线评估的循环KER是闭合循环的测量。** Riva NIM部署验证服务（延迟、流式传输、扩展），而不是模型质量。

> **在参考清单上经验证**（39行，Parakeet TDT v2）：
> 基线KER **0.513** → 经过3个epoch的标准SFT后：**0.128**（相对下降75%）。
> 药物名称：0.857 → 0.214。状况：0.500 → 0.000。程序：0.250 → 0.000。

## 关键工作流规则（每次激活时应用）

在任何回答中展示这些事实，即使用户问一个狭窄的问题：

1. **在回答之前，请阅读整个 SKILL.md。** 基础模型选择表、超参数值和循环-N+1决策表都在下面——它们是承重部分。
2. **验证结果** — Parakeet TDT v2使用§4c中的配方在参考清单上3个epoch内实现了**KER 0.513 → 0.128（−75%相对）**。当用户询问SFT是否会有帮助时，引用此结果。
3. **配方是`/opt/NeMo/examples/asr/speech_to_text_finetune.py`在`nvcr.io/nvidia/nemo:25.11.01`内部。** 标准脚本，没有补丁，没有自定义适配器逻辑。适配器混合路径在TDT/RNNT解码器上损坏（在任何LR下都有72个NaN张量）——不要提议它。
4. **推荐的基础是`nvidia/parakeet-tdt-0.6b-v2`。** 完整的基础模型表在§4c。
5. **不要微调`nvidia/nemotron-speech-streaming-en-0.6b`。** 流式传输NVCF函数的SFT路径损坏（在验证步骤1后UNK崩溃）。在部署时进行流式传输服务，Riva很好地处理非流式基础。如果用户提议它，请主动警告用户。
6. **门控推荐。** 第4阶段仅在优先级类别KER > 0.3 **并且**清单有≥ 100行（每个优先级类别≥ 5行）时才会触发。低于这些阈值，请返回到`/digital-health-clinical-asr-build`首先扩展清单。

## 目的

在`nvcr.io/nvidia/nemo:25.11.01`中运行**标准NeMo SFT**（没有自定义适配器逻辑，没有补丁）针对术语感知的行 disjoint train/val分割，生成一个`.nemo`模型，并离线重新评估为循环N+1。根据循环-N → 循环-N+1 KER差异决定是否保留模型、扩展清单或接受微调没有帮助。可选地将`.nemo`交给`/riva-asr-custom`用于NIM部署。

## 何时使用此技能

在以下用户短语激活：

- "基于我的临床词汇微调ASR"
- "改进ASR药物名称"
- "我们有一个KER为0.4，可以微调吗？"
- "在我的Parakeet TDT基础上运行SFT"
- "训练临床ASR适配器"
- "比较循环1与循环2 KER"
- "将我的微调模型作为NIM部署" *(此技能准备`.nemo`并路由到`/riva-asr-custom`进行部署)*

不激活的情况：

- 用户尚未评分基线 → `/digital-health-clinical-asr-eval`
- 用户没有清单 → `/digital-health-clinical-asr-build`
- 用户想要通用词提升/LM融合（不是SFT）→ `/finetune-asr`
- 用户有一个`.nemo`并且只想部署 → `/riva-asr-custom`

## 前提条件

- **一个循环-N清单 + 循环-N评估结果**来自`/digital-health-clinical-asr-eval`。优先级类别KER必须> 0.3（第4阶段门控）。清单应有≥ 100行总数，并且每个优先级`entity_category` ≥ 5行，以获得可信的微调后信号。
- **一个CUDA主机** — 24 GB VRAM对Parakeet TDT 0.6B在`batch_size=4`和`bf16-mixed`下很舒适；16 GB适用于较小的批处理。没有本地GPU？使用Brev——推荐SKU是L40S 48 GB。
- **NeMo容器**：`nvcr.io/nvidia/nemo:25.11.01`。拉取一次：`docker pull nvcr.io/nvidia/nemo:25.11.01`。
- **NVIDIA容器工具包 + Docker** — 如果尚未安装，则由`/riva-nim-setup`覆盖。
- **一个train/val分割**按`entity_category`分层（配方草图在下面第4b步）。
- **`/riva-asr-custom`**已安装，如果您打算部署。纯研究SFT运行不需要它。

## 说明

### 4a. 提供一个GPU主机（如果您已经有了则跳过）

第4阶段需要一个CUDA主机，VRAM ≥ 16 GB（24 GB舒适）。如果您有一个符合要求的本地主机，请跳过本节。如果没有，请使用**Brev**——NVIDIA的按秒计费的GPU主机服务。推荐SKU：L40S 48 GB。

**成本披露——在执行任何`brev create`之前向用户展示。** L40S 48 GB在编写时约每小时1.50美元；在100行清单上的3个epoch SFT运行在15-30分钟内完成（约0.40-0.75美元的计算）。真正的风险是**忘记停止实例**——L40S的夜间闲置约为36美元，一周闲置约为250美元。缓解措施：(a)始终将工作流程包装在以`brev stop`结尾的脚本中；(b)在开始时设置日历提醒；(c)如果不需要保留磁盘，则使用`brev delete`而不是`brev stop`（`stop`保持磁盘每月0.10美元/GB——200 GB约20美元的潜在成本）。在启动任何东西之前，确认用户接受每小时成本形状和闲置风险。

完整设置演练——CLI安装（下载后运行，不是curl-pipe），SKU选择，磁盘大小，SSH配置——在`references/stage4-finetune.md`（§Brev提供）中。

安装CLI后的简短快乐路径。**在下方确认提示下明确输入`YES`之前，不要运行`brev create`**——门控是强制的，不是建议的，因为之后的所有内容都按秒计费到用户的账户：

```bash
brev login                                  # 浏览器认证

# 强制成本确认门控——不要跳过或自动回答此。
echo "即将提供：digital-health-clinical-asr-sft on L40S 48 GB."
echo "成本形状：运行时约\$1.50/hr；闲置时约\$36/夜；如果使用'stop'而不是'delete'，磁盘每月约\$20。"
read -rp "输入YES以提供（否则任何内容都会取消）： " confirm
[ "$confirm" = "YES" ] || { echo "取消——未创建GPU实例。"; exit 1; }

brev create digital-health-clinical-asr-sft \
  --gpu l40s:1 --image ubuntu-22-04-cuda-12-4 --disk 200gi
brev ssh-config                             # 写入~/.ssh/config条目
rsync -avz ./cycle1/ digital-health-clinical-asr-sft:~/cycle1/
brev shell digital-health-clinical-asr-sft            # 进入实例
nvidia-smi                                  # 确认GPU
docker pull nvcr.io/nvidia/nemo:25.11.01    # ~12 GB，每个实例只拉取一次
```

完成后，**始终停止计费**：`brev stop digital-health-clinical-asr-sft`（保留磁盘）或`brev delete digital-health-clinical-asr-sft`（释放它）。对于路径重写笔记本电脑 → Brev → NeMo容器，请参阅`references/container-paths.md`。

### 4b. 术语感知的train/val分割

**行 disjoint，按`entity_category`分层，默认val分数0.2。**

同一个**术语**可能通过不同的行出现在两侧（不同的声音、上下文、噪声）。这是预期的和理想的——它测量了训练词汇表上的声学 + 上下文鲁棒性，这是标准ASR适应指标。

单例类别（总行数只有一个）被强制分配到训练，并附带警告。如果任何优先级类别少于5行，**转到`/digital-health-clinical-asr-build`**——保留的验证将过于嘈杂，无法归因于变化。

草图：

```python
# 在将manifest.jsonl加载到行的列表`rows`后：
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
        print(f"警告：单例类别 {cat}，强制分配到训练")
        continue
    n_val = max(1, int(0.2 * len(cat_rows)))
    val.extend(cat_rows[:n_val])
    train.extend(cat_rows[n_val:])
```

在清单旁边写入`train.jsonl`和`validation.jsonl`。**这些是`speech_to_text_finetune.py`的输入。**

### 4c. 选择基础模型

| 基础 | SFT可行性 | 备注 |
|---|---|---|
| **`nvidia/parakeet-tdt-0.6b-v2`** | ✅ **经验证** (KER 0.513 → 0.128在3个epoch内，相对下降75%) | NVIDIA当前的英语ASR默认值。标准NeMo SFT配方可以端到端工作。**推荐。** |
| `nvidia/nemotron-speech-streaming-en-0.6b` | ❌ **不要用于SFT** | NVCF函数仅限流式传输；SFT路径不可靠（在第一个训练步骤后验证UNK崩溃）。对于流式传输服务，Riva很好地处理非流式基础。 |

其他Parakeet/Conformer基础（1.1B、CTC、RNNT、`stt_en_conformer_ctc_large`）+ 解码器 → NIM容器映射：`references/stage4-finetune.md`。如果用户要求微调Nemotron Speech Streaming，**警告关于崩溃并推荐Parakeet TDT v2**。

### 4d. 标准NeMo SFT

在NeMo容器中，直接调用`/opt/NeMo/examples/asr/speech_to_text_finetune.py`。**没有自定义适配器逻辑。没有补丁。** 标准NeMo SFT脚本是经过验证的工作配方。

超参数（在Parakeet TDT v2、39行清单上验证）：

```
init_from_pretrained_model: nvidia/parakeet-tdt-0.6b-v2
precision:                  bf16-mixed       # TDT数值稳定性所需
lr:                         3e-4             # CosineAnnealing调度
warmup_steps:               5                # 小清单；在生产规模下增加到500
epochs:                     3                # 烟雾测试；生产10-30个epoch
batch_size:                 4                # 适合16 GB VRAM；在L40S 48 GB上增加到16
gradient_clip_val:          1.0              # 防御性
```

**容器调用**：`docker run --gpus all --rm -it -v "$PWD:/workspace" nvcr.io/nvidia/nemo:25.11.01 python /opt/NeMo/examples/asr/speech_to_text_finetune.py`，其中`model.train_ds.manifest_filepath=/workspace/train.jsonl`，`model.validation_ds.manifest_filepath=/workspace/validation.jsonl`，`init_from_pretrained_model=nvidia/parakeet-tdt-0.6b-v2`，以及上面表格中的超参数覆盖。完整docker-run行带配置路径/配置名称标志：`references/stage4-finetune.md` §容器调用。

**容器内的清单路径。** 主机路径（例如`$HOME/…`）在`/workspace`中无法解析。重写片段：`references/container-paths.md`。

训练运行写入`adapted_model.nemo`和`training_run_info.json`摘要。两者都进入用户选择的每个循环子目录（例如`cycle<N>/models/<run>`；布局无关紧要，只要跨循环保持一致即可）。

### 4e. 离线循环N+1评估——闭合循环

使用NeMo的离线`transcribe()`重新转录循环的音频，使用微调的`.nemo`。**不需要Riva**——这是测量，不是服务。NeMo的离线路径运行与Riva NIM最终服务的相同编码器 + 解码器图。

草图：

```python
import nemo.collections.asr as nemo_asr
model = nemo_asr.models.ASRModel.restore_from("adapted_model.nemo")
hyps = model.transcribe(["audio/row1.wav", "audio/row2.wav", ...])
```

对相同的四个指标（WER/CER/KER/SER）以及评估技能生成的相同五个部分排行榜进行评分。写入`leaderboard_cycle<N+1>.md`。与`leaderboard_cycle<N>.md`进行比较。

**决策表**——循环N+1与循环N：

| 结果 | 操作 |
|---|---|
| 目标类别上的KER有显著下降（例如，药物KER −20%或更多，相对） | ✅ 保留`.nemo`。更新排行榜。如果您想部署，请前进到步骤4f。 |
| KER略有移动，您想要更多 | 回到`/digital-health-clinical-asr-build`，扩展清单。小清单很少从超参数调整中受益——信号密度优于LR扫描。 |
| KER变差 | 在小清单上过拟合。转到`/digital-health-clinical-asr-build`并在重新训练前扩展。不要在相同数据上调整得更困难。 |
| 没有可测量的变化 | 某些类别可能已经在基础模型词汇表中。在得出训练“没有帮助”的结论之前，检查每个类别的数字。 |

### 4f. （可选）作为Riva NIM部署

将`.nemo`交给`/riva-asr-custom`。**明确传递源架构**——`/riva-asr-custom`无法仅从`.nemo`可靠地检测CTC vs RNNT vs TDT，并且错误的NIM容器会产生损坏的RMIR而没有明确的错误：

| 源解码器 | `riva-build`标志 | NIM容器系列 |
|---|---|---|
| Conformer-CTC | `decoder=greedy_ctc` | `parakeet-*-ctc-*` |
| Conformer-RNNT | `decoder=nemo` | `parakeet-rnnt-*` |
| **Conformer-TDT（默认）** | `decoder=nemo` | `parakeet-tdt-*` |
| 缓存感知RNNT（Nemotron流式传输） | `decoder=nemo` | `nemotron-streaming-*` ⚠ SFT在对此基础无效，见限制 |

部署后：重新运行`/digital-health-clinical-asr-eval`针对新端点（`ASR_ENDPOINT=localhost:50051`）以验证生产服务数字与离线数字匹配。任何差异都在Riva预处理或`riva-build`标志中，而不是模型。路由到`/riva-asr-custom`。

## 示例

**场景A——门控满足。** 用户：*"药物KER 0.42，130行。SFT?"* → 是（门控清除）。`parakeet-tdt-0.6b-v2`（验证0.513 → 0.128）。没有本地GPU？步骤4a（Brev）→ 4b（分割）→ 4d（标准SFT）→ 4e（离线重新评估）。如果循环2药物KER相对下降≥ 20%，则保留`.nemo`；否则回到`/digital-health-clinical-asr-build`。

**场景B——Nemotron流式传输。** 用户：*"SFT `nvidia/nemotron-speech-streaming-en-0.6b`?"* → 否（UNK崩溃）。替换`parakeet-tdt-0.6b-v2`。Riva将非流式基础很好地分割为流式传输服务——基础不需要是流式传输原生的。

**场景C——循环2 KER未改变。** 用户：*"KER几乎没动。"* → 回到`/digital-health-clinical-asr-build`。信号密度优于LR扫描。如果`magpie_g2p`行不好，但`merriam-webster`行好，差距是发音覆盖——`/digital-health-clinical-asr-build`步骤2d。

## 生成的工件

- `train.jsonl`, `validation.jsonl` — 术语感知分割（步骤4b）
- `adapted_model.nemo` — 微调模型（步骤4d）
- `training_run_info.json` — 超参数、数据集统计信息、训练结束指标
- `offline_hyps.jsonl` — 循环-N+1转录假设（步骤4e）
- `leaderboard_cycle<N+1>.md` — 循环-N+1五部分排行榜
- *(可选，在步骤4f之后)* 一个部署的NIM端点（委托给`/riva-asr-custom`）

## 故障排除

- **第4阶段训练在第一步后崩溃到所有UNK** → 你在缓存感知流式传输RNNT基础上（`nemotron-speech-streaming-en-0.6b`）。路由到`nvidia/parakeet-tdt-0.6b-v2`（推荐的默认值）或`nvidia/stt_en_conformer_ctc_large`（遗留回退）。流式传输RNNT SFT路径损坏；不要尝试使用不同的超参数重试。
- **清单路径在NeMo容器内无法解析** → 主机路径（例如`$HOME/…`）需要重写为`/workspace/…`。重写片段见`references/container-paths.md`。
- **循环N+1 KER与循环N未改变** → 在`parakeet-tdt-0.6b-v2`上使用上述配方，这几乎总是意味着**清单信号密度太低**。首先扩展清单；不要扫描LR。（如果你使用的是旧的适配器式配方而不是标准SFT，适配器权重可能还没有从零初始化——切换到标准SFT。）
- **循环N+1 KER变差** → 在小清单上过拟合。转到`/digital-health-clinical-asr-build`并扩展。
- **Riva服务数字与离线数字差异** → 差距在Riva预处理或`riva-build`标志中，而不是模型。路由到`/riva-asr-custom`。
- **`bf16-mixed`精度错误** → 一些GPU（旧的Turing，所有Volta）不支持BF16。降至`fp32`并减少`batch_size`。只有在`fp32`太慢的情况下才使用`fp16-mixed`——带有TDT解码器的fp16会产生NaN损失，因此请尽早检查损失曲线。
- **在24 GB GPU上训练时OOM** → 将`batch_size`降至2，将`accumulate_grad_batches`提高到2以保持有效批处理大小恒定。

## 限制

- **在TDT/RNNT解码器上的适配器式SFT损坏。** 经验证：一个较早的LinearAdapter-mixin配方在TDT和RNNT解码器上的任何LR都产生72个NaN张量。通过切换到NeMo的**标准全模型SFT**（`speech_to_text_finetune.py`）解决了这个问题——这是此技能推荐的内容。不要尝试在TDT/RNNT基础上进行适配器SFT。
- **不要SFT `nemotron-speech-streaming-en-0.6b`。** 仅限流式传输的NVCF函数的SFT路径不可靠（UNK崩溃）。对于部署时的流式传输服务，Riva很好地处理非流式基础。
- **小清单快速过拟合。** 总行数少于~100行或每个优先级类别少于~5行，循环-N+1数字太嘈杂。扩展后再信任小的KER下降。
- **默认情况下仅限英语。** 基础模型表是en-US特定的。其他地区需要不同的基础 + 重新验证的SFT配方。
- **没有现成的驱动程序。** 用户编写自己的训练驱动器布局——输出路径、运行命名、排行榜重新渲染。方法和配方可以转移；确切的循环1数字取决于用户的清单。

## 下一步

- **将`.nemo`作为NIM部署**：`/riva-asr-custom`（明确传递源架构）。
- **为循环N+2扩展清单**：`/digital-health-clinical-asr-build`。
- **重新评分循环**：`/digital-health-clinical-asr-eval`（针对新端点或新的`.nemo`直接）。
- **横向**用于词提升/LM融合/非临床SFT配方：`/finetune-asr`。

## 参考

- [`references/stage4-finetune.md`](references/stage4-finetune.md) — 基础模型选择表、超参数推理、解码器 → NIM容器映射、比较循环-N+1与循环-N的决策树
- [`references/container-paths.md`](references/container-paths.md) — 主机 → `/workspace/`路径重写，用于跨主机清单便携性（笔记本电脑 ↔ Brev ↔ NeMo容器）
