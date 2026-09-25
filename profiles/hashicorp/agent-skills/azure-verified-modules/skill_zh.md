# Azure 验证模块 (AVM) 要求

本指南涵盖了 Azure 验证模块认证的强制性要求。这些要求确保了 Azure Terraform 模块的一致性、质量和可维护性。

**参考资料：**
- [Azure 验证模块](https://azure.github.io/Azure-Verified-Modules/)
- [AVM 模块规范](https://azure.github.io/Azure-Verified-Modules/specs/module-specs/)

## 目录

- [模块交叉引用](#模块交叉引用)
- [Azure 提供商要求](#azure提供商要求)
- [代码风格标准](#代码风格标准)
- [变量要求](#变量要求)
- [输出要求](#输出要求)
- [本地值标准](#本地值标准)
- [Terraform 配置要求](#terraform配置要求)
- [测试要求](#测试要求)
- [文档要求](#文档要求)
- [破坏性变更与功能管理](#破坏性变更--功能管理)
- [贡献标准](#贡献标准)
- [合规性检查清单](#合规性检查清单)

---

## 模块交叉引用

**严重性：** 必须执行 | **要求：** TFFR1

在构建资源或模式模块时，模块所有者**可以**交叉引用其他模块。但是：

- 模块**必须**使用 HashiCorp Terraform 注册中心引用到固定版本
  - 示例：`source = "Azure/xxx/azurerm"` 与 `version = "1.2.3"`
- 模块**不得**使用 git 引用（例如，`git::https://xxx.yyy/xxx.git` 或 `github.com/xxx/yyy`）
- 模块**不得**包含对非 AVM 模块的引用

---

## Azure 提供商要求

**严重性：** 必须执行 | **要求：** TFFR3

作者**必须**仅使用以下 Azure 提供商：

| 提供商 | 最小版本 | 最大版本 |
|----------|-------------|-------------|
| azapi    | >= 2.0      | < 3.0       |
| azurerm  | >= 4.0      | < 5.0       |

**要求：**

- 作者**可以**选择 Azurerm、Azapi 或两者
- **必须**使用 `required_providers` 块来强制执行提供商版本
- **应该**使用悲观版本约束运算符（`~>`）

**示例：**

```hcl
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
    azapi = {
      source  = "Azure/azapi"
      version = "~> 2.0"
    }
  }
}
```

---

## 代码风格标准

### 小驼峰命名法

**严重性：** 必须执行 | **要求：** TFNFR4

**必须**使用小驼峰命名法：

- 本地变量
- 变量
- 输出
- 资源（符号名称）
- 模块（符号名称）

示例：`snake_casing_example`

### 资源与数据源排序

**严重性：** 应该执行 | **要求：** TFNFR6

- 依赖的资源**应该**首先出现
- 具有依赖关系的资源**应该**彼此定义靠近

### count 与 for_each 的使用

**严重性：** 必须执行 | **要求：** TFNFR7

- 使用 `count` 进行条件资源创建
- **必须**使用 `map(xxx)` 或 `set(xxx)` 作为资源的 `for_each` 集合
- 映射的键或集合的元素**必须**是静态文字

**示例：**

```hcl
resource "azurerm_subnet" "pair" {
  for_each             = var.subnet_map  # map(string)
  name                 = "${each.value}-pair"
  resource_group_name  = azurerm_resource_group.example.name
  virtual_network_name = azurerm_virtual_network.example.name
  address_prefixes     = ["10.0.1.0/24"]
}
```

### 资源与数据块内部排序

**严重性：** 应该执行 | **要求：** TFNFR8

资源/数据块内的顺序：

1. **元参数（顶部）**：
   - `provider`
   - `count`
   - `for_each`

2. **参数/块（中间，按字母顺序）**：
   - 必要参数
   - 可选参数
   - 必要嵌套块
   - 可选嵌套块

3. **元参数（底部）**：
   - `depends_on`
   - `lifecycle`（子顺序：`create_before_destroy`、`ignore_changes`、`prevent_destroy`）

用空行分隔各部分。

### 模块块排序

**严重性：** 应该执行 | **要求：** TFNFR9

模块块内的顺序：

1. **顶部元参数**：
   - `source`
   - `version`
   - `count`
   - `for_each`

2. **参数（按字母顺序）**：
   - 必要参数
   - 可选参数

3. **底部元参数**：
   - `depends_on`
   - `providers`

### lifecycle ignore_changes 语法

**严重性：** 必须执行 | **要求：** TFNFR10

`ignore_changes` 属性**不得**用双引号括起来。

**良好：**

```hcl
lifecycle {
  ignore_changes = [tags]
}
```

**不良：**

```hcl
lifecycle {
  ignore_changes = ["tags"]
}
```

### 条件创建的 Null 比较操作

**严重性：** 应该执行 | **要求：** TFNFR11

对于需要条件资源创建的参数，用 `object` 类型包装以避免计划阶段出现“known after apply”问题。

**推荐：**

```hcl
variable "security_group" {
  type = object({
    id = string
  })
  default = null
}
```

### 可选嵌套对象的动态块

**严重性：** 必须执行 | **要求：** TFNFR12

在条件下的嵌套块**必须**使用此模式：

```hcl
dynamic "identity" {
  for_each = <condition> ? [<some_item>] : []

  content {
    # 块内容
  }
}
```

### coalesce/try 的默认值

**严重性：** 应该执行 | **要求：** TFNFR13

**良好：**

```hcl
coalesce(var.new_network_security_group_name, "${var.subnet_name}-nsg")
```

**不良：**

```hcl
var.new_network_security_group_name == null ? "${var.subnet_name}-nsg" : var.new_network_security_group_name
```

### 模块中的提供商声明

**严重性：** 必须执行 | **要求：** TFNFR27

- `provider` **不得**在模块中声明（`configuration_aliases` 除外）
- 模块中的 `provider` 块**必须**仅使用 `alias`
- 提供商配置**应该**由模块用户传递

---

## 变量要求

### 不允许的变量

**严重性：** 必须执行 | **要求：** TFNFR14

模块所有者**不得**添加 `enabled` 或 `module_depends_on` 等变量来控制整个模块操作。特定资源的布尔功能开关是可接受的。

### 变量定义顺序

**严重性：** 应该执行 | **要求：** TFNFR15

变量**应该**遵循以下顺序：

1. 所有必需字段（按字母顺序）
2. 所有可选字段（按字母顺序）

### 变量命名规则

**严重性：** 应该执行 | **要求：** TFNFR16

- 遵循 [HashiCorp 的命名规则](https://www.terraform.io/docs/extend/best-practices/naming.html)
- 功能开关**应该**使用肯定陈述：`xxx_enabled` 而不是 `xxx_disabled`

### 带描述的变量

**严重性：** 应该执行 | **要求：** TFNFR17

- `description` **应该**精确描述参数的用途和预期数据类型
- 目标受众是模块用户，而不是开发者
- 对于 `object` 类型，使用 HEREDOC 格式

### 带类型的变量

**严重性：** 必须执行 | **要求：** TFNFR18

- 每个变量**必须**定义 `type`
- `type` **应该**尽可能精确
- `any` **可以**仅在有充分理由时使用
- 对于 true/false 值，使用 `bool` 而不是 `string`/`number`
- 使用具体的 `object` 而不是 `map(any)`

### 敏感数据变量

**严重性：** 应该执行 | **要求：** TFNFR19

如果变量的类型是 `object` 且包含敏感字段，整个变量**应该**为 `sensitive = true`，或者将敏感字段提取到单独的变量中。

### 集合的非空默认值

**严重性：** 应该执行 | **要求：** TFNFR20

在循环中使用集合值（集合、映射、列表）时，`nullable` **应该**设置为 `false`。对于标量值，null 可能具有语义意义。

### 默认情况下避免 Null 性

**严重性：** 必须执行 | **要求：** TFNFR21

`nullable = true` **必须**避免，除非有特定语义需求使用 null 值。

### 避免使用 sensitive = false

**严重性：** 必须执行 | **要求：** TFNFR22

`sensitive = false` **必须**避免（这是默认值）。

### 敏感默认值条件

**严重性：** 必须执行 | **要求：** TFNFR23

敏感输入**不得**设置默认值（例如，默认密码）。

### 处理已弃用的变量

**严重性：** 必须执行 | **要求：** TFNFR24

- 将已弃用的变量移动到 `deprecated_variables.tf`
- 在描述开头标注 `DEPRECATED`
- 声明替换名称
- 在主要版本发布期间清理

---

## 输出要求

### 额外的 Terraform 输出

**严重性：** 应该执行 | **要求：** TFFR2

作者**不应该**输出整个资源对象，因为它们可能包含敏感数据，并且 API 或提供商版本更改时架构也可能更改。

**最佳实践：**

- 输出资源的计算属性作为独立输出（反腐败层模式）
- **不应该**输出已经是输入的值（`name` 除外）
- 使用 `sensitive = true` 对敏感属性
- 对于使用 `for_each` 部署的资源，以映射结构输出计算属性

**示例：**

```hcl
# 单个资源计算属性
output "foo" {
  description = "MyResource foo 属性"
  value       = azurerm_resource_myresource.foo
}

# for_each 资源
output "childresource_foos" {
  description = "MyResource 子资源的 foo 属性"
  value = {
    for key, value in azurerm_resource_mychildresource : key => value.foo
  }
}

# 敏感输出
output "bar" {
  description = "MyResource bar 属性"
  value       = azurerm_resource_myresource.bar
  sensitive   = true
}
```

### 敏感数据输出

**严重性：** 必须执行 | **要求：** TFNFR29

包含机密数据的输出**必须**声明 `sensitive = true`。

### 处理已弃用的输出

**严重性：** 必须执行 | **要求：** TFNFR30

- 将已弃用的输出移动到 `deprecated_outputs.tf`
- 在 `outputs.tf` 中定义新输出
- 在主要版本发布期间清理

---

## 本地值标准

### locals.tf 组织

**严重性：** 可以执行 | **要求：** TFNFR31

- `locals.tf` **应该**仅包含 `locals` 块
- **可以**在资源旁边声明 `locals` 块以用于高级场景

### 按字母顺序排列本地值

**严重性：** 必须执行 | **要求：** TFNFR32

`locals` 块中的表达式**必须**按字母顺序排列。

### 精确本地类型

**严重性：** 应该执行 | **要求：** TFNFR33

使用精确类型（例如，`number` 用于年龄，而不是 `string`）。

---

## Terraform 配置要求

### Terraform 版本要求

**严重性：** 必须执行 | **要求：** TFNFR25

`terraform.tf` 要求：

- **必须**仅包含一个 `terraform` 块
- 第一行**必须**定义 `required_version`
- **必须**包含最小版本约束
- **必须**包含最大主版本约束
- **应该**使用 `~> #.#` 或 `>= #.#.#, < #.#.#` 格式

**示例：**

```hcl
terraform {
  required_version = "~> 1.6"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}
```

### required_providers 中的提供商

**严重性：** 必须执行 | **要求：** TFNFR26

- `terraform` 块**必须**包含 `required_providers` 块
- 每个提供商**必须**指定 `source` 和 `version`
- 提供商**应该**按字母顺序排列
- 仅包含直接需要的提供商
- `source` **必须**为 `namespace/name` 格式
- `version` **必须**包含最小和最大主版本约束
- **应该**使用 `~> #.#` 或 `>= #.#.#, < #.#.#` 格式

---

## 测试要求

### 测试工具

**严重性：** 必须执行 | **要求：** TFNFR5

AVM 需要的测试工具：

- Terraform (`terraform validate/fmt/test`)
- terrafmt
- Checkov
- tflint（带 azurerm 规则集）
- Go（可选用于自定义测试）

### 测试提供商配置

**严重性：** 应该执行 | **要求：** TFNFR36

为了进行稳健的测试，`prevent_deletion_if_contains_resources` 在测试提供商配置中**应该**显式设置为 `false`。

---

## 文档要求

### 模块文档生成

**严重性：** 必须执行 | **要求：** TFNFR2

- 文档**必须**通过 [Terraform Docs](https://github.com/terraform-docs/terraform-docs) 自动生成
- 模块根目录中**必须**存在 `.terraform-docs.yml` 文件

---

## 破坏性变更与功能管理

### 使用功能开关

**严重性：** 必须执行 | **要求：** TFNFR34

在次要/补丁版本中添加的新资源**必须**具有开关变量以避免默认创建：

```hcl
variable "create_route_table" {
  type     = bool
  default  = false
  nullable = false
}

resource "azurerm_route_table" "this" {
  count = var.create_route_table ? 1 : 0
  # ...
}
```

### 审查潜在的破坏性变更

**严重性：** 必须执行 | **要求：** TFNFR35

需要谨慎处理的破坏性变更：

**资源块：**

1. 添加新资源而不进行条件创建
2. 添加具有非默认值的参数
3. 添加没有 `dynamic` 的嵌套块
4. 未使用 `moved` 块重命名资源
5. 将 `count` 更改为 `for_each` 或反之

**变量/输出块：**

1. 删除/重命名变量
2. 更改变量 `type`
3. 更改变量 `default` 值
4. 将 `nullable` 更改为 false
5. 将 `sensitive` 从 false 更改为 true
6. 添加没有 `default` 的变量
7. 删除输出
8. 更改输出 `value`
9. 更改输出 `sensitive` 值

---

## 贡献标准

### GitHub 仓库分支保护

**严重性：** 必须执行 | **要求：** TFNFR3

模块所有者**必须**在默认分支（通常是 `main`）上设置分支保护策略：

1. 合并前需要 Pull Request
2. 需要最近可审查推送的批准
3. 当有新提交时忽略过时的 PR 批准
4. 需要线性历史记录
5. 防止强制推送
6. 不允许删除
7. 需要CODEOWNERS审查
8. 不允许绕过设置
9. 对管理员强制执行

---

## 合规性检查清单

在开发或审查 Azure 验证模块时使用此检查清单：

### 模块结构
- [ ] 模块交叉引用使用注册源并固定版本
- [ ] Azure 提供商（azurerm/azapi）版本符合 AVM 要求
- [ ] 模块根目录中存在 `.terraform-docs.yml`
- [ ] 存在 CODEOWNERS 文件

### 代码风格
- [ ] 所有名称使用小驼峰命名法
- [ ] 资源按依赖关系排序
- [ ] `for_each` 使用 `map()` 或 `set()` 并具有静态键
- [ ] 资源/数据块遵循正确的内部排序
- [ ] `ignore_changes` 未加引号
- [ ] 使用动态块进行条件嵌套对象
- [ ] 使用 `coalesce()` 或 `try()` 进行默认值

### 变量
- [ ] 没有 `enabled` 或 `module_depends_on` 变量
- [ ] 变量按顺序：必需（按字母顺序）然后可选（按字母顺序）
- [ ] 所有变量都有精确类型（避免 `any`）
- [ ] 所有变量都有描述
- [ ] 集合的 `nullable` 为 false
- [ ] 没有 `sensitive = false` 声明
- [ ] 没有对敏感输入设置默认值
- [ ] 已弃用的变量已移动到 `deprecated_variables.tf`

### 输出
- [ ] 输出使用反腐败层模式（离散属性）
- [ ] 敏感输出标记 `sensitive = true`
- [ ] 已弃用的输出已移动到 `deprecated_outputs.tf`

### Terraform 配置
- [ ] `terraform.tf` 包含版本约束（`~>` 格式）
- [ ] `required_providers` 块包含所有提供商
- [ ] 模块中未声明 `provider`（`configuration_aliases` 除外）
- [ ] 本地值按字母顺序排列

### 测试与质量
- [ ] 配置了所需的测试工具
- [ ] 新资源具有功能开关
- [ ] 审查并记录了破坏性变更

---

## 总结统计

- **功能要求：** 3
- **非功能要求：** 34
- **总要求：** 37

### 按严重性分类
- **必须：** 21 个要求
- **应该：** 14 个要求
- **可以：** 2 个要求

---

*基于：Azure 验证模块 - Terraform 要求*
