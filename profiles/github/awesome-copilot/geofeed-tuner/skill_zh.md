# Geofeed Tuner – 创建更好的 IP 地理位置 Feeds

这个技能帮助你创建和改进 CSV 格式的 IP 地理位置 Feeds，具体功能包括：

- 确保你的 CSV 符合规范且一致
- 检查是否符合 [RFC 8805](references/rfc8805.txt)（行业标准）
- 应用从实际部署中学习到的 **主观最佳实践**
- 提出提高准确性、完整性和隐私性的改进建议

## 使用此技能的场景

- 当用户需要帮助 **创建、改进或发布** CSV 格式的 IP 地理位置 Feeds 文件时，请使用此技能。
- 使用它来 **调整和排错** CSV 地理位置 Feeds — 捕获错误、提出改进建议，并确保 RFC 合规性之外的实际可用性。
- **目标受众**：
  - 负责公网可路由 IP 地址空间的网络运营商、管理员和工程师
  - 互联网服务提供商 (ISP)、移动运营商、云服务提供商、主机和托管公司、互联网交换运营商和卫星互联网提供商等组织
- **不要使用** 此技能进行私有或内部 IP 地址管理；它仅适用于 **公网可路由 IP 地址**。

## 前置条件

- **Python 3** 是必需的。

## 目录结构和文件管理

此技能在 **分发文件**（只读）和 **工作文件**（在运行时生成）之间使用明确的分离。

### 只读目录（不要修改）

以下目录包含静态分发资源。**不要在这些目录中创建、修改或删除文件**：

| 目录      | 用途                                                    |
|-----------|--------------------------------------------------------|
| `assets/`  | 静态数据文件（ISO 代码、示例）                        |
| `references/`  | RFC 规范和代码片段供参考                               |
| `scripts/`  | 可执行代码和报告模板文件                                |

### 工作目录（生成内容）

所有生成、临时和输出文件都放在这些目录中：

| 目录       | 用途                                              |
|-----------|---------------------------------------------------|
| `run/`    | 所有代理生成内容的工 作目录                      |
| `run/data/`  | 从远程 URL 下载的 CSV 文件                      |
| `run/report/`  | 生成的 HTML 调整报告                                |

### 文件管理规则

1. **永远不要写入 `assets/`、`references/` 或 `scripts/`** — 这些是技能分发的一部分，必须保持不变。
2. **所有下载的输入文件**（从远程 URL）必须保存到 `./run/data/`。
3. **所有生成的 HTML 报告**必须保存到 `./run/report/`。
4. **所有生成的 Python 脚本**必须保存到 `./run/`。
5. `run/` 目录可以在会话之间清除；不要在那里存储永久数据。
6. **执行的工作目录**：所有在 `./run/` 生成的脚本都必须以 **技能根目录**（包含 `SKILL.md` 的目录）作为当前工作目录执行，以便像 `assets/iso3166-1.json` 和 `./run/data/report-data.json` 这样的相对路径解析正确。在运行脚本之前，**不要** 进入 `./run/`。

## 处理流程：顺序阶段执行

所有阶段必须 **按顺序** 执行，从阶段 1 到阶段 2。每个阶段都依赖于前一个阶段的成功完成。例如，**结构检查** 必须完成才能运行 **质量分析**。

以下是各阶段的总结。代理必须遵循每个阶段部分中详细概述的步骤。

| 阶段 | 名称                       | 描述                                                                       |
|------|----------------------------|-----------------------------------------------------------------------------|
| 1    | 理解标准                 | 审查 RFC 8805 对自发布 IP 地理位置 Feeds 的关键要求                                 |
| 2    | 收集输入                 | 从本地文件或远程 URL 收集 IP 子网数据                                           |
| 3    | 检查和建议               | 验证 CSV 结构、分析 IP 前缀并检查数据质量                                     |
| 4    | 调整数据查找             | 使用 Fastah 的 MCP 工具检索改进地理位置准确性的调整数据                           |
| 5    | 生成调整报告             | 创建总结分析和建议的 HTML 报告                                               |
| 6    | 最终审查                 | 验证报告数据的完整性和一致性                                                   |

**不要跳过阶段。** 每个阶段都提供后续阶段所需的临界检查或数据转换。

### 执行计划规则

在执行每个阶段之前，代理必须生成一个可见的 TODO 清单。

计划必须：

- 出现在阶段的 **开始处**
- 列出每个步骤按顺序
- 使用复选框格式
- 随步骤完成而实时更新


