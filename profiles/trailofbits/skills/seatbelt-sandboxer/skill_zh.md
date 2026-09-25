# macOS Seatbelt Sandbox Profiling

为应用程序生成基于允许列表的最小权限 Seatbelt 沙盒配置。

## 使用场景

- 用户要求在 macOS 上对应用程序进行 "沙盒化"、"隔离" 或 "限制"
- 需要限制文件/网络访问的任何 macOS 进程的沙盒化
- 如果供应链攻击是担忧，创建纵深防御隔离

## 不适用场景

- Linux 容器（使用 seccomp-bpf、AppArmor 或命名空间）
- Windows 应用程序
- 确实需要广泛系统访问的应用程序
- 快速一次性脚本，其中沙盒开销不合理

## Profiling 方法

### 第 1 步：识别应用程序需求

确定应用程序在这些资源类别中的需求：

| 类别 | 操作 | 常见用例 |
|------|------|---------|
| **文件读取** | `file-read-data`、`file-read-metadata`、`file-read-xattr`、`file-test-existence`、`file-map-executable` | 读取源文件、配置、库 |
| **文件写入** | `file-write-data`、`file-write-create`、`file-write-unlink`、`file-write-mode`、`file-write-xattr`、`file-clone`、`file-link` | 输出文件、缓存、临时文件 |
| **网络** | `network-bind`、`network-inbound`、`network-outbound` | 服务器、API 调用、包下载 |
| **进程** | `process-fork`、`process-exec`、`process-exec-interpreter`、`process-info*`、`process-codesigning*` | 启动子进程、脚本 |
| **Mach IPC** | `mach-lookup`、`mach-register`、`mach-bootstrap`、`mach-task-name` | 系统服务、XPC、通知 |
| **POSIX IPC** | `ipc-posix-shm*`、`ipc-posix-sem*` | 共享内存、信号量 |
| **Sysctl** | `sysctl-read`、`sysctl-write` | 读取系统信息（CPU、内存） |
| **IOKit** | `iokit-open`、`iokit-get-properties`、`iokit-set-properties` | 硬件访问、设备驱动 |
| **信号** | `signal` | 进程间信号处理 |
| **伪终端** | `pseudo-tty` | 终端模拟 |
| **系统** | `system-fsctl`、`system-socket`、`system-audit`、`system-info` | 低级系统调用 |
| **用户偏好设置** | `user-preference-read`、`user-preference-write` | 读取/写入用户默认设置 |
| **通知** | `darwin-notification-post`、`distributed-notification-post` | 系统通知 |
| **AppleEvents** | `appleevent-send` | 应用间通信（AppleScript） |
| **相机/麦克风** | `device-camera`、`device-microphone` | 媒体捕获 |
| **动态代码** | `dynamic-code-generation` | JIT 编译 |
| **NVRAM** | `nvram-get`、`nvram-set`、`nvram-delete` | 固件变量 |

对于每个类别，确定：**是否需要** 和 **具体范围**（路径、服务等）。

如果应用程序有多个执行显著不同操作的子命令，例如 Webpack 这样的 JavaScript 打包器中的 `build` 和 `serve` 命令，请执行以下操作：
* 分别对子命令进行配置
* 为每个子命令创建单独的 Sandbox 配置
* 创建一个辅助脚本，作为原始二进制的替换，根据传递的子命令执行带有适当 Seatbelt 配置的沙盒化应用程序。

### 第 2 步：从最小配置开始

从拒绝所有操作和基本进程操作开始，保存在一个以 `.sb` 扩展名命名的 Seatbelt 配置文件中。

```scheme
(version 1)
(deny default)

;; 任何进程都需要的操作
(allow process-exec*)
(allow process-fork)
(allow sysctl-read)

;; 元数据访问（stat、readdir）- 不暴露文件内容
(allow file-read-metadata)
```

### 第 3 步：添加文件读取访问（允许列表）

使用 `file-read-data`（而不是 `file-read*`）进行基于允许列表的读取：

