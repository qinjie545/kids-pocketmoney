"""
收入和支出功能的自动化测试用例
"""
import unittest
import os
import sqlite3
from werkzeug.security import generate_password_hash

# 使用测试数据库
TEST_DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'test_cash_manager.db')

# 在导入app之前设置环境变量，让app使用测试数据库
os.environ['TEST_DATABASE_PATH'] = TEST_DATABASE_PATH

from app import app


class TransactionTestCase(unittest.TestCase):
    """交易功能测试用例"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化，创建测试数据库和测试用户"""
        # 设置测试数据库路径
        app.config['TESTING'] = True
        app.config['DATABASE_PATH'] = TEST_DATABASE_PATH

        # 删除可能存在的旧测试数据库
        if os.path.exists(TEST_DATABASE_PATH):
            os.remove(TEST_DATABASE_PATH)

        # 创建测试数据库
        conn = sqlite3.connect(TEST_DATABASE_PATH)
        cursor = conn.cursor()

        # 创建表结构
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # 创建测试用户
        hashed_password = generate_password_hash('test123')
        cursor.execute(
            'INSERT INTO users (id, username, password) VALUES (?, ?, ?)',
            (1, 'testuser', hashed_password)
        )

        conn.commit()
        conn.close()

    def setUp(self):
        """每个测试方法执行前的准备工作"""
        self.client = app.test_client()

        # 登录获取session
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'testuser'

        # 彻底清空交易记录
        conn = sqlite3.connect(TEST_DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM transactions')
        conn.commit()
        conn.close()

    def tearDown(self):
        """每个测试方法执行后的清理工作"""
        # 彻底清空交易记录
        conn = sqlite3.connect(TEST_DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM transactions')
        conn.commit()
        conn.close()

    @classmethod
    def tearDownClass(cls):
        """测试类清理，删除测试数据库"""
        if os.path.exists(TEST_DATABASE_PATH):
            os.remove(TEST_DATABASE_PATH)

    def test_add_income(self):
        """测试添加收入记录"""
        response = self.client.post('/api/transactions',
                                   json={
                                       'type': 'income',
                                       'amount': 100.00,
                                       'category': '零花钱',
                                       'description': '测试收入'
                                   },
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        
        # 验证余额
        balance_response = self.client.get('/api/balance')
        balance_data = balance_response.get_json()
        self.assertEqual(balance_data['balance'], 100.00)
        self.assertEqual(balance_data['income'], 100.00)
        self.assertEqual(balance_data['expense'], 0.00)

    def test_add_expense(self):
        """测试添加支出记录"""
        # 先添加一笔收入
        self.client.post('/api/transactions',
                        json={
                            'type': 'income',
                            'amount': 200.00,
                            'category': '零花钱',
                            'description': '初始收入'
                        },
                        content_type='application/json')
        
        # 添加一笔支出
        response = self.client.post('/api/transactions',
                                   json={
                                       'type': 'expense',
                                       'amount': 50.00,
                                       'category': '零食',
                                       'description': '测试支出'
                                   },
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        
        # 验证余额：200 - 50 = 150
        balance_response = self.client.get('/api/balance')
        balance_data = balance_response.get_json()
        self.assertEqual(balance_data['balance'], 150.00)
        self.assertEqual(balance_data['income'], 200.00)
        self.assertEqual(balance_data['expense'], 50.00)

    def test_expense_reduces_balance(self):
        """测试支出会减少余额（这是修复的bug）"""
        # 初始余额：100
        self.client.post('/api/transactions',
                        json={
                            'type': 'income',
                            'amount': 100.00,
                            'category': '零花钱',
                            'description': '初始收入'
                        },
                        content_type='application/json')
        
        # 获取初始余额
        balance_before = self.client.get('/api/balance').get_json()['balance']
        self.assertEqual(balance_before, 100.00)
        
        # 支出30
        self.client.post('/api/transactions',
                        json={
                            'type': 'expense',
                            'amount': 30.00,
                            'category': '零食',
                            'description': '买零食'
                        },
                        content_type='application/json')
        
        # 验证余额减少：100 - 30 = 70
        balance_after = self.client.get('/api/balance').get_json()['balance']
        self.assertEqual(balance_after, 70.00)
        self.assertLess(balance_after, balance_before, "支出后余额应该减少")

    def test_income_increases_balance(self):
        """测试收入会增加余额"""
        # 初始余额：50
        self.client.post('/api/transactions',
                        json={
                            'type': 'income',
                            'amount': 50.00,
                            'category': '零花钱',
                            'description': '初始收入'
                        },
                        content_type='application/json')
        
        # 获取初始余额
        balance_before = self.client.get('/api/balance').get_json()['balance']
        self.assertEqual(balance_before, 50.00)
        
        # 收入80
        self.client.post('/api/transactions',
                        json={
                            'type': 'income',
                            'amount': 80.00,
                            'category': '奖励',
                            'description': '奖励'
                        },
                        content_type='application/json')
        
        # 验证余额增加：50 + 80 = 130
        balance_after = self.client.get('/api/balance').get_json()['balance']
        self.assertEqual(balance_after, 130.00)
        self.assertGreater(balance_after, balance_before, "收入后余额应该增加")

    def test_multiple_transactions_balance(self):
        """测试多笔交易的余额计算"""
        # 添加多笔交易
        transactions = [
            {'type': 'income', 'amount': 100.00, 'category': '零花钱', 'description': '收入1'},
            {'type': 'income', 'amount': 50.00, 'category': '奖励', 'description': '收入2'},
            {'type': 'expense', 'amount': 30.00, 'category': '零食', 'description': '支出1'},
            {'type': 'expense', 'amount': 20.00, 'category': '文具', 'description': '支出2'},
            {'type': 'income', 'amount': 25.00, 'category': '红包', 'description': '收入3'},
        ]
        
        for tx in transactions:
            self.client.post('/api/transactions',
                           json=tx,
                           content_type='application/json')
        
        # 验证余额：(100 + 50 + 25) - (30 + 20) = 175 - 50 = 125
        balance_response = self.client.get('/api/balance')
        balance_data = balance_response.get_json()
        self.assertEqual(balance_data['balance'], 125.00)
        self.assertEqual(balance_data['income'], 175.00)
        self.assertEqual(balance_data['expense'], 50.00)

    def test_delete_transaction_updates_balance(self):
        """测试删除交易后余额更新"""
        # 添加收入和支出
        self.client.post('/api/transactions',
                         json={
                             'type': 'income',
                             'amount': 100.00,
                             'category': '零花钱',
                             'description': '收入'
                         },
                         content_type='application/json')
        
        self.client.post('/api/transactions',
                         json={
                             'type': 'expense',
                             'amount': 40.00,
                             'category': '零食',
                             'description': '支出'
                         },
                         content_type='application/json')
        
        # 验证初始余额：100 - 40 = 60
        balance_before = self.client.get('/api/balance').get_json()['balance']
        self.assertEqual(balance_before, 60.00)
        
        # 获取交易列表，找到支出记录的ID
        transactions_response = self.client.get('/api/transactions?page=1&per_page=10')
        transactions_data = transactions_response.get_json()
        self.assertTrue(transactions_data['success'])
        
        # 找到支出记录
        expense_tx = None
        for tx in transactions_data['transactions']:
            if tx['type'] == 'expense' and tx['amount'] == 40.00:
                expense_tx = tx
                break
        
        self.assertIsNotNone(expense_tx, "应该能找到支出记录")
        expense_id = expense_tx['id']
        
        # 删除支出记录
        delete_response = self.client.delete(f'/api/transactions/{expense_id}')
        self.assertEqual(delete_response.status_code, 200)
        delete_data = delete_response.get_json()
        self.assertTrue(delete_data['success'])
        
        # 验证余额恢复：100 - 0 = 100
        balance_after = self.client.get('/api/balance').get_json()['balance']
        self.assertEqual(balance_after, 100.00)

    def test_invalid_transaction_type(self):
        """测试无效的交易类型"""
        response = self.client.post('/api/transactions',
                                   json={
                                       'type': 'invalid',
                                       'amount': 100.00,
                                       'category': '测试',
                                       'description': '无效类型'
                                   },
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertIn('无效', data['message'])

    def test_negative_amount(self):
        """测试负数金额"""
        response = self.client.post('/api/transactions',
                                   json={
                                       'type': 'income',
                                       'amount': -10.00,
                                       'category': '测试',
                                       'description': '负数金额'
                                   },
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data['success'])

    def test_zero_amount(self):
        """测试零金额"""
        response = self.client.post('/api/transactions',
                                   json={
                                       'type': 'income',
                                       'amount': 0.00,
                                       'category': '测试',
                                       'description': '零金额'
                                   },
                                   content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data['success'])


if __name__ == '__main__':
    # 临时修改app模块的数据库路径
    import app as app_module
    
    # 保存原始路径
    original_db_path = app_module.DATABASE_PATH
    
    # 使用测试数据库路径
    app_module.DATABASE_PATH = TEST_DATABASE_PATH
    
    try:
        unittest.main(verbosity=2)
    finally:
        # 恢复原始路径
        app_module.DATABASE_PATH = original_db_path
