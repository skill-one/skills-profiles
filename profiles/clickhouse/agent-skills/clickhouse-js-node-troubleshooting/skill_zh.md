# ClickHouse Node.js 客户端故障排除

参考：https://clickhouse.com/docs/integrations/javascript

> **⚠️ 仅限 Node.js 运行时。** 本技巧涵盖仅在 **Node.js 运行时** 运行的 `@clickhouse/client` 包——包括 **Next.js Node 运行时** API 路径、React 服务器组件、服务器操作以及标准 Node.js 进程。**请勿**将本技巧应用于浏览器客户端组件、Web Workers、**Next.js Edge 运行时**、Cloudflare Workers 或任何 `@clickhouse/client-web` 的使用场景。对于浏览器/边缘环境，正确的包是 `@clickhouse/client-web`。

---

## 如何使用本技巧

1. **识别问题** — 将症状与下方的问题索引匹配，并阅读相应的参考文件。
2. **先进行诊断** — 在提供解决方案之前，先解释可能导致问题的原因。
3. **注意版本限制** — 标记如果解决方案需要最低客户端版本，并检查用户提供的版本是否符合要求。
4. **仅询问缺失信息** — 如果解决方案与版本相关而您不知道用户版本，则询问；否则立即提供帮助。

---

## 问题索引

从下方列表中识别用户的问题，并阅读相应的参考文件以获取详细的故障排除步骤。

| 问题                                      | 症状                                                                                                                                                                     | 参考文件                     |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| **Socket 挂起 / ECONNRESET**            | `socket hang up`，`ECONNRESET`，间歇性连接中断，长时间运行的查询超时                                                                               | `reference/socket-hangup.md`       |
| **数据类型不匹配**                   | 大整数被返回为字符串，小数精度丢失，日期/日期时间插入失败，`CANNOT_PARSE_INPUT_ASSERTION_FAILED` 插入 UUID 到 `UInt128` 列中 | `reference/data-types.md`          |
| **只读用户错误**                  | 使用响应压缩时 `readonly=1` 用户出现错误                                                                                                               | `reference/readonly-users.md`      |
| **代理 / 路径名 URL 混淆**         | 选择错误的数据库名称，在带有路径前缀的代理后面请求失败                                                                                                  | `reference/proxy-pathname.md`      |
| **TLS / 证书错误**               | TLS 握手失败，证书验证问题，相互 TLS 配置                                                                                                    | `reference/tls.md`                 |
| **压缩无效**                | 请求或响应未激活 GZIP 压缩                                                                                                                    | `reference/compression.md`         |
| **日志未显示任何内容**           | 无日志输出，需要自定义日志器集成                                                                                                                                | `reference/logging.md`             |
| **查询参数未插值**      | 参数化查询无效，SQL 注入问题                                                                                                                    | `reference/query-params.md`        |
| **FORMAT 子句 / `SHOW POLICIES` 错误** | 重复 `FORMAT` 的语法错误，或者即使提供了格式，`SHOW [ROW] POLICIES` 也失败                                                                         | `reference/query-format-clause.md` |

---

## 仍然卡住？

- [JS 客户端源代码 + 完整示例](https://github.com/ClickHouse/clickhouse-js/tree/main/examples)
- [ClickHouse JS 客户端文档](https://clickhouse.com/docs/integrations/javascript)
- [ClickHouse 支持的格式](https://clickhouse.com/docs/interfaces/formats)
