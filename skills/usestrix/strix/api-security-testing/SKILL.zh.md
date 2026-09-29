---
name: api-security-testing
description: 使用 Strix 对 REST、GraphQL 或 gRPC API 进行安全测试——Strix 是一组自主代理，它们可以从 OpenAPI/GraphQL 架构（或通过爬取）枚举端点，然后实际利用 OWASP API Security Top 10（2023）中 API 特定的漏洞类别——包括对象级授权失效（BOLA/IDOR）、对象属性级授权失效（过度数据暴露和批量赋值）、函数级授权失效、无限制资源消耗、SSRF、注入攻击以及认证/令牌缺陷。每个发现都附带一个可工作的概念验证请求。当用户要求对 API、端点或后端服务进行渗透测试、安全测试、审计或查找漏洞时使用。
---

# 测试 API 的安全性

API 的失败方式与 Web UI 不同：没有渲染的界面可供爬取，有趣的错误通常是授权相关的而非注入相关的，并且相同的端点在不同令牌下表现不同。此工作流程针对 Strix 的自主代理的这些具体问题，使用当前的 [OWASP API 安全 Top 10 (2023)](https://owasp.org/API-Security/editions/2023/en/0x11-t10/) 作为覆盖清单。对于 Web 应用的等效方案，当前版本是 OWASP Top 10:2025 — 请参阅 **owasp-top-10-testing**。

安装、LLM 设置、完整的 CLI 标志以及管理云路径都在 **penetration-testing-with-strix** 技能中。如果 `strix --version` 失败或目标不是 API，请阅读它。对于没有 Docker 且没有 LLM 密钥的运行，相同的二进制文件驱动管理平台：`strix cloud login`，然后 `strix cloud scans start ...`（详情在 **managed-pentesting-with-strix**）。

## 1. 收集代理所需的信息

API 几乎无法盲目测试，因此先收集：

| 输入 | 重要性 |
|---|---|
| **Schema** — OpenAPI/Swagger 文件、Postman 集合、GraphQL 端点（查询 introspection）或 gRPC `.proto` | 将猜测工作转化为完整的端点枚举。覆盖范围最大的单个收益。OpenAPI/Swagger 或 Postman 规范（`.json`/`.yaml`/`.yml`）是 Strix 直接处理的靶标；`.proto` 不是，因此需要使用 `--workspace-file` 传递它。 |
| **两组凭证/令牌**，理想情况下位于不同的租户中 | BOLA/IDOR — API1:2023，仍然是 #1 API 风险 — 只能通过使用租户 B 的令牌访问租户 A 的对象来 *证明*。 |
| **一个低权限和一个高权限令牌** | 用于证明损坏的函数级授权（API5:2023 — 一个 `user` 调用仅管理员路由）。 |
| **示例对象 ID** | 让代理立即测试 ID 恶意篡改，而不是寻找有效标识符。 |
| **超出范围的路线** | 支付、批量通知、破坏性管理端点。 |
| **API 前面的速率限制 / WAF** | 避免代理在限流请求上烧钱；提及它们以便测试适应。 |

向用户索要任何缺失的内容 — 不要编造令牌或扫描不属于他们的 API。

## 2. 运行扫描

将规范作为 **目标** 传递，而不是在指令中以散文形式传递 — Strix 直接解析 OpenAPI/Swagger（`.json`/`.yaml`）和 Postman 集合导出，因此代理从真实的端点列表开始：

```bash
strix -n -t ./openapi.yaml -t https://api.staging.example.com --max-budget 20 \
  --instruction "租户 A 令牌: <tokenA> (org 1111, user id 11, order id 501)。
租户 B 令牌: <tokenB> (org 2222, user id 22)。
管理员令牌: <tokenAdmin>。
重点：跨组织的 BOLA（API1）、/admin/* 上的函数级授权（API5）、PATCH /users/{id} 上的对象属性级授权 — 两者都是批量赋值和在列表响应中过度暴露的字段（API3）、无限制的资源消耗（API4）。
超出范围：POST /billing/*、POST /notifications/broadcast。"
```

- **Postman 而不是 OpenAPI**：集合导出可以作为目标使用（`-t ./collection.postman_collection.json`），或者使用 `-t postman://<collection-uuid>` 拉取实时集合（可选 `"postman://<collection-uuid>?env=<environment-uuid>"`），这需要环境中的 `POSTMAN_API_KEY`。
- **一次测试多个服务**：将一个目标每行放在文件中，并传递 `--target-list ./targets.txt`，可重复并可与 `-t` 组合。
- **添加后端源以进行深度分析**：`-t ./services/api -t https://api.staging.example.com`。通过代码访问，代理可以推理授权检查和对象所有权，而不是从响应中推断。
- **gRPC**：目标端点并将定义作为工作区文件传递，`-t https://grpc.staging.example.com --workspace-file ./service.proto`。只有 `.json`、`.yaml` 和 `.yml` 规范被识别为目标，因此 `-t ./service.proto` 会失败并显示 "Path exists but is not a directory"。
- **GraphQL**：指向 GraphQL 端点并说明是否启用查询 introspection；指出你希望测试批量/别名滥用、深度/复杂度限制和字段级授权。
- **无法从你的机器访问的内部/私有 API**：使用管理平台的网络连接器 — 请参阅 **managed-pentesting-with-strix**。
- 当凭证/上下文块过长时使用 `--instruction-file`，并保持令牌不在 shell 历史记录和提交的文件中。
- **支持文件**代理应该读取但不应测试，例如端点单词列表或关于租户模型的笔记：传递 `--workspace-file ./notes.md`。Strix 将文件复制到 `/workspace`。你机器上的文件不会改变。添加 `:DEST` 选择路径，例如 `--workspace-file ./wordlist.txt:lists/wordlist.txt`。

## 3. 验证结果

`strix_runs/<run>/penetration_test_report.md` 首先查看，然后 `vulnerabilities/*.md` — 每个文件都包含证明问题的确切请求。在报告之前重新播放它（例如，使用 `curl`）；对于授权发现，请确认响应确实包含其他租户的数据，而不是空的 200。

`findings.sarif` 上传到 GitHub 代码扫描；`vulnerabilities.json` 是用于工单的结构化索引。

## 4. 修复、重新测试并保持测试

使用 **fix-security-vulnerabilities-with-strix**（修复授权检查，而不是单个端点），然后重新运行针对相同的靶标以证明漏洞已被消除。使用 **ci-security-scanning-with-strix** 将其集成到拉取请求 CI 中，以便在发布时测试新端点。
