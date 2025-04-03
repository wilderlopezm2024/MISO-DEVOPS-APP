from .default import Config
import os
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}"
        f"@{os.getenv('DATABASE_HOST')}:5432/{os.getenv('DATABASE_NAME')}"
    )
    DEBUG = False