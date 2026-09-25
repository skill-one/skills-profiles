# 添加键盘快捷键指南

## 添加新热键的步骤

### 1. 更新热键常量

在 `src/types/hotkey.ts` 中：

```typescript
export const HotkeyEnum = {
  // 现有...
  ClearChat: 'clearChat', // 添加新项
} as const;
```

### 2. 注册默认热键

在 `src/const/hotkeys.ts` 中：

```typescript
import { KeyMapEnum as Key, combineKeys } from '@lobehub/ui';

export const HOTKEYS_REGISTRATION: HotkeyRegistration = [
  {
    group: HotkeyGroupEnum.Conversation,
    id: HotkeyEnum.ClearChat,
    keys: combineKeys([Key.Mod, Key.Shift, Key.Backspace]),
    scopes: [HotkeyScopeEnum.Chat],
  },
];
```

### 3. 添加 i18n 翻译

在 `packages/locales/src/default/hotkey.ts` 中：

```typescript
const hotkey: HotkeyI18nTranslations = {
  clearChat: {
    desc: '清空当前会话的所有消息记录',
    title: '清空聊天记录',
  },
};
```

### 4. 创建并注册 Hook

在 `src/hooks/useHotkeys/chatScope.ts` 中：

```typescript
export const useClearChatHotkey = () => {
  const clearMessages = useChatStore((s) => s.clearMessages);
  return useHotkeyById(HotkeyEnum.ClearChat, clearMessages);
};

export const useRegisterChatHotkeys = () => {
  useClearChatHotkey();
  // ...其他热键
};
```

### 5. 添加提示（可选）

```tsx
const clearChatHotkey = useUserStore(settingsSelectors.getHotkeyById(HotkeyEnum.ClearChat));

<Tooltip hotkey={clearChatHotkey} title={t('clearChat.title', { ns: 'hotkey' })}>
  <Button icon={<DeleteOutlined />} onClick={clearMessages} />
</Tooltip>;
```

## 最佳实践

1. **作用域**：根据功能选择全局或聊天作用域
2. **分组**：放置在适当的分组（系统/布局/聊天）
3. **冲突检查**：确保与系统/浏览器快捷键无冲突
4. **平台**：使用 `Key.Mod` 而不是硬编码的 `Ctrl` 或 `Cmd`
5. **清晰描述**：为用户提供标题和描述

## 故障排除

- **无效**：检查作用域和 `RegisterHotkeys` Hook
- **设置中未显示**：验证 `HOTKEYS_REGISTRATION` 配置
- **冲突**：`HotkeyInput` 组件显示警告
- **页面特定**：确保正确激活作用域
