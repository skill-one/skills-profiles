# 用户审批
[Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral) 的用户审批扩展。

## 概述

此技能添加基于审批的用户管理。用户请求访问权限；管理员批准或拒绝。已批准的用户可以访问受保护的功能。

前提条件：您必须先遵循 [extension-authorization](../extension-authorization/SKILL.md)，因为此集成依赖于它。

# 后端

## 模块 API

预制模块 `mo:caffeineai-user-approval/approval` 提供低级别的审批状态管理。不要修改它。

```mo:caffeineai-user-approval/approval
import AccessControl "mo:caffeineai-authorization/access-control";

module {
    public type ApprovalStatus = {
        #approved;
        #rejected;
        #pending;
    };

    public type UserApprovalState = { /* 内部状态 */ };

    public func initState(accessControlState : AccessControl.AccessControlState) : UserApprovalState;

    public func isApproved(state : UserApprovalState, caller : Principal) : Bool;
    public func requestApproval(state : UserApprovalState, caller : Principal);
    public func setApproval(state : UserApprovalState, user : Principal, approval : ApprovalStatus);

    public type UserApprovalInfo = {
        principal : Principal;
        status : ApprovalStatus;
    };

    public func listApprovals(state : UserApprovalState) : [UserApprovalInfo];
}
```

## 在 main.mo 中设置

`include MixinUserApproval(accessControlState, approvalState)` 必须放在 `main.mo` 中，而不是在自定义混合文件中。在 actor 的顶层声明 `approvalState`，并将其传递给混合。混合会自动提供以下公共端点：

- `isCallerApproved()`
- `requestApproval()`
- `setApproval(user, status)`
- `listApprovals()`

在特定应用的端点中，为自定义审批守卫保留 `approvalState` 在作用域内。

不要重新声明任何混合提供的函数。

```motoko filepath=src/backend/main.mo
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import MixinUserApproval "mo:caffeineai-user-approval/MixinUserApproval";
import UserApproval "mo:caffeineai-user-approval/approval";
import Runtime "mo:core/Runtime";

actor {
    let accessControlState : AccessControl.AccessControlState;
    include MixinAuthorization(accessControlState, null);
    let approvalState : UserApproval.UserApprovalState;
    include MixinUserApproval(accessControlState, approvalState);

    // 带有审批守卫的自定义端点示例：
    // public shared ({ caller }) func protectedFeature() : async () {
    //     if (not (UserApproval.isApproved(approvalState, caller) or AccessControl.hasPermission(accessControlState, caller, #admin))) {
    //         Runtime.trap("Unauthorized: Only approved users can perform this action");
    //     };
    // };
};
```

迁移链的头部 — `UserApproval.initState` 依赖于访问控制状态，因此按顺序在迁移体内计算它：

```motoko filepath=src/backend/migrations/00000000_000000.mo
import AccessControl "mo:caffeineai-authorization/access-control";
import UserApproval "mo:caffeineai-user-approval/approval";

module {
    type NewActor = {
        accessControlState : AccessControl.AccessControlState;
        approvalState : UserApproval.UserApprovalState;
    };

    public func migration(_old : {}) : NewActor {
        let accessControlState = AccessControl.initState();
        {
            accessControlState;
            approvalState = UserApproval.initState(accessControlState);
        };
    };
};
```

在 `initState` 中，现有管理员会自动被批准。所有其他用户都处于待审批状态。

重要提示：为每个自定义公共函数应用正确的授权和/或审批检查。

# 前端

基于审批的用户管理：

# 用户审批流程
- 检查审批状态 (`isCallerApproved`)
- 如果未批准，显示请求审批的选项 (`requestApproval`)
- 阻止未批准用户访问主要功能
- 管理员可以访问应用程序的所有功能
- 在 UI 中清晰显示审批状态

# 管理员控制面板
为管理员用户提供一个控制面板，以：
- 列出所有用户及其审批状态 (`listApprovals`)
- 批准或拒绝用户 (`setApproval`)
- 查看和分配用户角色（使用 `getCallerUserRole` 和 `assignCallerUserRole`）

# 后端集成
后端已经实现了以下功能。
完整接口可以在 <backend-interface> 中找到

// 检查当前用户是否已批准，管理员始终被批准
isCallerApproved(): Promise<boolean>;

// 提交审批请求
requestApproval(): Promise<void>;

// 获取所有用户及其审批状态（仅管理员）
listApprovals(): Promise<Array<UserApprovalInfo>>;

// 批准或拒绝用户（仅管理员）
setApproval(user: Principal, status: ApprovalStatus): Promise<void>;

// 为用户分配角色（仅管理员）
assignCallerUserRole(user: Principal, role: UserRole): Promise<void>;

// 获取特定用户的当前角色
getCallerUserRole(): Promise<UserRole>;
