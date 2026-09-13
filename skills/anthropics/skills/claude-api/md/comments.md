# claude-api (`anthropics/skills/claude-api`)

## comments

- user: 后端老兵·写了十年 Python, category: 妙用, comment: 凭记忆写了 thinking 带 budget_tokens,新模型直接 400。让它对照文档全查一遍,改成 adaptive 才过,省了线上排障。
- user: 第一次接大模型的前端, category: 坑, comment: 项目里全是 openai 导入,让它顺手改,它停下确认要不要换 Claude。没坏事,但急用时最好一开始就说清换不换供应商。
- user: 独立开发者, category: 妙用, comment: 模型迁完跑 prompt-audit:给老模型写的提示词过时点全被标出,带 file:line 和建议 diff。它默认只报告不改码,要改得明说。
- user: 管 API 账单的技术负责人, category: 注意, comment: 跑 cost-optimize 先备好 usage 日志或 Admin key,有真实数据它排的省钱项才有含金量;且要花钱跑验证前会先找你批。
- user: agent 开发者, category: 启发, comment: 起初把 Tool Runner 当 Claude Code 用:它只循环我自定义的工具,没内置读写文件。要开箱即用得装 claude-agent-sdk,是另一个包。
- user: 云上运维老哥, category: 注意, comment: 我们走 Vertex:联网搜索只有基础版,web fetch 根本没有。让它先查平台支持表再写代码,别照通用示例硬抄。
