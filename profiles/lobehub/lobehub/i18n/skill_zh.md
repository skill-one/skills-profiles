# LobeHub 国际化指南

- 默认语言：英语 (en-US)
- 框架：react-i18next
- **仅编辑 `packages/locales/src/default/` 目录下的文件** - 切勿编辑 `locales/` 目录下的 JSON 文件（除了手写的 en-US/zh-CN 预览文件）
- 默认将生成的国际化文件交给每日的 `auto-i18n.yml` 工作流处理；仅在需要立即使用时手动运行 `bun run i18n`

## 关键命名规范

**扁平化键名（使用点分隔符）**（非嵌套对象）：

```typescript
// ✅ 正确
export default {
  'alert.cloud.action': '立即体验',
  'sync.actions.sync': '立即同步',
  'sync.status.ready': '已连接',
};

// ❌ 避免嵌套对象
export default {
  alert: { cloud: { action: '...' } },
};
```

**命名模式：** `{功能}.{上下文}.{操作|状态}`

**参数：** 使用 `{{变量名}}` 语法

```typescript
'alert.cloud.desc': '我们提供 {{credit}} 额度积分',
```

**避免键名冲突：**

```typescript
// ❌ 冲突
'clientDB.solve': '自助解决',
'clientDB.solve.backup.title': '数据备份',

// ✅ 解决方案
'clientDB.solve.action': '自助解决',
'clientDB.solve.backup.title': '数据备份',
```

## 工作流程

1. 将键名添加到 `packages/locales/src/default/{命名空间}.ts`
2. 在 `packages/locales/src/default/index.ts` 中导出新的命名空间
3. 对于开发预览：手动翻译 `locales/zh-CN/{命名空间}.json` 和 `locales/en-US/{命名空间}.json`
4. 将其他所有国际化文件交给 `.github/workflows/auto-i18n.yml`，该工作流每日运行并自动创建翻译 PR
5. 仅在分支需要立即使用这些翻译时手动运行 `bun run i18n`；该操作较慢且需要 `OPENAI_API_KEY`

## 使用方法

```tsx
import { useTranslation } from 'react-i18next';

const { t } = useTranslation('common');

t('newFeature.title');
t('alert.cloud.desc', { credit: '1000' });

// 多个命名空间
const { t } = useTranslation(['common', 'chat']);
t('common:save');
```

## 常用命名空间

**最常用：** `common`（共享 UI）、`chat`（聊天功能）、`setting`（设置）

其他：auth、changelog、components、discover、editor、electron、error、file、hotkey、knowledgeBase、memory、models、plugin、portal、providers、tool、topic
