# k6 脚本生成

> **效率提示**：这是一个简单的线性流程（阅读示例 → 修改 → 保存 → 验证 → 审查）。待办事项列表只会镜像标题，不会增加价值，因此跳过规划开销，直接执行步骤。
>
> **与代理无关**：以下步骤描述的是功能，而不是特定工具。如果一个步骤说“获取一个 URL”或“写入一个文件”，请使用您的代理提供的相应功能（例如，一个网络获取工具、一个文件写入工具，或 shell 中的 `curl`/`tee`）。

---

## 第 1 步：选择正确的示例文件

仅读取与用户请求匹配的文件。示例提供结构化的脚手架——正确的脚手架、选项形状和导入模式。

| 用户需求 | 读取此文件 |
|---------|-----------|
| HTTP REST、认证流程、批量请求 | `examples/http.js` |
| HTML 解析，使用 parseHTML、SharedArray | `examples/html.js` |
| WebSocket | `examples/websocket.js` |
| gRPC | `examples/grpc.js` |
| 浏览器自动化 | `examples/browser.js` |
| 浏览器 + 功能测试 / `expect()` / k6-testing | `examples/functional.js`（浏览器场景） |
| 功能/集成测试，`expect()`，k6-testing | `examples/functional.js` |
| 自定义指标、执行模块、handleSummary、每个 VU 迭代 | `examples/metrics.js` |
| 负载模式、所有执行器（斜坡、到达率、每个 VU 等） | `examples/executors.js` |
| 云运行，`--local-execution`，`cloud` 选项 | `examples/cloud.js` |
| 加密（HMAC、MD5、SHA256）或编码（base64） | `examples/crypto-encoding.js` |
| xk6-faker | `examples/ext-faker.js` |
| xk6-redis | `examples/ext-redis.js` |
| xk6-sql / sqlite3 / postgres | `examples/ext-sql.js` |
| xk6-exec | `examples/ext-exec.js` |
| xk6-dns | `examples/ext-dns.js` |
| xk6-tls | `examples/ext-tls.js` |
| xk6-tcp | `examples/ext-tcp.js` |
| xk6-crawler | `examples/ext-crawler.js` |

示例文件位于此 `SKILL.md` 旁边的 `examples/` 目录中。

**当请求匹配多行时**（例如，“浏览器” + “功能测试”），优先选择断言风格与意图匹配的行。如果用户说“功能测试”、“断言”、“验证”或“expect”，即使测试涉及浏览器，也使用 `functional.js`——它展示了带有自动重试的浏览器匹配器的 `expect()`。对于不强调正确性断言的浏览器负载/性能测试，使用 `browser.js`。

---

## 第 2 步：修改示例

将加载的示例作为起点。根据用户的精确需求进行修改：
- 更改端点、VU 数量、持续时间、阈值
- 添加或删除场景步骤
- 将函数和变量重命名为匹配领域
- 每个表达式必须完整且可运行——没有 `{ ... }`、`// TODO` 或存根
- **匹配请求——不要过度构建。** 精确实现请求的内容。不要添加自定义请求标签、额外的 `sleep()` 调用、额外的端点或用户未请求的 `options`。未请求的复杂性会降低质量并减少对规范的遵循。

对于多场景脚本（浏览器 + HTTP、云）：使用命名的 `scenarios`，其中 `exec` 指向单独导出的函数。

---

## 第 3 步：使用文档填充空白（仅当需要时）

示例涵盖了常见模式。直接从它进行修改。**完全跳过此步骤**，如果示例提供了您所需的一切。

**仅当以下情况时才使用文档**：
- 用户要求示例中未演示的 API 或选项，**或**
- 您不确定确切的签名、选项名称或返回类型

当存在空白时，首先建立文档命令（会话内一次性）。

`k6 x docs` CLI 仅在检测到 TTY 时才渲染内容。由于代理以非交互方式运行，请将每个调用用 `script` 包装以分配伪 TTY，并将 ANSI 去除的内容管道输出到 stdout：

