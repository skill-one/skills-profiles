# 调试指南

## 字节码比较流程

Turso 旨在兼容 SQLite。当行为存在差异时：

```
1. 在 sqlite3 中执行 EXPLAIN 查询
2. 在 tursodb 中执行 EXPLAIN 查询
3. 比较字节码
   ├─ 不同 → 代码生成中的 bug
   └─ 相同但结果不同 → 虚拟机或存储层中的 bug
```

### 示例

```bash
# SQLite
sqlite3 :memory: "EXPLAIN SELECT 1 + 1;"

# Turso
cargo run --bin tursodb :memory: "EXPLAIN SELECT 1 + 1;"
```

## 手动查询检查

```bash
cargo run --bin tursodb :memory: 'SELECT * FROM foo;'
cargo run --bin tursodb :memory: 'EXPLAIN SELECT * FROM foo;'
```

## 日志记录

```bash
# 在测试中跟踪核心
RUST_LOG=none,turso_core=trace make test

# 输出到 testing/test.log
# 注意：每个测试运行可能产生数兆字节数据
```

## 线程问题

使用 ThreadSanitizer 进行压力测试：

```bash
rustup toolchain install nightly
rustup override set nightly
cargo run -Zbuild-std --target x86_64-unknown-linux-gnu \
  -p turso_stress -- --vfs syscall --nr-threads 4 --nr-iterations 1000
```

## 确定性模拟

使用种子重现 bug。注意：模拟器使用旧的 "limbo" 命名。

```bash
# 模拟器
RUST_LOG=limbo_sim=debug cargo run --bin limbo_sim -- -s <seed>

# Whopper (并发 DST)
SEED=1234 ./testing/concurrent-simulator/bin/run
```

## 架构参考

- **解析器** → 从 SQL 字符串生成 AST
- **代码生成器** → 从 AST 生成字节码
- **虚拟机** → 执行兼容 SQLite 的字节码
- **存储层** → B 树操作、分页

## 数据损坏调试

对于 WAL 损坏和数据库完整性问题，使用 [scripts](./scripts) 中的损坏调试工具。

有关详细使用说明，请参阅 [references/CORRUPTION-TOOLS.md](./references/CORRUPTION-TOOLS.md)。
