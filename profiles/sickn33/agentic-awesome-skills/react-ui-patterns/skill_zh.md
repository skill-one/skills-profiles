# React UI 模式

## 核心原则

1. **绝不展示过时的 UI** - 仅在真正加载时显示加载动画
2. **始终展示错误** - 用户必须知道何时出现失败
3. **乐观更新** - 让 UI 感觉即时响应
4. **渐进式披露** - 随着内容可用逐步展示
5. **优雅降级** - 部分数据优于无数据

## 加载状态模式

### 黄金法则

**仅在没有数据可展示时才显示加载指示器。**

```typescript
// 正确 - 仅在没有数据时显示加载状态
const { data, loading, error } = useGetItemsQuery();

if (error) return <ErrorState error={error} onRetry={refetch} />;
if (loading && !data) return <LoadingState />;
if (!data?.items.length) return <EmptyState />;

return <ItemList items={data.items} />;
```

```typescript
// 错误 - 即使有缓存数据也会显示加载动画
if (loading) return <LoadingState />; // 刷新时会闪烁！
```

### 加载状态决策树

```
是否有错误？
  → 是：显示带重试选项的错误状态
  → 否：继续

是否正在加载且没有数据？
  → 是：显示加载指示器（加载动画/骨架屏）
  → 否：继续

是否有数据？
  → 是，有项目：展示数据
  → 是，但为空：显示空状态
  → 否：显示加载（备用方案）
```

### 骨架屏 vs 加载动画

| 使用骨架屏时 | 使用加载动画时 |
|-------------|---------------|
| 已知内容形状 | 内容形状未知 |
| 列表/卡片布局 | 模态操作 |
| 初始页面加载 | 按钮提交 |
| 内容占位符 | 内联操作 |

## 错误处理模式

### 错误处理层级

```
1. 内联错误（字段级）→ 表单验证错误
2. Toast 通知 → 可恢复错误，用户可重试
3. 错误横幅 → 页面级错误，数据仍部分可用
4. 全屏错误 → 不可恢复，需要用户操作
```

### 始终展示错误

**关键：绝不无声地吞掉错误。**

```typescript
// 正确 - 错误始终展示给用户
const [createItem, { loading }] = useCreateItemMutation({
  onCompleted: () => {
    toast.success({ title: '项目已创建' });
  },
  onError: (error) => {
    console.error('createItem 失败:', error);
    toast.error({ title: '创建项目失败' });
  },
});

// 错误 - 错误被无声捕获，用户毫不知情
const [createItem] = useCreateItemMutation({
  onError: (error) => {
    console.error(error); // 用户什么也看不到！
  },
});
```

### 错误状态组件模式

```typescript
interface ErrorStateProps {
  error: Error;
  onRetry?: () => void;
  title?: string;
}

const ErrorState = ({ error, onRetry, title }: ErrorStateProps) => (
  <div className="error-state">
    <Icon name="exclamation-circle" />
    <h3>{title ?? '出现错误'}</h3>
    <p>{error.message}</p>
    {onRetry && (
      <Button onClick={onRetry}>重试</Button>
    )}
  </div>
);
```

## 按钮状态模式

### 按钮加载状态

```tsx
<Button
  onClick={handleSubmit}
  isLoading={isSubmitting}
  disabled={!isValid || isSubmitting}
>
  提交
</Button>
```

### 操作期间禁用

**关键：异步操作期间始终禁用触发器。**

```tsx
// 正确 - 加载时禁用按钮
<Button
  disabled={isSubmitting}
  isLoading={isSubmitting}
  onClick={handleSubmit}
>
  提交
</Button>

// 错误 - 用户可多次点击
<Button onClick={handleSubmit}>
  {isSubmitting ? '正在提交...' : '提交'}
</Button>
```

## 空状态

### 空状态要求

每个列表/集合必须具有空状态：

```tsx
// 错误 - 没有空状态
return <FlatList data={items} />;

// 正确 - 明确的空状态
return (
  <FlatList
    data={items}
    ListEmptyComponent={<EmptyState />}
  />
);
```

### 上下文相关空状态

```tsx
// 搜索无结果
<EmptyState
  icon="search"
  title="未找到结果"
  description="尝试不同的搜索词"
/>

// 列表尚未有项目
<EmptyState
  icon="plus-circle"
  title="尚未有项目"
  description="创建您的第一个项目"
  action={{ label: '创建项目', onClick: handleCreate }}
/>
```

## 表单提交模式

```tsx
const MyForm = () => {
  const [submit, { loading }] = useSubmitMutation({
    onCompleted: handleSuccess,
    onError: handleError,
  });

  const handleSubmit = async () => {
    if (!isValid) {
      toast.error({ title: '请修正错误' });
      return;
    }
    await submit({ variables: { input: values } });
  };

  return (
    <form>
      <Input
        value={values.name}
        onChange={handleChange('name')}
        error={touched.name ? errors.name : undefined}
      />
      <Button
        type="submit"
        onClick={handleSubmit}
        disabled={!isValid || loading}
        isLoading={loading}
      >
        提交
      </Button>
    </form>
  );
};
```

## 反模式

### 加载状态

```typescript
// 错误 - 数据存在时显示加载动画（会导致闪烁）
if (loading) return <Spinner />;

// 正确 - 仅在没有数据时显示加载
if (loading && !data) return <Spinner />;
```

### 错误处理

```typescript
// 错误 - 错误被吞掉
try {
  await mutation();
} catch (e) {
  console.log(e); // 用户什么也看不到！
}

// 正确 - 错误被展示
onError: (error) => {
  console.error('操作失败:', error);
  toast.error({ title: '操作失败' });
}
```

### 按钮状态

```typescript
// 错误 - 提交期间按钮未被禁用
<Button onClick={submit}>提交</Button>

// 正确 - 禁用并显示加载指示器
<Button onClick={submit} disabled={loading} isLoading={loading}>
  提交
</Button>
```

## 检查清单

完成任何 UI 组件前：

**UI 状态：**
- [ ] 错误状态已处理并展示给用户
- [ ] 仅在没有数据时显示加载状态
- [ ] 集合提供空状态
- [ ] 异步操作期间按钮被禁用
- [ ] 按钮在适当时候显示加载指示器

**数据 & 变更：**
- [ ] 变更有 onError 处理器
- [ ] 所有用户操作都有反馈（Toast/视觉）

## 与其他技能的集成

- **graphql-schema**: 使用带适当错误处理的变更模式
- **testing-patterns**: 测试所有 UI 状态（加载、错误、空、成功）
- **formik-patterns**: 应用表单提交模式

## 使用场景
此技能适用于执行概述中描述的工作流程或操作。

## 限制
- 仅在任务明确匹配上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家评审的替代品。
- 如果缺少必要的输入、权限、安全边界或成功标准，请停止并请求澄清。