```scheme
(allow file-read-data
    ;; 系统路径（大多数运行时所需）
    (subpath "/usr")
    (subpath "/bin")
    (subpath "/sbin")
    (subpath "/System")
    (subpath "/Library")
    (subpath "/opt")                    ;; Homebrew
    (subpath "/private/var")
    (subpath "/private/etc")
    (subpath "/private/tmp")
    (subpath "/dev")

    ;; 路径解析的根符号链接
    (literal "/")
    (literal "/var")
    (literal "/etc")
    (literal "/tmp")
    (literal "/private")

    ;; 应用程序特定配置（按需自定义）
    (regex (string-append "^" (regex-quote (param "HOME")) "/\\.myapp(/.*)?$"))

    ;; 工作目录
    (subpath (param "WORKING_DIR")))
```

**为什么使用 `file-read-data` 而不是 `file-read*`？**
- `file-read*` 允许所有文件读取操作，包括任何路径
- `file-read-data` 仅允许从列表中指定的路径读取文件内容
- 结合 `file-read-metadata`（广泛允许），这提供了：
  - ✅ 可以 stat/readdir 任何地方（路径解析所需）
  - ❌ 无法读取允许列表外文件的内容

### 第 4 步：添加文件写入访问（限制）

```scheme
(allow file-write*
    ;; 仅工作目录
    (subpath (param "WORKING_DIR"))

    ;; 临时目录
    (subpath "/private/tmp")
    (subpath "/tmp")
    (subpath "/private/var/folders")

    ;; 输出设备文件
    (literal "/dev/null")
    (literal "/dev/tty"))
```

### 第 5 步：配置网络

三种网络访问级别：

```scheme
;; 选项 1：阻止所有网络（最严格 - 用于构建工具）
(deny network*)

;; 选项 2：仅本地主机（用于开发服务器、本地服务）
;; 绑定到本地端口
(allow network-bind (local tcp "*:*"))
;; 接受传入连接
(allow network-inbound (local tcp "*:*"))
;; 仅本地主机和 DNS 的传出连接
(allow network-outbound
    (literal "/private/var/run/mDNSResponder")  ;; DNS 解析
    (remote ip "localhost:*"))                   ;; 仅本地主机

;; 选项 3：允许所有网络（最宽松 - 尽量避免）
(allow network*)
```

**网络过滤器语法：**
- `(local tcp "*:*")` - 任何本地 TCP 端口
- `(local tcp "*:8080")` - 特定本地端口
- `(remote ip "localhost:*")` - 仅本地主机传出
- `(remote tcp)` - 任何主机的传出 TCP
- `(literal "/private/var/run/mDNSResponder")` - DNS 的 Unix 套接字

### 第 6 步：迭代测试

生成或编辑 Seatbelt 配置后，在沙盒中测试目标应用程序的功能。如果任何功能无法正常工作，请修订 Seatbelt 配置。重复此过程，直到生成最小权限的 Seatbelt 文件，并确认通过生成的 Seatbelt 配置进行沙盒化时应用程序可以正常工作。

如果程序需要外部输入才能完全运行（例如需要应用程序进行打包的 JavaScript 打包器），从知名且最好是官方来源的示例输入中找到。例如，Rspack 打包器的示例项目：https://github.com/rstackjs/rstack-examples/tree/main/rspack/

```bash
# 测试基本执行
sandbox-exec -f profile.sb -D WORKING_DIR=/path -D HOME=$HOME /bin/echo "test"

# 测试实际应用程序
sandbox-exec -f profile.sb -D WORKING_DIR=/path -D HOME=$HOME \
  /path/to/application --args

# 测试安全限制
sandbox-exec -f profile.sb -D WORKING_DIR=/tmp -D HOME=$HOME \
  cat ~/.ssh/id_rsa
# 预期：操作不被允许
```

**常见失败模式：**

| 症状 | 原因 | 修复 |
|------|------|------|
| 退出码 134 (SIGABRT) | 沙盒违规 | 检查哪个操作被阻止 |
| 退出码 65 + 语法错误 | 无效的 Seatbelt 语法 | 检查 Seatbelt 语法 |
| `ENOENT` 对于现有文件 | 缺少 `file-read-metadata` | 添加 `(allow file-read-metadata)` |
| 进程挂起 | 缺少 IPC 权限 | 如果需要，添加 `(allow mach-lookup)` |

## Seatbelt 语法参考

### 路径过滤器
```scheme
(subpath "/path")           ;; /path 及所有子路径
(literal "/path/file")      ;; 精确路径
(regex "^/path/.*\\.js$")   ;; 正则匹配
```

