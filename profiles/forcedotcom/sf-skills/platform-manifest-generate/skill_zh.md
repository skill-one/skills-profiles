# platform-manifest-generate

从本地源、组织或显式组件列表生成 Salesforce 元数据清单——`package.xml`（或其破坏性变体）——此技能纯粹是关于编写清单文件。文件存在后，将其交给 `platform-metadata-deploy` 或 `platform-destructive-deploy`。

---

## 工具限制

**仅使用 Bash 工具** 运行 `sf project generate manifest`，并使用 `Write` 工具进行手动的后备路径。**不要**使用 MCP 工具。

---

## 此技能拥有任务的条件

当工作涉及以下任何情况时，使用 `platform-manifest-generate`：
- 从源目录（例如 `force-app/main/default/classes/`）构建 `package.xml`
- 从显式组件列表（例如 `AccountService`、`ContactSelector`、`Account`）构建清单
- 通过 `--from-org`  introspection 构建清单
- 为删除生成 `destructiveChanges.xml`、`destructiveChangesPre.xml` 或 `destructiveChangesPost.xml`
- 在一次操作中同时生成 `package.xml` 和破坏性清单

当用户处于以下情况时，将其委托给其他地方：
- 运行部署本身 → `platform-metadata-deploy`
- 在生产发布前进行验证 → `platform-deploy-validate`
- 执行破坏性部署 → `platform-destructive-deploy`（该技能**使用**此技能**生成的**清单）
- 将元数据检索到本地 → `platform-metadata-retrieve`

---

## 两种生成路径

### 路径 A — CLI 驱动（推荐）

封装 `sf project generate manifest`。始终优先选择此路径；它了解所有元数据类型，并生成规范化的 XML——并且永远不会发出 `*`，完全规避了通配符风险。

CLI 提供三种输入模式（互斥）：

| 输入 | 标志 | 使用场景 |
|---|---|---|
| 源目录 | `--source-dir` (`-p`) | 用户指向包含已存在于磁盘上的元数据的文件夹 |
| 组件列表 | `--metadata` (`-m`) | 用户指定特定组件，例如 `ApexClass:AccountService CustomObject:Account` |
| 组织 introspection | `--from-org` | 用户希望当前组织中的所有组件（或过滤后的子集） |

您可以指定 `--source-dir` 或 `--metadata`，但不能同时指定。`--from-org` 可以与 `--metadata`（过滤包含的类型）或 `--excluded-metadata`（过滤掉类型）组合。

**验证标志**（不确定时不要编造标志——使用 `sf project generate manifest --help` 进行验证）：

| 标志 | 目的 |
|---|---|
| `--source-dir`, `-p` | 扫描本地源路径 |
| `--metadata`, `-m` | 要包含的组件名称（例如 `ApexClass:AccountService`） |
| `--from-org` | 要 introspection 的组织的用户名或别名 |
| `--name`, `-n` | 自定义输出文件名（与 `--type` 互斥） |
| `--type`, `-t` | 预定义的清单类型：`package` \| `pre` \| `post` \| `destroy` |
| `--output-dir`, `-d` | 将清单写入的目录 |
| `--api-version` | 覆盖请求的 API 版本 |
| `--include-packages`, `-c` | 在使用 `--from-org` 时包含 `managed` 和/或 `unlocked` 包元数据 |
| `--excluded-metadata` | 在使用 `--from-org` 时排除的类型 |
| `--json` | 机器可读输出 |

**根据 `--type` 的清单文件名：**

| `--type` | 输出文件 |
|---|---|
| `package` (默认) | `package.xml` |
| `pre` | `destructiveChangesPre.xml` |
| `post` | `destructiveChangesPost.xml` |
| `destroy` | `destructiveChanges.xml` |

您可以指定 `--type` 或 `--name`，但不能同时指定。

#### 规范 CLI 示例

```bash
# 从源目录构建 package.xml
sf project generate manifest \
  --source-dir force-app/main/default \
  --name package.xml \
  --output-dir manifest \
  --json

# 从显式组件列表构建 package.xml
sf project generate manifest \
  --metadata ApexClass:AccountService \
  --metadata ApexClass:ContactSelector \
  --metadata CustomObject:Account \
  --name package.xml \
  --output-dir manifest \
  --json

# 从组件列表构建 destructiveChanges.xml
sf project generate manifest \
  --metadata CustomField:Account.OldField__c \
  --metadata CustomField:Account.OldStatus__c \
  --type destroy \
  --output-dir manifest \
  --json

# 通过 introspection 组织构建清单（过滤）
sf project generate manifest \
  --from-org <alias> \
  --metadata ApexClass,CustomObject,CustomLabels \
  --output-dir manifest \
  --json
```

