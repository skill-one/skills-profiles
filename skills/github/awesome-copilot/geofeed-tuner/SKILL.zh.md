---
name: geofeed-tuner
description: 当用户提及IP地理位置信息源、RFC 8805、地理位置信息源或需要帮助创建、调整、验证或发布CSV格式的自发布IP地理位置信息源时，请使用此技能。目标用户群体是网络运营商、互联网服务提供商、移动运营商、云服务提供商、主机公司、互联网交换点或卫星服务提供商，他们询问IP地理位置信息准确性或地理位置信息源编写最佳实践。该技能有助于创建、优化和改进CSV格式的IP地理位置信息源，并提供超越RFC 8805合规性的主观建议。请勿用于私有或内部IP地址管理——仅适用于公开可路由的IP地址。
---

# Geofeed Tuner – 创建更优的 IP 地理位置 Feeds

这项技能可以帮助您创建和改进 CSV 格式的 IP 地理位置 Feeds，具体功能包括：
- 确保 CSV 文件格式良好且一致
- 检查是否符合 [RFC 8805](references/rfc8805.txt)（行业标准）
- 应用从实际部署中学习到的**主观最佳实践**
- 提出关于准确性、完整性和隐私的改进建议

## 何时使用此技能

- 当用户需要帮助**创建、改进或发布** CSV 格式的 IP 地理位置 Feeds 文件时，请使用此技能。
- 使用它来**调优和排错 CSV 地理位置 Feeds** — 捕获错误、建议改进，并确保 RFC 合规性之外的实际可用性。
- **目标受众：**
  - 负责公开可路由 IP 地址空间的网络运营商、管理员和工程师
  - 互联网服务提供商（ISP）、移动运营商、云服务提供商、主机和托管公司、互联网交换运营商和卫星互联网提供商等组织
- **不要使用**此技能进行私有或内部 IP 地址管理；它仅适用于**公开可路由的 IP 地址**。

## 前置条件

- 需要 **Python 3**。

## 目录结构和文件管理

此技能在**分发文件**（只读）和**工作文件**（在运行时生成）之间使用清晰的分离。

### 只读目录（不要修改）

以下目录包含静态分发资源。**不要在这些目录中创建、修改或删除文件：**

| 目录      | 用途                                                    |
|----------|------------------------------------------------------------|
| `assets/` | 静态数据文件（ISO 代码、示例）                    |
| `references/` | RFC 规范和代码片段供参考         |
| `scripts/` | 可执行代码和报告 HTML 模板文件        |

### 工作目录（生成内容）

所有生成的、临时的和输出文件都放在这些目录中：

| 目录       | 用途                                              |
|----------|------------------------------------------------------|
| `run/`    | 所有代理生成内容的工 作目录    |
| `run/data/` | 从远程 URL 下载的 CSV 文件                |
| `run/report/` | 生成的 HTML 调优报告                        |

### 文件管理规则

1. **永远不要向 `assets/`、`references/` 或 `scripts/` 写入** — 这些是技能分发的一部分，必须保持不变。
2. **所有下载的输入文件**（从远程 URL）必须保存到 `./run/data/`。
3. **所有生成的 HTML 报告**必须保存到 `./run/report/`。
4. **所有生成的 Python 脚本**必须保存到 `./run/`。
5. `run/` 目录可以在会话之间清除；不要在那里存储永久数据。
6. **执行的工作目录：** 所有在 `./run/` 中生成的脚本都必须以**技能根目录**（包含 `SKILL.md` 的目录）作为当前工作目录执行，以便像 `assets/iso3166-1.json` 和 `./run/data/report-data.json` 这样的相对路径可以正确解析。在运行脚本之前，**不要**进入 `./run/`。

## 处理流程：顺序阶段执行

所有阶段必须**按顺序**执行，从阶段 1 到阶段 6。每个阶段都依赖于前一个阶段的成功完成。例如，**结构检查**必须完成才能运行**质量分析**。

以下是各阶段的总结。代理必须遵循每个阶段部分中概述的详细步骤。

| 阶段 | 名称                       | 描述                                                                       |
|------|----------------------------|-----------------------------------------------------------------------------------|
| 1    | 理解标准    | 审查 RFC 8805 对自发布 IP 地理位置 Feeds 的关键要求   |
| 2    | 收集输入               | 从本地文件或远程 URL 收集 IP 子网数据                            |
| 3    | 检查和建议       | 验证 CSV 结构，分析 IP 前缀，并检查数据质量               |
| 4    | 调优数据查找         | 使用 Fastah 的 MCP 工具检索用于提高地理位置准确性的调优数据  |
| 5    | 生成调优报告     | 创建一个总结分析和建议的 HTML 报告                    |
| 6    | 最终审查               | 验证报告数据的连贯性和完整性                            |

**不要跳过阶段。** 每个阶段都为后续阶段提供关键的检查或数据转换。

### 执行计划规则

在执行每个阶段之前，代理必须生成一个可见的 TODO 清单。

该计划必须：
- 出现在阶段的**最开始**
- 按顺序列出每个步骤
- 使用复选框格式
- 随步骤完成实时更新

### 阶段 1：理解标准

本技能强制执行的 RFC 8805 关键要求总结如下。**使用此摘要作为您的工作参考。** 只有在遇到边缘情况、模糊情况或用户询问此处未涵盖的标准问题时，才参考完整的 [RFC 8805 文本](references/rfc8805.txt)。

#### RFC 8805 关键事实

**目的：** 自发布 IP 地理位置 Feeds 允许网络运营商以简单的 CSV 格式发布其 IP 地址空间的权威位置数据，使地理位置提供者能够整合运营商提供的更正。

**CSV 列顺序（第 2.1.1.1–2.1.1.5 节）：**

