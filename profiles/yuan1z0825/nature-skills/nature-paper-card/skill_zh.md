# Nature Paper Card - 路由器

使用此技能将一张纸转化为基于证据的研究卡片，而不是翻译的摘要、通用概述、审稿报告或出版物文章。

该技能使用：

- `static/core/` 下的静态核心，用于原则、工作流程和固定的输出合同；
- `static/fragments/paper_type/` 下的一种纸型片段；
- 按需引用的参考文献，用于证据标签、精确的卡片模式和研究想法检查。

## 路由协议

每次都按照以下步骤操作。

### 1. 加载清单和核心层

读取 [manifest.yaml](manifest.yaml)，然后读取 `always_load` 下面的每个文件。不要仅从这个路由器生成卡片。

### 2. 建立源边界

识别哪些材料可用：

- 带有图表和表格的完整论文；
- 没有可靠布局的论文文本；
- 仅摘要或元数据；
- 具有稳定源 ID 的现有 `nature-reader` 工件。

当提供时，优先选择现有的 `nature-reader` 工件。不要重复完整的双语翻译或图表提取。如果只有部分材料可用，创建一个明显是部分的卡片，并将每个不支持的部分标记为 `Not assessable from supplied material`。

对于 PDF 或 `nature-reader` 源图 JSON，必须使用捆绑脚本。

1. 将 `SKILL_DIR` 解析为包含此加载的 `SKILL.md` 的目录。
2. 验证 `SKILL_DIR/scripts/prepare_paper.py` 存在。
3. 通过其解析路径运行精确的捆绑脚本：

```text
python "SKILL_DIR/scripts/prepare_paper.py" INPUT \
  --output WORKDIR/source_bundle.json
```

需要视觉页面审查时，添加 `--render-dir WORKDIR/rendered-pages`。在起草之前，检查脚本退出代码和捆绑验证块。

对于源图输入，还检查 `locator_summary` 和 `unlocated_blocks`。只有 `pages` 下面的记录有经过验证的正 PDF 页面定位器。丢失或无效的页面定位器保留在 `unlocated_blocks` 中，带有明确的状态，必须结构化引用，绝不能作为第 1 页引用。

在 Paper Card 运行期间，永远不要编写内联 Python、临时提取脚本或替换脚本。在正常的 Paper Card 运行期间，永远不要修补捆绑脚本。只有在用户明确要求开发、调试或改进技能本身时，才修改这些脚本。

使用固定的定位器状态机：

- `page-grounded`：捆绑脚本成功并验证可靠的 PDF 页面索引。使用 PDF 页面加上结构定位器。打印页面标签是可选的元数据。
- `structure-grounded`：页面提取不可靠，但可靠的章节、图表、表格、方程式、源块或完整文本仍然可用。不要发出页面编号引用。
- `source-limited`：只有摘要、元数据或用户提供的摘录是可靠的。不要发出页面编号引用或推断未见证据。

如果准备失败，记录失败。优先选择现有的 `nature-reader` 源图或环境 PDF/OCR 功能，但不要创建替换脚本。然后进入最强支持的后备模式。

### 3. 分类论文类型

使用清单选择一个主要的 `paper_type`，并且只有对于真正混合的论文，选择一个次要的贡献透镜：

- `methods`
- `discovery`
- `resource`
- `clinical`
- `materials`
- `review`

加载主要片段，并且不超过一个次要片段。根据论文的论证和证据结构进行分类，而不仅仅是其学科。在分析之前声明这两个选择。例如，一篇介绍大量数据集的算法论文可以使用 `methods` 作为主要透镜，并将 `resource` 作为次要透镜。

### 4. 在起草之前构建证据库

在起草之前构建内部证据清单。至少列举：

