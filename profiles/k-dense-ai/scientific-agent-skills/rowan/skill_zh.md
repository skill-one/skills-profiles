# 欧拉：云原生分子建模和药物设计工作流

## 概述

欧拉是一个用于分子模拟、药物化学和基于结构的药物设计的云原生工作流平台。其 Python API 提供了一个统一的接口，用于小分子建模、性质预测、对接、分子动力学和 AI 结构工作流。

当您希望以编程方式运行药物化学或分子设计工作流，而无需维护本地 HPC 基础设施、GPU 提供或一组独立的建模工具时，请使用欧拉。欧拉处理所有基础设施、结果管理和计算扩展。

## 何时使用欧拉

**欧拉适合以下情况：**

- 量子化学、半经验方法或神经网络势
- 批量性质预测（pKa、描述符、通透性、溶解度）
- 构象和互变异构体集合生成
- 对接工作流（单配体、类似物系列、构象优化）
- 蛋白质-配体共折叠和 MSA 生成
- 多步化学管道（例如，互变异构体搜索 → 对接 → 构象分析）
- 需要一致、可扩展基础设施的批量药物化学活动

**欧拉不适合以下情况：**
- 简单的分子 I/O（直接使用 RDKit）
- 后 HF *ab initio* 量子化学或相对论计算

## 快速入门

```bash
uv pip install rowan-python
```

```python
import rowan
rowan.api_key = "your_api_key_here"  # 或设置 ROWAN_API_KEY 环境变量

# 描述符需要一个 3D 分子，而不是一个裸的 SMILES 字符串。
mol = rowan.Molecule.from_smiles("CC(=O)Oc1ccccc1C(=O)O")
wf = rowan.submit_descriptors_workflow(mol, name="aspirin")
result = wf.result()

print(result.descriptors["MW"])       # 180.042 — 精确质量
print(result.descriptors["SLogP"])    # 1.31
print(result.descriptors["TopoPSA"])  # 63.6 — 拓扑极表面积
```

如果输出没有错误，则设置正确。这些值和示例
已通过 `rowan-python` 3.1.13 验证。

## 安装

```bash
uv pip install rowan-python
# 或: uv pip install rowan-python
```

## 用户和 webhook 管理

### 认证

通过环境变量设置 API 密钥（推荐）：

```bash
export ROWAN_API_KEY="your_api_key_here"
```

或者直接在 Python 中设置：

```python
import rowan
rowan.api_key = "your_api_key_here"
```

验证认证：

```python
import rowan
user = rowan.whoami()  # 如果认证成功，则返回用户信息
print(f"用户: {user.email}")
print(f"可用积分: {user.credits_available_string()}")
```

## 分子输入格式

欧拉接受以下格式的分子：

- **SMILES**（首选）: `"CCO"`, `"c1ccccc1O"`
- **SMARTS 模式**（用于某些工作流）: SMARTS 的子集，用于子结构匹配
- **InChI**（如果您的 API 版本支持）: `"InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3"`

API 验证分子输入，对于无法解析的 SMILES 或工作流不兼容的输入类型会引发 `ValueError`。始终使用规范化的 SMILES 以确保可重复性。

### SMILES 字符串与分子对象

`rowan-python` 3.1.13 中，不同工作流的接受输入类型不同。只有以下常见工作流接受裸字符串：pKa、构象搜索、膜通透性、ADMET、LogP、macropKa、溶解度和构象分析 MD。大多数其他工作流（包括描述符、互变异构体搜索、对接、类似物对接、BDE、NMR 和 Fukui）需要 `rowan.Molecule.from_smiles(smiles)` 或 RDKit 的 `Mol`/`RWMol`。类型错误会在提交前引发 `ValueError`。

**提示：** 提交前使用 RDKit 验证 SMILES：

```python
from rdkit import Chem
smiles = "CCO"
mol = Chem.MolFromSmiles(smiles)
if mol is None:
    raise ValueError(f"无效的 SMILES: {smiles}")
```

## 核心使用模式

大多数欧拉任务遵循相同的三个步骤模式：

1. **提交**一个工作流
2. **等待**完成（可选的流式传输）
3. **检索**带便利属性的类型化结果

```python
import rowan

# 1. 提交 — 使用特定的工作流函数（而不是通用的 submit_workflow）
workflow = rowan.submit_descriptors_workflow(
    rowan.Molecule.from_smiles("CC(=O)Oc1ccccc1C(=O)O"),
    name="aspirin descriptors",
)

# 2. & 3. 等待并检索
result = workflow.result()  # 阻塞直到完成（默认：wait=True, poll_interval=5）
print(result.data)              # 原始字典
print(result.descriptors["MW"]) # 180.042 精确质量；没有 result.molecular_weight 属性
```

