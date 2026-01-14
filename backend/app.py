import atexit
import csv
import os
import sqlite3
from datetime import datetime, timedelta
from functools import wraps
from io import StringIO

from flask import (
    Flask,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
from flask_babel import Babel, gettext as _, lazy_gettext as _l

# 设置Flask应用路径
project_root = os.path.dirname(os.path.dirname(__file__))
template_dir = os.path.join(project_root, "frontend", "templates")
static_dir = os.path.join(project_root, "frontend", "static")

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.secret_key = os.environ.get("SECRET_KEY", "your-secret-key-change-in-production")
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "database", "cash_manager.db")

# 配置Flask-Babel
app.config["BABEL_DEFAULT_LOCALE"] = "zh_CN"  # 默认中文
app.config["BABEL_SUPPORTED_LOCALES"] = ["zh_CN", "en_US"]  # 支持中文和英文
app.config["BABEL_TRANSLATION_DIRECTORIES"] = os.path.join(project_root, "backend", "translations")

babel = Babel(app)

def get_locale():
    """选择用户语言"""
    # 首先检查URL参数
    locale = request.args.get("lang")
    if locale and locale in app.config["BABEL_SUPPORTED_LOCALES"]:
        session["lang"] = locale
        return locale

    # 然后检查session
    locale = session.get("lang")
    if locale and locale in app.config["BABEL_SUPPORTED_LOCALES"]:
        return locale

    # 最后使用浏览器语言偏好
    return request.accept_languages.best_match(app.config["BABEL_SUPPORTED_LOCALES"], "zh_CN")

# 设置locale选择器
babel.init_app(app, locale_selector=get_locale)


# 允许测试时覆盖数据库路径
def get_database_path():
    return app.config.get("DATABASE_PATH", DATABASE_PATH)


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(get_database_path())
    conn.row_factory = sqlite3.Row
    return conn


def login_required(f):
    """登录验证装饰器"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def index():
    """首页，重定向到登录或主页面"""
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/set_language/<lang>")
def set_language(lang):
    """设置语言"""
    if lang in app.config["BABEL_SUPPORTED_LOCALES"]:
        session["lang"] = lang
    return redirect(request.referrer or url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """登录页面"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="用户名或密码错误")

    return render_template("login.html")


@app.route("/register", methods=["POST"])
def register():
    """注册新用户"""
    if request.is_json:
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
    else:
        username = request.form.get("username")
        password = request.form.get("password")

    if not username or not password:
        return jsonify({"success": False, "message": "用户名和密码不能为空"})

    conn = get_db_connection()
    try:
        hashed_password = generate_password_hash(password)
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password),
        )
        conn.commit()
        return jsonify({"success": True, "message": "注册成功，请登录"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "用户名已存在"})
    finally:
        conn.close()


@app.route("/logout")
def logout():
    """登出"""
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    """主控制面板"""
    return render_template("dashboard.html", username=session.get("username"))


@app.route("/api/transactions", methods=["GET", "POST"])
@login_required
def transactions():
    """获取或添加交易记录"""
    conn = get_db_connection()

    if request.method == "POST":
        data = request.get_json()
        trans_type = data.get("type")  # 'income' or 'expense'
        amount = data.get("amount")
        description = data.get("description", "")
        category = data.get("category", "")

        if trans_type not in ["income", "expense"]:
            conn.close()
            return jsonify({"success": False, "message": "无效的交易类型"})

        if not amount or float(amount) <= 0:
            conn.close()
            return jsonify({"success": False, "message": "金额必须大于0"})

        conn.execute(
            """INSERT INTO transactions (user_id, type, amount, description, category)
               VALUES (?, ?, ?, ?, ?)""",
            (session["user_id"], trans_type, float(amount), description, category),
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "添加成功"})

    else:
        # GET 请求 - 获取交易记录
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        offset = (page - 1) * per_page

        transactions = conn.execute(
            """SELECT * FROM transactions
               WHERE user_id = ?
               ORDER BY created_at DESC
               LIMIT ? OFFSET ?""",
            (session["user_id"], per_page, offset),
        ).fetchall()

        total = conn.execute(
            "SELECT COUNT(*) as count FROM transactions WHERE user_id = ?",
            (session["user_id"],),
        ).fetchone()["count"]

        conn.close()

        return jsonify(
            {
                "success": True,
                "transactions": [dict(tx) for tx in transactions],
                "total": total,
                "page": page,
                "per_page": per_page,
            }
        )


