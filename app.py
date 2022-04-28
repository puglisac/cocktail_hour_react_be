from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension
from models import Cocktail, connect_db
from flask_jwt_extended import JWTManager, create_access_token
import os
from datetime import timedelta
from flask import request, jsonify
from sqlalchemy.exc import IntegrityError
from models import User, db
from flask_jwt_extended import (jwt_required, create_access_token)
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'postgresql://@localhost:5433/cocktails_two')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'shh')
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
jwt = JWTManager(app)
debug = DebugToolbarExtension(app)

connect_db(app)


@app.route('/login', methods=['POST'])
def login():
    # login a user
    try:
        if User.authenticate(request.json['email'], request.json['password']):
            access_token = create_access_token(identity=request.json['email'])
            return jsonify(access_token=access_token)
        else:
            return {"message": "invalid email or password"}, 401
    except:
        return {"message": "invalid login"}, 500


@app.route('/signup', methods=['POST'])
def signup():

    d = request.json

    email = d['email']
    password = d['password']
    dob = d['dob']
    # create new user and add for commit
    new_user = User.signup(email, password, dob)
    db.session.add(new_user)
    try:
        # commit new user and return JWT
        db.session.commit()
        new_user = User.query.get_or_404(email, description="user not found")
        return jsonify({"user": new_user.to_dict()}), 201
    except IntegrityError:
        return {"message": "email already in use"}, 500


@app.route('/<email>')
@jwt_required()
def get_user(email):
    # get a user by email

    # check JWT identity is same as email
    u = User.query.get_or_404(email, description="user not found")
    if email != u.email:
        return {'message': 'unauthorized'}, 401
    # get user and return json

    return jsonify({"user": u.to_dict()})


@app.route('/<email>', methods=['PATCH'])
@jwt_required()
def update_user(email):
    # update a user

    # check JWT identity is same as email
    user = User.query.get_or_404(email, description="user not found")

    # return unauthorized message if user not authorized
    if email != user.email:
        return {'message': 'unauthorized'}, 401

    # get data from request.json and update user
    d = request.json

    for update in d:
        setattr(user, update, d[update])

    db.session.add(user)

    try:
        # commit to database and return updated user
        db.session.commit()
        updated_user = User.query.get_or_404(
            user.email, description="user not found")
        return jsonify({'user': updated_user.to_dict()})
    except IntegrityError:
        return jsonify({'message': 'Email already in use'}), 500
    except:
        return jsonify({'message': 'unable to edit user'}), 500


@app.route('/<email>', methods=['DELETE'])
@jwt_required()
def delete_user(email):
    # delete a user

    # check JWT identity is same as email
    user = User.query.get_or_404(email, description="user not found")

    # return unauthorized message if user not authorized
    if email != user.email:
        return {'message': 'unauthorized'}, 401

    # find and delete user
    db.session.delete(user)
    try:
        # commit and return success message
        db.session.commit()
        return jsonify({'message': 'user successfully deleted'})
    except:
        return jsonify({'message': 'unable to delete user'}), 500


@app.route('/<email>/save', methods=['POST'])
@jwt_required()
def save_cocktail(email):
    # save a cocktail to a user

    # check JWT identity is same as email
    user = User.query.get_or_404(email, description="user not found")

    # return unauthorized message if user not authorized
    if email != user.email:
        return {'message': 'unauthorized'}, 401
    c = request.json
    id = c['id']
    name = c['name']
    img_url = c['img_url']
    cocktail = Cocktail.query.get(id)

    if not cocktail:
        cocktail = Cocktail(id=id, name=name, drink_img_url=img_url)
        db.session.add(cocktail)
        try:
            db.session.commit()
        except:
            return jsonify({"message": "unable to add cocktail"})
    try:
        user.save_cocktail(cocktail)
        return jsonify({"cocktail": cocktail.to_dict()})
    except:
        return jsonify({"message": "unable to save cocktail to user"})


@app.route('/<email>/remove/<id>', methods=['POST'])
@jwt_required()
def remove_cocktail(email, id):
    # remove a cocktail from a user

    # check JWT identity is same as email
    user = User.query.get_or_404(email, description="user not found")

    # return unauthorized message if user not authorized
    if email != user.email:
        return {'message': 'unauthorized'}, 401

    cocktail = Cocktail.query.get_or_404(id)
    user.saved_cocktails.remove(cocktail)
    db.session.commit()

    if not cocktail.user:
        db.session.delete(cocktail)
        db.session.commit()

    return jsonify({"message": "removed"})