对于长时间运行的工作流，使用流式传输：

```python
for partial in workflow.stream_result(poll_interval=5):
    print(f"完成: {partial.complete}")  # 布尔值，不是百分比
    print(partial.data)
```

### result() vs. stream_result()

| 模式 | 使用场景 | 持续时间 |
|------|----------|----------|
| `result()` | 您可以等待完整结果 | 典型 <5 分钟 |
| `stream_result()` | 您需要进度反馈或需要早期部分结果 | >5 分钟，或交互式使用 |

**指南：** 使用 `result()` 用于描述符、pKa。使用 `stream_result()` 用于构象搜索、对接、共折叠。

## 处理结果

欧拉的 API 包括 **类型化的工作流结果对象** 和便利属性。

### 使用类型化属性和 .data

结果有两种访问模式：

1. **便利属性**（推荐首先使用）: `result.descriptors`, `result.best_pose`, `result.scores`。结果类不同：构象搜索使用 `get_energies()` 和 `get_conformers()` 方法。
2. **原始回退**: `result.data` — API 的原始字典

示例：

```python
result = rowan.submit_descriptors_workflow(
    rowan.Molecule.from_smiles("CCO"),
    name="ethanol",
).result()

# 便利属性（返回所有描述符）:
print(result.descriptors["MW"])       # 精确/单同位素质量
print(result.descriptors["SLogP"])
print(result.descriptors["TopoPSA"])  # 通常使用的拓扑极表面积

# 原始数据回退:
print(result.data["descriptors"])
```

**注意：** `DescriptorsResult` 没有 `molecular_weight` 属性。
`MW` 是精确/单同位素质量，不是平均分子质量。`TPSA` 是 3D 带电表面描述符；使用 `TopoPSA` 用于药物相似性规则中通常使用的拓扑极表面积。

### 缓存失效

某些结果属性是惰性加载的（例如，构象几何形状、蛋白质结构）。要刷新：

```python
result.clear_cache()
new_structures = result.get_conformers()  # ConformerSearchResult 重新获取
```

## 项目、文件夹和组织

对于非平凡的活动，使用项目和文件夹来保持工作组织。

### 项目

```python
import rowan

# 创建一个项目
project = rowan.create_project(name="CDK2 lead optimization")
rowan.set_project("CDK2 lead optimization")

# 所有后续的工作流都进入此项目
wf = rowan.submit_descriptors_workflow(
    rowan.Molecule.from_smiles("CCO"), name="test compound"
)

# retrieve_project 接收 UUID；list_workflows 使用 parent_uuid 进行作用域限制。
project = rowan.retrieve_project(project.uuid)
workflows = rowan.list_workflows(parent_uuid=project.uuid, size=50)
```

### 文件夹

```python
# 创建分层文件夹结构
folder = rowan.create_folder(name="docking/batch_1/screening")

wf = rowan.submit_docking_workflow(
    # ... 对接参数 ...
    folder=folder,
    name="compound_001",
)

# 列出文件夹中的工作流
results = rowan.list_workflows(parent_uuid=folder.uuid)
```

## 工作流决策树

### pKa vs. MacropKa

**使用微观 pKa 当：**

- 您需要一个单个可电离基团的 pKa
- 您对酸碱转换和质子化热力学感兴趣
- 分子有一个或两个可电离位点
- 速度至关重要（更快，积分更少）

**使用 macropKa 当：**

- 您需要在生理相关范围内（例如，0–14）获得 pH 依赖行为
- 您希望获得跨 pH 的电荷和质子化状态种群
- 分子有多个可电离基团且质子化相互关联
- 您需要不同 pH 下水溶性等下游性质

**示例决策：**

```text
苯酚（pKa ~10）: 使用微观 pKa
胺（pKa ~9–10）: 使用微观 pKa
多电离药物（N、O、酸性基团）: 使用 macropKa
跨 GI pH 的 ADME 评估: 使用 macropKa
```

### 构象搜索 vs. 互变异构体搜索

**使用构象搜索当：**

- 已知单个互变异构体形式
- 您需要一个多样化的 3D 集合用于对接、MD 或 SAR 分析
- 旋转键主导化学空间

**使用互变异构体搜索当：**

- 互变异构平衡不确定（例如，杂环、酮-烯醇系统）
- 您需要建模所有相关的质子化异构体
- 下游计算（对接、pKa）取决于互变异构体形式

**组合工作流：**

