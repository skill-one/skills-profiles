# platform-dataspace-access-configure

使用双层模型在 Salesforce Data Cloud 中配置 DataSpace 访问：

1. **DataSpace 级别的访问** — 通过在权限集 XML 中嵌入 `<dataspaceScopes>` 元素，并通过 MDAPI 授予 DataSpace 一个 `PermissionSet` 访问权限。
2. **对象级别的访问（可选）** — 使用 Object Access Grants Connect API 授予权限集访问 DataSpace 内部特定 DMO / DLO / CIO 对象的权限。

MDAPI 层是建立 PermissionSet → DataSpace 关联所必需的。Connect API 层是可选的，并且仅在访问应限定于特定对象而不是完全受数据治理策略管理时才需要。

---

## 首先确定用例

在编写任何文件之前，从下表中选择一个用例。每个用例都有不同的输出形状。

| 用例 | 用户意图 | 权限集状态 | 要发出的文件 |
|---|---|---|---|
| **A. 创建新的权限集并授予 DS 访问** | "创建一个名为 X 的权限集，具有数据空间范围 Y" | 尚不存在 | `permissionsets/<Name>.permissionset-meta.xml` **和** `package.xml` |
| **B. 向现有权限集添加 DS 访问** | "授予现有权限集 X 对数据空间 Y 的访问权限" | 已部署（可能包含其他权限） | 补丁 `permissionsets/<Name>.permissionset-meta.xml` **和** `package.xml` — 请参阅用例 B 工作流下方 |
| **C. 仅对象级别授权** | "授予权限集 X 对对象 Z（在数据空间 Y 中）的访问权限" — 权限集 + 范围已配置 | 已部署，具有 `dataspaceScopes` | `api-request.json`（Connect API 正文）。NO 权限集 XML，NO `package.xml` |
| **D. 检查现有 DS 访问** | "哪些权限集有权访问数据空间 Y？" | 任何 | 仅聊天/报告。NO 可部署文件，NO 运行时 API 修改 |

仅发出您选择的用例中列出的文件。为用例 C 提示（或反之）发出用例 A/B 文件是正确性失败 — 额外的文件会改变部署形状。

> **用例 B — 关键:** PermissionSet MDAPI 部署是一个 **完整的元数据替换**。您从重新部署中省略的每个 `<objectPermissions>`、`<fieldPermissions>`、`<userPermissions>`、`<tabSettings>`、`<applicationVisibilities>`、`<recordTypeVisibilities>`、`<customPermissions>`、`<pageAccesses>`、`<classAccesses>`、`<customMetadataTypeAccesses>`、`<customSettingAccesses>`、`<externalDataSourceAccesses>` 元素都会 **从组织中删除**。在向现有权限集添加 `<dataspaceScopes>` 之前，检索当前 XML 并进行修补 — 不要从头手写。

### 用例 B 工作流

1. 检索现有的权限集：
   ```bash
   sf project retrieve start --metadata PermissionSet:<Name> --target-org <alias>
   ```
2. 打开检索到的 `permissionsets/<Name>.permissionset-meta.xml`。保留其中已有的每个元素。
3. 插入目标 DataSpace 的 `<dataspaceScopes>` 块（文件中的元素顺序无关紧要，对于 MDAPI）。如果文件已经有一个针对 **此相同 DataSpace** 的 `<dataspaceScopes>` 块，则仅替换该块。保留其他 DataSpace 的每个 `<dataspaceScopes>` 块不变 — 每个数据空间一个块。对于请求的范围移除，仅移除匹配的块并部署；省略该块将撤销该 DataSpace 授予。通过检索权限集并确认匹配的 `<dataspaceScopes>` 块不存在来验证。
4. 编写 `package.xml`，在 `<members>` 中列出权限集。
5. 使用 `sf project deploy start` 重新部署。

---

## 首先确定情况

在编写任何文件之前，从下表中选择**一个**情况。每个情况都有不同的输出形状。

| 情况 | 用户意图 | 权限集状态 | 要发出的文件 |
|---|---|---|---|
| **A. 创建新的 permset 并授予 DS 访问** | "创建一个名为 X 的权限集，具有数据空间范围 Y" | 尚不存在 | `permissionsets/<Name>.permissionset-meta.xml` **和** `package.xml` |
| **B. 向现有 permset 添加 DS 访问** | "授予现有权限集 X 对数据空间 Y 的访问权限" | 已部署（可能包含其他权限） | 补丁 `permissionsets/<Name>.permissionset-meta.xml` **和** `package.xml` — 请参阅用例 B 工作流下方 |
| **C. 仅对象级别授权** | "授予 permset X 对对象 Z（在数据空间 Y 中）的访问权限" — permset + 范围已配置 | 已部署，具有 `dataspaceScopes` | `api-request.json`（Connect API 正文）。NO 权限集 XML，NO `package.xml` |
| **D. 检查现有 DS 访问** | "哪些权限集有权访问数据空间 Y？" | 任何 | 仅聊天/报告。NO 可部署文件，NO 运行时 API 修改 |