### 阶段 1：理解标准

RFC 8805 中此技能强制执行的关键要求总结如下。**将其用作你的工作参考。** 仅在边缘情况、模糊情况或用户询问此处未涵盖的标准问题时，才查阅完整的 [RFC 8805 文本](references/rfc8805.txt)。

#### RFC 8805 关键事实

**目的**：自发布的 IP 地理位置 Feeds 允许网络运营商以简单的 CSV 格式发布其 IP 地址空间的权威位置数据，使地理位置提供者能够结合运营商提供的更正。

**CSV 列顺序（第 2.1.1.1–2.1.1.5 节）**：

| 列 | 字段         | 必填 | 备注                                                      |
|----|--------------|------|------------------------------------------------------------|
| 1  | `ip_prefix`   | 是   | CIDR 表示法；IPv4 或 IPv6；必须是网络地址                 |
| 2  | `alpha2code`  | 否   | ISO 3166-1 alpha-2 国家代码；空或 "ZZ" = 不要地理位置 |
| 3  | `region`      | 否   | ISO 3166-2 行政区代码（例如，`US-CA`）             |
| 4  | `city`        | 否   | 自定义城市名称；没有权威的验证集                         |
| 5  | `postal_code` | 否   | **已弃用** — 必须为空或不存在                     |

**结构规则**：

- 文件可以包含以 `#` 开头的注释行（包括标题行，如果存在）。
- 标题行是可选的；如果存在，如果以 `#` 开头，则将其视为注释。
- 文件必须以 UTF-8 编码。
- 子网主机位不得设置（即 `192.168.1.1/24` 无效；使用 `192.168.1.0/24`）。
- 仅适用于 **全局可路由** 的单播地址 — 不包括私有、回环、链路本地或多播空间。

**不要地理位置**：具有空 `alpha2code` 或大小写不敏感的 `ZZ` 的条目是一个明确的信号，表明运营商不希望对某个前缀进行地理位置。

**已弃用的邮政编码（第 2.1.1.5 节）**：第五列不得包含邮政编码或 ZIP 码。它们对于 IP 范围映射来说过于精细，并引发隐私问题。


### 阶段 2：收集输入

- 如果用户尚未提供 IP 子网或范围的列表（有时也称为 `inetnum` 或 `inet6num`），请提示他们提供。接受的输入格式：

  - 粘贴到聊天中的文本
  - 本地 CSV 文件
  - 指向 CSV 文件的远程 URL

- 如果输入是 **远程 URL**：

  - 尝试在处理之前将 CSV 文件下载到 `./run/data/`。
  - 如果遇到 HTTP 错误（4xx、5xx、超时或重定向循环），**立即停止** 并向用户报告：

    `Feed URL 无法访问：HTTP {status_code}。请验证 URL 是否可以公开访问。`
  - 不要在下载不完整或为空的下载情况下继续到阶段 3。

- 如果输入是 **本地文件**，则直接处理，无需下载。

- **编码检测和规范化**：

  1. 首先尝试以 UTF-8 读取文件。
  2. 如果引发 `UnicodeDecodeError`，则尝试 `utf-8-sig`（带 BOM 的 UTF-8），然后尝试 `latin-1`。
  3. 成功解码后，重新编码并作为工作副本写入 UTF-3.8。
  4. 如果没有编码成功，则停止并报告：`无法解码输入文件。请将其保存为 UTF-8 并重试。`


### 阶段 3：检查和建议

#### 执行规则

- 为此阶段生成 **脚本**。
- **不要** 将此阶段与其他阶段组合。
- **不要** 预计算后续阶段的数据。
- 将输出存储为 JSON 文件，路径为：`./run/data/report-data.json`

#### Schema 定义

下面的 JSON 结构在阶段 3 **不可变**。阶段 4 将在稍后阶段向 `Entries` 中的每个对象添加 `TunedEntry` 对象 — 这是唯一允许的 schema 扩展，并且发生在单独的阶段。

JSON 键直接映射到模板占位符，如 `{{.CountryCode}}`、`{{.HasError}}` 等。

