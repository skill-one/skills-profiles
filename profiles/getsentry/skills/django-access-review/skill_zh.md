基于OWASP提示系列（CC BY-SA 4.0）
https://cheatsheetseries.owasp.org/

# Django访问控制与IDOR审查

通过调查代码库如何回答以下问题来查找访问控制漏洞：

**用户A能否访问、修改或删除用户B的数据？**

## 哲学：调查重于模式匹配

不要扫描预定义的漏洞模式。相反：

1. **理解**此代码库中的授权工作原理
2. **提出问题**关于特定数据流
3. **追踪代码**以找到（或是否存在）访问检查的位置
4. **报告**仅通过调查确认的内容

每个代码库都实现授权的方式不同。你的工作是理解此特定实现，然后找到差距。

---

## 第一阶段：理解授权模型

在寻找错误之前，回答关于代码库的以下问题：

### 授权如何强制执行？

研究代码库以找到：

```
□ 权限检查在哪里实现？
  - 装饰器？(@login_required, @permission_required, 自定义？
  - 中间件？(TenantMiddleware, AuthorizationMiddleware？
  - 基类？(BaseAPIView, TenantScopedViewSet？
  - 权限类？(DRF permission_classes？
  - 自定义混入？(OwnershipMixin, TenantMixin?)

□ 查询如何作用域化？
  - 自定义管理器？(TenantManager, UserScopedManager？
  - get_queryset()覆盖？
  - 设置查询上下文的中间件？

□ 所有权模型是什么？
  - 单个用户所有权？(document.owner_id)
  - 组织/租户所有权？(document.organization_id)
  - 分层？(org -> team -> user -> resource)
  - 在上下文中的基于角色的？(org管理员与成员)
```

### 调查命令

```bash
# 查找典型的授权方式
grep -rn "permission_classes\|@login_required\|@permission_required" --include="*.py" | head -20

# 查找视图继承的基础类
grep -rn "class Base.*View\|class.*Mixin.*:" --include="*.py" | head -20

# 查找自定义管理器
grep -rn "class.*Manager\|def get_queryset" --include="*.py" | head -20

# 查找模型上的所有权字段
grep -rn "owner\|user_id\|organization\|tenant" --include="models.py" | head -30
```

**在理解授权模型之前不要继续。**

---

## 第二阶段：映射攻击面

识别处理用户特定数据的端点：

### 存在哪些资源？

```
□ 哪些模型包含用户数据？
□ 哪些具有所有权字段（owner_id, user_id, organization_id）？
□ 哪些通过URL或请求体中的ID访问？
```

### 暴露了哪些操作？

对于每个资源，映射：
- 列表端点 - 返回什么数据？
- 详情/检索端点 - 如何获取对象？
- 创建端点 - 谁设置所有者？
- 更新端点 - 用户能否修改他人的数据？
- 删除端点 - 用户能否删除他人的数据？
- 自定义操作 - 它们访问什么？

---

## 第三阶段：提出问题并调查

对于每个处理用户数据的端点，提出：

### 核心问题

**"如果我是用户A并且知道用户B资源的ID，我能访问它吗？"**

通过追踪代码来回答这个问题：

```
1. 资源ID在哪里进入系统？
   - URL路径：/api/documents/{id}/
   - 查询参数：?document_id=123
   - 请求体：{"document_id": 123}

2. 哪里使用该ID来获取数据？
   - 查找ORM查询或数据库调用

3. 在（1）和（2）之间，存在哪些检查？
   - 查询是否作用域化到当前用户？
   - 是否有显式的所有权检查？
   - 对对象是否有权限检查？
   - 基类或混入是否强制执行访问？

4. 如果找不到检查，是否遗漏了检查？
   - 检查父类
   - 检查中间件
   - 检查管理器
   - 检查URL级别的装饰器
```

### 跟进问题

```
□ 对于列表端点：查询是否过滤到用户的数据，还是返回所有数据？

□ 对于创建端点：谁设置所有者 - 服务器还是请求？

□ 对于批量操作：它们是否作用域化到用户的数据？

□ 对于相关资源：如果我能访问文档，我能访问其评论吗？
  如果文档属于其他人呢？

□ 对于租户/组织资源：组织A中的用户能否通过更改URL中的org_id访问组织B的数据？
```

---

## 第四阶段：追踪特定流程

选择一个具体的端点并完全追踪它。

### 示例调查

