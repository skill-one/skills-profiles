# 针对顶级人工智能会议的论文写作

为**NeurIPS、ICML、ICLR、ACL、AAAI、COLM**等会议撰写目标为**发表水平**的论文的专业级指导。这项技能结合了顶尖研究人员（Nanda、Farquhar、Karpathy、Lipton、Steinhardt）的写作理念与实践工具：LaTeX模板、引用验证API和会议检查清单。

**对于系统会议（OSDI、NSDI、ASPLOS、SOSP）**，请使用**[systems-paper-writing](../systems-paper-writing/)**技能，该技能提供段落级别的结构蓝图、写作模式、特定会议的检查清单和系统会议的LaTeX模板。

## 核心理念：协作写作

**论文写作是协作的，但Claude应在交付初稿方面积极主动。**

典型的流程从一个包含代码、结果和实验工件的研究仓库开始。Claude的角色是：

1. **通过探索仓库、结果和现有文档来理解项目**
2. **在对其贡献有信心时交付完整的初稿**
3. **使用网络搜索和API搜索文献以找到相关引用**
4. **在科学家提供输入时通过反馈周期进行完善**
5. **仅在真正不确定关键决策时才寻求澄清**

**关键原则**：要积极主动。如果仓库和结果是清晰的，请交付完整的初稿。不要因为每个部分都在等待反馈而阻塞——科学家很忙。产出一些具体的东西让他们可以反应，然后根据他们的反馈进行迭代。

---

## ⚠️ 关键：永远不要虚构引用

**这是使用AI辅助进行学术写作时最重要的规则。**

### 问题

AI生成的引用有**约40%的错误率**。虚构的参考文献——不存在的论文、错误的作者、不正确的年份、编造的DOI——是一种严重的学术不端行为，可能导致直接拒稿或撤稿。

### 规则

**永远不要从记忆中生成BibTeX条目。始终以编程方式获取。**

| 操作 | ✅ 正确 | ❌ 错误 |
|------|--------|--------|
| 添加引用 | 搜索API → 验证 → 获取BibTeX | 从记忆中编写BibTeX |
| 不确定某篇论文 | 标记为`[CITATION NEEDED]` | 猜测参考文献 |
| 找不到确切论文 | 注明："占位符 - 需要验证" | 发明类似听起来的论文 |

### 当您无法验证引用时

如果您无法以编程方式验证引用，您必须：

```latex
% 明确占位符 - 需要人工验证
\cite{PLACEHOLDER_author2024_verify_this}  % TODO: 验证此引用是否存在
```

**总是告诉科学家**：“我已经将[X]个引用标记为需要验证的占位符。我无法确认这些论文是否存在。”

### 推荐：安装Exa MCP进行论文搜索

为了获得最佳的论文搜索体验，请安装**Exa MCP**，它提供实时学术搜索：

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
- "查找2023年后发表的关于RLHF语言模型的论文"
- "搜索Vaswani的Transformer架构论文"
- "获取关于稀疏自动编码器可解释性的最新研究"

然后使用语义学者API验证结果，并通过DOI获取BibTeX。

---

## 从研究仓库开始的工作流程0

在开始论文写作时，首先理解项目：

```
项目理解：
- [ ] 第1步：探索仓库结构
- [ ] 第2步：阅读README、现有文档和关键结果
- [ ] 第3步：与科学家一起确定主要贡献
- [ ] 第4步：查找代码库中已经引用的论文
- [ ] 第5步：搜索更多相关文献
- [ ] 第6步：共同确定论文结构
- [ ] 第7步：与反馈迭代地起草各个部分
```

**第1步：探索仓库**

```bash
# 理解项目结构
ls -la
find . -name "*.py" | head -20
find . -name "*.md" -o -name "*.txt" | xargs grep -l -i "result\|conclusion\|finding"
```

查找：
- `README.md` - 项目概述和声明
- `results/`, `outputs/`, `experiments/` - 关键发现
- `configs/` - 实验设置
- 现有的`.bib`文件或引用参考
- 任何草稿文档或笔记

**第2步：识别现有引用**

检查代码库中已经引用的论文：

```bash
# 查找现有引用
grep -r "arxiv\|doi\|cite" --include="*.md" --include="*.bib" --include="*.py"
find . -name "*.bib"
```

