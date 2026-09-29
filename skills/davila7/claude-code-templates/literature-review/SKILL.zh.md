---
name: literature-review
description: 使用多个学术数据库（PubMed、arXiv、bioRxiv、Semantic Scholar等）进行全面的系统性文献综述。这项技能应在进行系统性文献综述、元分析、研究综合或跨生物医学、科学和技术领域的全面文献检索时使用。创建具有专业格式化、包含经过验证引用的markdown文档和PDF文件，支持多种引用格式（APA、Nature、Vancouver等）。
---

# 文献综述

## 概述

遵循严格的学术方法进行系统、全面的文献综述。搜索多个文献数据库，按主题综合研究结果，验证所有引用的准确性，并生成专业输出文档（Markdown 和 PDF 格式）。

此技能与多个科学技能（数据库访问：gget、bioservices、datacommons-client）集成，并提供专门的引用验证、结果聚合和文档生成工具。

## 使用此技能的场景

当您需要：

- 进行系统性文献综述以用于研究或发表
- 跨多个来源综合特定主题的当前知识
- 执行荟萃分析或范围综述
- 撰写研究论文或学位论文的文献综述部分
- 调查研究领域的技术现状
- 确定研究差距和未来方向
- 需要经过验证的引用和专业格式

## 使用科学示意图进行视觉增强

**⚠️ 强制要求：每篇文献综述必须包含至少 1-2 个使用科学示意图技能生成的 AI 图表。**

这不是可选的。没有视觉元素的文献综述是不完整的。在最终确定任何文档之前：

1. 生成至少一个示意图或图表（例如，系统综述的 PRISMA 流程图）
2. 对于全面的综述，最好生成 2-3 个图表（搜索策略流程图、主题综合图、概念框架）

**如何生成图表：**

- 使用 **scientific-schematics** 技能生成 AI 驱动的出版级图表
- 用自然语言描述您想要的图表
- Nano Banana Pro 将自动生成、审查和改进示意图

**如何生成示意图：**

```bash
python scripts/generate_schematic.py "your diagram description" -o figures/output.png
```

AI 将自动：

- 创建具有正确格式的出版级图像
- 通过多次迭代进行审查和改进
- 确保可访问性（对色盲友好、高对比度）
- 将输出保存在 figures/ 目录中

**何时添加示意图：**

- 系统综述的 PRISMA 流程图
- 文献搜索策略流程图
- 主题综合图
- 研究差距可视化地图
- 引用网络图
- 概念框架插图
- 任何从可视化中受益的复杂概念

有关创建示意图的详细指南，请参阅 scientific-schematics 技能文档。

---

## 核心工作流程

文献综述遵循结构化、多阶段的工作流程：

### 第一阶段：规划和范围界定

1. **定义研究问题**：使用 PICO 框架（人群、干预、对照、结果）进行临床/生物医学综述
   - 示例："CRISPR-Cas9 (I) 治疗镰状细胞病 (P) 与标准护理 (C) 相比的有效性是什么？"

2. **确定范围和目标**：
   - 定义清晰、具体的研究问题
   - 确定综述类型（叙述性、系统性、范围性、荟萃分析）
   - 设置边界（时间范围、地理范围、研究类型）

3. **制定搜索策略**：
   - 从研究问题中确定 2-4 个主要概念
   - 列出每个概念的同义词、缩写和相关术语
   - 规划布尔运算符（AND、OR、NOT）以组合术语
   - 选择至少 3 个互补的数据库

4. **设置纳入/排除标准**：
   - 日期范围（例如，过去 10 年：2015-2024）
   - 语言（通常为英语，或指定多语言）
   - 出版类型（同行评审、预印本、综述）
   - 研究设计（随机对照试验、观察性研究、体外实验等）
   - 清晰记录所有标准

### 第二阶段：系统文献检索

