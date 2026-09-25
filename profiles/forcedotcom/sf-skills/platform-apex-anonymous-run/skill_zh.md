# platform-apex-anonymous-run

通过 `sf apex run --file` 在连接的 Salesforce 组织中运行匿名 Apex，捕获调试日志，并将编译时和运行时结果向开发者进行说明。

这是 VS Code 的 *Execute Anonymous Apex*（文档和选择）命令的代理端等效功能。

这项技能是**运行时，而非生成** — 编写 `.cls` / `.trigger` 文件请使用 `platform-apex-generate`；运行 Apex 单元测试请使用 `platform-apex-test-run`；进行深度调试日志分析（治理者分解、循环内 SOQL 检测）请交由 `platform-apex-logs-debug`。

---

## 工具限制

**仅使用 Bash 工具**来执行 `sf apex run`，并使用 `Write` 工具来暂存片段临时文件。**不要**使用 MCP 工具进行执行。

---

## 匿名 Apex 不是只读的

匿名 Apex 以运行用户的权限执行，**可以执行 DML、调用外部系统和平台事件**。除非开发者另有说明，否则将每次调用视为写入操作。

- **验证式脚本（推荐用于“测试这个”）：** 将主体包装在 savepoint + rollback 中，以保持组织状态不变：

  ```apex
  Savepoint sp = Database.setSavepoint();
  try {
      // ... 要测试的代码 ...
  } finally {
      Database.rollback(sp);
  }
  ```

- **生产环境提示：** 如果解析的 `<alias>` 指向生产环境（在 `sf org display --json` 中没有 scratch/sandbox 标记），在运行前显示清晰的警告。这仅是信息性提示 — 没有自动阻止。始终等待开发者明确“是，运行它”的指令，再执行破坏性脚本到生产环境。

- **不要运行你没有生成或未展示的匿名 Apex** — 如果开发者粘贴了片段，请回显并确认后再执行。

---

## 工作流程

### 第 1 步 — 确定目标组织

从配置中解析活动组织别名。如果 `target-org` 已设置，命令中可以省略 `--target-org` 标志，但始终在报告中记录使用的别名。

```bash
sf config get target-org --json
```

在此技能中，`<alias>` 是解析的别名或用户名。如果没有 `target-org` 设置，请询问开发者；不要无声地默认。如果组织未通过身份验证，请使用 `sf org login web` 重新身份验证或使用 `dx-org-switch` 技能切换组织。

### 第 2 步 — 解析输入模式

| 模式 | 当...时 | 操作 |
|---|---|---|
| **文件模式** | 开发者指向一个以 `.apex` 结尾的现有路径（或他们指定的任何路径） | 直接运行 `sf apex run --file <path>` |
| **片段模式** | 开发者将 Apex 代码粘贴到对话中 | 首先写入 `.sfdx/tmp/anon-<unix-ts>.apex`，然后运行 `sf apex run --file <tmp-path>` |

**为什么片段需要临时文件，而不是内联标志？** 当前的 `sf apex run` CLI 仅支持 `--file`（和交互式 stdin）。它**不**暴露 `--apex-code` 标志。即使在其他工具中支持内联代码，多行 Apex 通过内联传递会导致 shell 转义问题（字符串字面量中的单引号、反斜杠、嵌入的 `$`）。写入临时文件是处理任意片段的唯一可靠方法。

在偏离之前验证 CLI 标志：

```bash
sf apex run --help
```

支持的标志（截至编写时）：`--file/-f`、`--target-org/-o`、`--api-version`、`--json`、`--flags-dir`。**不要**编造标志 — 如果任务要求未列出的内容，请向开发者说明，而不是猜测。

### 第 3 步 — 设置跟踪标志（以获取有用的日志）

`sf apex run` 仅在为运行用户激活 `TraceFlag` 时返回调试日志（或附加流式尾随）。推荐路径 — 让开发者在另一个终端中尾随日志：

```bash
sf apex tail log --target-org <alias> --color
```

这会为运行用户自动创建一个短命的 TraceFlag，并在匿名 Apex 执行时流式传输日志。在报告中提及此内容，以便开发者可以复制/粘贴。

