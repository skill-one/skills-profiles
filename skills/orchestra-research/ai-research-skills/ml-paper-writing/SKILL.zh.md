---
name: ml-paper-writing
description: 为 NeurIPS、ICML、ICLR、ACL、AAAI、COLM 撰写符合发表标准的机器学习/人工智能论文。在从研究代码库撰写论文、构建论证、核实引用或准备最终提交版本时使用。对于系统会议（OSDI、NSDI、ASPLOS、SOSP），请使用 systems-paper-writing。
---

# 顶级AI会议论文写作指南

针对**NeurIPS、ICML、ICLR、ACL、AAAI、COLM**等顶级AI会议的专家级论文写作指导。这项技能融合了顶尖研究者的写作理念（如Nanda、Farquhar、Karpathy、Lipton、Steinhardt）以及实用工具：LaTeX模板、引用验证API和会议检查清单。

**对于系统会议（OSDI、NSDI、ASPLOS、SOSP）**，请使用[systems-paper-writing](../systems-paper-writing/)技能，该技能提供段落级别的结构蓝图、写作模式、特定会议的检查清单和系统会议的LaTeX模板。

## 核心理念：协作式写作

**论文写作是协作性的，但Claude应在提供初稿方面保持主动。**

典型的流程始于一个包含代码、结果和实验工件的研究代码库。Claude的角色是：

1. **理解项目**：通过探索代码库、结果和现有文档
2. **在自信于贡献时交付完整的初稿**
3. **使用网络搜索和API搜索文献**以找到相关引用
4. **在科学家提供输入时进行反馈循环**进行完善
5. **仅在真正不确定关键决策时才寻求澄清**

**关键原则**：保持主动。如果代码库和结果清晰，就交付完整的初稿。不要因等待每个部分的反馈而阻塞——科学家们很忙。产出一些具体的内容供他们反应，然后根据他们的反馈进行迭代。

---

## ⚠️ 关键：切勿凭空捏造引用

**这是使用AI辅助进行学术写作的最重要规则。**

### 问题

AI生成的引用错误率约为**40%**。凭空捏造的参考文献——不存在的论文、错误的作者、不正确的年份、编造的DOI——是一种严重的学术不端行为，可能导致直接拒稿或撤稿。

### 规则

**绝对不要凭记忆生成BibTeX条目。必须程序化获取。**

| 操作 | 正确 | 错误 |
|------|------|------|
| 添加引用 | 搜索API → 验证 → 获取BibTeX | 凭记忆编写BibTeX |
| 不确定论文 | 标记为`[CITATION NEEDED]` | 猜测引用 |
| 找不到确切论文 | 注明："占位符 - 需要验证" | 编造类似名称的论文 |

### 无法验证引用时

如果你无法程序化地验证引用，你必须：

```latex
% 明确占位符 - 需要人工验证
\cite{PLACEHOLDER_author2024_verify_this}  % TODO: 验证此引用是否存在
```

**务必告知科学家**："我已经将[X]个引用标记为需要验证的占位符。我无法确认这些论文是否存在。"

### 推荐安装Exa MCP进行论文搜索

为了获得最佳的论文搜索体验，请安装**Exa MCP**，它提供实时学术搜索功能：

**Claude代码：**
```bash
claude mcp add exa -- npx -y mcp-remote "https://mcp.exa.ai/mcp"
```

**Cursor / VS Code**（添加到MCP设置）：
```json
{
  "mcpServers": {
    "exa": {
      "type": "http",
      "url": "https://mcp.exa.ai/mcp"
    }
  }
}
```

Exa MCP支持以下搜索：
- "查找2023年后发表的语言模型RLHF论文"
- "搜索Vaswani的Transformer架构论文"
- "获取关于稀疏自动编码器可解释性的最新研究"

然后用Semantic Scholar API验证结果，通过DOI获取BibTeX。

---

## 从研究代码库开始的工作流程

开始论文写作时，首先理解项目：

```
项目理解：
- [ ] 步骤1：探索代码库结构
- [ ] 步骤2：阅读README、现有文档和关键结果
- [ ] 步骤3：与科学家一起确定主要贡献
- [ ] 步骤4：查找代码库中已引用的论文
- [ ] 步骤5：搜索更多相关文献
- [ ] 步骤6：共同勾勒论文结构
- [ ] 步骤7：与反馈迭代撰写各部分
```

**步骤1：探索代码库**

```bash
# 理解项目结构
ls -la
find . -name "*.py" | head -20
find . -name "*.md" -o -name "*.txt" | xargs grep -l -i "result\|conclusion\|finding"
```

寻找：
- `README.md` - 项目概述和主张
- `results/`, `outputs/`, `experiments/` - 关键发现
- `configs/` - 实验设置
- 现有的`.bib`文件或引用参考
- 任何草稿文档或笔记