1. **多数据库搜索**：

   选择适合领域的数据库：

   **生物医学与生命科学：**
   - 使用 `gget` 技能：`gget search pubmed "search terms"` 用于 PubMed/PMC
   - 使用 `gget` 技能：`gget search biorxiv "search terms"` 用于预印本
   - 使用 `bioservices` 技能用于 ChEMBL、KEGG、UniProt 等

   **通用科学文献：**
   - 通过直接 API 搜索 arXiv（物理学、数学、计算机科学、q-bio 预印本）
   - 通过 API 搜索 Semantic Scholar（2000 万篇论文，跨学科）
   - 使用 Google Scholar 进行全面覆盖（手动或谨慎抓取）

   **专业数据库：**
   - 使用 `gget alphafold` 用于蛋白质结构
   - 使用 `gget cosmic` 用于癌症基因组学
   - 使用 `datacommons-client` 用于人口统计/统计数据
   - 根据领域选择合适的专用数据库

2. **文档搜索参数**：
   ```markdown
   ## 搜索策略

   ### 数据库：PubMed
   - **搜索日期**：2024-10-25
   - **日期范围**：2015-01-01 至 2024-10-25
   - **搜索字符串**：
     ```
     ("CRISPR"[Title] OR "Cas9"[Title])
     AND ("sickle cell"[MeSH] OR "SCD"[Title/Abstract])
     AND 2015:2024[Publication Date]
     ```
   - **结果**：247 篇文章
   ```

   对每个搜索的数据库重复此步骤。

3. **导出和聚合结果**：
   - 从每个数据库以 JSON 格式导出结果
   - 将所有结果合并到一个文件中
   - 使用 `scripts/search_databases.py` 进行后处理：
     ```bash
     python search_databases.py combined_results.json \
       --deduplicate \
       --format markdown \
       --output aggregated_results.md
     ```

### 第三阶段：筛选和选择

1. **去重**：
   ```bash
   python search_databases.py results.json --deduplicate --output unique_results.json
   ```
   - 通过 DOI（主要）或标题（后备）删除重复项
   - 记录删除的重复项数量

2. **标题筛选**：
   - 根据纳入/排除标准审查所有标题
   - 排除明显不相关的研究
   - 记录在此阶段排除的数量

3. **摘要筛选**：
   - 阅读剩余研究的摘要
   - 严格应用纳入/排除标准
   - 记录排除的原因

4. **全文筛选**：
   - 获取剩余研究的全文
   - 根据所有标准进行详细审查
   - 记录排除的具体原因
   - 记录最终纳入的研究数量

5. **创建 PRISMA 流程图**：
   ```
   初始搜索：n = X
   ├─ 去重后：n = Y
   ├─ 标题筛选后：n = Z
   ├─ 摘要筛选后：n = A
   └─ 纳入综述：n = B
   ```

### 第四阶段：数据提取和质量评估

1. **从每个纳入的研究中提取关键数据**：
   - 研究元数据（作者、年份、期刊、DOI）
   - 研究设计和方法
   - 样本量和人群特征
   - 关键发现和结果
   - 作者指出的局限性
   - 资金来源和利益冲突

2. **评估研究质量**：
   - **对于随机对照试验**：使用 Cochrane 偏倚风险评估工具
   - **对于观察性研究**：使用 Newcastle-Ottawa 量表
   - **对于系统综述**：使用 AMSTAR 2
   - 评估每个研究的质量：高、中、低或极低
   - 考虑排除极低质量的研究

3. **按主题组织**：
   - 确定 3-5 个主要主题
   - 按主题分组研究（研究可能出现在多个主题中）
   - 注意模式、共识和争议

### 第五阶段：综合和分析

1. **从模板创建综述文档**：
   ```bash
   cp assets/review_template.md my_literature_review.md
   ```

2. **撰写主题综合**（不是逐个研究的总结）：
   - 按主题或研究问题组织结果部分
   - 在每个主题内综合多个研究的结果
   - 比较和对比不同的方法和结果
   - 确定共识领域和争议点
   - 突出最强证据

   示例结构：
   ```markdown
   #### 3.3.1 主题：CRISPR 递送方法

   多种递送方法已被研究用于治疗性基因编辑。病毒载体（AAV）在 15 项研究中^1-15^ 使用，显示出高转导效率（65-85%），但引发了免疫原性问题^3、7、12^。相比之下，脂质纳米颗粒显示出较低的效率（40-60%），但改善了安全性特征^16-23^。
   ```

3. **批判性分析**：
   - 评估研究的方法学优势和局限性
   - 评估证据的质量和一致性
   - 确定知识差距和方法学差距
   - 注意需要未来研究的领域

