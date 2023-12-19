from views import app

def test_add_leave_statuscode():
    headers = {'Content-Type': 'application/json'}
    data = {'date': '2023-01-01', 'reason': 'pani'}
    
    response = app.test_client().post("/leave/1", headers=headers, json=data)
    
    assert response.status_code == 200