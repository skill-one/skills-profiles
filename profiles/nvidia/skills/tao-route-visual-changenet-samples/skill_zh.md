# TAO VCN 示例路由技能

> **独立安装？** 如果此会话不是由 TAO 技能库插件初始化的，请先运行 `tao-setup` 技能（主机预检、凭证、跨技能发现）。

你是在 VCN AOI SDA 管道中差距分析和增强模块之间的调度者。每个增强模块只能对其知道的标签采取行动：

- **k-NN 矿掘** 仅能矿掘已存在于 **源池 CSV** 中的真实图像邻居。如果池中没有 `SHIFT` 行，则没有必要寻找 `SHIFT` 邻居。
- **AnomalyGen**（Cosmos SDG）仅能为其推理管道支持的类别生成合成异常：`PASS`、`EXCESS_SOLDER`、`MISSING`、`BRIDGE`。带有此集合外标签的弱样本无法路由到 AnomalyGen。

此技能在每个 SDA 迭代中运行 **一次，立即在差距分析之后**。它将差距分析 parquet 分割为每个模块一个过滤 parquet，以便每个模块对其自己的符合条件的子集进行操作，并写入人类可读的每标签路由决策摘要。

这项工作有意地简单：读取一个 parquet，执行两个 `.isin(...)` 过滤，写入两个 parquet，写入一个摘要。此技能的存在是为了使这些决策可审计——每个标签都必须在摘要中显示每个模块的 yes/no 裁决，以便下游审查者可以识别标签何时因没有模块接受它而被静默丢弃。

---

## 输入

1. **`gaps_parquet`** — 差距分析输出（通常为 `<exp_dir>/rca_results/<timestamp>/kpi_gaps.parquet` 来自 `tao-analyze-gaps-visual-changenet`）。必需列：`filepath`、`label`。其他列（`siamese_score`、`weakness`）将原样保留。
2. **`source_pool_csv`** — VCN 格式矿掘源池 CSV，带有 `label` 列。允许空字符串或不存在路径；此时矿掘子集将简单地为空。
3. 输出目录——写入两个路由 parquet、摘要和报告的位置。默认：在差距分析结果目录下带时间戳的文件夹：`<rca_result_dir>/routing_results/<timestamp>/`。
4. **`anomalygen_supported_labels`** *(可选)* — 覆盖默认 AnomalyGen-符合条件的标签集。默认：`{"PASS", "EXCESS_SOLDER", "MISSING", "BRIDGE"}`。**警告**：这必须与 `mdo-kratos-workflows/pipelines/sda/routing.py` 中的 `ANOMALYGEN_SUPPORTED_LABELS` 和 AnomalyGen 集成实际的生成器覆盖保持同步。向 AnomalyGen 添加新的缺陷类别也意味着在此处添加它。

---

## 方法

整个技能是针对大写标签列的两个 `.isin(...)` 掩码。

### 第 1 步 — 加载和大写

```python
df = pd.read_parquet(gaps_parquet)
labels_upper = df["label"].astype(str).str.upper()
```

匹配对**不区分大小写**。原始 `label` 列在输出 parquet 中保持不变——只有比较键被大写。

### 第 2 步 — 矿掘子集

```python
if source_pool_csv and os.path.isfile(source_pool_csv):
    pool_df = pd.read_csv(source_pool_csv)
    pool_labels = {str(l).upper() for l in pool_df["label"].unique()}
    mn_mask = labels_upper.isin(pool_labels)
    mn_df = df[mn_mask]
else:
    pool_missing = True
    pool_labels = set()
    mn_df = df.iloc[0:0]   # 空的，但具有相同的架构
mn_df.to_parquet(mining_gaps_parquet, index=False)
```

如果池 CSV 缺失或为空，矿掘子集是一个空的 DataFrame **具有与输入相同的列**，以便下游读者不会因架构不匹配而崩溃。在摘要中标记此情况。

### 第 3 步 — AnomalyGen 子集

```python
ANOMALYGEN_SUPPORTED = {"PASS", "EXCESS_SOLDER", "MISSING", "BRIDGE"}
ag_mask = labels_upper.isin(ANOMALYGEN_SUPPORTED)
ag_df = df[ag_mask]
ag_df.to_parquet(anomalygen_gaps_parquet, index=False)
```

标签在 AnomalyGen 支持集中时，其行将原样写入 `anomalygen_gaps.parquet`。架构与输入 parquet 完全匹配——下游 AnomalyGen（Cosmos SDG）不需要其他更改。

### 第 4 步 — 每标签路由分解

