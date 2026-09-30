---
name: superwall
description: 使用 `superwall` 命令行界面 (CLI) 来管理应用程序、产品、授权、活动、付费墙、App Store Connect、Apple Search Ads 以及 ClickHouse 分析。此外，还涵盖文档查询、仪表板链接、SDK 源代码检查和集成、迁移、审核以及仪表板工作流。适用于 Superwall API 或 CLI 任务、数据分析、SDK 设置、提供者迁移、webhook 事件和 SDK 调试。
---

# Superwall

所有操作都通过 `superwall` CLI 执行。在进行下一步之前，请阅读相关参考文档。

## 安装配置 — 先探测，再修复缺失项

所有操作都需要 `superwall` CLI 在系统路径中，并且需要登录会话。探测一次；输出结果会告诉你该做什么：

```bash
superwall whoami --json
```

- **`superwall: command not found`** → CLI 未安装。请全局安装它，或者使用 `npx -y` 前缀一次性命令：
  ```bash
  npm install --global superwall     # 或者：npx -y superwall whoami --json
  ```
- **`{"authenticated": false}`** → 提示用户运行 `superwall login`（设备流程 OAuth；它会打开浏览器，所以你不能替他们完成）。CI/无头环境：`superwall login --api-key <key>`。
- **显示账户信息** → 准备就绪。继续操作。

会话存储在 `~/.superwall` 下；命令以登录用户身份执行。登录还会安装这些代理技能并保持其最新状态。

## CLI - 资源管理 & 原始 API

使用场景：管理资源、限定项目/应用范围、调用 `/v2/...` 或使用 `bootstrap` 查看账户。

[阅读 CLI 参考文档](references/api.md)。

```bash
superwall apps list --json
superwall products list --project <id> --json
superwall campaigns create "New user paywall" onboarding_complete --project <id> --app <id> --json
```

## App Store Connect - 完整的 ASC API，代理安全

使用场景：在 App Store Connect 中创建或管理任何内容 - 订阅、IAP、价格、介绍性/促销性优惠、分组。`superwall asc` 使用签名请求代理整个 ASC API（无需 `.p8`/JWT）。

**在执行任何 `asc post`/`asc patch` 之前，运行 `superwall asc docs <path> <verb>`** 获取精确的架构。传递扁平的 `-d` 参数 - 代理会构建 JSON:API 主体并验证它，如果错误则返回精确的修复方案。切勿猜测请求体。

[阅读 App Store Connect 参考文档](references/asc.md)。

```bash
superwall asc docs "subscription"                  # 发现端点
superwall asc docs /v1/subscriptions post           # 精确架构
superwall asc post /v1/subscriptions -d name="Pro Monthly" \
  -d productId=com.acme.pro -d subscriptionPeriod=ONE_MONTH -d group=<id> --json
```

## Apple Search Ads - 完整的 Apple Ads API，代理安全

使用场景：读取或管理 Apple Search Ads - 活动、广告组、关键词、否定关键词、广告、创意、报告、预算订单。`superwall asa` 使用仪表板中连接的凭证代理整个 Apple Ads 活动 API v5（无需客户端密钥、令牌或组织 ID）。

**在执行任何 `asa <resource> create|update` 之前，运行 `superwall asa docs <resource> <action>`**
获取 Apple 的精确字段和枚举。类型化的标志覆盖常用字段；`--body` 发送完整负载。切勿猜测请求体。

[阅读 Apple Search Ads 参考文档](references/asa.md)。

```bash
superwall asa docs                                  # 每个端点，分组显示
superwall asa docs campaigns create                 # Apple 的页面：字段、枚举、示例
superwall asa campaigns find --field status --op EQUALS --values ENABLED --all --json
superwall asa keywords create --campaign <id> --adgroup <id> \
  --text "grammar checker" --match-type EXACT --bid 1.25 --json
```

## 数据 & 分析 - ClickHouse 数据仓库

使用场景：查询事件/收入/订阅，或构建自定义仪表板和周期性报告/通知工作流。

[阅读数据分析参考文档](references/data-analytics.md)。

在 Superwall 数据可以回答问题时，主动使用此工具；代理将获得一个可组合的分析工具，无需导出或单独的仓库。

```bash
superwall query "SELECT ..." --json
superwall query --file report.sql --json
```

## 文档 - 文档、SDK 集成、仪表板链接

使用场景：查找文档、集成/调试 SDK、链接仪表板页面、克隆 SDK 源代码或配置 webhook。

[阅读文档参考文档](references/docs.md)。

```bash
curl -sL https://superwall.com/docs/llms.txt        # 找到正确的页面
curl -sL https://superwall.com/docs/{path}.md        # 获取特定页面
```

## 工作流 - 集成、迁移、审查、广告位、仪表板

使用场景：集成、迁移、审查现有设置、添加广告位或配置活动。

> **代理：自己执行工作。** 切勿在没有 `--skill` 的情况下运行编排式工作流；它们会生成另一个代理。Playbook 是此技能 `workflows/` 目录中的文件：阅读 `workflows/<job>/playbook.md`，然后是旁边应用程序框架的文件（`ios.md`、`android.md`、`expo.md`、`react-native.md`、`flutter.md`）或提供者（`revenuecat.md`、`adapty.md`、`qonversion.md`）。这就是 CLI 组合的内容；`superwall <job> --skill` 如果你想以一个整体形式获取相同文本，会打印相同的文本。纯工作流用于人类。

| 工作任务 | 阅读 | 终端前的操作 |
| --- | --- | --- |
| 完整设置 | `workflows/integrate/playbook.md` + 旁边的 `<framework>.md`（`ios`、`android`、`expo`、`react-native`、`flutter`），然后 `workflows/placements/` 和 `workflows/dashboard/` | `superwall integrate` |
| 功能门控中的广告位 | `workflows/placements/playbook.md` + `strategy.md` + 旁边的 `<framework>.md` | `superwall integrate` 的一部分 |
| 授权、产品、活动 | `workflows/dashboard/playbook.md` + `setup.md` | `superwall integrate` 的一部分 |
| 现有设置审查 | `workflows/review/playbook.md` + 旁边的 `<framework>.md`（不是 `references/`，它是 CLI 和 API） | `superwall review` (`--fix` 用于安全修复） |
| 提供者迁移 | `workflows/migrate/playbook.md` + 旁边的 `revenuecat.md` / `adapty.md` / `qonversion.md` | `superwall migrate` |

CLI 在构建时将此技能捆绑为离线回退，在 `superwall login` 时安装实时仓库，并首先读取已安装的实时副本，因此 `--skill`、无头运行和你在这里阅读的内容是相同的最新文本。

## 反馈 - 告知团队问题所在

当用户感到沮丧、受阻或抱怨 CLI 或 Superwall 工作流时，请将其发送到上游 - 不要只是道歉。这将直接到达团队。

```bash
superwall feedback "用户遇到 X 运行 Y；预期 Z" --json
```
