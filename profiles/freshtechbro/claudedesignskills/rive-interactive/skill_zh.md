# Rive 交互式 - 基于状态机的矢量动画

## 概述

Rive 是一个基于状态机的动画平台，使设计师能够创建具有复杂逻辑和运行时交互性的交互式矢量动画。与仅支持时间轴的动画工具（如 Lottie）不同，Rive 支持状态机、输入处理以及应用程序代码与动画之间的双向数据绑定。

**主要功能**：
- 基于状态机的复杂交互逻辑系统
- ViewModel API 用于双向数据绑定
- 输入处理（布尔值、数字、触发器输入）
- 自定义事件用于动画与代码的通信
- 运行时属性控制（颜色、字符串、数字、枚举）
- 跨平台支持（Web、React、React Native、iOS、Android、Flutter）
- 使用矢量图形的小文件大小

**何时使用此技能**：
- 创建具有复杂状态转换的 UI 动画
- 构建交互式动画组件（按钮、切换器、加载器）
- 实现具有状态驱动动画的游戏式 UI
- 将实时数据绑定到动画可视化效果
- 创建响应用户输入的动画
- 处理需要运行时控制的设计师创建的动画

**替代方案**：
- **Lottie** (lottie-animations)：用于更简单的基于时间轴的动画，不包含状态机
- **Framer Motion** (motion-framer)：用于具有弹簧物理效果的代码优先 React 动画
- **GSAP** (gsap-scrolltrigger)：用于基于时间轴的网页动画，具有精确控制

## 核心概念

### 1. 状态机

状态机通过状态和转换定义动画行为：
- **状态**：不同的动画状态（例如，空闲、悬停、按下）
- **输入**：控制转换的变量（布尔值、数字、触发器）
- **转换**：在状态之间移动的规则
- **监听器**：响应状态变化的钩子

### 2. 输入

三种输入类型控制状态机行为：
- **布尔值**：开/关状态（例如，isHovered、isActive）
- **数字**：数值（例如，进度、音量）
- **触发器**：一次性事件（例如，点击、提交）

### 3. ViewModel

用于动态属性的绑定系统：
- **字符串属性**：文本内容（例如，username、title）
- **数字属性**：数值数据（例如，股票价格、分数）
- **颜色属性**：动态颜色（十六进制值）
- **枚举属性**：从预定义选项中选择
- **触发器属性**：动画事件

### 4. 事件

从动画发出的自定义事件：
- **通用事件**：自定义命名事件
- **事件属性**：附加到事件的数据
- **事件监听器**：处理事件的钩子

## 常见模式

### 模式 1：基本 Rive 动画

**用例**：在 React 中显示简单的 Rive 动画

**实现**：

```bash
# 安装
npm install rive-react
```

```jsx
import Rive from 'rive-react';

export default function SimpleAnimation() {
  return (
    <Rive
      src="animation.riv"
      artboard="Main"
      animations="idle"
      layout={{ fit: "contain", alignment: "center" }}
      style={{ width: '400px', height: '400px' }}
    />
  );
}
```

**要点**：
- `src`：.riv 文件的路径
- `artboard`：要显示的画板
- `animations`：要播放的动画时间轴
- `layout`：动画如何在容器中适配

### 模式 2：使用输入控制状态机

**用例**：根据用户交互控制动画状态

**实现**：

```jsx
import { useRive, useStateMachineInput } from 'rive-react';

export default function InteractiveButton() {
  const { rive, RiveComponent } = useRive({
    src: 'button.riv',
    stateMachines: 'Button State Machine',
    autoplay: true,
  });

  // 获取状态机输入
  const hoverInput = useStateMachineInput(
    rive,
    'Button State Machine',
    'isHovered',
    false
  );

  const clickInput = useStateMachineInput(
    rive,
    'Button State Machine',
    'isClicked',
    false
  );

  return (
    <div
      onMouseEnter={() => hoverInput && (hoverInput.value = true)}
      onMouseLeave={() => hoverInput && (hoverInput.value = false)}
      onClick={() => clickInput && clickInput.fire()} // 触发输入
      style={{ cursor: 'pointer' }}
    >
      <RiveComponent style={{ width: '200px', height: '100px' }} />
    </div>
  );
}
```

