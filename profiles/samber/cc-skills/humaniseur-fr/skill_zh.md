# 人类化：消除法语中的 AI 写作模式

## 你的任务

当给定法语文本进行人类化时：

0. **首先明确目标语体** - 缩写、俚语、口语、表情符号和排版都取决于预期的语言水平。如果从请求或输入中不明确（正式、常用、非正式？针对哪种媒介？），请在开始人类化之前询问用户
1. **识别 AI 模式** - 扫描以下列出的 38 种模式
2. **重写有问题的部分** - 将 AI 式表达替换为自然的法语表达
3. **保持原意** - 保留核心信息完整
4. **保持语气** - 符合预期的语调和语体
5. **注入灵魂** - 不要只是去除不良模式；要注入真正的个性（见第 4 部分）
6. **进行最终的 anti-AI 处理** - 询问：“什么让这段文字明显是 AI 生成的？” 简要回答剩余的线索，然后询问“现在，确保它不再如此”，并进行修改。应用三信号规则：一个孤立标记是噪音（大多数是正常的法语），但三个或更多在同一段落中同时出现会使读者皱眉——修改，直到没有段落积累三个

## 80% 规则：不完美服从是重点

遵循人类化规则 _大部分时间_ — 不总是这样。留下大约 20% 的这项技能的指令未应用是没问题的。

- 真实的法语散文包含低密度的标记模式：“ pour conclure ” 并不会使文本 100% AI，而一个机械地避开每个线索的文本以新的、同样可检测的方式变得一致。
- 故意违规：保留一个值得其位置的破折号，一个 « par ailleurs », 一个整洁的列表。
- 线索是密度和共存（见三信号规则），永远不会是一个单独的发生。

**一次处理即可。** 不要对同一文本重复运行此技能：每次处理都会去除方差并注入自己的习惯，质量会快速下降——第二次或第三次处理时，第一次创建的语气会被压扁。如果最终的反 AI 处理后结果仍然有 AI 的味道，修复方法是添加锚定内容（事实、日期、意见——见第 4 部分的限制说明），而不是再次清理。

## 优先级：此技能服从于上下文

这里的指令可能被用户的提示或加载的更具体的技能覆盖。当任务附带自己的散文和文案方法——领英帖子、新闻稿、广告文案、开发者文档中的 README——这些规则在冲突中获胜：仅将此技能应用于他们留下的空白（AI 词汇、英语外来语、人工制品、排版）。领英钩子、新闻稿结构或开发者文档中的 Markdown 格式可能合法地使用这里标记的模式（简短的段落、整洁的列表、标题和粗体、三条规则）；那是格式在说话，而不是机器。

## 重要提示：法语特定上下文

法语专业写作本质上比英语更正式。连接词如 « néanmoins » 和 « toutefois » 在人类的法语中是合法的。线索与英语不同：

- AI 词汇是不同的（“crucial”是法语中排名第一的 AI 单词，而不是“delve”）
- 来自模型英语优先架构的英语外来语是一个主要的线索
- 排版约定（斜体符号、标点符号前的空格）是严格的
- 论文传统（thèse/antithèse/synthèse）与 AI 结构重叠
- 法语自然地容忍较长的句子，因此爆发性信号有所不同

**切勿降低语言水平。** 如果输入是 « langage soutenu », 输出必须保持 « langage soutenu »。

- 将正式散文改写成非正式法语是一种不同类型的非真实性——与可检测性一样明显，一样人工。敌人是 _公式化_ 写作，而不是 _正式_ 写作。
- 一个结构良好的从句、一个精确的连接词、一个长的周期性句子——这些是好的法语特征，而不是 AI 人工制品。
- 仅删除真正机械的内容：膨胀的意义、避免系动词、同义词循环、促销填充。

---

## 第一部分：内容模式

### 模式 1 — 意义和遗产的膨胀

**触发器：** constitue/représente un tournant, témoigne de, joue un rôle crucial/essentiel/déterminant, souligne l'importance, reflète une tendance plus large, symbolisant son caractère durable, contribuant à, ouvrant la voie à, marquant une étape, un jalon décisif, un paysage en mutation, une empreinte indélébile, profondément ancré

