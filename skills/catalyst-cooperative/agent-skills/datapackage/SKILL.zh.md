---
name: datapackage
description: 探索并查询任何使用 Frictionless Data Package 描述符（datapackage.json）标注的数据集。当用户想要发现数据集包含哪些表格或资源、查询列名和描述、揭示元数据中嵌入的使用警告，或了解如何从 Parquet 文件、DuckDB 或 SQLite 数据库，或由 datapackage.json 描述的 CSV 文件加载数据时，请使用此技能。此外，当用户拥有 datapackage.json 并想知道其中包含的内容、如何高效地查询它，或如何将其元数据与实际数据文件连接时，也请使用此技能。它与特定数据集技能（如 `pudl`）配合良好，后者在顶层叠加领域知识。
---

# 无摩擦数据包指南

本技能涵盖任何由
[无摩擦数据包](https://datapackage.org/) 描述文件 (`datapackage.json`) 描述的数据集。它有意设计得通用——适用于任何符合规范的数据包，无论发布者是谁或数据包含什么内容。

对于 PUDL 特定知识（S3 存储桶路径、表层级规范、数据源上下文、使用警告），也应在该技能之上使用 `pudl` 技能。

## 什么是 datapackage.json？

`datapackage.json` 是一个描述表格数据资源集合的 JSON 文件。每个资源代表一个表（或文件），并包含：

- `name`：机器可读的标识符
- `description`：人类可读的描述，通常包括处理说明、主键和使用警告
- `path`：实际数据文件的文件名或 URL
- `schema.fields`：列的列表，每个列都有 `name` 和 `description`
- `schema.primaryKey`：唯一标识此资源中行的字段或字段
- `schema.foreignKeys`：从此资源的字段到另一个资源的主键声明的链接——在连接或聚合前检查这些（见
    [元数据查询](./references/metadata-querying.md)）

该文件可能很大（数百个资源，数兆字节的 JSON）。始终选择性地查询它——切勿将其全部加载到上下文中。

## 依赖检查

在查询元数据之前，验证 `jq` 是否可用：

```bash
command -v jq
```

如果没有找到，请告诉用户如何安装它：

- macOS: `brew install jq`
- Linux (apt): `sudo apt install jq`
- Linux (conda): `conda install jq`
- Windows: `winget install jqlang.jq`

对于数据加载和 SQL 查询，必须安装 `attach-db` 和 `query` 技能（可选 `install-duckdb` 太）。从 `duckdb/duckdb-skills` 安装它们。

## 工作流程概述

1. **定位描述符** — 查找或下载 `datapackage.json`（见下文）。
1. **选择性地查询元数据** — 使用 jq 提取您需要的部分。
    见 [元数据查询](./references/metadata-querying.md)。
1. **显示警告** — 在展示资源之前，始终检查使用警告。
1. **在连接或聚合前检查键** — 如果任务组合了两个资源，或汇总一个，首先查找每个资源上的 `schema.primaryKey` 和 `schema.foreignKeys`，而不是在同名或看起来相似的列上连接。见
    [元数据查询：连接资源](./references/metadata-querying.md#joining-resources-primary-keys-and-foreign-keys)。
1. **验证** *(可选)* — 如果用户想知道数据是否实际匹配描述符，或者如果您正在诊断可疑的数据包，请使用
    `frictionless validate`。见 [无摩擦验证](./references/frictionless-validate.md)。
1. **加载数据** *(可选)* — 只有当用户明确希望查询或探索实际数据时。数据文件可能很大，远程访问可能缓慢或昂贵。不要在没有确认用户想要的情况下作为元数据查询的后续操作来启动数据加载。见 [存储后端](./references/storage-backends.md)。

## 参考索引

- [元数据查询](./references/metadata-querying.md) — 定位描述符、使用 jq 选择性地查询它、显示使用警告
- [存储后端](./references/storage-backends.md) — 从描述符引用的 Parquet、DuckDB、SQLite 或 CSV 文件加载数据
- [无摩擦验证](./references/frictionless-validate.md) — 使用 `frictionless` CLI 验证数据包、检查数据质量、推断模式、诊断不熟悉的描述符；当用户想要验证描述符、检查数据是否匹配其模式或了解 `frictionless` 工具可以告诉他们关于数据包的信息时阅读

## 社区模式和配方

数据包标准是宽松的：发布者经常添加非标准字段。有两个约定值得立即了解：

- **自定义字段** — 发布者添加的非标准键很常见且有效。`_` 前缀约定标记系统生成或平台特定的键（例如 `_cache`、`_platformVersion`）。一些发布者添加没有前缀的自定义键（例如包级别的单位注册表，或每个资源的可追溯性元数据）。将未知字段视为信息性元数据，而不是错误。
- **压缩资源** — 路径带有 `.gz` 或 `.zip` 的资源可能有明确的 `"compression": "gz"` 字段。`bytes` 和 `hash` 字段适用于压缩文件，而不是未压缩的原始文件。

对于其他模式（目录、版本控制、外部外键、翻译支持、字段关系等），按需获取相关页面：

- v1 模式：<https://specs.frictionlessdata.io/patterns/>
- v2 配方：<https://datapackage.org/recipes/caching-of-resources/> (通过侧边栏或下一页/上一页链接导航——没有索引页面存在)

这两个页面涵盖了很大程度上相同的社区约定；参考与您正在处理的数据包版本匹配的那个。

## 伴随技能

此技能将实际数据查询委托给：

- **`/attach-db`** — 附加 `.duckdb` 或 `.sqlite` 数据库文件并
    设置持久会话以进行查询
- **`/query`** — 运行 SQL 或自然语言查询针对附加的
    数据库、临时文件（Parquet、CSV、远程 HTTPS/S3）和 JSON 文件包括
    `datapackage.json` 本身（通过 DuckDB 的 `read_json`）

这些技能必须安装。见项目根目录中的 `skills-lock.json`。

## 关键约束

- **金规则：切勿将完整的 datapackage.json 加载到上下文中。** 它可能有数兆字节，包含数百个资源。始终选择性地查询。
- **在展示资源之前阅读完整的描述。** 描述通常包含重要上下文：处理说明、主键约定、数据来源，或关于已知限制的注意事项。不要跳过它们。
- **使用 `uv` 安装 Python 包** — 优先 `uv add <package>` 而不是
    `pip install <package>`。`uv` 更快，并安装到虚拟环境中而不是全局。只有在 `uv` 不可用时才回退到 `pip`
    (`command -v uv` 返回空)。
- **不要使用 Python 查询描述符元数据。** Python 不是这个正确的工具——它将完整的 JSON 加载到内存中（违反上述金规则），添加不必要的依赖，并且无法轻松处理远程描述符。使用 jq 进行仅元数据的任务；使用 DuckDB 当您需要将元数据查询与数据查询组合时。Python 仅在您已经知道需要哪个表和列之后加载数据（通过 pandas 或 polars）时才适用。

## 模式参考和版本检测

两种版本的 Frictionless Data Package 标准在常用。从顶层描述符中识别版本，然后再解析：

| 字段存在 | 版本                          | 示例值                                             |
| ------------- | -------------------------------- | --------------------------------------------------------- |
| `"$schema"`   | v2.0                             | `"https://datapackage.org/profiles/2.0/datapackage.json"` |
| `"profile"`   | v1.0                             | `"tabular-data-package"` 或 `"data-package"`              |
| 既无        | 模糊（视为 v1 基线） | —                                                         |

版本之间影响解析的关键差异：

- **贡献者** — v1 有 `"role": "author"`（单个字符串）；v2 有
    `"roles": ["author"]`（数组）。两者都可能出现在野外。
- **名称模式** — v1 严格强制小写 `[-a-z0-9._/]`；v2 无限制。
- **`version` 字段** — v2 中存在，v1 中不存在。

捆绑的方案：

- [`assets/datapackage-v1.schema.json`](./assets/datapackage-v1.schema.json) — v1.0
    (JSON Schema draft-04)。由 FERC XBRL 数据包和许多旧数据集使用。
- [`assets/datapackage-v2.schema.json`](./assets/datapackage-v2.schema.json) — v2.0
    (JSON Schema draft-07)。当前标准。规范版本始终在：
    <https://datapackage.org/profiles/2.0/datapackage.json>

当您需要了解描述符中哪些字段是有效的或程序化验证一个时，请阅读适当的方案。
