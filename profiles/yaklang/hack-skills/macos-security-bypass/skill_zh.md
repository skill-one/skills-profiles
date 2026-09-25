# 技能：macOS 安全绕过 — 专家攻击手册

> **AI 加载指令**：专家级 macOS 安全绕过技术。涵盖 TCC 绕过、Gatekeeper 逃逸、SIP 限制、沙盒逃逸和权限滥用。基础模型会遗漏特定版本的绕过细节和保护交互效果。

## 0. 相关路由

深入学习前，请考虑加载：

- 当您在初次获取访问权限后需要 dylib 注入、XPC 利用或 Electron 滥用时，请加载 `[macos-process-injection](../macos-process-injection/SKILL.md)`
- 当您需要适用于 macOS 的 Unix 层提权技术（SUID、cron、可写路径）时，请加载 `[linux-privilege-escalation](../linux-privilege-escalation/SKILL.md)`
- 当您需要共享 Unix 安全绕过概念时，请加载 `[linux-security-bypass](../linux-security-bypass/SKILL.md)`

### 高级参考

当您需要以下内容时，请加载 `[TCC_BYPASS_MATRIX.md](./TCC_BYPASS_MATRIX.md)`：

- 每个macOS版本的 TCC 绕过映射
- 特定保护类型的绕过技术（相机、麦克风、FDA、自动化）
- MDM/配置文件滥用模式

---

## 1. TCC（透明度、同意、控制）概述

TCC 是 macOS 的权限框架，用于控制对敏感资源（相机、麦克风、联系人、全盘访问等）的访问。

### 1.1 TCC 数据库位置

| 数据库 | 路径 | 控制 | 保护 |
|---|---|---|---|
| 用户级 | `~/Library/Application Support/com.apple.TCC/TCC.db` | 单用户同意决策 | 自 Catalina 起 SIP 保护 |
| 系统级 | `/Library/Application Support/com.apple.TCC/TCC.db` | 全局同意决策 | SIP 保护 |
| MDM 管理 | 通过配置文件 | 推送 PPPC（隐私偏好策略控制） | 设备管理 |

```sql
-- 查询 TCC 数据库（需要 FDA 或 SIP 关闭）
sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db \
  "SELECT service, client, allowed FROM access;"
```

### 1.2 TCC 绕过类别

| 类别 | 机制 | 典型前提条件 |
|---|---|---|
| FDA 应用利用 | 依附于已获全盘访问的应用 | 写入 FDA 应用的捆绑包或插件目录 |
| 直接数据库修改 | 编辑 TCC.db 授权同意 | SIP 禁用或 FDA |
| 继承权限 | 子进程继承父进程的 TCC 授权 | 在 FDA 授权应用上下文中执行代码 |
| 自动化滥用 | Apple Events / osascript 控制TCC授权应用 | 自动化权限（低于直接 TCC） |
| 挂载技巧 | 挂载包含修改 TCC.db 的定制磁盘映像 | 本地访问，Ventura 之前 |
| TCC 中的 SQL 注入 | 形成不正确的捆绑包 ID 触发 TCC 子系统的 SQL 注入 | CVE-2023-32364 及类似漏洞 |

### 1.3 已知的 TCC 绕过模式

**终端 / iTerm FDA 继承**：Terminal.app 获得FDA → 任何运行的命令继承 FDA → 读取任何文件。

```bash
# 如果终端有 FDA，这将直接读取受保护文件
cat ~/Library/Mail/V*/MailData/Envelope\ Index
cat ~/Library/Messages/chat.db
```

**Finder 自动化**：自动化 Finder（权限较低）访问受保护位置的文件。

```applescript
tell application "Finder"
  set f to POSIX file "/Users/target/Library/Mail/V9/MailData/Envelope Index"
  duplicate f to desktop
end tell
```

**系统偏好设置 / 系统设置注入**：向已获 TCC 权限的进程写入其应用程序脚本文件夹以注入。

**MDM 配置文件滥用**：PPPC 配置文件可以预先批准 TCC 权限。恶意 MDM 注册或受感染的 MDM 服务器 → 推送 PPPC 负载。

---

## 2. Gatekeeper 绕过

Gatekeeper 阻止未签名或未签名的应用程序执行。核心执行依赖于 `com.apple.quarantine` 扩展属性。

### 2.1 隔离属性移除

```bash
# 检查隔离属性
xattr -l /path/to/app
# 输出: com.apple.quarantine: 0083;...

# 移除隔离（需要写入权限）
xattr -d com.apple.quarantine /path/to/app
# 递归用于应用程序捆绑包
xattr -rd com.apple.quarantine /path/to/MyApp.app
```

### 2.2 绕过技巧

