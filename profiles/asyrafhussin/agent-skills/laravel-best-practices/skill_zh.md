# Laravel 13 最佳实践

针对 Laravel 13 应用的全面最佳实践指南。包含 7 个类别中的 31 条规则，用于构建可扩展、可维护的 Laravel 应用。

## 何时应用

在以下情况下参考这些指南：
- 创建控制器、模型和服务
- 编写迁移和数据库查询
- 实现验证和表单请求
- 使用 Laravel 构建 API
- 结构化 Laravel 应用

## 按优先级划分的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | 架构与结构 | 关键 | `arch-` |
| 2 | Eloquent & 数据库 | 关键 | `eloquent-` |
| 3 | 控制器 & 路由 | 高 | `controller-`, `ctrl-` |
| 4 | 验证 & 请求 | 高 | `validation-`, `valid-` |
| 5 | 安全 | 高 | `sec-` |
| 6 | 性能 | 中 | `perf-` |
| 7 | API 设计 | 中 | `api-` |

## 快速参考

### 1. 架构与结构 (关键)

- `arch-service-classes` - 将业务逻辑提取到服务中
- `arch-action-classes` - 单用途动作类
- `arch-repository-pattern` - 何时使用仓库模式
- `arch-dto-pattern` - 数据传输对象
- `arch-value-objects` - 封装领域概念
- `arch-event-driven` - 使用事件和监听器解耦
- `arch-feature-folders` - 按领域/功能组织
- `arch-queue-routing` - 集中化任务队列路由（Laravel 13+）

### 2. Eloquent & 数据库 (关键)

- `eloquent-eager-loading` - 防止 N+1 查询
- `eloquent-chunking` - 处理大型数据集
- `eloquent-query-scopes` - 可重用的查询逻辑
- `eloquent-model-events` - 使用观察者处理副作用
- `eloquent-relationships` - 正确定义关系
- `eloquent-casts` - 自动属性转换
- `eloquent-accessors-mutators` - 转换属性
- `eloquent-soft-deletes` - 安全删除并支持恢复
- `eloquent-pruning` - 自动清理旧记录
- `eloquent-vector-search` - 使用 pgvector 进行语义搜索（Laravel 13+）

### 3. 控制器 & 路由 (高)

- `controller-resource-controllers` - 使用资源控制器
- `controller-single-action` - 单动作可调用控制器
- `controller-resource-methods` - RESTful 资源方法
- `controller-form-requests` - 使用表单请求
- `controller-api-resources` - 转换 API 响应
- `controller-middleware` - 正确应用中间件
- `controller-dependency-injection` - 注入依赖

### 4. 验证 & 请求 (高)

- `validation-form-requests` - 使用表单请求类
- `validation-custom-rules` - 创建自定义规则
- `validation-conditional-rules` - 条件验证
- `validation-array-validation` - 验证嵌套数组
- `validation-after-hooks` - 复杂验证逻辑

### 5. 安全 (高)

- `sec-mass-assignment` - 防止批量赋值

### 6. 性能 (中)

本类别尚无规则文件。

### 7. API 设计 (中)

本类别尚无规则文件。

## 基本模式

### 带表单请求的控制器

```php
<?php

namespace App\Http\Controllers;

use App\Http\Requests\StorePostRequest;
use App\Http\Requests\UpdatePostRequest;
use App\Models\Post;
use Illuminate\Http\RedirectResponse;

class PostController extends Controller
{
    public function store(StorePostRequest $request): RedirectResponse
    {
        // 自动进行验证
        $validated = $request->validated();

        $post = Post::create($validated);

        return redirect()
            ->route('posts.show', $post)
            ->with('success', 'Post created successfully.');
    }

    public function update(UpdatePostRequest $request, Post $post): RedirectResponse
    {
        $post->update($request->validated());

        return redirect()
            ->route('posts.show', $post)
            ->with('success', 'Post updated successfully.');
    }
}
```

