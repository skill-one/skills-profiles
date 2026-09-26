# 查询编写技巧

## 简单查询的工作流程

对于关于单个表的简单问题：

1. **识别表** - 哪个表包含数据？
2. **获取架构** - 使用 `sql_db_schema` 查看列
3. **编写查询** - 使用 WHERE/LIMIT/ORDER BY 选择相关列
4. **执行** - 使用 `sql_db_query` 运行
5. **格式化答案** - 清晰地呈现结果

## 复杂查询的工作流程

对于需要多个表的问题：

### 1. 规划方法
**使用 `write_todos` 将任务分解：**
- 识别所有需要的表
- 映射关系（外键）
- 规划 JOIN 结构
- 确定聚合操作

### 2. 检查架构
使用 `sql_db_schema` 对每个表进行检查，以找到 JOIN 列和所需字段。

### 3. 构建查询
- SELECT - 列和聚合操作
- FROM/JOIN - 基于 FK = PK 连接表
- WHERE - 聚合前的过滤条件
- GROUP BY - 所有非聚合列
- ORDER BY - 有意义的排序
- LIMIT - 默认 5 行

### 4. 验证和执行
检查所有 JOIN 是否有条件，GROUP BY 是否正确，然后运行查询。

## 示例：按国家统计收入
```sql
SELECT
    c.Country,
    ROUND(SUM(i.Total), 2) as TotalRevenue
FROM Invoice i
INNER JOIN Customer c ON i.CustomerId = c.CustomerId
GROUP BY c.Country
ORDER BY TotalRevenue DESC
LIMIT 5;
```

## 错误恢复

如果查询失败或返回意外结果：
1. **空结果** — 根据架构验证列名和 WHERE 条件；检查大小写敏感性或 NULL 值
2. **语法错误** — 重新检查 JOIN、GROUP BY 完整性和别名引用
3. **超时** — 添加更严格的 WHERE 过滤器或 LIMIT 以减少结果集，然后优化

## 质量指南

- 仅查询相关列（不要使用 SELECT *）
- 始终应用 LIMIT（默认 5）
- 使用表别名以提高清晰度
- 对于复杂查询：使用 write_todos 进行规划
- 不要使用 DML 语句（INSERT、UPDATE、DELETE、DROP）