| 列 | 字段         | 必填 | 备注                                                      |
|----|--------------|------|------------------------------------------------------------|
| 1  | `ip_prefix`   | 是   | CIDR 表示法；IPv4 或 IPv6；必须是网络地址                 |
| 2  | `alpha2code`  | 否   | ISO 3166-1 alpha-2 国家代码；空或 "ZZ" = 不要地理位置 |
| 3  | `region`      | 否   | ISO 3166-2 地区代码（例如，`US-CA`）               |
| 4  | `city`        | 否   | 自由文本城市名称；没有权威验证集                       |
| 5  | `postal_code` | 否   | **已弃用** — 必须为空或不存在             |

**结构规则：**
- 文件可以包含以 `#` 开头的注释行（包括标题行，如果存在）。
- 标题行是可选的；如果存在，如果它以 `#` 开头，则被视为注释。
- 文件必须使用 UTF-8 编码。
- 子网主机位不得设置（即 `192.168.1.1/24` 无效；使用 `192.168.1.0/24`）。
- 仅适用于**全球可路由**的单播地址 — 不包括私有、回环、链路本地或多播空间。

**不要地理位置：** 一个 `alpha2code` 为空或大小写不敏感的 `ZZ`（无论地区/城市值如何）的条目是一个明确的信号，表明运营商不希望对该前缀应用地理位置。

**邮政编码已弃用（第 2.1.1.5 节）：** 第五列不得包含邮政或 ZIP 码。它们对于 IP 范围映射来说过于精细，并引发隐私问题。

### 阶段 2：收集输入

- 如果用户尚未提供 IP 子网或范围的列表（有时称为 `inetnum` 或 `inet6num`），请提示他们提供。接受的输入格式：
  - 粘贴到聊天中的文本
  - 本地 CSV 文件
  - 指向 CSV 文件的远程 URL

- 如果输入是**远程 URL**：
  - 尝试在处理之前将 CSV 文件下载到 `./run/data/`。
  - 在 HTTP 错误（4xx、5xx、超时或重定向循环）时，**立即停止**并向用户报告：
    `Feed URL 无法访问：HTTP {status_code}。请验证 URL 是否公开可访问。`
  - 不要在下载不完整或空的情况下继续到阶段 3。

- 如果输入是**本地文件**，直接处理它，无需下载。

- **编码检测和规范化：**
  1. 首先尝试将其作为 UTF-8 读取。
  2. 如果引发 `UnicodeDecodeError`，尝试 `utf-8-sig`（带 BOM 的 UTF-8），然后 `latin-1`。
  3. 成功解码后，重新编码并写入工作副本作为 UTF-8。
  4. 如果没有编码成功，停止并报告：`无法解码输入文件。请将其保存为 UTF-8 并重试。`

### 阶段 3：检查和建议

#### 执行规则
- 为此阶段生成一个**脚本**。
- 不要将此阶段与其他阶段组合。
- 不要预计算后续阶段的数据。
- 将输出存储为 JSON 文件：`./run/data/report-data.json`

#### 模式定义

以下 JSON 结构在阶段 3 期间**不可变**。阶段 4 将在稍后向 `Entries` 中的每个对象添加一个 `TunedEntry` 对象 — 这是唯一允许的模式扩展，并且发生在单独的阶段。

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

**顶层元数据：**
- `InputFile`：原始输入源，无论是本地文件名还是远程 URL。
- `Timestamp`：调优执行时的 Unix 纪元毫秒数。
- `TotalEntries`：处理的数据行总数（不包括注释和空白行）。
- `IpV4Entries`：IPv4 子网条目的计数。
- `IpV6Entries`：IPv6 子网条目的计数。
- `InvalidEntries`：IP 前缀解析和 CSV 解析失败的条目计数。
- `Errors`：`Status` 为 `ERROR` 的条目总数。
- `Warnings`：`Status` 为 `WARNING` 的条目总数。
- `OK`：`Status` 为 `OK` 的条目总数。
- `Suggestions`：`Status` 为 `SUGGESTION` 的条目总数。
- `CityLevelAccuracy`：`City` 非空的合法条目计数。
- `RegionLevelAccuracy`：`RegionCode` 非空且 `City` 为空的合法条目计数。
- `CountryLevelAccuracy`：`CountryCode` 非空、`RegionCode` 为空且 `City` 为空的合法条目计数。
- `DoNotGeolocate`（元数据）：`CountryCode`、`RegionCode` 和 `City` 全部为空的合法条目计数。

**条目字段：**
- `Entries`：数组，每个数据行一个对象，具有以下每个条目字段：
  - `Line`：原始 CSV 中 1 进制的行号（包括所有行，包括注释和空白行）。
  - `IPPrefix`：CIDR 斜杠表示法中的标准化 IP 前缀。
  - `CountryCode`：ISO 3166-1 alpha-2 国家代码，或空字符串。
  - `RegionCode`：ISO 3166-2 地区代码（例如，`US-CA`），或空字符串。
  - `City`：城市名称，或空字符串。
  - `Status`：分配的最高严重性：`ERROR` > `WARNING` > `SUGGESTION` > `OK`。
  - `IPVersion`：根据解析的 IP 前缀为 `"IPv4"` 或 `"IPv6"`。
  - `Messages`：消息对象数组，每个对象具有：
    - `ID`：来自**验证规则参考**表（见下文）的字符串标识符（例如，`"1101"`、`"3301"`）。
    - `Type`：严重性类型：`"ERROR"`、`"WARNING"` 或 `"SUGGESTION"`。
    - `Text`：人类可读的验证消息字符串。
    - `Checked`：如果验证规则是自动可调的（参考表中 `Tunable: true`），则为 `true`，否则为 `false`。控制报告中的复选框是 `checked` 还是 `disabled`。
  - `HasError`：如果任何消息的 `Type` 为 `"ERROR"`，则为 `true`。
  - `HasWarning`：如果任何消息的 `Type` 为 `"WARNING"`，则为 `true`。
  - `HasSuggestion`：如果任何消息的 `Type` 为 `"SUGGESTION"`，则为 `true`。
  - `DoNotGeolocate`（条目）：`CountryCode` 为空或 `"ZZ"`，即条目是明确的不要地理位置信号。
  - `GeocodingHint`：阶段 3 中始终为空字符串 `""`。保留供将来使用。
  - `Tunable`：如果条目中的**任何**消息具有 `Checked: true`，则为 `true`。通过所有消息的 `Checked` 值的逻辑 OR 计算。此标志驱动报告中的“调优”按钮的可见性。

