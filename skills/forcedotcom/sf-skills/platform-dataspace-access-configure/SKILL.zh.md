---
name: platform-dataspace-access-configure
description: 使用此技能配置或检查 Salesforce Data Cloud DataSpace 对权限集的访问权限。通过 MDAPI 权限集 XML 中的 dataspaceScopes 元素授予数据空间级别的访问权限，可选择通过对象访问授权连接 API 授予 DMO、DLO 或 CIO 对象的对象级别访问权限，并通过只读权限集元数据检索检查现有范围。触发条件：用户需要创建或更新具有数据空间访问权限的权限集、授予特定数据空间的访问权限、列出具有数据空间访问权限的权限集、配置 dataAccessLevel/objectAccessLevel、添加 RBAC 对象访问授权，或列出/移除权限集 + 数据空间对的访问授权。不触发条件：任务是一个没有数据空间访问权限的通用权限集（使用 platform-permission-set-generate）、请求涉及数据摄取/流，或工作涉及创建数据空间本身而不是授予对它们的访问权限。
---

# platform-dataspace-access-configure

使用双层模型配置 Salesforce Data Cloud 中的 DataSpace 访问权限：

1. **DataSpace 级别的访问权限** — 通过在权限集 XML 中嵌入 `<dataspaceScopes>` 元素，并通过 MDAPI 授予 DataSpace 访问权限。
2. **对象级别的访问权限（可选）** — 使用 Object Access Grants Connect API 授予权限集访问 DataSpace 内特定 DMO / DLO / CIO 对象的权限。

MDAPI 层是建立 PermissionSet → DataSpace 关联关系所必需的。Connect API 层是可选的，并且仅在访问权限应限定于特定对象，而不是完全由数据治理策略管理时才需要。

---

## 首先确定用例

在编写任何文件之前，从下表中选择一个用例。每个用例都有不同的输出形状。

| 用例 | 用户意图 | 权限集状态 | 要生成的文件 |
|---|---|---|---|
| **A. 创建新的权限集并授予 DataSpace 访问权限** | "创建一个名为 X 的权限集，其 DataSpace 范围为 Y" | 尚不存在 | `permissionsets/<Name>.permissionset-meta.xml` **和** `package.xml` |
| **B. 向现有权限集添加 DataSpace 访问权限** | "授予现有权限集 X 对 DataSpace Y 的访问权限" | 已部署（可能包含其他权限） | 补丁化的 `permissionsets/<Name>.permissionset-meta.xml` **和** `package.xml` — 请参阅用例 B 工作流 |
| **C. 仅对象级别授权** | "授予权限集 X 对对象 Z（在 DataSpace Y 中）的访问权限" — 权限集 + 范围已配置 | 已部署并包含 `dataspaceScopes` | `api-request.json`（Connect API 正文）。NO 权限集 XML，NO `package.xml` |
| **D. 检查现有 DataSpace 访问权限** | "哪些权限集可以访问 DataSpace Y？" | 任何 | 仅聊天/报告。NO 可部署文件，NO 运行时 API 修改 |

仅生成您选择的用例所列出的文件。为用例 C 提示生成用例 A/B 文件（反之亦然）是正确性失败 — 额外的文件会改变部署形状。

> **用例 B — 关键点：** PermissionSet MDAPI 部署是一个 **完整的元数据替换**。您从重新部署中省略的每个 `<objectPermissions>`、`<fieldPermissions>`、`<userPermissions>`、`<tabSettings>`、`<applicationVisibilities>`、`<recordTypeVisibilities>`、`<customPermissions>`、`<pageAccesses>`、`<classAccesses>`、`<customMetadataTypeAccesses>`、`<customSettingAccesses>`、`<externalDataSourceAccesses>` 元素都会 **从组织中删除**。在将 `<dataspaceScopes>` 添加到现有权限集之前，检索当前的 XML 并进行修补 — 不要从头开始手动编写。

### 用例 B 工作流

