# 调试策略

通过成熟的策略、强大的工具和系统性的方法，将调试从令人沮丧的猜测工作转变为系统性的问题解决。

## 何时使用这项技能

- 追踪难以捉摸的 Bug
- 调查性能问题
- 理解不熟悉的代码库
- 调试生产环境问题
- 分析崩溃转储和堆栈跟踪
- 分析应用程序性能
- 调查内存泄漏
- 调试分布式系统

## 核心原则

### 1. 科学方法

**1. 观察**：实际行为是什么？
**2. 假设**：可能是什么原因导致的？
**3. 实验**：验证你的假设
**4. 分析**：实验结果是否证明/证伪了你的理论？
**5. 重复**：直到找到根本原因

### 2. 调试心态

**不要假设**：

- "不可能是 X" - 实际上可能是
- "我没有修改 Y" - 无论如何检查
- "在我的机器上可以工作" - 找出原因

**要**：

- 保持一致地复现
- 隔离问题
- 记录详细笔记
- 质疑一切
- 卡住时休息一下

### 3. 兔子鸭调试法

大声解释你的代码和问题（对一只兔子鸭、同事或你自己）。通常能揭示问题所在。

## 系统性调试流程

### 第一阶段：复现

```markdown
## 复现检查清单

1. **你能复现它吗？**
   - 总是？有时？随机？
   - 需要特定条件吗？
   - 他人能复现吗？

2. **创建最小复现案例**
   - 简化为最小示例
   - 移除无关代码
   - 隔离问题

3. **记录步骤**
   - 记录精确步骤
   - 记录环境细节
   - 捕获错误信息
```

### 第二阶段：收集信息

```markdown
## 信息收集

1. **错误信息**
   - 完整堆栈跟踪
   - 错误代码
   - 控制台/日志输出

2. **环境**
   - 操作系统版本
   - 语言/运行时版本
   - 依赖版本
   - 环境变量

3. **最近变更**
   - Git 历史记录
   - 部署时间线
   - 配置变更

4. **范围**
   - 影响所有用户还是特定用户？
   - 所有浏览器还是特定浏览器？
   - 仅生产环境还是开发环境？
```

### 第三阶段：形成假设

```markdown
## 假设形成

根据收集的信息，询问：

1. **发生了什么变化？**
   - 最近代码变更
   - 依赖更新
   - 基础设施变更

2. **有什么不同？**
   - 正常环境与异常环境
   - 正常用户与异常用户
   - 变更前与变更后

3. **可能在哪里失败？**
   - 输入验证
   - 业务逻辑
   - 数据层
   - 外部服务
```

### 第四阶段：测试与验证

```markdown
## 测试策略

1. **二分法**
   - 注释掉一半代码
   - 缩小问题范围
   - 重复直到找到

2. **添加日志**
   - 战略性 console.log/print
   - 跟踪变量值
   - 追踪执行流程

3. **隔离组件**
   - 分别测试每个部分
   - 模拟依赖
   - 移除复杂性

4. **对比正常与异常**
   - 比较配置
   - 比较环境
   - 比较数据
```

## 调试工具

### JavaScript/TypeScript 调试

```typescript
// Chrome DevTools Debugger
function processOrder(order: Order) {
  debugger; // 执行在这里暂停

  const total = calculateTotal(order);
  console.log("Total:", total);

  // 条件断点
  if (order.items.length > 10) {
    debugger; // 只有在条件为真时才断点
  }

  return total;
}

// 控制台调试技巧
console.log("Value:", value); // 基本用法
console.table(arrayOfObjects); // 表格格式
console.time("operation");
/* code */ console.timeEnd("operation"); // 计时
console.trace(); // 堆栈跟踪
console.assert(value > 0, "Value must be positive"); // 断言

// 性能分析
performance.mark("start-operation");
// ... 操作代码
performance.mark("end-operation");
performance.measure("operation", "start-operation", "end-operation");
console.log(performance.getEntriesByType("measure"));
```

