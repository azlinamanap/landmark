from app import app
from flask import render_template, redirect, url_for
from flask_assets import Environment, Bundle
from .util.assets import bundles
from models.user import Images


assets = Environment(app)
assets.register(bundles)


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
