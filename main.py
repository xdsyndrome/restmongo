"""Main module containing all APIs
"""
import json
from flask import Flask, jsonify, request, Response
from database import MongoDatabase
from data import Data


def create_app(testing):
    app = Flask(__name__)
    db = MongoDatabase(testing=testing)
    
    @app.route('/', methods=['GET'])
    def get_all_users():
        """Gets all users from collection

        Returns:
            flask.wrapper.Response: Flask response
        """
        users = db.get_all()
        response = Response(response=json.dumps({"get all users": users}),
                            status=200,
                            mimetype='application/json')
        return response


    @app.route('/<string:user_id>', methods=['GET'])
    def get_one_user(user_id):
        """Gets one user based on user_id from collection

        Args:
            user_id (str): ObjectId

        Returns:
            flask.wrapper.Response: Flask response
        """
        try:
            user = db.get_id(user_id)
            if user and user['_id']:
                return Response(response=json.dumps({"get user": user_id}),
                            status=200,
                            mimetype='application/json')
            else:
                return Response(response=json.dumps({"error": "No such user"}),
                            status=404,
                            mimetype='application/json')
        except Exception as e:
            return Response(response=json.dumps({"error": str(e)}),
                            status=400,
                            mimetype='application/json')


    @app.route('/', methods=['POST'])
    def create_user():
        """Creates a new user

        Returns:
            flask.wrapper.Response: Flask response
        """
        try:
            new_user = Data(**request.get_json())
        except TypeError as e:
            return Response(response=json.dumps({"error": "create-user-1", 
                                                 "message": str(e)}),
                            status=400,
                            mimetype='application/json'
                            )
        result = db.create_user(new_user.get_json())
        user = db.get_id(result)
        if user:
            return Response(response=json.dumps({"Created user": user}),
                            status=201,
                            mimetype='application/json'
                            )
        else:
            return Response(response=json.dumps({"error": "create-user-2", 
                                                 "message": "Failed to create user"}),
                            status=400,
                            mimetype='application/json')



    @app.route('/<string:user_id>', methods=['DELETE'])
    def delete_user(user_id):
        """Deletes a user based on user_id

        Args:
            user_id (str): ObjectId

        Returns:
            flask.wrapper.Response: Flask response
        """
        result = db.delete(user_id)
        if result['deleted_count'] >= 1:
            response = Response(response=json.dumps({"Deleted User": user_id}),
                                status=200,
                                mimetype='application/json')
        else:
            response = Response(response=json.dumps({'error': 'Deleted count is not 1'}),
                                status=404,
                                mimetype='application/json')
        return response


    @app.route('/<string:user_id>', methods=['PUT'])
    def update_user(user_id):
        """Updates a user based on user fields

        Args:
            user_id (str): ObjectId

        Returns:
            flask.wrapper.Response: Flask response
        """
        try:
            new_user = Data(**request.get_json())
        except TypeError as e:
            return Response(status=400,
                            mimetype='application/json'
                            )
        # Update returns int 1 if successful
        result = db.update(user_id, new_user.get_json())
        if result == 1:
            response = Response(response=json.dumps({"modified user": user_id,
                                                    "modified fields": new_user.get_json()}),
                                status=200,
                                mimetype='application/json')
        elif result == 0:
            # If result is 0, the update has not been made
            response = Response(response=json.dumps({"error": "Update not made"}),
                                status=304, 
                                mimetype='application/json')
        else:
            response = Response(response=json.dumps({"error": "Client error"}),
                                status=400,
                                mimetype='application/json')
        return response
    
    @app.route('/addfriend/<string:user_id>', methods=["PUT"])
    def add_friend(user_id):
        """Add a friend to the user's friend list.
        The friend must be an existing user in the database
        (i.e. friend_id is a valid _id in the database)

        Returns:
            flask.wrapper.Response: Flask response
        """
        try:
            new_data = Data(**request.get_json())
        except TypeError as e:
            return Response(response=json.dumps({"error": "Invalid Field"}),
                            status=400,
                            mimetype='application/json')
        
        result = db.add_friend(user_id, new_data.get_json()['friends'])

        if isinstance(result[user_id], list) & (len(result[user_id]) >= 1):
            return Response(response=json.dumps({"added friend": result}),
                            status=200,
                            mimetype='application/json')
        else:
            return Response(response=json.dumps({"error": result}),
                            status=400,
                            mimetype='application/json')

    @app.route('/removefriend/<string:user_id>', methods=["POST"])
    def remove_friend(user_id):
        """Remove a friend from the user's friend list.
        Function will also validate if a friend's ID has been provided.

        Args:
            user_id (ObjectId): User ID

        Returns:
            flask.wrapper.Response: Flask response
        """
        try:
            new_data = Data(**request.get_json())
        except TypeError as e:
            return Response(response=json.dumps({"error": "Invalid Field"}),
                            status=400,
                            mimetype='application/json')

        # If no friend id in JSON request
        if len(new_data.get_json()['friends']) == 0:
            return Response(response=json.dumps({"error": "No friend_id provided"}),
                            status=400,
                            mimetype='application/json')
        else:
            result = db.remove_friend(user_id, new_data.get_json()['friends'])

        # Parse results
        if isinstance(result[user_id], list):
            return Response(response=json.dumps({"removed friend": result}),
                            status=200,
                            mimetype='application/json')
        else:
            return Response(response=json.dumps({"error": result}),
                            status=400,
                            mimetype='application/json')
    
    return app, db


if __name__ == '__main__':
    app, db = create_app(testing=False)
    app.run(debug=True)
    