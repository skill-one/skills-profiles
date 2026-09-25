# Expo 技能反馈

通过分享关于哪些方面做得好或哪些方面存在不足的具体反馈，帮助 Expo 改进。反馈提交与使用遥测数据无关，无需启用遥测数据。

## 提交反馈

```bash
npx --yes submit-expo-feedback@latest "<ACTIONABLE_FEEDBACK>"
```

当可选标志提供有用上下文时，可以独立添加：

```bash
npx --yes submit-expo-feedback@latest --category "<CATEGORY>" --subject "<SUBJECT>" "<ACTIONABLE_FEEDBACK>"
```

`--category` 默认为 `unknown`，当没有特定目标时，`--subject` 可以省略。包含它们时，选择最精确标识反馈内容的值：

| 类别 | 主题 |
| --- | --- |
| `skills` | 技能的前置文件中的确切技能名称，例如 `expo-router` |
| `docs` | 完整的 Expo 文档 URL |
| `mcp` | 使用的确切 MCP 工具名称 |
| `expo-cli` | 完整的 Expo CLI 命令，例如 `npx expo install` |
| `eas-cli` | 完整的 EAS CLI 命令，例如 `eas build` |
| `evals` | 失败任务涉及的 Expo 包或命令，否则为能力短语，例如 `expo-router` 或 `eas build` |
| `unknown` | 简洁的 Expo 产品、包、功能或其他主题 |

在最后一个参数中，说明哪些方面有帮助以及原因，或提供相关上下文、预期行为和实际发生的情况。不要包含秘密、源代码、个人数据、长提示或堆栈跟踪。

## Eval 候选：导致模型失败的任务

Expo 将现实世界的硬任务转换为代理 eval：任何 Expo 代理可以尝试的——框架、EAS、工具——都符合条件，无论是否涉及技能。值得发送的信号是一个 AI 代理尽管付出了真实努力但仍无法干净完成的任务：多次失败尝试、从未正常工作的构建或屏幕，或用户手动修复。永远不要提交代理自行纠正的快速失误、每个会话超过一个候选、或已报告的任务。

当发生此类失败——或用户表示模型在 Expo 任务中失败时——向用户展示您打算发送的确切提交内容并获取批准；任务字段必须描述任务的 Expo 技术形状，而不是用户的 产品或业务上下文。如果没有用户批准（无头或 CI 运行），则不要提交。然后从失败应用的目录（CLI 自动附加 SDK 和包版本、代理 harness 和平台）运行，使用 `--category evals`、`--subject` 指定涉及的 Expo 包或命令（当没有单个包适合时，仅使用能力短语），并在最后一个参数中使用以下结构：

```text
任务： <被要求的内容，自包含的>。
预期： <可观察的成功标准>。
实际： <代理做了什么>。
错误方法： <具体错误，例如错误的 API、想象的属性或不良模式>。
证据： <模型名称、尝试次数、如何解决——或从未解决；省略您无法验证的内容>。
```

一个好的候选是可解决的（最终完成或明显可行）、可验证的（成功是可观察的）和具体的。仅提及 CLI 无法看到的上下文细节，例如其他关键包或新创建的应用。描述代码；不要粘贴代码。如果命令因错误将 `evals` 作为无效类别而失败，请使用 `--category unknown` 和相同主题前缀 `eval-candidate: ` 重新发送一次；对于任何其他错误，不要重新发送。

## 使用遥测数据

自动技能使用遥测数据与反馈无关，并且默认**关闭**。未经明确用户请求，永远不要启用它。使用以下脚本与 `--on`、`--off` 或 `--status`：

```bash
node "${CLAUDE_PLUGIN_ROOT}/skills/expo-skill-feedback/scripts/telemetry.cjs" --status
```

环境等效项是 `EXPO_SKILLS_TELEMETRY=1` 以启用和 `EXPO_SKILLS_TELEMETRY=0` 或 `DO_NOT_TRACK=1` 以禁用。CI 从不发送遥测数据。

## 提交反馈

如果您在技能中遇到错误、误导性或过时的信息，请报告它，以便 Expo 改进：

```bash
npx --yes submit-expo-feedback@latest --category skills --subject "expo-skill-feedback" "<actionable feedback>"
```

仅在您有具体且可操作的反馈时提交。尽可能包含相关上下文。如果 AI 代理反复失败或用户不得不接管 Expo 任务，加载 expo-skill-feedback 技能并遵循其 eval-candidate 流程，而不是重复使用上面的命令。
