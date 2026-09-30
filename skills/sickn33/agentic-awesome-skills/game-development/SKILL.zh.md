---
name: game-development
description: 游戏开发协调器。根据平台、维度和引擎适配（Web 2D/3D、混合 DOM+canvas、叙事工具）。在启动或构建游戏项目、选择框架，或从 Phaser、PixiJS、Kaplay、Canvas/WebGL、Three.js、Babylon.js、Godot、Unity、Ink/Twine 中选择时使用。
---

# 游戏开发

> **协调器技能** — 原则加上路由到专门的子技能。

---

## 何时使用此技能

你正在参与一个游戏开发项目。此技能教你**原则**，并根据上下文将你引导到正确的子技能。

---

## 子技能路由

### 平台选择

| 如果游戏目标是... | 使用子技能 |
|------------------------|---------------|
| 网页浏览器 (HTML5, WebGL, WebGPU) | `game-development/web-games` |
| 移动设备 (iOS, Android) | `game-development/mobile-games` |
| PC (Steam, 桌面) | `game-development/pc-games` |
| VR/AR 头显 | `game-development/vr-ar` |

### 维度选择

| 如果游戏是... | 使用子技能 |
|-------------------|---------------|
| 2D (精灵, 图块地图) | `game-development/2d-games` |
| 3D (网格, 着色器) | `game-development/3d-games` |

### 架构 / 工具

| 如果你需要... | 使用子技能 |
|----------------|---------------|
| 引擎 / 框架选择, 宿主 vs 客户端, 适配度 | `game-development/engine-selection` |
| 游戏设计文档, 平衡性, 玩家心理 | `game-development/game-design` |
| 多人游戏, 网络连接 | `game-development/multiplayer` |
| 视觉风格, 资源流水线, 动画 | `game-development/game-art` |
| 音频设计, 音乐, 自适应音频 | `game-development/game-audio` |

---

## 核心原则 (所有平台)

### 1. 游戏循环

```
INPUT  → 读取玩家操作
UPDATE → 处理游戏逻辑 (固定步长)
RENDER → 绘制帧 (插值)
```

**固定步长规则:**
- 物理逻辑: 固定速率 (例如, 50Hz)
- 渲染: 尽可能快
- 在状态之间插值以实现平滑视觉效果

**混合 / UI密集型游戏:** 外部应用可能是DOM事件驱动; 仅在canvas/WebGL视口 (或任何模拟计时处) 使用经典游戏循环。

### 2. 模式选择矩阵

| 模式 | 使用场景 | 示例 |
|---------|----------|---------|
| **状态机** | 3-5个离散状态 | 玩家: 空闲→行走→跳跃 |
| **对象池** | 频繁生成/销毁 | 子弹, 粒子 |
| **观察者/事件** | 跨系统通信 | 生命值→UI更新 |
| **ECS** | 数千个相似实体 | RTS单位, 粒子 |
| **命令** | 撤销, 回放, 网络连接 | 输入录制 |
| **行为树** | 复杂AI决策 | 敌人AI |
| **内容即数据** | 设计师无需代码即可发送关卡/事件 | JSON/YAML包 |

**决策规则:** 从状态机开始。仅在性能要求时才添加ECS。

### 3. 输入抽象

将输入抽象为**动作**，而不是原始按键:

```
"跳跃"  → 空格键, 控制器A键, 触摸点击
"移动"  → WASD, 左摇杆, 虚拟摇杆
```

### 4. 性能预算 (60 FPS = 16.67ms)

| 系统 | 预算 |
|--------|--------|
| 输入 | 1ms |
| 物理逻辑 | 3ms |
| AI | 2ms |
| 游戏逻辑 | 4ms |
| 渲染 | 5ms |
| 缓冲区 | 1.67ms |

**优化优先级:** 算法 → 批处理 → 池化 → LOD → 排除。

### 5. 根据复杂度选择AI

| AI类型 | 复杂度 | 使用场景 |
|---------|------------|----------|
| **FSM** | 简单 | 3-5个状态, 可预测行为 |
| **行为树** | 中等 | 模块化, 设计师友好 |
| **GOAP** | 高 | 自发式, 基于规划 |
| **效用AI** | 高 | 基于评分的决策 |

### 6. 碰撞策略

| 类型 | 最适合 |
|------|----------|
| **AABB** | 矩形, 快速检查 |
| **圆形** | 圆形物体, 便宜 |
| **空间哈希** | 许多相似大小的物体 |
| **四叉树** | 大型世界, 不同大小 |

---

## 反模式 (通用)

| 不要 | 要 |
|-------|-----|
| 每帧更新所有内容 | 使用事件, 污染标记 |
| 在热点循环中创建对象 | 对象池 |
| 什么也不缓存 | 缓存引用 |
| 未分析就优化 | 先分析 |
| 将输入与逻辑混合 | 抽象输入层 |
| 根据热度选择引擎 | 根据类型+团队+交付目标匹配引擎 |

---

## 路由示例

### “浏览器2D平台游戏”
→ `game-development/engine-selection` → `game-development/web-games` → `game-development/2d-games` → `game-development/game-design`

### “UI密集型网页游戏带小型街机挑战”
→ `game-development/engine-selection` (宿主vs客户端) → `game-development/web-games` → 仅对客户端使用`game-development/2d-games`

### “移动解谜游戏”
→ `game-development/mobile-games` → `game-development/game-design`

### “多人VR射击游戏”
→ `game-development/vr-ar` → `game-development/3d-games` → `game-development/multiplayer`

### “分支叙事带轻量级统计”
→ `game-development/engine-selection` (Ink/Twine) → 选择你喜欢的宿主UI

---

> **记住:** 伟大的游戏来自迭代，而非完美。快速原型，然后打磨。

## 限制

- 仅在任务明确匹配上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家评审的替代品。
- 如果缺少所需输入、权限、安全边界或成功标准，请停止并请求澄清。
