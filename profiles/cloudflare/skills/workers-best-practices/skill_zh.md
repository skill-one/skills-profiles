您的 Cloudflare Workers API、类型和配置知识可能已经过时。编写或审查 Workers 代码时，**优先考虑获取（retrieval）而非预训练（pre-training）**。

以项目已安装的版本、生成的类型和 Wrangler 兼容性设置为现有代码的基准。获取相关的 Cloudflare 文档以验证 API、配置、运行时行为和限制声明。

## 参考文献

阅读与任务相关的部分：

| 参考文献 | 使用时机 |
|-----------|----------------|
| [配置和可观察性](references/configuration.md) | 兼容性日期、绑定、生成类型、密钥、日志和跟踪 |
| [运行时模式](references/runtime-patterns.md) | 流式传输、Promise 生命周期、请求状态、服务调用、安全和运行时测试 |
| [平台 API 检查](references/platform-apis.md) | 处理器签名、平台类、绑定访问和序列化 |

对于缺失的证据，请参考 [Workers 最佳实践](https://developers.cloudflare.com/workers/best-practices/workers-best-practices/) 或在 [Cloudflare 文档目录](https://developers.cloudflare.com/directory/) 中找到受影响的产品。使用已安装的 Wrangler 模式来配置字段。更新的类型包不会取代项目的配置目标。

## 保持兼容性日期最新

为新 Workers 使用当前日期。鼓励定期更新现有 Workers，审查兼容性更改并运行相关测试。评估现有行为与其配置日期和标志；参见 [保持兼容性日期最新](references/configuration.md#keep-compatibility_date-current)。

## 启用可观察性

创建或为生产准备 Worker 时，启用 [Workers 日志](https://developers.cloudflare.com/workers/observability/logs/workers-logs/) 和 [跟踪](https://developers.cloudflare.com/workers/observability/traces/)。将 `observability.enabled` 和 `observability.traces.enabled` 设置为 `true`；仅顶层设置不会启用跟踪。使用结构化 JSON 日志记录，并为工作负载配置采样。在审查期间，标记缺失的日志或跟踪。参见 [配置示例](references/configuration.md#enable-workers-logs-and-traces)。

## 需要标记的反模式

| 反模式 | 后果和推荐模式 |
|-------------|-----------------------------------|
| `await response.text()` 或对无界数据的类似缓冲 | 可能耗尽 Worker 内存；[流式传输大型或无界正文](references/runtime-patterns.md#stream-request-and-response-bodies)。 |
| 源代码或配置中的硬编码密钥 | 通过版本控制泄露凭证；使用 Wrangler 密钥。 |
| 使用 `Math.random()` 生成安全敏感的令牌或 ID | 可预测的值；使用 `crypto.randomUUID()` 或 `crypto.getRandomValues()`。 |
| 未等待、返回或附加到 `ctx.waitUntil()` 的异步工作 | 工作可能被丢弃且错误被忽略；将其与请求或后台工作生命周期绑定。 |
| 模块级可变请求状态 | 跨请求泄露数据并可能导致 I/O 所有权错误；显式传递请求状态。 |
| 用于可通过 Worker 绑定执行的操作的 Cloudflare REST API 调用 | 增加网络和身份验证开销；使用可用的绑定。 |
| 作为通用错误处理的 `ctx.passThroughOnException()` | 通过转发到源隐藏 Worker 故障；使用显式错误处理和结构化错误响应。 |
| 复制 Wrangler 绑定的手写 `Env` | 可能与配置脱节；使用 `wrangler types` 生成绑定类型。 |
| 直接字符串比较密钥值 | 可能暴露时间差异；使用 [Web Crypto 比较模式](references/runtime-patterns.md#use-web-crypto-for-secure-token-generation)。 |
| 解构 `ctx` 方法，例如 `const { waitUntil } = ctx` | 丢失接收者；调用 `ctx.waitUntil(...)`。 |
| `Env` 或处理器参数上的 `any` | 隐藏绑定和处理器合同错误；使用项目的生成和平台类型。 |
| 使用 `as unknown as T` 强制平台类型匹配 | 隐藏不兼容性；修复底层合同。 |
| 使用 `implements` 替代扩展平台基类 | 不会继承运行时行为、`this.ctx` 或 `this.env`；使用适当的基类。 |
| 平台类方法中的未绑定 `env.X` | 绑定可通过 `this.env.X` 获取；参见 [绑定访问模式](references/platform-apis.md#binding-access--the-most-common-error)。 |
| 将一个序列化规则应用于队列、工作流步骤、存储和 WebSocket | 可能拒绝有效负载或接受不支持的负载；检查 [特定 API 和编码](references/platform-apis.md#serialization-boundaries)。 |

## 验证

使用项目现有的检查来验证受影响 Worker 的行为：检查绑定或处理器合同更改的类型，并为行为更改运行相关运行时测试。保留必需的存储库检查；狭窄的编辑不需要完整的 Worker 审计。

## 范围

本技能涵盖 Workers 特定的最佳实践和代码审查。对于相关主题：

- **持久对象**：加载 `durable-objects` 技能
- **工作流**：参见 [工作流规则](https://developers.cloudflare.com/workflows/build/rules-of-workflows/)
- **Wrangler CLI 命令**：加载 `wrangler` 技能