### 参数替换
```scheme
(param "WORKING_DIR")                                    ;; 直接使用
(subpath (param "WORKING_DIR"))                          ;; 在 subpath 中使用
(string-append (param "HOME") "/.config")                ;; 连接
(regex-quote (param "HOME"))                             ;; 正则转义
```

### 操作

**文件操作：**
```scheme
(allow file-read-data ...)          ;; 读取文件内容
(allow file-read-metadata)          ;; stat、lstat、readdir（不暴露内容）
(allow file-read-xattr ...)         ;; 读取扩展属性
(allow file-test-existence ...)     ;; 检查文件是否存在
(allow file-map-executable ...)     ;; mmap 可执行文件（dylibs）
(allow file-write-data ...)         ;; 写入现有文件
(allow file-write-create ...)       ;; 创建新文件
(allow file-write-unlink ...)       ;; 删除文件
(allow file-write* ...)             ;; 所有写入操作
(allow file-read* ...)              ;; 所有读取操作（谨慎使用）
```

**进程操作：**
```scheme
(allow process-exec* ...)           ;; 执行二进制文件
(allow process-fork)                ;; 启动子进程
(allow process-info-pidinfo)        ;; 查询进程信息
(allow signal)                      ;; 发送/接收信号
```

**网络操作：**
```scheme
(allow network-bind (local tcp "*:*"))              ;; 绑定到任何本地 TCP 端口
(allow network-bind (local tcp "*:8080"))           ;; 绑定到特定端口
(allow network-inbound (local tcp "*:*"))           ;; 接受 TCP 连接
(allow network-outbound (remote ip "localhost:*"))  ;; 仅本地主机传出
(allow network-outbound (remote tcp))               ;; 任何主机的传出 TCP
(allow network-outbound
    (literal "/private/var/run/mDNSResponder"))     ;; DNS 的 Unix 套接字
(allow network*)                                    ;; 所有网络（谨慎使用）
(deny network*)                                     ;; 阻止所有网络
```

**IPC 操作：**
```scheme
(allow mach-lookup ...)             ;; Mach IPC 查找
(allow mach-register ...)           ;; 注册 Mach 服务
(allow ipc-posix-shm* ...)          ;; POSIX 共享内存
(allow ipc-posix-sem* ...)          ;; POSIX 信号量
```

**系统操作：**
```scheme
(allow sysctl-read)                 ;; 读取系统信息
(allow sysctl-write ...)            ;; 修改 sysctl（罕见）
(allow iokit-open ...)              ;; IOKit 设备访问
(allow pseudo-tty)                  ;; 终端模拟
(allow dynamic-code-generation)     ;; JIT 编译
(allow user-preference-read ...)    ;; 读取用户默认设置
```

## 已知限制

1. **已弃用但功能正常**：Apple 已弃用 sandbox-exec，但在 macOS 14+ 上仍可工作
2. **通常需要临时目录访问**：许多应用程序需要 `/tmp` 和 `/var/folders`

## 示例：通用 CLI 应用程序

```scheme
(version 1)
(deny default)

;; 进程
(allow process-exec*)
(allow process-fork)
(allow sysctl-read)

;; 文件元数据（路径解析）
(allow file-read-metadata)

;; 文件读取（允许列表）
(allow file-read-data
    (literal "/") (literal "/var") (literal "/etc") (literal "/tmp") (literal "/private")
    (subpath "/usr") (subpath "/bin") (subpath "/sbin") (subpath "/opt")
    (subpath "/System") (subpath "/Library") (subpath "/dev")
    (subpath "/private/var") (subpath "/private/etc") (subpath "/private/tmp")
    (subpath (param "WORKING_DIR")))

;; 文件写入（限制）
(allow file-write*
    (subpath (param "WORKING_DIR"))
    (subpath "/private/tmp") (subpath "/tmp") (subpath "/private/var/folders")
    (literal "/dev/null") (literal "/dev/tty"))

;; 禁用网络
(deny network*)
```

**使用方法：**
```bash
sandbox-exec -f profile.sb \
  -D WORKING_DIR=/path/to/project \
  -D HOME=$HOME \
  /path/to/application
```

## 参考文献

- [Apple Sandbox Guide (逆向工程)](https://reverse.put.as/wp-content/uploads/2011/09/Apple-Sandbox-Guide-v1.0.pdf)
- [sandbox-exec man page](https://keith.github.io/xcode-man-pages/sandbox-exec.1.html)
