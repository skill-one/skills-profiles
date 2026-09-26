# 差异化模糊测试器

始终加载 [调试技巧参考](../debugging/)

差异化模糊测试器通过比较 Turso 结果与 SQLite 生成的 SQL 语句，以发现正确性错误。

## 位置

`testing/differential-oracle/fuzzer/`

## 运行模糊测试器

### 单次运行

```bash
# 基本运行 (100 条语句，随机种子)
cargo run --bin differential_fuzzer

# 使用特定种子以实现可重复性
cargo run --bin differential_fuzzer -- --seed 12345

# 更多的语句和详细输出
cargo run --bin differential_fuzzer -- -n 1000 --verbose

# 运行后保留数据库文件 (用于调试)
cargo run --bin differential_fuzzer -- --seed 12345 --keep-files

# 所有选项
cargo run --bin differential_fuzzer -- \
  --seed <SEED>           # 确定性种子
  -n <NUM>                # 语句数量 (默认: 100)
  -t <NUM>                # 表数量 (默认: 2)
  -c <NUM>                # 每表的列数 (默认: 5)
  --verbose               # 打印每个 SQL 语句
  --keep-files            # 将 .db 文件持久化到磁盘
```

### 持续模糊测试 (循环模式)

```bash
# 使用随机种子无限运行
cargo run --bin differential_fuzzer -- loop

# 运行 50 次迭代
cargo run --bin differential_fuzzer -- loop 50
```

### Docker 运行器 (CI/生产环境)

```bash
# 从仓库根目录构建和运行
docker build -f testing/differential-oracle/fuzzer/docker-runner/Dockerfile -t fuzzer .
docker run -e GITHUB_TOKEN=xxx -e SLACK_WEBHOOK_URL=xxx fuzzer
```

docker-runner 的环境变量:
- `TIME_LIMIT_MINUTES` - 总运行时间 (默认: 1440 = 24 小时)
- `PER_RUN_TIMEOUT_SECONDS` - 每次运行超时 (默认: 1200 = 20 分钟)
- `NUM_STATEMENTS` - 每次运行的语句数量 (默认: 1000)
- `LOG_TO_STDOUT` - 打印模糊测试器输出 (默认: false)
- `GITHUB_TOKEN` - 用于自动提交问题
- `SLACK_WEBHOOK_URL` - 用于通知

## 输出文件

所有输出都到 `simulator-output/` 目录:

| 文件 | 描述 |
|------|------|
| `test.sql` | 所有执行的 SQL 语句。失败的语句以 `-- FAILED:` 开头，错误以 `-- ERROR:` 开头 |
| `schema.json` | 运行结束或失败时的数据库架构 |
| `test.db` | Turso 数据库文件 (仅使用 `--keep-files` 时) |
| `test-sqlite.db` | SQLite 数据库文件 (仅使用 `--keep-files` 时) |

## 复现错误

始终遵循以下步骤

1. **在错误输出中查找种子和配置**:
   ```
   INFO: Starting differential_fuzzer with config: SimConfig { seed: 12345, ..., weight_profile: Writes }
   ```

2. **使用该种子和配置重新运行** (种子仅在相同配置下重放):
   ```bash
   cargo run --bin differential_fuzzer -- --seed 12345 --profile writes --verbose --keep-files
   ```

3. **首先阅读最小化重放脚本**。在 Oracle 失败时，模糊测试器将这些文件写入 `simulator-output/`:
   - `minimized.sql` - 缩小的状态脚本加上缩小的失败语句，自动生成。从这里开始。
   - `turso-state.sql` / `sqlite-state.sql` - 每个引擎的完整状态作为可重放的脚本，当你需要比最小化版本更多信息时。
   - `test.sql` - 每条执行的语句 (失败的语句标记为 `-- FAILED:`)。最小化器在失败取决于状态构建方式而非内容时，会回放此历史记录。
   - `schema.json` - 失败时的表结构。

4. **使用 `differential_probe` 探测重放**。它在 Turso 和 SQLite 端分别运行每行语句脚本，打印每个语句的两种结果，标记差异，并比较最终表内容。退出码 1 表示有差异。
   ```bash
   cargo run -q -p differential-fuzzer --bin differential_probe -- \
       simulator-output/minimized.sql
   ```
   代替将 SQL 管道到两个 shell：tursodb shell 不能 `ATTACH ':memory:' AS aux`，所以带有 `aux` 架构的模糊测试器重放只能通过探测正确运行。从标准输入读取也有效:
   `echo "SELECT ~X'96';" | cargo run -q -p differential-fuzzer --bin differential_probe`.

5. **通过编辑脚本进行二分法**。复制 `minimized.sql`，一次简化一点 (用常量替换表达式，删除列，删除状态行)，每次编辑后重新运行探测。差异标记会立即告诉你编辑是否保留了错误。这个循环通常会在一个单行内核结束，你可以将其交给两个引擎的 `EXPLAIN`。

6. **从内核创建回归测试**。在 `.sqltest` (首选) 或 `.rs` 中创建。始终加载 [调试技巧参考](../debugging/)。

## 理解失败

### Oracle 失败类型

1. **行集不匹配** - Turso 返回的行与 SQLite 不同
2. **Turso 错误但 SQLite 成功** - Turso 拒绝了有效的 SQL
3. **SQLite 错误但 Turso 成功** - Turso 接受了无效的 SQL
4. **架构不匹配** - DDL 后表/列不同

### 警告 (非致命)

- **无排序的 LIMIT 不匹配** - 没有 ORDER BY 的 LIMIT 可能返回不同的有效行

## 关键源文件

| 文件 | 目的 |
|------|------|
| `main.rs` | CLI 解析，入口点 |
| `runner.rs` | 主模拟循环，在两个数据库上执行语句 |
| `oracle.rs` | 比较 Turso 与 SQLite 结果 |
| `schema.rs` | 从两个数据库中检查架构 |
| `memory/` | 用于确定性模拟的内存 IO |

## 跟踪

设置 `RUST_LOG` 以获取更详细的输出:

```bash
RUST_LOG=debug cargo run --bin differential_fuzzer -- --seed 12345
```