```bash
# 一次性检测操作系统（macOS 与 Linux 的 `script` 标志不同）：
if [[ "$(uname -s)" == "Darwin" ]]; then
  DOCS_CMD="script -q /dev/null k6 x docs"
else
  DOCS_CMD="script -qc 'k6 x docs' /dev/null"
fi

# 验证它是否工作——应打印主题列表，而不是“浏览文件”指南：
$DOCS_CMD 2>/dev/null | head -5
```

如果输出仍然显示“k6 文档是一个 markdown 文件目录”，则 TTY 包装器不起作用。回退到 **网络文档** 在 `https://grafana.com/docs/k6/latest/` 下——使用您的代理具有的任何网络获取功能（内置获取工具，或 shell 中的 `curl`）获取页面。

如果 `k6 x docs` 完全失败（命令未找到、配置或 404 错误），请阅读 `SETUP.md`——它涵盖了 k6 v1.7.0+ 上的自动配置和旧版本的 xk6 手动构建。

然后查找您需要的内容：

```bash
$DOCS_CMD <路径>              # 例如. javascript-api k6-http
$DOCS_CMD <路径> --depth 2
$DOCS_CMD search <术语>
```

常见 CLI 路径和 2 调用策略在 `docs-guidance.md` 中。

**不要使用 unpkg、@types/k6 或任何 npm 类型定义 URL。**

---

## 第 4 步：保存

每个脚本的第一行必须是一个生成注释。首先获取当前的 UTC 时间戳（文件内容依赖于它，因此这不能与写入并行）：

```bash
date -u +%Y-%m-%dT%H:%M:%SZ
```

然后将其包含为第一行：
```javascript
// 由 grafana-k6 生成于 2026-03-25T22:02:20.203Z
```

保存到 `k6/scripts/<描述性名称>.js`。使用小写连字符命名法（kebab-case）文件名。如果您的文件写入功能不会自动创建父目录，请先执行 `mkdir -p k6/scripts`。

**磁盘上的脚本文件是交付物**——始终写入它。不要以仅在聊天中显示的脚本结束任务：步骤 5–7（验证、审查、展示）都需要文件存在于 `k6/scripts/<名称>.js`。如果写入失败，请在继续之前重试它。

---

## 第 5 步：验证

自上而下匹配——第一个匹配的行获胜：

| 脚本类型 | 命令 |
|---------|------|
| 导入 `k6/browser` | `k6 run k6/scripts/<名称>.js` |
| 任何 `ramping-vus` 或 `*-arrival-rate` 场景 | `k6 inspect k6/scripts/<名称>.js`——完整运行将针对目标执行整个负载配置 |
| 其他命名的 `executor:` 块（短场景） | `k6 run k6/scripts/<名称>.js` |
| 其他所有内容（HTTP、WS、gRPC） | `k6 run --vus 1 --iterations 1 k6/scripts/<名称>.js` |

**什么算作通过**：对于功能和浏览器脚本，验证仅在退出码为 0 *且* 摘要显示没有失败的检查或 `expect()` 错误时才通过——一个带有失败断言完成的脚本没有被验证。k6 的错误输出命名了失败的定位器或断言（以及它等待的内容）；使用它来修复选择器或逻辑。对于负载测试，退出码 0 是通过，在负载下的纯阈值违规（退出码 99）是可以接受的。

如果验证失败：读取 stderr，修复根本原因，最多重试 **3 次**。3 次失败后，展示错误并询问用户如何继续（或，在无人值守运行时，交付最佳尝试并清楚地报告未解决的错误）。

---

## 第 6 步：最佳实践审查

### 一般检查（所有脚本）

根据以下规则审查脚本。检查清单是权威的——如果对特定规则不确定，请查阅文档（`$DOCS_CMD best-practices` 或 `https://grafana.com/docs/k6/latest/using-k6/`）。

