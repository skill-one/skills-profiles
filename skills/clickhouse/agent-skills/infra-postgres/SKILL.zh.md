---
name: infra-postgres
description: 使用 clickhousectl CLI 设置和管理 Postgres——为开发运行本地 Docker 支持的 Postgres，并创建和操作 ClickHouse Cloud 上的托管 Postgres 服务（连接、TLS、运行时配置、读副本、故障转移、时间点恢复）。当用户需要为应用程序使用 Postgres 或 PostgreSQL 数据库、本地 Postgres 开发环境、psql 访问，或 ClickHouse Cloud 上的托管/生产 Postgres，或提及将本地 Postgres 迁移到生产环境时使用。也用于将现有 Postgres 数据库（Neon、Supabase、RDS、Aurora、Cloud SQL、自托管）迁移到 ClickHouse Cloud Postgres。
---

# 使用 clickhousectl 管理 Postgres

`clickhousectl` 在两种环境中管理 Postgres：

- **本地** — 用户机器上的命名、Docker 支持的 Postgres 实例，用于开发。
- **云端** — ClickHouse Cloud (beta) 中的托管 Postgres 服务，用于生产：高可用性 (HA)、读副本、时间点恢复。

本文件会根据用户情况路由到正确的参考文档。分步工作流程位于 `ref/local.md`、`ref/cloud.md` 和 `ref/migrate.md` 中 — 在运行命令前，请阅读与用户情况匹配的文档。

## 应使用哪个参考文档

| 用户希望... | 阅读 |
|----------------------|------|
| 本地开发或原型设计，对 Postgres 运行测试/CI，无需云账号 | [ref/local.md](ref/local.md) |
| 进入生产环境，托管一个托管的 Postgres，或明确使用 ClickHouse Cloud | [ref/cloud.md](ref/cloud.md) |
| 操作现有的云服务（密码、TLS、配置、副本、故障转移、恢复） | [ref/cloud.md](ref/cloud.md) |
| 将现有的 Postgres（Neon、Supabase、RDS、...）迁移到 ClickHouse Cloud Postgres | [ref/migrate.md](ref/migrate.md) |
| 现在本地开发，稍后部署到生产环境 | 从 [ref/local.md](ref/local.md) 开始；当准备进入生产环境时，它会指向 [ref/cloud.md](ref/cloud.md) |

如果确实存在歧义（例如“为我的应用设置 Postgres”），开发任务默认使用本地，并在创建云资源前进行询问 — 云服务需要付费。

## 前置条件（两种工作流程）

检查 `clickhousectl` 是否已安装：

```bash
which clickhousectl
```

如果未找到，请安装它：

```bash
curl -fsSL https://clickhouse.com/cli | sh
```

这会安装到 `~/.local/bin/clickhousectl`（带 `chctl` 别名）。如果命令仍然未找到，建议 `export PATH="$HOME/.local/bin:$PATH"` 或使用新终端。

所有命令都接受 `--json` 参数以获取机器可读的输出。退出码遵循 `gh` 规范：0 表示成功，1 表示错误，2 表示取消，4 表示需要认证。

## 相关

- 要将 Postgres 数据复制到 ClickHouse 进行分析，请参阅 ClickPipes (`clickhousectl cloud clickpipe --help`)。ClickPipes 不能针对 Postgres 服务 — 用于 Postgres 到 Postgres 迁移请使用 [ref/migrate.md](ref/migrate.md)。
- 对于 ClickHouse 本身（本地开发或 ClickHouse Cloud 服务），请使用 `infra-clickhouse` 技能。
