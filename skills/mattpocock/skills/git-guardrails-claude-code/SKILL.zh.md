---
name: git-guardrails-claude-code
description: 设置 Claude Code 钩子以阻止危险 git 命令（如 push、reset --hard、clean、branch -D 等）在执行前。当用户希望防止破坏性 git 操作、添加 git 安全钩子或阻止在 Claude Code 中的 git push/reset 时使用。
---

# 设置 Git 安全防护

设置一个 PreToolUse 钩子，在 Claude 执行它们之前拦截并阻止危险的 git 命令。

## 被阻止的内容

- `git push`（包括 `--force` 的所有变体）
- `git reset --hard`
- `git clean -f` / `git clean -fd`
- `git branch -D`
- `git checkout .` / `git restore .`

当被阻止时，Claude 会看到一个消息，告知它没有权限访问这些命令。

## 步骤

### 1. 确定范围

询问用户：为**当前项目**单独安装（`.claude/settings.json`）还是为**所有项目**安装（`~/.claude/settings.json`）？

### 2. 复制钩子脚本

捆绑的脚本位于：[scripts/block-dangerous-git.sh](scripts/block-dangerous-git.sh)

根据范围将脚本复制到目标位置：

- **项目**：`.claude/hooks/block-dangerous-git.sh`
- **全局**：`~/.claude/hooks/block-dangerous-git.sh`

使用 `chmod +x` 使其可执行。

### 3. 添加钩子到设置

将其添加到相应的设置文件：

**项目**（`.claude/settings.json`）：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/block-dangerous-git.sh"
          }
        ]
      }
    ]
  }
}
```

**全局**（`~/.claude/settings.json`）：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/block-dangerous-git.sh"
          }
        ]
      }
    ]
  }
}
```

如果设置文件已存在，请将钩子合并到现有的 `hooks.PreToolUse` 数组中。不要覆盖其他设置。

### 4. 询问是否需要自定义

询问用户是否希望从阻止列表中添加或删除任何模式。相应地编辑复制的脚本。

### 5. 验证

运行快速测试：

```bash
echo '{"tool_input":{"command":"git push origin main"}}' | <path-to-script>
```

应退出并带有代码 2，并将阻止消息打印到 stderr。