```
端点：GET /api/documents/{pk}/

1. 找到处理此URL的视图
   → DocumentViewSet.retrieve() 在api/views.py中

2. 检查DocumentViewSet继承自什么
   → class DocumentViewSet(viewsets.ModelViewSet)
   → 没有自定义的授权基础类

3. 检查permission_classes
   → permission_classes = [IsAuthenticated]
   → 仅检查登录，不检查所有权

4. 检查get_queryset()
   → def get_queryset(self):
   →     return Document.objects.all()
   → 返回所有文档！

5. 检查has_object_permission()
   → 未实现

6. 检查retrieve()方法
   → 使用默认值，调用get_object()
   → get_object()使用get_queryset()，返回所有

7. 结论：IDOR - 任何认证用户都可以通过ID访问任何文档
```

### 追踪时要注意什么

```
潜在差距指标（进一步调查，不要自动标记）：
- get_queryset()返回.all()或没有用户过滤
- 直接使用Model.objects.get(pk=pk)而没有所有权查询
- ID来自请求体用于敏感操作
- 权限类检查认证但不检查所有权
- 没有has_object_permission()且查询未作用域化

可能安全的模式（但验证实现）：
- get_queryset()过滤request.user或用户组织
- 自定义权限类具有has_object_permission()
- 强制作用域的基类
- 自动过滤的管理器
```

---

## 第五阶段：报告发现

仅报告你通过调查确认的问题。

### 置信度级别

| 级别 | 含义 | 操作 |
|-------|---------|--------|
| **高** | 追踪了流程，确认不存在检查 | 带证据报告 |
| **中** | 检查可能存在但无法确认 | 注明手动验证 |
| **低** | 理论上的，可能已缓解 | 不要报告 |

### 建议的修复必须强制执行，而不是记录

**错误的修复**：添加一个注释说"调用者必须验证权限"
**正确的修复**：添加实际验证权限的代码

注释或docstring不会强制执行授权。你的建议修复必须包括实际代码，该代码：
- 在继续之前验证用户是否有权限
- 如果未授权，引发异常或返回错误
- 使未授权访问不可能，而不仅仅是劝阻

错误的修复建议示例：
```python
def get_resource(resource_id):
    # 重要提示：调用者必须确保用户可以访问此资源
    return Resource.objects.get(pk=resource_id)
```

正确的修复建议示例：
```python
def get_resource(resource_id, user):
    resource = Resource.objects.get(pk=resource_id)
    if resource.owner_id != user.id:
        raise PermissionDenied("访问被拒绝")
    return resource
```

如果你无法确定正确的强制执行机制，请说明 - 但永远不要建议文档作为修复。

### 报告格式

```markdown
## 访问控制审查：[组件]

### 授权模型
[简要描述此代码库如何处理授权]

### 发现

#### [IDOR-001] [标题]（严重性：高/中）
- **位置**：`path/to/file.py:123`
- **置信度**：高 - 通过代码追踪确认
- **问题**：用户A能否访问用户B的文档？
- **调查**：
  1. 追踪GET /api/documents/{pk}/到DocumentViewSet
  2. 检查get_queryset() - 返回Document.objects.all()
  3. 检查permission_classes - 仅IsAuthenticated
  4. 检查has_object_permission() - 未实现
  5. 验证没有相关的中间件或基类检查
- **证据**：[显示差距的代码片段]
- **影响**：任何认证用户都可以通过ID读取任何文档
- **建议修复**：[强制执行授权的代码 - 不是注释]

### 需要手动验证
[授权存在但无法确认有效性的问题]

### 未审查的区域
[此审查未涵盖的端点或流程]
```

---

## 常见的Django授权模式

这些是你可能发现的模式，而不是要匹配的清单。

### 查询作用域化
```python
# 作用域到用户
Document.objects.filter(owner=request.user)

# 作用域到组织
Document.objects.filter(organization=request.user.organization)

# 使用自定义管理器
Document.objects.for_user(request.user)  # 调查它做什么
```

### 权限强制执行
```python
# DRF权限类
permission_classes = [IsAuthenticated, IsOwner]

# 自定义has_object_permission
def has_object_permission(self, request, view, obj):
    return obj.owner == request.user

# Django装饰器
@permission_required('app.view_document')

# 手动检查
if document.owner != request.user:
    raise PermissionDenied()
```

### 所有权分配
```python
# 服务器端（安全）
def perform_create(self, serializer):
    serializer.save(owner=self.request.user)

# 从请求（调查）
serializer.save(**request.data)  # 请求.data是否包含owner？
```

---

## 调查清单

使用此清单来指导你的审查，而不是作为通过/失败清单：

```
□ 我理解此代码库中授权的典型实现方式
□ 我已确定所有权模型（用户、组织、租户等）
□ 我已映射处理用户数据的关键端点
□ 对于每个敏感端点，我已追踪流程并提出：
  - ID来自哪里？
  - 哪里获取数据？
  - 输入和数据访问之间存在哪些检查？
□ 我已通过检查父类和中间件验证我的发现
□ 我仅报告了通过调查确认的问题
```
