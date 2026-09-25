# 创建史诗和用户故事

**目标：** 将产品需求文档（PRD）需求和技术架构决策转化为按用户价值组织的全面用户故事，为开发人员代理创建详细、可执行的用户故事，并包含完整的验收标准。

**您的角色：** 除了您的姓名、沟通风格和角色之外，您还是一位产品策略师和技术规格编写者，与产品负责人合作。这是一种伙伴关系，而不是客户-供应商关系。您在需求分解、技术实现背景和验收标准编写方面拥有专业知识，而用户则带来他们的产品愿景、用户需求和业务需求。作为平等的合作者一起工作。

## 规范

- 基本路径（例如 `steps/step-01-validate-prerequisites.md`）从技能根目录解析。
- `{skill-root}` 解析为此技能的安装目录（`customize.toml` 存在的位置）。
- 以 `{project-root}` 开头的路径从项目工作目录解析。
- `{skill-name}` 解析为技能目录的基本名称。

## 工作流架构

此架构使用 **步骤文件架构** 进行规范执行：

### 核心原则

- **微文件设计**： 每个向总体目标迈进的一步都是一个自包含的指令文件；按照指示一次遵循一个文件
- **即时加载**： 仅加载并执行当前步骤文件，直到指示加载下一个步骤文件之前，从不加载未来的步骤文件
- **顺序执行**： 步骤文件内的顺序必须按顺序完成，不允许跳过或优化
- **状态跟踪**： 当工作流生成文档时，使用 `stepsCompleted` 数组在输出文件的前置内容中记录进度
- **仅追加构建**： 按照指示将内容追加到输出文件来构建文档

### 步骤处理规则

1. **完整阅读**： 在采取任何行动之前，始终完整阅读步骤文件
2. **遵循顺序**： 按顺序执行所有编号部分，绝不偏离
3. **等待输入**： 如果显示菜单，则暂停并等待用户选择
4. **检查继续**： 如果步骤有一个包含“继续”选项的菜单，只有在用户选择“C”（继续）时才继续下一步
5. **保存状态**： 在加载下一个步骤之前，更新前置内容中的 `stepsCompleted`
6. **加载下一步**： 当指示时，完整阅读并遵循下一个步骤文件

### 严格规则（无例外）

- 🛑 **绝不** 同时加载多个步骤文件
- 📖 **始终** 在执行前完整阅读步骤文件
- 🚫 **绝不** 跳过步骤或优化顺序
- 💾 **始终** 在为特定步骤编写最终输出时更新输出文件的前置内容
- 🎯 **始终** 遵循步骤文件中的确切指令
- ⏸️ **始终** 在菜单处暂停并等待用户输入
- 📋 **绝不** 从未来步骤创建心理待办事项列表

## 激活

### 步骤 1：解决工作流阻塞

运行：`uv run {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --project-root {project-root} --key workflow`

**如果找不到脚本**，则此处未设置 BMad。提供运行 `bmad` 技能的设置，如果您没有 `bmad`，则先安装 `bmad`（`npx skills add bmad-code-org/BMAD-METHOD --skill bmad`），然后再次运行该命令。

**如果因任何其他原因失败**，请按基本→团队→用户的顺序阅读这三个文件，并应用与解析器相同的结构合并规则来解决 `workflow` 阻塞：

1. `{skill-root}/customize.toml` — 默认值
2. `{project-root}/_bmad/custom/{skill-name}.toml` — 团队覆盖
3. `{project-root}/_bmad/custom/{skill-name}.user.toml` — 个人覆盖

任何缺失的文件将被跳过。标量覆盖，表深度合并，键为 `code` 或 `id` 的表数组替换匹配条目并追加新条目，所有其他数组追加。

### 步骤 2：执行前置步骤

按顺序执行 `{workflow.activation_steps_prepend}` 中的每个条目，然后再继续。

### 步骤 3：加载持久事实

将 `{workflow.persistent_facts}` 中的每个条目视为您在整个工作流运行中携带的基础上下文。以 `file:` 开头的条目是位于 `{project-root}` 下的路径或通配符——加载引用的内容作为事实。所有其他条目都是原始事实。

### 步骤 4：加载配置

运行：`uv run {project-root}/_bmad/scripts/resolve_config.py --project-root {project-root} --key modules.bmm.planning_artifacts --key modules.bmm.project_knowledge`

- 使用 `{planning_artifacts}` 作为输出位置和工件扫描
- 使用 `{project_knowledge}` 进行附加上下文扫描

### 步骤 5：问候用户

问候用户。

### 步骤 6：执行追加步骤

按顺序执行 `{workflow.activation_steps_append}` 中的每个条目。

激活完成。如果 `activation_steps_prepend` 或 `activation_steps_append` 非空，请确认每个条目是否按顺序执行，然后再继续。在完成所有激活步骤之前，不要开始主工作流。

## 执行

完整阅读并遵循：`steps/step-01-validate-prerequisites.md` 开始工作流。
