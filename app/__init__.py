from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from config import config_by_name

db = SQLAlchemy()
ma = Marshmallow()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config_by_name['default'])
    

    db.init_app(app)
    ma.init_app(app)
    
    with app.app_context():
      db.create_all()  

    # Importa los blueprints después de inicializar la app
    from app.routes.blacklist_routes import blacklist_bp
    app.register_blueprint(blacklist_bp)

    return app
