# TileDB-VCF

## 概述

TileDB-VCF 是一个高性能的 C++ 库，具有 Python 和 CLI 接口，用于高效存储和检索基因组变异调用数据。基于 TileDB 的稀疏数组技术，它支持可扩展的 VCF/BCF 文件摄取、无需昂贵的合并操作即可增量添加样本，以及高效地并行查询本地或云中存储的变异数据。

## 何时使用此技能

当您需要以下功能时，应使用此技能：
- 学习 TileDB-VCF 概念和工作流程
- 原型设计基因组分析和管道
- 处理小到中等规模的数据集（< 1000 个样本）
- 需要增量添加新样本到现有数据集中
- 需要高效查询多个样本的特定基因组区域
- 处理云存储的变异数据（S3、Azure、GCS）
- 需要导出大型 VCF 数据集的子集
- 构建队列研究的变异数据库
- 教育项目和方法开发
- 变异数据操作对性能要求严格

## 快速入门

### 安装

**首选方法：Conda/Mamba**
```bash
# 如果您使用的是 M1 Mac，请输入以下两行
CONDA_SUBDIR=osx-64
conda config --env --set subdir osx-64

# 创建 conda 环境
conda create -n tiledb-vcf "python<3.10"
conda activate tiledb-vcf

# Mamba 是 conda 更快、更可靠的替代品
conda install -c conda-forge mamba

# 安装 TileDB-Py 和 TileDB-VCF，与其他有用库保持一致
mamba install -y -c conda-forge -c bioconda -c tiledb tiledb-py tiledbvcf-py pandas pyarrow numpy
```

**替代方法：Docker 镜像**
```bash
docker pull tiledb/tiledbvcf-py     # Python 接口
docker pull tiledb/tiledbvcf-cli    # 命令行接口
```

### 基本示例

**创建并填充数据集：**
```python
import tiledbvcf

# 创建新数据集
ds = tiledbvcf.Dataset(uri="my_dataset", mode="w",
                      cfg=tiledbvcf.ReadConfig(memory_budget=1024))

# 摄取 VCF 文件（必须是单样本且带索引）
# 要求：
# - VCF 必须是单样本（不能是多样本）
# - 必须有索引：.csi（bcftools）或 .tbi（tabix）
ds.ingest_samples(["sample1.vcf.gz", "sample2.vcf.gz"])
```

**查询变异数据：**
```python
# 以读取模式打开现有数据集
ds = tiledbvcf.Dataset(uri="my_dataset", mode="r")

# 查询特定区域和样本
df = ds.read(
    attrs=["sample_name", "pos_start", "pos_end", "alleles", "fmt_GT"],
    regions=["chr1:1000000-2000000", "chr2:500000-1500000"],
    samples=["sample1", "sample2", "sample3"]
)
print(df.head())
```

**导出到 VCF：**
```python
import os

# 导出两个 VCF 样本
ds.export(
    regions=["chr21:8220186-8405573"],
    samples=["HG00101", "HG00097"],
    output_format="v",
    output_dir=os.path.expanduser("~"),
)
```

## 核心功能

### 1. 数据集创建和摄取

创建 TileDB-VCF 数据集，并从多个 VCF/BCF 文件中增量摄取变异数据。这适用于构建人群基因组数据库和队列研究。

**要求：**
- **仅限单样本 VCF**：不支持多样本 VCF
- **需要索引文件**：VCF/BCF 文件必须有索引（.csi 或 .tbi）

**常见操作：**
- 使用优化的数组模式创建新数据集
- 并行摄取单个或多个 VCF/BCF 文件
- 增量添加新样本，无需重新处理现有数据
- 配置内存使用和压缩设置
- 处理各种 VCF 格式和 INFO/FORMAT 字段
- 恢复中断的摄取过程
- 在摄取过程中验证数据完整性


### 2. 高效查询和过滤

跨基因组区域、样本和变异属性进行高性能查询。这适用于关联研究、变异发现和人群分析。

**常见操作：**
- 查询单个或多个特定基因组区域
- 按样本名称或样本组过滤
- 提取特定变异属性（位置、等位基因、基因型、质量）
- 高效访问 INFO 和 FORMAT 字段
- 组合空间和属性过滤
- 流式传输大型查询结果
- 跨样本或区域执行聚合


### 3. 数据导出和互操作性

将数据导出为各种格式，用于下游分析或与其他基因组工具集成。这适用于共享数据集、创建分析子集或为其他管道提供输入。

**常见操作：**
- 导出标准 VCF/BCF 格式
- 生成带有选定字段的 TSV 文件
- 创建特定样本/区域的子集
- 维护数据溯源和元数据
- 无损数据导出，保留所有注释
- 压缩输出格式
- 大型数据集的流式导出


### 4. 人群基因组工作流程

TileDB-VCF 在需要高效访问许多样本和基因组区域的 大规模人群基因组分析 中表现优异。

