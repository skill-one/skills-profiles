# 探索性数据分析

## 概述

对跨多个领域的科学数据文件进行全面的探索性数据分析（EDA）。这项技能提供自动化的文件类型检测、格式特定分析、数据质量评估，并生成适合文档记录和下游分析规划详细markdown报告。

**主要功能：**
- 自动检测和分析200多种科学文件格式
- 全面提取特定格式的元数据
- 数据质量和完整性评估
- 统计摘要和分布
- 可视化建议
- 下游分析建议
- markdown报告生成

## 何时使用此技能

当用户：
- 提供科学数据文件路径进行分析时
- 询问“探索”、“分析”或“总结”数据文件时
- 想要了解科学数据的结构和内容时
- 在分析前需要数据集的全面报告时
- 想要评估数据质量或完整性时
- 询问适合文件的分析类型时

## 支持的文件类别

该技能全面覆盖科学文件格式，并按六个主要类别组织：

### 1. 化学和分子格式（60多种扩展名）
结构文件、计算化学输出、分子动力学轨迹和化学数据库。

**文件类型包括：** `.pdb`、`.cif`、`.mol`、`.mol2`、`.sdf`、`.xyz`、`.smi`、`.gro`、`.log`、`.fchk`、`.cube`、`.dcd`、`.xtc`、`.trr`、`.prmtop`、`.psf` 等更多。

**参考文件：** `references/chemistry_molecular_formats.md`

### 2. 生物信息学和基因组学格式（50多种扩展名）
序列数据、比对、注释、变异和表达数据。

**文件类型包括：** `.fasta`、`.fastq`、`.sam`、`.bam`、`.vcf`、`.bed`、`.gff`、`.gtf`、`.bigwig`、`.h5ad`、`.loom`、`.counts`、`.mtx` 等更多。

**参考文件：** `references/bioinformatics_genomics_formats.md`

### 3. 显微镜和成像格式（45多种扩展名）
显微镜图像、医学成像、全切片成像和电子显微镜。

**文件类型包括：** `.tif`、`.nd2`、`.lif`、`.czi`、`.ims`、`.dcm`、`.nii`、`.mrc`、`.dm3`、`.vsi`、`.svs`、`.ome.tiff` 等更多。

**参考文件：** `references/microscopy_imaging_formats.md`

### 4. 光谱学和分析化学格式（35多种扩展名）
核磁共振、质谱、红外/拉曼、紫外-可见、X射线、色谱和其他分析技术。

**文件类型包括：** `.fid`、`.mzML`、`.mzXML`、`.raw`、`.mgf`、`.spc`、`.jdx`、`.xy`、`.cif`（晶体学）、`.wdf` 等更多。

**参考文件：** `references/spectroscopy_analytical_formats.md`

### 5. 蛋白组学和代谢组学格式（30多种扩展名）
质谱蛋白组学、代谢组学、脂质组学和多种组学数据。

**文件类型包括：** `.mzML`、`.pepXML`、`.protXML`、`.mzid`、`.mzTab`、`.sky`、`.mgf`、`.msp`、`.h5ad` 等更多。

**参考文件：** `references/proteomics_metabolomics_formats.md`

### 6. 通用科学数据格式（30多种扩展名）
数组、表格、层次数据、压缩存档和通用科学格式。

**文件类型包括：** `.npy`、`.npz`、`.csv`、`.xlsx`、`.json`、`.hdf5`、`.zarr`、`.parquet`、`.mat`、`.fits`、`.nc`、`.xml` 等更多。

**参考文件：** `references/general_scientific_formats.md`

## 工作流程

### 第一步：文件类型检测

当用户提供文件路径时，首先识别文件类型：

1. 提取文件扩展名
2. 在相应的参考文件中查找扩展名
3. 识别文件类别和格式描述
4. 加载特定格式的信息

**示例：**
```
用户："分析 data.fastq"
→ 扩展名：.fastq
→ 类别：bioinformatics_genomics
→ 格式：FASTQ格式（带质量分数的序列数据）
→ 参考：references/bioinformatics_genomics_formats.md
```

### 第二步：加载格式特定信息

根据文件类型，读取相应的参考文件以了解：
- **典型数据：** 此格式包含何种数据
- **用例：** 此格式的常见应用
- **Python库：** 如何用Python读取文件
- **EDA方法：** 适合此数据类型应进行何种分析

在参考文件中搜索特定扩展名（例如，在 `bioinformatics_genomics_formats.md` 中搜索 "### .fastq"）。

