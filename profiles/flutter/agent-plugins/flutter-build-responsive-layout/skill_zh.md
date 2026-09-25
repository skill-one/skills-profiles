# 实现自适应布局

## 目录
- [空间测量指南](#空间测量指南)
- [组件尺寸和约束](#组件尺寸和约束)
- [设备和方向行为](#设备和方向行为)
- [工作流：构建自适应布局](#工作流构建自适应布局)
- [工作流：优化大屏幕](#工作流优化大屏幕)
- [示例](#示例)

## 空间测量指南
准确确定可用空间，确保布局适应应用窗口，而不仅仅是物理设备。

*   **使用 `MediaQuery.sizeOf(context)`** 获取整个应用窗口的尺寸。
*   **使用 `LayoutBuilder`** 基于父组件分配的空间做出布局决策。评估 `constraints.maxWidth` 以确定返回的适当组件树。
*   **不要在组件树的顶部使用 `MediaQuery.orientationOf` 或 `OrientationBuilder`** 来切换布局。设备方向并不能准确反映可用应用窗口空间。
*   **不要检查硬件类型**（例如，“手机”与“平板”）。Flutter 应用在可调整大小的窗口、多窗口模式和画中画模式下运行。严格基于可用窗口空间做出所有布局决策。

## 组件尺寸和约束
理解并应用 Flutter 的核心布局规则：**约束向下传递。尺寸向上传递。父组件设置位置。**

*   **分配空间：** 在 `Row`、`Column` 或 `Flex` 组件中使用 `Expanded` 和 `Flexible`。
    *   使用 `Expanded` 强制子组件填充所有剩余可用空间（相当于 `Flexible`，`fit: FlexFit.tight` 且 `flex` 因子为 1.0）。
    *   使用 `Flexible` 允许子组件根据特定限制调整大小，同时仍可扩展/收缩。使用 `flex` 因子定义兄弟组件之间的空间消耗比例。
*   **约束宽度：** 防止组件在大屏幕上占用所有水平空间。将 `GridView` 或 `ListView` 等组件包裹在 `ConstrainedBox` 或 `Container` 中，并在 `BoxConstraints` 中定义 `maxWidth`。
*   **惰性渲染：** 当渲染具有未知或大量项的列表时，始终使用 `ListView.builder` 或 `GridView.builder`。

## 设备和方向行为
确保应用在所有设备形态和输入方式下表现正确。

*   **不要锁定屏幕方向。** 锁定方向会导致折叠设备上严重的布局问题，通常导致应用居中显示并带有黑色边框。Android 大型格式层级要求同时支持横屏和竖屏。
*   **锁定方向的回退方案：** 如果业务需求严格要求锁定方向，使用 `Display API` 获取物理屏幕尺寸，而不是 `MediaQuery`。`MediaQuery` 在兼容模式下无法接收更大的窗口尺寸。
*   **支持多种输入方式：** 实现对基本鼠标、触控板和键盘快捷键的支持。确保触摸目标尺寸适当，键盘导航可访问。

## 工作流：构建自适应布局

遵循以下工作流以实现适应可用 `BoxConstraints` 的布局。

**任务进度：**
- [ ] 确定需要自适应行为的目标组件。
- [ ] 将组件树包裹在 `LayoutBuilder` 中。
- [ ] 从构建器回调中提取 `constraints.maxWidth`。
- [ ] 定义自适应断点（例如，`largeScreenMinWidth = 600`）。
- [ ] **如果 `maxWidth > largeScreenMinWidth`：** 返回大屏幕布局（例如，一个 `Row` 将导航侧边栏和内容区域并排放置）。
- [ ] **如果 `maxWidth <= largeScreenMinWidth`：** 返回小屏幕布局（例如，`Column` 或标准导航方式）。
- [ ] 运行验证器 -> 调整应用窗口大小 -> 审查布局过渡 -> 修复溢出错误。

## 工作流：优化大屏幕

遵循以下工作流以防止 UI 元素在大屏幕上异常拉伸。

**任务进度：**
- [ ] 确定全宽组件（例如，`ListView`、文本块、表单）。
- [ ] **如果优化列表：** 使用 `SliverGridDelegateWithMaxCrossAxisExtent` 将 `ListView.builder` 转换为 `GridView.builder`，根据窗口大小自动调整列数。
- [ ] **如果优化表单或文本块：** 将组件包裹在 `ConstrainedBox` 中。
- [ ] 对 `ConstrainedBox` 应用 `BoxConstraints(maxWidth: [optimal_width])`。
- [ ] 将 `ConstrainedBox` 包裹在 `Center` 组件中，以保持约束内容在大屏幕上居中。
- [ ] 运行验证器 -> 在桌面/平板目标上测试 -> 审查水平拉伸 -> 调整 `maxWidth` 或网格范围。

## 示例

### 使用 LayoutBuilder 的自适应布局
演示基于可用宽度在移动端和桌面端布局之间切换。

```dart
import 'package:flutter/material.dart';

const double largeScreenMinWidth = 600.0;

class AdaptiveLayout extends StatelessWidget {
  const AdaptiveLayout({super.key});

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        if (constraints.maxWidth > largeScreenMinWidth) {
          return _buildLargeScreenLayout();
        } else {
          return _buildSmallScreenLayout();
        }
      },
    );
  }

  Widget _buildLargeScreenLayout() {
    return Row(
      children: [
        const SizedBox(width: 250, child: Placeholder(color: Colors.blue)),
        const VerticalDivider(width: 1),
        Expanded(child: const Placeholder(color: Colors.green)),
      ],
    );
  }

  Widget _buildSmallScreenLayout() {
    return const Placeholder(color: Colors.green);
  }
}
```

### 在大屏幕上约束宽度
演示防止组件占用所有水平空间。

```dart
import 'package:flutter/material.dart';

class ConstrainedContent extends StatelessWidget {
  const ConstrainedContent({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(
            maxWidth: 800.0, // 最大宽度以提高可读性
          ),
          child: ListView.builder(
            itemCount: 50,
            itemBuilder: (context, index) {
              return ListTile(
                title: Text('Item $index'),
              );
            },
          ),
        ),
      ),
    );
  }
}
```
