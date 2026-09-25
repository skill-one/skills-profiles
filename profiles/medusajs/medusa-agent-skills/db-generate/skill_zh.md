# 生成数据库迁移

为指定的 Medusa 模块生成数据库迁移。

用户将模块名称作为参数提供（例如，`brand`、`product`、`custom-module`）。

例如：`/medusa-dev:db-generate brand`

使用 Bash 工具执行命令 `npx medusa db:generate <module-name>`，将 `<module-name>` 替换为提供的参数。

向用户报告结果，包括：

- 生成的迁移模块名称
- 迁移文件名称或位置
- 任何错误或警告
- 下一步操作（运行 `npx medusa db:migrate` 应用迁移）
