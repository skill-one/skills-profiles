# Phaser 3 游戏开发

你是一位使用 game-creator 插件进行 Phaser 游戏开发的专家。遵循以下模式，以生产结构良好、视觉精美且可维护的 2D 浏览器游戏。

## 核心原则

1. **先实现核心循环** — 在任何修饰之前，先实现最基本的游戏循环：boot → preload → create → update。在视觉效果、音频或动画之前，添加胜利/失败条件和计分。保持初始范围较小：1 个场景、1 个机制、1 个失败条件。在核心循环旁边布线展示性 EventBus 钩子 (`SPECTACLE_*` 事件) — 它们是脚手架的一部分，而不是延迟的修饰。
2. **TypeScript 优先** — 始终使用 TypeScript 以获得类型安全和 IDE 支持
3. **基于场景的架构** — 每个游戏界面都是一个 Scene；保持它们专注
4. **Vite 打包** — 使用官方的 `phaserjs/template-vite-ts` 模板
5. **组合优于继承** — 优先组合行为，而不是深层次的类层次结构
6. **数据驱动设计** — 在 JSON/数据文件中定义关卡、敌人和配置
7. **事件驱动通信** — 所有跨场景/系统的通信都通过 EventBus
8. **重启安全** — 游戏玩法必须完全重启安全且确定性。`GameState.reset()` 必须恢复一个干净的起点。没有陈旧的引用、残留的计时器或重启时的泄漏事件监听器。

## 展示性事件

每个玩家操作和游戏事件都必须至少发出一个展示性事件。这些钩子存在于模板 EventBus 中 — 设计阶段将视觉效果附加到它们上。

| 事件 | 常量 | 发出时机 |
|------|------|----------|
| `spectacle:entrance` | `SPECTACLE_ENTRANCE` | 在 `create()` 中，当玩家/实体首次出现在屏幕上时 |
| `spectacle:action` | `SPECTACLE_ACTION` | 在每个玩家输入（点击、跳跃、射击、滑动）时 |
| `spectacle:hit` | `SPECTACLE_HIT` | 当玩家击中/摧毁敌人、收集物品或得分时 |
| `spectacle:combo` | `SPECTACLE_COMBO` | 当连续击中/得分且没有失误时。传递 `{ combo: n }` |
| `spectacle:streak` | `SPECTACLE_STREAK` | 当连击达到里程碑（5、10、25、50）时。传递 `{ streak: n }` |
| `spectacle:near_miss` | `SPECTACLE_NEAR_MISS` | 当玩家险些避开危险（在 ~20% 的碰撞半径内）时 |

**规则**：如果一个游戏玩法时刻没有展示性事件，添加一个。设计阶段无法修饰它无法钩入的内容。

## 强制性约定

所有游戏必须遵循 [game-creator 约定](conventions.md)：

- **`core/` 目录** 包含 EventBus、GameState 和 Constants
- **EventBus 单例** — `domain:action` 事件命名，无直接场景引用
- **GameState 单例** — 集中化状态，带有 `reset()` 以实现干净的重启
- **常量文件** — 每个魔法数字、颜色、速度和配置值 — 零硬编码值
- **场景清理** — 在 `shutdown()` 中移除 EventBus 监听器

参见 [conventions.md](conventions.md) 获取完整细节和代码示例。

## 项目设置

使用官方的 Vite + TypeScript 模板作为你的起点：

```bash
npx degit phaserjs/template-vite-ts my-game
cd my-game && npm install
```

### 必要的目录结构

