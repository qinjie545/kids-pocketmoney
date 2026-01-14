"""
额外的测试用例，提高测试覆盖率
"""

import os
import sqlite3
import unittest
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash

# 使用测试数据库
TEST_DATABASE_PATH = os.path.join(
    os.path.dirname(__file__), "database", "test_cash_manager_additional.db"
)

# 在导入app之前设置环境变量
os.environ["TEST_DATABASE_PATH"] = TEST_DATABASE_PATH

from backend.app import app


class AdditionalTestCase(unittest.TestCase):
    """额外的功能测试用例"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        app.config["TESTING"] = True
        app.config["DATABASE_PATH"] = TEST_DATABASE_PATH
        app.config["SECRET_KEY"] = "test-secret-key"

        # 删除可能存在的旧测试数据库
        if os.path.exists(TEST_DATABASE_PATH):
            os.remove(TEST_DATABASE_PATH)

        # 创建测试数据库
        conn = sqlite3.connect(TEST_DATABASE_PATH)
        cursor = conn.cursor()

        # 创建表结构
        cursor.execute(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        cursor.execute(
            """
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
        """
        )

        # 创建测试用户
        hashed_password = generate_password_hash("test123")
        cursor.execute(
            "INSERT INTO users (id, username, password) VALUES (?, ?, ?)",
            (1, "testuser", hashed_password),
        )

        # 创建另一个测试用户
        hashed_password2 = generate_password_hash("test456")
        cursor.execute(
            "INSERT INTO users (id, username, password) VALUES (?, ?, ?)",
            (2, "testuser2", hashed_password2),
        )

        conn.commit()
        conn.close()

    def setUp(self):
        """每个测试方法执行前的准备工作"""
        self.client = app.test_client()

        # 登录获取session
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "testuser"

        # 彻底清空交易记录
        conn = sqlite3.connect(TEST_DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions")
        conn.commit()
        conn.close()

    def tearDown(self):
        """每个测试方法执行后的清理工作"""
        # 清空交易记录
        conn = sqlite3.connect(TEST_DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE user_id = ?", (1,))
        conn.commit()
        conn.close()

    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        if os.path.exists(TEST_DATABASE_PATH):
            os.remove(TEST_DATABASE_PATH)

    def test_login_page_get(self):
        """测试登录页面GET请求"""
        with self.client.session_transaction() as sess:
            sess.clear()  # 清除session，确保未登录状态

        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"login", response.data.lower())

    def test_dashboard_requires_login(self):
        """测试主页面需要登录"""
        with self.client.session_transaction() as sess:
            sess.clear()  # 清除session

        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 302)  # 重定向到登录页

    def test_index_redirects_to_login_when_not_logged_in(self):
        """测试首页在未登录时重定向到登录页"""
        with self.client.session_transaction() as sess:
            sess.clear()

        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_index_redirects_to_dashboard_when_logged_in(self):
        """测试首页在已登录时重定向到主页面"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/dashboard", response.location)

    def test_logout_clears_session(self):
        """测试登出清除session"""
        response = self.client.get("/logout")
        self.assertEqual(response.status_code, 302)

        # 验证session已清除
        with self.client.session_transaction() as sess:
            self.assertNotIn("user_id", sess)
            self.assertNotIn("username", sess)

    def test_register_success(self):
        """测试成功注册"""
        response = self.client.post(
            "/register",
            json={"username": "newuser", "password": "newpass123"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("注册成功", data["message"])

    def test_register_duplicate_username(self):
        """测试注册重复用户名"""
        # 先注册一个用户
        self.client.post(
            "/register",
            json={"username": "duplicate", "password": "pass123"},
            content_type="application/json",
        )

        # 再次注册相同用户名
        response = self.client.post(
            "/register",
            json={"username": "duplicate", "password": "pass456"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data["success"])
        self.assertIn("已存在", data["message"])

    def test_register_empty_fields(self):
        """测试注册空字段"""
        response = self.client.post(
            "/register",
            json={"username": "", "password": ""},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data["success"])
        self.assertIn("不能为空", data["message"])

    def test_login_success(self):
        """测试成功登录"""
        response = self.client.post(
            "/login", data={"username": "testuser", "password": "test123"}
        )

        self.assertEqual(response.status_code, 302)  # 重定向到dashboard

    def test_login_wrong_password(self):
        """测试密码错误登录"""
        with self.client.session_transaction() as sess:
            sess.clear()

        response = self.client.post(
            "/login", data={"username": "testuser", "password": "wrongpass"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"error", response.data.lower())

    def test_login_nonexistent_user(self):
        """测试不存在用户登录"""
        with self.client.session_transaction() as sess:
            sess.clear()

        response = self.client.post(
            "/login", data={"username": "nonexistent", "password": "pass123"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"error", response.data.lower())

    def test_transactions_pagination(self):
        """测试交易记录分页"""
        # 添加多条记录
        for i in range(25):
            self.client.post(
                "/api/transactions",
                json={
                    "type": "income",
                    "amount": 10.0,
                    "category": "零花钱",
                    "description": f"测试收入{i}",
                },
                content_type="application/json",
            )

        # 测试第一页
        response = self.client.get("/api/transactions?page=1&per_page=10")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["transactions"]), 10)
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["per_page"], 10)
        self.assertEqual(data["total"], 25)

        # 测试第二页
        response = self.client.get("/api/transactions?page=2&per_page=10")
        data = response.get_json()
        self.assertEqual(len(data["transactions"]), 10)

        # 测试第三页
        response = self.client.get("/api/transactions?page=3&per_page=10")
        data = response.get_json()
        self.assertEqual(len(data["transactions"]), 5)  # 最后5条

    def test_delete_nonexistent_transaction(self):
        """测试删除不存在的交易记录"""
        response = self.client.delete("/api/transactions/99999")
        # 即使记录不存在，DELETE操作也会成功（SQLite特性）
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])

    def test_balance_calculation_edge_cases(self):
        """测试余额计算的边界情况"""
        # 空账户
        response = self.client.get("/api/balance")
        data = response.get_json()
        self.assertEqual(data["balance"], 0.0)
        self.assertEqual(data["income"], 0.0)
        self.assertEqual(data["expense"], 0.0)

        # 只添加收入
        self.client.post(
            "/api/transactions",
            json={
                "type": "income",
                "amount": 100.50,
                "category": "零花钱",
                "description": "收入",
            },
            content_type="application/json",
        )

        response = self.client.get("/api/balance")
        data = response.get_json()
        self.assertEqual(data["balance"], 100.50)
        self.assertEqual(data["income"], 100.50)
        self.assertEqual(data["expense"], 0.0)

        # 只添加支出（会导致负余额）
        self.client.post(
            "/api/transactions",
            json={
                "type": "expense",
                "amount": 50.25,
                "category": "零食",
                "description": "支出",
            },
            content_type="application/json",
        )

        response = self.client.get("/api/balance")
        data = response.get_json()
        self.assertEqual(data["balance"], 50.25)  # 100.50 - 50.25
        self.assertEqual(data["income"], 100.50)
        self.assertEqual(data["expense"], 50.25)

    def test_trends_data_structure(self):
        """测试趋势数据的结构"""
        # 添加一些历史数据
        conn = sqlite3.connect(TEST_DATABASE_PATH)
        cursor = conn.cursor()

        # 添加过去几天的交易记录
        base_date = datetime.now()
        for i in range(5):
            transaction_date = base_date - timedelta(days=i)
            cursor.execute(
                """INSERT INTO transactions (user_id, type, amount, description, category, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    1,
                    "income",
                    10.0,
                    f"测试收入{i}",
                    "零花钱",
                    transaction_date.isoformat(),
                ),
            )

        conn.commit()
        conn.close()

        response = self.client.get("/api/trends?days=7")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertIn("dates", data)
        self.assertIn("income", data)
        self.assertIn("expense", data)
        self.assertIn("balance", data)

        # 验证数据结构
        self.assertIsInstance(data["dates"], list)
        self.assertIsInstance(data["income"], list)
        self.assertIsInstance(data["expense"], list)
        self.assertIsInstance(data["balance"], list)

        # 应该有5天的数据（我们添加了5天的数据）
        self.assertEqual(len(data["dates"]), 5)
        self.assertEqual(len(data["income"]), 5)
        self.assertEqual(len(data["expense"]), 5)
        self.assertEqual(len(data["balance"]), 5)

    def test_transaction_input_validation(self):
        """测试交易输入验证"""
        # 测试无效的交易类型
        response = self.client.post(
            "/api/transactions",
            json={
                "type": "invalid_type",
                "amount": 100.0,
                "category": "测试",
                "description": "无效类型",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data["success"])
        self.assertIn("无效", data["message"])

        # 测试零金额
        response = self.client.post(
            "/api/transactions",
            json={
                "type": "income",
                "amount": 0,
                "category": "测试",
                "description": "零金额",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data["success"])

        # 测试负金额
        response = self.client.post(
            "/api/transactions",
            json={
                "type": "income",
                "amount": -10.0,
                "category": "测试",
                "description": "负金额",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data["success"])

        # 测试小数金额
        response = self.client.post(
            "/api/transactions",
            json={
                "type": "income",
                "amount": 10.99,
                "category": "零花钱",
                "description": "小数金额",
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])

    def test_user_isolation(self):
        """测试用户数据隔离"""
        # 用户1添加交易
        self.client.post(
            "/api/transactions",
            json={
                "type": "income",
                "amount": 100.0,
                "category": "零花钱",
                "description": "用户1的收入",
            },
            content_type="application/json",
        )

        # 切换到用户2
        with self.client.session_transaction() as sess:
            sess["user_id"] = 2
            sess["username"] = "testuser2"

        # 用户2应该看不到用户1的交易
        response = self.client.get("/api/balance")
        data = response.get_json()
        self.assertEqual(data["balance"], 0.0)

        # 用户2添加交易
        self.client.post(
            "/api/transactions",
            json={
                "type": "income",
                "amount": 50.0,
                "category": "零花钱",
                "description": "用户2的收入",
            },
            content_type="application/json",
        )

        # 用户2应该只能看到自己的交易
        response = self.client.get("/api/balance")
        data = response.get_json()
        self.assertEqual(data["balance"], 50.0)

        # 切换回用户1
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "testuser"

        # 用户1应该只能看到自己的交易
        response = self.client.get("/api/balance")
        data = response.get_json()
        self.assertEqual(data["balance"], 100.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
