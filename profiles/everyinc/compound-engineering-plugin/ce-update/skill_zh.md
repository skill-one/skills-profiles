# 检查插件版本

验证已安装的 compound-engineering 插件版本是否与 `main` 分支上的上游 `plugin.json` 匹配，并在不匹配的情况下推荐更新命令。Claude Code 仅限。

上游版本来自 `plugins/compound-engineering/.claude-plugin/plugin.json` 在 `main` 分支上，而不是最新的 GitHub 发布标签，因为市场（marketplace）从 `main` HEAD 安装插件内容。当 `main` 分支领先于最后一个标签（发布之间的正常状态）时，与发布标签比较会产生误报。

## 第 1 步：探测版本

通过 Bash 工具并行运行以下三个脚本。每个脚本打印单行输出；捕获以下决策逻辑的值。使用 `${CLAUDE_SKILL_DIR}` 以确保路径在 `claude --plugin-dir` 本地开发会话和标准市场缓存安装中都解析正确。

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/upstream-version.sh"
bash "${CLAUDE_SKILL_DIR}/scripts/currently-loaded-version.sh"
bash "${CLAUDE_SKILL_DIR}/scripts/marketplace-name.sh"
```

如果 `${CLAUDE_SKILL_DIR}` 未设置或无法解析（上述命令失败并显示 `No such file or directory`），则框架（harness）不会暴露技能目录——这不是标准的 Claude Code 会话。将其与第 2 步中的 `__CE_UPDATE_NOT_MARKETPLACE__` 情况相同对待：解释并停止。

`scripts/upstream-version.sh` 通过 `gh api` 读取 `main` 分支上的 `plugin.json`。它打印版本字符串，如果 `gh` 不可用或被限流，则打印哨兵值 `__CE_UPDATE_VERSION_FAILED__`。

`scripts/currently-loaded-version.sh` 和 `scripts/marketplace-name.sh` 解析 `${CLAUDE_SKILL_DIR}` 与市场缓存布局 `~/.claude/plugins/cache/<marketplace>/compound-engineering/<version>/skills/ce-update`。它们打印版本段 / 市场段，如果路径不匹配（典型情况为 `claude --plugin-dir` 本地开发），则打印哨兵值 `__CE_UPDATE_NOT_MARKETPLACE__`。

## 第 2 步：应用决策逻辑

### 处理失败情况

如果 `scripts/upstream-version.sh` 打印了 `__CE_UPDATE_VERSION_FAILED__`：告诉用户无法获取上游版本（gh 可能不可用或被限流），并停止。

如果 `scripts/currently-loaded-version.sh` 打印了 `__CE_UPDATE_NOT_MARKETPLACE__`：技能是从标准市场缓存外部加载的。两种情况简化为相同的处理：`claude --plugin-dir` 本地开发会话，或非 Claude-Code 平台（此技能仅限 Claude Code，因为它依赖于插件框架缓存布局）。告诉用户：

> "技能从市场缓存外部加载在 `~/.claude/plugins/cache/`。在使用 `claude --plugin-dir` 进行本地开发时这是正常的。本次会话无需操作。您的市场安装（如果有）不受影响——在常规的 Claude Code 会话中（不带 `--plugin-dir`）运行 `/ce-update` 以检查该缓存。"

然后停止。

### 比较版本

**已更新** — `currently_loaded == upstream`：

> "compound-engineering **v{version}** 已安装并是最新的。"

**已过时** — `currently_loaded != upstream`：

> "compound-engineering 当前为 **v{currently_loaded}**，但 **v{upstream}** 可用。
>
> 使用：
> ```
> claude plugin update compound-engineering@{marketplace_name}
> ```
> 然后重启 Claude Code 以应用。"

`claude plugin update` 命令随 Claude Code 本身一同提供，并将已安装插件更新到最新版本；它取代了早期的手动缓存清理 / 市场刷新的解决方案。市场名称从技能路径中派生而不是硬编码，因为此插件在多个市场名称下分发（例如，根据 README 为公共安装提供 `compound-engineering-plugin`，或为内部/团队市场提供其他名称）。
