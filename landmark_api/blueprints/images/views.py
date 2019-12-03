from flask import Flask, Blueprint, request, jsonify, render_template, redirect, url_for, flash
from models.user import User
from models.user import Images
from models.user import Facts
import os
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
        images.append({
            "src": f'https://{os.environ.get("S3_BUCKET")}.s3-eu-west-2.amazonaws.com/'+image.image,
            "width": image.width,
            "height": image.height,
            "id": image.id,
            "title": image.name
        })

    return jsonify(images)

# GET ALL IMAGES FOR CURRENT USER


@images_api_blueprint.route('/me', methods=['GET'])
@jwt_required
def myimages():
    current_user_id = get_jwt_identity()
    images = []
    for image in Images.select().where(Images.user_id == current_user_id):
        images.append({
            "src": f'https://{os.environ.get("S3_BUCKET")}.s3-eu-west-2.amazonaws.com/'+image.image,
            "width": image.width,
            "height": image.height,
            "id": image.id,
            "title": image.name
        })

    return jsonify(images)

# GET SPECIFIC IMAGE


@images_api_blueprint.route('/<id>', methods=['GET'])
def getimage(id):
    # result = []
    image = Images.get_or_none(Images.id == id)
    user = User.get_or_none(User.id == image.user_id)
    if image:
        response = {
            'name': image.name,
            'url': f'https://{os.environ.get("S3_BUCKET")}.s3-eu-west-2.amazonaws.com/'+image.image,
            'description': image.description,
            'latitude': image.latitude,
            'longitude': image.longitude,
            'user': user.username,
            'profileImage': user.profile_image_path
        }
    # result.append(response)
    return jsonify(response)

# POST NEW FACT FOR A PLACE


@images_api_blueprint.route('/<id>/newfact', methods=['POST'])
@jwt_required
@csrf.exempt
def newfact(id):
    current_user_id = get_jwt_identity()

    image = Images.get_by_id(id)

    fact = Facts(
        # images_id=image.id,
        title=request.json.get('title'),
        text=request.json.get('text'),
        user_id=current_user_id,
        place=image.name
    )
    if fact.save():
        result = {
            "title": fact.title,
            "text": fact.text,
            "place": fact.place
        }
        return jsonify(result)
    else:
        return jsonify(fact.errors, {
            "status": "failed"
        }), 400

# GET ALL FACTS ASSOCIATED WITH PLACE


@images_api_blueprint.route('/<id>/facts', methods=['GET'])
def facts(id):
    image = Images.get_or_none(Images.id == id)
    facts = Facts.select().where(Facts.place == image.name)

    results = []
    for fact in facts:
        results.append({
            "username": User.get_or_none(User.id == fact.user_id).username,
            "title": fact.title,
            "text": fact.text,
            "id": fact.id
        })

    return jsonify(results)

# GET ALL IMAGES FOR A LOCATION


@images_api_blueprint.route('/search', methods=['POST'])
@csrf.exempt
def location():
    placename = request.form.get('placename')
    images = Images.select().where(Images.name.contains(placename))
    results = []
    if images:
        for image in images:
            results.append({
                "src": f'https://{os.environ.get("S3_BUCKET")}.s3-eu-west-2.amazonaws.com/'+image.image,
                "width": image.width,
                "height": image.height,
                "title": image.name,
                "id": image.id
            })
        return jsonify(results)

    else:
        flash('no images for this location yet.')
        return jsonify({
            "status": "failed"
        }), 400
