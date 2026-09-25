# ADK 开发工作流程与指南

## 会话连续性

如果这是一个长时间的会话，请在每个阶段之前重新阅读相关技能——
在编写代码之前阅读 `/adk-cheatsheet`，在运行评估之前阅读 `/adk-eval-guide`，
在部署之前阅读 `/adk-deploy-guide`，在搭建框架之前阅读 `/adk-scaffold`。
上下文压缩可能会删除先前的技能内容。

---

## DESIGN_SPEC.md — 您的主要参考

**重要提示**：如果此项目中存在 `DESIGN_SPEC.md`，它是您的主要真实来源。

首先阅读它以了解：
- 功能需求和功能
- 成功标准和质量阈值
- 代理行为约束
- 预期工具和集成

**规范是您的合同。** 所有实现决策都应与其保持一致。如有疑问，请参考 `DESIGN_SPEC.md`。

---

## 第一阶段：理解规范

在编写任何代码之前：
1. 仔细阅读 `DESIGN_SPEC.md`
2. 确定所需的核心功能
3. 记录任何约束或代理不应做的事情
4. 了解评估的成功标准

## 第二阶段：构建和实现

实现代理逻辑：

1. 在代理目录中编写/修改代码（检查代理指导文件，例如 GEMINI.md 或 CLAUDE.md，以获取目录名称）
2. 使用 `make playground`（或 `adk web .`）在开发过程中进行交互式测试
3. 根据用户反馈迭代实现

对于 ADK API 模式和代码示例，使用 `/adk-cheatsheet`。

## 第三阶段：评估

**这是最重要的阶段。** 评估使用评估集和评分指标端到端验证代理行为。

**强制要求**：在运行评估之前激活 `/adk-eval-guide`。它包含评估集模式、配置格式和关键注意事项。不要跳过这一步。

**测试（`pytest`）不是评估。** 它们测试代码的正确性，但无法说明代理是否行为正确。始终运行 `adk eval`。

1. **从小处着手**：从 1-2 个样本评估用例开始，而不是完整的套件
2. 运行评估：`adk eval`（如果项目有 Makefile，则使用 `make eval`）
3. 与用户讨论结果
4. 修复问题并首先迭代核心用例
5. 只有在核心用例通过后，才添加边缘案例和新场景
6. 重复直到达到质量阈值

**这里可能需要 5-10 次或更多的迭代。**

## 第四阶段：部署

一旦达到评估阈值：

1. 准备好时部署——有关部署选项，请参阅 `/adk-deploy-guide`

**重要提示**：未经明确的人工批准，永远不要部署。

---

# 编码代理的操作指南

## 原则 1：代码保留与隔离

在执行代码修改时，您的首要目标是外科手术般的精确性。您**必须仅修改用户请求直接针对的代码段**，同时**严格保留所有周围的和不相关的代码**。

**强制执行的前执行验证：**

在最终确定任何代码替换之前，请验证：

1. **目标识别**：根据用户明确的指示，明确定义要更改的确切行或表达式。
2. **保留检查**：确保所有代码、配置值（例如，`model`、`version`、`api_key`）、注释和格式化*在识别的目标之外*保持完全相同。

**示例：**

*   **用户请求**："将代理的指令更改为食谱建议者。"
*   **不正确（违反）**：
    ```python
    root_agent = Agent(
        name="recipe_suggester",
        model="gemini-1.5-flash",  # 意外 - 模型未被要求更改
        instruction="You are a recipe suggester."
    )
    ```
*   **正确（遵守）**：
    ```python
    root_agent = Agent(
        name="recipe_suggester",  # OK，与新的用途相关
        model="gemini-3-flash-preview",  # 保留
        instruction="You are a recipe suggester."  # OK，直接目标
    )
    ```

## 原则 2：执行最佳实践

*   **模型选择 — 关键**：
    *   **除非明确要求，否则永远不要更改模型。** 如果代码使用 `gemini-3-flash-preview`，请保留为 `gemini-3-flash-preview`。不要"升级"或"修复"模型名称。
    *   创建新代理时（不是修改现有代理），使用 Gemini 3 系列：`gemini-3-flash-preview`、`gemini-3-pro-preview`。
    *   除非用户明确要求，否则不要使用旧模型（`gemini-2.0-flash`、`gemini-1.5-flash` 等）。

