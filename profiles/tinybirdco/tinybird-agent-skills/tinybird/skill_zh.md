# Tinybird 最佳实践

关于 Tinybird 文件格式、SQL 规则、优化模式以及数据建模的指导。在创建或编辑 Tinybird 数据文件时使用此技能。

## 何时应用

- 创建或更新 Tinybird 资源 (.datasource, .pipe, .connection)
- 编写或优化 SQL 查询
- 设计端点模式和数据模型
- 组织项目结构和数据层
- 使用物化视图或复制管道
- 实现去重模式
- 审查或重构 Tinybird 项目文件

## 规则文件

- `rules/project-files.md`
- `rules/build-deploy.md`
- `rules/datasource-files.md`
- `rules/pipe-files.md`
- `rules/endpoint-files.md`
- `rules/materialized-files.md`
- `rules/materialized-join-prefilter.md`
- `rules/sink-files.md`
- `rules/copy-files.md`
- `rules/connection-files.md`
- `rules/sql.md`
- `rules/endpoint-optimization.md`
- `rules/tests.md`
- `rules/deduplication-patterns.md`

## 快速参考

- 项目本地文件是事实来源。
- 构建目标来自 `tinybird.config.json` 的 `dev_mode` (`local` 或 `branch`)。
- `tb deploy` 目标是 Tinybird Cloud 生产环境。
- 命令如 `tb sql` 和 `tb logs` 默认为本地，除非设置了 `--cloud` 或 `--branch=<branch-name>`。
- Tinybird 模板规则和严格参数处理下，SQL 仅支持 SELECT。
- 默认使用 MergeTree；物化目标使用 AggregatingMergeTree。
- 尽早过滤，仅选择需要的列，将复杂工作推迟到管道的后期处理。
