---
name: nature-literature-pipeline
description: '完整的自动化文献发现流程：多源检索 → 六维评分 → 精读 → 格式化输出 → 存档。

  结合可配置引擎与每日cron驱动的应用层。可与飞书、Telegram或任何即时通讯平台协同工作。'
---

# 自然文献处理流程

一个完整、经过生产环境测试的自动化文献处理流程。不仅限于"搜索论文"——它是一个结构化的引擎，每天对研究论文进行评分、分类、阅读、交付和归档。

## 功能概述

```
Cron (每日触发，例如 08:30)
  │
  ├─ ① 搜索 (30篇候选)
  │   arXiv / OpenAlex / Crossref / Semantic Scholar (自动降级)
  │
  ├─ ② 粗筛 (30 → 5)
  │   六维评分：主题匹配 × 35 + 方法论 × 20
  │   + 期刊质量 × 15 + 网络相关性 × 10
  │   + 应用价值 × 10 + 归档价值 × 10
  │
  ├─ ③ 精读 (前5篇)
  │   摘要级或全文。来源级别标记：
  │   全文 / 仅摘要 / 仅元数据
  │
  ├─ ④ 交付
  │   格式化摘要至飞书/Telegram等
  │   🏅 排名 | 标题 | 期刊 | ⭐ 分数 | 💡 一句话亮点
  │   🔬 方法 | 📊 关键结果 | 🧭 评论
  │
  └─ ⑤ 归档
      DOI/arXiv 去重 → 分类 → 写笔记 → 更新索引
```

## 快速入门

安装后，告知您的代理：

```
我的研究领域是 [X]，关键词：[Y]，交付至 [飞书群组名称]，归档至 [路径]
```

代理将自动配置关键词、交付目标和归档路径。

然后设置每日 Cron 任务：

```
设置每日文献推送，北京时间 08:30，30篇候选，交付前5篇
```

## 架构

该技能分为两层组织：

| 层级 | 目的 | 文件 |
|-------|---------|-------|
| **引擎层** | 评分、分类、笔记模板、差距分析 | `references/scoring-system.md`, `references/gap-analysis.md`, `references/note-template.md` |
| **应用层** | 每日 Cron 流程、交付格式化、归档工作流 | `references/push-format.md`, `references/cron-setup.md`, `references/review-compilation-workflow.md` |

## 配置

所有领域特定内容均可配置：

- **关键词** — 您的研究关键词（英文 + 中文）
- **评分权重** — 调整六个维度以适应您的领域
- **分类规则** — 定义您自己的等级系统（A-E 或自定义）
- **交付目标** — 飞书群组、Telegram 频道、邮箱等
- **归档路径** — 本地保险库/维基目录

配置模板提供在 `templates/literature-push-template.md`。

## 内置安全机制

- **分数验证**：每个维度设上限，总分重新计算——不允许 11/10
- **三重去重**：DOI / arXiv ID / OpenAlex ID
- **优雅降级**：Semantic Scholar 不可用 → 自动切换至 OpenAlex + Crossref + arXiv
- **只读归档**：每日流程仅写入 `raw/` 文献目录；未经用户批准永不修改维基/知识库

## 相关技能

- `nature-academic-search` — 临时文献搜索（互补；此技能提供结构化每日自动化）
- `nature-citation` — CNS 引文导出（用于将流程发现导入稿件）
- `zotero` — 图书馆管理（用于长期组织流程输出）
- `arxiv` — arXiv API（用作搜索源）

## 参考文献

| 参考文献 | 目的 |
|-----------|---------|
| `references/scoring-system.md` | 六维评分标准，含权重、上限和评估逻辑 |
| `references/gap-analysis.md` | 通过系统性文献调查识别研究差距的方法 |
| `references/note-template.md` | 标准化文献笔记格式，含 YAML 前置符 |
| `references/push-format.md` | 每日摘要消息模板，含领域指南和示例 |
| `references/cron-setup.md` | Cron 任务创建、验证和手动回退流程 |
| `references/review-compilation-workflow.md` | 集中文献综述写作的端到端工作流 |

## 常见问题

1. **关键词漂移**：每月审核关键词——研究方向会演变
2. **分数膨胀**：子代理可能虚报分数；始终验证算术
3. **重复蔓延**：经典论文会重新出现；维护去重索引
4. **维基安全**：流程仅写入 `raw/`；维基集成需手动
5. **Cron 本地化**：Hermes Cron 是本地而非云端——机器必须运行
