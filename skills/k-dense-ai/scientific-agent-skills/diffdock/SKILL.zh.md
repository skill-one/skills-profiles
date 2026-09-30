---
name: diffdock
description: DiffDock和DiffDock-L分子对接。用于从PDB或序列加SMILES/SDF/MOL2进行蛋白质小分子构象预测、批量对接、虚拟筛选和构象置信度解释。不用于结合亲和力预测。
---

# DiffDock：基于扩散模型的分子对接工具

## 概述

DiffDock 是一种基于扩散模型的深度学习分子对接工具，用于预测小分子配体与蛋白质靶标的 3D 结合构象。它代表了计算对接领域的最新技术，对于基于结构的药物发现和化学生物学至关重要。

**核心功能：**
- 使用深度学习以高精度预测配体结合构象
- 支持蛋白质结构（PDB 文件）或序列（通过 ESMFold）
- 处理单个复合物或批量虚拟筛选任务
- 生成置信度分数以评估预测可靠性
- 处理多种配体输入（SMILES、SDF、MOL2）

**关键区别：** DiffDock 预测**结合构象**（3D 结构）和**置信度**（预测确定性），而不是结合亲和力（ΔG、Kd）。始终需要结合评分函数（GNINA、MM/GBSA）进行亲和力评估。

## 何时使用此技能

当出现以下情况时，应使用此技能：

- "将此配体对接到蛋白质"或"预测结合构象"
- "运行分子对接"或"执行蛋白质-配体对接"
- "虚拟筛选"或"筛选化合物库"
- "此分子在何处结合？"或"预测结合位点"
- 基于结构的药物设计或先导化合物优化任务
- 涉及 PDB 文件 + SMILES 字符串或配体结构的任务
- 批量对接多个蛋白质-配体对

## 安装和环境配置

### 检查环境状态

在进行 DiffDock 任务之前，请验证环境设置：

```bash
# 使用提供的设置检查器
python scripts/setup_check.py
```

此脚本验证 Python 版本、PyTorch with CUDA、PyTorch Geometric、RDKit、ESM 和其他依赖项。

### 安装选项

**选项 1：Conda（推荐）**
```bash
git clone https://github.com/gcorso/DiffDock.git
cd DiffDock
conda env create --file environment.yml
conda activate diffdock
```

**选项 2：Docker**
```bash
docker pull rbgcsail/diffdock
docker run -it --gpus all --entrypoint /bin/bash rbgcsail/diffdock
micromamba activate diffdock
```

**重要提示：**
- 强烈推荐使用 GPU（比 CPU 快 10-100 倍）
- 首次运行会预计算 SO(2)/SO(3) 查找表（约 2-5 分钟）
- 模型检查点（约 500MB）如果不存在会自动下载
- 当前上游版本是 DiffDock v1.1.3；DiffDock-L 是 `default_inference_args.yaml` 中的默认模型系列

## 核心工作流程

### 工作流程 1：单个蛋白质-配体对接

**用例：** 将一个配体对接到一个蛋白质靶标

**输入要求：**
- 蛋白质：PDB 文件 或 氨基酸序列
- 配体：SMILES 字符串 或 结构文件（SDF/MOL2）

**命令：**
```bash
python -m inference \
  --config default_inference_args.yaml \
  --protein_path protein.pdb \
  --ligand_description "CC(=O)Oc1ccccc1C(=O)O" \
  --out_dir results/single_docking/
```

**替代方案（蛋白质序列）：**
```bash
python -m inference \
  --config default_inference_args.yaml \
  --protein_sequence "MSKGEELFTGVVPILVELDGDVNGHKF..." \
  --ligand_description ligand.sdf \
  --out_dir results/sequence_docking/
```

**输出结构：**
```
results/single_docking/
└── complex_0/
    ├── rank1.sdf                    # 便利地复制了排名最高的构象
    ├── rank1_confidence0.87.sdf     # 排名最高的构象，文件名中包含置信度
    ├── rank2_confidence0.42.sdf     # 第二高的构象
    ├── ...
    └── rank10_confidence-1.23.sdf   # 第 10 个构象（默认：10 个样本）
```

