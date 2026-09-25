# STEP Parts

来源：维护在 [earthtojake/text-to-cad](https://github.com/earthtojake/text-to-cad) 中。
使用已安装的本地技能文件作为运行时真实来源；仓库链接仅用于来源和发布审核。

## 概述

使用 step.parts 机器端点，而不是抓取 HTML 或依赖本地仓库文件。将 `https://api.step.parts` 视为规范 API 来源，将 `https://www.step.parts` 视为静态资源来源，除非用户提供不同的托管镜像。网络/DNS 故障不具有决定性：如果从沙盒无法访问 `api.step.parts`，在报告缺失或使用占位符几何体之前，使用网络权限重试一次。除非 API 可达且未返回相关候选者，否则不要描述零件不可用。

当 CAD 组装包含命名标准件（如执行器、伺服电机、电机、电子板、连接器或其他可购买组件）时，在创建简化占位符几何体之前搜索 step.parts。对于命名伺服电机、电机和执行器，在放弃之前搜索精确型号字符串和常见别名/供应商拼写。例如，`STS3215` 也可能以 `ST3215`、`3215`、`Waveshare Feetech ST3215` 或在 `family=feetech` 下出现。如果 API 可达且没有精确或近似匹配，记录搜索缺失，然后使用文档化的轮廓或简化替代品。

## 快速工作流程

1. 将请求的零件解释为搜索词和可选的方面：
   - `q` 用于模糊标记、标准、别名、尺寸、源/产品 URL 和属性名称/值。
   - 当用户提供精确方面时，使用 `category`、`family`、`standard` 或 `tag`。
2. 搜索 `/v1/parts` 并检查 `items`、`total` 和 `facets`。对于执行器型号，在将空结果视为缺失之前，重试可能的别名、遗漏的字母、供应商名称和相关的家族方面。
3. 如果结果不明确，在 `id`、`name`、`standard` 和关键属性中选择前，提供最好的几个选项。如果有一个结果明显匹配，则返回所选记录的详细信息，除非用户要求下载本地 STEP 文件。
4. 当找到精确或近似的标准件型号时，除非有明确的装配时间原因使用简化轮廓，否则优先下载并使用其 STEP 文件。明确记录该选择。
5. 当用户要求下载或保存 STEP 文件时，下载其 `stepUrl`，并在存在时使用记录的 `sha256` 验证文件。
6. 返回下载的本地路径，以及所选零件 ID 和页面/API URL，以便用户追溯来源。

## CAD 查看器交接

完成 step.parts 工作创建或更新本地 `.step` 或 `.stp` 文件后，当安装该技能时，必须始终将明确的文件路径传递给 `$cad-viewer`。`$cad-viewer` 必须在未运行时启动 CAD 查看器并返回相关创建或更新文件的链接；如果 `$cad-viewer` 不可用或启动失败，则报告该问题，而不是静默忽略交接。

## 嵌套下载器

使用 `scripts/download_step_part.py` 进行确定性搜索、下载和校验和验证：

```bash
python scripts/download_step_part.py "M3 socket head 12" --download
python scripts/download_step_part.py --id iso4762_socket_head_cap_screw_m3x12 --download
python scripts/download_step_part.py "bearing 608zz" --limit 5
```

有用选项：

- `--origin`：仅当用户提供另一个托管 API 来源时，覆盖 `https://api.step.parts`。
- `--tag`、`--category`、`--family`、`--standard`：可重复的方面过滤器。
- `--out-dir`：下载目标目录。它默认为系统临时目录，因此每次文件应在项目中保留时都传递它。
- `--filename`：重命名下载的一个文件；与 `--all` 一起被拒绝。
- `--limit`、`--page`：搜索页面大小（默认 10，API 限制 500）和 1 基于的页面。
- `--all`：与 `--download` 一起使用时，下载返回页面上的每个结果作为单独的 STEP 下载。
- `--overwrite`：替换现有输出文件。如果没有它，拒绝现有目标而不是覆盖。

脚本将 JSON 打印到标准输出。对于搜索，它打印匹配的记录。对于下载，它打印保存的文件路径、校验和和源 URL。失败打印一行纯文本消息到标准错误并退出 1。

## API 参考

需要端点详细信息、字段含义或查询语义时，阅读 `references/step-parts-api.md`。优先使用：

- `/v1/parts` 用于带绝对资产 URL 的过滤搜索。
- `/v1/parts/{id}` 用于一个丰富记录。
- 返回的 `stepUrl` 用于 STEP 下载。
- `/v1/catalog/parts.index.json` 用于紧凑的发现索引。
- `/v1/catalog/schema` 用于字段和家族属性含义。
- `/v1/openapi.json` 在生成客户端或工具时。

## 搜索指南

- 查询词由 API 通过 AND 连接，因此从具体但不要过度约束开始。例如，在添加精确家族和标准过滤器之前使用 `M3 SHCS 12`。
- 一个方面内的值通过 OR 连接，并且选择的 `tag`、`category`、`family` 和 `standard` 字段通过 AND 连接。使用精确方面在已知类别内缩小，然后手动按名称和属性排名。
- 标准 可以作为 `ISO 4762`、`ISO4762` 或精确的 `standard.designation` 查询。
- `attributes` 对象包含特定于家族的事实，如 `thread`、`lengthMm`、`bore1Mm`、`material`、`profileSeries`、`slotSizeMm` 和以毫米为单位的尺寸。
- 零件、GLB 和 PNG URL 模式在 `https://www.step.parts` 上是可预测的；STEP URL 是环境感知的，在生产中可能解析到 GitHub LFS 媒体。使用目录/API `stepUrl` 进行下载。
