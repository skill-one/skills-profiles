# Azure 存储服务

## 服务

| 服务 | 适用场景 | MCP 工具 | CLI |
|---------|----------|-----------|-----|
| 对象存储 | 对象、文件、备份、静态内容 | `azure__storage` | `az storage blob` |
| 文件共享 | SMB 文件共享、迁移部署 | - | `az storage file` |
| 队列存储 | 异步消息、任务队列 | - | `az storage queue` |
| 表存储 | NoSQL 键值（建议考虑 Cosmos DB） | - | `az storage table` |
| 数据湖 | 大数据分析、层级命名空间 | - | `az storage fs` |

## MCP 服务器（首选）

当已启用 Azure MCP 时：

- 使用 `azure__storage` 工具，命令为 `storage_account_list` - 列出存储账户
- 使用 `azure__storage` 工具，命令为 `storage_container_list` - 列出账户中的容器
- 使用 `azure__storage` 工具，命令为 `storage_blob_list` - 列出容器中的对象
- 使用 `azure__storage` 工具，命令为 `storage_blob_get` - 下载对象内容
- 使用 `azure__storage` 工具，命令为 `storage_blob_put` - 上传对象内容

**若未启用 Azure MCP：** 运行 `/azure:setup` 或通过 `/mcp` 启用。

## CLI 备用方案

```bash
# 列出存储账户
az storage account list --output table

# 列出容器
az storage container list --account-name ACCOUNT --output table

# 列出对象
az storage blob list --account-name ACCOUNT --container-name CONTAINER --output table

# 下载 Blob
az storage blob download --account-name ACCOUNT --container-name CONTAINER --name BLOB --file LOCAL_PATH

# 上传 Blob
az storage blob upload --account-name ACCOUNT --container-name CONTAINER --name BLOB --file LOCAL_PATH
```

## 存储账户层级

| 层级 | 适用场景 | 性能 |
|------|----------|-------------|
| 标准 | 通用用途、备份 | 毫秒级 |
| 高级 | 数据库、高 IOPS | 亚毫秒级 |

## 对象访问层级

| 层级 | 访问频率 | 成本 |
|------|---------|------|
| 热 | 频繁 | 存储成本较高，访问成本较低 |
| 温 | 低频（30 天以上） | 存储成本较低，访问成本较高 |
| 冷 | 罕见（90 天以上） | 更低 |
| 归档 | 极少（180 天以上） | 存储成本最低，需重新还原 |

## 冗余选项

| 类型 | 持久性 | 适用场景 |
|------|------------|----------|
| LRS | 11 个 9 | 开发/测试、可重建数据 |
| ZRS | 12 个 9 | 区域高可用 |
| GRS | 16 个 9 | 灾难恢复 |
| GZRS | 16 个 9 | 最佳持久性 |

## 服务详情

针对具体服务的深度文档：

- 对象存储模式与生命周期 -> [对象存储文档](https://learn.microsoft.com/azure/storage/blobs/storage-blobs-overview)
- 文件共享与 Azure File Sync -> [Azure Files 文档](https://learn.microsoft.com/azure/storage/files/storage-files-introduction)
- 队列模式与毒丸处理 -> [队列存储文档](https://learn.microsoft.com/azure/storage/queues/storage-queues-introduction)

## SDK 快速参考

使用 Azure Storage SDK 构建应用程序时，请参阅以下精简指南：

- **对象存储**：[Python](references/sdk/azure-storage-blob-py.md) | [TypeScript](references/sdk/azure-storage-blob-ts.md) | [Java](references/sdk/azure-storage-blob-java.md) | [Rust](references/sdk/azure-storage-blob-rust.md)
- **队列存储**：[Python](references/sdk/azure-storage-queue-py.md) | [TypeScript](references/sdk/azure-storage-queue-ts.md)
- **文件共享**：[Python](references/sdk/azure-storage-file-share-py.md) | [TypeScript](references/sdk/azure-storage-file-share-ts.md)
- **数据湖**：[Python](references/sdk/azure-storage-file-datalake-py.md)
- **表存储**：[Python](references/sdk/azure-data-tables-py.md) | [Java](references/sdk/azure-data-tables-java.md)

如需查看所有语言的全量包列表，请参阅 [SDK 使用指南](references/sdk-usage.md)。

## Azure SDK

对于通过编程方式与 Azure Storage 交互的应用程序，Azure 提供了多种语言（.NET、Java、JavaScript、Python、Go、Rust）的 SDK 包。请参阅 [SDK 使用指南](references/sdk-usage.md)，了解包名称、安装命令及快速入门示例。
