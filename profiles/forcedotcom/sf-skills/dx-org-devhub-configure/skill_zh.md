# 启用 Dev Hub 并查看 Scratch Org 配额

在 Salesforce 组织上启用 **Dev Hub**，验证其是否已启用，并查看组织的 **Scratch Org 配额**（活动配额和每日配额以及剩余数量）——针对默认组织或命名组织。该技能还可以配置 Dev Hub 子首选项（打包、组织形状导出、Scratch Org 快照）并列出从 Dev Hub 创建的活动 Scratch Org。

Dev Hub 是允许您 **创建和管理 Scratch Org** 以及 **第二代 (2GP) / 解锁包** 的组织功能。

## 使用场景

在以下请求时触发：

- "启用 Dev Hub" / "打开 Dev Hub" / "为此组织设置 Scratch Org"。
- "我的组织中 Dev Hub 是否已启用？" / "检查 Dev Hub 是否已启用"。
- "我可以创建多少个 Scratch Org？" / "我的 Scratch Org 配额/限制是多少？" / "我还有多少个 Scratch Org 剩余？"
- "打开打包 / 2GP / 解锁包" / "启用组织形状导出" / "启用 Scratch Org 快照"（Dev Hub 子首选项）。
- "列出我的 Dev Hub 上的 Scratch Org"。

## 不应使用场景

不要为此技能触发：

- **创建或删除单个 Scratch Org** —— 即 `sf org create scratch` / `sf org delete scratch`，不同的工作流。此技能启用 *Dev Hub 功能* 并报告 *配额*；它不会创建 Scratch Org。
- **切换默认/活动组织** —— 使用 `dx-org-switch`。
- **试用或组织过期日期**（"我的组织何时过期"）—— 使用 `dx-org-trial-expiration-check`。

## Dev Hub 启用状态的确定方式

标准对象 **`ScratchOrgInfo`** 仅在 Dev Hub 启用时才会被配置并变得可查询。因此，成功的 `SELECT COUNT() FROM ScratchOrgInfo` 意味着 Dev Hub 是 **已启用** 的；`INVALID_TYPE` 错误表示它 **未启用**。这是可靠的信号。

> 不要仅凭 `sf org list limits` 推断启用状态：它即使在 Dev Hub **未启用** 的组织中也会报告 `ActiveScratchOrgs` / `DailyScratchOrgs` 行，因此配额显示分配情况，但不显示启用状态。

## 启用工作原理（重要）

- Dev Hub 主开关是可部署的 Metadata API 字段 **`DevHubSettings.enableScratchOrgManagementPref`**。没有 `enableDevHub` 字段，也没有专门的 `sf` 命令来打开它——部署此设置正是 Setup 开关所做的操作。
- **启用是不可逆的**——一旦启用，Dev Hub 就无法关闭。
- **需要** 具有具有 **ModifyAllData** 或 **ModifyMetadata** 权限的用户（**系统管理员** 具有这些权限）。没有这些权限的用户会收到 `INSUFFICIENT_ACCESS`。
- **不能** 在 **沙盒** 中启用，或在一个具有 **注册命名空间** 的组织中启用。
- 可在 **开发者、企业、性能、无限** 和 **试用** 版本中使用。

## 步骤

1. **关键**：运行捆绑的辅助脚本，该脚本处理 Dev Hub 检测、启用部署（带有安全的 dry-run 默认值）、配额计算和结构化输出，并在 macOS 和 Linux 上工作。始终从技能目录通过 **绝对路径** 调用它——永远不要 `./scripts/`（脚本会拒绝非绝对路径的 `$0`）。脚本会自行检查此点：如果 `$0` 不是绝对路径，它会退出并显示使用错误，因此请将完整路径传递给 `<skill_dir>`（包含此 SKILL.md 的目录）。

   ```bash
   bash "<skill_dir>/scripts/devhub.sh" <别名或用户名>            # 状态：已启用？ + 配额
   bash "<skill_dir>/scripts/devhub.sh"                               # 默认组织（目标组织）
   bash "<skill_dir>/scripts/devhub.sh" <组织> --配额           # 仅配额
   bash "<skill_dir>/scripts/devhub.sh" <组织> --启用               # 验证启用（dry run）
   bash "<skill_dir>/scripts/devhub.sh" <组织> --启用 --应用       # 实际启用（不可逆）
   bash "<skill_dir>/scripts/devhub.sh" <组织> --列出-scratch         # 列出活动 Scratch Org
   bash "<skill_dir>/scripts/devhub.sh" <别名> --实例-url <url> --启用 --应用  # 先登录，然后启用
   bash "<skill_dir>/scripts/devhub.sh" <url>                        # 纯实例 URL：登录到它
   ```

   当用户提供一个实例 URL（他们的 My Domain、沙盒或预发布/Scratch 登录 URL——例如 `https://my-domain.my.salesforce.com`）时，请使用 `--instance-url <url>` 传递确切的 URL——脚本接受 Salesforce 拥有的主机名，并使用 `sf org login web --instance-url <url>` 登录，然后继续。纯 URL 位置参数作为简写接受相同操作。

   `<skill_dir>` 是包含此 SKILL.md 的目录的绝对路径。

