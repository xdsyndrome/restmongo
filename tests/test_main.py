import pytest
from bson import ObjectId
from main import *


# Set root url
url = 'http://127.0.0.1:5000'


@pytest.fixture
def client():
    """Initiates dict of client and db to be passed into other tests as fixture

    Yields:
        dict: dict(client, database)
    """
    app, db = create_app(testing=True)
    client = app.test_client()
    yield {"client": client, "db": db}


def test_create_user(client):
    """Mocks the creation of a user
    """
    # Create user with the following fields
    data_1 = {
        "name": "tester1",
        "dob": "12 Dec 1990",
        "address": "address_1",
        "description": "description_1"
    }
    r = client["client"].post("/", json=data_1)
    
    # Check for status code and fields
    assert r.status_code == 201
    assert r.json['Created user']
    for k, v in data_1.items():
        assert r.json['Created user'][k] == v
        
    # Delete user after test    
    d = client["db"].users.delete_one({"name": "tester1"})
    assert d.deleted_count == 1
    

def test_get_all_users(client):
    """Test the getting of all users
    """
    # Insert two users into database
    data_1 = {
        "name": "tester1",
        "dob": "12 Dec 1990",
        "address": "address_1",
        "description": "description_1"
    }
    
    data_2 = {
        "name": "tester2"
    }
    
    client["client"].post("/", json=data_1)
    client["client"].post("/", json=data_2)
    
    r = client["client"].get("/")
    
    # Check status code and if both users are inside
    assert r.status_code == 200
    testers = [r.json["get all users"][0]["name"], 
               r.json["get all users"][1]["name"]]
    assert "tester1" in testers
    assert "tester2" in testers
    
    # Delete test data
    d = client["db"].users.delete_many({})
    assert d.deleted_count == 2


def test_delete_user(client):
    """Test if delete user works
    """
    # Initiate mock user
    data_1 = {
        "name": "tester1"
    }
    
    # Add user to database
    r = client["client"].post("/", json=data_1)
    user_id = r.json["Created user"]["_id"]["$oid"]
    
    # Returns r_delete in the form of Response with json {"Deleted User": ObjectId}
    r_delete = client["client"].delete("/" + str(user_id))
    assert r_delete.status_code == 200
    assert r_delete.json["Deleted User"] == str(user_id)

    
def test_get_one_user(client):
    """Test get one user
    """
    # Insert user
    data_1 = {
        "name": "tester1"
    }
    r_insert = client["client"].post("/", json=data_1)
    user_id = r_insert.json["Created user"]["_id"]["$oid"]
    
    # Get user
    r_get = client["client"].get("/"+str(user_id))
    assert r_get.status_code == 200
    assert r_get.json["get user"] == str(user_id)
    
    # Delete test data
    d = client["db"].users.delete_many({})
    assert d.deleted_count == 1


def test_update_user(client):
    """Test updating of user fields
    """
    # Insert original user
    data_1 = {
        "name": "tester1"
    }
    r_insert = client["client"].post("/", json=data_1)
    user_id = r_insert.json["Created user"]["_id"]["$oid"]
    
    # Update original user with new name and new field: description
    data_2 = {
        "name": "tester2",
        "description": "description2"
    }
    r_update = client["client"].put("/"+str(user_id), json=data_2)
    # Check response
    assert r_update.status_code == 200
    assert r_update.json["modified user"] == str(user_id)
    assert r_update.json["modified fields"]["name"] == "tester2"
    assert r_update.json["modified fields"]["description"] == "description2"
    
    # Check if user name has changed and if description exists
    user_cursor = client["db"].users.find({"_id": ObjectId(user_id)})
    user_data = list(user_cursor)
    assert user_data[0]["name"] == "tester2"
    assert user_data[0]["description"] == "description2"
    
    # Remove record after testing
    d = client["db"].users.delete_many({})
    assert d.deleted_count == 1
    
    
def test_update_user_wrongly(client):
    """Test if function returns status code 400 if invalid fields are provided
    """
    # Insert original user
    data_1 = {
        "name": "tester1"
    }
    r_insert = client["client"].post("/", json=data_1)
    user_id = r_insert.json["Created user"]["_id"]["$oid"]
    
    # Update original user with new name and new field: description
    data_2 = {
        "wrong_field": "description2"
    }
    r_update = client["client"].put("/"+str(user_id), json=data_2)
    assert r_update.status_code == 400
    
    # Remove record after testing
    d = client["db"].users.delete_many({})
    assert d.deleted_count == 1


