# HTTP Outcalls
[Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral) 的 HTTP Outcalls 扩展。

## 概述

此技能涵盖了后端可以器对外的 HTTP 请求要求，包括 GET、HEAD、POST、PUT、DELETE 和 PATCH。在与外部 API 或服务集成时，请使用它。

## 关键要求

遵循以下规则：
- **必须使用提供者强制的有界 API 请求。** 请求必须通过标识符、分页、时间范围、地理区域、结果数量或其他适合功能的服务器端界限来限制响应。
  将每个响应限制在最多 10_000 条条目和最多 1 MB，如有需要则进行分页。
- **必须选择与功能匹配的界限。** 这五个界限不能互换。当功能通过用户提供的内容（航班号、订单 ID、股票代码、邮政编码）查找一个实体时，唯一正确的选择是标识符界限。将集合分页以查找该实体是反模式，而不是替代方案：无论每页有多小，工作量仍然与整个集合成正比。分页是用户故意分页的列表，而不是用于搜索。
- **必须将每个界限放入实际的 Motoko http 请求中。** 仅用于本地测试的界限不会保护可以器。
- **永远不要在可以器中获取无界集合并在其中进行过滤。** 预期的响应大小、典型流量或当前较小的数据集不是界限。
- **如果提供者无法执行响应界限并提供所需数据，则必须拒绝 API 或缩小功能。** 不要实现已知不安全的回退方案。
- **在本地使用 curl 实现。** 确保一对一的 curl 调用成功并返回应用程序消耗的每个字段。当 Motoko 代码更改时，重新进行本地 curl 测试。
- **使用 `check_canister_api_compliance` 检查界限。** 它探测端点并测量响应是否符合这些限制，并且它在部署门后面运行，因此它拒绝的端点无法发布。

上述 1 MB 和 10_000 条条目限制是模块自身的上限——`defaultMaxResponseBytes` 是 1 MB——`check_canister_api_compliance` 按照这两个数字进行测量。它比它们更早拒绝：当 URL 不包含服务器端界限时，一旦探测到的响应超过字节上限的四分之一或超过 1_000 条条目，它就会阻止。这个范围是危险的，因为它通过一次 curl 通过后就会增长，直到可以器在解析有效负载时超出每条消息指令预算。根据更严格的界限进行设计：在服务器端限制请求。

## 选择错误的界限

航班查找需要一个航班号并必须返回一架飞机。获取 `https://opensky-network.org/api/states/all`——全球所有在飞的飞机，大约 10-13k 行——并在 Motoko 中扫描解析结果以查找一个呼号是错误的。可以器下载并解析世界上的每条记录来回答单个查找，并且消息被拒绝：
`IC0522: Canister exceeded the limit of 40000000000 instructions for single message execution`。代码中没有任何错误——URL 是有效的，解析可以编译，并且一次性的 curl 返回 200。

这是一个指令限制，而不是字节限制。选择较小的页面大小没有帮助：可以器仍然遍历整个集合来查找一行。

提供者已经提供了正确的界限。`?icao24=<hex>` 在同一端点上标识符界限：千字节，一架飞机，一条记录要解析。

# 后端

对于必须在后端执行的 HTTP Outcalls：

现有的模块 `mo:caffeineai-http-outcalls/outcall.mo` 为 IC 支持的每个 HTTP 方法提供了一个通用的有界请求函数，以及向后兼容的 GET 和 POST 辅助函数。

```mo:caffeineai-http-outcalls/outcall
module {
  public type TransformationInput = {
    context : Blob;
    response : IC.HttpRequestResult;
  };
  public type TransformationOutput = IC.HttpRequestResult;
  public type Transform = query TransformationInput -> async TransformationOutput;
  public type Header = {
    name: Text;
    value: Text;
  };
  public type Method = {
    #get;
    #head;
    #post;
    #put;
    #delete;
    #patch;
  };
  public type Request = {
    url : Text;
    method : Method;
    headers : [Header];
    body : ?Blob;
    maxResponseBytes : Nat64;
    transform : Transform;
  };
  public type Response = IC.HttpRequestResult;
  public let defaultMaxResponseBytes : Nat64;

  // 辅助函数，用于 IC 在 HTTP Outcalls 中使用的转换回调。
  public func transform(input : TransformationInput) : TransformationOutput;

  // 支持 GET、HEAD、POST、PUT、DELETE 和 PATCH 的通用有界请求。
  public func httpRequest(request : Request) : async Response;

  // HTTP GET 请求，带有转换回调函数。
  public func httpGetRequest(url : Text, extraHeaders: [Header], transform : Transform) : async Text;

  // HTTP POST 请求，指定转换回调。
  public func httpPostRequest(url : Text, extraHeaders: [Header], body : Text, transform : Transform) : async Text;
};
```

