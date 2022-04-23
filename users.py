from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from models import User, db
from flask_jwt_extended import (
    jwt_required, create_access_token,
    get_jwt_identity
)

users_blueprint = Blueprint('users_blueprint', __name__)

@users_blueprint.route('/login', methods=['POST'])
def login():
    # login a user
    try:
        if User.authenticate(request.json['email'], request.json['password']):
            access_token = create_access_token(identity=request.json['email'])
            return jsonify(access_token=access_token)
        else:
            return {"message":"invalid email or password"}, 401
    except:
        return {"message":"invalid login"}, 500

@users_blueprint.route('/signup', methods=['POST'])
def signup():

    d=request.json

    email=d['email']
    password=d['password']
    dob=d['dob']
    # create new user and add for commit
    new_user = User.signup(email, password, dob)
    db.session.add(new_user)
    try:
        # commit new user and return JWT
        db.session.commit()
        new_user=User.query.get_or_404(email, description="user not found")
        return jsonify({"user": new_user.to_dict()}), 201
    except IntegrityError:
        return {"message":"email already in use"}, 500

@users_blueprint.route('/<email>')
@jwt_required()
def get_user(email):
    # get a user by email

    # check JWT identity is same as email
    token_user=get_jwt_identity()
    u=User.query.get_or_404(email, description="user not found")
    if email != u.email:
        return {'message': 'unauthorized'}, 401
    # get user and return json
    
    return jsonify({"user": u.to_dict()})

@users_blueprint.route('/<email>', methods=['PATCH'])
@jwt_required()
def update_user(email):
    # update a user

    # check JWT identity is same as email
    user=User.query.get_or_404(email, description="user not found")

    # return unauthorized message if user not authorized
    if email != user.email:
        return {'message': 'unauthorized'}, 401

    # get data from request.json and update user
    d=request.json
    
    for update in d:
        setattr(user, update, d[update])
            
    db.session.add(user)

    try: 
        # commit to database and return updated user
        db.session.commit()
        updated_user=User.query.get_or_404(user.email, description = "user not found")
        return jsonify({'user': updated_user.to_dict()})
    except IntegrityError:
        return jsonify({'message': 'Email already in use'}), 500
    except:  
        return jsonify({'message': 'unable to edit user'}), 500

@users_blueprint.route('/<email>', methods=['DELETE'])
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
