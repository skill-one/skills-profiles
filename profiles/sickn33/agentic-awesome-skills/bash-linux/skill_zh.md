# Bash Linux 模式

> Linux/macOS 上 Bash 的基本模式。

---

## 1. 运算符语法

### 命令串联

| 运算符 | 含义 | 示例 |
|--------|------|------|
| `;` | 顺序执行 | `cmd1; cmd2` |
| `&&` | 前一个命令成功时执行 | `npm install && npm run dev` |
| `\|\|` | 前一个命令失败时执行 | `npm test \|\| echo "Tests failed"` |
| `\|` | 管道输出 | `ls \| grep ".js"` |

---

## 2. 文件操作

### 基本命令

| 任务 | 命令 |
|------|------|
| 列出所有 | `ls -la` |
| 查找文件 | `find . -name "*.js" -type f` |
| 文件内容 | `cat file.txt` |
| 前N行 | `head -n 20 file.txt` |
| 后N行 | `tail -n 20 file.txt` |
| 跟踪日志 | `tail -f log.txt` |
| 文件中搜索 | `grep -r "pattern" --include="*.js"` |
| 文件大小 | `du -sh *` |
| 磁盘使用情况 | `df -h` |

---

## 3. 进程管理

| 任务 | 命令 |
|------|------|
| 列出进程 | `ps aux` |
| 按名称查找 | `ps aux \| grep node` |
| 通过PID终止 | `kill -9 <PID>` |
| 查找端口用户 | `lsof -i :3000` |
| 终止端口 | `kill -9 $(lsof -t -i :3000)` |
| 后台执行 | `npm run dev &` |
| 任务列表 | `jobs -l` |
| 带到前台 | `fg %1` |

---

## 4. 文本处理

### 核心工具

| 工具 | 用途 | 示例 |
|------|------|------|
| `grep` | 搜索 | `grep -rn "TODO" src/` |
| `sed` | 替换 | `sed -i 's/old/new/g' file.txt` |
| `awk` | 提取列 | `awk '{print $1}' file.txt` |
| `cut` | 切分字段 | `cut -d',' -f1 data.csv` |
| `sort` | 排序行 | `sort -u file.txt` |
| `uniq` | 唯一行 | `sort file.txt \| uniq -c` |
| `wc` | 计数 | `wc -l file.txt` |

---

## 5. 环境变量

| 任务 | 命令 |
|------|------|
| 查看所有 | `env` 或 `printenv` |
| 查看单个 | `echo $PATH` |
| 设置临时 | `export VAR="value"` |
| 脚本中设置 | `VAR="value" command` |
| 添加到PATH | `export PATH="$PATH:/new/path"` |

---

## 6. 网络

| 任务 | 命令 |
|------|------|
| 下载 | `curl -O https://example.com/file` |
| API请求 | `curl -X GET https://api.example.com` |
| POST JSON | `curl -X POST -H "Content-Type: application/json" -d '{"key":"value"}' URL` |
| 检查端口 | `nc -zv localhost 3000` |
| 网络信息 | `ifconfig` 或 `ip addr` |

---

## 7. 脚本模板

```bash
#!/bin/bash
set -euo pipefail  # 出错时退出，未定义变量时退出，管道失败时退出

# 颜色（可选）
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 函数
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

# 主函数
main() {
    log_info "Starting..."
    # 你的逻辑
    log_info "Done!"
}

main "$@"
```

---

## 8. 常用模式

### 检查命令是否存在

```bash
if command -v node &> /dev/null; then
    echo "Node is installed"
fi
```

### 默认变量值

```bash
NAME=${1:-"default_value"}
```

### 按行读取文件

```bash
while IFS= read -r line; do
    echo "$line"
done < file.txt
```

### 遍历文件

```bash
for file in *.js; do
    echo "Processing $file"
done
```

---

## 9. 与 PowerShell 的差异

| 任务 | PowerShell | Bash |
|------|------------|------|
| 列出文件 | `Get-ChildItem` | `ls -la` |
| 查找文件 | `Get-ChildItem -Recurse` | `find . -type f` |
| 环境 | `$env:VAR` | `$VAR` |
| 字符串拼接 | `"$a$b"` | `"$a$b"` (相同) |
| 空值检查 | `if ($x)` | `if [ -n "$x" ]` |
| 管道 | 基于对象 | 基于文本 |

---

## 10. 错误处理

### 设置选项

```bash
set -e          # 出错时退出
set -u          # 未定义变量时退出
set -o pipefail # 管道失败时退出
set -x          # 调试：打印命令
```

### 清理陷阱

```bash
cleanup() {
    echo "Cleaning up..."
    rm -f /tmp/tempfile
}
trap cleanup EXIT
```

---

> **记住：** Bash 是基于文本的。使用 `&&` 进行成功链，使用 `set -e` 进行安全检查，并引号化你的变量！

## 使用场景
这项技能适用于执行概述中描述的工作流程或操作。

## 限制
- 仅在任务明确匹配上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家评审的替代品。
- 如果缺少必要的输入、权限、安全边界或成功标准，请停止并请求澄清。