### 第三步：执行数据分析

使用 `scripts/eda_analyzer.py` 脚本或实现自定义分析：

**选项A：使用分析脚本**
```python
# 脚本自动执行：
# 1. 检测文件类型
# 2. 加载参考信息
# 3. 执行格式特定分析
# 4. 生成markdown报告

python scripts/eda_analyzer.py <filepath> [output.md]
```

**选项B：在对话中执行自定义分析**
根据参考文件中的格式信息，执行适当的分析：

对于表格数据（CSV、TSV、Excel）：
- 使用pandas加载
- 检查维度、数据类型
- 分析缺失值
- 计算摘要统计
- 识别异常值
- 检查重复项

对于序列数据（FASTA、FASTQ）：
- 计数序列
- 分析长度分布
- 计算GC含量
- 评估质量分数（FASTQ）

对于图像（TIFF、ND2、CZI）：
- 检查维度（X、Y、Z、C、T）
- 分析位深度和值范围
- 提取元数据（通道、时间戳、空间校准）
- 计算强度统计

对于数组（NPY、HDF5）：
- 检查形状和维度
- 分析数据类型
- 计算统计摘要
- 检查缺失/无效值

### 第四步：生成综合报告

创建包含以下部分的markdown报告：

#### 必须部分：
1. **标题和元数据**
   - 文件名和时间戳
   - 文件大小和位置

2. **基本信息**
   - 文件属性
   - 格式识别

3. **文件类型详情**
   - 来自参考的格式描述
   - 典型数据内容
   - 常见用例
   - 读取的Python库

4. **数据分析**
   - 结构和维度
   - 统计摘要
   - 质量评估
   - 数据特征

5. **关键发现**
   - 显著模式
   - 潜在问题
   - 质量指标

6. **建议**
   - 预处理步骤
   - 适当的分析
   - 工具和方法
   - 可视化方法

#### 模板位置
使用 `assets/report_template.md` 作为报告结构的参考。

### 第五步：保存报告

使用描述性文件名保存markdown报告：
- 模式：`{原始文件名}_eda_report.md`
- 示例：`experiment_data.fastq` → `experiment_data_eda_report.md`

## 详细格式参考

每个参考文件包含几十种文件类型的全面信息。要查找特定格式的信息：

1. 从扩展名识别类别
2. 读取相应的参考文件
3. 搜索与扩展名匹配的部分标题（例如，“### .pdb”）
4. 提取格式信息

### 参考文件结构

每个格式条目包括：
- **描述：** 格式是什么
- **典型数据：** 包含什么数据
- **用例：** 常见应用
- **Python库：** 如何读取（带代码示例）
- **EDA方法：** 应执行的具体分析

**示例查找：**
```markdown
### .pdb - 蛋白质数据银行
**描述：** 生物大分子3D结构的标准格式
**典型数据：** 原子坐标、残基信息、二级结构
**用例：** 蛋白质结构分析、分子可视化、对接
**Python库：**
- `Biopython`：`Bio.PDB`
- `MDAnalysis`：`MDAnalysis.Universe('file.pdb')`
**EDA方法：**
- 结构验证（键长、角度）
- B因子分布
- 缺失残基检测
- Ramachandran图
```

## 最佳实践

### 读取参考文件

参考文件较大（每个10,000+字）。为高效使用它们：

1. **按扩展名搜索：** 使用grep查找特定格式
   ```python
   import re
   with open('references/chemistry_molecular_formats.md', 'r') as f:
       content = f.read()
       pattern = r'### \.pdb[^#]*?(?=###|\Z)'
       match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
   ```

2. **提取相关部分：** 不要不必要地将整个参考文件加载到上下文中

3. **缓存格式信息：** 如果分析多个相同类型的文件，则重用格式信息

### 数据分析

1. **样本大文件：** 对于包含数百万条记录的文件，分析代表性样本
2. **优雅处理错误：** 许多科学格式需要特定库；提供清晰的安装说明
3. **验证元数据：** 交叉检查元数据一致性（例如，声明维度与实际数据）
4. **考虑数据来源：** 注明仪器、软件版本、处理步骤

### 报告生成

1. **保持全面：** 包含下游分析的所有相关信息
2. **保持具体：** 根据文件类型提供具体建议
3. **保持可操作：** 建议具体的下一步和工具
4. **包含代码示例：** 展示如何加载和处理数据

## 示例

### 示例1：分析FASTQ文件