对于输入差距 parquet 中的每个不同标签（大写），记录：
- `count` — 具有此标签的行数
- `mining` — 如果标签在 `pool_labels` 中，则为 yes，否则为 no
- `anomalygen` — 如果标签在 `ANOMALYGEN_SUPPORTED` 中，则为 yes，否则为 no

标签可以路由到**两个**模块（例如，PASS 行路由到 AnomalyGen，如果源池也包含 PASS 行，它们也路由到矿掘）。标签也可以路由到**零个**——标记这些，因为它们被静默丢弃，可能表示配置不匹配。

将分解写入 `routing_summary.txt`。格式与参考组件完全一致：

```
弱样本路由摘要
总弱样本数： <N>
矿掘子集：      <N_mn> -> <mining_gaps_parquet>
AnomalyGen 子集： <N_ag> -> <anomalygen_gaps_parquet>

[如果池缺失:]
未找到源池 CSV '<path>'；矿掘子集为空。

按标签分解（计数，矿掘，anomalygen）：
  PASS: 50 (矿掘=yes, anomalygen=yes)
  MISSING: 32 (矿掘=no, anomalygen=yes)
  SHIFT: 14 (矿掘=yes, anomalygen=no)
  EXCESS_SOLDER: 9 (矿掘=yes, anomalygen=yes)
  ...
```

### 第 5 步 — 检查

写入两个子集后，验证：
- 子集大小的总和**不需要**等于 `len(df)`——允许重叠（一个标签可以路由到两个模块）。重要的是**每个输入行至少出现在一个子集中，或出现在“无”列表中并带有明确原因**。
- 如果 `len(mn_df) == 0` 且 `len(ag_df) == 0`，则出错了——在报告中突出显示。
- 如果整个标签组没有路由到任何模块，`Recommended Actions` 部分必须指出这一点，以便用户可以种子源池中的该标签或扩展 AnomalyGen 支持的集。

---

## 参考Python配方

这是从 `mdo-kratos-workflows/pipelines/sda/routing.py` 直接提取的确切计算。通过 Bash 作为单个 Python 脚本运行；它生成除报告外的所有工件。

```python
import os
import pandas as pd

ANOMALYGEN_SUPPORTED = {"PASS", "EXCESS_SOLDER", "MISSING", "BRIDGE"}

df = pd.read_parquet(gaps_parquet)
labels_upper = df["label"].astype(str).str.upper()

# 矿掘子集
pool_missing = False
if source_pool_csv and os.path.isfile(source_pool_csv):
    pool_df = pd.read_csv(source_pool_csv)
    pool_labels = {str(l).upper() for l in pool_df["label"].unique()}
    mn_mask = labels_upper.isin(pool_labels)
    mn_df = df[mn_mask]
else:
    pool_missing = True
    pool_labels = set()
    mn_df = df.iloc[0:0]
os.makedirs(os.path.dirname(mining_gaps_parquet) or ".", exist_ok=True)
mn_df.to_parquet(mining_gaps_parquet, index=False)

# AnomalyGen 子集
ag_mask = labels_upper.isin(ANOMALYGEN_SUPPORTED)
ag_df = df[ag_mask]
os.makedirs(os.path.dirname(anomalygen_gaps_parquet) or ".", exist_ok=True)
ag_df.to_parquet(anomalygen_gaps_parquet, index=False)

# 按标签分解
summary_lines = [
    "Weak-sample routing summary",
    f"Total weak samples: {len(df)}",
    f"Mining subset:      {len(mn_df)} -> {mining_gaps_parquet}",
    f"AnomalyGen subset:  {len(ag_df)} -> {anomalygen_gaps_parquet}",
    "",
]
if pool_missing:
    summary_lines.append(f"No source pool CSV at {source_pool_csv!r}; mining subset is empty.")
    summary_lines.append("")
summary_lines.append("Per-label breakdown (count, mining, anomalygen):")
label_counts = labels_upper.value_counts()
for label, count in label_counts.items():
    in_mn = (not pool_missing) and label in pool_labels
    in_ag = label in ANOMALYGEN_SUPPORTED
    summary_lines.append(
        f"  {label}: {count} "
        f"(mining={'yes' if in_mn else 'no'}, "
        f"anomalygen={'yes' if in_ag else 'no'})"
    )
summary_text = "\n".join(summary_lines) + "\n"

os.makedirs(logs_dir, exist_ok=True)
with open(os.path.join(logs_dir, "routing_summary.txt"), "w", encoding="utf-8") as f:
    f.write(summary_text)
print(summary_text.strip())
```

---

## 输出

