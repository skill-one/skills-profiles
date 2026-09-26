# MinecraftConsoles (旧版主机版) 技能

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能合集。

## 项目简介

MinecraftConsoles 是一个 C++ 重写/续作的 **Minecraft 旧版主机版 v1.6.0560.0 (TU19)**，目标为现代 Windows（以及通过 Wine 的非官方 macOS/Linux）。目标包括：

- 多平台基础，用于模组、向后移植和 LCE 开发
- 高质量桌面体验，支持键盘/鼠标和控制器
- 局域网多人游戏和专用服务器软件
- 分屏多人游戏支持

**仓库：** `smartcmd/MinecraftConsoles`  
**主要语言：** C++  
**构建系统：** Visual Studio 2022 解决方案 (`.sln`) + CMake 支持  

---

## 快速入门

### 前置条件

- **Windows**（主要支持平台）
- [Visual Studio 2022](https://aka.ms/vs/17/release/vs_community.exe) 需要安装 C++ 桌面工作负载
- Git

### 克隆

```bash
git clone https://github.com/smartcmd/MinecraftConsoles.git
cd MinecraftConsoles
```

### 使用 Visual Studio 构建

1. 在 Visual Studio 2022 中打开 `MinecraftConsoles.sln`
2. 将 **启动项目** 设置为 `Minecraft.Client`
3. 将配置设置为 **Debug**（或 Release），平台设置为 **Windows64**
4. 按 **F5** 或 **Ctrl+F5** 构建并运行

### 使用 CMake 构建（Windows x64）

```powershell
# 配置
cmake -S . -B build -G "Visual Studio 17 2022" -A x64

# 构建客户端
cmake --build build --config Debug --target MinecraftClient

# 构建专用服务器
cmake --build build --config Debug --target MinecraftServer
```

在仓库中的 `COMPILE.md` 文件中查看针对特定平台的额外说明。

---

## 运行客户端

### 夜间构建（无需编译）

从 [夜间发布](https://github.com/smartcmd/MinecraftConsoles/releases/tag/nightly) 下载 `.zip` 文件，解压并运行 `Minecraft.Client.exe`。

### 设置用户名

在同一目录下创建 `username.txt`：

```
Steve
```

或者使用启动参数：

```powershell
Minecraft.Client.exe -name Steve
Minecraft.Client.exe -name Steve -fullscreen
```

### 客户端启动参数

| 参数 | 描述 |
|---|---|
| `-name <username>` | 覆盖游戏内用户名 |
| `-fullscreen` | 全屏启动 |

---

## 键盘和鼠标控制

| 操作 | 键/按钮 |
|---|---|
| 移动 | `W` `A` `S` `D` |
| 跳跃 / 上升飞行 | `Space` |
| 潜行 / 下降飞行 | `Shift`（按住） |
| 跑步 | `Ctrl`（按住）或双击 `W` |
| 物品栏 | `E` |
| 聊天 | `T` |
| 丢弃物品 | `Q` |
| 合成 | `C`（选项卡：`Q` / `E`） |
| 攻击 / 破坏 | 左键点击 |
| 使用 / 放置 | 右键点击 |
| 选择物品栏槽位 | `1`–`9` 或鼠标滚轮 |
| 暂停 | `Esc` |
| 全屏 | `F11` |
| 切换 HUD | `F1` |
| 切换调试信息 | `F3` |
| 调试覆盖层 | `F4` |
| 切换调试控制台 | `F6` |
| 切换 FPS/TPS 显示 | `F5` |
| 玩家列表 / 主机选项 | `Tab` |
| 接受教程提示 | `Enter` |
| 拒绝教程提示 | `B` |

---

## 局域网多人游戏

Windows 构建会自动支持局域网多人游戏：

- 主机世界会自动在本地网络进行广播
- 其他玩家通过 **游戏菜单** 发现会话
- TCP 端口：**25565**（游戏连接）
- UDP 端口：**25566**（局域网发现）
- 使用 **添加服务器** 按钮连接到已知 IP
- 用户名更改是安全的 — 保留 `uid.dat` 以跨重命名保留数据
- 分屏玩家可以加入局域网/多人游戏会话

---

## 专用服务器

### 下载夜间服务器构建

[Nightly 专用服务器](https://github.com/smartcmd/MinecraftConsoles/releases/tag/nightly-dedicated-server)

### 直接运行（Windows）

```powershell
Minecraft.Server.exe -name MyServer -port 25565 -ip 0.0.0.0 -maxplayers 8 -loglevel info
Minecraft.Server.exe -seed 123456789
```

### 服务器 CLI 参数

| 参数 | 描述 |
|---|---|
| `-port <1-65535>` | 覆盖 `server-port` |
| `-ip <addr>` | 覆盖 `server-ip`（绑定地址） |
| `-bind <addr>` | `-ip` 的别名 |
| `-name <name>` | 覆盖 `server-name`（最多16个字符） |
| `-maxplayers <1-8>` | 覆盖 `max-players` |
| `-seed <int64>` | 覆盖 `level-seed` |
| `-loglevel <level>` | `debug`, `info`, `warn`, `error` |
| `-help` / `--help` / `-h` | 打印使用说明并退出 |

### `server.properties` 配置

位于与 `Minecraft.Server.exe` 相同的目录中。如果缺失，会自动生成默认值。

```properties
server-name=DedicatedServer
server-port=25565
server-ip=0.0.0.0
max-players=8
level-name=world
level-id=world
level-seed=
world-size=classic
log-level=info
white-list=false
lan-advertise=false
autosave-interval=60
```

**关键属性说明：**

| 键 | 值 | 默认值 | 说明 |
|---|---|---|---|
| `server-port` | `1–65535` | `25565` | TCP 监听端口 |
| `server-ip` | 字符串 | `0.0.0.0` | 绑定地址 |
| `server-name` | 字符串 | `DedicatedServer` | 最多16个字符 |
| `max-players` | `1–8` | `8` | 玩家槽数量 |
| `level-seed` | int64 或空 | 空 | 空则随机 |
| `world-size` | `classic\|small\|medium\|large` | `classic` | 新世界大小 |
| `log-level` | `debug\|info\|warn\|error` | `info` | 详略程度 |
| `autosave-interval` | `5–3600` | `60` | 自动保存间隔（秒） |
| `white-list` | `true/false` | `false` | 启用白名单 |
| `lan-advertise` | `true/false` | `false` | LAN 广播（客户端通过游戏菜单发现） |

---

## Docker 中的专用服务器（Linux/Wine）

### 推荐：从 GHCR 拉取（无需本地构建）

```bash
# 启动（自动拉取最新镜像）
./start-dedicated-server.sh

# 启动但不拉取
./start-dedicated-server.sh --no-pull

# 等价手动命令
docker compose -f docker-compose.dedicated-server.ghcr.yml up -d
```

### 本地构建模式（可选）

需要本地编译的 `Minecraft.Server.exe`：

```bash
docker compose -f docker-compose.dedicated-server.yml up -d --build
```

### Docker 持久化卷

| 主机路径 | 容器路径 | 目的 |
|---|---|---|
| `./server-data/server.properties` | `/srv/mc/server.properties` | 服务器配置 |
| `./server-data/GameHDD` | `/srv/mc/Windows64/GameHDD` | 世界存档数据 |

### Docker 环境变量

| 变量 | 默认值 | 描述 |
|---|---|---|
| `XVFB_DISPLAY` | `:99` | 虚拟显示器编号 |
| `XVFB_SCREEN` | `64x64x16` | 虚拟屏幕大小（极小，Wine 需要） |

---

## 项目结构（关键区域）

```
MinecraftConsoles/
├── MinecraftConsoles.sln       # Visual Studio 解决方案
├── CMakeLists.txt              # CMake 构建定义
├── COMPILE.md                  # 详细编译说明
├── CONTRIBUTING.md             # 贡献者指南和项目目标
├── docker-compose.dedicated-server.ghcr.yml  # Docker (GHCR 镜像)
├── docker-compose.dedicated-server.yml       # Docker (本地构建)
├── start-dedicated-server.sh   # 快速启动脚本
├── server-data/
│   ├── server.properties       # 服务器配置（自动生成）
│   └── GameHDD/                # 世界存档数据
└── .github/
    └── banner.png
```

---

## 此代码库中的常见 C++ 模式

### 添加新的按键绑定（键盘输入）

项目在原始仅支持控制器的代码基础上添加了键盘/鼠标支持。扩展输入时：

```cpp
// 检查按键状态的典型模式
// 在输入处理文件中添加你的按键检查：

bool isKeyPressed(int virtualKey) {
    return (GetAsyncKeyState(virtualKey) & 0x8000) != 0;
}

// 示例：添加新的切换键
if (isKeyPressed(VK_F7)) {
    // 切换你的功能
    myFeatureEnabled = !myFeatureEnabled;
}
```

### 注册启动参数

遵循现有的 `-name` / `-fullscreen` 模式：

```cpp
// 在参数解析部分（通常在 main 或 init 中）：
for (int i = 1; i < argc; i++) {
    std::string arg = argv[i];

    if (arg == "-name" && i + 1 < argc) {
        username = argv[++i];
    }
    else if (arg == "-fullscreen") {
        launchFullscreen = true;
    }
    // 添加你的参数：
    else if (arg == "-myoption" && i + 1 < argc) {
        myOption = argv[++i];
    }
}
```

### 读取 `server.properties`

```cpp
#include <fstream>
#include <sstream>
#include <map>
#include <string>

std::map<std::string, std::string> loadServerProperties(const std::string& path) {
    std::map<std::string, std::string> props;
    std::ifstream file(path);
    std::string line;

    while (std::getline(file, line)) {
        if (line.empty() || line[0] == '#') continue;
        auto eq = line.find('=');
        if (eq == std::string::npos) continue;
        std::string key = line.substr(0, eq);
        std::string val = line.substr(eq + 1);
        props[key] = val;
    }
    return props;
}

// 使用：
auto props = loadServerProperties("server.properties");
int port = std::stoi(props.count("server-port") ? props["server-port"] : "25565");
std::string serverName = props.count("server-name") ? props["server-name"] : "DedicatedServer";
```

### 写入 `server.properties`（规范化 / 自动生成）

```cpp
void writeServerProperties(const std::string& path,
                            const std::map<std::string, std::string>& props) {
    std::ofstream file(path);
    for (auto& [key, val] : props) {
        file << key << "=" << val << "\n";
    }
}

// 从 level-name 规范化 level-id
std::string normalizeLevelId(const std::string& levelName) {
    std::string id = levelName;
    // 移除不安全字符，小写，空格替换为下划线
    for (char& c : id) {
        if (!std::isalnum(c) && c != '_' && c != '-') c = '_';
    }
    return id;
}
```

---

## 故障排除

### 构建失败：缺少 Windows SDK

- 打开 **Visual Studio 安装程序** → 修改 → 添加 **Windows 10/11 SDK**
- 确保平台设置为 **Windows64**（不是 x86）

### CMake 找不到 Visual Studio 生成器

```powershell
# 确认已安装 VS 2022，然后：
cmake -S . -B build -G "Visual Studio 17 2022" -A x64
# "17 2022" 是 VS 2022 的生成器名称
```

### 游戏启动但无显示 / 立即崩溃

- 确保从包含所有游戏资源的目录运行
- 检查你的 GPU 驱动程序支持所需的 DirectX 版本
- 尝试 **Debug** 构建以获取更详细的错误输出

### 服务器在局域网中不可见

- 检查防火墙规则允许 **TCP 25565** 和 **UDP 25566**
- 验证 `lan-advertise=true` 对专用服务器不是必需的（它是用于局域网广播；客户端通过游戏菜单发现）
- 确保客户端和服务器在同一子网

### Docker 服务器：Wine 无法显示

- `XVFB_DISPLAY` 环境变量必须与 Wine 使用的一致
- 容器使用极小的 `64x64x16` 虚拟帧缓冲区 — 除非有理由，否则不要更改

### 用户名重置 / UID 问题

- **不要删除 `uid.dat`** — 它存储你的唯一玩家 ID
- 如果你通过 `-name` 或 `username.txt` 重命名自己，你的现有 `uid.dat` 会保留与你的账户关联的世界数据

### macOS / Linux (Wine)

- 下载 Windows 夜间 `.zip` 文件
- 通过 `wine Minecraft.Client.exe` 或 CrossOver 运行
- 已知稳定性问题（帧时间间隔）并社区报告；不官方支持

---

## 贡献

提交 PR 前请阅读 [`CONTRIBUTING.md`](https://github.com/smartcmd/MinecraftConsoles/blob/main/CONTRIBUTING.md)。关键点：

- 遵循现有的代码风格和命名规范
- 除非讨论，否则不应破坏控制台构建兼容性
- 欢迎安全修复
- 检查开放问题（535+）以获取良好首次任务
- 加入 [Discord](https://discord.gg/jrum7HhegA) 进行贡献者讨论

---

## 平台支持总结

| 平台 | 状态 |
|---|---|
| Windows (VS 2022) | ✅ 完全支持 |
| macOS / Linux (Wine) | ⚠️ 社区报告运行正常，非官方 |
| Android (Wine) | ⚠️ 运行有帧时间问题 |
| iOS | ❌ 无支持 |
| 控制器 | ⚠️ 代码存在，未积极维护 |
