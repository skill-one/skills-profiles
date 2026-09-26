# Dynatrace JavaScript 运行时

Dynatrace JS 运行时是一个服务器端 AppEngine 沙盒，用于执行 JavaScript/TypeScript。

## 函数契约

每个入口点必须导出一个默认的异步函数：

```js
export default async function () {
  // ...
  return result;
}
```

需要使用 ES 模块语法。接受 TypeScript（类型注解、接口、泛型）。不支持其他导出形式。

## 参考

从这里开始，然后仅加载您需要的文件。

| 文件 | 加载时机 |
|------|-------------|
| [references/limits-and-restrictions.md](references/limits-and-restrictions.md) | 超时 / 内存 / I/O 配额；禁止的内容 (`eval`, WebSocket, 套接字, 文件系统) |
| [references/apis-and-modules.md](references/apis-and-modules.md) | 可用的 Web API 和 Node.js 兼容模块（fetch, crypto, streams, buffer, …） |
| [references/fetch.md](references/fetch.md) | 调用内部 `/platform/...` API 或外部 URL，凭证保险库，出站允许列表 |
| [references/sdk.md](references/sdk.md) | 任何 `@dynatrace-sdk/*` 包 — 索引会引导您到正确的每个 SDK 文件 |

## 使用 dtctl 运行函数

使用 `dtctl exec function` 在不部署应用程序的情况下运行 JS 运行时代码。

```dtctl
# 运行内联代码
dtctl exec function --code 'export default async function() { return "hello" }'

# 从文件运行
dtctl exec function -f script.js

# 传递 JSON 输入 — 解析后的对象是函数的参数
dtctl exec function -f script.js --payload '{"key":"value"}'
```

函数可以接受一个可选参数。`--payload` 被解析并直接作为该参数传递 — 它不会包裹在 `event.payload` 字段中：

```js
export default async function(payload) {
  // 使用 --payload '{"key":"value"}', payload 是 {"key": "value"}
  return payload.key;
}
```

加载 **`dynatrace-control`** 技能进行身份验证设置、上下文切换，以及完整的 `exec function` 参考。
