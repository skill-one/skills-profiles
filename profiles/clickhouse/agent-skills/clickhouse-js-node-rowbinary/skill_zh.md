# ClickHouse JS RowBinary Codec Generator for Node.js

该技能生成数据传输格式的双向：**读取器**（解码字节→值）和**写入器**（编码值→字节，镜像）。给定任务通常只需要其中一侧。此文件是共享的入口点——格式门控加上双向共通的原则；针对每个方向的决策、指导以及每个类型的参考表存在于两个兄弟文件中。

**选择你的方向——只阅读你需要的那一侧：**

- **将 ClickHouse 的 `RowBinary*` 响应解码为 JS 值** → **[reader.md](reader.md)**。流式处理与完整缓冲区、行对象与列式、固定与动态模式，以及每个类型的读取器参考。
- **将 JS 值编码为发送给 ClickHouse 的 `RowBinary` 负载** → **[writer.md](writer.md)**。`Sink`/`writeX` 构建块、`writeRows` 流式处理，以及每个类型的写入器参考。

每个类型的代码是真实的，按方向在 `src/readers/` 和 `src/writers/` 下拆分。

## 首先：RowBinary 真的是正确的格式吗？

RowBinary 存在是为了吞吐量，但它**不自动是最快路径**——在提交定制解析器之前，先匹配数据形状与格式。

**当结果主要是字符串/JSON 类似值，你需要整体消费时**（随机访问几乎每个字段、在这些值上运行字符串/正则方法、将值视为文本），优先选择 `JSON*` 格式（例如 `JSONEachRow`）。V8 的原生 `JSON.parse` 是高度优化的 C++，构建 JS 字符串和对象比 JS 层级的 RowBinary 解码器更快；将其与 HTTP 响应压缩（`gzip` / `zstd`，它们会粉碎 JSON 的重复键）配合使用，传输成本也会降低。

**当结果主要由以下内容主导时，RowBinary 明显更胜一筹：**

- **宽数值** — `Int128`/`Int256`/`UInt128`/`UInt256`、`Decimal128`/`Decimal256`。
- **二进制/固定宽度块** — `IPv4`、`IPv6`、`UUID`、`FixedString`。
- **高容量固定宽度数值列** 通常，其中每个值都是一个 `DataView` 读取。

**当列式加载数据和客户端分析是主要目标时**（折叠/扫描/过滤列、将类型化数组传递给 Worker 或 WASM），优先选择 `Native` 格式。`Native` 是按列主序的，因此它直接加载到每列一个类型化数组中，无需转置。

若需帮助选择和消费 `JSON*` 格式（或 CSV / TSV），请使用 **`clickhouse-js-node-coding`** 技能。

## 核心指导（双向）

无论你是生成读取器还是写入器，这些原则都适用；特定侧的操作指导在 [reader.md](reader.md) / [writer.md](writer.md) 中。

- **仅小端模式。** RowBinary 是小端模式；目标 x86/ARM。使用 `DataView` 访问器读取和写入每个多字节数时，将 **字面量** `true` 传递给 `littleEndian` 标志。

- **先正确，再优化。** 首先从纯类型 API 构建一个正确的编解码器。只有在它正确（并经过测试）之后，才进行专门化。不要在正确性之前就预设性能假设。

- **对通用/复合类型进行单例化。** 对每个类型组合生成专门化、内联的代码，而不是在已知类型的情况下将函数作为参数传递。

- **内联叶操作。** 每个类型的 `readX`/`writeX` 函数是正确的、可组合的参考；生成的编解码器应内联其主体，而不是调用它们，以便行循环是直线，没有每个字段的间接引用（因此固定宽度合并可以折叠偏移计算）。

- **按列注释类型。** 内联会消除类型结构，因此在每个列的编码/解码块上方添加简短注释，命名它处理的 ClickHouse 类型。

- **共享临时缓冲区不是可重入的。** 某些热方法将模块级临时缓冲区用作写入后读取对——正确是因为访问完全同步。在填充和读取它之间 `async`/`yield` 边界会破坏值。

- **默认使用 TypeScript。** 除非用户明确要求纯 JavaScript，否则生成 TypeScript 代码和辅助工具。

## 实例分析

在 [EXAMPLES.md](EXAMPLES.md) 中列出了六个端到端实例，具有真实的性能提升。

## 不在范围内

- **JSON / CSV / TSV / Parquet 解析** → 使用 `clickhouse-js-node-coding`。
- **连接错误、卡死、类型不匹配** → 使用 `clickhouse-js-node-troubleshooting`。
- **浏览器 / Web Worker / Edge** → `@clickhouse/client-web`。

## 仍然卡住？

- [ClickHouse RowBinary 格式](https://clickhouse.com/docs/interfaces/formats#rowbinary)
- [ClickHouse 数据类型](https://clickhouse.com/docs/sql-reference/data-types)
- [ClickHouse JS 客户端文档](https://clickhouse.com/docs/integrations/javascript)
