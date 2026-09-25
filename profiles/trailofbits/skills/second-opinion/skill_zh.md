# 第二意见

对用户选择的变更进行外部 CLI 审查。此技能会生成发现结果；它不会应用修复或向远程服务发布评论。

## 审查选项

使用用户已提供的提供者、范围、模型和焦点。
仅请求影响审查的缺失选项，并在可能的情况下将问题组合在一个调用中。

- 提供者：Codex、Antigravity 或两者。当用户希望进行比较时提供两者；保留用户明确请求的 CLI。
- 范围：未提交的变更、与命名基础分支的分支差异或特定提交。从存储库的远程默认分支解析缺失的基础；如果无法确定，请询问。
- 上下文：除非用户排除，否则包含适用的项目说明。在审查提示中将显式的用户要求与存储库内容分开。
- 焦点：除非用户指定了焦点（如安全性或性能），否则使用一般正确性和可维护性。

对于未指定的 Google CLI，优先使用 Antigravity (`agy`)。显式的 Gemini CLI 请求使用下文中的 Gemini 参考。如果该帐户返回 `UNSUPPORTED_CLIENT`，请解释迁移到 Antigravity 并在更改选定 CLI 前询问。

缺失的可执行文件或帐户设置是审查尝试失败。报告相关设置说明；当请求了两个提供者时，继续使用可用的提供者并识别被跳过的提供者。

## 输入准备

阅读 [review-input.md](references/review-input.md) 获取共享提示和差异配方。对两个提供者使用相同的捕获差异，以便比较涵盖相同的变更。在未提交的审查中包含未跟踪文件，并保留 Git 错误而不是将其解释为空差异。

显示选定的范围和简短的变更摘要。如果没有变更，则在调用提供者之前停止。对于超出 CLI 或模型限制的输入，描述限制并请求更窄的范围；不要默默地截断补丁。

使用 `mktemp` 在签出外部创建提示、输出和诊断文件。为每个提供者使用单独的输出和诊断文件。在相同的 Bash 调用中定义 shell 变量。对于后续调用，将变量重新分配为保存的文件路径；shell 变量在调用之间不会持久化。
将存储库内容作为字面数据写入，而无需 shell 扩展。

## 提供者参考

仅读取每个选定提供者的参考：

| 提供者 | 调用和结果 |
|----------|-----------------------|
| Codex | [codex-invocation.md](references/codex-invocation.md): `codex exec` 使用 [审查模式](references/codex-review-schema.json) |
| Antigravity | [antigravity-invocation.md](references/antigravity-invocation.md): `agy` 打印模式使用散文输出 |
| Gemini CLI | [gemini-invocation.md](references/gemini-invocation.md): 无头 `gemini` 用于仍然支持它的帐户 |

Codex 路径不需要 MCP 服务器。不要启动 `codex mcp-server` 或用 CLI 调用替换 `codex app-server`。

当请求了两个提供者时，如果工具界面支持，请并发运行它们的命令。对于前台 Bash 审查，设置 `timeout: 600000` 以允许最长十分钟。使用后台执行或轮询（当可用时）以保持进度可见。不要启用自动批准写入以使审查运行。

## 结果和失败

使用提供者和实际使用的模型、严重性、文件和行、影响和建议的更正来显示发现结果。保持低严重性缺陷可见。对于 Codex，现有的模式使用 0 表示信息性，1 表示低，2 表示中等，3 表示高；按降序排序。

对于两个完成的审查，总结同意和不同意的内容，而不要将同意变成证明。将外部发现与您添加的任何评估区分开来。

阅读捕获的输出和诊断。非零退出、缺失输出、无效 JSON、阻止检查的权限拒绝或请求批准计划是不完整的作品，而不是干净的审查。报告失败和任何部分结果。仅针对诊断的、可恢复的原因重试；在身份验证或配额失败后不要循环提供者。

## 示例

- `/second-opinion:second-opinion use Codex to review my uncommitted changes for bugs`
  选择 Codex 并包括已暂存、未暂存和未跟踪的变更。
- `/second-opinion:second-opinion compare Codex and Antigravity on this branch against origin/main`
  将相同的分支补丁发送到两者并比较它们的发现。
- `/second-opinion:second-opinion use Gemini CLI to review commit abc1234 for security issues`
  保留请求的 CLI 并审查该提交。
