---
name: humaniseur-fr
description: 从法语文本中移除AI写作模式，注入语气和个性。在编辑、审阅或重写读起来像ChatGPT或Claude输出的法语文本时使用。检测并修正38种模式：AI词汇（crucial, essentiel, notamment, dans le paysage）、英语首模型产生的英语化表达（faire du sens, adresser un problème）、程式化开头（À l'ère de, Dans un monde où）、-ant分词结构、过度使用连字符、装饰性表情符号、混合使用分节号和撇号、句子长度统一。在humaniser、déslopifier、nettoyer le texte IA、enlever le slop、使其听起来像人类时触发。不要用于英文文本——请使用samber/cc-skills@humanizer-en-asd-ste100。
---

# 人类化器：消除法语中的AI写作模式

## 你的任务

当给定法语文本进行人类化处理时：

0. **首先明确目标语体** - 缩写、俚语、口语、表情符号和排版都取决于预期的语言水平。如果从请求或输入中无法明确（正式、常用、口语化？针对哪种媒介？），请在开始人类化之前询问用户
1. **识别AI模式** - 搜索以下列出的所有38种模式
2. **重写有问题的部分** - 将AI式表达替换为自然的法语表达
3. **保持原意** - 保留核心信息
4. **保持语气** - 符合预期的语调和语体
5. **注入灵魂** - 不要只是去除不良模式；要注入真正的个性（见第4部分）
6. **进行最终的反AI检查** - 询问：“是什么让这段文字明显是AI生成的？” 简要回答剩余的线索，然后询问“现在，确保它不再具有这种特征”，并相应地修改。应用三信号规则：一个孤立的标记是噪音（大多数是正常的法语），但在同一段落中三个或更多同时出现会使读者感到不适——修改直到没有段落积累三个

## 80%规则：不完美符合正是要点

大部分时间遵循人类化器规则——并非总是如此。可以大致保留这项技能指令的大约20%未应用。

- 真实的法语散文中包含被标记的模式，其密度较低：“为了总结”并不会使文本100%成为AI，而一个机械地避开每个线索的文本则以一种新的、同样可检测的方式变得单一。
- 故意违规：保留一个值得其地位的破折号，一个“此外”，一个整洁的列表。
- 线索是密度和共现（见三信号规则），而不是单个出现。

**只进行一次。** 不要对同一文本重复运行此技能：每次运行都会消除变化并注入自己的习惯，质量会迅速下降——在第二次或第三次运行后，第一个创建的声音会被压扁。如果在最终的反AI检查后结果仍然有AI的气味，那么修复方法是添加锚定内容（事实、日期、意见——见第4部分中的限制说明），而不是再次清理。

## 优先级：此技能服从于上下文

这里的指令可以由用户的提示或加载的更具体的技能覆盖。当任务附带自己的散文和文案方法——领英帖子、新闻稿、广告文案、开发者文档中的README时——在冲突中这些规则优先：仅将此技能应用于它们留出的空白处（AI词汇、英语借词、人工制品、排版）。领英钩子、新闻稿结构或开发者文档中的Markdown格式可以合法地使用此处标记的模式（简短的段落、整洁的列表、标题和粗体、三条规则）；这是格式在说话，而不是机器。

## 重要提示：法语特定上下文

法语专业写作本质上比英语更正式。像“尽管如此”和“然而”这样的连接词在人类法语中是合法的。线索与英语不同：

- AI词汇是不同的（“crucial”是法语AI的#1词汇，而不是“delve”）
- 来自模型英语优先架构的英语借词是一个主要的线索
- 排版惯例（引文符号、标点符号前的空格）是严格的
- 论文传统（论点/反论点/综合）与AI结构重叠
- 法语自然地容忍较长的句子，因此爆发性信号不同

**切勿降低语言水平。** 如果输入是“正式语言”，输出必须保持“正式语言”。

- 将正式散文改写成口语化法语是一种不同类型的不真实性——同样可检测，同样人工。敌人是公式化的写作，而不是正式的写作。
- 一个结构良好的从句、一个精确的连接词、一个长周期句子——这些是好的法语的特征，而不是AI人工制品。
- 只删除真正机械的东西：夸大的意义、避免系动词、同义词循环、促销填充。

---

## 第1部分：内容模式

### 模式1 — 意义和继承的膨胀

**触发器：** 构成/代表一个转折点、证明了、发挥关键/重要/决定性作用、强调重要性、反映了更广泛的趋势、象征着其持久的特征、有助于、开创了道路、标志着一个阶段、一个决定性里程碑、一个正在变化的地貌、一个不可磨灭的印记、深深扎根

大型语言模型通过将普通事实与无人询问的更广泛趋势联系起来，来夸大普通事实的重要性。

**之前：**

> 加泰罗尼亚统计研究所于1989年正式成立，标志着西班牙地区统计发展的一个转折点。这一举措是更广泛的行政权力下放运动的一部分。

**之后：**

