# Terraform 提供商资源实现指南

## 概述

本指南涵盖开发 Terraform 提供商资源和数据源。
资源代表 Terraform 通过创建、读取、更新和删除（CRUD）操作管理的基础设施对象。

**使用 [插件框架](https://developer.hashicorp.com/terraform/plugin/framework) 开发所有全新的资源和数据源。** 插件 SDKv2 用于维护已存在的资源；不要针对它编写新代码。一个提供商可以通过混频（[terraform-plugin-mux](https://developer.hashicorp.com/terraform/plugin/mux)）在迁移期间同时服务，因此采用框架永远不会需要大规模重写。要判断现有提供商处于哪种模式，请检查 `go.mod`：`terraform-plugin-mux` 存在表示它同时服务 SDKv2 和框架代码；仅 `terraform-plugin-sdk/v2` 表示仅 SDKv2；仅 `terraform-plugin-framework` 表示仅框架。在迁移现有 SDKv2 资源时要谨慎：框架区分空值和零值，因此简单的迁移会改变现有用户的行为（如果可用，请使用 `provider-framework-migration` 技能）。

**参考文献**（按需加载）：
- `references/design-principles.md` — 应该（和不应该）成为资源的内容；数据源语义；关系和异步任务建模
- `references/retries-and-waiters.md` — 最终一致性、重试模式以及状态/等待函数结构

## 文件结构

大多数提供商将每个资源保存在一个包中：

```
internal/provider/
├── provider.go                  # 提供商模式 + Configure
├── widget_resource.go           # 资源实现
├── widget_resource_test.go      # 接受测试
├── widget_data_source.go        # 数据源（如果适用）
└── widget_data_source_test.go
```

大型多服务提供商（例如 terraform-provider-aws）会分成 `internal/service/<service>/` 包，一旦包增长，就应该采用一种惯用的文件分类：`consts.go`，`find.go`（查找器），`status.go`（状态函数），`wait.go`（等待器），`sweep.go`（测试清理器），`exports_test.go`。

文档位于 `docs/` 中，并使用 `tfplugindocs` 生成：

```
docs/
├── resources/<name>.md          # 生成的；可选 <name>.md.tmpl 模板
└── data-sources/<name>.md
```

（在一些较旧的大型提供商中存在手写的 `website/docs/r/*.html.markdown` 树——编辑其中一个时，请遵循目标存储库的约定。）

## 资源结构

框架资源是一个包含 API 客户端的 struct，接口断言使实现的行为明确：

```go
var (
    _ resource.Resource                = &widgetResource{}
    _ resource.ResourceWithConfigure   = &widgetResource{}
    _ resource.ResourceWithImportState = &widgetResource{}
)

func NewWidgetResource() resource.Resource {
    return &widgetResource{}
}

type widgetResource struct {
    client *examplecloud.Client
}

func (r *widgetResource) Metadata(_ context.Context, req resource.MetadataRequest, resp *resource.MetadataResponse) {
    resp.TypeName = req.ProviderTypeName + "_widget"
}

// Configure 接收提供商在其 Configure 中构建的客户端
func (r *widgetResource) Configure(_ context.Context, req resource.ConfigureRequest, resp *resource.ConfigureResponse) {
    if req.ProviderData == nil {
        return // 提供商尚未配置（例如验证阶段）
    }
    client, ok := req.ProviderData.(*examplecloud.Client)
    if !ok {
        resp.Diagnostics.AddError(
            "意外的资源 Configure 类型",
            fmt.Sprintf("预期 *examplecloud.Client，得到: %T.", req.ProviderData),
        )
        return
    }
    r.client = client
}

func (r *widgetResource) Schema(ctx context.Context, req resource.SchemaRequest, resp *resource.SchemaResponse) {
    resp.Schema = schema.Schema{
        Attributes: map[string]schema.Attribute{
            "name": schema.StringAttribute{
                Required: true,
                PlanModifiers: []planmodifier.String{
                    stringplanmodifier.RequiresReplace(),
                },
                Validators: []validator.String{
                    stringvalidator.LengthBetween(1, 255),
                },
            },
            "id": schema.StringAttribute{
                Computed: true,
                PlanModifiers: []planmodifier.String{
                    stringplanmodifier.UseStateForUnknown(),
                },
            },
        },
    }
}
```

提供商的 `Configure` 如何生成该客户端——模式、凭证解析、验证——由 `provider-configuration` 技能（如果可用）涵盖。

**关于 `id`：** SDKv2 要求一个魔法 `id` 属性；框架不需要。如果 API 有自己的标识符，请在其真实含义下暴露它，不要添加一个第二、冗余的 `id`。只有当它是 API 的标识符时才保留 `id`（如上所示）。

## CRUD 操作

### 创建

```go
func (r *widgetResource) Create(ctx context.Context, req resource.CreateRequest, resp *resource.CreateResponse) {
    var data widgetResourceModel
    resp.Diagnostics.Append(req.Plan.Get(ctx, &data)...)
    if resp.Diagnostics.HasError() {
        return
    }

    input := &examplecloud.CreateWidgetInput{
        Name: data.Name.ValueStringPointer(),
    }

    output, err := r.client.CreateWidget(ctx, input)
    if err != nil {
        resp.Diagnostics.AddError(
            "创建 Widget 错误",
            fmt.Sprintf("创建 Widget (%s): %s", data.Name.ValueString(), err),
        )
        return
    }

    data.ID = types.StringPointerValue(output.ID)

    // 对于最终一致性 API，在返回之前等待资源可用——参见 references/retries-and-waiters.md。

    resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}
```

### 读取

读取必须处理带外删除，通过从状态中删除资源，以便下一个计划重新创建它，而不是永远出错：

```go
func (r *widgetResource) Read(ctx context.Context, req resource.ReadRequest, resp *resource.ReadResponse) {
    var data widgetResourceModel
    resp.Diagnostics.Append(req.State.Get(ctx, &data)...)
    if resp.Diagnostics.HasError() {
        return
    }

    output, err := findWidgetByID(ctx, r.client, data.ID.ValueString())
    if isNotFound(err) {
        tflog.Warn(ctx, "Widget 未找到，从状态中移除", map[string]any{"id": data.ID.ValueString()})
        resp.State.RemoveResource(ctx)
        return
    }
    if err != nil {
        resp.Diagnostics.AddError(
            "读取 Widget 错误",
            fmt.Sprintf("读取 Widget (%s): %s", data.ID.ValueString(), err),
        )
        return
    }

    data.Name = types.StringPointerValue(output.Name)

    resp.Diagnostics.Append(resp.State.Set(ctx, &data)...)
}
```

### 更新

仅调用 API 更改的属性；比较计划与状态：

```go
func (r *widgetResource) Update(ctx context.Context, req resource.UpdateRequest, resp *resource.UpdateResponse) {
    var plan, state widgetResourceModel
    resp.Diagnostics.Append(req.Plan.Get(ctx, &plan)...)
    resp.Diagnostics.Append(req.State.Get(ctx, &state)...)
    if resp.Diagnostics.HasError() {
        return
    }

    if !plan.Description.Equal(state.Description) {
        input := &examplecloud.UpdateWidgetInput{
            ID:          plan.ID.ValueStringPointer(),
            Description: plan.Description.ValueStringPointer(),
        }
        if _, err := r.client.UpdateWidget(ctx, input); err != nil {
            resp.Diagnostics.AddError(
                "更新 Widget 错误",
                fmt.Sprintf("更新 Widget (%s): %s", plan.ID.ValueString(), err),
            )
            return
        }
    }

    resp.Diagnostics.Append(resp.State.Set(ctx, &plan)...)
}
```

### 删除

将“已消失”视为成功——达到期望的最终状态：

```go
func (r *widgetResource) Delete(ctx context.Context, req resource.DeleteRequest, resp *resource.DeleteResponse) {
    var data widgetResourceModel
    resp.Diagnostics.Append(req.State.Get(ctx, &data)...)
    if resp.Diagnostics.HasError() {
        return
    }

    _, err := r.client.DeleteWidget(ctx, &examplecloud.DeleteWidgetInput{
        ID: data.ID.ValueStringPointer(),
    })
    if isNotFound(err) {
        return
    }
    if err != nil {
        resp.Diagnostics.AddError(
            "删除 Widget 错误",
            fmt.Sprintf("删除 Widget (%s): %s", data.ID.ValueString(), err),
        )
        return
    }
}
```

### 导入

通过 `ResourceWithImportState` 断言，标识符的传递是一行：

```go
func (r *widgetResource) ImportState(ctx context.Context, req resource.ImportStateRequest, resp *resource.ImportStateResponse) {
    resource.ImportStatePassthroughID(ctx, path.Root("id"), req, resp)
}
```

对于多部分标识符，解析分隔的导入 ID（通常用逗号分隔），并显式设置每个属性。

## 资源设计原则

在实现之前，检查正在建模对象的形状（完整处理在 `references/design-principles.md` 中）：

- 资源是*最小*的有用构建块；如果 API 为其提供 CRUD，它可能值得拥有自己的资源。
- 资源应该只与**一个** API/服务通信——跨服务资源会破坏权限、审计和端点配置。
- 数据源是只读的，没有副作用。*单个*数据源在零个或多个匹配时出错；*复数*数据源（复数名词名称）返回零个或多个作为集合，并在两者都不匹配时出错。
- 附加的策略/规则、长时间运行的任务调用和版本化工件通常值得拥有*自己的*资源，而不是父属性的属性。
- 启动/停止或启用/禁用状态应作为资源中的属性，而不是作为单独的资源。

## 模式设计

### 属性类型

| Terraform 类型 | 框架类型 | 用例 |
|----------------|----------------|----------|
| `string` | `schema.StringAttribute` | 名称、标识符 |
| `number` | `schema.Int64Attribute`, `schema.Float64Attribute` | 计数、大小 |
| `bool` | `schema.BoolAttribute` | 功能标志 |
| `list` | `schema.ListAttribute` | 有序集合 |
| `set` | `schema.SetAttribute` | 无序唯一项 |
| `map` | `schema.MapAttribute` | 键值对 |
| `object` | `schema.SingleNestedAttribute` | 复杂嵌套配置 |

给每个属性一个 `MarkdownDescription`——`tfplugindocs` 会发布它，它是面向用户的主要文档。

### 计划修饰符

```go
// 当值变化时强制替换
stringplanmodifier.RequiresReplace()

// 在计划期间保持已知值，而不是（应用后已知）
stringplanmodifier.UseStateForUnknown()
```

### 验证器

```go
stringvalidator.LengthBetween(1, 255)
stringvalidator.RegexMatches(regexp.MustCompile(`^[a-z0-9-]+$`), "必须是小写字母数字，带连字符")
stringvalidator.OneOf("small", "medium", "large")
int64validator.Between(1, 100)
listvalidator.SizeAtLeast(1)
```

### 敏感属性

```go
"password": schema.StringAttribute{
    Required:  true,
    Sensitive: true,
},
```

## 状态管理

### 查找器

将“获取一个或类型的未找到”集中到一个查找器中，以便读取、删除、等待器和测试都共享相同的未找到语义：

```go
func findWidgetByID(ctx context.Context, client *examplecloud.Client, id string) (*examplecloud.Widget, error) {
    output, err := client.GetWidget(ctx, &examplecloud.GetWidgetInput{ID: &id})
    if err != nil {
        var apiErr *examplecloud.NotFoundError
        if errors.As(err, &apiErr) {
            return nil, &retry.NotFoundError{LastError: err}
        }
        return nil, fmt.Errorf("获取 Widget (%s): %w", id, err)
    }
    if output == nil || output.Widget == nil {
        return nil, &retry.NotFoundError{Message: "空结果"}
    }
    return output.Widget, nil
}

func isNotFound(err error) bool {
    var nfe *retry.NotFoundError
    return errors.As(err, &nfe)
}
```

### 等待资源状态

许多 API 在创建/删除之前返回，此时资源不可用/已消失。使用 `retry.StateChangeConf`（来自 `github.com/hashicorp/terraform-plugin-sdk/v2/helper/retry`——框架提供商可用），使用基于查找器的状态函数和命名常量中的超时：

```go
stateConf := &retry.StateChangeConf{
    Pending: []string{"CREATING", "PENDING"},
    Target:  []string{"ACTIVE"},
    Refresh: statusWidget(ctx, r.client, id), // 查找器的一次轮询： (obj, status, err)
    Timeout: widgetCreatedTimeout,
}
outputRaw, err := stateConf.WaitForStateContext(ctx)
```

完整的状态/等待函数对（创建和删除等待器、失败状态处理、创建后未找到重试、最终一致性模式）在 `references/retries-and-waiters.md` 中——每当 API 是异步的或最终一致性时，请阅读它。

## 测试

每个资源至少包含：

- **`_basic`** — 使用最小配置创建，断言属性，然后是一个导入步骤（`ImportState: true`，`ImportStateVerify: true`）
- **`_disappears`** — 在测试期间带外删除对象；下一个计划必须提议重新创建，而不是出错
- **按属性测试** — 对每个非平凡参数执行更新

命名语法：测试 `TestAcc{Resource}_{group?}_{description}`，帮助函数 `testAccCheck{Resource}Exists` / `testAccCheck{Resource}Destroy`，配置函数 `testAcc{Resource}Config_{description}`。保持配置自包含，随机化真实资源名称，并且永远不要硬编码特定于环境的值（账户 ID、区域、版本）。

```go
func TestAccWidget_basic(t *testing.T) {
    rName := acctest.RandStringFromCharSet(10, acctest.CharSetAlphaNum)
    resourceName := "examplecloud_widget.test"

    resource.ParallelTest(t, resource.TestCase{
        PreCheck:                 func() { testAccPreCheck(t) },
        ProtoV6ProviderFactories: testAccProtoV6ProviderFactories,
        CheckDestroy:             testAccCheckWidgetDestroy,
        Steps: []resource.TestStep{
            {
                Config: testAccWidgetConfig_basic(rName),
                ConfigStateChecks: []statecheck.StateCheck{
                    statecheck.ExpectKnownValue(resourceName, tfjsonpath.New("name"), knownvalue.StringExact(rName)),
                    statecheck.ExpectKnownValue(resourceName, tfjsonpath.New("id"), knownvalue.NotNull()),
                },
            },
            {
                ResourceName:      resourceName,
                ImportState:       true,
                ImportStateVerify: true,
            },
        },
    })
}

func testAccWidgetConfig_basic(rName string) string {
    return fmt.Sprintf(`
resource "examplecloud_widget" "test" {
  name = %[1]q
}
`, rName)
}
```

使用 `provider-test-patterns` 技能（如果可用）进行完整测试处理：配置帮助函数样式（`%[1]q` 索引动词），statecheck/plancheck，CompareValue，自定义 StateCheck 实现用于存在/消失帮助函数，清理器和临时资源测试。使用 `run-acceptance-tests` 技能执行和调试测试运行。

## 错误处理

按类型匹配 API 错误，而不是消息文本，并包装上下文：

```go
var notFound *examplecloud.NotFoundError
if errors.As(err, &notFound) {
    // 资源不存在
}

// 在帮助函数中包装：使用 %w 保留原因
return fmt.Errorf("创建 Widget (%s): %w", name, err)
```

诊断遵循一致的语法——摘要名称操作和类型，详细信息包含标识符和原因：

```go
resp.Diagnostics.AddError(
    "创建 Widget 错误",
    fmt.Sprintf("创建 Widget (%s): %s", name, err),
)

resp.Diagnostics.AddAttributeError(
    path.Root("name"),
    "无效的名称",
    "名称必须是小写字母数字",
)
```

## 文档

首先编写属性 `MarkdownDescription`——它们是事实来源。然后使用 `tfplugindocs` 生成注册表文档（`go generate ./...` 在连接处），仅添加 `docs/**/*.md.tmpl` 模板用于生成器无法派生的文本和示例。使用 `provider-docs` 技能（如果可用）进行完整文档工作流程和注册表发布规则。

## 提交前检查清单

- [ ] 使用插件框架（没有新的 SDKv2 代码）
- [ ] 资源实现了所有 CRUD 操作
- [ ] 读取从状态中移除缺失资源；删除容忍已删除
- [ ] 没有冗余的 `id` 属性（暴露真实 API 标识符而不是）
- [ ] 导入已实现并受 `ImportStateVerify` 步骤覆盖
- [ ] `_basic`，`_disappears` 和按属性测试存在
- [ ] API 是最终一致性时使用等待器
- [ ] 错误消息命名操作、类型和标识符
- [ ] 标记敏感属性；每个属性都有一个描述
- [ ] 使用 `tfplugindocs` 生成文档
- [ ] 添加了变更日志条目，如果存储库跟踪发布说明（检查 CONTRIBUTING）

## 参考文献

- [Terraform 插件框架](https://developer.hashicorp.com/terraform/plugin/framework)
- [资源开发](https://developer.hashicorp.com/terraform/plugin/framework/resources)
- [数据源开发](https://developer.hashicorp.com/terraform/plugin/framework/data-sources)
- [HashiCorp 提供商设计原则](https://developer.hashicorp.com/terraform/plugin/best-practices/hashicorp-provider-design-principles)
