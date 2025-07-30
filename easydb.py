import sqlite3
import json
from typing import Any, Optional, List, Union
import html


class EasyDBList:
    """
    表示一个数据库列表的类，支持索引操作
    """

    def __init__(self, db: 'EasyDB', list_name: str):
        self.db = db
        self.list_name = list_name

    def __getitem__(self, index: int) -> Any:
        """
        获取列表中指定位置的元素，用法：item = db.list_name[index]
        """
        return self.db.list_get_item(self.list_name, index)

    def __setitem__(self, index: int, item: Any):
        """
        设置列表中指定位置的元素，用法：db.list_name[index] = item
        """
        # 检查列表长度，如果索引超出范围，则添加元素
        length = self.db.list_len(self.list_name)
        if index >= length:
            # 添加新元素
            for i in range(length, index):
                self.db.list_append(self.list_name, None)
            self.db.list_append(self.list_name, item)
        else:
            self.db.list_set(self.list_name, index, item)

    def __len__(self) -> int:
        """
        获取列表长度，用法：len(db.list_name)
        """
        return self.db.list_len(self.list_name)

    def append(self, item: Any):
        """
        向列表末尾添加元素
        """
        self.db.list_append(self.list_name, item)

    def remove(self, index: int):
        """
        删除列表中指定位置的元素
        """
        self.db.list_remove(self.list_name, index)

    def __str__(self) -> str:
        """
        返回列表的字符串表示
        """
        return str(self.db.list_get(self.list_name))

    def __repr__(self) -> str:
        """
        返回列表的详细表示
        """
        return f"EasyDBList({self.db.list_get(self.list_name)})"


