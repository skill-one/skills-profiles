# 主路由器——游戏开发技能调度器

游戏开发工作的入口点。它通过项目特征来选择**一个**引擎，从请求中分类任务，命名**最小**的专业技能集，并指导你在行动前阅读它们。它**调度和组合**——它不会重新教授引擎API。

## 何时使用

- 在任何游戏开发请求**开始时**使用——无论是构建还是调试游戏、关卡、玩家、敌人、着色器、UI、存档系统、多人游戏、输入、音频、AI、对话、程序化内容还是视觉资源集——以决定要加载哪些技能。
- 当用户命名引擎或类型，说“制作一个游戏”，或问“我应该使用哪个技能？”时使用。

**不使用**的情况：一旦加载了正确的技能并且任务完全在其内部，就从该技能开始工作——不要每次都重新运行路由器。只有在任务**转向**新的引擎或关注点时才重新路由（路由步骤6）。

## 路由算法

1. **检测引擎和版本**——项目特征 → 至多一个引擎技能集（或“未知”），然后读取项目的版本源。§1。
2. **分类任务**——措辞 → 学科（s）+ 至多一个类型 + 工作流（s）。§2。
3. **解析**——最小集：引擎技能（s）+ 学科（s）+ 类型 + 工作流（s）。§3。
4. **阅读（披露）**——仅打开选择的 `SKILL.md` 正文；`references/` 仅按需读取。§4。
5. **组合**——顺序：引擎基础 → 学科概念 → 类型粘合 → 工作流。§5。
6. **回退**——引擎未知或没有技能匹配 → 询问或默认为 Godot；声明任何差距。§6。

---

## 1. 引擎检测（项目特征）

扫描最高置信度的信号；**选择恰好一个**引擎。在第一个匹配处停止。

| # | 引擎 | 主要信号 | 技能集根目录 |
|:-:|--------|----------------|----------------|
| 1 | Godot | `project.godot` | `skills/godot/` |
| 2 | Unreal | `*.uproject` | `skills/unreal/` |
| 3 | Unity | `Assets/` **和** `ProjectSettings/ProjectVersion.txt` | `skills/unity/` |
| 4 | Bevy | `Cargo.toml` 带有 `bevy` 依赖 | `skills/other-engines/bevy-ecs/` |
| 5 | Phaser | `package.json` 依赖 `phaser` | `skills/web-engines/phaser-*` |
| 6 | PixiJS | `package.json` 依赖 `pixi.js` | `skills/web-engines/pixijs-rendering/` |
| 7 | three.js | `package.json` 依赖 `three` | `skills/web-engines/threejs-*` |
| 8 | LÖVE | `conf.lua` / `main.lua` 调用 `love.*` | `skills/other-engines/love2d-core/` |
| 9 | pygame | `*.py` 带有 `import pygame` | `skills/other-engines/pygame-core/` |
| 10 | Roblox | `*.rbxl(x)` / `*.project.json` (Rojo) | `skills/other-engines/roblox-*` |

对于次要信号，Godot-C#/Unity/Bevy 和多网页歧义规则、单仓库和纯文本引擎提及，请阅读 `references/engine-detection.md`。

识别引擎后，从项目元数据或依赖锁定中读取其版本，然后选择API。现有项目保持其固定版本，除非请求迁移；目录基线仅适用于新项目。确切的版本来源在检测参考和 `../docs/VERSION-SUPPORT.md` 中。

## 2. 任务分类（措辞 → 类别）

在引擎之后，读取任务信号请求（三个**加性**类别）：

