# EasyDB

EasyDB 是一个简单易用的 SQLite 数据库封装库，让你可以像操作 Python 变量和列表一样操作数据库。它提供了直观的 API，同时保持与原生 SQLite 的完全兼容性。

EasyDB is a simple and easy-to-use SQLite database wrapper that allows you to work with databases just like Python variables and lists. It provides an intuitive API while maintaining full compatibility with native SQLite.

## 特性 / Features

- **直观的 API**：像操作普通变量一样操作数据库
- **自动序列化**：支持字符串、数字、列表、字典等复杂数据类型
- **双向兼容**：既可以通过 EasyDB API 操作数据，也可以通过原生 SQLite 访问
- **HTML 报告**：生成美观的 HTML 报告展示数据库内容
- **现有数据库支持**：可以读取和操作现有的 SQLite 数据库文件

- **Intuitive API**: Work with databases like Python variables
- **Automatic Serialization**: Supports complex data types such as strings, numbers, lists, and dictionaries
- **Bidirectional Compatibility**: Access data through both EasyDB API and native SQLite
- **HTML Reports**: Generate beautiful HTML reports to visualize database content
- **Existing Database Support**: Read and manipulate existing SQLite database files

## 安装 / Installation

EasyDB 只需要 Python 3 和内置的 sqlite3 模块，无需额外安装依赖。

