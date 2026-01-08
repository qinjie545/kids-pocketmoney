import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'cash_manager.db')

def migrate_database():
    """更新数据库表结构，添加day_of_week和day_of_month列"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    try:
        # 检查schedules表是否已有这些列
        cursor.execute("PRAGMA table_info(schedules)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'day_of_week' not in columns:
            print("添加day_of_week列...")
            cursor.execute("ALTER TABLE schedules ADD COLUMN day_of_week INTEGER")
        else:
            print("day_of_week列已存在")

        if 'day_of_month' not in columns:
            print("添加day_of_month列...")
            cursor.execute("ALTER TABLE schedules ADD COLUMN day_of_month INTEGER")
        else:
            print("day_of_month列已存在")

        conn.commit()
        print("数据库迁移完成")
    except Exception as e:
        print(f"迁移失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    migrate_database()
