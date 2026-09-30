---
name: tao-run-automl-deft-pipeline
description: 运行标准的NVIDIA AOI三阶段训练流程——第一阶段AutoML基线（HPO），第二阶段DEFT循环（RCA → SDG → 挖掘 → plain-train再训练），第三阶段在DEFT增强数据集上进行AutoML优化。当用户要求“运行AOI工作流”、“端到端微调我的PCB AOI模型”、“改进我的AOI ChangeNet模型”或“带AutoML的AOI工作流”时使用——除非用户明确要求仅运行DEFT循环（例如“仅运行DEFT循环”、“跳过AutoML，仅DEFT”），否则应将请求路由至此，而不是直接调用tao-run-deft-aoi。同时处理非AOI DEFT应用的相同三阶段模式——AutoML基线后从AutoML的获胜HP处启动DEFT循环热启动，然后在迭代增强数据集上进行DEFT后的AutoML优化。触发短语包括“运行AOI工作流”、“AOI端到端”、“AutoML + DEFT”、“AutoML然后DEFT”、“微调超参数然后DEFT”、“两端带AutoML的DEFT”、“DEFT热启动”、“改进我的AOI模型”。
---

# AutoML + DEFT 流水线

一个工作流桥接技能，通过委托给两个现有技能按顺序运行**三个阶段**——`tao-run-automl`用于超参数优化（HPO），以及一个DEFT应用技能（默认`tao-run-deft-aoi`用于AOI；其他`skills/applications/deft-*`技能用于非AOI情况）用于迭代数据改进循环。

这个技能**不**重新实现AutoML或DEFT。它只拥有连接组织：HPO规范输入、AutoML和DEFT之间的规范交接，以及DEFT后AutoML在增强数据集上的重新运行。

## 路由策略

- 用户询问“运行AOI工作流”或“改进我的AOI ChangeNet模型”——**默认选择此技能**，而不是直接选择`tao-run-deft-aoi`。裸DEFT循环是这个流水线的内部阶段。
- 用户希望将AutoML和DEFT链在同一模型/数据集上
- 用户说“两端都使用AutoML”、“先调优HPs再DEFT”、“DEFT热启动”、“AutoML在DEFT前后”
- 用户有一个AutoML调优的规范，并询问如何将其输入DEFT

## 此技能不适用的情况

- 用户明确要求仅DEFT循环（“仅运行DEFT循环”、“跳过AutoML”）→ 直接使用`tao-run-deft-aoi`
- 用户只想使用AutoML而没有后续DEFT → 直接使用`tao-run-automl`
- 用户正在进行零样本评估、RAG或非训练工作流

---

## 心智模型

```
阶段1（AutoML基线）        阶段2（DEFT循环，纯训练）        阶段3（AutoML精炼）
─────────────────────────        ────────────────────────────────        ───────────────────────────
specs/baseline_spec.yaml         (阶段1赢家预种子基线训练        ${RESULTS_DIR}/iter${N}/dataset/
train/base/training_set.csv       — DEFT跳过其基线训练)       train_combined_iter${N}.csv
        │                                       │                                       │
        ▼                                       ▼                                       ▼
[ AutoML HPO扫描 ]               [ DEFT: 基线推理 → RCA       [ AutoML HPO扫描 ]
   N个推荐                         → 迭代1..N（纯重新训练） ]        重新调优HPs针对DEFT增强的数据集
   根据val_loss / FAR选择最佳       RCA / 路由 / SDG / 矿工             赢家
        │                                       │                                       │
        ▼                                       ▼                                       ▼
最佳HPs规范 + 检查点 ─────►      DEFT增强的CSV ───────────►        最终最佳检查点
                                 + 迭代赢家检查点               (交付物；无进一步重新训练)
```

两个交接是：

- **阶段1 → 阶段2**：一个*规范文件*和*赢家检查点*——桥接深度合并阶段1的HPs到`specs/baseline_spec.yaml`，将检查点复制到`${RESULTS_DIR}/baseline/train/`，并预填充`deft_state.json`以便DEFT跳过其基线训练并从基线推理→评估→RCA→迭代1。DEFT保持纯训练（`automl_policy: off`保持不变）。
- **阶段2 → 阶段3**：一个*训练CSV*（`train_combined_iter${N_final}.csv`）和*迭代赢家的检查点*——检查点被连接到每个推荐的`train.pretrained_model_path`，因此阶段3从阶段2的赢家进行微调。阶段3的赢家检查点是交付物；阶段3后没有单独的重新训练。

