from flask import Flask, Blueprint, request, jsonify, render_template, redirect, url_for
from models.user import User
from models.user import Images
from models.user import Facts
from flask_jwt_extended import (
    jwt_required, get_jwt_identity)
from app import csrf

images_api_blueprint = Blueprint('images_api',
                                 __name__,
                                 template_folder='templates')

# GET IMAGES FOR SPECIFIED USER


@images_api_blueprint.route('/user/<id>', methods=['GET'])
def getuserimages(id):
    images = []
    for image in Images.select().where(Images.user_id == id):
        images.append(image.image)

    return jsonify(images)

# GET ALL IMAGES FOR CURRENT USER


@images_api_blueprint.route('/me', methods=['GET'])
@jwt_required
def myimages():
    current_user_id = get_jwt_identity()
    images = []
    for image in Images.select().where(Images.user_id == current_user_id):
        images.append(image.image)

    return jsonify(images)

# GET SPECIFIC IMAGE


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

# POST NEW FACT FOR AN IMAGE


@images_api_blueprint.route('/<id>/newfact', methods=['POST'])
@csrf.exempt
def newfact(id):
    current_user_id = get_jwt_identity()
    image = Images.get_by_id(id)
    fact = Facts(
        images_id=image,
        title=request.json.get('title'),  # no title needed
        text=request.json.get('text'),
        user_id=current_user_id
    )
    if fact.save():
        return redirect(url_for('home'))
    else:
        return jsonify(fact.errors, {
            "status": "failed"
        }), 400

# GET ALL FACTS ASSOCIATED WITH IMAGE


@images_api_blueprint.route('/<id>/facts', methods=['GET'])
def facts(id):
    image = Images.get_or_none(Images.id == id)

    facts = []
    for fact in Facts.select().where(Facts.image_id == image.id):
        facts.append(facts.id)

    return jsonify(facts)

# GET ALL IMAGES FOR A LOCATION


@images_api_blueprint.route('/search', methods=['GET'])
def location():
    placename = request.json.get('placename')
    images = Images.select().where(Images.name == placename)
    results = []
    if images:
        for image in images:
            results.append(image.id)
        return jsonify(results)

    else:
        flash('no images for this location yet.')
        return redirect(url_for('home'))
