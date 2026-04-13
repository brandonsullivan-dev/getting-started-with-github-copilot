import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_serves_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text
    assert "Mergington High School" in response.text

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "description" in data["Chess Club"]
    assert "participants" in data["Chess Club"]

def test_signup_success():
    # Sign up a new participant
    response = client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]

    # Verify they were added
    response = client.get("/activities")
    data = response.json()
    assert "newstudent@mergington.edu" in data["Chess Club"]["participants"]

def test_signup_duplicate():
    # First signup
    client.post("/activities/Programming Class/signup?email=dup@mergington.edu")
    # Duplicate attempt
    response = client.post("/activities/Programming Class/signup?email=dup@mergington.edu")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_nonexistent_activity():
    response = client.post("/activities/Nonexistent Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_delete_participant_success():
    # Add a participant first
    client.post("/activities/Gym Class/signup?email=deleteme@mergington.edu")
    # Delete them
    response = client.delete("/activities/Gym Class/participants/deleteme@mergington.edu")
    assert response.status_code == 200
    result = response.json()
    assert "Removed" in result["message"]

    # Verify they were removed
    response = client.get("/activities")
    data = response.json()
    assert "deleteme@mergington.edu" not in data["Gym Class"]["participants"]

def test_delete_participant_not_found():
    response = client.delete("/activities/Chess Club/participants/nonexistent@mergington.edu")
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]

def test_delete_nonexistent_activity():
    response = client.delete("/activities/Nonexistent Activity/participants/test@mergington.edu")
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]