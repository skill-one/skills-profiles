# Mole Mac Cleaner

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能集合。

Mole (`mo`) 是一个一体化的 macOS 维护 CLI 工具，将深度清理、智能应用卸载、磁盘分析、系统优化、实时监控和项目文件清理集成到一个单一的二进制文件中。

## 安装

```bash
# 通过 Homebrew（推荐）
brew install mole

# 通过安装脚本（支持版本锁定）
curl -fsSL https://raw.githubusercontent.com/tw93/mole/main/install.sh | bash

# 特定版本
curl -fsSL https://raw.githubusercontent.com/tw93/mole/main/install.sh | bash -s 1.17.0

# 最新主分支（夜间版）
curl -fsSL https://raw.githubusercontent.com/tw93/mole/main/install.sh | bash -s latest
```

## 核心命令

```bash
mo                    # 交互式菜单（使用箭头键或 vim 的 h/j/k/l）
mo clean              # 深度系统缓存 + 浏览器 + 开发工具清理
mo uninstall          # 删除应用及其所有隐藏残留文件
mo optimize           # 重建缓存、重置网络、刷新 Finder/Dock
mo analyze            # 可视化磁盘空间探索器
mo status             # 实时系统健康仪表盘
mo purge              # 删除项目构建文件（node_modules、target、dist）
mo installer          # 查找并删除安装器 .dmg/.pkg 文件

mo touchid            # 配置 Touch ID 以用于 sudo
mo completion         # 设置 shell 标签补全
mo update             # 更新 Mole
mo update --nightly   # 更新到最新未发布的构建（仅限脚本安装）
mo remove             # 卸载 Mole 本身
mo --help
mo --version
```

## 删除前安全预览

始终先运行破坏性命令的干运行：

```bash
mo clean --dry-run
mo uninstall --dry-run
mo purge --dry-run

# 与 debug 结合以获取详细输出
mo clean --dry-run --debug
mo optimize --dry-run --debug
```

## 关键命令详情

### `mo clean` — 深度清理

清理用户应用缓存、浏览器缓存（Chrome、Safari、Firefox）、开发工具缓存（Xcode、Node.js、npm）、系统日志、临时文件、应用特定缓存（Spotify、Dropbox、Slack）和废纸篓。

```bash
mo clean                  # 交互式清理
mo clean --dry-run        # 预览将要删除的内容
mo clean --whitelist      # 管理受保护的缓存（排除清理）
```

白名单配置位于 `~/.config/mole/`。编辑它以保护您想要保留的路径。

### `mo uninstall` — 智能应用删除

查找应用，显示大小和最后使用日期，然后删除应用包及其所有相关文件：
- 应用支持、缓存、偏好设置
- 日志、WebKit 存储、Cookie
- 扩展、插件、启动守护进程

```bash
mo uninstall              # 交互式多选列表
mo uninstall --dry-run    # 预览删除操作
```

### `mo optimize` — 系统刷新

```bash
mo optimize               # 运行所有优化
mo optimize --dry-run     # 预览
mo optimize --whitelist   # 排除特定优化
```

优化包括：
- 重建系统数据库并清除缓存
- 重置网络服务
- 刷新 Finder 和 Dock
- 清理诊断和崩溃日志
- 删除交换文件并重启动态分页器
- 重建启动服务和 Spotlight 索引

### `mo analyze` — 磁盘探索器

```bash
mo analyze                # 分析主目录（默认跳过 /Volumes）
mo analyze ~/Downloads    # 分析特定路径
mo analyze /Volumes       # 明确包含外部驱动器

# 用于脚本的可读输出
mo analyze --json ~/Documents
```

**JSON 输出示例：**
```json
{
  "path": "/Users/you/Documents",
  "entries": [
    { "name": "Library", "path": "...", "size": 80939438080, "is_dir": true }
  ],
  "total_size": 168393441280,
  "total_files": 42187
}
```

**`mo analyze` 内部的导航快捷键：**
| 键 | 操作 |
|-----|--------|
| `↑↓` 或 `j/k` | 导航列表 |
| `←→` 或 `h/l` | 返回 / 进入目录 |
| `O` | 在 Finder 中打开 |
| `F` | 在 Finder 中显示 |
| `⌫` | 通过 Finder 移至废纸篓（比直接删除更安全） |
| `L` | 显示大文件 |
| `Q` | 退出 |

### `mo status` — 实时仪表盘

```bash
mo status                 # 实时 CPU、GPU、内存、磁盘、网络、进程
mo status --json          # JSON 输出用于脚本
mo status | jq '.health_score'   # 自动检测管道 → 输出 JSON
```