2. **对于启用，默认先进行 dry run。** 运行 `--启用`（没有 `--应用`）以验证部署，然后传递结果。由于启用是 **不可逆的**，只有在用户明确要求实际启用 Dev Hub 时才运行 `--启用 --应用`。应用操作需要显式的组织别名或用户名；脚本拒绝修改隐式默认组织。如果部署因权限被拒绝，请显示脚本打印的 Setup-UI 回退。

3. 传递脚本输出。当无法查询组织时，请显示脚本打印的 `sf org login web` 命令，以便用户可以身份验证。根据请求选择可选标志（见下文）：`--配额` 仅用于限制，`--列出-scratch` 以枚举 Scratch Org，`--打包` / `--快照` / `--形状` 以启用子首选项，`--json` 用于自动化。

## 完成前验证

在返回您的答案之前，请验证以下内容：

- [ ] **关键**：通过其 **绝对路径** 调用了辅助脚本（`bash "<skill_dir>/scripts/devhub.sh" …`），永远不要 `./scripts/`（脚本会拒绝非绝对路径的 `$0`）。
- [ ] 除非用户明确要求实际启用 Dev Hub 或部署首选项——启用是 **不可逆的**，否则没有运行 `--应用`。
- [ ] 传递了脚本自己的输出（状态/配额或它打印的登录/Setup-UI 指导），而不是替换手写的答案。

## 选项

| 标志 | 目的 |
|------|---------|
| `--配额`, `-A` | 仅显示 Scratch Org 配额（活动/每日）。 |
| `--列出-scratch`, `-l` | 列出从此 Dev Hub 创建的活动 Scratch Org。 |
| `--启用`, `-e` | 启用 Dev Hub（部署 `enableScratchOrgManagementPref=true`）。如果没有 `--应用`，则为 dry run。 |
| `--配置`, `-c` | 配置子首选项而不（重新）启用主开关。与首选项标志配对。 |
| `--打包` | `enablePackaging2=true`（解锁包 + 2GP 包）。 |
| `--快照` | `enableScratchOrgSnapshotPref=true`。 |
| `--形状` | `enableShapeExportPref=true`。 |
| `--scratch-management` | `enableScratchOrgManagementPref=true`（Dev Hub 开关）。 |
| `--首选项 KEY=VALUE` | 任何 `DevHubSettings` 子首选项（KEY 以 `enable` 开头，VALUE `true`/`false`）。可重复。 |
| `--应用` | 实际部署到显式的组织参数。`--启用`/`--配置` 的默认值是仅验证的 dry run。 |
| `--登录` | 首先通过 `sf org login web`（打开浏览器）身份验证组织，然后运行操作。 |
| `--实例-url <url>` | 使用 `sf org login web --instance-url <url>` 登录特定实例（My Domain、沙盒或预发布/Scratch 实例）。隐含 `--登录`。 |
| `--json` | 发出机器可读的 JSON。 |
| `--fail-if-disabled` | 如果 Dev Hub 未启用，则退出 `3`（CI/cron 门）。 |
| `--帮助`, `-h` | 显示使用说明。 |

`--启用` 可以与子首选项标志组合使用，以便一次启用和配置（例如 `--启用 --打包 --应用`）。如果省略，组织默认为 `target-org`，然后是 `target-dev-hub`。

## 输出示例

脚本在运行时打印权威输出。如果您需要校准启用与未启用状态转录（包括配额表和启用/Setup-UI 指导），请阅读 [`examples/status-output.md`](examples/status-output.md)——否则跳过以保持此工作流简洁。

## 自动化结构化输出 (`--json`)

