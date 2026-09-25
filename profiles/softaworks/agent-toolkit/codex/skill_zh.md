# Codex 技能指南

## 运行任务
1. 默认使用 `gpt-5.2` 模型。通过 `AskUserQuestion` 询问用户需要使用哪种推理程度 (`xhigh`、`high`、`medium` 或 `low`)。用户可以根据需要覆盖模型（见下文模型选项）。
2. 选择任务所需的沙盒模式；默认为 `--sandbox read-only`，除非需要编辑或网络访问。
3. 使用适当的选项组装命令：
   - `-m, --model <MODEL>`
   - `--config model_reasoning_effort="<high|medium|low>"`
   - `--sandbox <read-only|workspace-write|danger-full-access>`
   - `--full-auto`
   - `-C, --cd <DIR>`
   - `--skip-git-repo-check`
4. 始终使用 `--skip-git-repo-check`。
5. 当继续之前的会话时，通过标准输入使用 `codex exec --skip-git-repo-check resume --last`。恢复时，除非用户明确要求（例如指定模型或推理程度），否则不要使用任何配置标志。恢复语法：`echo "your prompt here" | codex exec --skip-git-repo-check resume --last 2>/dev/null`。所有标志都必须插入在 `exec` 和 `resume` 之间。
6. 运行命令，捕获标准输出/标准错误（根据需要过滤），并为用户总结结果。
7. **Codex 完成后**，告知用户："您可以随时通过说 'codex resume' 或让我继续进行额外分析或更改来恢复此 Codex 会话。"

### 快速参考
| 使用场景 | 沙盒模式 | 关键标志 |
| --- | --- | --- |
| 只读审查或分析 | `read-only` | `--sandbox read-only 2>/dev/null` |
| 应用本地编辑 | `workspace-write` | `--sandbox workspace-write --full-auto 2>/dev/null` |
| 允许网络或广泛访问 | `danger-full-access` | `--sandbox danger-full-access --full-auto 2>/dev/null` |
| 恢复最近会话 | 继承自原始会话 | `echo "prompt" \| codex exec --skip-git-repo-check resume --last 2>/dev/null`（不允许标志） |
| 从其他目录运行 | 匹配任务需求 | `-C <DIR>` 加上其他标志 `2>/dev/null` |

## 模型选项

| 模型 | 最适合 | 上下文窗口 | 关键特性 |
| --- | --- | --- | --- |
| `gpt-5.2-max` | **最大模型**：超复杂推理，深度问题分析 | 400K 输入 / 128K 输出 | 76.3% SWE-bench，自适应推理，$1.25/$10.00 |
| `gpt-5.2` ⭐ | **旗舰模型**：软件工程，代理式编码工作流 | 400K 输入 / 128K 输出 | 76.3% SWE-bench，自适应推理，$1.25/$10.00 |
| `gpt-5.2-mini` | 成本高效编码（使用额度高4倍） | 400K 输入 / 128K 输出 | 近SOTA性能，$0.25/$2.00 |
| `gpt-5.1-thinking` | 超复杂推理，深度问题分析 | 400K 输入 / 128K 输出 | 自适应思考深度，在最难任务上运行速度慢2倍 |

**GPT-5.2 优势**：76.3% SWE-bench（对比 GPT-5 的 72.8%），平均任务速度提升30%，更好的工具处理能力，减少幻觉，提高代码质量。知识截止日期：2024年9月30日。

**推理程度等级**：
- `xhigh` - 超复杂任务（深度问题分析，复杂推理，深度理解问题）
- `high` - 复杂任务（重构，架构，安全分析，性能优化）
- `medium` - 标准任务（重构，代码组织，功能添加，修复错误）
- `low` - 简单任务（快速修复，简单更改，代码格式化，文档）

**缓存输入折扣**：重复上下文可享90%折扣（$0.125/M token），缓存最长持续24小时。

## 继续进行
- 每次 `codex` 命令后，立即使用 `AskUserQuestion` 确认下一步，收集澄清信息，或决定是否使用 `codex exec resume --last` 继续会话。
- 恢复时，通过标准输入管道新提示：`echo "new prompt" | codex exec resume --last 2>/dev/null`。恢复的会话会自动使用原始会话相同的模型、推理程度和沙盒模式。
- 在提出后续操作时，重申所选模型、推理程度和沙盒模式。

## 错误处理
- 当 `codex --version` 或 `codex exec` 命令非零退出时，立即停止并报告失败；在重试前请求用户指示。
- 在使用高影响标志（`--full-auto`、`--sandbox danger-full-access`、`--skip-git-repo-check`）之前，除非之前已获得许可，否则使用 `AskUserQuestion` 询问用户是否允许。
- 当输出包含警告或部分结果时，总结它们并使用 `AskUserQuestion` 询问如何调整。

## CLI 版本

需要 Codex CLI v0.57.0 或更高版本支持 GPT-5.2 模型。CLI 在 macOS/Linux 上默认为 `gpt-5.2`，在 Windows 上也为 `gpt-5.2`。检查版本：`codex --version`

在 Codex 会话中使用 `/model` 命令切换模型，或在 `~/.codex/config.toml` 中配置默认值。