#### 验证规则参考

向条目添加消息时，使用此表中的 `ID`、`Type`、`Text` 和 `Checked` 值。

| ID     | Type         | 文本                                                                                           | Checked | 条件参考                    |
|-------|--------------|------------------------------------------------------------------------------------------------|---------|--------------------------------|
| `1101` | `ERROR`      | IP 前缀为空                                                                             | `false` | IP 前缀分析：空              |
| `1102` | `ERROR`      | 无效 IP 前缀：无法解析为 IPv4 或 IPv6 网络                                     | `false` | IP 前缀分析：无效语法     |
| `1103` | `ERROR`      | 非公开 IP 范围不允许在 RFC 8805 Feeds 中                                         | `false` | IP 前缀分析：非公开         |
| `3101` | `SUGGESTION` | IPv4 前缀异常大，可能表示输入错误                                         | `false` | IP 前缀分析：IPv4 < /22         |
| `3102` | `SUGGESTION` | IPv6 前缀异常大，可能表示输入错误                                         | `false` | IP 前缀分析：IPv6 < /64         |
| `1201` | `ERROR`      | 无效国家代码：不是有效的 ISO 3166-1 alpha-2 值                                     | `true`  | 国家代码分析：无效         |
| `1301` | `ERROR`      | 无效地区格式；预期 COUNTRY-SUBDIVISION（例如，US-CA）                              | `true`  | 地区代码分析：坏格式       |
| `1302` | `ERROR`      | 无效地区代码：不是有效的 ISO 3166-2 下属区域                                        | `true`  | 地区代码分析：未知代码     |
| `1303` | `ERROR`      | 地区代码与指定的国家代码不匹配                                          | `true`  | 地区代码分析：不匹配         |
| `1401` | `ERROR`      | 无效城市名称：不允许占位符值                                            | `false` | 城市名称分析：占位符        |
| `1402` | `ERROR`      | 无效城市名称：检测到缩写或代码值                                            | `true`  | 城市名称分析：缩写       |
| `2401` | `WARNING`    | 城市名称格式不一致；考虑规范化该值                           | `true`  | 城市名称分析：格式         |
| `1501` | `ERROR`      | 邮政编码已由 RFC 8805 弃用，出于隐私原因必须删除                          | `true`  | 邮政编码检查                      |
| `3301` | `SUGGESTION` | 地区通常对小领土来说是不必要的；考虑删除地区值        | `true`  | 调优：小领土地区         |
| `3402` | `SUGGESTION` | 城市级粒度通常对小领土来说是不必要的；考虑删除城市值 | `true`  | 调优：小领土城市           |
| `3303` | `SUGGESTION` | 当指定城市时，建议地区代码；从下拉菜单中选择地区         | `true`  | 调优：缺少城市时地区       |
| `3104` | `SUGGESTION` | 确认此子网是否有意标记为不要地理位置或缺少位置数据 | `true`  | 调优：未指定地理位置        |

#### 填充消息

当验证检查匹配时，使用参考表中的值向条目的 `Messages` 数组添加消息：
```python
entry["Messages"].append({
    "ID": "1201",      # 来自表格
    "Type": "ERROR",   # 来自表格
    "Text": "无效的国家代码：不是有效的 ISO 3166-1 alpha-2 值",  # 来自表格
    "Checked": True    # 来自表格（True = 可调节）
})
```

在为条目填充所有消息后，派生条目级标志：
```python
entry["HasError"] = any(m["Type"] == "ERROR" for m in entry["Messages"])
entry["HasWarning"] = any(m["Type"] == "WARNING" for m in entry["Messages"])
entry["HasSuggestion"] = any(m["Type"] == "SUGGESTION" for m in entry["Messages"])
entry["Tunable"] = any(m["Checked"] for m in entry["Messages"])
```

#### 准确性级别计数规则

准确性级别是**互斥的**。根据最细粒度的非空地理字段将每个有效（非ERROR、非无效）条目分配到 exactly 一个桶中：

| 条件                                                    | 桶                      |
|--------------------------------------------------------------|-----------------------------|
| `City` 非空                                          | `CityLevelAccuracy`         |
| `RegionCode` 非空 AND `City` 为空                   | `RegionLevelAccuracy`       |
| `CountryCode` 非空，`RegionCode` 和 `City` 为空       | `CountryLevelAccuracy`      |
| `DoNotGeolocate`（条目）为 `true`                           | `DoNotGeolocate`（元数据） |

**不计算**具有 `HasError: true` 的条目或在任何准确性桶中的 `InvalidEntries` 条目。

代理**必须不**：
- 重命名字段
- 添加或删除字段
- 更改数据类型
- 重新排序键
- 修改嵌套
- 包装对象
- 分割到多个文件

如果值未知，**保持为空** — 永远不要编造数据。

#### 结构与格式检查

此阶段验证您的源是否格式良好且可解析。**关键结构错误**必须在调谐器分析地理位置质量之前解决。

##### CSV 结构

本节定义了用于 IP 地理位置 源的**CSV 格式输入文件**的规则。
目标是确保文件可以可靠地解析并规范化为**一致的内表示**。

- **CSV 结构检查**
  - 如果 `pandas` 可用，则使用它进行 CSV 解析。
  - 否则，回退到 Python 的内置 `csv` 模块。

  - 确保 CSV 包含**恰好 4 或 5 个逻辑列**。
  - 允许注释行。
  - 标题行**可能存在也可能不存在**。
  - 如果不存在标题行，则假设隐式列顺序：
    ```
    ip_prefix, alpha2code, region, city, postal code (已弃用)
    ```
  - 参考示例输入文件：
    [`assets/example/01-user-input-rfc8805-feed.csv`](assets/example/01-user-input-rfc8805-feed.csv)

