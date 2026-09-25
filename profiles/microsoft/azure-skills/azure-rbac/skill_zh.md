使用 'azure__documentation' 工具查找与用户希望分配给身份的所需权限匹配的最小角色定义。如果没有内置角色与所需权限匹配，请使用 'azure__extension_cli_generate' 工具创建具有所需权限的自定义角色定义。然后使用 'azure__extension_cli_generate' 工具生成分配该角色的所需 CLI 命令。最后，使用 'azure__bicepschema' 和 'azure__get_azure_bestpractices' 工具提供用于添加角色分配的 Bicep 代码片段。如果用户询问设置访问权限所需的角色，请参考下方的“授予权限的先决条件”：

## 授予权限的先决条件

要为身份分配 RBAC 角色，您需要一个包含 `Microsoft.Authorization/roleAssignments/write` 权限的角色。具有此权限的最常见角色包括：

- **用户访问管理员**（最小权限 - 推荐仅用于角色分配）
- **所有者**（完全访问权限，包括角色分配）
- 具有权限 `Microsoft.Authorization/roleAssignments/write` 的**自定义角色**
