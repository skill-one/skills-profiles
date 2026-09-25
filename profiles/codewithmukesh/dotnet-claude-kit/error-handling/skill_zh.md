# 错误处理

## 核心原则

1. **使用结果模式处理预期失败** — 不要为“订单未找到”或“验证失败”等异常情况抛出异常。这些是预期结果，而非异常条件。参见 ADR-002。
2. **保留异常处理预期失败** — 数据库连接丢失、空引用错误、网络超时——这些才是真正的异常情况，应传递给全局处理器。
3. **每个 API 错误返回 ProblemDetails** — RFC 9457 是标准。每个错误响应都包含 `type`、`title`、`status`、`detail`，以及可选的 `errors`。
4. **在边界处验证** — 在 API 层面验证传入请求，而不是深嵌在业务逻辑中。

## 模式

### 结果模式

一个简单、通用的结果类型，携带值或错误。

```csharp
public class Result
{
    public bool IsSuccess { get; }
    public bool IsFailure => !IsSuccess;
    public List<string> Errors { get; }

    protected Result(bool isSuccess, List<string>? errors = null)
    {
        IsSuccess = isSuccess;
        Errors = errors ?? [];
    }

    public static Result Success() => new(true);
    public static Result Failure(params string[] errors) => new(false, [..errors]);
    public static Result<T> Success<T>(T value) => new(value);
    public static Result<T> Failure<T>(params string[] errors) => new(errors);
}

public class Result<T> : Result
{
    public T Value { get; }

    internal Result(T value) : base(true) => Value = value;
    internal Result(IEnumerable<string> errors) : base(false, [..errors]) => Value = default!;
}
```

### 结果到 ProblemDetails 的映射

```csharp
public static class ResultExtensions
{
    public static IResult ToProblemDetails(this Result result, int statusCode = 400)
    {
        return TypedResults.Problem(
            title: "One or more errors occurred",
            statusCode: statusCode,
            extensions: new Dictionary<string, object?>
            {
                ["errors"] = result.Errors
            });
    }
}

// 在端点中使用
group.MapPost("/", async (CreateOrder.Command command, ISender sender, CancellationToken ct) =>
{
    var result = await sender.Send(command, ct);
    return result.IsSuccess
        ? TypedResults.Created($"/api/orders/{result.Value.Id}", result.Value)
        : result.ToProblemDetails();
});
```

### 全局异常处理器

捕获预期之外的异常并将其转换为 ProblemDetails。对于现代 `IExceptionHandler` 方法（推荐），参见 `knowledge/common-infrastructure.md`。以下内联 lambda 适用于简单场景：

```csharp
// Program.cs
app.UseExceptionHandler(errorApp =>
{
    errorApp.Run(async context =>
    {
        var exception = context.Features.Get<IExceptionHandlerFeature>()?.Error;
        var logger = context.RequestServices.GetRequiredService<ILogger<Program>>();

        logger.LogError(exception, "Unhandled exception for {Method} {Path}",
            context.Request.Method, context.Request.Path);

        var problem = new ProblemDetails
        {
            Title = "An unexpected error occurred",
            Status = StatusCodes.Status500InternalServerError,
            Type = "https://tools.ietf.org/html/rfc9110#section-15.6.1"
        };

        // 生产环境不要泄露细节
        if (context.RequestServices.GetRequiredService<IHostEnvironment>().IsDevelopment())
        {
            problem.Detail = exception?.Message;
        }

        context.Response.StatusCode = problem.Status.Value;
        await context.Response.WriteAsJsonAsync(problem);
    });
});
```

### FluentValidation 与端点过滤器