LLMs 通过将普通事实与无人询问的更广泛趋势联系起来来夸大普通事实的重要性。

**之前：**

> L'Institut de la Statistique de la Catalogne a été officiellement créé en 1989, marquant un tournant décisif dans l'évolution des statistiques régionales en Espagne. Cette initiative s'inscrivait dans un mouvement plus large de décentralisation administrative.

**之后：**

> L'Institut de la Statistique de la Catalogne a été créé en 1989 dans le cadre du transfert de compétences statistiques aux communautés autonomes. Il produit et publie des statistiques régionales indépendamment de l'INE.

### 模式 2 — 强调知名度和媒体覆盖面

**触发器：** couverture médiatique indépendante, médias locaux/nationaux/internationaux, cité par un expert reconnu, forte présence sur les réseaux sociaux

**之前：**

> Ses travaux ont été cités dans Le Monde, la BBC, Les Échos et Le Figaro. Elle maintient une présence active sur les réseaux sociaux avec plus de 200 000 abonnés.

**之后：**

> Dans un entretien au Monde en 2024, elle a défendu l'idée que la régulation de l'IA devrait porter sur les résultats plutôt que sur les méthodes.

### 模式 3 — 现在分词的表面分析

**触发器：** soulignant/mettant en lumière..., assurant..., reflétant/symbolisant..., contribuant à..., favorisant/encourageant..., englobant..., illustrant...

AI 将现在分词短语附加到句子中，以添加虚假的分析深度。法语中英语“-ing”问题的对应物。

**之前：**

> La palette du bâtiment, mêlant bleu, vert et or, évoque la beauté naturelle de la région, symbolisant les champs de lavande et la Méditerranée, reflétant l'attachement profond de la communauté à son terroir.

**之后：**

> Le bâtiment utilise du bleu, du vert et de l'or. L'architecte a expliqué que ces couleurs font référence aux champs de lavande et à la côte méditerranéenne.

### 模式 4 — 宣传和广告语言

**触发器：** dispose de, vibrant, riche (figuré), profond, renforçant son, illustrant, exemplifie, engagement envers, beauté naturelle, niché, au cœur de, révolutionnaire (figuré), renommé, à couper le souffle, incontournable, époustouflant, un joyau

**之前：**

> Niché au cœur de la région époustouflante du Luberon, ce village se dresse comme un joyau vibrant doté d'un riche patrimoine culturel et d'une beauté naturelle à couper le souffle.

**之后：**

> Le village est situé dans le Luberon, à une trentaine de kilomètres d'Apt. On y vient surtout pour le marché du samedi et l'église romane du XIIe siècle.

**细微变体（编辑或总结时）：** AI 插入价值化的形容词和包容性双关语，这些在源文本中不存在——“ nos soldats ” 变成 “ nos _vaillants_ soldats ”, “ concitoyens ” 变成 “ concitoyennes et concitoyens ”。它过度纠正以符合其训练规范，而不是遵循源文本。恢复源文本的措辞。

### 模式 5 — 模糊的归属和词汇陷阱

**触发器：** Des rapports sectoriels, Les observateurs soulignent, Les experts estiment, Certains critiques avancent, plusieurs sources/publications (quand peu sont citées), il est communément admis que, il est largement reconnu que

**之前：**

> Les experts estiment qu'elle joue un rôle crucial dans l'écosystème régional.

**之后：**

> La rivière abrite plusieurs espèces de poissons endémiques, selon un inventaire de 2019 du CNRS.

### 模式 6 — “挑战和前景”部分

**触发器：** Malgré son... fait face à plusieurs défis..., En dépit de ces défis, Défis et héritage, Perspectives d'avenir, L'avenir s'annonce prometteur

公式化的挑战-然后-乐观三明治。

**之前：**

> Malgré sa prospérité industrielle, la commune fait face à des défis typiques des zones urbaines. En dépit de ces défis, elle continue de prospérer.

**之后：**

> La congestion routière s'est aggravée après 2015 avec l'ouverture de trois zones d'activités. La mairie a lancé un programme de réfection du réseau pluvial en 2022.

---

## 第二部分：语言、语法和风格模式

