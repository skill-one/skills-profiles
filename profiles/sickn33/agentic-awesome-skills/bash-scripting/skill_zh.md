# Bash 脚本工作流

## 概述

创建健壮、生产就绪的 bash 脚本的专业工作流，包含防御性编程模式、全面的错误处理和自动化测试。

## 何时使用此工作流

当您需要：
- 创建自动化脚本
- 编写系统管理工具
- 构建部署脚本
- 开发备份解决方案
- 创建 CI/CD 脚本

时使用此工作流。

## 工作流阶段

### 阶段 1：脚本设计

#### 需要调用的技能
- `bash-pro` - 专业脚本
- `bash-defensive-patterns` - 防御性模式

#### 操作步骤
1. 定义脚本目的
2. 确定输入/输出
3. 规划错误处理
4. 设计日志记录策略
5. 记录需求

#### 复制粘贴提示
```
使用 @bash-pro 设计生产就绪的 bash 脚本
```

### 阶段 2：脚本结构

#### 需要调用的技能
- `bash-pro` - 脚本结构
- `bash-defensive-patterns` - 安全模式

#### 操作步骤
1. 添加 shebang 和严格模式
2. 创建使用函数
3. 实现参数解析
4. 设置日志记录
5. 添加清理处理程序

#### 复制粘贴提示
```
使用 @bash-defensive-patterns 实现严格模式和错误处理
```

### 阶段 3：核心实现

#### 需要调用的技能
- `bash-linux` - Linux 命令
- `linux-shell-scripting` - Shell 脚本

#### 操作步骤
1. 实现主函数
2. 添加输入验证
3. 创建辅助函数
4. 处理边缘情况
5. 添加进度指示器

#### 复制粘贴提示
```
使用 @bash-linux 实现系统命令
```

### 阶段 4：错误处理

#### 需要调用的技能
- `bash-defensive-patterns` - 错误处理
- `error-handling-patterns` - 错误模式

#### 操作步骤
1. 添加 trap 处理程序
2. 实现重试逻辑
3. 创建错误消息
4. 设置退出代码
5. 添加回滚功能

#### 复制粘贴提示
```
使用 @bash-defensive-patterns 添加全面的错误处理
```

### 阶段 5：日志记录

#### 需要调用的技能
- `bash-pro` - 日志模式

#### 操作步骤
1. 创建日志记录函数
2. 添加日志级别
3. 实现时间戳
4. 配置日志轮转
5. 添加调试模式

#### 复制粘贴提示
```
使用 @bash-pro 实现结构化日志记录
```

### 阶段 6：测试

#### 需要调用的技能
- `bats-testing-patterns` - Bats 测试
- `shellcheck-configuration` - ShellCheck

#### 操作步骤
1. 编写 Bats 测试
2. 运行 ShellCheck
3. 测试边缘情况
4. 验证错误处理
5. 使用不同输入进行测试

#### 复制粘贴提示
```
使用 @bats-testing-patterns 编写脚本测试
```

```
使用 @shellcheck-configuration 语法检查 bash 脚本
```

### 阶段 7：文档

#### 需要调用的技能
- `documentation-templates` - 文档

#### 操作步骤
1. 添加脚本头部
2. 记录函数
3. 创建使用示例
4. 列出依赖项
5. 添加故障排除部分

#### 复制粘贴提示
```
使用 @documentation-templates 记录 bash 脚本
```

## 脚本模板

```bash
#!/usr/bin/env bash
set -euo pipefail

readonly SCRIPT_NAME=$(basename "$0")
readonly SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"; }
error() { log "ERROR: $*" >&2; exit 1; }

usage() { cat <<EOF
用法: $SCRIPT_NAME [选项]
选项:
    -h, --help      显示帮助
    -v, --verbose   详细输出
EOF
}

main() {
    log "脚本开始"
    # 实现
    log "脚本完成"
}

main "$@"
```

## 质量门禁

- [ ] ShellCheck 通过
- [ ] Bats 测试通过
- [ ] 错误处理正常
- [ ] 日志功能正常
- [ ] 文档完整

## 相关工作流包

- `os-scripting` - 操作系统脚本
- `linux-troubleshooting` - Linux 故障排除
- `cloud-devops` - DevOps 自动化

## 限制
- 仅在任务明确匹配上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家评审的替代品。
- 如果缺少必要的输入、权限、安全边界或成功标准，请停止并请求澄清。
