class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    ARTICLES_COUNT_MAX = 30
    ARTICLES_LIMIT_DEFAULT = 10

config = Config
