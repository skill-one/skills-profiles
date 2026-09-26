# 用户体验设计师技能

在设计和评审界面时，应用以下UX/UI原则。

## 何时应用这项技能

使用这项技能的情况包括：
- 设计或评审用户界面、组件和移动优先布局
- 实现可访问性功能或根据WCAG 2.2 AA进行审计
- 创建表单、导航、搜索和其他交互元素
- 编写UI文案和微文案
- 规划用户研究，或构建和维护设计系统
- 设计协作/多人功能（存在、实时编辑、共享、权限、版本历史）
- 构建基于画布或白板的应用程序
- 设计AI驱动的界面（聊天、协作者、代理、生成式UI）
- 评估设计中的暗模式、符合伦理规范和用户信任
- 创建引导流程、激活漏斗和首次运行体验
- 设计通知系统和注意力管理
- 构建仪表板和数据可视化
- 国际化/本地化UI或添加从右到左（RTL）语言支持
- 设计语音、多模式或跨设备输入体验

## 核心设计理念

### 以用户为中心的设计
1. **首先理解用户** - 在设计前进行调研
2. **减少认知负荷** - 保持界面简单直观
3. **提供反馈** - 每个操作应有可见的响应
4. **保持一致性** - 遵循用户期望的既定模式
5. **设计可访问性** - 从一开始就包含所有用户

### 超越复杂，追求平静与清晰
- **认知清晰优于感官丰富** - 平静、易读的界面优于繁忙、花哨的界面。动画、颜色和密度应通过帮助理解而非令人印象深刻来获得其存在的价值。
- **AI作为尊重的协作者，而非自动驾驶仪** - 可选地提供AI协助（侧边栏、覆盖层、建议）；保持用户控制权，并且每个AI操作都是可撤销和透明的。参见[参考资料/14-ai-ux-patterns.md](references/14-ai-ux-patterns.md)。
- **负责任的适应优于过度个性化** - 适应真实的用户需求和上下文；避免操纵性或模糊的个性化。
- **深度和判断优于表面功夫** - 随着UI成为商品，价值在于研究、正确性和知道何时*不*添加东西。

### 用户体验需求层次
1. **功能性** - 它是否有效？
2. **可靠性** - 它是否可靠？
3. **可用性** - 它是否易于使用？
4. **便利性** - 它是否无摩擦？
5. **愉悦性** - 它是否令人愉悦？

## 核心指南

### 设计前
- 理解用户目标和痛点
- 审查代码库中的现有模式
- 考虑可访问性要求（WCAG 2.2 AA）
- 定义成功指标

### 视觉设计
- 每个屏幕一个主要元素——主要操作在大小和对比度上优先于所有其他操作
- 一致的排版（正文16px+，标题比例1.3-1.6x）
- 充足的颜色对比度（文本4.5:1）
- 间距来自单一比例（4px或8px基本单位）

### 交互设计
- 触摸目标最小44×44px（iOS）/ 48×48dp（Android）
- 重要操作在拇指友好的区域（移动端底部/中心）
- 每个交互产生可见响应
- 响应在输入后100ms内出现
- 平滑动画（300-500ms持续时间）
- 支持`prefers-reduced-motion`

### 表单
- 内联验证（失去焦点时，而非输入时）
- 字段附近有清晰的错误消息
- 必填字段用星号（*）标记
- 逻辑的字段顺序和分组

### 导航
- 顶级项目有限（7±2规则）
- 当前位置始终可见
- 移动端：优先使用底部导航
- 页面间一致的导航

### 可访问性
- 所有交互元素可通过键盘访问和操作
- 每个控件都有可访问的名称和角色，屏幕阅读器可暴露
- 颜色不应是唯一的信息传递方式
- 聚焦状态可见
- 图片有替代文本

### 协作功能
- 存在指示器（光标、头像、输入中）
- 清晰的冲突预防/解决
- 离线状态通信
- 客户端特定的撤销/重做
- 清晰传达权限级别

### 画布/空间应用
- 光标中心缩放（非屏幕中心）
- 带切换的智能指南和吸附
- 大型画布的缩略图
- 全键盘导航支持
- 视口剔除以提升性能

### AI界面
- AI生成内容清晰标记
- AI声明的来源归因
- 用户反馈机制（点赞/点踩）
- 停止/取消生成控制
- 始终可用的人工覆盖

### 引导
- 首次运行体验引导用户到"啊哈时刻"
- 空状态提供清晰的下一步操作
- 引导可跳过且不会重新显示
- 注册仅收集必要字段

