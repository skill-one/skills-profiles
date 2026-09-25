# 代码清理

## 概述

执行代码审查后的美化清理，使代码达到生产标准。此工作流现集成于 `/developer-kit-specs:specs.task-implementation` 的 T-7 阶段。也可以使用 `--action=cleanup` 手动调用。

**输入**: `docs/specs/[id]/tasks/TASK-XXX.md` (已审查状态)  
**输出**: 清理后的代码，任务标记为 `completed`

## 使用场景

- 在审查批准后，根据要求清理代码、润色、最终确定、整理或删除技术债务时使用。
- 用于准备代码完成：移除调试日志、死代码、优化导入并提高可读性。
- 作为规范驱动开发工作流中的最终质量关卡。
- 不用于重构逻辑或修复错误——仅专注于美化和卫生清理。

## 参数

| 参数 | 是否必需 | 描述 |
|------|----------|-------|
| `--lang` | 否 | `java`, `spring`, `typescript`, `nestjs`, `react`, `python`, `general` |
| `--task` | 是 | 任务文件路径 |
| `--action`| 否 | 设置为 `cleanup` 以手动调用 |

## 最佳实践

- **清理而非修改**: 仅移除或重新组织——绝不改变功能
- **保持行为**: 清理后代码必须完全按原样运行
- **使用项目工具**: 优先使用 `./mvnw spotless:apply`, `npm run lint:fix`, `black` 等
- **使用 TodoWrite**: 通过所有 8 个阶段跟踪进度
- **失败即停止**: 如果测试失败，停止并报告——不要继续

参考 `references/language-patterns.md` 获取特定语言的格式化命令、导入排序和 grep 模式。

## 操作说明

### 阶段 1：任务验证

1. 解析 `$ARGUMENTS` 获取参数:
   - `--lang` (可选): 目标语言/框架
   - `--task` (必需): 任务 ID 或文件路径
   - `--spec` (可选): 规范文件夹路径（与任务 ID 一起使用)
   
   **支持两种格式**:
   - 格式 1 (直接路径): `--task=docs/specs/001-feature/tasks/TASK-001.md`
   - 格式 2 (规范+任务): `--spec=docs/specs/001-feature --task=TASK-001`
   
   如果使用格式 2，构建任务文件路径为: `{spec}/tasks/{task}.md`

2. 读取任务文件。验证:
   - 状态为 `reviewed` 或 `implemented` (非 `completed`)
   - 审查报告 `TASK-XXX--review.md` 存在且已批准
   
3. 如果未审查 → 停止并提示用户先运行 `/developer-kit-specs:specs.task-review`
4. 提取任务 ID、标题和 `provides` 文件

### 阶段 2：识别待清理文件

1. 读取 `TASK-XXX--review.md` 获取创建/修改的文件
2. 读取任务 `provides` 字段获取文件路径
3. 验证文件存在；构建清理列表
4. 分类: 源文件、测试文件、配置文件

### 阶段 3：技术债务移除

使用 Grep 搜索文件中的临时/调试产物:
- `console.log`, `System.out.println`, `print(`, `// DEBUG:`, `// temp`, `// hack`
- 已解决的 `TODO`/`FIXME` 注释 (保留未解决的)

审查每个发现的上下文。移除确认的债务并记录已移除内容。

### 阶段 4：导入优化

1. 如果可用，运行特定语言的导入优化器（见参考资料）
2. 如果不存在工具，手动移除未使用的导入
3. 记录已修改文件

### 阶段 5：代码可读性改进

1. 如果可用，运行特定语言的格式化器（见参考资料）
2. 如果不存在格式化器: 修复缩进、拆分长行 (>120)、修复空格
3. 仅在明显安全的情况下移除死代码
4. 记录变更

### 阶段 6：文档验证

1. 验证类/文件头部和公共 API 文档
2. 检查剩余的 TODO 是否仍有效且包含上下文
3. 移除或更新过时的注释
4. 记录文档变更

### 阶段 7：最终验证

1. 如果可用，运行 linters
2. 如果可用，运行测试
3. 验证未引入逻辑或签名变更
4. 如果测试失败 → 停止并报告失败

### 阶段 8：任务完成

1. **自动更新任务状态**:
   - 在任务文件中添加 `## Cleanup Summary` 部分
   - 检查 DoD 部分中剩余的框
   - 钩子自动将状态更新为 `completed` 并设置 `completed_date` + `cleanup_date`
   
2. 将 `## Cleanup Summary` 追加到任务文件，包含:
   - 清理的文件
   - 修改内容
   - 验证清单 (linters, tests, 无功能变更)
3. 标记所有 todos 为完成

## 示例

### Spring Boot 清理

```bash
/developer-kit-specs:specs.task-implementation --lang=spring --task="docs/specs/001-user-auth/tasks/TASK-001.md" --action=cleanup
```

操作:
1. 验证 TASK-001 状态为 `reviewed`
2. 文件: `UserController.java`, `UserService.java`, `UserRepository.java`
3. 移除 5 个 `System.out.println` 和 2 个已解决的 TODO
4. 运行 `./mvnw spotless:apply`
5. 运行 `./mvnw test -q`
6. 标记任务 `completed`

### TypeScript 清理

```bash
/developer-kit-specs:specs.task-implementation --lang=typescript --task="docs/specs/002-dashboard/tasks/TASK-003.md" --action=cleanup
```

操作:
1. 验证 TASK-003 状态为 `reviewed`
2. 文件: `Dashboard.tsx`, `useDashboard.ts`, `Dashboard.test.tsx`
3. 移除 8 个 `console.log` 语句
4. 运行 `npm run lint:fix` 和 `npm run format`
5. 运行 `npm test`
6. 标记任务 `completed`

## 限制和警告

- 清理过程中绝不改变逻辑或签名
- 测试失败立即停止并报告
- 标记完成前验证行为未变更