当需要状态、标头、自定义响应限制或 GET 或 POST 之外的方法时，使用 `httpRequest`。`maxResponseBytes` 可以设置较低的限额；该模块将每个请求限制在 `defaultMaxResponseBytes`（1 MB）。该模块使用 `is_replicated = ?false` 执行每个 HTTP Outcall；调用者无法启用复制执行。向后兼容的辅助函数仍然是简单 GET 的最短路径：

```motoko filepath=src/backend/main.mo
import Text "mo:core/Text";
import OutCall "mo:caffeineai-http-outcalls/outcall";

actor {
  public query func transform(input: OutCall.TransformationInput) : async OutCall.TransformationOutput {
    OutCall.transform(input);
  };

  func setItemActive() : async OutCall.Response {
    await OutCall.httpRequest({
      url = "https://api.example.com/items/123";
      method = #patch;
      headers = [{ name = "Content-Type"; value = "application/json" }];
      body = ?("{\"active\":true}".encodeUtf8());
      maxResponseBytes = 100_000;
      transform;
    });
  };

  func makeGetOutcall(url: Text) : async Text {
    await OutCall.httpGetRequest(url, [], transform);
  };
};
```

通过 `httpPostRequest` 的 POST 使用类似。

## 验证每个外部 API 请求

在考虑 HTTP Outcall 完成之前，使用 `curl` 在本地执行等效请求。不要仅依赖记忆中的 API 文档或 Motoko 代码编译。以下每个检查都是必需的。如果任何检查失败，HTTP Outcall 不完整，**必须** 不得继续部署。

1. **必须测试 Motoko 中实现的精确请求：** 相同的 HTTP 方法、API 版本、端点路径、查询参数、标头和正文。测试相关端点或添加实现不使用的参数不是有效的验证。
2. **必须通过每个转换到 API 请求的代表性用户输入端到端跟踪**，然后测试精确的请求结果。例如，如果用户输入一个标识符，但提供者期望另一个标识符格式，请端到端验证该映射。仅调用提供者的基本或列表端点是不足的。
3. **必须验证消耗的响应契约。** 使用 `curl --fail-with-body --silent --show-error` 运行请求。验证成功状态以及应用程序消耗的每个响应字段和类型。仅仅是有效的 JSON 响应是不够的。
4. **必须在实现使用的精确 URL 和方法上运行 `check_canister_api_compliance`。** 它测量响应是否符合 Outcall 字节上限和条目界限，并报告 URL 是否服务器端有界，机械地并在部署门后面运行，因此它拒绝的端点无法发布。当它拒绝端点时，选择兼容的公共 API 或诚实地缩小功能；不要实现无界获取所有请求并在可以器中过滤。

响应界限是此检查的工作，而不是 curl 的工作。上述检查是它无法为您完成的检查：它探测端点，而不是应用程序，因此它永远不会知道应用程序读取哪些响应字段或用户键入了什么内容来生成 URL。

如果请求失败或任何上述检查未满足，请检查状态和响应正文。使用网络搜索检查提供者当前的官方 API 文档和发布或迁移说明。确认当前 API 版本、端点、参数名称和格式、必需的标头和请求正文。不要猜测失败。修复 Motoko 请求以匹配工作 REST 请求并重新运行 `curl`；重复直到所有检查通过，然后重新运行后端检查。在缺少或失败的任何必要检查的情况下，永远不要报告完成。

典型失败线索：`400` 表示参数或正文形状无效；`404`/`410` 通常表示过时的端点或 API 版本；`405` 表示方法错误；`415` 表示内容类型错误。在确认请求与当前官方文档一致后，将 `429` 和 `5xx` 响应视为配额或提供者可用性问题。
