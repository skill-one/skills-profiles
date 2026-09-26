# witr — 为什么它在运行？

> 技能来自 [ara.so](https://ara.so) — 每日 2026 技能集合。

**witr** 是一个 Go CLI/TUI 工具，用于回答任何进程、服务或端口“为什么它在运行？”的问题。它不会让你手动关联 `ps`、`lsof`、`ss`、`systemctl` 和 `docker ps`，而是让因果关系链明确化——显示一个运行中的事物来自哪里、如何启动的，以及负责的上级/容器/壳链。

---

## 安装

### 最快方式（Unix）
```bash
curl -fsSL https://raw.githubusercontent.com/pranshuparmar/witr/main/install.sh | bash
```

### 最快方式（Windows PowerShell）
```powershell
irm https://raw.githubusercontent.com/pranshuparmar/witr/main/install.ps1 | iex
```

### 软件包管理器
```bash
# Homebrew (macOS/Linux)
brew install witr

# Conda
conda install -c conda-forge witr

# Arch Linux (AUR)
yay -S witr-bin

# Windows winget
winget install -e --id Pranshuparmar.witr

# Windows Scoop
scoop install main/witr

# Alpine / apk
sudo apk add --allow-untrusted ./witr-*.apk

# Go 源码安装
go install github.com/pranshuparmar/witr/cmd/witr@latest
```

---

## 主要命令和标志

### 基本用法
```bash
# 通过 PID 检查进程
witr <pid>

# 通过进程名称（子串匹配）检查
witr <name>

# 检查绑定到端口的进程
witr --port <port>
witr -p <port>

# 启动交互式 TUI 仪表板
witr --interactive
witr -i

# 显示所有运行进程及因果关系信息
witr --all
witr -a

# 输出为 JSON（用于脚本）
witr --json <pid>

# 跟踪/监视模式——自动刷新
witr --watch <pid>
witr -w <pid>

# 详细输出——显示完整环境和元数据
witr --verbose <pid>
witr -v <pid>

# 按用户筛选进程
witr --user <username>

# 显示版本
witr --version
```

### 常用标志参考
| 标志 | 简写 | 描述 |
|------|-------|-------------|
| `--port` | `-p` | 通过端口号检查 |
| `--interactive` | `-i` | 启动 TUI 仪表板 |
| `--all` | `-a` | 显示所有进程 |
| `--json` | | 输出为 JSON |
| `--watch` | `-w` | 自动刷新/跟踪 |
| `--verbose` | `-v` | 完整元数据输出 |
| `--user` | | 按操作系统用户筛选 |
| `--version` | | 打印版本 |

---

## 交互式 TUI 模式

启动完整仪表板：
```bash
witr -i
# 或
witr --interactive
```

**TUI 键盘快捷键：**
| 键 | 动作 |
|-----|--------|
| `↑` / `↓` | 导航进程列表 |
| `Enter` | 展开进程详情 / 因果链 |
| `f` | 筛选/搜索进程 |
| `s` | 按列排序 |
| `r` | 刷新 |
| `j` | 切换 JSON 视图 |
| `q` / `Ctrl+C` | 退出 |

---

## 示例输出

### 检查 PID
```bash
witr 1234
```
```
PID: 1234
名称: node
二进制文件: /usr/local/bin/node
启动时间: 2026-03-18 09:12:44
用户: ubuntu

为什么它在运行？
  └─ 由 npm (PID 1200) 启动
       └─ 由 bash (PID 1180) 启动
            └─ 由 sshd (PID 980) 启动
                 └─ 由 systemd (PID 1) [服务: sshd.service] 启动
```

### 检查端口
```bash
witr --port 8080
```
```
端口: 8080 (TCP, 监听)
进程: python3 (PID 4512)
二进制文件: /usr/bin/python3
用户: deploy

为什么它在运行？
  └─ 由 gunicorn (PID 4490) 启动
       └─ 由 systemd (PID 1) [服务: myapp.service] 启动
            单位文件: /etc/systemd/system/myapp.service
            ExecStart: /usr/bin/gunicorn app:app --bind 0.0.0.0:8080
```

### JSON 输出（用于脚本）
```bash
witr --json 4512
```
```json
{
  "pid": 4512,
  "name": "python3",
  "binary": "/usr/bin/python3",
  "user": "deploy",
  "started_at": "2026-03-18T09:00:00Z",
  "causality_chain": [
    {"pid": 4490, "name": "gunicorn", "type": "父进程"},
    {"pid": 1,    "name": "systemd",  "type": "监督者", "service": "myapp.service"}
  ]
}
```

### 跟踪/监视进程
```bash
# 每 2 秒刷新
witr --watch 4512
```

---

## 常见模式

### 查找端口监听者是谁启动的
```bash
# 快速检查：端口 5432（Postgres）的所有者是谁？
witr --port 5432

# 获取机器可读输出用于自动化
witr --json --port 5432 | jq '.causality_chain[-1].service'
```

### 审计所有运行的服务
```bash
# 列出所有带因果关系信息，然后通过 less 查看
witr --all | less

# 导出完整审计到 JSON
witr --all --json > audit.json
```

### 检查 Docker/容器化进程
```bash
# witr 理解容器边界
witr <容器化进程的 PID>
# 输出将显示：容器 → 容器运行时 → systemd 链
```

### 在 Shell 脚本中使用
```bash
#!/usr/bin/env bash
# 检查端口 8080 是否在使用中及其原因
if witr --json --port 8080 > /tmp/witr_out.json 2>/dev/null; then
  SERVICE=$(jq -r '.causality_chain[-1].service // "unknown"' /tmp/witr_out.json)
  echo "端口 8080 属于服务: $SERVICE"
else
  echo "端口 8080 没有在使用中"
fi
```

### 按用户筛选进程
```bash
# 仅显示由 www-data 拥有且正在运行的原因
witr --all --user www-data
```

---

## 平台支持

| 平台 | 架构 | 备注 |
|----------|--------------|-------|
| Linux | amd64, arm64 | 完全支持 |
| macOS | amd64, arm64 (Apple Silicon) | 完全支持 |
| Windows | amd64 | 完全支持 |
| FreeBSD | amd64, arm64 | 完全支持 |

---

## Go 集成（嵌入 witr 逻辑）

如果你想在 Go 项目中程序化使用 witr：

```bash
go get github.com/pranshuparmar/witr
```

```go
package main

import (
    "fmt"
    "github.com/pranshuparmar/witr/pkg/inspector"
)

func main() {
    // 通过 PID 检查进程
    result, err := inspector.InspectPID(1234)
    if err != nil {
        panic(err)
    }

    fmt.Printf("进程: %s\n", result.Name)
    for _, link := range result.CausalityChain {
        fmt.Printf("  └─ %s (PID %d)\n", link.Name, link.PID)
    }
}
```

```go
// 通过端口检查
result, err := inspector.InspectPort(8080, "tcp")
if err != nil {
    panic(err)
}
fmt.Printf("端口 8080 属于 PID %d (%s)\n", result.PID, result.Name)
```

---

## 故障排除

### 对某些 PID 权限被拒绝
```bash
# witr 需要读取 /proc (Linux) 或等效位置的权限
# 对系统级进程使用 sudo 运行
sudo witr <pid>
sudo witr --port 80
```

### 安装后二进制文件未找到
```bash
# 确保 install 位置在 PATH 中
export PATH="$PATH:/usr/local/bin"   # Unix 默认 install
# 或对于 Go 安装：
export PATH="$PATH:$(go env GOPATH)/bin"
```

### 端口未找到 / 无输出
```bash
# 首先确认端口是否实际在监听
ss -tlnp | grep <port>       # Linux
netstat -an | grep <port>    # macOS/Windows

# 然后重试
witr --port <port>
```

### TUI 无法正确渲染
```bash
# 确保终端支持 256 色彩
export TERM=xterm-256color
witr --interactive

# 如果在 Windows 上，使用 Windows Terminal 获得最佳 TUI 体验
```

### 进程在检查前已退出
```bash
# witr 只能检查当前运行的进程
# 对长时间运行的进程使用 --watch 监控它
witr --watch <pid>
```

### macOS：某些进程需要提升权限
```bash
# 系统完整性保护可能会限制某些进程的元数据
sudo witr <pid>
```

---

## 快速参考卡

```
witr <pid>              # PID X 为什么在运行？
witr <name>            # 进程 "nginx" 为什么在运行？
witr -p <port>         # 端口 8080 上是什么及其原因？
witr -i                # 交互式 TUI 仪表板
witr -a                # 显示所有进程 + 因果关系
witr --json <pid>      # 机器可读输出
witr -w <pid>          # 跟踪/监视进程
witr -v <pid>          # 详细：完整环境 + 元数据
witr --user <user>     # 按操作系统用户筛选
```
