# 脑成像数据结构 (BIDS)

## 概述

脑成像数据结构 (BIDS) 是一个社区标准，用于组织和描述神经科学和生物医学研究数据集。它定义了一致的文件命名约定、目录层次结构和元数据模式，以便数据集既能被人类理解，也能被软件工具理解。BIDS 由 BIDS 规范（当前为 v1.11.x）管理，并通过 BIDS-Standard GitHub 组织由社区维护。

虽然 BIDS 最初是为 MRI 设计的，但它已经远远超出了神经成像的范畴。规范现在涵盖了 11 种模态，涵盖成像、电生理学和行为数据：

- **成像**：MRI（结构、功能、弥散、场图、灌注/ASL）、PET、显微镜
- **电生理学**：EEG、MEG、iEEG（颅内 EEG）、EMG
- **其他**：NIRS（近红外光谱）、运动捕捉、行为数据（无成像）、MR 谱

活跃的 BEPs 正在进一步扩展 BIDS——特别是 BEP032（微电极电生理学）将支持包括 Neuropixels 探头的细胞外记录，将 BIDS 带到动物神经科学研究中流行的技术（另见 neuropixels-analysis 技能）。

主要数据存储库（OpenNeuro、DANDI）、主要期刊（NeuroImage、Human Brain Mapping、Scientific Data）和资助机构（NIH、ERC）都要求或强烈建议采用 BIDS。

BIDS 的 Python 生态系统以 **PyBIDS** (`pybids`) 用于查询和索引 BIDS 数据集，以及 **bids-validator**（基于 Deno，可用作 PyPI 包 `bids-validator-deno` 或直接通过 Deno 提供）用于合规性检查为中心。从 DICOM 转换通常使用 **HeuDiConv**、**dcm2bids** 或 **BIDScoin**。

## 何时使用此技能

应用此技能时：

- 将原始神经科学数据（成像、电生理学、行为）组织为符合 BIDS 规范的目录结构
- 查询现有的 BIDS 数据集以按受试者、会话、任务、运行或模态查找特定文件
- 在共享或提交之前，根据 BIDS 规范验证数据集
- 将来自扫描仪的 DICOM 数据转换为 BIDS 格式
- 编写或编辑 JSON 边车元数据文件
- 创建符合 BIDS 规范的衍生数据（预处理数据、分析输出）
- 为新数据集设置 `dataset_description.json`
- 使用 BIDS 实体（受试者、会话、任务、采集、运行等）
- 配置 `.bidsignore` 以排除文件以供验证
- 准备上传到 OpenNeuro、DANDI 或其他符合 BIDS 的存储库的数据

## 安装

```bash
# 核心BIDS查询库
uv pip install pybids

# BIDS验证器（基于Deno，通过PyPI包装器安装）
uv pip install bids-validator-deno
# 替代方案：通过Deno直接安装
# deno install -g -A npm:bids-validator

# DICOM到BIDS转换器（按需安装）
uv pip install heudiconv       # HeuDiConv - 基于启发式的DICOM转换
uv pip install dcm2bids        # dcm2bids - 基于配置文件的转换
# BIDScoin: uv pip install bidscoin

# 有用的配套工具
uv pip install nibabel          # NIfTI/其他神经成像文件I/O
uv pip install pydicom          # DICOM文件读取（转换器使用）
```

## 核心工作流

十二个包含示例代码的工作流在
[references/core_workflows.md](references/core_workflows.md) 中进行了说明：