仅发出您选择的用例中列出的文件。为用例 C 提示（或反之）发出用例 A/B 文件是正确性失败 — 额外的文件会改变部署形状。

> **用例 B — 关键:** PermissionSet MDAPI 部署是一个 **完整的元数据替换**。您从重新部署中省略的每个 `<objectPermissions>`、`<fieldPermissions>`、`<userPermissions>`、`<tabSettings>`、`<applicationVisibilities>`、`<recordTypeVisibilities>`、`<customPermissions>`、`<pageAccesses>`、`<classAccesses>`、`<customMetadataTypeAccesses>`、`<customSettingAccesses>`、`<externalDataSourceAccesses>` 元素都会 **从组织中删除**。在向现有权限集添加 `<dataspaceScopes>` 之前，检索当前 XML 并进行修补 — 不要从头手写。

### 用例 B 工作流

1. 检索现有的权限集：
   ```bash
   sf project retrieve start --metadata PermissionSet:<Name> --target-org <alias>
   ```
2. 打开检索到的 `permissionsets/<Name>.permissionset-meta.xml`。保留其中已有的每个元素。
3. 插入目标 DataSpace 的 `<dataspaceScopes>` 块（文件中的元素顺序无关紧要，对于 MDAPI）。如果文件已经有一个针对 **此相同 DataSpace** 的 `<dataspaceScopes>` 块，则仅替换该块。保留其他 DataSpace 的每个 `<dataspaceScopes>` 块不变 — 每个数据空间一个块。对于请求的范围移除，仅移除匹配的块并部署；省略该块将撤销该 DataSpace 授予。通过检索权限集并确认匹配的 `<dataspaceScopes>` 块不存在来验证。
4. 编写 `package.xml`，在 `<members>` 中列出权限集。
5. 使用 `sf project deploy start` 重新部署。

---

## 当此技能拥有任务时

在用户想要以下操作时触发此技能：
- 创建一个授予访问 Data Cloud DataSpace 的权限集
- 在现有权限集上添加或修改 `dataspaceScopes`
- 授予权限集访问 DataSpace 内部特定 DMO / DLO / CIO 对象的权限
- 列出哪些权限集具有 DataSpace 范围并检查其访问级别
- 配置 DataSpace 范围的 `dataAccessLevel` 和 `objectAccessLevel`
- 列出或删除权限集 + DataSpace 对的对象访问授权

在以下情况时将任务委托给其他地方：
- 权限集完全没有 DataSpace 访问 → `platform-permission-set-generate`

---

## 第一层 — DataSpace 级别的访问 (MDAPI)

在 `PermissionSet` XML 内部嵌入 `<dataspaceScopes>` 元素。使用 MDAPI 部署。

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

| 元素 | 是否必需 | 有效值 | 目的 |
|---|---|---|---|
| `<dataspaceScopes>` | 是 | 父元素（复数） | 单个数据空间范围授予权限的容器 |
| `<dataspaceScope>` | 是 | DataSpace API 名称（例如 `default`） | 此授予权限是针对哪个 DataSpace |
| `<dataAccessLevel>` | 是 | `NONE`, `CONTROLLED_BY_PARENT`, `ALL` | DataSpace 内的行级数据访问 |
| `<objectAccessLevel>` | 是 | `BY_POLICY`, `ALL_IN_DATASPACE` | 对象级访问。`BY_POLICY` 推迟到数据治理策略。`ALL_IN_DATASPACE` 仅在 `dataAccessLevel` 为 `CONTROLLED_BY_PARENT` 时允许 |

### 常见错误

- **错误的父名称** — 使用 `<dataspaceScopeAccess>` 而不是 `<dataspaceScopes>`。部署会静默失败或出现加密错误。
- **错误的子名称** — 使用 `<dataspaceScopeName>` 而不是 `<dataspaceScope>`。
- **错误的枚举值** — `ViewAllRows` / `Read` / `OWNER` / `EDIT` 不是有效的。使用 `NONE`, `CONTROLLED_BY_PARENT`, 或 `ALL` 对于 `dataAccessLevel`；使用 `BY_POLICY` 或 `ALL_IN_DATASPACE` 对于 `objectAccessLevel`。请参阅元素规则表以获取允许的组合。部署错误 `-379999659` 表示枚举无效。
- **一个元素中包含多个范围** — `<dataspaceScopes>` 授予访问**一个** DataSpace。要授予多个范围，请添加多个 `<dataspaceScopes>` 块。

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

