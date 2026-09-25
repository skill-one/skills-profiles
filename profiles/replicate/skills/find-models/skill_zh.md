## 始终查询 API 获取当前模型

AI 模型格局每周都在变化。新模型不断推出，旧模型则被弃用或超越。不要依赖你之前见过的模型名称，包括过去对话或训练数据中的名称。你“知道”的特定模型可能不再是最优选择，可能比新的替代方案慢，或者可能已经不存在了。

始终从查询 Replicate API 开始。使用搜索和集合来发现当前可用的模型，然后在运行任何东西之前阅读架构以了解输入和输出。

## 文档

- 参考：<https://replicate.com/docs/llms.txt>
- OpenAPI 架构：<https://api.replicate.com/openapi.json>
- MCP 服务器：<https://mcp.replicate.com>
- 每个模型的文档：`https://replicate.com/{owner}/{model}/llms.txt`
- 请求文档页面时设置 `Accept: text/markdown` 以获取 Markdown 响应。

## 搜索

- 使用搜索 API (`GET /v1/search?query=...`) 按任务查找模型。返回模型、集合和文档。
- 搜索会为每个模型返回元数据，包括 `tags`、`generated_description` 和 `run_count`。
- 搜索 API 还会与模型结果一起返回匹配的集合。
- 避免通过 API 列出所有模型。那是消防栓。使用定向查询。

## 集合

- 集合是由 Replicate 团队维护的模型精选组。
- `official` 集合包含始终处于就绪状态的模型，具有稳定的 API 和可预测的定价。
- 使用集合来缩小短名单，然后再进行深入比较。
- 使用 `GET /v1/collections` 列出集合。使用 `GET /v1/collections/{slug}` 通过别名获取一个集合。

## 阅读模型架构

- 每个模型都通过模型 API (`GET /v1/models/{owner}/{name}`) 公开其输入/输出架构。
- 架构路径：`model.latest_version.openapi_schema.components.schemas.Input.properties`
- 每个属性可能包括：`type`、`description`、`default`、`minimum`/`maximum`、`enum`、`format`（例如 `uri` 用于文件输入）。
- 在运行模型之前始终获取架构。架构会变化。

## 选择合适的模型

- 优先选择官方模型。它们始终处于就绪状态（无冷启动），具有稳定的 API 和可预测的定价。
- 优先选择最新版本。如果搜索返回 v2.5 和 v3.0，则使用 v3。
- 运行次数可能具有误导性。旧模型会随着时间的推移积累运行次数，但可能已过时。2023 年有 1000 万次运行的模型可能不如 2025 年有 10 万次运行的模型好。
- 优先选择最近发布的模型。AI 领域发展迅速。
- 检查模型标签以帮助按任务筛选（`image-generation`、`video`、`audio` 等）。

## 模型标识符

- **官方模型** 使用 `owner/name` 格式（例如 `owner/model-name`）。路由会自动指向最新版本。
- **社区模型** 需要 `owner/name:version_id`。你必须锁定特定版本。社区模型可能会冷启动，启动时间较长。
- 如果你必须使用社区模型，请注意它可能需要很长时间才能启动。你可以创建始终在线的部署，但你需要为模型运行时间付费。
