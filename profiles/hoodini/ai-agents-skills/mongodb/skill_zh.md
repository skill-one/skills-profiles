# MongoDB & Mongoose

使用最佳实践构建和查询 MongoDB 数据库。

## 快速入门

```bash
npm install mongodb mongoose
```

### 原生驱动
```typescript
import { MongoClient, ObjectId } from 'mongodb';

const client = new MongoClient(process.env.MONGODB_URI!);
const db = client.db('myapp');
const users = db.collection('users');

// 连接
await client.connect();

// CRUD 操作
await users.insertOne({ name: 'Alice', email: 'alice@example.com' });
const user = await users.findOne({ email: 'alice@example.com' });
await users.updateOne({ _id: user._id }, { $set: { name: 'Alice Smith' } });
await users.deleteOne({ _id: user._id });
```

### Mongoose 设置
```typescript
import mongoose from 'mongoose';

await mongoose.connect(process.env.MONGODB_URI!, {
  maxPoolSize: 10,
  serverSelectionTimeoutMS: 5000,
  socketTimeoutMS: 45000,
});

// 连接事件
mongoose.connection.on('connected', () => console.log('MongoDB 连接成功'));
mongoose.connection.on('error', (err) => console.error('MongoDB 错误:', err));
mongoose.connection.on('disconnected', () => console.log('MongoDB 断开连接'));

// 优雅关闭
process.on('SIGINT', async () => {
  await mongoose.connection.close();
  process.exit(0);
});
```

## 模式设计

### 基本模式
```typescript
import mongoose, { Schema, Document, Model } from 'mongoose';

interface IUser extends Document {
  email: string;
  name: string;
  password: string;
  role: 'user' | 'admin';
  profile: {
    avatar?: string;
    bio?: string;
  };
  createdAt: Date;
  updatedAt: Date;
}

const userSchema = new Schema<IUser>({
  email: {
    type: String,
    required: [true, '邮箱是必填项'],
    unique: true,
    lowercase: true,
    trim: true,
    match: [/^\S+@\S+\.\S+$/, '无效的邮箱格式'],
  },
  name: {
    type: String,
    required: true,
    trim: true,
    minlength: 2,
    maxlength: 100,
  },
  password: {
    type: String,
    required: true,
    select: false,  // 默认情况下不返回密码
  },
  role: {
    type: String,
    enum: ['user', 'admin'],
    default: 'user',
  },
  profile: {
    avatar: String,
    bio: { type: String, maxlength: 500 },
  },
}, {
  timestamps: true,  // 添加 createdAt, updatedAt
  toJSON: {
    transform(doc, ret) {
      delete ret.password;
      delete ret.__v;
      return ret;
    },
  },
});

// 索引
userSchema.index({ email: 1 });
userSchema.index({ createdAt: -1 });
userSchema.index({ name: 'text', 'profile.bio': 'text' });  // 文本搜索

const User: Model<IUser> = mongoose.model('User', userSchema);
```

### 嵌入文档与引用

```typescript
// ✅ 嵌入文档：当数据一起读取，且不会无限制增长时
const orderSchema = new Schema({
  customer: {
    name: String,
    email: String,
    address: {
      street: String,
      city: String,
      country: String,
    },
  },
  items: [{
    product: String,
    quantity: Number,
    price: Number,
  }],
  total: Number,
});

// ✅ 引用：当数据较大、共享或独立变化时
const postSchema = new Schema({
  title: String,
  content: String,
  author: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true,
  },
  comments: [{
    type: Schema.Types.ObjectId,
    ref: 'Comment',
  }],
});

// 填充引用
const post = await Post.findById(id)
  .populate('author', 'name email')  // 选择特定字段
  .populate({
    path: 'comments',
    populate: { path: 'author', select: 'name' },  // 嵌套填充
  });
```

### 虚拟属性
```typescript
const userSchema = new Schema({
  firstName: String,
  lastName: String,
});

// 虚拟字段（不存储在数据库中）
userSchema.virtual('fullName').get(function() {
  return `${this.firstName} ${this.lastName}`;
});

// 虚拟填充（用于反向引用）
userSchema.virtual('posts', {
  ref: 'Post',
  localField: '_id',
  foreignField: 'author',
});

// 在 JSON 中启用虚拟属性
userSchema.set('toJSON', { virtuals: true });
userSchema.set('toObject', { virtuals: true });
```

## 查询操作

### 查找操作
```typescript
// 带过滤条件的查找
const users = await User.find({
  role: 'user',
  createdAt: { $gte: new Date('2024-01-01') },
});

// 查询构建器
const results = await User.find()
  .where('role').equals('user')
  .where('createdAt').gte(new Date('2024-01-01'))
  .select('name email')
  .sort({ createdAt: -1 })
  .limit(10)
  .skip(20)
  .lean();  // 返回普通对象（更快）

// 查找一个
const user = await User.findOne({ email: 'alice@example.com' });
const userById = await User.findById(id);

// 存在性检查
const exists = await User.exists({ email: 'alice@example.com' });

// 计数
const count = await User.countDocuments({ role: 'admin' });
```

