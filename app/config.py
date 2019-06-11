import os
import tempfile


class Config(object):
    # cat /dev/urandom | tr -cd 'a-f0-9' | head -c 32 获取随机字符
    SECRET_KEY = '6c61a71132325a99fecc0716b1b6d650'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DIALECT = "mysql"
    DRIVER = 'pymysql'
    USERNAME = os.environ.get('SQL_USERNAME')
    PASSWORD = os.environ.get('SQL_PASSWORD')
    HOST = '127.0.0.1'
    PORT = '3306'
    DATABASE = os.environ.get('SQL_DATABASE')
    MY_SQL = 'mysql+pymysql://{}:{}@127.0.0.1:3306/{}?charset=utf8'.format(USERNAME, PASSWORD, DATABASE)
    SQLALCHEMY_DATABASE_URI = MY_SQL
    CACHE_TYPE = 'null'
    COUNT_DEST = 'app/static/local_file/count'
    EXPORT_DEST = 'app/static/local_file/export'
    UPLOADED_FILERESULT_DEST = 'app/static/up_file/result'
    UPLOADED_FILEFASTQ_DEST = 'app/static/up_file'
    UPLOADED_FILEBAM_DEST = 'app/static/up_file'

    # celery 配置
    CELERY_BROKER_URL = 'amqp://guest@localhost//'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

    # 邮件服务  腾讯企业邮箱
    MAIL_SERVER = 'smtp.exmail.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')


class ProdConfig(Config):
    pass


class DevConfig(Config):
    DEBUG = True


class TestConfig(Config):
    pass