class EasyDB:
    """
    一个简单的数据库封装库，让使用者可以像操作变量和列表一样操作SQLite数据库
    """

    def __init__(self, db_name: str = "easy.db"):
        """
        初始化数据库连接
        
        Args:
            db_name: 数据库文件名，默认为"easy.db"
        """
        self.db_name = db_name
        self._initialize_database()

    def _initialize_database(self):
        """
        初始化数据库表
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # 创建存储键值对的表（如果不存在）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kv_store (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # 创建存储列表的表（如果不存在）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS list_store (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                list_name TEXT NOT NULL,
                item_index INTEGER NOT NULL,
                item_value TEXT,
                UNIQUE(list_name, item_index)
            )
        ''')
        
        conn.commit()
        conn.close()

    def __setitem__(self, key: str, value: Any):
        """
        设置键值对，用法：db['key'] = value
        
        Args:
            key: 键名
            value: 值（可以是任意可JSON序列化的对象）
        """
        self._set_key_value(key, value)

    def __getitem__(self, key: str) -> Any:
        """
        获取键对应的值，用法：value = db['key']
        
        Args:
            key: 键名
            
        Returns:
            键对应的值
            
        Raises:
            KeyError: 当键不存在时抛出异常
        """
        return self._get_key_value(key)

    def __delitem__(self, key: str):
        """
        删除键值对，用法：del db['key']
        
        Args:
            key: 要删除的键名
            
        Raises:
            KeyError: 当键不存在时抛出异常
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM kv_store WHERE key = ?
        ''', (key,))
        
        if cursor.rowcount == 0:
            conn.close()
            raise KeyError(f"Key '{key}' not found")
            
        conn.commit()
        conn.close()

    def __contains__(self, key: str) -> bool:
        """
        检查键是否存在，用法：'key' in db
        
        Args:
            key: 要检查的键名
            
        Returns:
            键是否存在
        """
        try:
            self.__getitem__(key)
            return True
        except KeyError:
            return False

    def __setattr__(self, name: str, value: Any):
        """
        设置属性值，支持db.tasks = [...]语法
        
        Args:
            name: 属性名
            value: 属性值
        """
        # 处理内部属性
        if name.startswith('_') or name in ['db_name']:
            super().__setattr__(name, value)
            return
            
        # 处理数据库属性
        if not name.startswith('_'):
            # 如果值是列表，则特殊处理
            if isinstance(value, list):
                self._set_list(name, value)
            else:
                self._set_key_value(name, value)
        else:
            super().__setattr__(name, value)

    def __getattr__(self, name: str) -> Any:
        """
        获取属性值，支持db.tasks语法
        
        Args:
            name: 属性名
            
        Returns:
            属性值
        """
        # 特殊属性：all_data
        if name == 'all_data':
            return self._get_all_data()
        
        # 特殊属性：html_report
        if name == 'html_report':
            return self._generate_html_report()
        
        # 检查是否为列表
        if self._is_list(name):
            return EasyDBList(self, name)
        
        # 尝试获取键值
        try:
            return self._get_key_value(name)
        except KeyError:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def _set_key_value(self, key: str, value: Any):
        """
        设置键值对的内部方法
        
        Args:
            key: 键名
            value: 值（可以是任意可JSON序列化的对象）
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # 将值转换为JSON字符串存储
        value_str = json.dumps(value)
        
        cursor.execute('''
            INSERT OR REPLACE INTO kv_store (key, value)
            VALUES (?, ?)
        ''', (key, value_str))
        
        conn.commit()
        conn.close()

    def _get_key_value(self, key: str) -> Any:
        """
        获取键值对的内部方法
        
        Args:
            key: 键名
            
        Returns:
            键对应的值
            
        Raises:
            KeyError: 当键不存在时抛出异常
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT value FROM kv_store WHERE key = ?
        ''', (key,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result is None:
            raise KeyError(f"Key '{key}' not found")
        
        # 将存储的JSON字符串转换回原始对象
        return json.loads(result[0])

    def _set_list(self, list_name: str, items: List[Any]):
        """
        设置列表的内部方法
        
        Args:
            list_name: 列表名称
            items: 列表项
        """
        # 先清空现有列表
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM list_store WHERE list_name = ?
        ''', (list_name,))
        
        # 添加新项
        for index, item in enumerate(items):
            item_str = json.dumps(item)
            cursor.execute('''
                INSERT INTO list_store (list_name, item_index, item_value)
                VALUES (?, ?, ?)
            ''', (list_name, index, item_str))
        
        conn.commit()
        conn.close()

    def _is_list(self, name: str) -> bool:
        """
        检查给定名称是否为列表
        
        Args:
            name: 名称
            
        Returns:
            是否为列表
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM list_store WHERE list_name = ?
        ''', (name,))
        
        result = cursor.fetchone()[0] > 0
        conn.close()
        return result

    def _get_all_data(self) -> dict:
        """
        获取所有数据，包括EasyDB格式的数据和其他表的数据
        
        Returns:
            包含所有数据的字典
        """
        all_data = {}
        
        # 获取所有EasyDB格式的键值对
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT key, value FROM kv_store
            ''')
            
            for key, value_str in cursor.fetchall():
                all_data[key] = json.loads(value_str)
        except sqlite3.OperationalError:
            # 如果表不存在，忽略错误
            pass
        
        try:
            # 获取所有EasyDB格式的列表
            cursor.execute('''
                SELECT DISTINCT list_name FROM list_store
            ''')
            
            for row in cursor.fetchall():
                list_name = row[0]
                all_data[list_name] = self.list_get(list_name)
        except sqlite3.OperationalError:
            # 如果表不存在，忽略错误
            pass
        
        # 获取其他表的信息
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                # 跳过EasyDB内部表
                if table_name in ['kv_store', 'list_store', 'sqlite_sequence']:
                    continue
                
                # 获取表结构
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = [col[1] for col in cursor.fetchall()]
                
                # 获取表数据
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                # 将数据转换为字典列表格式
                table_data = []
                for row in rows:
                    row_dict = {}
                    for i, col_name in enumerate(columns):
                        row_dict[col_name] = row[i]
                    table_data.append(row_dict)
                
                all_data[table_name] = table_data
        except sqlite3.OperationalError:
            # 如果有任何错误，忽略该表
            pass
        
        conn.close()
        return all_data

    def _generate_html_report(self) -> str:
        """
        生成HTML格式的数据库报告
        
        Returns:
            HTML格式的报告字符串
        """
        all_data = self._get_all_data()
        
        # 开始构建HTML
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EasyDB Report - {self.db_name}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #007acc;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #007acc;
            margin-top: 30px;
        }}
        .section {{
            margin-bottom: 30px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #fafafa;
        }}
        .table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}
        .table th, .table td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        .table th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}
        .table tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        .json {{
            font-family: 'Courier New', monospace;
            background-color: #f8f8f8;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
            white-space: pre-wrap;
        }}
        .key-value {{
            display: flex;
            margin-bottom: 10px;
        }}
        .key {{
            font-weight: bold;
            min-width: 150px;
        }}
        .value {{
            flex: 1;
        }}
        .collapsible {{
            background-color: #f1f1f1;
            color: #444;
            cursor: pointer;
            padding: 10px;
            width: 100%;
            border: none;
            text-align: left;
            outline: none;
            font-size: 15px;
            margin-top: 5px;
        }}
        .active, .collapsible:hover {{
            background-color: #ccc;
        }}
        .content {{
            padding: 0 18px;
            display: none;
            overflow: hidden;
            background-color: #f9f9f9;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>EasyDB 数据库报告</h1>
        <p><strong>数据库文件:</strong> {self.db_name}</p>
        <p><strong>生成时间:</strong> {self._get_current_time()}</p>
        
        <div class="section">
            <h2>数据库概览</h2>
            <div class="key-value">
                <div class="key">数据表数量:</div>
                <div class="value">{len([k for k, v in all_data.items() if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict)])}</div>
            </div>
            <div class="key-value">
                <div class="key">EasyDB 键值对:</div>
                <div class="value">{len([k for k in all_data.keys() if not (isinstance(all_data[k], list) and len(all_data[k]) > 0 and isinstance(all_data[k][0], dict))])}</div>
            </div>
        </div>
"""

        # 添加EasyDB数据部分
        easydb_data = {k: v for k, v in all_data.items() 
                      if not (isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict))}
        
        if easydb_data:
            html_content += """
        <div class="section">
            <h2>EasyDB 数据</h2>
"""
            for key, value in easydb_data.items():
                html_content += f"""
            <button class="collapsible">{html.escape(str(key))}</button>
            <div class="content">
                <div class="json">{html.escape(json.dumps(value, indent=2, ensure_ascii=False))}</div>
            </div>
"""
            html_content += "        </div>\n"

        # 添加表数据部分
        table_data = {k: v for k, v in all_data.items() 
                     if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict)}
        
        if table_data:
            html_content += """
        <div class="section">
            <h2>数据表</h2>
"""
            for table_name, rows in table_data.items():
                html_content += f"""
            <button class="collapsible">{html.escape(table_name)} ({len(rows)} 行)</button>
            <div class="content">
"""
                if rows:
                    # 表结构
                    columns = list(rows[0].keys())
                    html_content += f"""
                <table class="table">
                    <thead>
                        <tr>
"""
                    for col in columns:
                        html_content += f"                            <th>{html.escape(col)}</th>\n"
                    html_content += """                        </tr>
                    </thead>
                    <tbody>
"""
                    # 表数据（最多显示10行）
                    for i, row in enumerate(rows[:10]):
                        html_content += "                        <tr>\n"
                        for col in columns:
                            value = row.get(col, '')
                            html_content += f"                            <td>{html.escape(str(value))[:100]}{'...' if len(str(value)) > 100 else ''}</td>\n"
                        html_content += "                        </tr>\n"
                    
                    html_content += """                    </tbody>
                </table>
"""
                    if len(rows) > 10:
                        html_content += f"                <p><em>注意: 仅显示前10行，总共{len(rows)}行</em></p>\n"
                else:
                    html_content += "                <p>表为空</p>\n"
                
                html_content += """            </div>
"""
            html_content += "        </div>\n"

        # 结束HTML
        html_content += """
        <script>
            var coll = document.getElementsByClassName("collapsible");
            var i;
            
            for (i = 0; i < coll.length; i++) {
                coll[i].addEventListener("click", function() {
                    this.classList.toggle("active");
                    var content = this.nextElementSibling;
                    if (content.style.display === "block") {
                        content.style.display = "none";
                    } else {
                        content.style.display = "block";
                    }
                });
            }
        </script>
    </div>
</body>
</html>
"""
        
        return html_content

    def _get_current_time(self) -> str:
        """
        获取当前时间字符串
        
        Returns:
            当前时间字符串
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def keys(self) -> List[str]:
        """
        获取所有键的列表
        
        Returns:
            所有键的列表
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT key FROM kv_store
            ''')
            
            result = [row[0] for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            # 如果表不存在，返回空列表
            result = []
        
        conn.close()
        return result

    def values(self) -> List[Any]:
        """
        获取所有值的列表
        
        Returns:
            所有值的列表
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT value FROM kv_store
            ''')
            
            result = [json.loads(row[0]) for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            # 如果表不存在，返回空列表
            result = []
        
        conn.close()
        return result

    def items(self) -> List[tuple]:
        """
        获取所有键值对的列表
        
        Returns:
            所有键值对的列表
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT key, value FROM kv_store
            ''')
            
            result = [(row[0], json.loads(row[1])) for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            # 如果表不存在，返回空列表
            result = []
        
        conn.close()
        return result

    # 列表操作方法
    def list_create(self, list_name: str):
        """
        创建一个空列表
        
        Args:
            list_name: 列表名称
        """
        # 创建列表实际上不需要特殊操作，只需确保表存在
        pass

    def list_append(self, list_name: str, item: Any):
        """
        向列表末尾添加元素
        
        Args:
            list_name: 列表名称
            item: 要添加的元素
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # 获取列表当前长度作为新元素的索引
        cursor.execute('''
            SELECT COUNT(*) FROM list_store WHERE list_name = ?
        ''', (list_name,))
        
        index = cursor.fetchone()[0]
        item_str = json.dumps(item)
        
        cursor.execute('''
            INSERT INTO list_store (list_name, item_index, item_value)
            VALUES (?, ?, ?)
        ''', (list_name, index, item_str))
        
        conn.commit()
        conn.close()

    def list_get(self, list_name: str) -> List[Any]:
        """
        获取整个列表
        
        Args:
            list_name: 列表名称
            
        Returns:
            列表的所有元素
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT item_value FROM list_store 
            WHERE list_name = ?
            ORDER BY item_index
        ''', (list_name,))
        
        result = [json.loads(row[0]) for row in cursor.fetchall()]
        conn.close()
        return result

    def list_set(self, list_name: str, index: int, item: Any):
        """
        设置列表中指定位置的元素
        
        Args:
            list_name: 列表名称
            index: 索引位置
            item: 新的元素值
            
        Raises:
            IndexError: 当索引超出范围时抛出异常
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        item_str = json.dumps(item)
        
        cursor.execute('''
            UPDATE list_store 
            SET item_value = ?
            WHERE list_name = ? AND item_index = ?
        ''', (item_str, list_name, index))
        
        if cursor.rowcount == 0:
            # 检查索引是否有效
            cursor.execute('''
                SELECT COUNT(*) FROM list_store WHERE list_name = ?
            ''', (list_name,))
            
            count = cursor.fetchone()[0]
            conn.close()
            if index >= count:
                raise IndexError("list index out of range")
            else:
                # 索引存在但更新失败，这不应该发生
                raise Exception("Failed to update list item")
                
        conn.commit()
        conn.close()

    def list_get_item(self, list_name: str, index: int) -> Any:
        """
        获取列表中指定位置的元素
        
        Args:
            list_name: 列表名称
            index: 索引位置
            
        Returns:
            指定位置的元素
            
        Raises:
            IndexError: 当索引超出范围时抛出异常
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT item_value FROM list_store 
            WHERE list_name = ? AND item_index = ?
        ''', (list_name, index))
        
        result = cursor.fetchone()
        conn.close()
        
        if result is None:
            raise IndexError("list index out of range")
            
        return json.loads(result[0])

    def list_remove(self, list_name: str, index: int):
        """
        删除列表中指定位置的元素
        
        Args:
            list_name: 列表名称
            index: 要删除元素的索引位置
            
        Raises:
            IndexError: 当索引超出范围时抛出异常
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # 检查元素是否存在
        cursor.execute('''
            SELECT item_index FROM list_store 
            WHERE list_name = ? AND item_index = ?
        ''', (list_name, index))
        
        if cursor.fetchone() is None:
            conn.close()
            raise IndexError("list index out of range")
        
        # 删除元素
        cursor.execute('''
            DELETE FROM list_store 
            WHERE list_name = ? AND item_index = ?
        ''', (list_name, index))
        
        # 更新后续元素的索引
        cursor.execute('''
            UPDATE list_store 
            SET item_index = item_index - 1 
            WHERE list_name = ? AND item_index > ?
        ''', (list_name, index))
        
        conn.commit()
        conn.close()

    def list_len(self, list_name: str) -> int:
        """
        获取列表长度
        
        Args:
            list_name: 列表名称
            
        Returns:
            列表长度
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM list_store WHERE list_name = ?
        ''', (list_name,))
        
        result = cursor.fetchone()[0]
        conn.close()
        return result


