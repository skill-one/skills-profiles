# Go 测试

> 兼容性：差异示例可能使用 `github.com/google/go-cmp`。

## 资源路由

- `scripts/gen-table-test.sh` - 生成表格驱动测试框架时运行。
- `assets/table-test-template.go` - 用作可复制的表格测试起点。
- `references/TABLE-DRIVEN-TESTS.md` - 选择表格测试、子测试或并行测试模式时阅读。
- `references/TEST-HELPERS.md` - 编写辅助函数、固定装置、清理或测试替身时阅读。
- `references/TEST-ORGANIZATION.md` - 结构化包、黑盒测试或大型测试套件时阅读。
- `references/VALIDATION-APIS.md` - 选择 `t.Error`、`t.Fatal`、`cmp.Diff` 或断言风格时阅读。
- `references/INTEGRATION.md` - 测试外部服务、HTTP 处理程序、数据库或长时间运行设置时阅读。

## 快速参考

| 模式 | 使用场景 |
|------|----------|
| `t.Error` | 默认 — 报告失败，继续运行 |
| `t.Fatal` | 设置失败或继续无意义 |
| `cmp.Diff` | 比较结构体、切片、映射、协议缓冲区 |
| 表格驱动 | 许多情况共享相同逻辑 |
| 子测试 | 需要过滤、并行执行或命名 |
| `t.Helper()` | 任何测试辅助函数（作为第一条语句调用） |
| `t.Cleanup()` | 辅助函数中的清理操作（替代 `defer`） |

---

## 有用的测试失败

> **规范性**：测试失败必须在不阅读测试源的情况下可诊断。

每个失败消息必须包含：函数名、输入、实际（got）和预期（want）。使用格式 `YourFunc(%v) = %v, want %v`。

```go
// 良好：
t.Errorf("Add(2, 3) = %d, want %d", got, 5)

// 不良：缺少函数名和输入
t.Errorf("got %d, want %d", got, 5)
```

始终在 got 之前打印 want：`got %v, want %v` — 永不反转。

---

## 不使用断言库

> **规范性**：不要使用断言库。使用 `cmp.Diff` 进行复杂比较。

```go
if diff := cmp.Diff(want, got); diff != "" {
    t.Errorf("GetPost() 不匹配 (-want +got):\n%s", diff)
}
```

对于协议缓冲区，将 `protocmp.Transform()` 作为 cmp 选项添加。始终在 diff 消息中包含方向键 `(-want +got)`。避免比较 JSON/序列化输出 — 而是进行语义比较。

---

## t.Error 与 t.Fatal

> **规范性**：默认使用 `t.Error` 报告一次运行中的所有失败。仅在继续不可能时使用 `t.Fatal`。

**选择 `t.Fatal` 的情况：**
- 设置失败（DB 连接、文件加载）
- 下一个断言依赖于上一个断言成功（例如，编码后解码）

**永远不要从测试线程之外的 goroutine 调用 `t.Fatal`/`t.FailNow`** — 而是使用 `t.Error`。

---

## 表格驱动测试

> 搭建新表格驱动测试时，如果需要规范的结构、循环和子测试布局，请参阅 `assets/table-test-template.go`。

> **建议**：当许多情况共享相同逻辑时，使用表格驱动测试。

**使用表格测试的情况：**所有情况运行相同代码路径，无条件设置、模拟或断言。单个 `shouldErr` bool 是可接受的。

**不使用表格测试的情况：**情况需要复杂设置、条件模拟或多个分支 — 编写单独的测试函数。

**关键规则：**
- 使用字段名，当情况跨越多行或具有相同类型的相邻字段时
- 在失败消息中包含输入 — 永不通过索引识别行

> **验证**：生成或修改测试后，运行 `go test -run TestXxx -v` 验证测试是否编译并通过。在继续之前修复任何编译错误。

---

## 测试辅助函数

> **规范性**：测试辅助函数必须首先调用 `t.Helper()` 并使用 `t.Cleanup()` 进行清理。

```go
func setupTestDB(t *testing.T) *sql.DB {
    t.Helper()
    db, err := sql.Open("sqlite3", ":memory:")
    if err != nil {
        t.Fatalf("无法打开数据库: %v", err)
    }
    t.Cleanup(func() { db.Close() })
    return db
}
```

---

## 测试错误语义

> **建议**：测试错误语义，而不是错误消息字符串。

```go
// 不良：易碎的字符串比较
if err.Error() != "invalid input" { ... }

// 良好：语义检查
if !errors.Is(err, ErrInvalidInput) { ... }
```

对于简单的存在检查，当特定语义不重要时：

```go
if gotErr := err != nil; gotErr != tt.wantErr {
    t.Errorf("f(%v) 错误 = %v, want 错误存在 = %t", tt.input, err, tt.wantErr)
}
```

---

## 相关技能

- **错误测试**：测试错误语义时使用 `errors.Is`/`errors.As` 或哨兵错误，请参阅 [go-error-handling](../go-error-handling/SKILL.md)
- **接口模拟**：创建测试替身时通过在消费者端实现接口，请参阅 [go-interfaces](../go-interfaces/SKILL.md)
- **测试函数命名**：命名测试函数、子测试或测试辅助工具时，请参阅 [go-naming](../go-naming/SKILL.md)
- **代码检查器集成**：在 CI 或预提交钩子中与测试一起运行代码检查器时，请参阅 [go-linting](../go-linting/SKILL.md)
