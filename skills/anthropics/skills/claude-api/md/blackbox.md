# claude-api (`anthropics/skills/claude-api`)

## blackbox

**function**: 帮你在自己的程序里接入 Anthropic 的 Claude（一个 AI 大脑）：你说要什么功能，我给你能直接运行的代码；已有代码我还能帮你升级到新模型、审查过时写法、找出省钱空间。

- input: 一句需求，如「用 Python 写个小工具，把客服留言自动分类成投诉/咨询」, output: 一个可直接运行的代码文件，接好 Claude，跑起来就能输出分类结果
- input: 一段调用旧版 Claude 模型的现有代码 + 一句「migrate」（迁移到新模型）, output: 改好后的代码：已换用新模型、修掉不再兼容的写法，附改动说明
- input: 一段现有的提示词（指挥 AI 的文字）+ 一句「prompt-audit」（体检）, output: 一份审查报告：逐条指出哪些写法是给老模型用的、为什么现在不适用、建议改成什么样，附现成的修改稿
- input: 一句「每月 Claude 账单太高，帮我省点」, output: 一份按省钱效果排序的清单：每条写明能省多少、怎么改，改动前先跟你确认