### 表单请求类

```php
<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class StorePostRequest extends FormRequest
{
    public function authorize(): bool
    {
        return $this->user()->can('create', Post::class);
    }

    public function rules(): array
    {
        return [
            'title' => ['required', 'string', 'max:255'],
            'body' => ['required', 'string', 'min:100'],
            'category_id' => ['required', 'exists:categories,id'],
            'tags' => ['nullable', 'array'],
            'tags.*' => ['exists:tags,id'],
            'published_at' => ['nullable', 'date', 'after:now'],
        ];
    }

    public function messages(): array
    {
        return [
            'body.min' => 'The post body must be at least 100 characters.',
        ];
    }
}
```

### 服务类模式

```php
<?php

namespace App\Services;

use App\Models\User;
use App\Models\Post;
use App\Events\PostPublished;
use Illuminate\Support\Facades\DB;

class PostService
{
    public function __construct(
        private readonly NotificationService $notifications,
    ) {}

    public function publish(Post $post): Post
    {
        return DB::transaction(function () use ($post) {
            $post->update([
                'published_at' => now(),
                'status' => 'published',
            ]);

            event(new PostPublished($post));

            $this->notifications->notifyFollowers($post->author, $post);

            return $post->fresh();
        });
    }
}
```

### Eloquent 模型

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Builder;

class Post extends Model
{
    use HasFactory;

    protected $fillable = [
        'title',
        'slug',
        'body',
        'category_id',
        'published_at',
    ];

    protected $casts = [
        'published_at' => 'datetime',
    ];

    // 关系
    public function author(): BelongsTo
    {
        return $this->belongsTo(User::class, 'user_id');
    }

    public function category(): BelongsTo
    {
        return $this->belongsTo(Category::class);
    }

    public function tags(): BelongsToMany
    {
        return $this->belongsToMany(Tag::class)->withTimestamps();
    }

    // 范围
    public function scopePublished(Builder $query): Builder
    {
        return $query->whereNotNull('published_at')
            ->where('published_at', '<=', now());
    }

    public function scopeByCategory(Builder $query, int $categoryId): Builder
    {
        return $query->where('category_id', $categoryId);
    }

    // 访问器和修改器
    protected function title(): Attribute
    {
        return Attribute::make(
            set: fn (string $value) => ucfirst($value),
        );
    }
}
```

### 迁移最佳实践

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('posts', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->foreignId('category_id')->constrained()->cascadeOnDelete();
            $table->string('title');
            $table->string('slug')->unique();
            $table->text('body');
            $table->timestamp('published_at')->nullable();
            $table->timestamps();

            // 常用查询的索引
            $table->index(['user_id', 'published_at']);
            $table->index('category_id');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('posts');
    }
};
```

### 嵌套加载

```php
// N+1 问题
$posts = Post::all();
foreach ($posts as $post) {
    echo $post->author->name;  // 每个帖子查询一次
}

// 嵌套加载 - 总共 3 个查询
$posts = Post::with(['author', 'category', 'tags'])->get();
foreach ($posts as $post) {
    echo $post->author->name;  // 无额外查询
}

// 嵌套加载
$posts = Post::with([
    'author.profile',
    'comments.user',
    'tags',
])->get();

// 受约束的嵌套加载
$posts = Post::with([
    'comments' => fn ($query) => $query->latest()->limit(5),
])->get();
```

## 如何使用

阅读单个规则文件以获取详细说明和代码示例：

```
rules/arch-service-classes.md
rules/eloquent-eager-loading.md
rules/validation-form-requests.md
rules/_sections.md
```

每个规则文件包含：
- 带有元数据的 YAML 前置（标题、影响、标签）
- 解释为什么这很重要
- 坏示例及说明
- 好示例及说明
- Laravel 13 和 PHP 8.3 特定上下文和参考

## 完整编译文档

获取包含所有规则扩展的完整指南：`AGENTS.md`
