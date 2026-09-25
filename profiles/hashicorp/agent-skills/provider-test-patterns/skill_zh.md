# 提供商验收测试模式

使用
[terraform-plugin-testing](https://github.com/hashicorp/terraform-plugin-testing)
与
[Plugin Framework](https://github.com/hashicorp/terraform-plugin-framework)
编写验收测试的模式。

来源：[HashiCorp 测试模式](https://developer.hashicorp.com/terraform/plugin/testing/testing-patterns)

**参考资料**（按需加载）：
- `references/checks.md` — statecheck、plancheck、knownvalue 类型、tfjsonpath、comparers
- `references/sweepers.md` — sweeper 设置、TestMain、依赖项
- `references/ephemeral.md` — 临时资源测试、echoprovider、多步骤模式

---

## 测试生命周期

框架对每个 TestStep 运行：**计划 → 应用 → 刷新 → 最终计划**。如果最终计划显示有差异，测试将失败（除非设置了 `ExpectNonEmptyPlan`）。所有步骤完成后，将运行销毁，然后是 `CheckDestroy`。这意味着每个测试都会自动验证配置是否干净地应用且不会产生漂移——无需为此进行断言。

---

## 测试函数结构

```go
func TestAccExample_basic(t *testing.T) {
    var widget example.Widget
    rName := acctest.RandStringFromCharSet(10, acctest.CharSetAlphaNum)
    resourceName := "example_widget.test"

    resource.ParallelTest(t, resource.TestCase{
        PreCheck:                 func() { testAccPreCheck(t) },
        ProtoV6ProviderFactories: testAccProtoV6ProviderFactories,
        CheckDestroy:             testAccCheckExampleDestroy,
        Steps: []resource.TestStep{
            {
                Config: testAccExampleConfig_basic(rName),
                ConfigStateChecks: []statecheck.StateCheck{
                    stateCheckExampleExists(resourceName, &widget),
                    statecheck.ExpectKnownValue(resourceName,
                        tfjsonpath.New("name"), knownvalue.StringExact(rName)),
                    statecheck.ExpectKnownValue(resourceName,
                        tfjsonpath.New("id"), knownvalue.NotNull()),
                },
            },
        },
    })
}
```

默认使用 `resource.ParallelTest`。仅在测试共享状态或无法并发运行时使用 `resource.Test`。

---

## 提供商工厂

```go
// provider_test.go — 使用协议 6 的 Plugin Framework（如有需要，请使用协议 5 的变体）
var testAccProtoV6ProviderFactories = map[string]func() (tfprotov6.ProviderServer, error){
    "example": providerserver.NewProtocol6WithError(New("test")()),
}
```

---

## TestCase 字段

| 字段 | 目的 |
|-------|---------|
| `PreCheck` | `func()` — 验证先决条件（环境变量、API 访问） |
| `ProtoV6ProviderFactories` | Plugin Framework 提供商工厂 |
| `CheckDestroy` | `TestCheckFunc` — 验证所有步骤后资源被销毁 |
| `Steps` | `[]TestStep` — 顺序测试操作 |
| `TerraformVersionChecks` | `[]tfversion.TerraformVersionCheck` — 通过 CLI 版本进行限制 |

---

## TestStep 字段

### 配置模式

| 字段 | 目的 |
|-------|---------|
| `Config` | 要应用的行内 HCL 字符串 |
| `ConfigStateChecks` | `[]statecheck.StateCheck` — 现代断言（首选） |
| `ConfigPlanChecks` | `resource.ConfigPlanChecks{PreApply: []plancheck.PlanCheck{...}}` |
| `ExpectError` | `*regexp.Regexp` — 预期匹配模式的失败 |
| `ExpectNonEmptyPlan` | `bool` — 应用后预期非空计划 |
| `PlanOnly` | `bool` — 仅计划而不应用 |
| `Destroy` | `bool` — 运行销毁步骤 |
| `PreConfig` | `func()` — 步骤前的设置 |

### 导入模式

| 字段 | 目的 |
|-------|---------|
| `ImportState` | 设置为 `true` 以启用导入模式 |
| `ImportStateVerify` | 验证导入的 state 是否与先前的 state 匹配 |
| `ImportStateVerifyIgnore` | `[]string` — 在验证期间跳过的属性 |
| `ImportStateKind` | `resource.ImportBlockWithID` — 导入块的生成 |
| `ResourceName` | 要导入的资源地址 |
| `ImportStateId` | 覆盖用于导入的 ID |

---

## 检查函数

### 现代：ConfigStateChecks（首选）

类型安全，具有聚合错误报告。使用自定义 `statecheck.StateCheck` 实现组合内置检查。有关完整的 knownvalue 类型、tfjsonpath 导航和比较器的详细信息，请参阅 `references/checks.md`。

```go
ConfigStateChecks: []statecheck.StateCheck{
    stateCheckExampleExists(resourceName, &widget),
    statecheck.ExpectKnownValue(resourceName,
        tfjsonpath.New("name"), knownvalue.StringExact("my-widget")),
    statecheck.ExpectKnownValue(resourceName,
        tfjsonpath.New("enabled"), knownvalue.Bool(true)),
    statecheck.ExpectKnownValue(resourceName,
        tfjsonpath.New("id"), knownvalue.NotNull()),
    statecheck.ExpectSensitiveValue(resourceName,
        tfjsonpath.New("api_key")),
},
```

不要在同一个步骤中混合 `Check`（旧版）和 `ConfigStateChecks`。

### 旧版：Check（用于 CheckDestroy 和迁移）

`TestCase` 上的 `CheckDestroy` 需要 `TestCheckFunc`。`TestStep` 上的 `Check` 也接受 `TestCheckFunc`，但建议为新测试使用 `ConfigStateChecks`。

```go
Check: resource.ComposeAggregateTestCheckFunc(
    resource.TestCheckResourceAttr(name, "key", "expected"),
    resource.TestCheckResourceAttrSet(name, "id"),
    resource.TestCheckNoResourceAttr(name, "removed"),
    resource.TestMatchResourceAttr(name, "url", regexp.MustCompile(`^https://`)),
    resource.TestCheckResourceAttrPair(res1, "ref_id", res2, "id"),
),
```

`ComposeAggregateTestCheckFunc` 报告所有错误；`ComposeTestCheckFunc` 在第一个错误时快速失败。

---

## 配置辅助函数

使用编号格式动词——`%[1]q` 用于引用字符串，`%[1]s` 用于原始字符串：

```go
func testAccExampleConfig_basic(rName string) string {
    return fmt.Sprintf(`
resource "example_widget" "test" {
  name = %[1]q
}
`, rName)
}

func testAccExampleConfig_full(rName, description string) string {
    return fmt.Sprintf(`
resource "example_widget" "test" {
  name        = %[1]q
  description = %[2]q
  enabled     = true
}
`, rName, description)
}
```

---

## 场景模式

### 基本操作 + 更新（在一个测试中组合——更新是基本操作的超集）

```go
Steps: []resource.TestStep{
    {
        Config: testAccExampleConfig_basic(rName),
        ConfigStateChecks: []statecheck.StateCheck{
            stateCheckExampleExists(resourceName, &widget),
            statecheck.ExpectKnownValue(resourceName,
                tfjsonpath.New("name"), knownvalue.StringExact(rName)),
        },
    },
    {
        Config: testAccExampleConfig_full(rName, "updated"),
        ConfigStateChecks: []statecheck.StateCheck{
            stateCheckExampleExists(resourceName, &widget),
            statecheck.ExpectKnownValue(resourceName,
                tfjsonpath.New("description"), knownvalue.StringExact("updated")),
        },
    },
},
```

### 导入

在配置步骤后，验证导入是否产生相同的 state。使用 `ImportStateKind` 进行导入块的生成：

```go
{
    ResourceName:      resourceName,
    ImportState:       true,
    ImportStateVerify: true,
    ImportStateKind:   resource.ImportBlockWithID,
},
```

### 消失（资源被外部删除）

```go
{
    Config: testAccExampleConfig_basic(rName),
    ConfigStateChecks: []statecheck.StateCheck{
        stateCheckExampleExists(resourceName, &widget),
        stateCheckExampleDisappears(resourceName),
    },
    ExpectNonEmptyPlan: true,
},
```

### 验证（预期错误）

```go
{
    Config:      testAccExampleConfig_invalidName(""),
    ExpectError: regexp.MustCompile(`name must not be empty`),
},
```

### 回归（两提交工作流）

一个正确的错误修复至少需要两个提交：首先提交回归测试（该测试失败，确认了错误），然后提交修复（测试通过）。这允许审查者通过检出第一个提交，然后前进到修复来独立验证测试是否重现了问题。

命名和记录回归测试以识别它们修复的问题。在可能的情况下，包含指向原始错误报告的链接。

```go
// TestAccExample_regressionGH1234 验证 https://github.com/org/repo/issues/1234 的修复
func TestAccExample_regressionGH1234(t *testing.T) {
    rName := acctest.RandStringFromCharSet(10, acctest.CharSetAlphaNum)
    resourceName := "example_widget.test"

    resource.ParallelTest(t, resource.TestCase{
        PreCheck:                 func() { testAccPreCheck(t) },
        ProtoV6ProviderFactories: testAccProtoV6ProviderFactories,
        CheckDestroy:             testAccCheckExampleDestroy,
        Steps: []resource.TestStep{
            {
                // 重现问题：此配置触发了错误
                Config: testAccExampleConfig_regressionGH1234(rName),
                ConfigStateChecks: []statecheck.StateCheck{
                    stateCheckExampleExists(resourceName, nil),
                    statecheck.ExpectKnownValue(resourceName,
                        tfjsonpath.New("computed_field"), knownvalue.NotNull()),
                },
            },
        },
    })
}
```

---

## 辅助函数

### 自定义 StateCheck：Exists

实现 `statecheck.StateCheck` 以进行 API 存在性验证。将存在检查分离到自己的函数中，以便在多个步骤中重用——源代码建议这作为一个设计原则：

```go
type exampleExistsCheck struct {
    resourceAddress string
    widget          *example.Widget
}

func (e exampleExistsCheck) CheckState(ctx context.Context, req statecheck.CheckStateRequest, resp *statecheck.CheckStateResponse) {
    r, err := stateResourceAtAddress(req.State, e.resourceAddress)
    if err != nil {
        resp.Error = err
        return
    }

    id, ok := r.AttributeValues["id"].(string)
    if !ok {
        resp.Error = fmt.Errorf("no id found for %s", e.resourceAddress)
        return
    }

    conn := testAccAPIClient()
    widget, err := conn.GetWidget(id)
    if err != nil {
        resp.Error = fmt.Errorf("%s not found via API: %w", e.resourceAddress, err)
        return
    }

    if e.widget != nil {
        *e.widget = *widget
    }
}

func stateCheckExampleExists(name string, widget *example.Widget) statecheck.StateCheck {
    return exampleExistsCheck{resourceAddress: name, widget: widget}
}
```

### 自定义 StateCheck：Disappears

通过 API 删除资源以模拟外部删除：

```go
type exampleDisappearsCheck struct {
    resourceAddress string
}

func (e exampleDisappearsCheck) CheckState(ctx context.Context, req statecheck.CheckStateRequest, resp *statecheck.CheckStateResponse) {
    r, err := stateResourceAtAddress(req.State, e.resourceAddress)
    if err != nil {
        resp.Error = err
        return
    }

    id := r.AttributeValues["id"].(string)
    conn := testAccAPIClient()
    resp.Error = conn.DeleteWidget(id)
}

func stateCheckExampleDisappears(name string) statecheck.StateCheck {
    return exampleDisappearsCheck{resourceAddress: name}
}
```

### State Resource Lookup（共享实用工具）

```go
func stateResourceAtAddress(state *tfjson.State, address string) (*tfjson.StateResource, error) {
    if state == nil || state.Values == nil || state.Values.RootModule == nil {
        return nil, fmt.Errorf("no state available")
    }
    for _, r := range state.Values.RootModule.Resources {
        if r.Address == address {
            return r, nil
        }
    }
    return nil, fmt.Errorf("not found in state: %s", address)
}
```

### Destroy Check（TestCheckFunc — 由 CheckDestroy 需要）

```go
func testAccCheckExampleDestroy(s *terraform.State) error {
    conn := testAccAPIClient()
    for _, rs := range s.RootModule().Resources {
        if rs.Type != "example_widget" {
            continue
        }
        _, err := conn.GetWidget(rs.Primary.ID)
        if err == nil {
            return fmt.Errorf("widget %s still exists", rs.Primary.ID)
        }
        if !isNotFoundError(err) {
            return err
        }
    }
    return nil
}
```

### PreCheck

```go
func testAccPreCheck(t *testing.T) {
    t.Helper()
    if os.Getenv("EXAMPLE_API_KEY") == "" {
        t.Fatal("EXAMPLE_API_KEY must be set for acceptance tests")
    }
}
```