### 查询操作符
```typescript
// 比较操作
await User.find({ age: { $eq: 25 } });      // 等于
await User.find({ age: { $ne: 25 } });      // 不等于
await User.find({ age: { $gt: 25 } });      // 大于
await User.find({ age: { $gte: 25 } });     // 大于或等于
await User.find({ age: { $lt: 25 } });      // 小于
await User.find({ age: { $lte: 25 } });     // 小于或等于
await User.find({ age: { $in: [20, 25, 30] } });   // 在数组中
await User.find({ age: { $nin: [20, 25] } });      // 不在数组中

// 逻辑操作
await User.find({
  $and: [{ age: { $gte: 18 } }, { role: 'user' }],
});
await User.find({
  $or: [{ role: 'admin' }, { isVerified: true }],
});
await User.find({ age: { $not: { $lt: 18 } } });

// 元素操作
await User.find({ avatar: { $exists: true } });
await User.find({ score: { $type: 'number' } });

// 数组操作
await User.find({ tags: 'nodejs' });  // 数组包含值
await User.find({ tags: { $all: ['nodejs', 'mongodb'] } });  // 包含所有
await User.find({ tags: { $size: 3 } });  // 数组长度
await User.find({ 'items.0.price': { $gt: 100 } });  // 数组索引

// 文本搜索
await User.find({ $text: { $search: 'mongodb developer' } });

// 正则表达式
await User.find({ name: { $regex: /^john/i } });
```

### 更新操作
```typescript
// 更新一个
await User.updateOne(
  { _id: userId },
  { $set: { name: '新名称' } }
);

// 更新多个
await User.updateMany(
  { role: 'user' },
  { $set: { isVerified: true } }
);

// 查找并更新（返回文档）
const updated = await User.findByIdAndUpdate(
  userId,
  { $set: { name: '新名称' } },
  { new: true, runValidators: true }  // 返回更新后的文档，运行验证器
);

// 更新操作符
await User.updateOne({ _id: userId }, {
  $set: { name: '新名称' },          // 设置字段
  $unset: { tempField: '' },           // 移除字段
  $inc: { loginCount: 1 },             // 增加
  $mul: { score: 1.5 },                // 乘以
  $min: { lowScore: 50 },              // 如果小于则设置
  $max: { highScore: 100 },            // 如果大于则设置
  $push: { tags: 'new-tag' },          // 添加到数组
  $pull: { tags: 'old-tag' },          // 从数组中移除
  $addToSet: { tags: 'unique-tag' },   // 如果不存在则添加
});

// Upsert（如果不存在则插入）
await User.updateOne(
  { email: 'new@example.com' },
  { $set: { name: '新用户' } },
  { upsert: true }
);
```

## 聚合管道

### 基本聚合
```typescript
const results = await Order.aggregate([
  // 阶段 1：匹配
  { $match: { status: 'completed' } },
  
  // 阶段 2：分组
  { $group: {
    _id: '$customerId',
    totalOrders: { $sum: 1 },
    totalSpent: { $sum: '$total' },
    avgOrder: { $avg: '$total' },
  }},
  
  // 阶段 3：排序
  { $sort: { totalSpent: -1 } },
  
  // 阶段 4：限制
  { $limit: 10 },
]);
```

### 管道阶段
```typescript
const pipeline = [
  // $match - 过滤文档
  { $match: { createdAt: { $gte: new Date('2024-01-01') } } },
  
  // $project - 形状输出
  { $project: {
    name: 1,
    email: 1,
    yearJoined: { $year: '$createdAt' },
    fullName: { $concat: ['$firstName', ' ', '$lastName'] },
  }},
  
  // $lookup - 连接集合
  { $lookup: {
    from: 'orders',
    localField: '_id',
    foreignField: 'userId',
    as: 'orders',
  }},
  
  // $unwind - 展平数组
  { $unwind: { path: '$orders', preserveNullAndEmptyArrays: true } },
  
  // $group - 聚合
  { $group: {
    _id: '$_id',
    name: { $first: '$name' },
    orderCount: { $sum: 1 },
    orders: { $push: '$orders' },
  }},
  
  // $addFields - 添加计算字段
  { $addFields: {
    hasOrders: { $gt: ['$orderCount', 0] },
  }},
  
  // $facet - 多个管道
  { $facet: {
    topCustomers: [{ $sort: { orderCount: -1 } }, { $limit: 5 }],
    stats: [{ $group: { _id: null, avgOrders: { $avg: '$orderCount' } } }],
  }},
];
```

