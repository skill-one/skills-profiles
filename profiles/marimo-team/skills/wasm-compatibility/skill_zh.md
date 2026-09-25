# marimo 笔记本的 WASM 兼容性检查器

检查 marimo 笔记本是否可以在 WebAssembly (WASM) 环境中运行——marimo 沙盒、社区云或导出的 WASM HTML。

## 使用说明

### 1. 读取笔记本

读取目标笔记本文件。如果用户未指定，则询问要检查哪个笔记本。

### 2. 运行 marimo 的 WASM 检查规则

marimo 提供三种检查规则，可自动捕获大多数 WASM 兼容性问题。首先运行这些规则，并从其输出生成报告，而不是手动重新推导这些检查：

```bash
marimo check <notebook> --select MW --format json
```

- **MW001** `incompatible-import` — stdlib 模块缺失或 Pyodide 中无法正常工作（`subprocess`、`pdb`、`dbm`、`resource`、`fcntl`、`termios`、`readline`、`curses`、`tkinter`、`pydecimal`、`test`），以及需要原生同步、共享内存、管道或进程分叉的子模块（`Lock`、`Condition`、`Semaphore`、`Barrier`、`Manager`、`Pipe`、`RLock`、`shared_memory`、`ForkContext`/`ForkProcess`、`ThreadPool` 等）。`Process`、`Queue`、`SimpleQueue`、`Pool` 和 `ProcessPoolExecutor` 仍然允许——它们在 WASM 兼容的协作适配器上运行（见步骤 3）。
- **MW002** `unsafe-system-call` — 即使导入本身成功，Pyodide 中也会失败的调用，如 `os.system()`、`os.fork()`、`signal.signal()`、`breakpoint()`。
- **MW003** `incompatible-package` — 解析笔记本的 PEP 723 依赖树（跳过任何被 `sys_platform != 'emscripten'` 标记排除的内容），并检查 PyPI 以查找 WASM 兼容的轮子，捕获如 `jaxlib` 通过 `jax` 传递的情况。

**注意**：MW001 标记导入语句（`from multiprocessing import Lock`、`import multiprocessing.synchronize`），而不是后续的属性访问。一个简单的 `import multiprocessing` 后跟代码中更深层的 `multiprocessing.Lock()` 可能会绕过检查。对于包含并发代码的笔记本，也需要手动检查。

**注意**：干净的 MW003 结果本身并不表示该包在浏览器中安全使用。如果笔记本标记 `sys_platform != 'emscripten'`，MW003 会完全跳过它——这仅表示该包不会在 WASM 中*安装*，而不是笔记本可以自由使用它。检查笔记本是否也有 `cache_cells = true` 并使用 `--execute` 导出（见步骤 4）。如果是，被排除的包仍然可以通过缓存使用。如果不是，任何导入或接触被排除包的代码路径在浏览器中都会失败，MW003 也不会发出警告。

### 3. 检查检查器未覆盖的内容

这些是手动、代理驱动的检查：

- **PEP 723 元数据。** 如果笔记本没有 `# /// script` 块，或导入的包未列在 `dependencies` 中，则警告。没有这些元数据，包在笔记本以 WASM 启动时不会自动安装。版本固定和下限是允许的——marimo 在 WASM 运行时移除版本约束。
- **仅运行时模式。** 静态检查无法捕获这些：读取环境变量（`os.environ`、`os.getenv`）、硬编码的绝对文件路径或期望真实文件系统的 `Path.home()`/`Path.cwd()`，以及大型内存数据集（WASM 笔记本受限于 2GB）。在看到这些地方时标记它们。
- **并发语义。** WASM 笔记本为 `threading.Thread`、`Event`、`local`、`ThreadPoolExecutor`、`wait`、`as_completed` 和进程形 `multiprocessing.Process`、`Queue`、`SimpleQueue`、`Pool`、`ProcessPoolExecutor` 运行协作适配器。API 形状是真实的，但没有操作系统线程、没有共享内存、没有真正的并行性。所有内容都在单个 Pyodide 解释器中一次运行一个任务。如果笔记本依赖实际并发加速而不是仅 API 形状，则警告它运行正确但顺序执行。
- **已存在的缓存执行。** 检查笔记本的 `pyproject.toml`（或内联 `# /// script` 块）中的 `[tool.marimo.runtime] cache_cells = true`。如果已设置，标记为 `sys_platform != 'emscripten'` 的不兼容包不会自动失败——见步骤 4 中的例外情况。

### 4. 生成报告

输出清晰、可操作的报告：

**兼容性：PASS / FAIL / WARN**

- **PASS** — 检查和步骤 3 都未发现任何问题。
- **WARN** — 没有失败，但步骤 3 发现了一些值得再次查看的内容（缺失 PEP 723 元数据、仅运行时模式或并发但不会并行运行）。
- **FAIL** — 检查报告了诊断，或步骤 3 发现了完全无法运行的某些内容。

**检查结果** — 原封不动地粘贴步骤 2 的诊断（文件、行、代码、消息）。

**手动发现** — 列出步骤 3 的任何内容，包括单元格或行和建议的修复方案。

**建议** — 对于 FAIL/WARN 笔记本，建议具体的修复方案：
- 用 WASM 友好的替代包替换不兼容的包
- 重写不兼容的代码模式

对于没有 WASM 构建的包，没有即插即用的替代方案。存在两个例外情况，它们解决不同的问题——检查笔记本实际需要哪一个：

1. **预计算每个可达结果并缓存它。** 使用 `sys_platform != 'emscripten'` 标记排除包。marimo 然后运行一次真实计算，服务器端，并将结果捆绑到导出中：

   ```toml
   # /// script
   # dependencies = [
   #     "marimo",
   #     "torch; sys_platform != 'emscripten'",
   # ]
   #
   # [tool.marimo.runtime]
   # cache_cells = true
   # ///
   ```

   ```bash
   marimo export html-wasm notebook.py -o output_dir --execute
   ```

   这直接覆盖单个静态结果（一个图表、一次性计算）。对于小型、可枚举的结果集——一个固定选项的下拉菜单或滑块——用 `@mo.persistent_cache(method="lazy")` 装饰计算。在导出前，为每个选项添加一个调用它的单元格。见 [缓存预计算值](https://docs.marimo.io/guides/exporting/webassembly_html/#precomputed-values)。无论如何，被排除的包永远不会在浏览器中运行——笔记本只读取其缓存结果。
2. **使用兼容层在浏览器中运行真实计算。** 预计算无法覆盖无法提前枚举的输入空间——例如，一个驱动实时推理的滑块，覆盖连续范围。笔记本需要计算的真实 WASM 原生实现。`moutils.onnx.OnnxRuntime` 是这种模式的一个例子：它将 PyTorch 或 JAX 模型转换为 ONNX，它返回的对象使用 `onnxruntime-web` 在浏览器中运行推理，而不是原始框架。

## 额外背景

- WASM 笔记本通过 [Pyodide](https://pyodide.org) 在浏览器中运行
- 内存限制为 2GB
- 网络请求有效，但可能需要 CORS 兼容的端点
- Chrome 具有最佳 WASM 性能；Firefox、Edge、Safari 也受支持
- `micropip` 可以在运行时安装 PyPI 中的任何纯 Python 轮子
- 关于 marimo 的完整 WASM 检查规则列表，见 [检查规则参考](https://docs.marimo.io/guides/lint_rules/#-wasm-rules)
- 关于 Pyodide 内置包的手动维护快照，见 [pyodide-packages.md](references/pyodide-packages.md)。它是一个快速的人类可读参考，但 `marimo check --select MW003` 直接查询 PyPI 并自动保持最新
