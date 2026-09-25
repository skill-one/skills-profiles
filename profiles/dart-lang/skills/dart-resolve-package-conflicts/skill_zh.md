# 管理Dart依赖项

## 目录
- [核心概念](#核心概念)
- [版本约束](#版本约束)
- [工作流：审计依赖项](#工作流审计依赖项)
- [工作流：升级依赖项](#工作流升级依赖项)
- [工作流：解决版本冲突](#工作流解决版本冲突)
- [示例](#示例)

## 核心概念

Dart对依赖项执行严格的单版本规则：一个项目和所有其传递依赖项必须解析为任何给定包的单一、共享版本。这可以防止运行时类型不匹配，但引入了“版本锁定”的风险。

为了缓解版本锁定，Dart依赖于`pubspec.yaml`中的版本约束，而不是固定版本。`pubspec.lock`文件维护了可重复构建的确切解析版本。

理解`dart pub outdated`的输出列：
*   **当前：** `pubspec.lock`中当前记录的版本。
*   **可升级：** `pubspec.yaml`中约束允许的最新版本。`dart pub upgrade`解析为此版本。
*   **可解析：** 考虑项目中所有其他依赖项后可以解析的绝对最新版本。
*   **最新：** 包的最新发布版本（不包括预发布版本）。

## 版本约束

*   **使用尖括号语法：** 在`pubspec.yaml`中始终使用尖括号语法（例如，`^1.2.3`）来声明依赖项。这允许`pub`在解析期间选择更新的、非破坏性版本（最高到但不包括下一个主版本）。
*   **收紧开发依赖项：** 将`dev_dependencies`的下限设置为当前使用的确切版本。这减少了解析复杂性，并防止选择旧的不兼容的开发工具。
*   **在CI中强制锁定文件：** 在CI/CD管道中使用`dart pub get --enforce-lockfile`来确保本地测试使用的确切版本在生产环境中使用。

## 工作流：审计依赖项

定期运行此工作流以识别可能影响稳定性或性能的过时包。

**任务进度：**
- [ ] 运行`dart pub outdated`。
- [ ] 查看可升级列以识别可以在不修改`pubspec.yaml`的情况下更新的包。
- [ ] 查看可解析列以识别需要修改`pubspec.yaml`中的约束才能更新的包。
- [ ] 识别任何被撤回或停止维护的包。

## 工作流：升级依赖项

根据审计结果使用条件逻辑来升级依赖项。

**任务进度：**
- [ ] **如果更新到“可升级”版本：**
  - [ ] 运行`dart pub upgrade`。
  - [ ] 运行`dart pub upgrade --tighten`以自动更新`pubspec.yaml`中的下限以匹配新解析的版本。
- [ ] **如果更新到“可解析”版本（主版本更新）：**
  - [ ] 手动编辑`pubspec.yaml`将版本约束提升到与“可解析”列匹配（例如，将`^0.11.0`改为`^0.12.1`）。
  - [ ] 运行`dart pub upgrade`以解析新约束并更新`pubspec.lock`。
- [ ] **反馈循环：**
  - [ ] 运行`dart analyze` -> 查看错误 -> 修复破坏性API更改。
  - [ ] 运行`dart test` -> 查看失败 -> 修复回归。

## 工作流：解决版本冲突

当`pub`无法找到满足所有约束的特定版本集，或处理被撤回的包版本时，需要外科手术式地操作锁定文件。

**永远不要**删除整个`pubspec.lock`文件并运行`dart pub get`。这会导致整个依赖图不受控制地升级。

**任务进度：**
- [ ] 打开`pubspec.lock`。
- [ ] 定位冲突或被撤回包的特定YAML块。
- [ ] 仅从锁定文件中删除该包的条目。
- [ ] 运行`dart pub get`以获取该特定包的最新兼容、未被撤回的版本。
- [ ] **反馈循环：**
  - [ ] 运行`dart pub deps` -> 验证依赖图解析正确。
  - [ ] 如果解析失败，识别导致锁定的传递依赖项，在`pubspec.yaml`中更新其约束，并重试。

## 示例

### 收紧约束

当`dart pub outdated`显示包可以解析为更高的次要/补丁版本时，使用`--tighten`标志自动更新`pubspec.yaml`。

**输入 (`pubspec.yaml`):**
```yaml
dependencies:
  http: ^0.13.0
```

**命令:**
```bash
dart pub upgrade --tighten http
```

**输出 (`pubspec.yaml`):**
```yaml
dependencies:
  http: ^0.13.5
```

### 外科手术式锁定文件删除

如果`package_a`被撤回或在冲突中被锁定，仅删除`pubspec.lock`中的其块。

**之前 (`pubspec.lock`):**
```yaml
packages:
  package_a:
    dependency: "direct main"
    description:
      name: package_a
      url: "https://pub.dev"
    source: hosted
    version: "1.0.0" # 撤回的版本
  package_b:
    dependency: "direct main"
    # ...
```

**操作：** 完全删除`package_a`块。保留`package_b`不变。运行`dart pub get`。
