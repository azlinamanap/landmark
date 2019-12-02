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
import datetime
import random
from google.oauth2 import service_account

users_api_blueprint = Blueprint('users_api',
                                __name__,
                                template_folder='templates')

# GET ALL USERS


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

# GET CURRENT USER


@users_api_blueprint.route('/me', methods=['GET'])
@jwt_required
def me():
    current_user_id = get_jwt_identity()
    current_user = User.get_by_id(current_user_id)
    result = {
        "username": current_user.username,
        "password": current_user.password,
        "email": current_user.email,
        "description": current_user.description,
        "profileImage": current_user.profile_image_path
    }
    return jsonify(result)

# CREATE NEW USER


@users_api_blueprint.route('/signup', methods=['POST'])
@csrf.exempt
def newuser():
    username = request.json.get('username')
    email = request.json.get('email')
    check_user = User.get_or_none(User.username == username)
    check_email = User.get_or_none(User.email == email)
    if check_user:
        return jsonify({
            "status": "Username already taken."
        }), 418
    if check_email:
        return jsonify({
            "status": "Email already used."
        }), 418
    user = User(
        username=username,
        password=request.json.get('password'),
        email=email
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

# LOGIN USER


@users_api_blueprint.route('/login', methods=['POST'])
@csrf.exempt
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    user = User.get_or_none(User.username == username)
    expires = datetime.timedelta(days=1)

    if user and password == user.password:
        result = {
            "jwt": create_access_token(identity=user.id, expires_delta=expires),
            "username": user.username,
            "message": "Successfully signed in."
        }
        return jsonify(result)
    else:
        return jsonify({
            "status": "Failed to sign in."
        }), 400

# EDIT PROFILE FOR CURRENT USER


@users_api_blueprint.route('/me/edit', methods=['POST'])
@jwt_required
@csrf.exempt
def update():
    current_user_id = get_jwt_identity()
    current_user = User.get_by_id(current_user_id)
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')
    description = request.json.get('description')

    check_username = User.get_or_none(User.username == username)

    if check_username:
        return jsonify({
            "status": "Username already taken."
        }), 400

    if not username:
        username = current_user.username  # check for if username isnt changed
    if not password:
        password = current_user.password
    if not email:
        email = current_user.email
    if not description:
        description = current_user.description
    User.update(username=username, password=password, email=email,
                description=description).where(User.id == current_user_id).execute()
    result = {
        "jwt": create_access_token(identity=current_user_id),
        "username": username,
        "email": email,
        "description": description,
        "message": "Successfully edited details."
    }
    return jsonify(result)


# EDIT PROFILE PICTURE
@users_api_blueprint.route('/me/edit/picture', methods=['POST'])
@csrf.exempt
@jwt_required
def updatepic():
    profileImage = request.files.get('profileImage')

    current_user_id = get_jwt_identity()
    current_user = User.get_by_id(current_user_id)
    try:
        s3.upload_fileobj(
            profileImage,
            os.environ.get('S3_BUCKET'),
            profileImage.filename,
            ExtraArgs={
                "ACL": 'public-read',
                "ContentType": profileImage.content_type
            }
        )

        User.update(profilepic=profileImage.filename).where(
            User.id == current_user_id).execute()

    except:
        flash('Upload unsuccessful')

    result = {
        "jwt": create_access_token(identity=current_user_id),
        "profileImage": current_user.profile_image_path,
        "message": "Successfully edited details."
    }

    return jsonify(result)


# SEARCH FOR USER CONTAINING SUBSTRING


@users_api_blueprint.route('/search', methods=['POST'])
@csrf.exempt
def searchuser():
    string = request.form.get('searchInput')
    users = User.select().where(User.username.contains(string))
    matches = []

    if users:
        for user in users:
            matches.append({
                "profileImage": user.profile_image_path,
                "username": user.username,
                "description": user.description
            })
        return jsonify(matches)

    else:
        return jsonify({
            "status": "No such user."
        }), 400

# API SHIT


# @jwt_required
@users_api_blueprint.route('/json', methods=['POST'])
@csrf.exempt
def detect_landmarks_uri():
    """Detects landmarks in the file."""

    picture = request.files.get('user_image')

    current_user_id = get_jwt_identity()

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
    cred = service_account.Credentials.from_service_account_info(
        os.environ.get('GOOGLE_CRED'))
    client = vision.ImageAnnotatorClient(credentials=cred)
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
    width = random.randint(1, 4)
    height = random.randint(1, 4)
    add = Images(image=picture.filename,
                 name=result[0]["name"], description=wiki, latitude=result[0]["locations"][0]["lat_lng"]["latitude"], longitude=result[0]["locations"][0]["lat_lng"]["longitude"], user_id=current_user_id, width=width, height=height)
    add.save()

    result2 = [
        {
            "mid": landmark.mid,
            "name": landmark.description,
            "score": landmark.score,
            "id": add.id,
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

    return jsonify(result2)