**输入类型**：
- 布尔值：`input.value = true/false`
- 数字：`input.value = 50`
- 触发器：`input.fire()`

### 模式 3：ViewModel 数据绑定

**用例**：将应用程序数据绑定到动画属性

**实现**：

```jsx
import { useRive, useViewModel, useViewModelInstance,
         useViewModelInstanceString, useViewModelInstanceNumber } from 'rive-react';
import { useEffect, useState } from 'react';

export default function Dashboard() {
  const [stockPrice, setStockPrice] = useState(150.0);

  const { rive, RiveComponent } = useRive({
    src: 'dashboard.riv',
    autoplay: true,
    autoBind: false, // 手动绑定 ViewModel
  });

  // 获取 ViewModel 和实例
  const viewModel = useViewModel(rive, { name: 'Dashboard' });
  const viewModelInstance = useViewModelInstance(viewModel, { rive });

  // 绑定属性
  const { setValue: setTitle } = useViewModelInstanceString(
    'title',
    viewModelInstance
  );

  const { setValue: setPrice } = useViewModelInstanceNumber(
    'stockPrice',
    viewModelInstance
  );

  useEffect(() => {
    if (setTitle) setTitle('Stock Dashboard');
  }, [setTitle]);

  useEffect(() => {
    if (setPrice) setPrice(stockPrice);
  }, [setPrice, stockPrice]);

  // 模拟实时更新
  useEffect(() => {
    const interval = setInterval(() => {
      setStockPrice((prev) => prev + (Math.random() - 0.5) * 10);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return <RiveComponent style={{ width: '800px', height: '600px' }} />;
}
```

**ViewModel 属性钩子**：
- `useViewModelInstanceString` - 文本属性
- `useViewModelInstanceNumber` - 数值属性
- `useViewModelInstanceColor` - 颜色属性（十六进制）
- `useViewModelInstanceEnum` - 枚举选择
- `useViewModelInstanceTrigger` - 动画触发器

### 模式 4：处理 Rive 事件

**用例**：响应 Rive 动画发出的事件

**实现**：

```jsx
import { useRive, EventType, RiveEventType } from 'rive-react';
import { useEffect } from 'react';

export default function InteractiveRating() {
  const { rive, RiveComponent } = useRive({
    src: 'rating.riv',
    stateMachines: 'State Machine 1',
    autoplay: true,
    automaticallyHandleEvents: true,
  });

  useEffect(() => {
    if (!rive) return;

    const onRiveEvent = (event) => {
      const eventData = event.data;

      if (eventData.type === RiveEventType.General) {
        console.log('Event:', eventData.name);

        // 访问事件属性
        const rating = eventData.properties.rating;
        const message = eventData.properties.message;

        if (rating >= 4) {
          alert(`感谢 ${rating} 星评价：${message}`);
        }
      }
    };

    rive.on(EventType.RiveEvent, onRiveEvent);

    return () => {
      rive.off(EventType.RiveEvent, onRiveEvent);
    };
  }, [rive]);

  return <RiveComponent style={{ width: '400px', height: '300px' }} />;
}
```

### 模式 5：预加载 Rive 文件

**用例**：通过预加载动画优化加载时间

**实现**：

```jsx
import { useRiveFile, useRive } from 'rive-react';

export default function PreloadedAnimation() {
  const { riveFile, status } = useRiveFile({
    src: 'large-animation.riv',
  });

  const { RiveComponent } = useRive({
    riveFile: riveFile,
    artboard: 'Main',
    autoplay: true,
  });

  if (status === 'loading') {
    return <div>加载动画中...</div>;
  }

  if (status === 'failed') {
    return <div>加载动画失败</div>;
  }

  return <RiveComponent style={{ width: '600px', height: '400px' }} />;
}
```

