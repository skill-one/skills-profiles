---
name: block-no-verify-hook
description: 配置一个 PreToolUse 钩子，以防止 AI 代理使用 --no-verify 和其他绕过标志跳过 git 预提交钩子。在设置强制执行提交质量门禁的 Claude Code 项目时使用。
---

# 无验证拦截钩子

PreToolUse 钩子配置，在执行前拦截并阻止绕过标志的使用，确保 AI 代理无法跳过预提交钩子、GPG 签名或其他 git 安全机制。

## 概述

AI 编码代理（Claude Code、Codex 等）可以使用 `--no-verify` 等标志运行 shell 命令，从而绕过预提交钩子。这会破坏预提交钩子中配置的代码检查、格式化、测试和安全检查的目的。无验证拦截钩子添加了一个 PreToolUse 保护的钩子，在执行前拒绝包含绕过标志的任何工具调用。

## 问题

当 AI 代理提交代码时，它们可能会使用绕过标志来避免钩子失败：

```bash
# 这些命令完全跳过预提交钩子
git commit --no-verify -m "快速修复"
git push --no-verify
git commit --no-gpg-sign -m "未签名提交"
git merge --no-verify feature-branch
```

这允许：

- 未格式化的代码进入仓库
- 代码检查绕过检查
- 安全扫描被跳过
- 未签名的提交绕过签名策略
- 测试套件被规避

## 解决方案

在 `.claude/settings.json` 中添加一个 `PreToolUse` 钩子，检查每个 Bash 工具调用，并阻止包含绕过标志的命令。

### 配置

将以下内容添加到您项目的 `.claude/settings.json` 中：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if grep -qE '\"command\"[[:space:]]*:[[:space:]]*\"([^\"\\\\]|\\\\.)*(--no-(ver|g)|commit([^\"\\\\]|\\\\.)*([[:space:]]|\\\\[tn])-[a-zA-Z]*n)'; then echo 'BLOCKED: --no-verify and --no-gpg-sign flags are not allowed. Run the commit without bypass flags so that pre-commit hooks execute properly.' >&2; exit 2; fi"
          }
        ]
      }
    ]
  }
}
```

### 工作原理

1. **匹配器**：钩子仅针对 `Bash` 工具调用，因此不会干扰其他工具（Read、Edit、Grep 等）。
2. **检查**：Claude Code 将工具调用作为 JSON 发送到钩子，并通过 stdin 设置，不设置 `$TOOL_INPUT` 变量。钩子使用 `grep -E` 搜索该 JSON 中的 `command` 值，因此不需要 `jq` 或 `node`，并且其他字段（如 `cwd` 或工具调用的描述）无法触发它。它阻止 `--no-verify`、`--no-gpg-sign` 以及 git 接受的它们任何更短的缩写，例如 `--no-veri`。它还阻止在同一个命令中跟随 `commit` 的短选项组 `n`，例如 `-n` 或 `-nm`，因为 `-n` 是 `--no-verify` 的短形式。钩子不查找 `git` 这个词，因此它还会捕获 `if git ...`、`sudo git ...` 和 `g=git; $g commit --no-verify`。一个错误匹配，例如提交信息中提到标志，会阻止调用，这是安全的失败方式。
3. **拦截**：如果在 git 命令中找到绕过标志，钩子将退出并打印错误消息。退出代码 2 信号 Claude Code 拒绝整个工具调用。
4. **传递**：如果未找到绕过标志，钩子将退出并正常执行命令。
5. **限制**：钩子检查文本，因此它会阻止习惯性使用绕过标志的代理。它不会阻止试图规避它的代理，例如通过从碎片中构建标志或运行 `git -c core.hooksPath=/dev/null commit`。

### 退出代码

| 代码 | 含义 |
|------|---------|
| 0 | 允许工具调用继续 |
| 1 | 错误（工具调用仍继续，显示警告） |
| 2 | 完全阻止工具调用 |

## 被拦截的标志

| 标志 | 目的 | 为什么被拦截 |
|------|---------|-------------|
| `--no-verify` | 跳过预提交和 commit-msg 钩子 | 绕过代码检查、格式化、测试、安全检查 |
| `--no-gpg-sign` | 跳过 GPG 提交签名 | 绕过提交签名策略 |

## 安装

### 项目级设置

在项目根目录下创建或更新 `.claude/settings.json`：

```bash
mkdir -p .claude
cat > .claude/settings.json << 'EOF'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if grep -qE '\"command\"[[:space:]]*:[[:space:]]*\"([^\"\\\\]|\\\\.)*(--no-(ver|g)|commit([^\"\\\\]|\\\\.)*([[:space:]]|\\\\[tn])-[a-zA-Z]*n)'; then echo 'BLOCKED: --no-verify and --no-gpg-sign flags are not allowed. Run the commit without bypass flags so that pre-commit hooks execute properly.' >&2; exit 2; fi"
          }
        ]
      }
    ]
  }
}
EOF
```

### 全局设置

要在所有项目中强制执行，请将以下内容添加到 `~/.claude/settings.json`：

```bash
mkdir -p ~/.claude
cat > ~/.claude/settings.json << 'EOF'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if grep -qE '\"command\"[[:space:]]*:[[:space:]]*\"([^\"\\\\]|\\\\.)*(--no-(ver|g)|commit([^\"\\\\]|\\\\.)*([[:space:]]|\\\\[tn])-[a-zA-Z]*n)'; then echo 'BLOCKED: --no-verify and --no-gpg-sign flags are not allowed. Run the commit without bypass flags so that pre-commit hooks execute properly.' >&2; exit 2; fi"
          }
        ]
      }
    ]
  }
}
EOF
```

## 验证

测试钩子是否拦截绕过标志：

```bash
# 这应该被钩子拦截：
git commit --no-verify -m "test"