### 模式 7 — 过度使用的“AI”词汇

法语 AI 文本中最常见的单词是 **crucial**。副词 **notamment** 在 AI 文本中出现的频率约为人类法语的 1/200（4 倍过度使用）。

**高频 AI 词汇（查找和替换清单）：**

| AI 单词/短语 | 替换策略 |
| --- | --- |
| crucial, essentiel | 使用特定领域术语，或者直接删除 |
| également (最测量的法语 AI 标记) | « aussi », « de même », 或者删除——每段最多一个 |
| défi | « problème », « difficulté », 或者命名实际障碍 |
| significatif, robuste, substantiel | 精确：给出数字而不是 |
| holistique | 删除（英语“holistic”的直译） |
| compréhensif (= exhaustif) | 使用 « exhaustif » 或 « complet »（compréhensif 在法语中意为“富有同情心的”） |
| disruptif | « de rupture » 或描述实际变化 |
| notamment (如果 >1 per 800 words) | « en particulier », « entre autres », 或者重构 |
| par ailleurs, en outre, de plus | 使用 « ou », « reste que », « n'empêche que », « soit dit en passant »

**Jargon de ministre:** AI 法语倾向于使用行政词汇（« dispositif », « acteurs », « enjeux », « mise en œuvre », « dynamique territoriale »），即使在非机构环境中也是如此。在真正的行政文本之外，用普通词语替换。

**公式化开头一击即毁：**

- « Dans le paysage [actuel/numérique/contemporain] de... »
- « À l'ère de... »
- « Dans un monde [où/trépidant/tumultueux]... »
- « Il est essentiel/crucial de noter que... »
- « Plongeons dans... »（法语“Let's dive into”）
- « Découvrez comment... », « Dans cet article, nous allons explorer... », « Bienvenue dans ce guide complet... »（元公告——直接以内容本身开始）

**公式化结尾一击即毁：** “En conclusion”, “En résumé”, “En somme”, “En fin de compte”, “Au final” 开启的最后一句话。在具体事实的基础上结束，而不是在引言中预测。

**表明人类作者身份的连接词**（AI 几乎从不使用这些）：**Or**, **Quoi qu'il en soit**, **Toujours est-il que**, **Force est de constater que**, **Reste que**, **N'empêche que**, **Soit dit en passant**

### 模式 8 — 避免系动词（être/avoir）

**触发器：** constitue, fait office de, se positionne comme, représente [un], dispose de, offre [un]

**之前：** La galerie constitue l'espace d'exposition. Elle dispose de quatre salles. **之后：** La galerie est l'espace d'exposition. Elle a quatre salles.

### 模式 9 — 负面平行结构

**触发器：** Non seulement... mais aussi..., Il ne s'agit pas seulement de... mais de..., Ce n'est pas un simple X, c'est un Y

**之前：** Il ne s'agit pas simplement d'autocomplétion ; il s'agit de libérer la créativité. **之后：** L'outil dépasse la simple autocomplétion : il élargit l'espace de créativité disponible.

### 模式 10 — 系统性的三条规则

AI 将想法强行分组为三个一组。

**之前：** L'événement propose des conférences plénières, des tables rondes et des opportunités de réseautage. Innovation, inspiration et analyses sectorielles. **之后：** L'événement comprend des conférences et des tables rondes. Du temps est prévu pour le réseautage.

### 模式 11 — 同义词循环（优雅的变体）

重复惩罚代码导致对同一指称的过度同义词替换。

**之前：** Le protagoniste fait face à de nombreux défis. Le personnage principal doit surmonter les obstacles. La figure centrale finit par triompher. **之后：** Le protagoniste fait face à de nombreux obstacles, finit par les surmonter et rentre chez lui.

### 模式 12 — 错误的音阶

**触发器：** « de X à Y, de A à B » 其中 X-Y 和 A-B 不会形成有意义的等级。

**之前：** De la singularité du Big Bang au vaste réseau cosmique, de la naissance des étoiles à la danse de la matière noire. **之后：** Le livre couvre le Big Bang, la formation des étoiles et la matière noire.

### 模式 13 — 架构英语外来语

