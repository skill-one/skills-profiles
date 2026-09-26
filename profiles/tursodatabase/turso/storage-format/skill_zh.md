# 存储格式指南

## 数据库文件结构

```
┌─────────────────────────────┐
│ 第1页：头部 + 模式     │  ← 前100字节 = 数据库头部
├─────────────────────────────┤
│ 第2页..N：B树页         │  ← 表和索引
│            越界页       │
│            空闲页       │
└─────────────────────────────┘
```

页大小：2的幂次方，512-65536字节。默认4096。

## 数据库头部（前100字节）

| 偏移量 | 大小 | 字段 |
|--------|------|-------|
| 0 | 16 | 魔数：`"SQLite format 3\0"` |
| 16 | 2 | 页大小（大端序） |
| 18 | 1 | 写格式版本（1=回滚，2=WAL） |
| 19 | 1 | 读格式版本 |
| 24 | 4 | 变更计数器 |
| 28 | 4 | 数据库页大小 |
| 32 | 4 | 首个空闲页树页 |
| 36 | 4 | 空闲页总数 |
| 40 | 4 | 模式Cookie |
| 56 | 4 | 文本编码（1=UTF8，2=UTF16LE，3=UTF16BE） |

所有多字节整数：**大端序**。

## 页类型

| 标志 | 类型 | 用途 |
|------|------|---------|
| 0x02 | 内部索引 | 索引B树内部节点 |
| 0x05 | 内部表 | 表B树内部节点 |
| 0x0a | 叶子索引 | 索引B树叶子 |
| 0x0d | 叶子表 | 表B树叶子 |
| - | 越界 | 超出单元格容量的负载 |
| - | 空闲 | 未使用的页（树干或叶子） |

## B树结构

两种B树类型：
- **表B树**：64位行id键，存储行数据
- **索引B树**：任意键（索引列 + 行id）

```
内部页： [ptr0] key1 [ptr1] key2 [ptr2] ...
                   │         │         │
                   ▼         ▼         ▼
               子页     子页     子页

叶子页： key1:data  key2:data  key3:data ...
```

第1页始终是`sqlite_schema`表的根。

## 单元格格式

### 表叶子单元格
```
[payload_size: 可变长整数] [rowid: 可变长整数] [payload] [overflow_ptr: u32?]
```

### 表内部单元格
```
[left_child_page: u32] [rowid: 可变长整数]
```

### 索引单元格
类似，但键是任意的（列 + 行id），而不仅仅是行id。

## 记录格式（负载）

```
[header_size: 可变长整数] [type1: 可变长整数] [type2: 可变长整数] ... [data1] [data2] ...
```

序列类型：
| 类型 | 含义 |
|------|---------|
| 0 | NULL |
| 1-4 | 1/2/3/4字节有符号整数 |
| 5 | 6字节有符号整数 |
| 6 | 8字节有符号整数 |
| 7 | IEEE 754浮点数 |
| 8 | 整数0 |
| 9 | 整数1 |
| ≥12偶数 | BLOB，长度=(N-12)/2 |
| ≥13奇数 | 文本，长度=(N-13)/2 |

## 越界页

当负载超过阈值时，多余部分存储在越界链中：
```
[next_page: u32] [data...]
```
最后一页有`next_page=0`。

## 空闲页

包含叶子页编号的树干页的链表：
```
树干： [next_trunk: u32] [leaf_count: u32] [leaf_pages: u32...] 
```

## Turso实现

关键文件：
- `core/storage/sqlite3_ondisk.rs` - 磁盘格式，`PageType`枚举
- `core/storage/btree.rs` - B树操作（大文件）
- `core/storage/pager.rs` - 页面管理
- `core/storage/buffer_pool.rs` - 页面缓存

## 调试存储

```bash
# 完整性检查
cargo run --bin tursodb test.db "PRAGMA integrity_check;"

# 页面计数
cargo run --bin tursodb test.db "PRAGMA page_count;"

# 空闲页信息
cargo run --bin tursodb test.db "PRAGMA freelist_count;"
```

## 参考文献

- [SQLite文件格式](https://sqlite.org/fileformat.html)
- [SQLite B树模块](https://sqlite.org/btreemodule.html)
- [SQLite内部：页面与B树](https://fly.io/blog/sqlite-internals-btree/)
