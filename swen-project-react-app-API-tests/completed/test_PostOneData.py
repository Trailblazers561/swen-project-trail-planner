import requests
import pytest

# Base URL of the API
BASE_URL = "https://3tpxypd416.execute-api.us-east-1.amazonaws.com/trailplanner_api_stage/trail_data/"

headers = {
    "Authorization": "eyJraWQiOiJwMUpyNWQycUx0T0x4WUVINmZ6RXpOSm1LcSttK0xCRmZEOFdvMVNPanM4PSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiJiNGE4MTRmOC0yMDAxLTcwMDgtNjVmMC04NjZiZTk3YjNjMTgiLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiaXNzIjoiaHR0cHM6XC9cL2NvZ25pdG8taWRwLnVzLWVhc3QtMS5hbWF6b25hd3MuY29tXC91cy1lYXN0LTFfWDl0V0FRM3F3IiwiY29nbml0bzp1c2VybmFtZSI6ImI0YTgxNGY4LTIwMDEtNzAwOC02NWYwLTg2NmJlOTdiM2MxOCIsIm9yaWdpbl9qdGkiOiI4MmIwOTA0MS1iODI4LTQ4ZDItYjhkOC0yMzZiNDMzMDI3MTYiLCJhdWQiOiIxYThqZDE3M3RpdjhsNTlkNTM4M2tmMDVibSIsImV2ZW50X2lkIjoiMjMwYzcwY2MtMGE5YS00ZjM5LWE4ODMtMGQ4YjU0MWY4Y2ZjIiwidG9rZW5fdXNlIjoiaWQiLCJhdXRoX3RpbWUiOjE3NDM3MTQwNDksImV4cCI6MTc0MzcxNzY0OSwiaWF0IjoxNzQzNzE0MDQ5LCJqdGkiOiI1ZmFjYzdiMC1hZGJjLTQxOWMtYjA3Yi00NjMxNjI0ZjE1MzMiLCJlbWFpbCI6ImFkbWluQGdtYWlsLmNvbSJ9.IQ6IkfvKwn9ECMMiawAsRqLVyG_0zt_hS7PKAF4wchdn2WmkhNdwgE595y0dulK_A_sYhd3WiwMljVbwHdBXi24e3Jrqo57dgRz7qo0IxVTBFQcJzip1-NwIvorvvE3BkNDwCWaag9bR2Ds3NrZLImCCUov-OZq-u9rNXWnwtqoCQoOn55190ZWdb-EJ1Xb7hQJs-cKorQOd8mP-awc3SafBISfqti0rYCBxyiY0DfQCTAMb_blCPajF5Xo5pyKkg6sNIFst83vKF65QufTUmf4Ufg0dmzhQbDgap57SGImewufqNitwoz4gZBweBuKgdM2ubjr16qd1Mp6amtJKOQ",
    "Content-Type": "application/json"
}

@pytest.mark.API
def test_post_request():
    payload = {
        "id": 7,
        "timestamp": 1735691235
    }

    response = requests.post(BASE_URL, json=payload, headers=headers)
    
    print(response.json())  # Print response for debugging
    assert response.status_code == 200  # Assuming 201 Created is the expected response