```python
# 第 1 步：找到最佳互变异构体
taut_wf = rowan.submit_tautomer_search_workflow(
    initial_molecule=rowan.Molecule.from_smiles("O=c1[nH]ccnc1"),
    name="咪唑互变异构体",
)
best_taut = taut_wf.result().best_tautomer

# 第 2 步：从最佳互变异构体生成构象
conf_wf = rowan.submit_conformer_search_workflow(
    initial_molecule=best_taut,
    name="咪唑构象",
)
```

### 对接 vs. 类似物对接 vs. 共折叠

| 工作流 | 使用场景 | 输入 | 输出 |
|--------|----------|------|------|
| 对接 | 单配体，已知口袋 | 蛋白质 + SMILES + 口袋坐标 | 构象、分数、dG |
| 类似物对接 | 5–100+ 相关化合物 | 蛋白质 + SMILES 列表 + 参考配体 | 所有构象、参考对齐 |
| 蛋白质-配体共折叠 | 序列 + 配体，无晶体结构 | 蛋白质序列 + SMILES | ML 预测的结合复合物 |

## 蛋白质工具

### 上传蛋白质

```python
# 从本地 PDB 文件
protein = rowan.upload_protein(
    name="egfr_kinase_domain",
    file_path="egfr_kinase.pdb",
)

# 从 PDB 数据库
protein_from_pdb = rowan.create_protein_from_pdb_id(
    name="CDK2 (1M17)",
    code="1M17",
)

# 检索先前上传的蛋白质
protein = rowan.retrieve_protein("protein-uuid")

# 列出所有蛋白质
my_proteins = rowan.list_proteins()
```

### 蛋白质准备指南

- **文件格式**: PDB、mmCIF（欧拉自动检测）
- **水分子**: 欧拉通常保留相关水；如果需要，在上传前删除大量水
- **杂原子**: 辅因子、离子和结合配体通常被保留；在上传前删除不需要的杂原子
- **多链蛋白质**: 完全支持
- **分辨率**: 可与 NMR 结构、同源模型和冷冻电镜结构一起使用；质量对下游预测很重要
- **验证**: 欧拉验证 PDB 语法；严重损坏的文件可能会被拒绝

## 工作流目录

九个常见工作流类别——描述符、微观 pKa、MacropKa、构象搜索、互变异构体搜索、对接、类似物对接、MSA 生成和蛋白质-配体共折叠——每个都有提交代码和结果形状，以及支持的所有工作流类型（核心建模、基于结构的药物设计、高级计算化学、反应化学、高级性质、结合自由能和序列和结构生物学）在
[references/workflow_catalog.md](references/workflow_catalog.md)。

## 批量提交、webhooks 和异步工作

批量提交/轮询/检索、非阻塞的“发射并检查”模式、webhook 设置、密钥创建和旋转、有效载荷和签名验证（使用 FastAPI 处理程序）以及 webhook 最佳实践在
[references/batch_and_webhooks.md](references/batch_and_webhooks.md)。

## 访问、定价和积分

免费层限制、每个工作流的积分消耗和典型成本估计在
[references/access_and_pricing.md](references/access_and_pricing.md)。

## 实例和故障排除

一个完整的先导优化活动——项目设置、互变异构体、跨类似物系列 pKa、结果收集和对接后续——在
[references/end_to_end_example.md](references/end_to_end_example.md)。

常见错误及其修复方法以及调试技巧在
[references/troubleshooting.md](references/troubleshooting.md)。

## 推荐使用模式

- **优先使用 Rowan 原生工作流** 而不是低级组装，如果它们存在
- **使用项目和文件夹** 对于任何非平凡活动（>5 个工作流）
- **使用 `result()` 阻塞直到完成**（默认：`wait=True, poll_interval=5`）
- **首先使用类型化结果属性**，对于未映射的字段回退到 `.data`
- **使用批量提交** 对于化合物库或类似物系列
- **链式工作流** 对于多步化学活动：
  - `pKa → macropKa → 通透性`（ADME 评估）
  - `互变异构体搜索 → 对接 → 构象分析 MD`（构象优化）
  - `MSA 生成 → 蛋白质-配体共折叠`（AI 结构预测）
- **使用 webhooks** 对于长时间运行的活动（>50 个工作流）或异步管道
- **使用流式传输** 对于交互式反馈在大型构象/对接搜索

## 总结

当您的工 作流需要云执行用于分子设计任务，特别是当您希望有一个统一的 API 和跨小分子建模、蛋白质、对接、ADME 预测和 ML 结构生成的一致结果处理时，请使用欧拉。

欧拉是一个分子设计工作流平台，而不仅仅是一个远程化学引擎。它处理基础设施扩展、结果持久化和多步管道编排，以便您专注于科学。
