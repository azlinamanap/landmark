from landmark_api.blueprints.users.views import users_api_blueprint
from landmark_api.blueprints.images.views import images_api_blueprint
from flask import Flask, Blueprint, request, jsonify, flash, redirect, url_for
from app import app
from flask_cors import CORS
import json

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

## API Routes ##


app.register_blueprint(users_api_blueprint, url_prefix='/api/v1/users')
app.register_blueprint(images_api_blueprint, url_prefix='/api/v1/images')
