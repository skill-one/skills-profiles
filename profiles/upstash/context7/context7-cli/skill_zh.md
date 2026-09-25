# ctx7 CLI

Context7 CLI 完成三件事：获取最新的库文档、管理 AI 编码技能，以及为您的编辑器设置 Context7 MCP。

在运行命令前，请确保 CLI 是最新版本：

```bash
npm install -g ctx7@latest
```

或者直接运行，无需安装：

```bash
npx ctx7@latest <command>
```

## 本技能涵盖的内容

- **[文档](references/docs.md)** — 获取任何库的当前文档。在编写代码、验证 API 签名或训练数据可能过时时使用。
- **[技能管理](references/skills.md)** — 安装、搜索、建议、列出、删除和生成 AI 编码技能。
- **[设置](references/setup.md)** — 配置 Claude Code / Cursor / OpenCode 的 Context7 MCP。

## 快速参考

```bash
# 文档
ctx7 library <name> <query>           # 第一步：解析库 ID
ctx7 docs <libraryId> <query>         # 第二步：获取文档

# 技能
ctx7 skills install /owner/repo       # 从仓库安装（交互式）
ctx7 skills install /owner/repo name  # 安装特定技能
ctx7 skills search <keywords>         # 在注册表中搜索
ctx7 skills suggest                   # 基于项目依赖自动建议
ctx7 skills list                      # 列出已安装的技能
ctx7 skills remove <name>             # 卸载技能
ctx7 skills generate                  # 使用 AI 生成自定义技能（需要登录）

# 设置
ctx7 setup                            # 配置 Context7 MCP（交互式）
ctx7 login                            # 登录以获得更高的速率限制 + 技能生成
ctx7 whoami                           # 检查当前登录状态
```

大多数命令无需登录。例外：`skills generate` 总是需要登录；`ctx7 setup` 除非传递 `--api-key` 或 `--oauth`，否则需要登录。登录还可以解锁文档命令的更高速率限制。

通过环境变量设置 API 密钥以完全跳过交互式登录：

```bash
export CONTEXT7_API_KEY=your_key
```

## 常见错误

- 库 ID 需要一个 `/` 前缀 — `/facebook/react` 而不是 `facebook/react`
- 始终先运行 `ctx7 library` — 没有有效的 ID，`ctx7 docs react "hooks"` 会失败
- 技能的仓库格式是 `/owner/repo` — 例如，`ctx7 skills install /anthropics/skills`
- `skills generate` 需要登录 — 先运行 `ctx7 login`
