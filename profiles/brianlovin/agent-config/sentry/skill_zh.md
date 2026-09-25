# Sentry 集成

使用 Sentry 进行错误监控和性能追踪的指南。

## 异常捕获

在 try/catch 块中使用 `Sentry.captureException(error)`：

```javascript
try {
  await riskyOperation();
} catch (error) {
  Sentry.captureException(error);
  throw error;
}
```

## 性能追踪

为按钮点击、API 调用和函数调用等有意义的操作创建跨度。

### UI 操作

```javascript
function handleClick() {
  Sentry.startSpan(
    { op: "ui.click", name: "提交表单" },
    (span) => {
      span.setAttribute("formId", formId);
      submitForm();
    }
  );
}
```

### API 调用

```javascript
async function fetchData(id) {
  return Sentry.startSpan(
    { op: "http.client", name: `GET /api/items/${id}` },
    async () => {
      const response = await fetch(`/api/items/${id}`);
      return response.json();
    }
  );
}
```

## 配置 (Next.js)

Sentry 初始化文件：
- `sentry.client.config.ts` - 客户端
- `sentry.server.config.ts` - 服务器端
- `sentry.edge.config.ts` - 边缘运行时

使用 `import * as Sentry from "@sentry/nextjs"` 导入 - 无需在其他文件中初始化。

### 基本设置

```javascript
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  enableLogs: true,
});
```

### 带控制台日志

```javascript
Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  integrations: [
    Sentry.consoleLoggingIntegration({ levels: ["log", "warn", "error"] }),
  ],
});
```

## 结构化日志

使用 `logger.fmt` 进行带变量的模板字符串：

```javascript
const { logger } = Sentry;

logger.trace("开始连接", { database: "users" });
logger.debug(logger.fmt`缓存未命中: ${userId}`);
logger.info("更新了个人资料", { profileId: 345 });
logger.warn("达到速率限制", { endpoint: "/api/data" });
logger.error("支付失败", { orderId: "order_123" });
logger.fatal("连接池耗尽", { activeConnections: 100 });
```
