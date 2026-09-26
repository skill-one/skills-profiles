# Eloquent 最佳实践

## 查询优化

### 始终使用预加载关联

```php
// ❌ N+1 查询问题
$posts = Post::all();
foreach ($posts as $post) {
    echo $post->user->name; // 额外 N 个查询
}

// ✅ 预加载
$posts = Post::with('user')->get();
foreach ($posts as $post) {
    echo $post->user->name; // 无额外查询
}
```

### 仅选择需要的列

```php
// ❌ 获取所有列
$users = User::all();

// ✅ 仅需要的列
$users = User::select(['id', 'name', 'email'])->get();

// ✅ 带关联
$posts = Post::with(['user:id,name'])->select(['id', 'title', 'user_id'])->get();
```

### 使用查询范围

```php
// ✅ 定义可重用的查询逻辑
class Post extends Model
{
    public function scopePublished($query)
    {
        return $query->where('status', 'published')
                    ->whereNotNull('published_at');
    }
    
    public function scopePopular($query, $threshold = 100)
    {
        return $query->where('views', '>', $threshold);
    }
}

// 使用
$posts = Post::published()->popular()->get();
```

## 关联最佳实践

### 定义返回类型

```php
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Post extends Model
{
    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }
    
    public function comments(): HasMany
    {
        return $this->hasMany(Comment::class);
    }
}
```

### 使用 withCount 获取计数

```php
// ❌ 触发额外查询
foreach ($posts as $post) {
    echo $post->comments()->count();
}

// ✅ 高效加载计数
$posts = Post::withCount('comments')->get();
foreach ($posts as $post) {
    echo $post->comments_count;
}
```

## 批量赋值保护

```php
class Post extends Model
{
    // ✅ 白名单可填充属性
    protected $fillable = ['title', 'content', 'status'];
    
    // 或黑名单受保护属性
    protected $guarded = ['id', 'user_id'];
    
    // ❌ 切勿这样做
    // protected $guarded = [];
}
```

## 使用 Casts 保证类型安全

```php
class Post extends Model
{
    protected $casts = [
        'published_at' => 'datetime',
        'metadata' => 'array',
        'is_featured' => 'boolean',
        'views' => 'integer',
    ];
}
```

## 大数据集分块处理

```php
// ✅ 分块处理以节省内存
Post::chunk(200, function ($posts) {
    foreach ($posts as $post) {
        // 处理每个帖子
    }
});

// ✅ 或使用惰性集合
Post::lazy()->each(function ($post) {
    // 逐个处理
});
```

## 数据库级别操作

```php
// ❌ 慢 - 首先加载到内存
$posts = Post::where('status', 'draft')->get();
foreach ($posts as $post) {
    $post->update(['status' => 'archived']);
}

// ✅ 快 - 单个查询
Post::where('status', 'draft')->update(['status' => 'archived']);

// ✅ 自增/自减
Post::where('id', $id)->increment('views');
```

## 合理使用模型事件

```php
class Post extends Model
{
    protected static function booted()
    {
        static::creating(function ($post) {
            $post->slug = Str::slug($post->title);
        });
        
        static::deleting(function ($post) {
            $post->comments()->delete();
        });
    }
}
```

## 常见陷阱避免

### 循环中不要查询

```php
// ❌ 不良
foreach ($userIds as $id) {
    $user = User::find($id);
}

// ✅ 良好
$users = User::whereIn('id', $userIds)->get();
```

### 不要忘记索引

```php
// 迁移
Schema::create('posts', function (Blueprint $table) {
    $table->id();
    $table->foreignId('user_id')->constrained()->index();
    $table->string('slug')->unique();
    $table->string('status')->index();
    $table->timestamp('published_at')->nullable()->index();
    
    // 常见查询的复合索引
    $table->index(['status', 'published_at']);
});
```

### 开发环境中防止惰性加载

```php
// 在 AppServiceProvider 的 boot 方法中
Model::preventLazyLoading(!app()->isProduction());
```

## 检查清单

- [ ] 在需要的地方预加载关联
- [ ] 仅选择所需列
- [ ] 使用查询范围实现可重用性
- [ ] 配置批量赋值保护
- [ ] 定义适当的 Casts
- [ ] 外键和查询列上设置索引
- [ ] 尽可能使用数据库级别操作
- [ ] 大数据集分块处理
- [ ] 合理使用模型事件
- [ ] 开发环境中防止惰性加载
