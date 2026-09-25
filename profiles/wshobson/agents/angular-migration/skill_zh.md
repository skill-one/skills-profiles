# Angular 迁移

掌握 AngularJS 到 Angular 的迁移，包括混合应用、组件转换、依赖注入变更和路由迁移。

## 何时使用这项技能

- 将 AngularJS (1.x) 应用迁移到 Angular (2+)
- 运行混合 AngularJS/Angular 应用
- 将指令转换为组件
- 现代化依赖注入
- 迁移路由系统
- 更新到最新 Angular 版本
- 实施 Angular 最佳实践

## 迁移策略

### 1. 一揽子迁移（完全重写）

- 使用 Angular 重写整个应用
- 并行开发
- 一次性切换
- **最适合：** 小型应用、绿色项目

### 2. 增量迁移（混合方法）

- 并行运行 AngularJS 和 Angular
- 按功能逐个迁移
- ngUpgrade 用于互操作
- **最适合：** 大型应用、持续交付

### 3. 垂直切片

- 完全迁移一个功能
- 新功能使用 Angular，旧功能维持 AngularJS
- 逐步替换
- **最适合：** 中型应用、独立功能

## 混合应用设置

```typescript
// main.ts - 引导混合应用
import { platformBrowserDynamic } from "@angular/platform-browser-dynamic";
import { UpgradeModule } from "@angular/upgrade/static";
import { AppModule } from "./app/app.module";

platformBrowserDynamic()
  .bootstrapModule(AppModule)
  .then((platformRef) => {
    const upgrade = platformRef.injector.get(UpgradeModule);
    // 引导 AngularJS
    upgrade.bootstrap(document.body, ["myAngularJSApp"], { strictDi: true });
  });
```

```typescript
// app.module.ts
import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { UpgradeModule } from "@angular/upgrade/static";

@NgModule({
  imports: [BrowserModule, UpgradeModule],
})
export class AppModule {
  constructor(private upgrade: UpgradeModule) {}

  ngDoBootstrap() {
    // 在 main.ts 中手动引导
  }
}
```

## 组件迁移

### AngularJS 控制器 → Angular 组件

```javascript
// 之前：AngularJS 控制器
angular
  .module("myApp")
  .controller("UserController", function ($scope, UserService) {
    $scope.user = {};

    $scope.loadUser = function (id) {
      UserService.getUser(id).then(function (user) {
        $scope.user = user;
      });
    };

    $scope.saveUser = function () {
      UserService.saveUser($scope.user);
    };
  });
```

```typescript
// 之后：Angular 组件
import { Component, OnInit } from "@angular/core";
import { UserService } from "./user.service";

@Component({
  selector: "app-user",
  template: `
    <div>
      <h2>{{ user.name }}</h2>
      <button (click)="saveUser()">Save</button>
    </div>
  `,
})
export class UserComponent implements OnInit {
  user: any = {};

  constructor(private userService: UserService) {}

  ngOnInit() {
    this.loadUser(1);
  }

  loadUser(id: number) {
    this.userService.getUser(id).subscribe((user) => {
      this.user = user;
    });
  }

  saveUser() {
    this.userService.saveUser(this.user);
  }
}
```

### AngularJS 指令 → Angular 组件

```javascript
// 之前：AngularJS 指令
angular.module("myApp").directive("userCard", function () {
  return {
    restrict: "E",
    scope: {
      user: "=",
      onDelete: "&",
    },
    template: `
      <div class="card">
        <h3>{{ user.name }}</h3>
        <button ng-click="onDelete()">Delete</button>
      </div>
    `,
  };
});
```

```typescript
// 之后：Angular 组件
import { Component, Input, Output, EventEmitter } from "@angular/core";

@Component({
  selector: "app-user-card",
  template: `
    <div class="card">
      <h3>{{ user.name }}</h3>
      <button (click)="delete.emit()">Delete</button>
    </div>
  `,
})
export class UserCardComponent {
  @Input() user: any;
  @Output() delete = new EventEmitter<void>();
}

// 使用方式：<app-user-card [user]="user" (delete)="handleDelete()"></app-user-card>
```

## 服务迁移

```javascript
// 之前：AngularJS 服务
angular.module("myApp").factory("UserService", function ($http) {
  return {
    getUser: function (id) {
      return $http.get("/api/users/" + id);
    },
    saveUser: function (user) {
      return $http.post("/api/users", user);
    },
  };
});
```

```typescript
// 之后：Angular 服务
import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";

@Injectable({
  providedIn: "root",
})
export class UserService {
  constructor(private http: HttpClient) {}

  getUser(id: number): Observable<any> {
    return this.http.get(`/api/users/${id}`);
  }

  saveUser(user: any): Observable<any> {
    return this.http.post("/api/users", user);
  }
}
```

## 依赖注入变更

### Angular → AngularJS 降级

```typescript
// Angular 服务
import { Injectable } from "@angular/core";

@Injectable({ providedIn: "root" })
export class NewService {
  getData() {
    return "data from Angular";
  }
}

// 使其对 AngularJS 可用
import { downgradeInjectable } from "@angular/upgrade/static";

angular.module("myApp").factory("newService", downgradeInjectable(NewService));

// 在 AngularJS 中使用
angular.module("myApp").controller("OldController", function (newService) {
  console.log(newService.getData());
});
```

### AngularJS → Angular 升级

```typescript
// AngularJS 服务
angular.module('myApp').factory('oldService', function() {
  return {
    getData: function() {
      return 'data from AngularJS';
    }
  };
});

// 使其对 Angular 可用
import { InjectionToken } from '@angular/core';

export const OLD_SERVICE = new InjectionToken<any>('oldService');

@NgModule({
  providers: [
    {
      provide: OLD_SERVICE,
      useFactory: (i: any) => i.get('oldService'),
      deps: ['$injector']
    }
  ]
})

// 在 Angular 中使用
@Component({...})
export class NewComponent {
  constructor(@Inject(OLD_SERVICE) private oldService: any) {
    console.log(this.oldService.getData());
  }
}
```

## 路由迁移

```javascript
// 之前：AngularJS 路由
angular.module("myApp").config(function ($routeProvider) {
  $routeProvider
    .when("/users", {
      template: "<user-list></user-list>",
    })
    .when("/users/:id", {
      template: "<user-detail></user-detail>",
    });
});
```

```typescript
// 之后：Angular 路由
import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";

const routes: Routes = [
  { path: "users", component: UserListComponent },
  { path: "users/:id", component: UserDetailComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
```

## 其他模式和模板

更详细的模板和实例说明位于 `references/details.md`。阅读该文件以获取完整模式库。
