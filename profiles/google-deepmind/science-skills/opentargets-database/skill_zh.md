# Open Targets Database 技能

## 概述

该技能提供对 Open Targets 平台 GraphQL API 的访问。它聚合了来自遗传学（GWAS/eQTL）、通路、动物模型和临床试验的多模态证据，以对靶点-疾病关联进行排名并识别可药物基因。

## 前置条件

1.  **`uv`**：阅读 `uv` 技能并遵循其设置说明，确保已安装 `uv` 并将其添加到 PATH 环境变量中。
2.  **用户通知**：如果工作区根目录中不存在 `.licenses/opentargets_database_LICENSE.txt` 文件，则（1）向用户显著通知其检查 https://platform-docs.opentargets.org/licence 上的条款，然后（2）创建记录通知文本和时间戳的文件。

## 核心规则

-   **使用包装器**：始终使用提供的辅助脚本来查询数据库，而不是直接访问数据库。脚本会自动执行公平使用策略并实现重试逻辑。
-   **输出标志**：始终需要 `--output` 标志，因为输出可能非常大。使用 `jq` 或编写自己的代码来处理此 JSON 文件。
-   **通知**：如果使用此技能，请确保在输出中提及。

## 快速参考

始终使用提供的 Python 脚本 `scripts/query_opentargets.py` 快速查询数据库。它处理 API 通信、重试、格式化和自动截断过大的响应。绝对不要编写自己的 curl 或类似请求。

**用法：**

```bash
uv run scripts/query_opentargets.py --output /tmp/opentargets_results.json [OPTIONS] COMMAND [ARGS]...
```

**常用选项：**

-   `--output PATH`：**必需**。写入 JSON 输出文件的路径。
-   `--limit N`：限制数组中返回的项目数量（默认为 50）。在初步探索时使用较小的数字，如 10。
-   `--page-size N`：设置 API 分页大小（默认为 200）。如果需要更多结果（例如，包含许多可信集的研究），请增加。

**可用命令：**

-   **`get-gwas-studies`** *`disease_id`*：获取与特定疾病 ID（例如 `MONDO_0008383` 对应的类风湿性关节炎）相关的所有 GWAS 研究。
-   **`get-study-credible-sets`** *`study_id`*：获取给定研究 ID（例如 `FINNGEN_R12_RX_CROHN_2NDLINE`）的所有可信集。返回置信度、精细映射方法、变异体和 p 值信息。
-   **`get-qtl-credible-sets`** *`variant_id`*：检索特定变异体 ID（例如 `19_44908822_C_T`）的 QTL 可信集。
-   **`get-l2g`** *`variant_id [--study-id ID]`*：返回 Locus-to-Gene (L2G) 预测/评分，以识别最可能的因果基因。仅需要 `variant_id`；使用 `--study-id` 可筛选到特定研究。接受 `chr` 前缀（例如 `chr1_113834946_A_G`）。
-   **`get-target-druggability`** *`ensembl_id`*：为基因/靶点提供可及性数据（小分子、抗体等）和临床试验安全性信息。
-   **`get-associated-targets`** *`disease_id`*：查找与特定疾病 ID（EFO 或 MONDO）关联的所有靶点基因。
-   **`get-disease-drugs`** *`disease_id [--min-stage STAGE]`*：查找与疾病关联的所有药物和临床候选药物。使用 `--min-stage` 进行筛选（例如 `PHASE_3` 对应 III 期或已获批）。
-   **`get-associated-diseases`** *`ensembl_id`*：查找与特定靶点 Ensembl ID 关联的所有疾病。
-   **`search-disease`** *`query_string`*：通过名称搜索疾病，以找到其 ID 和其他元数据。
-   **`get-credible-sets-near-target`** *`ensembl_id [--window N]`*：获取靶点的可信集，并筛选出靶点周围基因组窗口内的可信集。用于查找基因附近的变异体。
-   **`custom-query`** *`query [--variables '{}']`*：运行原始 GraphQL 查询以获取任何其他 Open Targets 数据。

## L2G 查询用法

`get-l2g` 命令有两种模式：

*   **仅变异体** (`get-l2g <variant_id>`)：返回所有研究中该变异体作为主要变异体的可信集的 L2G 预测。这可能返回大量结果（例如数百个）。当用户想要了解基因在某个位点最可能的因果性，或未提及特定研究时使用此模式。
*   **变异体 + 研究** (`get-l2g <variant_id> --study-id <study_id>`)：仅返回来自特定研究的可信集的 L2G 预测。当用户询问特定 GWAS 研究或需要缩小结果范围时使用此模式。

