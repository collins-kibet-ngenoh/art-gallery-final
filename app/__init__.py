from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_name='app.config.Config'):
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_name)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)  # Enable CORS

    # Register blueprints
    from .routes import main
    app.register_blueprint(main)

    return app
