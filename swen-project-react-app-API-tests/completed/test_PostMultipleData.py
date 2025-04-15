import requests
import pytest

# Base URL of the API
BASE_URL = "https://h12yxdhdlj.execute-api.us-east-1.amazonaws.com/trailplanner_api_stage/trail_data/"

headers = {
    "Authorization": "eyJraWQiOiJKWlcxNG1oWnR6TkF2NTFXWnFVT3pUY1ZqT2dZZVF2SU5vT21FV2pmOWFjPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiIyNDE4MjRjOC1lMDIxLTcwOTQtZDU4ZC1mMzllZGQ5N2NiZjYiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfSHVNbzgwa0JMIiwiY29nbml0bzp1c2VybmFtZSI6IjI0MTgyNGM4LWUwMjEtNzA5NC1kNThkLWYzOWVkZDk3Y2JmNiIsIm9yaWdpbl9qdGkiOiJjZmJkMjY2NC0zMGNmLTQxYTItOTE0NS05YjA0ODA4MjA5ODIiLCJhdWQiOiI0bmQxcTMwZzR2OGF2cTdrbzA4MDNjbG4wOSIsImV2ZW50X2lkIjoiYzQwMTdlN2YtYmNjMC00MzlhLTkzOTItMzdkMzU2N2JjOGE2IiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NDQ3NTM4NzMsImV4cCI6MTc0NDc1NzQ3MywiaWF0IjoxNzQ0NzUzODczLCJqdGkiOiIzNGI4NmUzMi0wNGE4LTQzMzctYjUyMS1hYjZhOTk0NmVmNjAiLCJlbWFpbCI6ImFkbWluQGdtYWlsLmNvbSJ9.mIXBvJUYsImcE5jgEH2huDK1Gu_mCALw7zlJ9a-oV7vyvjx2GmI7wvTDBjKqtxnC1IbiLNtuI8YAkW7-pydDloymFttMPrO-d4At8orkl1ouNMnCmT8e9wc5KSLLTGts_CzgLYw5PTEmkTaSDrw4rDMqRqlKRmxIt7G1T0F1F-h-tOSi52h2W9mvVpFwF-LgrgM_DJVEDoH1k_-Fa-qSNLmKhTubUoiHfo-DaGUqOz6Z3Pc_89z5bQm3Rc3edLZqoNMspdqKWP1TIvJvjVnML10DswyGd_dycXWc2QgS_1P_kz6tyLHcU7jSzqEYre7fEFMFGQ_kdtCHu51SNMS-hA",
    "Content-Type": "application/json"
}

@pytest.mark.API
def test_post_request():
    payload = {
        "id" : 1,
        "data" : [
        {"timestamp" : 37334782784}, {"timestamp": 37334782764}, {"timestamp": 47777777777}
        ]

    }

    response = requests.post(BASE_URL, json=payload, headers=headers)
    
    print(response.json())  # Print response for debugging
    assert response.status_code == 200  # Assuming 201 Created is the expected response