### 通知
- 通知严重程度与视觉处理匹配
- 推送权限在上下文中请求（非首次访问时）
- 用户可控制每个渠道的通知偏好
- Toast在4-8s内自动消失
- 带有可撤销操作的Toast将操作显示为按钮

### 伦理设计
- 接受/拒绝按钮具有相等的视觉突出度
- 无预选的选项同意框
- 取消与订阅一样容易
- 拒绝文案中无确认羞辱

### 国际化
- RTL准备就绪（逻辑CSS属性，在`dir="rtl"`中验证布局）
- 容忍约30-40%的文本扩展（无固定宽度标签/按钮）
- 无文本嵌入图片；所有字符串外部化
- 通过`Intl`进行本地化日期/数字/货币格式化
- 使用ICU复数规则处理复数，而非字符串连接
- 语言切换器使用本名，而非旗帜

## 决策树

### 模态对话框 vs. 侧边面板 vs. 全页

```
用户正在做什么？
├── 快速确认或简单输入（1-3个字段）？
│   └── → 模态对话框
├── 查看编辑详情同时保持主上下文可见？
│   ├── 内容较窄（表单、属性、聊天）？
│   │   └── → 侧边面板
│   └── 内容需要显著宽度？
│       └── → 全页覆盖层（带返回导航）
├── 多步骤工作流或复杂表单？
│   ├── 步骤简短（每步2-3个字段）？
│   │   └── → 带步骤器的模态对话框
│   └── 步骤较长或需要参考其他内容？
│       └── → 带步骤器的全页
└── 创建复杂实体（文档、项目）？
    └── → 全页（专用创建流程）
```

### 通知类型选择

```
什么需要用户的注意？
├── 需要立即行动？
│   ├── 阻塞性（必须解决才能继续）？
│   │   └── → 模态对话框（确认、错误恢复）
│   └── 非阻塞性但紧急？
│       └── → Banner（页面顶部，直到关闭前持续显示）
├── 完成操作的反馈？
│   ├── 成功或低重要性信息？
│   │   └── → Toast（4-8s自动消失）
│   └── 警告或错误？
│       └── → 带操作按钮的Toast（手动关闭）
├── 背景事件（新消息、他人更新）？
│   ├── 用户在同一上下文中？
│   │   └── → Badge + 微妙的内联指示器
│   └── 用户在应用其他地方？
│       └── → 导航项上的Badge + 可选推送通知
└── 系统状态（维护、连接性）？
    └── → 持久性Banner（视口顶部或底部）
```

## 详细文档

- 核心UX原则和启发式方法，参见[参考资料/01-core-principles.md](references/01-core-principles.md)
- UX定律快速参考，参见[参考资料/02-laws-of-ux.md](references/02-laws-of-ux.md)
- WCAG 2.2可访问性合规性，参见[参考资料/03-accessibility.md](references/03-accessibility.md)
- 视觉设计模式，参见[参考资料/04-visual-design.md](references/04-visual-design.md)
- 信息架构，参见[参考资料/05-information-architecture.md](references/05-information-architecture.md)
- 交互设计模式，参见[参考资料/06-interaction-design.md](references/06-interaction-design.md)
- 表单和输入设计，参见[参考资料/07-forms-and-inputs.md](references/07-forms-and-inputs.md)
- 移动端UX最佳实践，参见[参考资料/08-mobile-ux.md](references/08-mobile-ux.md)
- UX写作和微文案，参见[参考资料/09-ux-writing.md](references/09-ux-writing.md)
- 用户研究方法，参见[参考资料/10-user-research.md](references/10-user-research.md)
- 设计系统创建，参见[参考资料/11-design-systems.md](references/11-design-systems.md)
- 协作存在、实时光标和意识指示器，参见[参考资料/12a-presence-awareness.md](references/12a-presence-awareness.md)
- 冲突解决、同步、共享和离线UX，参见[参考资料/12b-conflict-resolution-sync.md](references/12b-conflict-resolution-sync.md)
- 画布导航、缩放、平移和对象操作，参见[参考资料/13a-canvas-navigation.md](references/13a-canvas-navigation.md)
- 画布元素、图层、性能和白板模式，参见[参考资料/13b-canvas-objects-performance.md](references/13b-canvas-objects-performance.md)
- AI和LLM界面设计（聊天、协作者、代理），参见[参考资料/14-ai-ux-patterns.md](references/14-ai-ux-patterns.md)
- 伦理设计和暗模式避免，参见[参考资料/15-ethical-design.md](references/15-ethical-design.md)
- 引导流程和用户激活，参见[参考资料/16-onboarding.md](references/16-onboarding.md)
- 通知系统和注意力管理，参见[参考资料/17-notifications.md](references/17-notifications.md)
- 数据可视化和仪表板设计，参见[参考资料/18-data-visualization.md](references/18-data-visualization.md)
- 搜索界面设计和自动完成，参见[参考资料/19-search-ux.md](references/19-search-ux.md)
- 情感设计和信任建立模式，参见[参考资料/20-emotional-design.md](references/20-emotional-design.md)
- 数据表、可排序列表、分页和批量操作，参见[参考资料/21-data-tables.md](references/21-data-tables.md)
- 加载状态、骨架屏、乐观更新和感知性能，参见[参考资料/22-performance-ux.md](references/22-performance-ux.md)
- 国际化、本地化和RTL设计，参见[参考资料/23-internationalization.md](references/23-internationalization.md)
- 语音、多模式和跨设备输入模式，参见[参考资料/24-voice-and-multimodal.md](references/24-voice-and-multimodal.md)

