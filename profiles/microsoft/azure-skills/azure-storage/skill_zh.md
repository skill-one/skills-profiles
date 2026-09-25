# Azure 存储服务

## 服务

| 服务 | 使用场景 | MCP 工具 | CLI |
|---------|----------|-----------|-----|
| Blob 存储 | 对象、文件、备份、静态内容 | `azure__storage` | `az storage blob` |
| 文件共享 | SMB 文件共享、迁移 | - | `az storage file` |
| 队列存储 | 异步消息、任务队列 | - | `az storage queue` |
| 表存储 | NoSQL 键值对（考虑 Cosmos DB） | - | `az storage table` |
| 数据湖 | 大数据分析、分层命名空间 | - | `az storage fs` |

## MCP 服务器（推荐）

当 Azure MCP 启用时：

- `azure__storage` 命令 `storage_account_list` - 列出存储账户
- `azure__storage` 命令 `storage_container_list` - 列出账户中的容器
- `azure__storage` 命令 `storage_blob_list` - 列出容器中的 Blob
- `azure__storage` 命令 `storage_blob_get` - 下载 Blob 内容
- `azure__storage` 命令 `storage_blob_put` - 上传 Blob 内容

**如果 Azure MCP 未启用：** 运行 `/azure:setup` 或通过 `/mcp` 启用。

## CLI 备用方案

```bash
# 列出存储账户
az storage account list --output table

# 列出容器
az storage container list --account-name ACCOUNT --output table

# 列出 Blob
az storage blob list --account-name ACCOUNT --container-name CONTAINER --output table

# 下载 Blob
az storage blob download --account-name ACCOUNT --container-name CONTAINER --name BLOB --file LOCAL_PATH

# 上传 Blob
az storage blob upload --account-name ACCOUNT --container-name CONTAINER --name BLOB --file LOCAL_PATH
```

## 存储账户层级

| 层级 | 使用场景 | 性能 |
|------|----------|-------------|
| 标准 | 通用用途、备份 | 毫秒级 |
| 高级 | 数据库、高 IOPS | 亚毫秒级 |

## Blob 访问层级

| 层级 | 访问频率 | 成本 |
|------|-----------------|------|
| 热 | 频繁访问 | 更高存储成本、较低访问成本 |
| 冷 | 不频繁访问（30天以上） | 较低存储成本、较高访问成本 |
| 深冷 | 极不频繁访问（90天以上） | 存储成本更低 |
| 归档 | 极不频繁访问（180天以上） | 最低存储成本、需要重新激活 |

## 冗余选项

| 类型 | 可靠性 | 使用场景 |
|------|------------|----------|
| LRS | 11 个 9 | 开发/测试、可重建数据 |
| ZRS | 12 个 9 | 区域高可用性 |
| GRS | 16 个 9 | 灾难恢复 |
| GZRS | 16 个 9 | 最佳可靠性 |

## 服务详情

关于特定服务的深度文档：

- Blob 存储模式和管理生命周期 -> [Blob 存储文档](https://learn.microsoft.com/zh-cn/azure/storage/blobs/storage-blobs-overview)
- 文件共享和 Azure 文件同步 -> [Azure Files 文档](https://learn.microsoft.com/zh-cn/azure/storage/files/storage-files-introduction)
- 队列模式和处理中毒消息 -> [队列存储文档](https://learn.microsoft.com/zh-cn/azure/storage/queues/storage-queues-introduction)

## SDK 快速参考

使用 Azure 存储SDK构建应用程序，请参阅精简指南：

- **Blob 存储**: [Python](references/sdk/azure-storage-blob-py.md) | [TypeScript](references/sdk/azure-storage-blob-ts.md) | [Java](references/sdk/azure-storage-blob-java.md) | [Rust](references/sdk/azure-storage-blob-rust.md)
- **队列存储**: [Python](references/sdk/azure-storage-queue-py.md) | [TypeScript](references/sdk/azure-storage-queue-ts.md)
- **文件共享**: [Python](references/sdk/azure-storage-file-share-py.md) | [TypeScript](references/sdk/azure-storage-file-share-ts.md)
- **数据湖**: [Python](references/sdk/azure-storage-file-datalake-py.md)
- **表存储**: [Python](references/sdk/azure-data-tables-py.md) | [Java](references/sdk/azure-data-tables-java.md)

跨所有语言的完整包列表，请参阅 [SDK 使用指南](references/sdk-usage.md)。

## Azure SDK

为构建与 Azure 存储交互的程序，Azure 提供了多种语言的 SDK 包 (.NET、Java、JavaScript、Python、Go、Rust)。有关包名称、安装命令和快速入门示例，请参阅 [SDK 使用指南](references/sdk-usage.md)。
