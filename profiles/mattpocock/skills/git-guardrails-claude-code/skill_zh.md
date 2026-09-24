# 设置 Git 防护措施

配置一个 PreToolUse 钩子，在 Claude 执行命令之前拦截并阻止危险的 Git 命令。

## 将被拦截的内容

- `git push`（包括 `--force` 在内的所有变体）
- `git reset --hard`
- `git clean -f` / `git clean -fd`
- `git branch -D`
- `git checkout .` / `git restore .`

被拦截时，Claude 会看到一条消息，告知它无权执行这些命令。

## 步骤

### 1. 询问范围

询问用户是**仅针对此项目**（`.claude/settings.json`）还是**所有项目**（`~/.claude/settings.json`）？

### 2. 复制钩子脚本

随附的脚本位于：[scripts/block-dangerous-git.sh](scripts/block-dangerous-git.sh)

根据范围复制到目标位置：

- **项目**：` .claude/hooks/block-dangerous-git.sh`
- **全局**：`~/.claude/hooks/block-dangerous-git.sh`

使用 `chmod +x` 赋予执行权限。

### 3. 在设置中添加钩子

添加到合适的配置文件：

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

### 4. 询问定制需求

询问用户是否需要添加或移除拦截列表中的任何模式。根据实际情况相应编辑复制的脚本。

### 5. 验证

运行快速测试：

```bash
echo '{"tool_input":{"command":"git push origin main"}}' | <path-to-script>
```

应退出码为 2，并向标准错误（stderr）输出 BLOCKED 消息。
