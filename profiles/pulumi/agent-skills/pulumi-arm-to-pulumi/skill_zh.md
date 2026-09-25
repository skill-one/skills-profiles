## 重要：需要调整计划

**如果您在加载此技能之前已经生成了一个迁移计划，您必须：**

1. 将您的现有计划与该技能中的工作流和需求进行对比
2. 确定任何差距、缺失步骤或错误假设
3. 更新和修订您的计划，以符合该技能的指导
4. 在继续之前向用户传达调整后的计划

## 关键成功要求

迁移输出必须满足以下所有要求：

1. **完整资源覆盖**
   - 每个ARM模板资源必须：
     - 在Pulumi程序中体现 **或**
     - 在最终报告中明确说明。

2. **成功部署**
   - 生成的Pulumi程序必须结构有效，并且能够在配置正确的情况下成功执行 `pulumi preview`。

3. **零差异导入验证**（如果导入现有资源）
   - 导入后，`pulumi preview` 必须显示：
     - 无更新
     - 无替换
     - 无创建
     - 无删除
   - 任何差异必须使用预览解决工作流解决。参见 [arm-import.md](arm-import.md)。

4. **最终迁移报告**
   - 始终输出一份适合Pull Request的正式迁移报告。
   - 包括：
     - ARM → Pulumi资源映射
     - 提供商决策（azure-native vs azure）
     - 行为差异
     - 缺失或手动要求的步骤
     - 验证说明

## 信息缺失时

如果用户提供的ARM模板不完整、模糊或缺少工件，请在生成Pulumi代码之前提出**有针对性的问题**。

如果对如何处理导入时的特定资源属性存在歧义，请在修改Pulumi代码之前提出**有针对性的问题**。

## 迁移工作流

请严格按照以下顺序和流程执行：

### 1. 信息收集

#### 1.1 验证Azure凭证

运行Azure CLI命令（例如，`az resource list`，`az resource show`）。需要使用ESC进行初始登录。

- 如果用户已经提供了ESC环境，请使用它。
- 如果没有指定ESC环境，请**在继续执行Azure CLI命令之前询问用户要使用哪个ESC环境**。

**使用ESC设置Azure CLI：**

- ESC环境可以通过环境变量或Azure CLI配置提供Azure凭证
- 使用ESC登录Azure以提供凭证，例如：`pulumi env run {org}/{project}/{environment} -- bash -c 'az login --service-principal -u "$ARM_CLIENT_ID" --tenant "$ARM_TENANT_ID" --federated-token "$ARM_OIDC_TOKEN"'`。建立会话后不需要ESC
- 验证凭证是否正常工作：`az account show`
- 确认订阅：`az account list --query "[].{Name:name, SubscriptionId:id, IsDefault:isDefault}" -o table`

**有关详细ESC信息：** 通过调用名为"Skill"的工具，加载 `pulumi-esc` 技能，名称 = "pulumi-esc"

#### 1.2 分析ARM模板结构

ARM模板没有像CloudFormation那样的"堆栈"概念。直接读取ARM模板JSON文件：

```bash
# 查看模板结构
cat template.json | jq '.resources[] | {type: .type, name: .name}'

# 查看参数
cat template.json | jq '.parameters'

# 查看变量
cat template.json | jq '.variables'
```

提取：

- 资源类型和名称
- 参数及其默认值
- 变量和表达式
- 依赖关系（dependsOn数组）
- 嵌套模板或链接模板
- 复制循环（迭代结构）
- 条件部署（condition属性）

