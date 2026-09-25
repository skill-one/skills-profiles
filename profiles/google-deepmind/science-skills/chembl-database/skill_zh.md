# ChEMBL 数据库查询

## 前置条件

1.  **`uv`**: 阅读 `uv` 技能并遵循其设置说明，确保 `uv` 已安装并在 PATH 路径中。
2.  **用户通知**: 如果工作区根目录中不存在 `.licenses/chembl_database_LICENSE.txt`，则 (1) 显著通知用户检查条款，网址为
    https://chembl.gitbook.io/chembl-interface-documentation/about，然后 (2) 创建记录通知文本和时间戳的文件。

## 核心规则

-   [!IMPORTANT] **使用工具脚本**: 您必须始终使用提供的工具脚本 `scripts/chembl_api.py` 进行所有 ChEMBL API 交互，包括检查状态。绝对不要使用 `curl` 或自定义 Python 请求直接查询 ChEMBL API。这确保了速率限制得到执行，并在网络错误时重试。

-   **输出到文件（必需）**: 每个子命令都需要 `--output` 标志。所有 JSON 结果都写入指定文件。运行命令后，使用 jq 或您自己的代码读取输出文件以提取数据。列表结果通常以端点名称为键包裹在 JSON 数组中（例如，`molecules`、`activities`）。

-   **通知**: 如果使用此技能，请确保在输出中提及。

## 工具脚本

所有 ChEMBL API 查询使用一个带有子命令的脚本：

```bash
uv run scripts/chembl_api.py <子命令> --output <文件> [选项]
```

--------------------------------------------------------------------------------

### 1. 检查 API 状态

```bash
uv run scripts/chembl_api.py status --output /tmp/status.json
```

--------------------------------------------------------------------------------

### 2. 分子查询

**按 ChEMBL ID 获取**: `bash uv run scripts/chembl_api.py molecule --id CHEMBL25 --output /tmp/mol.json`

**按名称搜索**: `bash uv run scripts/chembl_api.py molecule --search "aspirin" --limit 3 --output /tmp/mol_search.json`

**批量获取**: `bash uv run scripts/chembl_api.py molecule --ids "CHEMBL25;CHEMBL1642" --limit 10 --output /tmp/mol_batch.json`

**按属性过滤**: `bash uv run scripts/chembl_api.py molecule --filter molecule_properties__mw_freebase__lte=500 --limit 5 --output /tmp/mol_filter.json`

**按范围过滤**: `bash uv run scripts/chembl_api.py molecule --filter molecule_properties__mw_freebase__range=150,200 --limit 5 --output /tmp/mol_range.json`

**下载 SDF 结构文件**: `bash uv run scripts/chembl_api.py molecule --id CHEMBL25 --dl_format sdf --output /tmp/aspirin.sdf`

> **提示**: SDF/MOL 文件可以直接传递给 PyMOL 或 RDKit 等工具进行 3D 可视化和分析。

--------------------------------------------------------------------------------

### 3. 靶点查询

**搜索靶点**: `bash uv run scripts/chembl_api.py target --search "EGFR" --limit 5 --output /tmp/targets.json`

**按 ID 获取**: `bash uv run scripts/chembl_api.py target --id CHEMBL203 --output /tmp/egfr.json`

--------------------------------------------------------------------------------

### 4. 生物活性数据

**按 ID 获取活动**: `bash uv run scripts/chembl_api.py activity --id 31863 --output /tmp/act.json`

**搜索活动**: `bash uv run scripts/chembl_api.py activity --search "EGFR" --limit 5 --output /tmp/act_search.json`

**按靶点过滤活动**: `bash uv run scripts/chembl_api.py activity --filter target_chembl_id=CHEMBL203 standard_type=IC50 --limit 10 --output /tmp/egfr_ic50.json`

**将生物活性单位标准化为 nM**: `bash uv run scripts/chembl_api.py activity --filter target_chembl_id=CHEMBL203 standard_type=IC50 --limit 5 --normalize --output /tmp/egfr_normalized.json`