参见`references/phase-handoffs.md`了解两个交接的确切步骤、代码和DEFT尊重此交接的详细信息。

## 为什么是三个阶段而不是两个

- **阶段1单独**在*原始*训练分布上找到好的HPs，但模型仍然有DEFT设计用来填补的分布差距。
- **阶段2单独**（仅DEFT）填补差距，但使用`specs/baseline_spec.yaml`手工编写的任何HPs——通常不是最优的。
- **阶段3单独**会在增强数据集上运行AutoML，但没有调优基线，DEFT循环的迭代成本更高（收敛速度慢，需要更多迭代才能达到KPI）。

运行所有三个阶段：AutoML在原始数据上廉价调优一次，DEFT进行重数据工作并使用合理的HPs，然后AutoML在更丰富的数据集上再次调优。阶段3是三个阶段中最重要的，对最终部署的FAR/召回率影响最大。

## 前期成本

流水线是顺序的。总运行时间≈阶段1（N_automl × 每个推荐训练）+ 阶段2（M次迭代 × 每次迭代成本）+ 阶段3（N_automl × 每个推荐训练）。

注意**阶段2没有单独的基线训练**——阶段1的赢家检查点被用作DEFT的基线，因此基线成本包含在阶段1的N_automl训练中而不是额外重新训练。在启动前向用户说明这一点。通常阶段2的迭代仍然占主导地位（每次迭代包括SDG + 重新训练），但阶段1和阶段3在单个GPU上各增加数小时。使用用户设置中的每个作业估计值，而不是猜测分钟数。参见`references/pitfalls-and-quality-checks.md`（**计算预算**）了解每个阶段的术语分解。

---

## 综合起飞前检查——一个门，所有三个阶段

**流水线只有一个用户门。** 在任何有副作用的操作（docker pull、docker login、委托给下游技能的任何作业启动调用、`${RESULTS_DIR}/`下的文件修改）之前，代理必须生成一个包含所有下游技能预起飞的单一综合起飞前检查摘要。一旦用户批准，运行将在所有三个阶段中自动进行——不再需要交互式暂停。

用户明确不想在不同阶段之间被打扰。DEFT循环自己的内置`## 起飞前摘要`门变成一个**无问题的显示步骤**（所有值都从这个综合门预先提供），`tao-run-automl`在阶段1和阶段3中的共享启动预起飞也是如此。

在打印摘要之前，代理必须完整打开并阅读每个下游技能的预起飞部分，运行这些部分规定的所有只读检查，并显示每个检查的结果。摘要有九个必填部分（工作区/主机/平台/网络；凭证状态；容器镜像；数据集表；阶段1配置；阶段2配置；阶段3配置；计算估计；确认行）。通过门后，每个下游交互式门都被通过收集的值抑制。允许的仅门后暂停是下游技能无法绕过的运行时硬停止安全门。

参见`references/consolidated-preflight.md`了解：要读取的完整预起飞部分列表、所需的DEFT `## 起飞前`运行、确切九部分摘要内容、值传递用于门抑制，以及技能库版本尚未支持门抑制时的程序。

---

## 阶段1 — AutoML基线

使用`tao-skill-bank:tao-run-automl`调用：

| 输入 | AOI默认值 | 备注 |
|---|---|---|
| `network_arch` | `visual-changenet` | 与DEFT循环期望的相同模型 |
| `train_dataset_uri` | `<workspace>/train/base/training_set.csv` | 与DEFT将从中开始的相同训练集 |
| `eval_dataset_uri` | `<workspace>/train/base/validation_set.csv` | 持有——绝不能是KPI测试集（`<workspace>/kpi/testing_set.csv`），因为该集保留给DEFT的最终报告 |
| `metric` | FAR @ 100%召回率（首选）或`val_loss` | 参见`references/pitfalls-and-quality-checks.md`中的**指标陷阱**——ChangeNet AOI是类别不平衡的，单独的val_loss可能导致模式崩溃 |
| `algorithm` | `bayesian` | LLM-brain或`autoresearch`如果计算紧张 |
| `automl_max_recommendations` | 5–10用于AOI | 推荐数量越多，HPs越好，但与计算呈线性关系 |
| `spec_overrides` | 固定epochs / batch_size；仅扫描优化器相关HPs | 否则AutoML会陷入长训练状态，超出阶段2的预算 |