~16% de ChatGPT 的法语错误具有英语起源。这些是最可靠的线索之一。

| AI 英语外来语 | 法语正确 |
| --- | --- |
| « faire du sens » | « avoir du sens » |
| « adresser un problème » | « traiter / aborder un problème » |
| « implémenter » (非信息) | « mettre en œuvre » |
| « impacter » | « affecter, toucher » |
| « supporter » (= soutenir) | « prendre en charge » |
| « définitivement » (= assurément) | « sans aucun doute » |
| « basiquement » | « en gros, fondamentalement » |
| Oxford comma before « et » | 法语中 « et » 前不加逗号 |

### 模式 14 — 重复的形容词性冗余

Token-by-token 生成会产生作为保护性使用的同义词对。

**触发器：** crucial et essentiel, robuste et fiable, innovant et avant-gardiste, dynamique et en pleine expansion, riche et varié

**之前：** Cette approche innovante et avant-gardiste offre une solution robuste et fiable. **之后：** Cette approche tient la charge sans maintenance lourde.

### 模式 15 — 过度使用方括号

AI 过度使用 em dashes 模仿英语“简洁”写作。法语更喜欢用逗号和括号来表示偶然的从句。

**之前：** Le terme est promu par les institutions — pas par les habitants. Cet étiquetage — même dans les documents officiels — persiste. **之后：** Le terme est promu par les institutions, pas par les habitants. Cet étiquetage persiste, même dans les documents officiels.

**新鲜度说明：** 自 2025 年 11 月以来，ChatGPT 遵守“不使用 em dash”的定制指令，读者也了解这个线索。存在证明很少（人类也使用它），不存在证明什么。仍然减少过度使用——目标是自然的法语，而不是检测规避。

**Medium 例外：** 在 Markdown 是原生格式的文档中——README、开发者文档、技术维基——标题、粗体、列表、表格和代码块是规范，而不是线索。此模式针对 Markdown 粘贴到不渲染它的上下文中，以及生成人工制品；它不适用于打算作为 Markdown 的文档。

---

## 第三部分：话语架构模式

词汇清理是不够的：最深的 AI 线索是架构。即使文本包含零标记单词，也可能因为构建方式而读起来像机器制作。与测量的词汇数据不同，这些模式是工艺启发式——来自有经验的读者的趋同观察，而不是语料库测量的数字。

### 模式 30 — 通知、摘要和指令的回声

**触发器：** an intro announcing what the text will say, a conclusion repeating what it said, section headings mirroring the announced plan 1:1, a first sentence rephrasing the question asked (« Vous vous demandez comment... ? », the assignment restated), a closing that loops back to the request

信息只存在一次，但被呈现三次。聊天机器人答案和学校论文回响提示。在两端回响指令。

**规则：** 在媒体中插入内容——第一句话交付内容，而不是一个程序。在引言中预测某处结束，而不是预测引言无法预测的地方。删除提示在两端。

### 模式 31 — 无角度的目录结构

**触发器：** sections that could be reordered without breaking anything; every aspect of the topic covered at equal depth (définition, avantages, inconvénients, bonnes pratiques, conclusion); no claim that later sections build on

AI 涵盖主题；人类做出一个要点。如果两个部分可以互换而不会造成损害，则文本是一个伪装的列表，而不是一个论点。

**规则：** 选择一个角度并坚持。剪切不服务于它的方面——可见的死胡同是人类。让每个部分都依赖于前一个部分，所以顺序变得必要。

### 模式 32 — 显式的段落框架