1. 检索现有的权限集：
   ```bash
   sf project retrieve start --metadata PermissionSet:<Name> --target-org <alias>
   ```
2. 打开检索到的 `permissionsets/<Name>.permissionset-meta.xml`。保留其中已有的每个元素。
3. 插入目标 DataSpace 的 `<dataspaceScopes>` 块（文件中的元素顺序无关紧要，对于 MDAPI）。如果文件已经有一个针对此相同 DataSpace 的 `<dataspaceScopes>` 块，则仅替换该块。保留其他 DataSpace 的每个 `<dataspaceScopes>` 块不变 — 每个数据空间一个块。对于请求的范围移除，仅删除匹配的块并部署；省略该块将撤销该 DataSpace 授权。通过检索权限集并确认匹配的 `<dataspaceScopes>` 块不存在来验证。
4. 编写 `package.xml`，在 `<members>` 中列出权限集。
5. 使用 `sf project deploy start` 进行重新部署。

---

## 确定此技能拥有任务的条件

当用户想要执行以下操作时触发此技能：
- 创建一个授予访问 Data Cloud DataSpace 的权限集
- 在现有权限集上添加或修改 `dataspaceScopes`
- 授予权限集访问 DataSpace 内特定 DMO / DLO / CIO 对象的权限
- 列出具有 DataSpace 范围的权限集并检查其访问级别
- 配置 DataSpace 范围的 `dataAccessLevel` 和 `objectAccessLevel`
- 列出或移除权限集 + DataSpace 对象的访问授权

在以下情况下将任务委托给其他技能：
- 权限集没有任何 DataSpace 访问权限 → `platform-permission-set-generate`

---

## 第一层 — DataSpace 级别的访问权限（MDAPI）

在 `PermissionSet` XML 内嵌入 `<dataspaceScopes>` 元素。使用 MDAPI 部署。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">
    <label>Data Cloud Analyst</label>
    <description>Data cloud analyst access to the default dataspace</description>
    <hasActivationRequired>false</hasActivationRequired>
    <dataspaceScopes>
        <dataspaceScope>default</dataspaceScope>
        <dataAccessLevel>ALL</dataAccessLevel>
        <objectAccessLevel>BY_POLICY</objectAccessLevel>
    </dataspaceScopes>
</PermissionSet>
```

### 元素规则

| 元素 | 必填 | 有效值 | 目的 |
|---|---|---|---|
| `<dataspaceScopes>` | 是 | 父元素（复数） | 单个 DataSpace 范围授权的容器 |
| `<dataspaceScope>` | 是 | DataSpace API 名称（例如 `default`） | 此授权针对哪个 DataSpace |
| `<dataAccessLevel>` | 是 | `NONE`, `CONTROLLED_BY_PARENT`, `ALL` | DataSpace 内的行级数据访问 |
| `<objectAccessLevel>` | 是 | `BY_POLICY`, `ALL_IN_DATASPACE` | 对象级访问。`BY_POLICY` 委托给数据治理策略。`ALL_IN_DATASPACE` 仅在 `dataAccessLevel` 为 `CONTROLLED_BY_PARENT` 时允许 |

### 常见错误

- **错误的父名称** — 使用 `<dataspaceScopeAccess>` 而不是 `<dataspaceScopes>`。部署会静默失败或出现令人费解的错误。
- **错误的子名称** — 使用 `<dataspaceScopeName>` 而不是 `<dataspaceScope>`。
- **错误的枚举值** — `ViewAllRows` / `Read` / `OWNER` / `EDIT` 不是有效的值。使用 `NONE`、`CONTROLLED_BY_PARENT` 或 `ALL` 作为 `dataAccessLevel`；使用 `BY_POLICY` 或 `ALL_IN_DATASPACE` 作为 `objectAccessLevel`。请参阅元素规则表以获取允许的组合。部署错误 `-379999659` 表示枚举值无效。
- **一个元素中包含多个范围** — `<dataspaceScopes>` 授予对单个 DataSpace 的访问权限。要授予对多个 DataSpace 的访问权限，请添加多个 `<dataspaceScopes>` 块。

### 包布局（用例 A 和用例 B）

用于第一层的可部署包始终包含 **两个** 文件：

```text
<output-root>/
  package.xml
  permissionsets/<Name>.permissionset-meta.xml
