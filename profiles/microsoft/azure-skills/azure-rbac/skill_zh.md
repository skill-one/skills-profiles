使用 'azure__documentation' 工具查找与用户希望分配给某个身份的权限相匹配的最简角色定义。如果不存在匹配期望权限的内置角色，请使用 'azure__extension_cli_generate' 工具创建包含期望权限的自定义角色定义。然后，使用 'azure__extension_cli_generate' 工具生成将上述角色分配给该身份所需的 CLI 命令。最后，使用 'azure__bicepschema' 和 'azure__get_azure_bestpractices' 工具提供一段用于添加角色分配的 Bicep 代码片段。如果用户询问设置访问权限所需的角色，请参阅下方“授予角色的前置条件”：

## 授予角色的前置条件

要将 RBAC 角色分配给身份，您需要包含 `Microsoft.Authorization/roleAssignments/write` 权限的角色。具有此权限的常见角色包括：

- **用户访问管理员**（最小权限 - 仅推荐用于角色分配）
- **所有者**（包含角色分配的完全访问权限）
- **带有 `Microsoft.Authorization/roleAssignments/write` 权限的自定义角色**