```json
{
  "InputFile": "",
  "Timestamp": 0,

  "TotalEntries": 0,
  "IpV4Entries": 0,
  "IpV6Entries": 0,
  "InvalidEntries": 0,

  "Errors": 0,
  "Warnings": 0,
  "OK": 0,
  "Suggestions": 0,

  "CityLevelAccuracy": 0,
  "RegionLevelAccuracy": 0,
  "CountryLevelAccuracy": 0,
  "DoNotGeolocate": 0,

  "Entries": [
    {
      "Line": 0,
      "IPPrefix": "",
      "CountryCode": "",
      "RegionCode": "",
      "City": "",

      "Status": "",
      "IPVersion": "",

      "Messages": [
        {
          "ID": "",
          "Type": "",
          "Text": "",
          "Checked": false
        }
      ],

      "HasError": false,
      "HasWarning": false,
      "HasSuggestion": false,
      "DoNotGeolocate": false,
      "GeocodingHint": "",
      "Tunable": false
    }
  ]
}
```

字段定义：

**顶层元数据**：

- `InputFile`: 原始输入源，无论是本地文件名还是远程 URL。
- `Timestamp`: 调整时 Unix 纪元以来的毫秒数。
- `TotalEntries`: 处理的数据行总数（不包括注释和空白行）。
- `IpV4Entries`: IPv4 子网条目的计数。
- `IpV6Entries`: IPv6 子网条目的计数。
- `InvalidEntries`: IP 前缀解析和 CSV 解析失败的条目计数。
- `Errors`: `Status` 为 `ERROR` 的条目总数。
- `Warnings`: `Status` 为 `WARNING` 的条目总数。
- `OK`: `Status` 为 `OK` 的条目总数。
- `Suggestions`: `Status` 为 `SUGGESTION` 的条目总数。
- `CityLevelAccuracy`: `City` 非空的合法条目的计数。
- `RegionLevelAccuracy`: `RegionCode` 非空且 `City` 为空的合法条目的计数。
- `CountryLevelAccuracy`: `CountryCode` 非空、`RegionCode` 为空且 `City` 为空的合法条目的计数。
- `DoNotGeolocate` (元数据): `CountryCode`、`RegionCode` 和 `City` 全部为空的合法条目的计数。

**条目字段**：

- `Entries`: 每个数据行一个对象组成的数组，包含以下每个条目字段：

  - `Line`: 原始 CSV 中 1 进制的行号（包括所有行，包括注释和空白行）。
  - `IPPrefix`: CIDR 斜杠表示法的规范化 IP 前缀。
  - `CountryCode`: ISO 3166-1 alpha-2 国家代码，或空字符串。
  - `RegionCode`: ISO 3166-2 行政区代码（例如，`US-CA`），或空字符串。
  - `City`: 城市名称，或空字符串。
  - `Status`: 分配的最高严重性：`ERROR` > `WARNING` > `SUGGESTION` > `OK`。
  - `IPVersion`: 基于解析的 IP 前缀为 `"IPv4"` 或 `"IPv6"`。
  - `Messages`: 消息对象数组，每个消息对象包含：

    - `ID`: 来自 **验证规则参考** 表（如下表所示）的字符串标识符（例如，`"1101"`、`"3301"`）。
    - `Type`: 严重性类型：`"ERROR"`、`"WARNING"` 或 `"SUGGESTION"`。
    - `Text`: 人类可读的验证消息字符串。
    - `Checked`: 如果验证规则是自动可调整的（参考表中 `Tunable: true`），则为 `true`，否则为 `false`。这控制报告中的复选框是 `checked` 还是 `disabled`。
  - `HasError`: 如果任何消息的 `Type` 为 `"ERROR"`，则为 `true`。
  - `HasWarning`: 如果任何消息的 `Type` 为 `"WARNING"`，则为 `true`。
  - `HasSuggestion`: 如果任何消息的 `Type` 为 `"SUGGESTION"`，则为 `true`。
  - `DoNotGeolocate` (条目): 如果 `CountryCode` 为空或 `"ZZ"`，则为 `true` — 该条目是明确的不要地理位置信号。
  - `GeocodingHint`: 始终为空字符串 `""`。
  - `Tunable`: 如果 **条目中的任何** 消息的 `Checked` 为 `true`，则为 `true`。计算方式为所有消息的 `Checked` 值的逻辑 OR。此标志驱动报告中“调整”按钮的可见性。

#### 验证规则参考

当向条目添加消息时，使用此表中的 `ID`、`Type`、`Text` 和 `Checked` 值。

