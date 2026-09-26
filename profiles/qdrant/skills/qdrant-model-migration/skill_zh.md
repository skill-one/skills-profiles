# 更换嵌入模型时该怎么做

不同模型的向量是不兼容的。你不能在同一个向量空间中混合使用旧的和新的嵌入。在 v1.18 及以上版本中，你可以向现有集合中添加或删除命名的向量字段——迁移不再总是需要创建新集合。在 v1.17 或更早版本中，所有命名的向量都必须在集合创建时定义。

- 在选择策略之前，先了解集合别名 [集合别名](https://skills.qdrant.tech/md/documentation/manage-data/collections/?s=collection-aliases)


## 我能避免重新嵌入吗？

使用场景：在提交完整迁移之前寻找捷径。

你必须重新嵌入的情况：更改模型提供者（OpenAI 改为 Cohere）、更改架构（CLIP 改为 BGE）、不同模型之间的不兼容维度数量，或向仅支持密集向量的集合中添加稀疏向量。

你可以避免重新嵌入的情况：使用 Matryoshka 模型（使用 `dimensions` 参数输出低维嵌入，从样本数据中学习线性变换，会有些召回率损失，适用于 1000 万+ 数据集）。或者更改量化（二进制改为标量）：Qdrant 会自动重新量化。[量化](https://skills.qdrant.tech/md/documentation/manage-data/quantization/)


## 需要零停机时间

使用场景：生产环境必须保持可用。推荐用于大规模模型替换。

- 如果集群是 v1.18 或更高版本 **并且** 集合包含命名的向量：

  - 直接将新的向量字段添加到现有集合中 [更新向量架构](https://skills.qdrant.tech/md/documentation/manage-data/collections/?s=update-vector-schema)
  - 使用 `UpdateVectors` 在后台重新嵌入所有数据 [更新向量](https://skills.qdrant.tech/md/documentation/manage-data/points/?s=update-vectors)
  - 验证搜索质量后，删除旧的向量字段

- 如果集群是 v1.17 或更早版本 **或者** 集合不包含命名的向量：

- 使用新模型的维度和距离度量创建新集合
- 在后台将所有数据重新嵌入到新集合中
- 将应用程序指向集合别名，而不是直接指向集合名称
- 原子性地将别名切换到新集合 [切换集合](https://skills.qdrant.tech/md/documentation/manage-data/collections/?s=switch-collection)
- 验证搜索质量后，删除旧集合

小心，别名切换仅重定向查询。有效负载必须单独重新上传。


## 需要两个模型同时在线（并排运行）

使用场景：模型 A/B 测试、多模态（密集 + 稀疏），或在提交前评估新模型。

- 如果集群是 v1.18 或更高版本：

  - 直接将新的向量字段添加到现有集合中 [更新向量架构](https://skills.qdrant.tech/md/documentation/manage-data/collections/?s=update-vector-schema)
  - 使用 `UpdateVectors` 逐步填充新模型嵌入 [更新向量](https://skills.qdrant.tech/md/documentation/manage-data/points/?s=update-vectors)

- 如果集群是 v1.17 或更早版本：你不能向现有集合中添加命名的向量。创建一个预先定义了两个向量字段的新集合：

  - 创建一个同时定义了旧向量和新向量的新集合 [包含多个向量的集合](https://skills.qdrant.tech/md/documentation/manage-data/collections/?s=collection-with-multiple-vectors)
  - 从旧集合迁移数据，保留旧命名字段中的现有向量
  - 使用 `UpdateVectors` 逐步填充新模型嵌入 [更新向量](https://skills.qdrant.tech/md/documentation/manage-data/points/?s=update-vectors)
  - 通过使用 `using: "old_model"` 与 `using: "new_model"` 进行查询来比较质量
  - 满意后，将别名切换到新集合

在并排迁移期间将大型多向量（尤其是 ColBERT）与密集向量共存会降低所有查询的性能，即使那些仅使用密集向量的查询也是如此。在百万级数据点中，用户报告在移除 ColBERT 后，延迟从 13 秒降至 2 秒。在并排迁移期间将大型向量放在磁盘上。

如果你预计未来会进行模型迁移，请在集合创建时预先定义两个向量字段。


## 从密集搜索迁移到混合搜索

使用场景：向现有的仅支持密集向量的集合中添加稀疏/BM25 向量。最常见的迁移模式。

你不能向使用默认（未命名）密集向量的现有集合中添加稀疏向量。必须重新创建：

- 创建一个同时定义了密集和稀疏向量配置的新集合
- 使用密集和稀疏模型重新嵌入所有数据
- 迁移有效负载，切换别名

如果集合已经使用命名的密集向量并且是 v1.18 及以上版本，则直接添加稀疏向量字段，无需重新创建 [更新向量架构](https://skills.qdrant.tech/md/documentation/manage-data/collections/?s=update-vector-schema)。

块级别的稀疏向量与文档级别的稀疏向量具有不同的 TF-IDF 特性。迁移后测试检索质量，特别是对于没有去除停用词的非英文文本。


## 重新嵌入太慢

使用场景：数据集很大，重新嵌入是瓶颈。

- 使用 `update_mode: insert`（v1.17+）进行安全的幂等迁移 [更新模式](https://skills.qdrant.tech/md/documentation/manage-data/points/?s=update-mode)
- 使用 `with_vectors=False` 滚动旧集合，分批重新嵌入，然后插入到新集合中
- 并行分批上传（每个请求 64-256 个数据点，2-4 个并行流） [批量上传](https://skills.qdrant.tech/md/documentation/manage-data/bulk-upload/)
- 批量加载期间禁用 HNSW（设置 `indexing_threshold_kb` 非常高，加载后恢复）
- 对于 Qdrant Cloud 推理，切换模型是一个配置更改，而不是管道更改 [推理文档](https://skills.qdrant.tech/md/documentation/inference/)

对于 400GB+ 的数据集，预计需要数天。对于小数据集（<25MB），从源重新索引比使用迁移工具更快。


## 不要做的事情

- 假设你可以在 v1.17 或更早版本的服务器上向现有集合中添加命名的向量；首先检查你的服务器版本
- 在验证新集合之前删除旧集合
- 忘记在应用程序代码中更新查询嵌入模型
- 在使用别名切换时跳过有效负载迁移（别名重定向查询，它们不会复制数据）
- 在长时间迁移期间将 ColBERT 向量与密集向量共存（I/O 成本会降低所有查询）
- 在没有在块级别测试 BM25 质量之前迁移到混合搜索