4. **撰写讨论**：
   - 在更广泛的背景下解释发现
   - 讨论临床、实际或研究意义
   - 承认综述本身的局限性
   - 如适用，与之前的综述进行比较
   - 提出具体的未来研究方向

### 第六阶段：引用验证

**关键**：所有引用在最终提交前必须验证其准确性。

1. **验证所有 DOI**：
   ```bash
   python scripts/verify_citations.py my_literature_review.md
   ```

   此脚本：
   - 从文档中提取所有 DOI
   - 验证每个 DOI 是否正确解析
   - 从 CrossRef 获取元数据
   - 生成验证报告
   - 输出格式正确的引用

2. **审查验证报告**：
   - 检查任何失败的 DOI
   - 验证作者姓名、标题和出版细节是否匹配
   - 修正原始文档中的任何错误
   - 重新运行验证，直到所有引用通过

3. **一致地格式化引用**：
   - 选择一种引用风格并始终如一地使用（见 `references/citation_styles.md`）
   - 常见风格：APA、Nature、温哥华、芝加哥、IEEE
   - 使用验证脚本输出正确格式化引用
   - 确保文内引用与参考文献列表格式一致

### 第七阶段：文档生成

1. **生成 PDF**：
   ```bash
   python scripts/generate_pdf.py my_literature_review.md \
     --citation-style apa \
     --output my_review.pdf
   ```

   选项：
   - `--citation-style`：apa、nature、chicago、vancouver、ieee
   - `--no-toc`：禁用目录
   - `--no-numbers`：禁用章节编号
   - `--check-deps`：检查是否安装 pandoc/xelatex

2. **审查最终输出**：
   - 检查 PDF 格式和布局
   - 验证所有部分是否存在
   - 确保引用正确显示
   - 检查图表/表格是否正确显示
   - 验证目录是否准确

3. **质量检查清单**：
   - [ ] 使用 verify_citations.py 验证所有 DOI
   - [ ] 引用格式一致
   - [ ] 系统性综述包含 PRISMA 流程图
   - [ ] 完整记录搜索方法
   - [ ] 清晰说明纳入/排除标准
   - [ ] 结果按主题组织（不是逐个研究）
   - [ ] 完成质量评估
   - [ ] 承认局限性
   - [ ] 参考文献完整且准确
   - [ ] PDF 生成无错误

## 数据库特定搜索指南

### PubMed / PubMed Central

通过 `gget` 技能访问：
```bash
# 搜索 PubMed
gget search pubmed "CRISPR 基因编辑" -l 100

# 带有过滤器的搜索
# 使用 PubMed 高级搜索构建器构建复杂查询
# 然后通过 gget 或直接 Entrez API 执行
```

**搜索技巧**：
- 使用 MeSH 术语：`"sickle cell disease"[MeSH]`
- 字段标签：`[Title]`、`[Title/Abstract]`、`[Author]`
- 日期过滤器：`2020:2024[Publication Date]`
- 布尔运算符：AND、OR、NOT
- MeSH 浏览器：https://meshb.nlm.nih.gov/search

### bioRxiv / medRxiv

通过 `gget` 技能访问：
```bash
gget search biorxiv "CRISPR 镰状细胞" -l 50
```

**重要注意事项**：
- 预印本未经同行评审
- 谨慎验证结果
- 检查预印本是否已发表（CrossRef）
- 注意预印本版本和日期

### arXiv

通过直接 API 或 WebFetch 访问：
```python
# 示例搜索类别：
# q-bio.QM（定量方法）
# q-bio.GN（基因组学）
# q-bio.MN（分子网络）
# cs.LG（机器学习）
# stat.ML（机器学习统计）

# 搜索格式：category AND terms
search_query = "cat:q-bio.QM AND ti:\"单细胞测序\""
```

### Semantic Scholar

通过直接 API 访问（需要 API 密钥，或使用免费版本）：
- 2000 万篇论文跨越所有领域
- 优秀的跨学科搜索
- 提供引用图和论文推荐
- 用于查找具有高度影响力的论文

### 专用生物医学数据库

使用适当的技能：
- **ChEMBL**：`bioservices` 技能用于化学生物活性
- **UniProt**：`gget` 或 `bioservices` 技能用于蛋白质信息
- **KEGG**：`bioservices` 技能用于通路和基因
- **COSMIC**：`gget` 技能用于癌症突变
- **AlphaFold**：`gget alphafold` 用于蛋白质结构
- **PDB**：`gget` 或直接 API 用于实验结构

