# Databricks

Databricks CLI、身份验证和数据探索的核心技能。

## 产品技能

针对特定产品，请使用专用技能：
- **databricks-jobs** - Lakeflow 作业的开发和部署
- **databricks-pipelines** - Lakeflow Spark 声明式管道（批处理和流式数据管道）
- **databricks-apps** - 全栈 TypeScript 应用开发部署
- **databricks-lakebase** - Lakebase Postgres 自动扩展项目管理
- **databricks-model-serving** - 模型服务端点管理和推理

对于**数据发现、探索和查询生成**——查找表、回答关于数据的自然语言问题或生成 SQL——请使用 **databricks-data-discovery**（它会先询问 Genie One，然后回退到手动探索）。如果未安装，请使用下面的 AI 工具命令和 [手动数据探索](manual-data-exploration.md)。

## 前置条件

1. **CLI 安装并当前**：CLI 必须是 >= v1.0.0。一个存在但过旧的 CLI 并不“足够好”——必须升级，而不是绕过。
   - **在 [CLI 安装](databricks-cli-install.md) 中运行楼层检查**。如果它报告 `UPGRADE` 或 `INSTALL`：停止并遵循该参考文件进行升级或安装——不要继续或告诉用户他们的 CLI 很好。
   - **如果另一个技能将您路由到此处进行升级**（它需要一个比 v1.0.0 新的 CLI —— 例如 `databricks-setup-local` 需要 v1.12.0），该技能已经检测到了差距。一个通过的 v1.0.0 楼层检查是不够的：请遵循更新/修复程序来安装最新的稳定版本，该版本满足任何技能的楼层要求。
   - 注意：在沙盒化环境（Cursor IDE、容器）中，安装命令会写入工作区外部，可能会被阻止。向用户展示安装命令，并要求他们在自己的终端中运行它。
   - **例外**：如果 CLI 安装被阻止（沙盒化容器、受限环境），请询问用户是否要回退到使用 `DATABRICKS_HOST` 和 `DATABRICKS_TOKEN` 环境变量（如果存在于 shell 中）进行直接 REST API 调用。参见 [Databricks REST API 文档](https://docs.databricks.com/api/workspace/introduction)。

2. **已身份验证**：`databricks auth profiles`
   - 如果没有：参见 [CLI 身份验证](databricks-cli-auth.md)

## 配置文件选择 - 关键

**永远不要自动选择配置文件。**

1. 列出配置文件：`databricks auth profiles`
2. 向用户展示所有配置文件及其工作区 URL
3. 让用户选择（即使只有一个存在）
4. 如有必要，提供创建新配置文件的选项

## Claude 代码 - 重要

每个 Bash 命令都在一个**单独的 shell 会话**中运行。

```bash
# 有效：--profile 标志
databricks apps list --profile my-workspace

# 有效：与 && 链接
export DATABRICKS_CONFIG_PROFILE=my-workspace && databricks apps list

# 无效：单独命令
export DATABRICKS_CONFIG_PROFILE=my-workspace
databricks apps list  # 未设置配置文件！
```

## 数据探索 — 使用 AI 工具

**使用这些命令代替手动导航目录/模式/表：**

```bash
# 发现表结构（列、类型、样本数据、统计信息）
databricks experimental aitools tools discover-schema catalog.schema.table --profile <PROFILE>

# 运行即席 SQL 查询
databricks experimental aitools tools query "SELECT * FROM table LIMIT 10" --profile <PROFILE>

# 查找默认仓库
databricks experimental aitools tools get-default-warehouse --profile <PROFILE>
```

**名称是字面的**。请使用给定的目录/模式/表名称，永远不要将连字符更改为下划线或以其他方式规范化它们。在 SQL 中，用反引号引号包含任何包含特殊字符的名称部分（例如 `` `my-catalog`.schema.table ``）；未引号的连字符会导致解析错误。

这些命令对于运行已知 SQL 和分析是第一流的——不需要 Genie。对于自然语言数据问题、定位您无法确定的数据或从问题生成查询，如果已安装，请优先使用上面的 `databricks-data-discovery` 技能。参见 [手动数据探索](manual-data-exploration.md) 了解完整的命令表面、引号规则和故障排除。

## 快速参考

**⚠️ 关键：某些命令使用位置参数，而不是标志**

```bash
# 当前用户
databricks current-user me --profile <PROFILE>

# 列出资源
databricks apps list --profile <PROFILE>
databricks jobs list --profile <PROFILE>
databricks clusters list --profile <PROFILE>
databricks warehouses list --profile <PROFILE>
databricks pipelines list --profile <PROFILE>
databricks serving-endpoints list --profile <PROFILE>

# ⚠️ Unity Catalog — 位置参数（不是标志！）
databricks catalogs list --profile <PROFILE>

# ✅ 正确：位置参数
databricks schemas list <CATALOG> --profile <PROFILE>
databricks tables list <CATALOG> <SCHEMA> --profile <PROFILE>
databricks tables get <CATALOG>.<SCHEMA>.<TABLE> --profile <PROFILE>

# ❌ 错误：这些标志/命令不存在
# databricks schemas list --catalog-name <CATALOG>    ← 将失败
# databricks tables list --catalog <CATALOG>           ← 将失败
# databricks sql-warehouses list                       ← 不存在，使用 `warehouses list`
# databricks execute-statement                         ← 不存在，使用 `experimental aitools tools query`
# databricks sql execute                               ← 不存在，使用 `experimental aitools tools query`

# 不确定时，检查帮助：
# databricks schemas list --help

# 获取详细信息
databricks apps get <NAME> --profile <PROFILE>
databricks jobs get --job-id <ID> --profile <PROFILE>
databricks clusters get --cluster-id <ID> --profile <PROFILE>

# 包
databricks bundle init --profile <PROFILE>
databricks bundle validate --profile <PROFILE>
databricks bundle deploy -t <TARGET> --profile <PROFILE>
databricks bundle run <RESOURCE> -t <TARGET> --profile <PROFILE>
```

## 故障排除

| 错误 | 解决方案 |
|------|----------|
| `cannot configure default credentials` | 使用 `--profile` 标志或先进行身份验证 |
| `configuration does not support OAuth tokens` | 该命令需要 OAuth（例如，`databricks apps logs`）。使用 `databricks auth login --host <URL> --profile <PROFILE>` 重新身份验证。参见 [CLI 身份验证](databricks-cli-auth.md)。 |
| `PERMISSION_DENIED` | 检查工作区/UC 权限 |
| `RESOURCE_DOES_NOT_EXIST` | 验证资源名称/ID 和配置文件 |

## 按任务阅读要求

| 任务 | 在继续之前阅读 |
|------|------------------------|
| 首次设置 | [CLI 安装](databricks-cli-install.md) |
| 身份验证问题/新工作区 | [CLI 身份验证](databricks-cli-auth.md) |
| 探索表/模式 | [手动数据探索](manual-data-exploration.md)（如果已安装则使用 `databricks-data-discovery`） |
| 部署作业/管道 | 使用 `/databricks-dabs` |

## 参考指南

- [CLI 安装](databricks-cli-install.md)
- [CLI 身份验证](databricks-cli-auth.md)
- [手动数据探索](manual-data-exploration.md)
