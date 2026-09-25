# 办公生产力工作流套件

## 概述

使用LibreOffice和Microsoft Office工具，实现文档创建、电子表格自动化、演示文稿生成和格式转换的全面办公生产力工作流。

## 何时使用此工作流

当您需要：
- 程序化创建办公文档
- 自动化文档工作流
- 在文档格式之间转换
- 生成报告
- 从数据创建演示文稿
- 处理电子表格

## 工作流阶段

### 阶段1：文档创建

#### 需要调用的技能
- `libreoffice-writer` - LibreOffice Writer
- `docx-official` - Microsoft Word
- `pdf-official` - PDF处理

#### 操作步骤
1. 设计文档模板
2. 创建文档结构
3. 程序化添加内容
4. 应用格式
5. 导出所需格式

#### 复制粘贴提示
```
使用@libreoffice-writer创建ODT文档
```

```
使用@docx-official创建Word文档
```

### 阶段2：电子表格自动化

#### 需要调用的技能
- `libreoffice-calc` - LibreOffice Calc
- `xlsx-official` - Excel电子表格
- `googlesheets-automation` - Google Sheets

#### 操作步骤
1. 设计电子表格结构
2. 创建公式
3. 导入数据
4. 生成图表
5. 导出报告

#### 复制粘贴提示
```
使用@libreoffice-calc创建ODS电子表格
```

```
使用@xlsx-official创建Excel报告
```

### 阶段3：演示文稿生成

#### 需要调用的技能
- `libreoffice-impress` - LibreOffice Impress
- `pptx-official` - PowerPoint
- `frontend-slides` - HTML幻灯片
- `nanobanana-ppt-skills` - AI PPT生成

#### 操作步骤
1. 设计幻灯片模板
2. 从数据生成幻灯片
3. 添加图表和图形
4. 应用动画
5. 导出演示文稿

#### 复制粘贴提示
```
使用@libreoffice-impress创建ODP演示文稿
```

```
使用@pptx-official创建PowerPoint演示文稿
```

```
使用@frontend-slides创建HTML演示文稿
```

### 阶段4：格式转换

#### 需要调用的技能
- `libreoffice-writer` - 文档转换
- `libreoffice-calc` - 电子表格转换
- `pdf-official` - PDF转换

#### 操作步骤
1. 确定源格式
2. 选择目标格式
3. 执行转换
4. 验证质量
5. 批量处理文件

#### 复制粘贴提示
```
使用@libreoffice-writer转换文档
```

### 阶段5：文档自动化

#### 需要调用的技能
- `libreoffice-writer` - 邮件合并
- `workflow-automation` - 工作流自动化
- `file-organizer` - 文件组织

#### 操作步骤
1. 设计自动化工作流
2. 创建模板
3. 设置数据源
4. 生成文档
5. 分发输出

#### 复制粘贴提示
```
使用@libreoffice-writer执行邮件合并
```

```
使用@workflow-automation自动化文档工作流
```

### 阶段6：图形和图表

#### 需要调用的技能
- `libreoffice-draw` - 矢量图形
- `canvas-design` - 画布设计
- `mermaid-expert` - 图表生成

#### 操作步骤
1. 设计图形
2. 创建图表
3. 生成图表
4. 导出图像
5. 与文档集成

#### 复制粘贴提示
```
使用@libreoffice-draw创建矢量图形
```

```
使用@mermaid-expert创建图表
```

### 阶段7：数据库集成

#### 需要调用的技能
- `libreoffice-base` - LibreOffice Base
- `database-architect` - 数据库设计

#### 操作步骤
1. 连接到数据源
2. 创建表单
3. 设计报告
4. 自动化查询
5. 生成输出

#### 复制粘贴提示
```
使用@libreoffice-base创建数据库报告
```

## 办公应用程序工作流

### LibreOffice
```
技能：libreoffice-writer, libreoffice-calc, libreoffice-impress, libreoffice-draw, libreoffice-base
格式：ODT, ODS, ODP, ODG, ODB
```

### Microsoft Office
```
技能：docx-official, xlsx-official, pptx-official
格式：DOCX, XLSX, PPTX
```

### Google Workspace
```
技能：googlesheets-automation, google-drive-automation, gmail-automation
格式：Google Docs, Sheets, Slides
```

## 质量门禁

- [ ] 文档格式正确
- [ ] 公式正常工作
- [ ] 演示文稿完整
- [ ] 转换成功
- [ ] 自动化测试
- [ ] 文件组织

## 相关工作流套件

- `development` - 应用开发
- `documentation` - 文档生成
- `database` - 数据集成

## 限制

- 仅在任务明确符合上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家评审的替代品。
- 如果缺少必要的输入、权限、安全边界或成功标准，请停止并请求澄清。