@app.route("/api/transactions/<int:tx_id>", methods=["DELETE"])
@login_required
def delete_transaction(tx_id):
    """删除交易记录"""
    conn = get_db_connection()
    conn.execute(
        "DELETE FROM transactions WHERE id = ? AND user_id = ?",
        (tx_id, session["user_id"]),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "删除成功"})


@app.route("/api/balance")
@login_required
def balance():
    """获取当前余额"""
    conn = get_db_connection()

    income = conn.execute(
        'SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = ? AND type = "income"',
        (session["user_id"],),
    ).fetchone()["total"]

    expense = conn.execute(
        'SELECT COALESCE(SUM(amount), 0) as total FROM transactions WHERE user_id = ? AND type = "expense"',
        (session["user_id"],),
    ).fetchone()["total"]

    balance = income - expense

    conn.close()

    return jsonify(
        {
            "success": True,
            "balance": round(balance, 2),
            "income": round(income, 2),
            "expense": round(expense, 2),
        }
    )


@app.route("/api/trends")
@login_required
def trends():
    """获取趋势数据"""
    days = int(request.args.get("days", 30))
    start_date = datetime.now() - timedelta(days=days)

    conn = get_db_connection()

    trend_data = conn.execute(
        """SELECT
            DATE(created_at) as date,
            SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as income,
            SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as expense
           FROM transactions
           WHERE user_id = ? AND DATE(created_at) >= ?
           GROUP BY DATE(created_at)
           ORDER BY date""",
        (session["user_id"], start_date.strftime("%Y-%m-%d")),
    ).fetchall()

    conn.close()

    dates = []
    income_data = []
    expense_data = []
    balance_data = []
    running_balance = 0

    for row in trend_data:
        dates.append(row["date"])
        income_data.append(round(row["income"], 2))
        expense_data.append(round(row["expense"], 2))
        running_balance += row["income"] - row["expense"]
        balance_data.append(round(running_balance, 2))

    return jsonify(
        {
            "success": True,
            "dates": dates,
            "income": income_data,
            "expense": expense_data,
            "balance": balance_data,
        }
    )


@app.route("/api/stats")
@login_required
def stats():
    """获取统计信息"""
    conn = get_db_connection()

    # 按类别统计支出
    expense_by_category = conn.execute(
        """SELECT category, SUM(amount) as total
           FROM transactions
           WHERE user_id = ? AND type = 'expense'
           GROUP BY category
           ORDER BY total DESC""",
        (session["user_id"],),
    ).fetchall()

    # 最近7天的收支
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    recent_income = conn.execute(
        """SELECT COALESCE(SUM(amount), 0) as total
           FROM transactions
           WHERE user_id = ? AND type = 'income' AND DATE(created_at) >= ?""",
        (session["user_id"], seven_days_ago),
    ).fetchone()["total"]

    recent_expense = conn.execute(
        """SELECT COALESCE(SUM(amount), 0) as total
           FROM transactions
           WHERE user_id = ? AND type = 'expense' AND DATE(created_at) >= ?""",
        (session["user_id"], seven_days_ago),
    ).fetchone()["total"]

    conn.close()

    return jsonify(
        {
            "success": True,
            "expense_by_category": [dict(row) for row in expense_by_category],
            "recent_income": round(recent_income, 2),
            "recent_expense": round(recent_expense, 2),
        }
    )