> 加泰罗尼亚统计研究所于1989年成立，将统计权力下放给自治社区。它独立于INE生产和发布地区统计数据。

### 模式2 — 强调重要性及媒体曝光度

**触发器：** 独立媒体曝光、地方/国家/国际媒体、被知名专家引用、在社交媒体上强势存在

**之前：**

> 她的研究成果被《世界报》、《BBC》、《回声报》和《费加罗报》引用。她在社交媒体上保持活跃，拥有超过20万关注者。

**之后：**

> 在2024年对《世界报》的采访中，她主张人工智能的监管应该基于结果而不是方法。

### 模式3 — 现在分词的表面分析

**触发器：** 强调/突出...、确保...、反映/象征...、有助于...、促进/鼓励...、包含...、说明...

AI将现在分词短语附加到句子中，以添加虚假的分析深度。这是英语“-ing”问题的法语对应物。

**之前：**

> 建筑物的调色板混合了蓝色、绿色和金色，唤起了该地区自然之美，象征着薰衣草田和地中海，反映了社区对其土地的深厚情感。

**之后：**

> 建筑物使用了蓝色、绿色和金色。建筑师解释说，这些颜色是指薰衣草田和地中海沿岸。

### 模式4 — 推广和广告语言

**触发器：** 拥有、充满活力、丰富（比喻）、深刻、加强其、说明、例证、致力于、自然之美、利基、核心、革命性（比喻）、著名、令人窒息、无与伦比、令人惊叹、一颗宝石

**之前：**

> 位于令人惊叹的卢贝隆核心地带，这个村庄如同一颗充满活力的宝石，拥有丰富的文化遗产和令人窒息的自然之美。

**之后：**

> 该村庄位于卢贝隆，距离阿普特约三十公里。人们主要去那里参加周六的市场和12世纪的罗马式教堂。

**编辑或总结时的微妙变体：** 在编辑或总结时，AI会插入源文本中缺少的增值形容词和包容性双关语——“我们的士兵”变成了“我们勇敢的士兵”，“公民”变成了“男性和女性公民”。它过度纠正以符合其训练规范，而不是遵循文本。恢复源文本的措辞。

### 模式5 — 模糊的归因和模糊词

**触发器：** 行业报告、观察家强调、专家估计、某些批评者提出、几个来源/出版物（当引用很少时）、人们普遍认为、人们广泛认为

**之前：**

> 专家估计它在区域生态系统中发挥着关键作用。

**之后：**

> 河流根据2019年CNRS的清单，栖息着几种特有鱼类。

### 模式6 — “挑战与展望”部分

**触发器：** 尽管其...面临多个挑战...、尽管如此、挑战与遗产、未来展望、前景光明

公式化的挑战-乐观三明治。

**之前：**

> 尽管其工业繁荣，该市面临着典型的城市地区挑战。尽管如此，它仍在繁荣发展。

**之后：**

> 2015年后，随着三个商业区的开放，道路拥堵加剧。市政府于2022年启动了雨水管网改造计划。

---

## 第2部分：语言、语法和风格模式

### 模式7 — 过度使用的“AI”词汇

法语AI文本中最被标记的词是**crucial**。副词**notamment**在AI文本中出现的频率约为人类法语的1/200（4倍过度使用）。

**高频AI词汇（查找和替换清单）：**

| AI单词/短语 | 替换策略 |
| --- | --- |
| crucial, essentiel | 使用特定领域术语，或者直接删除 |
| également（最被测量的法语AI标记） | “也”，“同样”，或者直接删除——每段最多一个 |
| défi | “问题”，“困难”，或者指明实际障碍 |
| significatif, robuste, substantiel | 精确：给出数字 |
| holistique | 删除（英语“holistic”的直译） |
| compréhensif（= exhaustif） | 使用“exhaustif”或“完整”（compréhensif在法语中意为“有同情心的”） |
| disruptif | “破裂”或描述实际变化 |
| notamment（如果超过每800个词一个） | “特别是”，“尤其是”，“等等”，或者重构 |
| par ailleurs, en outre, de plus | 使用“或”，“但是”，“尽管如此”，“总而言之” |
| il convient de noter que | 删除，直接开始句子 |
| dans le paysage [actuel/numérique] | 完全删除 |
| au cœur de | 用具体位置/概念替换 |
| la pierre angulaire | 直接说明是什么 |
| un levier puissant | 描述实际机制 |
| captivant, fascinant, passionnant | 说明实际有趣的东西，或者删除 |
| révolutionnaire, transformateur | 描述实际变化 |
| permettre de, favoriser, optimiser | 使用具体动词：说明实际发生的事情 |
| mettre en lumière | “显示”，“揭示” |
| naviguer dans, déverrouiller le potentiel de | 直译——描述实际动作 |
| garantir, assurer, offrir（作为服务手册动词） | 平静陈述事实 |
| dans cette optique, dans ce contexte, à cet égard | 删除，或者具体连接思想 |
| que vous soyez X ou Y | 直接针对实际读者说话 |