- **`export const options` 包含现实的 VUs/持续时间。** 默认 VUs/持续时间使测试在默认情况下就有意义。
- **为每个负载测试定义 `thresholds`。** 没有阈值，即使性能回归，运行也不会在 CI 中失败，这违背了运行负载测试的目的。至少包括 `http_req_duration` 和 `http_req_failed`（或协议等效项）。纯功能测试——仅包含 `expect()` 的单次迭代脚本——可以跳过此步骤。
- **在封闭模型（基于 VU）的负载测试中包含 `sleep()`。** `sleep()` 代表用户思考时间；没有它，VUs 比任何真实用户更快地冲击端点，导致吞吐量膨胀并挤占测试系统。这适用于基于 VU 的 HTTP、WebSocket、gRPC、加密和扩展脚本。**开放模型执行器**（`constant-arrival-rate`、`ramping-arrival-rate`）已经以目标速率调整迭代，因此通常不需要 `sleep()`——它只会占用 VU 而不改变提供的负载。浏览器脚本使用 `page.waitForTimeout()` 代替；单次迭代的功能测试和一次性连接/演示脚本可以跳过它。在事件驱动的 WebSocket 脚本中，将 `sleep()` 放在 `close` 处理器内（见 `examples/websocket.js`）——在主函数体中睡眠会阻塞事件循环，在消息到达之前就会发生。
- **断言每个响应。** **浏览器脚本**：使用 k6-testing 的 `expect()`——它自动重试定位器并替换 `waitFor()` + `isVisible()` + `check()` 链。如果您需要在异步浏览器函数内跟踪指标的 `check()`，标准的 `k6` 中的 `check` 工作得很好**只要谓词是同步的**——首先等待值，然后检查它。只有在谓词本身必须 `await` 某些内容时，才使用 k6-utils 包装器（`https://jslib.k6.io/k6-utils/1.5.0/index.js`）：裸 `async` 谓词返回 Promise，始终为真，因此检查会无声通过。**HTTP/gRPC/WS 脚本**：使用 `check()` 进行指标跟踪的断言，或使用 `expect()` 进行功能测试。无声失败比大声失败更糟。
- **浏览器脚本**：将交互包装在 `try/finally` 中，并在 `finally` 中使用 `page.close()`，以便即使断言抛出，页面也能清理。
- **gRPC 脚本**：将迭代中的调用包装在 `try/finally` 中，并在 `finally` 块中调用 `client.close()`，以便即使检查在迭代中途抛出，连接也会被释放。
- **WebSocket 脚本**：将接收到的消息的 `JSON.parse` 包装在 `try/catch` 中——服务器可以发送非 JSON 帧，一个坏帧不应杀死 VU。
- **顶层没有 `let`/`var`**——使用 `const`，因为模块范围状态在 VU 之间共享，并且在此处可变性几乎总是错误。
- **没有弃用的导入**——使用 `k6/websockets` 进行 WebSocket；`k6/ws` 和 `k6/experimental/websockets` 都已弃用。

### 负载和断点测试

- **断点测试：斜坡提供的负载，而不是 VUs。** 使用开放模型执行器（`ramping-arrival-rate`），以便请求速率与系统有多慢无关；封闭模型（`ramping-vus`）会随着延迟上升而自我限制，并掩盖断裂点。将阈值与 `abortOnFail: true` 和较短的 `delayAbortEval` 配对，以便在跨越 SLO 时运行停止（并报告）。
- **跟踪 SLO 相关的自定义指标** 进行报告：每个端点的延迟（`Trend`）、错误 `Rate` 和任何领域计数器——以及一个 `handleSummary`，它显示 p95/p99、吞吐量（req/s）和错误率。见 `examples/executors.js` 和 `examples/metrics.js`。
- **混合协议 + 浏览器负载测试**：将浏览器流程包装在 `try/catch` 中，并将失败记录到自定义错误指标，而不是让 `expect()` 抛出——一个有故障的浏览器迭代不应中止长时间的协议负载运行。

### 浏览器脚本——推荐实践

如果脚本导入 `k6/browser`，请阅读 `browser-best-practices.md` 并应用所有检查。修复问题并重新验证。

---

## 第 7 步：展示结果

1. 完整脚本及文件路径
2. 验证输出
3. 最佳实践注释（发现的问题，或“所有检查通过”）
4. 建议的运行命令

```bash
k6 run --vus 10 --duration 30s k6/scripts/api-load-test.js
k6 run k6/scripts/browser-test.js
k6 cloud run k6/scripts/cloud-test.js
k6 cloud run --local-execution k6/scripts/hybrid-test.js
./k6-with-faker run k6/scripts/faker-test.js
K6_BROWSER_HEADLESS=true k6 run k6/scripts/browser-test.js
```

## 第 8 步：执行

如果用户确认，运行该命令。
