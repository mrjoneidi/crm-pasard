from flask import Flask
from config import Config
from flasgger import Swagger
from flask_login import LoginManager
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    from modules.db import db, ma
    db.init_app(app)
    ma.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'web.login'
    login_manager.init_app(app)

    from modules.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    swagger = Swagger(app)

    # Register Audit Listeners
    from modules.audit import register_audit_listeners
    register_audit_listeners()

    # Setup Logging
    from modules.logger import setup_logger
    setup_logger(app)

    # Register Blueprints
    from api.cases.routes import cases_bp
    app.register_blueprint(cases_bp, url_prefix='/api/cases')

    from api.documents.routes import documents_bp
    app.register_blueprint(documents_bp, url_prefix='/api/documents')

    from api.contracts.routes import contracts_bp
    app.register_blueprint(contracts_bp, url_prefix='/api/contracts')

    from api.invoices.routes import invoices_bp
    app.register_blueprint(invoices_bp, url_prefix='/api/invoices')

    from web.routes import web_bp
    app.register_blueprint(web_bp, url_prefix='/')

    return app

if __name__ == '__main__':
    app = create_app()
    # Database management is handled via manage.py
    app.run(debug=True, port=5000)
