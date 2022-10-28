# restmongo
## About
This repository contains the backend for a mock service that allows for the CREATE, READ, UPDATE, DELETE of users in an application. The backend database is a MongoDB running in a self-contained Docker container. Other services can interact with this service through the REST APIs included in this module.

## Prerequisites
The app runs on Python 3.7 and above. The following packages are required.
```
flask
pymongo
```

## Getting Started
First start the MongoDB database. Port 8000 is exposed as the MongoDB service port.
```
docker run -d -p 8000:27017 --name test-mongo mongo:latest
```

Run the application by running the following command at the root of the project.
```
python main.py
```
The Flask application will run on localhost:5000. You can check if it is running by typing the following URL:
```
localhost:5000/
```

## Usage
### Functions
The following functions are included in the service.
- create_user
- get_all_users
- get_one_user
- delete_user
- update_user
- add_friend
- remove_friend

### Database Schema
While no specific fields are determined for MongoDB, any data passed into the MongoDB would be converted into a instance of the `Data` class. This ensures that the data fields are inline with the accepted fields for this application. The accepted fields are:
```
_id 
name
dob 
address
description
friends
createdAt
```
`createdAt` and `_id` are automatically generated when a user is created, and should not be amended.

### REST API
The following endpoints require the following URL parameters and JSON inputs.
- create_user
  - URL: `POST` `localhost:5000/`
  - JSON: json payload containing data fields to be included.
    - Payload Example:
      ```
      {
        "name": "Joe",
        "description": "An average joe"
      }
      ```
- get_all_users
  - URL: `GET` `localhost:5000/`
  - JSON: No json payload required.
- get_one_user
  - URL: `GET` `localhost:5000/<string:user_id>`
  - JSON: No json payload required.
- delete_user
  - URL: `DELETE` `localhost:5000/<string:user_id>`
  - JSON: No json payload required.
- update_user
  - URL: `PUT` `localhost:5000/<string:user_id>`
  - JSON: json payload containing data fields to be included.
    - Payload Example:
      ```
      {
        "name": "New Joe",
        "description": "A better joe than average joe"
      }
      ```
- add_friend
  - URL: `PUT` `localhost:5000/addfriend/<string:user_id>`
  - JSON: json payload containing friend's user_id to be included. Note that the friend must be an existing user in the database.
    - Payload Example:
      ```
      {
        "friends": "000000000000"
      }
      ```
- remove_friend
  - URL: `POST` `localhost:5000/removefriend/<string:user_id>`
  - JSON: json payload containing friend's user_id to be removed.
    - Payload Example:
      ```
      {
        "friends": "000000000000"
      }
      ```
## Testing
Functional tests are included. To run the tests, run the following command at the root of the project.
```
pytest -v -s
```
