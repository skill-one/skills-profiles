本技能教你如何发现并阅读当前的 Remotion 文档。
如果此内容与当前场景不相关，请加载 Remotion 最佳实践。

## 搜索文档

使用 Algolia 搜索 API 查找相关的文档页面：

```
POST https://plsduol1ca-dsn.algolia.net/1/indexes/*/queries?x-algolia-api-key=3e42dbd4f895fe93ff5cf40d860c4a85&x-algolia-application-id=PLSDUOL1CA
Content-Type: application/x-www-form-urlencoded

{
  "requests": [
    {
      "query": "<your search query>",
      "indexName": "remotion",
      "params": "attributesToRetrieve=[\"hierarchy.lvl0\",\"hierarchy.lvl1\",\"hierarchy.lvl2\",\"url\"]&hitsPerPage=10"
    }
  ]
}
```

每个命中项都包含一个指向文档页面的 `url` 字段。

## 以 Markdown 格式获取页面

在任意 Remotion 文档 URL 后追加 `.md`，即可获取其 Markdown 源码（节省 token）：

```
https://www.remotion.dev/docs/use-video-config.md
https://www.remotion.dev/docs/sequence.md
https://www.remotion.dev/docs/lambda/rENDERmediaonlambda.md
```

## 工作流程

1. 在 Algolia 中搜索所需的概念或 API。
2. 从搜索结果中选择最相关的 URL。
3. 使用 `.md` 后缀获取每个 URL。
4. 使用当前的文档进行实现，而非依赖记忆中的 API 知识。