扫描完成后，AutoML的`result["best"]["specs"]`是赢家超参数字典。

### 传递到阶段2

阶段1传递**两个工件**：赢家*规范*和赢家*检查点*。在DEFT的基线步骤中重新训练相同的HPs是浪费计算——相反，从阶段1的输出预种子DEFT的基线状态，以便DEFT从基线推理→评估→RCA→迭代1开始。这是一个四步桥接（写入合并规范→预种子`baseline/train/`→用基线已完成初始化`deft_state.json`→调用DEFT），然后是对赢家检查点的质量检查（每类预测计数；与零样本ChangeNet比较）。

参见`references/phase-handoffs.md`了解字面步骤1–4（包括`cp`命令和`deft_state.json`预种子代码）以及质量检查清单。

---

## 阶段2 — DEFT循环（纯训练，基线从阶段1预种子）

调用`tao-skill-bank:tao-run-deft-aoi`（阅读其`SKILL.md`以获取完整接口）。对于非AOI应用，调用匹配的DEFT技能；传递形状相同。

**DEFT循环的基线训练子步骤被跳过。** 阶段1已经生成了一个在赢家HPs上训练的检查点，阶段1的传递（见`references/phase-handoffs.md`）预填充了`${RESULTS_DIR}/baseline/train/`和`${RESULTS_DIR}/deft_state.json`，以便DEFT从基线推理→评估→RCA→迭代1开始。其余的DEFT循环保持不变。**不要修改其`automl_policy: off`不变量。**

DEFT循环拥有：其预起飞摘要显示步骤（**不是**一个全新的用户门——上述综合预起飞是唯一的门；DEFT摘要仍然记录预种子`baseline/train/`来源，并且不能重新提示）；基线推理→评估→RCA在预种子检查点上；完整的每次迭代RCA→路由→SDG→矿工→组装→训练周期；KPI门控和停止条件；以及`${RESULTS_DIR}/`布局（`deft_state.json`，`DEFT_Loop_Report.html`）。

循环退出后（达到KPI或`max_iterations`），从`deft_state.json`捕获两个值：`iterations.<best>.best_ckpt_path`（循环的最佳纯训练检查点）和最终迭代标签`N_final`（用于定位增强的训练CSV）。

如果DEFT循环在不可恢复的门上硬停止，**跳过阶段3**。没有经过验证的增强CSV可以输入AutoML。

---

## 阶段3 — DEFT增强数据集上的AutoML精炼

重新调用`tao-skill-bank:tao-run-automl`，将增强的训练CSV作为训练数据集，与之前相同的保留验证CSV，并将**阶段2的迭代赢家检查点作为热启动**：

| 输入 | AOI值 |
|---|---|
| `network_arch` | `visual-changenet` |
| `train_dataset_uri` | `${RESULTS_DIR}/iter${N_final}/dataset/train_combined_iter${N_final}.csv` |
| `eval_dataset_uri` | 与阶段1相同（`<workspace>/train/base/validation_set.csv`）——保持苹果对苹果的比较 |
| `metric` | 与阶段1相同 |
| `algorithm` | 与阶段1相同 |
| `automl_max_recommendations` | 5–10 |
| 初始规范 | 从`<workspace>/specs/baseline_spec_automl.yaml`（阶段1的赢家）开始——给扫描一个强质心以精炼 |
| **热启动检查点** | **`iterations.<best>.best_ckpt_path`来自`${RESULTS_DIR}/deft_state.json`** — 设置`spec_overrides["train"]["pretrained_model_path"]`到此路径。每个阶段3推荐然后**从阶段2的赢家进行微调**，而不是从零开始训练。 |