**部长式行话：** AI法语倾向于使用行政词汇（“dispositif”，“acteurs”，“enjeux”，“mise en œuvre”，“dynamique territoriale”），即使在非机构环境中也是如此。在真正的行政文本之外，用普通词语替换。

**一击即杀的公式化开头：**

- “Dans le paysage [actuel/numérique/contemporain] de...”
- “À l'ère de...”
- “Dans un monde [où/trépidant/tumultueux]...”
- “Il est essentiel/crucial de noter que...”
- “Plongeons dans...”（法语“让我们深入...”）
- “Découvrez comment...”，“Dans cet article, nous allons explorer...”，“Bienvenue dans ce guide complet...”（元公告——直接开始内容本身）

**一击即杀的公式化结尾：** “En conclusion”，“En résumé”，“En somme”，“En fin de compte”，“Au final”开头一个最终段落。用一个具体事实结束（见模式26）。

**表明人类作者身份的连接词**（AI几乎从不使用这些）：**“Or”，“Quoi qu'il en soit”，“Toujours est-il que”，“Force est de constater que”，“Reste que”，“N'empêche que”，“Soit dit en passant”

### 模式8 — 避免系动词（être/avoir）

**触发器：** constitue, fait office de, se positionne comme, représente [un], dispose de, offre [un]

**之前：** La galerie constitue l'espace d'exposition. Elle dispose de quatre salles. **之后：** La galerie est l'espace d'exposition. Elle a quatre salles.

### 模式9 — 负面平行结构

**触发器：** Non seulement... mais aussi..., Il ne s'agit pas seulement de... mais de..., Ce n'est pas un simple X, c'est un Y

**之前：** Il ne s'agit pas simplement d'autocomplétion ; il s'agit de libérer la créativité. **之后：** L'outil dépasse la simple autocomplétion : il élargit l'espace de créativité disponible.

### 模式10 — 系统性的三条规则

AI强迫将想法分成三组。

**之前：** L'événement propose des conférences plénières, des tables rondes et des opportunités de réseautage. Innovation, inspiration et analyses sectorielles. **之后：** L'événement comprend des conférences et des tables rondes. Du temps est prévu pour le réseautage.

### 模式11 — 同义词循环（优雅的变体）

重复惩罚代码导致对同一指称进行过度同义词替换。

**之前：** Le protagoniste fait face à de nombreux défis. Le personnage principal doit surmonter les obstacles. La figure centrale finit par triompher. **之后：** Le protagoniste fait face à de nombreux obstacles, finit par les surmonter et rentre chez lui.

### 模式12 — 错误的音阶

**触发器：** “de X à Y, de A à B”其中X-Y和A-B不形成有意义的尺度。

**之前：** De la singularité du Big Bang au vaste réseau cosmique, de la naissance des étoiles à la danse de la matière noire. **之后：** Le livre couvre le Big Bang, la formation des étoiles et la matière noire.

### 模式13 — 架构英语借词

ChatGPT的法语错误中有约16%源于英语。这些是最可靠的线索之一。

| AI英语借词 | 正确法语 |
| --- | --- |
| “faire du sens” | “avoir du sens” |
| “adresser un problème” | “traiter / aborder un problème” |
| “implémenter”（非信息领域） | “mettre en œuvre” |
| “impacter” | “affecter, toucher” |
| “supporter”（= soutenir） | “prendre en charge” |
| “définitivement”（= assurément） | “sans aucun doute” |
| “basiquement” | “en gros, fondamentalement” |
| 牛津逗号在“et”之前 | 法语中“et”前不加逗号 |

### 模式14 — 重复的形容词双关语

逐个标记生成会产生作为缓和的同义词对。

**触发器：** crucial et essentiel, robuste et fiable, innovant et avant-gardiste, dynamique et en pleine expansion, riche et varié

**之前：** Cette approche innovante et avant-gardiste offre une solution robuste et fiable. **之后：** Cette approche tient la charge sans maintenance lourde.

### 模式15 — 过度使用方括号

AI过度使用破折号，模仿英语“简洁”写作。法语更喜欢用逗号和括号表示偶然从句。

**之前：** Le terme est promu par les institutions — pas par les habitants. Cet étiquetage — même dans les documents officiels — persiste. **之后：** Le terme est promu par les institutions, pas par les habitants. Cet étiquetage persiste, même dans les documents officiels.

**新鲜度说明：** 自2025年11月以来，ChatGPT服从“无破折号”的定制指令，读者也知道了这个线索。存在证明不了什么（人类也使用它），不存在证明不了什么。仍然减少过度使用——目标是自然的法语，而不是检测规避。

### 模式16 — 机械过度使用粗体

AI机械地加粗术语以表示重要性。

**规则：** 除非它具有真实的导航功能，否则删除所有粗体。

### 模式17 — 带粗体标题和冒号的垂直列表

