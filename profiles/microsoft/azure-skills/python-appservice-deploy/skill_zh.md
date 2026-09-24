# Python on Azure App Service — 代码部署

将 Python (Flask, Django, FastAPI, 通用) 代码部署到 Azure App Service Linux (P0v3, Python 3.14)。若资源组 (RG)、规划 (Plan) 和 Web 应用不存在，则予以创建。将 VNet、密钥库、数据库或基础设施即代码 (IaC) 的工作移交给 `azure-prepare`。

**使用的 MCP 工具**: `mcp_azure_mcp_subscription_list`, `mcp_azure_mcp_group_list`, `mcp_azure_mcp_appservice`, `mcp_azure_mcp_azd` (当存在 `azure.yaml` 时)。

## 工作流程

1. **解析上下文 — 智能默认值，最小化提示。** 仅交互式输入应用名称；资源组 (`<app>-rg`)、规划 (`<app>-plan`)、区域（当前的 `az` 默认值或 `eastus2`）、订阅凭据通过推导得到。[create-app.md](references/create-app.md) §1。
2. **检测框架**（仅供参考，不阻塞流程）。[detect.md](references/detect.md)。
3. **选择路径** — 若为 `azure.yaml` 主机：指向 appservice 路径 → [deploy-azd.md](references/deploy-azd.md)；否则指向 [deploy-azcli.md](references/deploy-azcli.md)。
4. **确保 RG → Plan (`P0v3 --is-linux`) → Web App (`--runtime "PYTHON:3.14"`)** 已存在。遇到瞬态 ARM 错误时，请遵循 [transient-retry.md](references/transient-retry.md)。[create-app.md](references/create-app.md)。
5. **设置启动** — Flask/Django：无需设置（Oryx 会自动检测）。FastAPI：始终设置 `python -m uvicorn main:app --host 0.0.0.0`。其他情况：发出警告。[startup-commands.md](references/startup-commands.md)。
6. **设置 `SCM_DO_BUILD_DURING_DEPLOYMENT=true`**。
7. **部署** — 执行 `azd deploy` 或 `az webapp deploy --type zip --track-status false`。
8. **结束。打印部署后消息** ([post-deploy-message.md](references/post-deploy-message.md)) 并结束本次对话。

### 硬性规则

- ⛔ **不执行部署后验证** — 部署返回后，不要运行 `az webapp log tail`、`curl`、`Invoke-WebRequest` 或任何健康探测。App Service 需要 2–3 分钟预热；日志静默或早期出现 5xx 错误并不代表失败。
- ⛔ **shell 安全** — 对于 `--runtime` 参数，始终使用 `"PYTHON:3.14"`（冒号）。严禁使用 `"PYTHON|3.14"`（管道符是 shell 操作符）。
- ⛔ **切勿执行 `az webapp up`** — 该命令已弃用。请使用第 7 步的命令。
- ✅ **URL 格式** — 以 `https://...` 形式的 URL 呈现端点。

## 错误处理

请参阅 [errors.md](references/errors.md) 获取完整的 症状 → 原因 → 修复 矩阵。快速排查要点：缺少 plan/app → 重新执行第 4 步；8000 端口容器 ping 超时 → 修复启动配置（第 5 步）；部署后出现 `ModuleNotFoundError` → 确保已执行第 6 步，并重新部署。
