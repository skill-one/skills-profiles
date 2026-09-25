# Azure App Service 上的 Python — Code Deploy

将 Python (Flask、Django、FastAPI、通用) 代码部署到 Azure App Service Linux (P0v3、Python 3.14)。如果缺少，则创建资源组 (RG) + 计划 + Web 应用。交由 `azure-prepare` 处理 VNet、密钥保管库、数据库或 IaC。

**使用的 MCP 工具**：`mcp_azure_mcp_subscription_list`、`mcp_azure_mcp_group_list`、`mcp_azure_mcp_appservice`、`mcp_azure_mcp_azd`（当 `azure.yaml` 存在时）。

## 工作流

1. **解析上下文 — 智能默认值，最小化提示**。仅应用名称是交互式的；资源组 (`<app>-rg`)、计划 (`<app>-plan`)、区域（当前 `az` 默认或 `eastus2`）、订阅是派生的。[create-app.md](references/create-app.md) §1。
2. **检测框架**（建议性，从不阻塞）。[detect.md](references/detect.md)。
3. **选择路径** — `azure.yaml` 主机：appservice → [deploy-azd.md](references/deploy-azd.md)；否则 [deploy-azcli.md](references/deploy-azcli.md)。
4. **确保资源组 → 计划 (`P0v3 --is-linux`) → Web 应用 (`--runtime "PYTHON:3.14"`) 存在。在瞬态 ARM 错误时，请遵循 [transient-retry.md](references/transient-retry.md)。[create-app.md](references/create-app.md)。
5. **设置启动** — Flask/Django：无（Oryx 自动检测）。FastAPI：始终 `python -m uvicorn main:app --host 0.0.0.0`。其他：警告。[startup-commands.md](references/startup-commands.md)。
6. **设置 `SCM_DO_BUILD_DURING_DEPLOYMENT=true`**。
7. **部署** — `azd deploy` 或 `az webapp deploy --type zip --track-status false`。
8. **停止。打印部署后消息** ([post-deploy-message.md](references/post-deploy-message.md)) 并结束回合。

### 严格规则

- ⛔ **禁止部署后验证** — 部署返回后，不要运行 `az webapp log tail`、`curl`、`Invoke-WebRequest` 或任何健康探针。App Service 需要 2-3 分钟预热；安静日志或早期 5xx 不会失败。
- ⛔ **shell 安全性** — 对于 `--runtime` 始终使用 `"PYTHON:3.14"`（冒号）。绝不使用 `"PYTHON|3.14"`（管道是 shell 操作符）。
- ⛔ **绝不使用 `az webapp up`** — 已弃用。使用第 7 步命令。
- ✅ **URL 格式** — 以 `https://...` 格式显示端点。

## 错误处理

有关完整的症状 → 原因 → 修复矩阵，请参阅 [errors.md](references/errors.md)。快速排查：缺少计划/应用 → 重新运行第 4 步；8000 端口容器 ping 超时 → 修复启动（第 5 步）；部署后 `ModuleNotFoundError` → 确保 第 6 步已运行，重新部署。
