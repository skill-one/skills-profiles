---
name: code-review-quality
description: 进行以场景为基础的代码审查，重点关注质量、可测试性和可维护性。在审查代码、提供反馈或建立审查实践时使用。
---

# 代码审查质量

<default_to_action>
当审查代码或建立审查实践时：
1. 优先考虑反馈：🔴 阻塞（必须修复）→ 🟡 主要 → 🟢 次要 → 💡 建议
2. 关注：错误、安全性、可测试性、可维护性（而非样式偏好）
3. 提问优于命令： "你考虑过...吗？" > "将此更改为..."
4. 提供上下文：为什么这很重要，而不仅仅是说明要更改什么
5. 限制范围：每次审查少于400行代码以提高效率

**快速审查清单：**
- 逻辑：是否正确工作？是否处理了边界情况？
- 安全性：输入验证？身份验证检查？注入风险？
- 可测试性：能否测试？是否已测试？
- 可维护性：命名清晰？单一职责？DRY原则？
- 性能：O(n²)循环？N+1查询？内存泄漏？

**关键成功因素：**
- 审查代码，而非针对个人
- 捕获错误 > 纠正风格问题
- 快速反馈（< 24小时）> 彻底反馈
</default_to_action>

## 快速参考卡

### 使用场景
- PR代码审查
- 配对编程反馈
- 建立团队审查标准
- 开发人员指导

### 反馈优先级级别
| 级别 | 图标 | 含义 | 行动 |
|------|------|------|------|
| 阻塞 | 🔴 | 错误/安全性/崩溃 | 在合并前必须修复 |
| 主要 | 🟡 | 逻辑问题/测试缺口 | 在合并前应该修复 |
| 次要 | 🟢 | 样式/命名 | 值得修复 |
| 建议 | 💡 | 替代方法 | 考虑用于未来 |

### 审查范围限制
| 修改行数 | 建议 |
|----------|------|
| < 200 | 单次审查会话 |
| 200-400 | 分块审查 |
| > 400 | 申请拆分PR |

### 关注重点
| ✅ 审查 | ❌ 跳过 |
|--------|------|
| 逻辑正确性 | 格式化（使用linter） |
| 安全风险 | 命名偏好 |
| 测试覆盖率 | 架构争论 |
| 性能问题 | 样式观点 |
| 错误处理 | 琐碎的更改 |

---

## 反馈模板

### 阻塞（必须修复）
```markdown
🔴 **阻塞：SQL注入风险**

此查询容易受到SQL注入攻击：
```javascript
db.query(`SELECT * FROM users WHERE id = ${userId}`)
```

**修复：** 使用参数化查询：
```javascript
db.query('SELECT * FROM users WHERE id = ?', [userId])
```

**原因：** 用户输入直接在SQL中允许攻击者执行任意查询。
```

### 主要（应该修复）
```markdown
🟡 **主要：缺少错误处理**

如果`fetchUser()`抛出异常怎么办？错误未处理就冒泡。

**建议：** 添加try/catch并提供适当的错误响应：
```javascript
try {
  const user = await fetchUser(id);
  return user;
} catch (error) {
  logger.error('获取用户失败', { id, error });
  throw new NotFoundError('用户不存在');
}
```
```

### 次要（值得修复）
```markdown
🟢 **次要：变量名可以更清晰**

`d`没有传达意义。考虑使用`daysSinceLastLogin`。
```

### 建议（考虑）
```markdown
💡 **建议：考虑提取此逻辑为辅助函数**

此验证逻辑出现在3处。一个`validateEmail()`辅助函数可以减少重复。不阻塞，但可能值得后续的PR。
```

---

## 审查时需要询问的问题

### 逻辑
- 当X为null/空/负数时会发生什么？
- 这里是否存在竞态条件？
- 如果API调用失败会怎样？

### 安全性
- 用户输入是否经过验证/清理？
- 是否有身份验证检查？
- 是否暴露了密钥或PII？

### 可测试性
- 你会如何测试这个？
- 依赖项是否可注入？
- 是否有针对快乐路径的测试？边界情况？

### 可维护性
- 下一个开发者能否理解这段代码？
- 是否做了太多事情？
- 是否有我们可以减少的重复？

## 最小发现要求
审查必须达到3.0的加权发现分数（阻塞=3，高=2，中=1，低=0.5，信息=0.25）。如果初始审查未达标，运行`qe-devils-advocate`代理作为元审查者以发现更多观察结果。每次审查至少应有3条可操作的观察结果。

---

## 代理辅助审查

```typescript
// 全面代码审查
await Task("代码审查", {
  prNumber: 123,
  checks: ['security', '性能', '可测试性', '可维护性'],
  feedbackLevels: ['blocker', 'major', 'minor'],
  autoApprove: { maxBlockers: 0, maxMajor: 2 }
}, "qe-quality-analyzer");

// 安全性审查
await Task("安全审查", {
  prFiles: changedFiles,
  scanTypes: ['injection', 'auth', 'secrets', 'dependencies']
}, "qe-security-scanner");

// 测试覆盖率审查
await Task("覆盖率审查", {
  prNumber: 123,
  requireNewTests: true,
  minCoverageDelta: 0
}, "qe-coverage-analyzer");
```

---

## 代理协调提示

### 内存命名空间
```
aqe/code-review/
├── review-history/*     - 过去的审查决策
├── patterns/*           - 团队/仓库的常见问题
├── feedback-templates/* - 可重用反馈
└── metrics/*            - 审查周转时间
```

### 队伍协调
```typescript
const reviewFleet = await FleetManager.coordinate({
  strategy: 'code-review',
  agents: [
    'qe-quality-analyzer',    // 逻辑、可维护性
    'qe-security-scanner',    // 安全风险
    'qe-performance-tester',  // 性能问题
    'qe-coverage-analyzer'    // 测试覆盖率
  ],
  topology: 'parallel'
});
```

---

## 审查礼仪

| ✅ 做 | ❌ 不要 |
|------|------|
| "你考虑过...吗？" | "这是错误的" |
| 解释为什么这很重要 | 只说"修复这个" |
| 认可好的代码 | 只指出负面问题 |
| 建议，而非命令 | 不可怜悯 |
| 审查少于400行 | 一次性审查2000行 |

---

## 相关技能
- [agentic-quality-engineering](../agentic-quality-engineering/) - 代理协调
- [security-testing](../security-testing/) - 安全审查深度
- [refactoring-patterns](../refactoring-patterns/) - 可维护性模式

---

## 记住

**优先考虑反馈：** 🔴 阻塞 → 🟡 主要 → 🟢 次要 → 💡 建议。关注错误和安全性，而非样式。提问，而非命令。每次审查少于400行。快速反馈（< 24小时）胜过彻底反馈。

**使用代理：** 代理自动化安全、性能和覆盖率检查，让人类审查者专注于逻辑和设计。使用代理进行一致、快速的初始审查。

## 技能组合

- **安全关注** → 与`/security-testing`组合进行安全审查
- **覆盖率检查** → 对更改文件运行`/qe-coverage-analysis`
- **发布决策** → 将审查结果输入`/qe-quality-assessment`

## 注意事项

- 代理一次性审查超过400行并遗漏问题 — 最多分块审查200-400行
- 纠正样式时遗漏逻辑错误是代理审查的第一大失败 — 优先考虑正确性而非格式化
- 代理批准了编译但存在微妙竞态条件的代码 — 始终检查共享状态和异步模式
- 没有建议修复的审查评论是无用的 — 始终包含建议的替代方案
- 代理不检查PR是否实际解决了关联问题 — 验证实际问题是已修复
