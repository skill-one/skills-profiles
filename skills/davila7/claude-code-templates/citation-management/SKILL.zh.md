---
name: citation-management
description: 学术研究的全面引文管理。搜索 Google Scholar 和 PubMed 以查找论文，提取准确的元数据，验证引文，并生成格式正确的 BibTeX 条目。当您需要查找论文、验证引文信息、将 DOI 转换为 BibTeX 或确保科学写作中参考文献的准确性时，应使用此技能。
---

# 引用管理

## 概述

在整个研究和写作过程中系统化管理引用。这项技能提供搜索学术数据库（Google Scholar、PubMed）的工具和策略，从多个来源（CrossRef、PubMed、arXiv）提取准确的元数据，验证引用信息，并生成格式正确的BibTeX条目。

对于保持引用准确性、避免参考文献错误以及确保研究结果可重复至关重要。与文献综述技能无缝集成，用于全面的研究工作流程。

## 何时使用此技能

使用此技能的情况：

- 在Google Scholar或PubMed上搜索特定论文
- 将DOI、PMID或arXiv ID转换为格式正确的BibTeX
- 提取引用的完整元数据（作者、标题、期刊、年份等）
- 验证现有引用的准确性
- 清理和格式化BibTeX文件
- 查找特定领域的高被引论文
- 核实引用信息与实际出版物是否一致
- 为手稿或论文构建参考文献列表
- 检查重复引用
- 确保引用格式一致

## 使用科学示意图进行视觉增强

**创建使用此技能的文档时，请始终考虑添加科学图表和示意图以增强视觉交流。**

如果您的文档中尚未包含示意图或图表：

- 使用**scientific-schematics**技能生成AI驱动的出版级图表
- 仅用自然语言描述您想要的图表
- Nano Banana Pro将自动生成、审查和改进示意图

**对于新文档：** 科学示意图应默认生成，以视觉方式表示文本中描述的关键概念、工作流程、架构或关系。

**如何生成示意图：**
```bash
python scripts/generate_schematic.py "your diagram description" -o figures/output.png
```

AI将自动：

- 创建具有正确格式的出版级图像
- 通过多次迭代进行审查和改进
- 确保可访问性（对色盲友好、高对比度）
- 将输出保存在figures/目录中

**何时添加示意图：**

- 引用工作流程图表
- 文献搜索方法流程图
- 参考文献管理系统架构
- 引用样式决策树
- 数据库集成图表
- 任何从可视化中受益的复杂概念

有关创建示意图的详细指南，请参阅scientific-schematics技能文档。

---

## 核心工作流程

引用管理遵循系统化流程：

### 第一阶段：论文发现和搜索

**目标**：使用学术搜索引擎查找相关论文。

#### Google Scholar搜索

Google Scholar提供跨学科最全面的覆盖范围。

**基本搜索**：
```bash
# 搜索某个主题的论文
python scripts/search_google_scholar.py "CRISPR基因编辑" \
  --limit 50 \
  --output results.json

# 带年份过滤的搜索
python scripts/search_google_scholar.py "机器学习蛋白质折叠" \
  --year-start 2020 \
  --year-end 2024 \
  --limit 100 \
  --output ml_proteins.json
```

**高级搜索策略**（参见`references/google_scholar_search.md`）：
- 使用引号进行精确短语匹配：`"深度学习"`
- 按作者搜索：`author:LeCun`
- 仅在标题中搜索：`intitle:"神经网络"`
- 排除术语：`机器学习 -survey`
- 使用排序选项查找高被引论文
- 按日期范围过滤以获取近期工作

**最佳实践**：
- 使用具体、有针对性的搜索词
- 包含关键技术术语和缩写
- 对于快速发展的领域按近年过滤
- 查看"被引用次数"以找到开创性论文
- 导出顶级结果以进行进一步分析

#### PubMed搜索

PubMed专门用于生物医学和生命科学文献（超过3500万条引用）。

