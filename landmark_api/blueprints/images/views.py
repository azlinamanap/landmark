from flask import Flask, Blueprint, request, jsonify, render_template, redirect, url_for
from models.user import User
from models.user import Images
from flask_jwt_extended import (
    jwt_required, get_jwt_identity)


images_api_blueprint = Blueprint('images_api',
                                 __name__,
                                 template_folder='templates')


@images_api_blueprint.route('/user/<id>', methods=['GET'])
def getuserimages(id):
    images = []
    for image in Images.select().where(Images.user_id == id):
        images.append(image.image)

    return jsonify(images)


@images_api_blueprint.route('/me', methods=['GET'])
@jwt_required
def myimage():
    current_user_id = get_jwt_identity()
    images = []
    for image in Images.select().where(Images.user_id == current_user.id):
        images.append(image.image)

    return jsonify(images)


@images_api_blueprint.route('/<id>', methods=['GET'])
def getimage(id):
    result = []
    image = Images.get_or_none(Images.id == id)
    user = User.get_or_none(User.id == image.user_id)
    if image:
        response = {
            'name': image.name,
            'url': image.image,
            'description': image.description,
            'latitude': image.latitude,
            'longitude': image.longitude,
            'user': user.username
        }
    result.append(response)
    return jsonify(result)


@images_api_blueprint.route('/<id>/newfact', methods=['POST'])
@jwt_required
def newfact(id):
    current_user_id = get_jwt_identity()
    image = Images.get_by_id(id)
    fact = Facts(
        images=image,
        title=request.json.get('title')
        text=request.json.get('text')
        user=current_user_id
    )
    if fact.save():
        return redirect(url_for('home'))
    else:
        return jsonify(fact.errors, {
            "status": "failed"
        }), 400