**常见工作流程：**
- 全基因组关联研究（GWAS）数据准备
- 罕见变异负担测试
- 人群分层分析
- 跨人群等位基因频率计算
- 大型队列的质量控制
- 变异注释和过滤
- 跨人群比较分析


## 关键概念

### 数组模式和数据模型

**TileDB-VCF 数据模型：**
- 变异存储为以基因组坐标为维度的稀疏数组
- 样本存储为属性，允许高效的样本特定查询
- INFO 和 FORMAT 字段保留原始数据类型
- 自动压缩和分块，以优化存储

**模式配置：**
```python
# 具有特定瓦片范围的定制模式
config = tiledbvcf.ReadConfig(
    memory_budget=2048,  # MB
    region_partition=(0, 3095677412),  # 全基因组
    sample_partition=(0, 10000)  # 最多 10k 样本
)
```

### 坐标系统和区域

**关键：** TileDB-VCF 使用 **1-based 基因组坐标**，遵循 VCF 标准：
- 位置是 1-based（第一个碱基是位置 1）
- 范围两端都包含在内
- 区域 "chr1:1000-2000" 包括位置 1000-2000（共 1001 个碱基）

**区域指定格式：**
```python
# 单个区域
regions = ["chr1:1000000-2000000"]

# 多个区域
regions = ["chr1:1000000-2000000", "chr2:500000-1500000"]

# 整个染色体
regions = ["chr1"]

# BED 风格（0-based，内部转换为半开区间）
regions = ["chr1:999999-2000000"]  # 等价于 1-based chr1:1000000-2000000
```

### 内存管理

**性能考虑：**
1. **根据可用系统内存设置适当的内存预算**
2. **对于非常大的结果集使用流式查询**
3. **分区大型摄取以避免内存耗尽**
4. **配置瓦片缓存以重复访问区域**
5. **使用并行摄取处理多个文件**
6. **通过组合附近区域优化区域查询**


### 云存储集成

TileDB-VCF 与云存储无缝协作：
```python
# S3 数据集
ds = tiledbvcf.Dataset(uri="s3://bucket/dataset", mode="r")

# Azure Blob 存储
ds = tiledbvcf.Dataset(uri="azure://container/dataset", mode="r")

# Google Cloud 存储
ds = tiledbvcf.Dataset(uri="gcs://bucket/dataset", mode="r")
```

## 常见陷阱

1. **摄取过程中内存耗尽**：使用适当的内存预算和批量处理大型 VCF 文件
2. **低效的区域查询**：组合附近的区域而不是多个单独查询
3. **缺少样本名称**：确保 VCF 头中的样本名称与查询样本规范匹配
4. **坐标系统混淆**：记住 TileDB-VCF 使用 1-based 坐标，与 VCF 标准一致
5. **大型结果集**：使用流式传输或分页处理返回数百万个变异的查询
6. **云权限**：确保云存储访问的适当认证
7. **并发访问**：多个写入者对同一数据集可能导致损坏——使用适当的锁定


## CLI 使用

TileDB-VCF 提供命令行接口，具有以下子命令：

**可用子命令：**
- `create` - 创建空的 TileDB-VCF 数据集
- `store` - 将样本摄取到 TileDB-VCF 数据集
- `export` - 从 TileDB-VCF 数据集导出数据
- `list` - 列出 TileDB-VCF 数据集中所有样本名称
- `stat` - 打印 TileDB-VCF 数据集的高级统计信息
- `utils` - 用于处理 TileDB-VCF 数据集的工具
- `version` - 打印版本信息并退出

```bash
# 创建空数据集
tiledbvcf create --uri my_dataset

# 摄取样本（需要单样本 VCF 且带索引）
tiledbvcf store --uri my_dataset --samples sample1.vcf.gz,sample2.vcf.gz

# 导出数据
tiledbvcf export --uri my_dataset \
  --regions "chr1:1000000-2000000" \
  --sample-names "sample1,sample2"

# 列出所有样本
tiledbvcf list --uri my_dataset

# 显示数据集统计信息
tiledbvcf stat --uri my_dataset
```

## 高级功能

### 等位基因频率分析
```python
# 计算等位基因频率
af_df = tiledbvcf.read_allele_frequency(
    uri="my_dataset",
    regions=["chr1:1000000-2000000"],
    samples=["sample1", "sample2", "sample3"]
)
```

### 样本质量控制
```python
# 执行样本 QC
qc_results = tiledbvcf.sample_qc(
    uri="my_dataset",
    samples=["sample1", "sample2"]
)
```

### 自定义配置
```python
# 高级配置
config = tiledbvcf.ReadConfig(
    memory_budget=4096,
    tiledb_config={
        "sm.tile_cache_size": "1000000000",
        "vfs.s3.region": "us-east-1"
    }
)
```


## 资源

## 获取帮助

### 开源 TileDB-VCF 资源

