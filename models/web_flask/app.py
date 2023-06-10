from flask import Flask

def create_app():
    app = Flask(__name__, static_url_path='/static')
    app.config['SECRET_KEY'] = 'k5t_th34_br59'
    return app