> **不完整结果警告**：仅变异体模式可能返回数百个可信集。默认的 `--page-size` 为 200，如果 API 报告的 `count` 高于返回的 `rows` 数量，**您看到的是不完整的结果**。始终比较 `count` 与实际行数。如果它们不同，请增加 `--page-size` 或告知用户仅检索了部分结果。

## 按区域查询

要查找基因附近的变异体相关的研究，请使用 `get-credible-sets-near-target`，它通过基于基因组位置的灵活搜索改进了基础 API：`uv run scripts/query_opentargets.py --output /tmp/results.json get-credible-sets-near-target ENSG00000156515 --window 500000`

注意 Open Targets GraphQL 模式为 `credibleSets` 包含 `regions` 参数，但它对预计算的区域字符串（例如 `chr10:68769984-69903496`）执行精确匹配，并且存在一些缺失数据。使用 `get-credible-sets-near-target`，因为它允许基因组范围重叠搜索。

这会获取与靶点相关的可信集，并在 Python 中根据变异体的基因组位置进行筛选。

## 高级 GraphQL 查询

如果您需要查询内置子命令未暴露的端点或字段，请使用 `custom-query` 子命令。

**在编写自定义查询之前**：阅读参考文档以了解 API 模式、类型并查看示例查询。参见 [references/OpenTargets_GraphQL_Guide.md](references/OpenTargets_GraphQL_Guide) 获取完整模式细节、端点和示例。

**示例：查找疾病的药物**

```bash
uv run scripts/query_opentargets.py custom-query \
  query drugsForDisease($id: String!) {
    disease(efoId: $id) {
      name
      drugAndClinicalCandidates {
        count
        rows {
          maxClinicalStage
          drug {
            id
            name
          }
        }
      }
    }
  }' \
--variables '{"id": "EFO_1001006"}'
--output '/tmp/opentargets_result.json'
```

## 置信度星级评分

Open Targets 平台根据精细映射方法和质量检查为每个可信集分配一个**置信度级别**。这些对应于平台 UI 中显示的星级评分：

| 星级          | 置信度字符串（API 值）                             |
| -------------- | --------------------------------------------------------- |
| ★★★★ (4 星) | `SuSiE 精细映射的可信集，具有样本内 LD`        |
| ★★★ (3 星)  | `SuSiE 精细映射的可信集，具有样本外 LD`    |
| ★★ (2 星)   | `PICS 精细映射的可信集，从汇总统计数据中提取     |
:                : `                                               |
| ★ (1 星)     | `PICS 精细映射的可信集，基于报告的顶部命中` |
| 无            | `未知置信度`                                      |

当用户询问“N 星置信度”时，请将他们的请求与 API 响应中 `confidence` 字段的相应字符串匹配。

## 小贴士和常见错误

-   **ID 格式**：
    -   疾病 ID 通常是 MONDO ID（例如 `MONDO_0008383` 对应类风湿性关节炎）或 EFO ID（例如 `EFO_0009460`）。使用 `search-disease` 命令查找正确的 ID。
    -   靶点 ID 必须是 Ensembl ID（例如 `ENSG00000169083`），而不是 HGNC 符号。如果您只有基因符号，可能需要使用自定义 GraphQL `search` 查询将其映射。
    -   变异体 ID 的格式为 `染色体位置参考变异体`（例如 `1_154426264_C_T`）。工具会自动去除 `chr` 前缀（例如 `chr1_154426264_C_T`）。
    -   研究ID可以是 GWAS 目录ID（例如 `GCST90204201`）或项目特定ID（例如 `FINNGEN_R12_RX_CROHN_2NDLINE`）。
-   **截断**：工具会截断超过 `--limit` 的数组以保护上下文窗口。如果您看到 `"_truncated"`，如果确实需要更多数据，可以再次运行查询并使用更高的限制，但请谨慎使用较大的限制值。始终使用 `--output` 标志将结果保存到文件，以避免终端输出截断。
-   **分页和不完整结果**：`--page-size` 选项（默认：200）控制从 API 获取的项目数量。**始终检查响应中的 `count` 字段，并将其与实际返回的 `rows` 数量进行比较。** 如果 `count` > 行数，则您有不完整的数据——要么增加 `--page-size` 以获取更多数据，要么告知用户只返回了部分结果集。这对于没有 `--study-id` 的 `get-l2g` 尤其重要，它可能返回数百个可信集。
