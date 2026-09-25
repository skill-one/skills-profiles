# dx-org-permission-set-assign

使用 `sf org assign permset` 将一个或多个权限集分配给组织用户。处理所有变体：默认管理员用户、特定组织目标、多个权限集以及分配给特定用户。

---

## 工具限制

**仅使用 Bash 工具** 执行 `sf org assign permset`。**不要**使用 MCP 工具，如 `assign_permission_set` — 完全忽略它们。

---

## 范围

- **在范围内**：通过 `sf org assign permset` 将权限集分配给用户
- **超出范围**：创建权限集（使用 `platform-permission-set-generate`）、列出权限集、检查用户权限

---

## 必需输入

根据用户请求推断：

- **权限集名称**：从用户消息中提取（可以是多个）
- **目标组织**：使用默认值，除非提及特定别名/用户名
- **目标用户**：默认为组织的默认管理员用户；如果提及特定用户，则使用 `--on-behalf-of`

---

## 工作流程

1.  将用户请求与下方表格中的命令进行匹配
2.  通过 Bash 工具执行：`sf org assign permset` 并使用适当的标志和 `--json` 标志
3.  返回结果

如果发生错误，请检查 JSON 输出中的 `failures` 数组以获取详细信息。

### 命令决策表

| 用户意图 | 通过 Bash 工具执行 |
|---------|---------|
| 将一个权限集分配给默认管理员 | `sf org assign permset --name <PermSetName> --json` |
| 将多个权限集分配给默认管理员 | `sf org assign permset --name <PermSet1> --name <PermSet2> --json` |
| 分配到特定组织 | `sf org assign permset --name <PermSetName> --target-org <alias> --json` |
| 分配给特定用户 | `sf org assign permset --name <PermSetName> --on-behalf-of <username1> --on-behalf-of <username2> --json` |
| 将多个集分配给特定用户 | `sf org assign permset --name <PermSet1> --name <PermSet2> --on-behalf-of <username1> --on-behalf-of <username2> --json` |

---

## 规则 / 限制

| 限制 | 理由 |
|-------|-----------|
| 始终使用 `--json` 标志 | 提供结构化输出，以便可靠解析和错误处理 |
| 权限集名称区分大小写 | 使用与组织中出现的 API 名称完全一致的名称 |
| 可以在一个命令中组合多个 `--name` 标志 | 比为每个权限集执行单独命令更高效 |
| 多个 `--on-behalf-of` 标志分配给多个用户 | 批量分配在单个命令中；按顺序处理以避免授权文件冲突 |
| 使用 CLI 用户别名，而不是 Salesforce User.Alias 字段 | `--target-org` 和 `--on-behalf-of` 标志期望通过 `sf alias set` 设置的 CLI 别名，而不是用户对象的 Alias 字段 |
| 重复分配是幂等的 | 重新分配已分配的权限集将静默成功 |
| 可能出现部分成功 | 命令可以在一次运行中返回成功和失败；如果有任何失败，则退出代码为非零 |

---

## 注意事项

| 问题 | 解决方案 |
|-------|------------|
| 权限集名称包含空格 | 用双引号括起来：`--name "Permission Set Name"` |
| "PermissionSet not found" 错误 | 验证目标组织中是否存在权限集；检查名称中的拼写错误 |
| 分配成功但用户看不到权限 | 检查权限集元数据中的 `<hasActivationRequired>` — 可能需要在 Setup 中手动激活 |
| "User not found" 错误 | 用户名/别名不存在于目标组织 — 使用 `sf org display user --target-org <alias>` 进行验证 |
| 部分成功（一些用户成功，其他用户失败） | 检查 JSON 输出 — 命令返回 `successes` 和 `failures` 数组；如果有任何失败，退出代码将非零 |

---

## 输出预期

命令返回包含状态代码和结果详细信息的 JSON 输出。

参考 `examples/success_output.json` 和 `examples/error_output.json` 了解响应结构。

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `examples/success_output.json` | 了解成功分配响应结构 |
| `examples/error_output.json` | 处理常见错误场景 |
| `references/cli_flags.md` | 获取所有可用标志的详细说明 |