**基本搜索**：
```bash
# 搜索PubMed
python scripts/search_pubmed.py "阿尔茨海默病治疗" \
  --limit 100 \
  --output alzheimers.json

# 带MeSH术语和过滤器的搜索
python scripts/search_pubmed.py \
  --query '"阿尔茨海默病"[MeSH] AND "药物治疗"[MeSH]' \
  --date-start 2020 \
  --date-end 2024 \
  --publication-types "临床试验,综述" \
  --output alzheimers_trials.json
```

**PubMed高级查询**（参见`references/pubmed_search.md`）：
- 使用MeSH术语：`"糖尿病"[MeSH]`
- 字段标签：`"癌症"[标题]`, `"Smith J"[作者]`
- 布尔运算符：`AND`, `OR`, `NOT`
- 日期过滤器：`2020:2024[发表日期]`
- 发表类型：`"综述"[发表类型]`
- 与E-utilities API结合使用以实现自动化

**最佳实践**：
- 使用MeSH浏览器查找正确的受控词汇
- 首先在PubMed高级搜索构建器中构建复杂查询
- 使用OR包含多个同义词
- 获取PMIDs以便轻松提取元数据
- 导出为JSON或直接导出到BibTeX

### 第二阶段：元数据提取

**目标**：将论文标识符（DOI、PMID、arXiv ID）转换为完整、准确的元数据。

#### 快速DOI到BibTeX转换

对于单个DOI，使用快速转换工具：

```bash
# 转换单个DOI
python scripts/doi_to_bibtex.py 10.1038/s41586-021-03819-2

# 从文件转换多个DOI
python scripts/doi_to_bibtex.py --input dois.txt --output references.bib

# 不同的输出格式
python scripts/doi_to_bibtex.py 10.1038/nature12345 --format json
```

#### 全面元数据提取

对于DOI、PMID、arXiv ID或URL：

```bash
# 从DOI提取
python scripts/extract_metadata.py --doi 10.1038/s41586-021-03819-2

# 从PMID提取
python scripts/extract_metadata.py --pmid 34265844

# 从arXiv ID提取
python scripts/extract_metadata.py --arxiv 2103.14030

# 从URL提取
python scripts/extract_metadata.py --url "https://www.nature.com/articles/s41586-021-03819-2"

# 从文件批量提取（混合标识符）
python scripts/extract_metadata.py --input identifiers.txt --output citations.bib
```

**元数据来源**（参见`references/metadata_extraction.md`）：

1. **CrossRef API**：DOI的主要来源
   - 期刊文章的全面元数据
   - 出版社提供的信息
   - 包括作者、标题、期刊、卷、页码、日期
   - 免费使用，无需API密钥

2. **PubMed E-utilities**：生物医学文献
   - 官方NCBI元数据
   - 包括MeSH术语、摘要
   - PMID和PMCID标识符
   - 免费使用，建议使用API密钥以处理高容量请求

3. **arXiv API**：物理学、数学、计算机科学、q-bio预印本
   - 预印本的完整元数据
   - 版本跟踪
   - 作者所属机构
   - 免费开放访问

4. **DataCite API**：研究数据集、软件、其他资源
   - 非传统学术产出的元数据
   - 数据集和代码的DOI
   - 免费访问

**提取的内容**：
- **必需字段**：作者、标题、年份
- **期刊文章**：期刊、卷、期、页码、DOI
- **书籍**：出版社、ISBN、版本
- **会议论文**：会议名称、会议地点、页码
- **预印本**：存储库（arXiv、bioRxiv）、预印本ID
- **附加信息**：摘要、关键词、URL

### 第三阶段：BibTeX格式化

**目标**：生成干净、格式正确的BibTeX条目。

#### 理解BibTeX条目类型

参见`references/bibtex_formatting.md`的完整指南。

**常见条目类型**：
- `@article`：期刊文章（最常见）
- `@book`：书籍
- `@inproceedings`：会议论文
- `@incollection`：书籍章节
- `@phdthesis`：学位论文
- `@misc`：预印本、软件、数据集

