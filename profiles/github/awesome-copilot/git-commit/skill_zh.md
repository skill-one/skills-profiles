# 使用 Conventional Commits 进行 Git 提交

## 概述

使用 Conventional Commits 规范创建标准化、语义化的 Git 提交。分析实际差异，以确定适当的类型、范围和消息。

## Conventional Commit 格式

```
<type>`[optional scope]`: <description>`

[optional body]

[optional footer(s)]
```

## 提交类型

| 类型       | 用途                        |
| ---------- | ------------------------------ |
| `feat`     | 新功能                        |
| `fix`      | bug 修复                      |
| `docs`     | 仅文档                        |
| `style`    | 格式/样式（无逻辑）            |
| `refactor` | 代码重构（无功能/修复）        |
| `perf`     | 性能提升                      |
| `test`     | 新增/更新测试                  |
| `build`    | 构建系统/依赖项                |
| `ci`       | CI/配置变更                    |
| `chore`    | 维护/杂项                      |
| `revert`   | 回滚提交                      |

## 破坏性变更

```
# Exclamation mark after type/scope
feat!: remove deprecated endpoint

# BREAKING CHANGE footer
feat: allow config to extend other configs

BREAKING CHANGE: `extends` key behavior changed
```

## 工作流程

### 1. 分析差异

```bash
# If files are staged, use staged diff
git diff --staged

# If nothing staged, use working tree diff
git diff

# Also check status
git status --porcelain
```

### 2. 暂存文件（如需要）

如果未暂存文件或您希望以不同方式分组变更：

```bash
# Stage specific files
git add path/to/file1 path/to/file2

# Stage by pattern
git add *.test.*
git add src/components/*

# Interactive staging
git add -p
```

**切勿提交机密信息**（.env、credentials.json、私钥）。

### 3. 生成提交信息

分析差异以确定：

- **类型**：此类变更是什么类型？
- **范围**：受影响的领域/模块是什么？
- **描述**：变更的一行摘要（使用现在时、祈使语气，少于 <72 chars）

### 4. 执行提交

```bash
# Single line
git commit -m "<type>`[scope]`: <description>`"

# Multi-line with body/footer
git commit -m "$(cat <<'EOF'
<type>`[scope]`: <description>`

<optional body>`

<optional footer>`
EOF
)"
```

## 最佳实践

- 每个提交仅包含一个逻辑变更
- 使用现在时：“add”，而非“added”
- 使用祈使语气：“fix bug”，而非“fixes bug”
- 引用 Issue：`Closes #123`，`Refs #456`
- 保持描述在 72 个字符以内

## Git 安全协议

- 切勿更新 git 配置
- 未经明确请求，切勿运行破坏性命令（--force, hard reset）
- 未经用户请求，切勿跳过钩子（--no-verify）
- 切勿强制推送至 main/master
- 若因钩子导致提交失败，请修复并创建新提交（切勿使用 amend）
