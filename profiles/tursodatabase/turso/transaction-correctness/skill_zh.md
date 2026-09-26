# 事务正确性指南

Turso 独家使用 WAL（预写式日志）模式。

文件：`.db`，`.db-wal`（没有 `.db-shm` - Turso 使用内存中的 WAL 索引）

## WAL 机制

### 写路径
1. 写入应用程序将数据帧（页面数据）追加到 WAL 文件（顺序 I/O）
2. COMMIT = 标头中包含非零 db_size 的数据帧（标记事务结束）
3. 原始数据库在检查点之前保持不变

### 读路径
1. 读取器获取读取标记（mxFrame = 最后一个有效的提交帧）
2. 对于每个页面：检查 WAL 直到 mxFrame，回退到主数据库
3. 读取器在其读取标记处看到一致的快照

### 检查点
将 WAL 内容传输回主数据库。

```
WAL 增长 → 触发检查点（默认：1000 页）→ 页面复制到数据库 → WAL 重新使用
```

检查点类型：
- **PASSIVE**：非阻塞，在活动读取器需要的页面处停止
- **FULL**：等待读取器，检查点所有内容
- **RESTART**：类似于 FULL，还重置 WAL 到开始位置
- **TRUNCATE**：类似于 RESTART，还截断 WAL 文件到零长度

### WAL-索引
SQLite 使用共享内存文件（`-shm`）用于 WAL 索引。**Turso 不使用** - 它使用内存中的数据结构（`frame_cache` 哈希表，原子读取标记），因为不支持多进程访问。

## 并发规则

- 一次只有一个写入器
- 读取器不阻塞写入器，写入器不阻塞读取器
- 检查点必须在活动读取器需要的页面处停止

## 恢复

在崩溃时：
1. 第一个连接获取独占锁
2. 从 WAL 重放有效的提交
3. 释放锁，恢复正常操作

## Turso 实现

关键文件：
- [WAL 实现](../../../core/storage/wal.rs) - WAL 实现
- [页面管理，事务](../../../core/storage/pager.rs)

### 连接私有与共享

**每个连接（私有）：**
- `Pager` - 页面缓存，脏页面，保存点，提交状态
- `WalFile` - 连接的快照视图：
  - `max_frame` / `min_frame` - 此连接快照的帧范围
  - `max_frame_read_lock_index` - 此连接持有的读取锁槽位
  - `last_checksum` - 滚动校验和状态

**跨连接共享：**
- `WalFileShared` - 全局 WAL 状态：
  - `frame_cache` - 页面到帧索引（替换 `.shm` 文件）
  - `max_frame` / `nbackfills` - 全局 WAL 进度
  - `read_locks[5]` - 读取标记槽位（TursoRwLock 嵌入帧值）
  - `write_lock` - 独占写入器锁
  - `checkpoint_lock` - 检查点序列化
  - `file` - WAL 文件句柄
- `DatabaseStorage` - 主 `.db` 文件
- `BufferPool` - 共享内存分配

## 正确性不变量

1. **持久性**：COMMIT 记录必须在返回成功之前进行 fsync
2. **原子性**：部分事务永远不会对读取器可见
3. **隔离性**：每个读取器看到一致的快照
4. **无丢失更新**：检查点不能覆盖未提交的更改

## 参考文献

- [SQLite WAL](https://sqlite.org/wal.html)
- [WAL 文件格式](https://sqlite.org/walformat.html)
