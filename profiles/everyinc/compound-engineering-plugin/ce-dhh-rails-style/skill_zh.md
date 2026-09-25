<objective>
将 37signals/DHH Rails 规范应用于 Ruby 和 Rails 代码。这项技能提供了从分析生产环境 37signals 代码库（Fizzy/Campfire）和 DHH 的代码审查模式中提取的综合领域专业知识。
</objective>

<essential_principles>
## 核心理念

"最好的代码是你不需要编写的代码。第二好的代码是明显正确的代码。"

**Vanilla Rails 足够丰富：**
- 丰富的领域模型而非服务对象
- CRUD 控制器而非自定义动作
- 用于水平代码共享的 Concerns
- 记录作为状态而非布尔列
- 所有东西都依赖数据库（不使用 Redis）
- 在寻找 gem 之前构建解决方案

**他们故意避免的：**
- devise（自定义约 150 行的认证）
- pundit/cancancan（模型中的简单角色检查）
- sidekiq（Solid Queue 使用数据库）
- redis（所有东西都依赖数据库）
- view_component（部分工作得很好）
- GraphQL（带有 Turbo 的 REST 足够）
- factory_bot（ fixtures 更简单）
- rspec（Minitest 随 Rails 提供）
- Tailwind（带有层级的原生 CSS）

**开发理念：**
- 发送、验证、完善 - 原型质量的代码到生产环境以学习
- 修复根本原因而非症状
- 写时操作而非读时计算
- 数据库约束而非 ActiveRecord 验证
</essential_principles>

<intake>
你正在做什么？

1. **控制器** - REST 映射、Concerns、Turbo 响应、API 模式
2. **模型** - Concerns、状态记录、回调、作用域、POROs
3. **视图和前端** - Turbo、Stimulus、CSS、部分
4. **架构** - 路由、多租户、认证、作业、缓存
5. **测试** - Minitest、fixtures、集成测试
6. **Gems 和依赖项** - 使用什么与避免什么
7. **代码审查** - 根据 DHH 风格审查代码
8. **一般指导** - 理念和规范

**指定一个数字或描述你的任务。**
</intake>

<routing>

| 响应 | 参考 |
|------|------|
| 1, 控制器 | `references/controllers.md` |
| 2, 模型 | `references/models.md` |
| 3, 视图、前端、turbo、stimulus、css | `references/frontend.md` |
| 4, 架构、路由、认证、作业、缓存 | `references/architecture.md` |
| 5, 测试、测试、minitest、fixture | `references/testing.md` |
| 6, gem、依赖项、库 | `references/gems.md` |
| 7, 审查 | 读取所有参考，然后审查代码 |
| 8, 一般任务 | 根据上下文读取相关参考 |

**在读取相关参考后，将模式应用于用户的代码。**
</routing>

<quick_reference>
## 命名规范

**动词：** `card.close`, `card.gild`, `board.publish`（不是 `set_style` 方法）

**谓词：** `card.closed?`, `card.golden?`（根据相关记录的存在推导）

**Concerns：** 描述能力的形容词（`Closeable`, `Publishable`, `Watchable`）

**控制器：** 与资源匹配的名词（`Cards::ClosuresController`）

**作用域：**
- `chronologically`, `reverse_chronologically`, `alphabetically`, `latest`
- `preloaded`（标准的 eager loading 名称）
- `indexed_by`, `sorted_by`（参数化）
- `active`, `unassigned`（业务术语，不是 SQL 似的）

## REST 映射

创建新资源而不是自定义动作：

```
POST /cards/:id/close    → POST /cards/:id/closure
DELETE /cards/:id/close  → DELETE /cards/:id/closure
POST /cards/:id/archive  → POST /cards/:id/archival
```

## Ruby 语法偏好

```ruby
# 带有括号内空格的符号数组
before_action :set_message, only: %i[ show edit update destroy ]

# 私有方法缩进
  private
    def set_message
      @message = Message.find(params[:id])
    end

# 无表达式的 case 用于条件语句
case
when params[:before].present?
  messages.page_before(params[:before])
else
  messages.last_page
end

# Bang 方法用于快速失败
@message = Message.create!(params)

# Ternaries 用于简单条件
@room.direct? ? @room.users : @message.mentionees
```

## 关键模式

**状态作为记录：**
```ruby
Card.joins(:closure)         # 已关闭的卡片
Card.where.missing(:closure) # 打开的卡片
```

**当前属性：**
```ruby
belongs_to :creator, default: -> { Current.user }
```

**模型上的授权：**
```ruby
class User < ApplicationRecord
  def can_administer?(message)
    message.creator == self || admin?
  end
end
```
</quick_reference>

<reference_index>
## 领域知识

所有详细模式在 `references/`：

| 文件 | 主题 |
|------|------|
| `references/controllers.md` | REST 映射、Concerns、Turbo 响应、API 模式、HTTP 缓存 |
| `references/models.md` | Concerns、状态记录、回调、作用域、POROs、授权、广播 |
| `references/frontend.md` | Turbo Streams、Stimulus 控制器、CSS 层级、OKLCH 颜色、部分 |
| `references/architecture.md` | 路由、认证、作业、Current 属性、缓存、数据库模式 |
| `references/testing.md` | Minitest、fixtures、单元/集成/系统测试、测试模式 |
| `references/gems.md` | 他们使用什么与避免什么、决策框架、Gemfile 示例 |
</reference_index>

<success_criteria>
代码遵循 DHH 风格当且仅当：
- 控制器映射到资源的 CRUD 动词
- 模型使用 Concerns 进行水平行为
- 状态通过记录跟踪而非布尔值
- 没有不必要的服务对象或抽象
- 优先使用数据库解决方案而非外部服务
- 测试使用 Minitest 和 fixtures
- Turbo/Stimulus 用于交互（不使用重型 JS 框架）
- 原生 CSS 带有现代特性（层级、OKLCH、嵌套）
- 授权逻辑存在于 User 模型
- 作业是调用模型方法的浅层包装
</success_criteria>

<credits>
基于 [The Unofficial 37signals/DHH Rails Style Guide](https://github.com/marckohlbrugge/unofficial-37signals-coding-style-guide) 由 [Marc Köhlbrugge](https://x.com/marckohlbrugge) 编写，通过深度分析 Fizzy 代码库的 265 个 pull requests 生成。

**重要免责声明：**
- LLM 生成的指南 - 可能包含不准确之处
- Fizzy 的代码示例根据 O'Saasy 许可证授权
- 与 37signals 无关联或认可
</credits>
