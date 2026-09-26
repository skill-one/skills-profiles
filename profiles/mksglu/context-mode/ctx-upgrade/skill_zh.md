# 上下文模式升级

从 GitHub 拉取最新版本并重新安装插件。

## 操作步骤

1. 直接调用 `ctx_upgrade` MCP 工具。它会返回一个要执行的 shell 命令。
2. 使用你的 shell 执行工具（Bash、shell_execute 等）运行返回的命令。
3. 以 markdown 复选框形式显示结果：
   ```
   ## 上下文模式升级
   - [x] 从 GitHub 拉取最新版本
   - [x] 构建 v1.0.39 并安装
   - [x] 配置钩子
   - [x] Doctor：所有检查通过
   ```
   使用 `[x]` 表示成功，`[ ]` 表示失败。显示实际版本号。
4. 提示用户**重启会话**以加载新版本。
5. **回退方案**（仅当 MCP 工具调用失败时使用）：从该技能的基本目录派生**插件根目录**（向上两级——删除 `/skills/ctx-upgrade`），然后使用 Bash 运行：
   ```
   CLI="<PLUGIN_ROOT>/cli.bundle.mjs"; [ ! -f "$CLI" ] && CLI="<PLUGIN_ROOT>/build/cli.js"; node "$CLI" upgrade
   ```
