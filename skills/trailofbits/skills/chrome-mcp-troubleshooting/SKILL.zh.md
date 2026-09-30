---
name: chrome-mcp-troubleshooting
description: 诊断和修复 Chrome MCP 扩展中 Claude 的连接问题。当 mcp__claude-in-chrome__* 工具失效、返回“浏览器扩展未连接”或行为异常时使用。
---

# 在 Chrome MCP 中的 Claude 故障排除

当 Chrome MCP 工具无法连接或工作不可靠时，使用此技能。

## 使用时机

- `mcp__claude-in-chrome__*` 工具报错 "浏览器扩展未连接"
- 浏览器自动化工作异常或超时
- 更新 Claude Code 或 Claude.app 后
- 在 Claude Code CLI 和 Claude.app (Cowork) 之间切换时
- 本地主机进程正在运行，但 MCP 工具仍然失败

## 不使用时机

- **Linux 或 Windows 用户** - 此技能涵盖 macOS 特定路径和工具 (`~/Library/Application Support/`，`osascript`)
- 与 Claude 扩展无关的一般 Chrome 自动化问题
- Claude.app 桌面问题（与浏览器无关）
- 网络连接问题
- Chrome 扩展安装问题（使用 Chrome Web Store 支持）

## Claude.app 与 Claude Code 的冲突（主要问题）

**背景：** 当 Claude.app 添加了 Cowork 支持时（从桌面应用进行浏览器自动化），它引入了一个竞争性本地消息传递主机，与 Claude Code CLI 冲突。

### 两个本地主机，两种套接字格式

| 组件 | 本地主机二进制文件 | 套接字位置 |
|------|-------------------|-----------------|
| **Claude.app (Cowork)** | `/Applications/Claude.app/Contents/Helpers/chrome-native-host` | `/tmp/claude-mcp-browser-bridge-$USER/<PID>.sock` |
| **Claude Code CLI** | `~/.local/share/claude/versions/<version> --chrome-native-host` | `$TMPDIR/claude-mcp-browser-bridge-$USER` (单个文件) |

### 冲突原因

1. 两者都在 Chrome 中注册本地消息传递配置：
   - `com.anthropic.claude_browser_extension.json` → Claude.app 辅助程序
   - `com.anthropic.claude_code_browser_extension.json` → Claude Code 包装器

2. Chrome 扩展按名称请求本地主机
3. 如果活动配置错误，则运行错误的主机
4. 错误的主机创建 MCP 客户端未预期的格式/位置的套接字
5. 结果："浏览器扩展未连接"，尽管一切似乎都在运行

### 解决方法：禁用 Claude.app 的本地主机

**如果你使用 Claude Code CLI 进行浏览器自动化（不使用 Cowork）：**

```bash
# 禁用 Claude.app 的本地消息传递配置
mv ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/com.anthropic.claude_browser_extension.json \
   ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/com.anthropic.claude_browser_extension.json.disabled

# 确保 Claude Code 配置存在并指向包装器
cat ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json
```

**如果你使用 Cowork (Claude.app) 进行浏览器自动化：**

```bash
# 禁用 Claude Code 的本地消息传递配置
mv ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json \
   ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json.disabled
```

**你不能同时使用两者。** 选择一个并禁用另一个。

### 切换脚本

添加到 `~/.zshrc` 或直接运行：