**不同类型的必需字段**：

```bibtex
@article{citationkey,
  author  = {Last1, First1 and Last2, First2},
  title   = {Article Title},
  journal = {Journal Name},
  year    = {2024},
  volume  = {10},
  number  = {3},
  pages   = {123--145},
  doi     = {10.1234/example}
}

@inproceedings{citationkey,
  author    = {Last, First},
  title     = {Paper Title},
  booktitle = {Conference Name},
  year      = {2024},
  pages     = {1--10}
}

@book{citationkey,
  author    = {Last, First},
  title     = {Book Title},
  publisher = {Publisher Name},
  year      = {2024}
}
```

#### 格式化和清理

使用格式化工具标准化BibTeX文件：

```bash
# 格式化和清理BibTeX文件
python scripts/format_bibtex.py references.bib \
  --output formatted_references.bib

# 按引用键排序条目
python scripts/format_bibtex.py references.bib \
  --sort key \
  --output sorted_references.bib

# 按年份排序（最新优先）
python scripts/format_bibtex.py references.bib \
  --sort year \
  --descending \
  --output sorted_references.bib

# 删除重复项
python scripts/format_bibtex.py references.bib \
  --deduplicate \
  --output clean_references.bib

# 验证并报告问题
python scripts/format_bibtex.py references.bib \
  --validate \
  --report validation_report.txt
```

**格式化操作**：
- 标准化字段顺序
- 统一缩进和空格
- 标题中正确的首字母大写（用{}保护）
- 标准化作者姓名格式
- 统一引用键格式
- 删除不必要的字段
- 修复常见错误（缺少逗号、括号）

### 第四阶段：引用验证

**目标**：验证所有引用都是准确和完整的。

#### 全面验证

```bash
# 验证BibTeX文件
python scripts/validate_citations.py references.bib

# 验证并修复常见问题
python scripts/validate_citations.py references.bib \
  --auto-fix \
  --output validated_references.bib

# 生成详细验证报告
python scripts/validate_citations.py references.bib \
  --report validation_report.json \
  --verbose
```

**验证检查**（参见`references/citation_validation.md`）：

1. **DOI验证**：
   - 通过doi.org正确解析DOI
   - BibTeX和CrossRef之间的元数据匹配
   - 没有损坏或无效的DOI

2. **必需字段**：
   - 所有必需字段按条目类型存在
   - 没有空的或缺失的关键信息
   - 作者姓名格式正确

3. **数据一致性**：
   - 年份有效（4位数字，合理范围）
   - 卷/期是数字
   - 页码格式正确（例如，123--145）
   - URL可访问

4. **重复检测**：
   - 相同DOI多次使用
   - 标题相似（可能重复）
   - 相同作者/年份/标题组合

5. **格式合规性**：
   - 有效的BibTeX语法
   - 正确的括号和引号
   - 引用键是唯一的
   - 正确处理特殊字符

**验证输出**：
```json
{
  "total_entries": 150,
  "valid_entries": 145,
  "errors": [
    {
      "citation_key": "Smith2023",
      "error_type": "missing_field",
      "field": "journal",
      "severity": "high"
    },
    {
      "citation_key": "Jones2022",
      "error_type": "invalid_doi",
      "doi": "10.1234/broken",
      "severity": "high"
    }
  ],
  "warnings": [
    {
      "citation_key": "Brown2021",
      "warning_type": "possible_duplicate",
      "duplicate_of": "Brown2021a",
      "severity": "medium"
    }
  ]
}
```

### 第五阶段：与写作工作流程集成

#### 为手稿构建参考文献

创建参考文献列表的完整工作流程：

