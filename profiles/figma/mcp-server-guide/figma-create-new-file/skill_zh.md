# 在 Figma 中创建新文件

使用 `create_new_file` MCP 工具创建新的 Figma 设计、FigJam 或 Slides 文件的步骤。

## 第 1 步：确定方案和产品

使用用户为此任务提供的或选择的 `planKey`。否则，调用 `whoami` 并检查返回的方案。

- 无方案：通知用户无法继续创建文件。
- 一个方案：使用其 `key`。
- 多个方案：显示可用方案，要求用户选择一个，然后使用该方案的 `key`。

根据任务推断产品（设计、FigJam 或 Slides）。如果不确定，要求用户指定。

## 第 2 步：调用 create_new_file

- 使用第 1 步的 `planKey` 和产品调用 `create_new_file` 工具。
  - 如果用户未提供新文件名称，使用简洁的名称。
- 使用 `create_new_file` 工具响应中的 `file_key` 进行后续工具调用，如 `use_figma`。

## 第 3 步：（仅限 Slides）处理空网格

新的 Slides 文件不包含幻灯片：`figma.getSlideGrid()` 返回 `[]`。在从幻灯片读取主题标记等属性之前，调用 `figma.createSlide()` 或处理空情况。第一次调用 `createSlide()` 会自动创建第 0 行并插入幻灯片。