```bash
chrome-mcp-toggle() {
    local CONFIG_DIR=~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts
    local CLAUDE_APP="$CONFIG_DIR/com.anthropic.claude_browser_extension.json"
    local CLAUDE_CODE="$CONFIG_DIR/com.anthropic.claude_code_browser_extension.json"

    if [[ -f "$CLAUDE_APP" && ! -f "$CLAUDE_APP.disabled" ]]; then
        # 当前使用 Claude.app，切换到 Claude Code
        mv "$CLAUDE_APP" "$CLAUDE_APP.disabled"
        [[ -f "$CLAUDE_CODE.disabled" ]] && mv "$CLAUDE_CODE.disabled" "$CLAUDE_CODE"
        echo "切换到 Claude Code CLI"
        echo "重启 Chrome 和 Claude Code 以应用"
    elif [[ -f "$CLAUDE_CODE" && ! -f "$CLAUDE_CODE.disabled" ]]; then
        # 当前使用 Claude Code，切换到 Claude.app
        mv "$CLAUDE_CODE" "$CLAUDE_CODE.disabled"
        [[ -f "$CLAUDE_APP.disabled" ]] && mv "$CLAUDE_APP.disabled" "$CLAUDE_APP"
        echo "切换到 Claude.app (Cowork)"
        echo "重启 Chrome 以应用"
    else
        echo "当前状态不明确。检查配置："
        ls -la "$CONFIG_DIR"/com.anthropic*.json* 2>/dev/null
    fi
}
```

使用方法：`chrome-mcp-toggle` 然后重启 Chrome（如果切换到 CLI，则重启 Claude Code）。

## 快速诊断

```bash
# 1. 哪个本地主机二进制文件正在运行？
ps aux | grep chrome-native-host | grep -v grep
# Claude.app: /Applications/Claude.app/Contents/Helpers/chrome-native-host
# Claude Code: ~/.local/share/claude/versions/X.X.X --chrome-native-host

# 2. 套接字在哪里？
# 对于 Claude Code (TMPDIR 中的单个文件)：
ls -la "$(getconf DARWIN_USER_TEMP_DIR)/claude-mcp-browser-bridge-$USER" 2>&1

# 对于 Claude.app (包含 PID 文件的目录)：
ls -la /tmp/claude-mcp-browser-bridge-$USER/ 2>&1

# 3. 本地主机连接到什么？
lsof -U 2>&1 | grep claude-mcp-browser-bridge

# 4. 哪些配置是活动的？
ls ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/com.anthropic*.json
```

## 关键洞察

**MCP 在启动时连接。** 如果浏览器桥接在 Claude Code 启动时尚未准备好，则整个会话的连接将失败。解决方法通常是：确保 Chrome + 扩展使用正确的配置运行，然后重启 Claude Code。

## 完全重置步骤（Claude Code CLI）

```bash
# 1. 确保正确的配置处于活动状态
mv ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/com.anthropic.claude_browser_extension.json \
   ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/com.anthropic.claude_browser_extension.json.disabled 2>/dev/null

# 2. 更新包装器以使用最新的 Claude Code 版本
cat > ~/.claude/chrome/chrome-native-host << 'EOF'
#!/bin/bash
LATEST=$(ls -t ~/.local/share/claude/versions/ 2>/dev/null | head -1)
exec "$HOME/.local/share/claude/versions/$LATEST" --chrome-native-host
EOF
chmod +x ~/.claude/chrome/chrome-native-host

# 3. 杀死现有的本地主机并清理套接字
pkill -f chrome-native-host
rm -rf /tmp/claude-mcp-browser-bridge-$USER/
rm -f "$(getconf DARWIN_USER_TEMP_DIR)/claude-mcp-browser-bridge-$USER"

# 4. 重启 Chrome
osascript -e 'quit app "Google Chrome"' && sleep 2 && open -a "Google Chrome"

# 5. 等待 Chrome，点击 Claude 扩展图标

# 6. 验证正确的本地主机正在运行
ps aux | grep chrome-native-host | grep -v grep
# 应显示：~/.local/share/claude/versions/X.X.X --chrome-native-host

# 7. 验证套接字是否存在
ls -la "$(getconf DARWIN_USER_TEMP_DIR)/claude-mcp-browser-bridge-$USER"

# 8. 重启 Claude Code
```

## 其他常见原因

### 多个 Chrome 配置文件

如果你在多个 Chrome 配置文件中安装了 Claude 扩展，每个配置文件都会生成自己的本地主机和套接字。这可能导致混淆。