- **CSV 清理和规范化**
  - 使用与以下操作等效的 Python 逻辑清理和规范化 CSV：
    - 选择**仅前五个列**，删除第五个列之后的任何列。
    - 使用 UTF-8 BOM 写入输出文件。

  - **注释**
    - 删除**第一个列以 `#` 开头的注释行**。
    - 这也会删除以 `#` 开头的标题行。
    - 使用**1-based 行号**作为键，完整原始行作为值创建注释映射。还存储空白行。
    - 将此映射存储在 JSON 文件中：`./run/data/comments.json`
    - 示例：`{ "4": "# 对于小型城邦国家，省略州 ISO2 代码是允许的" }`

- **注意**
  - 两种实现路径（`pandas` 和内置 `csv`）都必须使用 `utf-8-sig` 编码写入输出，以确保**存在 UTF-8 BOM**。

#### IP 前缀分析
  - 检查每个条目的 `IPPrefix` 字段是否存在且非空。
  - 检查条目之间是否存在重复的 `IPPrefix` 值。
  - 如果发现重复项，停止技能并向用户报告消息：`Duplicate IP prefix detected: {ip_prefix_value} appears on lines {line_numbers}`
  - 如果未发现重复项，继续分析。

  - **检查**
    - 每个子网必须使用 `references/` 文件夹中的代码片段干净地解析为**IPv4 或 IPv6 网络**。
    - 子网必须规范化并以 CIDR 斜杠表示法显示。
      - 单主机 IPv4 子网必须表示为**`/32`**。
      - 单主机 IPv6 子网必须表示为**`/128`**。

  - **ERROR**
    - 将以下条件报告为**ERROR**：

    - **无效的子网语法**
      - 消息 ID：`1102`

    - **非公共地址空间**
      - 适用于**私有、回环、链路本地、多播或其他非公共**子网
        - 在 Python 中，使用 `is_private` 和相关地址属性（如 `./references` 中所示）检测非公共范围。
      - 消息 ID：`1103`

  - **SUGGESTION**
    - 将以下条件报告为**SUGGESTION**：

    - **过大的 IPv6 子网**
      - 前缀短于 `/64`
      - 消息 ID：`3102`

    - **过大的 IPv4 子网**
      - 前缀短于 `/22`
      - 消息 ID：`3101`

#### 地理位置 质量检查

分析地理位置数据的**准确性和一致性**：
  - 国家代码
  - 地区代码
  - 城市名称
  - 已弃用的字段

此阶段在结构检查通过后运行。

##### 国家代码分析
  - 使用本地可用的数据表 [`ISO3166-1`](assets/iso3166-1.json) 进行检查。
    - 包含国家和地区的 ISO 代码的 JSON 数组
    - 每个对象包括：
      - `alpha_2`：两字母国家代码
      - `name`：简短国家名称
      - `flag`：旗帜表情符号
    - 此文件表示 RFC 8805 CSV 的**有效 `CountryCode` 值的超集**。
  - 检查条目的 `CountryCode`（RFC 8805 第 2.1.1.2 节，列 `alpha2code`）与 `alpha_2` 属性。
  - 示例代码可在 `references/` 目录中找到。

  - 如果国家在 [`assets/small-territories.json`](assets/small-territories.json) 中找到，则将条目内部标记为小型领土。此标志用于后续检查和建议，但**不存储在输出 JSON 中**（它是瞬态验证状态）。

  - **注意**：`small-territories.json` 包含一些历史/有争议的代码（`AN`、`CS`、`XK`），这些代码在 `iso3166-1.json` 中不存在。使用其中任何一个作为 `CountryCode` 的条目将失败国家代码验证（ERROR），即使它作为小型领土匹配。国家代码 ERROR 优先级更高 — 不要基于小型领土标志抑制它。

  - **ERROR**
    - 将以下条件报告为**ERROR**：
    - **无效的国家代码**
      - 条件：`CountryCode` 存在但未在 `alpha_2` 集中找到
      - 消息 ID：`1201`

  - **SUGGESTION**
    - 将以下条件报告为**SUGGESTION**：

    - **子网的未指定地理位置**
      - 条件：子网的**所有地理字段**（`CountryCode`、`RegionCode`、`City`）都为空。
      - 操作： 
        - 将 `DoNotGeolocate = true` 设置为条目。
        - 将 `CountryCode` 设置为 `ZZ`。
      - 消息 ID：`3104`

##### 地区代码分析
  - 使用本地可用的数据表 [`ISO3166-2`](assets/iso3166-2.json) 进行检查。
    - 包含国家分区的 ISO 分配代码的 JSON 数组
    - 每个对象包括：
      - `code`：分区代码，以国家代码为前缀（例如，`US-CA`）
      - `name`：简短分区名称
    - 此文件表示 RFC 8805 CSV 的**有效 `RegionCode` 值的超集**。
  - 如果提供了 `RegionCode` 值（RFC 8805 第 2.1.1.3 节）：
    - 检查格式是否匹配 `{COUNTRY}-{SUBDIVISION}`（例如，`US-CA`、`AU-NSW`）。
    - 检查值是否与 `code` 属性（已带有国家代码前缀）匹配。

  - **小型领土例外**：如果条目是小型领土**并且** `RegionCode` 值等于条目的 `CountryCode`（例如，新加坡的 `SG` 作为国家和地区），则将地区视为可接受 — 跳过此条目的所有地区验证检查。小型领土实际上是城市国家，没有有意义的 ISO 3166-2 行政分区。

  - **ERROR**
    - 将以下条件报告为**ERROR**：
    - **无效的地区格式**
      - 条件：`RegionCode` 不匹配 `{COUNTRY}-{SUBDIVISION}` **并且** 小型领土例外不适用
      - 消息 ID：`1301`
    - **未知地区代码**
      - 条件：`RegionCode` 值不在 `code` 集中找到**并且** 小型领土例外不适用
      - 消息 ID：`1302`
    - **国家-地区不匹配**
      - 条件：`RegionCode` 的国家部分与 `CountryCode` 不匹配
      - 消息 ID：`1303`

