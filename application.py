from app import create_app, db

application = create_app()
app = application  # Add alias for compatibility

@application.before_first_request
def init_app_db():
    db.create_all()

if __name__ == '__main__':
    #with application.app_context():
    #    db.create_all()
    application.run(host='0.0.0.0', port=80)