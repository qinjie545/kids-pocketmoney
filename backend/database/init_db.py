import os
import sqlite3

from werkzeug.security import generate_password_hash

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "cash_manager.db")


def init_database():
    """初始化数据库，创建表结构"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # 读取并执行schema.sql
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = f.read()
        cursor.executescript(schema)

    conn.commit()
    conn.close()
    print("数据库初始化完成")


def create_default_user():
    """创建默认用户 admin/admin123"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        hashed_password = generate_password_hash("admin123")
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", hashed_password),
        )
        conn.commit()
        print("默认用户创建成功: admin/admin123")
    except sqlite3.IntegrityError:
        print("默认用户已存在")
    finally:
        conn.close()


if __name__ == "__main__":
    init_database()
    create_default_user()