**VS Code 调试配置：**

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Debug Program",
      "program": "${workspaceFolder}/src/index.ts",
      "preLaunchTask": "tsc: build - tsconfig.json",
      "outFiles": ["${workspaceFolder}/dist/**/*.js"],
      "skipFiles": ["<node_internals>/**"]
    },
    {
      "type": "node",
      "request": "launch",
      "name": "Debug Tests",
      "program": "${workspaceFolder}/node_modules/jest/bin/jest",
      "args": ["--runInBand", "--no-cache"],
      "console": "integratedTerminal"
    }
  ]
}
```

### Python 调试

```python
# 内置调试器 (pdb)
import pdb

def calculate_total(items):
    total = 0
    pdb.set_trace()  # 调试器从这里开始

    for item in items:
        total += item.price * item.quantity

    return total

# 断点 (Python 3.7+)
def process_order(order):
    breakpoint()  # 比 pdb.set_trace() 更方便
    # ... 代码

# 死后调试
try:
    risky_operation()
except Exception:
    import pdb
    pdb.post_mortem()  # 在异常点调试

# IPython 调试 (ipdb)
from ipdb import set_trace
set_trace()  # 比 pdb 更好的界面

# 调试用日志
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def fetch_user(user_id):
    logger.debug(f'Fetching user: {user_id}')
    user = db.query(User).get(user_id)
    logger.debug(f'Found user: {user}')
    return user

# 性能分析
import cProfile
import pstats

cProfile.run('slow_function()', 'profile_stats')
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative')
stats.print_stats(10)  # 最慢的 10 个
```

### Go 调试

```go
// Delve 调试器
// 安装: go install github.com/go-delve/delve/cmd/dlv@latest
// 运行: dlv debug main.go

import (
    "fmt"
    "runtime"
    "runtime/debug"
)

// 打印堆栈跟踪
func debugStack() {
    debug.PrintStack()
}

// 带调试的恐慌恢复
func processRequest() {
    defer func() {
        if r := recover(); r != nil {
            fmt.Println("Panic:", r)
            debug.PrintStack()
        }
    }()

    // ... 可能会恐慌的代码
}

// 内存分析
import _ "net/http/pprof"
// 访问 http://localhost:6060/debug/pprof/

// CPU 分析
import (
    "os"
    "runtime/pprof"
)

f, _ := os.Create("cpu.prof")
pprof.StartCPUProfile(f)
defer pprof.StopCPUProfile()
// ... 要分析的代码
```

## 高级调试技巧

### 技巧 1：二分法调试

```bash
# Git bisect 用于查找回归
git bisect start
git bisect bad                    # 当前提交有误
git bisect good v1.0.0            # v1.0.0 是正常的

# Git 检查中间提交
# 测试后：
git bisect good   # 如果工作正常
git bisect bad    # 如果仍然有误

# 继续直到找到 Bug
git bisect reset  # 完成时
```

### 技巧 2：差异调试

对比正常与异常：

```markdown
## 有什么不同？

| 方面       | 正常     | 异常         |
| ---------- | -------- | ------------ |
| 环境       | 开发环境 | 生产环境     |
| Node 版本 | 18.16.0  | 18.15.0      |
| 数据       | 空数据库 | 100 万条记录 |
| 用户       | 管理员   | 普通用户     |
| 浏览器     | Chrome   | Safari       |
| 时间       | 白天     | 午夜之后     |

假设：基于时间的问题？检查时区处理。
```

### 技巧 3：跟踪调试

```typescript
// 函数调用跟踪
function trace(
  target: any,
  propertyKey: string,
  descriptor: PropertyDescriptor,
) {
  const originalMethod = descriptor.value;

  descriptor.value = function (...args: any[]) {
    console.log(`调用 ${propertyKey} 使用参数:`, args);
    const result = originalMethod.apply(this, args);
    console.log(`${propertyKey} 返回:`, result);
    return result;
  };

  return descriptor;
}

