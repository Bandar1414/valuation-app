from flask import Flask
import locale

def create_app():
    app = Flask(__name__)
    app.secret_key = 'my_super_secret_key_123'

    # إعداد التنسيق المحلي للأرقام (العربية السعودية)
    try:
        locale.setlocale(locale.LC_NUMERIC, 'ar_SA.UTF-8')
    except:
        locale.setlocale(locale.LC_NUMERIC, '')

    # تسجيل الفلاتر الخاصة بالتنسيق
    from .routes import format_currency, format_number
    app.jinja_env.filters['format_currency'] = format_currency
    app.jinja_env.filters['format_number'] = format_number

    # تسجيل بلوبرنت المسارات الرئيسية
    from .routes import main_blueprint
    app.register_blueprint(main_blueprint)

    return app
