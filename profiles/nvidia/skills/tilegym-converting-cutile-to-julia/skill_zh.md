# cuTile Python → cuTile.jl (Julia) 转换

将 `@ct.kernel` Python 内核转换为 Julia `function ... end` cuTile.jl 内核。

## 工作流选择

- **标准转换** → 完整工作流：[`translations/workflow.md`](translations/workflow.md)
- **错误** (`MethodError`, `IRError`, 数值不匹配) → [`references/debugging.md`](references/debugging.md)
- **快速参考** → [`references/api-mapping.md`](references/api-mapping.md) + [`references/critical-rules.md`](references/critical-rules.md)
- **测试模式** → [`references/testing.md`](references/testing.md)

## 架构

Julia 内核是 **独立的** — 无 Python 桥接，无 pytest 集成。Julia 子项目位于仓库根目录下的 `julia/` 中，并拥有自己的 `Project.toml` 用于依赖管理。

```
julia/                          # 独立的 Julia 子项目
├── Project.toml                # 依赖：CUDA.jl, cuTile.jl, NNlib.jl, Test
├── kernels/                    # cuTile.jl 内核实现
│   ├── add.jl                  # ← 基准：1D 元素级带 alpha 缩放（张量+张量，张量+标量）
│   ├── matmul.jl               # ← 基准：2D 瓦片式 MMA，标准 Julia 布局 (M,K)×(K,N)→(M,N)
│   └── softmax.jl              # ← 基准：3 种策略（TMA，在线，分块）使用 ct.load/ct.store
└── test/                       # Julia 本地测试（使用 Test 标准库）
    ├── runtests.jl             # 测试运行器入口点
    ├── test_add.jl
    ├── test_matmul.jl
    └── test_softmax.jl
```

**基准参考**：始终查阅 `julia/kernels/*.jl` 和 `julia/test/*.jl` 以获取可编译且通过测试的模式。这些是工作 cuTile.jl 代码的规范示例。

## 说明

1. **分析** Python 内核：识别模式、形状、数据类型、操作
2. **编写 Julia 内核** — `julia/kernels/<op>.jl`，包含 cuTile.jl 内核 + 桥接函数
3. **转换** 内核签名（参见 `translations/workflow.md` 第 2 步）
4. **转换** 内核主体（应用 `references/api-mapping.md` + `references/critical-rules.md`）
5. **编写 Julia 测试** — `julia/test/test_<op>.jl`，使用 `Test` 标准库 + `NNlib.jl` 作为参考
6. **注册测试** — 在 `julia/test/runtests.jl` 中添加 `include(...)`（包含）
7. **验证** — 运行捆绑的验证器：`python <skill-dir>/scripts/validate_cutile_jl.py <file.jl>`
8. **测试** — 运行 `julia --project=julia/ julia/test/runtests.jl`

完整转换清单及转换后验证 → [`translations/workflow.md`](translations/workflow.md)

## ⚠️ 主要陷阱

最危险的翻译错误。完整规则（共 17 条）在 [`references/critical-rules.md`](references/critical-rules.md) 中。

| # | 陷阱 | 一行修复 |
|---|------|----------|
| 1 | `ct.full()` 在 Julia 中不存在 | 使用 `fill(val, shape)`，`zeros(T, dims...)`，或 `ones(T, dims...)` |
| 2 | 瓦片上的 `max(a, b)` → `IRError` | 使用 `max.(a, b)`（广播点乘） |
| 3 | 提及 `IRStructurizer` 的 `IRError` / `MethodError` | 编译器错误 — 上游文件包含最小化复现器 |
| 4 | `ct.launch` 参数顺序隐式错误 | 参数是位置参数 — 精确匹配内核签名 |
| 5 | `ct.load` 带有 `order` — 索引位置错误 | `order` 重映射 **同时** 形状和索引（关键规则 16） |

## 示例

与 `julia/kernels/` 中发布的 Julia 内核并排对应的 Python → Julia 转换。每个目录包含 `cutile_python.py`（之前）和 `cutile_julia.jl`（之后）。

| # | 示例 | 关键模式 | 参考时机 |
|---|------|----------|----------|
| 01 | [`add`](examples/01_add/) | 1D `ct.load`/`ct.store`，alpha 缩放，标量广播，`fill`/`zeros`，关键字加载/存储 | 起点；基本 TMA + 元素级模式 |
| 02 | [`matmul`](examples/02_matmul/) | `muladd`，TF32 转换，K 循环带 `for`，2D 混洗，标准 Julia 布局，`ct.@compiler_options` | MMA / 张量核操作 |
| 03 | [`softmax`](examples/03_softmax/) | 持久调度，`for` 循环，`gather`/`scatter`，`padding_mode`，多阶段 | 大张量归约模式 |

这些与 `julia/kernels/` 中的内核 (`add.jl`，`matmul.jl`，`softmax.jl`) 匹配。示例是简化的教学版本 — 始终查阅 `julia/kernels/*.jl` 获取规范、已测试的实现。

## 参考文档

| 类别 | 文档 | 内容 |
|------|------|------|
| **工作流** | [`translations/workflow.md`](translations/workflow.md) | 完整转换工作流，待办列表，验证循环，清单 |
| **规则** | [`references/critical-rules.md`](references/critical-rules.md) | cuTile Python → Julia 转换的 17 条关键规则 |
| **API** | [`references/api-mapping.md`](references/api-mapping.md) | Python↔Julia 双向 API 映射 + 内核模式 |
| **测试** | [`references/testing.md`](references/testing.md) | Julia 本地测试模式，容差，失败诊断 |
| **调试** | [`references/debugging.md`](references/debugging.md) | Julia 特定错误诊断 + IR 调试命令 |
| **脚本** | [`scripts/validate_cutile_jl.py`](scripts/validate_cutile_jl.py) | 静态验证 Julia 反模式（运行它） |
| **基准** | `julia/kernels/*.jl` + `julia/test/*.jl` | 代码库中实际工作的实现 |

## 环境设置

**前提条件 — Julia**：此技能需要 `julia/Project.toml` 中 `[compat] julia` 下声明的 Julia 版本。如果 `julia --version` 缺失或比该版本旧，请从官方 Julia 网站下载 <https://julialang.org/install/> 并遵循针对您操作系统的验证安装说明。一旦 `julia --version` 兼容，即可继续以下步骤。

然后，从仓库根目录：

```bash
# 安装 julia/Project.toml 中声明的 Julia 依赖
julia --project=julia/ -e 'using Pkg; Pkg.instantiate()'

# 运行测试
julia --project=julia/ julia/test/runtests.jl
```

要求：
- Julia（最低版本在 `julia/Project.toml` 的 `[compat] julia` 下声明）
- CUDA 13.1+ 驱动
- Blackwell GPU（计算能力 10+）
- 依赖通过 `julia/Project.toml` 管理：CUDA.jl, cuTile.jl, NNlib.jl, Test
