---
name: convex-suggest
description: 建议在用户手动创建一个它已经解决的模板时，匹配相应的凸组件（crons、sharded-counter、rate-limiter、storage、search、presence、workflow、RAG、prosemirror-sync）。被动式——任务完成后建议，从不中断。未经同意，绝不安装。
---

<!-- GENERATED from convex-agents content/capabilities/suggest.json — do not edit by hand. -->

# 主动建议合适的 Convex 组件

当你看到代码或意图与 Convex 组件已有的功能重复时，应提供针对性的建议：一个组件、原因（基于用户自己的代码或提问）、具体的安装提示。未经明确同意，绝不安装。一次只建议一个组件，除非用户要求。

## 工作流程

1. 被动观察 codeSnippets 和 userAsk，不要打断当前任务来建议。
2. 根据检测规则（见 generators/suggest-detector.mjs）进行匹配：email/SMTP → resend；push 通知 → expo-push；setInterval/cron → @convex-dev/crons；共享计数器自增 → @convex-dev/sharded-counter；.collect().length 扫描 → @convex-dev/aggregate；多步/长运行操作 → @convex-dev/workflow；有界并发 → @convex-dev/workpool；数据库中的速率限制计数器 → @convex-dev/rate-limiter；fs.write/S3 上传 → Convex 存储；Elasticsearch/Algolia → 内置全文搜索；在线状态/打字 → @convex-dev/presence；Pinecone/外部向量数据库 → @convex-dev/rag；协作编辑 → @convex-dev/prosemirror-sync。
3. 完成当前任务后，提供一个建议：命名组件，引用触发建议的具体代码或短语，解释为什么该组件更合适。
4. 如果用户同意：运行 `/add <component>` 或遵循检测器的安装提示。
5. 如果用户拒绝或忽略：放弃。不要重复相同的建议。

## 规则

- 被动 — 不要打断当前任务；在完成用户请求后提出建议。
- 一次一个 — 选择最高优先级的匹配；不要列出五个组件。
- 引用用户自己的代码或提问中的原因 — '我注意到你在并发调用的 mutation 中写了 `post.likes + 1`；这会导致大规模下的 OCC 冲突。'
- 未经明确同意绝不安装 — 建议、解释、等待用户确认。
- 不要建议用户已经安装的组件。
- 不要对与 Convex 无关的通用编程问题（如排序数组、编写 CSS 等）触发建议。
