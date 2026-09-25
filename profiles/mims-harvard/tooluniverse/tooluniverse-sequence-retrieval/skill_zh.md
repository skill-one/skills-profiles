# 生物序列检索

检索DNA、RNA和蛋白质序列，并进行正确的歧义消除和跨数据库处理。

**重要提示**：工具调用中始终使用英文术语。仅在必要时尝试原始语言术语作为后备方案。使用用户的语言进行回复。

**查找而非猜测**：不要假设登录号或序列版本。始终从NCBI或ENA检索并验证。

## 领域推理

序列质量层次：RefSeq（NM_/NP_ = 经过整理）> RefSeq预测（XM_/XP_）> GenBank（提交）。优先选择人类规范异构体的MANE Select转录本。检查版本号——注释随着版本更新而改进。

## 工作流程

```
阶段0：澄清（如有必要）→ 阶段1：基因/生物体歧义消除 → 阶段2：搜索和检索 → 阶段3：报告
```

---

## 阶段0：澄清（当需要时）

仅在以下情况下询问：基因存在于多个生物体中、序列类型不明确或菌株很重要。
跳过：特定登录号、清晰的生物体+基因组合、包含生物体的完整基因组请求。

---

## 阶段1：基因/生物体歧义消除

### 登录号类型决策树

| 前缀 | 类型 | 与...一起使用 |
|------|------|----------|
| NC_/NM_/NR_/NP_/XM_ | RefSeq | 仅限NCBI |
| U*/M*/K*/X*/CP*/NZ_ | GenBank | NCBI或ENA |
| EMBL格式 | EMBL | 优先ENA |

**关键**：不要尝试使用ENA工具检索RefSeq登录号——它们会返回404。

### 身份检查清单
- 确认生物体（科学名称）
- 确定基因符号/名称
- 确定序列类型（基因组/mRNA/蛋白质）
- 确定用于工具选择的登录号前缀

---

## 阶段2：数据检索（内部）

安静地检索。不要描述搜索过程。

```python
# 搜索NCBI核苷酸
result = tu.tools.NCBI_search_nucleotide(
    operation="search", organism=organism, gene=gene,
    strain=strain, keywords=keywords, seq_type=seq_type, limit=10
)

# 从UID获取登录号
accessions = tu.tools.NCBI_fetch_accessions(operation="fetch_accession", uids=result["data"]["uids"])

# 检索序列（FASTA或GenBank格式）
sequence = tu.tools.NCBI_get_sequence(operation="fetch_sequence", accession=accession, format="fasta")

# ENA替代方案（仅限非RefSeq登录号）
entry = tu.tools.ena_get_entry(accession=accession)
fasta = tu.tools.ena_get_sequence_fasta(accession=accession)
```

### 备用链

| 主要 | 备用 | 备注 |
|-------|------|-------|
| NCBI_get_sequence | ENA（如果GenBank格式） | NCBI不可用 |
| ena_get_entry | NCBI_get_sequence | ENA没有RefSeq |
| NCBI_search_nucleotide | 尝试更广泛的关键词 | 无结果 |

---

## 阶段3：报告序列概况

以**序列概况报告**的形式呈现。隐藏搜索过程。包括：

1. **搜索摘要**：查询、数据库、结果数量
2. **主要序列**：登录号、类型（RefSeq/GenBank）、生物体、菌株、长度、分子、拓扑结构、整理级别
3. **序列预览**：FASTA的前几行（截断）
4. **注释摘要**：CDS/tRNA/rRNA/调控特征数量（来自GenBank格式）
5. **替代序列**：按相关性和整理级别排序，并具有ENA兼容性
6. **跨数据库引用**：RefSeq、GenBank、ENA/EMBL、BioProject、BioSample
7. **下载选项**：FASTA（用于BLAST/比对）、GenBank（用于注释）

### 整理级别层次

| 层级 | 前缀 | 描述 |
|------|------|-------------|
| RefSeq参考（最佳） | NC_, NM_, NP_ | NCBI整理，黄金标准 |
| RefSeq预测 | XM_, XP_, XR_ | 计算预测 |
| GenBank验证 | 各种 | 提交，部分整理 |
| GenBank直接 | 各种 | 直接提交 |
| 第三方 | TPA_ | 第三方注释 |

---

## 推理框架

**序列质量**：优先选择RefSeq而不是GenBank。检查版本号。定义中包含"预测"的序列未经实验验证。

**登录号指南**：RefSeq = 仅限NCBI。GenBank = 在ENA/EMBL中镜像。默认情况下，为人类/模式生物选择RefSeq mRNA（NM_）；为微生物查询提供最完整的基因组组装。

**跨数据库协调**：同一序列可能具有不同的登录号（例如，GenBank U00096 = RefSeq NC_000913 对于大肠杆菌K-12）。当可用时，始终报告两者。GenBank/RefSeq之间的差异通常表明RefSeq整理纠正了提交错误。

### 综合问题
1. 可用的最高质量登录号是什么？
2. 其他数据库中是否有替代登录号？
3. 注释完整性如何？
4. 序列是否来自预期的生物体/菌株？
5. 哪种下载格式适合用户的下游分析？

---

## 错误处理

| 错误 | 响应 |
|-------|----------|
| "未提供搜索标准" | 添加生物体、基因或关键词 |
| "ENA 404错误" | 可能是RefSeq——仅使用NCBI |
| "未找到结果" | 放宽搜索范围，检查拼写，尝试同义词 |
| "序列太大" | 注明大小，提供下载链接 |

---

## 工具参考

**NCBI工具**：`NCBI_search_nucleotide`（搜索）、`NCBI_fetch_accessions`（UID→登录号）、`NCBI_get_sequence`（检索）
**ENA工具（仅限GenBank/EMBL）**：`ena_get_entry`（元数据）、`ena_get_sequence_fasta`（FASTA）、`ena_get_entry_summary`（摘要）

---

## 搜索参数参考

**NCBI_search_nucleotide**：`operation`="search", `organism`（科学名称）、`gene`（符号）、`strain`, `keywords`, `seq_type`（complete_genome/mrna/refseq）、`limit`

**NCBI_get_sequence**：`operation`="fetch_sequence", `accession`, `format`（fasta/genbank）