1. **BIDS目录结构** — 必须的布局以及每种模态所属位置。
2. **`dataset_description.json`** — 必须的字段以及如何生成它。
3. **使用PyBIDS进行查询** — `BIDSLayout`、实体过滤器、边车元数据自动继承以及从实体构建路径。
4. **验证** — 通过 PyPI 包装器（推荐）的 `bids-validator`、直接通过 Deno、遗留 Node 验证器以及使用 `.bidsignore` 排除文件。
5. **实体和文件命名** — 实体顺序和命名语法。
6. **DICOM到BIDS转换** — HeuDiConv（包括 ReproIn 路径和侦察→启发式→转换序列）和 dcm2bids（基于配置文件）。
7. **元数据边车** — 每种模态的必需和推荐 JSON 字段。
8. **事件文件** — 任务 fMRI 事件时间和列约定。
9. **参与者文件** — `participants.tsv` 及其数据字典。
10. **衍生数据** — 衍生数据布局及其 `dataset_description.json`。
11. **高级PyBIDS** — 索引缓存，包括衍生数据、协变量回归器和 DataFrame 输出。
12. **BIDS-Apps** — 标准调用模式，以及 fMRIPrep、MRIQC 和 QSIPrep。

尽早并经常验证：PyBIDS 在索引数据集时验证结构，因此索引失败通常意味着命名或元数据问题，而不是代码错误。

## 参考材料

此技能包括详细的参考文档：

