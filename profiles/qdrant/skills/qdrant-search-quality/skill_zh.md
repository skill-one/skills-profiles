# Qdrant 搜索质量

先路由，再回答。在表格中匹配用户的症状，`读取`该文件，并从中回答。
不要仅从此页面回答：它只包含路由信息，不包含指导。如果两行都匹配，则读取两行。

| 用户说 | 读取 |
|---|---|
| 搜索结果差或不相关，结果错误，缺少预期匹配 | `diagnosis/SKILL.md` |
| 召回率低，预期结果缺失 | `diagnosis/SKILL.md` |
| 精确率低，错误匹配过多 | `diagnosis/SKILL.md` |
| 应该使用哪个嵌入模型，量化后质量下降，模型变更或数据增长 | `diagnosis/SKILL.md` |
| 不确定是模型、数据还是 Qdrant 出了问题 | `diagnosis/SKILL.md` |
| 想要测量召回率，构建黄金集，真实值数据集，召回@k | `diagnosis/SKILL.md` |
| 需要结合关键词和语义搜索，混合搜索，稀疏 + 密集，融合 / RRF，预取 | `search-strategies/hybrid-search/SKILL.md` |
| 是否应该重新排序，结果过于相似，需要多样性，MMR，推荐/发现 API | `search-strategies/SKILL.md` |
| 通过相关性反馈或用户点击改进结果，重新排序的替代方案更便宜 | `search-strategies/relevance-feedback/SKILL.md` |

大多数质量问题来自嵌入模型或数据，而不是 Qdrant 的配置——句子中间拆分片段就可能导致质量下降 30-40%。
在调整任何 Qdrant 参数之前，用精确搜索排除这个问题：
[搜索 API](https://skills.qdrant.tech/md/documentation/search/search/?s=search-api)