### 引用链

通过引用网络扩展搜索：

1. **前向引用**（引用关键论文的论文）：
   - 使用 Google Scholar "被引用"
   - 使用 Semantic Scholar 或 OpenAlex API
   - 识别建立在经典工作之上的新研究

2. **后向引用**（关键论文的参考文献）：
   - 从纳入的论文中提取参考文献
   - 识别被高度引用的基础工作
   - 找到被多个纳入研究引用的论文

## 引用格式指南

详细的格式指南在 `references/citation_styles.md` 中。快速参考：

### APA（第 7 版）
- 文内引用： (Smith 等人，2023)
- 参考文献格式：Smith, J. D., Johnson, M. L., & Williams, K. R. (2023). 标题. *期刊*，*22*(4)，301-318. https://doi.org/xxx/yyy

### Nature
- 文内引用：上标数字^1、2^
- 参考文献格式：Smith, J. D., Johnson, M. L. & Williams, K. R. 标题. *Nat. Rev. Drug Discov.* **22**，301-318 (2023).

### Vancouver
- 文内引用：上标数字^1、2^
- 参考文献格式：Smith JD, Johnson ML, Williams KR. 标题. Nat Rev Drug Discov. 2023;22(4):301-18.

**始终使用 verify_citations.py 验证引用**，在最终确定之前。

## 最佳实践

### 搜索策略
1. **使用多个数据库**（至少 3 个）：确保全面覆盖
2. **包含预印本服务器**：捕获最新的未发表结果
3. **记录所有内容**：搜索字符串、日期、结果数量，以确保可重复性
4. **测试和改进**：运行试点搜索，审查结果，调整搜索术语

### 筛选和选择
1. **使用清晰的标准**：在筛选前记录纳入/排除标准
2. **系统筛选**：标题 → 摘要 → 全文
3. **记录排除**：记录排除研究的原因
4. **考虑双重筛选**：对于系统综述，有两个独立审查者进行筛选

### 综合
1. **按主题组织**：按主题分组，而不是按单个研究
2. **跨研究综合**：比较、对比、识别模式
3. **保持批判性**：评估证据的质量和一致性
4. **识别差距**：注意缺失或研究不足的领域

### 质量和可重复性
1. **评估研究质量**：使用适当的质量评估工具
2. **验证所有引用**：运行 verify_citations.py 脚本
3. **记录方法**：提供足够的细节，以便他人可以重复
4. **遵循指南**：使用 PRISMA 进行系统综述

### 写作
1. **保持客观**：公平呈现证据，承认局限性
2. **保持系统性**：遵循结构化模板
3. **保持具体**：包括数字、统计数据、效应量，如果可用
4. **保持清晰**：使用清晰的标题、逻辑流程、主题组织

## 避免常见错误

1. **单一数据库检索**：遗漏相关文献；始终使用多个数据库检索  
2. **无检索记录**：导致综述无法复现；记录所有检索过程  
3. **逐项研究总结**：缺乏整合；按主题组织  
4. **未验证引用**：易致错误；始终运行 verify_citations.py  
5. **检索范围过宽**：产生大量无关结果；使用具体术语精炼  
6. **检索范围过窄**：遗漏相关文献；包含同义词和相关术语  
7. **忽略预印本**：遗漏最新发现；包含 bioRxiv、medRxiv、arXiv  
8. **无质量评估**：同等对待所有证据；评估并报告质量  
9. **发表偏倚**：仅发表阳性结果；注明潜在偏倚  
10. **检索过时**：领域发展迅速；明确标注检索日期  

## 示例工作流程  

生物医学文献综述完整工作流程：  

