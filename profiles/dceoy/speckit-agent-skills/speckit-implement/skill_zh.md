## 用户输入

```text
$ARGUMENTS
```

在继续之前，您**必须**考虑用户输入（如果非空）。

## 执行前检查

**检查扩展钩子（在实现之前）**：

- 检查项目根目录中是否存在 `.specify/extensions.yml`。
- 如果存在，读取它并查找 `hooks.before_implement` 键下的条目。
- 如果 YAML 无法解析或无效，不要无声地跳过：告知用户无法读取 `.specify/extensions.yml`（包括解析错误），并且没有检查任何钩子，包括任何注册的强制（`optional: false`）钩子，然后正常继续。
- 过滤掉 `enabled` 显式为 `false` 的钩子。将没有 `enabled` 字段的钩子视为默认启用。
- 对于每个剩余的钩子，**不要**尝试解释或评估钩子 `condition` 表达式：
  - 如果钩子没有 `condition` 字段，或者它是 null/空，将钩子视为可执行。
  - 如果钩子定义了非空的 `condition`，则跳过该钩子，并将条件评估留给 HookExecutor 实现。
- 在从钩子命令名称构建命令调用时，将点（`.`）替换为连字符（`-`）。例如，`speckit.git.commit` → `/speckit-git-commit`。
- 对于每个可执行的钩子，根据其 `optional` 标志输出以下内容：
  - **可选钩子** (`optional: true`)：

    ```text
    ## 扩展钩子

    **可选预执行钩子**：{extension}
    命令：`/{command}`
    描述：{description}

    提示：{prompt}
    要执行：`/{command}`
    ```

  - **强制钩子** (`optional: false`)：

    ```text
    ## 扩展钩子

    **自动预执行钩子**：{extension}
    执行：`/{command}`
    EXECUTE_COMMAND: {command}

    在继续到 Outline 之前，等待钩子命令的结果。
    ```

    在发出上述块后，您**必须**实际调用钩子并等待其完成才能继续。以您在此代理/会话中自己运行命令的方式运行它（调用可能与上面显示的 `{command}` ID 字面量不同，例如，技能模式代理将其运行为 `/skill:speckit-...` 或 `$speckit-...`）。仅发出块不会运行钩子。

- 如果没有注册钩子或 `.specify/extensions.yml` 不存在，则无声地跳过。

## Outline

1. 从 repo root 运行 `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` 并解析 FEATURE_DIR 和 AVAILABLE_DOCS 列表。所有路径必须为绝对路径。对于像 "I'm Groot" 这样的参数中的单引号，使用转义语法：例如 'I'\''m Groot'（如果可能，也可以使用双引号："I'm Groot"）。

2. **检查清单状态**（如果存在 `FEATURE_DIR/checklists/`）：
   - 将清单标记视为只读门：扫描复选框状态，报告状态，并在需要时询问是否继续；**不要**修改清单文件或标记
   - `checklists/requirements.md` 是由 `/speckit-specify` 和 `/speckit-clarify` 维护的内置规范质量清单；由 `/speckit-checklist` 生成的自定义清单是审阅者拥有的要求质量审阅工件
   - 对于自定义清单，`[x]` 表示审阅者确定要求质量标准已满足；**不**表示实现工作已完成
   - 扫描 checklists/ 目录中的所有清单文件
   - 对于每个清单，统计：
     - 总项目数：所有匹配 `- [ ]` 或 `- [X]` 或 `- [x]` 的行
     - 已检查项目数：匹配 `- [X]` 或 `- [x]` 的行
     - 未检查项目数：匹配 `- [ ]` 的行
   - 创建状态表：

     ```text
     | 清单 | 总数 | 已检查 | 未检查 | 状态 |
     |------|------|--------|--------|------|
     | ux.md | 12   | 12     | 0      | ✓ PASS |
     | test.md | 8   | 5      | 3      | ✗ FAIL |
     | security.md | 6 | 6      | 0      | ✓ PASS |
     ```

   - 计算整体状态：
     - **PASS**：所有清单都没有未检查的项目
     - **FAIL**：一个或多个清单有未检查的项目

   - **如果任何清单有未检查的项目**：
     - 显示带有未检查项目计数的表格
     - **停止**并询问："某些清单有未检查的项目。您想无论如何继续实现吗？(yes/no)"
     - 在继续之前等待用户响应
     - 如果用户说 "no" 或 "wait" 或 "stop"，则停止执行
     - 如果用户说 "yes" 或 "proceed" 或 "continue"，则继续到步骤 3

   - **如果所有清单都已检查**：
     - 显示显示所有清单通过的表格
     - 自动继续到步骤 3

