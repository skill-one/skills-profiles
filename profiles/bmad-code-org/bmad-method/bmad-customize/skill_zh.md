# BMad Customize

将用户的意图翻译为位于 `{project-root}/_bmad/custom/` 下正确位置的 TOML 覆盖文件，用于可定制的代理或工作流技能。发现、路由、授权、编写、验证。

范围 v1：每个技能的 `[agent]` 覆盖（`bmad-agent-<角色>.toml` / `.user.toml`）和每个技能的 `[workflow]` 覆盖（`bmad-<工作流>.toml` / `.user.toml`）。中央配置（`{project-root}/_bmad/custom/config.toml`）不在范围内 — 指引用户至 [如何定制 BMad 指南](https://docs.bmad-method.org/how-to/customize-bmad/)。

当目标的 `customize.toml` 没有暴露用户想要的内容时，明确说明。不要编造字段。

## 预检查

- 没有 `{project-root}/_bmad/` → 这里没有设置 BMad。提供运行 `bmad` 技能的设置，如果还没有安装 `bmad` 则先安装它（`npx skills add bmad-code-org/BMAD-METHOD --skill bmad`）。如果用户拒绝则停止。
- `{project-root}/_bmad/scripts/resolve_customization.py` 缺失 → 继续，但步骤 6 验证会回退到手动合并。
- 两者都存在 → 继续。

## 激活

问候用户。如果用户的调用已经命名了一个目标技能和特定的更改，跳转到步骤 3。

## 步骤 1：分类意图

- **定向** — 具体技能 + 具体更改 → 步骤 3。
- **探索性** — "我能定制什么？" → 步骤 2。
- **审计/迭代** — 想要审查或更改已经定制的内容 → 步骤 2，优先展示已有覆盖的技能；在步骤 3 组合前读取现有的覆盖。
- **跨切** — 可以存在于多个表面上 → 步骤 3，明确与用户选择代理还是工作流。

## 步骤 2：发现

```
uv run {skill-root}/scripts/list_customizable_skills.py --project-root {project-root}
```

如果用户在额外位置安装了技能，使用 `--extra-root <路径>`（可重复）。

将返回的 `agents` 和 `workflows` 分组给用户；每个显示名称、描述、`has_team_override` 或 `has_user_override` 是否为真。展示任何 `errors[]`。对于审计/迭代意图，优先展示已覆盖的条目。

空列表：显示 `scanned_roots`，询问技能是否存在于其他地方（提供 `--extra-root`）；否则停止。

## 步骤 3：确定正确的表面

读取目标的 `customize.toml`。顶层 `[agent]` 或 `[workflow]` 块定义了表面。

如果团队或用户覆盖已存在，先读取它并总结已覆盖的内容，然后再组合。

**跨切意图 — 与用户一起检查两个表面：**
- 每个代理运行的所有工作流 → 代理表面（例如 `bmad-agent-pm.toml` 中的 `persistent_facts`、`principles`）。
- 只有一个工作流 → 工作流表面（例如 `bmad-prd.toml` 中的 `activation_steps_prepend`）。
- 几个特定的工作流 → 多个工作流覆盖按顺序排列，不是代理覆盖。

**单表面启发式：**
- 工作流级：模板交换、输出路径、步骤特定行为，或已暴露的命名标量（`*_template`、`on_complete`）。外科手术式、可靠。
- 代理级：角色、沟通风格、组织级事实、菜单更改、应该适用于代理分派到每个工作流的行为。

当模糊时，展示两者并权衡，推荐一个，让用户决定。

意图超出暴露的表面（步骤逻辑、顺序、任何不在 `customize.toml` 中的内容）：说明；提供 `activation_steps_prepend`/`append` 或 `persistent_facts` 作为近似值，或推荐 `bmad-builder` 创建自定义技能。

## 步骤 4：组合覆盖

将普通英语翻译为针对目标的 `customize.toml` 字段的 TOML。如果读取了现有的覆盖，将更改作为附加项来构建。

合并语义：
- **标量**（`icon`、`role`、`*_template`、`on_complete`） — 覆盖胜出。
- **追加数组**（`persistent_facts`、`activation_steps_prepend`/`append`、`principles`） — 团队/用户条目按顺序追加。
- **键数组表**（带有 `code` 或 `id` 的菜单项） — 匹配键替换，新键追加。

覆盖是稀疏的：只更改的字段。永远不会复制整个 `customize.toml`。

**模板交换**（`*_template` 标量）：提供将默认模板复制到 `{project-root}/_bmad/custom/{skill-name}-{目的}-template.md`，将覆盖指向新路径，提供帮助编辑它。

## 步骤 5：团队或用户放置

在 `{project-root}/_bmad/custom/` 下：
- `{skill-name}.toml` — 团队，提交。策略、组织惯例、合规性。
- `{skill-name}.user.toml` — 用户，git 忽略。个人语气、私人事实、快捷方式。

按字符默认（策略 → 团队，个人 → 用户），确认后再写入。

## 步骤 6：展示、确认、写入、验证

1. 展示完整的 TOML。如果文件存在，展示差异。永远不要无声覆盖。
2. 等待明确的“是”。
3. 写入。如果需要，创建 `{project-root}/_bmad/custom/`。
4. 验证：
   ```
   uv run {project-root}/_bmad/scripts/resolve_customization.py --skill <安装路径> --project-root {project-root} --key <代理或工作流>
   ```
   展示合并后的输出，指出更改的字段。

   **解析器缺失或失败：** 读取存在的层 — `<安装路径>/customize.toml`（基础）、`{project-root}/_bmad/custom/{skill-name}.toml`（团队）、`{project-root}/_bmad/custom/{skill-name}.user.toml`（用户） — 按相同合并规则应用基础 → 团队 → 用户（标量胜出，表深度合并，`code`/`id`-键数组按键合并，所有其他数组追加），描述更改的字段如何解析。

   **验证显示覆盖未生效**（字段未更改、合并冲突、未选中文件）：重新进入步骤 4，将验证输出作为上下文。通常是字段名错误、合并模式错误（标量 vs 数组）、范围错误。
5. 总结更改内容、文件位置、如何迭代。提醒用户提交团队覆盖。

## 完成时

- 覆盖文件写入（或用户明确中止）。
- 用户已看到解析器输出（或手动回退合并摘要）。
- 用户已确认摘要。

否则技能未完成 — 完成或告诉用户他们正在退出未完成状态。

## 当这个技能无法帮助时

- **中央配置**（`{project-root}/_bmad/custom/config.toml`） — 见 [如何定制 BMad 指南](https://docs.bmad-method.org/how-to/customize-bmad/)。
- **步骤逻辑、顺序、不在 `customize.toml` 中的行为** — 提交功能请求，或使用 `bmad-builder` 创建自定义技能。提供帮助。
- **没有 `customize.toml` 的技能** — 无法定制。