### 模式 6：使用 Refs 控制动画

**用例**：从父组件控制动画

**实现**：

```jsx
import { useRive, useViewModel, useViewModelInstance,
         useViewModelInstanceTrigger } from 'rive-react';
import { useImperativeHandle, forwardRef } from 'react';

const AnimatedComponent = forwardRef((props, ref) => {
  const { rive, RiveComponent } = useRive({
    src: 'logo.riv',
    autoplay: true,
    autoBind: false,
  });

  const viewModel = useViewModel(rive, { useDefault: true });
  const viewModelInstance = useViewModelInstance(viewModel, { rive });

  const { trigger: spinTrigger } = useViewModelInstanceTrigger(
    'triggerSpin',
    viewModelInstance
  );

  // 向父组件暴露方法
  useImperativeHandle(ref, () => ({
    spin: () => spinTrigger && spinTrigger(),
    pause: () => rive && rive.pause(),
    play: () => rive && rive.play(),
  }));

  return <RiveComponent style={{ width: '200px', height: '200px' }} />;
});

export default function App() {
  const animationRef = useRef();

  return (
    <div>
      <AnimatedComponent ref={animationRef} />
      <button onClick={() => animationRef.current?.spin()}>旋转</button>
      <button onClick={() => animationRef.current?.pause()}>暂停</button>
    </div>
  );
}
```

### 模式 7：多属性 ViewModel 更新

**用例**：从复杂数据更新多个动画属性

**实现**：

```jsx
import { useRive, useViewModel, useViewModelInstance,
         useViewModelInstanceString, useViewModelInstanceNumber,
         useViewModelInstanceColor } from 'rive-react';
import { useEffect } from 'react';

export default function UserProfile({ user }) {
  const { rive, RiveComponent } = useRive({
    src: 'profile.riv',
    autoplay: true,
    autoBind: false,
  });

  const viewModel = useViewModel(rive, { useDefault: true });
  const viewModelInstance = useViewModelInstance(viewModel, { rive });

  // 绑定所有属性
  const { setValue: setName } = useViewModelInstanceString('name', viewModelInstance);
  const { setValue: setScore } = useViewModelInstanceNumber('score', viewModelInstance);
  const { setValue: setColor } = useViewModelInstanceColor('avatarColor', viewModelInstance);

  useEffect(() => {
    if (user && setName && setScore && setColor) {
      setName(user.name);
      setScore(user.score);
      setColor(parseInt(user.color.substring(1), 16)); // 将十六进制转换为数字
    }
  }, [user, setName, setScore, setColor]);

  return <RiveComponent style={{ width: '300px', height: '300px' }} />;
}
```

## 集成模式

### 与 Framer Motion (motion-framer)

使用 Framer Motion 动画容器，Rive 处理交互内容：

```jsx
import { motion } from 'framer-motion';
import Rive from 'rive-react';

export default function AnimatedCard() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.05 }}
    >
      <Rive
        src="card.riv"
        stateMachines="Card State Machine"
        style={{ width: '300px', height: '400px' }}
      />
    </motion.div>
  );
}
```

### 与 GSAP ScrollTrigger (gsap-scrolltrigger)

滚动时触发 Rive 动画：

```jsx
import { useRive, useStateMachineInput } from 'rive-react';
import { useEffect, useRef } from 'react';
import gsap from 'gsap';
import ScrollTrigger from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export default function ScrollRive() {
  const containerRef = useRef();
  const { rive, RiveComponent } = useRive({
    src: 'scroll-animation.riv',
    stateMachines: 'State Machine 1',
    autoplay: true,
  });

  const trigger = useStateMachineInput(rive, 'State Machine 1', 'trigger');

  useEffect(() => {
    if (!trigger) return;

    ScrollTrigger.create({
      trigger: containerRef.current,
      start: 'top center',
      onEnter: () => trigger.fire(),
    });
  }, [trigger]);

  return (
    <div ref={containerRef}>
      <RiveComponent style={{ width: '100%', height: '600px' }} />
    </div>
  );
}
```

