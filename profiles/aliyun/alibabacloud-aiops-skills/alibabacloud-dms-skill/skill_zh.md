# 阿里云 DMS 数据库读写

通过阿里云 DMS OpenAPI 搜索目标数据库并执行 SQL 查询和数据修改。

## 场景描述

该技能实现以下工作流程：

1. **搜索目标数据库** — 通过关键词搜索数据库以获取数据库 ID
2. **执行 SQL 查询** — 在目标数据库上执行 SQL 语句

### 架构

```
用户请求 → 搜索数据库 → 获取数据库 ID → 执行 SQL → 返回结果
```

## 前置条件

### AI-Mode 生命周期（必须按顺序执行）

该技能必须在 AI-Mode 会话中运行。将以下五个步骤视为严格的生命周期——不要跳过、重新排序或混合设置步骤与命令执行：

```
1. aliyun configure ai-mode enable                                              # 启用 AI-Mode
2. aliyun configure ai-mode set-user-agent AlibabaCloud-Agent-Skills/alibabacloud-dms-skill   # 注册技能 User-Agent
3. aliyun configure set --auto-plugin-install true && aliyun plugin update      # 插件更新
4. <通过 ./scripts/*.sh 执行 DMS 命令>                                    # 执行命令
5. aliyun configure ai-mode disable                                             # 禁用 AI-Mode（清理）
```

