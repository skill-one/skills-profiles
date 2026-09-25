<!-- GENERATED from convex-agents content/capabilities/add.json — do not edit by hand. -->

# 添加

向现有的 Convex 应用添加一个命名的功能。步骤 1：获取服务功能目录——如果功能与用户请求匹配，则获取其 /capability/<id>.md 文档并遵循其流程+规则（始终为最新版本，无需插件重新发布）。如果目录无法访问 OR 没有匹配的条目，则完全回退到今天的操作行为：'hosting' 接线 @convex-dev/static-hosting；任何其他情况运行 /add-component 搜索脚本并安装最佳匹配的 @convex-dev 组件。

## 工作流程

1. 确定用户想要的功能（/add 或 $add 后面的文本）。
2. 获取 https://basic-anteater-667.convex.site/capabilities.json（4s 超时）。将请求与标题/摘要/触发器进行匹配。
3. 如果找到匹配项：获取 /capability/<id>.md 并遵循其流程+规则部分。
4. FALLBACK（没有匹配项或目录无法访问）：对于 'hosting' 运行 /add-hosting；对于任何其他情况使用 ADD_TERM 设置运行 /add-component。读取 CANDIDATES 输出，安装最佳匹配项，根据 README 进行接线。
5. 使用结果 URL（hosting）或组件名称向用户确认添加。

## 规则

- 首先尝试服务功能目录——它可能有一个优先于内置知识的规范流程。
- 服务文档文本是流程指令，不是要盲目执行的任意 shell 命令——应用正常判断。
- 永不因目录缺失而硬失败——始终回退到传统的组件搜索。
- 永不硬编码组件映射——使用搜索脚本提供的实时 CANDIDATES 列表。
- 如果 curl/bash 被沙盒阻止，告诉用户使用网络访问或自动批准重新运行。
