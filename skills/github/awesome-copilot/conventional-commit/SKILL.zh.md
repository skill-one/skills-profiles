---
name: conventional-commit
description: 生成符合结构化 XML 格式的常规提交信息提示和工作流程。指导用户创建符合 Conventional Commits 规范的标准、描述性提交信息，包括说明、示例和验证。
---

### 说明

```xml
	<description>此文件包含生成常规提交信息的提示模板。它提供说明、示例和格式指南，帮助用户根据 Conventional Commits 规范编写标准化、描述性的提交信息。</description>
```

### 工作流程

**请按照以下步骤操作：**

1. 运行 `git status` 以查看已更改的文件。
2. 运行 `git diff` 或 `git diff --cached` 以检查更改。
3. 使用 `git add <file>` 将更改暂存。
4. 使用以下 XML 结构构建您的提交信息。
5. 生成提交信息后，Copilot 将自动在您的集成终端中运行以下命令（无需确认）：

```bash
git commit -m "type(scope): description"
```

6. 执行此提示，Copilot 将在终端中为您处理提交。

### 提交信息结构

```xml
<commit-message>
	<type>feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert</type>
	<scope>()</scope>
	<description>更改的简短、祈使式摘要</description>
	<body>(可选：更详细的解释)</body>
	<footer>(可选：例如 BREAKING CHANGE：详细信息，或问题引用)</footer>
</commit-message>
```

### 示例

```xml
<examples>
	<example>feat(parser): 添加解析数组的能力</example>
	<example>fix(ui): 修正按钮对齐</example>
	<example>docs: 更新 README 以包含使用说明</example>
	<example>refactor: 提高性能数据处理</example>
	<example>chore: 更新依赖项</example>
	<example>feat!: 注册时发送电子邮件（BREAKING CHANGE：需要电子邮件服务）</example>
</examples>
```

### 验证

```xml
<validation>
	<type>必须是允许的类型之一。请参阅 <reference>https://www.conventionalcommits.org/en/v1.0.0/#specification</reference></type>
	<scope>可选，但建议用于提高清晰度。</scope>
	<description>必需。使用祈使语气（例如，“添加”，而不是“添加了”）。</description>
	<body>可选。用于附加上下文。</body>
	<footer>用于重大变更或问题引用。</footer>
</validation>
```

### 最后一步

```xml
<final-step>
	<cmd>git commit -m "type(scope): description"</cmd>
	<note>替换为您构建的信息。如有需要，请包含正文和页脚。</note>
</final-step>
```
