from flask import Blueprint, request, current_app
from flask_restful import Api, Resource
from app import db
from app.models.blacklist import Blacklist
from app.schemas.blacklist_schema import blacklist_schema

blacklist_bp = Blueprint('blacklist_bp', __name__)
api = Api(blacklist_bp)

STATIC_TOKEN = "my_static_token"

def check_token():
    auth = request.headers.get('Authorization', '')
    return auth == f"Bearer {current_app.config['STATIC_TOKEN']}"

class BlacklistListResource(Resource):
    def post(self):
        if not check_token():
            return {"message": "Unauthorized"}, 401

        data = request.get_json()
        email = data.get('email')
        app_uuid = data.get('app_uuid')
        reason = data.get('blocked_reason')

        if not email or not app_uuid:
            return {"message": "Missing required fields"}, 400

        if Blacklist.query.filter_by(email=email).first():
            return {"message": "Email already blacklisted"}, 400

        entry = Blacklist(email=email, app_uuid=app_uuid, blocked_reason=reason, blocked=True)
        db.session.add(entry)
        db.session.commit()

        return {"message": "Email successfully blacklisted", "data": blacklist_schema.dump(entry)}, 201

class BlacklistResource(Resource):
    def get(self, email):
        if not check_token():
            return {"message": "Unauthorized"}, 401

        entry = Blacklist.query.filter_by(email=email).first()
        if entry:
            return blacklist_schema.dump(entry), 200
        return {"email": email, "blocked": False, "blocked_reason": None}, 200

class PingResource(Resource):
    def get(self):
        return {"message": "pong"}, 200

class ResetResource(Resource):
    def post(self):
        if not check_token():
            return {"message": "Unauthorized"}, 401
        
        db.drop_all()
        db.create_all()
        return {"message": "Database reset successfully"}, 200


api.add_resource(BlacklistListResource, '/blacklists')
api.add_resource(BlacklistResource, '/blacklists/<string:email>')
api.add_resource(PingResource, '/ping')
api.add_resource(ResetResource, '/reset')

