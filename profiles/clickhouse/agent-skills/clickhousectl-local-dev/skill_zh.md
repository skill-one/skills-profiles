# 本地 ClickHouse 开发环境设置

本技能将指导您使用 `clickhousectl` 设置完整的本地 ClickHouse 开发环境。请按顺序执行以下步骤。

## 何时应用

当用户需要以下功能时，请使用此技能：
- 构建需要分析数据库或特定 ClickHouse 的应用程序
- 设置本地 ClickHouse 实例用于开发
- 在其机器上安装 ClickHouse
- 创建表并开始本地查询 ClickHouse
- 原型设计或实验 ClickHouse

---

## 第 1 步：安装 clickhousectl

检查 `clickhousectl` 是否已可用：

```bash
which clickhousectl
```

如果未找到，请安装它：

```bash
curl -fsSL https://clickhouse.com/cli | sh
```

这将安装 `clickhousectl` 到 `~/.local/bin/clickhousectl` 并创建 `chctl` 别名。

**如果安装后命令仍然未找到：** 用户可能需要将 `~/.local/bin` 添加到其 PATH 或打开新的终端会话。建议：

```bash
export PATH="$HOME/.local/bin:$PATH"
```

安装完成后，可以使用 `clickhousectl skills` 安装最新的 ClickHouse Agent 技能。

---

## 第 2 步：安装 ClickHouse 并设置默认值

安装最新版本的 ClickHouse 并将其设置为系统默认版本：

```bash
clickhousectl local use latest
```

这将安装 ClickHouse，将其设置为 `clickhousectl local` 命令使用的默认版本，并将 `~/.local/bin/clickhouse` 符号链接到二进制文件，将 `clickhouse` 添加到您的 PATH（这意味着您可以直接调用 `clickhouse`，例如 `clickhouse client` 如果需要）。

当需要时，您可以使用其他版本指定符，如 `stable`、`26.4`、`26.4.2.10`。

---

## 第 3 步：初始化项目

从用户的项目根目录执行：

```bash
clickhousectl local init
```

这将创建标准的文件夹结构：

```
clickhouse/
  tables/                 # CREATE TABLE 语句
  materialized_views/     # 物化视图定义
  queries/                # 保存的查询
  seed/                   # 种子数据 / INSERT 语句
```

**注意：** 此步骤是可选的。如果用户已经有自己的 SQL 文件文件夹结构，请跳过此步骤并调整后续步骤以使用其路径。

---

## 第 4 步：启动本地服务器

```bash
clickhousectl local server start --name <name>
```

这将启动 ClickHouse 服务器到后台。

**要检查正在运行的服务器并查看其暴露的端口：**

```bash
clickhousectl local server list
```

---

## 第 5 步：创建模式

根据用户的应用程序需求，编写 CREATE TABLE SQL 文件。

**将每个表定义写入其自己的文件** 到 `clickhouse/tables/`：

```bash
# 示例：clickhouse/tables/events.sql
```

```sql
CREATE TABLE IF NOT EXISTS events (
    timestamp DateTime,
    user_id UInt32,
    event_type LowCardinality(String),
    properties String
)
ENGINE = MergeTree()
ORDER BY (event_type, timestamp)
```

在设计模式时，如果 `clickhouse-best-practices` 技能可用，请参考它以获取关于 ORDER BY 列选择、数据类型和分区的指导。

**将模式应用到正在运行的服务器：**

```bash
clickhousectl local client --name <name> --queries-file clickhouse/tables/events.sql
```

---

## 第 6 步：种子数据（可选）

如果用户需要用于开发的样本数据，请将 INSERT 语句写入 `clickhouse/seed/`：

```bash
# 示例：clickhouse/seed/events.sql
```

```sql
INSERT INTO events (timestamp, user_id, event_type, properties) VALUES
    ('2024-01-01 00:00:00', 1, 'page_view', '{"page": "/home"}'),
    ('2024-01-01 00:01:00', 2, 'click', '{"button": "signup"}');
```

**应用种子数据：**

```bash
clickhousectl local client --name <name> --queries-file clickhouse/seed/events.sql
```

---

## 第 7 步：验证设置

确认表已创建：

```bash
clickhousectl local client --name <name> --query "SHOW TABLES"
```

运行测试查询：

```bash
clickhousectl local client --name <name> --query "SELECT count() FROM events"
```

---

如果用户希望使用托管的 ClickHouse 服务，请使用 `clickhousectl-cloud-deploy` 技能帮助用户部署到 ClickHouse Cloud。
