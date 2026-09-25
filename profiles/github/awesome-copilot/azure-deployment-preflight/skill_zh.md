# Azure 部署预执行验证

此技能在执行 Bicep 部署前进行验证，支持 Azure CLI (`az`) 和 Azure Developer CLI (`azd`) 工作流。

## 何时使用此技能

- 部署基础设施到 Azure 之前
- 准备或审查 Bicep 文件时
- 预览部署将带来的变更
- 验证部署权限是否充足
- 运行 `azd up`、`azd provision` 或 `az deployment` 命令之前

## 验证流程

按顺序执行以下步骤。即使前一步失败，也要继续到下一步——在最终报告中捕获所有问题。

### 第 1 步：检测项目类型

通过检查项目指标来确定部署工作流：

1. **检查 azd 项目**：查找项目根目录中的 `azure.yaml`
   - 如果找到 → 使用 **azd 工作流**
   - 如果未找到 → 使用 **az CLI 工作流**

2. **定位 Bicep 文件**：查找所有 `.bicep` 文件以进行验证
   - 对于 azd 项目：首先检查 `infra/` 目录，然后检查项目根目录
   - 对于独立项目：使用用户指定的文件或搜索常见位置（`infra/`、`deploy/`、项目根目录）

3. **自动检测参数文件**：对于每个 Bicep 文件，查找匹配的参数文件：
   - `<filename>.bicepparam`（Bicep 参数 - 优先）
   - `<filename>.parameters.json`（JSON 参数）
   - 同一目录中的 `parameters.json` 或 `parameters/<env>.json`

### 第 2 步：验证 Bicep 语法

在尝试部署验证之前，使用 Bicep CLI 检查模板语法：

```bash
bicep build <bicep-file> --stdout
```

**捕获内容：**
- 带行/列号的语法错误
- 警告消息
- 构建成功/失败状态

**如果未安装 Bicep CLI：**
- 在报告中记录问题
- 继续到第 3 步（Azure 将在 what-if 阶段验证语法）

### 第 3 步：运行预执行验证

根据第 1 步检测到的项目类型选择适当的验证。

#### 对于 azd 项目（存在 `azure.yaml`）

使用 `azd provision --preview` 验证部署：

```bash
azd provision --preview
```

如果指定了环境或存在多个环境：
```bash
azd provision --preview --environment <env-name>
```

#### 对于独立 Bicep（不存在 `azure.yaml`）

根据 Bicep 文件的 `targetScope` 声明确定部署范围：

| 目标范围 | 命令 |
|----------|------|
| `resourceGroup`（默认） | `az deployment group what-if` |
| `subscription` | `az deployment sub what-if` |
| `managementGroup` | `az deployment mg what-if` |
| `tenant` | `az deployment tenant what-if` |

**首先使用 Provider 验证级别运行：**

```bash
# 资源组范围（最常见）
az deployment group what-if \
  --resource-group <rg-name> \
  --template-file <bicep-file> \
  --parameters <param-file> \
  --validation-level Provider

# 订阅范围
az deployment sub what-if \
  --location <location> \
  --template-file <bicep-file> \
  --parameters <param-file> \
  --validation-level Provider

# 管理组范围
az deployment mg what-if \
  --location <location> \
  --management-group-id <mg-id> \
  --template-file <bicep-file> \
  --parameters <param-file> \
  --validation-level Provider

# 租户范围
az deployment tenant what-if \
  --location <location> \
  --template-file <bicep-file> \
  --parameters <param-file> \
  --validation-level Provider
```

**回退策略：**

如果 `--validation-level Provider` 因权限错误（RBAC）失败，重试使用 `ProviderNoRbac`：

```bash
az deployment group what-if \
  --resource-group <rg-name> \
  --template-file <bicep-file> \
  --validation-level ProviderNoRbac
```

在报告中记录回退——用户可能缺乏完整的部署权限。

### 第 4 步：捕获 what-if 结果

解析 what-if 输出以对资源变更进行分类：

| 变更类型 | 符号 | 含义 |
|----------|------|------|
| 创建 | `+` | 新资源将被创建 |
| 删除 | `-` | 资源将被删除 |
| 修改 | `~` | 资源属性将变更 |
| 无变更 | `=` | 资源未变更 |
| 忽略 | `*` | 资源未分析（限制达到） |
| 部署 | `!` | 资源将被部署（变更未知） |

对于修改的资源，捕获具体的属性变更。

### 第 5 步：生成报告

在**项目根目录**创建名为 `preflight-report.md` 的 Markdown 报告文件。

使用来自 [references/REPORT-TEMPLATE.md](references/REPORT-TEMPLATE.md) 的模板结构。

**报告部分：**
1. **摘要** - 总体状态、时间戳、验证文件、目标范围
2. **执行工具** - 运行的命令、版本、使用的验证级别
3. **问题** - 所有错误和警告及严重性和修复建议
4. **what-if 结果** - 创建/修改/删除/无变更的资源
5. **建议** - 可操作的下一步操作

## 必需信息

在运行验证前收集：

| 信息 | 必须用于 | 获取方式 |
|------|----------|----------|
| 资源组 | `az deployment group` | 询问用户或检查现有的 `.azure/` 配置 |
| 订阅 | 所有部署 | `az account show` 或询问用户 |
| 位置 | Sub/MG/租户范围 | 询问用户或使用配置中的默认值 |
| 环境 | azd 项目 | `azd env list` 或询问用户 |

如果缺少必需信息，在继续前提示用户。

## 错误处理

有关详细错误处理指导，请参阅 [references/ERROR-HANDLING.md](references/ERROR-HANDLING.md)。

**关键原则：** 即使出现错误也要继续验证。在最终报告中捕获所有问题。

| 错误类型 | 操作 |
|----------|------|
| 未登录 | 在报告中记录，建议 `az login` 或 `azd auth login` |
| 权限被拒绝 | 回退到 `ProviderNoRbac`，在报告中记录 |
| Bicep 语法错误 | 包含所有错误，继续到其他文件 |
| 工具未安装 | 在报告中记录，跳过该验证步骤 |
| 资源组未找到 | 在报告中记录，建议创建它 |

## 工具要求

此技能使用以下工具：

- **Azure CLI** (`az`) - 推荐 2.76.0+ 版本以用于 `--validation-level`
- **Azure Developer CLI** (`azd`) - 用于具有 `azure.yaml` 的项目
- **Bicep CLI** (`bicep`) - 用于语法验证
- **Azure MCP 工具** - 用于文档查找和最佳实践

开始前检查工具可用性：
```bash
az --version
azd version
bicep --version
```

## 示例工作流

1. 用户："在我运行部署之前验证我的 Bicep 部署"
2. 代理检测到 `azure.yaml` → azd 项目
3. 代理找到 `infra/main.bicep` 和 `infra/main.bicepparam`
4. 代理运行 `bicep build infra/main.bicep --stdout`
5. 代理运行 `azd provision --preview`
6. 代理在项目根目录生成 `preflight-report.md`
7. 代理向用户总结发现结果

## 参考文档

- [验证命令参考](references/VALIDATION-COMMANDS.md)
- [报告模板](references/REPORT-TEMPLATE.md)
- [错误处理指南](references/ERROR-HANDLING.md)