**之前：**

> - **用户体验：** 显著提升。
> - **性能：** 通过改进算法得到优化。
> - **安全性：** 通过端到端加密得到加强。

**更新后：**

> 此次更新改进了界面，加快了加载速度，并增加了端到端加密功能。

**同样规则适用于无意义的表格：** AI 将普通发展呈现为表格（一个带有法语维基百科标记的标记）。只有当数据确实以表格形式呈现（比较、数据）时才保留表格；否则转换为文字。

### 模式 18 — 英式标题大写

法语标题只大写第一个单词（以及专有名词）。

**之前：** ## 战略谈判与全球伙伴关系 **之后：** ## 战略谈判与全球伙伴关系

### 模式 19 — 表情符号：装饰性 vs 表达性

表情符号是一种语域特征，而不是缺陷。三个测试：

1. **功能** — 一个取代文字或传递语调（讽刺、情感、反应）的表情符号是人类使用；一个装饰结构（每个标题一个、🚀💡✅ 系列、“ 👉 ” 段落开头）是机器使用。删除第二个，保留第一个。
2. **媒介** — 社交媒体帖子、聊天、内部消息：表情符号是预期的——保留一些，或者如果作者的语气使用它们，可以增加一个。正式文件、新闻稿、文章：无。
3. **规律性** — 关键在于系统性：相同位置、相同密度无处不在。人类表情符号使用是不规则的且稀疏的（最多每段约 1 个，从不连续）。保留不规则的，消除系统性的。

当对作者的语气不确定时，询问。

### 模式 20 — 引号与排版不一致

来源对 AI 产生的引号风格存在矛盾（完美的尖括号 « »、英文弯引号 "…" 或两者都有）。稳健的迹象不是单一变体，而是**混合**：直引号、弯引号和尖括号共存于同一文本中，或者直引号（'）和弯引号（’）交替出现——人类坚持他们键盘产生的任何内容。