如果需要 `package.xml` 和破坏性清单，运行 CLI 两次——一次使用 `--type package`（或默认），一次使用 `--type destroy` / `pre` / `post`。

### 路径 B — 手动构建后备

仅在 CLI 无法表达用户意图时使用——例如，他们希望“仅今天更改的 Apex 类”，而变更集是从 `git diff` 而不是干净的目录或组件列表派生的。在这种情况下：

1. 自己解析组件（例如解析 `git diff --name-only` 并将路径映射回元数据类型）。
2. 按元数据类型分组。
3. 使用以下架构内联发出 XML。
4. 始终通过运行 `sf project deploy start --manifest <file> --dry-run`（将 `platform-metadata-deploy` 交给 `platform-destructive-deploy`）进行交叉检查。

#### 清单 XML 架构

根元素是元数据命名空间中的 `<Package>`。每种元数据类型都有一个 `<types>` 块，其中包含每个组件的一个 `<members>` 以及一个 `<name>`。尾随的 `<version>` 声明了清单的 API 版本。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>AccountService</members>
        <members>ContactSelector</members>
        <name>ApexClass</name>
    </types>
    <types>
        <members>Account</members>
        <name>CustomObject</name>
    </types>
    <types>
        <members>Account.Status__c</members>
        <name>CustomField</name>
    </types>
    <version>62.0</version>
</Package>
```

注意：
- 对于组件绑定类型（如 `CustomField`、`BusinessProcess`、`RecordType`、`Layout`、`ListView`、`ValidationRule`、`WebLink`、`CompactLayout`），成员使用 `Object.Name` 表示法。
- `destructiveChanges.xml`、`destructiveChangesPre.xml` 和 `destructiveChangesPost.xml` 使用**相同的 XML 结构**——只有文件名和意图不同。
- 空清单（没有 `<types>` 块）是合法的，有时与破坏性清单配对：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <version>62.0</version>
</Package>
```

---

## API 版本处理

每个清单底部的 `<version>` 元素必须反映项目的 API 版本。

**解析顺序：**
1. 从项目根目录的 `sfdx-project.json` 中读取 `sourceApiVersion`。
2. 如果用户传递了 `--api-version`，则使用该值。
3. 如果两者都不可用，则回退到 `sf --version` 报告的值（CLI 的捆绑 API 版本）——但**警告用户**并建议他们在 `sfdx-project.json` 中设置 `sourceApiVersion` 以确保可重复性。
4. 永远不要在输出中无声地硬编码值（例如 `62.0`）而不显示来源。

```bash
# 快速读取 sourceApiVersion
jq -r '.sourceApiVersion' sfdx-project.json
```

使用 CLI 路径时，除非用户明确覆盖，否则省略 `--api-version`——CLI 已经读取 `sourceApiVersion`。

---

## 通配符成员 (`<members>*</members>`)

通配符成员匹配该元数据类型的所有组件。**并非所有类型都合法。** 使用 `*` 对于不允许的类型会导致部署/检索错误，例如 `Wildcards are not supported for this metadata type`。

### 通配符 NOT 允许（必须枚举）

这些类型需要显式成员名称。常见示例：`Profile`、`PermissionSet`、`PermissionSetGroup`、`CustomLabels`、`CustomObjectTranslation`、`Layout`、`Workflow`（在某些包配置中）、`SharingRules`、`StandardValueSet`、`ManagedTopics`，以及大多数“容器”类型，其内容是对象绑定的（`CustomField`、`RecordType`、`BusinessProcess`、`ListView`、`ValidationRule`、`WebLink`、`CompactLayout`）。

对于这些，显式枚举：

```xml
<types>
    <members>Admin</members>
    <members>Standard User</members>
    <name>Profile</name>
</types>
```

### 通配符通常允许

大多数“自包含”组件类型接受 `*`。示例：`ApexClass`、`ApexTrigger`、`ApexComponent`、`ApexPage`、`AuraDefinitionBundle`、`LightningComponentBundle`、`CustomApplication`、`CustomTab`、`StaticResource`、`EmailTemplate`、`Report`、`Dashboard`、`Flow`、`FlexiPage`、`CustomMetadata`。有关完整枚举和边缘情况的详细信息，请参阅 [references/wildcard-allowlist.md](references/wildcard-allowlist.md)。

