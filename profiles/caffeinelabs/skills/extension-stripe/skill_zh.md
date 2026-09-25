# Stripe支付集成
[Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral)的Stripe支付扩展。

## 概述

该技能通过HTTP调用添加Stripe支付支持。后端管理Stripe配置，创建结账会话并检查支付状态。前端处理结账流程和支付结果页面。

# 后端

对于Stripe支付集成：

前提条件：你必须先遵循[extension-authorization](../extension-authorization/SKILL.md)，因为这个集成依赖于它。

有一个预制模块`mo:caffeineai-stripe/stripe.mo`，它不能被修改。它为后端进行HTTP GET或PUT请求提供基本功能。

```mo:caffeineai-stripe/stripe.mo
import OutCall "mo:caffeineai-http-outcalls/outcall";

module {
  public type StripeConfiguration = {
    secretKey : Text;
    allowedCountries : [Text];
  };

  public type ShoppingItem = {
    currency : Text;
    productName : Text;
    productDescription : Text;
    priceInCents : Nat;
    quantity : Nat;
  };

  /// 初始化购物项的支付会话。
  /// 返回Stripe JSON回复消息。
  public func createCheckoutSession(configuration : StripeConfiguration, caller : Principal, items : [ShoppingItem], successUrl : Text, cancelUrl : Text, transform : OutCall.Transform) : async Text;
  
  public type StripeSessionStatus = {
    #failed : { error : Text };
    #completed : { response : Text; userPrincipal : ?Text };
  };

  /// 检查支付状态。
  public func getSessionStatus(configuration : StripeConfiguration, sessionId : Text, transform : OutCall.Transform) : async StripeSessionStatus;
};
```

使用方法：

```motoko filepath=src/backend/main.mo
import Stripe "mo:caffeineai-stripe/stripe";
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import OutCall "mo:caffeineai-http-outcalls/outcall";
import Map "mo:core/Map";
import Iter "mo:core/Iter";
import Text "mo:core/Text";
import Runtime "mo:core/Runtime";

actor {
    // 包含授权
    let accessControlState : AccessControl.AccessControlState;
    include MixinAuthorization(accessControlState, null);

    // 购物数据
    public type Product = {
        id : Text;
        // 添加自定义字段
    };

    let products : Map.Map<Text, Product>;

    public query func getProducts() : async [Product] {
        products.values().toArray();
    };

    public shared ({ caller }) func addProduct(product : Product) : async () {
        if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
            Runtime.trap("Unauthorized: Only admins can add products");
        };
        products.add(product.id, product);
    };

    public shared ({ caller }) func updateProduct(product : Product) : async () {
        if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
            Runtime.trap("Unauthorized: Only admins can update products");
        };
        products.add(product.id, product);
    };

    public shared ({ caller }) func deleteProduct(productId : Text) : async () {
        if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
            Runtime.trap("Unauthorized: Only admins can delete products");
        };
        products.remove(productId);
    };

    // Stripe集成
    var configuration : ?Stripe.StripeConfiguration;

    public query func isStripeConfigured() : async Bool {
        configuration != null;
    };

    public shared ({ caller }) func setStripeConfiguration(config : Stripe.StripeConfiguration) : async () {
        if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
            Runtime.trap("Unauthorized: Only admins can perform this action");
        };
        configuration := ?config;
    };

    func getStripeConfiguration() : Stripe.StripeConfiguration {
        configuration ?? Runtime.trap("Stripe needs to be first configured");
    };

    public func getStripeSessionStatus(sessionId : Text) : async Stripe.StripeSessionStatus {
        await Stripe.getSessionStatus(getStripeConfiguration(), sessionId, transform);
    };

    public shared ({ caller }) func createCheckoutSession(items : [Stripe.ShoppingItem], successUrl : Text, cancelUrl : Text) : async Text {
        await Stripe.createCheckoutSession(getStripeConfiguration(), caller, items, successUrl, cancelUrl, transform);
    };

    public query func transform(input : OutCall.TransformationInput) : async OutCall.TransformationOutput {
        OutCall.transform(input);
    };

    // 根据需要添加更多数据和函数
};
```

迁移链头部：

```motoko filepath=src/backend/migrations/00000000_000000.mo
import Map "mo:core/Map";
import AccessControl "mo:caffeineai-authorization/access-control";

module {
    type Product = {
        id : Text;
    };

    type StripeConfiguration = {
        secretKey : Text;
        allowedCountries : [Text];
    };

    type NewActor = {
        accessControlState : AccessControl.AccessControlState;
        products : Map.Map<Text, Product>;
        configuration : ?StripeConfiguration;
    };

    public func migration(_old : {}) : NewActor {
        {
            accessControlState = AccessControl.initState();
            products = Map.empty<Text, Product>();
            configuration = null;
        };
    };
};
```

# 前端

对于Stripe支付集成：

使用方法：

1. 实现一个PaymentSetup组件，包含：
    * 使用`isStripeConfigured()`和`setStripeConfiguration()`
    * 检查Stripe支付是否已配置。
    * 如果未配置，打开管理面板并要求用户使用`StripeConfiguration`初始化Stripe。
      - Stripe密钥
      - 允许的国家列表，如["US", "CA", "GB"]等，参见Stripe文档。
    * 当已经配置时，不要显示支付设置！

2. 实现一个结账钩子：
    * 注意需要解析后端`createCheckoutSession`结果的JSON。
    * 验证解析的会话是否包含非空的`url`。如果缺失，抛出错误并不要重定向。
    
    ```
    import { useMutation } from '@tanstack/react-query';
    import { useActor } from '@caffeineai/core-infrastructure';
    import { ShoppingItem } from '../backend';

    export type CheckoutSession = {
        id: string;
        url: string;
    };

    export function useCreateCheckoutSession() {
        const { actor } = useActor();

        return useMutation({
            mutationFn: async (items: ShoppingItem[]): Promise<CheckoutSession> => {
                if (!actor) throw new Error('Actor not available');
                const baseUrl = `${window.location.protocol}//${window.location.host}`;
                const successUrl = `${baseUrl}/payment-success`;
                const cancelUrl = `${baseUrl}/payment-failure`;
                const result = await actor.createCheckoutSession(items, successUrl, cancelUrl);
                // JSON解析很重要！
                const session = JSON.parse(result) as CheckoutSession;
                if (!session?.url) {
                    throw new Error('Stripe session missing url');
                }
                return session;
            }
        });
    }
    ```

3. 实现一个Payment组件，包含：
    * `useCreateCheckoutSession()`
    * 将`ShoppingItem[]`作为输入传递。
    * 分析`CheckoutSession`结果。
    * 将网页重定向到`CheckoutSession`中的url：这允许用户完成支付。
    * 不要使用路由导航进行Stripe URL。使用`window.location.href`。
    * 永远不要导航到`/undefined`；如果`session.url`缺失，显示错误并停止。

    ```
    const session = await createCheckoutSession.mutateAsync(shoppingItems);
    if (!session?.url) throw new Error('Stripe session missing url');
    window.location.href = session.url;
    ```

4. 实现一个PaymentSuccess和PaymentFailure组件，分别处理支付成功或失败。

5. 将两个特定路径路由到支付状态组件：
   * 路径"/payment-success"到PaymentSuccess。
   * 路径"/payment-failure"到PaymentFailure。
   你需要使用@tanstack router。

6. 管理视图提供了一个菜单来配置Stripe。如果尚未配置，它在登录时要求管理员配置Stripe。

侧注：确保产品图片在产品画布中正确渲染和调整大小。