## 性能优化

### 1. 使用离屏渲染器

```jsx
<Rive
  src="animation.riv"
  useOffscreenRenderer={true} // 更好的性能
/>
```

### 2. 优化 Rive 文件

**在 Rive 编辑器中**：
- 保持画板小于 2MB
- 使用矢量图形（尽可能避免使用位图）
- 最小化骨骼动画中的骨骼数量
- 减少状态机的复杂性

### 3. 预加载关键动画

```jsx
const { riveFile } = useRiveFile({ src: 'critical.riv' });
// 在应用程序初始化时预加载
```

### 4. 禁用自动事件处理

```jsx
<Rive
  src="animation.riv"
  automaticallyHandleEvents={false} // 手动控制
/>
```

## 常见陷阱和解决方案

### 陷阱 1：状态机输入未找到

**问题**：`useStateMachineInput` 返回 null

**解决方案**：
```jsx
// ❌ 错误：输入名称不正确
const input = useStateMachineInput(rive, 'State Machine', 'wrongName');

// ✅ 正确：与 Rive 编辑器中的确切名称匹配
const input = useStateMachineInput(rive, 'State Machine', 'isHovered');

// 始终检查输入是否存在后再使用
if (input) {
  input.value = true;
}
```

### 陷阱 2：ViewModel 属性未更新

**问题**：ViewModel 属性不更新动画

**解决方案**：
```jsx
// ❌ 错误：启用 autoBind
const { rive } = useRive({
  src: 'dashboard.riv',
  autoplay: true,
  // autoBind: true (默认)
});

// ✅ 正确：禁用 autoBind 以手动控制 ViewModel
const { rive } = useRive({
  src: 'dashboard.riv',
  autoplay: true,
  autoBind: false, // 控制ViewModel所需的
});
```

### 陷阱 3：事件监听器未触发

**问题**：Rive 事件未触发回调

**解决方案**：
```jsx
// ❌ 错误：缺少 automaticallyHandleEvents
const { rive } = useRive({
  src: 'rating.riv',
  stateMachines: 'State Machine 1',
  autoplay: true,
});

// ✅ 正确：启用事件处理
const { rive } = useRive({
  src: 'rating.riv',
  stateMachines: 'State Machine 1',
  autoplay: true,
  automaticallyHandleEvents: true, // 事件所需的
});
```

## 资源

### 官方文档
- **Rive 文档**：https://rive.app/docs
- **React Rive GitHub**：https://github.com/rive-app/rive-react
- **Rive 社区**：https://rive.app/community

### Rive 编辑器
- **Web 编辑器**：https://rive.app/community
- **桌面应用程序**：适用于 macOS、Windows

### 学习资源
- **教程**：https://rive.app/learn
- **示例**：https://rive.app/community/files
- **状态机指南**：https://rive.app/docs/state-machine

## 相关技能

- **lottie-animations**：用于更简单的基于时间轴的动画，不包含状态机
- **motion-framer**：用于代码优先的 React 动画，具有手势
- **gsap-scrolltrigger**：用于滚动驱动的动画
- **spline-interactive**：用于 3D 交互式动画

## 脚本

此技能包含实用脚本：
- `component_generator.py` - 生成 Rive React 组件模板
- `viewmodel_builder.py` - 构建 ViewModel 属性绑定

从技能目录运行脚本：
```bash
./scripts/component_generator.py
./scripts/viewmodel_builder.py
```

## 资产

启动模板和示例：
- `starter_rive/` - 完整的 React + Rive 模板
- `examples/` - 真实的集成模式