当前的 `inference.py` 注册了 `--ligand_description` 用于单个复合物运行。一些上游 README 文本仍然说 `--ligand`；除非您的本地检出明确支持 `--ligand` 别名，否则请使用 `--ligand_description`。

### 工作流程 2：批量处理多个复合物

**用例：** 将多个配体对接到蛋白质，虚拟筛选任务

**步骤 1：准备批量 CSV**

使用提供的脚本创建或验证批量输入：

```bash
# 创建模板
python scripts/prepare_batch_csv.py --create --output batch_input.csv

# 验证现有 CSV
python scripts/prepare_batch_csv.py my_input.csv --validate
```

**CSV 格式：**
```csv
complex_name,protein_path,ligand_description,protein_sequence
complex1,protein1.pdb,CC(=O)Oc1ccccc1C(=O)O,
complex2,,COc1ccc(C#N)cc1,MSKGEELFT...
complex3,protein3.pdb,ligand3.sdf,
```

**必需列：**
- `complex_name`：唯一标识符
- `protein_path`：PDB 文件路径（如果使用序列，则为空）
- `ligand_description`：SMILES 字符串或配体文件路径
- `protein_sequence`：氨基酸序列（如果使用 PDB，则为空）

**步骤 2：运行批量对接**

```bash
python -m inference \
  --config default_inference_args.yaml \
  --protein_ligand_csv batch_input.csv \
  --out_dir results/batch/ \
  --batch_size 10
```

**对于大型虚拟筛选（>100 个化合物）：**

预计算蛋白质嵌入以加快处理速度：
```bash
# 预计算嵌入
python datasets/esm_embedding_preparation.py \
  --protein_ligand_csv screening_input.csv \
  --out_file protein_embeddings.pt

# 使用预计算的嵌入运行
python -m inference \
  --config default_inference_args.yaml \
  --protein_ligand_csv screening_input.csv \
  --esm_embeddings_path protein_embeddings.pt \
  --out_dir results/screening/
```

### 工作流程 3：分析结果

对接完成后，分析置信度分数和排名预测：

```bash
# 分析所有结果
python scripts/analyze_results.py results/batch/

# 每个复合物显示前 5 个
python scripts/analyze_results.py results/batch/ --top 5

# 按置信度阈值过滤
python scripts/analyze_results.py results/batch/ --threshold 0.0

# 导出到 CSV
python scripts/analyze_results.py results/batch/ --export summary.csv

# 显示所有复合物中前 20 个预测
python scripts/analyze_results.py results/batch/ --best 20
```

分析脚本：
- 解析所有预测中的置信度分数
- 将其分类为高（>0）、中等（-1.5 到 0）或低（<-1.5）
- 在复合物内部和跨复合物排名预测
- 生成统计摘要
- 将结果导出到 CSV 以供下游分析

## 置信度分数解释

**理解分数：**

| 分数范围 | 置信度级别 | 解释 |
|------------|------------------|----------------|
| **> 0** | 高 | 强预测，可能准确 |
| **-1.5 到 0** | 中等 | 合理预测，需仔细验证 |
| **< -1.5** | 低 | 不确定预测，需要验证 |

**重要提示：**
1. **置信度 ≠ 亲和力**：高置信度意味着模型对结构的确定性，而不是强结合
2. **上下文很重要**：调整预期，包括：
   - 大型配体（>500 Da）：预期置信度较低
   - 多个蛋白质链：可能会降低置信度
   - 新的蛋白质家族：可能表现不佳
3. **多个样本**：查看前 3-5 个预测，寻找共识

**详细指导：** 使用 Read 工具阅读 `references/confidence_and_limitations.md`

## 参数自定义

### 使用自定义配置

为特定用例创建自定义配置：

```bash
# 复制模板
cp assets/custom_inference_config.yaml my_config.yaml

# 编辑参数（查看模板中的预设）
# 然后使用自定义配置运行
python -m inference \
  --config my_config.yaml \
  --protein_ligand_csv input.csv \
  --out_dir results/
```

### 要调整的关键参数

**采样密度：**
- `samples_per_complex: 10` → 对于困难情况增加到 20-40
- 更多样本 = 覆盖率更好，但运行时间更长

