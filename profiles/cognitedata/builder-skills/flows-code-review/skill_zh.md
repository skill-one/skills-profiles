# Flows 代码评审

这项技能是技术评审步骤的**本地执行者**：

```
flows-app-brief  →  构建  →  flows-code-review (此技能，重复直到清理)  →  flows-design-review  →  flows-external-app-submit
```

**检查和评分在 `flows-review-checks` 中进行。** 不要将它们复制到这里。不要凭记忆评分。不要用 `test-coverage` 或其他 **修复** 技能来替代评审条。

此文件仅决定：git/app-brief 预检查、反馈轮文件夹、工作目录是应用根目录、文件写入位置以及提交者摘要块。

## 预检查

- 存在 `package.json`
- 我们位于 git 仓库内 (`git rev-parse --git-dir`)
- 如果仓库根目录缺少 `App-Brief.md`，则警告应先运行 `flows-app-brief`，但继续

反馈轮：查看 `reviews/code-review/`。如果不存在，使用 `feedback-round-1/`。否则使用下一个缺失的轮次编号。

所有评审命令的工作目录：**仓库根目录**（即应用）。

## 第 1 步 — 从 `cognitedata/builder-skills` 拉取最新检查，然后运行它们

每次评审运行都必须从 **`flows-review-checks` 和 `code-quality` 从 [cognitedata/builder-skills](https://github.com/cognitedata/builder-skills)** 中获取。不要从应用的 `skills/` 文件夹中已有的内容进行评分。

**如果此工作区已经是 `builder-skills`** (`git remote` 包含 `cognitedata/builder-skills`)：你位于该仓库 — `读取` 本地 `skills/flows-review-checks/SKILL.md`（它加载本地 `code-quality`）。

**否则**（评审应用）：从本仓库拉取这两个技能，然后读取它们：

```bash
npx @cognite/cli@latest apps skills pull --skill flows-review-checks
npx @cognite/cli@latest apps skills pull --skill code-quality
```

如果 CLI 拉取失败，从 `main` 获取相同的两个文件：

```bash
curl -fsSL https://raw.githubusercontent.com/cognitedata/builder-skills/main/skills/flows-review-checks/SKILL.md
curl -fsSL https://raw.githubusercontent.com/cognitedata/builder-skills/main/skills/code-quality/SKILL.md
```

然后 `Glob '**/skills/flows-review-checks/SKILL.md'` 并 `读取` 第一个匹配项（在成功拉取后，即你刚刚获取的副本）。完全遵循它：搜索（包括 `code-quality` 搜索 — 不要应用其修复）、包、覆盖率、评分、分类、共享验证。

## 第 2 步 — 在此处编写工件

轮次目录：`reviews/code-review/feedback-round-<N>/`

| 共享输出 | 此处文件名 |
| ------------- | ------------- |
| 文件清单 | `review-files.md` |
| 搜索 + 必须的/应该的/理想的 | `review-findings.md` |
| 包审计 | `review-packages.md` |
| 评分报告 | `code-review-report.md` |

`code-review-report.md` 必须包含 `flows-review-checks` 要求的所有内容（执行的检查、覆盖率 **范围**、评分 1.1 和 1.3–1.6、2.1–2.6、3.1、必须的/应该的/理想的带有 `_Impact:_` 在必须修复上），加上：

```markdown
# [应用名称] — Flows 代码评审

此文档是 [应用名称] 的平台评审，作为 Cognite Flows 应用认证过程的一部分进行的。

## 批准路径

此评审发现了 **[N]** 个必须修复项，阻止批准。一旦必须修复项得到解决，重新运行 `flows-code-review`。

### 审查的提交
`<完整 SHA>`
```

以该块结束 `code-review-report.md`（由 `flows-external-app-submit` 需要）：

```markdown
## 摘要

- 必须修复打开： <整数>
- 应该修复打开： <整数>
- 理想修复打开： <整数>
```

使用确切的标签。当所有必须修复项都解决后：`Must Fix open: 0`。

## 第 3 步 — 运行者验证

在 `flows-review-checks` 第 6 步之后：

1. 上述四个文件存在于此轮次的文件夹中。
2. 此运行从 `cognitedata/builder-skills` 拉取了（或在 `builder-skills` 中已经有的）当前的 `flows-review-checks` 和 `code-quality`，然后才进行评分。
3. 打印：

```
Must Fix open: <n>
Should Fix open: <n>
Nice Fix open: <n>
```

## 停止时机

重新运行此技能，直到最新轮次的 `code-review-report.md` 中 `Must Fix open: 0`。只有到那时才能继续 `flows-design-review`。