```bash
# 1. 从模板创建综述文档
cp assets/review_template.md crispr_sickle_cell_review.md

# 2. 使用适当技能检索多个数据库
# - 使用 gget 技能检索 PubMed、bioRxiv
# - 使用直接 API 访问检索 arXiv、Semantic Scholar
# - 以 JSON 格式导出结果

# 3. 汇总和处理结果
python scripts/search_databases.py combined_results.json \
  --去重 \
  --按引用排序 \
  --起始年份 2015 \
  --结束年份 2024 \
  --格式 markdown \
  --输出 search_results.md \
  --摘要

# 4. 筛选结果并提取数据
# - 手动筛选标题、摘要、全文
# - 提取关键数据至综述文档
# - 按主题组织

# 5. 按模板结构撰写综述
# - 具有明确目标的引言部分
# - 详细的方法学章节
# - 按主题组织的正文
# - 批判性讨论
# - 清晰的结论

# 6. 验证所有引用
python scripts/verify_citations.py crispr_sickle_cell_review.md

# 查看引用报告
cat crispr_sickle_cell_review_citation_report.json

# 修复失败的引用并重新验证
python scripts/verify_citations.py crispr_sickle_cell_review.md

# 7. 生成专业 PDF
python scripts/generate_pdf.py crispr_sickle_cell_review.md \
  --引用格式 nature \
  --输出 crispr_sickle_cell_review.pdf

# 8. 审核最终 PDF 和 markdown 输出
```

## 与其他技能的集成  

该技能可与其他科学技能无缝协作：  

### 数据库访问技能  
- **gget**：PubMed、bioRxiv、COSMIC、AlphaFold、Ensembl、UniProt  
- **bioservices**：ChEMBL、KEGG、Reactome、UniProt、PubChem  
- **datacommons-client**：人口统计、经济、健康统计  

### 分析技能  
- **pydeseq2**：RNA-seq 差异表达（用于方法学章节）  
- **scanpy**：单细胞分析（用于方法学章节）  
- **anndata**：单细胞数据（用于方法学章节）  
- **biopython**：序列分析（用于背景章节）  

### 可视化技能  
- **matplotlib**：为综述生成图表和绘图  
- **seaborn**：统计可视化  

### 撰写技能  
- **brand-guidelines**：将机构品牌应用于 PDF  
- **internal-comms**：为不同受众调整综述  

## 资源  

### 内嵌资源  

**脚本：**  
- `scripts/verify_citations.py`：验证 DOI 并生成格式化引用  
- `scripts/generate_pdf.py`：将 markdown 转换为专业 PDF  
- `scripts/search_databases.py`：处理、去重和格式化检索结果  

**参考文献：**  
- `references/citation_styles.md`：详细引用格式指南（APA、Nature、温哥华、芝加哥、IEEE）  
- `references/database_strategies.md`：综合数据库检索策略  

**资源文件：**  
- `assets/review_template.md`：完整文献综述模板（含所有章节）  

### 外部资源  

**指南：**  
- PRISMA（系统综述）：http://www.prisma-statement.org/  
- Cochrane 手册：https://training.cochrane.org/handbook  
- AMSTAR 2（综述质量）：https://amstar.ca/  

**工具：**  
- MeSH 浏览器：https://meshb.nlm.nih.gov/search  
- PubMed 高级检索：https://pubmed.ncbi.nlm.nih.gov/advanced/  
- 布尔检索指南：https://www.ncbi.nlm.nih.gov/books/NBK3827/  

**引用格式：**  
- APA 格式：https://apastyle.apa.org/  
- Nature Portfolio：https://www.nature.com/nature-portfolio/editorial-policies/reporting-standards  
- NLM/温哥华：https://www.nlm.nih.gov/bsd/uniform_requirements.html  

## 依赖项  

### 必要的 Python 包  
```bash
pip install requests  # 用于引用验证
```

### 必要的系统工具  
```bash
# 用于 PDF 生成
brew install pandoc  # macOS
apt-get install pandoc  # Linux

# 用于 LaTeX（PDF 生成）
brew install --cask mactex  # macOS
apt-get install texlive-xetex  # Linux
```

检查依赖项：  
```bash
python scripts/generate_pdf.py --check-deps
```

## 总结  

该文献综述技能提供：  

1. **系统化方法**，遵循学术最佳实践  
2. **多数据库集成**，通过现有科学技能实现  
3. **引用验证**，确保准确性和可信度  
4. **专业输出**，支持 markdown 和 PDF 格式  
5. **全面指导**，涵盖整个综述流程  
6. **质量保证**，通过验证和校验工具实现  
7. **可复现性**，通过详细文档要求保障  

执行严谨、系统的文献综述，满足学术标准，并全面整合任何领域的当前知识。
