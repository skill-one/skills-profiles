# 引文管理

## 概述

在整个研究和写作过程中系统化管理引文。这项技能提供搜索学术数据库（Google Scholar、PubMed）的工具和策略，从多个来源（CrossRef、PubMed、arXiv）提取准确的元数据，验证引文信息，并生成格式正确的BibTeX条目。

对于保持引文准确性、避免参考文献错误和确保可重复研究至关重要。与文献综述技能无缝集成，用于全面的研究工作流程。

## 何时使用此技能

使用此技能时：

- 在Google Scholar或PubMed上搜索特定论文
- 将DOI、PMID或arXiv ID转换为格式正确的BibTeX
- 提取引文的完整元数据（作者、标题、期刊、年份等）
- 验证现有引文的准确性
- 清理和格式化BibTeX文件
- 查找特定领域的高被引论文
- 核实引文信息是否与实际出版物一致
- 为手稿或论文构建参考文献列表
- 检查重复引文
- 确保一致的引文格式

## 使用科学示意图增强视觉传达

**使用此技能创建文档时，始终考虑添加科学图表和示意图以增强视觉传达。**

如果您的文档中尚未包含示意图或图表：

- 使用**scientific-schematics**技能生成AI驱动的出版级图表
- 用自然语言描述您想要的图表
- Nano Banana Pro将自动生成、审查和改进示意图

**对于新文档：** 科学示意图应默认生成，以视觉方式表示文本中描述的关键概念、工作流程、架构或关系。

**如何生成示意图：**
```bash
python scripts/generate_schematic.py "your diagram description" -o figures/output.png
```

AI将自动：

- 创建格式正确的出版级图像
- 通过多次迭代进行审查和改进
- 确保可访问性（对色盲友好、高对比度）
- 将输出保存在figures/目录中

**何时添加示意图：**

- 引文工作流程图表
- 文献搜索方法流程图
- 参考文献管理系统架构
- 引文样式决策树
- 数据库集成图表
- 任何受益于可视化的复杂概念

有关创建示意图的详细指南，请参阅scientific-schematics技能文档。

---

## 核心工作流程

引文管理遵循系统化流程：

### 第一阶段：论文发现和搜索

**目标**：使用学术搜索引擎查找相关论文。

#### Google Scholar搜索

Google Scholar提供跨学科的全面覆盖。

**基本搜索**：
```bash
# 搜索主题论文
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
- 排除术语：`machine learning -survey`
- 使用排序选项查找高被引论文
- 按日期范围过滤以获取最新工作

**最佳实践**：
- 使用具体、有针对性的搜索词
- 包含关键技术术语和缩写
- 对于快速发展的领域按近年过滤
- 查看"被引次数"以找到开创性论文
- 导出顶级结果以进行进一步分析

#### PubMed搜索

PubMed专门于生物医学和生命科学文献（超过3500万条引文）。

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
- 包含多个同义词，使用OR
- 检索PMIDs以便轻松提取元数据
- 直接导出到BibTeX

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
   - 出版商提供的信息
   - 包括作者、标题、期刊、卷、页码、日期
   - 免费使用，无需API密钥

2. **PubMed E-utilities**：生物医学文献
   - 官方NCBI元数据
   - 包括MeSH术语、摘要
   - PMID和PMCID标识符
   - 免费使用，建议使用API密钥进行高容量访问

3. **arXiv API**：物理学、数学、计算机科学、量子生物学的预印本
   - 预印本的完整元数据
   - 版本跟踪
   - 作者隶属关系
   - 免费使用，开放获取

4. **DataCite API**：研究数据集、软件和其他资源
   - 非传统学术产出的元数据
   - 数据集和代码的DOI
   - 免费访问

**提取的内容**：
- **必需字段**：作者、标题、年份
- **期刊文章**：期刊、卷、期、页码、DOI
- **书籍**：出版社、ISBN、版本
- **会议论文**：会议名称、会议地点、页码
- **预印本**：存储库（arXiv、bioRxiv）、预印本ID
- **其他**：摘要、关键词、URL

### 第三阶段：BibTeX格式化

**目标**：生成干净、格式正确的BibTeX条目。

#### 理解BibTeX条目类型

有关完整指南，请参阅`references/bibtex_formatting.md`。

**常见条目类型**：
- `@article`：期刊文章（最常见）
- `@book`：书籍
- `@inproceedings`：会议论文
- `@incollection`：书籍章节
- `@phdthesis`：论文
- `@misc`：预印本、软件、数据集

**按类型必需字段**：

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

# 按引文键排序条目
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
- 标准化的作者姓名格式
- 统一的引文键格式
- 删除不必要的字段
- 修复常见错误（缺少逗号、括号）

### 第四阶段：引文验证

**目标**：验证所有引文都是准确和完整的。

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
   - 相同DOI被多次使用
   - 类似的标题（可能是重复）
   - 相同作者/年份/标题组合

5. **格式合规性**：
   - 有效的BibTeX语法
   - 正确的括号和引号
   - 引文键是唯一的
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
# 第1步：搜索您主题的论文
python scripts/search_pubmed.py \
  '"CRISPR-Cas系统"[MeSH] AND "基因编辑"[MeSH]' \
  --date-start 2020 \
  --limit 200 \
  --output crispr_papers.json

python scripts/search_google_scholar.py "深度学习医学成像" \
  --date-start 2020 \
  --limit 50 \
  --output medical_dl_pm.json

# 第2步：从搜索结果中提取元数据并转换为BibTeX
python scripts/extract_metadata.py \
  --input crispr_papers.json \
  --output transformers.bib

python scripts/extract_metadata.py \
  --input medical_dl_pm.json \
  --output medical.bib

# 第3步：添加您已经知道的特定论文
python scripts/doi_to_bibtex.py 10.1038/nature12345 >> specific.bib
python scripts/doi_to_bibtex.py 10.1126/science.abcd1234 >> specific.bib

# 第4步：格式化和清理BibTeX文件
python scripts/format_bibtex.py combined.bib \
  --deduplicate \
  --sort year \
  --descending \
  --output references.bib

# 第5步：验证
python scripts/validate_citations.py references.bib \
  --auto-fix \
  --report validation.json \
  --output final_references.bib

# 第6步：审查任何问题
cat validation.json | grep -A 3 '"errors"'

# 第7步：在LaTeX中使用
# \bibliography{final_references}
```

