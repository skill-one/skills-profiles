# 编写与提升 Grafana 技能

如何编写、审查和改进 SKILL.md 文件，使其通过仓库的 CI 门槛，并在 Anthropic 对齐的评分标准 Tessl 中获得高分。

## 关键规则（始终适用）

1. **描述是主要触发因素** — 第三人称，≤1024 字符，必须包含明确的 "Use when..." 描述，并列出用户自然使用的具体触发词。参见 [references/descriptions.md](references/descriptions.md) 中的强推描述模式，以对抗触发不足。
2. **正文少于 500 行** — 接近限制时拆分为 `references/*.md`。SKILL.md 是路由层，不是整个知识库。
3. **参考资料仅嵌套一层** — 直接从 SKILL.md 链接，绝不 `SKILL.md → a.md → b.md`。Claude 可能使用 `head -100` 预览嵌套链，并遗漏内容。
4. **使用祈使语气** — "运行 X" 而不是 "你应该运行 X" 或 "运行 X 很重要"。解释原因，避免使用过于强硬的 `MUST` 标记。
5. **具体示例胜过说明文** — 可复制粘贴的命令、真实的配置片段。Tessl 的 `actionability` 维度直接评分此部分。
6. **技能名称中无保留词** — `anthropic` 和 `claude` 在技能名称中禁止使用。
7. **正文无时效性语言** — "2025 年 8 月之后…" 会过时。使用 `<details>` "旧模式" 部分来存放遗留信息。
8. **提交前验证** — `./scripts/lint-skills.sh skills/<plugin>/<your-skill>` 清洁 + Tessl 评分 ≥75（运行 `tessl skill review --json <dir>`）。

## 评分标准

CI 会在任何修改了 SKILL.md 的 PR 中，如果其评分在四个 0-3 维度（**简洁性**、**可操作性**、**工作流清晰度**、**渐进式披露**）中低于 **75**，则失败。完整的维度评分 + Anthropic 文档映射在 [references/rubric.md](references/rubric.md) 中。

## 评分差异

裁判是一个 LLM，每次运行会波动 7-10 分。本地 94 通常会达到 CI 85。**仅在连续三次本地 100 后才提交**。

## 新技能决策树

1. **这个技能属于哪个产品/领域？**
   选择正确的插件文件夹：`grafana-core/`、`grafana-cloud/`、`grafana-lgtm/`、`grafana-app-sdk/`、`grafana-k6/`、`grafana-plugins/`。如果无法完全匹配，在创建新的插件组前询问用户（新组需要更新三个 `marketplace.json` 文件）。

2. **估算正文长度。**
   - <200 行实质性内容 → 单个 `SKILL.md`，无捆绑
   - 200-500 行 → `SKILL.md` + `references/<topic>.md` 用于长格式内容
   - >500 行 → 强制捆绑拆分；参见 [references/anatomy.md § 拆分策略](references/anatomy.md#splitting-strategies)

3. **首先编写"强推"描述。**
   描述是唯一始终加载到上下文中的内容。如果代理未触发技能，其他内容都无关紧要。参见 [references/descriptions.md](references/descriptions.md) 中的模式。

4. **参考四个维度评分标准起草正文。**
   - 删除 Claude 已知的每一句话（简洁性）
   - 用代码块替换说明文（可操作性）
   - 为每一步多步骤流程编号 + 在末尾添加验证步骤（工作流清晰度）
   - 如果需要 `<details>`，考虑该内容是否应放在 `references/` 中（渐进式披露）

5. **在市场清单中注册。**
   将技能路径添加到所有三个的 `skills` 数组中：
   - `.claude-plugin/marketplace.json`
   - `.cursor-plugin/marketplace.json`
   - `.agents-plugin/marketplace.json`

6. **本地验证。**
   ```bash
   # 1. Lint 清洁（0 错误）
   ./scripts/lint-skills.sh skills/<plugin>/<your-skill>

   # 2. Tessl reviewScore ≥75（CI 门槛）
   tessl skill review --json skills/<plugin>/<your-skill> | jq '.review.reviewScore'

   # 3. 如果低于 75 或希望 ≥85：运行 --optimize（需要认证）
   tessl skill review --optimize --yes --max-iterations 3 skills/<plugin>/<your-skill>
   ```

   如果运行失败：阅读 lint 错误 / Tessl 建议，修复，重新运行。直到两个检查都干净通过才打开 PR。反馈循环模式优于一次性写作。

## 修复低分现有技能

1. 阅读裁判的逐字建议文本（非 JSON 输出）：
   ```bash
   tessl skill review skills/<plugin>/<name>
   ```
   每个维度下的 `Suggestions:` 块会命名要删除的确切句子/段落。**复制建议** — 不要猜测。然后验证最低维度是否与你的理解一致。

2. 应用 [references/rubric.md](references/rubric.md) 中的修复模式：
   - **简洁性 1-2** → 删除引言、定义、主要指向参考资料的多行表格
   - **可操作性 1-2** → 用代码块和 CLI 命令替换说明文
   - **工作流清晰度 1-2** → 添加编号步骤 + 验证检查点
   - **渐进式披露 1-2** → 拆分为 `references/*.md`

3. 如果技能**有意作为路由文档**（如 `grafana-k6/k6-docs`），不要让 `--optimize` 将捆绑内容重新内联到 SKILL.md 中。手动编写一个最小化的可复制粘贴"验证循环"内联，使 SKILL.md 具有独立可操作性，同时保留捆绑。

4. 本地重新评分五次。**直到所有五次运行都达到 100** — 参见上文的 "评分差异" 原因。

## 反模式

参见 [references/anti-patterns.md](references/anti-patterns.md)。

## 参考资料

- [`references/descriptions.md`](references/descriptions.md) — 强推描述模式 + 触发词清单
- [`references/rubric.md`](references/rubric.md) — 每个维度的评分，包含 Anthropic 文档引用和具体修复模式
- [`references/anatomy.md`](references/anatomy.md) — 三级渐进式披露、捆绑布局、拆分策略
- [`references/anti-patterns.md`](references/anti-patterns.md) — 不该做什么，附带示例
- [Anthropic — Agent Skills 最佳实践](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [anthropics/skills — skill-creator SKILL.md](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)
- [构建 Claude 技能的完整指南 (PDF)](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)
