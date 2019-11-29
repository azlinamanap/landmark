import io
from google.cloud.vision import types
import os
from flask import Blueprint, request, jsonify, flash, redirect, url_for
from flask_jwt_extended import (
    jwt_required, create_access_token, get_jwt_identity)
from app import csrf, s3
from models.user import User, Images
from google.cloud import vision
import requests
import wikipedia

users_api_blueprint = Blueprint('users_api',
                                __name__,
                                template_folder='templates')


@users_api_blueprint.route('/', methods=['GET'])
def getusers():
    users = []
    for user in User.select():
        response = {
            'username': user.username,
            'id': user.id
        }
        users.append(response)
    return jsonify(users)


@users_api_blueprint.route('/me', methods=['GET'])
@jwt_required
def me():
    current_user_id = get_jwt_identity()
    current_user = User.get_by_id(current_user_id)
    result = {
        "username": current_user.username,
        "password": current_user.password
    }
    return jsonify(result)


@users_api_blueprint.route('/', methods=['POST'])
def newuser():
    username = request.json.get('username')
    check_user = User.get_or_none(User.username == username)
    if check_user:
        return redirect('home')
    user = User(
        username=username,
        password=request.json.get('password')
    )
    if user.save():
        access_token = create_access_token(identity=user.id)
        return jsonify({
            "jwt": access_token,
        })
    else:
        return jsonify(user.errors, {
            "status": "Failed to create new account."
        }), 400


@users_api_blueprint.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    user = User.get_or_none(User.username == username)

    if user and password == user.password:
        result = {
            "jwt": create_access_token(identity=user.id),
            "username": user.username,
            "message": "Successfully signed in."
        }
        return jsonify(result)
    else:
        return jsonify({
            "status": "Failed to sign in."
        }), 400


@users_api_blueprint.route('/json', methods=['POST'])
@csrf.exempt
def detect_landmarks_uri():
    """Detects landmarks in the file."""

    picture = request.files.get('user_image')

    try:
        s3.upload_fileobj(
            picture,
            os.environ.get('S3_BUCKET'),
            picture.filename,
            ExtraArgs={
                "ACL": 'public-read',
                "ContentType": picture.content_type
            }
        )

    except:
        flash('Upload unsuccessful')

    client = vision.ImageAnnotatorClient()
    image = vision.types.Image()

    path = f'https://{os.environ.get("S3_BUCKET")}.s3-eu-west-2.amazonaws.com/' + \
        picture.filename

    image.source.image_uri = path

    response = client.landmark_detection(image=image)
    landmarks = response.landmark_annotations
    # print('Landmarks:')

    # kg_id = landmarks[0].mid
    # kg_request = requests.get(
    #     f"https://kgsearch.googleapis.com/v1/entities:search?ids={kg_id}&key={os.environ.get('GOOGLE_KG_API_KEY')}&limit=1&indent=True")
    # kg = kg_request.json()

    result = [
        {
            "mid": landmark.mid,
            "name": landmark.description,
            "score": landmark.score,
            "locations": [
                {
                    "lat_lng": {
                        "latitude": landmark.locations[0].lat_lng.latitude,
                        "longitude": landmark.locations[0].lat_lng.longitude
                    }
                }
            ],
            # "description": kg["itemListElement"][0]["result"]["detailedDescription"]["articleBody"]
        } for landmark in landmarks
    ]

    name1 = result[0]["name"]
    wiki = wikipedia.summary(name1)
    add = Images(image=picture.filename,
                 name=result[0]["name"], description=wiki, latitude=result[0]["locations"][0]["lat_lng"]["latitude"], longitude=result[0]["locations"][0]["lat_lng"]["longitude"])
    add.save()

    return redirect(url_for('info', name=name1))
