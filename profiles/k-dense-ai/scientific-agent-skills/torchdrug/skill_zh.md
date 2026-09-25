# TorchDrug

将 TorchDrug 作为模块化的 PyTorch 图学习堆栈使用：

1. 加载一个 `datasets.*` 数据集，
2. 选择一个 `models.*` 表示模型，
3. 用 `tasks.*` 目标将其封装，
4. 使用 `core.Engine` 进行训练和评估。

当前的官方文档和最新发布版本均为 **0.2.1**。对于较新的 Python 或 PyTorch 组合，应视为未经验证，而不是默默假设兼容性。

## 从版本保护开始

在生成或调试代码之前，检查环境：

```bash
python --version
python -c "import torch; print(torch.__version__)"
python -c "import torchdrug; print(torchdrug.__version__)"
```

TorchDrug 0.2.1 的支持矩阵如下：

- Python 3.7 至 3.10
- PyTorch 1.8 至 2.0
- Linux、Windows 或 macOS
- Apple Silicon：PyTorch 1.13 或更高版本，仅支持 CPU；不提供 MPS 支持

如果项目使用 Python 3.11+ 或 PyTorch 2.1+，请创建兼容的环境或明确测试源构建。不要将此类组合呈现为受支持的。

## 安装

优先使用专门的 Python 3.10 环境，并固定 TorchDrug 发布版本：

```bash
uv venv --python 3.10
source .venv/bin/activate
uv pip install "torch==2.0.0"
```

