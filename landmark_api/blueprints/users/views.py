import io
from google.cloud.vision import types
import os
from flask import Blueprint, request, jsonify
from app import csrf
from models.user import Images
from google.cloud import vision
from config import *
import requests
from landmark_web.util.helpers import upload_file_to_s3


users_api_blueprint = Blueprint('users_api',
                                __name__,
                                template_folder='templates')


@users_api_blueprint.route('/', methods=['GET'])
def index():
    return "USERS API"


@users_api_blueprint.route('/json', methods=['POST'])
@csrf.exempt
def detect_landmarks_uri():
    # # Get image from react front-end form; store image in database and upload to s3 bucket
    # get_image = request.files.get('user_image')

    # output = upload_file_to_s3(get_image)

    # add = Images(image=output, landmark="1")
    # add.save()

    # # Use image to run through vision cloud api
    # test_image = Images.select().where(Images.image == get_image.filename)
    # test_image_uri = test_image[0].image_url

    # client = vision.ImageAnnotatorClient()
    # image = vision.types.Image()
    # uri = test_image_uri
    # image.source.image_uri = uri

    # response = client.landmark_detection(image=image)
    # landmarks = response.landmark_annotations
    # print('Landmarks:')

    # for landmark in landmarks:
    #     print(landmark.locations)

    # kg_id = landmarks[0].mid
    # kg_request = requests.get(
    #     f"https://kgsearch.googleapis.com/v1/entities:search?ids={kg_id}&key={Config.GOOGLE_KG_API_KEY}&limit=1&indent=True")
    # kg = kg_request.json()

    # # print(kg)
    # print(kg["itemListElement"][0]["result"]["description"])

    # result = [
    #     {
    #         "mid": landmark.mid,
    #         "description": landmark.description,
    #         "score": landmark.score,
    #         "locations": [
    #             {
    #                 "lat_lng": {
    #                     "latitude": landmark.locations[0].lat_lng.latitude,
    #                     "longitude": landmark.locations[0].lat_lng.longitude
    #                 }
    #             }
    #         ],
    #         "generalInfo": kg["itemListElement"][0]["result"]["detailedDescription"]["articleBody"]
    #     } for landmark in landmarks
    # ]

    # print(result)

    # return jsonify(result)
    """Detects landmarks in the file."""

    client = vision.ImageAnnotatorClient()

    path = os.path.abspath('KLCC-Penthouse-KL-City-Malaysia.jpg')
    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    response = client.landmark_detection(image=image)
    landmarks = response.landmark_annotations
    print('Landmarks:')

    for landmark in landmarks:
        print(landmark)
        for location in landmark.locations:
            lat_lng = location.lat_lng
            print('Latitude {}'.format(lat_lng.latitude))
            print('Longitude {}'.format(lat_lng.longitude))

    return landmark
