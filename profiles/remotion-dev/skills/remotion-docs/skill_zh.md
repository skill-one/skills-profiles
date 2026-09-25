这个技能教你如何发现和阅读当前的 Remotion 文档。
如果不相关，请加载 Remotion 最佳实践。

## 搜索文档

使用 Algolia 搜索 API 查找相关文档页面：

```
POST https://plsduol1ca-dsn.algolia.net/1/indexes/*/queries?x-algolia-api-key=3e42dbd4f895fe93ff5cf40d860c4a85&x-algolia-application-id=PLSDUOL1CA
Content-Type: application/x-www-form-urlencoded

{
  "requests": [
    {
      "query": "<你的搜索查询>",
      "indexName": "remotion",
      "params": "attributesToRetrieve=[\"hierarchy.lvl0\",\"hierarchy.lvl1\",\"hierarchy.lvl2\",\"url\"]&hitsPerPage=10"
    }
  ]
}
```

每个命中项都包含一个 `url` 字段，指向文档页面。

## 以 Markdown 格式获取页面

在 Remotion 文档 URL 后追加 `.md` 以获取其 Markdown 源代码（节省代币）：

```
https://www.remotion.dev/docs/use-video-config.md
https://www.remotion.dev/docs/sequence.md
https://www.remotion.dev/docs/lambda/rendermediaonlambda.md
```

## 工作流程

1. 在 Algolia 中搜索你需要的概念或 API。
2. 从结果中选择最相关的 URL。
3. 使用 `.md` 后缀获取每个 URL。
4. 使用当前文档而不是记忆中的 API 知识进行实现。
