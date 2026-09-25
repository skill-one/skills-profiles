# openFDA 搜索和查询

## 前置条件

1.  **`uv`**: 阅读 `uv` 技能并遵循其安装说明，确保 `uv` 已安装并在 PATH 中。
2.  **用户通知**: 如果工作区根目录中不存在 `.licenses/openfda_database_LICENSE.txt`，则 (1) 显著通知用户检查 https://open.fda.gov/apis/ 和 https://open.fda.gov/license 上的条款，然后 (2) 创建记录通知文本和时间戳的文件。
3.  **`.env` 文件**: 确保您的家目录中存在 `.env` 文件。如果不存在，请创建一个。
4.  **`FDA_API_KEY`** (可选但推荐): 将每日请求限制从 1,000 提高到 120,000。该技能无需它也能工作，但代理很容易在一次会话中耗尽无密钥限制。您可以在 https://open.fda.gov/apis/authentication/ 注册一个免费密钥。如果此技能与用户的请求相关，您 **必须** 在 `credentials` 技能中使用安全凭证协议来检查并请求此密钥。

## 核心规则

-   **使用包装器**: 始终执行提供的辅助脚本来查询数据库，而不是直接访问数据库。脚本会自动优雅地执行所需的速率限制。

-   **速率限制**: 尊重 openFDA 速率限制。无 API 密钥: 每分钟 240 个请求，每天每个 IP 1,000 个请求。有 API 密钥: 每分钟 240 个请求，每天每个密钥 120,000 个请求。在运行多查询工作流之前，始终设置 API 密钥。

> **警告**: 自动代理很容易在一次研究会话中耗尽 1,000 请求的每日限制。在运行多查询工作流之前，始终设置 API 密钥。

> 如果此技能与用户的请求相关，您 **必须** 在 `credentials` 技能中使用安全凭证协议帮助用户将 `FDA_API_KEY` 添加到他们的 `.env` 文件中。如果检测不到 API 密钥，脚本将在标准错误输出中发出警告。

-   **始终使用 `--output`**: 所有子命令都需要 `--output <file>` 将结果写入文件。这可以防止大型输出变得令人不知所措。使用 jq 或代码读取输出文件。

-   **通知**: 如果使用此技能，请确保在输出中提及。

## 实用脚本

**所有操作的单一脚本:**

```bash
uv run scripts/openfda_query.py {search,count,download} --output <file> [options]
```

### 1. 搜索

搜索 28 个端点中的任何端点，并将 JSON 结果保存到文件。

```bash
uv run scripts/openfda_query.py search \
  --category drug --endpoint event \
  --search "patient.drug.medicinalproduct:aspirin" \
  --limit 5 --output /tmp/fda_results.json
```

标准输出打印紧凑的摘要：

```json
{"status": "success", "output": "/tmp/fda_results.json", "results_in_file": 5, "total_matching": 601477}
```

*选项:*

-   `--output`: 完整 JSON 结果的输出文件（必需）。
-   `--category`: API 类别 — `drug`（药物）、`device`（设备）、`food`（食品）、`tobacco`（烟草）、`other`（其他）、`animalandveterinary`（动物和兽医）、`cosmetic`（化妆品）、`transparency`（透明度）。
-   `--endpoint`: 类别内的端点（例如，`event`、`label`、`510k`）。有关完整列表，请参阅 [references/api_endpoints.md](references/api_endpoints.md)。
-   `--search`: 查询字符串（例如，
    `patient.drug.medicinalproduct:aspirin+AND+serious:1`）。
-   `--sort`: 排序字段和顺序（例如，`receivedate:desc`）。
-   `--limit`: 最大结果（默认 10，最大 1000）。
-   `--skip`: 分页偏移（默认 0）。
-   `--api_key`: API 密钥（也读取 `FDA_API_KEY` 环境变量）。

### 2. 计算

计算匹配结果中字段的唯一值。

```bash
uv run scripts/openfda_query.py count \
  --category drug --endpoint event \
  --search "patient.drug.medicinalproduct:aspirin" \
  --count_field "patient.reaction.reactionmeddrapt.exact" \
  --summary 10 --output /tmp/aspirin_reactions.json
```

标准输出打印包含前 5 个术语的摘要。完整数据在输出文件中。

*附加选项:*

-   `--count_field`: 要计数的字段（追加 `.exact` 用于短语计数）。
-   `--summary N`: 仅返回最频繁的前 N 个术语。使用此选项以避免用数百个不频繁的术语淹没上下文。

### 3. 下载

将多页结果下载到文件。

```bash
uv run scripts/openfda_query.py download \
  --category drug --endpoint event \
  --search "patient.drug.medicinalproduct:aspirin" \
  --limit 100 --max_pages 5 \
  --output /tmp/aspirin_events.json
```

*附加选项:*

-   `--max_pages`: 最大获取页数（默认 10）。
-   `--all_results`: 自动分页以获取所有匹配结果。安全上限为每个下载最多 25,000 条记录，以防止失控下载和过度 API 使用。

    > **提示**: 常见药物可能有过多的报告。使用日期范围（例如，
    > `receivedate:[20250101+TO+20250131]`）来限制下载量。

