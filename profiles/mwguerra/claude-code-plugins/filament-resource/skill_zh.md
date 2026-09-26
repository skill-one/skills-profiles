# FilamentPHP 资源生成技能

## 概述

该技能可生成完整的 FilamentPHP v4 资源，包括表单模式、表格配置、关系管理器和自定义页面。所有生成的代码均遵循官方文档规范。

## 文档参考

**重要提示：** 在生成任何资源之前，请阅读：
- `/home/mwguerra/projects/mwguerra/claude-code-plugins/filament-specialist/skills/filament-docs/references/general/03-resources/`
- `/home/mwguerra/projects/mwguerra/claude-code-plugins/filament-specialist/skills/filament-docs/references/forms/`
- `/home/mwguerra/projects/mwguerra/claude-code-plugins/filament-specialist/skills/filament-docs/references/tables/`

## 工作流程

### 第一步：收集需求

识别：
- 模型名称和命名空间
- 表单中包含的字段
- 表格中显示的列
- 需要管理的关系
- 需要的自定义操作
- 授权要求

### 第二步：生成基础资源

使用 Laravel artisan 命令创建资源：

```bash
# 基础资源
php artisan make:filament-resource ModelName

# 带生成标志（从模型创建表单/表格）
php artisan make:filament-resource ModelName --generate

# 支持软删除
php artisan make:filament-resource ModelName --soft-deletes

# 仅视图页面
php artisan make:filament-resource ModelName --view

# 简单资源（使用模态表单代替页面）
php artisan make:filament-resource ModelName --simple
```

### 第三步：自定义表单模式

阅读表单字段文档并实现：

```php
use Filament\Forms;
use Filament\Forms\Form;

public static function form(Form $form): Form
{
    return $form
        ->schema([
            Forms\Components\Section::make('基本信息')
                ->schema([
                    Forms\Components\TextInput::make('name')
                        ->required()
                        ->maxLength(255),
                    Forms\Components\Textarea::make('description')
                        ->rows(3)
                        ->columnSpanFull(),
                ]),
            Forms\Components\Section::make('设置')
                ->schema([
                    Forms\Components\Toggle::make('is_active')
                        ->default(true),
                    Forms\Components\Select::make('status')
                        ->options([
                            'draft' => '草稿',
                            'published' => '已发布',
                        ]),
                ]),
        ]);
}
```

### 第四步：自定义表格

阅读表格文档并实现：

```php
use Filament\Tables;
use Filament\Tables\Table;

public static function table(Table $table): Table
{
    return $table
        ->columns([
            Tables\Columns\TextColumn::make('name')
                ->searchable()
                ->sortable(),
            Tables\Columns\IconColumn::make('is_active')
                ->boolean(),
            Tables\Columns\BadgeColumn::make('status')
                ->colors([
                    'warning' => 'draft',
                    'success' => 'published',
                ]),
            Tables\Columns\TextColumn::make('created_at')
                ->dateTime()
                ->sortable()
                ->toggleable(isToggledHiddenByDefault: true),
        ])
        ->filters([
            Tables\Filters\SelectFilter::make('status')
                ->options([
                    'draft' => '草稿',
                    'published' => '已发布',
                ]),
            Tables\Filters\TernaryFilter::make('is_active'),
        ])
        ->actions([
            Tables\Actions\ViewAction::make(),
            Tables\Actions\EditAction::make(),
            Tables\Actions\DeleteAction::make(),
        ])
        ->bulkActions([
            Tables\Actions\BulkActionGroup::make([
                Tables\Actions\DeleteBulkAction::make(),
            ]),
        ]);
}
```

### 第五步：添加关系管理器

对于关系，创建关系管理器：

```bash
php artisan make:filament-relation-manager ResourceName RelationName column_name
```

在资源中注册：

```php
public static function getRelations(): array
{
    return [
        RelationManagers\CommentsRelationManager::class,
        RelationManagers\TagsRelationManager::class,
    ];
}
```

### 第六步：配置页面

定义资源页面：

```php
public static function getPages(): array
{
    return [
        'index' => Pages\ListModels::route('/'),
        'create' => Pages\CreateModel::route('/create'),
        'view' => Pages\ViewModel::route('/{record}'),
        'edit' => Pages\EditModel::route('/{record}/edit'),
    ];
}
```

### 第七步：添加授权

实现策略方法：

```php
public static function canViewAny(): bool
{
    return auth()->user()->can('view_any_model');
}

public static function canCreate(): bool
{
    return auth()->user()->can('create_model');
}
```

## 表单字段参考

### 文本字段
- `TextInput::make()` - 单行文本
- `Textarea::make()` - 多行文本
- `RichEditor::make()` -所见即所得编辑器
- `MarkdownEditor::make()` - Markdown 编辑器

### 选择字段
- `Select::make()` - 下拉选择
- `Radio::make()` - 单选按钮
- `Checkbox::make()` - 单个复选框
- `CheckboxList::make()` - 多个复选框
- `Toggle::make()` - 开关

### 日期/时间字段
- `DatePicker::make()` - 仅日期
- `DateTimePicker::make()` - 日期和时间
- `TimePicker::make()` - 仅时间

### 文件字段
- `FileUpload::make()` - 文件上传
- `SpatieMediaLibraryFileUpload::make()` - 媒体库

### 关系字段
- `Select::make()->relationship()` - BelongsTo 选择
- `CheckboxList::make()->relationship()` - BelongsToMany
- `Repeater::make()->relationship()` - HasMany 内联

### 布局组件
- `Section::make()` - 卡片区域
- `Fieldset::make()` - 字段分组
- `Tabs::make()` - 标签区域
- `Grid::make()` - 网格布局
- `Split::make()` - 分割布局

## 表格列参考

### 文本列
- `TextColumn::make()` - 基本文本
- `IconColumn::make()` - 布尔图标
- `ImageColumn::make()` - 图片缩略图
- `BadgeColumn::make()` - 徽章样式
- `ColorColumn::make()` - 颜色样本

### 列修饰符
- `->searchable()` - 启用搜索
- `->sortable()` - 启用排序
- `->toggleable()` - 可隐藏/显示
- `->wrap()` - 文本换行
- `->limit()` - 截断文本

## 输出

对于每个资源，生成：

1. **资源类** - `app/Filament/Resources/ModelResource.php`
2. **页面** - `app/Filament/Resources/ModelResource/Pages/`
3. **关系管理器** - `app/Filament/Resources/ModelResource/RelationManagers/`
4. **测试文件** - `tests/Feature/Filament/ModelResourceTest.php`