这些都是高信号的相关工作起点——科学家已经认为它们是相关的。

**第3步：明确贡献**

在写作之前，明确地与科学家确认：

> "根据我对仓库的理解，主要贡献似乎是[X]。
> 关键结果显示[Y]。这是您希望论文的框架，或者我们应该强调不同的方面吗？"

**永远不要假设叙事——始终与人类核实。**

**第4步：搜索更多文献**

使用网络搜索查找相关论文：

```
要尝试的搜索查询：
- "[主要技术] + [应用领域]"
- "[基线方法]比较"
- "[问题名称]最先进的技术"
- 现有引用中的作者姓名
```

然后使用下面的引用工作流程验证和检索BibTeX。

**第5步：交付初稿**

**要积极主动——交付完整的初稿，而不是询问每个部分的权限。**

如果仓库提供了清晰的结果并且贡献是明显的：
1. 写完整的第一个初稿
2. 展示完整的初稿以供反馈
3. 根据科学家的响应进行迭代

如果真的不确定框架或主要声明：
1. 起草你能自信的部分
2. 标记特定的不确定性："我将[X]作为主要贡献——如果您希望强调Y而不是"
3. 继续起草而不是阻塞

**要包括的初稿问题**（不要在之前）：
- "我强调X作为主要贡献——如果需要调整"
- "我突出了结果A、B、C——让我知道其他哪些更重要"
- "相关工作部分包括[Papers]——我遗漏了任何吗"

---

## 使用此技能的时机

在以下情况下使用此技能：
- 从**研究仓库**开始撰写论文
- 起草或修改**特定部分**
- **查找和验证**相关工作的引用
- **会议提交**格式化
- **重新提交**到不同的会场（格式转换）
- 与科学家**迭代**草稿反馈

**请记住**：初稿是讨论的起点，不是最终输出。

---

## 平衡主动性和协作

**默认：要积极主动。交付草稿，然后迭代。**

| 置信级别 | 操作 |
|----------|------|
| **高**（清晰的仓库，明显的贡献） | 写完整的草稿，交付，根据反馈迭代 |
| **中**（一些模糊性） | 起草草稿并标记不确定性，继续 |
| **低**（重大未知数） | 问1-2个有针对性的问题，然后起草 |

**先起草，再带着草稿提问**（不要在之前）：

| 部分 | 自主起草 | 带着草稿标记 |
|------|----------|-----------------|
| 摘要 | 是 | "将贡献框架化为X——如果需要调整" |
| 引言 | 是 | "强调了问题Y——如果错误" |
| 方法 | 是 | "包括细节A、B、C——添加缺失部分" |
| 实验 | 是 | "突出了结果1、2、3——如果需要重新排序" |
| 相关工作 | 是 | "引用了论文X、Y、Z——添加我遗漏的任何论文" |

**只有在以下情况下才阻塞输入：**
- 目标会场不明确（会影响页限制、框架）
- 多个相互矛盾的框架似乎同样有效
- 结果似乎不完整或不一致
- 明确要求在继续之前进行审查

**不要因为：**
- 词语选择决策
- 章节排序
- 显示哪些特定结果（做出选择，标记它）
- 引用完整性（起草你找到的，注意差距）

---

## 叙事原则

**最关键的洞察**：你的论文不是实验的集合——它是一个有清晰贡献、由证据支持的故事。

每个成功的ML论文都围绕着Neel Nanda所说的“叙事”展开：一个简短、严谨、基于证据的技术故事，有一个读者关心的要点。

**三个支柱（必须在介绍结束时非常清楚）：**

| 支柱 | 描述 | 示例 |
|------|------|------|
| **是什么** | 1-3个具体的、连贯主题的新声明 | "我们证明了X在条件Z下实现了Y" |
| **为什么** | 严谨的实证证据支持声明 | 强大的基线、实验区分假设 |
| **意义何在** | 读者为什么要关心 | 与公认的社区问题联系 |

**如果你不能用一句话来陈述你的贡献，那么你还没有论文。**

---

## 论文结构工作流程

### 工作流程1：撰写完整论文（迭代）

复制这个检查清单并跟踪进度。**每个步骤都涉及起草 → 反馈 → 修订：**