**触发器：** every paragraph = topic sentence + two or three supports + mini-conclusion, fully self-contained; paragraphs opening with sequence connectors (« D'abord », « Ensuite », « De plus », « Enfin ») ; no idea ever spilling across a paragraph break; zero digressions

结构被信号而不是由内容承载。人类段落相互依存：一个想法在一段的结尾开始，在下一段结束；一个旁白打断。

**规则：** 删除支架连接符——并列作用。允许至少一个想法跨越段落。允许在它值得的地方进行旁白。

### 模式 33 — 虚假的话语平衡

**触发器：** every claim immediately counterbalanced (« Cependant, il convient de nuancer... »), symmetrical « d'une part / d'autre part », conclusion of the « tout dépend du contexte » type

句子级别的保护（模式 25）规模扩大到整个文本：文本没有论点。两边主义读起来像机器的谨慎，而不是公平。

**规则：** 采取立场。在真正重要的情况下进行一次细微差别——不是在每一个声明之后。如果诚实的答案真的是“这取决于”，请说明取决于什么，具体说明。

**魁北克例外：** rédaction épicène 和 OQLF 平民语言规范推动人类机构作家走向完全相同的平坦、对称形状——在魁北克机构文本中，仅平衡本身不应被视为机器输出。

### 模式 34 — SEO 风格过度分段和幽灵问答

**触发器：** H2/H3 每两段出现一次，一个简短文本的目录，一个 FAQ 块，一个结束语或“要点回顾”；自我提问超出任何真实 FAQ（“Pourquoi est-ce important ? Parce que... »）

这是记录在案的法国 AI 内容农场文档。幽灵问答模拟了一个不存在的对话，其中没有真正的问答。

**规则：** 一个标题必须至少控制至少四段——否则合并。删除 FAQ/quiz 块，除非媒介确实需要它们。将自我提问转换为直接陈述。

### 模式 35 — 持续的粒度

**触发器：** the whole text sits at one level of abstraction — no date, no name, no price, no error message, no quoted sentence; 1 500 words at mid-altitude

人类在抽象级别之间切换：他们从抽象中跳转到极具体的细节（日期、堆栈跟踪、价格），然后回到原来的级别。LLMs 在整个文本中巡航于中等抽象级别。

**规则：** 强制至少每节至少一个：一个可验证的、日期的、命名的细节。如果作者没有可提供的，那是一个内容问题，而不是风格问题（见第 4 部分的限制说明）。围绕它们进行重写。

### 模式 36 — 缺少漏洞

**触发器：** every question the text raises gets answered; no abandoned thread, no unresolved tension, no open problem

真正的专业知识会留下漏洞，因为作者知道知识在哪里停止。AI 文本解决它打开的每个问题——这种整洁性本身就是一个线索。这是结构上的对应物，而不是“je ne sais pas”（第 4 部分）。

**规则：** 真诚地留下至少一个问题。命名限制（“je n'ai pas testé au-delà de X ”）而不是将其四舍五入。

### 模式 37 — 列表作为回避

**触发器：** bullet lists appearing exactly where the reasoning gets hard — at the decision point, the trade-off, the prioritization

枚举取代了作者拒绝做出的选择：列出五个选项比选择一个更容易。模式 17 将列表视为格式线索；这个模式将列表视为论证症状。

**规则：** 在每个列表中，询问它回避了什么决定。用一句话选择——保留列表只有在项目确实是同级时才保留。

### 模式 38 — 缺少写作场合

**触发器：** nothing in the text explains why it exists, now, triggered by what, addressed to whom — no event, no encounter, no deadline, no request

人类文本解释了它为什么存在，现在，由什么触发，面向谁——没有事件、没有相遇、没有最后期限、没有请求。

**规则：** 在前几段中将其锚定在其写作场合中：它是什么让这篇文章值得写作，以及为谁。如果不存在场合，请作者提供它。

---

## 第四部分：个性和灵魂

**避免 AI 模式只是工作的一半。** 无声、无个性的文本与充满“crucial”和“dans le paysage de”的文本一样可疑。这是最“人类化”指南忽略的维度。

**了解限制。** 有经验的法语读者、调解人和调查员不再依赖风格：他们信任的行为和生态系统级别的信号（发布节奏、作者是否存在、来源是否经过核实）。没有任何模式清理可以修复一个没有任何定位内容的文本——向作者标记以请求一个真实的例子、一个日期、一个来源，并围绕它们进行重写。

### 保留语体

正式 ≠ AI。非正式文本在重写后不应降级。

- 保留复杂的结构（从句、插入语、周期性句子）当它们承载意义时。
- 只简化那些机械地格式化的内容——不是简单地正式。
- 根据输入的语体调整本指南中的示例——以下重写针对的是常用语体；对于正式文本，请保持相同的语言水平。

**无意见、无边缘、无个性**

- 每个句子都是相同的长度和结构
- 没有意见，只有中立报道
- 没有承认不确定性或矛盾情绪
- 在适当的时候使用第一人称
- 没有幽默，没有棱角，没有个性
- 读起来像维基百科文章或新闻稿

### 如何在法语中添加语气

**表达意见。** “Franchement, je ne sais pas quoi en penser ” 比中立的“delve”更有人性。

**改变节奏。** 短句有力地打击。然后是较长的句子，带有嵌套从句，慢慢展开。法语有节奏不对称的传统（蒙田、科兰、德波）。与 AI 文本相比，AI 文本单调地规律。

**承认复杂性。** “C'est impressionnant mais aussi un peu flippant ” 比简单的“C'est impressionnant ” 更好。

**使用“je ”。** 第一人称不是不专业的。**“ J'y reviens sans arrêt... ”** 表明人类在思考。个人语气是 strongest 真实性标记之一。

**留下一些混乱。** 完美的结构读起来像算法。旁白、括号、不完整的想法是人类。法语有悠久的括号传统（普鲁斯特是 caricature，但在技术写作中，旁白也表明真实性）。在 Markdown 中，段落之间的空格和换行符是正确的。

**使用二级语气（仅限非正式语体）。** 在非正式写作中，人类会省略“ne ”（“ c'est pas faux », « y'a un truc »）。使用夸张的形容词和包含双关语。AI 从来不会自发地写出“pb ”，“tjs ”或“ 14h30 ”——这些是便宜、强大的真实性标记。根据媒介和目标语体进行调整（见第 0 步）：在正式文档中，坚持使用 cf.、etc.、NB 和 p. ex.；避免完整的 SMS 语言（slt, bjr）到处使用，除非在真实的聊天中。

**使用罕见的单词。** AI 法语避免低概率单词，无论是“séide ”还是“ nonobstant ”，无论是“chelou ”还是“ relou ”。使用一个精心挑选的罕见单词——soutenu 或 argotique，与语体匹配——表明人类在选择，而不是模型平均。

**使用俚语和熟悉语体（当语体允许时）。** AI 法语是统一的，而俚语是注入真实个性的最便宜的方式。以下是按地区划分的俚语：

- **法国（熟悉/俚语）** : chelou, relou, ouf, avoir le seum, la flemme, une galère, ça me saoule, bosser, un boulot, un bouquin, le fric, la thune, une bagnole, kiffer, se planter, un truc de dingue, grave (= très), carrément, vachement, se prendre le chou, bidouiller, une magouille, au taquet, à l'arrache
- **比利时** : septante, nonante, un GSM, un kot, tantôt (= tout à l'heure), à tantôt, une aubette, la guindaille, s'il te plaît (en tendant un objet), une farde, savoir (= pouvoir : « je ne saurais pas venir »), il drache
- **魁北克** : niaiser, jaser, magasiner, pantoute, c'est plate, c'est correct, un char, un dépanneur, une blonde / un chum, avoir de la misère, être dans le champ, ça prend pas la tête à Papineau, c'est tiguidou, se faire passer un sapin, présentement, à matin
- **瑞士法语区** : un natel, septante / huitante / nonante, une panosse, un cornet (= sac plastique), ça joue, se réjouir de (= avoir hâte), un linge (= serviette), une votation, faire la pièce droite

**在地理上确定。** AI 默认使用巴黎标准法语。

- 地区主义是强大的真实性标记，如果它们适合作者的语气——并且它们在据称是魁北克人、比利时人或瑞士人的文本中是系统性的。如果使用不当，则使用地区主义（或法语中常见的比利时“une fois ”）比没有更好。
- 不要强迫使用它们：一个误用的地区主义（或法语中常见的“une fois ”）比没有更好。
- 匹配作者的真正来源、媒介和语体。

**承认口语（仅限熟悉语体）。** 在非正式写作中，人类会省略“ne ”（“ c'est pas faux », « y'a un truc »）。使用夸张的形容词和包含双关语。AI 从来不会自发地写出“pb ”，“tjs ”或“ 14h30 ”——这些是便宜、强大的真实性标记。根据媒介和目标语体进行调整（见第 0 步）：在正式文档中，坚持使用 cf.、etc.、NB 和 p. ex.；避免完整的 SMS 语言（slt, bjr）到处使用，除非在真实的聊天中。

**像人类一样缩短。** AI 会详细说明一切；人类会不断缩写。根据语体允许的范围散布：

- **缩写和用法标记** : PS:, NB:, cf., etc., ex: / p. ex., càd, RDV, ASAP, FYI, pour info, cc ( mettre en copie), CR (compte rendu), retex, N+1, RH, WE
- **单位和数字** : min (« 5 min de marche »), h collé (« 14h30 », « 2h de route »), km, € collé (« 30€ »), ~ pour « environ », nb (nombre)
- **常用缩写** : « nos soldats » 变成 “ nos _vaillants_ soldats ”, “ concitoyens ” 变成 “ concitoyennes et concitoyens ”。它过度纠正以符合其训练规范，而不是遵循源文本。恢复源文本的措辞。

**Medium 例外：** 在 Markdown 是原生格式的文档中——README、开发者文档、技术维基——标题、粗体、列表、表格和代码块是规范，而不是线索。此模式针对 Markdown 粘贴到不渲染它的上下文中，以及生成人工制品；它不适用于打算作为 Markdown 的文档。

---

## 流程

1. 仔细阅读输入文本。如果目标语体不明确，请在开始重写之前询问用户预期的语言水平
2. 识别所有 38 种模式的实例
3. 重写每个有问题的部分
4. 注入声音和个性（第 4 部分）
5. 确保修改后的文本：
   - 当以法语朗读时听起来自然
   - 变换句子结构（段落长度标准偏差）
   - 使用具体细节而不是模糊的声明
   - 维持适当的语体以适应上下文——如果输入是“soutenu”, 输出必须保持“soutenu”
   - 使用简单的结构（est/a/fait）在适当的地方
   - 使用正确的法语排版（斜体符号、空格、数字格式）
   - 不包含任何英语外来语（模式 #13）
6. 提交草稿人类化版本
7. 询问：“什么让这段文字明显是 AI 生成的？”
8. 简要回答剩余的线索（最多 2-3 个要点）
9. 询问：“现在，确保它不再如此。”
10. 提交最终版本
11. 生成 Résumé des modifications 列出删除的模式（见输出格式）

## 参考

基于：

- [Wikipedia:Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)（WikiProject AI Cleanup）
- [Wikipedia FR: Aide:Identifier l'usage d'une IA générative](https://fr.wikipedia.org/wiki/Aide:Identifier_l'usage_d'une_IA_générative)
- [Wikipedia FR: Projet:Observatoire des IA](https://fr.wikipedia.org/wiki/Projet:Observatoire_des_IA)
- [Labbé, Labbé & Savoy — ChatGPT as speechwriter for the French presidents](https://arxiv.org/abs/2411.18382)（唯一测量了法语 AI 生成的风格的定量研究：** également **, ** défi **, 时态和代词配置）
- [The Conversation — Comment « dé-IA-iser » nos écrits](https://theconversation.com/comment-de-ia-iser-nos-ecrits-pour-eviter-la-disparition-des-particularités-des-langues-281811)
- [Next — Comment reconnaître les sites d'infos générés par des IA](https://next.ink/165310/comment-reconnaitre-les-sites-dinfos-generes-par-des-ia/)（残留人工制品狩猎方法）

**新鲜度警告：** AI 线索会过期。em dash 在 2025 年 11 月丢失了大部分诊断价值；已发布的标记列表在几个月内就会被反向工程成规避工具；人类通过接触会使用 AI 词汇。节奏、结构、个性的差异比词汇列表老化得慢得多。

**主要见解：** LLM 生成最有可能的 token 序列。结果趋势是所有可能上下文中的平均值。使文本“人性化”意味着使其“属于你”：具体的、有意见的、古怪的。

**不适用于英语文本（→ See `samber/cc-skills@humanizer-en-asd-ste100` 技能用于 ASD-STE100 简化技术英语，或 `blader/humanizer@humanizer` 用于一般英语散文）。