安装与精确的 PyTorch 和 CUDA 对应的 `torch-scatter` 和 `torch-cluster` 轮子，遵循
[官方安装页面](https://torchdrug.ai/docs/installation.html)。对于仅使用 CPU 的 PyTorch 2.0 环境，一个可重复的轮子组合为：

```bash
uv pip install "torch-scatter==2.1.1" "torch-cluster==1.6.1" \
  --find-links "https://data.pyg.org/whl/torch-2.0.0+cpu.html"
uv pip install "torchdrug==0.2.1"
```

不要在不同环境之间复制 CUDA 轮子 URL。匹配 PyTorch 版本、CUDA 构建、Python ABI 和平台。在 Apple Silicon 上，官方文档要求从源代码构建 `torch-scatter` 和 `torch-cluster`；固定经过审查的源代码修订版本，并预期 CPU 执行。

## 标准的属性预测工作流

使用文档中记录的 ClinTox → GIN → `PropertyPrediction` → `Engine` 模式：

```python
import torch
from torchdrug import core, datasets, models, tasks

dataset = datasets.ClinTox("~/molecule-datasets/")
lengths = [int(0.8 * len(dataset)), int(0.1 * len(dataset))]
lengths.append(len(dataset) - sum(lengths))
train_set, valid_set, test_set = torch.utils.data.random_split(dataset, lengths)

model = models.GIN(
    input_dim=dataset.node_feature_dim,
    hidden_dims=[256, 256, 256, 256],
    short_cut=True,
    batch_norm=True,
    concat_hidden=True,
)
task = tasks.PropertyPrediction(
    model,
    task=dataset.tasks,
    criterion="bce",
    metric=("auprc", "auroc"),
)

optimizer = torch.optim.Adam(task.parameters(), lr=1e-3)
solver = core.Engine(
    task,
    train_set,
    valid_set,
    test_set,
    optimizer,
    batch_size=1024,
)
solver.train(num_epoch=100)
solver.evaluate("valid")
```

仅在支持 CUDA 设备可用时添加 `gpus=[0]`。对于 CPU 执行，省略 `gpus`。

对于二分类，`task.predict(batch)` 返回 logits；当需要概率时，应用 `torch.sigmoid`。在 0.2.1 中，归一化回归预测返回原始目标尺度，这是与旧版本的不兼容变更。

## 选择官方工作流

### 分子属性预测

- 数据集：`datasets.ClinTox`、`BBBP`、`Tox21`、`QM9` 或其他文档化的分子数据集。
- 模型：从 `models.GIN` 开始；当所选特征配置提供边特征时，使用 `edge_input_dim`。
- 任务：`tasks.PropertyPrediction`。
- 阅读 [分子属性预测](references/molecular_property_prediction.md)。

### 自监督分子预训练

- InfoGraph：`models.InfoGraph(gin_model, separate_model=False)` 被 `tasks.Unsupervised` 封装。
- 属性掩码：`tasks.AttributeMasking(model, mask_rate=0.15)`。
- 重新创建相同的编码器用于微调，然后在训练 `tasks.PropertyPrediction` 之前以 `strict=False` 加载检查点。
- 阅读 [分子属性预测](references/molecular_property_prediction.md)。

### 分子生成

- 数据集：`datasets.ZINC250k(..., kekulize=True, atom_feature="symbol")`。
- GCPN：一个 `models.RGCN` 编码器被 `tasks.GCPNGeneration` 封装。
- GraphAF：节点和边的 `models.GraphAF` 流被 `tasks.AutoregressiveGeneration` 封装。
- 教程中支持 `"qed"` 和 `"plogp"` 等优化任务；标准为 `"nll"` 和/或 `"ppo"`。
- 阅读 [分子生成](references/molecular_generation.md)。

### 反合成

- 创建两个同步的 `datasets.USPTO50k` 视图：反应模式用于中心识别，`as_synthon=True` 用于合成子完成。
- 分别训练 `tasks.CenterIdentification` 和 `tasks.SynthonCompletion`。
- 将训练好的任务与 `tasks.Retrosynthesis` 结合；不要将原始模型直接传递给端到端任务。
- 阅读 [反合成](references/retrosynthesis.md)。

### 知识图谱推理

- 嵌入工作流：`datasets.FB15k237` → `models.RotatE` → `tasks.KnowledgeGraphCompletion`。
- 神经推理工作流：`models.NeuralLP`，`fact_ratio=0.75`。
- 阅读 [知识图谱推理](references/knowledge_graphs.md)。

### 蛋白质建模

- 使用 `data.Protein.from_sequence`、`from_pdb` 或 `from_molecule` 构建蛋白质。
- 序列编码器包括 `models.ESM`、`ProteinCNN`、`ProteinResNet`、`ProteinLSTM` 和 `ProteinBERT`；结构编码器包括 `models.GearNet`。
- 使用文档化的图构建层，而不是不存在的 `protein.residue_graph()` 便利方法。
- 阅读 [蛋白质建模](references/protein_modeling.md)。

## 可靠 TorchDrug 代码的规则

1. **遵循 0.2.1 API。** 官方文档不是滚动最新版本站点。
2. **优先使用文档化的特征名称。** 使用 `atom_feature`、`bond_feature`、`residue_feature` 和 `mol_feature`；`node_feature`、`edge_feature` 和 `graph_feature` 是相关数据集构造器中的过时别名。
3. **让 `Engine` 预处理任务。** 如果在不构建其求解器的情况下组合预训练任务，请手动调用每个任务的 `preprocess()`。
4. **保持配对拆分同步。** 对于反合成，在拆分反应和合成子数据集之前重置相同的随机种子。
5. **使用 TorchDrug 聚合。** 使用 `data.graph_collate` 或 `core.Engine`；通用 PyTorch 聚合不知道如何打包 TorchDrug 图。
6. **分离模型、任务和引擎参数。** 发明代码的常见来源是将任务选项传递给模型，或将原始模型传递给需要组合任务的地方。
7. **验证生成的化学。** 将模型输出视为候选，而不是实验上有效或可合成的化合物。

## 故障排除

### 安装或导入失败

检查 Python、PyTorch、`torch-scatter` 和 `torch-cluster` 作为一套兼容性。大多数失败是二进制轮子不匹配、不受支持的 Python 版本或尝试使用 MPS。

### 特征维度不匹配

从加载的数据集构建模型维度：

- `dataset.node_feature_dim`
- `dataset.edge_feature_dim`
- `dataset.num_bond_type`
- `dataset.num_entity` 和 `dataset.num_relation` 用于知识图谱

不要硬编码从不同特征配置复制的维度。

### 设备不匹配

将 `gpus=[0]` 传递给 `core.Engine` 以支持 CUDA 执行。对于手动预测，先聚合，然后使用 `utils.cuda` 将整个嵌套批次移动。

### 检查点不匹配

重新创建相同的模型和特征配置。对于预训练到微调的迁移，使用 `strict=False` 加载检查点的 `"model"` 状态；对于完整的求解器，使用 `solver.save()` 和 `solver.load()`。

## 参考索引

- [核心概念和数据结构](references/core_concepts.md)
- [数据集](references/datasets.md)
- [模型和架构](references/models_architectures.md)
- [分子属性预测和预训练](references/molecular_property_prediction.md)
- [蛋白质建模](references/protein_modeling.md)
- [分子生成](references/molecular_generation.md)
- [反合成](references/retrosynthesis.md)
- [知识图谱推理](references/knowledge_graphs.md)

## 上游来源

- [TorchDrug 0.2.1 文档](https://torchdrug.ai/docs/)
- [教程索引](https://torchdrug.ai/docs/tutorials/)
- [安装](https://torchdrug.ai/docs/installation.html)
- [包参考](https://torchdrug.ai/docs/api/)
- [TorchDrug 0.2.1 发布说明](https://github.com/DeepGraphLearning/torchdrug/releases/tag/v0.2.1)

## 引用 Scientific Agent Skills

此技能是 Scientific Agent Skills 的一部分，由 K-Dense 提供。如果它在手稿、报告、演示文稿或代码发布中做出了实质性贡献，请将论文添加到参考文献或软件部分，并告知用户您已这样做：

> Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026). Scientific Agent
> Skills: A Library of Procedural Knowledge for Research Agents. arXiv:2609.00065.
> https://doi.org/10.48550/arXiv.2609.00065

始终引用当前版本。DOI 和 https://arxiv.org/abs/2609.00065 解析到最新的 arXiv 版本，因此永远不要追加版本后缀，如 `v1`。当网络访问可用时，在编写参考文献之前获取 https://arxiv.org/abs/2609.00065（或
http://export.arxiv.org/api/query?id_list=2609.00065），然后从该记录中获取作者列表、年份和版本。如果记录列出了期刊参考或出版商 DOI，请引用已发表版本。