@app.route("/api/schedules", methods=["GET", "POST"])
@login_required
def schedules():
    """获取或添加定时发放配置"""
    conn = get_db_connection()

    if request.method == "POST":
        data = request.get_json()
        frequency = data.get("frequency")  # 'daily', 'weekly', 'monthly'
        amount = data.get("amount")
        category = data.get("category", "")
        description = data.get("description", "")
        day_of_week = data.get("day_of_week")
        day_of_month = data.get("day_of_month")

        if frequency not in ["daily", "weekly", "monthly"]:
            conn.close()
            return jsonify({"success": False, "message": "无效的发放周期"})

        if not amount or float(amount) <= 0:
            conn.close()
            return jsonify({"success": False, "message": "金额必须大于0"})

        conn.execute(
            """INSERT INTO schedules (user_id, frequency, amount, category, description, day_of_week, day_of_month)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                session["user_id"],
                frequency,
                float(amount),
                category,
                description,
                day_of_week,
                day_of_month,
            ),
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "添加成功"})

    else:
        schedules = conn.execute(
            "SELECT * FROM schedules WHERE user_id = ? ORDER BY created_at DESC",
            (session["user_id"],),
        ).fetchall()

        conn.close()

        return jsonify({"success": True, "schedules": [dict(s) for s in schedules]})


@app.route("/api/schedules/<int:schedule_id>", methods=["DELETE"])
@login_required
def delete_schedule(schedule_id):
    """删除定时发放配置"""
    conn = get_db_connection()
    conn.execute(
        "DELETE FROM schedules WHERE id = ? AND user_id = ?",
        (schedule_id, session["user_id"]),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "删除成功"})


@app.route("/api/change-password", methods=["POST"])
@login_required
def change_password():
    """修改密码"""
    data = request.get_json()
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not old_password or not new_password:
        return jsonify({"success": False, "message": "请输入旧密码和新密码"})

    if len(new_password) < 6:
        return jsonify({"success": False, "message": "新密码长度至少为6位"})

    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?", (session["user_id"],)
    ).fetchone()

    if not check_password_hash(user["password"], old_password):
        conn.close()
        return jsonify({"success": False, "message": "旧密码错误"})

    hashed_password = generate_password_hash(new_password)
    conn.execute(
        "UPDATE users SET password = ? WHERE id = ?",
        (hashed_password, session["user_id"]),
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "密码修改成功"})


@app.route("/api/export/transactions")
@login_required
def export_transactions():
    """导出交易记录为CSV"""
    conn = get_db_connection()
    transactions = conn.execute(
        """SELECT * FROM transactions
           WHERE user_id = ?
           ORDER BY created_at DESC""",
        (session["user_id"],),
    ).fetchall()
    conn.close()

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["日期", "类型", "金额", "分类", "备注"])

    for tx in transactions:
        type_text = "收入" if tx["type"] == "income" else "支出"
        writer.writerow(
            [
                tx["created_at"],
                type_text,
                tx["amount"],
                tx["category"] or "",
                tx["description"] or "",
            ]
        )

    output.seek(0)
    return send_file(
        StringIO(output.getvalue()),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f'transactions_{datetime.now().strftime("%Y%m%d")}.csv',
    )


@app.route("/api/transactions/<int:tx_id>", methods=["PUT"])
@login_required
def update_transaction(tx_id):
    """更新交易记录"""
    data = request.get_json()
    amount = data.get("amount")
    description = data.get("description", "")
    category = data.get("category", "")

    if not amount or float(amount) <= 0:
        return jsonify({"success": False, "message": "金额必须大于0"})

    conn = get_db_connection()
    conn.execute(
        """UPDATE transactions SET amount = ?, description = ?, category = ?
           WHERE id = ? AND user_id = ?""",
        (float(amount), description, category, tx_id, session["user_id"]),
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "更新成功"})


@app.route("/api/summary/monthly")
@login_required
def monthly_summary():
    """获取月度汇总数据"""
    conn = get_db_connection()

    monthly_data = conn.execute(
        """SELECT
            strftime('%Y-%m', created_at) as month,
            SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as income,
            SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as expense
           FROM transactions
           WHERE user_id = ?
           GROUP BY strftime('%Y-%m', created_at)
           ORDER BY month DESC
           LIMIT 12""",
        (session["user_id"],),
    ).fetchall()

    conn.close()

    return jsonify({"success": True, "data": [dict(row) for row in monthly_data]})


@app.route("/api/categories")
@login_required
def get_categories():
    """获取用户的分类统计"""
    conn = get_db_connection()

    categories = conn.execute(
        """SELECT category,
            SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as income,
            SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as expense,
            COUNT(*) as count
           FROM transactions
           WHERE user_id = ? AND category IS NOT NULL AND category != ''
           GROUP BY category
           ORDER BY count DESC""",
        (session["user_id"],),
    ).fetchall()

    conn.close()

    return jsonify({"success": True, "categories": [dict(row) for row in categories]})


@app.route("/api/search/transactions")
@login_required
def search_transactions():
    """搜索交易记录"""
    keyword = request.args.get("keyword", "")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    offset = (page - 1) * per_page

    conn = get_db_connection()

    query = """SELECT * FROM transactions
               WHERE user_id = ?
               AND (description LIKE ? OR category LIKE ?)
               ORDER BY created_at DESC
               LIMIT ? OFFSET ?"""

    search_pattern = f"%{keyword}%"
    transactions = conn.execute(
        query, (session["user_id"], search_pattern, search_pattern, per_page, offset)
    ).fetchall()

    total = conn.execute(
        """SELECT COUNT(*) as count FROM transactions
           WHERE user_id = ?
           AND (description LIKE ? OR category LIKE ?)""",
        (session["user_id"], search_pattern, search_pattern),
    ).fetchone()["count"]

    conn.close()

    return jsonify(
        {
            "success": True,
            "transactions": [dict(tx) for tx in transactions],
            "total": total,
            "page": page,
            "per_page": per_page,
        }
    )


@app.route("/api/stats/overview")
@login_required
def stats_overview():
    """获取统计概览"""
    conn = get_db_connection()

    # 今日收支
    today_income = conn.execute(
        """SELECT COALESCE(SUM(amount), 0) as total
           FROM transactions
           WHERE user_id = ? AND type = 'income' AND DATE(created_at) = DATE('now')""",
        (session["user_id"],),
    ).fetchone()["total"]

    today_expense = conn.execute(
        """SELECT COALESCE(SUM(amount), 0) as total
           FROM transactions
           WHERE user_id = ? AND type = 'expense' AND DATE(created_at) = DATE('now')""",
        (session["user_id"],),
    ).fetchone()["total"]

    # 本月收支
    this_month_income = conn.execute(
        """SELECT COALESCE(SUM(amount), 0) as total
           FROM transactions
           WHERE user_id = ? AND type = 'income'
           AND strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')""",
        (session["user_id"],),
    ).fetchone()["total"]

    this_month_expense = conn.execute(
        """SELECT COALESCE(SUM(amount), 0) as total
           FROM transactions
           WHERE user_id = ? AND type = 'expense'
           AND strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')""",
        (session["user_id"],),
    ).fetchone()["total"]

    # 总交易次数
    total_transactions = conn.execute(
        "SELECT COUNT(*) as count FROM transactions WHERE user_id = ?",
        (session["user_id"],),
    ).fetchone()["count"]

    # 平均每日交易
    avg_daily = (
        conn.execute(
            """SELECT AVG(daily_count) as avg_count
           FROM (SELECT COUNT(*) as daily_count FROM transactions
                 WHERE user_id = ?
                 GROUP BY DATE(created_at))""",
            (session["user_id"],),
        ).fetchone()["avg_count"]
        or 0
    )

    conn.close()

    return jsonify(
        {
            "success": True,
            "today": {
                "income": round(today_income, 2),
                "expense": round(today_expense, 2),
            },
            "this_month": {
                "income": round(this_month_income, 2),
                "expense": round(this_month_expense, 2),
            },
            "total_transactions": total_transactions,
            "avg_daily_transactions": round(avg_daily, 1),
        }
    )


if __name__ == "__main__":
    # 启动定时任务调度器
    from scheduler import start_scheduler, stop_scheduler

    try:
        start_scheduler()
        # 注册退出时停止调度器
        atexit.register(stop_scheduler)

        # 从环境变量获取配置
        debug_mode = os.environ.get("FLASK_ENV", "production") != "production"
        port = int(os.environ.get("PORT", 19754))
        host = os.environ.get("HOST", "0.0.0.0")

        app.run(debug=debug_mode, host=host, port=port)
    except Exception as e:
        print(f"启动失败: {e}")
        stop_scheduler()