```bash
# 1. 搜索您主题的论文
python scripts/search_pubmed.py \
  '"CRISPR-Cas系统"[MeSH] AND "基因编辑"[MeSH]' \
  --date-start 2020 \
  --limit 200 \
  --output crispr_papers.json

# 2. 从搜索结果中提取DOI并转换为BibTeX
python scripts/extract_metadata.py \
  --input crispr_papers.json \
  --output crispr_refs.bib

# 3. 通过DOI添加特定论文
python scripts/doi_to_bibtex.py 10.1038/nature12345 >> crispr_refs.bib
python scripts/doi_to_bibtex.py 10.1126/science.abcd1234 >> crispr_refs.bib

# 4. 格式化和清理BibTeX文件
python scripts/format_bibtex.py crispr_refs.bib \
  --deduplicate \
  --sort year \
  --descending \
  --output references.bib

# 5. 验证所有引用
python scripts/validate_citations.py references.bib \
  --auto-fix \
  --report validation.json \
  --output final_references.bib

# 6. 审查验证报告并修复任何剩余问题
cat validation.json

# 7. 在您的LaTeX文档中使用
# \bibliography{final_references}
```

#### 与文献综述技能集成

这项技能与`literature-review`技能相辅相成：

**文献综述技能** → 系统性搜索和综合
**引用管理技能** → 技术性引用处理

**组合工作流程**：
1. 使用`literature-review`进行多数据库综合搜索
2. 使用`citation-management`提取和验证所有引用
3. 使用`literature-review`按主题综合发现结果
4. 使用`citation-management`验证最终参考文献列表的准确性

```bash
# 完成文献综述后
# 验证综述文档中的所有引用
python scripts/validate_citations.py my_review_references.bib --report review_validation.json

# 如有需要，按特定引用样式格式化
python scripts/format_bibtex.py my_review_references.bib \
  --style nature \
  --output formatted_refs.bib
```

## 搜索策略

### Google Scholar最佳实践

**查找开创性论文**：
- 按被引次数排序（被引最多优先）
- 查找综述文章以获取概述
- 查看"被引用次数"以评估影响力
- 使用引用警报跟踪新引用

**高级运算符**（完整列表在`references/google_scholar_search.md`）：
```
"exact phrase"           # 精确短语匹配
author:lastname          # 按作者搜索
intitle:keyword          # 仅在标题中搜索
source:journal           # 搜索特定期刊
-exclude                 # 排除术语
OR                       # 替代术语
2020..2024              # 年份范围
```

**示例搜索**：
```
# 查找近期主题综述
"CRISPR" intitle:review 2023..2024

# 查找特定作者的主题论文
author:Church "合成生物学"

# 查找高被引基础性工作
"深度学习" 2012..2015 sort:citations

# 排除综述，专注于方法
"蛋白质折叠" -survey -review intitle:method
```

### PubMed最佳实践

**使用MeSH术语**：
MeSH（医学主题词）提供用于精确搜索的受控词汇。

1. **查找MeSH术语**：访问 https://meshb.nlm.nih.gov/search
2. **在查询中使用**：`"糖尿病"[MeSH]`
3. **与关键词结合**以获取全面覆盖

**字段标签**：
```
[Title]              # 仅在标题中搜索
[Title/Abstract]     # 在标题或摘要中搜索
[Author]             # 按作者姓名搜索
[Journal]            # 搜索特定期刊
[Publication Date]   # 日期范围
[Publication Type]   # 文章类型
[MeSH]              # MeSH术语
```

**构建复杂查询**：
```bash
# 近期糖尿病治疗临床试验
"糖尿病"[MeSH] AND "药物治疗"[MeSH] 
AND "临床试验"[发表类型] AND 2020:2024[发表日期]

# 某期刊上的CRISPR综述
"CRISPR-Cas系统"[MeSH] AND "Nature"[期刊] AND "综述"[发表类型]

# 特定作者的近期工作
"Smith AB"[作者] AND 癌症[标题/摘要] AND 2022:2024[发表日期]
```

**E-utilities用于自动化**：
脚本使用NCBI E-utilities API进行程序化访问：
- **ESearch**：搜索和检索PMIDs
- **EFetch**：检索完整元数据
- **ESummary**：获取摘要信息
- **ELink**：查找相关文章

参见`references/pubmed_search.md`的完整API文档。