**步骤2：识别现有引用**

检查代码库中已引用的论文：

```bash
# 查找现有引用
grep -r "arxiv\|doi\|cite" --include="*.md" --include="*.bib" --include="*.py"
find . -name "*.bib"
```

这些是高信号的开端，用于相关工作——科学家已经认为它们是相关的。

**步骤3：明确贡献**

在写作前，明确与科学家确认：

> "根据我对代码库的理解，主要贡献似乎是[X]。
> 关键结果显示[Y]。这是否是你希望论文的框架，
> 或者我们应该强调不同的方面？"

**切勿假设叙事——始终与人类确认。**

**步骤4：搜索更多文献**

使用网络搜索查找相关论文：

```
搜索查询尝试：
- "[主要技术] + [应用领域]"
- "[基线方法]比较"
- "[问题名称]当前最佳"
- 现有引用中的作者姓名
```

然后使用下文的引用工作流程进行验证和获取BibTeX。

**步骤5：交付初稿**

**保持主动——交付完整的初稿，而不是请求每个部分的许可。**

如果代码库提供清晰的结果且贡献明显：
1. 撰写完整的初稿端到端
2. 提交完整初稿以供反馈
3. 根据科学家的响应进行迭代

如果确实不确定框架或主要主张：
1. 撰写你能自信的部分
2. 标记具体的不确定性："我将X作为主要贡献——如果你更喜欢强调Y，请告诉我"
3. 继续撰写初稿而不是阻塞

**初稿中应包含的问题**（在提交前不要包含）：
- "我强调X作为主要贡献——如有需要请调整"
- "我突出结果A、B、C——请告诉我哪些更重要"
- "相关工作部分包括[papers]——我遗漏了哪些"

---

## 使用此技能的时机

在以下情况下使用此技能：
- **从研究代码库开始撰写论文**
- **起草或修改**特定部分
- **查找和验证**相关工作的引用
- **提交会议的格式化**
- **转投**到不同会议（格式转换）
- **与科学家反馈迭代**草稿

**始终记住**：初稿是讨论的起点，不是最终输出。

---

## 平衡主动性与协作

**默认：保持主动。交付草稿，然后迭代。**

| 置信水平 | 操作 |
|----------|------|
| **高**（代码库清晰，贡献明显） | 撰写完整草稿，交付，根据反馈迭代 |
| **中**（存在一些模糊性） | 撰写草稿并标记不确定性，继续 |
| **低**（存在重大未知数） | 提问1-2个有针对性的问题，然后草稿 |

**先草稿，后提问**（在提交前不要提问）：

| 部分 | 自主草稿 | 与草稿一起标记 |
|------|----------|----------------|
| 摘要 | 是 | "将贡献框架为X——如有需要请调整" |
| 引言 | 是 | "强调问题Y——如果错误请纠正" |
| 方法 | 是 | "包含细节A、B、C——添加缺失部分" |
| 实验 | 是 | "突出结果1、2、3——如有需要请重新排序" |
| 相关工作 | 是 | "引用论文X、Y、Z——添加我遗漏的" |

**仅在以下情况阻塞输入：**
- 目标会议不明确（影响页限制、框架）
- 多个看似同样有效的矛盾框架
- 结果似乎不完整或不一致
- 明确请求在继续前进行审查

**不要阻塞：**
- 词语选择决策
- 部分排序
- 显示哪些具体结果（做出选择，标记它）
- 引用完整性（根据你找到的内容草稿，注明差距）

---

## 叙事原则

**最关键的理解**：你的论文不是实验的集合——它是一个有明确贡献、由证据支持的故事。

每篇成功的ML论文都围绕Neel Nanda所说的"叙事"展开：一个简短、严谨、基于证据的技术故事，有一个读者关心的要点。

**三个支柱（在引言结束时必须清晰）：**

| 支柱 | 描述 | 示例 |
|------|------|------|
| **是什么** | 1-3个特定的新主张，具有连贯主题 | "我们证明X在条件Z下实现了Y" |
| **为什么** | 支持主张的严谨经验证据 | 强大的基线、区分假设的实验 |
| **意义何在** | 读者应该为什么关心 | 与公认的社区问题联系 |

**如果你不能用一句话陈述你的贡献，你还没有完成论文。**

---

## 论文结构工作流程

### 工作流程1：撰写完整论文（迭代）

复制此清单并跟踪进度。**每个步骤都涉及草稿 → 反馈 → 修订：**

