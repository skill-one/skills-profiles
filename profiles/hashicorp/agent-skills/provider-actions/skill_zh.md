# Terraform 提供商操作实现指南

## 概述

Terraform Actions 可在 Terraform 生命周期中执行命令式操作。Actions 是一项实验性功能，允许在特定的生命周期事件（创建前/后、更新前/后、销毁前/后）执行提供商操作。

**参考资料：**
- [Terraform 插件框架](https://developer.hashicorp.com/terraform/plugin/framework)
- [Terraform 插件框架 Actions](https://developer.hashicorp.com/terraform/plugin/framework/actions)

## 首次操作设置

当向从未有过 Actions 的提供商添加首个 Action 时，需要执行以下一次性脚手架步骤：

1. **实现 `ProviderWithActions`** — 向提供商添加一个返回 `[]func() action.Action` 的 `Actions()` 方法。
2. **在 `Configure` 中设置 `ActionData`** — 提供商的 `Configure` 方法必须与现有的 `ResourceData`、`DataSourceData` 和 `EphemeralResourceData` 赋值一起设置 `resp.ActionData = v`。
3. **创建 `ActionWithConfigure` 基类型** — 如果提供商使用嵌入式基类型（例如 `ResourceWithConfigure`），则需要创建一个实现 `action.ConfigureRequest` / `action.ConfigureResponse` 的等效 `ActionWithConfigure` 类型。
4. **Action-schema 辅助函数变体** — 如果提供商通过辅助函数注入通用模式属性（例如 `namespace`），则需要 Action-schema 变体，因为 `action/schema` 类型与 `resource/schema` 类型不同。

## 文件结构

大多数提供商将 Actions 与资源一起保存在提供商包中：

```
internal/provider/
├── <action_name>_action.go       # Action 实现
└── <action_name>_action_test.go  # Action 测试
```

（大型多服务提供商使用 `internal/service/<service>/` 包——遵循目标存储库的布局。）

文档与其他生成的文档一起存放：
```
docs/actions/
└── <action_name>.md              # 面向用户的文档
```

（一些较旧的、大型提供商手动编写 `website/docs/actions/<name>.html.markdown`——匹配存储库。）

## Action 模式定义

Actions 使用 Terraform 插件框架和标准模式：

```go
func (a *actionType) Schema(ctx context.Context, req action.SchemaRequest, resp *action.SchemaResponse) {
    resp.Schema = schema.Schema{
        Attributes: map[string]schema.Attribute{
            // 必要的配置参数
            "resource_id": schema.StringAttribute{
                Required:    true,
                Description: "要操作的资源的 ID",
            },
            // 带有默认值的可选参数
            "timeout": schema.Int64Attribute{
                Optional:    true,
                Description: "操作超时时间（秒）",
                Default:     int64default.StaticInt64(1800),
                Computed:    true,
            },
        },
    }
}
```

### 常见模式问题

**特别注意模式定义**——首次草稿后常见的常见问题：

1. **类型不匹配**
   - 模型结构体使用 `types.String`/`types.Int64`，而模式使用
     `types.StringType` 来自
     `github.com/hashicorp/terraform-plugin-framework/types`——不要混用来自其他包的类型
   - 一些大型提供商在其自定义类型包上分层（例如
     terraform-provider-aws 的内部 `fwtypes`）；在这样存储库中，
     一致遵循其约定，而不是纯类型

2. **列表/映射元素类型**
   ```go
   // 错误——缺少 ElementType
   "items": schema.ListAttribute{
       Optional: true,
   }

   // 正确
   "items": schema.ListAttribute{
       Optional:    true,
       ElementType: types.StringType,
   }
   ```

3. **计算与可选**
   - 具有默认值的属性必须同时 `Optional: true` 和 `Computed: true`
   - 除非它们有默认值，否则不要将 Action 输入标记为 `Computed`

4. **验证器导入**
   ```go
   // 确保正确的导入
   "github.com/hashicorp/terraform-plugin-framework-validators/int64validator"
   "github.com/hashicorp/terraform-plugin-framework-validators/stringvalidator"
   ```

5. **区域/提供商属性**（多区域提供商，例如 AWS）
   - 如果提供商有共享区域处理，请使用它
   - 不要在 Action 模式中手动重新定义提供商级配置

6. **嵌套属性**
   - 使用适当的嵌套对象类型处理复杂结构
   - 确保嵌套类型正确定义

### 模式验证清单

提交前验证：
- [ ] 所有属性都有描述
- [ ] 列表/映射属性有 `ElementType` 定义
- [ ] 验证器已导入并正确应用
- [ ] 模型结构体使用正确的框架类型
- [ ] 带有默认值的可选属性被标记为 `Computed`
- [ ] 代码编译没有类型错误
- [ ] 运行 `go build` 捕获类型不匹配

## Action 调用方法

Invoke 方法包含 Action 逻辑：

```go
func (a *actionType) Invoke(ctx context.Context, req action.InvokeRequest, resp *action.InvokeResponse) {
    var data actionModel
    resp.Diagnostics.Append(req.Config.Get(ctx, &data)...)
    if resp.Diagnostics.HasError() {
        return
    }

    // a.client 由 Configure 存储（来自 req.ProviderData），与资源使用相同模式。
    resp.SendProgress(action.InvokeProgressEvent{Message: "开始操作..."})

    // 实现操作逻辑并处理错误
    // 使用 context 进行超时管理
    // 如果是异步操作，则轮询

    resp.SendProgress(action.InvokeProgressEvent{Message: "操作完成"})
}
```

## 关键实现要求

### 1. 进度报告

- 使用 `resp.SendProgress(action.InvokeProgressEvent{...})` 进行实时更新
- 在长时间操作期间提供有意义的进度消息
- 在关键里程碑更新进度
- 对于长时间操作，包括经过时间

### 2. 超时管理

- 始终包含可配置的超时参数（默认：1800 秒）
- 使用 `context.WithTimeout()` 进行 API 调用
- 优雅地处理超时错误
- 验证超时范围（通常 60-7200 秒）

### 3. 错误处理

- 使用 `resp.Diagnostics.AddError()` 添加诊断
- 提供带上下文的清晰错误消息
- 在相关情况下包含 API 错误详细信息
- 将提供商错误类型映射到用户友好消息
- 记录所有可能的错误情况

示例错误处理：
```go
// 处理特定错误
var notFound *types.ResourceNotFoundException
if errors.As(err, &notFound) {
    resp.Diagnostics.AddError(
        "资源未找到",
        fmt.Sprintf("资源 %s 未找到", resourceID),
    )
    return
}

// 通用错误处理
resp.Diagnostics.AddError(
    "操作失败",
    fmt.Sprintf("无法完成 %s 的操作: %s", resourceID, err),
)
```

### 4. 提供商 SDK 集成

- 使用 Configure 时存储的 API 客户端（`a.client`），与资源和数据源共享
- 处理列表操作的分页
- 实现对瞬时失败的重试逻辑
- 使用适当的错误类型

### 5. 参数验证

- 使用框架验证器进行输入验证
- 在操作前验证资源存在
- 检查冲突参数
- 验证符合提供商命名要求

### 6. 轮询和等待

对于需要等待完成的操作，在上下文截止日期下使用计时器轮询，并报告进度。 （或者使用
`retry.StateChangeConf` 来自
`github.com/hashicorp/terraform-plugin-sdk/v2/helper/retry`，与资源使用的相同等待原语。）

```go
ctx, cancel := context.WithTimeout(ctx, timeout)
defer cancel()

ticker := time.NewTicker(5 * time.Second)
defer ticker.Stop()

// 快速轮询，慢速报告：进度事件跨插件协议，因此限制它们而不是每个轮询发出一个。
start := time.Now()
var lastProgress time.Time
for {
    res, err := findResource(ctx, a.client, id)
    if err != nil {
        resp.Diagnostics.AddError("轮询操作错误", fmt.Sprintf("检查 %s 状态: %s", id, err))
        return
    }
    switch res.Status {
    case "AVAILABLE", "COMPLETED":
        resp.SendProgress(action.InvokeProgressEvent{Message: "操作完成"})
        return
    case "CREATING", "PENDING":
        if time.Since(lastProgress) >= 30*time.Second {
            lastProgress = time.Now()
            resp.SendProgress(action.InvokeProgressEvent{
                Message: fmt.Sprintf("状态: %s, 经过: %v", res.Status, time.Since(start).Round(time.Second)),
            })
        }
    default:
        resp.Diagnostics.AddError("操作失败", fmt.Sprintf("%s 进入意外状态 %q", id, res.Status))
        return
    }

    select {
    case <-ctx.Done():
        resp.Diagnostics.AddError("操作超时", fmt.Sprintf("%s 在 %v 内未完成", id, timeout))
        return
    case <-ticker.C:
    }
}
```

## 常见 Action 模式

### 批量操作
- 可配置批量处理项目
- 每批报告进度
- 优雅地处理部分失败
- 支持前缀/过滤参数

### 命令执行
- 提交命令并获取操作 ID
- 轮询完成状态
- 获取并报告输出
- 轮询期间处理超时
- 执行前验证资源存在

### 服务调用
- 带参数调用服务
- 同步等待完成（如果同步）
- 返回输出/结果
- 处理服务特定错误

### 资源状态变更
- 验证当前状态
- 应用状态变更
- 轮询目标状态
- 处理过渡状态

### 异步任务提交
- 带配置提交任务
- 获取任务 ID
- 可选地等待完成
- 报告任务状态

## Action 触发器

Actions 通过 Terraform 配置中的 `action_trigger` 生命周期块触发。没有对应触发的独立 `action` 块被声明但从未执行。

### HCL 语法

Action 参数必须用 `config {}` 块包装。触发器引用使用 `action.` 前缀，`actions` 是一个列表。事件是裸标识符，不是引号字符串。

```hcl
action "provider_service_action" "name" {
  config {
    parameter = value
  }
}

resource "terraform_data" "trigger" {
  lifecycle {
    action_trigger {
      events  = [after_create]
      actions = [action.provider_service_action.name]
    }
  }
}
```

### 可用触发器事件

**支持的事件（截至 Terraform 1.14）：**
- `before_create` - 资源创建前
- `after_create` - 资源创建后
- `before_update` - 资源更新前
- `after_update` - 资源更新后

**不支持（截至 Terraform 1.14；检查当前发布说明）：**
- `before_destroy` - 不可用（将导致验证错误）
- `after_destroy` - 不可用（将导致验证错误）

## 测试 Action

### 接受测试

- 使用有效参数测试 Action 调用
- 测试超时场景
- 测试错误条件
- 验证提供商状态变更
- 测试进度报告
- 使用自定义参数测试
- 测试基于触发器的调用

### 测试模式

```go
func TestAccExampleAction_basic(t *testing.T) {
    resource.ParallelTest(t, resource.TestCase{
        PreCheck:                 func() { testAccPreCheck(t) },
        ProtoV6ProviderFactories: testAccProtoV6ProviderFactories,
        TerraformVersionChecks: []tfversion.TerraformVersionCheck{
            tfversion.SkipBelow(tfversion.Version1_14_0),
        },
        Steps: []resource.TestStep{
            {
                Config: testAccActionConfig_basic(),
                ConfigStateChecks: []statecheck.StateCheck{
                    // 断言 Action 对触发资源的影响的观察效果
                },
            },
        },
    })
}
```

### 使用清理函数的测试

测试中调用的 Action 可能会留下真实资源；注册清理器（列表→过滤测试前缀名称→删除）以便泄漏的资源可清理。清理器不是 Action 特定的——如果可用，使用
`provider-test-patterns` 技巧（如果可用）获取清理函数模式、注册、`TestMain` 和依赖排序。

### 使用 `terraform_data` 作为无操作触发器

`terraform_data` 可作为无操作触发器资源，用于不需要真实基础设施的 Action 测试。这对于错误情况和验证测试非常有价值：

```hcl
resource "terraform_data" "trigger" {
  lifecycle {
    action_trigger {
      events  = [after_create]
      actions = [action.provider_service_action.test]
    }
  }
}

action "provider_service_action" "test" {
  config {
    param = "无效值"
  }
}
```

### 使用 `PostApplyFunc` 验证副作用

Action 不会产生可通过 `resource.TestCheckResourceAttr` 检查的状态。在 `resource.TestStep` 上使用 `PostApplyFunc` 在应用后查询 API 并确认 Action 产生了预期的副作用：

```go
Steps: []resource.TestStep{
    {
        Config: testConfig,
        PostApplyFunc: func() {
            // 查询 API 以验证 Action 的副作用发生
        },
    },
},
```

### 测试最佳实践

**服务特定先决条件**
- 始终检查 Action 成功前必须满足的服务特定先决条件
- 在 Action 文档和测试配置中记录先决条件

**错误模式匹配**
- Terraform 用附加上下文包装 Action 错误
- 使用灵活的正则表达式模式：`regexp.MustCompile(\`(?s)Error Title.*key phrase\`)`

**不适用于 Action 的测试模式**
1. Actions 在生命周期事件上触发，而不是配置重新应用
2. Before/After Destroy 测试：截至 Terraform 1.14 不支持

### 运行测试

先编译检查，然后运行聚焦的接受测试：
```bash
go test -c -o /dev/null ./internal/provider
TF_ACC=1 go test ./internal/provider -run TestAccExampleAction_ -timeout 60m
```

如果可用，使用 `run-acceptance-tests` 技巧进行环境变量设置、调试失败测试和清理器运行。

## 文档标准

在提供商使用 `tfplugindocs` 生成 Action 文档（如果可用，使用 `provider-docs` 技巧进行该工作）。每个 Action 文档页面必须包含：

1. **前置内容**（仅限手写遗留布局）
   ```yaml
   ---
   subcategory: "服务名称"
   layout: "provider"
   page_title: "提供商: provider_service_action"
   description: |-
     Action 的简要描述。
   ---
   ```

2. **带警告的标题**
   - 关于实验状态的 Beta/Alpha 通知
   - 关于可能产生意外后果的警告
   - 链接到提供商文档

3. **示例用法**
   - 基本用法示例
   - 带所有选项的高级用法示例
   - 基于 `terraform_data` 的触发器示例
   - 真实用例示例

4. **参数参考**
   - 列出所有必需和可选参数
   - 包括描述和默认值
   - 注解任何验证规则

5. **文档检查**（可选工具）
   - 如果存储库使用 `terrafmt`，在提交前运行 `terrafmt fmt` 并使用 `terrafmt diff` 验证

## 更改日志条目格式（特定于提供商的约定）

一些提供商（例如 terraform-provider-aws）使用
[go-changelog](https://github.com/hashicorp/go-changelog) 跟踪发布说明：每个 PR 在 `.changelog/` 目录中的一个文件。检查目标存储库的 CONTRIBUTING 指南；如果存储库不使用它，则跳过此步骤。

```
.changelog/<pr_number>.txt
```

内容格式：
```release-note:new-action
action/provider_service_action: Action 的简要描述
```

## 提交前检查清单

在提交 Action 实现前：

- [ ] 代码编译：`go build -o /dev/null .`
- [ ] 测试编译：`go test -c -o /dev/null ./internal/provider`
- [ ] 代码格式化：`gofmt`（或存储库的 `make fmt`）
- [ ] 文档生成或按存储库约定格式化
- [ ] 更改日志条目创建（如果存储库使用）
- [ ] 模式使用正确的类型
- [ ] 所有列表/映射属性都有 `ElementType`
- [ ] 长时间操作实现了进度更新
- [ ] 错误消息包含上下文和资源标识符
- [ ] 文档包含多个示例
- [ ] 文档包含先决条件和警告

## 参考资料

- [Terraform 插件框架文档](https://developer.hashicorp.com/terraform/plugin/framework)
- [Terraform 提供商开发](https://developer.hashicorp.com/terraform/plugin)
- [terraform-plugin-framework GitHub](https://github.com/hashicorp/terraform-plugin-framework)
- [terraform-plugin-testing](https://github.com/hashicorp/terraform-plugin-testing)
- [编写 Terraform Action (博客)](https://danielmschmidt.de/posts/2025-09-26-writing-a-terraform-action/)
- 参考实现：`terraform-provider-tfe` (`action_query_run.go`, `action_query_run_test.go`), `terraform-provider-vault` (`action_rotate_root.go`)