**JSON 输出示例：**
```json
{
  "host": "MacBook-Pro",
  "health_score": 92,
  "cpu": { "usage": 45.2, "logical_cpu": 8 },
  "memory": { "total": 25769803776, "used": 15049334784, "used_percent": 58.4 },
  "disks": [],
  "uptime": "3d 12h 45m"
}
```

`mo status` 内部的快捷键：`k` 切换猫吉祥物，`q` 退出。

### `mo purge` — 项目文件清理

扫描 `node_modules`、`target`、`build`、`dist`、`venv` 和类似目录。默认情况下，7 天内的项目会被选中。

```bash
mo purge                  # 交互式多选
mo purge --dry-run        # 预览
mo purge --paths          # 配置自定义扫描目录
```

**配置自定义扫描路径** (`~/.config/mole/purge_paths`)：
```
~/Documents/MyProjects
~/Work/ClientA
~/Work/ClientB
```

当此文件存在时，Mole 仅使用这些路径。否则默认为 `~/Projects`、`~/GitHub`、`~/dev`。

> 安装 `fd` 以加快扫描：`brew install fd`

### `mo installer` — 安装器文件清理

```bash
mo installer              # 在下载、桌面、Homebrew 缓存、iCloud、邮件中查找 .dmg/.pkg 文件
mo installer --dry-run    # 预览删除操作
```

## 配置文件

所有配置都位于 `~/.config/mole/`：

| 文件 | 目的 |
|------|---------|
| `purge_paths` | `mo purge` 的自定义扫描目录 |
| `operations.log` | 所有文件操作的日志 |

**禁用操作日志：**
```bash
export MO_NO_OPLOG=1
mo clean
```

## Shell 标签补全

```bash
mo completion             # 交互式设置 bash/zsh/fish
```

## Touch ID 用于 sudo

```bash
mo touchid                # 启用 Touch ID 身份验证以用于 sudo 命令
mo touchid enable --dry-run
```

## 脚本与自动化模式

### 在脚本中检查磁盘健康

```bash
#!/bin/bash
health=$(mo status --json | jq -r '.health_score')
if [ "$health" -lt 70 ]; then
  echo "健康评分低：$health — 运行清理"
  mo clean --dry-run  # 准备好时替换为 `mo clean`
fi
```

### 获取最大目录作为 JSON 并使用 jq 处理

```bash
mo analyze --json ~/Downloads | jq '.entries | sort_by(-.size) | .[0:5] | .[] | {name, size_gb: (.size / 1073741824 | . * 100 | round / 100)}'
```

### 在 CI 拆卸时自动清理项目

```bash
#!/bin/bash
# 非交互式清理构建文件后 CI
MO_NO_OPLOG=1 mo purge --dry-run   # 脚本中始终首先预览
```

### Raycast / Alfred 快速启动器

```bash
curl -fsSL https://raw.githubusercontent.com/tw93/mole/main/install.sh | bash
# 然后在 Raycast 中将 `mo clean`、`mo status`、`mo analyze` 绑定为脚本命令
```

## 安全边界

- `mo analyze` 通过 Finder 将文件移至废纸篓（可恢复），而不是直接删除 — 临时清理时优先使用它
- `clean`、`uninstall`、`purge`、`installer` 和 `remove` 是**永久破坏性**的 — 始终先 `--dry-run`
- Mole 验证路径并执行受保护目录规则；它会跳过或拒绝高风险操作
- 操作日志：`~/.config/mole/operations.log` — 使用 `MO_NO_OPLOG=1` 禁用
- 使用前请查看 [SECURITY.md](https://github.com/tw93/Mole/blob/main/SECURITY.md) 和 [SECURITY_AUDIT.md](https://github.com/tw93/Mole/blob/main/SECURITY_AUDIT.md) 在自动化管道中使用

## 故障排除

| 问题 | 解决方案 |
|---------|----------|
| `mo: command not found` | 运行 `brew install mole` 或重新运行安装脚本；检查 `$PATH` |
| 清理扫描缓慢 | 安装 `fd`：`brew install fd` |
| 外部驱动器未在 analyze 中显示 | 明确运行 `mo analyze /Volumes` |
| 想要保护缓存不被清理 | 运行 `mo clean --whitelist` 添加它 |
| 需要排除优化步骤 | 运行 `mo optimize --whitelist` |
| 脚本获取交互式提示 | 使用 `--dry-run` 标志；检查 `MO_NO_OPLOG=1` 环境变量 |
| 夜间更新不工作 | 夜间更新 (`--nightly`) 仅适用于脚本安装，不适用于 Homebrew |

## 更新与删除

```bash
mo update                 # 更新到最新稳定版
mo update --nightly       # 更新到最新主分支（仅脚本安装）
mo remove                 # 完全卸载 Mole
mo remove --dry-run       # 预览删除操作
```