| ID     | Type         | 文本                                                                                           | Checked | 条件参考                    |
|--------|--------------|------------------------------------------------------------------------------------------------|---------|--------------------------------|
| `1101` | `ERROR`      | IP 前缀为空                                                                             | `false` | IP 前缀分析：空              |
| `1102` | `ERROR`      | 无效 IP 前缀：无法解析为 IPv4 或 IPv6 网络                                     | `false` | IP 前缀分析：无效语法     |
| `1103` | `ERROR`      | 非公网 IP 范围不允许在 RFC 8805 feed 中                                                | `false` | IP 前缀分析：非公网         |
| `3101` | `SUGGESTION` | IPv4 前缀异常大，可能表示输入错误                                                         | `false` | IP 前缀分析：IPv4 < /22         |
| `3102` | `SUGGESTION` | IPv6 前缀异常大，可能表示输入错误                                                         | `false` | IP 前缀分析：IPv6 < /64         |
| `1201` | `ERROR`      | 无效国家代码：不是有效的 ISO 3166-1 alpha-2 值                                             | `true`  | 国家代码分析：无效         |
| `1301` | `ERROR`      | 无效区域格式；预期 COUNTRY-SUBDIVISION（例如，US-CA）                              | `true`  | 区域代码分析：格式错误       |
| `1302` | `ERROR`      | 无效区域代码：不是有效的 ISO 3166-2 行政区代码                                         | `true`  | 区域代码分析：未知代码     |
| `1303` | `ERROR`      | 区域代码与指定的国家代码不匹配                                                   | `true`  | 区域代码分析：不匹配         |
| `1401` | `ERROR`      | 无效城市名称：不允许占位符值                                                        | `false` | 城市名称分析：占位符        |
| `1402` | `ERROR`      | 无效城市名称：检测到缩写或代码值                                                      | `true`  | 城市名称分析：缩写         |
| `2401` | `WARNING`    | 城市名称格式不一致；建议规范化该值                                                   | `true`  | 城市名称分析：格式         |
| `1501` | `ERROR`      | 邮政编码已由 RFC 8805 弃用，出于隐私原因必须删除                  | `true`  | 邮政编码检查                  |
| `3301` | `SUGGESTION` | 对于小地区，区域通常是多余的；建议删除区域值                                       | `true`  | 调整：小地区区域         |
| `3402` | `SUGGESTION` | 对于小地区，城市级别的粒度通常是多余的；建议删除城市值                                       | `true`  | 调整：小地区城市         |
| `3303` | `SUGGESTION` | 当指定城市时，建议区域代码；从下拉列表中选择区域                                       | `true`  | 调整：指定城市时缺少区域       |
| `3104` | `SUGGESTION` | 确认此子网是否有意标记为不要地理位置或缺少位置数据                                       | `true`  | 调整：未指定地理位置        |

#### 填充消息

当验证检查匹配时，使用参考表中的值向条目的 `Messages` 数组添加消息：

```python
entry["Messages"].append({
    "ID": "1201",      # 来自参考表
    "Type": "ERROR",   # 来自参考表
    "Text": "Invalid country code: not a valid ISO 3166-1 alpha-2 value",  # 来自参考表
    "Checked": True    # 来自参考表（True = 可调整）
})
```

填充完一个条目的所有消息后，导出条目级标志：

```python
entry["HasError"] = any(m["Type"] == "ERROR" for m in entry["Messages"])
entry["HasWarning"] = any(m["Type"] == "WARNING" for m in entry["Messages"])
entry["HasSuggestion"] = any(m["Type"] == "SUGGESTION" for m in entry["Messages"])
entry["Tunable"] = any(m["Checked"] for m in entry["Messages"])
```

#### 准确性级别计数规则

准确性级别是 **互斥的**。根据最细粒度的非空地理字段将每个有效（非 ERROR、非无效）条目分配到 exactly 一个桶：

| 条件                                                    | 桶                      |
|--------------------------------------------------------|-----------------------------|
| `City` 非空                                              | `CityLevelAccuracy`         |
| `RegionCode` 非空 AND `City` 为空                   | `RegionLevelAccuracy`       |
| `CountryCode` 非空, `RegionCode` 和 `City` 空缺       | `CountryLevelAccuracy`      |
| `DoNotGeolocate` (条目) 为 `true`                           | `DoNotGeolocate` (元数据) |

**不要** 计数具有 `HasError: true` 的条目或在任何准确性桶中的无效条目。

代理 **不得**：

- 重命名字段
- 添加或删除字段
- 更改数据类型
- 重新排序键
- 改变嵌套
- 包装对象
- 分割到多个文件

如果值未知，**必须为空** — 永远不要编造数据。

#### 结构和格式检查

