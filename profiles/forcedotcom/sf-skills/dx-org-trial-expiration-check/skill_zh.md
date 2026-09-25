# 组织过期检查

确定 Salesforce 组织何时过期、剩余多少天以及是否已经过期 — 可针对单个组织、默认组织或所有经过身份验证的组织进行检查。结果会**优先排序**（已过期和即将过期的优先显示），并提供一行摘要。该技能还可以输出机器可读的用于告警的输出、为有风险的组织打印**备份**命令，并解释如何**续订**即将过期的试用版或开发者版组织。

## 使用场景

在以下请求时触发：

- "我的试用组织何时过期？" / "它是否仍然活跃或已过期？"
- "我的试用版还剩多少天？"
- "哪些我的组织即将过期？" / "在30天内即将过期？"
- "提醒我 / 设置一个定时任务来检查即将过期的组织"（使用 `--json` + `--fail-if-expiring`）。
- "在组织过期前备份我的组织"（使用 `--preserve`）。
- "我该如何延长/续订我的试用版（或开发者版）组织？"（使用 `--renew`）。

此技能涵盖**试用版、开发者版组织**（任何具有 `TrialExpirationDate` 的组织）和**沙盒组织**（通过 `sf org list` 中的 `expirationDate`）。

## 不应使用场景

不要为此技能触发：

- **沙盒刷新时间** — 这不是过期日期。
- **创建、删除或切换组织** — 此技能仅*读取*过期日期并*打印*指导；它从不创建、删除、刷新或更改活动/默认组织。（要切换默认组织，请使用 `dx-org-switch`。）
- **非 Salesforce 试用版** — 例如 AWS 免费套餐、Netflix 或任何其他供应商的试用版。此技能仅适用于 Salesforce。

## 过期日期的确定方式

- **试用版/开发者版组织**：权威来源是组织的 `Organization.TrialExpirationDate` 字段，通过 SOQL (`sf data query`) 读取。此字段对于付费/生产组织为 `null`，因此报告**无试用版过期** — 这是预期的，不是错误。
- **沙盒组织**：通过 `sf org list` 报告的 `expirationDate`（沙盒组织不进行 SOQL 查询）。

## 步骤

1. **关键**：运行捆绑的辅助脚本，该脚本处理日期计算（剩余天数、已过期、即将过期警告）、优先排序和结构化输出，并在 macOS 和 Linux 上工作。始终从技能目录通过**绝对路径**调用它 — 绝不使用 `./scripts/`，这会相对于用户当前目录解析，要么运行错误的脚本，要么失败。

   **执行前请验证：**
   - [ ] `<skill_dir>` 是绝对路径（以 `/` 开头），不是相对路径
   - [ ] 路径指向此技能的目录（包含此 SKILL.md 的目录）

   ```bash
   bash "<skill_dir>/scripts/check_expiration.sh" <别名或用户名>   # 单个组织
   bash "<skill_dir>/scripts/check_expiration.sh"                   # 默认组织（目标组织配置）
   bash "<skill_dir>/scripts/check_expiration.sh" --all             # 所有经过身份验证的组织
   bash "<skill_dir>/scripts/check_expiration.sh" --all --within 30  # 仅在30天内即将过期的组织
   ```

   `<skill_dir>` 是包含此 SKILL.md 的目录的绝对路径。

2. 将脚本输出传递给用户。当无法查询某个组织时，显示脚本打印的 `sf org login web` 命令，以便用户进行身份验证。根据用户请求的内容选择可选标志（见下文）：`--preserve` 当他们想要保存工作时，`--renew` 当他们询问如何延长时，`--json`/`--csv` 用于自动化，`--fail-if-expiring` 用于定时任务/CI 闸门。

## 选项

| 标志 | 目的 |
|------|------|
| `--all`, `-a` | 检查所有经过身份验证的组织。 |
| `--within <days>`, `-w` | 仅显示在 N 天内即将过期的组织（包括已过期；不包括付费/生产组织）。`--within=30` 也适用。 |
| `--json` | 输出一个 JSON 数组组织记录（仅数据）。 |
| `--csv` | 输出 CSV 行（仅数据）。 |
| `--preserve` | 为即将过期/已过期的组织打印备份命令。 |
| `--renew` | 打印试用版/DE 延长和重新激活的指导。 |
| `--fail-if-expiring[=N]` | 如果任何组织在 N 天内过期，则退出 3（并将 `ALERT:` 行打印到 stderr），以便定时任务在组织过期前提醒您： |
| `--no-scratch` | 排除沙盒组织（仅试用版/DE）。 |
| `--help`, `-h` | 显示用法。 |

标志顺序是灵活的，标志可以组合（例如 `--all --within 30 --json`）。

## 优先级输出

人类输出按紧急程度分组 — **已过期** 首先显示，然后 **即将过期**（7 天内，标记为 `Warning`），然后 **活跃**，然后 **无试用版过期**，然后任何无法查询的组织 — 最后以一行摘要结束：

```text
所有经过身份验证的组织过期状态：

已过期：
  old-trial                       试用版/DE 版本已于 2026-06-20 过期 (EXPIRED 19 天前)

即将过期（7 天内）：
  almost-up                       试用版/DE 版本将于 2026-07-14 过期 (将在 5 天后过期  Warning)

活跃（不久内不会过期）：
  acme-trial                      试用版/DE 版本将于 2026-08-15 过期 (将在 37 天后过期)
  my-scratch                      沙盒组织将于 2026-07-25 过期 (将在 16 天后过期)

无试用版过期（付费/生产组织）：
  prod                            无试用版过期 (付费/生产组织)

摘要：1 个已过期，1 个在 7 天内即将过期，2 个活跃，1 个无过期。
```