#### 与文献综述技能的集成

**引文管理**为**文献综述**提供技术基础设施：

- **文献综述**：多数据库系统搜索和综合
- **引文管理**：元数据提取和验证

**组合工作流程**：
1. 使用literature-review进行系统化搜索方法
2. 使用citation-management提取和验证引文
3. 使用literature-review进行主题综合
4. 使用citation-management确保参考文献准确性

### 与其他技能的集成

#### 文献综述技能

**引文管理**为**科学写作**提供准确的参考文献：

- 导出验证后的BibTeX用于LaTeX手稿
- 验证引文符合出版标准
- 按期刊要求格式化参考文献

#### 场地模板技能

**引文管理**与**场地模板**配合使用，用于提交就绪的手稿：

- 不同的场地需要不同的引文样式
- 生成格式正确的参考文献
- 验证引文符合场地要求

## 资源

### 内嵌资源

**参考文献**（在`references/`）：
- `google_scholar_search.md`：完整的Google Scholar搜索指南
- `pubmed_search.md`：PubMed和E-utilities API文档
- `metadata_extraction.md`：元数据来源和字段要求
- `citation_validation.md`：验证标准和质量检查
- `bibtex_formatting.md`：BibTeX条目类型和格式规则

**脚本**（在`scripts/`）：
- `search_google_scholar.py`：Google Scholar搜索自动化
- `search_pubmed.py`：PubMed E-utilities API客户端
- `extract_metadata.py`：通用元数据提取器
- `validate_citations.py`：引文验证和确认
- `format_bibtex.py`：BibTeX格式化和清理
- `doi_to_bibtex.py`：快速DOI到BibTeX转换

**资源**（在`assets/`）：
- `bibtex_template.bib`：所有类型的示例BibTeX条目
- `citation_checklist.md`：质量保证清单

### 外部资源

**搜索引擎**：
- Google Scholar：https://scholar.google.com/
- PubMed：https://pubmed.ncbi.nlm.nih.gov/
- PubMed高级搜索：https://pubmed.ncbi.nlm.nih.gov/advanced/

**元数据API**：
- CrossRef API：https://api.crossref.org/
- PubMed E-utilities：https://www.ncbi.nlm.nih.gov/books/NBK25501/
- arXiv API：https://arxiv.org/help/api/
- DataCite API：https://api.datacite.org/

**工具和验证器**：
- MeSH浏览器：https://meshb.nlm.nih.gov/search
- DOI解析器：https://doi.org/
- BibTeX格式：http://www.bibtex.org/Format/

**引文样式**：
- BibTeX文档：http://www.bibtex.org/
- LaTeX参考文献管理：https://www.overleaf.com/learn/latex/Bibliography_management

## 依赖项

### 必要的Python包

```bash
# 核心依赖项
pip install requests  # HTTP请求用于API
pip install bibtexparser  # BibTeX解析和格式化
pip install biopython  # PubMed E-utilities访问

# 可选（用于Google Scholar）
pip install scholarly  # Google Scholar API包装器
# 或
pip install selenium  # 更强大的Scholar抓取
```

### 可选工具

```bash
# 用于高级验证
pip install crossref-commons  # 增强CrossRef API访问
pip install pylatexenc  # LaTeX特殊字符处理
```

## 总结

引文管理技能提供：

1. **全面的搜索功能**，用于Google Scholar和PubMed
2. **自动化的元数据提取**，从DOI、PMID、arXiv ID、URL
3. **引文验证**，包括DOI验证和完整性检查
4. **BibTeX格式化**，包括标准化和清理工具
5. **质量保证**，通过验证和报告
6. **与科学写作工作流程的集成**
7. **可重复性**，通过记录的搜索和提取方法

使用此技能在整个研究和写作过程中维护准确的、完整的引文，并确保符合出版标准的参考文献列表。