- **学科**（跨引擎概念）：`create-game-assets`、`game-ai`、`ai-behavior-trees-utility-ai`、`procedural-gen`、`dialogue-systems`、`save-systems`、`audio-design`、`shader-programming`、`physics-tuning`、`level-design`、`input-systems`、`game-feel`、`camera-systems`、`game-ui-ux`、`performance-optimization`。由概念词触发（“精灵表”、“艺术方向”、“纹理”、“路径规划”、“存档槽”、“片段着色器”、“屏幕抖动”、“相机跟随”、“HUD/菜单”、“优化/低FPS”）。
- **类型**（整个游戏模板）：`platformer`、`roguelike`、`rpg`、`fps-shooter`、`tower-defense`、`card-game`、`visual-novel`、`survival-crafting`、`puzzle`。由类型词触发（“制作一个roguelike”、“deckbuilder”）。
- **工作流**（过程/发布）：`game-jam`、`prototype-fast`、`steam-publish`、`itch-publish`。由过程词触发（“在 Steam 上发布”、“垂直切片”）。

文件信号可以锐化这些：`*.yarn`/`*.ink` → `dialogue-systems`/`visual-novel`；`steam_appid.txt` → `steam-publish`；`*.inputactions` → `unity-input-system`。

## 3. 路由表（任务 → 类别 → 技能）

### 3a. 引擎技能——读取与检测到的引擎+子任务匹配的技能

- **Godot** (`skills/godot/`)：语言 `godot-gdscript` / `godot-csharp`；结构 `godot-nodes-scenes`、`godot-signals-groups`；2D `godot-2d-movement`、`godot-tilemap`；3D `godot-3d-essentials`；物理 `godot-physics`；UI `godot-ui-control`；动画 `godot-animation`；着色器 `godot-shaders`；数据 `godot-resources`；音频 `godot-audio`；网络代码 `godot-multiplayer`；发布 `godot-export`。
- **Unity** (`skills/unity/`)：脚本 `unity-csharp-scripting`；输入 `unity-input-system`；物理 `unity-physics`；动画 `unity-animation`；数据 `unity-scriptableobjects`；2D `unity-tilemap-2d`；AI 导航 `unity-navmesh`；发布 `unity-build-pipeline`。
- **Unreal** (`skills/unreal/`)：可视化脚本 `unreal-blueprints`；C++ 游戏逻辑 `unreal-cpp-gameplay`；输入 `unreal-enhanced-input`；AI `unreal-behavior-trees`；VFX `unreal-niagara`；发布 `unreal-packaging`。
- **Web** (`skills/web-engines/`)：`phaser-core`、`phaser-arcade-physics`；`pixijs-rendering`；`threejs-scene-setup`、`threejs-gltf-loading`、`threejs-materials-lighting`。
- **其他** (`skills/other-engines/`)：`bevy-ecs`、`pygame-core`、`love2d-core`；Roblox 基础 `roblox-luau`，持久化 `roblox-datastores`，UI `roblox-ui`，远程/安全 `roblox-networking`，角色生命周期 `roblox-characters`，模拟/查询 `roblox-physics`，以及在工作室的操作 `roblox-studio-workflow`。

### 3b. 学科——与引擎技能一起加载（概念 ↔ 引擎API）

| 概念 (`says:`) | 学科技能 | 与（引擎API）配对 |
|-------------------|------------------|-------------------------|
| 艺术方向、游戏资源、精灵、瓦片集、纹理、图标、3D道具 | `create-game-assets` | 引擎导入/渲染技能；`imagegen` 当可用时 |
| 敌人AI、行为树、路径规划、转向 | `game-ai` | `unity-navmesh` / `unreal-behavior-trees` / Godot 导航 |
| BT运行时、黑板、装饰器、选择器/序列、实用AI、响应曲线、考虑因素 | `ai-behavior-trees-utility-ai` | `game-ai`（模型选择） / `unreal-behavior-trees`（引擎资源） |
| 程序化、噪声、种子、地牢生成器 | `procedural-gen` | 引擎瓦片/网格技能 |
| 对话、Yarn、Ink、对话树 | `dialogue-systems` | 引擎UI技能 |
| 存档/加载、槽位、持久化 | `save-systems` | `roblox-datastores` / 引擎IO |
| 自适应音乐、混音器、静音、SFX | `audio-design` | `godot-audio` / Unity AudioMixer |
| 着色器、片段、溶解/轮廓 | `shader-programming` | `godot-shaders` / 引擎材质 |
| 抖动、隧道、固定时间步 | `physics-tuning` | `godot-physics` / `unity-physics` |
| 白盒、快速布局、瓦片布局、节奏 | `level-design` | `godot-tilemap` / `unity-tilemap-2d` |
| 重新绑定、游戏手柄、输入缓冲 | `input-systems` | `unity-input-system` / `unreal-enhanced-input` / Godot InputMap |
| 屏幕抖动、停止、效果、挤压和拉伸、“让它更有力” | `game-feel` | 引擎动画/tween + `camera-systems`（抖动） |
| 相机跟随、死区、预览、轨道、第一人称 | `camera-systems` | `godot-2d-movement` / `godot-3d-essentials` / Cinemachine |
| HUD、菜单、UI布局、缩放、安全区域、焦点导航 | `game-ui-ux` | `godot-ui-control` / Unity UI (UGUI/UI Toolkit) |
| 低FPS、优化、绘制调用、GC峰值、池化、分析器 | `performance-optimization` | 引擎分析器 + `physics-tuning` |

