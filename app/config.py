import os

class Config:
    DEBUG = os.getenv("FLASK_DEBUG", "False") == "True"
    SECRET_KEY = os.getenv("SECRET_KEY", "my_super_secret_key_123")
    # يمكنك لاحقًا إضافة إعدادات أخرى مثل قاعدة بيانات أو API Keys
