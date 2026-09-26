# SoulTrace 人格评估

通过 [soultrace](https://soultrace.app/?utm_source=skills.sh&utm_medium=referral&utm_campaign=skills) API 进行自适应人格评估。在1-7李克特量表上回答24个问题，并根据5色心理模型获得您的人格原型。

## API 端点

```
POST https://soultrace.app/api/agent
```

无需认证。每IP每小时限制100次请求。

## 工作原理

API是**无状态的**。您需要每次请求都传递所有累积的答案，服务器通过贝叶斯推理来选择下一个最佳问题。

### 第1步：开始测试

发送一个空的答案数组以获取第一个问题：

```bash
curl -X POST https://soultrace.app/api/agent \
  -H "Content-Type: application/json" \
  -d '{"answers": []}'
```

响应：
```json
{
  "status": "in_progress",
  "question": {
    "id": 42,
    "text": "我在掌握复杂系统时能获得深深的满足感。"
  },
  "currentDistribution": {
    "white": 0.2,
    "blue": 0.2,
    "black": 0.2,
    "red": 0.2,
    "green": 0.2
  },
  "entropy": 2.322,
  "progress": { "answered": 0, "total": 24 }
}
```

### 第2步：回答问题

用户在1-7量表上回答每个问题：
- **1** = 非常不同意
- **4** = 中立
- **7** = 非常同意

追加答案并发送迄今为止所有的答案：

```bash
curl -X POST https://soultrace.app/api/agent \
  -H "Content-Type: application/json" \
  -d '{"answers": [{"questionId": 42, "score": 6}]}'
```

持续累积答案。每次响应都会给出下一个问题。

### 第3步：获取结果

回答24个问题后，响应会自动返回最终结果：

```json
{
  "status": "complete",
  "resultId": "abc-123-def",
  "resultUrl": "https://soultrace.app/en/results/abc-123-def",
  "distribution": {
    "white": 0.15,
    "blue": 0.35,
    "black": 0.25,
    "red": 0.10,
    "green": 0.15
  },
  "entropy": 1.89,
  "archetype": {
    "key": "blue-black",
    "name": "策略家",
    "alignmentScore": 87.3,
    "coreDynamic": "...",
    "strengths": ["..."],
    "weaknesses": ["..."]
  },
  "topMatches": [
    { "key": "blue-black", "name": "策略家", "alignmentScore": 87.3 },
    { "key": "blue", "name": "理性主义者", "alignmentScore": 82.1 },
    { "key": "black-blue", "name": "执行者", "alignmentScore": 78.5 }
  ],
  "shadowColors": [
    { "color": "red", "score": 0.10 },
    { "color": "green", "score": 0.15 }
  ],
  "progress": { "answered": 24, "total": 24 }
}
```

## 代理交互协议

当用户要求进行人格测试时：

1. **开始**通过调用API并传递 `{"answers": []}`。
2. **清晰地向用户展示**每个问题。告诉他们回答1-7（1=非常不同意，4=中立，7=非常同意）。
3. **收集**用户的数值答案（1-7）。如果他们给出非数值或描述性答案，将其映射到量表：
   - "非常不同意" / "完全不是" → 1
   - "不同意" / "不太" → 2
   - "略微不同意" → 3
   - "中立" / "可能" / "有时" → 4
   - "略微同意" → 5
   - "同意" / "是" → 6
   - "非常同意" / "绝对" → 7
4. **累积**答案，每次发送所有之前的答案加上新的答案。
5. **在回答完所有24个问题后**，通过以下方式展示结果：
   - 他们的原型名称和一致性分数
   - 他们的颜色分布（显示为百分比）
   - 他们的前3个原型匹配
   - 他们的完整结果页面的链接
6. **永远不要跳过问题**或代表用户自动回答。

## 评分量表

| 评分 | 含义 |
|-------|---------|
| 1 | 非常不同意 |
| 2 | 不同意 |
| 3 | 略微不同意 |
| 4 | 中立 |
| 5 | 略微同意 |
| 6 | 同意 |
| 7 | 非常同意 |

## 五种颜色

| 颜色 | 动机 | 本质 |
|-------|-------|---------|
| 白色 | 结构、公平 | 秩序、责任感 |
| 蓝色 | 理解、掌握 | 好奇心、精确 |
| 黑色 | 能动性、成就 | 雄心、策略 |
| 红色 | 强度、表达 | 热情、诚实 |
| 绿色 | 连接、成长 | 归属感、耐心 |

## 速率限制

- 每IP每小时100次请求
- 每个测试需要25次请求（1次开始 + 24次回答）
- 每小时最多约4次完整测试

## 错误处理

| 状态 | 含义 |
|--------|---------|
| 400 | 请求正文无效或答案格式错误 |
| 429 | 超出速率限制（检查 `Retry-After` 头） |
| 500 | 服务器错误 |

## API 信息

```bash
GET https://soultrace.app/api/agent
```

返回API元数据（版本、问题数量、评分范围）。
