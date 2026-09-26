# 方案探索技能

## 工作流程

### 1. 列出所有表格
使用 `sql_db_list_tables` 工具查看数据库中所有可用的表格。

这会返回你可以查询的表格的完整列表。

### 2. 获取特定表格的方案
使用带有表格名称的 `sql_db_schema` 工具来检查：
- **列名称** - 可用的字段有哪些
- **数据类型** - INTEGER、TEXT、DATETIME 等
- **示例数据** - 3 行示例数据以了解内容
- **主键** - 行的唯一标识符
- **外键** - 与其他表格的关系

### 3. 映射关系
识别表格如何连接：
- 查找以 "Id" 结尾的列（例如，CustomerId、ArtistId）
- 外键链接到其他表格中的主键
- 记录父子关系

### 4. 回答问题
提供清晰的信息：
- 可用的表格及其用途
- 列名称及其包含的内容
- 表格如何相互关联
- 示例数据以说明内容

## 示例： "有哪些可用的表格？"

**步骤 1：** 使用 `sql_db_list_tables`

**响应：**
```
Chinook 数据库有 11 个表格：
1. Artist - 音乐艺术家
2. Album - 音乐专辑
3. Track - 单个歌曲
4. Genre - 音乐类型
5. MediaType - 文件格式（MP3、AAC 等）
6. Playlist - 用户创建的播放列表
7. PlaylistTrack - 播放列表中的歌曲
8. Customer - 商店客户
9. Employee - 商店员工
10. Invoice - 客户购买
11. InvoiceLine - 发票中的单个项目
```

## 示例： "Customer 表有哪些列？"

**步骤 1：** 使用带有表格名称 "Customer" 的 `sql_db_schema`

**响应：**
```
Customer 表有这些列：

- CustomerId (INTEGER) - 主键，唯一的客户 ID
- FirstName (NVARCHAR) - 客户的名字
- LastName (NVARCHAR) - 客户的姓氏
- Company (NVARCHAR) - 公司名称（可选）
- Address, City, State, Country, PostalCode - 位置字段
- Phone (NVARCHAR) - 电话号码
- Fax (NVARCHAR) - 传真号码
- Email (NVARCHAR) - 电子邮件地址
- SupportRepId (INTEGER) - 链接到 Employee 表的外键

示例数据显示客户如：
- 来自巴西的 Luís Gonçalves
- 来自德国的 Leonie Köhler
- 来自加拿大的 François Tremblay
```

## 示例： "如何按艺术家查找收入？"

**步骤 1：** 识别需要的表格
- Artist（包含艺术家名称）
- Album（将艺术家链接到歌曲）
- Track（将专辑链接到销售）
- InvoiceLine（包含销售数据）
- Invoice（包含收入总计）

**步骤 2：** 映射关系
```
Artist (ArtistId)
  ↓ 1:many
Album (ArtistId, AlbumId)
  ↓ 1:many
Track (AlbumId, TrackId)
  ↓ 1:many
InvoiceLine (TrackId, UnitPrice, Quantity)
```

**响应：**
```
要按艺术家查找收入，你需要：
1. 从 Artist 表开始
2. JOIN 到 Album 基于 ArtistId
3. JOIN 到 Track 基于 AlbumId
4. JOIN 到 InvoiceLine 基于 TrackId
5. SUM 收入（UnitPrice * Quantity）
6. 按艺术家名称分组

这需要查询编写技能来执行。
```

## 质量指南

**对于 "列出表格" 问题：**
- 显示所有表格名称
- 添加每个表格包含内容的简要描述
- 将相关表格分组（例如，音乐目录、交易、人员）

**对于 "描述表格" 问题：**
- 列出所有列及其数据类型
- 解释每列包含的内容
- 显示示例数据以提供上下文
- 注记主键和外键
- 解释与其他表格的关系

**对于 "如何查询 X" 问题：**
- 识别需要的表格
- 映射 JOIN 路径
- 解释关系链
- 建议下一步（使用查询编写技能）