对于 Roblox，将跨引擎概念与焦点引擎技能组合：HUD/菜单请求使用 `roblox-ui` + `game-ui-ux`（+ `input-systems` 用于游戏绑定）；远程利用/复制请求使用 `roblox-networking` + `roblox-luau`；重生/骨骼请求使用 `roblox-characters`；物理模拟/查询请求使用 `roblox-physics`（+ `physics-tuning` 用于稳定性）；直接在工作室中编辑也使用 `roblox-studio-workflow`。

### 3c. 类型——**组合**引擎 + 学科（将 `*` 绑定到检测到的引擎）

| 类型 (`says:`) | 组合 |
|-----------------|----------|
| 平台跳跃、跳跃、双跳 | `godot-2d-movement`（或引擎物理）+ `godot-tilemap`/`unity-tilemap-2d` + `level-design` + `camera-systems` + `game-feel` |
| Roguelike、程序化地牢、永久死亡 | `procedural-gen` + `godot-tilemap`/`unity-tilemap-2d` + `game-ai` + `save-systems` + `game-feel` |
| RPG、属性、背包、任务 | `godot-resources`/`unity-scriptableobjects` + `dialogue-systems` + `save-systems` + `game-ui-ux` |
| FPS、第一人称、命中扫描 | `godot-3d-essentials`/`unreal-cpp-gameplay` + `input-systems` + `game-ai` + `camera-systems` + `game-feel` |
| 防御塔、波浪、路线 | `game-ai` + 引擎移动 + `level-design` + `game-ui-ux` |
| 卡牌游戏、卡牌构建器、TCG | `godot-resources`/`unity-scriptableobjects` + `game-ui-ux`（+ 引擎UI） |
| 视觉小说、分支故事 | `dialogue-systems` + `save-systems` + `game-ui-ux` |
| 生存、制作、收集 | `save-systems` + `godot-resources`/`unity-scriptableobjects` + `procedural-gen` + `game-ui-ux` |
| 拼图、匹配3、网格逻辑 | `godot-tilemap`/`unity-tilemap-2d` + `level-design` + `game-feel` |

### 3d. 工作流——与引擎无关的过程和发布

`game-jam`（Jam、48小时、Ludum Dare/GMTK）· `prototype-fast`（垂直切片、MVP、灰盒）· `steam-publish`（Steam、Steamworks、depot；`steam_appid.txt`）· `itch-publish`（itch.io、butler；`.itch.toml`）。

对于每个技能的触发词列表和每个引擎绑定，请阅读 `references/routing-table.md`。

## 4. 阅读协议（渐进式披露）

1. **预加载**：仅每个技能的 `name` + `description` 在上下文中。根据这些加上特征来决定——**不要**预读正文。
2. **选择时**：读取每个选择的 `skills/<category>/<name>/SKILL.md` 正文——仅那些。永远不要批量加载整个类别。
3. **按需**：仅在子任务需要该深度时读取技能的捆绑 `references/` 文件（技能正文说明何时）。
