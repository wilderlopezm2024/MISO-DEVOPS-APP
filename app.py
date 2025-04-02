from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api, Resource
from datetime import datetime
import os

app = Flask(__name__)

# Configuración de la base de datos. Utiliza la variable de ambiente DATABASE_URL.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost:5432/blacklist_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)

# Token estático para autorización
STATIC_BEARER_TOKEN = "my_static_token"

def token_required(func):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or auth_header != f"Bearer {STATIC_BEARER_TOKEN}":
            return {'message': 'Token is missing or invalid'}, 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# Modelo de la lista negra
class Blacklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    app_uuid = db.Column(db.String(36), nullable=False)
    blocked_reason = db.Column(db.String(255), nullable=True)
    request_ip = db.Column(db.String(45), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Esquema de serialización con Marshmallow
class BlacklistSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Blacklist

blacklist_schema = BlacklistSchema()
blacklists_schema = BlacklistSchema(many=True)

# Endpoint para agregar un email a la lista negra (POST /blacklists)
class BlacklistResource(Resource):
    @token_required
    def post(self):
        data = request.get_json()
        if not data:
            return {'message': 'No input data provided'}, 400

        email = data.get('email')
        app_uuid = data.get('app_uuid')
        blocked_reason = data.get('blocked_reason', None)

        if not email or not app_uuid:
            return {'message': 'email and app_uuid are required'}, 400

        # Obtiene la IP del solicitante
        request_ip = request.remote_addr

        # Verifica si el email ya existe en la lista negra
        if Blacklist.query.filter_by(email=email).first():
            return {'message': 'Email already in blacklist'}, 400

        new_entry = Blacklist(email=email, app_uuid=app_uuid, blocked_reason=blocked_reason, request_ip=request_ip)
        db.session.add(new_entry)
        db.session.commit()

        return {'message': 'Email added to blacklist successfully'}, 201

# Endpoint para consultar si un email está en la lista negra (GET /blacklists/<email>)
class BlacklistQueryResource(Resource):
    @token_required
    def get(self, email):
        entry = Blacklist.query.filter_by(email=email).first()
        if entry:
            return {'blocked': True, 'blocked_reason': entry.blocked_reason}, 200
        else:
            return {'blocked': False, 'blocked_reason': ''}, 200

api.add_resource(BlacklistResource, '/blacklists')
api.add_resource(BlacklistQueryResource, '/blacklists/<string:email>')

@app.before_first_request
def init_db():
    db.create_all()

if __name__ == '__main__':
    # Crea las tablas si aún no existen
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')
