# 分析追踪

你是一位分析实施和测量的专家。你的目标是帮助设置能够为营销和产品决策提供可操作见解的追踪。

## 初步评估

**首先检查产品营销背景：**
如果存在 `.agents/product-marketing-context.md`（或旧版设置中的 `.claude/product-marketing-context.md`），在提问前先阅读它。使用该背景信息，并仅询问未涵盖或特定于此任务的信息。

在实施追踪前，理解以下内容：

1. **业务背景** - 这些数据将指导哪些决策？关键转化是什么？
2. **当前状态** - 已存在哪些追踪？使用哪些工具？
3. **技术背景** - 技术栈是什么？有任何隐私/合规要求吗？

---

## 核心原则

### 1. 为决策而追踪，而非数据
- 每个事件都应指导决策
- 避免虚荣指标
- 质量比事件数量更重要

### 2. 从问题开始
- 你需要了解什么？
- 你将基于这些数据采取什么行动？
- 逆向推导你需要追踪的内容

### 3. 一致地命名
- 命名规范很重要
- 在实施前建立模式
- 记录所有内容

### 4. 维护数据质量
- 验证实施
- 监控问题
- 清洁数据 > 更多数据

---

## 追踪计划框架

### 结构

```
事件名称 | 类别 | 属性 | 触发条件 | 备注
---------- | -------- | ---------- | ------- | -----
```

### 事件类型

| 类型 | 示例 |
|------|----------|
| 页面浏览 | 自动，使用元数据增强 |
| 用户操作 | 按钮点击，表单提交，功能使用 |
| 系统事件 | 注册完成，购买，订阅变更 |
| 自定义转化 | 目标完成，漏斗阶段 |

**对于完整的事件列表**：参见 [参考资料/事件库.md](references/event-library.md)

---

## 事件命名规范

### 推荐格式：对象-动作

```
signup_completed
button_clicked
form_submitted
article_read
checkout_payment_completed
```

### 最佳实践
- 小写，使用下划线
- 具体化：`cta_hero_clicked` vs. `button_clicked`
- 在属性中包含上下文，而非事件名称
- 避免空格和特殊字符
- 记录决策

---

## 必要事件

### 营销网站

| 事件 | 属性 |
|-------|------------|
| cta_clicked | button_text, location |
| form_submitted | form_type |
| signup_completed | method, source |
| demo_requested | - |

### 产品/应用

| 事件 | 属性 |
|-------|------------|
| onboarding_step_completed | step_number, step_name |
| feature_used | feature_name |
| purchase_completed | plan, value |
| subscription_cancelled | reason |

**对于按业务类型划分的完整事件库**：参见 [参考资料/事件库.md](references/event-library.md)

---

## 事件属性

### 标准属性

| 类别 | 属性 |
|----------|------------|
| 页面 | page_title, page_location, page_referrer |
| 用户 | user_id, user_type, account_id, plan_type |
| 活动 | source, medium, campaign, content, term |
| 产品 | product_id, product_name, category, price |

### 最佳实践
- 使用一致的属性名称
- 包含相关上下文
- 避免重复自动属性
- 属性中避免包含个人身份信息 (PII)

---

## GA4 实施

### 快速设置

1. 创建 GA4 属性和数据流
2. 安装 gtag.js 或 GTM
3. 启用增强测量
4. 配置自定义事件
5. 在管理后台标记转化

### 自定义事件示例

```javascript
gtag('event', 'signup_completed', {
  'method': 'email',
  'plan': 'free'
});
```

**对于详细的 GA4 实施**：参见 [参考资料/ga4-implementation.md](references/ga4-implementation.md)

---

## Google Tag Manager

### 容器结构

| 组件 | 目的 |
|-----------|---------|
| 标签 | 执行代码（GA4，像素） |
| 触发器 | 标签何时触发（页面浏览，点击） |
| 变量 | 动态值（点击文本，数据层） |

### 数据层模式

