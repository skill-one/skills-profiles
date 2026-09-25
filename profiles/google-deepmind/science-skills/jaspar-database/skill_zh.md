# JASPAR 技能

JASPAR 是转录因子（TF）结合谱的权威开放获取数据库，以位置频率矩阵（PFM）的形式存储。

使用此技能将抽象序列基序或基因组区域映射到特定的生物调节因子（例如，“此处结合哪些 TF？”或“CTCF 的基序是什么？”）。

## 前置条件

1.  **`uv`**：阅读 `uv` 技能并遵循其设置说明，确保 `uv` 已安装并在 PATH 中。
2.  **用户通知**：如果工作区根目录中不存在 `.licenses/jaspar_database_LICENSE.txt`，则（1）显著通知用户检查 https://jaspar.elixir.no/ 和 https://jaspar.elixir.no/api/ 上的条款，然后（2）创建记录通知文本和时间戳的文件。

## 核心规则

**关键**：你必须遵守 JASPAR API 使用条款，并遵循以下规定：

-   **使用包装器**：始终使用提供的辅助脚本查询数据库，而不是直接访问数据库。脚本会自动优雅地执行所需的速率限制。
-   **最大 API 窗口大小**：单个 API 查询的基因组窗口大小不得超过 100,000 bp（100kb）。`jaspar_api.py` 脚本会自动将较大的请求分块，以便在查询较大区域时绕过此限制。
-   **有效的矩阵 ID**：`get_tf_motif`、`get_tf_metadata` 和 `get_tf_pwm` 需要 JASPAR 矩阵 ID（例如，`MA0488.2`）。如果用户提供基因符号（例如，`JUN`），你必须首先使用 `resolve_tf_id` 解析它。
-   **分类学要求**：解析 ID 需要一个 `tax_id` 以确保目标搜索。常见 ID：人类=9606，小鼠=10090。
-   **通知**：如果使用此技能，请确保在输出中提及。

## 实用脚本

使用捆绑的 Python 脚本运行所有命令：

### 1. 解析 TF 到矩阵 ID

将转录因子名称映射到稳定的矩阵 ID。如果仅提供基因名称，则在获取基序之前是必需步骤。

```bash
uv run scripts/jaspar_api.py resolve_tf_id --name "JUN" --tax-id 9606
```

### 2. 获取 TF 基序（PFM）

检索特定 TF 的原始位置频率矩阵。支持 `--format` 标志。

```bash
uv run scripts/jaspar_api.py get_tf_motif --matrix-id "MA0488.2"
uv run scripts/jaspar_api.py get_tf_motif --matrix-id "MA0488.2" --format meme
```

### 3. 获取 TF 元数据

检索 TF 类别、家族以及指向外部数据库（例如，UniProt）的链接。支持 `--format` 标志。

```bash
uv run scripts/jaspar_api.py get_tf_metadata --matrix-id "MA0488.2"
uv run scripts/jaspar_api.py get_tf_metadata --matrix-id "MA0488.2" --format yaml
```

### 4. 计算 PWM（位置权重矩阵）

获取矩阵的 PFM 并将其转换为对数优势分数（PWM）。

```bash
uv run scripts/jaspar_api.py get_tf_pwm --matrix-id "MA0488.2"
uv run scripts/jaspar_api.py get_tf_pwm --matrix-id "MA0488.2" --pseudocount 0.1
```

### 5. 从蛋白质序列推断矩阵

从原始转录因子蛋白质序列推断潜在的 JASPAR 矩阵基序。

```bash
uv run scripts/jaspar_api.py infer_from_sequence --sequence "QAQLLPSHHVG"
```

### 6. 获取 TF 灵活模型（TFFM）

检索 JASPAR TF 灵活模型的元数据。（注意：JASPAR TFFM 端点偶尔会遇到 500 内部服务器错误）。

```bash
uv run scripts/jaspar_api.py get_tffm --tffm-id "TFFM0001.1"
```

### 输出格式

`get_tf_motif` 和 `get_tf_metadata` 命令接受可选的 `--format` 标志。支持的格式：`json`（默认）、`jsonp`、`jaspar`、`meme`、`transfac`、`pfm`、`yaml`。

## 反模式

*   **不要**将基因符号（例如，`JUN`）传递给 `get_tf_motif`。你必须传递 `MA...` 矩阵 ID。
*   **不要**在解析 TF 名称时忘记 `--tax-id`。
*   **不要**使用此技能来确定组织特异性表观遗传可用性（JASPAR 显示的是*潜在*结合，而不是*实际*组织表达背景）。
*   **不要**使用此技能来模拟特定蛋白质突变如何影响结合。