```python
# 用户提供："分析 reads.fastq"

# 1. 检测文件类型
extension = '.fastq'
category = 'bioinformatics_genomics'

# 2. 读取参考信息
# 在 references/bioinformatics_genomics_formats.md 中搜索 "### .fastq"

# 3. 执行分析
from Bio import SeqIO
sequences = list(SeqIO.parse('reads.fastq', 'fastq'))
# 计算：读数计数、长度分布、质量分数、GC含量

# 4. 生成报告
# 包括：格式描述、分析结果、质量控制建议

# 5. 保存为：reads_eda_report.md
```

### 示例2：分析CSV数据集

```python
# 用户提供："探索 experiment_results.csv"

# 1. 检测：.csv → general_scientific

# 2. 读取CSV格式的参考

# 3. 分析
import pandas as pd
df = pd.read_csv('experiment_results.csv')
# 维度、数据类型、缺失值、统计、相关性

# 4. 生成报告，包括：
# - 数据结构
# - 缺失值模式
# - 统计摘要
# - 相关系数矩阵
# - 异常值检测结果

# 5. 保存报告
```

### 示例3：分析显微镜数据

```python
# 用户提供："分析 cells.nd2"

# 1. 检测：.nd2 → microscopy_imaging（尼康格式）

# 2. 读取ND2格式的参考
# 学习：多维（XYZCT）、需要nd2reader

# 3. 分析
from nd2reader import ND2Reader
with ND2Reader('cells.nd2') as images:
    # 提取：维度、通道、时间点、元数据
    # 计算：强度统计、帧信息

# 4. 生成报告，包括：
# - 图像维度（XY、Z栈、时间、通道）
# - 通道波长
# - 像素大小和校准
# - 图像分析建议

# 5. 保存报告
```

## 故障排除

### 缺少库

许多科学格式需要专用库：

**问题：** 尝试读取文件时出现导入错误

**解决方案：** 提供清晰的安装说明
```python
try:
    from Bio import SeqIO
except ImportError:
    print("安装Biopython：uv pip install biopython")
```

按类别常见的需求：
- **生物信息学：** `biopython`、`pysam`、`pyBigWig`
- **化学：** `rdkit`、`mdanalysis`、`cclib`
- **显微镜：** `tifffile`、`nd2reader`、`aicsimageio`、`pydicom`
- **光谱学：** `nmrglue`、`pymzml`、`pyteomics`
- **通用：** `pandas`、`numpy`、`h5py`、`scipy`

### 未知文件类型

如果文件扩展名不在参考中：

1. 询问用户关于文件格式
2. 检查是否为供应商特定变体
3. 尝试基于文件结构进行通用分析（文本 vs 二进制）
4. 提供通用建议

### 大文件

对于非常大的文件：

1. 使用采样策略（前N条记录）
2. 使用内存映射访问（对于HDF5、NPY）
3. 分块处理（对于CSV、FASTQ）
4. 提供基于样本的估计

## 脚本使用

`scripts/eda_analyzer.py` 可以直接使用：

```bash
# 基本用法
python scripts/eda_analyzer.py data.csv

# 指定输出文件
python scripts/eda_analyzer.py data.csv output_report.md

# 脚本将：
# 1. 自动检测文件类型
# 2. 加载格式参考
# 3. 执行适当分析
# 4. 生成markdown报告
```

脚本支持许多常见格式的自动分析，但在对话中执行自定义分析提供更多灵活性和特定领域的见解。

## 高级用法

### 多文件分析

当分析多个相关文件时：
1. 对每个文件执行单独的EDA
2. 创建汇总比较报告
3. 识别关系和依赖
4. 建议集成策略

### 质量控制

对于数据质量评估：
1. 检查格式合规性
2. 验证元数据一致性
3. 评估完整性
4. 识别异常值和异常
5. 与预期范围/分布进行比较

### 预处理建议

根据数据特征，建议：
1. 归一化策略
2. 缺失值插补
3. 异常值处理
4. 批次校正
5. 格式转换

## 资源

### scripts/
- `eda_analyzer.py`：可直接运行或导入的全面分析脚本

### references/
- `chemistry_molecular_formats.md`：60多种化学/分子文件格式
- `bioinformatics_genomics_formats.md`：50多种生物信息学格式
- `microscopy_imaging_formats.md`：45多种成像格式
- `spectroscopy_analytical_formats.md`：35多种光谱学格式
- `proteomics_metabolomics_formats.md`：30多种组学格式
- `general_scientific_formats.md`：30多种通用格式

### assets/
- `report_template.md`：用于EDA报告的全面markdown模板