```

`package.xml`（必需 — 在 `<members>` 中列出正在部署的每个权限集）：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>Data_Cloud_Analyst</members>
        <name>PermissionSet</name>
    </types>
    <version>67.0</version>
</Package>
```

部署：

```bash
sf project deploy start --source-dir force-app/main/default/permissionsets/ --target-org <alias>
```

---

## 读取-only DataSpace 范围检查 — 用例 D

当用户询问哪些权限集可以访问 DataSpace，或询问检查 `dataAccessLevel` 和 `objectAccessLevel` 而不进行更改时，使用用例 D。

**永远不要使用 SOQL 查询 `DataspaceScope` 或 `DataspaceScopeAccess`。** 这些对象不是此关系的支持查询表面。不要尝试 SOQL 作为发现、回退或故障排除。

1. 将权限集元数据检索到隔离的临时本地项目和输出目录中。不要检索到用户的现有元数据树中。首先保存技能存储库路径（如果可能，作为绝对路径）：
   ```bash
   REPO_ROOT="<absolute/path/to/sf-skills-internal>"  # 或 $(pwd) 如果你在存储库根目录
   WORK_DIR=$(mktemp -d)
   sf project generate --name dataspace-scope-inspection --output-dir "$WORK_DIR"
   cd "$WORK_DIR/dataspace-scope-inspection"
    sf project retrieve start --json \
      --metadata "PermissionSet:*" --target-org <alias> \
      --output-dir "$WORK_DIR/retrieved"
   ```
    在继续之前检查 JSON 结果。命令状态非零、`result.status` 失败、警告或 `result.fileProperties` 计数意外低表示检索可能不完整。报告该限制，而不是将结果视为空，并且不要回退到 SOQL。
2. 从技能目录运行检查脚本（在 `cd` 改变工作目录后不要依赖相对路径）。提供检索到的目录和可选 DataSpace 名称：
   ```bash
   "$REPO_ROOT/skills/platform-dataspace-access-configure/scripts/inspect-dataspace-scopes.sh" \
     "$WORK_DIR/retrieved" "<DataSpace API 名称，如果提供>"
   ```
   将输出报告给用户，每行一个结果。

用例 D 对组织是只读的。不要部署元数据、分配权限集、执行 Apex、执行记录 DML 或发出 POST、PUT、PATCH 或 DELETE 请求。不要在用户的工位空间中作为检查生成 `package.xml`、权限集 XML 或 `api-request.json`。报告后删除临时工作目录：`rm -rf "$WORK_DIR"`。范围级 `objectAccessLevel` 不是显式对象授权的清单；仅在请求时使用只读对象访问授权端点单独检查。

---

## 第二层 — 对象级别访问权限（Connect API）— 用例 C

仅在 `objectAccessLevel` 不是 `BY_POLICY`，或治理策略不涵盖目标对象时才需要。授权是运行时的 — **无 MDAPI 部署，无 `package.xml`，无权限集 XML**。用例 C 任务唯一的工件是一个描述 Connect API 调用的单个 `api-request.json`。

### 首先解析 API 版本

此层中的每个 Connect API `endpoint` 都包含一个 `/services/data/v<apiVersion>/…` 段。**不要硬编码 `v67.0`**。在编写信封之前解析目标组织的实际 API 版本，以便请求与组织的支持表面匹配：

```bash
sf org display --target-org <alias> --json | jq -r '.result.apiVersion'
```