```
论文写作进度：
- [ ] 步骤1：与科学家定义一句话的贡献
- [ ] 步骤2：草稿图1 → 获取反馈 → 修订
- [ ] 步骤3：草稿摘要 → 获取反馈 → 修订
- [ ] 步骤4：草稿引言 → 获取反馈 → 修订
- [ ] 步骤5：草稿方法 → 获取反馈 → 修订
- [ ] 步骤6：草稿实验 → 获取反馈 → 修订
- [ ] 步骤7：草稿相关工作 → 获取反馈 → 修订
- [ ] 步骤8：草稿局限性 → 获取反馈 → 修订
- [ ] 步骤9：完整论文检查清单（必需）
- [ ] 步骤10：最终审查周期和提交
```

**步骤1：定义一句话的贡献**

**此步骤需要科学家的明确确认。**

在撰写任何内容之前，阐明并验证：
- 你的论文贡献的是什么？
- 在你的工作之前，什么是不明显的或存在的？

> "我建议将贡献框架为：'[一句话]'. 这是否捕捉到你视为主要要点的核心？
> 我们是否需要调整重点？"

**步骤2：草稿图1**

图1值得特别关注——许多读者会直接跳过它。
- 传达核心思想、方法或最吸引人的结果
- 使用矢量图形（PDF/EPS用于绘图）
- 撰写独立于正文的自述
- 确保在黑白环境下可读（8%的男性有色觉缺陷）

**步骤3：撰写摘要（五句公式）**

来自Sebastian Farquhar（DeepMind）：

```
1. 你实现了什么： "我们引入..."、"我们证明..."、"我们展示了..."
2. 为什么这很难且重要
3. 你是如何做的（使用专业关键词以提高可发现性）
4. 你有什么证据
5. 你最显著的数字/结果
```

**删除**通用的开头，如"大型语言模型取得了惊人的成功..."

**步骤4：撰写引言（最多1-1.5页）**

必须包括：
- 2-4个贡献点列表（每点最多1-2行，两栏格式）
- 清晰的问题陈述
- 简要的方法概述
- 方法部分应在第2-3页最多

**步骤5：方法部分**

实现可重放性：
- 概念性概述或伪代码
- 列出所有超参数
- 架构细节足以进行复现
- 展示最终设计决策；消融实验放在实验部分

**步骤6：实验部分**

对于每个实验，明确说明：
- 它支持什么主张
- 它如何与主要贡献相关
- 实验设置（附录中有详细信息）
- 观察什么："蓝线显示X，这表明Y"

要求：
- 带有方法的误差线（标准差与标准误差）
- 超参数搜索范围
- 计算基础设施（GPU类型，总小时数）
- 种子设置方法

**步骤7：相关工作**

按方法组织，而不是按论文组织：

**好**："一条研究线使用Floogledoodle的假设[参考文献]，而我们使用Doobersnoddle的假设，因为..."

**差**："Snap等人引入了X，而Crackle等人引入了Y。"

慷慨引用——审稿人可能撰写了相关的论文。

**步骤8：局限性部分（必需）**

所有主要会议都要求这部分。反直觉地，诚实有助于：
- 审稿人被指示不要因诚实承认局限性而扣分
- 通过首先识别弱点来预判批评
- 解释为什么局限性不会削弱核心主张

**步骤9：论文检查清单**

NeurIPS、ICML和ICLR都要求论文检查清单。参见[references/checklists.md](references/checklists.md)。

---

## 顶级ML会议的写作理念

**本节提炼了来自顶尖ML研究者的最重要写作原则。** 这些不是可选的样式建议——它们是区分被接受论文和被拒论文的因素。

> "一篇论文是一个简短、严谨、基于证据的技术故事，有一个读者关心的要点。" — Neel Nanda

### 源自此指导的来源

这项技能综合了在顶级会议发表过多论文的研究者的写作理念：

