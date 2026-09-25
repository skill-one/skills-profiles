## 使用方法

所有脚本都可以使用 Node.js 执行。将 `<param_name>` 和 `<param_value>` 替换为实际值。

**Bash:**
`node <skill_dir>/scripts/<script_name>.js '{"<param_name>": "<param_value>"}'`

**PowerShell:**
`node <skill_dir>/scripts/<script_name>.js '{\"<param_name>\": \"<param_value>\"}'`

注意：脚本会自动从各种 .env 文件中加载环境变量。除非技能执行因环境变量缺失而失败，否则不要要求用户设置变量。


## 脚本


### lookup_context

检索一个或多个数据资产及其关系的丰富元数据。

#### 参数

| 名称 | 类型 | 描述 | 必填 | 默认值 |
| :--- | :--- | :--- | :--- | :--- |
| resources | 数组 | 必填。最多 10 个资源名称的列表。资源可以属于不同的项目，但必须属于同一位置。 | 是 |  |


---

### lookup_entry

从 Catalog 中检索特定数据资产（例如表/数据集/视图）的特定元数据

#### 参数

| 名称 | 类型 | 描述 | 必填 | 默认值 |
| :--- | :--- | :--- | :--- | :--- |
| entry | 字符串 | 必填。Entry 资源名称，格式如下：projects/{project}/locations/{location}/entryGroups/{entryGroup}/entries/{entry}。 | 是 |  |
| view | 整数 | 
				## 参数：view

				**类型：** 整数

				**描述：** 可选。指定要返回的条目及其方面的部分。

				**可能值：**

				*   1 (BASIC)：返回不带方面的条目。
				*   2 (FULL)：返回所有必需方面和非必需方面的键。（默认）
				*   3 (CUSTOM)：返回条目和在 aspect_types 字段中请求的方面（最多 100 个方面）。当 aspect_types 不为空时，始终使用此视图。
				*   4 (ALL)：返回条目和必需及可选方面（最多 100 个方面）
				 | 否 | `2` |
| aspectTypes | 数组 | 可选。将返回的方面限制为提供的方面类型。它仅在与 CUSTOM 视图一起使用时才起作用。 | 否 | `[]` |


---

### search_aspect_types

搜索与查询相关的方面类型。

#### 参数

| 名称 | 类型 | 描述 | 必填 | 默认值 |
| :--- | :--- | :--- | :--- | :--- |
| query | 字符串 | 要匹配的方面类型查询。 | 是 |  |
| pageSize | 整数 | 搜索页面中返回的方面类型数量。 | 否 | `5` |
| orderBy | 字符串 | 指定结果的排序顺序。支持值：relevance, last_modified_timestamp, last_modified_timestamp asc | 否 | `relevance` |


---

### search_entries

根据提供的搜索查询在 Catalog 中搜索数据资产（例如表/数据集/视图）。

#### 参数

| 名称 | 类型 | 描述 | 必填 | 默认值 |
| :--- | :--- | :--- | :--- | :--- |
| query | 字符串 | 用于搜索条目的查询字符串，遵循 Dataplex 搜索语法。支持逻辑运算符（AND, OR, NOT）和分组。例如，要查找可能已重命名的表，可以使用 'type:table (name:books OR fiction)'。这比多次单独调用更高效。警告：执行不带特定过滤器的广泛搜索（例如，type:table）可能会很慢并消耗大量资源。在执行探索性搜索时，始终使用 pageSize 参数限制返回的结果数量。 | 是 |  |
| scope | 字符串 | 范围将搜索空间限制为特定项目或组织。它必须采用以下格式：organizations/<org_id> 或 projects/<project_id> 或 projects/<project_number>。 | 否 | `` |
| pageSize | 整数 | 搜索页面中的结果数量。 | 否 | `5` |
| orderBy | 字符串 | 指定结果的排序顺序。支持值：relevance, last_modified_timestamp, last_modified_timestamp asc | 否 | `relevance` |