##### 城市名称分析

  - 城市名称仅使用**启发式检查**进行验证。
  - 目前**没有**可用于验证城市名称的权威数据集。

  - **ERROR**
    - 将以下条件报告为**ERROR**：
    - **占位符或无意义的值**
      - 条件：包括但不限于占位符或无意义的值：
        - `undefined`
        - `Please select`
        - `null`
        - `N/A`
        - `TBD`
        - `unknown`
      - 消息 ID：`1401`

    - **截断名称、缩写或机场代码**
      - 条件：不表示有效城市名称的截断名称、缩写或机场代码：
        - `LA`
        - `Frft`
        - `sin01`
        - `LHR`
        - `SIN`
        - `MAA`
      - 消息 ID：`1402`

  - **WARNING**
    - 将以下条件报告为**WARNING**：
    - **不一致的大小写或格式**
      - 条件：大小写、空格或格式不一致的城市名称，可能会降低数据质量，例如：
        - `HongKong` vs `Hong Kong`
        - 混合大小写或意外的脚本使用
      - 消息 ID：`2401`

##### 邮政编码检查
  - RFC 8805 第 2.1.1.5 节明确**弃用**邮政或 ZIP 代码。
  - 邮政代码可以表示非常小的人口，并且**不被认为是**映射 IP 地址范围（本质上是统计性的）的隐私安全。

  - **ERROR**
    - 将以下条件报告为**ERROR**：
    - **存在邮政代码**
      - 条件：邮政/ZIP 代码字段存在非空值。
      - 消息 ID：`1501`

#### 调谐和建议

此阶段应用**主观建议**，这些建议超越了 RFC 8805，从现实世界的地理位置源部署中学习，以提高准确性和可用性。

- **SUGGESTION**
  - 将以下条件报告为**SUGGESTION**：

  - **小型领土指定了地区或城市**
    - 条件：
      - 条目是小型领土
      - `RegionCode` 非空 **OR**
      - `City` 非空。
    - 消息 ID：`3301`（地区）、`3402`（城市）

  - **指定了城市但缺少地区代码**
    - 条件：
      - `City` 非空
      - `RegionCode` 为空
      - 条目**不是**小型领土
    - 消息 ID：`3303`

### 阶段 4：调谐数据查找

#### 目标
使用 Fastah 的 `rfc8805-row-place-search` 工具查找所有 `Entries`。

#### 执行规则
- 仅生成一个**脚本**用于有效载荷生成（读取数据集并写入一个或多个有效载荷 JSON 文件；不要从该脚本调用 MCP）。
- 服务器每批仅接受 1000 个条目，因此如果有超过 1000 个条目，则分成多个请求。
- 代理必须读取生成的有效载荷文件，从它们构造请求，并将这些请求以最多 1000 个条目为一批发送到 MCP 服务器。
- **MCP 失败**：如果 MCP 服务器无法访问、返回错误或对任何一批返回无结果，则记录警告并继续到阶段 5。将受影响的条目的 `TunedEntry: {}` 设置。不要阻塞报告生成。向用户明确通知：`Tuning data lookup unavailable; the report will show validation results only.`
- 建议**仅供参考** — **永远不要自动填充**它们。

#### 步骤 1：使用去重构建查找有效载荷

从 `./run/data/report-data.json` 加载数据集
- 读取 `Entries` 数组。每个条目将用于构建 MCP 查找有效载荷。

通过去重减少服务器请求：
- 对于 `Entries` 中的每个条目，计算内容哈希（`CountryCode` + `RegionCode` + `City` 的哈希）。
- 创建去重映射：`{ contentHash -> { rowKey, payload, entryIndices: [] } }`。rowKey 是发送到 MCP 服务器以匹配响应的 UUID。
- 如果条目的哈希已存在，将其**0-based array index** 在 `Entries` 中添加到该去重条目的 `entryIndices` 数组。
- 如果哈希是新的，生成一个**UUID (rowKey)** 并创建一个新的去重条目。

构建请求批次：
- 从映射中提取唯一的去重条目，保持去重顺序。
- 构建每个批次最多 1000 项。
- 对于每个批次，保留一个内存结构，如 `[{ rowKey, payload, entryIndices }, ...]`，以通过 rowKey 匹配响应。
- 在写入 MCP 有效载荷文件时，在每个有效载荷对象中包含 `rowKey` 字段：

```json
[
    {"rowKey": "550e8400-e29b-41d4-a716-446655440000", "countryCode":"CA","regionCode":"CA-ON","cityName":"Toronto"},
    {"rowKey": "6ba7b810-9dad-11d1-80b4-00c04fd430c8", "countryCode":"IN","regionCode":"IN-KA","cityName":"Bangalore"},
    {"rowKey": "6ba7b811-9dad-11d1-80b4-00c04fd430c8", "countryCode":"IN","regionCode":"IN-KA"}
]
```

- 在读取响应时，将每个响应 `rowKey` 字段与相应的去重条目匹配以检索所有相关 `entryIndices`。

规则：
- 将有效载荷写入：`./run/data/mcp-server-payload.json`
- 写入有效载荷后退出脚本。

#### 步骤 2：调用 Fastah MCP 工具

- Fastah MCP 服务器的示例 `mcp.json` 风格配置如下：
```json
    "fastah-ip-geofeed": {
      "type": "http",
      "url": "https://mcp.fastah.ai/mcp"
    }
```
- 服务器：`https://mcp.fastah.ai/mcp`
- 工具及其模式：在第一个 `tools/call` 之前，代理**必须**发送 `tools/list` 请求以读取**`rfc8805-row-place-search`** 的输入和输出模式。
  使用发现的模式作为字段名称、类型和约束的权威来源。
