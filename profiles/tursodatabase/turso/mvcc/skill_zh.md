# MVCC 指南（实验性）

多版本并发控制。**开发中，不适用于生产环境。**

**重要提示**：调试时忽略 MVCC，除非问题是 MVCC 特有的。

## 启用 MVCC

```sql
PRAGMA journal_mode = 'mvcc';
```

运行时配置，不是编译时特性标志。数据库级别设置。

## 工作原理

标准 WAL：每页一个版本，读取者在读取标记时间点看到快照。

MVCC：多行版本，快照隔离。每个事务在开始时看到一致的快照。

### 与 WAL 的关键区别

| 方面 | WAL | MVCC |
|------|-----|------|
| 写粒度 | 每次提交写入完整页面 | 只影响受影响的行 |
| 读取者/写入者 | 互相不阻塞 | 互相不阻塞 |
| 持久化 | `.db-wal` | `.db-log`（逻辑日志） |
| 隔离性 | 快照（页面级别） | 快照（行级别） |

### 版本控制

每个行版本跟踪：
- `begin` - 可见时的时间戳
- `end` - 删除/替换时的时间戳
- `btree_resident` - MVCC 启用前已存在

## 架构

```
数据库
  └─ mv_store: MvStore
      ├─ rows: SkipMap<RowID, Vec<RowVersion>>
      ├─ txs: SkipMap<TxID, Transaction>
      ├─ 存储 (.db-log 文件)
      └─ CheckpointStateMachine
```

**每个连接**：`mv_tx` 跟踪当前的 MVCC 事务。

**共享**：使用无锁 `crossbeam_skiplist` 结构的 `MvStore`。

## 关键文件

- `core/mvcc/mod.rs` - 模块概述
- `core/mvcc/database/mod.rs` - 主要实现（约 3000 行）
- `core/mvcc/cursor.rs` - 合并 MVCC + B-tree 游标
- `core/mvcc/persistent_storage/logical_log.rs` - 磁盘格式
- `core/mvcc/database/checkpoint_state_machine.rs` - 检查点逻辑

## 检查点

定期将行版本刷新到 B-tree。

```sql
PRAGMA mvcc_checkpoint_threshold = <pages>;
```

流程：获取锁 → 开始 Pager 事务 → 写入行 → 提交 → 截断日志 → fsync → 释放。

## 当前限制

**未实现**：
- 垃圾回收（旧版本会累积）
- 重启时从逻辑日志恢复

**已知问题**：
- 检查点会阻塞其他事务，即使是读取操作！
- 没有磁盘溢出；内存使用问题

## 测试

```bash
# 运行 MVCC 特定测试
cargo test mvcc

# 带有 MVCC 的 TCL 测试
make test-mvcc
```

使用 `#[turso_macros::test(mvcc)]` 属性进行 MVCC 启用测试。

```rust
#[turso_macros::test(mvcc)]
fn test_something() {
    // 带有 MVCC 启用运行
}
```

## 参考

- `core/mvcc/mod.rs` 记录数据异常（脏读、丢失更新等）
- 快照隔离与可串行化：MVCC 提供前者，不提供后者
