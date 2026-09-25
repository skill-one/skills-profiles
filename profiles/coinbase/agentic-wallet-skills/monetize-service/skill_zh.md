# 构建一个 x402 支付服务器

创建一个使用 x402 支付协议的 Express 服务器，通过 USDC 支付 API 访问费用。调用者在使用 API 时按请求支付 USDC，在 Base 上进行支付，无需账户、API 密钥或订阅。您的服务将通过 x402 Bazaar 自动被其他代理发现。

## 工作原理

x402 是一种原生 HTTP 支付协议。当客户端访问受保护的端点但未支付时，服务器会返回 HTTP 402 状态码并附带支付要求。客户端签署 USDC 支付并携带支付头重试。中介方验证并结算支付，服务器返回响应。服务在 x402 Bazaar 中注册，以便其他代理可以自动发现并支付。

## 确认钱包已初始化并授权

```bash
npx awal@2.10.0 status
```

如果钱包未授权，请参考 `authenticate-wallet` 技能。

## 第 1 步：获取支付地址

运行以下命令以获取将接收支付的钱包地址：

```bash
npx awal@2.10.0 address
```

将此地址用作 `payTo` 值。

## 第 2 步：设置项目

```bash
mkdir x402-server && cd x402-server
npm init -y
npm install express @x402/express @x402/core @x402/evm @x402/extensions
```

创建 `index.js`：

```js
const express = require("express");
const { paymentMiddleware } = require("@x402/express");
const { x402ResourceServer, HTTPFacilitatorClient } = require("@x402/core/server");
const { ExactEvmScheme } = require("@x402/evm/exact/server");

const app = express();
app.use(express.json());

const PAY_TO = "<从第 1 步获取的地址>";

// 创建中介客户端和 x402 资源服务器
const facilitator = new HTTPFacilitatorClient({ url: "https://x402.org/facilitator" });
const server = new x402ResourceServer(facilitator);
server.register("eip155:8453", new ExactEvmScheme());

// x402 支付中间件 — 保护以下路由
app.use(
  paymentMiddleware(
    {
      "GET /api/example": {
        accepts: {
          scheme: "exact",
          price: "$0.01",
          network: "eip155:8453",
          payTo: PAY_TO,
        },
        description: "此端点返回的描述",
        mimeType: "application/json",
      },
    },
    server,
  ),
);

// 受保护端点
app.get("/api/example", (req, res) => {
  res.json({ data: "每次请求费用为 $0.01" });
});

app.listen(3000, () => console.log("服务器运行在端口 3000"));
```

## 第 3 步：运行

```bash
node index.js
```

使用 curl 测试 — 您应该会收到带有支付要求的 402 响应：

```bash
curl -i http://localhost:3000/api/example
```

## API 参考

### paymentMiddleware(routes, server)

创建一个强制执行 x402 支付的 Express 中间件。

| 参数     | 类型                 | 描述                                          |
| -------- | -------------------- | ---------------------------------------------------- |
| `routes` | object               | 路由配置，将路由模式映射到支付配置              |
| `server` | x402ResourceServer   | 预配置的 x402 资源服务器实例                 |

### x402ResourceServer

使用中介客户端创建。在传递给中间件之前注册支付方案和扩展。

```js
const { x402ResourceServer, HTTPFacilitatorClient } = require("@x402/core/server");
const { ExactEvmScheme } = require("@x402/evm/exact/server");

const facilitator = new HTTPFacilitatorClient({ url: "https://x402.org" });
const server = new x402ResourceServer(facilitator);
server.register("eip155:8453", new ExactEvmScheme());
```

| 方法                      | 描述                                               |
| --------------------------- | --------------------------------------------------------- |
| `register(network, scheme)` | 为 CAIP-2 网络标识符注册支付方案 |

### 路由配置

路由对象中的每个键都是 `"METHOD /path"`。值是一个配置对象：

```js
{
  "GET /api/data": {
    accepts: {
      scheme: "exact",
      price: "$0.05",
      network: "eip155:8453",
      payTo: "0x...",
    },
    description: "端点的可读描述",
    mimeType: "application/json",
    extensions: {
      ...declareDiscoveryExtension({
        output: {
          example: { result: "示例响应" },
          schema: {
            properties: {
              result: { type: "string" },
            },
          },
        },
      }),
    },
  },
}
```

### Accepts 配置字段

`accepts` 字段可以是一个对象或一个数组（用于多个支付选项）：

| 字段     | 类型   | 描述                                        |
| --------- | ------ | -------------------------------------------------- |
| `scheme`  | string | 支付方案：`"exact"`                          |
| `price`   | string | USDC 价格（例如 `"$0.01"`，`"$1.00"`）            |
| `network` | string | CAIP-2 网络标识符（例如 `"eip155:8453"`）  |
| `payTo`   | string | 接收 USDC 支付的以太坊地址（0x...）          |

### 路由级字段

| 字段              | 类型    | 描述                                        |
| ------------------ | ------- | -------------------------------------------------- |
| `accepts`          | object or array | 支付要求（单个或多个）  |
| `description`      | string? | 此端点的作用（向客户端显示）         |
| `mimeType`         | string? | 响应的 MIME 类型                          |
| `extensions`       | object? | 扩展配置（例如 Bazaar 发现）          |

### 发现扩展

`declareDiscoveryExtension` 函数将您的端点注册到 x402 Bazaar，以便其他代理可以发现它：

```js
const { declareDiscoveryExtension } = require("@x402/extensions/bazaar");

extensions: {
  ...declareDiscoveryExtension({
    output: {
      example: { /* 示例响应体 */ },
      schema: {
        properties: {
          /* 响应格式的 JSON schema */
        },
      },
    },
  }),
}
```