## 工具和脚本

### search_google_scholar.py

搜索Google Scholar并导出结果。

**功能**：
- 自动化搜索并限制速率
- 分页支持
- 年份范围过滤
- 导出为JSON或BibTeX
- 引用计数信息

**使用方法**：
```bash
# 基本搜索
python scripts/search_google_scholar.py "量子计算"

# 带过滤条件的高级搜索
python scripts/search_google_scholar.py "量子计算" \
  --year-start 2020 \
  --year-end 2024 \
  --limit 100 \
  --sort-by 引用次数 \
  --output 量子论文.json

# 直接导出为 BibTeX
python scripts/search_google_scholar.py "机器学习" \
  --limit 50 \
  --format bibtex \
  --output 机器学习论文.bib
```

### search_pubmed.py

使用 E-utilities API 搜索 PubMed。

**功能**：
- 支持复杂查询（MeSH、字段标签、布尔运算）
- 日期范围过滤
- 发表类型过滤
- 批量检索带元数据
- 导出为 JSON 或 BibTeX

**使用方法**：
```bash
# 简单关键词搜索
python scripts/search_pubmed.py "CRISPR 基因编辑"

# 带过滤条件的高级查询
python scripts/search_pubmed.py \
  --query '"CRISPR-Cas Systems"[MeSH] AND "therapeutic"[Title/Abstract]' \
  --date-start 2020-01-01 \
  --date-end 2024-12-31 \
  --publication-types "临床试验,综述" \
  --limit 200 \
  --output crispr_therapeutic.json

# 导出为 BibTeX
python scripts/search_pubmed.py "阿尔茨海默病" \
  --limit 100 \
  --format bibtex \
  --output 阿尔茨海默病.bib
```

### extract_metadata.py

从论文标识符提取完整元数据。

**功能**：
- 支持DOI、PMID、arXiv ID、URL
- 查询 CrossRef、PubMed、arXiv API
- 处理多种标识符类型
- 批量处理
- 多种输出格式

**使用方法**：
```bash
# 单个DOI
python scripts/extract_metadata.py --doi 10.1038/s41586-021-03819-2

# 单个PMID
python scripts/extract_metadata.py --pmid 34265844

# 单个arXiv ID
python scripts/extract_metadata.py --arxiv 2103.14030

# 从URL获取
python scripts/extract_metadata.py \
  --url "https://www.nature.com/articles/s41586-021-03819-2"

# 批量处理（文件中每行一个标识符）
python scripts/extract_metadata.py \
  --input paper_ids.txt \
  --output 参考文献.bib

# 不同的输出格式
python scripts/extract_metadata.py \
  --doi 10.1038/nature12345 \
  --format json  # 或 bibtex, yaml
```

### validate_citations.py

验证 BibTeX 条目的准确性和完整性。

**功能**：
- 通过 doi.org 和 CrossRef 验证 DOI
- 检查必填字段
- 重复检测
- 格式验证
- 自动修复常见问题
- 详细报告

**使用方法**：
```bash
# 基本验证
python scripts/validate_citations.py references.bib

# 带自动修复
python scripts/validate_citations.py references.bib \
  --auto-fix \
  --output 修复后的参考文献.bib

# 详细验证报告
python scripts/validate_citations.py references.bib \
  --report 验证报告.json \
  --verbose

# 仅检查DOI
python scripts/validate_citations.py references.bib \
  --check-dois-only
```

### format_bibtex.py

格式化和清理 BibTeX 文件。

**功能**：
- 标准化格式
- 按键、年份、作者排序条目
- 移除重复项
- 验证语法
- 修复常见错误
- 强制引用键规范

**使用方法**：
```bash
# 基本格式化
python scripts/format_bibtex.py references.bib

# 按年份排序（最新优先）
python scripts/format_bibtex.py references.bib \
  --sort year \
  --descending \
  --output 排序后的参考文献.bib

# 移除重复项
python scripts/format_bibtex.py references.bib \
  --deduplicate \
  --output 清理后的参考文献.bib

# 完整清理
python scripts/format_bibtex.py references.bib \
  --deduplicate \
  --sort year \
  --validate \
  --auto-fix \
  --output 最终参考文献.bib
```