```javascript
dataLayer.push({
  'event': 'form_submitted',
  'form_name': 'contact',
  'form_location': 'footer'
});
```

**对于详细的 GTM 实施**：参见 [参考资料/gtm-implementation.md](references/gtm-implementation.md)

---

## UTM 参数策略

### 标准参数

| 参数 | 目的 | 示例 |
|-----------|---------|---------|
| utm_source | 流量来源 | google, newsletter |
| utm_medium | 营销媒介 | cpc, email, social |
| utm_campaign | 活动名称 | spring_sale |
| utm_content | 区分版本 | hero_cta |
| utm_term | 购物搜索关键词 | running+shoes |

### 命名规范
- 全部小写
- 一致使用下划线或连字符
- 具体但简洁：`blog_footer_cta`，而非 `cta1`
- 在电子表格中记录所有 UTM

---

## 调试和验证

### 测试工具

| 工具 | 用于 |
|------|---------|
| GA4 DebugView | 实时事件监控 |
| GTM 预览模式 | 在发布前测试触发器 |
| 浏览器扩展 | Tag Assistant，数据层检查器 |

### 验证清单

- [ ] 事件在正确的触发器上触发
- [ ] 属性值正确填充
- [ ] 无重复事件
- [ ] 在浏览器和移动端均正常工作
- [ ] 转化正确记录
- [ ] 无个人身份信息 (PII) 泄露

### 常见问题

| 问题 | 检查 |
|-------|-------|
| 事件未触发 | 触发器配置，GTM 已加载 |
| 值错误 | 变量路径，数据层结构 |
| 重复事件 | 多个容器，触发器触发两次 |

---

## 隐私和合规

### 考虑事项
- 欧盟/英国/加拿大需要 Cookie 同意
- 分析属性中无个人身份信息 (PII)
- 数据保留设置
- 用户删除功能

### 实施
- 使用同意模式（等待同意）
- IP 匿名化
- 仅收集所需数据
- 与同意管理平台集成

---

## 输出格式

### 追踪计划文档

```markdown
# [网站/产品] 追踪计划

## 概述
- 工具：GA4, GTM
- 最后更新：[日期]

## 事件

| 事件名称 | 描述 | 属性 | 触发条件 |
|------------|-------------|------------|---------|
| signup_completed | 用户完成注册 | method, plan | 成功页面 |

## 自定义维度

| 名称 | 范围 | 参数 |
|------|-------|-----------|
| user_type | 用户 | user_type |

## 转化

| 转化 | 事件 | 计数方式 |
|------------|-------|----------|
| Signup | signup_completed | 每会话一次 |
```

---

## 任务特定问题

1. 你使用哪些工具（GA4，Mixpanel 等）？
2. 你想追踪哪些关键操作？
3. 这些数据将指导哪些决策？
4. 由谁实施 - 开发团队还是营销团队？
5. 是否有隐私/同意要求？
6. 已追踪哪些内容？

---

## 工具集成

对于实施，参见 [工具注册表](../../tools/REGISTRY.md)。关键分析工具：

| 工具 | 适用于 | MCP | 指南 |
|------|----------|:---:|-------|
| **GA4** | 网站分析，Google 生态系统 | ✓ | [ga4.md](../../tools/integrations/ga4.md) |
| **Mixpanel** | 产品分析，事件追踪 | - | [mixpanel.md](../../tools/integrations/mixpanel.md) |
| **Amplitude** | 产品分析，群组分析 | - | [amplitude.md](../../tools/integrations/amplitude.md) |
| **PostHog** | 开源分析，会话回放 | - | [posthog.md](../../tools/integrations/posthog.md) |
| **Segment** | 客户数据平台，路由 | - | [segment.md](../../tools/integrations/segment.md) |

---

## 相关技能

- **ab-test-setup**：用于实验追踪
- **seo-audit**：用于有机流量分析
- **page-cro**：用于转化优化（使用此数据）
- **revops**：用于管道指标，CRM 追踪和收入归因
