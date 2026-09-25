## 用户输入

```text
$ARGUMENTS
```

在继续之前，您**必须**考虑用户输入（如果非空）。

## 执行前检查

**检查扩展钩子（在规划之前）**：

- 检查项目根目录中是否存在 `.specify/extensions.yml`。
- 如果存在，读取它并查找 `hooks.before_plan` 键下的条目。
- 如果 YAML 无法解析或无效，不要静默跳过：告知用户无法读取 `.specify/extensions.yml`（包括解析错误），并且没有检查任何钩子，包括那里注册的任何必需的（`optional: false`）钩子，然后正常继续。
- 过滤掉 `enabled` 显式为 `false` 的钩子。将没有 `enabled` 字段的钩子视为默认启用。
- 对于每个剩余的钩子，**不要**尝试解释或评估钩子 `condition` 表达式：
  - 如果钩子没有 `condition` 字段，或者它是空/无，将钩子视为可执行。
  - 如果钩子定义了非空的 `condition`，则跳过该钩子，并将条件评估留给 HookExecutor 实现来处理。
- 在从钩子命令名称构建命令调用时，将点（`.`）替换为连字符（`-`）。例如，`speckit.git.commit` → `/speckit-git-commit`。
- 对于每个可执行的钩子，根据其 `optional` 标志输出以下内容：
  - **可选钩子** (`optional: true`)：

    ```text
    ## 扩展钩子

    **可选预执行钩子**：{extension}
    命令：`/{command}`
    描述：{description}

    提示：{prompt}
    执行：`/{command}`
    ```

  - **必需钩子** (`optional: false`)：

    ```text
    ## 扩展钩子

    **自动预执行钩子**：{extension}
    执行：`/{command}`
    EXECUTE_COMMAND: {command}

    在继续到 Outline 之前，等待钩子命令的结果。
    ```

    在发出上述块后，您**必须**实际调用钩子并等待其完成才能继续。以您在此代理/会话中运行命令的方式运行它（调用可能与上面显示的 `{command}` 字面量 ID 不同，例如，技能模式代理将其运行为 `/skill:speckit-...` 或 `$speckit-...`）。仅发出块不会运行钩子。
- 如果没有注册钩子或 `.specify/extensions.yml` 不存在，则静默跳过。

## Outline

1. **设置**：从仓库根目录运行 `.specify/scripts/bash/setup-plan.sh --json` 并解析 JSON 以获取 FEATURE_SPEC、IMPL_PLAN、FEATURE_DIR、BRANCH。对于像 "I'm Groot" 这样的参数中的单引号，使用转义语法：例如 'I'\''m Groot'（如果可能，请使用双引号："I'm Groot"）。

2. **加载上下文**：读取 FEATURE_SPEC 和 `.specify/memory/constitution.md`。加载 IMPL_PLAN 模板（已复制）。

3. **执行计划工作流**：按照 IMPL_PLAN 模板的结构执行：
   - 填写技术上下文（将未知项标记为 "NEEDS CLARIFICATION"）
   - 从宪法中填写宪法检查部分
   - 评估门（如果违规理由不充分，则报错）
   - 阶段 0：生成 research.md（解决所有 NEEDS CLARIFICATION）
   - 阶段 1：生成 data-model.md、contracts/、quickstart.md
   - 重新评估设计后的宪法检查

## 必需的执行后钩子

**在向用户报告完成之前，您必须完成此部分。**

检查项目根目录中是否存在 `.specify/extensions.yml`。

- 如果不存在，或者 `hooks.after_plan` 下没有注册钩子，则跳转到完成报告。
- 如果存在，读取它并查找 `hooks.after_plan` 键下的条目。
- 如果 YAML 无法解析或无效，不要静默跳过：告知用户无法读取 `.specify/extensions.yml`（包括解析错误），并且没有检查任何钩子，包括那里注册的任何必需的（`optional: false`）钩子，然后继续到完成报告。
- 过滤掉 `enabled` 显式为 `false` 的钩子。将没有 `enabled` 字段的钩子视为默认启用。
- 对于每个剩余的钩子，**不要**尝试解释或评估钩子 `condition` 表达式：
  - 如果钩子没有 `condition` 字段，或者它是空/无，将钩子视为可执行
  - 如果钩子定义了非空的 `condition`，则跳过该钩子，并将条件评估留给 HookExecutor 实现来处理
