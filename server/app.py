#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        # Create a new user with the username in signup form
        username = request.get_json()["username"]
        password = request.get_json()["password"]
        image_url = request.get_json()["image_url"]
        bio = request.get_json()["bio"]

        if username and password:
            new_user = User(
                username=username,
                image_url=image_url,
                bio=bio
            )

            # encrypted password, image URL, and bio.
            new_user.password_hash = password
            # new_user.image_url = request.get_json()["image_url"]
            # new_user.bio = request.get_json()["bio"]
            # Save a new user to the database 
            db.session.add(new_user)
            db.session.commit()

            # Save the user's ID in the session object as user_id.
            session["user_id"] = new_user.id
            # Return a JSON response, HTTP status code of 201 (Created)
            return new_user.to_dict(), 201
        # If the user is not valid: error message + 422
        return {'error': '422 Unprocessable Entity'}, 422


class CheckSession(Resource):
    def get(self):
        # if the user is logged in (if their user_id is in the session object):
        if session.get("user_id"):
            # Return a JSON response + an HTTP status code of 200
            user = User.query.filter_by(id=session["user_id"]).first()
            return user.to_dict(), 200
        # not logged in: Return a JSON response + 401 (Unauthorized).
        return {"error": {"401: Unauthorized user"}}, 401

class Login(Resource):
    def post(self):
        username = request.get_json()["username"]
        password = request.get_json()["password"]
        user = User.query.filter_by(username=username).first()
        if user.authenticate(password):
            session["user_id"] = user.id
            return user.to_dict(), 200
        return {"error": "401: Unauthorized"}, 401


class Logout(Resource):
    def delete(self):
        # if the user is logged in 
        if session.get('user_id'):
            # Remove the user's ID from the session object.
            session["user_id"] = None
            # Return an empty response with an HTTP status code of 204 (No Content).
            return {}, 204
        return {"error": "401: Unauthorized"}, 401


class RecipeIndex(Resource):
    def get(self):
        # if the user is logged in (if their user_id is in the session object):
        # Return a JSON response with an array of all recipes with their title, instructions, and minutes to complete data 
        # along with a nested user object; and an HTTP status code of 200 (Success).
        if session.get("user_id"):
            recipes = Recipe.query.all()
            recipes_dict = [recipe.to_dict(rules=("users")) for recipe in recipes]
            return make_response(recipes_dict, 200)
        return {"error": "401: Unauthorized"}, 401
    
    # create new recipes
    def post(self):
        if session.get("user_id"):
            title = request.get_json()["title"]
            instructions = request.get_json()["instructions"]
            minutes_to_complete = request.get_json()["minutes_to_complete"]
            # Save a new recipe to the database if it is valid. along with a nested user object
            if title and instructions and minutes_to_complete:
                new_recipe = Recipe(
                    title=title, instructions=instructions, minutes_to_complete=minutes_to_complete
                )
                db.session.add(new_recipe)
                db.session.commit()
                session["user_id"] = new_recipe.id
                return new_recipe.to_dict("users"), 201
            # If the recipe is not valid
            return {"error": "422: Unprocessable Entity"}, 422
        # If the user is not logged in
        return {"error", "401: Unauthorized"}, 401


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
