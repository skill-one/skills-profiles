# Mantine 下拉选择组件技能

## 概述

`Combobox` 提供了构建任何选择式 UI 的底层基础组件。内置的 `Select`、`Autocomplete` 和 `TagsInput` 组件都是在其之上构建的。

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

| 场景 | 使用方式 |
|---|---|
| 按钮触发（无文本输入） | `<Combobox.Target targetType="button">` |
| 输入触发 | `<Combobox.Target>`（默认） |
| 药丸 + 分离输入（多选） | `<Combobox.DropdownTarget>` + `<Combobox.EventsTarget>` |

## 参考

- **[`references/api.md`](references/api.md)** — 完整 API：`useCombobox` 选项和 store，所有子组件属性，CSS 变量，Styles API 选择器
- **[`references/patterns.md`](references/patterns.md)** — 代码示例：可搜索选择，带药丸的多选，分组，自定义渲染，清除按钮，表单集成