步骤 1–3 属于设置（本节）。步骤 4 由 [核心工作流](#core-workflow) 覆盖。步骤 5 由 [清理](#cleanup) 覆盖。

### 预检查

> **预检查 0：要求阿里云 CLI >= 3.3.3**
> 运行 `aliyun version` 以验证 >= 3.3.3。如果未安装或版本过低，
> 运行 `curl -fsSL https://aliyuncli.alicdn.com/setup.sh | bash` 以安装/更新，
> 或参阅 `references/cli-installation-guide.md` 获取安装说明。

> **预检查 1：启用 AI-Mode**
> [必须] 在任何其他配置或命令之前运行 `aliyun configure ai-mode enable` 以启用 AI-Mode。
> 这会激活下游 OpenAPI 服务使用的 AI-Mode 会话，以识别代理发出的流量。

> **预检查 2：在 AI-Mode 下注册技能 User-Agent**
> [必须] 运行 `aliyun configure ai-mode set-user-agent AlibabaCloud-Agent-Skills/alibabacloud-dms-skill`
> 以将此技能的标识符注册为当前会话的 AI-Mode User-Agent。
> 立即运行此命令，并在 `ai-mode enable` 之后、任何插件更新或 DMS 命令之前。

> **预检查 3：要求阿里云 CLI 插件更新**
> [必须] 运行 `aliyun configure set --auto-plugin-install true` 以启用自动插件安装。
> [必须] 运行 `aliyun plugin update` 以确保任何现有插件始终保持最新。
> 插件更新必须在 AI-Mode 启用和 User-Agent 注册之后发生，以便插件管理器本身报告正确的标识符。

- 阿里云 CLI >= 3.3.3
- jq（用于 JSON 解析）：`brew install jq`
- 通过 `aliyun configure` 配置的凭证

> **预检查 4：要求阿里云凭证**
>
> **安全规则：**
> - **绝不**读取、回显或打印 AK/SK 值（例如，`echo $ALIBABA_CLOUD_ACCESS_KEY_ID` 是禁止的）
> - **绝不**在对话或命令行中直接要求用户输入 AK/SK
> - **绝不**使用 `aliyun configure set` 与字面凭证值
> - **仅**使用 `aliyun configure list` 检查凭证状态
>
> ```bash
> aliyun configure list
> ```
> 检查输出以查看有效的配置文件（AK、STS 或 OAuth 身份）。
>
> **如果不存在有效的配置文件，请在此处停止。**
> 1. 从 [阿里云控制台](https://ram.console.aliyun.com/manage/ak) 获取凭证
> 2. 在此会话**外部**配置凭证（通过终端中的 `aliyun configure` 或 shell 配置文件中的环境变量）
> 3. 在 `aliyun configure list` 显示有效配置文件后重新运行

**[必须] 每个命令的 CLI User-Agent** — 除了在预检查 2 中注册的 AI-Mode User-Agent，
步骤 4 中的每个 `aliyun` CLI 命令调用**必须**也包含：
`--user-agent AlibabaCloud-Agent-Skills/alibabacloud-dms-skill`
每个命令标志和 AI-Mode 会话级别的设置是互补的——两者都必须存在，以便即使 AI-Mode 会话过期，也会在每次请求中发送标识符。

## RAM 权限

> **[必须] RAM 权限预检查：** 在执行之前，验证当前用户是否具有以下 RAM 权限。
> 参见 `references/ram-policies.md` 获取完整的权限列表。

## 参数确认

> **重要提示：参数确认** — 在执行任何命令或 API 调用之前，
> 所有用户可自定义的参数（例如，数据库关键词、SQL 语句、db-id 等）
> **必须**与用户确认。不要假设或使用默认值，除非获得明确的用户批准。

| 参数 | 必填/可选 | 描述 | 默认 |
|-----------|------------------|-------------|---------|
| keyword | 必填 | 数据库搜索关键词（1-128 个字符，字母数字） | - |
| db-id | 必填 | 数据库 ID（正整数，从搜索中获取） | - |
| sql | 必填 | 要执行的 SQL 语句（1-10000 个字符） | - |
| logic | 可选 | 是否使用逻辑数据库模式 | false |
| force | 可选 | 确认写操作（INSERT/UPDATE/DELETE） | false |
| dry-run | 可选 | 预览写操作而不执行 | false |

## 核心工作流

### 任务 1：搜索目标数据库

通过关键词搜索数据库以获取数据库 ID：

```bash
./scripts/search_database.sh <keyword> --json
```

示例：

```bash
# 搜索包含 "mydb" 的数据库
./scripts/search_database.sh mydb --json
```

输出包括 `database_id`、`schema_name`、`db_type`、`host`、`port` 等。

### 任务 2：执行 SQL 查询

使用上一步获得的数据库 ID 执行 SQL：

```bash
./scripts/execute_query.sh --db-id <database_id> --sql "<SQL_statement>"
```

#### 写操作保护

对于写操作（INSERT/UPDATE/DELETE），脚本实现了保护性预检查：

| 参数 | 描述 |
|-----------|-------------|
| `--force` | 确认并执行写操作 |
| `--dry-run` | 预览写操作而不执行 |

**DDL 操作（DROP/TRUNCATE/ALTER/RENAME）完全被阻止** — 这些必须通过 DMS 控制台执行。

示例：

```bash
# 读取操作（无需确认）
./scripts/execute_query.sh --db-id 78059000 --sql "SHOW TABLES"
./scripts/execute_query.sh --db-id 78059000 --sql "SELECT * FROM users LIMIT 10" --json

# 写操作 - 首先预览（推荐）
./scripts/execute_query.sh --db-id 78059000 --sql "INSERT INTO users (name) VALUES ('test')" --dry-run

# 写操作 - 带确认执行
./scripts/execute_query.sh --db-id 78059000 --sql "INSERT INTO users (name) VALUES ('test')" --force
./scripts/execute_query.sh --db-id 78059000 --sql "UPDATE users SET name='test' WHERE id=1" --force
./scripts/execute_query.sh --db-id 78059000 --sql "DELETE FROM users WHERE id=1" --force

# 逻辑数据库模式
./scripts/execute_query.sh --db-id 78059000 --sql "SELECT 1" --logic
```

### 完整示例

```bash
# 1. 搜索数据库（假设搜索 "order")
./scripts/search_database.sh order --json
# 示例输出：
# [{"DatabaseId": "78059000", "SchemaName": "order_db", ...}]

# 2. 执行查询
./scripts/execute_query.sh --db-id 78059000 --sql "SELECT COUNT(*) FROM orders"
```

## 成功验证

执行 SQL 后，检查返回的结果：

1. 脚本返回码为 0
2. 输出包含查询结果（列名和行数据）
3. 无错误消息

```bash
# 验证查询成功
./scripts/execute_query.sh --db-id <db-id> --sql "SELECT 1" --json
# 预期输出：[{"Success": true, "RowCount": 1, ...}]
```

## 清理

该技能执行读写操作，但不会创建持久资源，因此无需释放数据库资源。

然而，AI-Mode 生命周期需要明确的拆除步骤：

> **[必须] 在所有任务完成后禁用 AI-Mode**
> 运行 `aliyun configure ai-mode disable`，在此技能会话中的所有 DMS 命令（成功或失败）完成后
> 这会终止 AI-Mode 会话，并防止注册的
> `AlibabaCloud-Agent-Skills/alibabacloud-dms-skill` User-Agent 泄露到后续无关的 CLI 使用中。

```bash
aliyun configure ai-mode disable
```

## 写操作安全

| 操作类型 | 行为 |
|---------------|----------|
| SELECT / SHOW / DESC | 直接执行 |
| INSERT / UPDATE / DELETE | 需要 `--force` 或 `--dry-run` |
| DROP / TRUNCATE / ALTER / RENAME | **阻止** — 使用 DMS 控制台 |

## 可用脚本

| 脚本 | 描述 |
|--------|-------------|
| `scripts/search_database.sh` | 通过关键词搜索数据库 |
| `scripts/execute_query.sh` | 执行 SQL 查询 |

> **注意：** 脚本使用通过 `aliyun configure` 配置的 aliyun-cli 凭证。

## 最佳实践

1. **确认数据库** — 在执行 SQL 之前验证目标数据库
2. **使用 --json 参数** — 促进对输出的程序化处理
3. **预览写操作** — 始终先使用 `--dry-run` 进行 INSERT/UPDATE/DELETE
4. **显式确认** — 仅在审查预览后使用 `--force`
5. **避免 DDL 操作** — DROP/TRUNCATE/ALTER/RENAME 被阻止；使用 DMS 控制台代替

## 参考链接

| 文档 | 描述 |
|----------|-------------|
| [references/cli-installation-guide.md](references/cli-installation-guide.md) | CLI 安装指南 |
| [references/ram-policies.md](references/ram-policies.md) | RAM 权限策略 |
| [references/related-apis.md](references/related-apis.md) | 相关 API 列表 |
| [references/acceptance-criteria.md](references/acceptance-criteria.md) | 接受标准 |
