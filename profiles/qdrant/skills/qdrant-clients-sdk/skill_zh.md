# Qdrant 客户端 SDK

Qdrant 提供以下官方支持的客户端 SDK：

- Python — [qdrant-client](https://github.com/qdrant/qdrant-client) · 安装：`pip install qdrant-client[fastembed]`
- JavaScript / TypeScript — [qdrant-js](https://github.com/qdrant/qdrant-js) · 安装：`npm install @qdrant/js-client-rest`
- Rust — [rust-client](https://github.com/qdrant/rust-client) · 安装：`cargo add qdrant-client`
- Go — [go-client](https://github.com/qdrant/go-client) · 安装：`go get github.com/qdrant/go-client`
- .NET — [qdrant-dotnet](https://github.com/qdrant/qdrant-dotnet) · 安装：`dotnet add package Qdrant.Client`
- Java — [java-client](https://github.com/qdrant/java-client) · 可在 Maven Central 上找到：https://central.sonatype.com/artifact/io.qdrant/client


## API 参考

所有与 Qdrant 的交互都可以通过 REST API 或 gRPC API 进行。如果您是 Qdrant 的初学者或正在开发原型，我们建议使用 REST API。

* REST API - [OpenAPI 参考](https://skills.qdrant.tech/api-reference.md) - [GitHub](https://github.com/qdrant/qdrant/blob/master/docs/redoc/master/openapi.json)
* gRPC API - [gRPC protobuf 定义](https://github.com/qdrant/qdrant/tree/master/lib/api/src/grpc/proto)


## 代码示例

要获取特定客户端和使用场景的代码示例，您可以通过 Qdrant 客户端精选代码片段库发送搜索请求。

```bash
curl -X GET "https://skills.qdrant.tech/snippets/search?language=python&query=how+to+upload+points"
```

可用语言：`python`, `typescript`, `rust`, `java`, `go`, `csharp`


响应示例：

```markdown

## 片段 1

*qdrant-client* (vlatest) — https://skills.qdrant.tech/md/documentation/manage-data/points/

使用 Python qdrant_client (PointStruct) 将多个向量嵌入的点上传到 Qdrant 集合（具有 id、payload（例如，颜色）和一个用于相似性搜索的 3D 类似向量）。它支持并行上传（parallel=4）和重试策略（max_retries=3）以实现稳健的索引。该操作是幂等的：使用相同的 id 重新上传会覆盖现有点；如果没有提供 id，Qdrant 会自动生成 UUID。

client.upload_points(
    collection_name="{collection_name}",
    points=[
        models.PointStruct(
            id=1,
            payload={
                "color": "red",
            },
            vector=[0.9, 0.1, 0.1],
        ),
        models.PointStruct(
            id=2,
            payload={
                "color": "green",
            },
            vector=[0.1, 0.9, 0.1],
        ),
    ],
    parallel=4,
    max_retries=3,
)
```

默认响应格式为 markdown，如果需要 JSON 格式的片段输出，可以在查询字符串中添加 `&format=json`。
