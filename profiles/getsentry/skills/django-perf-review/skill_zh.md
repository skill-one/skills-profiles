# Django 性能审查

审查 Django 代码以发现**已验证**的性能问题。研究代码库以确认问题后再报告。仅报告你能证明的问题。

## 审查方法

1. **先研究** - 追踪数据流，检查现有优化，验证数据量
2. **报告前验证** - 模式匹配不是验证
3. **零发现是可以接受的** - 不要制造问题以显得全面
4. **严重性必须与影响匹配** - 如果你发现自己在一个关键发现中写"轻微"，那它就不是关键的。降级或跳过它。

## 影响类别

问题按影响分类。重点关注 CRITICAL 和 HIGH - 这些在规模上会导致真实问题。

| 优先级 | 类别 | 影响 |
|--------|------|------|
| 1 | N+1 查询 | **CRITICAL** - 随数据量增加而增加，导致超时 |
| 2 | 无限查询集 | **CRITICAL** - 内存耗尽，OOM 杀死 |
| 3 | 缺少索引 | **HIGH** - 大表上的全表扫描 |
| 4 | 写入循环 | **HIGH** - 锁竞争，请求缓慢 |
| 5 | 低效模式 | **LOW** - 很少值得报告 |

---

## 优先级 1：N+1 查询 (CRITICAL)

**影响**：每个 N+1 增加数据库往返 `O(n)` 次请求。100 行 = 100 次额外查询。10,000 行 = 超时。

### 规则：在循环中预取相关数据

通过追踪验证：视图 → 查询集 → 模板/序列化器 → 循环访问

```python
# 问题：N+1 - 每次迭代查询 profile
def user_list(request):
    users = User.objects.all()
    return render(request, 'users.html', {'users': users})

# 模板：
# {% for user in users %}
#     {{ user.profile.bio }}  ← 每个用户触发查询
# {% endfor %}

# 解决方案：在视图中预取
def user_list(request):
    users = User.objects.select_related('profile')
    return render(request, 'users.html', {'users': users})
```

### 规则：在序列化器中预取，而不仅仅是视图

DRF 序列化器访问相关字段时，如果查询集未优化，会导致 N+1。

```python
# 问题：SerializerMethodField 每个对象查询
class UserSerializer(serializers.ModelSerializer):
    order_count = serializers.SerializerMethodField()

    def get_order_count(self, obj):
        return obj.orders.count()  # ← 每个用户查询

# 解决方案：在视图集注释，序列化器中访问
class UserViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return User.objects.annotate(order_count=Count('orders'))

class UserSerializer(serializers.ModelSerializer):
    order_count = serializers.IntegerField(read_only=True)
```

### 规则：模型属性在循环中查询是危险的

```python
# 问题：属性触发查询时访问
class User(models.Model):
    @property
    def recent_orders(self):
        return self.orders.filter(created__gte=last_week)[:5]

# 在模板循环中使用 = N+1

# 解决方案：使用 Prefetch 与自定义查询集，或注释
```

### N+1 验证清单
- [ ] 从视图到模板/序列化器追踪数据流
- [ ] 确认相关字段在循环内访问
- [ ] 搜索代码库中现有的 select_related/prefetch_related
- [ ] 验证表有显著行数 (1000+)
- [ ] 确认这是热点路径（不是管理后台，不是罕见操作）

---

## 优先级 2：无限查询集 (CRITICAL)

**影响**：加载整个表会耗尽内存。大表会导致 OOM 杀死和工作进程重启。

### 规则：始终分页列表端点

```python
# 问题：无分页 - 加载所有行
class UserListView(ListView):
    model = User
    template_name = 'users.html'

# 解决方案：添加分页
class UserListView(ListView):
    model = User
    template_name = 'users.html'
    paginate_by = 25
```

### 规则：使用 iterator() 进行大批量处理

```python
# 问题：一次将所有对象加载到内存中
for user in User.objects.all():
    process(user)

# 解决方案：使用 iterator() 流式传输
for user in User.objects.iterator(chunk_size=1000):
    process(user)
```

### 规则：永远不要在无限查询集上调用 list()

```python
# 问题：强制全部评估到内存
all_users = list(User.objects.all())

# 解决方案：保持为查询集，需要时切片
users = User.objects.all()[:100]
```

### 无限查询集验证清单
- [ ] 表很大 (10k+ 行) 或将无限制增长
- [ ] 无分页类，paginate_by 或切片
- [ ] 这在用户请求上运行（不是带分块的后台作业）

---

## 优先级 3：缺少索引 (HIGH)

**影响**：全表扫描。在小表上可忽略不计，在大表上灾难性。

### 规则：在大型表上对 WHERE 子句中使用的字段添加索引

```python
# 问题：在未索引字段上过滤
# User.objects.filter(email=email)  # 无索引时全扫描

class User(models.Model):
    email = models.EmailField()  # ← 无 db_index

# 解决方案：添加索引
class User(models.Model):
    email = models.EmailField(db_index=True)
```

### 规则：在大型表上对 ORDER BY 中使用的字段添加索引

```python
# 问题：无索引时排序需要全扫描
Order.objects.order_by('-created')

# 解决方案：索引排序字段
class Order(models.Model):
    created = models.DateTimeField(db_index=True)
```

### 规则：为常见查询模式使用复合索引

```python
class Order(models.Model):
    user = models.ForeignKey(User)
    status = models.CharField(max_length=20)
    created = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['user', 'status']),  # 用于 filter(user=x, status=y)
            models.Index(fields=['status', '-created']),  # 用于 filter(status=x).order_by('-created')
        ]
```