### doi_to_bibtex.py

快速 DOI 到 BibTeX 转换。

**功能**：
- 快速单个 DOI 转换
- 批量处理
- 多种输出格式
- 支持剪贴板

**使用方法**：
```bash
# 单个DOI
python scripts/doi_to_bibtex.py 10.1038/s41586-021-03819-2

# 多个DOI
python scripts/doi_to_bibtex.py \
  10.1038/nature12345 \
  10.1126/science.abc1234 \
  10.1016/j.cell.2023.01.001

# 从文件获取（每行一个DOI）
python scripts/doi_to_bibtex.py --input dois.txt --output 参考文献.bib

# 复制到剪贴板
python scripts/doi_to_bibtex.py 10.1038/nature12345 --clipboard
```

## 最佳实践

### 搜索策略

1. **先广后窄**：
   - 从通用术语开始了解领域
   - 使用具体关键词和过滤器细化
   - 使用同义词和相关术语

2. **使用多个来源**：
   - Google Scholar 用于全面覆盖
   - PubMed 用于生物医学重点
   - arXiv 用于预印本
   - 结合结果以确保完整性

3. **利用引用**：
   - 查看 "被引用" 获取经典论文
   - 审查关键论文的参考文献
   - 使用引用网络发现相关研究

4. **记录搜索过程**：
   - 保存搜索查询和日期
   - 记录结果数量
   - 记录应用的过滤器或限制

### 元数据提取

1. **优先使用DOI**：
   - 最可靠的标识符
   - 永久链接到出版物
   - 通过 CrossRef 获取最佳元数据

2. **验证提取的元数据**：
   - 检查作者姓名是否正确
   - 验证期刊/会议名称
   - 确认发表年份
   - 验证页码和卷号

3. **处理特殊情况**：
   - 预印本：包含存储库和ID
   - 已发表的预印本：使用发表版本
   - 会议论文：包含会议名称和地点
   - 书籍章节：包含书名和编者

4. **保持一致性**：
   - 使用一致的作者姓名格式
   - 标准化期刊缩写
   - 使用相同的DOI格式（URL优先）

### BibTeX 质量

1. **遵循规范**：
   - 使用有意义的引用键（FirstAuthor2024keyword）
   - 使用 {} 保护标题中的大写字母
   - 使用 -- 表示页码范围（不使用单破折号）
   - 所有现代出版物都包含 DOI 字段

2. **保持简洁**：
   - 移除不必要的字段
   - 无冗余信息
   - 保持一致格式
   - 定期验证语法

3. **系统组织**：
   - 按年份或主题排序
   - 分组相关论文
   - 使用不同项目文件
   - 小心合并以避免重复

### 验证

1. **尽早频繁验证**：
   - 添加引用时检查
   - 提交前验证完整参考文献
   - 编辑后重新验证

2. **及时修复问题**：
   - 坏DOI：找到正确标识符
   - 缺少字段：从原始来源提取
   - 重复项：选择最佳版本，删除其他
   - 格式错误：安全时使用自动修复

3. **关键引用手动审核**：
   - 验证引用的论文是否正确
   - 检查作者姓名与出版物是否匹配
   - 确认页码和卷号
   - 确保URL是当前的

## 常见错误

1. **单一来源偏差**：仅使用 Google Scholar 或 PubMed
   - **解决方案**：搜索多个数据库以获得全面覆盖

2. **盲目接受元数据**：不验证提取的信息
   - **解决方案**：与原始来源核对提取的元数据

3. **忽略DOI错误**：参考文献中损坏或错误的DOI
   - **解决方案**：提交前运行验证

4. **格式不一致**：混合引用键样式、格式
   - **解决方案**：使用 format_bibtex.py 标准化

