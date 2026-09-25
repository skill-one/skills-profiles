# 国际化与本地化

> 国际化（i18n）与本地化（L10n）最佳实践。

---

## 1. 核心概念

| 术语 | 含义 |
|------|---------|
| **i18n** | 国际化 - 使应用可翻译 |
| **L10n** | 本地化 - 实际翻译 |
| **Locale** | 语言 + 地区 (en-US, tr-TR) |
| **RTL** | 从右到左的语言 (阿拉伯语, 希伯来语) |

---

## 2. 何时使用国际化

| 项目类型 | 是否需要国际化 |
|--------------|--------------|
| 公共 Web 应用 | ✅ 是 |
| SaaS 产品 | ✅ 是 |
| 内部工具 | ⚠️ 可能 |
| 单一地区应用 | ⚠️ 考虑未来 |
| 个人项目 | ❌ 可选 |

---

## 3. 实现模式

### React (react-i18next)

```tsx
import { useTranslation } from 'react-i18next';

function Welcome() {
  const { t } = useTranslation();
  return <h1>{t('welcome.title')}</h1>;
}
```

### Next.js (next-intl)

```tsx
import { useTranslations } from 'next-intl';

export default function Page() {
  const t = useTranslations('Home');
  return <h1>{t('title')}</h1>;
}
```

### Python (gettext)

```python
from gettext import gettext as _

print(_("Welcome to our app"))
```

---

## 4. 文件结构

```
locales/
├── en/
│   ├── common.json
│   ├── auth.json
│   └── errors.json
├── tr/
│   ├── common.json
│   ├── auth.json
│   └── errors.json
└── ar/          # 从右到左的语言
    └── ...
```

---

## 5. 最佳实践

### 应该 ✅

- 使用翻译键而非原始文本
- 按功能命名空间化翻译
- 支持复数形式
- 按地区处理日期/数字格式
- 从一开始就规划支持从右到左的语言
- 使用 ICU 消息格式处理复杂字符串

### 不应该 ❌

- 在组件中硬编码字符串
- 连接翻译后的字符串
- 假设文本长度（德语比英语长 30%）
- 忘记从右到左的布局
- 在同一文件中混合多种语言

---

## 6. 常见问题

| 问题 | 解决方案 |
|-------|----------|
| 缺失翻译 | 回退到默认语言 |
| 硬编码字符串 | 使用 linter/检查器脚本 |
| 日期格式 | 使用 Intl.DateTimeFormat |
| 数字格式 | 使用 Intl.NumberFormat |
| 复数形式 | 使用 ICU 消息格式 |

---

## 7. 从右到左的语言支持

```css
/* CSS 逻辑属性 */
.container {
  margin-inline-start: 1rem;  /* 不是 margin-left */
  padding-inline-end: 1rem;   /* 不是 padding-right */
}

[dir="rtl"] .icon {
  transform: scaleX(-1);
}
```

---

## 8. 检查清单

发布前：

- [ ] 所有用户界面字符串使用翻译键
- [ ] 所有支持的语言都有本地化文件
- [ ] 日期/数字格式使用 Intl API
- [ ] 从右到左的布局已测试（如适用）
- [ ] 回退语言已配置
- [ ] 组件中无硬编码字符串

---

## 脚本

| 脚本 | 目的 | 命令 |
|--------|---------|---------|
| `scripts/i18n_checker.py` | 检测硬编码字符串和缺失的翻译 | `python scripts/i18n_checker.py <项目路径>` |

## 何时使用
此技能适用于执行概述中描述的工作流程或操作。

## 限制
- 仅在任务明确符合上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家评审的替代品。
- 如果缺少必要的输入、权限、安全边界或成功标准，请停止并请求澄清。
