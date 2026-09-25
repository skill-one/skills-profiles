# Proof - 协作式 Markdown 编辑器

Proof 是一个面向人类和智能体的协作式文档编辑器。通过托管在 `https://www.proofeditor.ai` 的 Web API 可访问，通过 HTTP 从 Bash 获得。

**结果：** 用户获得一个可工作的 Proof 链接（tokenized link），或者文档包含用户请求的读取、评论、建议或编辑操作。

**完成：** 操作在其自身级别上得到确认，用户获得结果和简短摘要。创建操作通过返回的 `tokenUrl` 确认。变更操作通过 `ok: true` 确认；在 `202` 或 `partial: true` 响应中，通过重新读取 `v3/document` 确认。拉取操作通过写入的本地文件确认，读取操作通过返回的内容确认。

**在首次进行 Proof 读取或变更（HTTP 或 MCP）之前，请先阅读 `references/api.md`。** 它定义了端点：`share/markdown`、v3 文档和编辑端点、存在状态、标题以及 `DELETE /api/documents/<slug>`。它还包含操作表、错误和重试类，以及 Claude Code 的 `curl` 权限提示。

**在审查共享文档、创建和共享文档、以及将文档拉取到本地文件之前，请先阅读 `references/workflows.md`。** 这些流程中有精确的配方。

如果 harness 中已经提供 `proof_*` MCP 工具（`proof_share_markdown`、`proof_v3_document`、`proof_v3_edit`、`proof_presence`、`proof_document_title`、`proof_document_delete`、`proof_report_bug`），请优先使用它们。否则使用 HTTP 配方。在 MCP 模式下，服务器注入 `by`、`X-Agent-Id` 和存在状态身份。将 Proof URL 中的 `?token=` 值作为 `shareToken` 传递，用于对未拥有用户的所有文档进行编辑和存在状态更新。

在 MCP 模式下，删除权限保持不变。未认领的文档仍需要其 `ownerSecret`，已认领的文档需要其所有者的会话。传递作为 `shareToken` 的编辑 `accessToken` 不能删除。

## 身份

每次写入操作都会使用这两个字段进行归属，并且它们不会变化。机器 ID 是 `ai:compound-engineering`，在每次操作中作为 `by` 发送，并作为 `X-Agent-Id` 标头发送。显示名称是 `Compound Engineering`，在 `POST /presence` 中作为 `name` 发送，每个文档会话只设置一次，因此 Proof 将其绑定到该智能体 ID。调用者可以在不同的子智能体应拥有文档时传递不同的 `identity` 对。切勿临时创建类似 `ai:compound` 的变体。

## 凭证和边界

- `accessToken` 是日常读取、编辑、存在状态和事件的凭证。`ownerSecret` 仅携带所有者权限——删除和其他所有者级操作——并且永远不会作为日常凭证。在创建时捕获两者，并将 `ownerSecret` 与 `accessToken` 分开持久化（在 shell 变量或等效方式中）；在文档未被认领时，所有者删除操作需要它。两者都不应出现在仓库跟踪文件、提交或持久日志中，`ownerSecret` 永远不会出现在面向用户的副本中。
- 将 tokenized 链接（`tokenUrl`）交给人类，而不是裸的 `/d/<slug>` —— 该链接中的 token 也允许已登录用户认领无所有者的文档。
- 公开创建的文档在已登录的 Every 用户在浏览器中认领之前是无所有者的。认领会永久撤销 `ownerSecret`，而 `accessToken` 仍然有效，因此删除需要所有者的 Every 会话——询问所有者，或使用他们的会话 token。两个响应表示密钥已被撤销：一个带有 `code: "DOCUMENT_DELETE_FORBIDDEN"` 和 `reason: "CREDENTIAL_NOT_OWNER"` 的 `403`，或当提供创建 `ownerSecret` 时的 `401`。停止使用密钥，而不是重试。`reason: "DOCUMENT_HAS_NO_OWNER"` 是相反的情况：文档仍未被认领，因此只有原始 `ownerSecret` 可以删除它，而 Every 会话不能。
- 除非用户明确批准，否则切勿将密钥、凭证、API 密钥、私有 token 或敏感个人数据放入 Proof 文档中，并且切勿在未明确替换的情况下将仓库跟踪项目文档替换为 Proof 链接。
- 清空 Markdown 内容**不会**清除评论标记。引文和评论对任何拥有共享凭证的人都是可读的，因此内容清除不是隐私清理。删除文档才是——在文档未被认领时使用 `ownerSecret`，或在认领后作为所有者使用。
- 不要在发布交接后自动删除。需要审查的文档必须保留。在用户请求时删除，或在完成显式短暂的草稿文档后删除。

## 发布模式

主要用途是单向发布。完整读取现有的本地 Markdown 文件，将其内容作为新文档的正文发布，并将可共享的 URL 交给用户。本地文件保持规范——发布不会将任何内容同步回磁盘。

有两个入口点共享这些机制。一个是用户请求命名本地 Markdown 文件（“分享到 Proof”、“为这个文档获取 Proof 链接”）；如果存在歧义，才询问哪个文件，并期望没有上游调用者。另一个是从 `ce-brainstorm`、`ce-ideate` 或 `ce-plan` 的交接，传递文件路径和标题。

仅发布 Markdown。如果源是 HTML 统一计划，则返回本地浏览器/打开路径，而不是上传它。发布统一计划时，根据其准备状态标记标题，例如 `Plan: <title> (仅要求)` 或 `Plan: <title> (实现就绪)`。

发布源文件的字节，而不是手写或占位符内容。`references/workflows.md` 提供了 `jq --rawfile` 配方，可以正确转义换行符、引号和反引号。发布交接后，向用户显示 URL 并返回控制权。

## 编辑

`GET /api/agent/<slug>/v3/document` 和 `POST /api/agent/<slug>/v3/edit` 是智能体唯一读取和写入的端点。评论、回复、解决、建议和内容更改都是 v3 编辑正文中的 `operations`，因此你未在 `references/api.md` 中读取的路径是你自己编造的。

编辑前，将 `v3/document` 作为真实来源读取。然后选择最能表达更改的最窄操作：针对文本的 `replace`、`insert` 或 `delete`；当更改应作为跟踪更改可见时使用 `suggest`；仅在用户要求整个文档替换或更改无法狭义表达时使用 `set_document`。目标是 Markdown 中的可见文本，而不是原始 Markdown 语法或块引用。

从该读取中获得的 `comments[]` 和 `suggestions[]` 是审查状态。通过 ID 回复、解决、取消解决、接受或拒绝。v3 没有删除评论操作。一个标记为 `orphaned: true` 的评论仍然可读和可回复，但其旧引文不再是活动锚点。

在重试任何操作之前需要停止并检查的错误：

- `TARGET_AMBIGUOUS` — 锚点匹配多次且未更改。使用 `error.candidates` 中的 `occurrence` / `before` / `after` 消歧义；切勿假设第一个匹配是沉默的，并且切勿盲目重试评论。
- `retryable: false` — 修复请求。`retryable: true` 且 `error.current` — 重新针对 `current` 解决目标，然后重试一次。
- `202` / `PENDING`，或 `ok: false` 且 `partial: true` — 写入可能已提交。在串联或报告成功之前重新读取 `v3/document`，并仅重试失败的操作（重复的 `Idempotency-Key` 安全重放）。
- 在新鲜读取和安全重试后仍然失败——根据 `references/api.md` 报告错误，而不是循环。

将文档拉取到本地文件会覆盖该文件。当拉取是其他操作的非用户请求副作用时，首先确认路径。