# 使用示例
if __name__ == "__main__":
    # 创建数据库实例
    db = EasyDB("example.db")
    
    # 使用字典风格操作
    db['name'] = '张三'
    db['age'] = 25
    db['hobbies'] = ['读书', '游泳', '编程']
    
    print(f"姓名: {db['name']}")
    print(f"年龄: {db['age']}")
    print(f"爱好: {db['hobbies']}")
    
    # 检查键是否存在
    if 'name' in db:
        print("'name' 键存在")
    
    # 获取所有键值对
    print("所有数据:")
    for key, value in db.items():
        print(f"  {key}: {value}")
    
    # 使用列表操作
    db.list_create('numbers')
    for i in range(5):
        db.list_append('numbers', i * 2)
    
    print(f"numbers 列表: {db.list_get('numbers')}")
    print(f"numbers 列表长度: {db.list_len('numbers')}")
    
    # 修改列表元素
    db.list_set('numbers', 2, 100)
    print(f"修改后的 numbers 列表: {db.list_get('numbers')}")
    
    # 获取特定元素
    print(f"numbers[0] = {db.list_get_item('numbers', 0)}")
    
    # 删除元素
    db.list_remove('numbers', 1)
    print(f"删除元素后的 numbers 列表: {db.list_get('numbers')}")