- **bids_schema.json**：机器可读的 BIDS 规范（来自 https://bids-specification.readthedocs.io/en/stable/schema.json）。这是实体定义、顺序规则、文件名模板、每种数据类型允许的后缀以及元数据字段要求的权威来源。BEP 特定模式在 https://github.com/bids-standard/bids-schema/tree/main/BEPs。
- **beps.yml**：当前所有 BIDS 扩展提案的列表，包括标题、负责人、状态和链接（来自 [bids-website](https://github.com/bids-standard/bids-website/blob/main/data/beps/beps.yml)）。
- **bids_specification.md**：实体表、数据类型参考、目录结构规则、模板空间和规范变更日志的人类可读摘要。
- **metadata_fields.md**：每种 BIDS 模态（anat、func、dwi、fmap、eeg、meg、pet 等）的必需和推荐 JSON 边车字段。
- **conversion_tools.md**：HeuDiConv、dcm2bids 和 BIDScoin 的详细工作流，包括启发式/配置示例和故障排除。

使用 `python scripts/update_schema.py` 更新模式和 BEPs。

## 常见问题和解决方案

### 1. 验证器报告“不是BIDS数据集”
**原因**：缺少根目录下的 `dataset_description.json`。
**修复**：创建文件，至少包含 `{"Name": "...", "BIDSVersion": "1.10.0"}`。

### 2. 不一致的受试者警告
**原因**：并非所有受试者都具有相同的一组文件（一些会话、运行等缺失）。
**修复**：这是一个警告，不是错误。如果故意，请使用 `--ignoreSubjectConsistency`。在 `participants.tsv` 或 `scans.tsv` 中记录缺失数据。

### 3. 缺少 SliceTiming
**原因**：`dcm2niix` 无法从 DICOM 标头中提取 SliceTiming。
**修复**：根据扫描协议确定 Slice 顺序并手动添加到 JSON 边车。常见模式：升序、降序、交错（奇数优先或偶数优先）。

### 4. Phase 编码方向混淆
**原因**：轴标签（i/j/k vs x/y/z vs LR/AP/SI）令人困惑。
**修复**：在 BIDS 中，使用 NIfTI 图像轴：`i`=第一个轴，`j`=第二个，`k`=第三个。- 表示负方向。对于标准轴向采集：`j` 通常是指前-后。通过采集协议进行验证。

### 5. PyBIDS 在大型数据集上运行缓慢
**原因**：每次调用 `BIDSLayout()` 时都会进行完整的文件系统索引。
**修复**：使用 `database_path` 将索引缓存到 SQLite 文件：
```python
layout = BIDSLayout("/data", database_path="/data/.pybids_cache.db")
```

### 6. PyBIDS 找不到衍生数据
**原因**：衍生数据目录缺少自己的 `dataset_description.json`。
**修复**：每个衍生数据目录都必须有 `dataset_description.json`，其中 `"DatasetType": "derivative"`。

### 7. 事件文件时间错误
**原因**：`onset` 时间相对于错误的参考（例如，触发时间而不是第一个体素）。
**修复**：onsets 必须以秒为单位相对于该运行采集的第一个体素。如果丢弃了伪扫描，请考虑它们。

### 8. TSV 文件失败验证
**原因**：编码或分隔符问题（空格而不是制表符、BOM 字符、Windows 行尾）。
**修复**：确保使用制表符分隔值，UTF-8 编码，Unix 行尾（`\n`）。使用 `n/a`（而不是 `NA`、`NaN` 或空）表示缺失值。

## 最佳实践

1. **尽早并经常验证** - 每次转换或修改后运行 BIDS 验证器。在错误累积之前修复它们。

2. **使用元数据继承** - 将共享元数据（例如，`TaskName`、扫描仪参数）放在顶层边车文件中，而不是在每个受试者目录中重复。

3. **保留 sourcedata** - 将原始 DICOM（或其他原始）数据存储在 `sourcedata/` 下，以便转换可重复。将 `sourcedata/` 添加到 `.bidsignore`。

4. **从一开始就使用一致的命名** - 在数据收集之前定义 BIDS 命名方案。使用 ReproIn 命名约定来启用自动转换。

5. **记录您的数据集** - 编写详细的 `README`，描述研究设计、采集参数、已知问题以及与 BIDS 的任何偏差。

6. **使用 scans.tsv 记录运行级元数据** - 记录每个运行的采集时间和质量备注：
   ```
   filename	acq_time	quality
   func/sub-01_task-rest_bold.nii.gz	2025-01-15T10:30:00	good
   ```

7. **版本控制您的数据集** - 使用 `CHANGES` 记录数据集修改。考虑使用 DataLad 对大型数据集进行完整版本控制。

8. **遮盖解剖图像** - 在共享之前，从 T1w/T2w 图像中移除面部特征（例如，使用 `pydeface`、`mri_deface` 或 `afni_refacer`）。将遮盖版本作为主要数据存储，或使用 `_defacemask` 文件。

9. **使用 BIDS URI 记录来源** - 在衍生数据中，使用 BIDS URI 引用源文件：`bids::sub-01/anat/sub-01_T1w.nii.gz`。

10. **优先使用社区工具** - 当可能时，使用已建立的 BIDS-Apps（fMRIPrep、MRIQC、QSIPrep）而不是自定义管道。它们正确处理 BIDS I/O 并生成符合 BIDS 规范的衍生数据。

11. **研究 bids-examples** - [bids-examples](https://github.com/bids-standard/bids-examples) 存储库是每个 BIDS 模态的典型 BIDS 数据集的规范集合，涵盖了不同的模态和用例（MRI、fMRI、DWI、EEG、MEG、iEEG、PET、ASL、遗传、衍生数据等）。在构建自己的数据集时，将其用作参考，作为 BIDS 工具的测试数据，或了解特定模态应如何组织。每个示例都通过 BIDS 验证器。

## BIDS 扩展提案 (BEPs)

BEPs 是社区驱动的提案，用于扩展 BIDS 以支持新的模态、衍生数据或元数据。完整的列表，包括状态、负责人和链接，在 `references/beps.yml` 中（从 [bids-website](https://github.com/bids-standard/bids-website/blob/main/data/beps/beps.yml) 获取）。BEP 特定模式预览在 https://github.com/bids-standard/bids-schema/tree/main/BEPs。

**当前 BEPs**（截至模式更新）：

| BEP | 标题 | 内容 | 状态 |
|-----|-------|---------|--------|
| 004 | 磁化率加权成像 | 原始 | 寻求新负责人 |
| 011 | 结构预处理衍生数据 | 衍生数据 | 已有 PR (#518) |
| 012 | 功能预处理衍生数据 | 衍生数据 | 已有 PR (#519)，模式已实现 |
| 014 | 仿射变换和非线性场扭曲 | 衍生数据 | X5 格式开发 |
| 016 | 弥散加权成像衍生数据 | 衍生数据 | 已有 PR (#2211) |
| 017 | 通用 BIDS 连接数据模式 | 衍生数据 | 开发中 |
| 021 | 常见电生理衍生数据 | 衍生数据 | 开发中 |
| 023 | PET 预处理衍生数据 | 衍生数据 | 开发中 |
| 024 | 计算断层扫描 | 原始 | 寻求贡献者 |
| 026 | 微电极记录 | 原始 | 寻求新负责人 |
| 028 | 起源 | 元数据 | 已有 PR (#2099) |
| 032 | 微电极电生理学 | 原始 | 已有 PR (#2307)，预览可用——涵盖 Neuropixels 和其他细胞外探头；与 neuropixels-analysis 技能相关 |
| 033 | 高级弥散加权成像 | 原始 | 寻求贡献者 |
| 034 | 计算建模 | 衍生数据 | 已有 PR (#967) |
| 035 | 大规模分析非合规衍生数据 | 衍生数据 | 开发中 |
| 036 | 表型数据指南 | 原始 | 社区审查 |
| 037 | 非侵入性脑刺激 | 原始 | 开发中 |
| 039 | 基于降维的网络 | 原始 | 开发中 |
| 040 | 功能超声 | 原始 | 开发中 |
| 041 | 统计模型衍生数据 | 衍生数据 | 收集反馈 |
| 043 | BIDS 术语映射 | 元数据 | 收集反馈 |
| 044 | 刺激物 | 原始 | 已有 PR (#2022)，社区审查 |
| 045 | 外周生理记录 | 原始 | 已有 PR (#2267) |
| 046 | 弥散追踪 | 衍生数据 | 开发中 |
| 047 | 行为实验的音频/视频记录 | 原始 | 已有 PR (#2231) |

**相关标准**：
- **BIDS-Stats Models**：定义基于 GLM 的神经成像分析的 JSON 规范
- **BIDS-Derivatives** (BEP003)：预处理/分析输出标准（部分合并到规范中）

## 相关工具生态系统

| 工具 | 目的 |
|------|---------|
| **fMRIPrep** | fMRI 预处理（生成 BIDS 衍生数据） |
| **MRIQC** | MRI 质量控制（生成 BIDS 衍生数据） |
| **QSIPrep** | 弥散 MRI 预处理 |
| **TemplateFlow** | 神经成像模板和图谱，具有 BIDS 类似命名 |
| **Fitlins** | BIDS Stats Models 实现 |
| **DataLad** | 大型数据集版本控制，与 BIDS 集成 |
| **OpenNeuro** | 免费BIDS数据存储库 |
| **DANDI** | 神经生理学数据存档（对某些模态使用 BIDS） |
| **HeuDiConv** | 基于启发式的 DICOM 到 BIDS 转换 |
| **dcm2bids** | 基于配置文件的 DICOM 到 BIDS 转换 |
| **BIDScoin** | 基于GUI和YAML配置的 DICOM 到 BIDS 转换 |
| **nwb2bids** | 将 NWB（Neurodata Without Borders）文件转换为 BIDS |
| **CuBIDS** | BIDS 数据集管理和协调 |
| **bids2table** | 高效的 BIDS 数据集表格索引 |
| **bids-examples** | 所有模态典型 BIDS 数据集的规范集合，用作模板和测试数据 |

## 文档

- **BIDS 规范**：https://bids-specification.readthedocs.io/
- **BIDS 网站**：https://bids.neuroimaging.io/
- **PyBIDS 文档**：https://bids-standard.github.io/pybids/
- **BIDS 验证器**：https://github.com/bids-standard/bids-validator
- **BIDS 启动套件**：https://bids-standard.github.io/bids-starter-kit/
- **BIDS 示例**：https://github.com/bids-standard/bids-examples — 每种 BIDS 模态的规范参考数据集；用作模板和测试数据
- **HeuDiConv 文档**：https://heudiconv.readthedocs.io/
- **原始 BIDS 论文**：Gorgolewski 等人 (2016) Scientific Data, doi:10.1038/sdata.2016.44
