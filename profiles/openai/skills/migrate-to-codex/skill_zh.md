# 迁移到 Codex

## 自主性

持续进行，直到选定的迁移完全完成：运行迁移器，检查报告，修复迁移的 Codex 指令/技能/代理/MCP 配置，并重新运行检查，无需停止以确认下一步。如果用户已选择目标，在创建、编辑、替换或删除该目标中生成的 Codex 资产（`AGENTS.md`、`.codex/`、`.agents/` 或 `~/.codex/`）之前，不要询问。保留 `.codex/config.toml` 或 `~/.codex/config.toml` 中无关的现有 Codex 配置条目，例如 `notify`、`projects`、`marketplaces` 或无关的 MCP 服务器；除非它们验证失败或直接与迁移冲突，否则不要询问它们。不要编辑源 Claude 代码文件（`.claude/`、`~/.claude/`、`.mcp.json` 或 `.claude.json`）、无关的项目代码、密钥或另一个存储库。

## 迁移顺序

对每个选定的全局或项目源，按此顺序运行迁移：

1. 首先使用 Codex 的内置 TODO/任务列表工具。除非用户明确要求，否则不要创建 `MIGRATION_TODOS.md` 或任何 TODO 文件。TODO 列表的输入具有一个 `plan` 数组，其项目每个都有 `step` 和 `status`；使用状态 `pending`、`in_progress` 和 `completed`。在完成之前，更新 TODO 列表，以便每个完成的步骤都标记为 `completed`，并且没有步骤保持 `in_progress`。使用字面量源 → Codex 目标标签，例如：
   - 检查 `.claude/commands` → Codex 技能/提示
   - 检查 `.claude/agents` → `.codex/agents`
   - 检查 `.mcp.json` → `.codex/config.toml` MCP 服务器
   - 检查 `.claude/settings.json` 钩子 → `.codex/hooks.json`
   - 迁移安全选定的资产 → Codex 文件
   - 验证生成的 `.codex/config.toml`
   - 验证生成的 `.codex/agents`
   - 报告迁移的资产和手动审核项

2. 阅读 `references/differences.md`（如果其 `Docs last checked` 日期已旧，请刷新 Codex 文档）。

3. 在写入之前扫描和检查：
   - `--scan-only` 列出活动和非活动源表面。
   - `--plan` 打印已阶段化的 Codex 资产路径和报告行。
   - `--doctor` 总结准备情况、手动审核工作以及验证风险。

4. 按 CLI 使用的相同顺序转换表面：
   - 指令：`CLAUDE.md` / `AGENTS.md` 到 `AGENTS.md`
   - 插件：报告 Claude 插件树和市集作为手动迁移工作
   - 钩子：将支持的 Claude 钩子重写为 `.codex/hooks.json` 并启用 `[features].codex_hooks = true`
   - 技能和命令：在 `.agents/skills/` 下写入 Codex 技能
   - 配置：从 Claude 模型/沙盒设置和 MCP 服务器写入 `.codex/config.toml`，配置生成时包括 `personality = "friendly"` 
   - 子代理：在 `.codex/agents/` 下写入 Codex 自定义代理

5. 干运行，然后写入选定的目标。仅在应删除孤儿生成的技能或代理时使用 `--replace`。

6. 实际运行后检查终端输出和 `.codex/migrate-to-codex-report.txt`。

7. 按此顺序审核生成的资产：`AGENTS.md`、`.agents/skills/`、`.codex/config.toml`、`.codex/hooks.json`、`.codex/agents/`，然后是仅报告的插件项。

8. 编辑后对每个目标运行 `--validate-target`。

9. 编辑后重新运行检查和 `--dry-run`。