热启动是强制的：没有它，每个推荐从随机初始化开始，只有10-20个时期才能重新收敛，`val_loss`相对于iter1回归0.03-0.05，并且`_pick_best`安全网无声地回滚到迭代赢家。输出到`${RESULTS_DIR}/final_automl/`；这次扫描的赢家检查点是流水线的交付物。扫描后，在`deft_state.json`中将阶段3的检查点注册在`iterations.final_automl`下，并重新运行`prepare_inference_spec.py`，以便传递看到它（如果阶段3回归，则回退到循环的最佳）。

参见`references/phase-handoffs.md`了解：完整的“为什么热启动是强制的”理由和权衡、具体的`spec_overrides`选择代码、阶段3的输出精确地反馈到DEFT报告的两步接线，以及回归的安全说明。

---

## 陷阱和质量检查

这些适用于两个AutoML阶段。将它们融入代理行为——不要只是粘贴一次。完整细节在`references/pitfalls-and-quality-checks.md`中；简而言之：

- **指标陷阱——AOI是类别不平衡的。** ChangeNet AOI数据集是PASS占主导地位（90%+），所以val_loss赢家可能是一个模式崩溃的模型。直接使用FAR @ 100%-recall，或用`pred_counts`进行合理性检查来保护val_loss，或在选择前按FAR @ 100%-recall评估top-K。对于平衡/回归任务，val_loss是合适的。
- **运行间噪声。** AutoML对于相同的HP配置可以显示2–3倍的方差。如果赢家比第二名好得可疑，在将规范提交给阶段2之前用新种子重新运行。
- **清洁性（数据泄漏）。** 两个AutoML阶段都使用与KPI测试集（`<workspace>/kpi/testing_set.csv`）不同的验证集，该集保留给DEFT的最终报告。阶段3在增强CSV上训练，但保持相同的验证集，以便阶段1和阶段3的数字保持可比。
- **计算预算。** 阶段1 `N_automl × 每个推荐训练`；阶段2 `M_iter × (RCA + SDG + 矿工 + 重新训练)`（通常最大）；阶段3 `N_automl × 每个推荐训练`在更大的增强数据集上。在报价墙时钟之前向用户询问每个作业的时间。

---

## 快速入门（AOI工作示例）

从“运行AOI工作流”开始时，代理向用户展示一个三阶段计划（阶段1 AutoML基线→阶段2 DEFT循环→阶段3 AutoML精炼），说明总成本结构（前面没有额外的基线重新训练，结束时没有额外的重新训练），请求用户为墙时钟估计提供每个运行时间，并等待批准。确认后，它调用阶段1，写入合并规范，预种子`deft_state.json`，预供所有输入调用DEFT循环，然后调用阶段3——除非下游技能遇到不可恢复的硬停止，否则不会进一步暂停。它在结束时总结轨迹（基线AutoML最佳→DEFT迭代1→...→DEFT迭代N_final→阶段3最佳）。

参见`references/quick-start-example.md`了解字面的客户面对消息块和确切的确认后调用序列。

## 非AOI DEFT应用

相同的三个阶段模式适用于其他DEFT技能。交换：

- `network_arch`到相关模型
- 阶段2调用的DEFT技能
- “最佳HP规范文件”和“最佳HP检查点”路径约定到目标DEFT技能期望的内容
- 阶段3中的增强-CSV路径到目标DEFT技能生成的路径

传递形状——阶段1发出*规范+检查点*（检查点预种子DEFT基线），阶段2消费两者并发出增强数据集，阶段3发出最终检查点——是相同的。阶段1→阶段2的基线跳过机制是通用的：任何可以以可恢复基线状态公开的DEFT式循环都可以以相同方式种子。

---

## 参见

- `tao-skill-bank:tao-run-automl` — AutoML接口、算法、HP范围
- `tao-skill-bank:tao-run-deft-aoi` — 完整DEFT AOI循环（阶段2默认）
- `tao-skill-bank:tao-train-visual-changenet` — 底层ChangeNet训练/评估/推理技能（AutoML和DEFT都使用）
- 其他`skills/applications/deft-*`技能 — 非AOI阶段2目标
- `references/consolidated-preflight.md` — 单一门的预起飞完整内容
- `references/phase-handoffs.md` — 两个交接、基线预种子、阶段3热启动，字面
- `references/pitfalls-and-quality-checks.md` — 指标陷阱、运行间噪声、泄漏、计算预算
- `references/quick-start-example.md` — 客户面对的工作示例消息
