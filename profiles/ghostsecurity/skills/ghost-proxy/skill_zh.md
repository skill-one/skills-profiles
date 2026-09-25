# Reaper MITM 代理

Reaper 是一个基于命令行的 MITM HTTPS 代理，用于应用安全测试。它可以拦截、记录并允许检查通过它的 HTTP/HTTPS 流量。使用它来捕获用于安全验证的实时请求/响应对。

## 前置条件

在使用任何 reaper 命令之前，请确保已安装最新版本的二进制文件：

```bash
curl -sfL https://raw.githubusercontent.com/ghostsecurity/reaper/main/scripts/install.sh | bash
```

本文档中所有的 `reaper` 命令都应作为 `~/.ghost/bin/reaper` 调用，除非 `~/.ghost/bin` 在 `PATH` 中。

## 快速参考

| 命令 | 目的 |
|---------|---------|
| `reaper start --domains example.com` | 启动代理（前台） |
| `reaper start --domains example.com -d` | 启动代理（守护进程） |
| `reaper logs` | 显示最近的捕获条目 |
| `reaper search --method POST --path /api/*` | 搜索捕获的流量 |
| `reaper get <id>` | 显示完整的请求 + 响应 |
| `reaper req <id>` | 仅显示原始 HTTP 请求 |
| `reaper res <id>` | 仅显示原始 HTTP 响应 |
| `reaper stop` | 停止守护进程 |

## 启动代理

针对目标域启动 reaper。至少需要一个 `--domains` 或 `--hosts` 标志。

```bash
# 拦截所有到 example.com 及其子域的流量
reaper start --domains example.com

# 多个域
reaper start --domains example.com,api.internal.co

# 精确主机名匹配
reaper start --hosts api.example.com

# 域后缀和精确主机名匹配
reaper start --domains example.com --hosts special.internal.co

# 自定义端口（默认：8443）
reaper start --domains example.com --port 9090

# 以后台守护进程方式运行
reaper start --domains example.com -d
```

**作用域行为**：
- `--domains`：后缀匹配。`example.com` 匹配 `example.com`、`api.example.com`、`sub.api.example.com`
- `--hosts`：精确匹配。`api.example.com` 仅匹配 `api.example.com`
- 范围外的流量透明通过且不记录

## 通过代理路由流量

配置 HTTP 客户端使用代理。默认监听地址是 `localhost:8443`。

```bash
# curl
curl -x http://localhost:8443 -k https://api.example.com/endpoint

# 环境变量（适用于许多工具）
export http_proxy=http://localhost:8443
export https_proxy=http://localhost:8443

# Python requests
import requests
requests.get("https://api.example.com/endpoint",
             proxies={"http": "http://localhost:8443", "https": "http://localhost:8443"},
             verify=False)
```

需要 `-k` / `verify=False` 标志，因为 reaper 在启动时生成自己的 CA 证书，用于 MITM TLS 拦截。

## 查看捕获的流量

### 最近条目

```bash
# 显示最后 50 条条目（默认）
reaper logs

# 显示最后 200 条条目
reaper logs -n 200
```

输出列：`ID`、`METHOD`、`HOST`、`PATH`、`STATUS`、`MS`、`REQ`（请求体大小）、`RES`（响应体大小）。

### 搜索

```bash
# 按 HTTP 方法
reaper search --method POST

# 按主机（支持 * 通配符）
reaper search --host *.api.example.com

# 按域后缀
reaper search --domains example.com

# 按路径前缀（支持 * 通配符）
reaper search --path /api/v3/transfer

# 按状态码
reaper search --status 200

# 组合过滤器
reaper search --method POST --path /api/v3/* --status 200 -n 50
```

### 检查单个条目

```bash
# 完整请求和响应（原始 HTTP）
reaper get 42

# 仅请求
reaper req 42

# 仅响应
reaper res 42
```

输出为原始 HTTP/1.1 格式，包括头部和正文，适合分析或重放。

## 停止代理

```bash
reaper stop
```

## 常见工作流程

### 验证安全发现

使用 `validate` 技能时（可能需要与用户协作设置测试环境）：

1. 针对应用域启动 reaper
2. 通过运行 `reaper logs` 验证流量是否被捕获——在通过代理路由测试请求后，至少应出现一条条目
3. 如果没有条目出现，请验证代理设置和域作用域是否与目标匹配
4. 以普通用户身份进行认证（或要求用户进行认证），并合法地使用漏洞端点
5. 搜索捕获的请求以了解预期的请求格式
6. 构造并发送一个执行发现中描述的漏洞的恶意请求
7. 检查响应以确定漏洞是否成功
8. 使用 `reaper get <id>` 捕获完整的请求/响应作为证据

## 数据存储

所有数据存储在 `~/.reaper/`：
- `reaper.db` - 包含捕获条目的 SQLite 数据库
- `reaper.sock` - 用于 CLI 到守护进程的 IPC 的 Unix 套接字
- `reaper.pid` - 守护进程进程 ID

CA 证书在每次启动时在内存中生成，不会持久化。
