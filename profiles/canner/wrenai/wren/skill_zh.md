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
wren skills get genbi                   # 构建 & 部署可共享的 GenBI 网络应用程序
# 添加 --full 以包含技能的参考文档
# 添加 --script <名称> 以获取捆绑脚本（例如 dlt-connector / introspect_dlt）
```

## 参考文档

完整的参考文档位于网上：<https://github.com/Canner/WrenAI/tree/main/docs/core>

```bash
wren docs connection-info <ds>          # 数据源所需的 + 可选连接字段
```

## 提示增强（为代理包装用户问题）

```bash
wren ask "<问题>" --guided          # 用于较弱的 LLM（严格的任务流程）
wren ask "<问题>" --direct          # 用于较强的 LLM（最小包装）
```

## 日常数据命令（不是子应用程序——顶级）

```bash
wren --sql '...'                        # 通过 MDL 层执行 SQL
wren query --sql '...'                  # 相同，显式
wren dry-plan --sql '...'               # 仅转换，不访问数据库
wren context show / build / validate    # 项目 / MDL 生命周期
wren profile add / list / switch        # 命名连接配置文件
wren memory index / recall / store      # 语义记忆（需要 `[memory]` 额外）
```

运行 `wren --help` 获取完整界面；在使用任何多步骤工作流之前，先加载匹配的 `wren skills get <名称>` 指南。
