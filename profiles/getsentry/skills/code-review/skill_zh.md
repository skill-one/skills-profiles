# Sentry 代码审查

在审查 Sentry 项目的代码时，请遵循以下指南。

## 审查清单

### 识别问题

在代码变更中查找以下问题：

- **运行时错误**：潜在的异常、空指针问题、越界访问
- **性能**：无界的 O(n²) 操作、N+1 查询、不必要的分配
- **副作用**：影响其他组件的意外行为变化
- **向后兼容性**：没有迁移路径的破坏 API 变更
- **ORM 查询**：具有意外查询性能的复杂 Django ORM
- **安全漏洞**：注入、XSS、访问控制漏洞、密钥暴露

### 设计评估

- 组件交互是否合乎逻辑？
- 变更是否与现有项目架构一致？
- 是否与当前需求或目标存在冲突？

### 测试覆盖率

每个 PR 都应有适当的测试覆盖率：

- 业务逻辑的功能测试
- 组件交互的集成测试
- 关键用户路径的端到端测试

验证测试是否覆盖实际需求和边缘情况。避免在测试代码中过度分支或循环。

### 长期影响

当变更涉及以下内容时，标记为高级工程师审查：

- 数据库模式修改
- API 合约变更
- 新框架或库的采用
- 性能关键代码路径
- 安全敏感功能

## 反馈指南

### 语气

- 保持礼貌和同理心
- 提供可操作的建议，而非模糊的批评
- 不确定时，用疑问句表达："您考虑过...吗？"

### 批准

- 仅剩轻微问题时批准
- 不要因样式偏好阻止 PR
- 记住：目标是降低风险，而非完美代码

## 需要标记的常见模式

### Python/Django

```python
# 不好：N+1 查询
for user in users:
    print(user.profile.name)  # 每个用户单独查询

# 好：预取关联
users = User.objects.prefetch_related('profile')
```

### TypeScript/React

```typescript
// 不好：useEffect 缺少依赖
useEffect(() => {
  fetchData(userId);
}, []);  // userId 未包含在依赖中

// 好：包含所有依赖
useEffect(() => {
  fetchData(userId);
}, [userId]);
```

### 安全

```python
# 不好：SQL 注入风险
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# 好：参数化查询
cursor.execute("SELECT * FROM users WHERE id = %s", [user_id])
```

## 参考

- [Sentry 代码审查指南](https://develop.sentry.dev/engineering-practices/code-review/)
