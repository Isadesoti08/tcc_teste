from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, login_required, current_user

from config import Config
from models import db, User
from routes.auth_routes import auth_bp
from routes.product_routes import products_bp
from routes.search_routes import search_bp
from routes.movement_routes import movements_bp
from routes.report_routes import reports_bp


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Faça login para acessar esta página."
    login_manager.login_message_category = "warning"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(movements_bp)
    app.register_blueprint(reports_bp)

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return redirect(url_for("auth.login"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        return render_template("dashboard.html")

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)