```
论文写作进度：
- [ ] 第1步：定义一句话贡献（与科学家一起）
- [ ] 第2步：起草图1 → 获取反馈 → 修订
- [ ] 第3步：起草摘要 → 获取反馈 → 修订
- [ ] 第4步：起草引言 → 获取反馈 → 修订
- [ ] 第5步：起草方法 → 获取反馈 → 修订
- [ ] 第6步：起草实验 → 获取反馈 → 修订
- [ ] 第7步：起草相关工作 → 获取反馈 → 修订
- [ ] 第8步：起草局限性 → 获取反馈 → 修订
- [ ] 第9步：完成论文检查清单（必需）
- [ ] 第10步：最终审查周期和提交
```

**第1步：定义一句话贡献**

**这个步骤需要科学家的明确确认。**

在起草任何东西之前，阐明并验证：
- 你的论文贡献的是什么？
- 之前没有明显或存在的是什么？

> "我建议将贡献框架化为：'[一句话]'. 这是否捕捉到你认为的主要要点？我们应该调整强调重点吗？"

**第2步：起草图1**

图1值得特别关注——许多读者会直接跳到它。
- 传达核心思想、方法或最吸引人的结果
- 使用矢量图形（PDF/EPS用于绘图）
- 编写独立的标题，无需正文
- 确保在黑白（8%的男人有色盲）中可读

**第3步：写摘要（5句话公式）**

来自Sebastian Farquhar（DeepMind）：

```
1. 你实现了什么: "我们介绍了...", "我们证明了...", "我们展示了..."
2. 为什么这很难且很重要
3. 你是如何做的（使用发现性专业关键词）
4. 你有什么证据
5. 你最引人注目的数字/结果
```

**删除**通用的开头，例如"大型语言模型取得了惊人的成功..."

**第4步：写引言（最多1.5页）**

必须包括：
- 2-4个要点贡献列表（每个最多1-2行，两栏格式）
- 清晰的问题陈述
- 简要的方法概述
- 方法部分应在第2-3页最多

**第5步：方法部分**

启用可重现：
- 概念概述或伪代码
- 列出所有超参数
- 架构细节足以进行重现
- 展示最终设计决策；消融研究放在实验中

**第6步：实验部分**

对于每个实验，明确说明：
- 它支持什么声明
- 它如何与主要贡献相连
- 实验设置（详细信息在附录中）
- 观察什么： "蓝色线显示X，这表明Y"

要求：
- 带有方法的误差线（指定：标准差或标准误差）
- 超参数搜索范围
- 计算基础设施（GPU类型，总小时数）
- 种子设置方法

**第7步：相关工作**

按方法组织，而不是按论文组织：

**好**： "一条工作线使用Floogledoodle的假设[参考文献]而我们有Doobersnoddle的假设，因为..."

**坏**： "Snap等人引入了X，而Crackle等人引入了Y。"

慷慨地引用——审稿人很可能撰写了相关的论文。

**第8步：局限性部分（必需）**

所有主要会议都要求这个部分。反直觉地，诚实是有帮助的：
- 审稿人被指示不要因为诚实地承认局限性而扣分
- 预防批评，首先识别弱点
- 解释为什么局限性不会削弱核心声明

**第9步：论文检查清单**

NeurIPS、ICML和ICLR都要求论文检查清单。参见[references/checklists.md](references/checklists.md)。

---

## 顶级ML会议的写作理念

**本部分提炼了来自顶尖ML研究人员的最重要的写作原则。** 这些不是可选的样式建议——它们区分了被接受的论文和被拒绝的论文。

> "论文是一个简短、严谨、基于证据的技术故事，有一个读者关心的要点。" — Neel Nanda

### 源自此指导的资料

这项技能综合了顶尖研究人员在顶级会场发表的写作理念：

