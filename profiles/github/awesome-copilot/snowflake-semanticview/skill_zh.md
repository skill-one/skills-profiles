# Snowflake 语义视图

## 一次性设置

- 通过在新终端中运行 `snow --help` 来验证 Snowflake CLI 的安装。
- 如果缺少 Snowflake CLI 或用户无法安装，请指导他们访问 https://docs.snowflake.com/en/developer-guide/snowflake-cli/installation/installation。
- 根据 https://docs.snowflake.com/en/developer-guide/snowflake-cli/connecting/configure-connections#add-a-connection 使用 `snow connection add` 配置 Snowflake 连接。
- 在所有验证和执行步骤中使用配置的连接。

## 每个语义视图请求的工作流程

1. 确认目标数据库、模式、角色、仓库和最终的语义视图名称。
2. 确认模型遵循星型模式（事实与一致性维度）。
3. 使用官方语法草拟语义视图 DDL：
   - https://docs.snowflake.com/en/sql-reference/sql/create-semantic-view
4. 为每个维度、事实和指标填充同义词和注释：
   - 优先读取 Snowflake 表/视图/列注释（首选来源）：
     - https://docs.snowflake.com/en/sql-reference/sql/comment
   - 如果缺少注释或同义词，询问是否可以创建它们，用户是否希望提供文本，或是否应草拟建议供批准。
5. 使用带有 DISTINCT 和 LIMIT（最多 1000 行）的 SELECT 语句来发现事实表和维度表之间的关系，识别列数据类型，并为列创建更有意义的注释和同义词。
6. 在保持相同数据库和模式的情况下，创建一个临时验证名称（例如，追加 `__tmp_validate`）。
7. 在最终确定之前，始终通过 Snowflake CLI 将 DDL 发送到 Snowflake 进行验证：
   - 使用配置的连接通过 `snow sql` 执行语句。
   - 如果版本之间标志不同，请检查 `snow sql --help` 并使用那里显示的连接选项。
8. 如果验证失败，迭代 DDL 并重新运行验证步骤，直到成功。
9. 使用真实的语义视图名称应用最终的 DDL（创建或修改）。
10. 对最终的语义视图运行示例查询以确认其按预期工作。其 SQL 语法与这里所示的不同：https://docs.snowflake.com/en/user-guide/views-semantic/querying#querying-a-semantic-view
示例：

```SQL
SELECT * FROM SEMANTIC_VIEW(
    my_semview_name
    DIMENSIONS customer.customer_market_segment
    METRICS orders.order_average_value
)
ORDER BY customer_market_segment;
```

11. 清理验证过程中创建的任何临时语义视图。

## 同义词和注释（必需）

- 使用语义视图语法为同义词和注释：

```
WITH SYNONYMS [ = ] ( 'synonym' [ , ... ] )
COMMENT = 'comment_about_dim_fact_or_metric'
```

- 将同义词视为仅供参考；不要使用它们来引用其他地方的维度、事实或指标。
- 将 Snowflake 注释作为首选和第一来源用于同义词和注释：
  - https://docs.snowflake.com/en/sql-reference/sql/comment
- 如果 Snowflake 注释缺失，询问是否可以创建它们，用户是否希望提供文本，或是否应草拟建议供批准。
- 未经用户批准，不要自行编造同义词或注释。

## 验证模式（必需）

- 不要跳过验证。在将其作为最终版本呈现之前，始终使用 Snowflake CLI 对 Snowflake 执行 DDL。
- 优先为验证使用临时名称，以避免覆盖真实视图。

## 示例 CLI 验证（模板）

```bash
# 用实际值替换占位符。
snow sql -q "<CREATE OR ALTER SEMANTIC VIEW ...>" --connection <connection_name>
```

如果 CLI 在您的版本中使用不同的连接标志，请运行：

```bash
snow sql --help
```

## 注意事项

- 将安装和连接设置视为一次性步骤，但在第一次验证之前确认它们已完成。
- 保持最终的语义视图定义与验证的临时定义相同，除了名称。
- 不要省略同义词或注释；即使语法中可选，也应将其视为完整性的必需项。