此阶段验证你的 feed 是否符合规范且可解析。**在调谐器可以分析地理位置质量之前，必须解决关键结构错误**。

##### CSV 结构

本节定义了用于 IP 地理位置 Feeds 的 **CSV 格式输入文件** 的规则。
目标是确保文件可以可靠地解析并规范化为 **一致的内表示**。

- **CSV 结构检查**
  - 如果 `pandas` 可用，则使用它进行 CSV 解析。
  - 否则，回退到 Python 的内置 `csv` 模块。

  - 确保 CSV 包含 **正好 4 或 5 个逻辑列**。
  - 允许注释行。
  - 标题行 **可以** 或 **不可以** 存在。
  - 如果没有标题行，则假设隐式列顺序：

    ```
    ip_prefix, alpha2code, region, city, postal code (已弃用)
    ```
  - 参考示例输入文件：
    [`assets/example/01-user-input-rfc8805-feed.csv`](assets/example/01-user-input-rfc8805-feed.csv)

- **CSV 清理和规范化**
  - 使用与以下操作等效的 Python 逻辑清理和规范化 CSV：

    - 选择 **仅** 前 5 列，删除第 5 列之后的任何列。
    - 使用 UTF-8 BOM 写入输出文件。

  - **注释**
    - 删除以 **第一个** 列以 `#` 开头的注释行。
    - 这也会删除以 `#` 开头的标题行（如果存在）。
    - 创建一个使用 **1 进制行号** 作为键、完整原始行作为值的注释映射。还存储空白行。
    - 将此映射存储在 JSON 文件中：`./run/data/comments.json`
    - 示例：`{ "4": "# 小城市州可以留空州 ISO2 代码" }`

- **注意**
  - 两个实现路径（`pandas` 和内置 `csv`）必须使用 `utf-8-sig` 编码写入输出，以确保存在 **UTF-8 BOM**。

#### IP 前缀分析

- 检查每个条目是否存在 `IPPrefix` 字段，且非空。
- 检查条目之间是否存在重复的 `IPPrefix` 值。
- 如果发现重复，则停止技能并报告给用户消息：`检测到重复 IP 前缀：{ip_prefix_value} 出现在行 {line_numbers}`
- 如果没有重复，则继续分析。

  - **检查**
    - 每个子网必须能够干净地解析为 **IPv4 或 IPv6 网络**，使用 `references/` 文件夹中的代码片段。
    - 子网必须规范化并显示为 **CIDR 斜杠表示法**。
      - 单主机 IPv4 子网必须表示为 **`/32`**。
      - 单主机 IPv6 子网必须表示为 **`/128`**。

  - **错误**
    - 将以下条件报告为 **错误**：

    - **无效子网语法**
      - 消息 ID：`1102`

    - **非公网地址空间**
      - 适用于 **私有、回环、链路本地、多播或其他非公网** 子网。
      - 在 Python 中，使用 `is_private` 和相关地址属性（如 `./references` 中所示）检测非公网范围。
      - 消息 ID：`1103`

  - **建议**
    - 将以下条件报告为 **建议**：

    - **过大的 IPv6 子网**
      - 前缀短于 `/64`
      - 消息 ID：`3102`

    - **过大的 IPv4 子网**
      - 前缀短于 `/22`
      - 消息 ID：`3101`


### 阶段 4：调整数据查找

#### 目标

使用 Fastah 的 `rfc8805-row-place-search` 工具查找所有 `Entries`。

#### 执行规则

- 生成一个新的 **脚本**，仅用于生成有效负载（读取数据集并写入一个或多个有效负载 JSON 文件；不要从该脚本调用 MCP）。
- 服务器只接受每批最多 1000 个条目，因此如果条目超过 1000 个，则分成多个请求。
- 代理必须读取生成的有效负载文件，从它们构造请求，并将这些请求以最多 1000 个条目每批发送到 MCP 服务器。
- **MCP 失败**：如果 MCP 服务器无法访问、返回错误或对任何批次返回无结果，则记录警告并继续到阶段 5。为受影响的条目设置 `TunedEntry: {}`。不要阻止报告生成。向用户明确通知：`调整数据查找不可用；报告将仅显示验证结果。`
- 建议是 **仅供参考** — **永远不要自动填充** 它们。

#### 步骤 1：使用去重构建查找有效负载

从 `./run/data/report-data.json` 加载数据集
- 读取 `Entries` 数组。每个条目将用于构建 MCP 查找有效负载。