*   **位置比模型更重要**：
    *   如果模型返回 404，几乎总是 `GOOGLE_CLOUD_LOCATION` 问题（例如，需要 `global` 而不是 `us-central1`）。
    *   更改模型名称来"修复" 404 是违反规定的——修复位置而不是模型。
    *   某些模型（如 `gemini-3-flash-preview`）需要特定的位置。检查错误消息以获取提示。

*   **ADK 内置工具导入（精确要求）**：
    ```python
    # 正确 - 导入工具实例
    from google.adk.tools.load_web_page import load_web_page

    # 错误 - 导入模块，而不是工具
    from google.adk.tools import load_web_page
    ```
    将导入的工具直接传递给 `tools=[load_web_page]`，而不是 `tools=[load_web_page.load_web_page]`。

*   **运行 Python 命令**：
    *   始终使用 `uv` 执行 Python 命令（例如，`uv run python script.py`）
    *   在执行脚本之前运行 `make install`（或 `uv sync`）
    *   查阅 `Makefile` 和 `README.md` 以获取可用命令（如果存在）

*   **打破无限循环**：
    *   如果您连续 3 次看到相同的错误，请**立即停止**
    *   **不要重试失败的操作**——首先修复根本原因
    *   **危险信号**：锁 ID 递增，名称追加 v5->v6->v7，反复说"我会再试一次"
    *   **状态冲突**（错误 409：资源已存在）：使用 `terraform import` 导入现有资源，而不是重试创建
    *   **工具错误**：在继续之前修复源代码错误——不要绕过它们
    *   **卡住时**：直接运行底层命令（例如，`terraform` CLI）而不是调用有问题的工具

*   **故障排除**：
    *   首先检查 `/adk-cheatsheet`——它涵盖了大多数常见模式
    *   使用 Glob/Grep/Read 搜索已安装的 ADK 包（使用 `python -c "import google.adk; print(google.adk.__path__[0])"` 找到它——如果使用 uv，请使用 `uv run python`）
    *   对于 ADK 文档索引，使用 `curl https://adk.dev/llms.txt`
    *   对于框架问题或 GCP 产品，请检查官方文档
    *   当遇到持续错误时，有针对性的 Google 搜索通常能更快地找到解决方案

---

## 搭建作为参考

当您需要特定的基础设施文件，但不想直接在当前项目中搭建时，使用 `/adk-scaffold` 技能创建 `/tmp/` 中的临时参考项目，并复制您需要的内容。

有关完整的 CLI 命令和选项，请参阅 `/adk-scaffold`。

---

## 开发命令

通过 Agent Starter Pack CLI 创建的项目包含一个包含这些命令的 Makefile。
要创建或增强项目，请参阅 `/adk-scaffold` 技能获取完整说明。
对于非搭建项目，请使用 ADK CLI 对应命令。

| Make（搭建） | ADK CLI 对应命令 | 目的 |
|------------|-------------------|---------|
| `make playground` | `adk web .` | 交互式本地测试 |
| `make test` | `pytest` | 运行单元和集成测试 |
| `make eval` | `adk eval <agent_dir> <evalset>` | 对评估集运行评估 |
| `make lint` | `ruff check .` | 检查代码质量 |
| `make setup-dev-env` | —（仅搭建项目） | 设置开发基础设施（Terraform） |
| `make deploy` | —（仅搭建项目） | 部署到开发环境（需要人工批准） |

---

## 技能版本

> **故障排除提示**：如果您遇到重复错误、意外的工具故障或这些技能中的指令似乎不完整或引用了您找不到的功能，技能可能已过时。运行：
> ```
> npx skills check -g
> ```
> 如果它报告过时的技能，请告诉用户更新：
> ```
> npx skills update -g
> ```
> 不要在每次会话中都运行此检查——只有在您怀疑过时的技能导致问题时才运行。