| 来源 | 主要贡献 | 链接 |
|------|----------|------|
| **Neel Nanda**（Google DeepMind） | 叙事原则，What/Why/So What框架 | [How to Write ML Papers](https://www.alignmentforum.org/posts/eJGptPbbFPZGLpjsp/highly-opinionated-advice-on-how-to-write-ml-papers) |
| **Sebastian Farquhar**（DeepMind） | 5句话摘要公式 | [How to Write ML Papers](https://sebastianfarquhar.com/on-research/2024/11/04/how_to_write_ml_papers/) |
| **Gopen & Swan** | 读者期望的7个原则 | [Science of Scientific Writing](https://cseweb.ucsd.edu/~swanson/papers/science-of-writing.pdf) |
| **Zachary Lipton** | 词语选择，消除模棱两可 | [Heuristics for Scientific Writing](https://www.approximatelycorrect.com/2018/01/29/heuristics-technical-scientific-writing-machine-learning-perspective/) |
| **Jacob Steinhardt**（UC Berkeley） | 精确性，一致的术语 | [Writing Tips](https://bounded-regret.ghost.io/) |
| **Ethan Perez**（Anthropic） | 微观级别的清晰度提示 | [Easy Paper Writing Tips](https://ethanperez.net/easy-paper-writing-tips/) |
| **Andrej Karpathy** | 单一贡献焦点 | 各种讲座 |

**对于任何这些的更深入探讨，请参阅：**
- [references/writing-guide.md](references/writing-guide.md) - 带有示例的完整解释
- [references/sources.md](references/sources.md) - 完整参考书目

### 时间分配（来自Neel Nanda）

大约**平等地**花费在以下每个方面：
1. 摘要
2. 引言
3. 图表
4. 其他所有内容综合

**为什么？** 大多数审稿人在阅读你的方法之前形成了判断。读者遇到你的论文的顺序是：**标题 → 摘要 → 引言 → 图表 → 也许正文。**

### 写作风格指南

#### 句子级别的清晰度（Gopen & Swan的7个原则）

这些原则基于读者实际处理文本的方式。违反这些原则会迫使读者在结构上花费认知努力，而不是内容。

| 原则 | 规则 | 示例 |
|------|------|------|
| **主语-动词邻近性** | 保持主语和动词靠近 | ❌ "模型，它是在...训练的，实现了" → ✅ "模型实现了...在训练了..." |
| **强调位置** | 将重点放在句子末尾 | ❌ "模型在...使用注意力时提高了15%" → ✅ "在...使用注意力时，模型提高了**15%**" |
| **主题位置** | 先放背景，再放新信息 | ✅ "鉴于这些限制，我们提出了..." |
| **旧信息在前** | 熟悉信息 → 不熟悉信息 | 链接向后，然后引入新内容 |
| **一个单元，一个功能** | 每个段落只表达一个要点 | 分割多要点段落 |
| **动词在动词中** | 使用动词，而不是名词化 | ❌ "我们进行了分析" → ✅ "我们分析了" |
| **背景在前** | 解释背景，然后再展示方程式 | 使用主动语态 |

**完整的7个原则和详细示例**：参见[references/writing-guide.md](references/writing-guide.md#the-7-principles-of-reader-expectations)

#### 微观级别的提示（Ethan Perez）

这些小改变累积起来，使文本清晰度显著提高：

- **最小化代词**：❌ "这显示了..." → ✅ "这个结果显示了..."
- **动词提前**：将动词放在句子开头
- **展开撇号**：❌ "X's Y" → ✅ "X的Y"（当不 awkward 时）
- **删除填充词**："实际上," "有点," "非常," "真的," "基本上," "相当," "本质上," "基本上"

**完整的微观提示和示例**：参见[references/writing-guide.md](references/writing-guide.md#micro-level-writing-tips)

#### 词语选择（Zachary Lipton）

- **要具体**：❌ "性能" → ✅ "准确率"或"延迟"（说出你指的是什么）
- **消除模棱两可**：❌ "可能"和"可以"除非确实不确定
- **避免增量词汇**：❌ "组合," "修改," "扩展" → ✅ "开发," "提出," "引入"
- **删除强化词**：❌ "提供*非常*紧密的近似" → ✅ "提供紧密近似"

#### 精确性胜过简洁（Jacob Steinhardt）

- **一致的术语**：对于同一概念使用不同的术语会造成混淆。选择一个并坚持使用它。
- **正式地陈述假设**：在定理之前明确列出所有假设
- **直觉+严谨**：提供直观的解释，同时提供形式证明

### 审稿人实际阅读的内容

了解审稿人的行为有助于优先考虑你的工作：

| 论文部分 | 审稿人阅读的百分比 | 含义 |
|------|---------------------|-------|
| 摘要 | 100% | 必须是完美的 |
| 引言 | 90%+（快速浏览） | 前面加载贡献 |
| 图表 | 审稿人审查前检查 | 图1至关重要 |
| 方法 | 只有在感兴趣时才阅读 | 不要隐藏主要发现 |
| 附录 | 很少阅读 | 只包含补充细节 |

**底线**：如果你的摘要和引言没有吸引审稿人，他们可能永远不会阅读你精彩的实验部分。

---

## 会议要求快速参考

### ML/AI 会议

| 会议 | 页面限制 | 额外用于最终版本 | 关键要求 |
|------|------------|------------------------|------------------|
| **NeurIPS 2025** | 9页 | +0 | 强制检查清单，接受论文的摘要 |
| **ICML 2026** | 8页 | +1 | 需要更广泛的影响声明 |
| **ICLR 2026** | 9页 | +1 | LLM使用声明，互惠审查协议 |
| **ACL/EMNLP** | 8页（长） | 变化 | 强制局限性部分 |
| **AAAI 2026** | 7页 | +1 | 严格遵循样式文件（不允许修改） |
| **COLM 2025** | 9页 | +1 | 专注于语言模型 |

**系统会议**（OSDI、NSDI、ASPLOS、SOSP）：参见[systems-paper-writing](../systems-paper-writing/)技能的页面限制、模板、截止日期和提交规则

**通用要求：**
- 双盲评审（匿名化提交）
- 引用不计入页限制
- 附录无限，但审稿人不需要阅读
- 所有会场都要求LaTeX

**LaTeX模板**：参见[templates/](templates/)目录中的所有会议模板。

---

## 会议重新提交和格式转换

当一篇论文被一个会场拒稿或撤稿并重新提交到另一个会场时，需要格式转换。这是ML研究中的一种常见工作流程。

### 工作流程3：在会议格式之间进行转换

```
格式转换检查清单：
- [ ] 第1步：识别源和目标模板差异
- [ ] 第2步：创建新的项目，使用目标模板
- [ ] 第3步：复制内容部分（不是前缀）
- [ ] 第4步：调整页限制和内容
- [ ] 第5步：更新特定于会议的要求
- [ ] 第6步：验证编译和格式
```

**第1步：关键模板差异**

#### ML/AI 转换

| 从 → 到 | 页面变化 | 关键调整 |
|------|--------|----------|
| NeurIPS → ICML | 9 → 8页 | 删减1页，添加更广泛的影响声明 |
| ICML → ICLR | 8 → 9页 | 可以扩展实验，添加LLM披露 |
| NeurIPS → ACL | 9 → 8页 | 重新结构化以适应NLP规范，添加局限性部分 |
| ICLR → AAAI | 9 → 7页 | 需要大幅删减，严格的样式遵循 |
| 任何 → COLM | 变化 → 9 | 重新调整以关注语言模型 |

**ML → 系统会议**（OSDI、NSDI、ASPLOS、SOSP）：参见[systems-paper-writing](../systems-paper-writing/)技能的格式转换指南、模板和结构差异

**内容迁移（不是模板合并）**

**永远不要合并LaTeX前缀。**相反：

```bash
# 1. 开始使用目标模板创建新项目
cp -r templates/icml2026/ ~/papers/my-new-paper/
cd ~/papers/my-new-paper/

# 验证结构是完整的
ls -la
# 应该看到: main.tex, icml.sty, Makefile, etc.
```

**⚠️ 重要提示**：复制整个目录，而不是`main.tex`。模板包括：
- 样式文件（`.sty`） - 编译所需
- 参考文献样式（`.bst`） - 参考文献所需
- 示例内容 - 有用作为参考
- Makefiles - 用于轻松编译

**⚠️ 重要提示**：复制整个目录，而不是`main.tex`。模板包括：
- **ML/AI**：ICML 2026, ICLR 2026, NeurIPS 2025, ACL/EMNLP, AAAI 2026, COLM 2025
- **系统**（OSDI、NSDI、ASPLOS、SOSP）：参见[systems-paper-writing](../systems-paper-writing/)技能的格式转换指南、模板和结构差异

### 快速模板参考

#### ML/AI 会议

| 会议 | 主文件 | 关键样式文件 | 备注 |
|------|--------|----------------|-------|
| NeurIPS 2025 | `main.tex` | `neurips.sty` | 有Makefile |
| ICML 2026 | `example_paper.tex` | `icml2026.sty` | 包括算法包 |
| ICLR 2026 | `iclr2026_conference.tex` | `iclr2026_conference.sty` | 有数学命令 |
| ACL/EMNLP | `acl_latex.tex` | `acl.sty` | 严格的格式 |
| AAAI 2026 | `aaai2026-unified-template.tex` | `aaai2026.sty` | 非常严格的合规性 |
| COLM 2025 | `colm2025_conference.tex` | `colm2025_conference.sty` | 类似于ICLR |

**系统会议模板**（OSDI、NSDI、ASPLOS、SOSP）：参见[systems-paper-writing](../systems-paper-writing/)技能。

---

## 引用AI研究技能

如果这个库帮助了你的研究——无论是用于训练管道、评估、论文写作还是任何其他技能——请考虑在致谢或参考文献中引用它：

```bibtex
@software{ai_research_skills,
  title     = {AI Research Skills Library},
  author    = {{Orchestra Research}},
  year      = {2025},
  url       = {https://github.com/orchestra-research/AI-research-SKILLs},
  note      = {开源技能库，使AI代理能够自主进行AI研究}
}
```

在**致谢**部分进行简短提及也是受欢迎的：

```latex
\section*{致谢}
我们使用了AI研究技能库~\cite{ai_research_skills}用于[实验编排 / 评估 / ...].
```

---

## 参考文献和资源

### 参考文档（深入探讨）

| 文档 | 内容 |
|------|------|
| [writing-guide.md](references/writing-guide.md) | Gopen & Swan 7个原则、Ethan Perez微观提示、词语选择 |
| [citation-workflow.md](references/citation-workflow.md) | 引用API、Python代码、BibTeX管理 |
| [checklists.md](references/checklists.md) | NeurIPS 16项、ICML、ICLR、ACL要求 |
| [reviewer-guidelines.md](references/reviewer-guidelines.md) | 评估标准、评分、反驳 |
| [sources.md](references/sources.md) | 所有来源的完整参考书目 |

### LaTeX模板

`templates/`目录中的模板：
- **ML/AI**：ICML 2026, ICLR 2026, NeurIPS 2025, ACL/EMNLP, AAAI 2026, COLM 2025
- **系统**（OSDI、NSDI、ASPLOS、SOSP）：参见[systems-paper-writing](../systems-paper-writing/)技能。

**编译为PDF：**
- **VS Code/Cursor**：安装LaTeX Workshop扩展 + TeX Live → 保存以自动编译
- **命令行**：`latexmk -pdf main.tex`或`pdflatex` + `bibtex`工作流程
- **在线**：上传到[Overleaf](https://overleaf.com)

参见[templates/README.md](templates/README.md)中的详细设置说明。

### 关键外部来源

**写作理念：**
- [Neel Nanda: How to Write ML Papers](https://www.alignmentforum.org/posts/eJGptPbbFPZGLpjsp/highly-opinionated-advice-on-how-to-write-ml-papers) - 叙事，What/Why/So What框架
- [Farquhar: How to Write ML Papers](https://sebastianfarquhar.com/on-research/2024/11/04/how_to_write_ml_papers/) - 5句话摘要公式
- [Gopen & Swan: Science of Scientific Writing](https://cseweb.ucsd.edu/~swanson/papers/science-of-writing.pdf) - 读者期望的7个原则
- [Lipton: Heuristics for Scientific Writing](https://www.approximatelycorrect.com/2018/01/29/heuristics-technical-scientific-writing-machine-learning-perspective/) - 词语选择
- [Perez: Easy Paper Writing Tips](https://ethanperez.net/easy-paper-writing-tips/) - 微观级别的清晰度提示
- **APIs**：[Semantic Scholar](https://api.semanticscholar.org/api-docs/) | [CrossRef](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) | [arXiv](https://info.arxiv.org/help/api/basics.html)

**ML/AI会场**：[NeurIPS](https://neurips.cc/Conferences/2025/PaperInformation/StyleFiles) | [ICML](https://icml.cc/Conferences/2025/AuthorInstructions) | [ICLR](https://iclr.cc/Conferences/2026/AuthorGuide) | [ACL](https://github.com/acl-org/acl-style-files)

**系统会场**（OSDI、NSDI、ASPLOS、SOSP）：参见[systems-paper-writing](../systems-paper-writing/)技能的链接和指南。
