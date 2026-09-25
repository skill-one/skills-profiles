# Firecrawl 知识库

使用此工具将 URL 或主题转换为结构化的 LLM 准备内容。

## 欢迎面谈

根据上下文推断来源、目标、深度和输出位置。如果来源和目标明确，请立即进行。

如果遇到阻塞，最多只问 1-3 个简洁的问题，例如来源 URL/主题、输出是参考/RAG/训练/文档，或者如果请求训练，请提供训练格式。

## Firecrawl 收集计划

使用 Firecrawl 地图处理文档网站，搜索基于主题的语料库，将页面抓取为 Markdown 格式，并保留代码示例和表格。

对于文件，请遵循 Firecrawl 下载式约定：

```text
.firecrawl/
  <hostname>/
    <path>/
      index.md
```

## 并行工作

如果适用，请使用子代理或等效的并行任务运行器：

- 每位研究人员负责一个文档部分
- 官方文档、教程、社区讨论和按来源类型的参考
- 来源抓取与块生成与清单生成

## 输出模式

- 参考：Markdown 文件、`index.md` 和 `sources.json`。
- RAG：Markdown 文件、块文件和 `manifest.json`。
- 训练：抓取的来源文件、`training-data.jsonl` 和 `training-metadata.json`。
- 文档镜像：完整的 Markdown 镜像，包含目录。

## 最终交付物

```markdown
# 知识库：[来源]

## 摘要
[收集了什么以及为什么]

## 输出结构
[创建的文件/目录]

## 覆盖范围
[部分、来源类型、数量]

## 使用说明
[如何在 RAG、文档、训练或代理上下文中使用]

## 来源
[收集的 URL]

## 重新运行输入
workflow: firecrawl-knowledge-base
source: [url/主题]
goal: [参考/rag/train/docs]
depth: [快速/彻底/详尽]
output_dir: [.firecrawl/]
```

## 质量标准

- 保留代码示例和格式。
- 尽可能移除样板导航。
- 在前文或元数据中包含来源 URL。
