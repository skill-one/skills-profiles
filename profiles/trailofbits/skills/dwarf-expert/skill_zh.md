# DWARF专家

DWARF调试信息的专长：解析和搜索它，验证其完整性，回答关于标准的疑问，以及编写使用它的代码。超出范围：运行时调试（使用gdb/lldb）、DWARF节之外的逆向工程（使用Ghidra/IDA），以及特定于编译器的DWARF生成错误。

# 权威资料来源

当精确性重要时，查阅标准细节而不是凭记忆回答：

1. **dwarfstd.org** — 官方规范。通过网页搜索特定章节，例如 "DWARF5 DW_TAG_subprogram属性 site:dwarfstd.org"。
2. **LLVM** — `llvm/lib/DebugInfo/DWARF/` 是一个可靠的参考实现：`DWARFDie.cpp`（DIE和属性访问）、`DWARFUnit.cpp`（编译单元）、`DWARFDebugLine.cpp`（行表）、`DWARFVerifier.cpp`（验证）。
3. **libdwarf** — GitHub上的参考C实现（github.com/davea42/libdwarf-code）。

# 使用dwarfdump进行解析和搜索

对于DWARF特定工作，优先选择`dwarfdump`而不是`readelf`。存在两种实现——libdwarf的`dwarfdump`和LLVM的`llvm-dwarfdump`——选项不同，而一个简单的`dwarfdump`命令可能是其中之一：首先检查`dwarfdump --version`。下面的选项是LLVM的。

在macOS上，链接的Mach-O可执行文件不携带DWARF：它保留在`.o`文件中，直到`dsymutil`将其收集到`.dSYM`包中。将`dwarfdump`指向dSYM（或对象文件），而不是可执行文件。`pyelftools`仅支持ELF——对于Mach-O脚本工作，坚持使用LLVM工具。

- `--all`：转储所有DWARF节；`--debug-info`、`--debug-line`等转储一个节
- `--show-children [--recurse-depth=<n>]`：在打印选定条目时包含子DIE——参数、局部变量和结构成员是函数和类型DIE的子项
- `--show-parents [--parent-recurse-depth=<n>]`：包含父DIE
- `--show-form`：打印属性形式类型，当编码细节重要时
- `--find=<name>`：通过加速表进行精确名称查找——快速但不全面；当它遗漏时回退到`--name`
- `--name=<pattern> [--ignore-case] [--regex]`：全面的DIE名称搜索
- `--lookup=<address>`：查找覆盖地址的DIE
- `--verbose`：打印低级编码细节

## 搜索DIE

随着查询变得更加复杂，逐步升级这些策略：

1. **名称或地址匹配**：`--find`，然后`--name`；`--lookup`用于地址。
2. **属性或类型查询**（例如类型为`float *`的所有参数）：转储并过滤。`grep -B`拉入包含每个DIE偏移的标题行：`llvm-dwarfdump file | grep -B 5 "float *" | grep DW_TAG_formal_parameter`，然后使用`--debug-info=<offset> --show-children`打印每个DIE在其偏移处（`--lookup`接受程序地址，而不是DIE偏移）。
3. **多属性或结构查询**：当grep管道变得脆弱时，使用`pyelftools`编写Python脚本。

# 验证DWARF完整性

- `llvm-dwarfdump --verify <binary>`：结构检查（单元链、DIE关系、地址范围）。`--error-display=<quiet|summary|details|full>`控制细节；`--verify-json=<path>`写入机器可读的错误摘要；`--quiet`用于仅检查退出码。
- `llvm-dwarfdump --statistics <binary>`：作为JSON的调试信息质量指标——跨编译器版本或优化级别比较以捕获回归。

在生成DWARF后（编译器、二进制重写器）、调试器在二进制文件上行为异常时、以及开发针对已知良好文件的DWARF工具时进行验证。

当当前一代编译器发出旧版DWARF版本时，构建明确传递了`-gdwarf-N`——现代gcc和clang默认为v4/v5，因此检查构建系统而不是假设工具链默认。GCC将其标志嵌入`DW_AT_producer`中，因此通常可以立即读取；clang的生产者字符串不包含标志。旧版本在野外仍然很常见，并且除了表面形式外以相同方式读取：在v2输出中，成员偏移量作为位置表达式（`DW_OP_plus_uconst`）出现，链接名称作为`DW_AT_MIPS_linkage_name`。

# readelf

对于通用ELF结构，或当`dwarfdump`不可用时：

- `--debug-dump=<section>`：转储DWARF节（`info`、`line`、...）
- `--dwarf-depth=<n>` / `--dwarf-start=<n>`：限制DIE深度/起始偏移

# 编写解析DWARF的代码

优先选择现有库而不是手动解析：

| 库 | 语言 | 备注 |
|----|------|------|
| `libdwarf` | C/C++ | github.com/davea42/libdwarf-code — 低级；用于实现`dwarfdump` |
| `pyelftools` | Python | github.com/eliben/pyelftools — 也解析通用ELF |
| `gimli` | Rust | github.com/gimli-rs/gimli — 与`object`配合加载容器文件 |
| `debug/dwarf` | Go | 标准库 |
| `LibObjectFile` | .NET | github.com/xoofx/LibObjectFile — 也处理ELF/PE对象文件 |

除非任务要求否则默认使用Python和`pyelftools`进行一次性脚本。

DWARF特定陷阱需要处理——以及在审查DWARF代码时需要检查：

- 属性是可选的：一个DIE可以省略`DW_AT_name`、`DW_AT_type`、范围等。
- 属性间接引用：一个DIE的属性可能存在于其`DW_AT_abstract_origin`（内联实例）或`DW_AT_specification`（离线定义）引用的DIE上——在得出数据缺失的结论之前解决链。
- 类型链：限定符和修饰符（`DW_TAG_const_type`、`DW_TAG_pointer_type`、...）包装基本类型；遍历`DW_AT_type`链接以到达基本类型。
