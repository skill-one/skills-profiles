## 步骤

1. 识别组织：用户提供一个用户名或别名（`orgIdentifier`）。如果未提供，则运行 `sf org list` 显示已认证的组织，并询问用户要使用哪个组织。
2. 设置默认组织：
   - 本地（默认）：`sf config set target-org <orgIdentifier>`
     - 仅适用于当前项目目录。用于常规项目工作。
   - 全局（仅当用户明确请求时）：`sf config set target-org <orgIdentifier> --global`
     - 系统范围内适用于所有目录。在非项目环境中工作或用户要求全局范围时使用。
   - 如果失败，报告错误并建议运行 `sf org login web`，如果组织可能未授权。
3. 验证：
   - `sf config get target-org --json`
   - 注意：JSON 输出不包含范围/位置字段——它无法确认值是本地还是全局。仅确认值，例如：`target-org is now set to: <value>`
   - 如果失败，报告错误并建议运行 `sf config get target-org`。

## 注意事项

- 统一 CLI 使用 `target-org` 和 `target-dev-hub` 等键。在此上下文中，旧版 sfdx 键（`defaultusername`、`defaultdevhubusername`）已弃用。
- sf CLI 没有 `--local` 或 `--scope` 标志用于 `config set`。本地范围是默认行为。
- 如果设置配置后组织未更改，请检查是否设置了 `SF_TARGET_ORG`——环境变量会覆盖配置值。
- Salesforce CLI 配置（统一）参考：https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/cli_reference_config_commands_unified.htm#cli_reference_config_set_unified