在任何模式下使用 `--json` 以获得机器可读输出（无散文）。状态返回 `devHubEnabled`、`status` 和 `allocation` 对象；启用返回 `success`、`applied` 和 `devHubVerifiedState`。确定性，无需 LLM。

```bash
bash "<skill_dir>/scripts/devhub.sh" my-devhub --json
# {"org":"my-devhub","devHubEnabled":true,"status":"enabled", ... }
```

`--fail-if-disabled` 如果 Dev Hub 未启用，则退出 `3`（并将 `ALERT:` 行打印到 stderr），因此计划任务可以基于它进行门控。

## 退出代码

- `0` 成功
- `1` 无法查询组织，或部署失败（身份验证/连接/部署）
- `2` 使用不当或缺少依赖项（`sf` 或 `jq`）
- `3` Dev Hub 未启用（仅当 `--fail-if-disabled` 设置时）

## 身份验证

如果组织尚未经过身份验证，该技能可以使用 `--登录`（或 `--实例-url <url>`）为您登录，然后在同一运行中继续请求的操作——当用户提供实例 URL 时这是首选路径：

将用户的实际实例 URL 替换为 `<url>`（此处显示为通用 `https://my-domain.my.salesforce.com` 占位符）：

```bash
# 登录到特定实例（My Domain / 预发布 / 沙盒），然后启用：
bash "<skill_dir>/scripts/devhub.sh" my-alias \
  --instance-url https://my-domain.my.salesforce.com --启用 --应用

# 纯实例 URL 作为简写——登录到它，然后报告状态：
bash "<skill_dir>/scripts/devhub.sh" https://my-domain.my.salesforce.com

# 仅身份验证组织（无其他操作）：
bash "<skill_dir>/scripts/devhub.sh" my-alias --登录
```

`sf org login web` 打开浏览器进行 OAuth 流程；及时完成它（会话超时）。提供的位置参数（`my-alias`）成为 CLI 别名；看起来像 URL 的位置参数（包含 `://`）被视为要登录的 `--实例-url`。脚本仅接受 HTTPS Salesforce 拥有的主机名。如果浏览器流程持续超时，脚本会打印 `sf org login device` 回退以进行基于代码的登录。

如果组织未经过身份验证且未传递登录标志，脚本会打印确切的命令以进行登录并重新运行——如果有提供实例 URL，则使用该 URL：

```text
  my-org                         无法查询组织 (...)

  要针对 https://my-domain.my.salesforce.com 进行身份验证，请运行：
    sf org login web --instance-url "https://my-domain.my.salesforce.com" --alias "my-org"
  或让此脚本登录并继续一步：
    devhub.sh "my-org" --instance-url "https://my-domain.my.salesforce.com" --登录
  然后重新运行。使用以下命令列出现有登录：  sf org list
```

## 手动回退（如果脚本不可用）

```bash
# 检测 Dev Hub（INVALID_TYPE 错误表示未启用；计数表示已启用）：
sf data query --query "SELECT COUNT() FROM ScratchOrgInfo" --target-org <org> --json

# 通过 Tooling API 启用 Dev Hub（Setup 开关所做的操作；不可逆）：
sf api request rest "/services/data/v47.0/tooling/sobjects/DevHubSettings/DevHub" \
  --method PATCH \
  --body '{"FullName":"DevHub","Metadata":{"enableScratchOrgManagementPref":true}}' \
  --target-org <org>

# 或者通过 UI 启用：Setup > Quick Find > "Dev Hub" > 打开启用 Dev Hub。

# 查看Scratch Org配额：
sf org list limits --target-org <org> --json | jq '.result[] | select(.name|test("ScratchOrg"))'
```

## 注意事项

- 需要 Salesforce CLI (`sf`) 和 `jq` 在 PATH 上，并且至少有一个经过身份验证的组织（`sf org login web`）。
- 启用后，将组织设置为您的默认 Dev Hub：
  `sf config set target-dev-hub <org>`。
- 启用 **打包** (`enablePackaging2`) 需要先启用 Dev Hub——`--启用 --打包` 在单个部署中处理顺序。
- 非管理员用户仍然需要对象访问权限（在 `ScratchOrgInfo` 和 `ActiveScratchOrg` 上具有读取/创建权限），以及“创建和更新第二代包”权限来构建 2GP/解锁包。
- 要 *切换* 默认组织，请使用 `dx-org-switch`；要检查 *过期*，请使用 `dx-org-trial-expiration-check`。
