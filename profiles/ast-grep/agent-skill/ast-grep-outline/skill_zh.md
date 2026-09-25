# 使用 ast-grep outline

`ast-grep outline` 打印源代码的结构性地图，包含行号：顶层 **项目**（导入、函数、类、结构体、接口、模块、枚举）及其直接 **成员**（字段、方法、构造函数、枚举变体）。它是一个本地、仅基于语法的视图——足够轻量，可以在任何完整的文件读取之前运行。

分阶段阅读代码：使用搜索或文件名找到候选文件，对它们进行概述，然后仅打开概述指向的源代码范围。默认值会根据输入进行调整：一个文件显示其本地结构，包含成员摘要；一个目录仅显示其导出的表面，以分组名称的形式呈现。

## 使用场景

**编辑文件之前理解文件结构。** 在阅读实现细节之前，获取目录、依赖关系和公共入口点：

```shell
ast-grep outline <file>
ast-grep outline <file> --items imports
ast-grep outline <file> --items exports
```

**映射不熟悉的目录。** 扫描子树公共表面，当你知道你在寻找什么时，通过符号类型进行缩小：

```shell
ast-grep outline <dir> --items exports
ast-grep outline <dir> --type struct,enum,function
```

**聚焦于已知的符号。** 搜索找到可能的名称后，用行号列出其成员，而不是阅读整个主体：

```shell
ast-grep outline <file> --match <symbol> --type class --view expanded
```

**追踪依赖方向。** 找到哪些文件导入包或模块，以决定更改属于哪里：

```shell
ast-grep outline <dir> --items imports --view signatures
```

**编辑后审查更改的文件。** Git 告诉你什么发生了变化；概述总结了结果结构和公共表面：

```shell
ast-grep outline $(git diff --name-only HEAD) --items exports
```

## 参数指南

- `--items <KIND>` 选择顶层项目：`structure` 用于本地声明（文件默认），`exports` 用于公共 API（目录默认），`imports` 用于依赖关系，`all` 当导入/导出边一起重要时。
- `--view <VIEW>` 控制细节，从最少到最多：`names` 用于目录扫描，`signatures` 每个项目一行，`digest` 签名加成员名称，`expanded` 每个成员一行，包含其行号。
- `--match <REGEX>` 通过名称或签名过滤顶层项目。Rust 正则表达式，区分大小写；它永远不会匹配成员。
- `--type <TYPE[,TYPE...]>` 仅保留某些顶层符号类型，例如 `--type class,function`。成员类型如 `method,field` 永远不会匹配顶层项目。
- `--pub-members` 当视图打印成员时，隐藏私有成员。
- `--json=stream` 每个文件发出一个 JSON 对象，包含精确的范围。仅用于管道或后处理条目；优先使用文本进行导航。

## 限制

`outline` 显示本地语法结构。它不会解析引用、推断类型、跟随重新导出链或构建调用图。对于这些问题，使用 `ast-grep run`、`rg` 或编译器支持的工具，然后概述它们显示的候选文件。