将 [easydb.py](file:///Users/mcl/Desktop/easy_db/easydb.py) 文件复制到你的项目中即可使用。

EasyDB only requires Python 3 and the built-in sqlite3 module, with no additional dependencies needed.

Copy the [easydb.py](file:///Users/mcl/Desktop/easy_db/easydb.py) file into your project to get started.

## 快速开始 / Quick Start

### 基本用法 / Basic Usage

```python
from easydb import EasyDB

# 创建数据库实例
# Create a database instance
db = EasyDB("my_database.db")

# 像操作变量一样设置值
# Work with data like Python variables
db.username = "Alice"
db.age = 30
db.is_active = True

# 存储复杂数据类型
# Store complex data types
db.settings = {
    "theme": "dark",
    "language": "zh-CN",
    "notifications": True
}

db.tasks = ["写代码", "测试功能", "写文档"]
# Translated: ["Write code", "Test features", "Write documentation"]

# 像访问变量一样获取值
# Access data the same way
print(db.username)  # 输出: Alice / Output: Alice
print(db.settings["theme"])  # 输出: dark / Output: dark

# 检查键是否存在
# Check if a key exists
if 'username' in db:
    print("用户名已设置")
    # Translated: print("Username is set")

# 删除键值对
# Delete a key-value pair
del db.age
```

### 列表操作 / List Operations

```python
# 创建和操作列表
# Create and manipulate lists
db.my_list = [1, 2, 3, 4, 5]

# 访问列表元素
# Access list elements
print(db.my_list[0])  # 输出: 1 / Output: 1

# 修改列表元素
# Modify list elements
db.my_list[0] = 10
print(db.my_list)  # 输出: [10, 2, 3, 4, 5] / Output: [10, 2, 3, 4, 5]

# 获取列表长度
# Get list length
print(len(db.my_list))  # 输出: 5 / Output: 5

# 使用索引添加新元素（自动扩展列表）
# Add new elements by index (list auto-expands)
db.my_list[10] = "新元素"
# Translated: db.my_list[10] = "New element"
print(len(db.my_list))  # 输出: 11 / Output: 11
```

### 获取所有数据 / Get All Data

```python
# 获取所有数据
# Get all data
all_data = db.all_data
print(all_data)

# 获取所有键
# Get all keys
keys = db.keys()
print(keys)

# 获取所有值
# Get all values
values = db.values()
print(values)

# 获取所有键值对
# Get all key-value pairs
items = db.items()
for key, value in items:
    print(f"{key}: {value}")
```

### HTML 报告 / HTML Reports

```python
# 生成 HTML 报告
# Generate HTML report
html_report = db.html_report

# 保存到文件
# Save to file
with open("database_report.html", "w", encoding="utf-8") as f:
    f.write(html_report)
```

## 高级用法 / Advanced Usage

### 使用现有数据库 / Working with Existing Databases

EasyDB 可以读取和操作现有的 SQLite 数据库文件：

EasyDB can read and manipulate existing SQLite database files:

```python
# 连接到现有数据库
# Connect to an existing database
db = EasyDB("existing_database.db")

# 查看所有数据（包括原有表数据）
# View all data (including original table data)
all_data = db.all_data

# 原有表数据以列表形式展示，每行是一个字典
# Original table data is displayed as a list, with each row as a dictionary
if 'users' in all_data:
    for user in all_data['users']:
        print(f"用户: {user['username']}, 邮箱: {user['email']}")
        # Translated: print(f"User: {user['username']}, Email: {user['email']}")
```

### 与原生 SQLite 互操作 / Interoperability with Native SQLite

EasyDB 创建的数据可以通过原生 SQLite 直接访问：

Data created by EasyDB can be directly accessed through native SQLite:

```python
import sqlite3
import json

# EasyDB 创建的数据存储在 kv_store 和 list_store 表中
# Data created by EasyDB is stored in kv_store and list_store tables
conn = sqlite3.connect("my_database.db")
cursor = conn.cursor()

# 读取键值对数据
# Read key-value data
cursor.execute("SELECT key, value FROM kv_store")
for key, value_str in cursor.fetchall():
    value = json.loads(value_str)  # EasyDB 使用 JSON 存储数据
    # Translated: value = json.loads(value_str)  # EasyDB stores data as JSON
    print(f"{key}: {value}")

# 修改数据
# Modify data
cursor.execute("""
    UPDATE kv_store 
    SET value = ? 
    WHERE key = 'username'
""", (json.dumps("Bob"),))

conn.commit()
conn.close()
```

同样，通过原生 SQLite 添加的数据也可以通过 EasyDB 访问：

Similarly, data added through native SQLite can also be accessed through EasyDB:

```python
import sqlite3

# 创建新表
# Create a new table
conn = sqlite3.connect("my_database.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL
    )
""")

cursor.execute("""
    INSERT INTO products (name, price) 
    VALUES (?, ?)
""", ("笔记本电脑", 5999.99))
# Translated: ("Laptop", 5999.99)

conn.commit()
conn.close()

# 通过 EasyDB 访问新表
# Access the new table through EasyDB
db = EasyDB("my_database.db")
products = db.all_data['products']  # 自动识别新表
# Translated: products = db.all_data['products']  # Automatically recognizes new tables
for product in products:
    print(f"产品: {product['name']}, 价格: {product['price']}")
    # Translated: print(f"Product: {product['name']}, Price: {product['price']}")
```

## API 参考 / API Reference

### EasyDB 类 / EasyDB Class

#### `EasyDB(db_name="easy.db")`

创建 EasyDB 实例。

Create an EasyDB instance.

参数 / Parameters:
- `db_name`: 数据库文件名，默认为 "easy.db"
- `db_name`: Database file name, defaults to "easy.db"

#### 属性操作 / Attribute Operations

```python
# 设置值
# Set value
db.key = value

# 获取值
# Get value
value = db.key

# 删除值
# Delete value
del db.key

# 检查键是否存在
# Check if key exists
key in db
```

#### 列表操作 / List Operations

```python
# 设置列表
# Set list
db.my_list = [1, 2, 3]

# 访问元素
# Access element
element = db.my_list[0]

# 修改元素
# Modify element
db.my_list[0] = new_value

# 获取长度
# Get length
len(db.my_list)
```

#### 特殊属性 / Special Attributes

- `db.all_data`: 获取包含所有数据的字典
- `db.html_report`: 生成 HTML 格式的数据库报告
- `db.keys()`: 获取所有键的列表
- `db.values()`: 获取所有值的列表
- `db.items()`: 获取所有键值对的列表

- `db.all_data`: Get a dictionary containing all data
- `db.html_report`: Generate an HTML database report
- `db.keys()`: Get a list of all keys
- `db.values()`: Get a list of all values
- `db.items()`: Get a list of all key-value pairs

## 数据存储结构 / Data Storage Structure

EasyDB 使用两个表来存储数据：

EasyDB uses two tables to store data:

1. **kv_store**: 存储键值对数据
   - `key`: 键名（TEXT PRIMARY KEY）
   - `value`: 值（TEXT，以 JSON 格式存储）

1. **kv_store**: Stores key-value data
   - `key`: Key name (TEXT PRIMARY KEY)
   - `value`: Value (TEXT, stored in JSON format)

2. **list_store**: 存储列表数据
   - `id`: 自增主键（INTEGER PRIMARY KEY AUTOINCREMENT）
   - `list_name`: 列表名称（TEXT NOT NULL）
   - `item_index`: 元素索引（INTEGER NOT NULL）
   - `item_value`: 元素值（TEXT，以 JSON 格式存储）

2. **list_store**: Stores list data
   - `id`: Auto-incrementing primary key (INTEGER PRIMARY KEY AUTOINCREMENT)
   - `list_name`: List name (TEXT NOT NULL)
   - `item_index`: Element index (INTEGER NOT NULL)
   - `item_value`: Element value (TEXT, stored in JSON format)

所有非 EasyDB 格式的数据表都会被自动识别并在 `all_data` 和 `html_report` 中展示。

All non-EasyDB format data tables are automatically recognized and displayed in `all_data` and `html_report`.

## 使用示例 / Usage Examples

### 项目配置管理 / Project Configuration Management

```python
from easydb import EasyDB

db = EasyDB("config.db")

# 存储应用配置
# Store application configuration
db.app_config = {
    "database_url": "sqlite:///app.db",
    "debug": True,
    "secret_key": "your-secret-key"
}

# 存储用户设置
# Store user preferences
db.user_preferences = {
    "theme": "dark",
    "language": "zh-CN",
    "notifications": {
        "email": True,
        "push": False
    }
}

# 存储任务队列
# Store task queue
db.task_queue = [
    "处理用户注册",
    "发送欢迎邮件",
    "初始化用户数据"
]
# Translated: [
# Translated:     "Process user registration",
# Translated:     "Send welcome email",
# Translated:     "Initialize user data"
# Translated: ]

# 持久化存储，即使程序重启数据也不会丢失
# Persistent storage - data remains even after program restart
```

### 数据分析和报告 / Data Analysis and Reporting

```python
from easydb import EasyDB

db = EasyDB("analytics.db")

# 存储统计数据
# Store statistical data
db.daily_visits = [120, 150, 180, 200, 250]
db.user_feedback = [
    {"rating": 5, "comment": "很好用"},
    {"rating": 4, "comment": "功能不错"},
    {"rating": 3, "comment": "还可以"}
]
# Translated: {"rating": 5, "comment": "Great"},
# Translated: {"rating": 4, "comment": "Good features"},
# Translated: {"rating": 3, "comment": "Okay"}

# 生成报告
# Generate report
html_report = db.html_report
with open("analytics_report.html", "w", encoding="utf-8") as f:
    f.write(html_report)
```

## 注意事项 / Notes

1. **数据类型**: EasyDB 使用 JSON 序列化存储数据，因此只能存储 JSON 支持的数据类型（字符串、数字、布尔值、列表、字典和 None）

2. **性能**: 对于大量数据操作，直接使用 SQLite 可能更高效

3. **并发访问**: EasyDB 没有特殊的并发控制，如需并发访问请使用 SQLite 的锁机制

4. **备份**: 可以直接复制 .db 文件进行备份

1. **Data Types**: EasyDB uses JSON serialization to store data, so it can only store data types supported by JSON (strings, numbers, booleans, lists, dictionaries, and None)

2. **Performance**: For large data operations, using SQLite directly may be more efficient

3. **Concurrent Access**: EasyDB has no special concurrency control. For concurrent access, please use SQLite's locking mechanism

4. **Backup**: You can directly copy the .db file for backup

## 许可证 / License

MIT License

## 贡献 / Contributing

欢迎提交 Issue 和 Pull Request 来改进 EasyDB。

Welcome to submit Issues and Pull Requests to improve EasyDB.
