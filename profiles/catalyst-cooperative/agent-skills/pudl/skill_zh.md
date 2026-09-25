# PUDL 数据探索指南

本指南面向**数据使用者**，旨在帮助其探索、理解和加载数据解放项目（PUDL）的公共能源数据产品。本指南假设使用者无法访问 PUDL Python 包或源代码库，仅能使用公开分发的数据文件及其元数据。

PUDL 的主要输出是 Apache Parquet 文件，由 Frictionless Data 包描述符描述。对于通用的描述符查询模式（jq），请使用 `datapackage` 技能——本技能在通用技能之上提供了 PUDL 特定的知识。

除了主要的 Parquet 输出外，PUDL 还分发原始的每表 FERC Parquet 数据（涵盖表单 1/2/6/60/714，每个表单都有自己的 `datapackage.json`）以及 FERC EQR（分区 Parquet，与主构建分离）。这些具有不同的访问模式，不由主要的 Frictionless 描述符覆盖——请参阅 [数据访问](./references/data-access.md) 获取完整图景。

## 工作流概述

以下每一步都是低成本的，并且应在与问题相关时默认执行，而不仅限于用户通过名称请求时。

1.  **定位元数据**——主要的 PUDL 描述符（Parquet 输出）位于：

    -   S3: `s3://pudl.catalyst.coop/nightly/pudl_parquet_datapackage.json`
    -   HTTPS: `https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/nightly/pudl_parquet_datapackage.json`

    原始的每表 FERC 数据在每个表单/时代目录中都有自己的 `datapackage.json`，例如 `s3://pudl.catalyst.coop/nightly/ferc1_xbrl/datapackage.json` 和 `s3://pudl.catalyst.coop/nightly/ferc1_dbf/datapackage.json`——请参阅 [原始的每表 Parquet 目录](./references/data-access.md#raw-per-form-parquet-directories) 获取完整列表。

    FERC EQR（电力季度报告）由于其大小而单独分发，并且一次只公开提供一个版本：

    -   S3: `s3://pudl.catalyst.coop/ferceqr/ferceqr_parquet_datapackage.json`
    -   HTTPS: `https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/ferceqr/ferceqr_parquet_datapackage.json`

    对于离线或开发使用，请使用以下命令本地下载所有描述符：

    ```bash
    python scripts/fetch_descriptor.py
    ```

    这将填充 `assets/cache/`。该脚本具有缓存感知功能——比一天年轻的缓存文件会直接重用，无需网络调用，因此每次需要描述符时运行该脚本都是安全的，而不是先自行检查 `assets/cache/`。传递 `--force` 以绕过缓存并忽略年龄（例如，如果您怀疑 PUDL 的架构今天发生了变化，需要最新的副本）。

    原始输入存档（用于可追溯性）位于 `s3://pudl.catalyst.coop/zenodo/<dataset>/<concrete-doi>/datapackage.json`。对于原始元数据和文件访问，请优先使用缓存的 S3 存档，而不是 Zenodo 网站或 API。源文档页面通常为整个数据集谱系提供概念 DOI；S3 路径使用具体 DOI 指向一个特定的存档版本。请参阅 [数据质量和背景](./references/data-quality-and-context.md) 获取详细信息。

1.  **选择性地查询元数据**——使用 `/datapackage` 技能模式（jq）查找相关表格、读取描述并显示警告。

    对于“PUDL 是否有关于 X 的数据”的问题，不要在您已经通过声誉认定的匹配项上停止——首先在相关的描述/代码字段中运行更广泛的键词搜索（对于 FERC 账户，请参阅 [交叉引用 FERC 表单 1 和表单 2 的表单和账户](#cross-referencing-ferc-form-1-and-form-2-schedules-and-accounts)；对其他来源的 `core_*__codes_*` 表也适用相同的习惯）。如果答案来自回忆知识而不是搜索，请标记它。

1.  **当元数据无法完全解释某些内容时，查阅原始表单和说明**——不要等待用户通过名称请求这些内容。请参阅 [数据源：空白表单和申报人说明](./references/data-sources.md#blank-forms-and-filer-instructions)。

1.  **检查表格级别**——请参阅 [数据质量和背景](./references/data-quality-and-context.md)。优先选择 `out_*` 表；警告用户关于 `_core_*` 表。

1.  **在连接表格前检查键**——如果任务将 FERC 源表格与 EIA 源表格（或任何两个表格）组合，请首先检查每个 `schema.foreignKeys`，并通过 `utility_id_pudl` / `plant_id_pudl` 路由公用事业/工厂连接，而不是通过名称字符串匹配。请参阅 [PUDL Datapackage 扩展：连接 PUDL 表格](./references/metadata-and-querying.md#joining-pudl-tables-use-declared-foreign-keys-and-pudls-id-crosswalks)。

1.  **在实现细节之前检查方法**——如果用户询问 PUDL 如何清理、插补、分配、协调、估计或建模数据，请先阅读 [方法](./references/methodology.md)，然后获取相关的公共方法页面（将 `.md` 添加到 URL 以供您自己阅读——但在指向用户时，请给他们 `.html` 链接），然后再查看源代码、docstrings 或实现细节。总结公共方法页面并指向它。只有在用户看过该摘要或该主题不存在公共方法页面时，才深入代码级别的实现。

1.  **高效地加载数据**——加载数据不必意味着下载整个表格。DuckDB 中的 `SELECT ... LIMIT`、polars 中的 `pl.scan_parquet()`（在 `.collect()` 之前使用 `.select()`/.`.filter()`）以及 pandas 中的 `columns=` 参数都将选择下推到 Parquet 读取器本身。将采样和下选择视为探索表格的正常方式，而不是当文件被证明很大时才保留的优化。您应该在完全无过滤加载之前估计表格的大小，并且只有当工作确实需要每一行时才加载整个表格；请参阅 [数据访问](./references/data-access.md) 获取加载模式本身。

## 参考索引

-   [数据源](./references/data-sources.md) ——如何查询 PUDL 描述符自身的 `sources` 数组（31 个数据集，具有简短代码、名称、许可和每个来源的文档链接），以及在哪里找到并阅读每个来源的空白表单和申报人说明；当用户询问特定的来源数据集（EIA-860、FERC 表单 714、EPA CEMS 等）或需要文档链接、在解析原始存档 S3 路径时您需要简短代码并且必须区分概念 DOI 和具体 DOI，或每当解释列、代码或表单实际含义时。
-   [数据访问](./references/data-access.md) ——S3 路径、加载模式（pandas/DuckDB/polars/纯 SQL）、原始的每表 FERC Parquet 位置和 EQR 访问；每当生成数据加载代码或解释如何访问任何 PUDL 输出时。
-   [PUDL Datapackage 扩展](./references/metadata-and-querying.md) ——PUDL 对标准 datapackage schema 的特定扩展：RST/docstring 格式的描述、每个资源的可追溯性字段、包级单位注册表，以及如何通过 `utility_id_pudl`/`plant_id_pudl` 跨 FERC/EIA ID 系统连接表格；在查询 PUDL 描述符上的 `description` 或其他非标准字段之前，以及在连接任何两个 PUDL 表格之前阅读，使用 `datapackage` 技能而不是通用的描述符查询机制。
-   [数据质量和背景](./references/data-quality-and-context.md) ——表格级别命名约定（`out_*` vs `core_*` vs 原始）、警告类型以及每个级别对分析可靠性的含义；当用户询问数据质量、在选择表格级别时，或在提供加载代码之前显示警告时。
-   [方法](./references/methodology.md) ——PUDL 数据处理和建模方法页面索引（实体解析、时间序列插补、所有权提取）；当用户询问 PUDL 如何清理、协调、插补、分配、估计或建模数据时。获取特定的公共方法页面，总结它，并指向它，然后再从代码或 docstrings 深入实现细节。
-   [FERC 电力账户](./references/ferc-electricity-accounts.md) ——FERC 电力公用事业账户的完整分层图（资产负债表、电力工厂、运营收入、O&M 费用），包括账户编号和描述；当解释 FERC 表单 1 财务数据或用户询问特定账户编号的含义时——优先查询 `ferc_electricity_accounts.json` 而不是阅读此文件。
-   [FERC 表单 1 表单](./references/ferc1-schedules.md) ——所有 75 个表单 1 表单，包括标题、描述和表格映射；当用户通过编号或名称引用表单（例如，“表单 301”、“第 400a 页”、“服务中的工厂表单”）时——优先查询 `ferc1_schedules.json` 而不是阅读此文件。
-   [ferc1_schedules.json](./assets/ferc1_schedules.json) ——**首先查询此文件**以获取任何 FERC 表单 1 表单或表格查找；使用 jq 通过关键词、账户编号或 PUDL 表格名称查找表单，而无需将完整的 markdown 加载到上下文中。
-   [FERC 表单 2 表单](./references/ferc2-schedules.md) ——所有 77 个表单 2 表单，包括标题、描述和 XBRL 表格映射（表单 2 尚未集成到 PUDL 中）；当用户引用表单 2 表单或询问天然气管道财务或运营数据时——优先查询 `ferc2_schedules.json` 而不是阅读此文件。
-   [ferc2_schedules.json](./assets/ferc2_schedules.json) ——**首先查询此文件**以获取任何 FERC 表单 2 表单或表格查找；使用 jq 通过关键词、账户编号或 XBRL 表格名称查找表单，而无需将完整的 markdown 加载到上下文中。
-   [ferc_electricity_accounts.json](./assets/ferc_electricity_accounts.json) ——**首先查询此文件**以获取任何 FERC 表单 1（电力公用事业）账户编号查找；使用 jq 解析账户定义并通过 `ferc_accounts` 数组与表单 1 表单交叉引用。

## PUDL 特定约束

-   **许可**：所有 PUDL 数据均在 [知识共享署名 4.0 国际许可协议](https://creativecommons.org/licenses/by/4.0/) 下发布。用户可以自由使用、共享和适应数据，但需注明来自 Catalyst Cooperative。

-   **引用**：当用户询问如何引用 PUDL 时，请提供此参考：

    > Selvans, Z., Gosnell, C., Sharpe, A., Schira, Z., Lamb, K., Belfer, E., Xia, D.,
    > & Mazaitis, K. *公共事业数据解放 (PUDL) 项目* [数据集].
    > Catalyst Cooperative. <https://doi.org/10.5281/zenodo.3653158>

    BibTeX:

    ```bibtex
    @misc{pudl,
      author       = {Selvans, Zane and Gosnell, Christina and Sharpe, Austen and
                      Schira, Zachary and Lamb, Katherine and Belfer, Ella and
                      Xia, Dazhong and Mazaitis, Kathryn},
      title        = {The Public Utility Data Liberation (PUDL) Project},
      publisher    = {Catalyst Cooperative},
      doi          = {10.5281/zenodo.3653158},
      url          = {https://doi.org/10.5281/zenodo.3653158},
    }
    ```

-   S3 存储桶 `s3://pudl.catalyst.coop` 是**免费且公开可访问的**——无需 AWS 凭据，并且任何环境凭据（即使无效）也应明确绕过，而不是假设不存在。

-   **DuckDB、pandas 和 polars 每个都需要显式设置以可靠地查询此存储桶**——请参阅
    [数据访问：DuckDB 和 S3](./references/data-access.md#duckdb-and-s3-required-setup)
    (`s3_url_style` 加上清除 S3 凭据设置；通过 `/query` 也适用）以及 pandas/polars 部分下方的原因，为什么每个都需要。

-   **核心 PUDL 输出表格的 Parquet 路径是**
    `s3://pudl.catalyst.coop/nightly/<table_name>.parquet`。原始的每表 FERC 表格使用不同的路径——请参阅
    [原始的每表 Parquet 目录](./references/data-access.md#raw-per-form-parquet-directories)。

-   **在提供加载代码之前，始终显示来自描述符的用法警告**。

-   **方法优先规则**：如果用户询问的主题存在公共方法页面，请在检查实现细节之前使用它。代码级别的解释是后续步骤，而不是默认的第一响应。

-   **优先选择 `out_*` 表**用于分析师工作。如果用户询问一个主题但没有指定表格，请首先在元数据中搜索 `out_` 表。

-   **使用 `uv` 安装 Python 包**——优先选择 `uv add <package>` 而不是 `pip install <package>`。`uv` 更快，并且将安装到虚拟环境中而不是全局环境中。仅在 `uv` 不可用时（`command -v uv` 返回空）才回退到 `pip`——如果这样做，请安装到项目本地虚拟环境中（如果不存在，则使用 `python -m venv .venv` 创建一个），而不是系统/全局 Python。**`pip install --user` 也不是安全的回退**——它仍然会写入用户的全局用户站点包，跨越机器上的每个其他项目共享，而不是将更改限制于此任务。如果工作目录已经有自己的环境管理器（pixi、poetry、现有的 venv 或 conda 环境），请通过该管理器安装，而不是引入第二个。

-   **PUDL 的 datapackage 描述符以 PUDL 特定方式扩展了标准架构**：RST 格式的、docstring 风格的描述、每个资源的可追溯性元数据，以及包级单位注册表。在编写针对 `description` 或其他非标准字段的 jq 查询之前，请阅读
    [PUDL Datapackage 扩展](./references/metadata-and-querying.md)——它仅涵盖 PUDL 独有的内容；对于通用的描述符查询机制，请使用 `datapackage` 技能。

-   **优先选择在 ID 列上连接 PUDL 表格，而不是名称字符串列**
    (`utility_name_ferc1`, `utility_name_eia`, 工厂名称等.)——跨 FERC 和 EIA 的同名称实体不一定代表同一家公司。通过 `core_pudl__assn_*` 跨表路由连接，首先检查 `schema.foreignKeys`。名称匹配是一种合法的回退，当没有 ID 跨表时，但将其结果视为未经验证，直到进行核实。请参阅
    [PUDL Datapackage 扩展：连接 PUDL 表格](./references/metadata-and-querying.md#joining-pudl-tables-use-declared-foreign-keys-and-pudls-id-crosswalks)。

### 交叉引用 FERC 表单 1 和表单 2 的表单和账户

`ferc1_schedules.json` 和 `ferc2_schedules.json` 共享相同的架构。每条记录都有一个 `ferc_accounts` 数组，其中包含表单引用的账户编号，预先提取以供直接查找。使用 `description` 进行主题关键词搜索；使用 `ferc_accounts` 进行账户编号交叉引用。

**快速查找模式 (jq):**

```bash
# 查找所有引用特定账户编号的表单 1 表单
jq '[.[] | select(.ferc_accounts[] == "182.3")] | .[] | {schedule, title}' \
    assets/ferc1_schedules.json

# 查找所有引用特定账户编号的表单 2 表单
jq '[.[] | select(.ferc_accounts[] == "489.2")] | .[] | {schedule, title}' \
    assets/ferc2_schedules.json

# 获取特定表单 1 表单的所有账户定义
SCHED="232"
jq --arg s "$SCHED" '.[] | select(.schedule == $s) | .ferc_accounts[]' \
    assets/ferc1_schedules.json |
xargs -I{} jq --arg a {} '.[] | select(.account == $a)' assets/ferc_electricity_accounts.json
```

**跨文件连接 (jq):** 使用 `--slurpfile` 加载账户文件并使用 `INDEX()` 构建账户编号查找，然后将其与每个表单的 `ferc_accounts` 数组连接：

```bash
# 查找 PUDL 表格和账户定义以获取表单 1 主题（例如，“监管资产”）
jq --slurpfile accounts assets/ferc_electricity_accounts.json '
  ($accounts[0] | INDEX(.account)) as $acct_lookup
  | .[]
  | select(.description | test("regulatory asset"; "i"))
  | .schedule as $sched | .title as $title | .pudl_tables as $tables
  | .ferc_accounts[]
  | {schedule: $sched, title: $title, pudl_tables: $tables,
     account: ., account_description: $acct_lookup[.].description}
' assets/ferc1_schedules.json

# 查找主题的表单 2 XBRL 表格（例如，“存储”）——单个文件，无需连接
jq '[.[] | select(.description | test("storage"; "i"))] |
    .[] | {schedule, title, xbrl_tables}' assets/ferc2_schedules.json
```

## 委托

| 用户意图                        | 转交至    |
| ---------------------------------- | -------------- |
| 查询 datapackage.json 元数据    | `/datapackage` |
| 运行 SQL 或 NL 查询对数据进行操作 | `/query`       |