5. **重复条目**：同一篇论文使用不同键引用多次
   - **解决方案**：在验证中使用重复检测

6. **缺少必填字段**：不完整的 BibTeX 条目
   - **解决方案**：验证并确保所有必填字段存在

7. **过时的预印本**：引用预印本时已发表版本存在
   - **解决方案**：检查预印本是否已发表，更新为期刊版本

8. **特殊字符问题**：由于字符导致 LaTeX 编译损坏
   - **解决方案**：在 BibTeX 中使用正确的转义或 Unicode

9. **提交前无验证**：带有引用错误的提交
   - **解决方案**：始终作为最终检查运行验证

10. **手动输入 BibTeX**：手动输入条目
    - **解决方案**：始终使用脚本从元数据源提取

## 示例工作流程

### 示例 1：为论文构建参考文献

```bash
# 第一步：查找您主题的关键论文
python scripts/search_google_scholar.py "Transformer 神经网络" \
  --year-start 2017 \
  --limit 50 \
  --output transformer_gs.json

python scripts/search_pubmed.py "深度学习医学影像" \
  --date-start 2020 \
  --limit 50 \
  --output medical_dl_pm.json

# 第二步：从搜索结果提取元数据
python scripts/extract_metadata.py \
  --input transformer_gs.json \
  --output transformer.bib

python scripts/extract_metadata.py \
  --input medical_dl_pm.json \
  --output medical.bib

# 第三步：添加您已知的特定论文
python scripts/doi_to_bibtex.py 10.1038/s41586-021-03819-2 >> specific.bib
python scripts/doi_to_bibtex.py 10.1126/science.aam9317 >> specific.bib

# 第四步：合并所有 BibTeX 文件
cat transformers.bib medical.bib specific.bib > combined.bib

# 第五步：格式化和去重
python scripts/format_bibtex.py combined.bib \
  --deduplicate \
  --sort year \
  --descending \
  --output formatted.bib

# 第六步：验证
python scripts/validate_citations.py formatted.bib \
  --auto-fix \
  --report validation.json \
  --output final_references.bib

# 第七步：审查任何问题
cat validation.json | grep -A 3 '"errors"'

# 第八步：用于 LaTeX
# \bibliography{final_references}
```

### 示例 2：转换 DOI 列表

```bash
# 您有一个包含 DOI 的文本文件
# dois.txt 包含：
# 10.1038/s41586-021-03819-2
# 10.1126/science.aam9317
# 10.1016/j.cell.2023.01.001

# 转换所有为 BibTeX
python scripts/doi_to_bibtex.py --input dois.txt --output references.bib

# 验证结果
python scripts/validate_citations.py references.bib --verbose
```

### 示例 3：清理现有 BibTeX 文件

```bash
# 您有一个来自不同来源的混乱 BibTeX 文件
# 系统清理

# 第一步：格式化和标准化
python scripts/format_bibtex.py messy_references.bib \
  --output step1_formatted.bib

# 第二步：移除重复项
python scripts/format_bibtex.py step1_formatted.bib \
  --deduplicate \
  --output step2_deduplicated.bib

# 第三步：验证和自动修复
python scripts/validate_citations.py step2_deduplicated.bib \
  --auto-fix \
  --output step3_validated.bib

# 第四步：按年份排序
python scripts/format_bibtex.py step3_validated.bib \
  --sort year \
  --descending \
  --output clean_references.bib

# 第五步：最终验证报告
python scripts/validate_citations.py clean_references.bib \
  --report final_validation.json \
  --verbose

# 查看报告
cat final_validation.json
```

### 示例 4：查找并引用经典论文

```bash
# 查找高被引论文
python scripts/search_google_scholar.py "AlphaFold 蛋白质结构" \
  --year-start 2020 \
  --year-end 2024 \
  --sort-by 引用次数 \
  --limit 20 \
  --output alphafold_seminal.json

# 提取引用次数最多的前10篇
# (脚本将包含JSON中的引用次数)

# 转换为 BibTeX
python scripts/extract_metadata.py \
  --input alphafold_seminal.json \
  --output alphafold_refs.bib

# BibTeX 文件现在包含最有影响力的论文
```

