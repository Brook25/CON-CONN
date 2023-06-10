from flask import Flask
from flask_login import  LoginManager
from models import engine
from models.data.users import User 



#db = client.my_db

def create_app():
    app = Flask(__name__)
    app.config['MONGODB_SETTINGS'] = {
    'db': 'my_db',
    'host': 'mongodb://127.0.0.1:27017'
    }

    app.secret_key = 'secret-key'
    from .views import views
    from .auth import auth
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.objects(pk=user_id).first()
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    return app
