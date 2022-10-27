"""Module containing all database methods
"""

from pymongo import MongoClient
from bson import json_util, ObjectId
import json


class MongoDatabase:
    def __init__(self, testing=False) -> None:
        """Init
        """
        self.client = MongoClient('mongodb://localhost:8000/')
        # Database
        self.db = self.client.db
        # Collection
        if testing:
            self.users = self.db.users_test
        else:
            self.users = self.db.users
        
    def get_all(self):
        """Get all users

        Returns:
            list: List of users
        """
        cursor = self.users.find({})
        users = json.loads(json_util.dumps(list(cursor)))
        for user in users:
            user["_id"] = user["_id"]["$oid"]
        return users
    
    def get_id(self, user_id):
        """_summary_

        Args:
            user_id (str): ObjectId

        Returns:
            dict: User
        """
        user = self.users.find_one({"_id": ObjectId(user_id)})
        user = json.loads(json_util.dumps(user))
        return user
    
    def create_user(self, new_data):
        """_summary_

        Args:
            new_data (dict): Dictionary containing new user with corresponding fields

        Returns:
            str: Id of new user
        """
        result = self.users.insert_one(new_data)
        new_id = json.loads(json_util.dumps(result.inserted_id))
        return list(new_id.values())[0]
    
    def update(self, user_id, new_data) -> int:
        """_summary_

        Args:
            user_id (str): ObjectId
            new_data (dict): Dictionary containing fields with updated values

        Returns:
            dict: Dictionary containing deleted_count. Deleted_count is 1 if successful
        """
        result = self.users.update_one(filter={"_id": ObjectId(user_id)},
                                       update={"$set": new_data})
        return result.modified_count
    
    def delete(self, user_id):
        result = self.users.delete_one({"_id": ObjectId(user_id)})
        output = {
            'deleted_count': result.deleted_count,
        }
        return output
    
    def validate_user(self, user_id):
        """Checks if user_id exists in database

        Args:
            user_id (ObjectId): User's ID
        
        Returns:
            boolean: True if valid, else false
        """
        cursor = self.users.find({"_id": ObjectId(user_id)})
        if list(cursor):
            return True
        else: 
            return False
    
    def add_friend(self, user_id, friend_id):
        """Finds user's friend list using user_id, then appends friend_id to the list
        Before adding, need to validate if friend is a user too

        Args:
            user_id (ObjectId): User's ID
            friend_id (ObjectId): Friend's ID
        
        Returns:
            dict: Dictionary containing user's ID and new list of friends
        """
        # Validate friend ID
        if self.validate_user(friend_id):
            self.users.update_one({"_id": ObjectId(user_id)},
                                  {"$push": {"friends": friend_id}})
            cursor = self.users.find({"_id": ObjectId(user_id)})
            d = list(cursor)[0]
            return {user_id: d["friends"]}
        else:
            return {user_id: "unable to validate"}
    
    def remove_friend(self, user_id, friend_id):
        """Finds user's friend list using user_id, then removes friend_id from the list
        Before removing, need to validate if friend is a user too

        Args:
            user_id (ObjectId): User's ID
            friend_id (ObjectId): Friend to be removed's ID
        
        Returns:
            dict: Dictionary containing user's ID and new list of friends
        """
        if self.validate_user(friend_id):
            cursor = self.users.find({"_id": ObjectId(user_id)})
            d = list(cursor)[0]
            try:
                d['friends'].remove(friend_id)
                self.users.update_one({"_id": ObjectId(user_id)},
                                      {"$set": {"friends": d['friends']}})
                cursor = self.users.find({"_id": ObjectId(user_id)})
                d = list(cursor)[0]
                return {user_id: d["friends"]}
            except ValueError:
                return {user_id: "friend not found in list"}
        else:
            return {user_id: "unable to validate"}
    