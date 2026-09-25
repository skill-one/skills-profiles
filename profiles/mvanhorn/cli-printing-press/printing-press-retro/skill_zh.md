# /printing-press-retro

**结果：** 一个清理过的复古文档，并且在问题门禁通过后，仅针对 Printing Press 缺陷的 GitHub 问题。

**下一个消费者：** 一个维护者或代理人，将更改 Printing Press（生成器、评分器、技能或二进制文件）——而不是刚刚发布的打印 CLI。

**完成：** 手稿校样存在且已清理；每个工作单元都是新建文件、评论现有文件或仅本地操作；没有未删除的机密或个人身份信息（PII）残留；用户已获得结果列表。

**意图：** "提高底线"是分析语言，不是申报栏。仅当 Printing Press 必须更改以停止当前可复现的、泛化的 P1 或 P2 缺陷时才申报。对单个 CLI 进行手动迭代是预期工作，而不是发现。在面向用户输出时说 "Printing Press"；在指向修复时命名子系统。

## 边界

- **在引用前清理**所有真实机密和 PII。问题正文和复古文档是公开的。使用 [references/secret-scrubbing.md](references/secret-scrubbing.md) 层级 0。永远不要将泄露的值作为泄露的证据进行引用。
- **默认情况下不要更改机器**。举证责任在于发现者。
- **没有 P3。** 仅申报 P1/P2。任何其他内容都是跳过或丢弃，而不是低优先级问题。问题门禁仅申报 P1/P2 工作单元。
- **永远不要上传未清理的工件。** 永远不要修改手稿或库源树；仅清理副本。

## 权限

调用授权阅读手稿/库并编写复古证明及草稿副本。它不授权 GitHub 申报或公开上传，直到用户确认提交。它不授权编辑已打印的 CLI 或 Printing Press 源代码。

## 步骤

首先阅读 [references/run-resolution.md](references/run-resolution.md)。它解析 `$API_NAME`、`$RUN_ID`、`$RUN_DIR`、`$CLI_DIR` 和 `$IN_REPO`。

**永远不要从内存中执行一个阶段。当你进入一个阶段时，首先从 phases/ 中读取其文件。**

| 步骤 | 文件 |
|---:|---|
| 1 | [phases/01-gather-evidence.md](phases/01-gather-evidence.md) |
| 2 | [phases/02-mine-the-session.md](phases/02-mine-the-session.md) |
| 3 | [phases/03-triage-candidates.md](phases/03-triage-candidates.md) |
| 4 | [phases/04-classify-findings.md](phases/04-classify-findings.md) |
| 5 | [phases/05-prioritize.md](phases/05-prioritize.md) |
| 6 | [phases/06-write-the-retro.md](phases/06-write-the-retro.md) |
| 7 | [phases/07-plannable-work-units.md](phases/07-plannable-work-units.md) |
| 8 | [phases/08-issue-gate.md](phases/08-issue-gate.md) |
| 9 | [phases/09-package-upload-present.md](phases/09-package-upload-present.md) |

遵循每个文件的最终 `Next:` 指针。后期程序存在于阶段文件或它加载的角色命名的参考中（[references/artifact-packaging.md](references/artifact-packaging.md)、[references/issue-template.md](references/issue-template.md)、[references/secret-scrubbing.md](references/secret-scrubbing.md)）。不要在这里重述这些文件。
