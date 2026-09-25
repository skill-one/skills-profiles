# 使用 clickhousectl 管理 ClickHouse

`clickhousectl` 可在两种环境中管理 ClickHouse：

- **本地** — ClickHouse 安装并运行在用户机器上，用于开发。
- **云端** — 管理的 ClickHouse Cloud 服务，用于生产：完全托管、自动扩展、备份和升级。

此文件会引导至正确的参考文档。分步工作流程位于 `ref/local.md` 和 `ref/cloud.md` 中 — 在执行命令前，请阅读与用户情况匹配的文档。

## 应使用哪个参考文档

| 用户希望... | 阅读 |
|------------|------|
| 使用 ClickHouse 构建应用程序，在本地开发或原型设计，无需云账户 | [ref/local.md](ref/local.md) |
| 进入生产环境，托管管理的 ClickHouse，或明确使用 ClickHouse Cloud | [ref/cloud.md](ref/cloud.md) |
| 操作现有的云服务（模式、用户、对其的查询） | [ref/cloud.md](ref/cloud.md) |
| 现在本地开发，稍后部署到生产环境 | 从 [ref/local.md](ref/local.md) 开始；当准备进入生产环境时，它会指向 [ref/cloud.md](ref/cloud.md) |

如果确实存在歧义（例如“为我的应用程序设置 ClickHouse”），对于开发任务默认使用本地，并在云端创建任何内容前进行询问 — 云服务需要付费。

## 前置条件（两种工作流程）

检查 `clickhousectl` 是否已安装：

```bash
which clickhousectl
```

如果没有找到，请安装它：

```bash
curl -fsSL https://clickhouse.com/cli | sh
```

这将安装到 `~/.local/bin/clickhousectl`（带有 `chctl` 别名）。如果命令仍然找不到，建议 `export PATH="$HOME/.local/bin:$PATH"` 或使用新终端。

所有命令都接受 `--json` 以获取机器可读的输出。退出码遵循 `gh` 规范：0 表示成功，1 表示错误，2 表示取消，4 表示需要认证。

## 相关

- 在设计模式时，请参考 `clickhouse-best-practices` 技能，了解 ORDER BY 选择、数据类型和分区。
- 对于 Postgres（本地开发或管理的 ClickHouse Cloud Postgres），请使用 `infra-postgres` 技能。