经验法则：如果您不确定，**显式列出组件**。CLI 路径（`--source-dir` / `--metadata`）避免了这个问题，因为它永远不会发出 `*`。

---

## 示例

### 示例 1 — 从目录构建 `package.xml`

> "从 `force-app/main/default/classes/` 生成 package.xml"

```bash
sf project generate manifest \
  --source-dir force-app/main/default/classes \
  --name package.xml \
  --output-dir manifest \
  --json
```

结果：`manifest/package.xml` 列出该文件夹中的每个 Apex 类。

### 示例 2 — 构建涵盖特定组件的清单

> "构建涵盖 AccountService、ContactSelector 和 Account 自定义对象的清单"

```bash
sf project generate manifest \
  --metadata ApexClass:AccountService \
  --metadata ApexClass:ContactSelector \
  --metadata CustomObject:Account \
  --name package.xml \
  --output-dir manifest \
  --json
```

结果：`manifest/package.xml` 包含这三个组件。

### 示例 3 — 为删除生成 `package.xml` 和 `destructiveChanges.xml`

> "为这些删除创建 package.xml 和 destructiveChanges.xml：`Account.OldField__c`、`Account.OldStatus__c`"

```bash
# 空的/最小的 package.xml（删除性部署仍然需要一个包描述符）
sf project generate manifest \
  --metadata CustomLabels \
  --name package.xml \
  --output-dir manifest \
  --json

# destructiveChanges.xml
sf project generate manifest \
  --metadata CustomField:Account.OldField__c \
  --metadata CustomField:Account.OldStatus__c \
  --type destroy \
  --output-dir manifest \
  --json
```

生成后，将 `platform-destructive-deploy` 交给 `platform-destructive-deploy` 以验证和执行删除。

---

## 失败模式

| 症状 | 可能原因 | 恢复 |
|---|---|---|
| `Path does not exist: <dir>` | `--source-dir` 指向一个缺失的文件夹 | 确认路径；使用 `ls` 验证；如果用户含糊不清，则默认为 `force-app/main/default` |
| 生成的清单为空 | 源目录不包含任何可识别的元数据，或所有文件都被忽略 | 检查 `.forceignore`；验证路径实际上包含元数据文件（`*.cls`、`*-meta.xml` 等） |
| `Wildcards are not supported for this metadata type` 在部署时出现 | 手动构建的清单对不允许的类型使用了 `*` | 参考上面的通配符允许列表；显式枚举组件 |
| `<version>` 缺失或不匹配 | `sfdx-project.json` 缺少 `sourceApiVersion` | 将 `sourceApiVersion` 添加到 `sfdx-project.json`，或将 `--api-version` 传递给 CLI |
| `You can specify either --type or --name, but not both` | CLI 调用传递了两个标志 | 放弃一个；使用 `--type` 表示预定义名称，`--name` 表示自定义名称 |
| `You can specify either --source-dir or --metadata, but not both` | CLI 调用传递了两个 | 选择一种输入模式 |
| `Components missing from --from-org` 输出 | 组织 introspection 批量过于激进，或类型在受管理的包中 | 设置 `SF_LIST_METADATA_BATCH_SIZE` 更低；如果打算包含，则添加 `--include-packages managed` |

---

## 跨技能集成

| 需要 | 委托给 | 原因 |
|---|---|---|
| 运行生成的清单的部署 | `platform-metadata-deploy` | 此技能在文件生成后停止 |
| 在生产发布前进行验证 | `platform-deploy-validate` | 针对生产的前飞测试 |
| 实际删除清单中的组件 | `platform-destructive-deploy` | 该技能验证并执行破坏性部署 |
| 检索清单中列出的元数据 | `platform-metadata-retrieve` | 将组织元数据拉取到本地 |
| 编写清单中列出的元数据 | 其他 `platform-*` 生成器（例如 `platform-custom-object-generate`） | 清单仅列出磁盘上已存在的元数据 |

---

## 完成格式

```text
清单目标：<package | pre | post | destroy>
输入模式：<source-dir | 元数据列表 | from-org | 手动构建>
输出：<路径/to/manifest.xml>
API 版本：<值>（来源：sfdx-project.json | --api-version | CLI 默认）
组件数量：<N> 跨越 <M> 种元数据类型
下一步：<platform-metadata-deploy | platform-deploy-validate | platform-destructive-deploy>
```