当用户询问哪些权限集有权访问 DataSpace，或询问在不进行更改的情况下检查 `dataAccessLevel` 和 `objectAccessLevel` 时，使用用例 D。

**永远不要使用 SOQL 查询 `DataspaceScope` 或 `DataspaceScopeAccess`。** 这些对象不是此关系的支持查询表面。不要尝试 SOQL 作为发现、回退或故障排除。

1. 将权限集元数据检索到隔离的临时本地项目和输出目录中。不要检索到用户的现有元数据树中。首先保存技能存储库路径（如果可能，作为绝对路径）：
   ```bash
   REPO_ROOT="<absolute/path/to/sf-skills-internal>"  # 或 $(pwd) 如果您在存储库根目录
   WORK_DIR=$(mktemp -d)
   sf project generate --name dataspace-scope-inspection --output-dir "$WORK_DIR"
   cd "$WORK_DIR/dataspace-scope-inspection"
    sf project retrieve start --json \
      --metadata "PermissionSet:*" --target-org <alias> \
      --output-dir "$WORK_DIR/retrieved"
   ```
    在继续之前检查 JSON 结果。命令状态非零、`result.status` 失败、警告或意外低 `result.fileProperties` 计数意味着检索可能不完整。报告该限制，而不是将结果视为空，并且不要回退到 SOQL。
2. 从技能目录运行检查脚本（在 `cd` 改变工作目录后，不要依赖相对路径）。提供检索到的目录和可选 DataSpace 名称：
   ```bash
   "$REPO_ROOT/skills/platform-dataspace-access-configure/scripts/inspect-dataspace-scopes.sh" \
     "$WORK_DIR/retrieved" "<DataSpace API 名称，如果给出>"
   ```
   向用户报告输出，每行一个结果。

用例 D 对组织是只读的。不要部署元数据、分配权限集、执行 Apex、执行记录 DML 或发出 POST、PUT、PATCH 或 DELETE 请求。不要在用户的工位空间中作为检查生成 `package.xml`、权限集 XML 或 `api-request.json`。报告后删除临时工作目录：`rm -rf "$WORK_DIR"`。范围级别的 `objectAccessLevel` 不是显式对象授权的清单；仅在请求时使用只读对象访问授权端点单独检查它们。

---

## 第二层 — 对象级别访问 (Connect API) — 用例 C

仅在 `objectAccessLevel` 不是 `BY_POLICY`，或者治理策略不涵盖目标对象时才需要。授权是运行时的 — **无需 MDAPI 部署，无需 `package.xml`，无需权限集 XML**。用例 C 任务唯一的工件是一个描述 Connect API 调用的单个 `api-request.json`。

### 首先解析 API 版本

此层中的每个 Connect API `endpoint` 都包含 `/services/data/v<apiVersion>/…` 段。**不要硬编码 `v67.0`**。在编写信封之前，先解析目标组织的实际 API 版本，以便请求与组织的支持表面匹配：

```bash
sf org display --target-org <alias> --json | jq -r '.result.apiVersion'
```

- 将返回的值（例如 `67.0`、`68.0`）作为 `v<apiVersion>` 代入 `endpoint`。
- 如果组织无法查询（离线创作，还没有别名），则回退到此技能的前matter 中的 `minApiVersion`（`67.0`） — 该端点是在那里引入的，任何更新的版本都接受相同的正文。
- 如果用户在提示中明确指定了版本，则原样使用该版本。

在以下模板中，`{apiVersion}` 是一个占位符。在发出 `api-request.json` 之前，用解析的 API 版本（例如 `67.0`、`68.0`）替换它。

### `api-request.json` — 标准形状

将请求作为具有 `method`、`endpoint`、`headers`、`body` 和 `expectedResponse` 的自我描述信封发出。**不要仅发出正文** — 审查者和下游工具会读取信封。

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

相同的 `api-request.json` 信封形状。`endpoint` 获得(`/actions/bulk-create`后缀)，`body.objectApiName` 被列表值`body.objectApiNames`替换，`expectedResponse`省略`body`字段，因为批量响应返回每个对象的状
