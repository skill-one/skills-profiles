您对 Cloudflare Workers API、类型和配置的了解可能已过时。在编写或审查 Workers 代码时，**优先使用检索而非预训练**。

以项目安装的版本、生成的类型和 Wrangler 兼容性设置为现有代码的基础。检索相关的 Cloudflare 文档，以验证 API、配置、运行时行为和限制声明。

## 参考资料

阅读与任务相关的章节：

| **参考** | **适用场景** |
|-----------|----------------------|
| \[Configuration and observability](references/configuration.md) | 兼容性日期、绑定、生成的类型、密钥、日志和追踪 |
| \[Runtime patterns](references/runtime-patterns.md) | 流式传输、Promise 生命周期、请求状态、服务调用、安全及运行时测试 |
| \[Platform API checks](references/platform-apis.md) | Handler 签名、平台类、绑定访问和序列化 |

对于缺失的证据，请查阅 [Workers 最佳实践](https://developers.cloudflare.com/workers/best-practices/workers-best-practices/) 或在 [Cloudflare 文档目录](https://developers.cloudflare.com/directory/) 中查找受影响的产品。使用已安装的 Wrangler 模式配置字段。更新的类型包不能取代项目配置的 target。

## 保持兼容性日期为最新

为新 Workers 使用当前日期。鼓励对现有 Workers 进行定期更新，审查兼容性变更并运行相关测试。将现有行为与配置的日期和标记进行核对；参见 [兼容性指导](references/configuration.md#keep-compatibility_date-current)。

## 启用可观测性

在创建或准备 Worker 用于生产时，启用 [Workers Logs](https://developers.cloudflare.com/workers/observability/logs/workers-logs/) 和 [Traces](https://developers.cloudflare.com/workers/observability/traces/)。将 `observability.enabled` 和 `observability.traces.enabled` 设置为 `true`；仅设置顶层设置并不能启用追踪。使用结构化的 JSON 日志，并配置工作负载的采样。在审查过程中，标记缺失的日志或追踪。参见 [配置示例](references/configuration.md#enable-workers-logs-and-traces)。

## 需标记的反模式

| **反模式** | **后果及推荐模式** |
|-------------|---------------------|
| \`\`\`
| `await response.text()` 或类似对无界数据进行的缓冲操作 | 可能导致 Worker 内存耗尽；[流式传输大型或无界请求体](references/runtime-patterns.md#stream-request-and-response-bodies)。 |
| 源码或配置中的硬编码密钥 | 会通过版本控制泄露凭证；使用 Wrangler 密钥。 |
| 使用 `Math.random()` 生成安全敏感的令牌或 ID | 数值可预测；使用 `crypto.randomUUID()` 或 `crypto.getRandomValues()`。 |
| 启动异步任务时未进行 await、返回或将任务挂载到 `ctx.waitUntil()` | 工作可能被丢弃且错误被遗漏；将其与请求或后台任务生命周期关联。 |
| 模块级别的可变请求状态 | 会在请求间泄露数据，并可能导致 I/O 所有权错误；显式传递请求状态。 |
| 使用 Cloudflare REST API 调用通过 Worker 绑定可获取的操作 | 会增加网络和身份验证开销；使用可用的绑定。 |
| 将 `ctx.passThroughOnException()` 用作通用错误处理 | 会通过将错误转发到源站来掩盖 Worker 故障；使用显式错误处理及结构化的错误响应。 |
| 手写的 `Env` 与 Wrangler 绑定重复 | 可能与配置不一致；使用 `wrangler types` 生成绑定类型。 |
| 直接字符串比较密钥值 | 可能暴露时序差异；使用 [Web Crypto 比较模式](references/runtime-patterns.md#use-web-crypto-for-secure-token-generation)。 |
| 解构 `ctx` 方法，例如 `const { waitUntil } = ctx` | 会丢失接收者；调用 `ctx.waitUntil(...)`。 |
| 在 `Env` 或处理器参数上使用 `any` | 会隐藏绑定和处理器契约错误；使用项目生成的及平台类型。 |
| 使用 `as unknown as T` 强制平台类型匹配 | 会隐藏不兼容；修复底层契约。 |
| 用 `implies` 代替扩展平台基类 | 不会继承运行时行为、`this.ctx` 或 `this.env`；使用适当的基类。 |
| 在平台类方法中使用未绑定的 `env.X` | 绑定可通过 `this.env.X` 访问；参见 [绑定访问模式](references/platform-apis.md#binding-access--the-most-common-error)。 |
| 对 Queues、Workflow 步骤、存储和 WebSockets 应用统一的序列化规则 | 可能拒绝有效载荷或接受不支持的内容；检查 [特定 API 和编码](references/platform-apis.md#serialization-boundaries)。 |

## 验证

使用项目针对受影响 Workers 行为的现有检查：对绑定或处理器契约变更进行类型检查，并针对行为变更运行相关运行时测试。保留必要的仓库检查；小幅编辑无需进行全面 Workers 审计。

## 范围

该技能涵盖 Workers 特有的最佳实践和代码审查。相关主题：

- **持久对象**：加载 `durable-objects` 技能
- **工作流**：参见 [工作流规则](https://developers.cloudflare.com/workflows/build/rules-of-workflows/)
- **Wrangler CLI 命令**：加载 `wrangler` 技能
