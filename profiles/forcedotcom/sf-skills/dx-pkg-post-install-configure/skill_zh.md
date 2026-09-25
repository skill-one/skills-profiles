## 何时使用此技能

在自动化 Salesforce 任何受管理的包的安装后配置时使用此技能。该技能读取包的安装后文档，发现可用的执行方法，并自动化配置步骤——包括权限集、对象/字段权限、页面布局、Visualforce 页面访问和标签设置。

## 输入

- **必需：** 包名称（例如，`LMA`、`FMA`、`work.com`）
- **可选：** 安装后文档路径（PDF、Markdown、URL）

如果未提供文档，请要求用户提供。

## 工作流程

按顺序执行阶段。每个阶段必须通过才能继续。

---

### 阶段 1：发现可用的执行方法

**优先顺序：**
1. 组织原生平台 MCP 服务器（最高——通过 Headless 360 直接访问组织）
2. Claude Code 外部 MCP 服务器（sf-sobject-all、sf-sobject-all-sb 等）
3. sf CLI 备用（如果已认证始终可用）

#### 步骤 1A：解析组织 API 版本

动态发现组织的当前 API 版本——永远不要硬编码版本号：

```bash
sf org display --target-org <别名> --json
```

从 JSON 响应中读取 `result.apiVersion`（例如，`"67.0"`）。存储此值并在后续所有 REST 路径中将其用作 `v<apiVersion>`。如果命令失败，则回退到此技能的元数据中声明的 `minApiVersion`（`67.0`）。

#### 步骤 1B：检查组织原生平台 MCP 服务器

查询 Tooling API 以检查 MCP 服务器是否可用：

```bash
sf api request rest "/services/data/v<apiVersion>/tooling/query?q=SELECT+Id,DeveloperName,MasterLabel+FROM+McpServerAccess" --target-org <别名>
```

#### 步骤 1C：确定执行方法

检查哪些 Claude Code MCP 工具可用并已通过身份验证。

**MCP 工具前缀按组织类型：**

| 组织类型 | 工具前缀 |
|---|---|
| 生产环境 | `mcp__sf-sobject-all__` |
| 沙盒 | `mcp__sf-sobject-all-sb__` |
| Falcon 测试（pc-rnd） | `mcp__sf-sobject-all-falcon__` |

如果 MCP 需要身份验证，请调用身份验证工具。如果身份验证失败，则回退到 sf CLI。

---

### 阶段 2：验证身份验证和组织身份

1. 运行轻量级测试查询（`SELECT Id, Name, IsSandbox FROM Organization`）
2. 如果 MCP 身份验证失败，则自动回退到 sf CLI
3. 显示组织信息并要求用户确认后再继续

---

### 阶段 3：验证包安装

1. 确定包的命名空间（如果未知，请询问用户）
2. 通过 Tooling API（`InstalledSubscriberPackage`）检查——**不要**使用 `PackageLicense`
3. 如果未找到包，则停止并通知用户

---

### 阶段 4：读取和解析安装后文档

读取提供的文档并提取离散的配置步骤。

**支持的格式：** PDF、Markdown、URL（通过 WebFetch）、粘贴的文本。

**解析方法：**
1. 从文档中提取每个编号/项目符号步骤
2. 在继续之前向用户展示提取的步骤以供验证

---

### 阶段 5：分类步骤和交互式计划审查

对于从文档中提取的每个步骤，将其分类为自动或手动。

#### 自动化能力参考

**通过 MCP（sobject-all）或 sf CLI CRUD：**
- 对任何标准或自定义对象进行 CRUD（PermissionSet、ObjectPermissions、FieldPermissions、SetupEntityAccess、PermissionSetTabSetting、PermissionSetAssignment 等）

**通过 Metadata API 获取/部署（sf CLI）：**
- 页面布局修改（添加相关列表、字段、部分）
- 配置文件设置
- 自定义元数据类型记录

**通过 sf CLI Tooling API：**
- Tooling 查询（InstalledSubscriberPackage、ApexPage、ApexClass 等）
- 任何可访问的 Tooling 操作

**手动（没有 API 路径——需要 Setup UI）：**
- 未通过 REST 暴露的系统权限
- 连接应用的 OAuth 配置
- 环境 Hub 链接

#### 交互式批准

展示分类的计划并让用户选择：
- **"全部批准"** — 按计划执行所有步骤
- **"让我选择"** — 选择要批准/跳过的步骤
- **"我有问题"** — 在决定之前讨论特定步骤

---

### 阶段 6：执行批准的步骤

对于每个批准的步骤，使用解析的执行方法。

#### 执行方法参考

| 操作 | 通过 MCP | 通过 sf CLI |
|---|---|---|
| SOQL 查询 | `soqlQuery` 工具 | `sf data query --query "<SOQL>" --target-org <别名> --json` |
| 创建记录 | `createSobjectRecord` 工具 | `sf data create record --sobject <对象> --values "..." --target-org <别名> --json` |
| 更新记录 | `updateSobjectRecord` 工具 | `sf data update record --sobject <对象> --record-id <id> --values "..." --target-org <别名> --json` |
| 描述对象 | `getObjectSchema` 工具 | `sf api request rest "/services/data/v<apiVersion>/sobjects/<对象>/describe" --target-org <别名>` |
| 页面布局 | N/A | Metadata API 获取/部署 |

#### 通过 Metadata API 修改页面布局

使用 `sf project retrieve start` → 编辑布局 XML → `sf project deploy start`。

#### 执行规则

- **幂等性：** 在创建任何记录之前，查询以检查它是否已存在。如果存在，则跳过。
- **每步报告：** 显示成功计数、跳过项和原因。
- **自动回退：** 如果 MCP 在执行中途失败，则通过 sf CLI 重试。
- **失败时：** 报告错误，要求用户重试/跳过/停止。

---

### 阶段 7：指导手动步骤（如有）

如果任何步骤无法自动化，请展示每个步骤的 Setup 导航说明。
等待用户确认后再继续到下一个步骤。

---

### 阶段 8：总结

显示最终总结，包括每步状态、使用的执行方法以及任何跳过的项。

---

## 错误处理

- **执行中途身份验证失败：** 停止，要求用户重新认证，提供继续选项
- **重复记录错误：** 治为"已配置"，跳过并继续
- **权限错误：** 报告缺少哪个权限，建议解决方案
- **未知步骤类型：** 要求用户澄清，提供标记为手动选项

## 注意事项

- **优先级：** 组织原生 MCP > Claude Code MCP > sf CLI > 手动
- sf CLI 始终是所有 CRUD 和 Tooling API 操作的有效回退
- 页面布局修改通过 Metadata API 获取/部署自动化
- 在进行任何更改之前，始终验证组织身份
- 所有操作都尊重已认证用户的权限