**推理步骤：**
- `inference_steps: 20` → 增加到 25-30 以提高精度
- 更多步骤 = 可能会提高质量，但更慢

**温度参数（控制多样性）：**
- `temp_sampling_tor: 7.04` → 增加用于柔性配体（8-10）
- `temp_sampling_tor: 7.04` → 减少用于刚性配体（5-6）
- 更高的温度 = 更多样化的构象

**模板中提供的预设：**
1. 高精度：更多样本 + 步骤，较低温度
2. 快速筛选：较少样本，更快
3. 柔性配体：增加扭转温度
4. 刚性配体：降低扭转温度

**完整参数参考：** 使用 Read 工具阅读 `references/parameters_reference.md`

## 高级技术

### 众包对接（蛋白质柔性）

对于具有已知柔性的蛋白质，对接到多个构象：

```python
# 创建众包 CSV
import pandas as pd

conformations = ["conf1.pdb", "conf2.pdb", "conf3.pdb"]
ligand = "CC(=O)Oc1ccccc1C(=O)O"

data = {
    "complex_name": [f"ensemble_{i}" for i in range(len(conformations))],
    "protein_path": conformations,
    "ligand_description": [ligand] * len(conformations),
    "protein_sequence": [""] * len(conformations)
}

pd.DataFrame(data).to_csv("ensemble_input.csv", index=False)
```

使用增加的采样运行对接：
```bash
python -m inference \
  --config default_inference_args.yaml \
  --protein_ligand_csv ensemble_input.csv \
  --samples_per_complex 20 \
  --out_dir results/ensemble/
```

### 与评分函数集成

DiffDock 生成构象；结合其他工具进行亲和力评估：

**GNINA（快速神经网络评分）：**
```bash
for pose in results/single_docking/complex_0/*confidence*.sdf; do
    gnina -r protein.pdb -l "$pose" --score_only
done
```

**MM/GBSA（更准确，更慢）：**
使用 AmberTools MMPBSA.py 或 gmx_MMPBSA 在能量最小化后运行

**自由能计算（最准确）：**
使用 OpenMM + OpenFE 或 GROMACS 进行 FEP/TI 计算

**推荐工作流程：**
1. DiffDock → 生成带置信度分数的构象
2. 可视化检查 → 检查结构合理性
3. GNINA 或 MM/GBSA → 重新评分并按亲和力排名
4. 实验验证 → 生化实验

## 限制和范围

**DiffDock 适用于：**
- 小分子配体（通常 100-1000 Da）
- 药物样有机化合物
- 小肽（<20 个残基）
- 单链或多链蛋白质

**DiffDock 不适用于：**
- 大型生物分子（蛋白质-蛋白质对接）→ 使用 DiffDock-PP 或 AlphaFold-Multimer
- 大型肽（>20 个残基）→ 使用替代方法
- 共价对接 → 使用专门的共价对接工具
- 结合亲和力预测 → 结合评分函数
- 膜蛋白质 → 未专门训练，需谨慎使用

**完整限制：** 使用 Read 工具阅读 `references/confidence_and_limitations.md`

## 故障排除

### 常见问题

**问题：所有预测的置信度分数低**
- 原因：大型/不寻常的配体，结合位点不明确，蛋白质柔性
- 解决方案：增加 `samples_per_complex`（20-40），尝试众包对接，验证蛋白质结构

**问题：内存错误**
- 原因：GPU 内存不足以处理批量大小
- 解决方案：减少 `--batch_size 2` 或一次处理较少的复合物

**问题：运行缓慢**
- 原因：在 CPU 上运行而不是 GPU
- 解决方案：使用 `python -c "import torch; print(torch.cuda.is_available())"` 验证 CUDA，使用 GPU

**问题：不现实的结合构象**
- 原因：蛋白质准备不佳，配体太大，结合位点错误
- 解决方案：检查蛋白质以修复缺失的残基，删除远处的水，考虑指定结合位点

**问题："模块未找到"错误**
- 原因：缺少依赖项或环境不正确
- 解决方案：运行 `python scripts/setup_check.py` 进行诊断

### 性能优化

