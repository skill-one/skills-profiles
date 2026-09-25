# 无需验证钩子

PreToolUse 钩子配置，用于拦截并在执行前阻止绕过标志的使用，确保 AI 代理无法跳过预提交钩子、GPG 签名或其他 git 安全机制。

## 概述

AI 编码代理（如 Claude Code、Codex 等）可以使用 `--no-verify` 等标志运行 shell 命令，从而绕过预提交钩子。这会破坏预提交钩子中配置的代码检查、格式化、测试和安全检查的目的。无需验证钩子添加了一个 PreToolUse 保护的守卫，在执行前拒绝包含绕过标志的任何工具调用。

## 问题

当 AI 代理提交代码时，它们可能会使用绕过标志来避免钩子失败：

```bash
# 这些命令完全跳过预提交钩子
git commit --no-verify -m "快速修复"
git push --no-verify
git commit --no-gpg-sign -m "未签名的提交"
git merge --no-verify feature-branch
```

这允许：

- 未格式化的代码进入仓库
- 代码检查绕过检查
- 安全扫描被跳过
- 未签名的提交绕过签名策略
- 测试套件被规避

## 解决方案

在 `.claude/settings.json` 中添加一个 `PreToolUse` 钩子，用于检查每个 Bash 工具调用并阻止包含绕过标志的命令。

### 配置

将以下内容添加到您项目的 `.claude/settings.json` 中：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hook": {
          "type": "command",
          "command": "if printf '%s' \"$TOOL_INPUT\" | grep -qE '(^|&&|;|\\|)\\s*git\\s+.*--(no-verify|no-gpg-sign)'; then echo 'BLOCKED: --no-verify and --no-gpg-sign flags are not allowed. Run the commit without bypass flags so that pre-commit hooks execute properly.' >&2; exit 2; fi"
        }
      }
    ]
  }
}
```

### 工作原理

1. **匹配器**：钩子仅针对 `Bash` 工具调用，因此不会干扰其他工具（Read、Edit、Grep 等）。
2. **检查**：`$TOOL_INPUT` 环境变量包含代理即将执行的完整命令。钩子使用 `printf` 安全地传递输入（避免 `echo` 在特殊字符上的陷阱），仅在 `git` 命令前检查 `--no-verify` 或 `--no-gpg-sign` 标志。
3. **阻止**：如果 git 命令中找到绕过标志，钩子将退出并打印错误消息。退出码 2 信号 Claude Code 拒绝整个工具调用。
4. **传递**：如果未找到绕过标志，钩子将退出并正常执行命令。

### 退出码

| 码 | 含义 |
|------|---------|
| 0 | 允许工具调用继续 |
| 1 | 错误（工具调用仍继续，显示警告） |
| 2 | 完全阻止工具调用 |

## 被阻止的标志

| 标志 | 目的 | 为什么被阻止 |
|------|---------|-------------|
| `--no-verify` | 跳过预提交和 commit-msg 钩子 | 绕过代码检查、格式化、测试、安全检查 |
| `--no-gpg-sign` | 跳过 GPG 提交签名 | 绕过提交签名策略 |

## 安装

### 项目级设置

在项目根目录中创建或更新 `.claude/settings.json`：

```bash
mkdir -p .claude
cat > .claude/settings.json << 'EOF'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hook": {
          "type": "command",
          "command": "if printf '%s' \"$TOOL_INPUT\" | grep -qE '(^|&&|;|\\|)\\s*git\\s+.*--(no-verify|no-gpg-sign)'; then echo 'BLOCKED: --no-verify and --no-gpg-sign flags are not allowed. Run the commit without bypass flags so that pre-commit hooks execute properly.' >&2; exit 2; fi"
        }
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
        "hook": {
          "type": "command",
          "command": "if printf '%s' \"$TOOL_INPUT\" | grep -qE '(^|&&|;|\\|)\\s*git\\s+.*--(no-verify|no-gpg-sign)'; then echo 'BLOCKED: --no-verify and --no-gpg-sign flags are not allowed. Run the commit without bypass flags so that pre-commit hooks execute properly.' >&2; exit 2; fi"
        }
      }
    ]
  }
}
EOF
```

## 验证

测试钩子是否阻止绕过标志：

```bash
# 这应该被钩子阻止：
git commit --no-verify -m "test"

# 这应该正常成功：
git commit -m "test"
```

## 扩展钩子

### 添加更多被阻止的标志

要阻止其他标志（例如 `--force`），请扩展 grep 模式：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hook": {
          "type": "command",
          "command": "if printf '%s' \"$TOOL_INPUT\" | grep -qE '(^|&&|;|\\|)\\s*git\\s+.*--(no-verify|no-gpg-sign|force-with-lease|force)'; then echo 'BLOCKED: Bypass flags are not allowed.' >&2; exit 2; fi"
        }
      }
    ]
  }
}
```

### 与其他钩子结合

无需验证钩子可以与其他 PreToolUse 钩子协同工作：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hook": {
          "type": "command",
          "command": "if printf '%s' \"$TOOL_INPUT\" | grep -qE '(^|&&|;|\\|)\\s*git\\s+.*--(no-verify|no-gpg-sign)'; then echo 'BLOCKED: Bypass flags not allowed.' >&2; exit 2; fi"
        }
      },
      {
        "matcher": "Bash",
        "hook": {
          "type": "command",
          "command": "if printf '%s' \"$TOOL_INPUT\" | grep -qE 'rm\\s+-rf\\s+/'; then echo 'BLOCKED: Dangerous rm command.' >&2; exit 2; fi"
        }
      }
    ]
  }
}
```

## 最佳实践

1. **提交设置文件** -- 将 `.claude/settings.json` 添加到版本控制，以便所有团队成员都能从钩子中受益。
2. **入职文档中说明** -- 在您项目的贡献指南中提及钩子，以便开发人员了解为什么绕过标志被阻止。
3. **与预提交钩子配合** -- 无需验证钩子确保预提交钩子运行；确保您已配置有意义的预提交钩子。
4. **设置后测试** -- 通过在测试提交中故意触发钩子来验证其工作情况。
