"""Module containing data package (payload)
"""
import json
from datetime import datetime

class Data:
    def __init__(self, _id=None, name=None, dob=None, address=None, description=None):
        """Init

        Args:
            _id (str, optional): _description_. Defaults to None.
            name (str, optional): _description_. Defaults to None.
            dob (str, optional): _description_. Defaults to None.
            address (str, optional): _description_. Defaults to None.
            description (str, optional): _description_. Defaults to None.
        """
        self._id = _id
        self.name = name
        self.dob = dob
        self.address = address
        self.description = description
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
    