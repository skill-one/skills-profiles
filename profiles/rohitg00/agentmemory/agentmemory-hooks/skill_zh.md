Claude Code 插件注册了生命周期钩子，以便自动捕获内存。对于常规工作，您无需调用 `memory_save`；钩子会观察工具使用情况、提示和会话边界，并为您记录观察结果。

## 快速入门

安装插件后，钩子会自动注册：

```bash
/plugin marketplace add rohitg00/agentmemory
/plugin install agentmemory
```

观察结果将实时显示在 `http://localhost:3113`。

## 钩子的作用

- 会话开始和结束钩子会为每个工作单元添加框架，并允许 `handoff` 恢复它。
- 工具使用钩子会捕获变化的原因，这是 `recall` 和 `recap` 的原始材料。
- 提示提交钩子会捕获意图。预压缩会在主机修剪之前保留上下文。
- 提交后钩子会将提交与会话关联，从而支持 `commit-context` 和 `commit-history`。

## 重要提示

- 捕获功能默认开启，且为零 LLM。将观察结果转换为 LLM 摘要 (`AGENTMEMORY_AUTO_COMPRESS`) 并将其注入上下文 (`AGENTMEMORY_INJECT_CONTEXT`) 是单独的选项，因为它们会消耗 token。
- 如果观察结果缺失，请确认插件已启用且服务器正在运行。请参阅 ../_shared/TROUBLESHOOTING.md。

## 参考信息

确切的注册钩子事件位于 REFERENCE.md 中，该文件由 `plugin/hooks/hooks.json` 生成。
