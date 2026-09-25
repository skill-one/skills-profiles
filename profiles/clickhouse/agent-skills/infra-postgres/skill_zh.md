# 使用 clickhousectl 管理 Postgres

`clickhousectl` 在两种环境中管理 Postgres：

- **本地** — 用户机器上的命名、Docker 支持的 Postgres 实例，用于开发。
- **云端** — ClickHouse Cloud (beta) 中的托管 Postgres 服务，用于生产：高可用性、读副本、时间点恢复。

此文件会根据情况路由到正确的参考文档。分步工作流程位于 `ref/local.md` 和 `ref/cloud.md` 中 — 在运行命令前，请阅读与用户情况匹配的文档。

## 应使用哪个参考文档

| 用户希望... | 阅读 |
|----------------------|------|
| 本地开发或原型设计，运行针对 Postgres 的测试/CI，无需云账户 | [ref/local.md](ref/local.md) |
| 进入生产环境，托管一个托管的 Postgres，或明确使用 ClickHouse Cloud | [ref/cloud.md](ref/cloud.md) |
| 操作现有的云服务（密码、TLS、配置、副本、故障转移、恢复） | [ref/cloud.md](ref/cloud.md) |
| 现在本地开发，稍后部署到生产环境 | 从 [ref/local.md](ref/local.md) 开始；当准备进入生产环境时，它会指向 [ref/cloud.md](ref/cloud.md) |

如果确实存在歧义（例如“为我的应用设置 Postgres”），对于开发任务默认使用本地，并在创建云中的任何内容前进行询问 — 云服务需要付费。

## 前置条件（两种工作流程）

检查 `clickhousectl` 是否已安装：

```bash
which clickhousectl
```

如果没有找到，请安装它：

```bash
curl -fsSL https://clickhouse.com/cli | sh
```

这将安装到 `~/.local/bin/clickhousectl`（带有 `chctl` 别名）。如果命令仍然找不到，建议 `export PATH="$HOME/.local/bin:$PATH"` 或一个新的终端。

所有命令都接受 `--json` 以生成机器可读的输出。退出代码遵循 `gh` 规范：0 表示成功，1 表示错误，2 表示取消，4 表示需要认证。

## 相关

- 要将 Postgres 数据复制到 ClickHouse 进行分析，请参阅 ClickPipes (`clickhousectl cloud clickpipe --help`)。
- 对于 ClickHouse 本身（本地开发或 ClickHouse Cloud 服务），请使用 `infra-clickhouse` 技能。
