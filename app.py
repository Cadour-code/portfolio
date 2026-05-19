import os
from flask import Flask
from config import Config
from extensions import db, login_manager, bcrypt, csrf, mail
from models import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)

    upload_folder = os.path.join(app.instance_path, 'uploads', 'achievements')
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.skills import skills_bp
    from routes.goals import goals_bp
    from routes.achievements import achievements_bp
    from routes.profile import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(skills_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(achievements_bp)
    app.register_blueprint(profile_bp)

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