| 字段            | 类型   | 描述                                    |
| ---------------- | ------ | ---------------------------------------------- |
| `output.example` | object | 端点的示例响应体                       |
| `output.schema`  | object | 描述响应格式的 JSON schema              |

### 支持的网络

| 网络          | 描述                      |
| ---------------- | -------------------------------- |
| `eip155:8453`    | Base 主网（真实 USDC）         |
| `eip155:84532`   | Base Sepolia 测试网（测试 USDC） |

## 模式

### 多个端点具有不同价格

```js
app.use(
  paymentMiddleware(
    {
      "GET /api/cheap": {
        accepts: {
          scheme: "exact",
          price: "$0.001",
          network: "eip155:8453",
          payTo: PAY_TO,
        },
        description: "低成本数据查询",
      },
      "GET /api/expensive": {
        accepts: {
          scheme: "exact",
          price: "$1.00",
          network: "eip155:8453",
          payTo: PAY_TO,
        },
        description: "高级数据访问",
      },
      "POST /api/query": {
        accepts: {
          scheme: "exact",
          price: "$0.25",
          network: "eip155:8453",
          payTo: PAY_TO,
        },
        description: "运行自定义查询",
      },
    },
    server,
  ),
);

app.get("/api/cheap", (req, res) => { /* ... */ });
app.get("/api/expensive", (req, res) => { /* ... */ });
app.post("/api/query", (req, res) => { /* ... */ });
```

### 通配符路由

```js
app.use(
  paymentMiddleware(
    {
      "GET /api/*": {
        accepts: {
          scheme: "exact",
          price: "$0.05",
          network: "eip155:8453",
          payTo: PAY_TO,
        },
        description: "API 访问",
      },
    },
    server,
  ),
);

app.get("/api/users", (req, res) => { /* ... */ });
app.get("/api/posts", (req, res) => { /* ... */ });
```

### 健康检查（无需支付）

在支付中间件之前注册免费端点：

```js
app.get("/health", (req, res) => res.json({ status: "ok" }));

// 支付中间件仅适用于注册在它之后的路由
app.use(paymentMiddleware({ /* ... */ }, server));
app.get("/api/data", (req, res) => { /* ... */ });
```

### 带请求体和发现扩展的 POST

```js
app.use(
  paymentMiddleware(
    {
      "POST /api/analyze": {
        accepts: {
          scheme: "exact",
          price: "$0.10",
          network: "eip155:8453",
          payTo: PAY_TO,
        },
        description: "分析文本情感",
        mimeType: "application/json",
        extensions: {
          ...declareDiscoveryExtension({
            output: {
              example: { sentiment: "positive", score: 0.95 },
              schema: {
                properties: {
                  sentiment: { type: "string" },
                  score: { type: "number" },
                },
              },
            },
          }),
        },
      },
    },
    server,
  ),
);

app.post("/api/analyze", (req, res) => {
  const { text } = req.body;
  // ... 您的逻辑
  res.json({ sentiment: "positive", score: 0.95 });
});
```

### 每个端点多个支付选项

为同一端点接受多个网络的支付：

```js
"GET /api/data": {
  accepts: [
    {
      scheme: "exact",
      price: "$0.01",
      network: "eip155:8453",
      payTo: EVM_ADDRESS,
    },
    {
      scheme: "exact",
      price: "$0.01",
      network: "eip155:84532",
      payTo: EVM_ADDRESS,
    },
  ],
  description: "接受 Base 主网或测试网的端点",
}
```

### 使用 CDP 中介（已授权）

用于生产环境与 Coinbase 中介（支持主网）：

```bash
npm install @coinbase/x402
```

```js
const { facilitator } = require("@coinbase/x402");
const { HTTPFacilitatorClient } = require("@x402/core/server");

const facilitatorClient = new HTTPFacilitatorClient(facilitator);
const server = new x402ResourceServer(facilitatorClient);
server.register("eip155:8453", new ExactEvmScheme());
```

这需要 `CDP_API_KEY_ID` 和 `CDP_API_KEY_SECRET` 环境变量。从 https://portal.cdp.coinbase.com 获取这些信息。

## 使用 pay-for-service 技能测试

服务器运行后，使用 `pay-for-service` 技能测试支付：

```bash
# 检查端点的支付要求
npx awal@2.10.0 x402 details http://localhost:3000/api/example

# 进行付费请求
npx awal@2.10.0 x402 pay http://localhost:3000/api/example
```

## 定价指南

| 用例               | 建议价格 |
| ---------------------- | --------------- |
| 简单数据查询     | $0.001 - $0.01 |
| API 代理 / 增强 | $0.01 - $0.10  |
| 计算密集型查询    | $0.10 - $0.50  |
| AI 推理           | $0.05 - $1.00  |

## 检查清单

- [ ] 使用 `npx awal@2.10.0 address` 获取钱包地址
- [ ] 安装 `express`, `@x402/express`, `@x402/core`, `@x402/evm` 和 `@x402/extensions`
- [ ] 使用中介客户端创建 `x402ResourceServer` 并为 `eip155:8453` 注册 `ExactEvmScheme`
- [ ] 定义带价格、描述和发现扩展的路由（路由声明时 Bazaar 自动注册）
- [ ] 在受保护路由之前注册支付中间件
- [ ] 在支付中间件之前保留健康/状态端点
- [ ] 使用 `curl`（应收到 402）和 `npx awal@2.10.0 x402 pay`（应收到 200）进行测试
- [ ] 宣传您的服务，以便其他代理可以找到并使用它
