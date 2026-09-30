---
name: speckit-taskstoissues
description: 将现有任务转换为基于可用设计工件的功能GitHub问题，并按依赖关系排序以实现可执行性。
---

## 用户输入

```text
$ARGUMENTS
```

在继续之前，您**必须**考虑用户输入（如果非空）。

## 执行前检查

**检查扩展钩子（任务到问题转换之前）**：

- 检查项目根目录中是否存在 `.specify/extensions.yml`。
- 如果存在，读取它并查找 `hooks.before_taskstoissues` 键下的条目。
- 如果 YAML 无法解析或无效，不要无声地跳过：告诉用户无法读取 `.specify/extensions.yml`（包括解析错误），并且没有检查任何钩子，包括那里注册的任何强制（`optional: false`）钩子，然后正常继续。
- 过滤掉 `enabled` 显式为 `false` 的钩子。将没有 `enabled` 字段的钩子视为默认启用。
- 对于每个剩余的钩子，**不要**尝试解释或评估钩子 `condition` 表达式：
  - 如果钩子没有 `condition` 字段，或者它是 null/空，将钩子视为可执行。
  - 如果钩子定义了非空的 `condition`，跳过该钩子，并将条件评估留给 HookExecutor 实现。
- 在从钩子命令名称构建命令调用时，将点（`.`）替换为连字符（`-`）。例如，`speckit.git.commit` → `/speckit-git-commit`。
- 对于每个可执行的钩子，根据其 `optional` 标志输出以下内容：
  - **可选钩子** (`optional: true`)：

    ```text
    ## 扩展钩子

    **可选预钩子**：{extension}
    命令：`/{command}`
    描述：{description}

    提示：{prompt}
    要执行：`/{command}`
    ```

  - **强制钩子** (`optional: false`)：

    ```text
    ## 扩展钩子

    **自动预钩子**：{extension}
    执行：`/{command}`
    EXECUTE_COMMAND：{command}

    在继续到 Outline 之前，等待钩子命令的结果。
    ```

    在发出上述块后，您**必须**实际调用钩子并等待它完成才能继续。以您在此代理/会话中自己运行命令的方式运行它（调用可能与上面显示的 `{command}` 字符串字面量不同，例如，技能模式代理作为 `/skill:speckit-...` 或 `$speckit-...` 运行它）。仅发出块本身不会运行钩子。
- 如果没有注册钩子或 `.specify/extensions.yml` 不存在，无声地跳过

## Outline

1. 从 repo root 运行 `.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` 并解析 FEATURE_DIR 和 AVAILABLE_DOCS 列表。所有路径必须为绝对路径。对于像 "I'm Groot" 这样的参数中的单引号，使用转义语法：例如 'I'\''m Groot'（如果可能，请使用双引号："I'm Groot"）。
1. **如果存在**：加载 `.specify/memory/constitution.md` 以获取项目原则和治理约束。
1. 从执行的脚本中提取任务路径。
1. 通过运行获取 Git 远端：

```bash
git config --get remote.origin.url
```

> [!警告]
> 只有当远程是 GITHUB URL 时才继续下一步

1. **获取现有问题以进行去重**：在创建任何内容之前，从 `tasks.md`（每个都是一个 `T` 后面跟着**至少**三个数字，例如 `T001` — `/speckit-converge` 使用 `T{M+1:03d}` 为新 ID 分配，这是一个地板而不是上限，所以一旦文件中有超过 999 个任务，ID 就是四位数或更长）。然后使用 GitHub MCP 服务器的 `list_issues` 工具查找已经涵盖这些 ID 的问题。不要传递 `state` 值，因为省略它会使工具返回打开和关闭的问题。请求 `perPage: 100` 以减少调用次数，并且由于该工具使用基于游标的分页，请求带有 `after` 参数的页面（使用来自先前响应的 `endCursor`）。对于每个问题标题，将其与任务 ID 模式 `\bT\d{3,}\b`（`{3,}` 接受四位数和更长的 ID — `\d{3}` 一个包含 `T1000` 的标题将完全不匹配，因为尾随的 `\b` 不能落在两个数字之间，因此该任务将无声地既不会被去重也不会被创建；词边界仍然会阻止像 `ST001` 这样的标记匹配，并强制整个数字序列被消耗，因此 `T100` 永远不可能在 `T1000` 内匹配；这也识别写为 `T001 ...`、`T001: ...` 或 `[T001] ...` 的问题标题）并匹配您的任务 ID 之一时，将标记该 ID 已经有一个问题。一旦每个任务 ID 都被匹配，或者当没有更多页面时停止分页，因此您不会继续获取整个仓库的问题历史，一旦所有任务 ID 都已 accounted for。这限制了具有大型问题历史的仓库的调用次数，并且在命令重新运行 `tasks.md` 重新生成或技能重新调用后仍然防止重复。
1. 对于列表中的每个任务，使用 GitHub MCP 服务器在代表 Git 远端的仓库中创建一个新问题。`tasks.md` 中的任务行以 markdown 复选框开头，因此首先删除开头的 `- [ ]`（以及任何 `[P]` / `[US#]` 标记）以恢复任务 ID 及其描述。使用单个规范标题创建问题 `T001: <description>`，ID 写一次后跟任务描述（例如，行 `- [ ] T001 Create project structure` 成为标题 `T001: Create project structure`）。
   - **跳过**任何其 ID 已存在于上一步生成的现有问题集中的任务，并报告它（例如，`T001 已经有一个问题，跳过`）。
   - 仅创建尚未具有匹配问题的任务的 issue。

> [!警告]
> 绝对不要在与远程 URL 不匹配的仓库中创建问题

## 执行后检查

**检查扩展钩子（任务到问题转换之后）**：
检查项目根目录中是否存在 `.specify/extensions.yml`。

- 如果存在，读取它并查找 `hooks.after_taskstoissues` 键下的条目。
- 如果 YAML 无法解析或无效，不要无声地跳过：告诉用户无法读取 `.specify/extensions.yml`（包括解析错误），并且没有检查任何钩子，包括那里注册的任何强制（`optional: false`）钩子，然后正常继续。
- 过滤掉 `enabled` 显式为 `false` 的钩子。将没有 `enabled` 字段的钩子视为默认启用。
- 对于每个剩余的钩子，**不要**尝试解释或评估钩子 `condition` 表达式：
  - 如果钩子没有 `condition` 字段，或者它是 null/空，将钩子视为可执行。
  - 如果钩子定义了非空的 `condition`，跳过该钩子，并将条件评估留给 HookExecutor 实现。
- 在从钩子命令名称构建命令调用时，将点（`.`）替换为连字符（`-`）。例如，`speckit.git.commit` → `/speckit-git-commit`。
- 对于每个可执行的钩子，根据其 `optional` 标志输出以下内容：
  - **可选钩子** (`optional: true`)：

    ```text
    ## 扩展钩子

    **可选钩子**：{extension}
    命令：`/{command}`
    描述：{description}

    提示：{prompt}
    要执行：`/{command}`
    ```

  - **强制钩子** (`optional: false`)：

    ```text
    ## 扩展钩子

    **自动钩子**：{extension}
    执行：`/{command}`
    EXECUTE_COMMAND：{command}
    ```

    在发出上述块后，您**必须**实际调用钩子并等待它完成才能继续。以您在此代理/会话中自己运行命令的方式运行它（调用可能与上面显示的 `{command}` 字符串字面量不同，例如，技能模式代理作为 `/skill:speckit-...` 或 `$speckit-...` 运行它）。仅发出块本身不会运行钩子。
- 如果没有注册钩子或 `.specify/extensions.yml` 不存在，无声地跳过