- 文献元数据和访问状态；
- 研究问题和声称的贡献；
- 方法组件、假设和数据流；
- 每个主要图表、表格和必要方程式及其论证作用；
- 实验、基线、指标、消融和报告结果；
- 作者声明的局限性；
- 到页面、章节、方程式、图表、表格或 `nature-reader` 块 ID 的稳定源指针。

然后构建一个紧凑的声明-证据矩阵，将每个中心声明链接到支持它的证据以及任何未解决的差距。

仅在 04 节、15 节、文献验证或显式新颖性检查时使用外部搜索。永远不要将论文自己的相关工作叙述作为独立验证的领域历史呈现。记录上下文模式是 `paper-only`、`targeted external check` 还是 `externally verified`。

### 5. 生成固定的 01-16 Paper Card

按顺序应用：

1. 核心原则；
2. 选定的纸型片段；
3. 核心工作流程；
4. 输出合同。

在做出分析或外部验证声明之前，阅读 [references/evidence-and-provenance.md](references/evidence-and-provenance.md)。在起草最终 Markdown 时，阅读 [references/card-schema.md](references/card-schema.md)。在写 16 节之前，阅读 [references/research-idea-gates.md](references/research-idea-gates.md)。

编写真实的 Markdown 工件，默认为 `paper-card.md`。保持所有 16 个编号部分按顺序排列，但写 `Not applicable` 或 `Not assessable` 而不是编造内容。

默认匹配用户语言。技能源和模式保持英语，但在用户使用其他语言时，本地化 Paper Card 标题和散文。保留规范的技术术语和公式。

### 6. 运行基于证据的 QA

在交付之前，从 `SKILL_DIR` 解析捆绑审计器。在 `page-grounded` 模式下，运行：

```text
python "SKILL_DIR/scripts/audit_paper_card.py" \
  --card WORKDIR/paper-card.md \
  --bundle WORKDIR/source_bundle.json \
  --locator-mode page-grounded \
  --report WORKDIR/audit-report.json
```

在任何后备模式下，运行相同的审计器而不带捆绑：

```text
python "SKILL_DIR/scripts/audit_paper_card.py" \
  --card WORKDIR/paper-card.md \
  --locator-mode structure-grounded-or-source-limited \
  --report WORKDIR/audit-report.json
```

用实际规范模式替换最后一个值。将审计错误视为阻断器。用科学判断审查警告，而不是机械地抑制它们。

还验证：

- 数值结果与源匹配；
- 证据清单涵盖每个主要图表和表格；
- 每个主要方法、结果、边界和局限性都有一个源指针；
- PDF 页面指针区分 PDF 页面索引和打印页面标签；
- 作者声明与 Agent 分析分开；
- 外部领域历史声明有外部引用或标记为未验证；
- 提出的想法是假设，不是新颖性声明；
- 17 节和 18 节不存在；
- 没有添加学术英语集合、理解测验或公共文章草稿。

如果审计器本身无法运行，声明该失败，并手动应用其记录的检查。不要编写替代审计器。

## 脚本红线

- 不要将捆绑脚本相对于用户的当前工作目录解析。
- 不要编写或执行内联 Python 作为捆绑脚本的替代。
- 不要创建 `extract_pdf.py`、`parse_paper.py` 或其他一次性替换脚本。
- 在正常 Paper Card 生成请求期间，不要修补技能代码。
- 准备失败时，不要编造页码。
- 在后备模式下，不要移除所有基于证据；使用结构定位器或显式源范围定位器。

## 与相邻技能的关系

- 使用 `nature-reader` 进行全文双语阅读工件、提取和稳定源图。
- 当需要外部文献验证领域历史或知识连接时，使用 `nature-academic-search`。
- 使用 `nature-reviewer` 进行正式的审稿式手稿评估。
- 使用 `nature-literature-pipeline` 进行批量发现和轻量级监控笔记。
- 当请求的最终产品是演示文稿时，使用 `nature-paper2ppt`。

不要将请求的 Paper Card 静默切换为其中任何一种输出。