10. 将最终迁移报告作为每个具有行的范围的 Markdown 表格返回。表格仅涵盖您执行的非原生后续迁移工作，例如从斜杠命令创建的技能、子代理、MCP 服务器、钩子、不支持的/本地插件注释和手动审核注意事项。仅在您在此后续运行中亲自迁移了配置、指令、技能或支持插件时，才包括程序化原生导入行。

    如果只有一个范围有行，则仅渲染无标题的表格。如果多个范围有行，则在每个表格之前渲染一个标题。使用 `**User Config**` 对于用户范围的行。对于项目范围的行，使用实际的项目文件夹名作为标题，例如 `**northstar-support-portal**`；不要使用 `Current Project` 作为标题。不要在表格输出之前或之后添加散文。

    使用以下确切列：

    **northstar-support-portal**

    | 状态 | 项 | 备注 |
    | --- | --- | --- |
    | `Added` | `Slash command` pr-review | 转换为 Codex 技能 |
    | `Added` | `Subagent` release-lead | 添加为 Codex 子代理 |
    | `Check before using` | `Hook` PreToolUse | 转换，但某些 Claude 钩子行为在 Codex 中有所不同 |
    | `Not Added` | `Hook` Notification | Codex 没有等效的通知钩子 |
    | `Not Added` | `Plugin` team-macros | 插件需要手动设置 |

    `状态` 必须是 `Added`、`Check before using` 或 `Not Added`。当创建或更改 Codex 面向的资产且无需特殊审核时，使用 `Added`。当创建或更改 Codex 面向的资产，但迁移改变了语义、推断行为、将工具规则作为指南或删除了不受支持的行为时，使用 `Check before using`。当检测到源资产但未创建 Codex 面向的资产时，使用 `Not Added`。`项` 将资产类型和具体项名合并到一个单元格中。资产类型必须是单数：`Skill`、`Slash command`、`Subagent`、`MCP`、`Hook` 或 `Plugin`。将资产类型用内联代码括起来；在它之后以纯文本形式写入项名。`备注` 总是必需的；永远不要让它为空。保持备注简短、平实和字面。避免使用内部实现术语，如运行时扩展。优先使用短语，如 `转换为 Codex 技能`、`添加为 Codex 子代理`、`添加到 Codex 配置`、`转换为 Codex 钩子`、`转换，但某些 Claude 钩子行为在 Codex 中有所不同`、`Codex 没有等效的通知钩子`、`插件需要手动设置` 或 `插件市集需要手动设置`。

## 自愈循环

持续循环，直到选定的迁移完成：

1. 运行 `--plan` 或 `--doctor`。
2. 使用 `--dry-run` 运行迁移。
3. 实际运行迁移。
4. 修复每个生成的 `## 需要手动迁移` 块和每个可以内部 Codex 资产中解决的 `manual_fix_required` 或 `skipped` 报告行。
5. 运行 `--validate-target`。
6. 重新运行迁移器和验证器，直到报告和验证器不再有可操作的生成资产修复项。

在此循环期间，不要编辑源 Claude 代码文件、无关的项目代码、密钥或另一个存储库。如果报告行需要源提供者更改或产品判断，请保留生成的 Codex 资产，并提供清晰的手动指导，而不是更改源。

## 命令

选择迁移器命令。

   ```bash
   MIGRATE_TO_CODEX='python3 .codex/skills/migrate-to-codex/scripts/migrate-to-codex.py'
   ```

在写入之前检查迁移。

   ```bash
   $MIGRATE_TO_CODEX --source ~/.claude/ --scan-only
   $MIGRATE_TO_CODEX --source ~/.claude/ --target ~/.codex/ --plan
   $MIGRATE_TO_CODEX --source ~/.claude/ --target ~/.codex/ --doctor
   ```

干运行，然后运行不带 `--dry-run`，用于全局和项目。

   ```bash
   $MIGRATE_TO_CODEX --source ~/.claude/ --target ~/.codex/ --dry-run
   $MIGRATE_TO_CODEX --source ~/.claude/ --target ~/.codex/
   $MIGRATE_TO_CODEX --source ./.claude/ --target ./.codex/ --dry-run
   $MIGRATE_TO_CODEX --source ./.claude/ --target ./.codex/
   ```

编辑后对每个目标运行迁移后验证器。

   ```bash
   $MIGRATE_TO_CODEX --validate-target ~/.codex/
   $MIGRATE_TO_CODEX --validate-target ./.codex/
   ```

运行 `$MIGRATE_TO_CODEX --help` 获取标志（`--scan-only`、`--plan`、`--doctor`、`--validate-target`、默认值等）。深度表格和更多链接在 `references/differences.md` 中。
