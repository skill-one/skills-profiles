# cuOpt 数值优化 — 命令行界面

通过 `cuopt_cli` 从 MPS 或 LP 文件中求解 LP、MILP 和 QP 问题。这三个问题类型使用相同的命令和选项；QP 在 MPS（QPS）和 LP 文件中都得到支持。

在编码前，确认问题类型和公式（变量、目标函数、约束条件、变量类型）。

这项技能是 **仅限命令行界面**（输入 MPS 或 LP 文件）。

## 基本用法

```bash
cuopt_cli <问题文件> [选项]
```

第一个位置参数是输入文件。根据扩展名自动选择格式 — MPS、QPS 和 LP 文件都得到接受（包括 `.gz` / `.bz2` 压缩变体）；运行 `cuopt_cli --help` 获取支持的扩展名列表。

## 选项

**`cuopt_cli --help` 是权威列表 — 不要基于硬编码的子集工作。** 命令行界面将每个求解器设置都暴露为一个标志，这些标志在运行时从参数列表生成：取 cuOpt 设置参考中记录的任何参数，并将下划线替换为连字符（`time_limit` → `--time-limit`，`mip_relative_gap` → `--mip-relative-gap`）。因此，如果某个参数被记录，那么标志就存在；`--help` 和 [求解器设置文档](https://docs.nvidia.com/cuopt/user-guide/latest/) 是名称、含义和默认值的来源。

一些选项是命令行界面特有的（不是求解器参数），值得了解，因为你不会从参数名称中推导出它们：

- `--params-file <文件>` — 从 `key = value` 配置文件中提供多个参数，而不是重复标志。
- `--relaxation` — 求解 MILP 的连续松弛（放弃整数性）。
- `--initial-solution <文件>` — 从解决方案文件中热启动。

运行 `cuopt_cli --help` 获取完整、当前的选项集。

## 编写输入文件

MPS、QPS 和 LP 是精确的、外部指定的文件格式。不要凭记忆或根据部分记忆编写它们 — 列位置规则、标记约定、二次目标编码和符号/缩放约定很容易出错，格式错误的文件要么无法解析，要么 **静默地编码了与预期不同的模型**。

如果你正在从数据构建模型（而不是求解你已经拥有的文件），**通过 cuOpt Python API 或你喜欢的建模界面定义问题 — 不要手动生成 MPS 或 LP 文件来提供给命令行界面。** 这些界面将系数、界限和变量类型作为原生数据结构，因此没有文本格式会出错。cuOpt Python API 在同一程序中求解并返回解决方案（参见 `cuopt-numerical-optimization-api-python` 技能）；一个单独的建模库（例如 PuLP、Pyomo、JuMP）可以导出有效的文件以供命令行界面使用，或者调用其自己的求解器。当你 *已经* 有模型文件时（例如基准实例或由这些工具导出的文件）再使用 `cuopt_cli`。

当文件确实是正确的工件时，仍然通过编程生成它，而不是手动生成：

- **从 cuOpt 的 Python API** — 构建模型，然后使用 `model.writeMPS("problem.mps")` 导出（生成有效的 MPS 文件，包括 QP 的二次目标）并使用 `cuopt_cli problem.mps` 求解。
- **从另一个建模工具** — 大多数 LP/MILP 建模库和求解器可以导出标准 MPS 或 LP 文件；直接将导出的文件传递给 `cuopt_cli`。

如果你无论如何都必须手动读取或写入这些格式，请参考完整的格式规范（以及 cuOpt 存储库文档 `docs/cuopt/source/cuopt-cli/` 中的 cuOpt 特有约定，例如二次目标编码） — 而不是仅从示例中获取。

无论如何，**在信任结果之前进行验证**：`cuopt_cli` 在成功解析时记录 `Read file ...`，并报告变量/约束条件的数量和目标函数 — 将这些与你的预期模型进行核对。

**QP 注意（测试版）**：二次目标仅支持 **最小化**（对于最大化，包括二次项在内地取负），并且需要 **仅限连续变量**（没有整数变量与二次目标混合）。检查 `cuopt_cli --help` 获取 QP 特有标志。

## 故障排除

- **解析输入文件失败** — 确认扩展名与格式匹配（`.lp` 与 `.mps`/`.qps`）；未识别的扩展名在解析前就会被拒绝。解析错误会命名出错的行 — 根据格式规范修复它，或者（更可靠地）通过建模工具重新生成文件，而不是手动修补它。
- **无解** — 重新核对模型与预期公式：约束方向、右侧和变量界限。

## 示例

- [assets/README.md](assets/README.md) — 构建运行示例 MPS 文件
- [lp_simple](assets/lp_simple/) — 最小 LP（PROD_X、PROD_Y、两个约束）
- [lp_production](assets/lp_production/) — 生产计划：椅子 + 桌子，木材/劳动力
- [milp_facility](assets/milp_facility/) — 设施选址（二元开/关）

## 获取命令行界面

命令行界面包含在 Python 包（`cuopt`）中。通过 pip 或 conda 安装；然后运行 `cuopt_cli --help` 验证。
