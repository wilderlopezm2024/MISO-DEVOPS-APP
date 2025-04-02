from config.default import Config
from config.production import ProductionConfig

config_by_name = {
    'default': Config,
    'production': ProductionConfig
}
