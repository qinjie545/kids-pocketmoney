import sqlite3
import random
from datetime import datetime, timedelta
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'cash_manager.db')

def generate_test_data():
    """生成过去30天的测试数据"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # 获取用户ID（假设第一个用户）
    cursor.execute('SELECT id FROM users LIMIT 1')
    user = cursor.fetchone()
    if not user:
        print("没有找到用户，请先创建用户")
        return

    user_id = user[0]

    # 清空现有交易数据
    cursor.execute('DELETE FROM transactions WHERE user_id = ?', (user_id,))
    print("已清空现有交易数据")

    # 收入分类和描述
    income_data = [
        ('零花钱', '每周零花钱', 50),
        ('奖励', '数学考试满分奖励', 20),
        ('奖励', '帮忙做家务奖励', 10),
        ('红包', '奶奶给的红包', 100),
        ('礼物', '生日礼物钱', 50),
        ('压岁钱', '过年压岁钱', 200),
        ('帮忙家务', '洗碗奖励', 5),
        ('帮忙家务', '倒垃圾奖励', 3),
        ('零花钱', '表现良好奖励', 15),
    ]

    # 支出分类和描述
    expense_data = [
        ('零食', '买糖果', 5),
        ('零食', '买薯片', 8),
        ('零食', '买冰淇淋', 6),
        ('文具', '买铅笔', 2),
        ('文具', '买橡皮擦', 1),
        ('文具', '买笔记本', 5),
        ('玩具', '买玩具车', 25),
        ('玩具', '买积木', 30),
        ('游戏', '游戏充值', 10),
        ('游戏', '买游戏卡', 15),
        ('书籍', '买故事书', 12),
        ('书籍', '买漫画书', 8),
        ('娱乐', '看电影', 15),
        ('娱乐', '去游乐园', 50),
        ('交通', '坐公交', 2),
        ('礼物', '给同学买生日礼物', 20),
        ('捐款', '慈善捐款', 5),
        ('其他', '其他支出', 10),
    ]

    # 生成过去30天的数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    current_date = start_date
    balance = 0

    while current_date <= end_date:
        # 每天随机生成0-3笔交易
        num_transactions = random.randint(0, 3)

        for _ in range(num_transactions):
            # 55%概率是支出，45%概率是收入（提高收入比例）
            if random.random() < 0.55:
                # 支出
                category, description, max_amount = random.choice(expense_data)
                amount = round(random.uniform(1, max_amount), 2)
                transaction_type = 'expense'
            else:
                # 收入
                category, description, max_amount = random.choice(income_data)
                amount = round(random.uniform(10, max_amount), 2)
                transaction_type = 'income'

            # 随机时间（白天）
            hour = random.randint(9, 21)
            minute = random.randint(0, 59)
            transaction_time = current_date.replace(hour=hour, minute=minute)

            cursor.execute(
                '''INSERT INTO transactions (user_id, type, amount, category, description, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (user_id, transaction_type, amount, category, description, transaction_time.strftime('%Y-%m-%d %H:%M:%S'))
            )

            # 更新余额
            if transaction_type == 'income':
                balance += amount
            else:
                balance -= amount

        current_date += timedelta(days=1)

    conn.commit()
    conn.close()

    print(f"已生成30天的测试数据，最终余额：¥{balance:.2f}")

if __name__ == '__main__':
    generate_test_data()