3. 加载并分析实现上下文：
   - **必须**：读取 tasks.md 获取完整的任务列表和执行计划
   - **必须**：读取 plan.md 获取技术栈、架构和文件结构
   - **如果存在**：读取 data-model.md 获取实体和关系
   - **如果存在**：读取 contracts/ 获取 API 规范和测试要求
   - **如果存在**：读取 research.md 获取技术决策和约束
   - **如果存在**：读取 .specify/memory/constitution.md 获取治理约束
   - **如果存在**：读取 quickstart.md 获取集成场景

4. **项目设置验证**：
   - **必须**：根据实际项目设置创建/验证忽略文件：

   **检测和创建逻辑**：
   - 检查以下命令是否成功以确定仓库是否为 git 仓库（如果是，则创建/验证 .gitignore）：

     ```sh
     git rev-parse --git-dir 2>/dev/null
     ```

   - 检查是否存在 Dockerfile* 或 plan.md 中的 Docker → 创建/验证 .dockerignore
   - 检查是否存在 .eslintrc* → 创建/验证 .eslintignore
   - 检查是否存在 eslint.config.* → 确保配置的 `ignores` 条目覆盖所需模式
   - 检查是否存在 .prettierrc* → 创建/验证 .prettierignore
   - 检查是否存在 .npmrc 或 package.json → 创建/验证 .npmignore（如果发布）
   - 检查是否存在 terraform 文件 (*.tf) → 创建/验证 .terraformignore
   - 检查是否需要 .helmignore（存在 helm 图表）→ 创建/验证 .helmignore

   **如果忽略文件已存在**：验证其是否包含基本模式，仅追加缺失的关键模式
   **如果忽略文件缺失**：使用检测到的技术创建完整模式集

   **按技术划分的常见模式**（来自 plan.md 技术栈）：
   - **Node.js/JavaScript/TypeScript**：`node_modules/`, `dist/`, `build/`, `*.log`, `.env*`
   - **Python**：`__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `dist/`, `*.egg-info/`
   - **Java**：`target/`, `*.class`, `*.jar`, `.gradle/`, `build/`
   - **C#/.NET**：`bin/`, `obj/`, `*.user`, `*.suo`, `packages/`
   - **Go**：`*.exe`, `*.test`, `vendor/`, `*.out`
   - **Ruby**：`.bundle/`, `log/`, `tmp/`, `*.gem`, `vendor/bundle/`
   - **PHP**：`vendor/`, `*.log`, `*.cache`, `*.env`
   - **Rust**：`target/`, `debug/`, `release/`, `*.rs.bk`, `*.rlib`, `*.prof*`, `.idea/`, `*.log`, `.env*`
   - **Kotlin**：`build/`, `out/`, `.gradle/`, `.idea/`, `*.class`, `*.jar`, `*.iml`, `*.log`, `.env*`
   - **C++**：`build/`, `bin/`, `obj/`, `out/`, `*.o`, `*.so`, `*.a`, `*.exe`, `*.dll`, `.idea/`, `*.log`, `.env*`
   - **C**：`build/`, `bin/`, `obj/`, `out/`, `*.o`, `*.a`, `*.so`, `*.exe`, `*.dll`, `autom4te.cache/`, `config.status`, `config.log`, `.idea/`, `*.log`, `.env*`
   - **Swift**：`.build/`, `DerivedData/`, `*.swiftpm/`, `Packages/`
   - **R**：`.Rproj.user/`, `.Rhistory`, `.RData`, `.Ruserdata`, `*.Rproj`, `packrat/`, `renv/`
   - **通用**：`.DS_Store`, `Thumbs.db`, `*.tmp`, `*.swp`, `.vscode/`, `.idea/`

   **特定工具的模式**：
   - **Docker**：`node_modules/`, `.git/`, `Dockerfile*`, `.dockerignore`, `*.log*`, `.env*`, `coverage/`
   - **ESLint**：`node_modules/`, `dist/`, `build/`, `coverage/`, `*.min.js`
   - **Prettier**：`node_modules/`, `dist/`, `build/`, `coverage/`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
   - **Terraform**：`.terraform/`, `*.tfstate*`, `*.tfvars`, `.terraform.lock.hcl`
   - **Kubernetes/k8s**：`*.secret.yaml`, `secrets/`, `.kube/`, `kubeconfig*`, `*.key`, `*.crt`

5. 解析 tasks.md 结构并提取：
   - **任务阶段**：Setup, Tests, Core, Integration, Polish
   - **任务依赖**：顺序与并行执行规则
   - **任务详情**：ID、描述、文件路径、并行标记 [P]
   - **执行流程**：顺序和依赖要求

6. 按任务计划执行实现：
   - **按阶段执行**：完成每个阶段后再进入下一个阶段
   - **尊重依赖**：按顺序运行顺序任务，并行任务 [P] 可以一起运行
   - **遵循 TDD 方法**：在相应的实现任务之前执行测试任务
   - **基于文件的协调**：影响相同文件的任务必须按顺序运行
   - **验证检查点**：在继续之前验证每个阶段的完成情况

7. 实现执行规则：
   - **首先设置**：初始化项目结构、依赖项、配置
   - **先测试后代码**：如果您需要为合约、实体和集成场景编写测试
   - **核心开发**：实现模型、服务、CLI 命令、端点
   - **集成工作**：数据库连接、中间件、日志记录、外部服务
   - **精炼和验证**：单元测试、性能优化、文档

8. 进度跟踪和错误处理：
   - 在每个完成的任务后报告进度
   - 如果任何非并行任务失败，则停止执行
   - 对于并行任务 [P]，继续成功的任务，报告失败的任务
   - 提供清晰的错误消息和上下文以进行调试
   - 如果实现无法继续，则建议下一步操作
   - **重要**：对于完成的任务，确保在任务文件中将其标记为 [X]。

9. 完成验证：
   - 验证所有必需的任务是否已完成
   - 确认实现的功能与原始规范一致
   - 验证测试是否通过且覆盖率满足要求
   - 确认实现遵循了技术计划

注意：此命令假设在 tasks.md 中存在完整的任务分解。如果任务不完整或缺失，建议先运行 `/speckit-tasks` 重新生成任务列表。

## 强制执行后钩子

**在向用户报告完成之前，您必须完成本节**。

检查项目根目录中是否存在 `.specify/extensions.yml`。

- 如果不存在，或者 `hooks.after_implement` 下没有注册钩子，则跳转到完成报告。
- 如果存在，读取它并查找 `hooks.after_implement` 键下的条目。
- 如果 YAML 无法解析或无效，不要无声地跳过：告知用户无法读取 `.specify/extensions.yml`（包括解析错误），并且没有检查任何钩子，包括任何注册的强制（`optional: false`）钩子，然后继续到完成报告。
- 过滤掉 `enabled` 显式为 `false` 的钩子。将没有 `enabled` 字段的钩子视为默认启用。
- 对于每个剩余的钩子，**不要**尝试解释或评估钩子 `condition` 表达式：
  - 如果钩子没有 `condition` 字段，或者它是 null/空，将钩子视为可执行
  - 如果钩子定义了非空的 `condition`，则跳过该钩子，并将条件评估留给 HookExecutor 实现
- 在从钩子命令名称构建命令调用时，将点（`.`）替换为连字符（`-`）。例如，`speckit.git.commit` → `/speckit-git-commit`。
- 对于每个可执行的钩子，根据其 `optional` 标志输出以下内容：
  - **强制钩子** (`optional: false`) — **对于每个强制钩子，您必须发出 `EXECUTE_COMMAND:`**：

    ```text
    ## 扩展钩子

    **自动钩子**：{extension}
    执行：`/{command}`
    EXECUTE_COMMAND: {command}
    ```

    在发出上述块后，您**必须**实际调用钩子并等待其完成才能继续。以您在此代理/会话中自己运行命令的方式运行它（调用可能与上面显示的 `{command}` ID 字面量不同，例如，技能模式代理将其运行为 `/skill:speckit-...` 或 `$speckit-...`）。仅发出块不会运行钩子。

  - **可选钩子** (`optional: true`)：

    ```text
    ## 扩展钩子

    **可选钩子**：{extension}
    命令：`/{command}`
    描述：{description}

    提示：{prompt}
    要执行：`/{command}`
    ```

## 完成报告

报告最终状态，总结已完成的工作。

## 完成时

- [ ] tasks.md 中的所有任务完成并标记 `[X]`
- [ ] 实现与规范、计划和测试覆盖率进行验证
- [ ] 扩展钩子根据上述强制执行后钩子的规则进行分发或跳过
- [ ] 向用户报告完成，并总结已完成的工作
