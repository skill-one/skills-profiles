# pygame 核心基础

使用 Python 构建 pygame 游戏的基础：主循环、基于时间差（delta-time）的移动、使用 `Surface`/`Rect` 绘图、输入处理以及 `Sprite`/`Group` 的管理。目标版本为 **pygame-ce 2.5.7**（活跃维护的社区分支；与 `import pygame` 兼容）。

## 使用场景

- 在开始 pygame 游戏时、修复循环、帧率依赖的速度、输入处理、光栅操作（blitting）或精灵/组碰撞时使用。
- 当代码执行 `import pygame` 且项目依赖于 `pygame-ce`（或 `pygame`）时使用。

**不适用场景：** 与 pygame 无关的 Python 语言问题。3D 渲染（pygame 为 2D）。跨引擎保存/加载请使用 `save-systems`；可重新绑定输入架构请参考 `input-systems`。

## 核心工作流程

1. **安装 pygame-ce，而非旧版 pygame。** `pip install pygame-ce` — 它是维护分支且导入时作为 `pygame`。不要在一个环境中安装两者。
2. **初始化并打开窗口。** `pygame.init()`，`screen = pygame.display.set_mode((w, h))`，`clock = pygame.time.Clock()`。
3. **运行一个主循环：事件 → 更新 → 绘制 → 刷新。** 每帧处理事件队列（`for event in pygame.event.get()`），更新状态，重绘，然后 `pygame.display.flip()`。
4. **实现帧率无关性。** 获取 `dt = clock.tick(60) / 1000`（秒）并按 `dt` 缩放所有运动。将位置保持为浮点数；在整数矩形处光栅操作。
5. **两种方式处理输入：** 基于事件（`KEYDOWN`/`MOUSEBUTTONDOWN`，用于离散动作）和轮询（`pygame.key.get_pressed()`，用于持续移动）。
6. **使用 `Sprite` + `Group` 组织对象。** 继承 `pygame.sprite.Sprite` 并设置 `image`/`rect`；`group.update(dt)` 和 `group.draw(screen)` 处理批量操作。运行它并在假设其工作前观察窗口。

## 模式

### 1. 最小游戏循环（骨架）

```python
import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("我的游戏")
clock = pygame.time.Clock()

running = True
while running:
    dt = clock.tick(60) / 1000          # 限制在 60 FPS；dt = 帧之间的秒数
    for event in pygame.event.get():    # 必须清空队列，否则操作系统认为卡死
        if event.type == pygame.QUIT:
            running = False

    # 在此处更新游戏状态，按 dt 缩放 ...

    screen.fill((18, 18, 28))           # 每帧清除
    # 在此处绘制所有内容 ...
    pygame.display.flip()               # 呈现帧

pygame.quit()
```

### 2. 基于时间差（delta-time）的移动（帧率无关）

```python
from pygame.math import Vector2

pos = Vector2(100, 100)        # 将位置保持为浮点数
speed = 220                    # 每秒像素数，非每帧

# 在循环内，计算 dt 后：
keys = pygame.key.get_pressed()
direction = Vector2(
    keys[pygame.K_RIGHT] - keys[pygame.K_LEFT],
    keys[pygame.K_DOWN]  - keys[pygame.K_UP],
)
if direction.length_squared() > 0:
    direction = direction.normalize()      # 对角线速度相同
pos += direction * speed * dt              # 右移：按 dt 缩放
screen.blit(player_img, (round(pos.x), round(pos.y)))  # 在整数像素处光栅操作
```

### 3. 输入：事件 vs 轮询

```python
for event in pygame.event.get():
    if event.type == pygame.QUIT:
        running = False
    elif event.type == pygame.KEYDOWN:        # 离散按键：跳跃、菜单、暂停
        if event.key == pygame.K_SPACE:
            jump()
        elif event.key == pygame.K_ESCAPE:
            running = False
    elif event.type == pygame.MOUSEBUTTONDOWN:
        shoot_at(event.pos)                   # event.pos = (x, y)

# 轮询状态（每帧读取一次）用于持续/按住输入：
keys = pygame.key.get_pressed()
if keys[pygame.K_a]:
    move_left(dt)
```

### 4. 一个 Sprite 子类 + 一个 Group

```python
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # 加载时一次性调用 convert() 可大幅提升光栅操作速度；_alpha 保持透明度。
        self.image = pygame.image.load("player.png").convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 240

    def update(self, dt):                      # Group.update(dt) 对每个精灵调用此方法
        keys = pygame.key.get_pressed()
        self.pos.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

all_sprites = pygame.sprite.Group()
all_sprites.add(Player(400, 300))

# 在循环内：
all_sprites.update(dt)        # 调用每个精灵的 update(dt)
all_sprites.draw(screen)      # 在每个精灵的矩形处光栅操作
```

### 5. 碰撞检测

```python
# Sprite vs group: 例如玩家拾取金币（True = 移除碰撞的金币）。
collected = pygame.sprite.spritecollide(player, coins, dokill=True)
score += len(collected)

# Group vs group: 子弹 vs 敌人（命中时双方都消失）。
hits = pygame.sprite.groupcollide(bullets, enemies, True, True)

# 普通矩形重叠（无需精灵）：
if player.rect.colliderect(door_rect):
    open_door()
```

## 常见问题

- **窗口冻结/无响应** → 你没有处理事件队列。每帧调用 `pygame.event.get()`（或 `pygame.event.pump()`）。
- **速度在不同机器上差异** → 你每帧移动固定量。按 `dt = clock.tick(fps) / 1000` 缩放，并使用每秒像素值。
- **亚像素移动出现抖动/跳跃** → `rect` 坐标为整数；将真实位置存储为浮点数的 `Vector2`，每帧赋值 `rect.center = round(...)`。
- **光栅操作慢/帧率下降** → 对加载的图像一次性调用 `.convert()`（不透明）或 `.convert_alpha()`（透明）；未转换的表面光栅操作速度远慢。
- **画面无显示** → 忘记 `pygame.display.flip()`（或 `update()`），或你在 `screen.fill(...)` 之前绘制导致被清除。
- **绘制顺序错误** → pygame 使用画家模型；后绘制的覆盖先绘制的。先绘制背景，后绘制精灵。
- **`pip install pygame` 安装了旧版** → 使用维护分支 `pip install pygame-ce`；安装两者会导致导入冲突。
- **对角线移动更快** → 在缩放速度前归一化方向向量。

## 参考

- 关于 `Group` 变体（`GroupSingle`，`LayeredUpdates` 用于 z-order）、像素级碰撞（`mask`）、精灵表切片、简单动画、音效/音乐以及文本渲染，请阅读 `references/sprites-and-collision.md`。

## 相关技能

- `love2d-core` — 在 LÖVE/Lua 中相同的主循环概念。
- `bevy-ecs` — 当项目规模超出 pygame 时使用的更重量的 ECS 引擎。
- `input-systems` / `save-systems` — 引擎无关的输入和持久化。
- `platformer` / `roguelike` — 与 pygame 配合的游戏类型模板。