## 参考值

### 布局与排版

| 指标 | 值 | 上下文 |
|------|-------|---------|
| 触摸目标 | 44-48px | 最小可点击区域 |
| 正文文本 | 16px+ | 最小可读尺寸 |
| 行高 | 1.2-1.45 | 最佳可读性 |
| 行长 | 50-75字符 | 理想的阅读长度 |
| 对比度 | 4.5:1 | WCAG AA标准文本 |
| 对比度 | 3:1 | WCAG AA大文本 |
| 工作记忆 | 7±2项 | 米勒定律 |
| 文本扩展 | ~30-40% | 翻译增长（DE/FI/RU） |

### 交互与动画

| 指标 | 值 | 上下文 |
|------|-------|---------|
| 动画 | 300-500ms | 自然感持续时间 |
| 触摸反馈 | < 100ms | 感知即时响应 |
| 表单放弃 | 81% | 开始但未完成的用户 |
| 画布缩放范围 | 10%-4000% | 典型设计工具范围 |
| 智能指南吸附 | 2-8px | 吸附前距离 |
| 画布渲染 | 60fps | 平移/缩放时的目标帧率 |

### 协作

| 指标 | 值 | 上下文 |
|------|-------|---------|
| 光标更新率 | 50-100ms | 平滑实时光标移动 |
| 光标标签最大 | 12字符 | 截断较长的用户名 |
| 头像堆叠 | 3-5个可见 | 溢出使用"+N" |

### AI界面

| 指标 | 值 | 上下文 |
|------|-------|---------|
| AI首个token | < 1s | 感知响应速度 |
| AI流式传输 | 30-80tok/s | 自然阅读节奏 |
| 协作者接受率 | 25-35% | 建议有用性 |

### 参与度指标

| 指标 | 值 | 上下文 |
|------|-------|---------|
| 引导完成率 | > 65% | 检查清单完成率 |
| 首次价值时间 | < 5分钟 | 注册到激活 |
| Toast持续时间 | 4-8s | 自动消失时间 |
| 搜索成功 | > 70% | 用户找到结果 |
| NPS | > 50 | 用户情绪 |

## 应避免的反模式

