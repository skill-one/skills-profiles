# diagnose-ci-failures

通过编程方式诊断 PR 的 CI 失败，并生成修复计划。

## 概述

此技能提供了一种确定性工作流程，用于检查 PR 的 CI 状态、提取失败日志、分析错误，并创建一个计划（不是代码更改）来解决问题。输出始终是一个可以在执行前进行审查的计划文档。

## 工作流程

### 1. 验证当前分支是否存在 PR

获取当前分支并检查是否存在 PR：

```bash
# 获取当前分支
git branch --show-current

# 检查 PR
GH_PAGER=cat gh pr view <branch-name> --json number,title,url,state
```

如果不存在 PR，则通知用户并建议使用 `create-pr` 技能创建一个。

### 2. 检查 CI 状态

获取所有 CI 检查的状态：

```bash
GH_PAGER=cat gh pr view <branch-name> --json statusCheckRollup
```

解析输出以识别：
- 已完成的检查与进行中的检查
- 成功的检查
- 失败的检查及其名称和详细信息 URL

如果 CI 仍在运行，则通知用户哪些检查已经失败或通过，突出显示仍在运行的检查，并建议等待完成后再进行诊断。

### 3. 提取失败日志

对于每个失败的检查，使用状态检查中的运行 ID 拉取日志：

```bash
GH_PAGER=cat gh run view <run-id> --log-failed
```

重点关注提取：
- 错误消息及其位置（文件路径、行号）
- 编译错误（未使用的导入、类型不匹配等）
- Linting/clippy 错误及其具体的 lint 名称
- 测试失败消息和堆栈跟踪
- 构建失败及其根本原因

### 4. 分类错误

按类型分组错误：
- **格式问题**：`cargo fmt` 失败
- **Linting 问题**：`cargo clippy` 警告/错误
- **编译错误**：类型错误、缺失导入、签名不匹配
- **测试失败**：失败的测试及其名称和失败原因
- **平台特定问题**：WASM、Linux、macOS、Windows 特定的失败

### 5. 生成修复计划

使用 `create_plan` 工具创建计划文档，包含：
- **问题描述**：失败检查的摘要
- **当前状态**：发现哪些错误及其位置
- **建议更改**：每个错误类别所需的特定修复
- **验证步骤**：用于验证修复的命令（fmt、clippy、测试、presubmit）

计划应参考 `fix-errors` 技能以获取解决特定错误类型的详细指导。

## 重要提示

- **GitHub CLI 分页**：在每次 `gh` 调用时设置 `GH_PAGER=cat`。GitHub CLI 不支持作为全局选项的 `--no-pager`；`GH_PAGER` 和 `PAGER` 是其文档中记录的分页控制
- **始终先创建计划**：不要直接进行代码更改。生成计划供用户审查
- **在 CI 中检查测试状态**：即使本地测试失败，也要在标记为问题之前验证 CI 中是否通过
- **无关的测试失败**：如果 CI 中通过但本地失败，它们可能是环境特定或间歇性的
- **多种错误类型**：一次修复一个类别（例如，在测试之前修复所有 clippy 错误）
- **交叉引用 fix-errors 技能**：对于详细的错误解决策略，使用 `fix-errors` 技能

## 常见 CI 检查名称

- `Formatting + Clippy (MacOS)`
- `Formatting + Clippy (Linux)`
- `Run MacOS tests`
- `Run Linux tests`
- `Run Windows tests`
- `Check CI results`（汇总检查）
- `WASM build`

## 示例命令

**获取带详细信息的 PR 状态：**
```bash
GH_PAGER=cat gh pr view --json number,title,state,statusCheckRollup
```

**获取特定失败运行的日志：**
```bash
GH_PAGER=cat gh run view 12345678 --log-failed
```

**在日志中检查特定错误：**
```bash
GH_PAGER=cat gh run view 12345678 --log-failed 2>&1 | grep -A 5 "error:"
```
