# 预览 Flutter 组件

## 目录
- [预览指南](#预览指南)
- [处理限制](#处理限制)
- [工作流程](#工作流程)
- [示例](#示例)

## 预览指南

使用 Flutter 组件预览器实时渲染组件，使其与完整的应用程序上下文隔离。

- **目标元素：** 将 `@Preview` 注解应用于顶层函数、类中的静态方法或无必需参数且返回 `Widget` 或 `WidgetBuilder` 的公共组件构造函数/工厂。
- **导入：** 始终导入 `package:flutter/widget_previews.dart` 以访问预览注解。
- **自定义注解：** 扩展 `Preview` 类以创建自定义注解，跨多个组件注入常用属性（例如，主题、包装器）。
- **多配置：** 将多个 `@Preview` 注解应用于单个目标以生成多个预览实例。或者，扩展 `MultiPreview` 以封装常见的多预览配置。
- **运行时转换：** 在自定义 `Preview` 或 `MultiPreview` 类中重写 `transform()` 方法，以在运行时动态修改预览配置（例如，根据动态值生成名称，这在 `const` 上下文中是不可能的）。

## 处理限制

在编写可预览组件时，请遵循以下约束，因为组件预览器在 Web 环境中运行：

- **无原生 API：** 不要使用来自 `dart:io` 或 `dart:ffi` 的原生插件或 API。依赖于 `dart:io` 或 `dart:ffi` 的组件在调用时将抛出异常。使用条件导入来模拟或绕过预览模式下的这些内容。
- **资源路径：** 对于通过 `dart:ui` `fromAsset` API 加载的资源，使用基于包的路径（例如，`packages/my_package_name/assets/my_image.png` 而不是 `assets/my_image.png`）。
- **公共回调：** 确保提供给预览注解的所有回调参数都是公共和常量，以满足代码生成要求。
- **约束：** 如果您的组件无约束，请使用 `@Preview` 注解中的 `size` 参数应用显式约束，因为预览器默认将它们约束为视口大小的大约一半。

## 工作流程

### 创建组件预览
在实现新的组件预览时，复制并跟踪此清单：

- [ ] 导入 `package:flutter/widget_previews.dart`。
- [ ] 确定一个有效目标（顶层函数、静态方法或无参数的公共构造函数）。
- [ ] 将 `@Preview` 注解应用于目标。
- [ ] 根据需要配置预览参数（`name`、`group`、`size`、`theme`、`brightness` 等）。
- [ ] 如果将相同的配置应用于多个组件，请将配置提取到扩展 `Preview` 的自定义类中。

### 与预览交互
遵循适当的条件工作流程以启动并与组件预览器交互：

**如果使用受支持的 IDE（Android Studio、IntelliJ、带有 Flutter 3.38+ 的 VS Code）：**
1. 启动 IDE。组件预览器将自动启动。
2. 在侧边栏中打开 "Flutter Widget Preview" 选项卡。
3. 如果您希望在当前活动文件之外查看预览，请左下角切换 "Filter previews by selected file"。

**如果使用命令行：**
1. 导航到 Flutter 项目的根目录。
2. 运行 `flutter widget-preview start`。
3. 查看自动打开的 Chrome 环境。

**预览迭代反馈循环**
1. 修改组件代码或预览配置。
2. 在组件预览器中观察自动更新。
3. 如果修改了全局状态（例如，静态初始化器）：点击右下角的全球热重启动按钮。
4. 如果只需要重置本地组件状态：点击特定预览卡上的单个热重启动按钮。
5. 查看 IDE/CLI 控制台中的错误 -> 修复 -> 重复。

## 示例

### 基本预览
```dart
import 'package:flutter/widget_previews.dart';
import 'package:flutter/material.dart';

@Preview(name: '我的示例文本', group: '排版')
Widget mySampleText() {
  return const Text('Hello, World!');
}
```

### 带运行时转换的自定义预览
```dart
import 'package:flutter/widget_previews.dart';
import 'package:flutter/material.dart';

final class TransformativePreview extends Preview {
  const TransformativePreview({
    super.name,
    super.group,
  });

  PreviewThemeData _themeBuilder() {
    return PreviewThemeData(
      materialLight: ThemeData.light(),
      materialDark: ThemeData.dark(),
    );
  }

  @override
  Preview transform() {
    final originalPreview = super.transform();
    final builder = originalPreview.toBuilder();
    
    builder
      ..name = '转换后 - ${originalPreview.name}'
      ..theme = _themeBuilder;

    return builder.toPreview();
  }
}

@TransformativePreview(name: '自定义主题按钮')
Widget myButton() => const ElevatedButton(onPressed: null, child: Text('点击'));
```

### MultiPreview 实现
```dart
import 'package:flutter/widget_previews.dart';
import 'package:flutter/material.dart';

/// 自动创建亮色和暗色模式预览。
final class MultiBrightnessPreview extends MultiPreview {
  const MultiBrightnessPreview({required this.name});

  final String name;

  @override
  List<Preview> get previews => const [
        Preview(brightness: Brightness.light),
        Preview(brightness: Brightness.dark),
      ];

  @override
  List<Preview> transform() {
    final previews = super.transform();
    return previews.map((preview) {
      final builder = preview.toBuilder()
        ..group = '亮度'
        ..name = '$name - ${preview.brightness!.name}';
      return builder.toPreview();
    }).toList();
  }
}

@MultiBrightnessPreview(name: '主要卡片')
Widget cardPreview() => const Card(child: Padding(padding: EdgeInsets.all(8.0), child: Text('内容')));
```