- 以下是一个说明性示例，仅作参考；始终以 `tools/list` 返回的模式为准：

```json
[
    {"rowKey": "550e8400-...", "countryCode":"CA", ...},
    {"rowKey": "690e9301-...", "countryCode":"ZZ", ...}
]
- 打开 `./run/data/mcp-server-payload.json` 并发送所有去重后的条目及其 rowKeys。
- 如果去重后有多于 1000 个去重后的条目，则分成多个每个包含 1000 个条目的请求。
- 服务器将在每个响应中返回相同的 `rowKey` 字段用于映射回原始数据。
- **不要**使用本地数据。

#### 第 3 步：将调优数据附加到条目

- 生成一个新的 **脚本** 用于附加调优数据。
- 加载 `./run/data/report-data.json` 和去重映射（保存在步骤 1 的内存中，或从负载文件重新派生）。
- 对于 MCP 服务器的每个响应：
  - 从响应中提取 `rowKey`。
  - 从去重映射中查找与该 `rowKey` 关联的 `entryIndices` 数组。
  - 对于 `entryIndices` 中的每个索引，将最佳匹配附加到 `Entries[index]`。
- 在可用时，使用响应中的**第一个（最佳）匹配**。

如果受影响的条目中不存在该字段，则创建该字段。将 MCP API 响应键映射到 Go 结构体字段名：

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
|----------------------|----------------------------|
| `placeName`          | `Name`                     |
| `countryCode`        | `CountryCode`              |
| `stateCode`          | `RegionCode`               |
| `placeType`          | `PlaceType`                |
| `h3Cells`            | `H3Cells`                  |
| `boundingBox`        | `BoundingBox`              |

没有 UUID 匹配的条目（即 MCP 服务器没有为其 UUID 返回响应）必须接收一个空的 `TunedEntry: {}` 对象——**不要**让该字段为空。

- 将数据集写回：`./run/data/report-data.json`
- 规则：
  - 保持所有现有的验证标志。
  - **不要**创建额外的中间文件。

### 第 5 步：生成调优报告

通过使用 `./scripts/templates/index.html` 模板渲染 `./run/data/report-data.json` 和 `./run/data/comments.json` 中的数据来生成一个**自包含的 HTML 报告**。

将完成的报告写入 `./run/report/geofeed-report.html`。生成后，尝试在系统的默认浏览器中打开它（例如，`webbrowser.open()`）。如果在无头环境、CI 管道或远程容器中运行且没有浏览器可用，则跳过浏览器步骤，而是向用户显示文件路径，以便他们可以打开或下载。

**该模板使用 Go `html/template` 语法**（`{{.Field}}`、`{{range}}`、`{{if eq}}` 等）。编写一个 Python 脚本，读取模板，从 JSON 数据文件构建渲染上下文，并处理模板占位符以生成最终的 HTML。**不要**修改模板文件本身——所有处理都在渲染时的 Python 脚本中完成。

#### 第 1 步：替换元数据占位符

在模板中用 `report-data.json` 中的相应值替换每个 `{{.Metadata.X}}` 占位符。由于 JSON 键与模板占位符匹配，映射是直接的——`{{.Metadata.InputFile}}` 映射到 `InputFile` JSON 键，等等。

| 模板占位符                   | JSON 键 (`report-data.json`)     |
|--------------------------------|-----------------------------------|
| `{{.Metadata.InputFile}}`              | `InputFile`                       |
| `{{.Metadata.Timestamp}}`              | `Timestamp`                       |
| `{{.Metadata.TotalEntries}}`           | `TotalEntries`                    |
| `{{.Metadata.IpV4Entries}}`            | `IpV4Entries`                     |
| `{{.Metadata.IpV6Entries}}`            | `IpV6Entries`                     |
| `{{.Metadata.InvalidEntries}}`         | `InvalidEntries`                  |
| `{{.Metadata.Errors}}`                 | `Errors`                          |
| `{{.Metadata.Warnings}}`               | `Warnings`                        |
| `{{.Metadata.Suggestions}}`            | `Suggestions`                     |
| `{{.Metadata.OK}}`                     | `OK`                              |
| `{{.Metadata.CityLevelAccuracy}}`      | `CityLevelAccuracy`               |
| `{{.Metadata.RegionLevelAccuracy}}`    | `RegionLevelAccuracy`             |
| `{{.Metadata.CountryLevelAccuracy}}`   | `CountryLevelAccuracy`            |
| `{{.Metadata.DoNotGeolocate}}`         | `DoNotGeolocate` (元数据)       |

**关于 `{{.Metadata.Timestamp}}` 的说明：** 该占位符出现在 JavaScript `new Date(...)` 调用内部。用原始整数值替换它（不需要对 `<script>` 内的数字字面量进行 HTML 转义）。所有其他元数据值应在 HTML 元素文本中 HTML 转义。

#### 第 2 步：替换评论映射占位符

在模板中找到此模式：
```javascript
const commentMap = {{.Comments}};
```

用 `./run/data/comments.json` 中的序列化 JSON 对象替换 `{{.Comments}}`。JSON 直接嵌入为 JavaScript 对象字面量（不在字符串内部），因此不需要额外的转义：

```python
comments_json = json.dumps(comments)
template = template.replace("{{.Comments}}", comments_json)
```

#### 第 3 步：扩展条目范围块

模板包含一个 `{{range .Entries}}...{{end}}` 块在 `<tbody id="entriesTableBody">` 内。按以下方式处理它：

1. **提取** 范围块正文，使用正则表达式。**关键：** 块包含嵌套的 `{{end}}` 标签（来自 `{{if eq .Status ...}}`、`{{if .Checked}}` 和 `{{range .Messages}}`）。像 `\{\{range \.Entries\}\}(.*?)\{\{end\}\}` 这样的非贪婪匹配会匹配**第一个**内部 `{{end}}`，从而截断块。相反，将外部的 `{{end}}` 锚定到其后的 `</tbody>`：
    ```python
    m = re.search(
        r'\{\{range \.Entries\}\}(.*?)\{\{end\}\}\s*</tbody>',
        template,
        re.DOTALL,
    )
    entry_body = m.group(1)  # 模板文本，表示一个条目迭代
    ```
    这确保您捕获包括所有三个 `<tr>` 行和嵌套的 `{{range .Messages}}...{{end}}` 在内的完整块正文。
2. **迭代** `report-data.json` 的 `Entries` 数组中的每个条目。
3. **扩展** 每个条目的块正文，使用以下处理顺序。
4. **替换** 整个匹配（从 `{{range .Entries}}` 到 `</tbody>`）为连接的扩展 HTML，后跟 `</tbody>`。

**每个条目的处理顺序**（从最内层结构开始，以避免 `{{end}}` 混乱）：
1. 评估 `{{if eq .Status ...}}...{{end}}` 条件式（状态徽章 CSS 类和图标）。
2. 评估 `{{if .Checked}}...{{end}}` 条件式（消息复选框）。
3. 扩展 `{{range .Messages}}...{{end}}` 内部范围。
4. 替换简单的 `{{.Field}}` 占位符。

##### 条目字段映射

在范围块正文内，为每个条目替换这些占位符。由于 JSON 键与模板占位符匹配，模板占位符 `{{.X}}` 直接映射到 JSON 键 `X`：

| 模板占位符           | JSON 键 (`Entries[]`)       | 备注                                                        |
|--------------------------------|------------------------------|--------------------------------------------------------------|
| `{{.Line}}`                    | `Line`                       | 直接整数值                                         |
| `{{.IPPrefix}}`                | `IPPrefix`                   | HTML 转义                                                 |
| `{{.CountryCode}}`             | `CountryCode`                | HTML 转义                                                 |
| `{{.RegionCode}}`              | `RegionCode`                 | HTML 转义                                                 |
| `{{.City}}`                    | `City`                       | HTML 转义                                                 |
| `{{.Status}}`                  | `Status`                     | HTML 转义                                                 |
| `{{.HasError}}`                | `HasError`                   | 小写字符串：`"true"` 或 `"false"`                      |
| `{{.HasWarning}}`              | `HasWarning`                 | 小写字符串：`"true"` 或 `"false"`                      |
| `{{.HasSuggestion}}`           | `HasSuggestion`              | 小写字符串：`"true"` 或 `"false"`                      |
| `{{.GeocodingHint}}`           | `GeocodingHint`              | 空字符串 `""`                                            |
| `{{.DoNotGeolocate}}`          | `DoNotGeolocate`             | `"true"` 或 `"false"`                                        |
| `{{.Tunable}}`                 | `Tunable`                    | `"true"` 或 `"false"`                                        |
| `{{.TunedEntry.CountryCode}}`  | `TunedEntry.CountryCode`     | 如果 `TunedEntry` 为空 `{}`，则为 `""`                           |
| `{{.TunedEntry.RegionCode}}`   | `TunedEntry.RegionCode`      | 如果 `TunedEntry` 为空 `{}`，则为 `""`                           |
| `{{.TunedEntry.Name}}`         | `TunedEntry.Name`            | 如果 `TunedEntry` 为空 `{}`，则为 `""`                           |
| `{{.TunedEntry.H3Cells}}`      | `TunedEntry.H3Cells`         | 方括号括起、空格分隔；`"[]"` 如果为空（见格式下方） |
| `{{.TunedEntry.BoundingBox}}`  | `TunedEntry.BoundingBox`     | 方括号括起、空格分隔；`"[]"` 如果为空（见格式下方） |

**`data-h3-cells` 和 `data-bounding-box` 格式：** 这些是**不是 JSON 数组**。它们是方括号括起、空格分隔的值。**不要**使用 JSON 序列化（字符串元素周围没有引号，数字之间没有逗号）。示例：
- `[836752fffffffff 836755fffffffff]` — 正确
- `["836752fffffffff","836755fffffffff"]` — **错误**，引号会破坏解析
- `[-71.70 10.73 -71.52 10.55]` — 正确
- `[]` — 正确

##### 评估状态条件式

**在替换简单的 `{{.Field}}` 占位符之前处理这些**——否则 `{{end}}` 标记会被消耗，正则表达式将无法匹配。

模板使用 `{{if eq .Status "..."}}` 条件式来设置状态徽章的 CSS 类和图标。通过检查条目的 `status` 值并保留匹配的分支文本来评估这些。

状态徽章行包含**两个** `{{if eq .Status ...}}...{{end}}` 块在同一行上——一个用于 CSS 类，一个用于图标。使用 `re.sub` 和回调函数来解决所有出现：

```python
STATUS_CSS = {"ERROR": "error", "WARNING": "warning", "SUGGESTION": "suggestion", "OK": "ok"}
STATUS_ICON = {
    "ERROR": "bi-x-circle-fill",
    "WARNING": "bi-exclamation-triangle-fill",
    "SUGGESTION": "bi-lightbulb-fill",
    "OK": "bi-check-circle-fill",
}
```

def resolve_status_if(match_obj, status):
    """从 {{if eq .Status ...}}...{{end}} 块中挑选匹配 `status` 的分支。"""
    block = match_obj.group(0)
    # 尝试每个分支：{{if eq .Status "X"}}val{{else if ...}}val{{else}}val{{end}}
    for st, val in [("ERROR",), ("WARNING",), ("SUGGESTION",)]:
        # 无需通用解析 — 仅从已知模式映射
    ...
```

