---
name: difit-review
description: 一种用于审查特定差异并作为 difit（差异查看器）中的注释显示发现结果的功能。使用它来审查分支差异、提交差异或 GitHub PR，然后在启动 difit 之前，通过 `--comment` 参数预加载发现结果或代码解释。
---

# Difit 评测

## 概述

该技能在易于人类阅读的查看器中启动请求的 git diff。同时，代理可以通过 `--comment` 选项附加任意评论。
这种评论机制非常适合代码审查结果和代码解释。

在此本地仓库副本中，请使用 `pnpm run dev` 而不是已安装的 `difit` 命令。

## 步骤

最终命令通常如下所示：

```bash
pnpm run dev <目标> [与...比较] \
  --comment '{"type":"thread","filePath":"src/foobar.ts","position":{"side":"old","line":102},"body":"第1行\n第2行"}' \
  --comment '{"type":"thread","filePath":"src/example.ts","position":{"side":"new","line":{"start":36,"end":39}},"body":"L36-L39的范围评论"}'
```

详细步骤如下。

1. 确定目标 diff 并查看其内容。

- 检查用户指定的 diff。这可能是一个本地 git 版本、一个 GitHub URL、一个补丁文件或类似的东西。
- 通常理解 diff，必要时检查周围代码，并思考用户请求所需的响应，无论是审查结果、解释还是其他内容。
- 对于 PR 审查，请本地检查 PR，并将审查结果限制为 difit 输出。不要将评论回帖到远程 GitHub。

2. 附加准备好的评论并启动 difit。

- **pnpm run dev 启动选项**
  - 使用 `pnpm run dev <目标> [与...比较]` 指定目标 diff。
  - 在此仓库中不要在 `pnpm run dev` 后插入 `--`。`pnpm run dev -- ...` 会在这里破坏参数解析。
  - 对于未提交的更改使用 `pnpm run dev .`，对于工作树更改使用 `pnpm run dev working`，对于已暂存的更改使用 `pnpm run dev staging`。
  - 对于标准输入，使用类似 `diff -u file1.txt file2.txt | pnpm run dev` 的形式。
- **评论参数**
  - 每条评论使用 `type: "thread"`。
  - 在用户使用的语言中编写评论正文。
  - 对于 diff 目标侧存在的行，使用 `position.side: "new"`。
  - 对于仅在删除侧存在的行，使用 `position.side: "old"`。
  - 对于跨多行的错误，使用范围评论。
  - 不要从 diff 中复制密钥、令牌、密码、API 密钥、私钥或其他凭证类材料到 `--comment` 正文或任何命令行参数中。
- **尚未添加到 git 的文件的附加参数**
  - 对于未提交的更改，如果你决定尚未添加到 git 的文件也应该出现在 diff 中，请添加 `--include-untracked`。

3. 分享 difit URL 并完成响应。
   - 如果没有要附加的评论，请明确说明。
   - 不需要手动验证启动的 difit 页面。
