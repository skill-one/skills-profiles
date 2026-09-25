# 部署到 ClickHouse Cloud

本指南将指导您使用 `clickhousectl` 部署到 ClickHouse Cloud。它涵盖了账户设置、CLI 身份验证、服务创建、模式迁移以及连接您的应用程序。请按顺序执行以下步骤。

## 何时适用

当用户希望执行以下操作时，请使用此指南：
- 将 ClickHouse 应用程序部署到生产环境
- 将 ClickHouse 作为托管云服务进行托管
- 从本地 ClickHouse 设置迁移到 ClickHouse Cloud
- 创建 ClickHouse Cloud 服务
- 首次设置 ClickHouse Cloud

---

## 第 1 步：注册 ClickHouse Cloud

在使用任何云命令之前，用户需要拥有一个 ClickHouse Cloud 账户。

**询问用户：** "您是否已经拥有 ClickHouse Cloud 账户？"

**如果他们没有账户**，请解释：

> ClickHouse Cloud 是一个完全托管的云服务，它为您运行 ClickHouse — 无需维护基础设施，包含自动扩展、备份和升级。提供免费试用，您无需信用卡即可开始使用。
>
> 要创建账户，请访问：**https://clickhouse.cloud**
>
> 使用您的电子邮件、Google 或 GitHub 账户进行注册。进入控制台后，请告诉我，我们将继续下一步。

**等待用户确认**他们已经注册或已经拥有账户，然后再继续。

---

## 第 2 步：CLI 身份验证

首先，确保已安装 `clickhousectl`。使用以下命令检查：

```bash
which clickhousectl
```

如果未找到，请安装它：

```bash
curl -fsSL https://clickhouse.com/cli | sh
```

使用 ClickHouse Cloud API 密钥对 `clickhousectl` 进行身份验证。

### 创建 API 密钥

指导用户在 ClickHouse Cloud 控制台中创建一个 API 密钥：

> 1. 点击左侧边栏中的 **齿轮图标**（设置）
> 2. 转到 **API 密钥**
> 3. 点击 **创建 API 密钥**
> 4. 给它命名（例如，"clickhousectl"）
> 5. 为密钥选择 **管理员** 角色。需要管理员权限，因为 `cloud service query` 在首次使用时自动配置每个服务的查询端点 API 密钥，这需要创建密钥的权限。作用域为开发者的密钥可以管理服务，但可能无法完成自动配置步骤。
> 6. 点击 **生成 API 密钥**
> 7. **复制密钥 ID 和密钥密钥** — 密钥密钥只显示一次

### 使用密钥对 clickhousectl 进行身份验证

请用户 **在同一工作目录中打开一个新的终端标签页**，并在其中运行登录命令，使用他们的密钥 ID 和密钥密钥 — 这样可以将密钥密钥保持在聊天会话之外。告诉他们完成后回来通知您。

```bash
clickhousectl cloud login --api-key <key> --api-secret <secret>
```

`--api-key` 和 `--api-secret` 都是必需的 — 如果用户只有一个，请告诉他们两个都需要。

---

**验证身份验证是否成功：**

```bash
clickhousectl cloud org list
```

这应该返回用户的组织。

---

## 第 3 步：创建云服务

创建一个新的 ClickHouse Cloud 服务：

```bash
clickhousectl cloud service create --name <service-name>
```

从输出中，将 HTTPS 主机和端口添加到 `.env` 作为 `CLICKHOUSE_HOST` 和 `CLICKHOUSE_PORT`。确保 `.env` 被忽略。

然后轮询直到服务状态为 `running`：

```bash
clickhousectl cloud service get <service-id>
```

---

## 第 4 步：迁移模式

如果用户有本地表定义（例如，在使用 `clickhousectl-local-dev` 技能时），请将它们迁移到云服务。

使用 `cloud service query` 通过 HTTP 对云服务运行 SQL。只需传递服务名称（或 `--id`）。

**从 `clickhouse/tables/` 读取本地模式文件**，并将每个文件应用到云服务：

```bash
clickhousectl cloud service query --name <service-name> \
  --queries-file clickhouse/tables/<table>.sql
```

按依赖顺序应用它们 — 被物化视图引用的表应首先创建。

**如果存在，也应用物化视图**：

```bash
clickhousectl cloud service query --name <service-name> \
  --queries-file clickhouse/materialized_views/<view>.sql
```

要针对特定数据库，请传递 `--database <name>`。

---

## 第 5 步：验证部署

连接到云服务并确认表存在：

```bash
clickhousectl cloud service query --name <service-name> --query "SHOW TABLES"
```

运行测试查询以确认模式正确：

```bash
clickhousectl cloud service query --name <service-name> --query "DESCRIBE TABLE <table-name>"
```

---

## 第 6 步：为应用程序创建专用用户

`default` 用户拥有完全的管理权限，不应由应用程序使用。创建一个作用域为第 4 步中部署的模式专用用户。

生成一个强随机密码，并在创建用户**之前**将凭证追加到 `.env`，以便即使后续步骤失败，密码也能被持久化：

```bash
PASSWORD=$(openssl rand -base64 32)
echo "CLICKHOUSE_USER=app_user" >> .env
echo "CLICKHOUSE_PASSWORD=$PASSWORD" >> .env
```

然后创建用户并授予应用程序所需的最小权限。将 `<database>` 替换为模式所在的数据库（通常是 `default`）：

```bash
clickhousectl cloud service query --name <service-name> --query \
  "CREATE USER app_user IDENTIFIED BY '$PASSWORD'"

clickhousectl cloud service query --name <service-name> --query \
  "GRANT SELECT, INSERT ON <database>.* TO app_user"
```

根据应用程序调整授权：
- 只读应用程序 → 删除 `INSERT`
- 需要创建/删除自己的表 → 还授予 `CREATE TABLE, DROP TABLE` 在数据库上（但最好作为管理员用户运行迁移）
- 多个数据库 → 重复每个数据库的 `GRANT`，或按表作用域 `ON <database>.<table>`

验证用户存在并具有预期的授权：

```bash
clickhousectl cloud service query --name <service-name> --query "SHOW GRANTS FOR app_user"
```

ClickHouse 无法以后显示密码，因此如果 `.env` 丢失，用户必须通过 `ALTER USER app_user IDENTIFIED BY '<new>'` 重置密码。

---

现在，应用程序可以使用 `.env` 中的凭证连接到 ClickHouse Cloud。
