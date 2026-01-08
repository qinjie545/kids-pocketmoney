import sqlite3
import os
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import logging

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'cash_manager.db')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def process_daily_schedules():
    """处理每日发放任务"""
    logger.info("开始处理每日发放任务")
    conn = get_db_connection()

    schedules = conn.execute(
        '''SELECT * FROM schedules WHERE frequency = 'daily' '''
    ).fetchall()

    for schedule in schedules:
        # 检查今天是否已经发放过
        last_transaction = conn.execute(
            '''SELECT * FROM transactions
               WHERE user_id = ?
               AND category = ?
               AND DATE(created_at) = DATE('now')
               ORDER BY created_at DESC LIMIT 1''',
            (schedule['user_id'], schedule['category'])
        ).fetchone()

        if last_transaction is None:
            # 发放零钱
            conn.execute(
                '''INSERT INTO transactions (user_id, type, amount, category, description)
                   VALUES (?, 'income', ?, ?, ?)''',
                (schedule['user_id'], schedule['amount'],
                 schedule['category'], f"[自动发放] {schedule['description'] or schedule['category']}")
            )
            logger.info(f"用户 {schedule['user_id']} 每日发放 {schedule['amount']} 元")

    conn.commit()
    conn.close()
    logger.info("每日发放任务完成")

def process_weekly_schedules():
    """处理每周发放任务"""
    logger.info("开始处理每周发放任务")
    conn = get_db_connection()

    schedules = conn.execute(
        '''SELECT * FROM schedules WHERE frequency = 'weekly' '''
    ).fetchall()

    for schedule in schedules:
        # 检查本周是否已经发放过（周一作为本周开始）
        last_transaction = conn.execute(
            '''SELECT * FROM transactions
               WHERE user_id = ?
               AND category = ?
               AND created_at >= datetime('now', 'weekday 0', '-7 days')
               ORDER BY created_at DESC LIMIT 1''',
            (schedule['user_id'], schedule['category'])
        ).fetchone()

        if last_transaction is None:
            conn.execute(
                '''INSERT INTO transactions (user_id, type, amount, category, description)
                   VALUES (?, 'income', ?, ?, ?)''',
                (schedule['user_id'], schedule['amount'],
                 schedule['category'], f"[自动发放] {schedule['description'] or schedule['category']}")
            )
            logger.info(f"用户 {schedule['user_id']} 每周发放 {schedule['amount']} 元")

    conn.commit()
    conn.close()
    logger.info("每周发放任务完成")

def process_monthly_schedules():
    """处理每月发放任务（每月1号）"""
    logger.info("开始处理每月发放任务")
    conn = get_db_connection()

    schedules = conn.execute(
        '''SELECT * FROM schedules WHERE frequency = 'monthly' '''
    ).fetchall()

    for schedule in schedules:
        # 检查本月是否已经发放过
        last_transaction = conn.execute(
            '''SELECT * FROM transactions
               WHERE user_id = ?
               AND category = ?
               AND strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
               ORDER BY created_at DESC LIMIT 1''',
            (schedule['user_id'], schedule['category'])
        ).fetchone()

        if last_transaction is None:
            conn.execute(
                '''INSERT INTO transactions (user_id, type, amount, category, description)
                   VALUES (?, 'income', ?, ?, ?)''',
                (schedule['user_id'], schedule['amount'],
                 schedule['category'], f"[自动发放] {schedule['description'] or schedule['category']}")
            )
            logger.info(f"用户 {schedule['user_id']} 每月发放 {schedule['amount']} 元")

    conn.commit()
    conn.close()
    logger.info("每月发放任务完成")

def start_scheduler():
    """启动定时任务调度器"""
    # 每天早上9点执行每日发放任务
    scheduler.add_job(
        process_daily_schedules,
        CronTrigger(hour=9, minute=0),
        id='daily_schedule',
        name='每日发放任务',
        replace_existing=True
    )

    # 每周一早上9点执行每周发放任务
    scheduler.add_job(
        process_weekly_schedules,
        CronTrigger(day_of_week='mon', hour=9, minute=0),
        id='weekly_schedule',
        name='每周发放任务',
        replace_existing=True
    )

    # 每月1号早上9点执行每月发放任务
    scheduler.add_job(
        process_monthly_schedules,
        CronTrigger(day=1, hour=9, minute=0),
        id='monthly_schedule',
        name='每月发放任务',
        replace_existing=True
    )

    scheduler.start()
    logger.info("定时任务调度器已启动")

    # 启动时立即执行一次，处理可能遗漏的任务
    process_daily_schedules()
    process_weekly_schedules()
    process_monthly_schedules()

def stop_scheduler():
    """停止定时任务调度器"""
    scheduler.shutdown()
    logger.info("定时任务调度器已停止")

if __name__ == '__main__':
    start_scheduler()

    try:
        import time
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        stop_scheduler()
