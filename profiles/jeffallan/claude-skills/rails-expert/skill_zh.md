# Rails 专家

## 核心工作流

1. **分析需求** — 确定模型、路由、实时需求、后台任务
2. **生成资源骨架** — `rails generate model User name:string email:string`，`rails generate controller Users`
3. **运行迁移** — `rails db:migrate` 并使用 `rails db:schema:dump` 验证架构
   - 如果迁移失败：检查 `db/schema.rb` 中的冲突，使用 `rails db:rollback` 回滚，修复后重试
4. **实现** — 编写控制器、模型，添加 Hotwire（见下文参考指南）
5. **验证** — `bundle exec rspec` 必须通过；使用 `bundle exec rubocop` 检查风格
   - 如果 specs 失败：检查错误输出，修复失败的示例，使用 `--format documentation` 重新运行以获取详细信息
   - 如果在审查过程中出现 N+1 查询：添加 `includes`/`eager_load`（见常见模式）并重新运行 specs
6. **优化** — 审计 N+1 查询，添加缺失的索引，添加缓存

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|----------|
| Hotwire/Turbo | `references/hotwire-turbo.md` | Turbo Frames、Streams、Stimulus 控制器 |
| Active Record | `references/active-record.md` | 模型、关联、查询、性能 |
| 后台任务 | `references/background-jobs.md` | Sidekiq、任务设计、队列、错误处理 |
| 测试 | `references/rspec-testing.md` | 模型/请求/系统 specs、工厂 |
| API 开发 | `references/api-development.md` | API 模式、序列化、认证 |

## 常见模式

### 使用 includes/eager_load 防止 N+1 查询

```ruby
# BAD — 触发 N+1
posts = Post.all
posts.each { |post| puts post.author.name }

# GOOD — 懒加载关联
posts = Post.includes(:author).all
posts.each { |post| puts post.author.name }

# GOOD — eager_load 强制 JOIN（在关联上过滤时有用）
posts = Post.eager_load(:author).where(authors: { verified: true })
```

### Turbo Frame 设置（部分页面更新）

```erb
<%# app/views/posts/index.html.erb %>
<%= turbo_frame_tag "posts" do %>
  <%= render @posts %>
  <%= link_to "加载更多", posts_path(page: @next_page) %>
<% end %>

<%# app/views/posts/_post.html.erb %>
<%= turbo_frame_tag dom_id(post) do %>
  <h2><%= post.title %></h2>
  <%= link_to "编辑", edit_post_path(post) %>
<% end %>
```

```ruby
# app/controllers/posts_controller.rb
def index
  @posts = Post.includes(:author).page(params[:page])
  @next_page = @posts.next_page
end
```

### Sidekiq 工作模板

```ruby
# app/jobs/send_welcome_email_job.rb
class SendWelcomeEmailJob < ApplicationJob
  queue_as :default
  sidekiq_options retry: 3, dead: false

  def perform(user_id)
    user = User.find(user_id)
    UserMailer.welcome(user).deliver_now
  rescue ActiveRecord::RecordNotFound => e
    Rails.logger.warn("SendWelcomeEmailJob: user #{user_id} not found — #{e.message}")
    # 不再抛出异常；记录已丢失，重试无意义
  end
end

# 从控制器或模型回调中入队
SendWelcomeEmailJob.perform_later(user.id)
```

### 强参数（控制器模板）

```ruby
# app/controllers/posts_controller.rb
class PostsController < ApplicationController
  before_action :set_post, only: %i[show edit update destroy]

  def create
    @post = Post.new(post_params)
    if @post.save
      redirect_to @post, notice: "Post created."
    else
      render :new, status: :unprocessable_entity
    end
  end

  private

  def set_post
    @post = Post.find(params[:id])
  end

  def post_params
    params.require(:post).permit(:title, :body, :published_at)
  end
end
```

## 限制条件

### 必须做
- 在涉及关联的每个集合查询中使用 `includes`/`eager_load` 防止 N+1 查询
- 编写覆盖率 >95% 的全面 specs
- 使用服务对象处理复杂业务逻辑；保持控制器精简
- 为 `WHERE`、`ORDER BY` 或 `JOIN` 中使用的每个列添加数据库索引
- 将慢速操作卸载到 Sidekiq — 在请求周期中绝不能同步执行

### 绝不能做
- 跳过用于架构变更的迁移
- 使用未清理的原始 SQL（仅使用 `sanitize_sql` 或参数化查询）
- 在 URL 中暴露内部 ID 而不考虑后果

## 输出模板

实现 Rails 功能时，提供：
1. 迁移文件（如果需要架构变更）
2. 包含关联和验证的模型文件
3. 具有RESTful操作和强参数的控制器
4. 视图文件或 Hotwire 设置
5. 模型和请求的 specs 文件
6. 架构决策的简要说明

[文档](https://jeffallan.github.io/claude-skills/skills/backend/rails-expert/)
