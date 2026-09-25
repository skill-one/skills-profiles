# Unslop

编辑文本以去除 AI 模式。

## 流程

1. 扫描以下模式。
2. 重写。保留含义，匹配预期语气。
3. 自我审计："是什么让这段文字明显是 AI 生成的？" 修复剩余的线索。

## 需要检测和修复的模式

规则编号是其他技能引用的稳定 ID。删除一条规则会留下一个空白。

### 内容

3. **表面化的 -ing 短语。** "highlighting..."、"ensuring..."、"reflecting..."、"showcasing..."、"fostering..."。删除或用真实来源扩展。
5. **模糊的归因。** "Experts believe"（专家认为）、"Industry reports suggest"（行业报告建议）、"Some critics argue"（一些批评家认为）。命名来源或删除。

### 语言

7. **AI 词汇。** 此外、crucial（关键）、delve（深入研究）、enduring（持久的）、enhance（增强）、fostering（培养）、garner（获取）、interplay（相互作用）、intricate（错综复杂的）、landscape（抽象）、pivotal（关键的）、showcase（展示）、tapestry（抽象）、testament（证明）、underscore（强调）、vibrant（充满活力的）。用简单的词语替换。
8. **"是"的华丽说法。** "serves as"（充当）、"stands as"（作为）、"boasts"（拥有）、"features"（以...为特色）。直接说 "is"（是）或 "has"（有）。
9. **"不仅仅是 X，而且是 Y。"** 直接陈述观点。
10. **三点规则。** 将想法强行分组为三个。使用自然数字。
11. **同义词循环。** 一个段落中包含主角、main character（主要角色）、central figure（中心人物）、hero（英雄）。选择一个，重复它。
12. **虚假的范围。** "from X to Y"（从 X 到 Y），其中 X 和 Y 不是在有意义尺度上的。直接列出主题。

### 风格

13. **连字符过度使用。** 完全避免连字符。仅使用句号或逗号（不要括号、不要连字符、不要作为连字符的符号替代）。如果一个想法需要分隔，结束句子或使用逗号。
14. **冒号过度使用。** 冒号在列表或示例之前是合适的。不作为句子中的连接符。"If you're coming from traditional automation: instead of registering event handlers, you describe conditions"（如果你来自传统自动化：而不是注册事件处理程序，你描述条件）与冒号一起什么都没增加。重写，让观点在没有比较框架的情况下自立。"Describing when the scheduler should fire works best as plain English."（描述调度器何时触发最好用平实的英语。）相同含义，没有辅助标点。
15. **粗体过度使用。** 不要粗体每个专有名词或缩写。
16. **行内标题列表。** 线索是一个粗体标签和冒号，它重述了这一行："**Performance:** Performance improved..."（**性能：** 性能提高...）。将这些转换为散文。一个以句号结尾的粗体引言，命名项目，并随后跟上有真正新细节的引言（"**Schema in TypeScript.** Tables live in one file."（**TypeScript 中的模式。** 表单存储在一个文件中。））是好的，不是线索。
17. **标题大小写标题。** 使用句子大小写。
18. **装饰性表情符号。** 从标题和项目符号中删除。
19. **弯引号。** 替换为直引号。

### 沟通痕迹

20. **聊天机器人短语。** "I hope this helps!"（我希望这有帮助！）、"Let me know if..."（如果让我知道...）、"Of course!"（当然！）、"Certainly!"（当然！）、"Found the smoking gun!"（找到了烟枪！）。删除。
22. **奉承语气。** "Great question! You're absolutely right!"（好问题！你绝对正确！）直接回应。

### 填充词

23. **填充短语。** "In order to"（为了）变成 "To"（到）、"Due to the fact that"（由于）变成 "Because"（因为）、"It is important to note that"（重要的是要注意）被删除。
24. **过度犹豫。** "could potentially possibly be argued that it might"（可能可能可能被论证）变成 "may"（可能）。
25. **通用结论。** "The future looks bright."（未来看起来光明。）陈述具体计划或事实。