class OrderService {
  @trace
  calculateTotal(items: Item[]): number {
    return items.reduce((sum, item) => sum + item.price, 0);
  }
}
```

### 技巧 4：内存泄漏检测

```typescript
// Chrome DevTools 内存分析器
// 1. 拍摄堆快照
// 2. 执行操作
// 3. 拍摄另一个快照
// 4. 比较快照

// Node.js 内存调试
if (process.memoryUsage().heapUsed > 500 * 1024 * 1024) {
  console.warn("高内存使用:", process.memoryUsage());

  // 生成堆转储
  require("v8").writeHeapSnapshot();
}

// 测试中的内存泄漏
let beforeMemory: number;

beforeEach(() => {
  beforeMemory = process.memoryUsage().heapUsed;
});

afterEach(() => {
  const afterMemory = process.memoryUsage().heapUsed;
  const diff = afterMemory - beforeMemory;

  if (diff > 10 * 1024 * 1024) {
    // 10MB 阈值
    console.warn(`可能的内存泄漏: ${diff / 1024 / 1024}MB`);
  }
});
```

## 按问题类型划分的调试模式

### 模式 1：间歇性 Bug

```markdown
## 不稳定 Bug 的策略

1. **添加大量日志**
   - 记录时间信息
   - 记录所有状态转换
   - 记录外部交互

2. **查找竞态条件**
   - 对共享状态的并发访问
   - 异步操作顺序错误
   - 缺少同步

3. **检查时间依赖**
   - setTimeout/setInterval
   - Promise 解决顺序
   - 动画帧时间

4. **压力测试**
   - 多次运行
   - 改变时间
   - 模拟负载
```

### 模式 2：性能问题

```markdown
## 性能调试

1. **先分析**
   - 不要盲目优化
   - 优化前后测量
   - 找到瓶颈

2. **常见原因**
   - N+1 查询
   - 不必要的重新渲染
   - 大数据处理
   - 同步 I/O

3. **工具**
   - 浏览器 DevTools 性能标签
   - Lighthouse
   - Python: cProfile, line_profiler
   - Node: clinic.js, 0x
```

### 模式 3：生产环境 Bug

```markdown
## 生产环境调试

1. **收集证据**
   - 错误跟踪 (Sentry, Bugsnag)
   - 应用程序日志
   - 用户报告
   - 指标/监控

2. **本地复现**
   - 使用生产数据（匿名化）
   - 匹配环境
   - 按照精确步骤

3. **安全调查**
   - 不要修改生产环境
   - 使用功能标志
   - 添加监控/日志
   - 在测试环境测试修复
```

## 最佳实践

1. **先复现**：不能修复无法复现的问题
2. **隔离问题**：移除复杂性直到最小案例
3. **阅读错误信息**：它们通常很有帮助
4. **检查最近变更**：大多数 Bug 都是最近引入的
5. **使用版本控制**：Git bisect, blame, 历史记录
6. **休息一下**：新鲜的眼睛看得更清楚
7. **记录发现**：帮助未来的自己
8. **修复根本原因**：不只是症状

## 常见调试错误

- **同时进行多个修改**：一次只改一件事
- **不阅读错误信息**：阅读完整堆栈跟踪
- **假设问题复杂**：通常很简单
- **生产环境调试日志**：发布前移除
- **不使用调试器**：console.log 不总是最佳选择
- **过早放弃**：坚持就是胜利
- **不测试修复**：验证它是否真的工作

## 快速调试检查清单

```markdown
## 卡住时检查：

- [ ] 拼写错误（变量名中的拼写错误）
- [ ] 大小写敏感（fileName vs filename）
- [ ] null/undefined 值
- [ ] 数组索引偏移一位
- [ ] 异步时间（竞态条件）
- [ ] 作用域问题（闭包、提升）
- [ ] 类型不匹配
- [ ] 缺少依赖
- [ ] 环境变量
- [ ] 文件路径（绝对 vs 相对）
- [ ] 缓存问题（清除缓存）
- [ ] 过期数据（刷新数据库）
```
