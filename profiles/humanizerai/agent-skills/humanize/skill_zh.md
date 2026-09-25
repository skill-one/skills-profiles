# 将 AI 文本人性化

使用 HumanizerAI API 将 AI 生成的文本转换为自然、类似人类的写作。

## 工作原理

当用户调用 `/humanize` 时，您应该：

1. 解析 $ARGUMENTS 以获取文本和可选的 --intensity 标志
2. 调用 HumanizerAI API 来人性化文本
3. 带有前后分数展示人性化后的文本
4. 显示剩余的积分

## 解析参数

用户可以提供：
- 仅文本：`/humanize [他们的文本]`
- 带有强度：`/humanize --intensity aggressive [他们的文本]`

默认强度是 `medium`。

## 强度级别

| 值 | 名称 | 描述 | 适用于 |
|-------|------|-------------|----------|
| `light` | 轻度 | 轻微的更改，保留风格 | 已编辑的文本，低 AI 分数 |
| `medium` | 中度 | 平衡的重写（默认） | 大多数用例 |
| `aggressive` | 跳过 | 最大跳过模式 | 高 AI 分数，严格的检测器 |

## API 调用

向 `https://humanizerai.com/api/v1/humanize` 发送 POST 请求：

```
Authorization: Bearer $HUMANIZERAI_API_KEY
Content-Type: application/json

{
  "text": "<用户的文本>",
  "intensity": "medium"
}
```

## 响应格式

像这样展示结果：

```
## 人性化完成

**分数：** X → Y（改进）
**处理的字数：** N
**剩余积分：** X

---
### 人性化后的文本

[人性化后的文本]

---

[基于最终分数的建议]
```

## 积分使用

- 1 个字 = 1 个积分
- 检测免费
- 在 https://humanizerai.com/dashboard 查看积分

## 错误处理

### 积分不足
如果用户没有足够的积分：
1. 显示需要的积分与可用的积分
2. 指导他们到 https://humanizerai.com/dashboard 充值

### 无效的 API 密钥
1. 检查 HUMANIZERAI_API_KEY 环境变量
2. 指导他们到 https://humanizerai.com 获取密钥

### 超出速率限制
如果超出速率限制，建议等待或升级到商业计划。