| 技巧 | 工作原理 | macOS 版本 |
|---|---|---|
| `xattr -d` 移除 | 执行前移除隔离 | 所有（需要本地访问） |
| 应用程序位置绕过 | 某些位置的应用程序跳过隔离 | 预 Catalina |
| 去除隔离的归档工具 | 某些解压缩应用程序不会传播隔离 | 因工具而异 |
| 签名捆绑包中的未签名代码 | 已签名的应用程序捆绑包中包含未签名的嵌套辅助程序 | 预 Ventura (CVE-2022-42821) |
| Safari 自动提取 + 打开 | 下载的 ZIP 文件自动解压，应用程序在隔离完全应用前打开 | Safari 特定，已修复 |
| ACL 滥用 | `com.apple.quarantine` 可被下载前设置的 ACL 阻止 | 需要预先定位 |
| 磁盘映像技巧 | 从网络共享挂载的 DMG 可能不携带隔离 | 网络共享上下文 |
| BOM（物料清单）绕过 | 定制的 BOM 在 pkg 中跳过提取文件的隔离 | CVE-2022-22616 |

### 2.3 Gatekeeper 检查流程

```
应用程序启动
│
├── 存在 `com.apple.quarantine` 属性？
│   ├── 否 → 执行（无 Gatekeeper 检查）
│   └── 是 ↓
│
├── 代码签名有效？
│   ├── 否 → 阻止
│   └── 是 ↓
│
├── 已签名（捆绑包票证或在线检查）？
│   ├── 否 → 阻止（Catalina+）
│   └── 是 → 执行
│
└── 用户覆盖？（右键点击 → 打开 → 确认）
    └── 一次性绕过该应用程序的 Gatekeeper
```

---

## 3. SIP（系统完整性保护）

SIP 限制 root 修改受保护的系统位置、加载未签名的内核扩展和调试系统进程。

### 3.1 SIP 保护位置

```
/System/
/usr/（除 /usr/local/）
/bin/
/sbin/
/var/（选定子目录）
/Applications/（预安装的 Apple 应用）
```

### 3.2 SIP 状态和配置

```bash
csrutil status              # 检查 SIP 状态
csrutil disable             # 仅恢复模式
csrutil enable --without fs # 部分禁用（风险高）
```

### 3.3 绕过 SIP 的权限

| 权限 | 效果 |
|---|---|
| `com.apple.rootless.install` | 写入 SIP 保护路径 |
| `com.apple.rootless.install.heritable` | 子进程继承 SIP 绕过 |
| `com.apple.security.cs.allow-unsigned-executable-memory` | 内存中的 JIT/未签名代码 |
| `com.apple.private.security.clear-library-validation` | 加载未签名库 |

### 3.4 历史上的 SIP 绕过

| CVE | macOS | 技巧 |
|---|---|---|
| CVE-2021-30892 (Shrootless) | Monterey 预 12.0.1 | `system_installd` + 签名 pkg 中的安装脚本 |
| CVE-2022-22583 | Monterey 预 12.2 | `packagekit` + 挂载点操作 |
| CVE-2022-46689 (MacDirtyCow) | Ventura 预 13.1 | 写入 SIP 文件的 copy-on-write 竞态条件 |
| CVE-2023-32369 (Migraine) | Ventura 预 13.4 | 通过 systemmigrationd 的迁移助手 TCC/SIP 绕过 |
| CVE-2024-44243 | Sequoia 预 15.2 | StorageKit 守护进程利用 |

---

## 4. 沙盒逃逸

macOS 沙盒（应用程序沙盒，通过 `sandbox-exec` 或权限）限制应用程序对文件系统、网络和 IPC 的访问。

### 4.1 办公沙盒逃逸模式

| 向量 | 描述 |
|---|---|
| 打开/保存对话框滥用 | 用户通过对话框授权文件访问 → 宏读取/写入沙盒外 |
| `~/Library/LaunchAgents/` 持久化 | 某些沙盒配置文件允许写入 LaunchAgent plist |
| 登录项操作 | 添加指向沙盒外有效载荷的登录项 |
| 共享容器利用 | 多个应用程序共享相同的 App Group 容器 |

### 4.2 基于IPC的逃逸

| IPC 机制 | 逃逸向量 |
|---|---|
| XPC 服务 | 连接到验证不足的特权 XPC 服务 |
| Mach 端口 | 获取对特权任务端口的发送权 |
| Apple 事件 | 自动化未沙盒应用程序执行操作 |
| 分布式通知 | 信号未沙盒辅助程序执行有效载荷 |
| 剪贴板 | 将有效载荷写入剪贴板，由未沙盒应用程序消耗 |

### 4.3 浏览器沙盒

- Chromium：多进程模型，渲染器被沙盒，浏览器进程未被沙盒
- Safari：WebContent 进程被沙盒，父 Safari 进程权限更高
- 利用链：渲染器 RCE → 沙盒逃逸（通过 IPC 漏洞到浏览器进程）→ 系统访问

---

## 5. 代码签名和权限

### 5.1 检查签名和权限

```bash
codesign -dv --verbose=4 /path/to/app       # 签名详情
codesign -d --entitlements :- /path/to/app   # 报出权限
security cms -D -i /path/to/mobileprovision  # 配置文件

# 验证签名有效性
codesign --verify --deep --strict /path/to/app
spctl --assess --type execute /path/to/app   # Gatekeeper 评估
```

### 5.2 权限滥用用于提权

