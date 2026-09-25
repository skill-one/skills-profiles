### 说明

```xml
	<description>该文件包含生成常规提交信息的提示模板。它提供说明、示例和格式指南，帮助用户根据 Conventional Commits 规范编写标准化、描述性的提交信息。</description>
```

### 工作流程

**请按照以下步骤操作：**

1. 运行 `git status` 查看已更改的文件。
2. 运行 `git diff` 或 `git diff --cached` 检查更改。
3. 使用 `git add <文件>` 将更改暂存。
4. 使用以下 XML 结构构建您的提交信息。
5. 生成提交信息后，Copilot 将自动在您的集成终端中运行以下命令（无需确认）：

```bash
git commit -m "类型(范围): 描述"
```

6. 执行此提示，Copilot 将在终端中为您处理提交。

### 提交信息结构

```xml
<commit-message>
	<类型>feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert</类型>
	<范围>()</范围>
	<描述>更改的简短、祈使式摘要</描述>
	<正文>(可选: 更详细的解释)</正文>
	<页脚>(可选: 例如 BREAKING CHANGE: 详情，或问题引用)</页脚>
</commit-message>
```

### 示例

```xml
<examples>
	<示例>feat(parser): 添加解析数组的能力</示例>
	<示例>fix(ui): 修正按钮对齐</示例>
	<示例>docs: 更新 README 以包含使用说明</示例>
	<示例>refactor: 提高性能的数据处理</示例>
	<示例>chore: 更新依赖项</示例>
	<示例>feat!: 注册时发送电子邮件 (BREAKING CHANGE: 需要电子邮件服务)</示例>
</examples>
```

### 验证

```xml
<validation>
	<类型>必须是允许的类型之一。请参阅 <参考>https://www.conventionalcommits.org/en/v1.0.0/#specification</参考></类型>
	<范围>可选，但建议用于清晰度。</范围>
	<描述>必需。使用祈使语气（例如，“添加”，而不是“添加了”）。</描述>
	<正文>可选。用于附加上下文。</正文>
	<页脚>用于重大更改或问题引用。</页脚>
</validation>
```

### 最后一步

```xml
<final-step>
	<cmd>git commit -m "类型(范围): 描述"</cmd>
	<注意>替换为您构建的信息。如有需要，请包含正文和页脚。</注意>
</final-step>
```