通过去重减少服务器请求：
- 对于 `Entries` 中的每个条目，计算内容哈希（`CountryCode` + `RegionCode` + `City`）。
- 创建去重映射：`{ contentHash -> { rowKey, payload, entryIndices: [] }`。rowKey 是将发送到 MCP 服务器以匹配响应的 UUID。
- 如果条目的哈希已存在，则将其 **0** 进制数组索引添加到该去重条目的 `entryIndices` 数组中。
- 如果哈希是新的，则生成一个 **UUID (rowKey)** 并创建一个新的去重条目。

构建请求批次：
- 从映射中提取唯一的去重条目，保持去重顺序。
- 构建最多包含 1000 项的请求批次。
- 对于每个批次，保留一个内存结构，如 `[{ rowKey, payload, entryIndices }, ...]` 以便通过 `rowKey` 匹配响应。
- 在写入 MCP 有效负载文件时，为每个有效负载对象包含 `rowKey` 字段：

```json
[
    {"rowKey": "550e8400-e29b-41d4-a716-446655440000", "countryCode":"CA","regionCode":"CA-ON","cityName":"Toronto"},
    {"rowKey": "6ba7b810-9dad-11d1-80b4-00c04fd430c8", "countryCode":"IN","regionCode":"IN-KA","cityName":"Bangalore"},
    {"rowKey": "6ba7b811-9dad-11d1-80b4-00c04fd430c8", "countryCode":"IN","regionCode":"IN-KA"}
]
```

- 在读取响应时，使用响应的 `rowKey` 字段与去重映射中的相应 `entryIndices` 条目进行匹配以检索所有相关 `entryIndices`。

规则：
- 写入有效负载到：`./run/data/mcp-server-payload.json`
- 执行脚本后退出。

#### 步骤 2：调用 Fastah MCP 工具

- Fastah MCP 服务器的一个示例 `mcp.json` 风格配置如下：

```json
    "fastah-ip-geofeed": {
      "type": "http",
      "url": "https://mcp.fastah.ai/mcp"
    }
```

- 服务器：`https://mcp.fastah.ai/mcp`
- 工具及其模式：在第一个 `tools/call` 之前，代理必须发送 `tools/list` 请求以读取 **`rfc8805-row-place-search`** 的输入和输出模式。
  使用发现的模式作为字段名、类型和约束的权威来源。
- 以下是一个说明性示例，仅用于参考；始终以 `tools/list` 返回的模式为准：

  ```json
  [
      {"rowKey": "550e8400-...", "countryCode":"CA", ...},
      {"rowKey": "690e9301-...", "countryCode":"ZZ", ...}
  ]
```

- 打开 `./run/data/mcp-server-payload.json` 并将所有去重条目（带有它们的 rowKeys）发送到 MCP 服务器。
- 如果去重后的条目超过 1000 个，则分成多个包含 1000 个条目的请求。
- 服务器将使用相同的 `rowKey` 字段在每个响应中返回以映射回响应。
- **不要** 使用本地数据。

#### 步骤 3：将调整数据附加到条目

- 生成一个新的 **脚本**，用于附加调整数据。
- 加载 `./run/data/report-data.json` 和去重映射（从步骤 1 持有在内存中，或重新导出从有效负载文件中导出）。
- 对于 MCP 服务器返回的每个响应：
  - 从响应中提取 `rowKey`。
  - 从去重映射中查找与该 `rowKey` 相关的 `entryIndices` 数组。
  - 对于 `entryIndices` 中的每个索引，将最佳匹配附加到 `Entries[index]`。
- 使用 **第一个（最佳）匹配** 当可用时。

为每个受影响的条目创建字段（如果不存在），将 MCP API 响应键映射到 Go 结构字段名：

```json
"TunedEntry": {
  "Name": "",
  "CountryCode": "",
  "RegionCode": "",
  "PlaceType": "",
  "H3Cells": [],
  "BoundingBox": []
}
```

`TunedEntry` 字段是一个 **单个对象**（不是数组）。它包含从 MCP 服务器返回的最佳匹配。

**MCP 响应键 → JSON 键映射**：

| MCP API 响应键 | JSON 键                   |
|----------------|----------------------------|
| `placeName`          | `Name`                     |
| `countryCode`        | `CountryCode`                  |
| `stateCode`         | `RegionCode`               |
| `placeType`         | `PlaceType`                |
| `h3Cells`          | `H3Cells`                  |
| `boundingBox`        | `BoundingBox`              |

