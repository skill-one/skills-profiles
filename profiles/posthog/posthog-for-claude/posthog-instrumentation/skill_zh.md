# PostHog 代码集成技能

帮助用户将 PostHog 分析、事件追踪和功能开关添加到他们的代码中。

## 使用场景

- 用户询问“添加 PostHog”或“添加分析”
- 用户希望追踪事件或用户操作
- 用户需要实现功能开关
- 用户询问如何对他们代码进行集成

## 工作流程

1. 确定框架（React、Next.js、Python、Node.js 等）
2. 检查现有的 PostHog 设置
3. 添加适当的集成代码

## 代码示例

### JavaScript/TypeScript
```javascript
// 事件追踪
posthog.capture('button_clicked', { button_name: 'signup' })

// 功能开关
if (posthog.isFeatureEnabled('new-feature')) {
  // 显示新功能
}

// 用户识别
posthog.identify(userId, { email: user.email })
```

### Python
```python
from posthog import Posthog
posthog = Posthog(api_key='<ph_project_api_key>')

# 事件追踪
posthog.capture(distinct_id='user_123', event='purchase_completed')

# 功能开关
if posthog.feature_enabled('new-feature', 'user_123'):
    # 显示新功能
```

### React
```jsx
import { usePostHog } from 'posthog-js/react'

function MyComponent() {
  const posthog = usePostHog()

  const handleClick = () => {
    posthog.capture('button_clicked')
  }
}
```

## 最佳实践

- 使用一致的事件命名（推荐 snake_case 格式）
- 在事件中包含相关属性
- 在用户会话早期进行用户识别
- 使用功能开关进行渐进式发布