如果没有设置跟踪标志，`sf apex run` 仍会执行代码并返回编译/运行状态 — 但 *调试日志主体* 将缺失或稀疏。

### 第 4 步 — 片段模式：写入临时文件

仅适用于输入是粘贴的片段：

```bash
mkdir -p .sfdx/tmp
TS=$(date +%s)
# 通过 Write 工具将片段内容写入 .sfdx/tmp/anon-${TS}.apex，而不是通过 shell heredoc
```

使用代理的 `Write` 工具（而不是 heredoc），以保留片段的逐字内容 — heredoc 会使内容受额外的 shell 扩展影响。在报告中向开发者回显解析的临时路径。执行后不要自动清理临时文件 — 将其保留在 `.sfdx/tmp/` 下以供检查。`.sfdx/` 目录通常被 git 忽略。

### 第 5 步 — 执行

```bash
sf apex run --file <path> --target-org <alias> --json
```

- 始终传递 `--json`。人类格式输出会混淆编译和运行时错误。
- 如果 `target-org` 已配置，可以省略 `--target-org`，但记录使用的别名。
- 该命令在编译错误时退出非零。捕获 stdout 和解析的 JSON。

### 第 6 步 — 解析 JSON 响应

`sf apex run --json` 响应形状（相关字段）：

```json
{
  "status": 0,
  "result": {
    "compiled": true,
    "success": true,
    "compileProblem": "",
    "exceptionMessage": "",
    "exceptionStackTrace": "",
    "line": -1,
    "column": -1,
    "logs": "...完整的调试日志文本..."
  }
}
```

决策树：

| `compiled` | `success` | 含义 | 显示 |
|---|---|---|---|
| `false` | — | 编译失败 | `compileProblem`、`line`、`column`、违规的源代码行 |
| `true` | `false` | 运行时异常 | `exceptionMessage`、`exceptionStackTrace`，以及日志尾随 |
| `true` | `true` | 成功 | 脚本通过 `System.debug` 打印的内容（从 `logs` 中提取） |

`status !== 0`（顶层）表示 CLI 本身失败（未通过身份验证、文件未找到、网络）。显示原始错误并停止。

### 第 7 步 — 显示调试日志

- **短日志（< ~200 行）：** 在报告中的围栏代码块内内联日志主体。
- **长日志：** 将日志写入 `.sfdx/tmp/anon-<ts>.log` 并报告路径。内联包含最后 30 行作为尾随摘要。
- **空/缺失日志：** 可能没有活动的 TraceFlag。显示第 3 步的设置提示，然后继续返回的编译/运行状态。

在日志中突出显示以下模式：

| 模式 | 为什么重要 |
|---|---|
| `LIMIT_USAGE_FOR_NS` 行 | 治理者消耗快照 — 标记 SOQL/DML/CPU 接近限制 |
| `EXCEPTION_THROWN` | 未处理的异常在匿名块内 |
| `FATAL_ERROR` | 无法恢复的错误 — 显示完整的尾随块 |
| `SOQL_EXECUTE_BEGIN` 计数 > 1 在循环内 | SOQL-循环提示（交由 `platform-apex-logs-debug`） |
| `DML_BEGIN` 计数高 | 未批量的 DML 提示 |

不要尝试在此处进行完整日志解析 — 仅显示信号，然后交由 `platform-apex-logs-debug` 进行深度分析。

### 第 8 步 — 报告

```text
匿名 Apex 运行：<一行摘要 — 文件或片段，成功或失败>
组织：<别名>  (模式：scratch | sandbox | production)
来源：<文件路径或片段的临时路径>
编译：成功 | <错误 + 行:列>
运行时：成功 | <异常类型 + 消息>
限制：<CPU=x/10000ms, SOQL=y/100, DML=z/150>  (仅当日志包含 LIMIT_USAGE_FOR_NS 时)
日志：<内联 | 路径 .sfdx/tmp/anon-<ts>.log>
回滚：已应用 | 未应用 | 不适用
后续：<建议的后续操作>
```

---

## 示例

### 示例 1 — 文件模式

> "在默认组织上运行 `scripts/seed-test-data.apex`。"

