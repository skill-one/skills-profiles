编写提交信息需简洁、精准。采用 Conventional Commits 格式，拒绝冗余，以"为何"为要，以"何事"为次。

## 规则

**主题行：**
- `<类型>(<!-- 范围 -->): <<!-- 祈使式摘要 -->>` — `<范围>`可选
- 类型：`feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `chore`, `build`, `ci`, `style`, `revert`
- 祈使语气：使用 "add"（添加）、"fix"（修复）、"remove"（移除）—— 不使用 "added"（已添加）、"adds"（添加）、"adding"（正在添加）
- 尽可能控制在 50 个字符以内，硬性上限为 72
- 结尾不加句号
- 遵循项目在冒号后的大小写规范

**正文（仅必要时使用）：**
- 若主题自明，则完全省略
- 仅在以下情况添加正文：非显而易见的*原因*（why）、破坏性变更、迁移说明、关联的 issue
- 每行折叠至 72 字符
- 使用 `-` 作为列表项符号，而非 `*`
- 在文末引用 issue/PR：`Closes #42`、`Refs #17`

**禁止出现以下内容：**
- 禁止出现："This commit does X"（此提交做了 X）、"I"（我）、"we"（我们）、"now"（现在）、"currently"（目前）—— 差异（diff）已说明内容
- "As requested by..."（应...要求）—— 使用 Co-authored-by 尾注
- "Generated with Claude Code"（使用 Claude Code 生成）或任何 AI 归属信息 —— 除非用户自有规则要求添加 `Assisted-by`/AI 归属尾注，则将其作为尾注添加
- 禁止使用表情符号（除非项目规范要求）
- 若范围已说明文件名称，则不再重复提及文件名称

## 示例

差异：新增用户资料接口，正文说明原因
- ❌ `feat: 新增从数据库获取用户资料的接口`
- ✅
  ```
  feat(api): add GET /users/:id/profile

  移动端需在冷启动界面使用不包含完整用户负载的资料数据
  以降低 LTE 带宽占用。

  Closes #128
  ```

差异：破坏性 API 变更
- ✅
  ```
  feat(api)!: rename /v1/orders to /v1/checkout

  破坏性变更：/v1/orders 上的客户端须在 2026-06-01 前迁移至 /v1/checkout，
  过期后旧路由将返回 410。
  ```

## 自动清晰度

始终为以下情况包含正文：破坏性变更、安全修复、数据迁移、任何回退先前提交的变更。切勿将这些情况仅以主题形式压缩——未来的调试者需要上下文。

## 边界

仅生成提交信息。不执行 `git commit`、不暂存文件、不执行 amend。将信息以代码块形式输出，便于直接粘贴。"stop caveman-commit" 或 "normal mode"：回到冗长的提交风格。