1. **暗模式** - 欺骗用户的UI → 参见[参考资料/15-ethical-design.md](references/15-ethical-design.md)
2. **无上下文的无限滚动** - 没有进度感 → 参见[参考资料/21-data-tables.md](references/21-data-tables.md)
3. **隐藏导航** - 桌面端的汉堡菜单 → 参见[参考资料/05-information-architecture.md](references/05-information-architecture.md)
4. **自动播放媒体** - 意外的声音/视频 → 参见[参考资料/03-accessibility.md](references/03-accessibility.md)
5. **无解释的禁用按钮** - 令人困惑的阻塞状态 → 参见[参考资料/06-interaction-design.md](references/06-interaction-design.md)
6. **文本墙** - 无视觉层次或分块 → 参见[参考资料/04-visual-design.md](references/04-visual-design.md)
7. **纯颜色反馈** - 排除色盲用户 → 参见[参考资料/03-accessibility.md](references/03-accessibility.md)
8. **微小的触摸目标** - 移动端令人沮丧 → 参见[参考资料/08-mobile-ux.md](references/08-mobile-ux.md)
9. **无加载状态** - 用户认为系统出故障 → 参见[参考资料/22-performance-ux.md](references/22-performance-ux.md)
10. **弹窗/模态过度使用** - 中断用户流程 → 参见[参考资料/06-interaction-design.md](references/06-interaction-design.md)
11. **无存在指示器** - 用户不知道其他人正在工作 → 参见[参考资料/12a-presence-awareness.md](references/12a-presence-awareness.md)
12. **无声同步失败** - 无警告的数据丢失 → 参见[参考资料/12b-conflict-resolution-sync.md](references/12b-conflict-resolution-sync.md)
13. **光标过载** - 过多的实时光标产生视觉噪音 → 参见[参考资料/12a-presence-awareness.md](references/12a-presence-awareness.md)
14. **屏幕中心缩放** - 令人迷失方向；应在光标处缩放 → 参见[参考资料/13a-canvas-navigation.md](references/13a-canvas-navigation.md)
15. **无离线指示** - 用户认为已连接时实际上未连接 → 参见[参考资料/12b-conflict-resolution-sync.md](references/12b-conflict-resolution-sync.md)
16. **隐藏AI** - 用户应始终知道何时与AI交互 → 参见[参考资料/14-ai-ux-patterns.md](references/14-ai-ux-patterns.md)
17. **过度自动化** - AI更改未经用户意识或同意 → 参见[参考资料/14-ai-ux-patterns.md](references/14-ai-ux-patterns.md)
18. **无AI撤销** - AI应用的更改必须可撤销 → 参见[参考资料/14-ai-ux-patterns.md](references/14-ai-ux-patterns.md)
19. **确认羞辱** - 拒绝按钮上的负罪感语言 → 参见[参考资料/15-ethical-design.md](references/15-ethical-design.md)
20. **非对称同意** - 大的"接受"按钮，微小的"拒绝"链接 → 参见[参考资料/15-ethical-design.md](references/15-ethical-design.md)
21. **强制性长引导** - 强迫用户完成10+引导步骤 → 参见[参考资料/16-onboarding.md](references/16-onboarding.md)
22. **通知地毯轰炸** - 每个事件都作为推送通知 → 参见[参考资料/17-notifications.md](references/17-notifications.md)
23. **首次访问权限** - 在用户看到价值前请求推送权限 → 参见[参考资料/17-notifications.md](references/17-notifications.md)
24. **硬编码/不可翻译的字符串** - 文本嵌入代码/图片，固定宽度容器，仅LTR布局 → 参见[参考资料/23-internationalization.md](references/23-internationalization.md)
25. **仅语音流程/隐藏麦克风** - 无备用模态，无识别反馈，隐藏语音输入 → 参见[参考资料/24-voice-and-multimodal.md](references/24-voice-and-multimodal.md)

## 来源

这项技能综合了以下最佳实践：
- [UX定律](https://lawsofux.com/) - Jon Yablonski
- [尼尔森诺曼集团](https://www.nngroup.com/) - 可用性研究
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/) - 可访问性指南
- [材料设计](https://m3.material.io/) - Google的设计系统
- [人类界面指南](https://developer.apple.com/design/) - Apple
- [交互设计基金会](https://www.interaction-design.org/)
- [Liveblocks](https://liveblocks.io/) - 实时协作模式
- [Figma工程博客](https://www.figma.com/blog/category/engineering/) - 多人及画布
- [Ably](https://ably.com/blog/collaborative-ux-best-practices) - 协作UX
- [Google PAIR指南](https://pair.withgoogle.com/guidebook) - AI设计模式
- [Microsoft HAX工具包](https://www.microsoft.com/en-us/haxtoolkit/) - 人机交互
- [欺骗性设计](https://www.deceptive.design/) - 暗模式目录
- [欧盟数字服务法案](https://digital-strategy.ec.europa.eu/en/policies/digital-services-act-package) - 平台监管
- [欧盟可访问性法案](https://ec.europa.eu/social/main.jsp?catId=1202) - EN 301 549 / WCAG 2.1 AA强制要求
- [W3C国际化(i18n)活动](https://www.w3.org/International/) - i18n/l10n标准
- [Baymard研究所](https://baymard.com/) - 电子商务UX研究
- [爱德华·塔夫特](https://www.edwardtufte.com/) - 数据可视化
- [ColorBrewer](https://colorbrewer2.org/) - 色盲安全调色板
- [A11y项目](https://www.a11yproject.com/) - 可访问性社区资源
- [web.dev](https://web.dev/) - 核心网络指标和性能UX
- [Smashing Magazine](https://www.smashingmagazine.com/) - 实用UX/UI模式