**开源文档：**
- TileDB Academy: https://cloud.tiledb.com/academy/
- 人群基因组指南: https://cloud.tiledb.com/academy/structure/life-sciences/population-genomics/
- TileDB-VCF GitHub: https://github.com/TileDB-Inc/TileDB-VCF

### TileDB-Cloud 资源

**用于大规模/生产基因组学：**
- TileDB-Cloud 平台: https://cloud.tiledb.com
- TileDB Academy（所有文档）: https://cloud.tiledb.com/academy/

**入门指南：**
- 免费账户注册: https://cloud.tiledb.com
- 联系: sales@tiledb.com（企业需求）

## 扩展到 TileDB-Cloud

当您的基因组工作负载超出单节点处理能力时，TileDB-Cloud 提供企业级扩展能力，用于生产基因组学管道。

**注意**：本节基于可用文档涵盖 TileDB-Cloud 功能。有关完整的 API 详细信息和当前功能，请参阅官方 TileDB-Cloud 文档和 API 参考。

### 设置 TileDB-Cloud

**1. 创建账户和获取 API 令牌**
```bash
# 在 https://cloud.tiledb.com 注册
# 在账户设置中生成 API 令牌
```

**2. 安装 TileDB-Cloud Python 客户端**
```bash
# 基础安装
uv pip install tiledb-cloud

# 带有基因组学特定功能的安装
uv pip install tiledb-cloud[life-sciences]
```

**3. 配置认证**
```bash
# 使用 API 令牌设置环境变量
export TILEDB_REST_TOKEN="your_api_token"
```

```python
import tiledb.cloud

# 通过 TILEDB_REST_TOKEN 自动认证
# 无需在代码中显式登录
```

### 从开源迁移到 TileDB-Cloud

**大规模摄取**
```python
# TileDB-Cloud：分布式 VCF 摄取
import tiledb.cloud.vcf

# 使用专门的 VCF 摄取模块
# 注意：确切 API 需要查阅 TileDB-Cloud 文档
# 这代表可用功能的结构
tiledb.cloud.vcf.ingestion.ingest_vcf_dataset(
    source="s3://my-bucket/vcf-files/",
    output="tiledb://my-namespace/large-dataset",
    namespace="my-namespace",
    acn="my-s3-credentials",
    ingest_resources={"cpu": "16", "memory": "64Gi"}
)
```

**分布式查询处理**
```python
# TileDB-Cloud：跨分布式存储的 VCF 查询
import tiledb.cloud.vcf
import tiledbvcf

# 定义数据集 URI
dataset_uri = "tiledb://TileDB-Inc/gvcf-1kg-dragen-v376"

# 从数据集中获取所有样本
ds = tiledbvcf.Dataset(dataset_uri, tiledb_config=cfg)
samples = ds.samples()

# 定义要查询的属性和范围
attrs = ["sample_name", "fmt_GT", "fmt_AD", "fmt_DP"]
regions = ["chr13:32396898-32397044", "chr13:32398162-32400268"]

# 执行分布式读取
df = tiledb.cloud.vcf.read(
    dataset_uri=dataset_uri,
    regions=regions,
    samples=samples,
    attrs=attrs,
    namespace="my-namespace",  # 指定要计费哪个账户
)
df.to_pandas()
```

### 企业功能

**数据共享和协作**
```python
# TileDB-Cloud 通过命名空间权限和组管理提供企业数据共享功能

# 通过 TileDB-Cloud URI 访问共享数据集
dataset_uri = "tiledb://shared-namespace/population-study"

# 通过共享笔记本和计算资源协作
# （具体 API 需要查阅 TileDB-Cloud 文档）
```

**成本优化**
- **无服务器计算**：仅按实际计算时间付费
- **自动扩展**：根据工作负载自动扩展/缩减
- **竞价实例**：使用成本优化的计算进行批处理作业
- **数据分层**：自动热/冷存储管理

**安全和合规**
- **端到端加密**：数据在传输和静止时都加密
- **访问控制**：细粒度权限和审计日志
- **HIPAA/SOC2 合规**：企业安全标准
- **VPC 支持**：部署在私有云环境

### 迁移检查清单

✅ **如果满足以下条件，请迁移到 TileDB-Cloud：**
- [ ] 数据集 > 1000 个样本
- [ ] 需要处理 > 100GB 的 VCF 数据
- [ ] 需要分布式计算
- [ ] 多个团队成员需要访问
- [ ] 需要企业安全/合规
- [ ] 希望使用成本优化的无服务器计算
- [ ] 需要 24/7 生产运行


### 开始使用 TileDB-Cloud

1. **免费试用**：TileDB-Cloud 提供免费层用于评估
2. **迁移支持**：TileDB 团队提供迁移协助
3. **培训**：访问基因组学特定教程和示例
4. **专业服务**：定制部署和优化

**下一步：**
- 访问 https://cloud.tiledb.com 创建账户
- 查阅 https://cloud.tiledb.com/academy/ 文档
- 联系 sales@tiledb.com（企业需求）
