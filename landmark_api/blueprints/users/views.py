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
    cred = service_account.Credentials.from_service_account_info({"type": "service_account","project_id": "landmarkit-1574492827189","private_key_id": "8516f1b9582bb8c3f93bf28e8ecf68db09a7e379","private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQDQzLJb+EU62HYR\n8nAvypuitRc8gL7zFMiCwzGLpXVwZ9WcmEfYp7gcItKiYExk6t7CPjezulUx/mSR\nsWXMk4k9L87rgUS/SBsLjCkozugf9+lCCtr1ZMTmCodrtjqm1JED4/OEcBZYHowd\nOiYzCOUT6Mn5w2/Op62PasL+hMlNdPbxPfhPlJLqHerHA2qo6KOKIobeJYByjLKx\n97TNbQAzC0Ag83weK01761ypPRKm4vIuu/9tDt4h8qc7FZ+Di/Z0TF0PKQ6sHGg4\nb7I7B5wyWuzlsTWS7GdMI51VBY2dL8E7LU8RnY9JvOERKgZioewrRG6PV4yCu5QD\nYh3iEf/3AgMBAAECggEAA9+losbT2KLMafUn91MDGSfSkwjxF0cNmJNwzLOYnqm7\n0PMS83uFEwyNq30tiE/CgIhb9dshRSiq3/hnuD23yulN+u4ugtKedyk2Au+iZyQX\nxpBh/dx35Kv8VYIPdinfuNqWmXXk4Y9LhSf02SHd8hpxqM8N43UWkgsRLAdK9Bi3\nT0gso/u6LEExEXe0YKv32Pc73oTIWZMOstDbrHamGbzaBkrdUfvO9t9fjg0bae+t\nMgG3wR/E/v1ScJgJafbGcKX1Y98xg6Y9sqfvT9Va5HLiNBoeYvDDIyXk4ZwdSTvR\nONNV9h/ChoNIDdG+uNQOMY9wpjphGU3xZS8cDosW0QKBgQD3/aZgSLgVsiO5Vt4c\nVbwNj3GV41jPXjhtVXOeqgZ1QeY6iAqB+e08t2deR/TrOIA1ysK4m+GQOfL5llqV\nBBxnI4e/2MEJ6ILUB2VX4FgHP1rzuDl0SmR6+pjWo/wtsy4Migq291b9EbG/4NWA\nrp0Lq2T2ToFchwx7WvztTdacMQKBgQDXiwUQU20Jl7QCoE4vrhimNLeSzu/h0WRk\nIQ6rSLTJHV8LdmcBeQizYiZ8w5yzBSjFOvgHTD3Ovx6BIPaOaRO+Lh4yfyuu9flg\n6HDvZ+prZ+e6OYHCQOJyCjo7jIGWp8Pqz0R33G5epUrF/0ctrPorStrmDrfwZFIz\nDkSSvFjcpwKBgQCgawpnGmNKVZPaXqELP0KImxPk284lRlPGFhLWvjGzRE/D6SCy\n95NJRXKugGmkh0YYhfL0LJH7FCFi5qnt31zoMwmrRnGJEUkgEzCxacRH2+nf4nn4\nCe95xgV8Q1Pr1A6jueA4f0NcLUgIUU6LEWkxlUuYMSxpSEsAuNkIQOPk4QKBgGaY\nsrlZrI4jWrjhSzYg3XTHpRXJUJ+hhvKuVYgsXHladLJFErS9wul376/1gHIqI4T2\nE7eNj+IIUOHQKewRkic1VoRcyhNG3ARHv/IE+a1UURXwZ5ZqQh9cROmxcMGga34q\nWIHhN9vvO89ROrVAH/hZciaNnPpdFk9dHEDoTDgDAoGBAPTrLSWomEonyoMCj/lm\noh16QM8fZqd9f0M47e3bIlxzailwF3ddYZ1xM3M6l5eGqnpfatNa8Sc+u0vXyjTb\n9WvmqZNJylkyC+FJuH5wy+BDnVtXUOR1mAZE5NgYUOSZC28T0n6sd0c6L7rt6iX1\nr2TEikVRckD69R1GmVDMVxCc\n-----END PRIVATE KEY-----\n","client_email": "starting-account-2xyb6t56zwpw@landmarkit-1574492827189.iam.gserviceaccount.com","client_id": "104823819347629366265","auth_uri": "https://accounts.google.com/o/oauth2/auth","token_uri": "https://oauth2.googleapis.com/token","auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/starting-account-2xyb6t56zwpw%40landmarkit-1574492827189.iam.gserviceaccount.com"})
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