# 这应该正常成功：
git commit -m "test"
```

## 扩展钩子

### 添加更多被拦截的标志

要拦截额外的标志（例如 `--force`），扩展 `grep` 模式：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if grep -qE '\"command\"[[:space:]]*:[[:space:]]*\"([^\"\\\\]|\\\\.)*(--no-(ver|g)|commit([^\"\\\\]|\\\\.)*([[:space:]]|\\\\[tn])-[a-zA-Z]*n|git([[:space:]]|\\\\t)([^\"\\\\]|\\\\.)*--force)'; then echo 'BLOCKED: Bypass flags are not allowed.' >&2; exit 2; fi"
          }
        ]
      }
    ]
  }
}
```

### 与其他钩子结合

无验证拦截钩子可以与其他 PreToolUse 钩子协同工作：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if grep -qE '\"command\"[[:space:]]*:[[:space:]]*\"([^\"\\\\]|\\\\.)*(--no-(ver|g)|commit([^\"\\\\]|\\\\.)*([[:space:]]|\\\\[tn])-[a-zA-Z]*n)'; then echo 'BLOCKED: Bypass flags not allowed.' >&2; exit 2; fi"
          }
        ]
      },
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "if grep -qE 'rm[[:space:]]+-rf[[:space:]]+/'; then echo 'BLOCKED: Dangerous rm command.' >&2; exit 2; fi"
          }
        ]
      }
    ]
  }
}
```

## 最佳实践

1. **提交设置文件** -- 将 `.claude/settings.json` 添加到版本控制，以便所有团队成员都能从钩子中受益。
2. **入职文档中记录** -- 在您项目的贡献指南中提及钩子，以便开发人员了解为什么绕过标志被阻止。
3. **与预提交钩子配合** -- 无验证拦截钩子确保预提交钩子运行；确保您配置了有意义的预提交钩子。
4. **设置后测试** -- 通过在测试提交中故意触发它来验证钩子是否正常工作。
