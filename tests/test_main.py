import pytest
from bson import ObjectId
from main import *


# Set root url
url = 'http://127.0.0.1:5000'


@pytest.fixture
def client():
    app, db = create_app(testing=True)
    client = app.test_client()
    yield {"client": client, "db": db}


def test_create_user(client):
    data_1 = {
        "name": "tester1",
        "dob": "12 Dec 1990",
        "address": "address_1",
        "description": "description_1"
    }
    r = client["client"].post("/", json=data_1)
    
    assert r.status_code == 201
    assert r.json['Created user']
    for k, v in data_1.items():
        assert r.json['Created user'][k] == v
        
    # Delete user after test    
    d = client["db"].users.delete_one({"name": "tester1"})
    assert d.deleted_count == 1
    

def test_get_all_users(client):
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
    assert r.status_code == 200
    testers = [r.json[0]["name"], r.json[1]["name"]]
    assert "tester1" in testers
    assert "tester2" in testers
    
    # Delete test data
    d = client["db"].users.delete_many({})
    assert d.deleted_count == 2


def test_delete_user(client):
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
    