> **重要**: 生物活性值以各种单位（nM、µM、pM）提供。使用 `--normalize` 将所有值转换为 nM 以进行一致性比较。每条记录将包含 `normalized_value_nM` 和 `normalization_note`。

--------------------------------------------------------------------------------

### 5. 药物信息

**获取药物详情**: `bash uv run scripts/chembl_api.py drug --id CHEMBL25 --output /tmp/drug.json`

**药物适应症**: `bash uv run scripts/chembl_api.py drug_indication --filter molecule_chembl_id=CHEMBL25 --limit 10 --output /tmp/indications.json`

**按分期过滤适应症**: `bash uv run scripts/chembl_api.py drug_indication --filter molecule_chembl_id=CHEMBL25 max_phase_for_ind=4.0 --limit 10 --output /tmp/approved_indications.json`

**药物警告**: `bash uv run scripts/chembl_api.py drug_warning --limit 5 --output /tmp/warnings.json`

**作用机制**: `bash uv run scripts/chembl_api.py mechanism --filter molecule_chembl_id=CHEMBL25 --limit 5 --output /tmp/mech.json`

--------------------------------------------------------------------------------

### 6. 基于结构的搜索

> **注意**: 相似性和子结构搜索都在 ChEMBL 的预索引数据库上执行服务器端。它们不需要本地 RDKit 安装。

**相似性搜索（SMILES + 阈值）**: `bash uv run scripts/chembl_api.py similarity --smiles "CC(=O)Oc1ccccc1C(=O)O" --similarity 85 --limit 5 --output /tmp/similar.json`

**子结构搜索（SMILES）**: `bash uv run scripts/chembl_api.py substructure --smiles "c1ccccc1" --limit 5 --output /tmp/substruct.json`

--------------------------------------------------------------------------------

### 7. 化合物图像

下载 2D 结构图像（默认为 SVG，可缩放用于发表）：

```bash
uv run scripts/chembl_api.py image --id CHEMBL25 --output /tmp/chembl25.svg
```

*选项:*

-   `--dimensions`: 图像大小（像素）（最大 500，默认 500）。
-   `--engine`: 渲染引擎（默认：rdkit）。
-   `--img_format`: 输出格式 — `svg`（默认，矢量）或 `png`（光栅）。

--------------------------------------------------------------------------------

### 8. 与其他数据库交叉引用

ChEMBL 集成了 UniProt、Ensembl、PubChem 等数据库。常见的交叉引用模式：

**从 UniProt 登录号查找 ChEMBL 靶点**: `bash uv run scripts/chembl_api.py target --filter target_components__accession=P00533 --limit 5 --output /tmp/uniprot_target.json`

**解析任何 ChEMBL ID 到其实体类型**: `bash uv run scripts/chembl_api.py chembl_id_lookup --id CHEMBL203 --output /tmp/lookup.json`

**查找交叉引用来源**: `bash uv run scripts/chembl_api.py xref_source --limit 10 --output /tmp/xrefs.json`

> **提示**: 使用 `target_component` 端点查找任何 ChEMBL 靶点的 UniProt 登录号、基因名称和蛋白质序列。

--------------------------------------------------------------------------------

### 9. 分页

所有列表端点支持 `--limit` 和 `--offset` 进行分页：

```bash
# 第一页：从偏移量 0 开始的 2 个结果
uv run scripts/chembl_api.py molecule --limit 2 --offset 0 --output /tmp/page1.json

# 第二页：从偏移量 2 开始的下一个 2 个结果
uv run scripts/chembl_api.py molecule --limit 2 --offset 2 --output /tmp/page2.json
```

响应包括 `page_meta`，其中包含 `total_count`、`limit`、`offset`、`next` 和 `previous` 链接。使用连续的 `--offset` 值分页浏览大量结果集。

--------------------------------------------------------------------------------

### 10. 其他端点

所有剩余端点遵循相同模式：

