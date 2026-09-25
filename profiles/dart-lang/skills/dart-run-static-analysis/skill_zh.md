# 分析和修复 Dart 代码

## 目录
- [分析配置](#分析配置)
- [诊断抑制](#诊断抑制)
- [工作流：执行静态分析](#工作流执行静态分析)
- [工作流：应用自动修复](#工作流应用自动修复)
- [示例](#示例)

## 分析配置

使用位于包根目录的 `analysis_options.yaml` 文件配置 Dart 分析器。

- **基础配置**：始终使用 `include:` 指令包含标准规则集（例如，`package:lints/recommended.yaml` 或 `package:flutter_lints/flutter.yaml`）。
- **严格类型检查**：在 `analyzer: language:` 节点下启用严格类型检查，以防止隐式向下转型和动态推断。设置 `strict-casts: true`、`strict-inference: true` 和 `strict-raw-types: true`。
- **Linter 规则**：在 `linter: rules:` 节点下显式启用或禁用特定规则。使用键值映射（`rule_name: true/false`）覆盖包含的规则，或使用列表（`- rule_name`）定义全新规则集。在同一个 `rules` 块中不要混合列表和映射语法。
- **格式化配置**：在 `formatter:` 节点下配置 `dart format` 行为。设置 `page_width`（默认 80）和 `trailing_commas`（`automate` 或 `preserve`）。
- **分析器插件**：通过在 `analyzer: plugins:` 节点下添加插件来启用自定义诊断。确保插件包作为 `dev_dependency` 添加到 `pubspec.yaml` 中。

## 诊断抑制

当诊断（lint 或警告）产生误报或适用于生成代码时，显式抑制它。

- **文件级排除**：在 `analysis_options.yaml` 中使用 `analyzer: exclude:` 节点排除整个文件或目录（例如，`**/*.g.dart`），使用通配符模式。
- **文件级抑制**：在 Dart 文件顶部添加 `// ignore_for_file: <diagnostic_code>` 来抑制整个文件的特定诊断。使用 `// ignore_for_file: type=lint` 抑制所有 linter 规则。
- **行级抑制**：在出问题的代码直接上方添加 `// ignore: <diagnostic_code>`，或附加到出问题行的末尾。
- **Pubspec 抑制**：在 `pubspec.yaml` 文件中，在出问题行上方添加 `# ignore: <diagnostic_code>`（例如，`# ignore: sort_pub_dependencies`）。
- **插件诊断**：抑制插件特定问题时，在诊断代码前缀插件名称（例如，`// ignore: some_plugin/some_code`）。

## 工作流：执行静态分析

使用此工作流来识别与类型相关的错误、样式违规和潜在的运行时错误。

**任务进度：**
- [ ] 1. 验证项目根目录下存在 `analysis_options.yaml`。
- [ ] 2. 使用 `analyze_files` MCP 工具（如果可用）或 CLI 命令 `dart analyze <目标目录>` 运行分析器。
- [ ] 3. 审阅诊断输出。
- [ ] 4. 如果必须将 info 级别的错误视为失败，附加 `--fatal-infos` 标志。
- [ ] 5. 手动修复报告的错误，或继续到自动修复工作流。

## 工作流：应用自动修复

使用此工作流来修复过时的 API 使用、应用快速修复以及迁移代码（例如，Dart 3 迁移）。

**任务进度：**
- [ ] 1. 执行干运行，使用 `dart_fix` MCP 工具或 CLI 命令 `dart fix --dry-run` 预览建议的更改。
- [ ] 2. 审阅建议的修复，确保它们与预期架构一致。
- [ ] 3. 如果需要额外的修复，验证 `analysis_options.yaml` 中已启用相应的 linter 规则。
- [ ] 4. 使用 `dart_fix` MCP 工具或 CLI 命令 `dart fix --apply` 应用修复。
- [ ] 5. 使用 `dart_format` MCP 工具或 CLI 命令 `dart format .` 格式化修改后的代码。
- [ ] 6. 运行静态分析工作流以验证所有诊断均已解决。

## 示例

### 完整的 `analysis_options.yaml`

```yaml
include: package:flutter_lints/recommended.yaml

analyzer:
  exclude:
    - "**/*.g.dart"
    - "lib/generated/**"
  language:
    strict-casts: true
    strict-inference: true
    strict-raw-types: true
  errors:
    todo: ignore
    invalid_assignment: warning
    missing_return: error

linter:
  rules:
    avoid_shadowing_type_parameters: false
    await_only_futures: true
    use_super_parameters: true

formatter:
  page_width: 100
  trailing_commas: preserve
```

### 行内诊断抑制

```dart
// 对整个文件抑制
// ignore_for_file: unused_local_variable, dead_code

void processData() {
  // 对特定行抑制
  // ignore: invalid_assignment
  int x = '';
  
  const y = 10; // ignore: constant_identifier_names
}
```
