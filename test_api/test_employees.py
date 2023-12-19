from views import app

def test_employees_status_get_200():
    response=app.test_client().get("/employees")
    assert response.status_code == 200

def test_employees_status_post_200():
    response=app.test_client().post("/employees")
    assert response.status_code == 200

def test_single_employee_status_get_200():
    response=app.test_client().get("/employee/1")
    assert response.status_code == 200


