# Flutter 应用国际化

## 目录
- [核心概念](#核心概念)
- [设置流程](#设置流程)
- [实现流程](#实现流程)
- [高级格式化](#高级格式化)
- [示例](#示例)

## 核心概念
Flutter 通过 `flutter_localizations` 和 `intl` 包处理国际化（i18n）和本地化（l10n）。标准方法使用应用资源包（`.arb`）文件定义本地化字符串，然后将其编译为生成的 `AppLocalizations` 类，以便在组件树中安全地访问。

## 设置流程

在 Flutter 项目中初始化国际化时，复制并跟踪此清单：

- [ ] **任务进度**
  - [ ] 1. 向 `pubspec.yaml` 添加依赖项。
  - [ ] 2. 启用 `generate` 标志。
  - [ ] 3. 创建 `l10n.yaml` 配置文件。
  - [ ] 4. 配置 `MaterialApp` 或 `CupertinoApp`。

### 1. 添加依赖项
将所需的本地化包添加到项目中。在终端中执行以下命令：
```bash
flutter pub add flutter_localizations --sdk=flutter
flutter pub add intl:any
```

验证 `pubspec.yaml` 在 `dependencies` 下包含以下内容：
```yaml
dependencies:
  flutter:
    sdk: flutter
  flutter_localizations:
    sdk: flutter
  intl: any
```

### 2. 启用代码生成
打开 `pubspec.yaml` 并在 `flutter` 部分中启用 `generate` 标志，以自动化本地化任务：
```yaml
flutter:
  generate: true
```

### 3. 创建配置文件
在 Flutter 项目的根目录中创建一个名为 `l10n.yaml` 的新文件。定义输入目录、模板文件和输出文件：
```yaml
arb-dir: lib/l10n
template-arb-file: app_en.arb
output-localization-file: app_localizations.dart
synthetic-package: true
```

### 4. 配置应用入口点
在 `main.dart` 中导入生成的本地化和 `flutter_localizations` 库。将委托和支持的区域设置注入到 `MaterialApp` 或 `CupertinoApp` 中。

```dart
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart'; // 如果 synthetic-package 为 false，请调整路径

// ... 在 build 方法内
return MaterialApp(
  localizationsDelegates: const [
    AppLocalizations.delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
  ],
  supportedLocales: const [
    Locale('en'), // 英语
    Locale('es'), // 西班牙语
  ],
  home: const MyHomePage(),
);
```

## 实现流程

添加或修改本地化内容时，请遵循此流程。

### 1. 定义 ARB 文件
*   **如果创建新内容：** 将基本字符串添加到模板文件（`lib/l10n/app_en.arb`）。为上下文添加描述。
*   **如果编辑现有内容：** 在所有支持的 `.arb` 文件中定位键并更新值。

```json
{
  "helloWorld": "Hello World!",
  "@helloWorld": {
    "description": "传统的初学者程序员问候语"
  }
}
```

为其他区域创建相应的文件（例如，`app_es.arb`）：
```json
{
  "helloWorld": "¡Hola Mundo!"
}
```

### 2. 生成本地化类
运行以下命令以触发代码生成：
```bash
flutter pub get
```
*反馈循环：* 运行验证器 -> 审查终端输出中的 ARB 语法错误 -> 修复缺失的逗号或不匹配的占位符 -> 重新运行 `flutter pub get`。

### 3. 消费本地化字符串
使用 `AppLocalizations.of(context)` 在组件树中访问本地化字符串。确保调用此方法的组件是 `MaterialApp` 的后代。

```dart
Text(AppLocalizations.of(context)!.helloWorld)
```

## 高级格式化

使用占位符处理动态数据、复数和条件选择。

### 占位符
在花括号内定义参数，并在元数据对象中指定其类型。
```json
"hello": "Hello {userName}",
"@hello": {
  "description": "包含单个参数的消息",
  "placeholders": {
    "userName": {
      "type": "String",
      "example": "Bob"
    }
  }
}
```

### 复数
使用 `plural` 语法处理基于数量的字符串变化。`other` 情况是必需的。
```json
"nWombats": "{count, plural, =0{没有袋熊} =1{1 只袋熊} other{{count} 只袋熊}}",
"@nWombats": {
  "description": "一个复数消息",
  "placeholders": {
    "count": {
      "type": "num",
      "format": "compact"
    }
  }
}
```

### 选择
使用 `select` 语法处理条件字符串，例如性别化文本。
```json
"pronoun": "{gender, select, male{他} female{她} other{他们}}",
"@pronoun": {
  "description": "一个性别化消息",
  "placeholders": {
    "gender": {
      "type": "String"
    }
  }
}
```

## 示例

### 完整的 `l10n.yaml`
```yaml
arb-dir: lib/l10n
template-arb-file: app_en.arb
output-localization-file: app_localizations.dart
synthetic-package: true
use-escaping: true
```

### 完整的组件实现
```dart
import 'package:flutter/material.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';

class GreetingWidget extends StatelessWidget {
  final String userName;
  final int notificationCount;

  const GreetingWidget({
    super.key, 
    required this.userName, 
    required this.notificationCount,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return Column(
      children: [
        Text(l10n.hello(userName)),
        Text(l10n.nWombats(notificationCount)),
      ],
    );
  }
}
```