1. 从 `sf config get target-org --json` 解析 `<alias>`。
2. 确认文件存在；如果不存在，停止并显示 `文件未找到`。
3. 运行 `sf apex run --file scripts/seed-test-data.apex --target-org <alias> --json`。
4. 解析 JSON。报告编译/运行状态、日志尾随和组织模式。
5. 建议： "如果这个脚本种下了真实数据，并且你想在不持久化的情况下验证，请使用回滚包装（片段模式）重新运行。"

### 示例 2 — 片段模式（读取查询）

> "执行 `System.debug([SELECT count() FROM Account]);` 并告诉我计数。"

1. 解析 `<alias>`。
2. 回显片段；确认。
3. 将片段写入 `.sfdx/tmp/anon-<ts>.apex`（Write 工具）。
4. 运行 `sf apex run --file .sfdx/tmp/anon-<ts>.apex --target-org <alias> --json`。
5. 解析 `result.logs`；提取 `USER_DEBUG` 行以获取计数。
6. 报告： "Account 计数 = N。来源：`.sfdx/tmp/anon-<ts>.apex`（保留以供参考）。"

### 示例 3 — 带回滚的验证

> "测试这个 Apex 是否正确插入 Contact，然后回滚。"

1. 解析 `<alias>`。如果生产环境，运行前显示提示。
2. 包装开发者的片段：

   ```apex
   Savepoint sp = Database.setSavepoint();
   try {
       // ---- 开发者片段开始 ----
       Contact c = new Contact(LastName = 'Smoke', Email = 'smoke@example.com');
       upsert c Email;
       System.debug('Upserted: ' + c.Id);
       // ---- 开发者片段结束 ----
   } finally {
       Database.rollback(sp);
       System.debug('Rolled back savepoint.');
   }
   ```

3. 写入 `.sfdx/tmp/anon-<ts>.apex`，执行，解析 JSON。
4. 报告编译/运行状态、日志中的插入 Id，以及 `Rollback: applied`。

---

## 失败模式

| 症状 | 原因 | 恢复 |
|---|---|---|
| `No authorization information found for ...` | 组织未通过身份验证，或别名错误 | 运行 `sf org list --json`；使用 `sf org login web` 重新身份验证或使用 `dx-org-switch` |
| `ENOENT: no such file or directory, open '<path>'` | `.apex` 文件路径错误或相对于错误的 cwd | 确认绝对路径；重新运行 |
| `compileProblem` 非空在 JSON 中 | Apex 编译错误 | 显示 `compileProblem`、`line`、`column`；显示该行；建议修复 |
| `success: false` 且有 `exceptionMessage` | 匿名块内的运行时异常 | 显示异常类型 + 消息 + 堆栈；如果存在，显示治理者计数 |
| `logs` 字段即使成功也为空 | 运行用户没有活动的 `TraceFlag` | 告知开发者在另一个终端运行 `sf apex tail log --target-org <alias>`，然后重新运行 |
| `status !== 0` 且没有 `result` | 执行前的 CLI / 网络 / 身份验证失败 | 显示原始 stderr；不要盲目重试 |
| 未识别的标志错误 | 安装的 CLI 与规范漂移 | 重新检查 `sf apex run --help`；不要编造标志 |

---

## 规则

- 始终传递 `--json`。
- 始终从配置或开发者解析 `<alias>`；不要硬编码。
- 不要使用 `--apex-code` 风格的内联标志 — 当前 CLI 不支持它们，且对 shell 友好性差。始终通过 `--file` 执行。
- 始终在执行前向开发者回显粘贴的片段以供确认。
- 对于验证式脚本，默认使用 `Database.setSavepoint()` + `Database.rollback()`。
- 对于生产环境，显示提示但不要自动阻止 — 开发者负责。
- 不要自动删除 `.sfdx/tmp/` 下的临时文件。
- 此技能执行匿名 Apex；它不编写、部署或测试 `.cls`/`.trigger` 文件。对于这些，交由 `platform-apex-generate`、部署技能或 `platform-apex-test-generate`。
- 对于深度日志分析，交由 `platform-apex-logs-debug`。
