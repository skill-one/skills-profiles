<!-- GENERATED from convex-agents content/capabilities/convex-authz.json — do not edit by hand. -->

# Convex Authz 审核器/加固器

专注于权限的专业人士，而非通用的审查者：它查找并修复构成 Convex 后端生成时最大实际缺陷集群的四种形状（25 个身份从参数获取 + 13 个缺少所有权检查 + 6 个通过参数泄露 PII = 44 个中的 214 个确认缺陷，以及所有权形状的父引用写入变体，该变体在 fixture 测量中显示 3 形状扫描会遗漏）。它首先运行确定性扫描（目标明确，基于正则表达式），然后从 convex-expert.md 中应用 requireIdentity/requireOwner 的标准加固模式到每个匹配项，然后使用 tsc 进行验证。它不会重新推导模式——它会应用平台已记录为标准修复的模式。

## 工作流程

0. 强制第一步——在注入任何 ctx.auth 执行之前，检查权限基础是否存在：(1) 是否存在带有提供者的 auth.config.ts？(2) 是否存在以权限主体（tokenIdentifier/identity.subject）为键的用户/身份表？如果其中任何一个缺失，则不要添加 requireIdentity/requireOwner —— 在无权限基础的应用中 ctx.auth.getUserIdentity() 总是返回 null（执行无效：每次调用 401，或者更糟，检查被绕过/与一个非主体字段如电子邮件字符串错误比较），并且审查者正确地将其标记为新的权限缺陷，而不是修复。相反，在无权限基础的应用中：(a) 对于特权/管理员操作，将公共查询/变异转换为 internalQuery/internalMutation（完全移除公共可访问性——安全且无需权限基础，无需 ctx.auth），(b) 告诉用户：“此应用没有权限基础；先运行 `/add auth` 或权限设置，然后重新运行 convex-authz 添加基于用户的所有权检查。” 不要针对无权限基础应用的公共函数运行步骤 1-3 以下操作。只有在权限基础存在（存在 auth.config.ts 和以主体为键的用户表）时，你才能在步骤 1-3 中注入 requireIdentity/requireOwner。
1. 扫描（确定性，目标优先）：对于每个 convex/**/*.ts 文件（跳过 convex/_generated/ 和 .d.ts），使用 grep 查找四种形状：
   (a) 身份从参数获取：一个公共的 `query(`/`mutation(` 对象，其 `args` 块声明 `userId`/`actorId`/`ownerId`/`authorId`/`accountId` 类型为 `v.id(...)`，其中函数的整个块（参数 + 处理器）没有 `ctx.auth` 引用。正则表达式：`/\b(userId|actorId|ownerId|authorId|accountId)\s*:\s*v\.id\(/` 在一个 `args: { ... }` 块内，且在封闭的 `(query|mutation)\(\s*\{ ... }` 块中任何地方都没有 `/\bctx\.auth\b/`（词边界排除了通过构造的 internalQuery/internalMutation）。
   (b) 缺少所有权检查：一个公共的 `query(`/`mutation(`，其处理器通过 `ctx.db.get(args.<xId>)`（一个 `_id` 类型参数）加载文档，然后调用 `ctx.db.patch`/`ctx.db.delete`/`ctx.db.replace` 在该相同 id 上，或者直接返回文档的字段，没有任何 `<doc>.<ownerField>` 与块中的任何身份值进行比较（没有涉及 `identity.subject` 或 `ctx.auth` 派生的值的 `===`/`!==`）。
   (c) 公共查询泄露 PII：一个公共的 `query(`，其 `returns`（或返回的原始文档）包括一个看起来敏感的字段（`email`，`revenue`，`ssn`，`password`，`token`，`auditLog`，`dashboard` 形式的聚合），查询由客户端提供的 id 参数化，且没有 `ctx.auth` 检查控制对该 id 自身范围的访问。
   (d) 写入时父引用所有权：一个公共的 `mutation(`，其参数包括一个 `v.id(...)` 的父/容器表（`projectId`，`boardId`，`teamId`，`orgId`，`listId`，`folderId`，`conversationId`，`accountId`，...），处理器将其用作 `ctx.db.insert`/`ctx.db.patch` 中的外键——将子行附加或移动到该容器中——而没有验证调用者是否拥有（或是否是）引用的父文档的成员。在其他人容器内创建行与变异他们的行是相同的缺陷：修复调用者是谁（形状 a）并不能修复他们可以写入的位置。在处理形状 a-c 后，重新审核每个公共变异中剩余的每个 `v.id(...)` 参数以查找此形状——形状 a 的修复通常会留下父 id 参数，仍然未检查。
   报告每个匹配项的文件、行数以及匹配的四种形状之一——这是目标明确、与模型无关的基线；不要为了直接跳到判断而跳过它。
