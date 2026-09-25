# 移动触控动画

将迪士尼的12项动画原则应用于移动手势、触觉反馈和原生应用动画。

## 快速参考

| 原则 | 移动实现 |
|------|----------|
| 压缩与拉伸 | 弹簧效果、滚动边界反弹 |
| 预期 | 提前预览再执行、长按预览 |
| 舞台效果 | 簿记式呈现、焦点状态 |
| 直接前进/姿态到姿态 | 手势驱动过渡 vs 预设过渡 |
| 后续动作/重叠 | 动态滚动、拖尾元素 |
| 缓入缓出 | iOS 弹簧动画、材质过渡 |
| 弧线 | 滑动删除曲线、卡片抛出 |
| 次要动作 | 触觉脉冲配合视觉反馈 |
| 时序 | 触摸响应 <100ms、过渡 250-350ms |
| 夸张 | 反弹幅度、触觉强度 |
| 实体绘制 | 尊重安全区域、一致锚点 |
| 吸引力 | 最低60fps、手势连续性 |

## 原则应用

**压缩与拉伸**：在滚动边界实现弹簧效果。下拉刷新应自然拉伸内容。按钮在触摸时压缩。

**预期**：长按显示执行前的预览。拖拽阈值在物品抬起前提供视觉提示。滑动显示目标内容边缘。

**舞台效果**：使用簿记式呈现保持上下文。在模态焦点时变暗并缩放背景。英雄过渡有意义地连接视图。

**直接前进 vs 姿态到姿态**：手势跟随动画（拖拽、捏合）是直接前进——由触摸输入驱动。系统过渡（推送、呈现）是姿态到姿态——预定义关键帧。

**后续动作与重叠**：手指抬起后内容继续移动（惯性）。导航栏元素在主内容动画后轻微动画。列表项以交错方式稳定。

**缓入缓出**：iOS 使用弹簧物理——配置质量、刚度、阻尼。Android 材质使用标准缓动：`FastOutSlowIn`。用户触发的动画绝不用线性。

**弧线**：抛出的卡片遵循抛物线弧。滑动删除曲线基于速度矢量。FAB 展开/收起遵循自然弧线路径。

**次要动作**：将触觉反馈与视觉响应配对。按钮涟漪伴随按压。成功对勾触发轻微触觉。

**时序**：触摸确认：<100ms。快速操作：150-250ms。视图过渡：250-350ms。复杂动画：350-500ms。触觉应与视觉精确同步。

**夸张**：下拉刷新应超出自然拉伸——使反馈清晰。错误摇晃应明显。成功动画应适当庆祝。

**实体绘制**：动画时尊重设备安全区域。保持一致的变换原点。在运动路径中考虑刘海/动态岛。

**吸引力**：最低60fps，ProMotion 显示器目标120fps。手势驱动动画必须感觉与手指连接。可中断动画至关重要。

## 平台模式

### iOS
```swift
// 弹簧动画带后续动作
UIView.animate(withDuration: 0.5,
               delay: 0,
               usingSpringWithDamping: 0.7,
               initialSpringVelocity: 0.5,
               options: .curveEaseOut)

// 触觉配对
let feedback = UIImpactFeedbackGenerator(style: .medium)
feedback.impactOccurred()
```

### Android
```kotlin
// 材质弹簧动画
SpringAnimation(view, DynamicAnimation.TRANSLATION_Y)
    .setSpring(SpringForce()
        .setStiffness(SpringForce.STIFFNESS_MEDIUM)
        .setDampingRatio(SpringForce.DAMPING_RATIO_MEDIUM_BOUNCY))
    .start()
```

## 触觉指南

| 动作 | iOS | Android |
|------|-----|---------|
| 选择 | `.selection` | `EFFECT_TICK` |
| 成功 | `.success` | `EFFECT_CLICK` |
| 警告 | `.warning` | `EFFECT_DOUBLE_CLICK` |
| 错误 | `.error` | `EFFECT_HEAVY_CLICK` |

触觉是次要动作——始终与视觉确认配对。
