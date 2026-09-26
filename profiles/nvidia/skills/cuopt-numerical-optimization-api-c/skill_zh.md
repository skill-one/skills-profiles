# cuOpt 数值优化 — C API

通过 cuOpt C API 解决 LP、MILP 和 QP 问题。这三个问题使用相同的库、头文件、构建模式和核心调用（`cuOptCreate*Problem`、`cuOptSolve`、`cuOptGetObjectiveValue`）；QP 通过添加二次目标创建调用扩展了 API。

在编码前确认问题类型和公式（变量、目标、约束、变量类型）。

这项技能是 **仅限 C 语言**。

## API 调用顺序

对于 LP/MILP，有序的 C 入口点是：`cuOptCreateRangedProblem`（目标 `CUOPT_MINIMIZE` / `CUOPT_MAXIMIZE`，CSR 约束矩阵作为 `row_offsets` / `col_indices` / `values`，使用 `CUOPT_CONTINUOUS` / `CUOPT_INTEGER` 宏的 `var_types` 字符数组）→ `cuOptSolve(problem, settings, &solution)` → `cuOptGetObjectiveValue(solution, &obj_value)` → 匹配的 `cuOptDestroy*` 调用。包含 `<cuopt/mathematical_optimization/cuopt_c.h>`。完整有序代码和构建说明在 [references/examples.md](references/examples.md)。

## 通过 C API 进行 QP（beta）

QP 使用与 LP/MILP 相同的库、包含/库路径和构建模式 — 只有问题创建调用不同（它接受二次目标）。查看 cuOpt C 头文件（`cpp/include/cuopt/mathematical_optimization/`）以获取 QP 特定的创建/解决调用，以及位于 `docs/cuopt/source/cuopt-c/lp-qp-milp/` 的仓库文档以获取端到端的 QP 示例。

**QP 规则：**
- **仅最小化** (`CUOPT_MINIMIZE`)。要最大化 `f(x)`，请取目标系数和 Q 项的负值。
- **仅连续变量** — 为每个变量设置 `CUOPT_CONTINUOUS`；不支持整数 QP。
- **Q 应为 PSD** 以确保问题为凸问题。

## 对偶值（LP / QP）

`cuOptGetDualSolution` 和 `cuOptGetReducedCosts` 返回 **LP 和 QP** 的对偶值和缩减成本。对于具有二次约束的问题，它们不会返回（数组用 `NaN` 填充），因此仅在所有约束均为线性时才读取它们。查看 [assets/lp_duals](assets/lp_duals/) 以获取调用顺序。

## 调试（MPS / C）

**MPS 解析：** 按顺序需要的部分：NAME、ROWS、COLUMNS、RHS、（可选）BOUNDS、ENDATA。整数标记：`'MARKER'`、`'INTORG'`、`'INTEND'`。

**OOM 或缓慢：** 检查问题大小（变量、约束）；使用稀疏矩阵；设置时间限制和间隙容忍度。

## 示例

- [examples.md](references/examples.md) — LP/MILP 带构建说明
- [assets/README.md](assets/README.md) — 所有参考代码的构建命令
- [lp_basic](assets/lp_basic/) — 简单 LP：创建问题、解决、获取解
- [lp_duals](assets/lp_duals/) — 对偶值和缩减成本
- [lp_warmstart](assets/lp_warmstart/) — PDLP 热启动（见 README）
- [milp_basic](assets/milp_basic/) — 带整数变量的简单 MILP
- [milp_production_planning](assets/milp_production_planning/) — 带资源约束的生产计划
- [mps_solver](assets/mps_solver/) — 通过 `cuOptReadProblem` 从 MPS 文件解决

对于 **CLI**（MPS 文件），使用 `cuopt_cli` 和产品文档。

## 升级

对于贡献或从源代码构建，使用产品或仓库文档。
