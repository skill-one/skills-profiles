# 为社会科学人性化学术写作

## 学术诚信声明

**目的**：此技能帮助研究人员通过AI辅助写作工具提升其原创思想的表达质量和自然度。

**规范使用**：
- ✅ 基于自身研究和想法修改AI草拟的文本
- ✅ 提升非英语母语者的写作质量  
- ✅ 学习更优的学术写作模式
- ❌ 使用AI生成自己不理解的想法
- ❌ 提交未能体现个人智力贡献的作品

**原则**：目标是实现真实的学术交流，而非欺骗。

---

## 目标受众

社会科学（社会学、人类学、政治学、教育学、心理学）领域的非英语母语者，他们：
- 拥有原创思想和研究成果
- 使用AI工具撰写文本
- 需要使写作风格更自然
- 希望减少明显的AI模式

---

## 使用此技能的场景

- 用户基于自身想法生成了AI草稿
- 文本感觉“过于完美”、“机械化”或重复
- 需要减少AI检测标记
- 希望为社会科学写作赋予真实的学术声音
- 段落过渡显得机械化
- 语言过于抽象缺乏具体实例

---

## 核心工作流程

### 第1步：分析文本

首先运行AI检测分析器以识别问题模式：

```bash
python scripts/ai_detector.py input.txt
```

分析器识别：
- 重复的句式结构和长度
- 过度使用的AI过渡短语（Moreover, Furthermore, Additionally）
- 抽象/模糊语言模式（"various aspects", "in terms of"）
- 机械化段落过渡
- 社会科学领域不自然的用词
- 词汇多样性低（Type-Token Ratio）
- 过度使用被动语态
- 连续句子相似度

**输出**：AI概率评分 + 每段标记的具体问题

### 第2步：应用针对性改写策略

根据检测到的问题，应用以下修正：

#### 策略1：变化句式节奏（解决统一性）

**AI模式**：所有句子长度相似（15-20个词）

**人类修正**：混合短（5-10个词）、中（15-20个词）和长（25-35个词）的句子

示例：
- AI: "This study examines social media impact. The research focuses on young adults. The analysis considers multiple factors."
- Human: "This study examines social media's impact on young adults, considering factors ranging from identity formation to civic engagement."

#### 策略2：减少抽象框架

**AI模式**：意义不明确的占位符短语

常见问题：
- "various aspects"
- "in terms of"
- "it is important to note that"
- "multiple factors"
- "different perspectives"

**人类修正**：用具体概念、命名理论、具体实例替换

示例：
- AI: "In terms of the various aspects of social interaction, multiple factors play important roles."
- Human: "Social interaction depends on trust, reciprocity, and shared norms—factors that vary across cultural contexts."

#### 策略3：消除机械化过渡

**AI模式**：过度使用句首的正式连接词

过度使用的词语：
- Moreover,
- Furthermore,
- Additionally,
- In addition,
- It is important to note that

**人类修正**：使用多样化的过渡策略：
- 直接逻辑流程（无需连接词）
- "This pattern echoes..."
- "Building on this insight..."
- "Yet" / "Still" / "However"（谨慎使用）
- 通过内容隐含逻辑连接
- 最小化正式连接词

#### 策略4：增强学术语气

**AI模式**：通用学术语气缺乏个性或批判性参与

**人类修正**：
- 包含适当的保留性表述（"may suggest", "appears to", "potentially"）
- 展示对来源的批判性参与
- 自然使用学科语言
- 展现真实的智力探索过程

示例：
- AI: "The data shows a correlation between X and Y."
- Human: "The data suggest a correlation between X and Y, though the causal mechanism remains unclear and warrants further investigation."

#### 策略5：具体化内容

**AI模式**：缺乏具体支撑的泛化陈述

**人类修正**：
- 命名具体理论/学者
- 包含具体实例
- 引用特定背景
- 引用实际研究细节

示例：
- AI: "Research has shown various effects of social media on society."
- Human: "Recent ethnographic work documents how Instagram reshapes young women's body image practices (Tiidenberg 2018), while experimental studies reveal minimal effects on political polarization (Guess et al. 2023)."

### 第3步：带理由改写

对每个段落遵循以下格式：

**原文（AI生成）**：
[Paste the original text]

**修订（人性化）**：
[您的改写版本]

**理由**：
解释1-2句AI模式修正。示例：
- "移除重复的'Moreover/Additionally'过渡，变化句式节奏（增加一句短句、一句长句）；用具体概念（信任、互惠、规范）替换'various aspects'。"
- "消除抽象框架（'in terms of', 'multiple factors'）；增加具体引用（Smith 2022）和具体研究发现；使用学术保留性表述（'suggests'而非'shows'）。"
- "打破18词的统一句子长度，调整为8、24、15词长度；移除机械的'Furthermore'开头；在命名理论（社会资本）和具体背景（中国城市）中支撑主张。"

---

## 人性化文本的关键原则

### 1. 突显性（不可预测性）
- **问题**：AI文本过于可预测
- **修正**：增加适当但意外的用词选择；变化句法结构

### 2. 跳动感（节奏变化）
- **问题**：AI使用统一句子长度
- **修正**：混合简短有力句与长复合句；创造自然阅读节奏

### 3. 具体性胜于抽象性
- **问题**：AI默认使用模糊抽象
- **修正**：使用具体实例、具体数据、命名理论；在特定背景下支撑主张

