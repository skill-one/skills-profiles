# acomo CLI / API 标准指南

acomo 是一个工作流管理平台。本指南将引导您了解 **acomo CLI 和公开 API 的标准使用方法**（模型列表、模型定义获取、流程启动、保存、提交、批准、拒绝、退回等）。

## 前提条件与执行环境

- 需要确保 **能够执行 acomo CLI 的环境**（PATH 中存在 `acomo`）。
- 当代理（Agent）执行 CLI 时，在远程沙盒等环境中可能无法自动继承本地 `~/.acomo/config.json` 或环境变量。在 CI 或代理执行时，推荐设置环境变量（`ACOMO_ACCESS_TOKEN`, `ACOMO_TENANT_ID`, `ACOMO_BASE_URL`）。
- 即使未设置认证，API 命令也存在，执行时会以退出码 2 和 stderr 中的 `AUTH_REQUIRED` 失败。这种情况下，请提示用户重新登录（或设置环境变量）。

## 认证错误处理

**出现认证错误（未设置认证/401/403、退出码 2）时，不要尝试通过尝试错误来解决问题。** 应立即提示用户登录并中断处理。

- 执行 `acomo login` 或设置环境变量 `ACOMO_ACCESS_TOKEN`, `ACOMO_TENANT_ID`。

## 认证

- **本地使用**: 通过 `acomo login` 将 `~/.acomo/config.json` 持久化保存。
- **CI 或代理环境**: 推荐使用环境变量进行认证。

访问令牌是在浏览器中登录 acomo 后获取的，并在 CLI 中指定。

```bash
# 使用环境变量认证（非交互式）
export ACOMO_ACCESS_TOKEN="your-token"
export ACOMO_TENANT_ID="your-tenant-id"

# 或者通过 login 保存
acomo login --tenant-id <tenantId> --access-token <accessToken>
```

| 环境变量             | 说明                                            | 必须项 |
| -------------------- | ----------------------------------------------- | ---- |
| `ACOMO_ACCESS_TOKEN` | 访问令牌                                        | Yes  |
| `ACOMO_TENANT_ID`    | 租户 ID                                         | Yes  |
| `ACOMO_BASE_URL`     | API 基础 URL（省略时: `https://acomo.app`）     | No   |

CLI 的输出是 JSON 格式。参数可通过 `acomo <operationId> --help` 查询。

## 调用格式

```bash
acomo <operationId> [--option value...] [body-json]
```

- **path/query 参数** → `--name value` 形式的 named option
- **请求体** → 位置参数的 JSON 字符串（或 stdin）

```bash
# 仅 path 参数（GET 等）
acomo getWorkflowModel --modelId <ID>

# query 参数
acomo listWorkflowModels --take 10 --filter '{"name":{"contains":"申请"}}'

# 仅 body（POST）
acomo createWorkflowModel '{"name":"费用申请","definition":{},"dataSchema":{},"policy":{}}'

# path 参数 + body（PUT）
acomo saveWorkflowModel --modelId <ID> '{"name":"费用申请","definition":{},"dataSchema":{},"policy":{}}'

# 从 stdin 传递 body
echo '{"name":"费用申请","definition":{},"dataSchema":{},"policy":{}}' | acomo createWorkflowModel
```

## 标准流程

1. **模型列表**: 使用 `acomo listWorkflowModels` 查找目标模型。过滤示例: `acomo listWorkflowModels --take 10 --filter '{"name":{"contains":"申请"}}'`
2. **模型定义**: 使用 `acomo getWorkflowModel --modelId <ID>` 获取 definition / dataSchema / policy 的 JSON。
3. **流程操作**: 根据需要使用 `startWorkflowProcess` / `saveWorkflowProcess` / `submitWorkflowProcess` / `submitWorkflowProcessWithNodeId` / `approveWorkflowProcess` / `rejectWorkflowProcess` / `revertWorkflowProcess`。自己的流程列表可考虑使用 `listMyProcesses` 或 `listProcessWithNodeActions`。

## 主要命令概览

| 用途 | 命令 |
| --- | --- |
| 模型列表 | `listWorkflowModels` |
| 获取模型定义 | `getWorkflowModel --modelId <ID>` |
| 编辑中模型 | `getWorkflowModelWithLatestModelHistory --modelId <ID>` |
| 流程启动 | `startWorkflowProcess --modelId <ID>` |
| 数据保存 | `saveWorkflowProcess --processId <ID> '{"data":{...}}'` |
| 提交 | `submitWorkflowProcess --processId <ID>` |
| 批准 | `approveWorkflowProcess --processId <ID>` |
| 拒绝 | `rejectWorkflowProcess --processId <ID>` |
| 退回 | `revertWorkflowProcess --processId <ID> --nodeId <nodeId>` |
| 自己的流程列表 | `listMyProcesses` / `listProcessWithNodeActions` |
| 获取自己的流程 | `getMyProcesses` / `getProcessWithNodeActions` |

流程操作中，在任务节点需根据 dataSchema 沿着 `saveWorkflowProcess` 的 body 中的 `data` 字段发送数据。通过 submit / approve / reject / revert 执行状态转移。根据 policy 的 write/read 规则，仅处理当前节点可编辑的项。

## 补充说明

- 数据结构（definition / dataSchema / policy / 条件式）的详细说明请参考 [reference.md](reference.md)。
- 所有命令列表可通过 `acomo --help` 查看。
