# Airflow 操作

使用 `af` 命令查询、管理和排错 Airflow 工作流。

## Astro CLI

[Astro CLI](https://www.astronomer.io/docs/astro/cli/overview) 是推荐的本地运行 Airflow 并部署到生产环境的方式。它提供了一个开箱即用的容器化 Airflow 环境：

```bash
# 初始化新项目
astro dev init

# 启动本地 Airflow（Web 服务器在 http://localhost:8080）
astro dev start

# 快速解析 DAG 以捕获错误（无需启动 Airflow）
astro dev parse

# 对 DAG 运行 pytest
astro dev pytest

# 部署到生产环境
astro deploy            # 全量部署（镜像 + DAG）
astro deploy --dags     # 仅 DAG 部署（快速，无需构建镜像）
```

更多详情：
- **新项目？** 查看 **setting-up-astro-project** 技能
- **本地环境？** 查看 **managing-astro-local-env** 技能
- **部署？** 查看 **deploying-airflow** 技能

---

## 运行 CLI

这些命令假设 `af` 在 PATH 中。通过 `astro otto` 自动获取，或使用 `uv tool install astro-airflow-mcp` 独立安装。

## 实例配置

管理多个 Airflow 实例，并使用持久化配置：

```bash
# 添加新实例
af instance add prod --url https://airflow.example.com --token "$API_TOKEN"
af instance add staging --url https://staging.example.com --username admin --password admin

# 列出和切换实例
af instance list      # 以表格形式显示所有实例
af instance use prod  # 切换到 prod 实例
af instance current   # 显示当前实例
af instance delete old-instance

# 自动发现实例（使用 --dry-run 预览）
af instance discover --dry-run        # 预览所有可发现的实例
af instance discover                  # 从所有后端（astro, local）发现
af instance discover astro            # 仅发现 Astro 部署
af instance discover astro --all-workspaces  # 包含所有可访问的工作空间
af instance discover local            # 扫描常见本地 Airflow 端口
af instance discover local --scan     # 深度扫描端口 1024-65535

# 重要提示：始终先使用 --dry-run 运行，并在没有它的情况下请求用户同意。
# 非干跑模式会在 Astro Cloud 中创建 API 令牌，这是一个敏感操作，需要明确批准。

# 显示实例来源（文件路径 + 范围）
af instance show prod

# 通过环境变量覆盖单个命令的实例
AIRFLOW_API_URL=https://staging.example.com AIRFLOW_AUTH_TOKEN=$STG af dags list

# 或持久切换
af instance use staging
```

配置布局（镜像 `git config` 系统/全局/本地）：

| 范围 | 文件 | 提交状态 |
|---|---|---|
| 全局 | `~/.astro/config.yaml` | 无（用户级） |
| 项目共享 | `<root>/.astro/config.yaml` | 是 |
| 项目本地 | `<root>/.astro/config.local.yaml` | 否（git 忽略） |

`<root>` 通过从当前工作目录向上查找 `.astro/` 来定位。项目内默认写路由：`add`/`discover` → 项目共享，`use` → 项目本地。使用 `--global` / `--project` / `--local` 覆盖。设置 `AF_CONFIG=<path>` 以绕过分层并使用单个文件。

使用 `af migrate` 从旧版 `~/.af/config.yaml` 迁移（幂等；将旧文件重命名为 `.bak`）。

配置中的令牌可使用 `${VAR}` 语法引用环境变量：
```yaml
instances:
- name: prod
  url: https://airflow.example.com
  auth:
    token: ${AIRFLOW_API_TOKEN}
```

或直接使用环境变量（无需配置文件）：

```bash
export AIRFLOW_API_URL=http://localhost:8080
export AIRFLOW_AUTH_TOKEN=your-token-here
# 或用户名/密码：
export AIRFLOW_USERNAME=admin
export AIRFLOW_PASSWORD=admin
```

或 CLI 标志：`af --airflow-url http://localhost:8080 --token "$TOKEN" <command>`

## 快速参考

| 命令 | 描述 |
|---------|-------------|
| `af health` | 系统健康检查 |
| `af dags list` | 列出所有 DAG |
| `af dags get <dag_id>` | 获取 DAG 详情 |
| `af dags explore <dag_id>` | 全部 DAG 调查 |
| `af dags source <dag_id>` | 获取 DAG 源代码 |
| `af dags pause <dag_id>` | 暂停 DAG 调度 |
| `af dags unpause <dag_id>` | 恢复 DAG 调度 |
| `af dags errors` | 列出导入错误 |
| `af dags warnings` | 列出 DAG 警告 |
| `af dags stats` | DAG 运行统计 |
| `af runs list` | 列出 DAG 运行 |
| `af runs get <dag_id> <run_id>` | 获取运行详情 |
| `af runs trigger <dag_id>` | 触发 DAG 运行 |
| `af runs trigger-wait <dag_id>` | 触发并等待完成 |
| `af runs delete <dag_id> <run_id>` | 永久删除 DAG 运行 |
| `af runs clear <dag_id> <run_id>` | 清除运行以重新执行 |
| `af runs diagnose <dag_id> <run_id>` | 诊断失败运行 |
| `af tasks list <dag_id>` | 列出 DAG 中的任务 |
| `af tasks get <dag_id> <task_id>` | 获取任务定义 |
| `af tasks instance <dag_id> <run_id> <task_id>` | 获取任务实例 |
| `af tasks logs <dag_id> <run_id> <task_id>` | 获取任务日志 |
| `af config version` | Airflow 版本 |
| `af config show` | 完整配置 |
| `af config connections` | 列出连接 |
| `af config variables` | 列出变量 |
| `af config variable <key>` | 获取特定变量 |
| `af config pools` | 列出池 |
| `af config pool <name>` | 获取池详情 |
| `af config plugins` | 列出插件 |
| `af config providers` | 列出提供者 |
| `af config assets` | 列出资产/数据集 |
| `af api <endpoint>` | 直接 REST API 访问 |
| `af api ls` | 列出可用 API 端点 |
| `af api ls --filter X` | 列出匹配模式的端点 |
| `af registry providers` | 列出 Airflow Registry 中的提供者 |
| `af registry modules <provider>` | 列出提供者中的算子/钩子/传感器/传输 |
| `af registry parameters <provider>` | 构造函数签名（名称、类型、默认值、必需） |
| `af registry connections <provider>` | 提供者暴露的连接类型 |

## 用户意图模式

### 入门指南
- "如何本地运行 Airflow？" / "设置 Airflow" -> 使用 **managing-astro-local-env** 技能（使用 Astro CLI）
- "创建新的 Airflow 项目" / "初始化项目" -> 使用 **setting-up-astro-project** 技能（使用 Astro CLI）
- "如何安装 Airflow？" / "开始使用 Airflow" -> 使用 **setting-up-astro-project** 技能

### DAG 操作
- "有哪些 DAG？" / "列出所有 DAG" -> `af dags list`
- "告诉我关于 DAG X" / "DAG Y 是什么？" -> `af dags explore <dag_id>`
- "DAG X 的调度是什么？" -> `af dags get <dag_id>`
- "给我 DAG X 的代码" -> `af dags source <dag_id>`
- "停止 DAG X" / "暂停此工作流" -> `af dags pause <dag_id>`
- "恢复 DAG X" -> `af dags unpause <dag_id>`
- "DAG 中是否有错误？" -> `af dags errors`
- "创建新的 DAG" / "编写管道" -> 使用 **authoring-dags** 技能

### 运行操作
- "已执行哪些运行？" -> `af runs list`
- "运行 DAG X" / "触发管道" -> `af runs trigger <dag_id>`
- "运行 DAG X 并等待" -> `af runs trigger-wait <dag_id>`
- "为什么这个运行失败？" -> `af runs diagnose <dag_id> <run_id>`
- "删除此运行" / "移除卡住的运行" -> `af runs delete <dag_id> <run_id>`
- "清除此运行" / "重试此运行" / "重新运行" -> `af runs clear <dag_id> <run_id>`
- "测试此 DAG 并在失败时修复" -> 使用 **testing-dags** 技能

### 任务操作
- "DAG X 中有哪些任务？" -> `af tasks list <dag_id>`
- "获取任务日志" / "任务为什么失败？" -> `af tasks logs <dag_id> <run_id> <task_id>`
- "全面根本原因分析" / "诊断和修复" -> 使用 **debugging-dags** 技能

### 数据操作
- "数据是否新鲜？" / "此表上次更新时间？" -> 使用 **checking-freshness** 技能
- "数据来自哪里？" -> 使用 **tracing-upstream-lineage** 技能
- "哪些依赖于此表？" / "如果更改此表会怎样？" -> 使用 **tracing-downstream-lineage** 技能

### 部署操作
- "部署我的 DAG" / "推送到生产环境" -> 使用 **deploying-airflow** 技能
- "设置 CI/CD" / "自动化部署" -> 使用 **deploying-airflow** 技能
- "部署到 Kubernetes" / "设置 Helm" -> 使用 **deploying-airflow** 技能
- "astro deploy" / "仅 DAG 部署" -> 使用 **deploying-airflow** 技能

### 系统操作
- "Airflow 的版本是什么？" -> `af config version`
- "有哪些连接？" -> `af config connections`
- "池是否已满？" -> `af config pools`
- "Airflow 是否健康？" -> `af health`

### API 探索
- "有哪些 API 端点可用？" -> `af api ls`
- "查找变量端点" -> `af api ls --filter variable`
- "访问 XCom 值" / "获取 XCom" -> `af api xcom-entries -F dag_id=X -F task_id=Y`
- "获取事件日志" / "审计跟踪" -> `af api event-logs -F dag_id=X`
- "通过 API 创建连接" -> `af api connections -X POST --body '{...}'`
- "通过 API 创建变量" -> `af api variables -X POST -F key=name -f value=val`

### Registry 发现
- "提供者 X 有哪些算子？" -> `af registry modules <provider>`
- "算子 Y 的构造函数参数是什么？" -> `af registry parameters <provider>`
- "有哪些提供者存在？" / "是否存在提供者 Z？" -> `af registry providers`
- "提供者 X 暴露哪些连接类型？" -> `af registry connections <provider>`
- "使用特定算子编写 DAG" -> 使用 registry 在复制示例前验证当前签名

## 常见工作流

### 部署前验证 DAG

如果你使用 Astro CLI，可以在没有运行 Airflow 实例的情况下验证 DAG：

```bash
# 解析 DAG 以捕获导入错误和语法问题
astro dev parse

# 运行单元测试
astro dev pytest
```

否则，针对运行中的实例验证：

```bash
af dags errors     # 检查解析/导入错误
af dags warnings   # 检查弃用警告
```

### 编写代码前发现算子签名

Airflow Registry (`airflow.apache.org/registry`) 是提供者类及其当前构造函数签名的权威来源。在编写 DAG 时，优先使用它而不是内存或过时的文档——registry 反映了实时提供者发布。

```bash
# 列出所有提供者并选择所需的
af registry providers | jq '.providers[] | {id, name, version}'

# 列出提供者中的每个算子/钩子/传感器（例如 standard, amazon, google）
af registry modules standard \
  | jq '.modules[] | {name, type, import_path, docs_url}'

# 获取特定类的当前构造函数签名
af registry parameters standard \
  | jq '.classes["airflow.providers.standard.operators.hitl.ApprovalOperator"].parameters'

# 通过子字符串过滤模块（当你知道概念但不知道类时很有用）
af registry modules standard \
  | jq '.modules[] | select(.import_path | test("hitl"))'
```

结果本地缓存：最新版本 1 小时，固定版本 30 天（不可变）。在 `modules` / `parameters` / `connections` 调用中添加 `--version X.Y.Z` 可针对特定版本。

### 调查失败运行

```bash
# 1. 列出最近运行以找到失败
af runs list --dag-id my_dag

# 2. 诊断特定运行
af runs diagnose my_dag manual__2024-01-15T10:00:00+00:00

# 3. 获取失败任务的日志（从诊断输出）
af tasks logs my_dag manual__2024-01-15T10:00:00+00:00 extract_data

# 4. 修复后，清除运行以重试所有任务
af runs clear my_dag manual__2024-01-15T10:00:00+00:00
```

### 早晨健康检查

```bash
# 1. 整体系统健康
af health

# 2. 检查损坏的 DAG
af dags errors

# 3. 检查池利用率
af config pools
```

### 理解 DAG

```bash
# 获取综合概览（元数据 + 任务 + 源）
af dags explore my_dag
```

### 检查 DAG 为什么未运行

```bash
# 检查是否暂停
af dags get my_dag

# 检查导入错误
af dags errors

# 检查最近运行
af runs list --dag-id my_dag
```

### 触发和监控

```bash
# 选项 1：触发并等待（阻塞）
af runs trigger-wait my_dag --timeout 1800

# 选项 2：触发后稍后检查
af runs trigger my_dag
af runs get my_dag <run_id>
```

## 输出格式

所有命令输出 JSON（`instance` 命令除外，使用人类可读表格）：

```bash
af dags list
# {
#   "total_dags": 5,
#   "returned_count": 5,
#   "dags": [...]
# }
```

使用 `jq` 进行过滤：

```bash
# 查找失败运行
af runs list | jq '.dag_runs[] | select(.state == "failed")'

# 获取 DAG ID 仅
af dags list | jq '.dags[].dag_id'

# 查找暂停的 DAG
af dags list | jq '[.dags[] | select(.is_paused == true)]'
```

## 任务日志选项

```bash
# 获取特定重试尝试的日志
af tasks logs my_dag run_id task_id --try 2

# 获取映射任务索引的日志
af tasks logs my_dag run_id task_id --map-index 5
```

## 使用 `af api` 进行直接 API 访问

使用 `af api` 访问未涵盖高级命令的端点（XCom、事件日志、回填等）。

```bash
# 发现可用端点
af api ls
af api ls --filter variable

# 基本用法
af api dags
af api dags -F limit=10 -F only_active=true
af api variables -X POST -F key=my_var -f value="my value"
af api variables/old_var -X DELETE
```

**字段语法**：`-F key=value` 自动转换类型，`-f key=value` 保持为字符串。

**完整参考**：参见 [api-reference.md](api-reference.md) 获取所有选项、常见端点（XCom、事件日志、回填）和示例。

## 相关技能

| 技能 | 在...时使用 |
|-------|-------------|
| **authoring-dags** | 创建或编辑 DAG 文件的最佳实践 |
| **testing-dags** | 迭代测试 -> 调试 -> 修复 -> 重新测试循环 |
| **debugging-dags** | 深度根本原因分析和失败诊断 |
| **checking-freshness** | 检查数据是否最新或过时 |
| **tracing-upstream-lineage** | 查找数据来源 |
| **tracing-downstream-lineage** | 影响分析——如果更改会怎样 |
| **deploying-airflow** | 将 DAG 部署到生产环境（Astro、Docker Compose、Kubernetes） |
| **migrating-airflow-2-to-3** | 将 DAG 从 Airflow 2.x 升级到 3.x |
| **managing-astro-local-env** | 启动、停止或排错本地 Airflow |
| **setting-up-astro-project** | 初始化新的 Astro/Airflow 项目 |
| **airflow-state-store** | 每任务检查点、水位线、崩溃安全算子（Airflow 3.3+） |
| **airflow-hitl** | 暂停 DAG 以供人工审批或输入（Airflow 3.1+） |