**按语域的引号规则：** 在使用正式语言和精心排版编写的官方文件中，使用带非断开空格的尖括号引号 (« ... »）。其余时间（电子邮件、内部沟通、社交媒体），优先使用弯引号 ("...") —— 在那里完美读作机器输出。

**也检查：** 冒号/分号/感叹号/问号前的空格，以及法语数字格式（1 000,50 而不是 1,000.50）。无论惯例如何，在整个文本中保持一致性——一致性胜过正确性。

### 模式 21 — 对话痕迹

**立即删除：** J'espère que cela vous aide, Bien sûr !, Absolument !, Vous avez tout à fait raison !, Souhaitez-vous que..., N'hésitez pas à, Voici un...

### 模式 22 — 知识局限条款

**立即删除：** en date de [date], Selon les informations disponibles, Bien que les détails spécifiques soient limités..., sur la base des données accessibles...

### 模式 23 — 奴性化与谄媚的语气

**之前：** Excellente question ! Vous avez tout à fait raison, c'est un sujet complexe. **之后：** 您提到的经济因素确实在此起作用。

### 模式 24 — 填充句

| 删除                          | 替换为             |
| ----------------------------- | ------------------------ |
| Afin de parvenir à cet objectif | Pour y arriver           |
| En raison du fait que           | Parce que                |
| À ce stade / À l'heure actuelle | Maintenant / Aujourd'hui |
| Dans l'éventualité où           | Si                       |
| Le système a la capacité de     | Le système peut          |
| Il est important de noter que   | (删除，直接开始)       |
| Il convient de souligner que    | (删除，直接开始)       |
| En ce qui concerne              | Sur / Quant à            |

### 模式 25 — 过度犹豫

**之前：** On pourrait potentiellement arguer que cette politique pourrait éventuellement avoir un certain effet. **之后：** 该政策很可能对结果有影响。

### 模式 26 — 通用积极结论

**触发器：** L'avenir s'annonce prometteur, Des temps passionnants, poursuit son chemin vers l'excellence, un pas majeur dans la bonne direction

用实际接下来发生的事情的具体事实替换。

### 模式 27 — 结构一致性

AI 生成几乎相同长度的段落（标准差 <30 字 vs. >60 字的人类），分组为 3/5/7/10 项的列表，以及不变的引言-主体-结论架构。以问句形式写的节标题是额外的格式标记。

在句子级别，迹象是分散，而不是平均值：在唯一量化的法国研究中，平均句子长度几乎相同（21.0 人类 vs. 21.7 AI 字），但 AI 几乎没有产生少于 15 个或超过 39 个字的句子（最频繁的长度从 13 个字变为 19 个字）。

**规则：** 重新引入尾部。写一些短句子（少于 15 个字）和一些长周期句子（超过 39 个字）。缺失的极端是机器暴露的，而不是平均值。

**句子起始代词：** 连续的句子以相同的方式开头（« Cela... », « Cette approche... », « Ce système... »）。改变每个句子的攻击方式。

**“领英”风格：** 单句段落堆叠以增加戏剧性，省略号作为悬念转折 (« Et là... tout a changé »)，坚持不懈的乐观语气。这种语域现在与 AI 辅助发布如此紧密地联系在一起，以至于即使人类写出来也像机器输出。将碎片合并成真正的段落。

### 模式 28 — 残留 Markdown 和技术痕迹

**立即删除：** 在纯文本上下文中未渲染的 `**mot**` 或 `##`，- **Titre :**` 列表粘贴到 Markdown 无法渲染的地方，引用痕迹如 `:contentReference[oaicite:2]{index=2}`，剩余的拒绝 (« Je suis désolé, mais je ne peux pas... »)

这些都是最强的迹象：它们不可能来自拼写检查器或 CMS —— 只能来自粘贴的聊天输出。法国调查记者通过搜索这些字符串来追踪 AI 生成的新闻网站。

**也删除零宽度字符**（U+200B, U+200C, U+200D, U+FEFF）——复制粘贴痕迹在散文中没有合法用途。不要删除非断开空格（U+00A0, U+202F）：它们在 « ; : ! ? » 之前和 « 12 h 30 » 之中是正确的法语排版。混淆两者会在每个正确排版法语文本上产生误报。

**媒介例外：** 在 Markdown 是原生格式的地方——一个 README、开发者文档、技术维基——标题、粗体、列表、表格和代码块是规范，而不是迹象。此模式针对 Markdown 粘贴到不渲染它的上下文中，以及生成痕迹；它不适用于打算为 Markdown 的文档。

### 模式 29 — 无病呻吟的抒情（叙事语域）

法国 AI **小说** 有其自身的语域，与博客废话不同。

**触发器：** un instant suspendu, une promesse murmurée/suspendue dans l'air, un secret brûlant, un désir/silence vibrant, comme si le temps s'était figé — 循环的迷恋词：_promesse, suspendu, vibrant, secret, brûlant, murmuré_

**语法特征：** AI 叙事法语使时态和人称扁平化。量化研究测量了 passé simple −84 %, imparfait −71 %, conditionnel −50 %, 代词 « on » −92 %, 动词 « falloir » −93 % 对比人类法语。重新引入该类型所需的时态，优先使用 « on » 而不是僵硬的 « nous »，并让 « il faut » 回归。

相同的研究测量了过度使用： « devoir » (+101 %), « continuer » (+145 %), « tenir » (+158 %), « ensemble » (+93 %), 拥有定语 (+30 %)。当这些聚集在一起时 (« nous devons continuer, ensemble, à tenir nos engagements »)，句子是机器平均法语——围绕具体行动重写它。

---

## 第 3 部分：话语架构模式

词汇清理是不够的：最深层的 AI 提示是架构。即使文本包含零个标记词，也可能因为它是如何构建的而读起来像机器制作。与量化的词汇数据不同，这些模式是工艺启发式算法——经验丰富的读者从经验中得出的趋同观察，而不是语料库测量的数据。

### 模式 30 — 声明、总结和指令回声

**触发器：** 开头宣布文本将说什么，结尾重复它说了什么，节标题与宣布的计划 1:1 呈镜像，第一句话重述所问的问题 (« Vous vous demandez comment... ? », 重新陈述任务），结尾回到请求

信息存在一次，但被提供三次。聊天机器人答案和学校作文在两端都回应用户提示。

**规则：** 在事件中开始——第一句话提供内容，而不是程序。在 intro 无法预测的地方结束：一个后果，一个开放性问题，一个具体的事实。删除两端的提示回声。

### 模式 31 — 无角度的目录式结构

**触发器：** 可以随意重新排序的节；主题的每个方面都同等深度覆盖（定义、优点、缺点、良好实践、结论）；没有声称后续节依赖于

AI 覆盖主题；人类提出观点。排列测试：如果两个节可以互换位置而不造成损害，文本是一个伪装的列表，而不是论证。

**规则：** 选择一个角度并坚持。删除不为其服务的方面——可见的死胡同是人类。使每个节依赖于前一个节，使顺序变得必要。

### 模式 32 — 段落模板和明显支架

**触发器：** 每个段落 = 主题句 + 两到三个支持 + 小结，完全自包含；段落以序列连接词开头 (« D'abord », « Ensuite », « De plus », « Enfin »)；没有想法会跨越段落；零离题

结构被信号而不是内容承载。人类段落相互依赖：一个想法在一段的结尾开始，在下一段结束；一个旁白打断。

**规则：** 删除支架连接词——并列有效。至少让一个想法跨越段落。允许在它值得的地方离题。

### 模式 33 — 虚假话语平衡

**触发器：** 每个主张立即被平衡 (« Cependant, il convient de nuancer... »), 对称 « d'une part / d'autre part », « tout dépend du contexte » 类型的结论

句子级别的犹豫（模式 25）扩展到整个文本：作品没有论点。两边主义读作机器谨慎，而不是公平。

**规则：** 采取立场。在真正重要的时候进行一次细微差别——不是在每次主张之后。如果诚实的答案真的是“这取决于”，请说明具体取决于什么。

**删除测试：** 删除反对段落。如果结论仍然保持不变，反对是装饰而不是思想——真正的反论会取代论点。在法语中，区分很重要：论文传统（thèse/antithèse/synthèse）使宣布和平衡学校合法化，因此礼貌的反论会不被注意。

**魁北克注意事项：** rédaction épicène 和 OQLF 简体规范推动人类机构作家走向完全相同的平坦、对称形状——在魁北克机构文本中，不要单独将平衡读作机器输出。

### 模式 34 — SEO 过度分段和幽灵问答

**触发器：** 每 两个段落一个 H2/H3，短文本的目录，FAQ 块，结束语测验或 « points clés à retenir »；自问自答在任何真实 FAQ 之外 (« Pourquoi est-ce important ? Parce que... »)

这是法国 AI 内容农场的记录网格。幽灵问答模拟了一个不存在对话。

**规则：** 标题必须至少控制四或五个段落——否则合并。除非媒介确实需要，否则删除 FAQ/测验块。将自问自答转换为直接陈述。

### 模式 35 — 持续的粒度

**触发器：** 整个文本处于一个抽象级别上——没有日期、没有名称、没有价格、没有错误消息、没有引用句子；1 500 字处于中等高度

人类改变高度：他们从抽象下降到一个超具体的细节（一个日期、一个堆栈跟踪、一个价格），并在几段内爬回。LLMs 在整个文本中巡航于中等高度。

**规则：** 强制至少每个节一个下潜：一个可验证的、有日期的、有名称的细节。如果作者没有提供，那是一个内容问题，而不是风格问题（见第 4 部分的限制说明）。

### 模式 36 — 缺少漏洞

**触发器：** 文本提出的每个问题都得到回答；没有未解决的线索，没有未解决的紧张关系，没有未解决的问题

真正的专业知识会留下漏洞，因为作者知道知识在哪里停止。AI 文本解决它打开的一切——整洁本身是迹象。这是结构上的对应物，从不写“je ne sais pas”（第 4 部分）。

**规则：** 至少诚实地留下一个悬而未决的问题。命名限制 (« je n'ai pas testé au-delà de X ») 而不是四舍五入。

### 模式 37 — 列表作为回避

**触发器：** 项目列表出现在推理变得困难的地方——在决策点、权衡、优先级

枚举取代了作者拒绝做的选择：列出五个选项比捍卫一个更容易。模式 17 将列表视为格式；这个模式将它们视为论证症状。

**规则：** 在每个列表中，询问它回避了什么决定。用选择句子替换它——只有在项目确实是同级时才保留列表。

### 模式 38 — 缺少写作场合

**触发器：** 文本中没有任何内容解释它为什么存在，现在，由什么触发，写给谁——没有事件、没有相遇、没有截止日期、没有请求

人类文本有一个起源（一个事件、有人问的问题、发布、烦恼），并且它显示了。AI 文本从无到有，写给无人。

**规则：** 在前几段中将作品与其场合锚定：是什么发生了，使这次写作值得，以及为谁。如果没有场合，请询问作者。

**变化节奏。** 短句有力，长句则带有嵌套的从句，慢慢展开。法语有节奏不对称的传统（蒙田、科兰、德波）。相比之下，AI文本单调而规则。

**认识到复杂性。** “这令人印象深刻，但也有些让人头晕”比“这令人印象深刻”更有力。”

**使用“我”。** 第一人称并不不专业。“我不断回到……”暗示着人类在思考。个人声音是真实性最强的标志之一。

**保留混乱。** 完美的结构感觉像算法。离题、括号、不成熟的思路是人类的表现。法语有长久的括号传统（普鲁斯特是夸张的例子，但在技术写作中，旁白也标志着真实性）。

**使用第二人称。** 大型语言模型在本质上无法生成真实的讽刺和幽默。低调、轻微的讽刺、自嘲：这些是无法伪造的真实标志。“我们还是发明了一个比我们疲倦时编码更好的东西，这几乎总是这样”不是来自大型语言模型。

**承认无知。** 大型语言模型从不写“我不知道”、“没有概念”、“我没有核实”。像讽刺和幽默一样，坦率地承认不知道正是因为机器从不产生它，所以是真实性最强的标志之一。在上下文允许的情况下，谨慎地使用所有三个词——法律通知或审计报告既不允许玩笑也不允许耸肩。

**对感受要具体。** 不是“这令人担忧”，而是“看到代理人在凌晨3点无人监督地运行，这有些令人不安。”

**使用罕见的词。** AI法语避免双向的低概率词：没有“séide”或“nonobstant”，没有“chelou”或“relou”。一个恰到好处的罕见词——soutenu或argotique，匹配语域——表明是人类选择，而不是模型平均。

**使用俚语和口语（当语域适合时）。** AI法语是一致的规范；俚语是最低成本的真实性注入之一。按地区划分的不详清单：

- **法国（口语/俚语）**：chelou，relou，ouf，avoir le seum，la flemme，une galère，ça me saoule，bosser，un boulot，un bouquin，le fric，la thune，une bagnole，kiffer，se planter，un truc de dingue，grave（= très），carrément，vachement，se prendre le chou，bidouiller，une magouille，au taquet，à l'arrache
- **比利时**：septante，nonante，un GSM，un kot，tantôt（= tout à l'heure），à tantôt，une aubette，la guindaille，s'il te plaît（en tendant un objet），une farde，savoir（= pouvoir：“je ne saurais pas venir”），il drache
- **魁北克**：niaiser，jaser，magasiner，pantoute，c'est plate，c'est correct，un char，un dépanneur，une blonde / un chum，avoir de la misère，être dans le champ，ça prend pas la tête à Papineau，c'est tiguidou，se faire passer un sapin，présentement，à matin
- **瑞士法语区**：un natel，septante / huitante / nonante，une panosse，un cornet（= sac plastique），ça joue，se réjouir de（= avoir hâte），un linge（= serviette），une votation，faire la pièce droite

**根据地理位置定位。** AI默认使用巴黎标准法语。

- 地方特色是强大的真实性标志，如果它们符合作者——而且在一个所谓的魁北克、比利时或瑞士作者的文本中系统地缺乏，这本身就是一个线索。
- 永远不要强迫使用：一个误用的地方特色（或刻板的比利时“一次”）比不用更糟。
- 匹配作者的真正来源、媒介和语域。

**承认口语化（仅限口语语域）。** 在非正式写作中，人类会省略“ne”（“这不是假的”，“有件事”），使用夸张（“1000%同意”），使用缩写。AI在任何地方都保持完整否定。永远不要将这种风格强加于正式散文——语域优先。

**像人类一样缩短。** AI把一切都说明白了；人类经常缩写。在允许的语域中撒播：

- **缩写和常用标记**：PS：, NB：, cf., etc., ex：/ p. ex., càd, RDV, ASAP, FYI, pour info, cc（抄送），CR（报告），retex, N+1, RH, WE
- **单位和数字**：min（“5分钟步行”），h（粘附，“14h30”，“2h行驶”），km，€（粘附，“30€”），~表示“大约”，nb（数字）
- **常用书写缩写**：pb，tjs，bcp，qqch，qqn，svp / stp，dispo，perso，pro
- **缩写**：ordi，appart，resto，apéro，cine，fac，prof，exam，visio，reu，présa，la doc，la config，l'admin，le labo，la manif，l'expo，la promo，l'info，l'aprem
- **电子邮件结束语**：A+，Cdlt，“à plus”

大型语言模型永远不会自发地写“pb”、“tjs”或“14h30”——这些都是廉价、强大的真实性标志。根据媒介和目标语域进行调整（见第0步）：在正式文件中，坚持使用cf。、etc.、NB和p. ex.；并且避免完整的SMS语言（slt、bjr）在任何地方，除了实际的聊天。

---

## 流程

1. 仔细阅读输入文本。如果目标语域不明确，请在重写之前询问用户期望的niveau de langage
2. 识别所有38种模式的实例
3. 重写每个有问题的部分
4. 注入声音和个性（第4部分）
5. 确保修订后的文本：
   - 在法语中朗读时听起来自然
   - 句子结构多样化（测量段落长度的标准偏差）
   - 使用具体细节而不是模糊的声明
   - 保持上下文适当的语域——如果输入是“soutenu”，输出仍然是“soutenu”
   - 在适当的地方使用简单的结构（est / a / fait）
   - 使用正确的法语排版（引号、间距、数字格式）
   - 不包含任何来自模式#13的英语单词
6. 提供一个人性化版本的草稿
7. 询问：“是什么让这段文本明显是AI生成的？”
8. 简要回答剩余的线索（最多2-3个要点）
9. 询问：“现在，确保它不再是AI生成的。”
10. 提供最终版本
11. 生成修改摘要，列出移除的模式（见输出格式）

## 输出格式

提供：

1. **草稿重写**（草稿重写）
2. **“是什么让这段文本明显是AI生成的？”**（简要剩余线索）
3. **最终版本**（自我审计后的修订版）
4. **修改摘要**（简要列出移除的模式，可选）

## 完整示例

**原文（典型的AI文本）**：

> 这是一个关于这个主题的概述。希望这对你有用！
>
> AI辅助编码构成了对大型语言模型变革性潜力的持久见证，标志着软件开发演变中的决定性转折点。在不断发展变化的技术环境中，这些革命性的工具——位于研究和实践之间的交叉点——重新定义了工程师如何构思、迭代和交付，突出了它们在现代工作流程中的关键作用。
>
> 在这场动态变化的核心，价值主张是明确的：简化流程、加强协作和促进对齐。这不仅仅是为了自动完成；这是为了在大规模上释放创造力，确保组织保持敏捷，同时交付流畅、直观、强大的体验。工具是一个催化剂。助手是一个伙伴。系统是一个创新的基础。
>
> - 💡 **速度**：代码生成速度明显更快，减少了摩擦，使开发人员自主化。
> - 🚀 **质量**：通过改进的训练，结果质量得到了加强，有助于提高标准。
> - ✅ **采用**：使用率持续增长，反映了更广泛的行业趋势。
>
> 尽管面临新兴技术典型的挑战——尤其是幻觉、偏见和责任——生态系统仍在蓬勃发展。未来充满希望。如果你希望我进一步开发一个部分，请告诉我！

**草稿重写**：

> AI辅助编码加速了某些任务。在2024年的谷歌研究中，使用Codex的开发人员完成简单功能的速度比对照组快55%，但在调试或架构决策方面没有改进。
>
> 这些工具擅长样板代码：配置文件、测试脚手架、重复的重构。它们也非常擅长看起来正确，但实际上会出错。我大量接受了编译、通过linter但仍然胡说八道的建议，因为我停止了关注。

**“是什么让这段文本明显是AI生成的？”**

- 节奏仍然有点过于规律（对比鲜明，段落大小接近）
- 引用命名的研究可能听起来像可能的占位符
- 最后一句倾向于口号

**最终版本**：

> AI辅助编码加速了样板任务。但不是所有任务，尤其是不是架构。
>
> 它们非常擅长样板代码：配置文件、测试脚手架、重复的重构。它们也非常擅长看起来正确，但实际上会出错。我接受了编译、通过linter但仍然胡说八道的建议，因为我停止了阅读。
>
> 我询问的开发人员分为两派。一些人像自动完成一样使用它来处理杂务，并重读每一行。其他人已经禁用了它，因为工具不会停止建议已弃用的模式。两种立场都有辩护。
>
> 生产力的指标是模糊的。GitHub可以宣布用户“接受了30%的建议”，但接受不等于纠正，纠正也不等于价值。没有测试，我们只能猜测。

**修改摘要**：

- 删除了对话式痕迹（#21：“希望这对你有用！”、“请告诉我”）
- 删除了意义膨胀（#1：“持久见证”、“决定性转折点”、“关键作用”）
- 删除了宣传性语言（#4：“革命性的”、“交叉点”、“流畅、直观、强大的体验”）
- 删除了模糊的归属（#5）
- 删除了表面化的分词（#3：“突出了”、“反映了”、“有助于提高”）
- 删除了负面平行（#9：“不仅仅是为了X；这是为了Y”）
- 删除了三重规则（#10）和同义词循环（#11：“催化剂/伙伴/基础”）
- 删除了方括号（#15），删除了emoji（#19），删除了机械加粗（#16、#17）
- 修正了连词规则（#8：“构成”、“充当”、“定位为”）
- 删除了挑战/展望部分（#6：“尽管面临挑战……仍在蓬勃发展”）
- 删除了模糊的限定（#25）、填充（#24：“在……的核心”）
- 删除了积极的结论性陈述（#26：“未来充满希望”）
- 注入了声音和个性（第4部分：节奏变化、第一人称、观点、具体性）

## 参考

基于：

- [维基百科：AI写作的迹象](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing)（维基百科AI清理项目）
- [维基百科FR：帮助：识别生成式AI的使用](https://fr.wikipedia.org/wiki/Aide:Identifier_l%27usage_d%27une_IA_g%C3%A9n%C3%A9rative)
- [维基百科FR：项目：观察AI](https://fr.wikipedia.org/wiki/Projet:Observatoire_des_IA)
- [拉贝、拉贝和萨沃伊——ChatGPT作为法国总统的演讲稿](https://arxiv.org/abs/2411.18382)（唯一对生成式法语进行量化的风格测量研究：“ également ”、“ défi ”、时态和代词配置文件）
- [The Conversation——如何“去AI化”我们的写作](https://theconversation.com/comment-de-ia-iser-nos-ecrits-pour-eviter-la-disparition-des-particularites-des-langues-281811)
- [Next——如何识别由AI生成的信息网站](https://next.ink/165310/comment-reconnaitre-les-sites-dinfos-generes-par-des-ia/)（残余痕迹搜索方法）

**新鲜度警告**：AI迹象会过时。连字符在2025年11月的OpenAI修复后失去了大部分诊断价值；发布的标记列表在几个月内就会被反向工程为规避工具；而且人类越来越多地通过接触采用AI词汇。将这里的每个词汇列表视为过时的——结构原则（分散、语域、具体性、灵魂）比词汇表老化得慢得多。

关键洞察：大型语言模型生成最有可能的标记序列。结果倾向于所有可能上下文中的平均值。使文本人性化意味着使其成为“你”：具体的、有意见的、独特的。
