# 启用交易市场接收合作伙伴提议组织偏好设置

此技能通过 `TransactableMarketplacePrivateOfferSettings` 元数据 API 类型配置 `enableTransactableMarketplaceReceivePartnerOffers` 组织偏好设置，该设置控制 Salesforce 组织是否可以通过交易市场接收合作伙伴提议。对于参与 TM 合作伙伴提议流程的订阅组织，这是必需的。

## 范围

- **在范围内**：读取当前偏好值、通过元数据 API 启用或禁用（`TransactableMarketplacePrivateOfferSettings`），以及验证更改是否生效。
- **超出范围**：创建或管理合作伙伴提议记录、配置市场列表或与提议处理相关的任何 Apex/触发器更改。

---

## 必需输入

- **目标组织别名或用户名**：应设置偏好的组织。如果未提供，请询问。
- **期望状态**：`true`（启用）或 `false`（禁用）。默认：`true`。

---

## 工作流

### 第一阶段 — 检查当前状态

1. **查询当前偏好值**，运行：
   ```bash
   sf data query -q "SELECT Preference, Value FROM OrgPreference WHERE Preference = 'TransactableMarketplaceReceivePartnerOffers'" --target-org <别名> --use-tooling-api
   ```
   如果记录存在且 `Value = true`，则偏好已启用 — 在继续之前与用户确认。
   如果查询返回无行，则偏好尚未设置（默认为 `false`）。

2. **解析组织的包目录**，以确定写入元数据的路径。运行此命令并使用其输出作为 `<packageDir>`：
   ```bash
   jq -r '.packageDirectories[0].path // "force-app/main/default"' sfdx-project.json
   ```

### 第二阶段 — 应用偏好设置

3. **写入 TransactableMarketplacePrivateOfferSettings 元数据文件** — 加载 `assets/org-pref-template.md` 获取确切的 XML 结构，然后写入以下路径：
   ```text
   <packageDir>/settings/TransactableMarketplacePrivateOffer.settings
   ```
   设置 `<enableTransactableMarketplaceReceivePartnerOffers>true</enableTransactableMarketplaceReceivePartnerOffers>`（如果禁用则为 `false`）。

4. **将元数据部署到目标组织**。在运行部署之前，与用户确认：
   - [ ] 确认了目标组织别名（部署到错误组织不易逆转）
   - [ ] 确认了期望状态（`true`/`false`）与用户的意图一致
   ```bash
   sf project deploy start --metadata TransactableMarketplacePrivateOfferSettings --target-org <别名>
   ```

### 第三阶段 — 验证

5. **通过重新运行步骤 1 的 Tooling API 查询来确认更改**，并验证 `Value` 列是否与期望状态匹配。

6. **向用户报告** — 见下方输出预期。

---

## 规则 / 限制

| 规则 | 理由 |
|------|-----------|
| 始终在写入元数据前查询当前值 | 避免不必要的部署并检测冲突更改 |
| 使用 `TransactableMarketplacePrivateOfferSettings` 作为元数据类型 | 这是平台注册为此偏好设置的具象类型，不是通用的 `OrgPreferenceSettings` |
| 设置文件必须命名为 `TransactableMarketplacePrivateOffer.settings` | 元数据 API 要求文件名与设置节点名称匹配 |
| 不要硬编码 `force-app/main/default/` | 始终读取 `sfdx-project.json` 获取实际包目录 |
| 从不未经用户确认组织别名就部署 | 部署到错误组织不易逆转 |

---

## 注意事项

| 问题 | 解决方案 |
|-------|------------|
| Tooling API 查询返回无行 | 偏好未设置（默认为 `false`）。可以安全地创建新的设置文件。 |
| 部署失败并显示 `INVALID_TYPE` | 元数据类型名称为 `TransactableMarketplacePrivateOfferSettings` — 检查 `--metadata` 标志值。 |
| 部署成功但值未更改 | 项目中可能有其他 `TransactableMarketplacePrivateOffer.settings` 文件覆盖了此文件。在项目中搜索其他 `TransactableMarketplacePrivateOffer.settings` 文件。 |
| 部署时出现 `INSUFFICIENT_ACCESS_OR_READONLY` | 运行部署的用户必须在目标组织中具有 "修改所有数据" 或组织偏好管理员权限。 |
| 偏好在 UI 中不可见 | `enableTransactableMarketplaceReceivePartnerOffers` 未在 Setup UI 中显示 — Tooling API 查询是验证它的唯一方法。 |
| 仅从 API 版本 67.0+ 可用 | 该类型从 API v67.0 可用 — 部署针对较旧 API 版本将失败。 |

---

## 输出预期

完成所有阶段后，报告：

```text
组织: <别名>
偏好: enableTransactableMarketplaceReceivePartnerOffers
先前值: <true|false|未设置>
新值: <true|false>
文件写入: <packageDir>/settings/TransactableMarketplacePrivateOffer.settings
部署状态: 成功
```

---

## 参考文件索引

| 文件 | 何时读取 |
|------|-------------|
| `assets/org-pref-template.md` | 第二阶段，步骤 3 — 用作设置文件的精确 XML 结构 |
| `examples/org-preference-settings.xml` | 验证生成的文件是否匹配预期格式 |