```
src/
├── core/
│   ├── EventBus.ts        # 单例事件总线 + 事件常量
│   ├── GameState.ts       # 集中化状态，带有 reset()
│   └── Constants.ts       # 所有配置值
├── scenes/
│   ├── Boot.ts            # 最小化设置，启动 Game 场景
│   ├── Preloader.ts       # 加载所有资源，显示进度条
│   ├── Game.ts            # 主要游戏玩法（立即开始，无标题屏幕）
│   └── GameOver.ts        # 结束屏幕，带重启
├── objects/               # 游戏实体（玩家、敌人等）
├── systems/               # 管理器和子系统
├── ui/                    # UI 组件（按钮、条形图、对话框）
├── audio/                 # 音频管理器、音乐、SFX
├── config.ts              # Phaser.Types.Core.GameConfig
└── main.ts                # 入口点
```

参见 [project-setup.md](project-setup.md) 获取完整配置和工具细节。

## 场景架构

- **生命周期**：`init()` → `preload()` → `create()` → `update(time, delta)`
- 使用 `init()` 接收场景转换的数据
- 在专门的 `Preloader` 场景中加载资源，而不是在每个场景中加载
- 保持 `update()` 简洁 — 将委托给子系统和游戏对象
- **默认无标题屏幕** — 直接进入游戏玩法。只有当用户明确要求时，才添加标题/菜单场景
- **默认无游戏内计分 HUD** — Play.fun 小部件在游戏顶部死区显示得分。不要为计分显示创建单独的 UIScene 或 HUD 叠加层
- 仅在请求时使用并行场景进行 UI 叠加层（暂停菜单）

### Play.fun 安全区

当游戏在移动 Safari 的 Play.fun 仪表板中运行时，SDK 在游戏 iframe 的 `document.documentElement` 上设置 CSS 自定义属性：

- `--ogp-safe-top-inset` — Play.fun 标题气泡下方的空间（移动端约 68px）
- `--ogp-safe-bottom-inset` — Safari 底部控件上方的空间（移动端约 148px）

两者在不在仪表板中运行时（桌面、独立）默认为 `0px`。

模板的 `Constants.js` 在启动时读取这些值，并在 canvas 像素中暴露 `SAFE_ZONE.TOP` 和 `SAFE_ZONE.BOTTOM`（CSS 值 × DPR）。静态回退（`GAME.HEIGHT * 0.08`）确保即使没有 SDK，顶部安全区也能工作。

**规则**：
- 所有 UI 文本、按钮和 HUD 元素必须定位在 `SAFE_ZONE.TOP` 下方和 `GAME.HEIGHT - SAFE_ZONE.BOTTOM` 上方
- 游戏实体不应在安全区生成
- 游戏结束屏幕、计分面板和重启按钮必须偏移 `SAFE_ZONE.TOP` 和 `SAFE_ZONE.BOTTOM`
- 使用 `const usableH = GAME.HEIGHT - SAFE_ZONE.TOP - SAFE_ZONE.BOTTOM` 计算比例位置（在 UI 场景中）
- 游戏画布和背景应填满整个视口（超出浏览器边框）
- 底部的触摸控制必须考虑 `SAFE_ZONE.BOTTOM`

```js
import { SAFE_ZONE } from '../core/Constants.js';

// 在任何 UI 场景中：
const safeTop = SAFE_ZONE.TOP;
const safeBottom = SAFE_ZONE.BOTTOM;
const usableH = GAME.HEIGHT - safeTop - safeBottom;
const title = this.add.text(cx, safeTop + usableH * 0.15, 'GAME OVER', { ... });
const button = createButton(scene, cx, safeTop + usableH * 0.6, 'PLAY AGAIN', callback);

// 触摸控制 / 底部 HUD：
const bottomY = GAME.HEIGHT - safeBottom - 40 * PX;
```

**在 Constants.js 中如何工作**：

```js
function _readSafeInsets() {
  const s = getComputedStyle(document.documentElement);
  const top = parseInt(s.getPropertyValue('--ogp-safe-top-inset')) || 0;
  const bottom = parseInt(s.getPropertyValue('--ogp-safe-bottom-inset')) || 0;
  return { top: top * DPR, bottom: bottom * DPR };
}
const _insets = _readSafeInsets();

export const SAFE_ZONE = {
  TOP: Math.max(GAME.HEIGHT * 0.08, _insets.top),
  BOTTOM: _insets.bottom,
  LEFT: 0,
  RIGHT: 0,
};
```

