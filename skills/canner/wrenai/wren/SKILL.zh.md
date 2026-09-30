---
name: wren
description: Wren CLI 用于 AI 代理——一个覆盖 22+ 数据库（Postgres、MySQL、BigQuery、Snowflake、Spark 等）的语义 SQL 层。实际工作流程指导直接在 `wren` CLI 内部进行；这只是一个发现性占位符。当用户提出数据问题（如多少、展示、前 N 名、比较、趋势、分解、指标、收入、客户、订单）、想要安装/设置 Wren 引擎、连接新数据库、通过 dlt 连接 SaaS 数据（HubSpot、Stripe、Salesforce、GitHub、Slack）、从数据库模式生成或重新生成 MDL 项目、为项目添加业务上下文（枚举含义、单位、如 ARR/DAU/流失率等立方体），或将项目上下文层转换为可共享的 GenBI Web 应用/仪表板并部署到 Vercel 或 Cloudflare 时，都可以使用。触发器：'安装 wren'、'设置 wren 引擎'、'将数据库连接到 wren'、'将 SaaS 连接到 wren'、'加载数据（HubSpot/Stripe/Salesforce）'、'生成 mdl'、'搭建 wren 项目'、'丰富 wren 上下文'、'增强我的项目'、'添加立方体'、'构建仪表板'、'制作可共享的分析应用'、'将上下文层部署为 Web 应用'、'genbi 应用'、'wren 引导'、'wren 使用'、'wren 生成 mdl'、'wren dlt 连接器'、'wren 丰富上下文'、'wren genbi'。
---

# Wren CLI

这是一个发现性占位符。实际的工作流指南和提示辅助工具位于 `wren` CLI 本身中，因此它们始终与安装的 wrenai 版本匹配（没有技能缓存，没有版本漂移）。

安装：`pip install wrenai`。

## 工作流指南

```bash
wren skills list                        # 所有可用的工作流指南
wren skills get onboarding              # 设置 Wren 端到端
wren skills get usage                   # 日常查询
wren skills get generate-mdl            # 从数据库模式生成 MDL
wren skills get dlt-connector           # 通过 dlt 连接 SaaS 源
wren skills get enrich-context          # 添加业务上下文（单位、枚举、立方体）
wren skills get genbi                   # 构建 & 部署可共享的 GenBI 网页应用
# 添加 --full 以包含技能的参考文档
# 添加 --script <name> 以获取捆绑脚本（例如 dlt-connector / introspect_dlt）
```

## 参考文档

完整的参考文档位于网上：<https://github.com/Canner/WrenAI/tree/main/docs/core>

```bash
wren docs connection-info <ds>          # 数据源所需的 + 可选连接字段
```

## 提示增强（为代理包装用户问题）

```bash
wren ask "<question>" --guided          # 用于较弱的 LLM（严格的任务流程）
wren ask "<question>" --direct          # 用于较强的 LLM（最小包装）
```

## 日常数据命令（不是子应用 — 顶级）

```bash
wren --sql '...'                        # 通过 MDL 层执行 SQL
wren query --sql '...'                  # 同样，显式
wren dry-plan --sql '...'               # 仅编译，不访问数据库
wren context show / build / validate    # 项目 / MDL 生命周期
wren profile add / list / switch        # 命名连接配置文件
wren memory index / recall / store      # 语义记忆（需要 `[memory]` 额外）
```

运行 `wren --help` 获取完整界面；在使用任何多步骤工作流之前，先加载匹配的 `wren skills get <name>` 指南。
