import io
from google.cloud.vision import types
import os
from flask import Blueprint, request, jsonify, flash, redirect, url_for
from app import csrf, s3
from models.user import Images
from google.cloud import vision
import requests


users_api_blueprint = Blueprint('users_api',
                                __name__,
                                template_folder='templates')


@users_api_blueprint.route('/', methods=['GET'])
def index():
    return "USERS API"


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
        add = Images(image=picture.filename, landmark_id="1")
        add.save()
    except:
        flash('Upload unsuccessful')

    client = vision.ImageAnnotatorClient()
    image = vision.types.Image()

    path = f'https://{os.environ.get("S3_BUCKET")}.s3-eu-west-2.amazonaws.com/' + \
        picture.filename

    image.source.image_uri = path

    response = client.landmark_detection(image=image)
    landmarks = response.landmark_annotations
    print('Landmarks:')

    kg_id = landmarks[0].mid
    kg_request = requests.get(
        f"https://kgsearch.googleapis.com/v1/entities:search?ids={kg_id}&key={os.environ.get('GOOGLE_KG_API_KEY')}&limit=1&indent=True")
    kg = kg_request.json()

    result = [
        {
            "mid": landmark.mid,
            "description": landmark.description,
            "score": landmark.score,
            "locations": [
                {
                    "lat_lng": {
                        "latitude": landmark.locations[0].lat_lng.latitude,
                        "longitude": landmark.locations[0].lat_lng.longitude
                    }
                }
            ],
            "generalInfo": kg["itemListElement"][0]["result"]["detailedDescription"]["articleBody"]
        } for landmark in landmarks
    ]

    print(result)

    return jsonify(result[0])

    # return kg["itemListElement"][0]["result"]["detailedDescription"]["articleBody"]
