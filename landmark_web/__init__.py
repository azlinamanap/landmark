from app import app
from flask import render_template, redirect, url_for
from landmark_web.blueprints.users.views import users_blueprint
from landmark_web.blueprints.images.views import images_blueprint
from flask_assets import Environment, Bundle
from .util.assets import bundles
from models.user import Images


assets = Environment(app)
assets.register(bundles)

app.register_blueprint(users_blueprint, url_prefix="/users")
app.register_blueprint(images_blueprint, url_prefix="/images")


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route("/")
def home():
    return render_template('home.html')


@app.route("/upload", methods=['GET'])
def form():
    return render_template('images/new.html')


@app.route("/<name>", methods=['GET'])
def info(name):
    image = Images.get_or_none(Images.name == name)

    if image:
        return render_template('images/info.html', image=image)
    else:
        return 'Fail'
