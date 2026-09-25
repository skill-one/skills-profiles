# 调试向导

专业的调试工具，采用系统化方法来定位和解决任何代码库中的问题。

## 核心工作流程

1. **复现** - 建立一致的复现步骤
2. **隔离** - 缩小到最小的失败案例
3. **假设和测试** - 形成可测试的理论，验证/证伪每个理论
4. **修复** - 实施并验证解决方案
5. **预防** - 添加测试/防护措施防止回归

## 参考指南

根据上下文加载详细指导：

<!-- 系统化调试行改编自 obra/superpowers by Jesse Vincent (@obra), MIT 许可证 -->

| 主题 | 参考 | 加载时机 |
|------|------|------|
| 调试工具 | `references/debugging-tools.md` | 通过语言设置调试器 |
| 常见模式 | `references/common-patterns.md` | 识别错误模式 |
| 策略 | `references/strategies.md` | 二分法、git bisect、时间旅行 |
| 快速修复 | `references/quick-fixes.md` | 常见错误解决方案 |
| 系统化调试 | `references/systematic-debugging.md` | 复杂错误、多次失败修复、根本原因分析 |

## 限制条件

### 必须做
- 首先复现问题
- 收集完整的错误消息和堆栈跟踪
- 一次测试一个假设
- 记录发现结果供将来参考
- 修复后添加回归测试
- 提交前移除所有调试代码

### 不必做
- 不经测试就猜测
- 同时进行多个更改
- 跳过复现步骤
- 假设你知道原因
- 没有防护措施在生产环境调试
- 代码中留下 console.log/debugger 语句

## 常见调试命令

**Python (pdb)**
```bash
python -m pdb script.py          # 启动调试器
# 在 pdb 中:
# b 42          — 在第 42 行设置断点
# n             — 跳过
# s             — 进入
# p some_var    — 打印变量
# bt            — 打印完整堆栈跟踪
```

**JavaScript (Node.js)**
```bash
node --inspect-brk script.js     # 在第一行暂停，连接 Chrome 开发者工具
# 在 Chrome 中: 打开 chrome://inspect → 点击 "inspect"
# 源代码面板: 添加断点、监视表达式、逐步调试
```

**Git bisect (回归查找)**
```bash
git bisect start
git bisect bad                   # 当前提交有错误
git bisect good v1.2.0           # 最后已知正常的标签/提交
# Git 检出中点 — 测试，然后:
git bisect good   # 或: git bisect bad
# 重复直到 git 识别出第一个有问题的提交
git bisect reset
```

**Go (delve)**
```bash
dlv debug ./cmd/server           # 构建并附加
# (dlv) break main.go:55
# (dlv) continue
# (dlv) print myVar
```

## 输出模板

调试时提供：
1. **根本原因**：具体是什么导致了问题
2. **证据**：证明它的堆栈跟踪、日志或测试
3. **修复**：解决它的代码更改
4. **预防**：防止再次发生的测试或防护措施

[文档](https://jeffallan.github.io/claude-skills/skills/quality/debugging-wizard/)
