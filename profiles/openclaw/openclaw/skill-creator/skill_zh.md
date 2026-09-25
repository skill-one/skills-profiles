# 技能创建器

## 工作流程

1. 建立合同。
   - 阅读现有技能及其资源，或收集新技能的具体需求。
   - 将实际工作流分支与同义词分支分离。
   - **完成时：** 每个分支都有具体的触发器、预期结果和持久化目标。

2. 选择调用方式。
   - 模型可发现：编写面向模型的 `description`；省略 `disable-model-invocation`。
   - 仅手动：设置 `disable-model-invocation: true`；编写面向人类的摘要。
   - 直接工具命令：仅在命令绕过模型时添加 `command-dispatch: tool`、`command-tool` 和 `command-arg-mode`。
   - **完成时：** 前置部分与技能实际被访问的方式匹配。

3. 结构化技能。
   - 将共享的有序流程映射到 `SKILL.md`；每个步骤都以可检查的完成标准结束，并以验证结束。
   - 将路由条件保留在 `description` 中；以执行开始主体。
   - 将分支专有细节映射到 `references/`，确定性辅助工具映射到 `scripts/`，输出资源映射到 `assets/`，可选的 UI 元数据映射到 `agents/`。
   - **完成时：** 每个计划资源都有单一目的，并且从 `SKILL.md` 有直接指向。

4. 起草并持久化。
   - 活动工作区技能：使用 `skill_workshop` 创建或修订待处理的提案；在应用前保持活动文件不变。
   - 仓库拥有的技能源：使用仓库的正常编辑和审查工作流。
   - **完成时：** 提案或源差异实现了步骤 1 中的每个分支，并包含步骤 3 中的每个资源。

5. 验证。
   - 运行 `python {baseDir}/scripts/quick_validate.py <skill-directory>` 并执行每个被修改的辅助工具的聚焦测试。
   - **完成时：** 前置部分通过，资源指针解析，并且每个被修改的辅助工具通过其聚焦测试。

## 前置部分

必需：`name`、`description`。

OpenClaw 还支持 `metadata`、`homepage`、`license`、`allowed-tools`、`user-invocable`、`disable-model-invocation`、`command-dispatch`、`command-tool` 和 `command-arg-mode`。仅在它们改变运行时行为或发现时添加可选字段。