| 来源 | 主要贡献 | 链接 |
|------|----------|------|
| **Neel Nanda**（谷歌DeepMind） | 叙事原则，What/Why/So What框架 | [如何撰写ML论文](https://www.alignmentforum.org/posts/eJGptPbbFPZGLpjsp/highly-opinionated-advice-on-how-to-write-ml-papers) |
| **Sebastian Farquhar**（DeepMind） | 5句摘要公式 | [如何撰写ML论文](https://sebastianfarquhar.com/on-research/2024/11/04/how_to_write_ml_papers/) |
| **Gopen & Swan** | 读者期望的7个原则 | [科学写作的科学](https://cseweb.ucsd.edu/~swanson/papers/science-of-writing.pdf) |
| **Zachary Lipton** | 词语选择，消除犹豫 | [科学写作的启发式方法](https://www.approximatelycorrect.com/2018/01/29/heuristics-technical-scientific-writing-machine-learning-perspective/) |
| **Jacob Steinhardt**（加州大学伯克利分校） | 精确性，一致术语 | [写作技巧](https://bounded-regret.ghost.io/) |
| **Ethan Perez**（Anthropic） | 微观层面清晰技巧 | [轻松论文写作技巧](https://ethanperez.net/easy-paper-writing-tips/) |
| **Andrej Karpathy** | 单一贡献焦点 | 各种讲座 |

**要深入了解任何内容，请参阅：**
- [references/writing-guide.md](references/writing-guide.md) - 带有示例的完整解释
- [references/sources.md](references/sources.md) - 完整参考书目

### 时间分配（来自Neel Nanda）

在以下方面大约**平均分配时间**：
1. 摘要
2. 引言
3. 图表
4. 其他部分合并

**为什么？** 大多数审稿人在看到你的方法之前就形成了判断。读者遇到你的论文的顺序是：**标题 → 摘要 → 引言 → 图表 → 也许其他部分。**

### 写作风格指南

#### 句子级清晰度（Gopen & Swan的7个原则）

这些原则基于读者实际如何处理文本。违反这些原则会迫使读者在结构上花费认知努力，而不是内容。

| 原则 | 规则 | 示例 |
|------|------|------|
| **主语-动词邻近性** | 保持主语和动词靠近 | ❌ "模型，它是在...训练的，实现了" → ✅ "模型在训练后实现了..." |
| **强调位置** | 将重点放在句子末尾 | ❌ "使用注意力时，准确率提高了15%" → ✅ "使用注意力时，准确率**提高了15%**" |
| **主题位置** | 先放背景，再放新信息 | ✅ "在这些约束下，我们提出了..." |
| **旧信息在前** | 熟悉信息 → 新信息 | 向后链接，然后引入新内容 |
| **一个单元，一个功能** | 每个段落只做一个点 | 分割多点的段落 |
| **动词中使用动作** | 使用动词，而不是名词化 | ❌ "我们进行了分析" → ✅ "我们分析了" |
| **背景在前** | 先设置场景，再展示方程 | |

**包含详细示例的完整7原则**：参见[references/writing-guide.md](references/writing-guide.md#读者期望的7原则)

#### 微观层面技巧 (Ethan Perez)

这些微小的改动会积累成显著更清晰的文风：

- **最小化代词**：❌ "这显示了..." → ✅ "这个结果显示了..."
- **动词前置**：将动词放在句子开头
- **展开撇号**：❌ "X's Y" → ✅ "X的Y"（当不合适时）
- **删除填充词**："实际上," "有点," "非常," "真正地," "基本上," "相当," "本质上"

**包含示例的完整微观技巧**：参见[references/writing-guide.md](references/writing-guide.md#微观写作技巧)

#### 词语选择 (Zachary Lipton)

- **具体化**：❌ "性能" → ✅ "准确率"或"延迟"（说出你的意思）
- **消除犹豫**：除非确实不确定，否则删除"可能"和"可以"
- **避免增量词汇**：❌ "组合," "修改," "扩展" → ✅ "开发," "提出," "引入"
- **删除强化词**：❌ "提供*非常*紧密的近似" → ✅ "提供紧密的近似"

#### 精确性胜于简洁性 (Jacob Steinhardt)

- **术语一致**：同一概念的不同术语会造成混淆。选择一个并坚持使用。
- **正式陈述假设**：在定理之前，明确列出所有假设
- **直观解释+严谨性**：提供直观的解释，同时提供正式的证明

### 审稿人实际阅读的内容

理解审稿人的行为有助于优先考虑你的工作：

| 论文部分 | 百分比审稿人阅读 | 含义 |
|---------|------------------|------|
| 摘要 | 100% | 必须完美 |
| 引言 | 90%+（略读） | 前置贡献 |
| 图表 | 方法之前检查 | 图1至关重要 |
| 方法 | 只有感兴趣才阅读 | 不要埋没主要信息 |
| 附录 | 很少 | 只放补充细节 |

**底线**：如果你的摘要和引言没有吸引审稿人，他们可能永远不会阅读你出色的方法部分。

---

## 会议要求快速参考

### 机器学习/人工智能会议

| 会议 | 页面限制 | 摄影版额外页数 | 关键要求 |
|------|----------|----------------|----------|
| **NeurIPS 2025** | 9页 | +0 | 强制检查清单，接受后必须有非技术性摘要 |
| **ICML 2026** | 8页 | +1 | 需要更广泛的影响声明 |
| **ICLR 2026** | 9页 | +1 | 需要LLM披露，互惠审稿 |
| **ACL 2025** | 8页（长） | 变化 | 强制要求局限性部分 |
| **AAAI 2026** | 7页 | +1 | 严格遵循样式文件 |
| **COLM 2025** | 9页 | +1 | 专注于语言模型 |

**系统会议（OSDI, NSDI, ASPLOS, SOSP）**：参见[systems-paper-writing](../systems-paper-writing/)技能了解页面限制、模板、截止日期和提交规则。

**通用要求**：
- 双盲审稿（匿名化提交）
- 参考文献不计入页面限制
- 附录无限但审稿人不必阅读
- 所有场合都需要LaTeX

**LaTeX模板**：参见[templates/](templates/)目录获取所有会议模板。

---

## 正确使用LaTeX模板

### 工作流程4：从模板开始新论文

**始终先复制整个模板目录，然后在其中编写。**

```
模板设置清单：
- [ ] 步骤1：将整个模板目录复制到新项目
- [ ] 步骤2：验证模板在未做任何更改的情况下可以编译
- [ ] 步骤3：阅读模板的示例内容以了解结构
- [ ] 步骤4：逐段替换示例内容
- [ ] 步骤5：保留模板注释/示例作为参考，直到完成
- [ ] 步骤6：仅在最后清理模板文件
```

**步骤1：复制完整模板**

```bash
# 创建包含完整模板的论文目录
cp -r templates/neurips2025/ ~/papers/my-new-paper/
cd ~/papers/my-new-paper/

# 验证结构是否完整
ls -la
# 应该看到：main.tex, neurips.sty, Makefile, 等等
```

**⚠️ 重要提示**：复制整个目录，而不仅仅是`main.tex`。模板包括：
- 样式文件（`.sty`）- 编译所需
- 参考文献样式（`.bst`）- 参考文献所需
- 示例内容 - 有用作参考
- Makefiles - 用于轻松编译

**步骤2：首先验证模板可以编译**

在做出任何更改之前，先编译未修改的模板：

```bash
# 使用latexmk（推荐）
latexmk -pdf main.tex

# 或手动编译
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

如果未修改的模板无法编译，请先修复。常见问题：
- 缺少TeX包 → 通过`tlmgr install <package>`安装
- TeX发行版不正确 → 使用TeX Live（推荐）

**步骤3：保留模板内容作为参考**

不要立即删除所有示例内容。相反：

```latex
% 保留模板示例作为注释，边编写边参考
% 这显示了预期的格式

% 模板示例（保留以供参考）：
% \begin{figure}[t]
%   \centering
%   \includegraphics[width=0.8\linewidth]{example-image}
%   \caption{模板显示标题样式}
% \end{figure}

% 你的实际图表：
\begin{figure}[t]
  \centering
  \includegraphics[width=0.8\linewidth]{your-figure.pdf}
  \caption{遵循相同样式的标题。}
\end{figure}
```

**步骤4：逐段替换内容**

系统地处理论文：

```
替换顺序：
1. 标题和作者（提交时匿名化）
2. 摘要
3. 引言
4. 方法
5. 实验
6. 相关工作
7. 结论
8. 参考文献（你的.bib文件）
9. 附录
```

对于每个部分：
1. 阅读模板的示例内容
2. 注意任何特殊格式或宏
3. 按照相同的模式替换你的内容
4. 频繁编译以尽早发现错误

**步骤5：使用模板宏**

模板通常定义有用的宏。检查前言中的：

```latex
% 常用模板宏：
\newcommand{\method}{YourMethodName}  % 一致的方法命名
\newcommand{\eg}{e.g.,\xspace}        % 正确的缩写
\newcommand{\ie}{i.e.,\xspace}
\newcommand{\etal}{\textit{et al.}\xspace}
```

**步骤6：仅在最后清理**

仅在论文几乎完成时删除模板文件：

```latex
% 提交前 - 删除这些：
% - 注释掉的模板示例
% - 未使用的包
% - 模板的示例图表/表格
% - 洞察文或占位符文本

% 保留这些：
% - 所有样式文件（.sty）
% - 参考文献样式（.bst）
% - 模板中的必要包
% - 你正在使用的任何自定义宏
```

### 应避免的模板陷阱

| 陷阱 | 问题 | 解决方案 |
|------|------|----------|
| 只复制`main.tex` | 缺少`.sty`，无法编译 | 复制整个目录 |
| 修改`.sty`文件 | 破坏会议格式 | 不要编辑样式文件 |
| 添加随机包 | 冲突，破坏模板 | 只有在必要时添加 |
| 过早删除模板内容 | 丢失格式参考 | 作为注释保留，直到完成 |
| 不频繁编译 | 错误累积 | 每个部分后编译 |

### 快速模板参考

#### 机器学习/人工智能会议

| 会议 | 主文件 | 关键样式文件 | 备注 |
|------|--------|--------------|------|
| NeurIPS 2025 | `main.tex` | `neurips.sty` | 有Makefile |
| ICML 2026 | `example_paper.tex` | `icml2026.sty` | 包括算法包 |
| ICLR 2026 | `iclr2026_conference.tex` | `iclr2026_conference.sty` | 需要数学命令文件 |
| ACL | `acl_latex.tex` | `acl.sty` | 严格格式 |
| AAAI 2026 | `aaai2026-unified-template.tex` | `aaai2026.sty` | 严格遵守样式文件 |
| COLM 2025 | `colm2025_conference.tex` | `colm2025_conference.sty` | 类似ICLR |

**系统会议模板**（OSDI, NSDI, ASPLOS, SOSP）：参见[systems-paper-writing](../systems-paper-writing/)技能。

---

## 会议重新提交和格式转换

当一篇论文被一个会议拒绝或撤回，并重新提交到另一个会议时，需要格式转换。这是机器学习研究中的一种常见工作流程。

### 工作流程3：在会议格式之间转换

```
格式转换清单：
- [ ] 步骤1：识别源和目标模板的差异
- [ ] 步骤2：创建使用目标模板的新项目
- [ ] 步骤3：复制内容部分（不是前言）
- [ ] 步骤4：调整页面限制和内容
- [ ] 步骤5：更新会议特定要求
- [ ] 步骤6：验证编译和格式
```

**步骤1：关键模板差异**

#### 机器学习/人工智能转换

| 从→到 | 页面变化 | 关键调整 |
|------|----------|----------|
| NeurIPS→ICML | 9→8页 | 删减1页，如果缺少更广泛的影响声明 |
| ICML→ICLR | 8→9页 | 可以扩展实验，添加LLM披露 |
| NeurIPS→ACL | 9→8页 | 重新结构化以适应NLP惯例，添加局限性部分 |
| ICLR→AAAI | 9→7页 | 需要大幅删减，严格样式遵守 |
| 任何→COLM | 变化→9页 | 重新调整以关注语言模型 |

**机器学习→系统转换**：转换为OSDI、NSDI、ASPLOS或SOSP时，参见[systems-paper-writing](../systems-paper-writing/)技能了解格式转换指南、模板和结构差异。

**步骤2：内容迁移（不是模板合并）**

**绝对不要在模板之间复制LaTeX前言。** 相反：

```bash
# 1. 使用目标模板开始新提交
cp -r templates/icml2026/ new_submission/

# 2. 从旧论文复制仅内容部分
# - 摘要文本
# - 部分内容（在\section{}命令之间）
# - 图表和表格
# - 参考文献条目

# 3. 粘贴到目标模板结构
```

**步骤3：调整页面限制**

当删减页面（例如，NeurIPS 9→AAAI 7）时：
- 将详细证明移至附录
- 精简相关工作（引用综述而不是单个论文）
- 合并类似实验为统一表格
- 使用较小的图表尺寸和子图表
- 紧凑写作：消除冗余，使用主动语态

当扩展（例如，ICML 8→ICLR 9）时：
- 添加审稿人要求的消融研究
- 扩展局限性讨论
- 添加更多基线
- 添加定性示例

**步骤4：会议特定调整**

#### 机器学习/人工智能会场

| 目标会场 | 需要添加的内容 |
|----------|---------------|
| **ICML** | 更广泛的影响声明（结论之后） |
| **ICLR** | LLM使用披露，互惠审稿协议 |
| **ACL/EMNLP** | 局限性部分（强制），伦理声明 |
| **AAAI** | 严格遵守样式文件（不允许修改） |
| **NeurIPS** | 论文检查清单（附录），如果接受，必须有非技术性摘要 |

**系统会场**（OSDI, NSDI, ASPLOS, SOSP）：参见[systems-paper-writing](../systems-paper-writing/)技能了解会场特定要求、清单和审稿人指南。

**步骤5：更新参考文献**

```latex
% 删除揭示身份的自引（用于盲审）
% 更新任何"审稿中"的引用为已发表版本
% 添加自上次提交以来发表的相关新工作
```

**步骤6：处理先前审稿意见**

在拒绝后重新提交时：
- **要**在修订版中回应审稿人意见
- **要**添加审稿人要求的实验/澄清
- **不要**包含"与先前提交的更改"部分（盲审）
- **不要**引用先前提交或审稿意见

**常见转换陷阱**：
- ❌ 复制`\usepackage`命令（导致冲突）
- ❌ 保留旧会议页眉/页脚命令
- ❌ 忘记更新`\bibliography{}`路径
- ❌ 遗漏会议特定必需部分
- ❌ 删减后超过页面限制

---

## 引用工作流程（防止幻觉）

**⚠️ 关键**：AI生成的引用错误率高达40%。**永远不要凭记忆写BibTeX。**

### 金科玉律

```
如果你不能程序化获取引用：
    → 标记为[CITATION NEEDED]或[PLACEHOLDER - 需要验证]
    → 明确告知科学家
    → **永远不要**编造听起来合理的参考文献
```

### 工作流程2：添加引用

```
引用验证（每个引用的强制要求）：
- [ ] 步骤1：使用Exa MCP或Semantic Scholar API搜索
- [ ] 步骤2：在Semantic Scholar和arXiv/CrossRef中验证论文存在
- [ ] 步骤3：通过DOI程序化获取BibTeX
- [ ] 步骤4：验证你引用的声明确实出现在论文中
- [ ] 步骤5：将验证的BibTeX添加到参考文献
- [ ] 步骤6：如果任何步骤失败→标记为占位符，通知科学家
```

**步骤0：使用Exa MCP进行初始搜索（推荐）**

如果安装了Exa MCP，使用它查找相关论文：
```
搜索："RLHF语言模型对齐2023"
搜索："稀疏自动编码器可解释性"
搜索："注意力机制Transformer Vaswani"
```

然后使用Semantic Scholar验证每个结果并通过DOI获取BibTeX。

**步骤1：搜索Semantic Scholar**

```python
from semanticscholar import SemanticScholar
sch = SemanticScholar()
results = sch.search_paper("注意力机制Transformer", limit=5)
for paper in results:
    print(f"{paper.title} - {paper.paperId}")
    print(f"  DOI: {paper.externalIds.get('DOI', 'N/A')}")
```

**步骤2：验证存在**

确认论文至少出现在两个来源（Semantic Scholar + CrossRef/arXiv）。

**步骤3：通过DOI获取BibTeX**

```python
import requests

def doi_to_bibtex(doi: str) -> str:
    """通过CrossRef获取验证的BibTeX。"""
    response = requests.get(
        f"https://doi.org/{doi}",
        headers={"Accept": "application/x-bibtex"}
    )
    response.raise_for_status()
    return response.text

# 示例
bibtex = doi_to_bibtex("10.48550/arXiv.1706.03762")
print(bibtex)
```

**步骤4：验证声明**

在为特定声明引用之前，访问论文并确认所归因的声明确实出现。

**步骤5：明确处理失败**

在任何步骤无法验证引用时：

```latex
% 选项1：明确占位符
\cite{PLACEHOLDER_smith2023_verify}  % 无法验证 - 科学家必须确认

% 选项2：在文本中注明
...如先前工作所示[CITATION NEEDED - 无法验证Smith等人2023年].
```

**始终通知科学家**：
> "我无法验证以下引用，并已将其标记为占位符：
> - Smith等人2023年关于奖励攻击 - 无法在Semantic Scholar中找到
> - Jones 2022年关于规模法则 - 找到类似论文但作者不同
> 请在提交前验证这些。"

### 摘要：引用规则

| 情况 | 动作 |
|------|------|
| 找到论文，获取DOI，获取BibTeX | ✅ 使用该引用 |
| 找到论文，没有DOI | ✅ 使用arXiv BibTeX或手动从论文中输入 |
| 论文存在但无法获取BibTeX | ⚠️ 标记占位符，通知科学家 |
| 不确定论文是否存在 | ❌ 标记[CITATION NEEDED]，通知科学家 |
| "我认为关于X有一篇论文" | ❌ **绝对不要引用** - 先搜索或标记占位符 |

**🚨 永远不要凭记忆生成BibTeX——总是程序化获取。 🚨**

参见[references/citation-workflow.md](references/citation-workflow.md)获取完整的API文档。

---

## 常见问题和解决方案

**问题：摘要过于笼统**

如果第一句可以是任何机器学习论文的前言，请删除它。从你的具体贡献开始。

**问题：引言超过1.5页**

将背景分为相关工作。前置贡献要点。方法应从第2-3页开始。

**问题：实验缺乏明确声明**

在每次实验之前添加句子："这个实验测试了[具体声明]..."

**问题：审稿人发现论文难以理解**

- 添加明确的指示： "在本节中，我们展示了X"
- 使用一致术语
- 包含自包含的图表标题

**问题：缺少统计显著性**

始终包括：
- 误差线（指定：标准差或标准误差）
- 运行次数
- 如果比较方法，则进行统计检验

---

## 审稿人评估标准

审稿人从四个维度评估论文：

| 标准 | 审稿人关注点 |
|------|--------------|
| **质量** | 技术严谨性，有充分支持的论点 |
| **清晰度** | 清晰的写作，可被专家复现 |
| **重要性** | 社区影响，推动理解 |
| **原创性** | 新的见解（不需要新方法） |

**评分（NeurIPS 6分制）：**
- 6：强烈接受 - 创新性，无瑕疵
- 5：接受 - 技术可靠，高影响力
- 4：边缘接受 - 基础扎实，评估有限
- 3：边缘拒绝 - 基础扎实但弱点突出
- 2：拒绝 - 技术缺陷
- 1：强烈拒绝 - 已知结果或伦理问题

参见 [references/reviewer-guidelines.md](references/reviewer-guidelines.md) 获取详细的审稿人指南。

---

## 表格和图表

### 表格

使用 `booktabs` LaTeX 包创建专业表格：

```latex
\usepackage{booktabs}
\begin{tabular}{lcc}
\toprule
方法 & 准确度 ↑ & 延迟 ↓ \\
\midrule
基线 & 85.2 & 45ms \\
\textbf{我们} & \textbf{92.1} & 38ms \\
\bottomrule
\end{tabular}
```

**规则：**
- 每个指标的最佳值加粗
- 包含方向符号（↑ 更高更好，↓ 更低更好）
- 数值列右对齐
- 保持小数精度一致

### 图表

- **矢量图形**（PDF、EPS）用于所有图表和示意图
- **光栅**（PNG 600 DPI）仅用于照片
- 使用 **无色盲风险调色板**（Okabe-Ito 或 Paul Tol）
- 验证 **灰度可读性**（8% 的男性有色觉缺陷）
- **图表内无标题**——图注承担此功能
- **自包含图注**——读者无需正文即可理解

---

## 引用 AI 研究技能

如果这个库帮助了你的研究——无论是用于训练流程、评估、论文写作还是其他技能——请考虑在致谢或参考文献中引用它：

```bibtex
@software{ai_research_skills,
  title     = {AI Research Skills Library},
  author    = {{Orchestra Research}},
  year      = {2025},
  url       = {https://github.com/orchestra-research/AI-research-SKILLs},
  note      = {开源技能库，使 AI 代理能够自主进行 AI 研究}
}
```

在 **致谢** 部分简要提及也受欢迎：

```latex
\section*{Acknowledgments}
我们使用了 AI Research Skills Library~\cite{ai_research_skills} 进行 [实验编排 / 评估 / ...].
```

---

## 参考文献 & 资源

### 参考文献（深入阅读）

| 文档 | 内容 |
|------|------|
| [writing-guide.md](references/writing-guide.md) | Gopen & Swan 7 原则，Ethan Perez 微型技巧，用词 |
| [citation-workflow.md](references/citation-workflow.md) | 引用 API，Python 代码，BibTeX 管理 |
| [checklists.md](references/checklists.md) | NeurIPS 16 项，ICML，ICLR，ACL 要求 |
| [reviewer-guidelines.md](references/reviewer-guidelines.md) | 评估标准，评分，反驳意见 |
| [sources.md](references/sources.md) | 所有来源的完整参考文献 |

### LaTeX 模板

`templates/` 目录中的模板：
- **ML/AI**：ICML 2026，ICLR 2026，NeurIPS 2025，ACL/EMNLP，AAAI 2026，COLM 2025
- **系统**（OSDI，NSDI，ASPLOS，SOSP）：参见 [systems-paper-writing](../systems-paper-writing/) 技能

**编译为 PDF：**
- **VS Code/Cursor**：安装 LaTeX Workshop 扩展 + TeX Live → 保存自动编译
- **命令行**：`latexmk -pdf main.tex` 或 `pdflatex` + `bibtex` 工作流
- **在线**：上传至 [Overleaf](https://overleaf.com)

参见 [templates/README.md](templates/README.md) 获取详细的设置说明。

### 关键外部资源

**写作理念：**
- [Neel Nanda: 如何撰写 ML 论文](https://www.alignmentforum.org/posts/eJGptPbbFPZGLpjsp/highly-opinionated-advice-on-how-to-write-ml-papers) - 叙事，"是什么/为什么/有什么意义"
- [Farquhar: 如何撰写 ML 论文](https://sebastianfarquhar.com/on-research/2024/11/04/how_to_write_ml_papers/) - 5 句摘要
- [Gopen & Swan: 科学写作的科学](https://cseweb.ucsd.edu/~swanson/papers/science-of-writing.pdf) - 7 读者期望原则
- [Lipton: 科学写作启发式方法](https://www.approximatelycorrect.com/2018/01/29/heuristics-technical-scientific-writing-machine-learning-perspective/) - 用词
- [Perez: 简易论文写作技巧](https://ethanperez.net/easy-paper-writing-tips/) - 微观层面清晰度

**APIs**：[Semantic Scholar](https://api.semanticscholar.org/api-docs/) | [CrossRef](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) | [arXiv](https://info.arxiv.org/help/api/basics.html)

**ML/AI 会议**：[NeurIPS](https://neurips.cc/Conferences/2025/PaperInformation/StyleFiles) | [ICML](https://icml.cc/Conferences/2025/AuthorInstructions) | [ICLR](https://iclr.cc/Conferences/2026/AuthorGuide) | [ACL](https://github.com/acl-org/acl-style-files)

**系统会议**：参见 [systems-paper-writing](../systems-paper-writing/) 技能获取 OSDI、NSDI、ASPLOS、SOSP 链接和指南
