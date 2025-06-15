from flask import Flask
import locale
from .config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # إعداد اللغة
    try:
        locale.setlocale(locale.LC_NUMERIC, 'ar_SA.UTF-8')
    except:
        locale.setlocale(locale.LC_NUMERIC, '')

    # تسجيل الفلاتر والمخططات
    from .routes import format_currency, format_number, main_blueprint
    app.jinja_env.filters['format_currency'] = format_currency
    app.jinja_env.filters['format_number'] = format_number
    app.register_blueprint(main_blueprint)

    return app
