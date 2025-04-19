from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from models import db
from config import DevConfig, ProdConfig
from routes.user_bp import user_bp
from routes.project_bp import project_bp
from routes.time_entry_bp import time_entry_bp
from routes.time_pause_bp import time_pause_bp
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, supports_credentials=True)

env = os.getenv("FLASK_ENV", "").lower()
if env == "dev":
    app.config.from_object(DevConfig)
else:
    app.config.from_object(ProdConfig)

# Extensions initialisieren
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Blueprints registrieren
app.register_blueprint(user_bp, url_prefix="/api")
app.register_blueprint(project_bp, url_prefix="/api")
app.register_blueprint(time_entry_bp, url_prefix="/api")
app.register_blueprint(time_pause_bp, url_prefix="/api")

if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"])
