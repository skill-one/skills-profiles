# Datadog 技能

AI 代理所需的核心 Datadog 技能。

## 核心技能

| 技能 | 描述 |
|------|-------------|
| **dd-account-setup** | 确保 Datadog 账户在正确的区域拥有有效的 API 密钥；验证密钥，修复错误区域的 403 错误，登录或创建账户 |
| **dd-apm** | 跟踪、服务、性能分析 |
| **dd-apps**              | 构建 Datadog 应用程序 — 框架、运行、上传、发布、CI/CD |
| **dd-aws-integration** | 使用 Terraform 将 AWS 账户连接到 Datadog - 跨账户 IAM 角色、指标和资源收集 |
| **dd-azure-integration** | 使用 Terraform 将 Azure 订阅或管理组连接到 Datadog - Entra 应用程序注册、监控读取器 |
| **dd-browser-sdk** | 浏览器 SDK 设置、RUM、日志、会话回放、版本迁移 |
| **dd-docs** | 搜索 Datadog 文档 |
| **dd-gcp-integration** | 使用 Terraform 将 GCP 项目或文件夹连接到 Datadog - 无密钥服务账户模拟 |
| **dd-llmo** | LLM 可观察性跟踪、实验、评估 |
| **dd-logs** | 搜索日志、管道、存档 |
| **dd-monitors** | 创建、管理、静音监控器和警报 |
| **dd-oci-integration** | 使用 Terraform 将 Oracle Cloud 订阅连接到 Datadog - Datadog 的官方 OCI 模块 |
| **dd-product-recommender** | 为代码库和/或目标推荐合适的 Datadog 产品（仅推荐） |
| **dd-pup** | 主要 CLI - 所有 pup 命令、认证、PATH 设置 |
| **dd-software-delivery** | CI/CD 工作流技能 — 解锁 PR、筛选不稳定测试 |
| **dd-instrument-rum** | 使用 Datadog 浏览器 RUM 仪器浏览器应用程序 — React、Next.js、Angular、Vue、Nuxt、Svelte、原生 |

## 安装

```bash
# 安装核心技能
npx skills add datadog-labs/agent-skills \
  --skill dd-pup \
  --skill dd-monitors \
  --skill dd-logs \
  --skill dd-apm \
  --skill dd-docs \
  --full-depth -y

# 安装 CI/CD 工作流技能
npx skills add datadog-labs/agent-skills \
  --skill dd-software-delivery/unblock-pr \
  --skill dd-software-delivery/triage-flaky-test \
  --full-depth -y
```

## 前置条件

请参阅 [Setup Pup](https://github.com/datadog-labs/agent-skills/tree/main?tab=readme-ov-file#setup-pup) 了解安装和认证。

## 命令执行策略

使用此顺序执行作用域命令：

1. 首先检查上下文（对话、先前的输出、已知值）。
2. 当所需值缺失时运行发现命令。
3. 仅在值仍然模糊时询问用户。
4. 在已知所需输入后运行目标命令。
5. 避免可能失败的推测性命令。

## 快速参考

| 任务 | 命令 |
|------|---------|
| 搜索错误日志 | `pup logs search --query "status:error" --from 1h` |
| 列出监控器 | `pup monitors list` |
| 安排监控器停机时间 | `pup downtime create --file downtime.json` |
| 查找慢速跟踪 | `pup traces search --query "service:api @duration:>500ms" --from 1h` |
| 查询指标 | `pup metrics query --query "avg:system.cpu.user{*}"` |
| 检查认证 | `pup auth status` |
| 刷新令牌 | `pup auth refresh` |

## 认证

```bash
pup auth login          # OAuth2（推荐）
pup auth status         # 检查令牌
pup auth refresh        # 刷新过期令牌
```

**令牌过期**：OAuth 令牌过期（约 1 小时）。如果命令因 401/403 失败，请运行 `pup auth refresh`。

## 更多技能

更多技能即将推出。

```bash
npx skills add datadog-labs/agent-skills --list --full-depth
```