具有无 UUID 匹配的条目（即 MCP 服务器对它们的 UUID 返回无响应）必须接收一个空的 `TunedEntry: {}` 对象 — 永远不要让该字段为空。

- 写回数据到：`./run/data/report-data.json`
- 规则：
  - 维护所有现有的验证标志。
  - **不要** 创建任何中间文件。


### 阶段 5：生成调整报告

通过使用 `./scripts/templates/index.html` 中的模板渲染，使用来自 `./run/data/report-data.json` 和 `./run/data/comments.json` 的数据生成一个自包含的 HTML 报告。

将完成的报告写入 `./run/report/geofeed-report.html`。生成后，尝试在系统的默认浏览器中打开它（例如，`webbrowser.open()`）。如果运行在无头环境、CI 管道或远程容器中，没有可用的浏览器，则跳过浏览器步骤，而是向用户显示文件路径，以便他们可以打开或下载。

**模板使用 Go `html/template` 语法** (`{{.Field}}`, `{{range}}`, `{{if eq}}`, 等）。编写一个 Python 脚本，读取模板，从 JSON 数据文件构建渲染上下文，并处理模板占位符以生成最终 HTML。不要修改模板文件本身 — 所有处理都在渲染时的 Python 脚本中发生。

#### 步骤 1：替换元数据占位符

将模板中的每个 `{{.Metadata.X}}` 占位符替换为 `report-data.json` 中的相应值。由于 JSON 键与模板占位符直接对应，映射是直接的 — `{{.Metadata.InputFile}}` 映射到 JSON 键 `InputFile`，等等。

| 模板占位符                   | JSON 键 (`report-data.json`)     |
|--------------------------------|-----------------------------|
| `{{.Metadata.InputFile}}`              | `InputFile`                       |
| `{{.Metadata.Timestamp}}`              | `Timestamp`                       |
| `{{.Metadata.TotalEntries}}`           | `TotalEntries`                    |
| `{{.Metadata.IpV4Entries}}`            | `IpV4Entries`                     |
| `{{.Metadata.IpV6Entries}}`            | `IpV6Entries`                     |
| `{{.Metadata.InvalidEntries}}`         | `InvalidEntries`                  |
| `{{.Metadata.Errors}}`                 | `Errors`                          |
| `{{.Metadata.Warnings}}`                 | `Warnings`                        |
| `{{.Metadata.Suggestions}}`            | `Suggestions`                     |
| `{{.Metadata.OK}}`                     | `OK`                              |
| `{{.Metadata.CityLevelAccuracy}}`      | `CityLevelAccuracy`               |
| `{{.Metadata.RegionLevelAccuracy}}`    | `RegionLevelAccuracy`             |
| `{{.Metadata.CountryLevelAccuracy}}`   | `CountryLevelAccuracy`            |
| `{{.Metadata.DoNotGeolocate}}`         | `DoNotGeolocate` (元数据) |

**关于 `{{.Metadata.Timestamp}}` 的注意**：此占位符出现在 JavaScript `new Date(...)` 调用内部。用原始整数值替换它（不需要对数字字面量进行 HTML 转义）。所有其他元数据值应进行 HTML 转义，因为它们出现在 HTML 元素文本内。

#### 步骤 2：替换注释映射占位符

在模板中找到此模式：

```javascript
const commentMap = {{.Comments}};
```

将 `{{.Comments}}` 替换为来自 `./run/data/comments.json` 的序列化 JSON 对象。JSON 嵌入为 JavaScript 对象字面量（不是字符串内），因此不需要额外的转义：

```python
comments_json = json.dumps(comments)
template = template.replace("{{.Comments}}", comments_json)
```

#### 步骤 3：扩展条目范围块

模板包含一个 `{{range .Entries}}...{{end}}` 块在 `<tbody id="entriesTableBody">` 内。按以下方式处理它：

1. **提取** 范围块正文，使用正则表达式。**关键**：块包含嵌套的 `{{end}}` 标签（来自 `{{if eq .Status ...}}`、`{{if .Checked}}` 和 `{{range .Messages}}`）。像 `\{\{range \.Entries\}\}(.*?)\{\{end\}\}` 这样的简单非贪婪匹配会匹配 **第一个** 内部 `{{end}}`，从而截断块。相反，将外部的 `{{end}}` 锚定到它后面的 `</tbody>`：

    ```python
    m = re.search(
        r'\{\{range \.Entries\}\}(.*?)\{\{end\}\}\s*</tbody>',
        template,
        re.DOTALL,
    )
    entry_body = m.group(1)  # template 文本，表示一个条目迭代
    ```

    这确保了你能够捕获包括所有三个 `<tr>` 行和嵌套 `{{range .Messages}}...{{end}}` 在内的完整块正文。

2. **迭代** `report-data.json` 中的每个条目。
3. **扩展** 每个条目的块正文，使用以下处理顺序：

**处理顺序**（从最内层构造开始以避免 `{{end}}` 混乱）：

1. 评估 `{{if eq .Status ...}}...{{end}}` 条件性（状态徽章类和图标）。
2. 评估 `{{if .Checked}}...{{end}}` 条件性（消息复选框）。
3. 扩展 `{{range .Messages}}...{{end}}` 内部范围。
4. 替换简单的 `{{.Field}}` 占位符。

##### 条目字段映射

在范围块正文内，替换每个条目的以下占位符：

| 模板占位符           | JSON 键 (`Entries[]`)       | 备注                                                        |
|--------------------------|-----------------------|--------------------------------------------------------------|
| `{{.Line}}`                    | `Line`                       | 直接整数值                                                 |
| `{{.IPPrefix}}`                | `IPPrefix`                   | HTML-转义                                                 |
| `{{.CountryCode}}`             | `CountryCode`                | HTML-转义                                                 |
| `{{.RegionCode}}`             | `RegionCode`                 | HTML-转义                                                 |
| `{{.City}}`                | `City`                       | HTML-转义                                                 |
| `{{.Status}}`                  | `Status`                     | HTML-转义                                                 |
| `{{.HasError}}`                | `HasError`                   | 小写字符串：`"true"` 或 `"false"`                      |
| `{{.HasWarning}}`                | `HasWarning`                 | 小写字符串：`"true"` 或 `"false"`                      |
| `{{.HasSuggestion}}`            | `HasSuggestion`              | 小写字符串：`"true"` 或 `"false"`                      |
| `{{.GeocodingHint}}`          | `GeocodingHint`              | 空字符串 `""`                                            |
| `{{.Tunable}}`                 | `Tunable`                    | `"true"` 或 `"false"`                                        |
| `{{.TunedEntry.CountryCode}}`  | `TunedEntry.CountryCode`     | 如果 `TunedEntry` 为空 `{}`，则为 `""`                   |
| `{{.TunedEntry.RegionCode}}`   | `TunedEntry.RegionCode`      | 如果 `TunedEntry` 为空 `{}`，则为 `""`                   |
| `{{.TunedEntry.Name}}`         | `TunedEntry.Name`            | 如果 `TunedEntry` 为空 `{}`，则为 `""`                   |
| `{{.TunedEntry.H3Cells}}`      | `TunedEntry.H3Cells`         | 括号括号分隔的空格；`""` 如果为空（见格式下方） |
| `{{.TunedEntry.BoundingBox}}`  | `TunedEntry.BoundingBox`     | 括号括号分隔的空格；`""` 如果为空（见格式下方） |

具有 `TunedEntry` 字段（即使其值为 `{}`）的每个条目都必须有一个 `TunedEntry` 键（即使其值为 `{}`）。如果条目缺少该键，则添加 `"TunedEntry": {}`，然后重新保存 `report-data.json`。

**`data-h3-cells` 和 `data-bounding-box` 格式**：它们 **不是** JSON 数组。它们是括号括号分隔的空格。**不要** 使用 JSON 序列化（字符串元素周围没有引号，数字之间没有逗号）。示例：

- `[836752fffffffff 836755fffffffff]` — 正确
- `["836752fffffffff","836755fffffffff]` — **错误**，引号会破坏解析
- `[-71.70 10.73 -71.52 10.55]` — 正确
- `[]` — 正确，为空

#### 输出保证

- 报告必须在任何现代浏览器中可读，无需额外的网络依赖，除了模板中已有的 CDN 链接（`leaflet`、`h3-js`、`bootstrap-icons`、Raleway 字体）。
- 嵌入 HTML 中的所有值都必须进行 **HTML 转义** (`<`, `>`, `&`, `"`) 以防止渲染问题。
- `commentMap` 嵌入为直接的 JavaScript 对象字面量（不是字符串内），因此不需要额外的 JavaScript 字符串转义 — 直接发出有效的 JSON。
- 所有值都必须仅从分析输出中派生，**不要** 重新计算启发式值。