### 4. 真实学术语气
- **问题**：通用正式语气缺乏个性
- **修正**：展示对思想的真诚参与；包含适当保留性表述；展现批判性思维

### 5. 自然流畅性
- **问题**：机械化过渡和段落连接
- **修正**：让内容驱动连接；使用隐含逻辑；最小化正式连接词

---

## 社会科学领域特点

### 学科语言

**社会学**：
- 关键概念：阶层化、能动性、惯习、资本、制度、不平等
- 理论传统：功能主义、冲突论、符号互动论、实践理论
- 常用方法：民族志、调查、访谈、档案分析

**人类学**：
- 关键概念：文化、仪式、亲属关系、阈限、立场、厚描
- 允许更多反思性声音
- 重视民族志细节

**政治学**：
- 关键概念：制度、权力、合法性、治理、国家能力
- 因果推理语言
- 假设检验框架

**教育学**：
- 关键概念：教学法、课程、公平、成就差距、学习成果
- 常用混合方法
- 强调政策相关性

**社会心理学**：
- 关键概念：认知、行为、态度、干预、机制
- 操作性定义至关重要
- 实验设计突出

### 非英语母语者注意事项

**常见AI拐杖**：
1. 过度依赖强化词（"very", "really", "quite"）
2. 重复句子开头
3. 过度使用正式连接词表示逻辑

**需要保留的优势**：
- 清晰的逻辑结构（保持）
- 正式语域（适合学术写作）
- 严谨语法（不要过度非正式化）

**需要人性化的领域**：
- 变化从句结构和句子类型
- 自信使用领域特定术语
- 包含适当学术保留性表述
- 包含对来源的批判性参与
- 将抽象概念具体化

---

## 额外资源

获取详细指导，请参阅：

- **[docs/rewriting-principles.md](docs/rewriting-principles.md)**：包含扩展示例的全面改写技术
- **[docs/examples.md](docs/examples.md)**：不同部分类型（引言、方法、发现、讨论）的完整改写前/后示例
- **[docs/social-science-patterns.md](docs/social-science-patterns.md)**：学科特定惯例和术语

---

## 脚本和工具

### ai_detector.py
分析文本中的AI模式并提供详细评分

```bash
# 基础分析
python scripts/ai_detector.py input.txt

# 详细输出，包含段落级分析
python scripts/ai_detector.py input.txt --detailed

# JSON输出，用于程序化使用
python scripts/ai_detector.py input.txt --json > analysis.json
```

### text_analyzer.py
提供文本质量量化指标

```bash
# 分析文本指标
python scripts/text_analyzer.py input.txt

# 比较前后版本
python scripts/text_analyzer.py original.txt revised.txt --compare
```

**提供的指标**：
- 句子长度分布和方差
- 词汇多样性（Type-Token Ratio）
- 学术词使用频率
- 过渡词密度
- 被动语态百分比
- 平均句子复杂度

---

## 示例工作流程

1. **用户提供AI生成文本**： "你能帮我人性化这段论文段落吗？"

2. **先分析**：
   - 运行`ai_detector.py`或手动识别模式
   - 记录具体问题（例如："重复句式结构，3次'Moreover'，抽象语言"）

3. **策略性改写**：
   - 应用上述相关策略
   - 保持用户的核心理念和论点
   - 保留准确的引用和数据

4. **解释修改**：
   - 展示原文→修订版
   - 解释修正的AI模式
   - 帮助用户为未来写作学习

5. **验证改进**：
   - 可选运行`text_analyzer.py`确认指标改善
   - 确认意义和准确性未丢失

---

## 有效使用技巧

### 要做：
- ✅ 保留用户的原始思想和论点
- ✅ 保持引用准确性
- ✅ 维持适当的学术语域
- ✅ 关注模式而非单个词语
- ✅ 解释修改以便用户学习

### 不要：
- ❌ 改变意义或论点
- ❌ 添加原文中未有的信息
- ❌ 过度非正式化学术语言
- ❌ 删除所有正式连接词（有些是必要的）
- ❌ 故意制造语法错误

### 平衡：
学术写作应：
- **清晰但不简单**
- **正式但不机械化**
- **结构化但不机械**
- **精确但不迂腐**

---

## 常见误区

1. **过度修正**：不要使每个句子长度差异过大。自然变化存在于一定范围内。

2. **删除所有连接词**：某些过渡对于复杂论证的清晰性是必要的。

3. **添加口语化表达**：学术写作应保持正式；避免非正式表达。

4. **失去精确性**：不要为“自然性”牺牲技术准确性。

5. **忽视学科差异**：社会科学子领域有不同的惯例——尊重它们。

---

## 总结检查清单

改写后验证：

- [ ] 句子长度变化（混合短、中、长）
- [ ] 机械过渡（Moreover, Furthermore, Additionally）被移除或减少
- [ ] 抽象占位符短语被具体概念替换
- [ ] 至少增加一个具体实例或命名理论
- [ ] 适当包含学术保留性表述
- [ ] 保留原始意义和论点
- [ ] 引用准确
- [ ] 学科语言自然
- [ ] 提供理由解释修正的AI模式

---

此技能强调**真实的学术交流**，同时尊重非英语母语者负责任地使用AI工具的智力工作。