- 通过 EventBus（而不是直接引用）在场景之间通信

参见 [scenes-and-lifecycle.md](scenes-and-lifecycle.md) 获取模式和示例。

## 游戏对象

- 继承 `Phaser.GameObjects.Sprite`（或其他基础类）以创建自定义对象
- 使用 `Phaser.GameObjects.Group` 进行对象池（子弹、金币、敌人）
- 使用 `Phaser.GameObjects.Container` 进行组合对象，但避免深层嵌套
- 使用 `GameObjectFactory` 注册自定义对象以进行场景级访问

参见 [game-objects.md](game-objects.md) 获取实现模式。

## 物理引擎

- **Arcade Physics** — 用于简单游戏（平台游戏、俯视视角）。快速且轻量级。
- **Matter.js** — 当你需要真实碰撞、约束或复杂形状时使用。
- 在同一游戏中永远不要混合物理引擎。
- 使用 **状态模式** 进行角色移动（空闲、行走、跳跃、攻击）。

参见 [physics-and-movement.md](physics-and-movement.md) 获取详细信息。

## 性能（关键规则）

- **使用纹理图集** — 将精灵打包进图集，在规模上不要加载单独的图像
- **对象池** — 使用 Groups 带有 `maxSize`；使用 `setActive(false)` / `setVisible(false)` 回收
- **最小化更新工作** — 仅迭代活动对象；使用 `getChildren().filter(c => c.active)`
- **相机剔除** — 用于大型世界；屏幕外的对象跳过渲染
- **批量渲染** — 每帧唯一的纹理越少 = 更好的绘制调用批处理
- **移动端** — 减少粒子数量，简化物理，考虑 30fps 目标
- **`pixelArt: true`** — 在游戏配置中启用（用于像素艺术游戏，最近邻缩放）

参见 [assets-and-performance.md](assets-and-performance.md) 获取完整优化指南。

## 高级模式

- **ECS with bitECS** — 实体组件系统，用于数据导向设计（Phaser 4 内部使用）
- **状态机** — 清晰管理实体行为状态
- **单例管理器** — 跨场景服务（音频、保存数据、分析）
- **事件总线** — 使用共享 EventEmitter 解耦系统
- **Tiled 集成** — 使用 Tiled 地图编辑器进行关卡设计

参见 [patterns.md](patterns.md) 获取实现。

## 移动输入策略（60/40 规则）

所有游戏必须适用于桌面和移动端，除非明确指定否则如此。60% 移动端 / 40% 桌面端进行权衡。为每个游戏概念选择最佳移动输入：

| 游戏类型 | 主要移动输入 | 桌面输入 |
|-----------|---------------------|---------------|
| 平台游戏 | 点击左/右半边 + 点击跳跃 | 箭头键 / WASD |
| 跑酷/无尽 | 点击 / 滑动向上跳跃 | 空格键 / 上箭头 |
| 解谜/匹配 | 点击目标（最小 44px） | 点击 |
| 射击游戏 | 虚拟摇杆 + 点击射击 | 鼠标 + WASD |
| 俯视视角 | 虚拟摇杆 | 箭头键 / WASD |

### 实现模式

将输入抽象为 `inputState` 对象，使游戏逻辑与源无关：

```typescript
// 在 Scene update() 中：
const isMobile = this.sys.game.device.os.android ||
  this.sys.game.device.os.iOS || this.sys.game.device.os.iPad;

let left = false, right = false, jump = false;

// 键盘
left = this.cursors.left.isDown || this.wasd.left.isDown;
right = this.cursors.right.isDown || this.wasd.right.isDown;
jump = Phaser.Input.Keyboard.JustDown(this.spaceKey);

// 触摸（与键盘合并）
if (isMobile) {
  // 左半边点击 = 左，右半边 = 右，或使用点击区域
  this.input.on('pointerdown', (p) => {
    if (p.x < this.scale.width / 2) left = true;
    else right = true;
  });
}

this.player.update({ left, right, jump });
```

