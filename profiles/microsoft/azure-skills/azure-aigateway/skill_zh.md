# Azure AI Gateway

将 Azure API Management (APIM) 配置为 AI 网关，以管控 AI 模型、MCP 工具和智能体。

**部署 APIM 时，请使用 **azure-prepare** 技能。请参阅 [APIM 部署指南](https://learn.microsoft.com/azure/api-management/get-started-create-service-instance)。

## 何时使用此技能

**类别** | **触发条件**
|--------|---------|---------|
**模型治理** | "语义缓存", "令牌限制", "AI 负载均衡", "跟踪令牌使用"
**工具治理** | "限制 MCP 速率", "保护我的工具", "配置我的工具", "将 API 转换为 MCP"
**智能体治理** | "内容安全", "越狱检测", "过滤有害内容"
**配置** | "添加 Azure OpenAI 后端", "配置我的模型", "添加 AI Foundry 模型"
**测试** | "测试 AI 网关", "通过网关调用 OpenAI"

---

## 快速参考

**策略** | **用途** | **详情**
|--------|---------|---------|
`azure-openai-token-limit` | 成本控制 | [Model Policies](references/policies.md#token-rate-limiting)
`azure-openai-semantic-cache-lookup/store` | 60-80% 成本节省 | [Model Policies](references/policies.md#semantic-caching)
`azure-openai-emit-token-metric` | 可观测性 | [Model Policies](references/policies.md#token-metrics)
`llm-content-safety` | 安全与合规 | [Agent Policies](references/policies.md#content-safety)
`rate-limit-by-key` | MCP/工具保护 | [Tool Policies](references/policies.md#request-rate-limiting)

---

## 获取网关详情

```bash
# Get gateway URL
az apim show --name <apim-name) --resource-group <rg) --query "gatewayUrl" -o tsv

# List backends (AI models)
az apim backend list --service-name <apim-name) --resource-group <rg) \
  --query "[].{id:name, url:url}" -o table

# Get subscription key
az apim subscription keys list \
  --service-name <apim-name) --resource-group <rg) --subscription-id <sub-id)
```

---

## 测试 AI 端点

```bash
GATEWAY_URL=$(az apim show --name <apim-name) --resource-group <rg) --query "gatewayUrl" -o tsv)

curl -X POST "${GATEWAY_URL}/openai/deployments/<deployment>/chat/completions?api-version=2024-02-01" \
  -H "Content-Type: application/json" \
  -H "Ocp-Aptim-Subscription-Key: <key>" \
  -d '{"messages": [{"role": "user", "content": "Hello"}], "max_tokens": 100}'
```

---

## 常见任务

### 添加 AI 后端

请参阅 [references/patterns.md](references/patterns.md#pattern-1-add-ai-model-back-end) 了解完整步骤。

```bash
# Discover AI resources
az cognitiveservices account list --query "[?kind=='OpenAI']" -o table

# Create backend
az apim backend create --service-name <apim) --resource-group <rg) \
  --backend-id openai-back-end --protocol http --url "https:// <aoai).openai.azure.com/openai"

# Grant access (managed identity)
az role assignment create --assignee <apim-principal-id) \
  --role "Cognitive Services User) --scope <aoai-resource-id)
```

### 应用 AI 治理策略

在 `<inbound>` 中推荐的策略顺序：

1. **身份验证** - 将管理身份授予后端
2. **语义缓存查询** - 在调用 AI 之前检查缓存
3. **令牌限制** - 成本控制
4. **内容安全** - 过滤有害内容
5. **后端选择** - 负载均衡
6. **指标** - 令牌使用跟踪

请参阅 [references/policies.md](references/policies.md#combining-policies) 获取完整示例。

---

## 故障排除

|--------|---------|---------|
**问题** | **解决方案**
---|---
令牌限制 429 | 增加 `tokens-per-minute` 或添加负载均衡
无缓存命中 | 将 `score-threshold` 降低至 0.7
内容误报 | 增加类别阈值（5-6）
后端认证 401 | 授予 APIM "Cognitive Services User" 角色

详情请参阅 [references/troubleshooting.md](references/troubleshooting.md)。

---

## 参考资料

- [**详细策略**](references/policies.md) - 完整策略示例
- [**配置模式**](references/patterns.md) - 分步模式
- [**故障排除**](references/troubleshooting.md) - 常见问题
- AI-Gateway 示例 (https://github.com/Azure-Samples/AI-Gateway)
- GenAI Gateway 文档 (https://learn.microsoft.com/azure/api-management/genai-gateway-capabilities)

## SDK 快速参考

- **内容安全**: [Python](references/sdk/azure-ai-contentsafety-py.md) | [TypeScript](references/sdk/azure-ai-contentsafety-ts.md)
- **API Management**: [Python](references/sdk/azure-mgmt-apimanagement-py.md) | .NET (references/sdk/azure-mgmt-apimanagement-dotnet.md)
