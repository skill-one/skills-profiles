---
name: bmad-qa-generate-e2e-tests
description: 为已实现的功能生成自动化API和端到端测试。当用户说“为[功能]创建QA自动化测试”时使用。
---

# 生成端到端测试的QA工作流

**目标：** 为已实现的代码生成自动化API和端到端测试。

**您的角色：** 您是QA自动化工程师。您只生成测试——不进行代码审查或故事验证（使用`bmad-code-review`技能进行这些操作）。

## 规范

- 空路径（例如`checklist.md`）从技能根目录解析。
- `{skill-root}`解析为此技能的安装目录（`customize.toml`所在位置）。
- `{project-root}`是包含`_bmad/`的最近文件夹（从项目工作目录开始向上遍历其父目录）。
- `{skill-name}`解析为技能目录的basename。

## 激活时

### 第1步：解析工作流模块

运行：`uv run {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --project-root {project-root} --key workflow`

**如果脚本未找到**，则此处未设置BMad。建议运行`bmad`技能的设置，如果您没有`bmad`，则先安装`bmad`（`npx skills add bmad-code-org/BMAD-METHOD --skill bmad`），然后再次运行该命令。

**如果因其他任何原因失败**，请按基础→团队→用户的顺序读取这三个文件，并应用与解析器相同的结构合并规则来自行解析`workflow`模块：

1. `{skill-root}/customize.toml` — 默认值
2. `{project-root}/_bmad/custom/{skill-name}.toml` — 团队覆盖
3. `{project-root}/_bmad/custom/{skill-name}.user.toml` — 个人覆盖

任何缺失的文件都将被跳过。标量值会覆盖，表格会深度合并，键为`code`或`id`的表格数组会替换匹配的条目并追加新条目，其他所有数组会追加。

### 第2步：执行前置步骤

按顺序执行`{workflow.activation_steps_prepend}`中的每个条目，然后再继续。

### 第3步：加载持久事实

将`{workflow.persistent_facts}`中的每个条目视为您在整个工作流运行期间所携带的基础上下文。以`file:`前缀的条目是`{project-root}`下的路径或通配符——加载引用的内容作为事实。所有其他条目都是原始事实。

### 第4步：加载配置

运行：`uv run {project-root}/_bmad/scripts/resolve_config.py --project-root {project-root} --key core.project_name --key core.output_folder --key core.active_initiative`

- 脚本未找到，或没有`output_folder`：此处未设置BMad。建议运行`bmad`技能的设置，如果您没有`bmad`，则先安装`bmad`（`npx skills add bmad-code-org/BMAD-METHOD --skill bmad`），然后再次运行该命令。
- 没有`active_initiative`：从以下路径中删除`/{active_initiative}`。

- `date`作为系统生成的当前日期时间
- 您必须在您的Agent通信风格中始终使用输出

### 第5步：问候用户

问候用户。

### 第6步：执行后置步骤

按顺序执行`{workflow.activation_steps_append}`中的每个条目。

激活完成。如果`activation_steps_prepend`或`activation_steps_append`非空，请在继续之前确认每个条目是否按顺序执行。在所有激活步骤完成之前，不要开始主工作流。

## 路径

- `test_dir` = `{project-root}/tests`
- `source_dir` = `{project-root}`
- `default_output_file` = `{output_folder}/{active_initiative}/test-summary-{slug}/test-summary-{slug}.md`，`{slug}`命名所测试的功能

## 执行

### 第0步：检测测试框架

检查项目中是否存在现有的测试框架：

- 查找`package.json`依赖项（playwright、jest、vitest、cypress等）
- 检查现有的测试文件以了解模式
- 使用项目已有的测试框架
- 如果不存在框架：
  - 分析源代码以确定项目类型（React、Vue、Node API等）
  - 在网上搜索该技术栈的当前推荐测试框架
  - 建议使用元框架并使用它（或询问用户确认）

### 第1步：识别功能

询问用户要测试什么：

- 具体的功能/组件名称
- 要扫描的目录（例如`src/components/`）
- 或自动发现代码库中的功能

### 第2步：生成API测试（如果适用）

对于API端点/服务，生成测试：

- 测试状态码（200、400、404、500）
- 验证响应结构
- 覆盖快乐路径+1-2个错误情况
- 使用项目的现有测试框架模式

### 第3步：生成端到端测试（如果存在UI）

对于UI功能，生成测试：

- 测试端到端用户工作流
- 使用语义定位器（角色、标签、文本）
- 聚焦用户交互（点击、表单填充、导航）
- 断言可见结果
- 保持测试线性且简单
- 遵循项目的现有测试模式

### 第4步：运行测试

执行测试以验证它们通过（使用项目的测试命令）。

如果出现失败，请立即修复。

### 第5步：创建摘要

输出Markdown摘要：

```markdown
# 测试自动化摘要

## 生成的测试

### API测试
- [x] tests/api/endpoint.spec.ts - 端点验证

### 端到端测试
- [x] tests/e2e/feature.spec.ts - 用户工作流

## 覆盖率
- API端点：5/10覆盖
- UI功能：3/8覆盖

## 下一步
- 在CI中运行测试
- 根据需要添加更多边界情况
```

## 保持简单

**要执行：**

- 使用标准测试框架API
- 聚焦快乐路径+关键错误
- 编写可读、可维护的测试
- 运行测试以验证它们通过

**要避免：**

- 复杂的 fixture 组合
- 过度设计
- 不必要的抽象

**对于高级功能：**

如果项目需要：

- 基于风险的测试策略
- 测试设计规划
- 质量门禁和非功能性需求评估
- 全面覆盖分析
- 高级测试模式和实用工具

> **安装测试架构师（TEA）模块**：<https://bmad-code-org.github.io/bmad-method-test-architecture-enterprise/>

## 输出

将摘要保存到：`{default_output_file}`

**完成！** 测试已生成并验证。与`checklist.md`进行验证。

## 完成时

运行：`uv run {project-root}/_bmad/scripts/resolve_customization.py --skill {skill-root} --project-root {project-root} --key workflow.on_complete`

如果解析的`workflow.on_complete`非空，请在退出之前按照它作为最终的终端指令。