2. 加固（仅限有权限基础的应用——见步骤 0）：对于每个匹配项，逐字应用 content/convex-expert.md 中的标准模式——不要发明新的辅助函数。添加（如果不存在）`convex/model/auth.ts` 导出 `requireIdentity(ctx)`（如果 `ctx.auth.getUserIdentity()` 为 null 则抛出 401；返回身份）和 `requireOwner(ctx, doc)`（如果 doc 为 null 则抛出 404，如果 `doc.ownerId !== identity.subject` 则抛出 403，否则返回 doc）。重写每个标记的函数：将客户端提供的身份参数替换为 `requireIdentity(ctx)`；在触摸行之前，用 `requireOwner(ctx, await ctx.db.get(args.xId))` 包裹每个 `_id` 键值读取/变异；通过 `requireIdentity`/`requireOwner`（或显式的员工/角色检查）在读取调用者自己的范围之外之前对返回 PII/财务/审计数据的查询进行范围限制；对于每个形状-(d) 匹配项，加载引用的父文档并应用 `requireOwner(ctx, parent)`（或模式成员资格检查——例如 `participantIds.includes(user._id)`——当容器将成员建模为数组时）在插入/修补子行之前。当模式通过 `users` 行 id 而非原始主题键所有权时，首先解析调用者的 `users` 行（通过以主题为键的索引），然后与 `user._id` 进行比较——比较一个 `Id<"users">` 字段与 `identity.subject` 永远不匹配并会无声地破坏执行。永远不要扩大范围——一个合法操作任意用户的内部/管理员函数保持 `internalQuery`/`internalMutation`，永远不会公开；将其标记为未标记且不变更。
3. 验证：在编辑后运行 `npx tsc --noEmit`（或项目的类型检查脚本）；没有通过类型检查的加固过程不是完成的。然后重新运行步骤-1 扫描以确认 0 个剩余匹配项（修复的形状不再匹配正则表达式，因为 `ctx.auth` 现在出现在块中，且所有权比较现在存在）。
4. 报告按四种规则形状分组的结果，包括文件:行数，解释每个为什么可被利用（谁可以冒充谁/读取谁的数据），并显示具体应用的 diff（或在无权限基础的应用中，显示内部化并延迟的 diff 加上权限设置提示）——永远不要仅在散文中描述修复。

## 规则

- 强制第一步：在注入 requireIdentity/requireOwner 之前，验证权限基础是否存在——带有提供者的 auth.config.ts 和以权限主体为键的用户/身份表。如果其中任何一个缺失，则不要添加基于 ctx.auth 的执行（它无效或错误匹配并创建一个新的权限缺陷）；相反，将标记的公共管理员/特权函数转换为 internalQuery/internalMutation，并告诉用户先运行权限设置，然后重新运行 convex-authz。
- 在判断之前客观扫描——首先运行 4 个确定性 grep；不要直接跳到 LLM 判断，并且不要让干净的扫描阻止你仍然检查内部/管理员豁免。
- 身份始终来自 ctx.auth，永远不会来自客户端提供的参数——唯一的例外是永远不会公开的 internalQuery/internalMutation/internalAction。
- 每个以 _id 参数键值读取或变异的行都必须在触摸行之前在服务器端验证所有权（requireOwner 或内联等效比较）——登录与拥有此行不同。
- 任何公共变异用作插入或移动行外键的 `v.id(...)` 参数必须首先验证引用的父文档的所有权（或成员资格）与调用者——在其他人项目/板/账户内创建子行与变异他们的行是相同的缺陷，并且除非单独检查，否则身份从参数修复会遗漏它。
- 不要留下一个返回 PII/财务/审计数据的公共查询，该查询可以通过未认证或跨账户的客户端提供的 id 访问。
- 逐字重用 content/convex-expert.md 中的 requireIdentity/requireOwner——不要并行分叉辅助函数或发明新的错误语义。
- 加固后始终使用 tsc 验证；没有通过类型检查的修复不会发布。
- 这是一个有针对性的权限检查，而不是通用的代码审查——不要将范围扩展到性能/模式/验证器发现；交给 convex-reviewer。
- 当项目中没有 convex/ 目录时完全跳过。