### 分析示例
```typescript
// 按月统计销售额
const salesByMonth = await Order.aggregate([
  { $match: { status: 'completed' } },
  { $group: {
    _id: {
      year: { $year: '$createdAt' },
      month: { $month: '$createdAt' },
    },
    totalSales: { $sum: '$total' },
    orderCount: { $sum: 1 },
  }},
  { $sort: { '_id.year': -1, '_id.month': -1 } },
]);

// 最受欢迎的产品
const topProducts = await Order.aggregate([
  { $unwind: '$items' },
  { $group: {
    _id: '$items.productId',
    totalQuantity: { $sum: '$items.quantity' },
    totalRevenue: { $sum: { $multiply: ['$items.price', '$items.quantity'] } },
  }},
  { $lookup: {
    from: 'products',
    localField: '_id',
    foreignField: '_id',
    as: 'product',
  }},
  { $unwind: '$product' },
  { $project: {
    name: '$product.name',
    totalQuantity: 1,
    totalRevenue: 1,
  }},
  { $sort: { totalRevenue: -1 } },
  { $limit: 10 },
]);
```

## 中间件（钩子）

```typescript
// 保存前中间件
userSchema.pre('save', async function(next) {
  if (this.isModified('password')) {
    this.password = await bcrypt.hash(this.password, 12);
  }
  next();
});

// 保存后中间件
userSchema.post('save', function(doc) {
  console.log('用户保存:', doc._id);
});

// 查找前中间件
userSchema.pre(/^find/, function(next) {
  // 默认排除已删除的用户
  this.find({ isDeleted: { $ne: true } });
  next();
});

// 聚合前中间件
userSchema.pre('aggregate', function(next) {
  // 在所有聚合中添加匹配阶段
  this.pipeline().unshift({ $match: { isDeleted: { $ne: true } } });
  next();
});
```

## 事务

```typescript
const session = await mongoose.startSession();

try {
  session.startTransaction();
  
  // 事务中的所有操作
  const user = await User.create([{ name: 'Alice' }], { session });
  await Account.create([{ userId: user[0]._id, balance: 0 }], { session });
  await Order.updateOne({ _id: orderId }, { $set: { status: 'paid' } }, { session });
  
  await session.commitTransaction();
} catch (error) {
  await session.abortTransaction();
  throw error;
} finally {
  session.endSession();
}

// 带回调的事务
await mongoose.connection.transaction(async (session) => {
  await User.create([{ name: 'Alice' }], { session });
  await Account.create([{ userId: user._id }], { session });
});
```

## 索引

```typescript
// 单字段索引
userSchema.index({ email: 1 });

// 复合索引
userSchema.index({ role: 1, createdAt: -1 });

// 唯一索引
userSchema.index({ email: 1 }, { unique: true });

// 部分索引
userSchema.index(
  { email: 1 },
  { partialFilterExpression: { isActive: true } }
);

// TTL 索引（自动删除后时间）
sessionSchema.index({ createdAt: 1 }, { expireAfterSeconds: 3600 });

// 文本索引用于搜索
postSchema.index({ title: 'text', content: 'text' });

// 地理空间索引
locationSchema.index({ coordinates: '2dsphere' });

// 检查索引
const indexes = await User.collection.getIndexes();
```

## 性能技巧

```typescript
// 使用 lean() 进行只读查询
const users = await User.find().lean();

// 选择需要的字段
const users = await User.find().select('name email');

// 使用游标处理大数据集
const cursor = User.find().cursor();
for await (const user of cursor) {
  // 逐个处理
}

// 批量操作
const bulkOps = [
  { insertOne: { document: { name: 'User 1' } } },
  { updateOne: { filter: { _id: id1 }, update: { $set: { name: 'Updated' } } } },
  { deleteOne: { filter: { _id: id2 } } },
];
await User.bulkWrite(bulkOps);

// 查询解释
const explanation = await User.find({ role: 'admin' }).explain('executionStats');
```

## MongoDB Atlas

```typescript
// Atlas 连接字符串
const uri = 'mongodb+srv://user:password@cluster.mongodb.net/dbname?retryWrites=true&w=majority';

// Atlas 搜索（全文搜索）
const results = await Product.aggregate([
  { $search: {
    index: 'default',
    text: {
      query: 'wireless headphones',
      path: ['name', 'description'],
      fuzzy: { maxEdits: 1 },
    },
  }},
  { $project: {
    name: 1,
    score: { $meta: 'searchScore' },
  }},
]);

// Atlas 向量搜索
const results = await Product.aggregate([
  { $vectorSearch: {
    index: 'vector_index',
    path: 'embedding',
    queryVector: [0.1, 0.2, ...],
    numCandidates: 100,
    limit: 10,
  }},
]);
```

## 资源

- **MongoDB 文档**: https://www.mongodb.com/docs/
- **Mongoose 文档**: https://mongoosejs.com/docs/
- **MongoDB 大学**: https://learn.mongodb.com/
- **Atlas 文档**: https://www.mongodb.com/docs/atlas/