**为获得最佳结果：**
1. 使用 GPU（实际使用中必不可少）
2. 预计算 ESM 嵌入以供重复使用的蛋白质使用
3. 批量处理多个复合物
4. 默认参数开始，如有必要再调整
5. 验证蛋白质结构（修复缺失的残基）
6. 使用规范化的 SMILES 配体

## 图形用户界面

对于交互式使用，启动网络界面：

```bash
python app/main.py
# 导航到 http://localhost:7860
```

或使用在线演示而无需安装：
- https://huggingface.co/spaces/reginabarzilaygroup/DiffDock-Web

## 资源

### 辅助脚本（`scripts/`）

**`prepare_batch_csv.py`**：创建和验证批量输入 CSV 文件
- 创建带示例条目的模板
- 验证文件路径和 SMILES 字符串
- 检查必需列和格式问题

**`analyze_results.py`**：分析置信度分数和排名预测
- 解析单个或批量运行的结果
- 生成统计摘要
- 导出到 CSV 以供下游分析
- 识别跨复合物的顶级预测

**`setup_check.py`**：验证 DiffDock 环境设置
- 检查 Python 版本和依赖项
- 验证 PyTorch 和 CUDA 的可用性
- 测试 RDKit 和 PyTorch Geometric 的安装
- 如有必要提供安装说明

### 参考文档（`references/`）

**`parameters_reference.md`**：完整参数文档
- 所有命令行选项和配置参数
- 默认值和可接受范围
- 控制多样性的温度参数
- 模型检查点位置和版本标志

当用户需要时，阅读此文件：
- 详细参数说明
- 特定系统的微调指导
- 采样策略的替代方案

**`confidence_and_limitations.md`**：置信度分数解释和工具限制
- 详细置信度分数解释
- 何时信任预测
- DiffDock 的范围和限制
- 与互补工具的集成
- 预测质量的故障排除

当用户需要时，阅读此文件：
- 解释置信度分数
- 了解何时不应使用 DiffDock
- 指导如何结合其他工具
- 验证策略

**`workflows_examples.md`**：综合工作流程示例
- 详细的安装说明
- 所有工作流程的逐步示例
- 高级集成模式
- 常见问题故障排除
- 最佳实践和优化技巧

当用户需要时，阅读此文件：
- 带代码的完整工作流程示例
- 与 GNINA、OpenMM 或其他工具的集成
- 虚拟筛选工作流程
- 众包对接程序

### 资产（`assets/`）

**`batch_template.csv`**：批量处理模板
- 带有必需列的预格式化 CSV
- 示例条目显示不同输入类型
- 准备好用实际数据自定义

**`custom_inference_config.yaml`**：配置模板
- 带注释的 YAML，包含所有参数
- 四种预设配置用于常见用例
- 详细说明每个参数
- 准备好自定义和使用

## 最佳实践

1. **始终使用 `setup_check.py` 验证环境** 在开始大型任务之前
2. **验证批量 CSV** 使用 `prepare_batch_csv.py` 以便尽早发现错误
3. **从默认值开始** 然后根据系统特定需求调整参数
4. **生成多个样本**（10-40）以获得稳健的预测
5. **对接前进行可视化检查** 顶级构象
6. **结合评分函数** 进行亲和力评估
7. **使用置信度分数** 进行初始排名，而不是最终决定
8. **预计算嵌入** 用于虚拟筛选任务
9. **记录使用的参数** 以确保可重复性
10. **可能时进行实验验证**

卡西斯，T.，阿格拉瓦尔，V.，何，Y.，帕特尔，D.，& 布鲁克纳，A. M. (2026)。科学代理技能：研究代理的程序知识库。arXiv:2609.00065。
https://doi.org/10.48550/arXiv.2609.00065

始终引用最新版本。DOI 和 https://arxiv.org/abs/2609.00065 解析到最新的 arXiv 版本，因此切勿附加版本后缀，如 `v1`。当网络可访问时，在编写参考文献之前，先获取 https://arxiv.org/abs/2609.00065（或 http://export.arxiv.org/api/query?id_list=2609.00065），并从该记录中获取作者列表、年份和版本。如果记录列出了期刊引用或出版商 DOI，则引用已发表版本。
