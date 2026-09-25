# 从 Oracle 迁移存储过程到 PostgreSQL

将 Oracle PL/SQL 存储过程和函数转换为 PostgreSQL PL/pgSQL 兼容版本。

## 工作流程

```
进度：
- [ ] 第 1 步：读取 Oracle 源过程
- [ ] 第 2 步：转换为 PostgreSQL PL/pgSQL
- [ ] 第 3 步：将迁移后的过程写入 Postgres 输出目录
```

**第 1 步：读取 Oracle 源过程**

从 `.github/oracle-to-postgres-migration/DDL/Oracle/Procedures and Functions/` 读取 Oracle 存储过程。参考 `.github/oracle-to-postgres-migration/DDL/Oracle/Tables and Views/` 中的 Oracle 表/视图定义以进行类型解析。

**第 2 步：转换为 PostgreSQL PL/pgSQL**

应用以下转换规则：

- 将所有 Oracle 特定语法转换为 PostgreSQL 兼容版本。
- 保留原始功能和控制流逻辑。
- 保持类型锚定的输入参数（例如，`PARAM_NAME IN table_name.column_name%TYPE`）。
- 对传递给其他过程的输出参数使用显式类型（`NUMERIC`、`VARCHAR`、`INTEGER`）——不要对这些进行类型锚定。
- 不要修改方法签名。
- 除非 Oracle 源中已存在模式名，否则不要在对象名前加模式名前缀。
- 保持异常处理和回滚逻辑不变。
- 不要生成 `COMMENT` 或 `GRANT` 语句。
- 在排序文本时有意应用排序规则：
  - 仅当需要 Oracle 兼容的二进制排序且未指定其他排序顺序时，使用 `COLLATE "C"`。
  - 如果 Oracle 使用显式语言排序（例如 `NLS_SORT = French`），则映射到 PostgreSQL 显式区域设置排序规则，而不是 `"C"`。
  - 使用 `SELECT collname, collprovider, collcollate, collctype FROM pg_collation ORDER BY collname;` 发现目标环境中的排序规则。
- 将 `UNION ALL` 视为审查检查点。按分支验证计划质量，如果合并分支规划导致回归（例如，大型表出现意外的顺序扫描），则重新结构化。
- 当 `orafce` 扩展提高清晰度或保真度时，利用它。

参考 `.github/oracle-to-postgres-migration/DDL/Postgres/{ProjectName}/Tables and Views/` 中的 PostgreSQL 表/视图定义以获取目标模式详细信息。

**第 3 步：将迁移后的过程写入 Postgres 输出目录**

将每个迁移后的过程放在 `.github/oracle-to-postgres-migration/DDL/Postgres/{ProjectName}/Procedures and Functions/{PACKAGE_NAME_IF_APPLICABLE}/` 下的独立文件中。每个过程一个文件。

> `{ProjectName}` 是项目的程序集/文件夹名，空格规范化为 `-`（例如 `MyApp.DataAccess`）。这匹配代理和其他迁移技能使用的路径。