## 实体解析：使用 `.exact` 获取精确匹配

在搜索特定产品名称、药物名称或分类术语时，始终在字段上使用 `.exact` 后缀以获取精确匹配结果。如果没有它，API 会将多词值分词并返回嘈杂的部分匹配。

```bash
# 精确匹配: 仅匹配 "ADVIL"
uv run scripts/openfda_query.py search --category drug --endpoint label \
  --search 'openfda.brand_name.exact:"ADVIL"' \
  --limit 5 --output /tmp/advil_label.json
```

> **注意**: FDA 数据库中的许多品牌名称包括变体后缀（例如，
> "TYLENOL Extra Strength" 而不是仅 "TYLENOL"）。如果 `.exact` 搜索返回 0 结果，请尝试不使用 `.exact` 以查看可用的品牌名称变体，然后使用完整的精确名称重新查询。

`.exact` 后缀在使用 `--count_field` 聚合短语而不是单个单词时也是必需的。

## NDC 查询：连字符和已停产药物

1.  **始终引用连字符 NDC**: 在 openFDA 搜索语法中，未引用的连字符（`-`）充当布尔 **NOT** 操作符（例如，`51285-092` 搜索 `51285 AND NOT 092`）。始终用转义双引号将连字符 NDC 字符串括起来：

    ```bash
    uv run scripts/openfda_query.py search --category drug --endpoint ndc \
      --search 'product_ndc:"51285-092"' \
      --limit 5 --output /tmp/ndc.json
    ```
2.  **已停产药物的回退 (`drug/label`)**: `drug/ndc` 端点仅包含 **当前活跃/上市** 的产品。如果有效的 NDC 在 `drug/ndc` 中返回 0 结果，请使用精确短语引号查询 `drug/label` 端点（`--search '"51285-092"'`）。请注意，对于已停产的药物，`openfda` 元数据块可能为空（`{}`），因此请从标签文本字段 (`package_label_principal_display_panel`、`description` 或 `spl_product_data_elements`) 读取品牌名称、活性成分和标签者。

## MedDRA 术语解析

openFDA 不良事件数据使用 MedDRA（监管活动医学词典）术语来表示反应。API 报告 **首选术语 (PTs)**，但不会提供 MedDRA 层次结构（系统器官类别、高级术语等）。

> **注意**: MedDRA 是一种专有本体，在 EMBL-EBI OLS 中 **未索引**。要近似 MedDRA 层次结构查询，请使用 **人类表型本体 (HP)** 或 **NCI 词典 (NCIT)** 作为代理本体——它们交叉引用 MedDRA ID 并提供父/祖先关系。

```bash
# 第 1 步: 从 openFDA 获取顶级反应
uv run scripts/openfda_query.py count \
  --category drug --endpoint event \
  --search "patient.drug.medicinalproduct:metformin" \
  --count_field "patient.reaction.reactionmeddrapt.exact" \
  --summary 5 --output /tmp/metformin_reactions.json

# 第 2 步: 使用生物医学本体服务技能（例如 embl-ebi-ols 技能）查找顶级反应术语
# MedDRA 在 OLS 中不可用；使用人类表型本体 (HP) 或 NCI 词典 (NCIT) 作为代理来查找反应术语的层次分类。
```

## 可用端点 (共 28 个)

类别到端点的映射:

-   `drug`: event（事件）、label（标签）、ndc（NDC）、enforcement（执法）、drugsfda（药物 FDA）、shortages（短缺）
-   `device`: 510k（510k）、classification（分类）、enforcement（执法）、event（事件）、pma（PMA）、recall（召回）、registrationlisting（注册列表）、udi（UDI）、covid19serology（COVID-19 血清学）
-   `food`: enforcement（执法）、event（事件）
-   `tobacco`: problem（问题）、researchpreventionads（研究预防广告）、researchdigitalads（研究数字广告）、researchsmokefree（研究无烟）
-   `other`: historicaldocument（历史文档）、nsde（NSDE）、substance（物质）、unii（UNII）
-   `animalandveterinary`: event（事件）
-   `cosmetic`: event（事件）
-   `transparency`: crl（CRL）

## 参考

-   **查询语法和所有端点**: 有关字段名称、搜索语法、日期范围和布尔操作符，请参阅 [references/api_endpoints.md](references/api_endpoints.md)。

## 配方

药物、设备、食品、烟草、化妆品、动物和兽医产品、物质、透明度数据、不良事件、召回、标签、批准、短缺、510(k) 清除、NDC 查询、任何 FDA 安全或监管数据查询等常见查询模式。有关完整配方，请参阅 [references/recipes.md](references/recipes.md)。

## 工作流

1.  使用 `search` 和 `--output` 搜索记录。读取输出文件。
2.  使用 `count` 和 `--summary 10 --output` 总结字段分布。
3.  使用 `download`（使用 `--all_results` 进行彻底拉取）以获取更大的数据集。
4.  使用标准工具读取和分析输出文件。
5.  对于 MedDRA 术语层次结构问题，使用生物医学本体服务技能（例如 EMBL-EBI OLS 技能与 HP 或 NCIT 本体）来查找术语。