将所有内容写入带时间戳的文件夹。任何运行时打包挂钩可以在 `Routing_Report.md` 写入后添加 `routing_config/` 和会话捕获工件。

```
<output_dir>/routing_results/YYYY-MM-DD_HHMMSS/
├── Routing_Report.md           # 完整路由报告
├── mining_gaps.parquet         # 路由到 k-NN 矿掘的子集
├── anomalygen_gaps.parquet     # 路由到 AnomalyGen (Cosmos SDG) 的子集
├── routing_summary.txt         # 每标签分解的纯文本
├── routing_config/             # 由挂钩自动复制
└── session log/artifacts       # 可选，运行时依赖的打包捕获
```

在运行开始时，通过在 Bash 中运行 `date +%Y-%m-%d_%H%M%S` 获取真实时间戳。如果用户指定了自定义输出路径，请直接使用它，但保持内部布局。

---

## 报告结构

保持报告简短（400–800 字）。路由是确定性决策；价值在于使决策可审计，而不是叙述。

```
# VCN 路由报告： <迭代 / 实验名称>

## 1. 裁决
- 输入中的总弱样本数： <N>
- 矿掘子集：     <N_mn> 行  →  `mining_gaps.parquet`
- AnomalyGen 子集： <N_ag> 行  →  `anomalygen_gaps.parquet`
- 源池存在？ <yes/no — 以及路径>
- 一句话标题："<X> 标签路由，<Y> 标签被丢弃（没有模块接受）"

## 2. 输入
| 输入 | 路径 | 备注 |
|------|------|------|
| gaps_parquet     | … | 行数=<N>, 列=<列列表> |
| source_pool_csv  | … | 行数=<M> 或 "未提供" / "缺失" |

## 3. 每标签路由决策
| 标签 | 差距中的计数 | 在源池中？ | 矿掘？ | AnomalyGen？ | 路由到 |
|------|----------------|----------------|--------|--------------|-------|

(每个 `gaps_parquet` 中的不同标签（大写）一行。`Routed To` 是以下之一：
`仅矿掘`，`仅 AnomalyGen`，`矿掘+AnomalyGen`，`既不（丢弃）`。
每当没有模块接受标签时，使用 `既不（丢弃）`。按计数降序排序。)

## 4. 模块级摘要
### 4.1 k-NN 矿掘
- 池标签（来自 source_pool_csv）： <列表，或 "池缺失">
- 从输入接受的标签： <列表>
- 路由的行总数： <N_mn>
- 按标签行计数： <分解>

### 4.2 AnomalyGen (Cosmos SDG)
- 配置的符合条件的标签： PASS, EXCESS_SOLDER, MISSING, BRIDGE
- 从输入接受的标签： <列表>
- 路由的行总数： <N_ag>
- 按标签行计数： <分解>

## 5. 被丢弃的标签（路由到 NEITHER 模块）
| 标签 | 计数 | 丢弃原因 | 建议的修复 |
|------|------|----------|------------|

(空表可以接受，表示没有标签被丢弃。如果非空，则每行都需要一个 "原因"——通常为：
"不在源池 AND 不在 AnomalyGen 支持集中"，"源池完全缺失 AND 标签不在 AnomalyGen 集中"，"标签名称不匹配任何模块的预期规范化"。)

## 6. 建议的操作
1. **如果任何标签被丢弃**：用该标签种子源池，或扩展 `ANOMALYGEN_SUPPORTED_LABELS`（以及 AnomalyGen 生成器覆盖）。
2. **如果源池缺失**：提供 `source_pool_csv` 以启用矿掘分支。没有它，增强管道的一半是黑暗的。
3. **如果 AnomalyGen 子集为空**：差距分析仅突出了 AnomalyGen 无法生成的标签；依赖矿掘进行此迭代，或扩展 AnomalyGen 集成。
4. **如果两个子集都为空**：停止 SDA 迭代。下游无法运行任何东西。
```

---

## 执行顺序

1. 运行 `date +%Y-%m-%d_%H%M%S` 获取时间戳；创建 `<output_dir>/routing_results/<timestamp>/`。
2. 运行 Python 配方（步骤 1–4）以生成 `mining_gaps.parquet`、`anomalygen_gaps.parquet` 和 `routing_summary.txt`。将摘要统计信息打印到 stdout，以便脚本检查挂钩可以验证它已运行。
3. 通过读取两个 parquet 并计算每个标签的路由到决策来构建每标签决策表。
4. 最后写入 `Routing_Report.md`——写入它将触发打包挂钩，该挂钩将会话日志和技能配置与它一起复制。
