# Supabase

## 核心原则

**1. Supabase 经常变更 — 实施前请对照变更日志和当前文档进行验证。**
不要依赖训练数据来验证 Supabase 功能。函数签名、config.toml 配置和 API 约定在不同版本之间会发生变化。

首先，获取 `https://supabase.com/changelog.md`（一个轻量级的摘要索引——不是重量级拉取），扫描与您的任务相关的 `breaking-change` 标签，并遵循适用于这些标签的链接页面。然后，使用下文提到的文档访问方法查找相关主题。

**2. 验证您的工作。**
在实施任何修复后，运行测试查询以确认更改是否生效。没有验证的修复是不完整的。

**3. 从错误中恢复，不要循环。**
如果一种方法在尝试 2-3 次后失败，请停止并重新考虑。尝试不同的方法，检查文档，仔细检查错误，并在可用时查看相关日志。Supabase 问题并不总是通过重试相同的命令来解决，答案也不一定在日志中，但在继续操作之前，日志通常值得检查。

**4. 将表暴露给数据 API：** 根据 [数据 API 设置](https://supabase.com/dashboard/project/<ref>/integrations/data_api/settings)，新创建的表可能不会自动通过数据（REST）API 暴露。如果是这种情况，`anon` 和 `authenticated` 角色需要被明确授予访问权限。

> 注意，这与 RLS 是分开的，RLS 控制一旦表可访问时哪些 _行_ 是可见的，而不是表是否可访问。

当用户报告 SQL 创建的表意外无法访问时，请检查他们的数据 API 设置以及是否通过显式的 `GRANT` SQL 授予了角色访问权限。在授予公共 (`anon`/`authenticated`) 访问权限时，始终启用 RLS。有关完整设置工作流程，请参阅 [将表暴露给数据 API](https://supabase.com/docs/guides/api/securing-your-api.md)。

**5. 暴露模式中的 RLS。**
在所有暴露模式中的每个表上启用 RLS，这包括默认的 `public` 模式。在 Supabase 中，这是至关重要的，因为暴露模式中的表可以通过数据 API 在 `anon`/`authenticated` 角色具有访问权限时被访问（参见 [将表暴露给数据 API](https://supabase.com/docs/guides/api/securing-your-api.md)）。对于私有模式，请优先使用 RLS 作为纵深防御。启用 RLS 后，创建与实际访问模型匹配的策略，而不是将每个表默认设置为相同的 `auth.uid()` 模式。

**6. 安全检查清单。**
在处理任何触及认证、RLS、视图、存储或用户数据的 Supabase 任务时，请运行此检查清单。这些是 Supabase 特有的安全陷阱，会默默创建漏洞：

- **认证和会话安全**
  - **永远不要在基于 JWT 的授权决策中使用 `user_metadata` 声明。** 在 Supabase 中，`raw_user_meta_data` 是用户可编辑的，并且可能出现在 `auth.jwt()` 中，因此它不适用于 RLS 策略或任何其他授权逻辑。将授权数据存储在 `raw_app_meta_data` / `app_metadata` 中。
  - **删除用户不会使现有访问令牌失效。** 首先注销或撤销会话，对敏感应用保持 JWT 过期时间短，并在敏感操作中验证 `session_id` 与 `auth.sessions`。
  - **如果您使用 `app_metadata` 或 `auth.jwt()` 进行授权，请记住 JWT 声明并不总是新鲜的，直到用户的令牌被刷新。**

- **API 密钥和客户端暴露**
  - **永远不要在公共客户端中暴露 `service_role` 或密钥。** 前端代码优先使用可发布密钥。遗留的 `anon` 密钥仅用于兼容性。在 Next.js 中，任何 `NEXT_PUBLIC_` 环境变量都会发送到浏览器。

- **RLS、视图和特权数据库代码**
  - **视图默认绕过 RLS。** 在 Postgres 15 及更高版本中，使用 `CREATE VIEW ... WITH (security_invoker = true)`。在较旧版本的 Postgres 中，通过从 `anon` 和 `authenticated` 角色撤销访问或将其放入未暴露模式来保护您的视图。
  - **UPDATE 需要一个 SELECT 策略。** 在 Postgres RLS 中，UPDATE 需要先选择行。如果没有 SELECT 策略，更新会默默返回 0 行——没有错误，只是没有变化。
  - **`auth.role()` 已弃用——请使用 `TO` 子句代替。** Supabase 已弃用 `auth.role()`，改为在策略上直接指定目标角色，使用 `TO authenticated` 或 `TO anon`。除了弃用之外，`auth.role() = 'authenticated'` 在启用匿名登录时会默默失效，因为匿名用户携带 `authenticated` Postgres 角色，无论用户是否真正登录，都会通过检查。
    ```sql
    -- 已弃用（不要使用）
    create policy "example" on table_name for select
    using ( auth.role() = 'authenticated' );
    ```
  - **仅 `TO authenticated` 是认证而非授权 (BOLA / IDOR)。** 使用 `TO authenticated` 仅检查角色——它不会限制用户可以访问哪些行。正确的模式是将 `TO authenticated` 与 `USING` 中的所有权谓词结合：
    ```sql
    create policy "example" on table_name for select
    to authenticated
    using ( (select auth.uid()) = user_id );
    ```
  - **UPDATE 策略需要 `USING` 和 `WITH CHECK`。** 没有 `WITH CHECK`，用户可以将行的 `user_id` 重新分配给其他用户：
    ```sql
    create policy "example" on table_name for update
    to authenticated
    using ( (select auth.uid()) = user_id )
    with check ( (select auth.uid()) = user_id );
    ```
  - **`SECURITY DEFINER` 函数绕过 RLS。** `SECURITY DEFINER` 函数以其创建者的权限运行——通常是具有 `bypassrls` 的角色（例如 `postgres`）。永远不要添加 `SECURITY DEFINER` 来解决权限错误；它默默移除了访问控制而没有修复根本原因。优先使用 `SECURITY INVOKER`。
  - **`public` 中的 `SECURITY DEFINER` 函数对所有角色都可调用。** Postgres 默认为每个新函数向 `PUBLIC` 授予 `EXECUTE`，因此 `public` 中的任何 `SECURITY DEFINER` 函数都是可被 `anon` 和 `authenticated`（它们继承自 `PUBLIC`）调用的公共 API 端点，无需任何额外的授权。当 `SECURITY DEFINER` 真正需要时（例如，在内部查找表中绕过 RLS），请将函数保存在非暴露模式中，始终在函数体中包含 `auth.uid()` 检查，并在做出更改后运行 `supabase db advisors`。

- **存储访问控制**
  - **存储更新需要 INSERT + SELECT + UPDATE。** 仅授予 INSERT 允许新上传，但文件替换（更新）会默默失败。您需要所有三个。

- **依赖项和供应链安全**
  - **安装 Supabase 包（`supabase-js`、`@supabase/ssr`、`supabase-py` 等）时，始终固定包版本并提交锁文件**。有关完整检查清单，请参阅 [npm 安全指南](https://supabase.com/docs/guides/security/npm-security.md)。

对于上述未涵盖的任何安全问题，请获取 Supabase 产品安全索引：`https://supabase.com/docs/guides/security/product-security.md`

## Supabase CLI

始终通过 `--help` 发现命令——永远不要猜测。CLI 结构在不同版本之间会发生变化。

```bash
supabase --help                    # 所有顶级命令
supabase <group> --help            # 子命令（例如，supabase db --help）
supabase <group> <command> --help  # 特定命令的标志
```

**Supabase CLI 已知的陷阱：**

- `supabase db query` 需要 **CLI v2.79.0+** → 使用 MCP `execute_sql` 或 `psql` 作为备用
- `supabase db advisors` 需要 **CLI v2.81.3+** → 使用 MCP `get_advisors` 作为备用
- 在命令式迁移项目中，首先使用 `supabase migration new <name>` 创建新的手写迁移文件。永远不要凭空发明迁移文件名或依赖记忆来预期格式。声明式模式项目从 `supabase/schemas/` 生成迁移；参见下文“提交模式更改”。

**版本检查和升级：** 运行 `supabase --version` 进行检查。有关 CLI 变更日志和特定版本的功能，请参阅 [CLI 文档](https://supabase.com/docs/reference/cli/introduction) 或 [GitHub 发布](https://github.com/supabase/cli/releases)。

## Supabase MCP Server

有关设置说明、服务器 URL 和配置，请参阅 [MCP 设置指南](https://supabase.com/docs/guides/getting-started/mcp)。

**故障排除连接问题** — 按顺序执行以下步骤：

1. **检查服务器是否可达：**
   `curl -so /dev/null -w "%{http_code}" https://mcp.supabase.com/mcp`
   预期 `401`（无令牌），表示服务器已启动。超时或“连接拒绝”表示可能已关闭。

2. **检查 `.mcp.json` 配置：**
   验证项目根目录是否有一个有效的 `.mcp.json`，其中包含正确的服务器 URL。如果缺失，请创建一个指向 `https://mcp.supabase.com/mcp` 的文件。

3. **认证 MCP 服务器：**
   如果服务器可达且 `.mcp.json` 正确，但工具不可见，用户需要认证。Supabase MCP 服务器使用 OAuth 2.1——告诉用户在他们的代理中触发认证流程，在浏览器中完成它，并重新加载会话。

## Supabase 文档

在实施任何 Supabase 功能之前，找到相关文档。按优先顺序使用以下方法：

1. **MCP `search_docs` 工具**（首选——直接返回相关片段）
2. **获取文档页面作为 markdown**——任何文档页面都可以通过将 `.md` 添加到 URL 路径来获取。
3. **在您不知道要查看哪个页面时，通过 Web 搜索 Supabase 特定主题。**

## 提交和提交模式更改

首先决定项目使用哪种模式工作流程。

### 选项 A：声明式模式

当 `supabase/schemas/` 存在或 `config.toml` 设置 `schema_paths` 时使用此选项。编辑这些文件中的所需模式状态，然后生成并审查迁移。不要从手写迁移开始。有关详细信息，请参阅 [声明式数据库模式指南](https://supabase.com/docs/guides/local-development/declarative-database-schemas)。

### 选项 B：命令式迁移

当项目不使用声明式模式时使用此选项。

**要执行模式更改，请使用 `execute_sql`（MCP）或 `supabase db query`（CLI）。** 这些直接在数据库上运行 SQL，不会创建迁移历史记录条目，因此您可以自由迭代，并在准备好时生成干净的迁移。

**绝对不要使用 `apply_migration` 来更改本地数据库模式**——它在每次调用时都会写入迁移历史记录条目，这意味着您无法迭代，并且 `supabase db diff` / `supabase db pull` 将产生空或冲突的差异。如果您使用它，您将被迫接受第一次尝试传递的 SQL。

**当准备好提交**您的更改到迁移文件时：

1. **运行顾问** → `supabase db advisors`（CLI v2.81.3+）或 MCP `get_advisors`。修复任何问题。
2. **如果您的更改涉及视图、函数、触发器或存储，请审查上述安全检查清单。**
3. **生成迁移** → `supabase db pull <描述性名称> --local --yes`
4. **验证** → `supabase migration list --local`

## 调试

当您在 Supabase 相关请求中遇到错误时，例如 Supabase REST API、Postgres 数据库或 PostgREST 的错误代码、空结果、意外被 RLS 阻止，或来自 Supabase 服务（如认证、实时、边缘函数或存储）的错误，您**必须**在诊断或提出修复之前获取 Supabase 的 [监控和调试](https://supabase.com/docs/guides/monitoring-and-debugging.md) 文档，而不是依赖记忆。相同的文档还涵盖了性能优化，例如慢查询和缺失索引。

## 参考指南

- **技能反馈** → [references/skill-feedback.md](references/skill-feedback.md)
  **当**用户报告此技能提供了不正确的指导或缺少信息时，**必须**阅读。
