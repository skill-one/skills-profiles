---
name: discover-azure-skills
description: 搜索 Azure 技能目录，并通过将 Azure 任务与技能元数据和插件安装指南进行匹配，推荐可安装的代理技能。何时使用：在开始涉及 Azure 或 Microsoft 云服务、产品或数据源的任何任务之前，当当前加载的技能或工具无法覆盖该任务时。
---

请按照以下步骤查找与给定任务描述匹配的可用 Azure 技能。

1. 列出插件

从 GitHub 内容 API 列出 Azure 插件目录：https://api.github.com/repos/microsoft/azure-skills/contents/.github/plugins?ref=main

在结果中，`type` 为 `dir` 的每个条目都是一个插件目录。技能按插件组织。

2. 列出技能

对于每个插件，从 GitHub 内容 API 列出其技能：https://api.github.com/repos/microsoft/azure-skills/contents/.github/plugins/{plugin-dirname}/skills?ref=main

在结果中，`type` 为 `dir` 的每个条目都是一个技能目录。每个技能都有一个 SKILL.md 文件，该文件解释了该技能的用途。

3. 发现相关技能

通过名称消除明显不相关的技能。然后，对于每个剩余的技能，从 API 读取其描述：https://raw.githubusercontent.com/microsoft/azure-skills/main/.github/plugins/{plugin-dirname}/skills/{skill-name}/SKILL.md

使用描述进一步消除不相关的技能。

4. 发现相关技能的插件名称

对于每个相关技能，通过从 GitHub 内容 API 读取 `plugin.json` 来发现其插件名称：https://raw.githubusercontent.com/microsoft/azure-skills/main/.github/plugins/{plugin-dirname}/.plugin/plugin.json

这很重要，因为插件的名称可能与其目录名称不同。安装命令取决于插件的名称。

5. 报告匹配的技能

报告匹配的技能并提供安装说明。可以通过安装其插件来安装技能。读取与代理客户端匹配的安装说明以提供安装说明。

- [Copilot CLI](./references/install/copilot-cli.md)
- [Claude Code](./references/install/claude-code.md)
- [其他](./references/install/other.md)
