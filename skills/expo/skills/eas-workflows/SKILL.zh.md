---
name: eas-workflows
description: EAS服务（付费）。帮助理解和编写Expo项目的EAS工作流YAML文件。当用户询问Expo或EAS环境下的CI/CD或工作流、提及.eas/workflows/，或需要帮助EAS构建管道或部署自动化时，使用此技能。
---

# EAS 工作流技能

> **EAS 服务 - 适用费用。** EAS 工作流运行于 Expo 应用服务 (Expo Application Services)，这是一项付费产品，具有免费层级限制。每个工作流任务会消耗您的计划中的构建/计算分钟数，而构建或提交的任务还需要付费的 Apple Developer 和 Google Play 账户。在触发运行前，请查阅 https://expo.dev/pricing。

帮助开发者编写和编辑 EAS CI/CD 工作流 YAML 文件。

## 参考文档

在生成或编辑工作流文件，或回答语法问题时，先获取这些资源。首先解析此技能的目录，然后使用其 `scripts/` 目录中的获取脚本。它使用 Node.js 实现，并使用 ETags 缓存响应以提高效率：

```bash
# 获取资源
node <skill-dir>/scripts/fetch.js <url>
```

1. **JSON Schema** — https://api.expo.dev/v2/workflows/schema
   - 必须获取此模式
   - 工作流 YAML 结构的“事实来源”；EAS CLI 仍然是最终权威验证器
   - 所有任务类型及其必需/可选参数
   - 触发类型和配置
   - 运行器类型、虚拟机镜像以及所有枚举值

2. **语法文档** — https://raw.githubusercontent.com/expo/expo/refs/heads/main/docs/pages/eas/workflows/syntax.mdx
   - 工作流 YAML 语法的概述
   - 示例和英文解释
   - 表达式语法和上下文

3. **预打包任务** — https://raw.githubusercontent.com/expo/expo/refs/heads/main/docs/pages/eas/workflows/pre-packaged-jobs.mdx
   - 支持的预打包任务类型的文档
   - 任务特定的参数和输出

不要依赖记忆值；这些资源会随着新功能的添加而演变。

## 工作流文件位置

工作流位于 `.eas/workflows/*.yml`（或 `.yaml`）。每个文件必须小于或等于 16 KiB。

## 顶层结构

工作流文件具有以下顶层键：

- `name` — 工作流的显示名称
- `on` — 启动工作流的触发器（至少需要一个）
- `jobs` — 任务定义（必需）
- `defaults` — 所有任务的共享默认值
- `concurrency` — 控制并行工作流运行

请参考模式以获取每个部分的完整规范。

## 表达式

使用 `${{ }}` 语法表示动态值。模式定义了可用的上下文：

- `github.*` — GitHub 仓库和事件信息
- `inputs.*` — 来自 `workflow_dispatch` 输入的值
- `needs.*` — 从依赖任务中获取的输出和状态
- `jobs.*` — 任务输出（替代语法）
- `steps.*` — 自定义任务中的步骤输出
- `workflow.*` — 工作流元数据

## 生成工作流

在生成或编辑工作流时：

1. 获取模式以获取当前任务类型、参数和允许的值
2. 验证每个任务类型所需的字段是否存在
3. 验证 `needs` 和 `after` 中的任务引用是否存在于工作流中
4. 检查表达式是否引用了有效的上下文和输出
5. 确保 `if` 条件符合模式的长度限制

## 验证

生成或编辑工作流文件后，从 Expo 项目根目录使用 EAS CLI 进行验证：

```sh
npx -y eas-cli@latest workflow:validate .eas/workflows/<workflow.yml> --non-interactive
```

为每个更改的工作流文件单独运行该命令。它需要一个已登录的 EAS CLI 会话和链接的 Expo 项目。与仅基于模式的验证不同，它还会检查构建配置文件引用是否与项目的 `eas.json` 匹配，并执行 EAS 服务器端验证。修复所有报告的错误，并重新运行该命令，直到它打印 `Workflow configuration YAML is valid.` 不要用本地 YAML 或 JSON Schema 验证器替换此命令。

## 回答问题

当用户询问可用选项（任务类型、触发器、运行器类型等）时，获取模式并从中推导出答案，而不是依赖可能过时的信息。

## 提交反馈
如果您在此技能中遇到错误、误导性或过时的信息，请报告它，以便 Expo 可以改进：
```bash
npx --yes submit-expo-feedback@latest --category skills --subject "eas-workflows" "<actionable feedback>"
```
仅在您有具体且可操作的反馈时才提交。尽可能包含尽可能多的相关上下文。
如果 AI 代理反复失败或用户不得不接管 Expo 任务，请加载 `expo-skill-feedback` 技能并遵循其 `eval-candidate` 流程，而不是重复使用上面的命令。