## 与其他技能的集成

### 文献综述技能

**引用管理**为**文献综述**提供技术基础设施：

- **文献综述**：多数据库系统搜索和综合
- **引用管理**：元数据提取和验证

**组合工作流程**：
1. 使用文献综述进行系统搜索方法
2. 使用引用管理提取和验证引用
3. 使用文献综述综合结果
4. 使用引用管理确保参考文献准确性

### 科研写作技能

**引用管理**确保**科研写作**的准确引用：

- 导出验证后的 BibTeX 用于 LaTeX 手稿
- 验证引用符合出版标准
- 按期刊要求格式化参考文献

### 会议模板技能

**引用管理**与**会议模板**配合提交准备好的手稿：

- 不同会议要求不同的引用格式
- 生成格式正确的参考文献
- 验证引用满足会议要求

## 资源

### 内置资源

**参考文献**（在 `references/`）：
- `google_scholar_search.md`：完整 Google Scholar 搜索指南
- `pubmed_search.md`：PubMed 和 E-utilities API 文档
- `metadata_extraction.md`：元数据来源和字段要求
- `citation_validation.md`：验证标准和质量检查
- `bibtex_formatting.md`：BibTeX 条目类型和格式规则

**脚本**（在 `scripts/`）：
- `search_google_scholar.py`：Google Scholar 搜索自动化
- `search_pubmed.py`：PubMed E-utilities API 客户端
- `extract_metadata.py`：通用元数据提取器
- `validate_citations.py`：引用验证和确认
- `format_bibtex.py`：BibTeX 格式化和清理
- `doi_to_bibtex.py`：快速 DOI 到 BibTeX 转换

**资源**（在 `assets/`）：
- `bibtex_template.bib`：所有类型的示例 BibTeX 条目
- `citation_checklist.md`：质量保证清单

### 外部资源

**搜索引擎**：
- Google Scholar：https://scholar.google.com/
- PubMed：https://pubmed.ncbi.nlm.nih.gov/
- PubMed 高级搜索：https://pubmed.ncbi.nlm.nih.gov/advanced/

**元数据 API**：
- CrossRef API：https://api.crossref.org/
- PubMed E-utilities：https://www.ncbi.nlm.nih.gov/books/NBK25501/
- arXiv API：https://arxiv.org/help/api/
- DataCite API：https://api.datacite.org/

**工具和验证器**：
- MeSH 浏览器：https://meshb.nlm.nih.gov/search
- DOI 解析器：https://doi.org/
- BibTeX 格式：http://www.bibtex.org/Format/

**引用格式**：
- BibTeX 文档：http://www.bibtex.org/
- LaTeX 参考文献管理：https://www.overleaf.com/learn/latex/Bibliography_management

## 依赖项

### 必要的 Python 包

```bash
# 核心依赖
pip install requests  # HTTP 请求用于 API
pip install bibtexparser  # BibTeX 解析和格式化
pip install biopython  # PubMed E-utilities 访问

# 可选（用于 Google Scholar）
pip install scholarly  # Google Scholar API 包装器
# 或
pip install selenium  # 更健壮的 Scholar 爬取
```

### 可选工具

```bash
# 用于高级验证
pip install crossref-commons  # 增强 CrossRef API 访问
pip install pylatexenc  # LaTeX 特殊字符处理
```

## 总结

引用管理技能提供：

1. **全面的搜索功能**：Google Scholar 和 PubMed
2. **自动化元数据提取**：从 DOI、PMID、arXiv ID、URL
3. **引用验证**：DOI 验证和完整性检查
4. **BibTeX 格式化**：标准化和清理工具
5. **质量保证**：验证和报告
6. **与科研写作流程集成**
7. **可重复性**：记录搜索和提取方法

使用此技能维护研究过程中的准确完整引用，并确保符合出版标准的参考文献。