- 在从钩子命令名称构建命令调用时，将点（`.`）替换为连字符（`-`）。例如，`speckit.git.commit` → `/speckit-git-commit`。
- 对于每个可执行的钩子，根据其 `optional` 标志输出以下内容：
  - **必需钩子** (`optional: false`) — **对于每个必需钩子，您必须发出 `EXECUTE_COMMAND:`**：

    ```text
    ## 扩展钩子

    **自动钩子**：{extension}
    执行：`/{command}`
    EXECUTE_COMMAND: {command}
    ```

    在发出上述块后，您**必须**实际调用钩子并等待其完成才能继续。以您在此代理/会话中运行命令的方式运行它（调用可能与上面显示的 `{command}` 字面量 ID 不同，例如，技能模式代理将其运行为 `/skill:speckit-...` 或 `$speckit-...`）。仅发出块不会运行钩子。

  - **可选钩子** (`optional: true`)：

    ```text
    ## 扩展钩子

    **可选钩子**：{extension}
    命令：`/{command}`
    描述：{description}

    提示：{prompt}
    执行：`/{command}`
    ```

## 完成报告

设计阶段 1 结束后命令结束。报告分支、IMPL_PLAN 路径和生成的工件。

## 阶段

### 阶段 0：Outline & Research

1. **从技术上下文中提取未知项**：

   - 对于每个 NEEDS CLARIFICATION → 研究任务
   - 对于每个依赖项 → 最佳实践任务
   - 对于每个集成 → 模式任务

2. **生成和分派研究代理**：

   ```text
   对于技术上下文中的每个未知项：
     任务： "研究 {unknown} for {feature context}"
   对于每个技术选择：
     任务： "在 {domain} 中查找 {tech} 的最佳实践"
   ```

3. **使用以下格式在 `research.md` 中整合结果**：
   - 决策：[选择的内容]
   - 理由：[为什么选择]
   - 考虑的其他选项：[评估的其他内容]

**输出**：research.md，其中所有 NEEDS CLARIFICATION 已解决

### 阶段 1：设计 & 合同

**前提条件**：`research.md` 完成

1. **从功能规范中提取实体** → `data-model.md`：
   - 实体名称、字段、关系
   - 从要求中提取验证规则
   - 如适用，状态转换

2. **定义接口合同**（如果项目有外部接口）→ `/contracts/`：
   - 确定项目向用户或其他系统暴露的接口
   - 记录适合项目类型的合同格式
   - 示例：库的公共 API、CLI 工具的命令模式、Web 服务的端点、解析器的语法、应用程序的 UI 合同
   - 如果项目完全是内部的（构建脚本、一次性工具等），则跳过

3. **创建快速启动验证指南** → `quickstart.md`：
   - 记录可运行的验证场景，以证明功能端到端工作
   - 包括先决条件、设置命令、测试/运行命令和预期结果
   - 使用链接或引用到合同和数据模型详细信息，而不是重复它们
   - 不要包括完整的实现代码、模型/服务/控制器主体、迁移或完整的测试套件
   - 将此工件作为验证/运行指南；实现细节属于 `tasks.md` 和实现阶段

**输出**：data-model.md、/contracts/*、quickstart.md

## 关键规则

- 文件系统操作使用绝对路径；文档中的引用使用项目相对路径
- 在门失败或未解决的澄清时报错

## Done When

- [ ] 计划工作流执行并生成设计工件
- [ ] 扩展钩子根据上述必需的执行后钩子中的规则分派或跳过
- [ ] 向用户报告完成，包括分支、计划路径和生成的工件