## 结构化输出用于告警和定时任务 (`--json` / `--csv`)

对于仪表板、电子表格或计划任务，使用 `--json` 或 `--csv` 获取机器可读的记录（无散文）。每条记录都有 `org`、`kind`、`expirationDate`、`daysRemaining`（负数 = 已过期，`null` = 无过期）、`status` 和 `orgId`。这是确定性的，不需要 LLM 参与。

```bash
# JSON，过滤为 30 天内即将过期的组织：
bash "<skill_dir>/scripts/check_expiration.sh" --all --within 30 --json
```

**定时任务监视器** — `--fail-if-expiring[=N]` 如果任何组织在 N 天内过期，则退出 `3`（并将 `ALERT:` 行打印到 stderr），以便定时任务在组织过期前提醒您：

```bash
# crontab：每天早上 9 点，如果任何组织在 7 天内过期，则提醒
0 9 * * *  bash "<skill_dir>/scripts/check_expiration.sh" --all --fail-if-expiring 7 \
             || mail -s "Salesforce 组织即将过期" me@example.com
```

## 在组织过期前保存您的工作 (`--preserve`)

当组织过期时，您将失去对其元数据和数据的访问权限。`--preserve` 为每个即将过期或已过期的组织打印准备就绪的备份命令（元数据清单 + `retrieve`，以及批量数据导出）。它仅*打印*命令 — 您自己审查并运行它们：

```bash
bash "<skill_dir>/scripts/check_expiration.sh" my-trial --preserve
```

## 延长或续订试用版/开发者版组织 (`--renew`)

`--renew` 打印保持组织活跃的当前指导，并显示有风险组织的 Org ID，以便步骤更具可操作性：

- **合作伙伴**：通过 `partners.salesforce.com` 请求试用组织延长（最多 +12 个月）→ **联系 Agentforce** → "我想延长我的试用组织"，并提供 Org ID。在活跃或过期 < 30 天时适用；不适用于 LDV 组织。（Salesforce 帮助文章 000387818。）
- **非营利组织**：将主题为 "Trial Extension" 的邮件发送给您的客户经理，并提供试用启动电子邮件、Org ID 和用户名；AMER `PowerOfUsDesk@salesforce.com`，其他地区 `myaccount@salesforce.com` / 1-800-NO-SOFTWARE。即使已过期也适用。（文章 004754220。）
- **开发者版**：开发者版组织没有订阅时钟，但在长时间不活动后（约 180 天未登录）会被停用；定期登录。如果被锁定（尚未删除），请打开 Salesforce 客户支持案例以重新激活 — 一旦永久删除，组织将无法恢复。
- 要在标准试用版过期前保留数据/配置，请在过期前转换为付费版本。

## 退出代码

- `0` 成功
- `1` 无法查询组织（认证/连接错误）
- `2` 使用不当或缺少依赖项 (`sf` 或 `jq`)
- `3` `--fail-if-expiring` 阈值被突破（至少有一个组织即将过期）

当两者都适用时，`--fail-if-expiring` 突破（`3`）优先于认证错误（`1`）：告警信号优先，因此定时任务仍然会触发。如果您的任务必须检测无法访问的组织，请运行 `--json` 并检查记录中是否有 `status: "auth_error"`，除了检查退出代码。请注意，如果凭证失败，则无法检查日期，因此它本身永远不会计入 `--fail-if-expiring` 突破。

`--fail-if-expiring` 未指定明确数字时，会将后面的**纯数字**参数视为天数（例如 `--fail-if-expiring 12345`）。在极少数情况下，如果组织的别名完全是数字，请先传递组织（`check_expiration.sh 12345 --fail-if-expiring 7`），以免将其误认为是阈值。

## 身份验证

如果组织未经过身份验证（没有保存的凭证，或令牌过期/被吊销），脚本不会静默失败 — 它会打印登录的确切命令，然后重新运行：

```text
  my-trial                       未经过身份验证 — 此组织没有保存的凭证

  要进行身份验证，运行以下之一：
    sf org login web --alias "my-trial"
    sf org login web --alias <我的别名> --instance-url https://test.salesforce.com
  然后重新运行此检查。列出现有登录信息： sf org list
```

`sf org login web` 会打开浏览器完成 OAuth 流程。对于沙盒，使用 `--instance-url https://test.salesforce.com`，或在适用情况下使用自定义 My Domain URL。

## 手动回退（如果脚本不可用）

```bash
# 单个组织试用版/DE 过期（null = 不是试用版/付费组织）：
sf data query --query "SELECT Id, TrialExpirationDate FROM Organization" --target-org <组织> --json

# 沙盒过期来自组织列表，不是 SOQL：
sf org list --json
```

## 注意事项

- 需要 Salesforce CLI (`sf`) 和 `jq` 在 PATH 上，并且至少有一个经过身份验证的组织 (`sf org login web`)。
- 避免并发启动许多 `sf` 命令 — 在竞争条件下，CLI 可能会变慢。脚本按顺序查询组织，原因在此。
- `sf org list` 暴露的 `trailExpirationDate`（注意拼写错误）字段通常是 `null`；脚本不依赖它来检查试用版/DE 组织 — 它使用可靠的 SOQL `TrialExpirationDate`。它确实使用列表中的 `expirationDate` 来检查沙盒组织。
