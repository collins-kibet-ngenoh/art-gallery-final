from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import logging
import importlib


# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_name='config.Config'):
   app = Flask(__name__)


   # Handle configuration based on a simple name or full dotted path
   if config_name == 'testing':
       config_name = 'config.TestingConfig'


   try:
       config_module, config_class = config_name.rsplit('.', 1)
       config = getattr(importlib.import_module(config_module), config_class)
       app.config.from_object(config)
   except (ImportError, AttributeError, ValueError) as e:
       raise ImportError(f"Could not load configuration '{config_name}': {e}")


   # Initialize extensions
   db.init_app(app)
   migrate.init_app(app, db)
   jwt.init_app(app)


   # Setup logging
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)


   @app.before_request
   def log_request_info():
       logger.info('Request: %s %s', request.method, request.url)


   @app.after_request
   def log_response_info(response):
       logger.info('Response: %s %s', response.status, response.get_data(as_text=True))
       return response


   # Setup CORS
   CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})


   # Register blueprints with URL prefixes
   from app.routes.auth import bp as auth_bp
   from app.routes.artist_profile import bp as artist_profile_bp
   from app.routes.comments import bp as comments_bp
   from app.routes.follow import bp as follow_bp
   from app.routes.art import bp as art_bp
   from app.routes.home import bp as home_bp


   app.register_blueprint(home_bp, url_prefix='/api/home')
   app.register_blueprint(auth_bp, url_prefix='/api/auth')
   app.register_blueprint(artist_profile_bp, url_prefix='/api/artist')  # Updated prefix here
   app.register_blueprint(comments_bp, url_prefix='/api/comments')
   app.register_blueprint(follow_bp, url_prefix='/api/follow')
   app.register_blueprint(art_bp, url_prefix='/api/art')


   # Define error handlers
   @app.errorhandler(404)
   def page_not_found(e):
       return "Welcome to Art Gallery", 404


   return app



