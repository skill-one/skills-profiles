# 技能搜索 — 代理行为指令

## 自动引导（首次运行）

在其他任何操作之前，检查是否可用ccpm。如果不可用，请使用一个命令引导整个生态系统：

```bash
# 检查可用性
which ccpm || npx @daymade/ccpm setup
```

`ccpm setup`会安装此技能并配置Claude桌面MCP服务器（如果已安装）。引导完成后，以下所有命令可直接运行。

## 核心行为

当此技能被激活时，你必须使用Bash工具直接执行相应的`ccpm`命令。不要向用户显示命令并让他们复制粘贴——你自己执行它。

如果`ccpm`没有全局安装，请使用`npx @daymade/ccpm`作为所有以下命令的替代方案。

## 意图映射

将用户的意图匹配到正确的操作：

| 用户意图 | 操作 |
|-------------|--------|
| "查找X的技能" / "搜索X技能" | `ccpm search <query>` |
| "哪些技能很受欢迎" / "顶级技能" | `ccpm popular` |
| "有什么新技能" / "最新技能" | `ccpm recent` |
| "安装X" / "添加X技能" | `ccpm install <skill-name>` |
| "X是什么" / "告诉我关于X的信息" | `ccpm info <skill-name>` |
| "我有哪些技能" / "列出技能" | `ccpm list` |
| "删除X" / "卸载X" | `ccpm uninstall <skill-name>` |
| "更新X" / "更新所有技能" | `ccpm update [name] [--all]` |
| "我需要PDF/Excel/...的帮助" | `ccpm search <topic>`，然后提供安装最佳匹配项的选项 |

## 执行规则

1. **始终直接执行** — 通过Bash工具运行`ccpm`命令，不要要求用户手动运行。
2. **总结结果** — 执行后，以清晰易读的格式呈现输出结果。
3. **建议下一步操作** — 搜索结果后，提供安装选项。安装后，提醒用户重启Claude Code。
4. **优雅处理错误** — 如果找不到`ccpm`，则回退到`npx @daymade/ccpm`。如果注册表无法访问，请明确说明。
5. **命名空间技能** — 支持格式`@org/skill-name`（例如，`ccpm install @daymade/skill-creator`）。

## 命令参考

### 搜索
```bash
ccpm search <query> [--limit <n>] [--tags <t1,t2>] [--author <name>] [--smart]
```

### 发现
```bash
ccpm popular [--limit <n>]       # 下载量最多的
ccpm recent [--limit <n>]        # 最近发布/更新的
```

### 安装与管理
```bash
ccpm install <skill-name>        # 安装（用户级，默认）
ccpm install <name> --project    # 仅安装到当前项目
ccpm install <name> --force      # 强制重新安装
ccpm list                        # 列出已安装的技能
ccpm info <skill-name>           # 技能详细信息
ccpm update [name]               # 更新技能
ccpm update --all                # 更新所有技能
ccpm uninstall <skill-name>      # 删除技能
```

## 安装后提醒

在成功安装任何技能后，始终告诉用户：

> 技能安装成功。请重启Claude Code（或开始新的对话）以使技能可用。

## MCP服务器替代方案

对于希望原生工具集成的Claude桌面用户（无需Bash），相同的功能可作为MCP服务器提供：

```json
{
  "mcpServers": {
    "skill-search": {
      "command": "npx",
      "args": ["-y", "skills-search-mcp"]
    }
  }
}
```

此技能和MCP服务器都封装了相同的`ccpm` CLI——它们是互补的，不是冲突的。

## 故障排除

### "ccpm: 命令未找到"
使用`npx @daymade/ccpm`，或全局安装：`npm install -g @daymade/ccpm`。

### 安装后技能不可用
重启Claude Code——技能在启动时加载。

### 权限错误
检查对`~/.claude/skills/`的写入权限。尝试使用`--project`指定项目级范围进行安装。
