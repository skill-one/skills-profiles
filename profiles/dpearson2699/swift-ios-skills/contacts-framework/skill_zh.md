# 联系人框架

使用 `CNContactStore`、`CNSaveRequest` 和 `CNContactPickerViewController` 在 Swift 6.3 / iOS 26+ 应用中获取、创建、更新或选择联系人。

## 目录

- [设置](#设置)
- [授权](#授权)
- [获取联系人](#获取联系人)
- [键描述符](#键描述符)
- [创建和更新联系人](#创建和更新联系人)
- [联系人选择器](#联系人选择器)
- [观察变更](#观察变更)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 设置

### 项目配置

1. 在 Info.plist 中添加 `NSContactsUsageDescription`，解释为什么应用访问联系人。如果没有此键，应用在尝试使用联系人数据 API 时会崩溃。
2. 普通联系人访问不需要额外的权限或权利。
3. 仅在读取或写入 `CNContactNoteKey` / `CNContact.note` 时添加 `com.apple.developer.contacts.notes`；此权利需要在公开发布前获得苹果的批准。

### 导入

```swift
@preconcurrency import Contacts  // CNContactStore, CNSaveRequest, CNContact
import ContactsUI                // CNContactPickerViewController
```

## 授权

在获取或保存联系人之前请求访问权限。选择器 (`CNContactPickerViewController`) 不需要授权——系统仅授予用户选择的联系人访问权限。

```swift
let store = CNContactStore()

func requestAccess() async throws -> Bool {
    return try await store.requestAccess(for: .contacts)
}

// 无需提示检查当前状态
func checkStatus() -> CNAuthorizationStatus {
    CNContactStore.authorizationStatus(for: .contacts)
}
```

### 授权状态

| 状态 | 含义 |
|---|---|
| `.notDetermined` | 用户尚未被提示 |
| `.authorized` | 授予完全读写访问权限 |
| `.denied` | 用户拒绝访问；直接跳转到设置 |
| `.restricted` | 家长控制或 MDM 限制访问 |
| `.limited` | iOS 18+: 用户仅授予对选定联系人的访问权限 |

将 `.authorized` 和 `.limited` 都视为可用的联系人 API 状态。使用 `.limited` 时，获取、编辑和删除操作仅适用于用户授予或应用创建的联系人。使用 `ContactAccessButton` 或 `contactAccessPicker(isPresented:completionHandler:)` 让用户将联系人添加到应用的有限访问集中。

## 获取联系人

使用 `unifiedContacts(matching:keysToFetch:)` 进行基于谓词的查询。使用 `enumerateContacts(with:usingBlock:)` 对所有联系人进行批量枚举。对于大型缓存的通讯录，首先获取标识符，然后按标识符分批获取详细联系人。

### 按名称获取

```swift
func fetchContacts(named name: String) throws -> [CNContact] {
    let predicate = CNContact.predicateForContacts(matchingName: name)
    let keys: [CNKeyDescriptor] = [
        CNContactGivenNameKey as CNKeyDescriptor,
        CNContactFamilyNameKey as CNKeyDescriptor,
        CNContactPhoneNumbersKey as CNKeyDescriptor
    ]
    return try store.unifiedContacts(matching: predicate, keysToFetch: keys)
}
```

### 按标识符获取

```swift
func fetchContact(identifier: String) throws -> CNContact {
    let keys: [CNKeyDescriptor] = [
        CNContactGivenNameKey as CNKeyDescriptor,
        CNContactFamilyNameKey as CNKeyDescriptor,
        CNContactEmailAddressesKey as CNKeyDescriptor
    ]
    return try store.unifiedContact(withIdentifier: identifier, keysToFetch: keys)
}
```

### 枚举所有联系人

在主线程外执行 I/O 密集型枚举。

```swift
func fetchAllContacts() throws -> [CNContact] {
    let keys: [CNKeyDescriptor] = [
        CNContactGivenNameKey as CNKeyDescriptor,
        CNContactFamilyNameKey as CNKeyDescriptor
    ]
    let request = CNContactFetchRequest(keysToFetch: keys)
    request.sortOrder = .givenName

    var contacts: [CNContact] = []
    try store.enumerateContacts(with: request) { contact, _ in
        contacts.append(contact)
    }
    return contacts
}
```

## 键描述符

仅获取您需要的属性。访问未获取的属性会抛出 `CNContactPropertyNotFetchedException`。

### 常见键

| 键 | 属性 |
|---|---|
| `CNContactGivenNameKey` | 名字 |
| `CNContactFamilyNameKey` | 姓氏 |
| `CNContactPhoneNumbersKey` | 电话号码数组 |
| `CNContactEmailAddressesKey` | 电子邮件地址数组 |
| `CNContactPostalAddressesKey` | 邮寄地址数组 |
| `CNContactImageDataKey` | 高分辨率联系人照片 |
| `CNContactThumbnailImageDataKey` | 缩略图联系人照片 |
| `CNContactBirthdayKey` | 生日日期组件 |
| `CNContactOrganizationNameKey` | 公司名称 |

### 复合键描述符

使用 `CNContactFormatter.descriptorForRequiredKeys(for:)` 获取格式化联系人名称所需的所有键。

```swift
let nameKeys = CNContactFormatter.descriptorForRequiredKeys(for: .fullName)
let keys: [CNKeyDescriptor] = [nameKeys, CNContactPhoneNumbersKey as CNKeyDescriptor]
```

## 创建和更新联系人

使用 `CNMutableContact` 构建新联系人，并使用 `CNSaveRequest` 持久化更改。

### 创建新联系人

```swift
func createContact(givenName: String, familyName: String, phone: String) throws {
    let contact = CNMutableContact()
    contact.givenName = givenName
    contact.familyName = familyName
    contact.phoneNumbers = [
        CNLabeledValue(
            label: CNLabelPhoneNumberMobile,
            value: CNPhoneNumber(stringValue: phone)
        )
    ]

    let saveRequest = CNSaveRequest()
    saveRequest.add(contact, toContainerWithIdentifier: nil) // nil = 默认容器
    try store.execute(saveRequest)
}
```

### 更新现有联系人

您必须获取您打算修改的属性对应的联系人，创建可变副本，更改属性，然后保存。

```swift
func updateContactEmail(identifier: String, email: String) throws {
    let keys: [CNKeyDescriptor] = [
        CNContactEmailAddressesKey as CNKeyDescriptor
    ]
    let contact = try store.unifiedContact(withIdentifier: identifier, keysToFetch: keys)
    guard let mutable = contact.mutableCopy() as? CNMutableContact else { return }

    mutable.emailAddresses.append(
        CNLabeledValue(label: CNLabelWork, value: email as NSString)
    )

    let saveRequest = CNSaveRequest()
    saveRequest.update(mutable)
    try store.execute(saveRequest)
}
```

### 删除联系人

```swift
func deleteContact(identifier: String) throws {
    let keys: [CNKeyDescriptor] = [CNContactIdentifierKey as CNKeyDescriptor]
    let contact = try store.unifiedContact(withIdentifier: identifier, keysToFetch: keys)
    guard let mutable = contact.mutableCopy() as? CNMutableContact else { return }

    let saveRequest = CNSaveRequest()
    saveRequest.delete(mutable)
    try store.execute(saveRequest)
}
```

### 保存结果和恢复

`try store.execute(saveRequest)` 返回而不抛出是保存成功的检查点。仅在返回后更新应用端缓存或成功 UI。如果抛出，显示或传播错误，保持未保存的意图可供用户使用，并在构建新请求之前纠正已知原因——例如授权、只读容器或无效输入。序列化重叠的保存，在 `execute(_:)` 使用它时不访问请求，并在允许访问时重新获取可能过时的联系人进行修正重试。不要盲目重复相同的破坏性请求，或要求当前访问级别可能不允许的通用回读。加载 [扩展联系人模式](references/contacts-patterns.md) 以支持多选、vCard 和优化搜索工作流。

## 联系人选择器

`CNContactPickerViewController` 允许用户在不授予完全联系人访问权限的情况下选择联系人。应用仅接收选定的联系人数据。

### SwiftUI 包装器

```swift
import SwiftUI
import ContactsUI

struct ContactPicker: UIViewControllerRepresentable {
    @Binding var selectedContact: CNContact?

    func makeUIViewController(context: Context) -> CNContactPickerViewController {
        let picker = CNContactPickerViewController()
        picker.delegate = context.coordinator
        return picker
    }

    func updateUIViewController(_ uiViewController: CNContactPickerViewController, context: Context) {}

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    final class Coordinator: NSObject, CNContactPickerDelegate {
        let parent: ContactPicker

        init(_ parent: ContactPicker) {
            self.parent = parent
        }

        func contactPicker(_ picker: CNContactPickerViewController, didSelect contact: CNContact) {
            parent.selectedContact = contact
        }

        func contactPickerDidCancel(_ picker: CNContactPickerViewController) {
            parent.selectedContact = nil
        }
    }
}
```

### 使用选择器

```swift
struct ContactSelectionView: View {
    @State private var selectedContact: CNContact?
    @State private var showPicker = false

    var body: some View {
        VStack {
            if let contact = selectedContact {
                Text("\(contact.givenName) \(contact.familyName)")
            }
            Button("选择联系人") {
                showPicker = true
            }
        }
        .sheet(isPresented: $showPicker) {
            ContactPicker(selectedContact: $selectedContact)
        }
    }
}
```

### 过滤选择器

使用谓词来控制哪些联系人显示以及用户可以选择什么。

```swift
let picker = CNContactPickerViewController()
// 仅显示具有电子邮件地址的联系人
picker.predicateForEnablingContact = NSPredicate(format: "emailAddresses.@count > 0")
// 选择联系人后直接返回（无详细卡片）
picker.predicateForSelectionOfContact = NSPredicate(value: true)
```

## 观察变更

监听外部联系人数据库变更以刷新缓存数据。

```swift
func observeContactChanges() {
    NotificationCenter.default.addObserver(
        forName: .CNContactStoreDidChange,
        object: nil,
        queue: .main
    ) { _ in
        // 重新获取联系人——缓存的 CNContact 对象已过时
        refreshContacts()
    }
}
```

## 常见错误

### 不要：在您只需要一个名字时获取所有键

过度获取会浪费内存并减慢查询，特别是对于具有大型照片的联系人。

```swift
// 错误：获取远比 UI 显示的更多内容，包括高分辨率照片
let keys: [CNKeyDescriptor] = [
    CNContactFormatter.descriptorForRequiredKeys(for: .fullName),
    CNContactImageDataKey as CNKeyDescriptor,
    CNContactPhoneNumbersKey as CNKeyDescriptor,
    CNContactEmailAddressesKey as CNKeyDescriptor,
    CNContactPostalAddressesKey as CNKeyDescriptor,
    CNContactBirthdayKey as CNKeyDescriptor
]

// 正确：仅获取您显示的内容
let keys: [CNKeyDescriptor] = [
    CNContactGivenNameKey as CNKeyDescriptor,
    CNContactFamilyNameKey as CNKeyDescriptor
]
```

### 不要：访问未获取的属性

访问未在 `keysToFetch` 中获取的属性会在运行时抛出 `CNContactPropertyNotFetchedException`。

```swift
// 错误：仅获取了名字键，现在访问电话
let keys: [CNKeyDescriptor] = [CNContactGivenNameKey as CNKeyDescriptor]
let contact = try store.unifiedContact(withIdentifier: id, keysToFetch: keys)
let phone = contact.phoneNumbers.first // 崩溃

// 正确：包含您需要的键
let keys: [CNKeyDescriptor] = [
    CNContactGivenNameKey as CNKeyDescriptor,
    CNContactPhoneNumbersKey as CNKeyDescriptor
]
```

### 不要：直接修改 CNContact

`CNContact` 是不可变的。您必须调用 `mutableCopy()` 来获取 `CNMutableContact`。

```swift
// 错误：CNContact 没有设置器
let contact = try store.unifiedContact(withIdentifier: id, keysToFetch: keys)
contact.givenName = "New Name" // 编译错误

// 正确：创建可变副本
guard let mutable = contact.mutableCopy() as? CNMutableContact else { return }
mutable.givenName = "New Name"
```

### 不要：跳过授权并假设访问

不要让获取或保存调用成为用户首次看到授权的地方。如果状态是 `.notDetermined`，请求访问；如果访问被拒绝，联系人操作会因为授权错误而失败。

```swift
// 错误：直接跳转到获取
let contacts = try store.unifiedContacts(matching: predicate, keysToFetch: keys)

// 正确：首先检查或请求授权
let granted = try await store.requestAccess(for: .contacts)
guard granted else { return }
let contacts = try store.unifiedContacts(matching: predicate, keysToFetch: keys)
```

### 不要：在主线程上运行重型获取

`enumerateContacts` 执行 I/O。在主线程上运行它会阻塞 UI。当严格的并发检查抱怨 `CNContact` 跨越任务或 actor 边界时，在该文件中使用 `@preconcurrency import Contacts`，或在返回它们之前将联系人映射到可发送的视图模型。

```swift
// 错误：主线程枚举
func loadContacts() {
    try store.enumerateContacts(with: request) { contact, _ in ... }
}

// 正确：在后台线程运行
func loadContacts() async throws -> [CNContact] {
    try await Task.detached {
        var results: [CNContact] = []
        try store.enumerateContacts(with: request) { contact, _ in
            results.append(contact)
        }
        return results
    }.value
}
```

## 审查清单

- [ ] Info.plist 中添加了 `NSContactsUsageDescription`
- [ ] 在获取或保存操作之前调用了 `requestAccess(for: .contacts)`
- [ ] 将 `.limited` 视为可用访问，并考虑选定联系人的限制
- [ ] 当用户需要扩展有限访问时提供 `ContactAccessButton` 或 `contactAccessPicker`
- [ ] 优雅地处理授权拒绝（引导用户到设置）
- [ ] 获取请求中仅包含所需的 `CNKeyDescriptor` 键
- [ ] 使用 `CNContactFormatter.descriptorForRequiredKeys(for:)` 格式化名称
- [ ] 在修改联系人之前通过 `mutableCopy()` 创建可变副本
- [ ] 每个创建/更新/删除都使用 `CNSaveRequest`；应用状态仅在 `execute(_:)` 成功后推进，并且失败会在构建修正请求之前显示
- [ ] 重型获取 (`enumerateContacts`) 在主线程外运行
- [ ] 观察 `CNContactStoreDidChange` 以刷新缓存联系人
- [ ] 当不需要完全联系人访问时使用 `CNContactPickerViewController`
- [ ] 在显示选择器视图控制器之前设置选择器谓词
- [ ] 在整个应用中重用单个 `CNContactStore` 实例

## 参考资料

- 扩展模式（多选选择器、vCard 导出、搜索优化）：[references/contacts-patterns.md](references/contacts-patterns.md)
- [联系人框架](https://sosumi.ai/documentation/contacts)
- [CNContactStore](https://sosumi.ai/documentation/contacts/cncontactstore)
- [CNContactFetchRequest](https://sosumi.ai/documentation/contacts/cncontactfetchrequest)
- [CNSaveRequest](https://sosumi.ai/documentation/contacts/cnsaverequest)
- [CNMutableContact](https://sosumi.ai/documentation/contacts/cnmutablecontact)
- [CNContactPickerViewController](https://sosumi.ai/documentation/contactsui/cncontactpickerviewcontroller)
- [CNContactPickerDelegate](https://sosumi.ai/documentation/contactsui/cncontactpickerdelegate)
- [访问联系人存储](https://sosumi.ai/documentation/contacts/accessing-the-contact-store)
- [NSContactsUsageDescription](https://sosumi.ai/documentation/bundleresources/information-property-list/nscontactsusagedescription)
- [ContactAccessButton](https://sosumi.ai/documentation/contactsui/contactaccessbutton)
- [contactAccessPicker(isPresented:completionHandler:)](https://sosumi.ai/documentation/swiftui/view/contactaccesspicker(ispresented:completionhandler:))
- [联系人键](https://sosumi.ai/documentation/contacts/contact-keys)
