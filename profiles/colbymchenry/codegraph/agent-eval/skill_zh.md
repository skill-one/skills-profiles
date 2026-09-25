# CodeGraph 质量审计

衡量 CodeGraph 相对于纯 grep/read 如何帮助代理，针对选定的 CodeGraph 版本和选定的真实世界代码库。通过 `scripts/agent-eval/` 中的 harness 来驱动。

## 前置条件
- `tmux` 3+，登录的 `claude` CLI，`node`，`git`（macOS/Linux）。
- 从代码库根目录运行。

## 工作流程

复制这个清单：
```
- [ ] 1. 选择版本（本地或 npm）
- [ ] 2. 选择语言
- [ ] 3. 按大小选择代码库
- [ ] 4. 选择 harness（无头 / tmux / 都选）
- [ ] 5. 在后台运行 audit.sh
- [ ] 6. 报告结果
```

**步骤 1 — 版本。** 使用 `AskUserQuestion` 询问要测试哪个 CodeGraph 版本。提供 "本地开发构建" 和 "最新发布"；自由文本 "其他" 允许用户输入特定版本（例如 `0.7.10`）。将答案映射到 VERSION 令牌：
- "本地开发构建" → `local`
- "最新发布" → `latest`
- 输入的版本 → 该字符串（例如 `0.7.10`）

**步骤 2 — 语言。** 读取 `.claude/skills/agent-eval/corpus.json`。使用 `AskUserQuestion` 询问要测试哪种语言，并列出具有条目的语言。

**步骤 3 — 代码库。** 从选定语言的条目中，询问哪个代码库。用其大小和文件数量标记每个选项，例如 `excalidraw — 中等 (~600 个文件)`。每个条目包含 `repo` URL 和一个代表性 `question`。

**步骤 4 — harness。** 使用 `AskUserQuestion` 询问要运行哪个 harness，并将答案映射到 MODE 令牌：
- "无头" → `headless` — `claude -p` 配合 stream-json：精确的 token/成本和干净的工具序列（2 次运行，快速，无 TTY）。
- "交互式 (tmux)" → `tmux` — 在 tmux 中驱动真实的 Claude TUI：忠实的 Explore-subagent 行为，会话日志中的指标（2 次运行，较慢）。
- "都选" → `all` — 无头 + 交互式（4 次运行）。

**步骤 5 — 运行。** 在后台启动（设置版本，如果缺失则克隆，清除并重新索引，运行选定的分支——需要几分钟）：
```bash
scripts/agent-eval/audit.sh <VERSION> <repo-name> <repo-url> "<question>" <MODE>
```

**步骤 6 — 报告。** 当作业完成时，读取日志并按分支报告：
- 无头 (`parse-run.mjs`)：总工具调用次数、文件 `Read`、Grep/Bash、codegraph-tool 调用、持续时间、**总成本**。
- 交互式 (`parse-session.mjs`)：`VERDICT: codegraph_explore 使用 Nx | Read N | Grep/Bash N` 和 `TOKENS:` 行。
- 两个路径还会打印三个反馈指标——残差上下文占用率、探索充分性、分配效率——无头 A/B 结尾会显示一个并排的 `ARM COMPARISON` 表。报告该表，并首先检查其污染行：`CLI 调用返回输出` > 0 表示该分支通过 Bash 达到 codegraph，其数字无效。如何阅读其余部分：
`docs/benchmarks/agent-eval-feedback-metrics.md`。

首先报告成本 + 工具/Read 计数——它们是可靠的信号；原始 token 输入/输出会被子代理委托和提示缓存混淆。说明 codegraph 是否减少了工作量，以及两个分支是否得到了正确答案。

## 备注
- 每次运行都会重建索引（`audit.sh` 会清除 `.codegraph`）——不同版本提取不同，因此索引必须由构建它的同一二进制文件提供。
- `audit.sh` 会暂时修改全局 `codegraph` 安装以进行测试，然后通过 `local-install.sh` 恢复你的开发链接。
- 语料库代码库克隆到 `/tmp/codegraph-corpus`（如果已存在则重用）。
- 在 `corpus.json` 中添加或编辑代码库（字段：`name`，`repo`，`size`，`files`，`question`）。
