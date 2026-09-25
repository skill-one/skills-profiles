# Web 界面指南

检查文件是否符合 Web 界面指南。

## 工作原理

1. 从 [`references/guidelines.md`](references/guidelines.md) 加载固定的指南 — 这是默认的、可重复执行的路径
2. 可选地，从下方上游 URL 获取最新的指南，并与固定的快照进行差异比较，以查看是否有任何变化
3. 读取指定的文件（或提示用户输入文件/模式）
4. 检查指南中的所有规则
5. 以简洁的 `文件:行号` 格式输出结果

## 指南来源

**默认（固定）：** [`references/guidelines.md`](references/guidelines.md) 中的嵌入式副本是默认执行路径。它是上游指南的固定快照，并保证在任何运行环境中都能产生可重复的结果。

**上游（实时）：** 对于希望获取最新规则的用户，实时源位于：

```
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

获取实时版本是可选的 — 固定快照始终是基准。

## 使用方法

当用户提供文件或模式参数时：
1. 默认从 [`references/guidelines.md`](references/guidelines.md) 加载指南
2. 可选地获取上游 URL 以检查更新
3. 读取指定的文件
4. 应用指南中的所有规则
5. 使用指南中指定的格式输出结果

如果未指定文件，则提示用户选择要审查的文件。