### 响应式画布配置（Retina/高 DPI）

参见 [project-setup.md](project-setup.md) 获取完整的响应式画布配置、实体尺寸、HTML 模板和优先竖屏游戏模式。

### 可见触摸控制

在触摸设备上始终显示视觉触摸指示器 — 永远不要依赖不可见的点击区域。使用 **能力检测**（而不是基于 OS 的检测）来确定触摸支持：

```js
// 好 — 检测触摸笔记本电脑、平板电脑、2-in-1s
const hasTouch = ('ontouchstart' in window) || (navigator.maxTouchPoints > 0);

// 坏 — 错过触摸屏笔记本电脑、iPadOS（报告为桌面）
const isMobile = device.os.android || device.os.iOS;
```

在屏幕底部渲染半透明的箭头按钮（或方向指示器）。使用 Constants.js 中的 `TOUCH` 常量进行尺寸（画布宽度的 12%）、透明度（空闲 0.35 / 激活 0.6）和边距。在 `update()` 循环中根据输入状态更新透明度以提供视觉反馈。

在 **所有** 设备上启用指针输入（pointerdown、pointermove、pointerup）— 指针事件适用于鼠标和触摸。这消除了对移动/桌面输入代码路径的单独需求。

### 移动端最小实体尺寸

收集品、危险和交互物品必须在至少 **7–8% 的 `GAME.WIDTH`** 以在手机屏幕上可识别。较小的实体在移动端会变成无法区分的模糊块。

```js
// 好 — 在移动端可识别
ATTACK_WIDTH: _canvasW * 0.09,
POWERUP_WIDTH: _canvasW * 0.072,

// 坏 — 手机屏幕太小
ATTACK_WIDTH: _canvasW * 0.04,
POWERUP_WIDTH: _canvasW * 0.035,
```

对于主要玩家角色，使用 12–15% 的 `GAME.WIDTH`（见上文实体尺寸）。

### 按钮模式（容器 + 图形 + 文本）

参见 [game-objects.md](game-objects.md) 获取完整的按钮实现模式（容器 + 图形 + 文本，带悬停/按下状态）和应避免的破例模式列表。

## 反模式（避免这些）

- **臃肿的 `update()` 方法** — 不要在一个巨大的 update 中放入所有游戏逻辑，并使用嵌套条件。委托给对象和系统。
- **覆盖场景注入映射属性** — 不要将你的属性命名为 `world`、`input`、`cameras`、`add`、`make`、`scene`、`sys`、`game`、`cache`、`registry`、`sound`、`textures`、`events`、`physics`、`matter`、`time`、`tweens`、`lights`、`data`、`load`、`anims`、`renderer` 或 `plugins`。这些是 Phaser 保留的。
- **在 `update()` 中无池创建对象** — 这会导致 GC 峰值。始终池化频繁创建/销毁的对象。避免昂贵的每帧分配 — 重用对象、数组和临时变量。
- **加载单个精灵而不是图集** — 每个单独的纹理都是一个绘制调用。将它们打包。
- **场景紧密耦合** — 不要在场景之间存储直接引用。使用 EventBus。
- **忽略 `delta` 在更新中** — 始终使用 `delta` 进行基于时间的移动，而不是基于帧。
- **深层容器嵌套** — 容器禁用子项的渲染批处理。保持层次结构扁平。
- **不清理** — 在 `shutdown()` 中移除事件监听器和计时器，以防止内存泄漏。这对于重启安全性至关重要 — 陈旧的监听器会导致重启后的双发射和幽灵行为。
- **硬编码值** — 每个数字都属于 `Constants.ts`。游戏逻辑中没有魔法数字。
- **未连接的物理碰撞器** — 使用 `physics.add.existing(obj, true)` 创建静态体本身什么也不做。你必须调用 `physics.add.collider(bodyA, bodyB, callback)` 连接两个体。每个静态碰撞器（地面、墙壁、平台）都需要一个显式的碰撞器或重叠调用将其连接到应该与之交互的实体。
- **不可见或隐藏的按钮元素** — 永远不要将交互式游戏对象的 `setAlpha(0)` 设置为顶层，并在此之上层叠图形或其他显示对象。**对于按钮，始终使用容器 + 图形 + 文本模式**（见 [game-objects.md](game-objects.md)）。常见破例模式：(1) 在添加文本后绘制图形矩形，将标签隐藏在其后面。(2) 创建用于碰撞区域的 Zone，但用绘制的图形覆盖它，使 Zone 无法到达。(3) 使文本交互式，但随后绘制图形背景。修复始终是：容器首先，图形添加到容器，文本添加到容器（按此顺序），容器是交互式元素。
- **无静音切换** — 见 `mute-button` 规则。带音频的游戏必须有静音切换。

