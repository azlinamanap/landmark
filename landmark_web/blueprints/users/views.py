from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from models.user import User, Images
import os

users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')


@users_blueprint.route('/signup', methods=['GET'])
def new():
    return render_template('users/new.html')


@users_blueprint.route('/signup', methods=['POST'])
def signup():

    username = request.form.get('username')
    password = request.form.get('password')

    check_username = User.get_or_none(User.username == username)

    if check_username:
        flash('Username already taken. Pick another bro')
        return render_template('users/new.html')

    new_user = User(username=username, password=password)

    if new_user.save():
        login_user(new_user)
        return redirect(url_for('home'))
    else:
        return render_template('users/new.html')


@users_blueprint.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@users_blueprint.route('/<username>', methods=["GET"])
def show(username):
    pass


@users_blueprint.route('/', methods=["GET"])
def index():
    return "USERS"


@users_blueprint.route('/<id>/edit', methods=['GET'])
def edit(id):
    pass


@users_blueprint.route('/<id>', methods=['POST'])
def update(id):
    pass
