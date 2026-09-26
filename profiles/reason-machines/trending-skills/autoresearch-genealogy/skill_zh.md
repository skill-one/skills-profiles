# autoresearch-genealogy

> 技能由 [ara.so](https://ara.so) 提供 — 每日 2026 技能集合。

一个结构化的自动研究提示系统、Obsidian 密钥库模板、档案指南和方法论参考，用于 AI 辅助的家族谱研究。为 Claude Code 的自主研究循环而构建，可适应任何 AI 工具或手动工作流程。

---

## 本项目的作用

- 提供 12 个 Claude Code `/autoresearch` 提示，可自动搜索网络、更新您的密钥库并自我验证结果
- 提供 19 个文件的完整 Obsidian 密钥库入门套件，包含 YAML 前置文本和 Markdown 模板
- 包含 24 个国家/地区特定的档案指南（欧洲、美洲、大洋洲、犹太谱系）
- 提供 9 份方法论参考文档，涵盖信心等级、DNA 护栏、命名惯例和来源层次结构
- 定义 7 个分步工作流程，用于 OCR 管道、口述历史、差异解决和阶段规划

---

## 安装

```bash
# 克隆存储库
git clone https://github.com/mattprusak/autoresearch-genealogy.git
cd autoresearch-genealogy

# 将密钥库模板复制到您的 Obsidian 密钥库
cp -r vault-template/ ~/path/to/your/ObsidianVault/genealogy/

# 或者复制到任何 Markdown 编辑器文件夹
cp -r vault-template/ ~/Documents/my-genealogy/
```

无需包管理器或构建步骤 — 这是一个纯 Markdown/提示项目。

---

## 项目结构

```
autoresearch-genealogy/
├── prompts/              # 12 个用于 Claude Code 的自动研究提示文件
├── vault-template/       # 19 文件的 Obsidian 密钥库入门套件
│   ├── Family_Tree.md
│   ├── Research_Log.md
│   ├── Open_Questions.md
│   ├── templates/        # 人物、证书、明信片、地区等
│   └── ...
├── archives/             # 24 个国家/地区研究指南
├── reference/            # 9 份方法论文档
├── workflows/            # 7 个分步流程指南
└── examples/             # 6 个匿名案例
```

---

## 快速入门工作流程

### 第 1 步：为您的家谱树提供种子数据

打开 `vault-template/Family_Tree.md` 并填写您已经知道的信息，从自己开始并向后追溯：

```markdown
---
title: Family Tree
last_updated: 2026-03-19
generations_documented: 3
lines_active: 2
---

# Family Tree

## Generation 1 (Self)
- **Name**: Jane Smith (b. 1985, Chicago, IL)

## Generation 2 (Parents)
- **Father**: John Smith (b. 1955, Detroit, MI)
- **Mother**: Mary O'Brien (b. 1958, Boston, MA)

## Generation 3 (Grandparents)
- **Paternal Grandfather**: Robert Smith (b. ~1920, unknown)
- **Paternal Grandmother**: Helen Kowalski (b. ~1925, Poland?)
```

### 第 2 步：扫描实体文档

拍摄或扫描证书、信件、明信片。使用 OCR 工作流程：

```
See: workflows/ocr-pipeline.md
```

### 第 3 步：在 Claude Code 中运行自动研究提示

```
/autoresearch prompts/01-tree-expansion.md
```

### 第 4 步：审核和验证

```
/autoresearch prompts/02-cross-reference-audit.md
```

---

## 自动研究提示 — 参考

`prompts/` 中的每个提示都遵循以下结构：

```markdown
## 目标
[本次迭代应完成的事项]

## 指标
[可衡量的成功条件 — 例如，"将来源文件从 N 增加到 N+10"]

## 方向
[AI 的分步说明]

## 验证
[每次迭代后运行的交叉检查]

## 护栏
[不要做的事情 — 防止幻觉，保持来源严谨]

## 迭代次数
[在人工审核之前运行多少次循环]

## 协议
[输出格式、文件命名、要填充的 YAML 字段]
```

### 所有 12 个提示

| 文件 | 目的 |
|------|------|
| `01-tree-expansion.md` | 使用网络研究将每个分支向后追溯 |
| `02-cross-reference-audit.md` | 查找并解决树和来源之间的差异 |
| `03-findagrave-sweep.md` | 定位 Find a Grave 纪念碑，用于已故祖先 |
| `04-gedcom-completeness.md` | 将 GEDCOM 文件与密钥库数据同步 |
| `05-source-citation-audit.md` | 验证每个人是否至少有 2 个独立来源 |
| `06-unresolved-persons.md` | 识别和解决文档中的无名人士 |
| `07-timeline-gap-analysis.md` | 查找记录中应该存在但不存在的生活事件 |
| `08-open-question-resolution.md` | 系统地解决每个开放研究问题 |
| `09-bygdebok-extraction.md` | 从数字化地方历史书中提取数据 |
| `10-colonial-records-search.md` | 搜索 1800 年前的美国殖民地记录 |
| `11-immigration-search.md` | 定位乘客名单和入籍记录 |
| `12-dna-chromosome-analysis.md` | 分析每个染色体的祖先数据 |

### 在 Claude Code 中运行提示

```bash
# 在 Claude Code 终端或聊天中：
/autoresearch prompts/08-open-question-resolution.md

# 带有特定密钥库路径上下文：
/autoresearch prompts/03-findagrave-sweep.md --context vault-template/Family_Tree.md
```

---

## 密钥库模板文件

### 人物文件模板 (`vault-template/templates/person.md`)

```markdown
---
full_name: ""
birth_date: ""
birth_place: ""
death_date: ""
death_place: ""
father: ""
mother: ""
spouse: ""
children: []
confidence: "Moderate Signal"  # Strong Signal | Moderate Signal | Speculative
sources: []
open_questions: []
last_updated: ""
---

# [Full Name]

## Life Events

| Event | Date | Place | Source |
|-------|------|-------|--------|
| Birth | | | |
| Marriage | | | |
| Death | | | |

## Sources

1. [Source 1 — 类型、存储库、访问日期]
2. [Source 2 — 类型、存储库、访问日期]

## Open Questions

- [ ] 问题 1
- [ ] 问题 2

## Notes

[Narrative summary, naming variant notes, contextual history]
```

### 证书转录模板 (`vault-template/templates/certificate.md`)

```markdown
---
document_type: ""        # birth | death | marriage | baptism
document_date: ""
repository: ""
file_reference: ""
transcribed_by: ""
transcription_date: ""
confidence: ""
---

# Certificate: [Type] — [Name] — [Year]

## Transcription

[文档的逐字转录]

## Key Data Extracted

- **Subject**: 
- **Date**: 
- **Place**: 
- **Witnesses/Informants**: 
- **Officiant**: 

## Discrepancies

[注意与其他来源的任何冲突]

## Image

![[filename.jpg]]
```

### 研究日志条目模式 (`vault-template/Research_Log.md`)

```markdown
## 2026-03-19 — Tree Expansion Session

**Prompt run**: 01-tree-expansion.md  
**Iterations**: 5  
**Metric start**: 42 sourced person files  
**Metric end**: 51 sourced person files  

### Searches Performed
- FamilySearch: "Kowalski Poznan 1880–1920" — 3 results, 2 useful
- Ancestry: "Smith Michigan census 1920" — found Robert Smith (b. 1919)
- FindAGrave: "Helen Kowalski Detroit" — memorial #12345678

### Negative Results (Important)
- 没有找到 Stanislaw Kowalski 的乘客名单，搜索了 1890–1910 年
- 没有找到 1850 年前的科克郡教堂记录

### New Open Questions
- [ ] Robert Smith 出生于密歇根州还是俄亥俄州？1920 年人口普查显示 MI，1930 年显示 OH。
```

---

## 信心等级系统

来自 `reference/confidence-tiers.md`：

```
Strong Signal    — 两个或多个独立的一手来源一致
Moderate Signal  — 一个一手来源，或两个二手来源一致
Speculative      — 逻辑推断、DNA 建议，或单个二手来源
```

在每个人物文件 YAML 中应用信心：

```markdown
---
confidence: "Moderate Signal"
---
```

---

## 档案指南 — 主要国家

`archives/` 中的每个指南涵盖：

- 哪里可以找到记录（免费与付费）
- AI 工具可以直接访问的内容与需要浏览器的內容
- 每个时代可用的记录类型

```
archives/
├── ireland.md
├── england-wales.md
├── scotland.md
├── norway.md
├── sweden.md
├── poland.md
├── germany.md
├── italy.md
├── france.md
├── spain-portugal.md
├── netherlands.md
├── austria.md
├── hungary.md
├── russia-ukraine.md
├── usa-colonial.md
├── usa-immigration.md
├── usa-census.md
├── usa-vital-records.md
├── african-american.md
├── canada.md
├── mexico-latin-america.md
├── australia-new-zealand.md
├── jewish-genealogy.md
└── ...
```

示例用法在提示中：

```markdown
# 在 prompts/09-bygdebok-extraction.md 中
## 方向
参考 archives/norway.md 中的 Digitalarkivet 访问模式。
搜索 Rogaland 地区的 Bygdebok 集合，1750–1900 年。
```

---

## 常见模式

### 模式 1：新祖先录入

当在研究过程中发现新祖先时：

```markdown
1. 从 vault-template/templates/person.md 创建人物文件
2. 根据来源数量设置信心等级
3. 在正确的世代中添加到 Family_Tree.md
4. 在 Research_Log.md 中记录发现
5. 将未解决的问题添加到 Open_Questions.md
6. 运行 02-cross-reference-audit.md 检查冲突
```

### 模式 2：解决日期差异

```markdown
# Open_Questions.md 条目
## Q-042: Robert Smith 出生州冲突
- 1920 年人口普查：出生在密歇根州
- 1930 年人口普查：出生在俄亥俄州
- 状态：未解决
- 下一步：运行 07-timeline-gap-analysis.md，针对 Robert Smith
```

然后在 Claude Code 中：

```
/autoresearch prompts/07-timeline-gap-analysis.md
# 聚焦：Robert Smith，约 1919 年出生，差异 Q-042
```

### 模式 3：DNA 到谱系映射

```markdown
# 在 vault-template/Genetic_Profile.md 中
---
test_company: AncestryDNA
test_date: 2024-11-01
ethnicity_summary:
  - region: Eastern Europe
    percentage: 38
  - region: Ireland/Scotland
    percentage: 31
---

# 然后运行：
/autoresearch prompts/12-dna-chromosome-analysis.md
```

### 模式 4：移民研究循环

```bash
# 运行移民搜索提示
/autoresearch prompts/11-immigration-search.md

# 提示将：
# 1. 从 Family_Tree.md 拉取所有外国出生的祖先
# 2. 搜索乘客名单（Ellis Island、Ancestry、FamilySearch）
# 3. 搜索入籍记录（NARA、Ancestry）
# 4. 更新人物文件，添加船名、到达日期、港口
# 5. 为每个未解决的祖先记录负面结果
```

---

## 参考文档

| 文件 | 内容 |
|------|------|
| `reference/confidence-tiers.md` | 强 / 中 / 推测定义 |
| `reference/source-hierarchy.md` | 一手来源与二手来源与衍生来源 |
| `reference/dna-guardrails.md` | DNA 可以和不能证明的内容；centimorgan 阈值 |
| `reference/naming-conventions.md` | 专利名、农场名、波兰 przydomki |
| `reference/gedcom-guide.md` | GEDCOM 字段参考和导出说明 |
| `reference/common-pitfalls.md` | 家族谱中 AI 幻觉模式、日期陷阱 |
| `reference/glossary.md` | 记录类型定义、拉丁术语、缩写 |
| `reference/ai-capabilities.md` | AI 可以直接访问的内容与需要人工的内容 |
| `reference/case-for-autoresearch.md` | 方法论理由 |

---

## 故障排除

### AI 正在编造来源

在您的提示会话中明确设置护栏：

```markdown
## 护栏（添加到任何提示）
- 不要编造人口普查记录 URL 或 Ancestry 记录 ID
- 如果来源不能直接链接，标记为 "reported" 而不是 "confirmed"
- 所有新声明都需要一个真实 URL 或存储库参考
- 不确定时，添加到 Open_Questions.md — 不要猜测
```

### 密钥库文件与 GEDCOM 不同步

运行完整性审核：

```
/autoresearch prompts/04-gedcom-completeness.md
```

这将比较您 GEDCOM 中的每个人物与密钥库人物文件，并标记不匹配项。

### 姓名变体导致重复人物文件

检查 `reference/naming-conventions.md` 中您家族的相关地区。常见陷阱：

- 挪威农场名变化（Haugen → Bakke 在移民时）
- 波兰教堂记录中的名称拉丁化（Stanisław → Stanislaus）
- 爱尔兰英语化（Ó Briain → O'Brien → Bryan）
- 人口普查记录中的拼写变体（"Sakkarias" vs "Zacharias" — 两者都有效）

向人物文件 YAML 添加别名：

```markdown
---
full_name: "Stanisław Kowalski"
name_variants:
  - "Stanislaus Kowalski"
  - "Stanley Kowalski"
  - "S. Kowalski"
---
```

### Autoresearch 循环运行时间过长

每个提示都有一个 `## Iterations` 字段。明确设置它：

```markdown
## Iterations
最多运行 3 次迭代，然后停止并输出供人工审核的摘要。
```

### OCR 在旧文档上产生差结果

见 `workflows/ocr-pipeline.md`。一般指导：

1. 最低 600 DPI 拍照
2. 使用均匀、漫射的光线 — 不要使用闪光灯
3. 在运行 OCR 之前进行对比度调整预处理
4. 使用 `vault-template/templates/transcription.md` 将 OCR 输出和您的手动更正并排记录

---

## 贡献

要添加新的档案指南或提示：

1. 遵循现有的文件结构和 YAML 前置文本模式
2. 在所有示例中使用占位符名称（不要使用真实家族数据）
3. 打开一个 PR，简要说明您添加的地区或记录类型

许可证：MIT
