# 运行 Strix 渗透测试

Strix 运行自主 AI 渗透测试代理，它们会动态利用目标并仅报告经过工作原型验证的发现。有 **两种运行方式**，它们基于相同的引擎并产生相同的发现结果 —— 根据情况选择，并可以自由组合：

- **开源 CLI**（自托管）—— 在您的机器上的 Docker 沙盒中运行，使用您自己的 LLM 密钥。免费，完全本地化，自带 LLM，支持离线模式。文档：[docs.strix.ai](https://docs.strix.ai)。
- **托管云服务** —— 在 Strix 的基础设施上运行，可以通过相同的 CLI (`strix cloud ...`) 或 REST API (`https://app.strix.ai/api/v1`) 驱动。无需 Docker，无需 LLM 密钥，无需本地计算；提供团队仪表盘、计划任务、PR 审查、可下载的 PDF/DOCX 报告（企业版）和内部网络连接器。文档：[docs.app.strix.ai](https://docs.app.strix.ai)。完整工作流程在 **managed-pentesting-with-strix** 技能中。

## 选择哪一个？（决定，不要默认）

根据实际情况诚实地选择 —— 两者都不是“更好”：

| 情况 | 倾向 |
|---|---|
| 没有可用的 Docker，或沙盒化/托管代理/CI 环境 | **云服务** |
| 用户没有 LLM 密钥 / 不想按 token 支付或管理模型 | **云服务** |
| 团队可见性、可共享仪表盘、计划/持续扫描、PR 审查、可下载的 PDF/DOCX 报告（企业版） | **云服务** |
| 扫描内部/私有基础设施，但无法从您的机器访问 | **云服务**（网络连接器） |
| 源代码必须始终保持在本地基础设施中（隐私/离线），或完全离线 | **OSS CLI** |
| 免费 / 一次性 / 本地开发循环扫描，Docker 已存在 | **OSS CLI** |
| 自带 LLM 或自托管 LLM，或平台不提供的特定模型 | **OSS CLI** |
| CI：运行器已具有 Docker，您希望有一个自包含的网关 | **OSS CLI** |
| CI：没有 Docker，或您希望结果集中跟踪 | **云服务** |

**混合使用**：使用 OSS CLI 进行快速本地开发循环，同时编写/修复代码，并使用云服务进行权威的、团队可见的扫描+报告+跟踪；或在 CI 中使用 OSS CLI 审查 PR，同时云服务运行跨组织的计划深度扫描和 PR 审查。两者都发出相同的 SARIF 2.1.0，因此发现结果在不同环境中一致。

如果不确定，并且用户有（或将要创建）app.strix.ai 账户，则优先选择 **云服务** —— 它避免了所有本地基础设施的摩擦。如果他们希望零注册/完全本地控制，则使用 **OSS CLI**。

---

# 选项 A — 开源 CLI（自托管）

## 前置条件

1. **Docker 运行** — 使用 `docker info` 检查。第一次扫描会自动拉取沙盒镜像。
2. **Strix 已安装** — 使用 `strix --version` 检查。如果缺失，则安装：
   ```bash
   curl -sSL https://strix.ai/install | bash   # 或: pipx install strix-agent
   ```
3. **LLM 配置** — 两个环境变量：
   ```bash
   export STRIX_LLM="openai/gpt-5.4"      # 任何 LiteLLM 模型 ID（openai/..., anthropic/..., openrouter/...）
   export LLM_API_KEY="<提供者 API 密钥>"
   ```
   如果未设置，请向用户索要这些信息。切勿硬编码或提交密钥。

## 运行扫描

始终使用 `-n`（非交互式/无头模式）—— 默认的 TUI 会阻塞代理。除非用户另有说明，否则始终设置 `--max-budget`。

```bash
# 本地代码（白盒）
strix -n -t ./ --scan-mode standard --max-budget 10

# 部署的应用程序 / API（黑盒）
strix -n -t https://staging.example.com --max-budget 20

# 仓库 + 部署的应用程序一起（最佳覆盖范围）
strix -n -t https://github.com/org/app -t https://staging.example.com

# 带有凭证或范围提示的聚焦测试
strix -n -t https://app.example.com \
  --instruction "使用凭证 user@example.com:pass123。聚焦于 IDOR 和身份验证绕过。"

# API 规范作为一级目标（OpenAPI/Swagger 或 Postman 集合导出）
strix -n -t ./openapi.yaml -t https://api.staging.example.com

# 从文件中获取多个目标，每行一个
strix -n --target-list ./targets.txt --max-budget 30

# 给代理一个文件以供使用（单词列表、规范、笔记），而无需将其作为目标
strix -n -t https://staging.example.com --workspace-file ./wordlist.txt --max-budget 20
```

使用 `-t` 传递的本地路径会挂载到沙盒中**可写**——代理可以读取和修改它，因此指向一个干净的检出，而不是您关心的未提交工作。

关键标志：

| 标志 | 含义 |
|---|---|
| `-t, --target` | URL、仓库 URL、本地路径、域名、IP、OpenAPI/Postman 规范，或 `postman://<uuid>`。可重复。 |
| `--target-list PATH` | 目标文件，每行一个（允许 `#` 注释）。可重复，与 `-t` 结合使用。 |
| `-n, --non-interactive` | 无头模式，完成后退出。代理必需。 |
| `-m, --scan-mode` | `quick`（分钟）/ `standard`（~30 分钟）/ `deep`（小时，默认）。 |
| `--instruction` / `--instruction-file` | 凭证、聚焦区域、范围规则。 |
| `--workspace-file PATH[:DEST]` | 在扫描前将此机器上的文件复制到 `/workspace`，用于单词列表、规范或笔记。可重复。 |
| `--max-budget USD` | LLM 花费上限；扫描在限制处干净地结束。 |
| `--max-turns N` | 每个代理回合上限（默认 500）。 |
| `--resume RUN_NAME` | 从 `strix_runs/` 中恢复先前的运行，保留其代理历史记录和目标。不能与 `-t` 结合使用。 |
| `--scope-mode` | 对于代码目标：`auto`（CI/无头模式中的差异范围）、`diff`（强制仅更改的文件）、`full`（整个树）。 |
| `--diff-base REF` | 与 `diff` 范围比较的分支或提交。默认为仓库的默认分支。 |

扫描需要几分钟（`quick`）到几小时（`deep`）。在后台运行它们并轮询完成状态，而不是阻塞。

### 退出代码（无头模式）

- `0` — 完成且在分析的内容中没有验证的漏洞
- `1` — 严重错误（缺少环境变量、Docker 停止、配置错误）
- `2` — 发现漏洞

`0` 不是完整覆盖的证明：如果 `--max-budget`/`--max-turns` 在扫描完成前达到，它将提前结束并仍然退出 `0`。当您需要确保扫描完成时，给它足够的预算并检查 `strix_runs/<run>/run.json`：硬预算停止会留下 `status: "stopped"`，但在预算警告下提前结束的代理仍然调用 `finish_scan` 并记录 `"completed"` —— 因此，在将干净的结果视为完整覆盖之前，请检查运行的成本与 `--max-budget` 和报告声明的覆盖范围是否一致。

### 读取结果

工件位于 `strix_runs/<run-name>/`：

| 文件 | 内容 |
|---|---|
| `penetration_test_report.md` | 执行报告 —— 首先阅读此文件。 |
| `vulnerabilities/*.md` | 每个验证的发现一个文件，包含 PoC 和修复建议。 |
| `vulnerabilities.json` / `vulnerabilities.csv` | 所有发现作为结构化 JSON / CSV 索引。 |
| `findings.sarif` | SARIF 2.1.0，用于 GitHub 代码扫描 / ASPM 导入。 |
| `run.json` | 运行元数据、状态、目标、使用情况/成本。 |

---

# 选项 B — 托管云服务（无需本地基础设施）

相同的 `strix` 二进制文件驱动托管平台。每个命令都以 `strix cloud` 开头。详细信息——资产注册、源代码上传、报告、PR 审查、计划任务、Webhook 和计费——在 **managed-pentesting-with-strix** 技能中。最小流程：

```bash
# 1. 登录（设备流程——用户在浏览器中确认代码；这也创建了账户和工作区，如果需要）
strix cloud login

# 如果需要特定权限，使用 --scopes 请求它们：
#   strix cloud login --scopes scans:read scans:write assets:read assets:write \
#     vulnerabilities:read billing:read billing:write

# 2. 注册并验证目标域名（验证会打印用户 DNS 记录）
strix cloud domains add --domain staging.example.com --asset-type web_app
strix cloud domains verify <domain-id>

# 3. 启动并等待
strix cloud scans start --engagement-type live_test --domain-ids <domain-id> --wait

# 4. 读取验证的发现
strix cloud vulns list --severity critical
```

对于本地仓库，`strix cloud scans start --source .` 上传工作树（需要 `uploads:write`）并推断代码审查。当信用额度用完时，`strix cloud billing topup` 启动一个代理可支付的 Stripe 挑战——托管技能涵盖了支付流程。当 stdout 不是一个终端时，输出是 JSON，因此命令可以在脚本中组合。

原始 REST API 也有效 (`https://app.strix.ai/api/v1`，组织范围的凭据令牌——见 [docs.app.strix.ai](https://docs.app.strix.ai))。如果 Docker 或本地先决条件尚未满足，请使用此路径，而不是尝试安装基础设施。

---

## 报告和下一步

按严重性（关键/高/中/低/信息）总结发现，并包含 PoC 证据。为了修复和验证修复（通过两种路径），使用 **fix-security-vulnerabilities-with-strix** 技能。要将扫描集成到 CI/CD 中，使用 **ci-security-scanning-with-strix** 技能。

## 安全性

仅扫描用户拥有或有权测试的目标。云平台在执行外部扫描前强制域名验证；对于 OSS CLI，如果目标看起来像第三方基础设施，请自行确认授权。