- 将返回的值（例如 `67.0`、`68.0`）作为 `v<apiVersion>` 代入 `endpoint`。
- 如果组织无法查询（离线创作，尚无别名），则回退到此技能的前matter 中的 `minApiVersion`（`67.0`） — 该端点是在那里引入的，任何较新版本都接受相同的正文。
- 如果用户在提示中明确指定了版本，则使用该文本。

在下面的模板中，`{apiVersion}` 是一个占位符。在发出 `api-request.json` 之前，用解析的 API 版本（例如 `67.0`、`68.0`）替换它。

### `api-request.json` — 标准形状

将请求作为具有 `method`、`endpoint`、`headers`、`body` 和 `expectedResponse` 的自描述信封发出。**不要仅发出正文** — 审查者和下游工具会读取信封。

```json
{
  "method": "POST",
  "endpoint": "/services/data/v{apiVersion}/ssot/data-governance/object-access-grants",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "permissionSetName": "Data_Cloud_Analyst",
    "dataSpaceName": "default",
    "objectApiName": "Account__dlm"
  },
  "expectedResponse": {
    "status": 201,
    "body": {
      "permissionSetName": "Data_Cloud_Analyst",
      "dataSpaceName": "default",
      "objectApiName": "Account__dlm"
    }
  }
}
```

### 批量授权

相同的 `api-request.json` 信封形状。`endpoint` 获得(`/actions/bulk-create`后缀)，`body.objectApiName` 被替换为列表值`body.objectApiNames`，`expectedResponse`省略`body`字段，因为批量响应返回每个对象的状

| 规则 | 原因 |
|---|---|
| 使用 `<dataspaceScopes>`（复数）作为父级，`<dataspaceScope>`（单数）作为子级 | XML 模式要求；其他名称部署失败 |
| `dataAccessLevel` 值：仅 `NONE`、`CONTROLLED_BY_PARENT`、`ALL` | 其他值（例如 `OWNER`、`ViewAllRows`）将被拒绝 |
| `objectAccessLevel` 值：仅 `BY_POLICY`、`ALL_IN_DATASPACE` | 其他值（例如 `READ`、`EDIT`、`Read`）将被拒绝。`ALL_IN_DATASPACE` 需要 `dataAccessLevel=CONTROLLED_BY_PARENT` |
| 当存在数据治理策略时，优先使用 `BY_POLICY` | 将行/列过滤委托给中央策略 — 无需为每个对象授予权限 |
| 每个数据空间使用一个 `<dataspaceScopes>` 块 | 在相同的权限集中，为多个数据空间重复该块 |
| 组织必须已配置数据云才能部署 `<dataspaceScopes>` | 在非数据云组织中，该元素将被忽略或拒绝 |
| 不要通过 SOQL 查询 `DataspaceScope` / `DataspaceScopeAccess` | 无法查询；使用案例 D 权限集元数据 API 检查现有范围。切勿将 SOQL 作为后备方案使用 |

---

## 注意事项

| 问题 | 解决方案 |
|---|---|
| 部署失败并显示错误 `-379999659` | 检查枚举值 — `dataAccessLevel` 必须为 `NONE`/`CONTROLLED_BY_PARENT`/`ALL`；`objectAccessLevel` 必须为 `BY_POLICY`/`ALL_IN_DATASPACE` |
| 权限集部署成功，但用户仍无法查询数据空间数据 | 层级 2 未应用 — 如果 `objectAccessLevel != BY_POLICY`，对象需要显式授予权限 |
| 批量创建返回某些对象的 `AlreadyExists` | 幂等操作 — 安全重试；响应显示每个对象的状态 |
| 连接 API 返回 404 错误的对象授予权限端点 | 组织缺少数据云配置，或解析的 API 版本低于最低要求。该端点是在 `v67.0` 中引入的 — 运行 `sf org display --json` 确认组织的 `apiVersion` 字段为 `67.0` 或更高，并将该值替换到 `endpoint` 路径中 |
| 检索到的权限集 XML 显示与部署不同的元素名称 | 元数据 API 有时会回显旧名称 — 始终使用当前名称编写 |
