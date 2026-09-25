# nf-core Pipeline 部署

在本地或公共测序数据上运行 nf-core 生物信息学管道。

**目标用户：** 无需专业生物信息学培训的实验室科学家和研究人员，他们需要运行大规模组学分析——差异表达、变异检测或染色质可及性分析。

## 工作流清单

```
- [ ] 第 0 步：获取数据（如果来自 GEO/SRA）
- [ ] 第 1 步：环境检查（必须通过）
- [ ] 第 2 步：选择管道（与用户确认）
- [ ] 第 3 步：运行测试配置文件（必须通过）
- [ ] 第 4 步：创建样本表
- [ ] 第 5 步：配置并运行（与用户确认基因组）
- [ ] 第 6 步：验证输出
```

---

## 第 0 步：获取数据（仅限 GEO/SRA）

**如果用户有本地 FASTQ 文件，可以跳过此步骤。**

对于公共数据集，首先从 GEO/SRA 获取。有关完整工作流的详细信息，请参阅 [references/geo-sra-acquisition.md](references/geo-sra-acquisition.md)。

**快速启动：**

```bash
# 1. 获取研究信息
python scripts/sra_geo_fetch.py info GSE110004

# 2. 下载（交互模式）
python scripts/sra_geo_fetch.py download GSE110004 -o ./fastq -i

# 3. 生成样本表
python scripts/sra_geo_fetch.py samplesheet GSE110004 --fastq-dir ./fastq -o samplesheet.csv
```

**决策点：** 获取研究信息后，与用户确认：
- 如果有多个数据类型，下载哪些样本子集
- 建议的基因组和管道

然后继续到第 1 步。

---

## 第 1 步：环境检查

**首先运行。如果没有通过环境检查，管道将失败。**

```bash
python scripts/check_environment.py
```

所有关键检查必须通过。如果有任何失败，请提供修复说明：

### Docker 问题

| 问题 | 修复 |
|---------|-----|
| 未安装 | 从 https://docs.docker.com/get-docker/ 安装 |
| 权限被拒绝 | `sudo usermod -aG docker $USER` 然后重新登录 |
| 守护进程未运行 | `sudo systemctl start docker` |

### Nextflow 问题

| 问题 | 修复 |
|---------|-----|
| 未安装 | `curl -s https://get.nextflow.io \| bash && mv nextflow ~/bin/` |
| 版本 < 23.04 | `nextflow self-update` |

### Java 问题

| 问题 | 修复 |
|---------|-----|
| 未安装 / < 11 | `sudo apt install openjdk-11-jdk` |

**所有检查通过前不要继续。** 对于 HPC/Singularity，请参阅 [references/troubleshooting.md](references/troubleshooting.md)。

---

## 第 2 步：选择管道

**决策点：** 在继续之前与用户确认。

| 数据类型 | 管道 | 版本 | 目标 |
|-----------|----------|---------|------|
| RNA-seq | `rnaseq` | 3.22.2 | 基因表达 |
| WGS/WES | `sarek` | 3.7.1 | 变异检测 |
| ATAC-seq | `atacseq` | 2.1.2 | 染色质可及性分析 |

从数据自动检测：
```bash
python scripts/detect_data_type.py /path/to/data
```

对于管道特定详细信息：
- [references/pipelines/rnaseq.md](references/pipelines/rnaseq.md)
- [references/pipelines/sarek.md](references/pipelines/sarek.md)
- [references/pipelines/atacseq.md](references/pipelines/atacseq.md)

---

## 第 3 步：运行测试配置文件

**使用小数据验证环境。在处理真实数据前必须通过。**

```bash
nextflow run nf-core/<pipeline> -r <version> -profile test,docker --outdir test_output
```

| 管道 | 命令 |
|----------|---------|
| rnaseq | `nextflow run nf-core/rnaseq -r 3.22.2 -profile test,docker --outdir test_rnaseq` |
| sarek | `nextflow run nf-core/sarek -r 3.7.1 -profile test,docker --outdir test_sarek` |
| atacseq | `nextflow run nf-core/atacseq -r 2.1.2 -profile test,docker --outdir test_atacseq` |

验证：
```bash
ls test_output/multiqc/multiqc_report.html
grep "Pipeline completed successfully" .nextflow.log
```

如果测试失败，请参阅 [references/troubleshooting.md](references/troubleshooting.md)。

---

## 第 4 步：创建样本表

### 自动生成

```bash
python scripts/generate_samplesheet.py /path/to/data <pipeline> -o samplesheet.csv
```

脚本：
- 发现 FASTQ/BAM/CRAM 文件
- 配对 R1/R2 读数
- 推断样本元数据
- 在写入前验证

**对于 sarek：** 如果未自动检测肿瘤/正常状态，脚本会提示用户输入。

### 验证现有样本表