```bash
uv run scripts/chembl_api.py <子命令> --output <文件> [--id ID | --ids ID1;ID2 | --search QUERY] [--limit N] [--offset N] [--filter KEY=VAL ...]
```

**关键子命令一览**:

-   `molecule`（可搜索：是）：分子/化合物 — 主要入口点
-   `target`（可搜索：是）：药物靶点（蛋白质、生物体等）
-   `activity`（可搜索：是）：生物活性数据（IC50、Ki、EC50 等）
-   `drug`（可搜索：否）：已批准的药物
-   `mechanism`（可搜索：否）：作用机制
-   `assay`（可搜索：是）：实验描述
-   `similarity`（可搜索：否）：相似性搜索（特殊）
-   `substructure`（可搜索：否）：子结构搜索（特殊）
-   `image`（可搜索：否）：化合物图像下载（特殊）

**完整子命令列表**:

-   `activity_supp`（可搜索：否）：补充活动数据
-   `assay_class`（可搜索：否）：实验分类
-   `atc_class`（可搜索：否）：ATC 药物分类
-   `binding_site`（可搜索：否）：结合位点信息
-   `biotherapeutic`（可搜索：否）：生物治疗分子
-   `cell_line`（可搜索：否）：细胞系详情
-   `chembl_id_lookup`（可搜索：是）：ChEMBL ID 解析
-   `chembl_release`（可搜索：否）：数据库发布信息
-   `compound_record`（可搜索：否）：化合物记录
-   `compound_structural_alert`（可搜索：否）：结构警报
-   `document`（可搜索：是）：文献文档
-   `document_similarity`（可搜索：否）：文档相似性
-   `drug_indication`（可搜索：否）：药物适应症
-   `drug_warning`（可搜索：否）：药物安全警告
-   `go_slim`（可搜索：否）：GO 瘦削术语
-   `metabolism`（可搜索：否）：代谢数据
-   `molecule_form`（可搜索：否）：分子形式（盐/母体）
-   `organism`（可搜索：否）：生物体
-   `protein_classification`（可搜索：是）：蛋白质分类
-   `source`（可搜索：否）：数据来源
-   `target_component`（可搜索：否）：靶点蛋白质成分
-   `target_relation`（可搜索：否）：靶点关系
-   `tissue`（可搜索：否）：组织类型
-   `xref_source`（可搜索：否）：交叉引用来源
-   `status`（可搜索：否）：API 状态检查（特殊）

## 常见选项

-   `--output FILE`: **必需**。JSON 结果的输出文件路径。
-   `--id ID`: 按 ID 获取单个记录。
-   `--ids ID1;ID2;...`: 批量获取多个记录。
-   `--search QUERY`: 自由文本搜索（仅适用于可搜索端点，标记 ✓）。
-   `--limit N`: 返回的最大结果数（默认：5）。
-   `--offset N`: 分页偏移量。
-   `--filter KEY=VAL`: 过滤参数（可以指定多个）。
-   `--normalize`:（仅适用于活动）将值标准化为 nM。
-   `--dl_format sdf|mol`:（仅适用于分子）下载结构文件。

## 参考

-   **API 端点参考**: 参考
    [references/api_endpoints.md](references/api_endpoints.md) 获取完整的端点和过滤运算符列表。

## 工作流程

1.  使用 `status --output /tmp/status.json` 验证 API 是否可用。
2.  使用相关子命令搜索靶点、分子或药物。
3.  读取输出 JSON 文件以提取 ID 和数据。
4.  使用搜索结果中的 ID 获取详细记录。
5.  查询 `activity` 并使用过滤器获取靶点/分子的生物活性数据。在跨研究比较值时使用 `--normalize`。
6.  使用 `similarity` 或 `substructure` 进行服务器端基于结构的查询。
7.  使用 `image` 下载化合物图像或使用 `molecule --dl_format sdf` 下载结构文件。
8.  使用 `target --filter target_components__accession=<UniProt>` 与 UniProt 交叉引用。
