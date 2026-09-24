# Supabase

## 核心原则

**1. Supabase 变化频繁 —— 实现前务必对照 changelog 和最新文档进行验证。**
不要依赖训练数据来获取 Supabase 的功能。Function 签名、`config.toml` 设置和 API 约定在不同版本间会发生变化。

首先获取 `https://supabase.com/changelog.md`（一份轻量级摘要索引 —— 不是重型拉取），扫描与你的任务相关的 `breaking-change` 标签，并跟进其中适用的链接页面。然后使用以下方法查询相关主题的文档。

**2. 验证你的工作。**
实现任何修复后，运行测试查询以确认更改生效。没有验证的修复是不完整的。

**3. 从错误中恢复，而非循环重试。**
如果在 2-3 次尝试后某种方法失败，请停止并重新考虑。尝试不同的方法、查阅文档、更仔细地检查错误，并在有可用日志时检查相关日志。Supabase 的问题并非总是通过重试相同的命令即可解决，答案也并非总是在日志中，但继续操作前检查日志通常是值得的。

**4. 将表暴露给 Data API：** 根据用户的 [Data API 设置](https://supabase.com/dashboard/project/<ref>/integrations/data_api/settings)，新创建的表可能不会自动通过 Data（REST）API 暴露。在这种情况下，需要显式授予 `anon` 和 `authenticated` 角色访问权限。

> 请注意，这与其他的 RLS 不同，RLS 控制的是表可访问后可见的_行_，而非表本身是否可访问。

当用户报告 SQL 创建的表意外不可访问时，检查其 Data API 设置以及角色是否通过显式 `GRANT` SQL 获得了访问权限。授予公共（`anon`/`authenticated`）访问时，始终也要启用 RLS。完整的配置流程请参阅 [将表暴露给 Data API](https://supabase.com/docs/guides/api/securing-your-api.md)。

**5. 暴露模式中的 RLS。**
在所有暴露模式中的每个表上都启用 RLS，`public` 模式默认为此。在 Supabase 中，这至关重要，因为暴露模式中的表在 `anon`/`authenticated` 角色有访问权限时，可通过 Data API 访问（请参阅 [将表暴露给 Data API](https://supabase.com/docs/guides/api/securing-your-api.md)）。对于私有模式，优先使用 RLS 作为纵深防御手段。启用 RLS 后，创建与实际操作模型匹配的策略，而不是默认将所有表设为相同的 `auth.uid()` 模式。

**6. 安全清单。**
在处理任何涉及认证、RLS、视图、存储或用户数据的 Supabase 任务时，请运行此清单。这些都是 Supabase 特有的安全陷阱，会静默地造成漏洞：

- **认证与会话安全**
  - **切勿在基于 JWT 的授权决策中使用 `user_metadata` 声明。** 在 Supabase 中，`raw_user_meta_data` 可由用户编辑，并可能出现在 `auth.jwt()` 中，因此不适合用于 RLS 策略或任何其他授权逻辑。应改用 `raw_app_meta_data` / `app_metadata` 存储授权数据。
  - **删除用户不会使现有访问令牌失效。** 请先注销或撤销会话，对敏感应用保持较短的 JWT 过期时间，并在严格保障场景下，对敏感操作将 `session_id` 与 `auth.sessions` 进行验证。
  - **如果使用 `app_metadata` 或 `auth.jwt()` 进行授权，请记住 JWT 声明不一定在用户刷新令牌时立即更新。**

- **API 密钥与客户端暴露**
  - **切勿在公共客户端中暴露 `service_role` 或密钥。** 优先为前端代码使用可发布的密钥。旧版 `anon` 密钥仅用于兼容。在 Next.js 中，任何 `NEXT_PUBLIC_` 环境变量都会发送给浏览器。

- **RLS、视图与特权数据库代码**
  - **视图默认会绕过 RLS。** 在 Postgres 15 及以上版本中，使用 `CREATE VIEW ... WITH (security_invoker = true)`。在旧版 Postgres 版本中，通过撤销 `anon` 和 `authenticated` 角色的访问权限，或将视图置于未暴露的模式中来保护视图。
  - **UPDATE 需要 SELECT 策略。** 在 Postgres RLS 中，UPDATE 必须先 SELECT 该行。如果没有 SELECT 策略，更新会静默返回 0 行 —— 没有错误，只是没有变更。
  - **`auth.role()` 已被废弃 —— 请改用 `TO` 子句。** Supabase 已废弃 `auth.role()`，改为在策略中使用 `TO authenticated` 或 `TO anon` 直接指定目标角色。除废弃外，在启用匿名登录时，`auth.role() = 'authenticated'` 会静默失败，因为匿名用户携带 `authenticated` Postgres 角色，无论用户是否真实登录，都能通过该检查。
    ```sql
    -- 已废弃（请勿使用）
    create policy "example" on table_name for select
    using ( auth.role() = 'authenticated' );
    ```
  - **仅用 `TO authenticated` 等于认证而非授权（BOLA / IDOR）。** 使用 `TO authenticated` 只检查角色 —— 不会限制用户可访问的行。正确的模式是将 `TO authenticated` 与 `USING` 中的所有权谓词结合：
    ```sql
    create policy "example" on table_name for select
    to authenticated
    using ( (select auth.uid()) = user_id );
    ```
  - **UPDATE 策略需要同时包含 `USING` 和 `WITH CHECK`。** 没有 `WITH CHECK` 时，用户可以将行的 `user_id` 重新分配给其他用户：
    ```sql
    create policy "example" on table_name for update
    to authenticated
    using ( (select auth.uid()) = user_id )
    with check ( (select auth.uid()) = user_id );
    ```
  - **`SECURITY DEFINER` 函数会绕过 RLS。** `SECURITY DEFINER` 函数以创建者的权限运行 —— 通常是拥有 `bypassrls` 的角色（例如 `postgres`）。切勿在解决权限错误时添加 `SECURITY DEFINER`；这会在不修复根本原因的情况下静默移除访问控制。请优先使用 `SECURITY INVOKER`。
  - **`public` 模式中的 `SECURITY DEFINER` 函数可被所有角色调用。** Postgres 默认会为每个新函数授予 `PUBLIC` 的 `EXECUTE`，因此 `public` 中的任何 `SECURITY DEFINER` 函数都是可被 `anon` 和 `authenticated`（它们继承自 `PUBLIC`）调用的公开 API 端点，无需额外授予。当确实需要 `SECURITY DEFINER`（例如在内置查找表上绕过 RLS）时，请将函数放在非暴露模式中，始终在函数体内包含 `auth.uid()` 检查，并在更改后运行 `supabase db advisors`。

- **存储访问控制**
  - **存储 upsert 需要 INSERT + SELECT + UPDATE。** 仅授予 INSERT 允许新上传，但文件替换（upsert）会静默失败。需要全部三项。

- **依赖与供应链安全**
  - **安装 Supabase 包（`supabase-js`、`@supabase/ssr`、`supabase-py` 等）时，始终固定包版本并提交 lockfile。** 完整清单请参阅 [npm 安全指南](https://supabase.com/docs/guides/security/npm-security.md)。

对于上述未涵盖的任何安全问题，获取 Supabase 产品安全索引：`https://supabase.com/docs/guides/security/product-security.md`

## Supabase CLI

始终通过 `--help` 发现命令 —— 切勿猜测。CLI 结构在不同版本间会发生变化。

```bash
supabase --help                    # 所有顶层命令
supabase <group> --help            # 子命令（例如 supabase db --help）
supabase <group> <command> --help  # 特定命令的标志
```

**Supabase CLI 已知问题：**

- `supabase db query` 需要 **CLI v2.79.0+** → 使用 MCP `execute_sql` 或 `psql` 作为备选方案
- `supabase db advisors` 需要 **CLI v2.81.3+** → 使用 MCP `get_advisors` 作为备选方案
- 在命令式迁移项目中，请先使用 `supabase migration new <name>` 创建新的手动编写的迁移文件。切勿虚构迁移文件名，也不应依赖记忆来获取预期格式。声明式 schema 项目从 `supabase/schemas/` 生成迁移；请参阅下方的“Schema 变更的创建与提交”。

**版本检查与升级：** 运行 `supabase --version` 进行检查。针对 CLI 的 changelog 和版本特定功能，请查阅 [CLI 文档](https://supabase.com/docs/reference/cli/introduction) 或 [GitHub releases](https://github.com/supabase/cli/releases)。

## Supabase MCP 服务器

关于设置说明、服务器 URL 和配置，请参阅 [MCP 设置指南](https://supabase.com/docs/guides/getting-started/mcp)。

**连接问题排查 —— 请按以下步骤依次操作：**

1. **检查服务器是否可达：**
   `curl -so /dev/null -w "%{http_code}" https://mcp.supabase.com/mcp`
   预期返回 `401`（无 token）表示服务器正常运行。超时或“连接被拒绝”表示服务器可能已停止运行。

2. **检查 `.mcp.json` 配置：**
   验证项目根目录下存在有效的 `.mcp.json` 且服务器 URL 正确。如果缺失，创建一个指向 `https://mcp.supabase.com/mcp` 的配置文件。

3. **认证 MCP 服务器：**
   如果服务器可达且 `.mcp.json` 正确，但工具不可见，则需要用户进行认证。Supabase MCP 服务器使用 OAuth 2.1 —— 请告知用户在代理中触发认证流程，在浏览器中完成，然后重新加载会话。

## Supabase 文档

实现任何 Supabase 功能之前，先找到相关文档。按以下优先级使用以下方法：

1. **MCP `search_docs` 工具**（首选 —— 直接返回相关代码片段）
2. **以 Markdown 格式获取文档页面** —— 任何文档页面都可以通过在 URL 路径末尾追加 `.md` 来获取。
3. **对 Supabase 特定主题进行网络搜索**，当不确定查看哪一页面时使用。

## Schema 变更的创建与提交

首先决定项目使用的哪种 schema 工作流程。

### 选项 A：声明式 schema

当存在 `supabase/schemas/` 或 `config.toml` 设置了 `schema_paths` 时使用此方式。在那些文件中编辑所需的 schema 状态，然后生成并审查迁移。不要直接手写迁移。请参阅 [声明式数据库 schema 指南](https://supabase.com/docs/guides/local-development/declarative-database-schemas)。

### 选项 B：命令式迁移

当项目不使用声明式 schema 时使用此方式。

**要创建 schema 变更，使用 MCP 的 `execute_sql` 或 CLI 的 `supabase db query`。** 这些直接在数据库上运行 SQL，不会创建迁移历史记录，因此你可以自由迭代，待准备好后再生成干净的迁移。

**不要使用 `apply_migration` 来更改本地数据库 schema** —— 每次调用都会写入迁移历史记录，这意味着无法迭代，且 `supabase db diff` / `supabase db pull` 会产生空或冲突的差异。如果使用它，将 stuck 在你首次传入的 SQL 中。

**准备将变更提交到迁移文件时：**

1. **运行建议器** → `supabase db advisors`（CLI v2.81.3+）或 MCP `get_advisors`。修复所有问题。
2. **如果变更涉及视图、函数、触发器或存储，则审查上文的安全清单。**
3. **生成迁移** → `supabase db pull <描述性名称> --local --yes`
4. **验证** → `supabase migration list --local`

## 调试

当你在 Supabase 相关请求上遇到错误，例如 Supabase REST API、Postgres 数据库或 PostgREST 的错误码、空结果、意外被 RLS 拦截，或来自 Supabase 服务（Auth、Realtime、Edge Functions、Storage）的错误时，**必须**在诊断或提出修复方案前，获取 Supabase 的 [监控与调试](https://supabase.com/docs/guides/monitoring-and-debugging.md) 文档，而非凭记忆工作。这些文档同样涵盖性能优化，如慢查询和缺失的索引。

## 参考指南

- **技能反馈** → [references/skill-feedback.md](references/skill-feedback.md)
  **必须在以下情况时阅读：** 用户报告本技能给出了错误指引或信息缺失。