**解决方法：** 仅在一个 Chrome 配置文件中启用 Claude 扩展。

### 多个 Claude Code 会话

运行多个 Claude Code 实例可能导致套接字冲突。

**解决方法：** 仅运行一个 Claude Code 会话，或在关闭其他会话后使用 `/mcp` 重新连接。

### 包装器中的硬编码版本

`~/.claude/chrome/chrome-native-host` 中的包装器可能有一个在更新后过时的硬编码版本。

**诊断：**
```bash
cat ~/.claude/chrome/chrome-native-host
# 坏的：exec "/Users/.../.local/share/claude/versions/2.0.76" --chrome-native-host
# 好的：使用 $(ls -t ...) 来查找最新版本
```

**解决方法：** 使用上述完全重置步骤中所示的动态版本包装器。

### TMPDIR 未设置

Claude Code 期望 `TMPDIR` 已设置以找到套接字。

```bash
# 检查
echo $TMPDIR
# 应显示：/var/folders/XX/.../T/

# 解决方法：添加到 ~/.zshrc
export TMPDIR="${TMPDIR:-$(getconf DARWIN_USER_TEMP_DIR)}"
```

## 深入诊断

```bash
echo "=== 本地主机二进制文件 ==="
ps aux | grep chrome-native-host | grep -v grep

echo -e "\n=== 套接字 (Claude Code 位置) ==="
ls -la "$(getconf DARWIN_USER_TEMP_DIR)/claude-mcp-browser-bridge-$USER" 2>&1

echo -e "\n=== 套接字 (Claude.app 位置) ==="
ls -la /tmp/claude-mcp-browser-bridge-$USER/ 2>&1

echo -e "\n=== 本地主机打开的文件 ==="
pgrep -f chrome-native-host | xargs -I {} lsof -p {} 2>/dev/null | grep -E "(sock|claude-mcp)"

echo -e "\n=== 活动的本地消息传递配置 ==="
ls ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/com.anthropic*.json 2>/dev/null

echo -e "\n=== 自定义包装器内容 ==="
cat ~/.claude/chrome/chrome-native-host 2>/dev/null || echo "没有自定义包装器"

echo -e "\n=== TMPDIR ==="
echo "TMPDIR=$TMPDIR"
echo "预期：$(getconf DARWIN_USER_TEMP_DIR)"
```

## 文件参考

| 文件 | 目的 |
|------|---------|
| `~/.claude/chrome/chrome-native-host` | 自定义包装器脚本，用于 Claude Code |
| `/Applications/Claude.app/Contents/Helpers/chrome-native-host` | Claude.app (Cowork) 本地主机 |
| `~/.local/share/claude/versions/<version>` | Claude Code 二进制文件（使用 `--chrome-native-host` 运行） |
| `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.anthropic.claude_browser_extension.json` | Claude.app 本地主机的配置 |
| `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.anthropic.claude_code_browser_extension.json` | Claude Code 本地主机的配置 |
| `$TMPDIR/claude-mcp-browser-bridge-$USER` | 套接字文件（Claude Code） |
| `/tmp/claude-mcp-browser-bridge-$USER/<PID>.sock` | 套接字文件（Claude.app） |

## 总结

1. **主要问题：** Claude.app (Cowork) 和 Claude Code 使用不同的本地主机，其套接字格式不兼容
2. **解决方法：** 禁用你未使用的那个本地消息传递配置
3. **任何修复后：** 必须重启 Chrome 和 Claude Code（MCP 在启动时连接）
4. **一个配置文件：** 仅在一个 Chrome 配置文件中安装 Claude 扩展
5. **一个会话：** 仅运行一个 Claude Code 实例

---

*原始技能由 [@jeffzwang](https://github.com/jeffzwang) 从 [@ExaAILabs](https://github.com/ExaAILabs) 提供。针对当前版本的 Claude 桌面和 Claude Code 进行了增强和更新。*