更简单的方法：由于恰好有两个已知模式，将它们作为字面字符串替换：
```python
css_class = STATUS_CSS.get(status, "ok")
icon_class = STATUS_ICON.get(status, "bi-check-circle-fill")
body = body.replace(
    '{{if eq .Status "ERROR"}}error{{else if eq .Status "WARNING"}}warning{{else if eq .Status "SUGGESTION"}}suggestion{{else}}ok{{end}}',
    css_class,
)
body = body.replace(
    '{{if eq .Status "ERROR"}}bi-x-circle-fill{{else if eq .Status "WARNING"}}bi-exclamation-triangle-fill{{else if eq .Status "SUGGESTION"}}bi-lightbulb-fill{{else}}bi-check-circle-fill{{end}}',
    icon_class,
)
```
这完全避免了正则表达式，并且是安全的，因为这些确切的字符串在模板中按字面出现。

#### 第 4 步：扩展嵌套消息范围

`{{range .Messages}}...{{end}}` 块包含一个嵌套的 `{{if .Checked}} checked{{else}} disabled{{end}}` 条件，因此其内部的 `{{end}}` 会导致简单的非贪婪正则表达式过早匹配。将正则表达式锚定到 `</td>`（消息范围关闭 `{{end}}` 后立即的标签）以捕获整个块体：

