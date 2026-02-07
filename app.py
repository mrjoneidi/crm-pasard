from flask import Flask
from config import Config
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

    # Register Audit Listeners
    from modules.audit import register_audit_listeners
    register_audit_listeners()

    # Register Blueprints
    from api.cases.routes import cases_bp
    app.register_blueprint(cases_bp, url_prefix='/api/cases')

    from api.documents.routes import documents_bp
    app.register_blueprint(documents_bp, url_prefix='/api/documents')

    from api.contracts.routes import contracts_bp
    app.register_blueprint(contracts_bp, url_prefix='/api/contracts')

    from api.invoices.routes import invoices_bp
    app.register_blueprint(invoices_bp, url_prefix='/api/invoices')

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        from modules.db import db
        db.create_all()
        print("Database initialized.")
    app.run(debug=True, port=5000)
