---
name: mantine-combobox
description: 使用 Mantine 的 Combobox 基础组件构建自定义的下拉/选择/自动完成/多选组件。在以下情况下使用此技巧：(1) 使用 Combobox 基础组件创建新的自定义选择类组件，(2) 构建可搜索的下拉菜单，(3) 实现多选或标签输入变体，(4) 自定义选项渲染，(5) 添加自定义过滤逻辑，或 (6) 任何涉及 useCombobox、Combobox.Target、Combobox.Option 或 Combobox.Dropdown 的任务。
---

# Mantine 下拉选择组件技能

## 概述

`Combobox` 提供了构建任何选择类 UI 的底层原语。内置的
`Select`、`Autocomplete` 和 `TagsInput` 组件都是在其之上构建的。

## 核心工作流程

### 1. 创建 store

```tsx
const combobox = useCombobox({
  onDropdownClose: () => combobox.resetSelectedOption(),
  onDropdownOpen: () => combobox.selectFirstOption(),
});
```

### 2. 渲染结构

```tsx
<Combobox store={combobox} onOptionSubmit={handleSubmit}>
  <Combobox.Target>
    <InputBase
      component="button"
      pointer
      rightSection={<Combobox.Chevron />}
      onClick={() => combobox.toggleDropdown()}
    >
      {value || <Input.Placeholder>选择值</Input.Placeholder>}
    </InputBase>
  </Combobox.Target>
  <Combobox.Dropdown>
    <Combobox.Options>
      {options.map((item) => (
        <Combobox.Option value={item} key={item}>{item}</Combobox.Option>
      ))}
    </Combobox.Options>
  </Combobox.Dropdown>
</Combobox>
```

### 3. 处理提交

```tsx
const handleSubmit = (val: string) => {
  setValue(val);
  combobox.closeDropdown();
};
```

## 目标类型

| 场景 | 使用 |
|---|---|
| 按钮触发（无文本输入） | `<Combobox.Target targetType="button">` |
| 输入触发 | `<Combobox.Target>`（默认） |
| 药丸 + 分离输入（多选） | `<Combobox.DropdownTarget>` + `<Combobox.EventsTarget>` |

## 参考

- **[`references/api.md`](references/api.md)** — 完整 API：`useCombobox` 选项和 store，所有子组件的属性，CSS 变量，Styles API 选择器
- **[`references/patterns.md`](references/patterns.md)** — 代码示例：可搜索的选择，带药丸的多选，分组，自定义渲染，清除按钮，表单集成