```python
msg_match = re.search(
    r'\{\{range \.Messages\}\}(.*?)\{\{end\}\}\s*(?=</td>)',
    body, re.DOTALL
)
```

前瞻 `(?=</td>)` 确保正则表达式跳过复选框条件的 `{{end}}`（它后面跟着的是 `>` 而不是 `</td>`）并且仅匹配范围关闭的 `{{end}}`（它后面跟着空格然后是 `</td>`）。

对于条目 `Messages` 数组中的每条消息，克隆捕获的块体并展开它：

1. **按每条消息解析复选框条件**（必须发生在简单占位符替换之前以移除嵌套的 `{{end}}`）：
   ```python
   if msg.get("Checked"):
       msg_body = msg_body.replace(
           '{{if .Checked}} checked{{else}} disabled{{end}}', ' checked'
       )
   else:
       msg_body = msg_body.replace(
           '{{if .Checked}} checked{{else}} disabled{{end}}', ' disabled'
       )
   ```

2. **替换消息字段占位符**：

   | 模板占位符 | 源                          | 备注                          |
   |--------------------------|-----------------------------|--------------------------------|
   | `{{.ID}}`                | `Messages[i].ID`            | 直接来自 JSON 的字符串值      |
   | `{{.Text}}`              | `Messages[i].Text`          | HTML 转义                    |

3. **连接**所有展开的消息块，并用结果替换原始的 `{{range .Messages}}...{{end}}` 匹配 (`msg_match.group(0)`)：
   ```python
   body = body[:msg_match.start()] + "".join(expanded_msgs) + body[msg_match.end():]
   ```

如果 `Messages` 为空，用空字符串替换整个匹配区域（没有消息 div — 只有问题标题保留）。

#### 输出保证

- 报告必须在任何现代浏览器中可读，无需额外的网络依赖，除了模板中已有的 CDN 链接（`leaflet`、`h3-js`、`bootstrap-icons`、Raleway 字体）。
- HTML 中嵌入的所有值必须 **HTML 转义** (`<`, `>`, `&`, `"`) 以防止渲染问题。
- `commentMap` 作为直接的 JavaScript 对象字面量嵌入（不在字符串内），因此无需 JS 字符串转义 — 仅输出有效的 JSON。
- 所有值必须仅从分析输出中获取，不能重新计算启发式值。

### 第 6 步：最终审查

在向用户展示结果之前，使用具体、可验证的断言进行最终验证。

**检查 1 — 条目计数完整性**
- 统计原始输入 CSV 中非注释、非空的数据行。
- 断言：`len(entries) in report-data.json == data_row_count`
- 失败时：`行数不匹配：输入有 {N} 数据行，但报告包含 {M} 条目。`

**检查 2 — 摘要计数器完整性**
- 这些计数器基于布尔标志的 **互斥**，这与最高严重性的 `Status` 字段类似。具有 `HasError: true` 和 `HasWarning: true` 的条目仅在 `Errors` 中计数，绝不会在 `Warnings` 中计数。这相当于按条目的 `Status` 字段计数。
- 断言以下所有内容；在生成报告前修正任何失败的项：
  - `Errors == sum(1 for e in Entries if e['HasError'])`
  - `Warnings == sum(1 for e in Entries if e['HasWarning'] and not e['HasError'])`
  - `Suggestions == sum(1 for e in Entries if e['HasSuggestion'] and not e['HasError'] and not e['HasWarning'])`
  - `OK == sum(1 for e in Entries if not e['HasError'] and not e['HasWarning'] and not e['HasSuggestion'])`
  - `Errors + Warnings + Suggestions + OK == TotalEntries - InvalidEntries`

**检查 3 — 准确性桶完整性**
- 断言：`CityLevelAccuracy + RegionLevelAccuracy + CountryLevelAccuracy + DoNotGeolocate == TotalEntries - InvalidEntries`
- **注意**：第 3 阶段中定义的准确性桶说明“不计数具有 `HasError: true` 的条目”，但上述检查 3 公式使用 `TotalEntries - InvalidEntries`（这仍然包括 ERROR 条目）。这意味着 ERROR 条目（那些解析为有效 IP 但验证失败的条目）**按其地理字段存在**计入准确性桶。只有 `InvalidEntries`（无法解析的 IP 前缀）被排除。按检查 3 公式作为权威规则执行。
- 失败时，跟踪并修复桶逻辑。

**检查 4 — 无重复行号**
- 断言 `Entries` 中的所有 `Line` 值都是唯一的。
- 失败时，向用户报告重复的行号。

**检查 5 — TunedEntry 完整性**
- 断言 `Entries` 中的每个对象都有一个 `TunedEntry` 键（即使其值为 `{}`）。
- 失败时，向缺少该键的任何条目添加 `"TunedEntry": {}`，然后重新保存 `report-data.json`。

**检查 6 — 报告文件存在且非空**
- 确认 `./run/report/geofeed-report.html` 已写入且文件大小大于零字节。
- 失败时，在向用户展示前重新生成报告。
