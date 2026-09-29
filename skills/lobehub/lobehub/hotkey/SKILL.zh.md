---
name: hotkey
description: 用于键盘快捷键、注册、键组合、作用范围、冲突和快捷键工具提示。
---

# 添加键盘快捷键指南

## 添加新热键的步骤

### 1. 更新热键常量

在 `packages/types/src/hotkey.ts` 中，将新 id 添加到 `HotkeyId` 联合类型中 — 这是 `HotkeyEnum` 类型定义的来源：

```typescript
export type HotkeyId =
  | 'addUserMessage'
  // 现有...
  | 'saveTopic';
```

### 2. 注册默认热键

在 `packages/const/src/hotkeys.ts` 中，`KeyEnum` 和 `combineKeys` 已经在本文件中本地定义，因此无需导入 — 将条目添加到 `HotkeyEnum` 和 `HOTKEYS_REGISTRATION` 中：

```typescript
export const HotkeyEnum = {
  // 现有...
  SaveTopic: 'saveTopic',
} as const satisfies Record<string, HotkeyId>;

export const HOTKEYS_REGISTRATION: HotkeyRegistration = [
  // 现有...
  {
    group: HotkeyGroupEnum.Conversation,
    id: HotkeyEnum.SaveTopic,
    keys: combineKeys([KeyEnum.Alt, 'n']),
    scopes: [HotkeyScopeEnum.Chat],
  },
];
```

### 3. 添加 i18n 翻译

在 `packages/locales/src/default/hotkey.ts` 中：

```typescript
const hotkey: HotkeyI18nTranslations = {
  saveTopic: {
    desc: '保存当前话题并新建一个话题',
    title: '保存话题',
  },
};
```

### 4. 创建并注册 Hook

在 `src/hooks/useHotkeys/chatScope.ts` 中：

```typescript
export const useSaveTopicHotkey = () => {
  const openNewTopicOrSaveTopic = useChatStore((s) => s.openNewTopicOrSaveTopic);
  return useHotkeyById(HotkeyEnum.SaveTopic, openNewTopicOrSaveTopic);
};

export const useRegisterChatHotkeys = () => {
  useSaveTopicHotkey();
  // ...其他热键
};
```

### 5. 添加提示框（可选）

```tsx
const saveTopicHotkey = useUserStore(settingsSelectors.getHotkeyById(HotkeyEnum.SaveTopic));

<Tooltip hotkey={saveTopicHotkey} title={t('saveTopic.title', { ns: 'hotkey' })}>
  <Button icon={<SaveOutlined />} onClick={openNewTopicOrSaveTopic} />
</Tooltip>;
```

## 最佳实践

1. **作用域**：根据功能选择全局或聊天作用域
2. **分组**：放置在适当的组（系统/布局/聊天）
3. **冲突检查**：确保与系统/浏览器快捷键无冲突
4. **平台**：使用 `KeyEnum.Mod` 而不是硬编码的 `Ctrl` 或 `Cmd`
5. **清晰描述**：为用户提供标题和描述

## 故障排除

- **无效**：检查作用域和 `RegisterHotkeys` hook
- **设置中未显示**：验证 `HOTKEYS_REGISTRATION` 配置
- **冲突**：`HotkeyInput` 组件显示警告
- **页面特定**：确保正确激活作用域
