**角色设定：** 你是一位 Go 工程师，将测试视为可执行的规范。你编写测试来约束行为并使失败具有自解释性——而不是为了达成覆盖率目标。

**模式：**

- **编写模式**——向代码库添加新的测试或模拟。
- **审查模式**——审计现有的测试代码以检查 testify 的误用。

# stretchr/testify

testify 通过可读的断言、模拟和测试套件来补充 Go 的 `testing` 包。它不会取代 `testing`——始终使用 `*testing.T` 作为入口点。

这项技能并不详尽——请参考库文档和代码示例以获取更多信息：

- 对于 Go 包文档、符号、版本、导入者和已知漏洞，→ 查看 `samber/cc-skills-golang@golang-pkg-go-dev` 技能（`godig`），优先于 Context7 以获取 Go 包事实。
- 要导航你自己的代码中该库的使用情况（定义、调用位置、诊断），→ 查看 `samber/cc-skills-golang@golang-gopls` 技能（`gopls`）。
- Context7 仍然是未在 pkg.go.dev 上索引的文档的备用方案。

## assert 与 require 的区别

两者都提供相同的断言。区别在于失败行为：

- **assert**：记录失败，继续——一次查看所有失败
- **require**：调用 `t.FailNow()`——用于前提条件，如果继续会引发恐慌或误导

使用 `assert.New(t)` / `require.New(t)` 以提高可读性。将它们命名为 `is` 和 `must`：

```go
func TestParseConfig(t *testing.T) {
    is := assert.New(t)
    must := require.New(t)

    cfg, err := ParseConfig("testdata/valid.yaml")
    must.NoError(err)    // 如果解析失败则停止——cfg 将为 nil
    must.NotNil(cfg)

    is.Equal("production", cfg.Environment)
    is.Equal(8080, cfg.Port)
    is.True(cfg.TLS.Enabled)
}
```

**规则**：`require` 用于前提条件（设置、错误检查），`assert` 用于验证。切勿随意混用。

## 核心断言

```go
is := assert.New(t)

// 等价性
is.Equal(expected, actual)              // DeepEqual + 精确类型
is.NotEqual(unexpected, actual)
is.EqualValues(expected, actual)        // 首先转换为通用类型
is.EqualExportedValues(expected, actual)

// 空值 / 布尔值 / 空值
is.Nil(obj)                  is.NotNil(obj)
is.True(cond)                is.False(cond)
is.Empty(collection)         is.NotEmpty(collection)
is.Len(collection, n)

// 包含（字符串、切片、映射键）
is.Contains("hello world", "world")
is.Contains([]int{1, 2, 3}, 2)
is.Contains(map[string]int{"a": 1}, "a")

// 比较
is.Greater(actual, threshold)     is.Less(actual, ceiling)
is.Positive(val)                  is.Negative(val)
is.Zero(val)

// 错误
is.Error(err)                     is.NoError(err)
is.ErrorIs(err, ErrNotFound)      // 遍历错误链
is.ErrorAs(err, &target)
is.ErrorContains(err, "not found")

// 类型
is.IsType(&User{}, obj)
is.Implements((*io.Reader)(nil), obj)
```

**参数顺序**：始终为 `(expected, actual)`——交换顺序会产生令人困惑的差异输出。

## 高级断言

```go
is.ElementsMatch([]string{"b", "a", "c"}, result)             // 无序比较
is.InDelta(3.14, computedPi, 0.01)                            // 浮点数容差
is.JSONEq(`{"name":"alice"}`, `{"name": "alice"}`)             // 忽略空白/键顺序
is.WithinDuration(expected, actual, 5*time.Second)
is.Regexp(`^user-[a-f0-9]+$`, userID)

// 异步轮询
is.Eventually(func() bool {
    status, _ := client.GetJobStatus(jobID)
    return status == "completed"
}, 5*time.Second, 100*time.Millisecond)

// 异步轮询与丰富断言
is.EventuallyWithT(func(c *assert.CollectT) {
    resp, err := client.GetOrder(orderID)
    assert.NoError(c, err)
    assert.Equal(c, "shipped", resp.Status)
}, 10*time.Second, 500*time.Millisecond)
```

## testify/mock

模拟接口以隔离待测单元。嵌入 `mock.Mock`，使用 `m.Called()` 实现方法，始终使用 `AssertExpectations(t)` 进行验证。

关键匹配器：`mock.Anything`，`mock.AnythingOfType("T")`，`mock.MatchedBy(func)`。调用修饰符：`.Once()`，`.Times(n)`，`.Maybe()`，`.Run(func)`。

有关模拟定义、参数匹配器、调用修饰符、返回序列和验证的说明，请参阅 [Mock 参考](./references/mock.md)。

## testify/suite

测试套件将相关的测试与共享的设置/清理分组。

### 生命周期

```
SetupSuite()    → 所有测试之前执行一次
  SetupTest()   → 每个测试之前执行
    TestXxx()
  TearDownTest() → 每个测试之后执行
TearDownSuite() → 所有测试之后执行一次
```

### 示例

```go
type TokenServiceSuite struct {
    suite.Suite
    store   *MockTokenStore
    service *TokenService
}

func (s *TokenServiceSuite) SetupTest() {
    s.store = new(MockTokenStore)
    s.service = NewTokenService(s.store)
}

func (s *TokenServiceSuite) TestGenerate_ReturnsValidToken() {
    s.store.On("Save", mock.Anything, mock.Anything).Return(nil)
    token, err := s.service.Generate("user-42")
    s.NoError(err)
    s.NotEmpty(token)
    s.store.AssertExpectations(s.T())
}

// 必须的启动器
func TestTokenServiceSuite(t *testing.T) {
    suite.Run(t, new(TokenServiceSuite))
}
```

套件方法如 `s.Equal()` 的行为与 `assert` 类似。对于 require：`s.Require().NotNil(obj)`。

## 常见错误

- **忘记 `AssertExpectations(t)`**——模拟期望在未验证的情况下静默通过
- **`is.Equal(ErrNotFound, err)`**——在包装错误上失败。使用 `is.ErrorIs` 遍历错误链
- **参数顺序交换**——testify 假设 `(expected, actual)`。交换顺序会产生反向差异
- **使用 `assert` 作为守卫**——测试在失败后继续，并在空值引用时引发恐慌。使用 `require`
- **缺少 `suite.Run()`**——没有启动器函数，零个测试将静默执行
- **比较指针**——`is.Equal(ptr1, ptr2)` 比较地址。取消引用或使用 `EqualExportedValues`

## Linters

使用 `testifylint` 捕获错误的参数顺序、assert/require 误用等。请参阅 `samber/cc-skills-golang@golang-lint` 技能。

## 交叉引用

- → 查看 `samber/cc-skills-golang@golang-testing` 技能以获取一般测试模式、表格驱动测试和 CI
- → 查看 `samber/cc-skills-golang@golang-lint` 技能以获取 testifylint 配置
