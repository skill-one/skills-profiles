# GSAP 时间轴

## 何时使用此技能

当构建多步骤动画、协调多个补间动画按顺序或并行执行，或用户询问关于 GSAP 的时间轴、序列化或关键帧式动画时，使用此技能。

**相关技能：** 对于单个补间动画和缓动效果，使用 **gsap-core**；对于滚动驱动时间轴，使用 **gsap-scrolltrigger**；对于 React 项目，使用 **gsap-react**。

## 创建时间轴

```javascript
const tl = gsap.timeline();
tl.to(".a", { x: 100, duration: 1 })
  .to(".b", { y: 50, duration: 0.5 })
  .to(".c", { opacity: 0, duration: 0.3 });
```

默认情况下，补间动画会**依次追加**。使用**位置参数**将补间动画放置到特定时间或相对于其他补间动画的位置。

## 位置参数

第三个参数（或 vars 中的位置属性）控制放置方式：

- **绝对**：`1` — 从 1 秒开始。
- **相对（默认）**：`"+=0.5"` — 在结束后的 0.5 秒处；`"-=0.2"` — 在结束前 0.2 秒处。
- **标签**：`"labelName"` — 在该标签处；`"labelName+=0.3"` — 在标签后 0.3 秒处。
- **放置**：`" <"` — 在最近添加的动画开始时开始；`">"` — 在最近添加的动画结束时开始（默认）；`" <0.2"` — 在最近添加的动画开始后 0.2 秒处。

示例：

```javascript
tl.to(".a", { x: 100 }, 0);           // 在 0 处
tl.to(".b", { y: 50 }, "+=0.5");      // 在最后结束后的 0.5 秒处
tl.to(".c", { opacity: 0 }, "<");     // 与上一个动画开始位置相同
tl.to(".d", { scale: 2 }, "<0.2");    // 在之前的动画开始后 0.2 秒处
```

## 时间轴默认值

将默认值传入时间轴，使所有子补间动画继承：

```javascript
const tl = gsap.timeline({ defaults: { duration: 0.5, ease: "power2.out" } });
tl.to(".a", { x: 100 }).to(".b", { y: 50 }); // 两者均使用 0.5 秒和 power2.out
```

## 时间轴选项（构造函数）

- **paused: true** — 创建为暂停状态；调用 `.play()` 开始播放。
- **repeat**、**yoyo** — 与补间动画相同；应用于整个时间轴。
- **onComplete**、**onStart**、**onUpdate** — 时间轴级别的回调。
- **defaults** — 变量合并到每个子补间动画中。

## 标签

使用标签实现可读、易于维护的序列化：

```javascript
tl.addLabel("intro", 0);
tl.to(".a", { x: 100 }, "intro");
tl.addLabel("outro", "+=0.5");
tl.to(".b", { opacity: 0 }, "outro");
tl.play("outro");  // 从 "outro" 开始
tl.tweenFromTo("intro", "outro"); // 暂停时间轴并返回一个新的 Tween，该 Tween 无缓动地动画化时间轴指针从 intro 移动到 outro。
```

## 嵌套时间轴

时间轴可以包含其他时间轴。

```javascript
const master = gsap.timeline();
const child = gsap.timeline();
child.to(".a", { x: 100 }).to(".b", { y: 50 });
master.add(child, 0);
master.to(".c", { opacity: 0 }, "+=0.2");
```

## 控制播放

- **tl.play()** / **tl.pause()**
- **tl.reverse()** / **tl.progress(1)** 然后 **tl.reverse()**
- **tl.restart()** — 从开始处。
- **tl.time(2)** — 跳转至 2 秒处。
- **tl.progress(0.5)** — 跳转至 50%。
- **tl.kill()** — 终止时间轴及其（默认）子元素。

## GSAP 官方最佳实践

- ✅ 优先使用时间轴进行序列化
- ✅ 使用**位置参数**（第三个参数）将补间动画放置到特定时间或相对于标签的位置。
- ✅ 使用 `addLabel()` 添加**标签**，实现可读、易于维护的序列化。
- ✅ 将**defaults**传入时间轴构造函数，使子补间动画继承持续时间、缓动效果等。
- ✅ 将 ScrollTrigger 放置在时间轴（或顶层补间动画）上，而不是放置在时间轴内的补间动画上。

## 不要这样做

- ❌ 当时间轴可以序列化动画时，不要使用**延迟**链式添加动画；优先使用 `gsap.timeline()` 和位置参数来实现多步骤动画。
- ❌ 在多个子补间动画共享相同持续时间或缓动效果时，忘记传入**defaults**（例如 `defaults: { duration: 0.5, ease: "power2.out" }`）。
- ❌ 忘记时间轴构造函数中的**duration**与补间动画的 duration 不同；时间轴的"duration"由其子元素决定。
- ❌ 嵌套包含 ScrollTrigger 的动画；ScrollTrigger 只能位于顶层补间动画/时间轴上。
