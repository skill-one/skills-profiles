---
name: printing-press
description: 为任何 API 设置新的集成、连接器或 CLI 绑定。通过精简的研究 -> 生成 -> 构建 -> shipcheck 循环，从 OpenAPI、HAR 或 Postman 规范中包装或生成可部署的 Go CLI。当用户说构建 CLI、包装此 API、设置新集成、添加连接器、与服务集成或按域名命名 API 时使用。
---

# /printing-press

**结果：** 在 `$PRESS_LIBRARY/<api-slug>/` 目录下生成一个可工作的 Go CLI，并最多存档五个密集型文稿到 `$PRESS_MANUSCRIPTS/<api-slug>/<run-id>/` 目录：研究简报、吸收清单、构建日志、发货检查证明和实时烟雾证明（在实时测试运行时生成）。

**下一个使用者：** 用户，运行 CLI 或将其部署，以及从这里开始的兄弟技能：`printing-press-polish` 用于二次处理，`printing-press-publish` 用于公共库，`printing-press-retro` 用于针对 Press 本身的发现。

**完成：** 在吸收关卡批准的所有功能都已实现，发货检查已达到发货状态，实时 dogfood 矩阵已针对真实目标运行，CLI 已推广，收据账本在最后阶段关闭。

**意图：** 为没有小时级阶段戏剧的 API 提供最佳实用 CLI。优化时间到发货，而不是时间到文档：当已有研究足够好时重用，早期运行廉价高信号检查，在优化前修复阻塞项。

## 边界

- **绝不泄露秘密。** API 密钥值、令牌值、密码和会话 Cookie 绝不能到达源代码、文稿、证明、README、HAR、收据或任何已提交的内容。环境变量名和占位符是安全的。阶段 5.6 和发布适用 [references/secret-protection.md](references/secret-protection.md)。
- **绝不未经测试就发布。** `go build` 和 `verify` 通过率是结构性信号，不是正确性信号。一个未在 [phases/18-dogfood-testing.md](phases/18-dogfood-testing.md) 中通过实时矩阵的 CLI 是不可发布的，一个通过修改 1-3 个文件即可解决的错误现在就修复，而不是提交给 v0.2。
- **绝不引用人类时间估计** 用于子任务（"~15-30 分钟"，"快速修复"）。代理执行工作，不是用户；描述范围而不是时间。例外是真正有时间限制的：整个运行（30-60 分钟）、工具安装和受网络限制的 printing-press 子命令。
- **绝不凭记忆排序。** 收据账本决定下一个阶段是哪个；参见 [references/phase-receipts.md](references/phase-receipts.md)。

## 权限

调用授权在 `$PRESS_RUNSTATE/`、`$PRESS_LIBRARY/` 和 `$PRESS_MANUSCRIPTS/` 下读取和写入，运行 printing-press 二进制文件和 Go 工具链，以及在公开网络上研究 API。它不授权发布到公共库、打开 Pull Request 或在用户机器上的其他地方写入。

## 步骤

在任何用户界面提示之前进入 [phases/01-preflight.md](phases/01-preflight.md)，然后阅读 [references/run-resolution.md](references/run-resolution.md)：它解析 API 目标、简报上下文和组合运行时的源优先级。

**绝不凭记忆执行阶段。当你进入一个阶段时，首先从 phases/ 目录读取其文件。**

| 步骤 | 文件 |
|---:|---|
| 1 | [phases/01-preflight.md](phases/01-preflight.md) |
| 2 | [phases/02-run-initialization.md](phases/02-run-initialization.md) |
| 3 | [phases/03-resolve-and-reuse.md](phases/03-resolve-and-reuse.md) |
| 4 | [phases/04-research-brief.md](phases/04-research-brief.md) |
| 5 | [phases/05-pre-browser-sniff-auth-intelligence.md](phases/05-pre-browser-sniff-auth-intelligence.md) |
| 6 | [phases/06-browser-sniff-gate.md](phases/06-browser-sniff-gate.md) |
| 7 | [phases/07-crowd-sniff-gate.md](phases/07-crowd-sniff-gate.md) |
| 8 | [phases/08-ecosystem-absorb-gate.md](phases/08-ecosystem-absorb-gate.md) |
| 9 | [phases/09-api-reachability-gate.md](phases/09-api-reachability-gate.md) |
| 10 | [phases/10-generate.md](phases/10-generate.md) |
| 11 | [phases/11-build-the-goat.md](phases/11-build-the-goat.md) |
| 12 | [phases/12-shipcheck.md](phases/12-shipcheck.md) |
| 13 | [phases/13-sync-param-drop-gate.md](phases/13-sync-param-drop-gate.md) |
| 14 | [phases/14-agentic-skill-review.md](phases/14-agentic-skill-review.md) |
| 15 | [phases/15-readme-skill-agents-correctness-audit.md](phases/15-readme-skill-agents-correctness-audit.md) |
| 16 | [phases/16-agentic-output-review.md](phases/16-agentic-output-review.md) |
| 17 | [phases/17-local-code-review.md](phases/17-local-code-review.md) |
| 18 | [phases/18-dogfood-testing.md](phases/18-dogfood-testing.md) |
| 19 | [phases/19-polish.md](phases/19-polish.md) |
| 20 | [phases/20-promote-and-archive.md](phases/20-promote-and-archive.md) |
| 21 | [phases/21-next-steps.md](phases/21-next-steps.md) |

遵循每个文件的最终 `Next:` 指针，并记录每个阶段名称的收据交接。后期程序存在于阶段文件或它加载的以角色命名的参考中 ([references/phase-receipts.md](references/phase-receipts.md)、[references/codex-delegation.md](references/codex-delegation.md)、[references/fetch-docs.md](references/fetch-docs.md))。不要在这里重述这些文件。