```csharp
// 验证器
public class CreateOrderValidator : AbstractValidator<CreateOrderRequest>
{
    public CreateOrderValidator()
    {
        RuleFor(x => x.CustomerId)
            .NotEmpty().WithMessage("Customer ID is required");

        RuleFor(x => x.Items)
            .NotEmpty().WithMessage("At least one item is required");

        RuleForEach(x => x.Items).ChildRules(item =>
        {
            item.RuleFor(x => x.ProductId).NotEmpty();
            item.RuleFor(x => x.Quantity).GreaterThan(0);
        });
    }
}

// 通用验证过滤器
public class ValidationFilter<TRequest> : IEndpointFilter
{
    public async ValueTask<object?> InvokeAsync(
        EndpointFilterInvocationContext context,
        EndpointFilterDelegate next)
    {
        var validator = context.HttpContext.RequestServices.GetService<IValidator<TRequest>>();
        if (validator is null)
            return await next(context);

        var request = context.Arguments.OfType<TRequest>().FirstOrDefault();
        if (request is null)
            return await next(context);

        var result = await validator.ValidateAsync(request);
        if (!result.IsValid)
        {
            return TypedResults.ValidationProblem(result.ToDictionary());
        }

        return await next(context);
    }
}

// 注册
group.MapPost("/", CreateOrder)
    .AddEndpointFilter<ValidationFilter<CreateOrderRequest>>();
```

### 带类型错误结果

为更丰富的错误处理，使用类型化的错误枚举或错误对象。

```csharp
public abstract record Error(string Code, string Message);
public record NotFoundError(string Entity, object Id)
    : Error("not_found", $"{Entity} with ID {Id} was not found");
public record ValidationError(string Field, string Message)
    : Error("validation", Message);
public record ConflictError(string Message)
    : Error("conflict", Message);

// 映射到 HTTP 状态码
public static IResult ToHttpResult(this Error error) => error switch
{
    NotFoundError => TypedResults.Problem(title: error.Message, statusCode: 404),
    ValidationError => TypedResults.Problem(title: error.Message, statusCode: 400),
    ConflictError => TypedResults.Problem(title: error.Message, statusCode: 409),
    _ => TypedResults.Problem(title: error.Message, statusCode: 500)
};
```

## 反模式

### 不要为流程控制抛出异常

```csharp
// BAD — 为预期结果抛出异常
public Order GetOrder(Guid id)
{
    var order = db.Orders.Find(id)
        ?? throw new NotFoundException($"Order {id} not found");
    return order;
}

// GOOD — 结果模式
public Result<Order> GetOrder(Guid id)
{
    var order = db.Orders.Find(id);
    return order is not null
        ? Result.Success(order)
        : Result.Failure<Order>($"Order {id} not found");
}
```

### 不要从 API 返回原始错误字符串

```csharp
// BAD — 不一致的错误格式
return Results.BadRequest("Something went wrong");
return Results.BadRequest(new { error = "Invalid input" });

// GOOD — 始终返回 ProblemDetails
return TypedResults.Problem(title: "Invalid input", statusCode: 400);
return TypedResults.ValidationProblem(validationResult.ToDictionary());
```

### 不要捕获并吞掉异常

```csharp
// BAD — 沉默地吞掉
try { await ProcessOrder(order); }
catch (Exception) { /* ignore */ }

// GOOD — 记录并适当处理
try { await ProcessOrder(order); }
catch (PaymentException ex)
{
    logger.LogWarning(ex, "Payment failed for order {OrderId}", order.Id);
    return Result.Failure<Order>("Payment processing failed");
}
```

## 决策指南

| 场景 | 建议 |
|------|------|
| 预期的业务失败 | 结果模式 |
| 输入验证 | FluentValidation 与端点过滤器 |
| 预期之外的崩溃 | 全局异常处理器 → ProblemDetails |
| API 错误格式 | RFC 9457 ProblemDetails — 始终 |
| 处理器中的验证 | 返回 Result.Failure，不要抛出 |
| 外部服务失败 | 捕获特定异常，返回 Result.Failure |
| 记录错误 | 带关联 ID 的结构化日志记录 |