```bash
python scripts/generate_samplesheet.py --validate samplesheet.csv <pipeline>
```

### 样本表格式

**rnaseq:**
```csv
sample,fastq_1,fastq_2,strandedness
SAMPLE1,/abs/path/R1.fq.gz,/abs/path/R2.fq.gz,auto
```

**sarek:**
```csv
patient,sample,lane,fastq_1,fastq_2,status
patient1,tumor,L001,/abs/path/tumor_R1.fq.gz,/abs/path/tumor_R2.fq.gz,1
patient1,normal,L001,/abs/path/normal_R1.fq.gz,/abs/path/normal_R2.fq.gz,0
```

**atacseq:**
```csv
sample,fastq_1,fastq_2,replicate
CONTROL,/abs/path/ctrl_R1.fq.gz,/abs/path/ctrl_R2.fq.gz,1
```

---

## 第 5 步：配置并运行

### 5a. 检查基因组可用性

```bash
python scripts/manage_genomes.py check <genome>
# 如果未安装：
python scripts/manage_genomes.py download <genome>
```

常见基因组：GRCh38（人类）、GRCh37（遗留）、GRCm39（小鼠）、R64-1-1（酵母）、BDGP6（果蝇）

### 5b. 决策点

**决策点：** 与用户确认：

1. **基因组：** 使用哪个参考基因组
2. **管道特定选项：**
   - **rnaseq：** 对齐器（推荐 star_salmon，低内存时使用 hisat2）
   - **sarek：** 工具（germline 使用 haplotypecaller，somatic 使用 mutect2）
   - **atacseq：** 读长（50、75、100 或 150）

### 5c. 运行管道

```bash
nextflow run nf-core/<pipeline> \
    -r <version> \
    -profile docker \
    --input samplesheet.csv \
    --outdir results \
    --genome <genome> \
    -resume
```

**关键标志：**
- `-r`：固定版本
- `-profile docker`：使用 Docker（或 `singularity` 用于 HPC）
- `--genome`：iGenomes 键
- `-resume`：从检查点继续

**资源限制（如果需要）：**
```bash
--max_cpus 8 --max_memory '32.GB' --max_time '24.h'
```

---

## 第 6 步：验证输出

### 检查完成情况

```bash
ls results/multiqc/multiqc_report.html
grep "Pipeline completed successfully" .nextflow.log
```

### 各管道的关键输出

**rnaseq:**
- `results/star_salmon/salmon.merged.gene_counts.tsv` - 基因计数
- `results/star_salmon/salmon.merged.gene_tpm.tsv` - TPM 值

**sarek:**
- `results/variant_calling/*/` - VCF 文件
- `results/preprocessing/recalibrated/` - BAM 文件

**atacseq:**
- `results/macs2/narrowPeak/` - 峰调用
- `results/bwa/mergedLibrary/bigwig/` - 覆盖图

---

## 快速参考

对于常见退出代码和修复方法，请参阅 [references/troubleshooting.md](references/troubleshooting.md)。

### 继续失败的运行

```bash
nextflow run nf-core/<pipeline> -resume
```

---

## 参考文献

- [references/geo-sra-acquisition.md](references/geo-sra-acquisition.md) - 下载公共 GEO/SRA 数据
- [references/troubleshooting.md](references/troubleshooting.md) - 常见问题和修复方法
- [references/installation.md](references/installation.md) - 环境设置
- [references/pipelines/rnaseq.md](references/pipelines/rnaseq.md) - RNA-seq 管道详细信息
- [references/pipelines/sarek.md](references/pipelines/sarek.md) - 变异检测详细信息
- [references/pipelines/atacseq.md](references/pipelines/atacseq.md) - ATAC-seq 详细信息

---

## 免责声明

此功能作为原型示例，展示了如何将 nf-core 生物信息学管道集成到 Claude Code 中以实现自动化分析工作流。当前实现支持三个管道（rnaseq、sarek 和 atacseq），为社区扩展对 nf-core 所有管道的支持奠定了基础。

它旨在用于教育和研究目的，未经针对特定用例的适当验证，不应被视为生产就绪。用户有责任确保其计算环境满足管道要求，并验证分析结果。

Anthropic 不保证生物信息学输出的准确性，用户应遵循验证计算分析的标准做法。此集成并非正式获得或与 nf-core 社区关联。

## 署名

发布结果时，请引用相应的管道。引用可在每个 nf-core 仓库的 CITATIONS.md 文件中找到（例如，https://github.com/nf-core/rnaseq/blob/3.22.2/CITATIONS.md）。

## 许可证

- **nf-core 管道：** MIT 许可证（https://nf-co.re/about）
- **Nextflow：** Apache 许可证，版本 2.0（https://www.nextflow.io/about-us.html）
- **NCBI SRA 工具包：** 公共领域（https://github.com/ncbi/sra-tools/blob/master/LICENSE）
