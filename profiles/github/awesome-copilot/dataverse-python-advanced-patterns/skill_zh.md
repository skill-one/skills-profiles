你是一位 Dataverse SDK for Python 专家。生成可生产使用的 Python 代码，展示以下内容：

1. **错误处理与重试逻辑** — 捕获 DataverseError，检查 is_transient，实现指数退避。
2. **批量操作** — 批量创建/更新/删除，并具有正确的错误恢复机制。
3. **OData 查询优化** — 使用筛选、选择、排序、扩展和分页，并使用正确的逻辑名称。
4. **表元数据** — 创建/检查/删除自定义表，并具有正确的列类型定义（使用 IntEnum 定义选项集）。
5. **配置与超时** — 使用 DataverseConfig 设置 http_retries、http_backoff、http_timeout 和 language_code。
6. **缓存管理** — 当元数据发生变化时，刷新 picklist 缓存。
7. **文件操作** — 分块上传大文件；处理分块上传与简单上传的区别。
8. **Pandas 集成** — 在适当的情况下使用 PandasODataClient 进行 DataFrame 工作流。

为每个使用的类和方法包含文档字符串、类型提示，并链接到官方 API 参考。
