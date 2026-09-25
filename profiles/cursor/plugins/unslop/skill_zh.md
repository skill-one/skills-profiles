# Unslop

编辑文本以去除 AI 模式。

## 流程

1.  扫描以下模式。
2.  重写。保留含义，匹配预期语气。

## 检测和修复的模式

规则编号是其他技能引用的稳定 ID。删除一条规则会留下空白。

### 内容

3.  **表面性的 -ing 短语。** "highlighting...", "ensuring...", "reflecting...", "showcasing...", "fostering..."。删除或用真实来源扩展。
5.  **模糊的归因。** "Experts believe", "Industry reports suggest", "Some critics argue"。命名来源或删除。

### 语言

7.  **AI 词汇。** 此外，crucial, delve, enduring, enhance, fostering, garner, interplay, intricate, landscape (抽象), pivotal, showcase, tapestry (抽象), testament, underscore, vibrant。用平实词语替换。
8.  **“是”的华丽说法。** "serves as", "stands as", "boasts", "features"。直接说 "is" 或 "has"。
9.  **“不仅仅是 X，而且是 Y。”** 直接陈述观点。
10. **三点规则。** 将观点强行分组。使用自然数字。
11. **同义词循环。** 一段中包含主角、main character、central figure、hero。选择一个，重复它。
12. **虚假范围。** "from X to Y"，其中 X 和 Y 不在有意义尺度上。直接列出主题。

### 风格

13. **连字符滥用。** 完全避免连字符。仅使用句号或逗号（不要括号、连字符、作为连字符的短横线替代品）。如果一个想法需要分隔，结束句子或使用逗号。
14. **冒号滥用。** 冒号在列表或示例之前是 fine。不作为句子中的连接符。"If you're coming from traditional automation: instead of registering event handlers, you describe conditions" 使用冒号什么也没增加。重写，让观点在没有比较框架的情况下自立。"Describing when the scheduler should fire works best as plain English." 同样含义，没有 crutch 标点。
15. **粗体滥用。** 不要粗体每个专有名词或缩写。
16. **行内标题列表。** 关键在于粗体标签和冒号重述该行： "**Performance:** Performance improved..."。将这些转换为散文。一个以句号结尾的粗体引言，命名项目，并随后提供真正的新细节 ("**Schema in TypeScript.** Tables live in one file.") 是 fine，不是关键。
17. **标题大小写。** 使用句子大小写。
18. **装饰性表情符号。** 从标题和项目符号中删除。
19. **弯引号。** 用直引号替换。

### 沟通痕迹

20. **聊天机器人短语。** "I hope this helps!", "Let me know if...", "Of course!", "Certainly!", "Found the smoking gun!" 删除。
22. **奉承语气。** "Great question! You're absolutely right!" 直接回复。

### 填充词

23. **填充短语。** "In order to" 变成 "To"。 "Due to the fact that" 变成 "Because"。 "It is important to note that" 被删除。
24. **过度犹豫。** "could potentially possibly be argued that it might" 变成 "may"。
25. **通用结论。** "The future looks bright." 陈述具体计划或事实。

### 行话

26. **抽象隐喻名词。** Substrate, wedge, vector, locus, vantage, nexus, primitive (作为名词), harness (作为隐喻), surface (如在 "API surface"), bedrock, scaffolding (作为隐喻), modality, paradigm, gold-plating, ratchet (作为隐喻), evacuate (用于移动代码), endgame, north star, flywheel。这些读起来像技术术语，但通常有一个更平实的具体词语。"Substrate" 变成 "base"。 "Wedge in" 变成 "add"。 "Vector" 变成 "way" 或 "method"。 "Gold-plating" 变成 "more than the job needs"。 "Ratchet" 变成机制的真实名称或 "a limit that only tightens"。 "Evacuate" 变成 "move out"。 "Endgame" 变成 "the last phase"。选择具体词语。

### 平实语言

27. **说出它做什么，而不是感觉如何。** "the database stays close at hand", "SQL you can read", "types that follow your schema" 描述感觉。修复命名机制或数字："`.toSQL()` returns the exact string sent to the database", "a column rename fails the build"。询问句子告诉读者做什么或知道什么，然后写下来。如果你不能将其重述为具体的指令、事实或数字，就删除它。一个检查：如果句子可以不变地出现在另一个项目的文档中，它对这个项目什么也没说。删除它。
28. **缩短或拆分密集句子。** 如果读者必须回溯来解析句子，将其分成两部分或删除从句。每个句子一个想法。
29. **主动语态。** 优先使用。捕获 "is/are/was/were + 过去分词" 并命名行动者："queries are validated" 变成 "the compiler validates queries"，"the file is parsed by the loader" 变成 "the loader parses the file"。被动语态只有在行动者未知或确实不重要时才 fine。
30. **删除副词，或使用更强的动词。** "runs quickly" 变成 "is fast" 或数字。"significantly improves" 变成测量的差异。支撑弱动词的副词意味着动词是错误的。
31. **优先使用平实词语。** "utilize" 变成 "use"，"leverage" 变成 "use"，"facilitate" 变成 "help"，"numerous" 变成 "many"，"in the event that" 变成 "if"。更华丽的同义词很少更清晰。
32. **文雅的散文。** 隐喻或花哨的短语，存在字面短语：警句（"wire it or delete it"），为了效果而使用的修辞片段，拟人化的代码（"the plan holds it"），比喻动词（"rides along"，"stands on"），陈词滥调。"A dial worth turning" 变成 "a parameter worth varying"。说出你的意思。规则 26 涵盖了隐喻名词。
33. **过度压缩。** 漏掉冠词，无动词片段，符号语言，以及让读者解码而不是阅读的缩写。"Parser rejects bad date → exit 2, no write" 变成 "The parser rejects a bad date, exits with code 2, and writes nothing." 写完整的句子，包括冠词和动词，并拼写出箭头和缩写。
