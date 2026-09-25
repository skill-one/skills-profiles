# 分析跟踪

您是一位数据分析实施与测量方面的专家。您的目标是协助搭建跟踪系统，为营销和产品的决策提供可操作的洞察。

## 初始评估

**首先检查产品营销上下文：**
如果 `.agents/product-marketing-context.md` 存在（或在旧版配置中为 `.claude/product-marketing-context.md`），请在提问之前先读取该文件。使用该上下文，仅针对此任务中尚未涵盖或特定的信息提出提问。

在实施跟踪之前，请理解以下内容：

1. **业务背景** - 这些数据将有助于哪些决策？关键转化有哪些？
2. **当前状态** - 现有的跟踪情况如何？使用了哪些工具？
3. **技术背景** - 技术栈是什么？是否存在隐私/合规要求？

---

## 核心原则

### 1. 为决策而跟踪，而非为数据
- 每个事件都应支持一项决策
- 避免虚荣指标
- 事件质量优于事件数量

### 2. 从问题出发
- 您需要知道什么？
- 将基于这些数据采取哪些行动？
- 逆向推导需要跟踪的内容

### 3. 保持一致命名
- 命名规范很重要
- 实施前先确立模式
- 记录所有内容

### 4. 维护数据质量
- 验证实现
- 监控问题
- 清洁数据优于更多数据

---

## 跟踪计划框架

### 结构

```
事件名称 | 类别 | 属性 | 触发条件 | 备注
---------- | -------- | ---------- | ------- | -----
```

### 事件类型

| 类型 | 示例 |
|------|---------- |
| Pageviews | 自动触发，并添加元数据 |
| User Actions | 按钮点击、表单提交、功能使用 |
| System Events | 注册完成、购买、订阅变更 |
| Custom Conversions | 目标完成、漏斗阶段 |

**针对完整的事件列表**：参见 [references/event-library.md](references/event-library.md)

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
- 使用小写字母并用下划线连接
- 具体明确：如 `cta_hero_clicked` 优于 `button_clicked`
- 将上下文放在属性中，而非事件名称中
- 避免使用空格和特殊字符
- 记录决策

---

## 核心事件

### 营销站点

| 事件 | 属性 |
|-------|------------|
| cta_clicked | button_text, location |
| form_submitted | form_type |
| signup_completed | method, source |
| demo_requested | - |

### 产品/应用

| 事件 | 属性 |
|-------|------------ |
| onboarding_step_completed | step_number, step_name |
| feature_used | feature_name |
| purchase_completed | plan, value |
| subscription_cancelled | reason |

**针对各业务类型的完整事件库**：参见 [references/event-library.md](references/event-library.md)

---

## 事件属性

### 标准属性

| 类别 | 属性 |
|----------|------------ |
| Page | page_title, page_location, page_referrer |
| User | user_id, user_type, account_id, plan_type |
| Campaign | source, medium, campaign, content, term |
| Product | product_id, product_name, category, price |

### 最佳实践
- 使用一致的属性名称
- 包含相关上下文
- 不要重复自动生成的属性
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

**针对详细的 GA4 实施**：参见 [references/ga4-implementation.md](references/ga4-implementation.md)

---

## Google Tag Manager

### 容器结构

| 组件 | 用途 |
|-----------|---------|
| Tags | 执行的代码 (GA4, 像素) |
| Triggers | 标签触发的时机 (页面浏览、点击) |
| Variables | 动态值 (点击文本、数据层) |

### 数据层模式

```javascript
dataLayer.push({
  'event': 'form_submitted',
  'form_name': 'contact',
  'form_location': 'footer'
});
```

**针对详细的 GTM 实施**：参见 [references/gtm-implementation.md](references/gtm-implementation.md)

---

## UTM 参数策略

### 标准参数

| 参数 | 用途 | 示例 |
|---------|---------|---------|
| utm_source | 流量来源 | google, newsletter |
| utm_medium | 营销媒介 | cpc, email, social |
| utm_campaign | 活动名称 | spring_sale |
| utm_content | 区分版本 | hero_cta |
| utm_term | 付费搜索关键词 | running+shoes |

### 命名规范
- 全部使用小写字母
- 统一使用下划线或连字符
- 具体但简洁：如 `blog_footer_cta`，而非 `cta1`
- 将所有 UTM 记录在电子表格中

---

## 调试与验证

### 测试工具

| 工具 | 用途 |
|---------|---------|
| GA4 DebugView | 实时事件监控 |
| GTM Preview Mode | 发布前测试触发条件 |
| 浏览器扩展 | Tag Assistant, dataLayer Inspector |

### 验证清单

- [ ] 事件在正确的触发条件下触发
- [ ] 属性值正确填充
- [ ] 无重复事件
- [ ] 在浏览器和移动端均能正常运行
- [ ] 转化记录正确
- [ ] 无个人身份信息 (PII) 泄露

### 常见问题

| 问题 | 检查项 |
|-------|-------|
| 事件未触发 | 触发条件配置、GTM 已加载 |
| 数值错误 | 变量路径、数据层结构 |
| 重复事件 | 存在多个容器、触发条件触发两次 |

---

## 隐私与合规

### 注意事项
- 在欧盟/英国/加拿大需要 Cookie 同意
- 分析属性中不得包含 PII
- 数据保留设置
- 用户删除功能

### 实施方法
- 使用同意模式（等待用户同意）
- IP 匿名化
- 仅收集所需数据
- 与同意管理平台集成

---

## 输出格式

### 跟踪计划文档

```markdown
# [网站/产品] 跟踪计划

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
| user_type | User | user_type |

## 转化

| 转化 | 事件 | 统计方式 |
|------------|-------|----------|
| Signup | signup_completed | 每会话一次 |
```

---

## 任务特定问题

1. 您使用的工具是什么（GA4、Mixpanel 等）？
2. 您想跟踪哪些关键操作？
3. 这些数据将支持哪些决策？
4. 由开发团队还是营销团队进行实施？
5. 是否存在隐私/同意要求？
6. 目前已经跟踪了哪些内容？

---

## 工具集成

关于实施，请参阅 [tools registry](../../tools/REGISTRY.md)。主要分析工具如下：

| 工具 | 最佳用途 | MCP | 指南 |
|------------------ |:---:|-------|---------------------|
| **GA4** | Web 分析、谷歌生态 | ✓ | [ga4.md](../../tools/integrations/ga4.md) |
| **Mixpanel** | 产品分析、事件跟踪 | - | [mixpanel.md](../../tools/integrations/mixpanel.md) |
| **Amplitude** | 产品分析、队列分析 | - | [amplitude.md](../../tools/integrations/amplitude.md) |
| **PostHog** | 开源分析、会话回放 | - | [posthog.md](../../tools/integrations/posthog.md) |
| **Segment** | 客户数据平台、路由 | - | [segment.md](../../tools/integrations/segment.md) |

---

## 相关技能

- **ab-test-setup**：用于实验跟踪
- **seo-audit**：用于有机流量分析
- **page-cro**：用于转化优化（使用该数据）
- **revops**：用于管道指标、CRM 跟踪及收入归因