## 示例

- [简单游戏](examples/simple-game.md) — 最小完整 Phaser 游戏（收集游戏）
- [复杂游戏](examples/complex-game.md) — 多场景游戏，带状态机、池化、EventBus 和所有约定

## 上线前验证清单

在考虑游戏完成之前，验证：

- [ ] **核心循环工作** — 玩家可以开始、玩、输/赢，并看到结果
- [ ] **重启干净** — `GameState.reset()` 恢复干净的起点，无陈旧监听器或计时器
- [ ] **触摸 + 键盘输入** — 游戏在移动端（点击/滑动）和桌面端（键盘/鼠标）工作
- [ ] **响应式画布** — `Scale.FIT` + `CENTER_BOTH` + `zoom: 1/DPR`，带 DPR 放大的尺寸，在 Retina 上清晰
- [ ] **所有值在 Constants 中** — 游戏逻辑中没有硬编码的魔法数字
- [ ] **仅 EventBus** — 无直接跨场景/模块导入用于通信
- [ ] **场景清理** — 所有 EventBus 监听器在 `shutdown()` 中移除
- [ ] **物理连接** — 每个静态体都有一个显式的 `collider()` 或 `overlap()` 调用
- [ ] **对象池** — 频繁创建/销毁的对象使用带有 `maxSize` 的 Groups
- [ ] **基于 delta 的移动** — 所有运动使用 `delta`，而不是帧计数
- [ ] **静音切换** — 见 `mute-button` 规则
- [ ] **展示性钩子连接** — 每个玩家操作和游戏事件都发出一个 `SPECTACLE_*` 事件；入口序列在 `create()` 中触发
- [ ] **构建通过** — `npm run build` 成功，无错误
- [ ] **无控制台错误** — 游戏运行无未捕获异常或 WebGL 失败

## 参考文件

| 文件 | 主题 |
|------|-------|
| [conventions.md](conventions.md) | 强制性 game-creator 架构约定 |
| [project-setup.md](project-setup.md) | 框架、Vite、TypeScript 配置、响应式画布、实体尺寸、竖屏模式 |
| [scenes-and-lifecycle.md](scenes-and-lifecycle.md) | 场景系统深入探讨 |
| [game-objects.md](game-objects.md) | 自定义对象、组、容器、按钮模式 |
| [physics-and-movement.md](physics-and-movement.md) | 物理引擎、移动模式 |
| [assets-and-performance.md](assets-and-performance.md) | 资源、优化、移动端 |
| [patterns.md](patterns.md) | ECS、状态机、单例 |
| [no-asset-design.md](no-asset-design.md) | 程序化视觉效果：渐变、视差、粒子、动画 |
