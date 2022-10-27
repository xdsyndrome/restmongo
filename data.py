"""Module containing data package (payload)
"""
import json
from datetime import datetime

class Data:
    def __init__(self, _id=None, name=None, dob=None, address=None, description=None, friends=None):
        """Init

        Args:
            _id (str, optional): User's ObjectId
            name (str, optional): User name
            dob (str, optional): User's Date of birth text
            address (str, optional): User's Address text
            description (str, optional): User's Description text
            friends (list, optional): User's List of friends
        """
        self._id = _id
        self.name = name
        self.dob = dob
        self.address = address
        self.description = description
        self.friends = friends
        self.createdAt = str(datetime.now())
        
    def get_json(self):
        """Returns a dictionary containing attributes

        Returns:
            dict: Dictionary of attributes
        """
        result = {}
        for attr, value in self.__dict__.items():
            if value:
                result[attr] = value
        return result
    