def test_update_user_nonexistent(client):
    """Test if status code 400 is returned if a non existent user is updated
    """
    # Insert original user
    data_1 = {
        "name": "tester1"
    }
    r_insert = client["client"].post("/", json=data_1)
    user_id = r_insert.json["Created user"]["_id"]["$oid"]
    
    # Delete user
    d = client["db"].users.delete_many({})
    assert d.deleted_count == 1
    
    # Update original name but user does not exist in database
    data_2 = {
        "name": "tester2"
    }
    r_update = client["client"].put("/"+str(user_id), json=data_2)
    assert r_update.status_code == 304


def test_add_friend(client):
    """Test adding of friends
    
    Test will first create tester1, tester2 and tester3, then add tester2 and 3
    as friends for tester1
    """
    # Insert first user
    data_1 = {
        "name": "tester1"
    }
    r_insert_1 = client["client"].post("/", json=data_1)
    user_id_1 = r_insert_1.json["Created user"]["_id"]["$oid"]
    
    # Insert second user (friend)
    data_2 = {
        "name": "tester2"
    }
    r_insert_2 = client["client"].post("/", json=data_2)
    user_id_2 = r_insert_2.json["Created user"]["_id"]["$oid"]
    
    # Add tester2 as friend for tester1
    data_friend = {
        "friends": user_id_2
    }
    r_add_friend = client["client"].put("/addfriend/"+str(user_id_1), json=data_friend)
    assert r_add_friend.status_code == 200
    assert user_id_2 in r_add_friend.json['added friend'][user_id_1]
    assert len(r_add_friend.json['added friend'][user_id_1]) == 1
    
    # Add one more friend for tester1
    data_3 = {
        "name": "tester3"
    }
    
    r_insert_3 = client["client"].post("/", json=data_3)
    user_id_3 = r_insert_3.json["Created user"]["_id"]["$oid"]
    
    data_friend_3 = {
        "friends": user_id_3
    }
    r_add_friend = client["client"].put("/addfriend/"+str(user_id_1), json=data_friend_3)
    assert r_add_friend.status_code == 200
    assert user_id_3 in r_add_friend.json['added friend'][user_id_1]
    
    # Remove record after testing
    d = client["db"].users.delete_many({})
    assert d.deleted_count == 3

def test_add_invalid_friend(client):
    """Mocks the addition of a friend that is not a user in the database
    """
    # Insert first user
    data_1 = {
        "name": "tester1"
    }
    r_insert_1 = client["client"].post("/", json=data_1)
    user_id_1 = r_insert_1.json["Created user"]["_id"]["$oid"]
    
    # Add invalid as friend for tester1
    invalid_objectId = '635aae9f3e87bc873c34dd0b'
    assert user_id_1 != invalid_objectId
    
    data_friend = {
        "friends": invalid_objectId
    }
    r_add_friend = client["client"].put("/addfriend/"+str(user_id_1), json=data_friend)
    assert r_add_friend.status_code == 400
    assert r_add_friend.json['error'][user_id_1] == "unable to validate"
    
    # Remove record after testing
    d = client["db"].users.delete_many({})
    assert d.deleted_count == 1
    
def test_remove_friend(client):
    """Tests if a friend can be removed
    """
    # Insert first user
    data_1 = {
        "name": "tester1"
    }
    r_insert_1 = client["client"].post("/", json=data_1)
    user_id_1 = r_insert_1.json["Created user"]["_id"]["$oid"]
    
    # Insert second user (friend)
    data_2 = {
        "name": "tester2"
    }
    r_insert_2 = client["client"].post("/", json=data_2)
    user_id_2 = r_insert_2.json["Created user"]["_id"]["$oid"]
    
    # Add tester2 as friend for tester1
    data_friend = {
        "friends": user_id_2
    }

    r_add_friend = client["client"].put("/addfriend/"+str(user_id_1), json=data_friend)
    
    # Check if friend has been added
    user_cursor = client["db"].users.find({"_id": ObjectId(user_id_1)})
    user_data = list(user_cursor)
    assert len(user_data[0]["friends"]) == 1
    
    # Remove tester2 as friend from tester1
    r_remove_friend = client["client"].post("/removefriend/"+str(user_id_1), json=data_friend)
    assert r_remove_friend.status_code == 200
    assert user_id_2 not in r_remove_friend.json["removed friend"][user_id_1]
    
    # Check if friend list has changed
    user_cursor = client["db"].users.find({"_id": ObjectId(user_id_1)})
    user_data = list(user_cursor)
    assert len(user_data[0]["friends"]) == 0

    # Remove record after testing
    d = client["db"].users.delete_many({})
    assert d.deleted_count == 2
    