### 缺少索引验证清单
- [ ] 表有 10k+ 行
- [ ] 字段在热点路径上用于 filter() 或 order_by()
- [ ] 检查模型 - 无 db_index=True 或 Meta.indexes 条目
- [ ] 不是外键（自动索引）

---

## 优先级 4：写入循环 (HIGH)

**影响**：N 次数据库写入而不是 1 次。锁竞争。请求缓慢。

### 规则：使用 bulk_create 而不是在循环中 create()

```python
# 问题：N 次插入，N 次往返
for item in items:
    Model.objects.create(name=item['name'])

# 解决方案：单个批量插入
Model.objects.bulk_create([
    Model(name=item['name']) for item in items
])
```

### 规则：使用 update() 或 bulk_update 而不是在循环中 save()

```python
# 问题：N 次更新
for obj in queryset:
    obj.status = 'done'
    obj.save()

# 解决方案 A：单个 UPDATE 语句（所有值相同）
queryset.update(status='done')

# 解决方案 B：bulk_update（不同值）
for obj in objects:
    obj.status = compute_status(obj)
Model.objects.bulk_update(objects, ['status'], batch_size=500)
```

### 规则：使用 queryset.delete() 而不是在循环中 delete()

```python
# 问题：N 次删除
for obj in queryset:
    obj.delete()

# 解决方案：单个 DELETE
queryset.delete()
```

### 写入循环验证清单
- [ ] 循环迭代 100+ 项（或无限制）
- [ ] 每次迭代调用 create()、save() 或 delete()
- [ ] 这在用户请求上运行（不是一次性迁移脚本）

---

## 优先级 5：低效模式 (LOW)

**很少值得报告**。仅在已经报告真实问题时作为次要备注包含。

### 模式：count() vs exists()

```python
# 略微次优
if queryset.count() > 0:
    do_thing()

# 稍好
if queryset.exists():
    do_thing()
```

**通常跳过** - 在大多数情况下，差异小于 1ms。

### 模式：len(queryset) vs count()

```python
# 获取所有行以计数
if len(queryset) > 0:  # 如果查询集尚未评估，则不好

# 单个 COUNT 查询
if queryset.count() > 0:
```

**仅标记** - 如果查询集很大且尚未评估。

### 模式：小循环中的 get()

```python
# N 次查询，但如果 N 小 (< 20)，通常可以接受
for id in ids:
    obj = Model.objects.get(id=id)
```

**仅标记** - 如果循环很大或这在非常热路径上。

---

## 验证要求

在报告任何问题之前：

1. **追踪数据流** - 从查询集创建到消费追踪
2. **搜索现有优化** - Grep for select_related、prefetch_related、分页
3. **验证数据量** - 检查表是否确实很大
4. **确认热点路径** - 追踪调用点，验证此路径运行频繁
5. **排除缓解措施** - 检查缓存、速率限制

**如果你无法验证所有步骤，不要报告。**

---

## 输出格式

```markdown
## Django 性能审查：[文件/组件名称]

### 摘要
已验证问题：X (Y 严重，Z 高)

### 发现

#### [PERF-001] UserListView 中的 N+1 查询 (CRITICAL)
**位置**：`views.py:45`

**问题**：相关字段 `profile` 在模板循环中未预取。

**验证**：
- 追踪：UserListView → users 查询集 → user_list.html → `{{ user.profile.bio }}` 在循环中
- 搜索代码库：未找到 select_related('profile')
- 用户表：50k+ 行（在管理后台验证）
- 热点路径：从主页导航链接

**证据**：
```python
def get_queryset(self):
    return User.objects.filter(active=True)  # 无 select_related
```

**修复**：
```python
def get_queryset(self):
    return User.objects.filter(active=True).select_related('profile')
```
```

如果未发现问题：在审查 [文件] 和验证 [你检查的内容] 后未发现性能问题。

**提交前，对每个发现进行合理性检查**：
- 严重性是否与实际影响匹配？("轻微低效" ≠ CRITICAL)
- 这是否是真实的性能问题，还是仅仅是风格偏好？
- 修复此问题是否能显著提高性能？

如果任何问题的答案是 "否" - 移除该发现。

---

## 不要报告的内容

- 测试文件
- 仅管理员视图
- 管理命令
- 迁移文件
- 一次性脚本
- 被禁用功能标志后的代码
- 行数少于 1000 且不会增长的表
- 冷路径上的模式（很少执行的代码）
- 微优化（exists vs count，只有/defer 无证据）

### 避免误报

**查询集变量赋值不是问题**：
```python
# 这很好 - 无性能差异
projects_qs = Project.objects.filter(org=org)
projects = list(projects_qs)

# vs 这 - 相同性能
projects = list(Project.objects.filter(org=org))
```
查询集是惰性的。赋值给变量不会执行任何操作。

**单个查询模式不是 N+1**：
```python
# 这是单个查询，不是 N+1
projects = list(Project.objects.filter(org=org))
```
N+1 需要一个触发额外查询的循环。单个 `list()` 调用是好的。

**单个对象获取中缺少 select_related 不是 N+1**：
```python
# 这是 2 次查询，不是 N+1 - 最多报告为 LOW
state = AutofixState.objects.filter(pr_id=pr_id).first()
project_id = state.request.project_id  # 第二次查询
```
N+1 需要一个循环。单个对象执行 2 次查询而不是 1 次可以报告为 LOW（如果相关），但永远不会报告为 CRITICAL/HIGH。

**风格偏好不是性能问题**：
如果你的唯一建议是 "合并这两行" 或 "重命名这个变量" - 那是风格，不是性能。不要报告它。
