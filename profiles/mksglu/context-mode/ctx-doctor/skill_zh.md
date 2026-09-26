# 上下文模式医生

直接在对话中运行诊断并显示结果。

## 使用说明

1. 直接调用 `ctx_doctor` MCP 工具。它会在服务器端运行所有检查，并返回纯文本状态报告。
2. 原样显示结果——它们已经使用纯文本状态前缀格式化：`[OK]` PASS, `[FAIL]` FAIL, `[WARN]` WARN。渲染安全（无 markdown 任务列表语法），以实现跨客户端兼容性（例如 Z.ai GLM）。
3. **备用方案**（仅当 MCP 工具调用失败时使用）：从此技能的基本目录（向上两级——删除 `/skills/ctx-doctor`）派生**插件根目录**，然后使用 Bash 运行：
   ```
   CLI="<PLUGIN_ROOT>/cli.bundle.mjs"; [ ! -f "$CLI" ] && CLI="<PLUGIN_ROOT>/build/cli.js"; node "$CLI" doctor
   ```
   使用相同的 `[OK]`/`[FAIL]`/`[WARN]` 前缀重新原样显示结果。