### 行话

26. **抽象隐喻名词。** Substrate（基质）、wedge（楔子）、vector（向量）、locus（焦点）、vantage（优势）、nexus（中心）、primitive（作为名词）、harness（作为隐喻）、surface（例如 API surface）、bedrock（基石）、scaffolding（作为隐喻）、modality（模式）、paradigm（范式）、gold-plating（过度装饰）、ratchet（作为隐喻）、evacuate（移动代码）、endgame（终局）、north star（北极星）、flywheel（飞轮）。这些看起来像技术术语，但通常有一个更简单的具体词语。"Substrate"（基质）变成 "base"（基础）。"Wedge in"（楔入）变成 "add"（添加）。"Vector"（向量）变成 "way"（方式）或 "method"（方法）。"Gold-plating"（过度装饰）变成 "more than the job needs"（比工作需要的更多）。"Ratchet"（作为隐喻）变成机制的真实名称或 "a limit that only tightens"（一个只会收紧的限制）。"Evacuate"（移动）变成 "move out"（搬出）。"Endgame"（终局）变成 "the last phase"（最后阶段）。选择具体词语。

### 平实语言

27. **说出它做什么，而不是感觉如何。** "the database stays close at hand"（数据库保持在手边）、"SQL you can read"（你可以阅读的 SQL）、"types that follow your schema"（遵循你模式的类型）命名一种感觉。修复命名机制或数字："`.toSQL()` returns the exact string sent to the database"（`.toSQL()` 返回发送到数据库的确切字符串）、"a column rename fails the build"（列重命名导致构建失败）。问句子告诉读者做什么或知道什么，然后写下来。如果你不能将其重述为具体的指令、事实或数字，就删除它。一个额外的检查：如果句子可以不变地出现在另一个项目的文档中，它对这个项目什么都没说。删除它。
28. **缩短或拆分密集的句子。** 如果读者必须回溯来解析一个句子，将其分成两部分或删除从句。每个句子一个想法。
29. **主动语态。** 优先考虑它。捕获 "is/are/was/were + 过去分词" 并命名行动者："queries are validated"（查询被验证）变成 "the compiler validates queries"（编译器验证查询）、"the file is parsed by the loader"（文件由加载器解析）变成 "the loader parses the file"（加载器解析文件）。被动语态只有在行动者未知或确实不重要时才合适。
30. **删除副词，或使用更强的动词。** "runs quickly"（运行快速）变成 "is fast"（很快）或数字。"significantly improves"（显著改进）变成测量的差异。一个支撑弱动词的副词意味着动词是错误的。
31. **优先使用平实词语。** "utilize"（利用）变成 "use"（使用）、"leverage"（利用）变成 "use"（使用）、"facilitate"（促进）变成 "help"（帮助）、"numerous"（许多）变成 "many"（许多）、"in the event that"（如果）变成 "if"（如果）。更华丽的同义词很少更清晰。
32. **文雅的散文。** 在存在字面短语的地方使用隐喻或华丽辞藻：警句（"wire it or delete it"（连接它或删除它））、为了效果而使用的修辞片段、拟人化的代码（"the plan holds it"（计划保持它））、比喻动词（"rides along"（一路骑行）、"stands on"（站在上面））、陈词滥调。"A dial worth turning"（值得旋转的旋钮）变成 "a parameter worth varying"（值得变化的参数）。说出你的意思。规则 26 涵盖了隐喻名词。
33. **过度压缩。** 省略冠词、无动词片段、符号语言和使读者解码而不是阅读的缩写。"Parser rejects bad date → exit 2, no write"（解析器拒绝无效日期 → 退出 2，不写入）变成 "The parser rejects a bad date, exits with code 2, and writes nothing."（解析器拒绝无效日期，退出代码 2，什么也不写。）用冠词和动词写出完整的句子，并拼写出箭头和缩写。
