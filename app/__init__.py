from flask import Flask
import locale
from app.visitor_tracker import init_db

def create_app():
    app = Flask(__name__)
    app.secret_key = 'my_super_secret_key_123'

    # إعداد التنسيق المحلي
    try:
        locale.setlocale(locale.LC_NUMERIC, 'ar_SA.UTF-8')
    except:
        locale.setlocale(locale.LC_NUMERIC, '')

    # تهيئة قاعدة بيانات الزوار
    init_db()

    # تسجيل الفلاتر والبلوبرنت
    from .routes import format_currency, format_number
    app.jinja_env.filters['format_currency'] = format_currency
    app.jinja_env.filters['format_number'] = format_number

    from .routes import main_blueprint
    app.register_blueprint(main_blueprint)

    return app  # ← تأكد أن هذا السطر مزاح إلى اليمين بنفس مستوى `app.register_blueprint`
