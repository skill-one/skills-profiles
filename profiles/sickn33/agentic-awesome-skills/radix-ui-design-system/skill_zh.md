# Radix UI 设计系统

使用 Radix UI 基础组件构建生产级、可访问的设计系统，具有完全的自定义控制权和零样式预设。

## 详细指南

在执行此技能前，请阅读 [详细指南](references/detailed-guide.md)。它保留了完整流程和参考材料。将其安全性、先决条件和验证要求视为强制性要求。对于专注工作，加载相关部分；对于端到端工作，完整阅读指南。

## 何时使用此技能

- 从零开始创建自定义设计系统
- 构建可访问的 UI 组件库
- 实现复杂的交互组件（对话框、下拉菜单、选项卡等）
- 从样式组件库迁移到无样式基础组件
- 使用 CSS 变量或 Tailwind 设置主题系统
- 需要完全控制组件行为和样式
- 构建需要 WCAG 2.1 AA/AAA 合规的应用程序

## 不应使用此技能时

- 您需要开箱即用的预样式组件（使用 shadcn/ui、Mantine 等）
- 构建简单的无交互静态页面
- 项目不使用 React 16.8+（Radix 需要 hooks）
- 您需要除 React 之外的其他框架的组件

---

## 真实世界示例

### 示例 1：命令面板（组合对话框）

```tsx
import * as Dialog from '@radix-ui/react-dialog';
import { Command } from 'cmdk';

export function CommandPalette() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((open) => !open);
      }
    };
    document.addEventListener('keydown', down);
    return () => document.removeEventListener('keydown', down);
  }, []);

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50" />
        <Dialog.Content className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
          <Command>
            <Command.Input placeholder="输入命令..." />
            <Command.List>
              <Command.Empty>未找到结果。</Command.Empty>
              <Command.Group heading="建议">
                <Command.Item>日历</Command.Item>
                <Command.Item>搜索表情</Command.Item>
              </Command.Group>
            </Command.List>
          </Command>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
```

### 示例 2：带图标的下拉菜单

```tsx
import * as DropdownMenu from '@radix-ui/react-dropdown-menu';
import { DotsHorizontalIcon } from '@radix-ui/react-icons';

export function ActionsMenu() {
  return (
    <DropdownMenu.Root>
      <DropdownMenu.Trigger asChild>
        <button className="icon-button" aria-label="操作">
          <DotsHorizontalIcon />
        </button>
      </DropdownMenu.Trigger>

      <DropdownMenu.Portal>
        <DropdownMenu.Content className="dropdown-content" align="end">
          <DropdownMenu.Item className="dropdown-item">
            编辑
          </DropdownMenu.Item>
          <DropdownMenu.Item className="dropdown-item">
            复制
          </DropdownMenu.Item>
          <DropdownMenu.Separator className="dropdown-separator" />
          <DropdownMenu.Item className="dropdown-item text-red-500">
            删除
          </DropdownMenu.Item>
        </DropdownMenu.Content>
      </DropdownMenu.Portal>
    </DropdownMenu.Root>
  );
}
```

### 示例 3：带有 Radix Select + React Hook Form 的表单

```tsx
import * as Select from '@radix-ui/react-select';
import { useForm, Controller } from 'react-hook-form';

interface FormData {
  country: string;
}

export function CountryForm() {
  const { control, handleSubmit } = useForm<FormData>();

  return (
    <form onSubmit={handleSubmit((data) => console.log(data))}>
      <Controller
        name="country"
        control={control}
        render={({ field }) => (
          <Select.Root onValueChange={field.onChange} value={field.value}>
            <Select.Trigger className="select-trigger">
              <Select.Value placeholder="选择国家" />
              <Select.Icon />
            </Select.Trigger>
            
            <Select.Portal>
              <Select.Content className="select-content">
                <Select.Viewport>
                  <Select.Item value="us">美国</Select.Item>
                  <Select.Item value="ca">加拿大</Select.Item>
                  <Select.Item value="uk">英国</Select.Item>
                </Select.Viewport>
              </Select.Content>
            </Select.Portal>
          </Select.Root>
        )}
      />
      <button type="submit">提交</button>
    </form>
  );
}
```

---

## 限制
- 仅在任务明确匹配上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家评审的替代品。
- 如果缺少必要的输入、权限、安全边界或成功标准，请停止并请求澄清。
