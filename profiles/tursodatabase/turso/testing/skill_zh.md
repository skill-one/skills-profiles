# 测试指南

## 测试类型及使用场景

| 类型 | 位置 | 使用场景 |
|------|------|----------|
| `.sqltest` | `sqlite/conformance/sqlite-sqltests/` | SQL 兼容性。**优先用于新测试** |
| TCL `.test` | `testing/` | 遗留 SQL 兼容（正在逐步淘汰） |
| Rust 集成 | `tests/integration/` | 回归测试、复杂场景 |
| Fuzz | `tests/fuzz/` | 复杂功能、边缘案例发现 |

**注意：** TCL 测试正在逐步淘汰，优先使用 `sqlite/conformance/` 中的 `.sqltest` 套件。`.sqltest` 格式允许相同的测试用例在多个后端（CLI、Rust 绑定等）上运行。

## 运行测试

```bash
# 主测试套件（TCL 兼容、sqlite3 兼容、Python 绑定）
make test

# 单个 TCL 测试
make test-single TEST=select.test

# SQL 测试运行器
make -C sqlite/conformance run-cli

# 或者
cargo run -p sqltest -- run <测试文件或目录>

# Rust 单元/集成测试（完整工作区）
cargo test
```

## 编写测试

### .sqltest（推荐）
```
@database :default:

test example-addition {
    SELECT 1 + 1;
}
expect {
    2
}

test example-multiple-rows {
    SELECT id, name FROM users WHERE id < 3;
}
expect {
    1|alice
    2|bob
}
```
位置：`sqlite/conformance/sqlite-sqltests/*.sqltest`

你必须使用测试运行器中的 `convert` 命令开始转换 TCL 测试（例如 `cargo run -- convert <TCL_test_path> -o <out_dir>`）。它并不总是准确，但可以转换大部分测试。如果某些转换发出警告，你需要手动编写缺失的部分（例如手动展开 for each 循环）。然后你需要通过 `make -C sqlite/conformance run-rust` 运行测试来验证它们是否正常工作，并调整转换错误的结果。此外，我们在 TCL 中使用硬编码的数据库，但在 `.sqltest` 中我们使用不同的种子生成数据库，因此你可能需要更改预期的测试结果以匹配新的数据库查询输出。避免更改测试中的 SQL 语句，只需更改预期结果。

### TCL
```tcl
do_execsql_test_on_specific_db {:memory:} test-name {
  SELECT 1 + 1;
} {2}
```
位置：`testing/*.test`

### Rust 集成
```rust
// tests/integration/test_foo.rs
#[test]
fn test_something() {
    let conn = Connection::open_in_memory().unwrap();
    // ...
}
```

### 断言

对于任何超出简单断言的情况，优先使用 [`asserting`](https://github.com/innoave/asserting) crate。它提供的断言功能非常丰富，使测试更易读。一些简单示例：

```rust
use asserting::prelude::*;

assert_that!(conn.execute("SELECT * FROM t1;")).is_err();
assert_that_code!(|| parse(bad_input)).panics_with_message("unexpected token");

assert_that!(&rows)
    .has_length(3)
    .any_satisfies(|r| r
    .name == "bob")
    .first_element_ref()
    .is_equal_to(&Row { id: 1, name: "alice".into() });

assert_that!(&header)
    .named("page 2 header")
    .satisfies_with_message("be a leaf table page", |h| h[0] == 0x0d);

// 软断言：标记测试失败但不会停止
verify_that!(&plan)
    .starts_with("SEARCH")
    .contains("USING INDEX")
    .soft_panic();
```

`crate::assertions` 添加了 `row!` 用于结果行，以及 `column` 和查询计划断言：

```rust
use crate::assertions::{AssertColumn, AssertQueryPlan, Cell, NULL};

assert_that!(limbo_exec_rows(&conn, "SELECT id, name FROM t ORDER BY id"))
    .is_equal_to(vec![row![1, "alice"], row![2, NULL]]);

assert_that!(limbo_exec_rows(&conn, "SELECT id FROM t WHERE id = 1"))
    .single_element()
    .is_equal_to(row![1]);

assert_that!(limbo_exec_rows(&conn, "SELECT id, name FROM t"))
    .column(1)
    .contains(Cell::from("alice"));

assert_that!(limbo_exec_rows(&conn, "EXPLAIN QUERY PLAN SELECT id FROM t WHERE name = 'a'"))
    .uses_index("idx_name")
    .searches_table("t")
    .has_table_access_order(["t"]);
```

## 关键规则

- 每个功能变更都需要测试
- 测试在不变更时必须失败，变更后必须通过
- 优先使用内存数据库：`:memory:`（sqltest）或 `{:memory:}`（TCL）
- 不要发明新的测试格式。遵循现有模式
- 尽可能先编写测试

## 测试数据库模式

`testing/system/testing.db` 包含 `users` 和 `products` 表。参见 [docs/testing.md](../../../docs/testing.md) 获取模式。

## 测试期间的日志记录

```bash
RUST_LOG=none,turso_core=trace make test
```
输出：`testing/system/test.log`。警告：非常冗长。
