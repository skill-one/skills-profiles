## 何时使用

当您需要深入的 Node.js 内部知识时，请使用此技能，包括：
- C++ 扩展开发
- V8 引擎调试
- libuv 事件循环问题
- 构建系统问题
- 编译失败
- 引擎级别的性能优化
- 理解 Node.js 核心架构
- 编写或审查 `nodejs/node` 提交和拉取请求描述

## 如何使用

阅读单个规则文件以获取详细的解释和代码示例：

### V8 引擎

- [rules/v8-garbage-collection.md](rules/v8-garbage-collection.md) - 清除、标记-清除、标记-压缩、代际 GC
- [rules/v8-hidden-classes.md](rules/v8-hidden-classes.md) - 隐藏类、内联缓存、优化
- [rules/v8-jit-compilation.md](rules/v8-jit-compilation.md) - TurboFan、优化/去优化模式

### libuv

- [rules/libuv-event-loop.md](rules/libuv-event-loop.md) - 事件循环阶段、计时器、I/O、空闲、检查、关闭
- [rules/libuv-thread-pool.md](rules/libuv-thread-pool.md) - 线程池大小、阻塞操作、UV_THREADPOOL_SIZE
- [rules/libuv-async-io.md](rules/libuv-async-io.md) - 异步 I/O 模式、句柄、请求

### 本地扩展

- [rules/napi.md](rules/napi.md) - N-API 开发、ABI 稳定性、异步工作线程
- [rules/node-addon-api.md](rules/node-addon-api.md) - C++ 包装模式、最佳实践
- [rules/native-memory.md](rules/native-memory.md) - 缓冲区处理、外部内存、防止内存泄漏

### 核心模块内部

- [rules/streams-internals.md](rules/streams-internals.md) - Node.js 流在 C++ 层面的工作原理
- [rules/net-internals.md](rules/net-internals.md) - TCP/UDP 实现、套接字处理
- [rules/fs-internals.md](rules/fs-internals.md) - libuv 文件系统操作、同步与异步
- [rules/crypto-internals.md](rules/crypto-internals.md) - OpenSSL 集成、性能考虑
- [rules/child-process-internals.md](rules/child-process-internals.md) - IPC、spawn、fork 实现
- [rules/worker-threads-internals.md](rules/worker-threads-internals.md) - SharedArrayBuffer、Atomics、MessageChannel

### JavaScript 内部

- [rules/primordials.md](rules/primordials.md) - **使用 primordials 防止原型污染（`lib/internal/` 所需）**

### 构建 & 贡献

- [rules/build-and-test-workflow.md](rules/build-and-test-workflow.md) - **编辑-构建-检查-测试循环（从这里开始）**
- [rules/pre-commit-lint.md](rules/pre-commit-lint.md) - **每次提交必须强制进行 lint、格式化以及 `core-validate-commit` 验证，以确保 CI 一次性通过**
- [rules/configure.md](rules/configure.md) - `./configure` 标志用于调试构建、ASan、Ninja 等
- [rules/build-system.md](rules/build-system.md) - gyp、ninja、make、跨平台编译
- [rules/cli-options.md](rules/cli-options.md) - 添加 CLI 选项并限制实验性模块
- [rules/contributing.md](rules/contributing.md) - 如何为 Node.js 核心做出贡献、流程
- [rules/commit-and-pr-guideline.md](rules/commit-and-pr-guideline.md) - 提交消息和 PR 描述风格、跟踪信息、DCO 签名和验证
- [rules/reviewing-prs.md](rules/reviewing-prs.md) - 审查 PR 以确保正确性、清晰性和贡献质量

### 文档