| 权限 | 滥用场景 |
|---|---|
| `com.apple.security.cs.disable-library-validation` | 将攻击者 dylib 注入授权进程 |
| `com.apple.security.cs.allow-dyld-environment-variables` | DYLD_INSERT_LIBRARIES 注入 |
| `com.apple.security.get-task-allow` | 附加调试器，注入代码 |
| `com.apple.security.cs.debugger` | 调试任何进程 |
| `com.apple.private.apfs.revert-to-snapshot` | 撤销 APFS 快照，绕过修改 |

### 5.3 硬化运行时绕过

硬化运行时防止：DYLD 环境变量、调试、未签名内存执行。绕过：
- 找到削弱硬化运行时的授权应用程序（`disable-library-validation`）
- 利用 JIT 授权应用程序（浏览器、虚拟机）执行未签名代码
- 使用 `get-task-allow` 授权调试构建（生产中遗留）

### 5.4 库验证绕过

库验证确保仅加载 Apple 签名或同团队签名的 dylib。

```bash
# 查找禁用库验证的应用程序
codesign -d --entitlements :- /Applications/*.app/Contents/MacOS/* 2>/dev/null | \
  grep -l "disable-library-validation"
```

---

## 6. 绕过后的持久化

| 方法 | 位置 | 重启后存活 | 备注 |
|---|---|---|---|
| LaunchAgent | `~/Library/LaunchAgents/` | 是 | 用户级，登录时运行 |
| LaunchDaemon | `/Library/LaunchDaemons/` | 是 | root 级，启动时运行 |
| 登录项 | `~/Library/Application Support/com.apple.backgroundtaskmanagementagent/` | 是 | 系统设置中可见 |
| Cron | `crontab -e` | 是 | 防御者常被忽视 |
| dylib 劫持 | 可写 dylib 搜索路径 | 是 | 目标应用程序启动时触发 |
| 文件夹操作 | `~/Library/Scripts/Folder Action Scripts/` | 是 | 触发文件夹事件 |

---

## 7. macOS 安全绕过决策树

```
目标 macOS 终端
│
├── 需要执行未信任二进制？
│   ├── 存在隔离属性？
│   │   ├── 是 → xattr -d com.apple.quarantine (§2.1)
│   │   └── 否 → 直接执行
│   └── Gatekeeper 仍阻止？
│       ├── 已签名但未签名 → 右键点击 → 打开覆盖
│       └── 未签名 → 嵌入签名捆绑包或使用归档技巧 (§2.2)
│
├── 需要访问 TCC 保护资源？
│   ├── FDA 授权应用可用？
│   │   ├── 是 → 利用 FDA 应用上下文 (§1.3)
│   │   └── 否 ↓
│   ├── 可获得自动化权限？
│   │   ├── 是 → Apple 事件到 TCC 授权应用 (§1.3)
│   │   └── 否 ↓
│   ├── SIP 禁用？
│   │   ├── 是 → 直接 TCC.db 修改 (§1.2)
│   │   └── 否 → 检查特定版本的 TCC 绕过 (→ TCC_BYPASS_MATRIX.md)
│   └── MDM 存在？
│       └── 受感染的 MDM → 推送 PPPC 配置文件 (§1.3)
│
├── 需要绕过 SIP？
│   ├── 检查 macOS 版本 → 历史 SIP CVE? (§3.4)
│   ├── 找到授权 Apple 二进制 → 利用 SIP 绕过权限 (§3.3)
│   └── 恢复模式访问？ → csrutil disable (§3.2)
│
├── 需要沙盒逃逸？
│   ├── 办公宏上下文 → 对话框/LaunchAgent 技巧 (§4.1)
│   ├── 验证不足的 XPC 服务 → IPC 逃逸 (§4.2)
│   └── 浏览器上下文 → 渲染器 → 沙盒逃逸链 (§4.3)
│
├── 需要注入签名进程？
│   ├── disable-library-validation 权限？ → dylib 注入
│   ├── allow-dyld-environment-variables？ → DYLD_INSERT_LIBRARIES
│   ├── get-task-allow？ → 调试器附加
│   └── 无 → 检查 macos-process-injection SKILL.md
│
└── 需要持久化？
    └── 根据访问级别选择方法 (§6)
```

---

## 8. 快速参考：工具命令

```bash
# 列出 TCC 权限
tccutil reset All                              # 重置所有 TCC（管理员）
sqlite3 TCC.db "SELECT * FROM access;"         # 读取 TCC DB

# Gatekeeper 状态
spctl --status                                 # Gatekeeper 启用？
spctl --assess -v /path/to/app                 # 检查应用程序评估

# SIP 状态
csrutil status

# 在系统中查找有趣的权限
find /System/Applications /Applications -name "*.app" -exec sh -c \
  'codesign -d --entitlements :- "$1" 2>/dev/null | grep -q "disable-library-validation" && echo "$1"' _ {} \;

# 列出加载的 kext（内核扩展）
kextstat | grep -v com.apple

# 沙盒配置文件检查
sandbox-exec -p "(version 1)(allow default)" /bin/ls  # 测试沙盒规则
```
