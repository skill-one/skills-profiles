# 在 Magento 环境中执行 Shell 命令

此实用技能检测 Magento 开发环境，并提供适当的命令包装器以执行 Shell 命令。

## 使用方法

其他技能在需要执行 Magento 环境中的命令时应引用此技能。检测到的包装器确保命令在正确的上下文中运行（容器或本地）。

## 第 1 步：检测环境

**重要提示：** 请从 Magento 项目根目录执行此脚本，或作为参数提供路径。

在任何需要执行 Shell 命令的技能开始时运行一次此检测：

```bash
<skill_path>/scripts/detect_env.sh [magento_root_path]
```

其中 `<skill_path>` 是包含此 SKILL.md 文件的目录（例如：`.claude/skills/hyva-exec-shell-cmd`）。

可选的 `magento_root_path` 参数指定 Magento 安装目录。如果省略，脚本将使用当前工作目录。

输出：`warden`、`docker-magento`、`ddev` 或 `local`

## 第 2 步：应用命令包装器

根据检测到的环境，按如下方式包装命令：

| 环境       | 命令包装器                                     | 描述                               |
|------------|-----------------------------------------------|-----------------------------------|
| Warden    | `warden env exec -T php-fpm bash -c "<command>"` | 由 Warden 管理的 Docker 环境     |
| docker-magento | `bin/clinotty bash -c "<command>"`            | Mark Shust 的 docker-magento 设置 |
| DDEV      | `ddev exec <command>`                         | DDEV 容器化环境                   |
| 本地      | 直接运行 `<command>`                          | 无容器的原生环境                 |

## 示例

### 单个命令

```bash
# Warden
warden env exec -T php-fpm bash -c "bin/magento cache:clean"

# docker-magento
bin/clinotty bash -c "bin/magento cache:clean"

# DDEV
ddev exec bin/magento cache:clean

# 本地
bin/magento cache:clean
```

### 带目录切换的命令

```bash
# Warden
warden env exec -T php-fpm bash -c "cd vendor/hyva-themes/magento2-default-theme/web/tailwind && npm run build"

# docker-magento
bin/clinotty bash -c "cd vendor/hyva-themes/magento2-default-theme/web/tailwind && npm run build"

# DDEV
ddev exec bash -c "vendor/hyva-themes/magento2-default-theme/web/tailwind && npm run build"

# 本地
cd vendor/hyva-themes/magento2-default-theme/web/tailwind && npm run build
```

## 不需要包装的命令

某些命令在主机系统上运行，不应进行包装：

- `composer` 命令（在主机上运行，而非容器内）
- `git` 命令
- 主机文件系统上的文件操作（`ls`、`find`、`cp` 用于主机可访问的文件）
- `warden` CLI 命令
- `ddev` CLI 命令

## 集成模式

需要执行命令的技能应：

1. 引用此技能："使用 `hyva-exec-shell-cmd` 技能确定命令包装器"
2. 使用第 1 步检测环境
3. 在整个技能中存储包装器模式
4. 按第 2 步应用包装器到所有容器命令

## 在环境中运行捆绑技能脚本

某些技能附带一个辅助脚本（例如 `scripts/` 下的 PHP 脚本），必须通过 PHP/Node 解释器运行。在加固的主机上没有本地解释器，且安装在用户级别的技能（`~/.../skills/...`）不在项目中，因此容器无法访问它。**不要**将脚本复制到项目树中：文件如何到达容器因环境而异（绑定挂载、Mutagen、命名卷），某些路径根本不同步（例如 Warden 从单独的卷提供 `var/`、`generated/`、`pub/static`、`pub/media`，因此主机写入的文件永远不会出现在容器中）。

相反，**通过标准输入流将脚本传输到解释器**——这独立于挂载/同步策略，无需临时文件，也无需清理：

1. 检测环境（第 1 步）并解析包装器（第 2 步）。
2. **容器化环境**——通过包装器将脚本管道到 `php /dev/stdin`（使用非 TTY `-T` exec 以转发标准输入）。`<skill_path>` 是包含调用技能的 SKILL.md 的目录：

   ```bash
   # Warden
   cat "<skill_path>/scripts/<script>.php" | warden env exec -T php-fpm bash -c "php /dev/stdin [args]"

   # docker-magento
   cat "<skill_path>/scripts/<script>.php" | bin/clinotty bash -c "php /dev/stdin [args]"

   # DDEV
   cat "<skill_path>/scripts/<script>.php" | ddev exec bash -c "php /dev/stdin [args]"
   ```

   脚本以容器的当前工作目录为项目根目录运行，因此使用 `getcwd()` 定位项目文件的脚本可以保持不变。捕获标准输出以获取结果。

   **此方法的脚本约束：** 脚本不能从标准输入读取（标准输入包含脚本本身），且不能依赖 `__FILE__`/`__DIR__`（它是 `/dev/stdin`）——改用 `getcwd()` 定位项目文件。
3. **本地环境**：主机没有解释器（在加固过程中移除）。不要尝试直接运行脚本——报告需要容器化开发环境（或本地解释器）才能执行此步骤。

<!-- 版权所有 © Hyvä Themes https://hyva.io。保留所有权利。根据 OSL 3.0 许可。 -->