- [rules/documentation.md](rules/documentation.md) - **更新 doc/api/*.md 文件：结构、链接顺序、错误文档、代码示例限制**

### 调试 & 分析

- [rules/debugging-native.md](rules/debugging-native.md) - gdb、lldb、调试 C++ 扩展
- [rules/profiling-v8.md](rules/profiling-v8.md) - --prof、--trace-opt、--trace-deopt、火焰图
- [rules/memory-debugging.md](rules/memory-debugging.md) - 堆快照、内存泄漏检测

## 说明

### Node.js 贡献编写

在起草 `nodejs/node` 提交或拉取请求时，请阅读
[rules/commit-and-pr-guideline.md](rules/commit-and-pr-guideline.md)。
使用子系统前缀的简短标题和简洁、客观的文本。首先描述具体行为，解释变更的原因，并省略宣传、模板化标题、逐文件描述和支持不足的声明。包含贡献者的 DCO 签名，并且永远不要添加 `PR-URL:` 或 `Reviewed-By:` — 这些是在变更合并时添加的。使用
`npx core-validate-commit --no-validate-metadata <sha>` 在 `nodejs/node`
检出中验证结果。

### 强制：测试前必须重新构建

Node.js 通过 `js2c` 在编译时将 `lib/` JavaScript 文件嵌入二进制文件中。**在 `src/` 或 `lib/` 的任何变更后，您必须重新构建才能运行测试。** 没有重新构建，测试将针对过时的代码运行，结果无意义。

```
编辑 src/ 或 lib/  →  make -j$(nproc)  →  make lint  →  然后测试
```

永远不要跳过重新构建步骤。编辑后永远不要在构建之前运行 `./node test/...`。

在开始工作之前，**询问用户**他们的构建配置（Make vs Ninja、调试 vs 发布、他们使用的 configure 标志）。不要假设特定的设置。大多数情况下，`./configure` 已经运行，只需要 `make -j$(nproc)` 即可重新构建。

### 强制：每次提交前必须进行 lint 和格式化

Node.js 在每个非草稿拉取请求上运行 `Linters` CI 工作流，并且在 Unix 上 `make test` 运行**没有** lint。在每次 `git
commit` 之前运行 `make lint` — 对于 C++ 变更，还需要 `make format-cpp` — 这样 lint 任务在第一次 CI 运行时通过，而不是导致强制推送和另一个完整周期。

```bash
make -j$(nproc)                                        # 首先重新构建
make lint                                              # JS、C++、MD、文档、YAML

# 仅 C++ 变更 — 使用合并基形式，这是 CI 检查的形式：
CLANG_FORMAT_START="$(git merge-base HEAD upstream/main)" make format-cpp
git --no-pager diff --exit-code                        # 必须为空

git add -A && git commit -s                            # -s 是强制性的
npx core-validate-commit --no-validate-metadata HEAD
```

因为变更看起来很简单而跳过任何步骤，或者使用 "将在后续修复 lint" 提交。

**仅 `make format-cpp` 不够。** 它默认为
`CLANG_FORMAT_START=HEAD` 并仅格式化*暂存*的变更，而 `format-cpp` CI 任务格式化合并基以来的所有内容，并在任何结果差异时失败 — 所以分支中先前的未格式化代码在本地通过并在 CI 中失败。始终使用上面显示的合并基形式。

**每个提交必须使用 `git commit -s` 创建。** `-s` 标志添加了 `Signed-off-by:` 跟踪信息，证明开发者原始权利。没有它，`core-validate-commit` 的 `signed-off-by` 规则将失败，PR 无法合并。签名必须是贡献者的姓名和电子邮件 — 永远不要使用工具或 AI 身份签名，也永远不要编造他人的身份。如果你忘记了，使用 `git commit --amend --signoff` 修正。

`make lint` 运行 `lint-js`、`lint-cpp`、`lint-addon-docs`、`lint-md` 和
`lint-yaml` — 它不涵盖所有 CI lint 任务。Python (`make lint-py`)、shell (`tools/lint-sh.mjs .`)、C++ 格式化和提交消息验证是单独的任务。有关完整门禁和 CI 任务到命令映射，请参阅 [rules/pre-commit-lint.md](rules/pre-commit-lint.md)。

使用 `core-validate-commit` 验证每个提交消息，始终使用
`--no-validate-metadata` — 元数据验证默认启用，并强制在合并后存在的跟踪信息。**永远不要在您编写的提交中添加 `PR-URL:` 或
`Reviewed-By:`；合并过程会添加它们。**

有关完整工作流，包括 configure 标志、lint 目标和测试命令，请参阅 [rules/build-and-test-workflow.md](rules/build-and-test-workflow.md)。

### 核心知识领域

在这些领域应用对 Node.js 内部的深入知识：

- **核心架构**：Node.js 核心模块及其 C++ 实现、V8 GC 和 JIT、libuv 事件循环机制、线程池行为、启动/模块加载生命周期
- **本地开发**：N-API、node-addon-api 和 NAN 扩展开发；V8 C++ API 句柄管理；内存安全；使用 gdb/lldb 调试本地代码
- **构建系统**：node-gyp、gyp、ninja、make；跨平台编译；链接器错误；依赖问题；平台特定考虑（Windows、macOS、Linux、嵌入式）
- **性能 & 调试**：事件循环分析、JS 和本地代码中的内存泄漏检测、CPU 火焰图、V8 优化/去优化跟踪

### 快速参考调试命令

**V8 优化跟踪：**
```bash
node --trace-opt --trace-deopt script.js
# 检查点：在继续分析之前确认没有意外的去优化警告
node --prof script.js && node --prof-process isolate-*.log > processed.txt
```

**事件循环延迟检测：**
```bash
node --trace-event-categories v8,node,node.async_hooks script.js
```

**本地扩展调试 (gdb)：**
```bash
gdb --args node --napi-modules ./build/Release/addon.node
# 在 gdb 中：
run
bt        # 在崩溃时回溯
# 检查点：在应用修复之前验证回溯是否显示预期的调用位置
```

**堆快照用于内存泄漏：**
```bash
node --inspect script.js   # 然后打开 chrome://inspect，获取堆快照
# 检查点：在修复前后比较两个连续的堆快照以确认泄漏增长；运行 valgrind --leak-check=full node addon_test.js 以确认没有剩余的本地内存泄漏
```

### Node.js 特定的诊断决策树

**本地扩展中的段错误/崩溃：**
1. 使用 `node --napi-modules` 是否可以复现崩溃？→ 运行 `gdb`，捕获 `bt`
2. `bt` 是否指向 V8 句柄范围问题？→ 检查 `HandleScope` / `EscapableHandleScope` 在扩展中的使用
3. 它是否指向 libuv 回调？→ 检查异步句柄生命周期和 `uv_close()` 顺序
4. 没有清晰的 C++ 帧？→ 检查传递到本地绑定的 JS 端类型不匹配

**V8 去优化/性能回归：**
1. 运行 `--trace-opt --trace-deopt` → 识别去优化的函数和原因（例如，“不是 Smi”、“映射错误”）
2. 检查点：确认同一函数在多次运行中一致地去优化
3. 检查隐藏类转换 (`--trace-ic`) 并修复属性添加顺序或类型不一致
4. 重新运行 `--trace-opt` 以确认函数现在已优化

**构建失败 (node-gyp / binding.gyp)：**
1. 是缺少头文件吗？→ 验证 `binding.gyp` 中的 `include_dirs` 和 Node.js 头文件安装
2. 是链接器错误吗？→ 检查 `libraries` 和 `link_settings` 条目；确认 ABI 兼容性
3. 是平台特定的吗？→ 参考 `rules/build-system.md` 中的 Windows/macOS/Linux 差异

始终考虑 JavaScript 级别和本地级别的原因，解释性能影响和权衡，并指示讨论的任何实验性功能的稳定性状态。代码示例应展示 Node.js 内部模式，并准备用于生产，考虑典型开发人员可能遗漏的边缘情况。