**文档：** [ARM模板结构](https://learn.microsoft.com/en-us/azure/azure-resource-manager/templates/syntax)

#### 1.3 构建资源清单（如果导入现有资源）

如果ARM模板已经部署，并且您要导入现有资源：

```bash
# 列出资源组中的所有资源
az resource list \
  --resource-group <resource-group-name> \
  --output json

# 获取特定资源详细信息
az resource show \
  --ids <resource-id> \
  --output json

# 使用JMESPath查询特定属性
az resource show \
  --ids <resource-id> \
  --query "{name:name, location:location, properties:properties}" \
  --output json
```

**文档：** [Azure CLI文档](https://learn.microsoft.com/en-us/cli/azure/)

### 2. 代码转换（ARM → PULUMI）

**重要提示：** ARM到Pulumi的转换需要手动翻译。对于ARM模板**没有**自动转换工具。您负责完整的转换。

#### 关键转换原则

1. **提供商策略**：
   - **默认**：使用 `@pulumi/azure-native` 以实现完整的Azure Resource Manager API覆盖
   - **备用**：使用 `@pulumi/azure`（经典提供商）当 `azure-native` 不支持特定功能或需要简化抽象时

   **文档：**
   - [Azure Native Provider](https://www.pulumi.com/registry/packages/azure-native/)
   - [Azure Classic Provider](https://www.pulumi.com/registry/packages/azure/)

2. **语言支持**：
   - **TypeScript/JavaScript**：最常见，优秀的IDE支持
   - **Python**：适合数据团队和ML工作流
   - **C#**：适合.NET团队
   - **Go**：高性能，强类型
   - **Java**：适合企业Java团队
   - **YAML**：简单的声明性方法
   - 根据用户偏好或现有代码库选择

3. **完整覆盖**：
   - 转换ARM模板中的所有资源
   - 保留所有条件、循环和依赖关系
   - 维持参数和变量逻辑

**遵循 [arm-conversion-patterns.md](arm-conversion-patterns.md) 中的转换模式。**

[arm-conversion-patterns.md](arm-conversion-patterns.md) 提供：

- 参数、变量和输出映射
- 复制循环、条件和 dependsOn 翻译
- 嵌套模板 → ComponentResource
- Azure Classic提供商示例（VNet、App Service）
- TypeScript输出处理和常见陷阱

### 3. 资源导入（现有资源）- 可选

转换后，您可以可选地导入现有资源以由Pulumi管理。如果用户不要求此操作，建议将其作为转换后的后续步骤。

**关键**：当用户请求将现有Azure资源导入Pulumi时，请参见 [arm-import.md](arm-import.md) 以获取详细的导入程序和零差异验证工作流。

[arm-import.md](arm-import.md) 提供：

- 内联导入ID模式和示例
- Azure资源ID格式约定
- 子资源处理（例如，WebAppApplicationSettings）
- **预览解决工作流**以在导入后实现零差异
- 属性冲突的逐步调试

#### 关键导入原则

1. **内联导入方法**：
   - 使用 `import` 资源选项与Azure资源ID
   - 没有单独的导入工具（与 `pulumi-cdk-importer` 不同）

2. **Azure资源ID**：
   - 遵循可预测的模式：`/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/{resourceProviderNamespace}/{resourceType}/{resourceName}`
   - 可以通过约定生成或通过Azure CLI查询

3. **零差异验证**：
   - 导入后运行 `pulumi preview`
   - 使用预览解决工作流解决所有差异
   - 目标：无更新、替换、创建或删除

### 4. PULUMI配置

设置与ARM模板参数匹配的堆栈配置：

```bash
# 设置Azure区域
pulumi config set azure-native:location eastus --stack dev

# 设置应用程序参数
pulumi config set storageAccountName mystorageaccount --stack dev

# 设置密钥参数
pulumi config set --secret adminPassword MyS3cr3tP@ssw0rd --stack dev
```

### 5. 验证

在预览中实现零差异后（如果导入），验证迁移：

1. **审查所有导出：**

   ```bash
   pulumi stack output
   ```

2. **验证资源关系：**

   ```bash
   pulumi stack graph
   ```

3. **测试应用程序功能**（如果适用）

4. **记录迁移后需要的任何手动步骤**

## 与用户合作

如果用户要求帮助规划或执行ARM到Pulumi的迁移，请使用上述信息指导用户完成转换和导入过程。

## 详细文档

当用户需要更多信息时，使用网络抓取工具从官方Pulumi文档中获取内容：

- **ARM迁移指南：** https://www.pulumi.com/docs/iac/adopting-pulumi/migrating-to-pulumi/from-arm/
- **Azure Native Provider：** https://www.pulumi.com/registry/packages/azure-native/
- **Azure Classic Provider：** https://www.pulumi.com/registry/packages/azure/

**Microsoft Azure文档：**

- **ARM模板参考：** https://learn.microsoft.com/en-us/azure/azure-resource-manager/templates/
- **Azure CLI参考：** https://learn.microsoft.com/en-us/cli/azure/
- **Azure资源ID：** https://learn.microsoft.com/en-us/azure/azure-resource-manager/templates/template-functions-resource

## 输出格式（必需）

在执行迁移时，始终生成：

1. **概述**（高级描述）
2. **迁移计划摘要**
   - 识别的ARM模板资源
   - 转换策略（语言、提供商）
   - 导入方法（如果适用）
3. **Pulumi代码输出**（按文件组织）
   - 主程序文件
   - Component资源（如果有）
   - 配置说明
4. **资源映射表**（ARM → Pulumi）
   - ARM资源类型 → Pulumi资源类型
   - ARM资源名称 → Pulumi逻辑名称
   - 导入ID（如果导入）
5. **预览解决说明**（如果导入）
   - 遇到的差异
   - 应用的解决策略
   - 忽略的属性与添加的属性
6. **最终迁移报告**（PR适用）
   - 变更摘要
   - 测试说明
   - 已知限制
   - 下一步
7. **配置设置**
   - 需要的配置值
   - 示例 `pulumi config set` 命令

保持代码语法有效，并按文件清晰分隔。
