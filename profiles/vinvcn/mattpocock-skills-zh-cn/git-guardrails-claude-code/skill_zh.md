# 设置 Git 安全防护

设置一个 PreToolUse 钩子，在 Claude 执行危险的 git 命令前拦截并阻止它们。

## 被拦截的内容

- `git push`（包括 `--force` 在内的所有变体）
- `git reset --hard`
- `git clean -f` / `git clean -fd`
- `git branch -D`
- `git checkout .` / `git restore .`

被阻止时，Claude 会看到一条消息，说明它无权访问这些命令。

## 操作步骤

### 1. 确定作用范围

询问用户：只为**当前项目**安装（`.claude/settings.json`），还是为**所有项目**安装（`~/.claude/settings.json`）？

### 2. 复制钩子脚本

捆绑脚本位于：[scripts/block-dangerous-git.sh](scripts/block-dangerous-git.sh)

根据作用范围复制到目标位置：

- **项目级别**: `.claude/hooks/block-dangerous-git.sh`
- **全局级别**: `~/.claude/hooks/block-dangerous-git.sh`

使用 `chmod +x` 使其可执行。

### 3. 添加钩子到配置

添加到对应的配置文件：

**项目级别** (`.claude/settings.json`):

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

**全局级别** (`~/.claude/settings.json`):

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

如果配置文件已存在，将钩子合并到现有的 `hooks.PreToolUse` 数组中，不要覆盖其他配置。

### 4. 询问是否需要定制

询问用户是否需要在拦截列表中添加或移除模式。相应地编辑复制的脚本。

### 5. 验证

运行快速测试：

```bash
echo '{"tool_input":{"command":"git push origin main"}}' | <path-to-script>
```

应以 code 2 退出，并向 stderr 打印 BLOCKED 消息。
